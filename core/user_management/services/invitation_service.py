"""
User Invitation Service
File: core/user_management/services/invitation_service.py

Service for managing user invitations and email integration.
"""

import logging
import secrets
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.user_management.models.invitation_models import UserInvitation, PasswordResetToken
from core.user_management.models.user_models import Organization
from core.notifications.services.gmail_smtp_service import GmailSMTPService
from core.audit.services.audit_service import AuditService

CustomUser = get_user_model()
logger = logging.getLogger(__name__)

class UserInvitationService:
    """
    Service for managing user invitations with email integration (SRS R1.2.2)
    """
    
    def __init__(self):
        self.email_service = GmailSMTPService()
        self.audit_service = AuditService()
    
    def send_invitation(self, inviter: CustomUser, organization: Organization, 
                       email: str, role: str = 'viewer', message: str = '') -> Dict[str, Any]:
        """
        Send a user invitation email
        
        Args:
            inviter: User sending the invitation
            organization: Organization to invite user to
            email: Email address of invitee
            role: Role to assign ('viewer' or 'publisher')
            message: Optional message from inviter
            
        Returns:
            Dictionary with invitation result
        """
        try:
            # Validate inviter permissions
            if not self._can_invite_users(inviter, organization):
                return {
                    'success': False,
                    'message': 'You do not have permission to invite users to this organization'
                }
            
            # Check if user already exists in the organization
            if self._user_exists_in_organization(email, organization):
                return {
                    'success': False,
                    'message': 'User is already a member of this organization'
                }
            
            # Check for existing pending invitation
            existing_invitation = UserInvitation.objects.filter(
                email=email,
                organization=organization,
                status='pending'
            ).first()
            
            if existing_invitation and not existing_invitation.is_expired:
                return {
                    'success': False,
                    'message': 'A pending invitation already exists for this email address'
                }
            
            # Generate secure invitation token
            invitation_token = self._generate_invitation_token()
            
            with transaction.atomic():
                # Cancel any existing pending invitations
                if existing_invitation:
                    existing_invitation.cancel()
                
                # Create new invitation
                invitation = UserInvitation.objects.create(
                    email=email,
                    organization=organization,
                    inviter=inviter,
                    invited_role=role,
                    token=invitation_token,
                    message=message
                )
                
                # Send invitation email
                email_result = self.email_service.send_user_invitation_email(
                    email=email,
                    organization=organization,
                    inviter=inviter,
                    invitation_token=invitation_token
                )
                
                if email_result.get('success'):
                    # Log the invitation
                    self.audit_service.log_user_action(
                        user=inviter,
                        action='user_invitation_sent',
                        resource_type='invitation',
                        resource_id=str(invitation.id),
                        details={
                            'invitee_email': email,
                            'organization_id': str(organization.id),
                            'organization_name': organization.name,
                            'invited_role': role
                        }
                    )
                    
                    return {
                        'success': True,
                        'message': f'Invitation sent successfully to {email}',
                        'invitation_id': str(invitation.id),
                        'expires_at': invitation.expires_at.isoformat()
                    }
                else:
                    # Email failed, mark invitation as failed
                    invitation.delete()
                    return {
                        'success': False,
                        'message': f'Failed to send invitation email: {email_result.get("message", "Unknown error")}'
                    }
                    
        except Exception as e:
            logger.error(f"Failed to send invitation: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to send invitation. Please try again later.'
            }
    
    def accept_invitation(self, invitation_token: str, user: CustomUser) -> Dict[str, Any]:
        """
        Accept a user invitation
        
        Args:
            invitation_token: Secure invitation token
            user: User accepting the invitation
            
        Returns:
            Dictionary with acceptance result
        """
        try:
            invitation = UserInvitation.objects.filter(token=invitation_token).first()
            
            if not invitation:
                return {
                    'success': False,
                    'message': 'Invalid invitation token'
                }
            
            if not invitation.is_pending:
                status_messages = {
                    'accepted': 'This invitation has already been accepted',
                    'expired': 'This invitation has expired',
                    'cancelled': 'This invitation has been cancelled'
                }
                return {
                    'success': False,
                    'message': status_messages.get(invitation.status, 'This invitation is no longer valid')
                }
            
            # Check if email matches
            if user.email.lower() != invitation.email.lower():
                return {
                    'success': False,
                    'message': 'Your email address does not match the invitation'
                }
            
            with transaction.atomic():
                # Add user to organization
                organization_result = self._add_user_to_organization(
                    user, invitation.organization, invitation.invited_role
                )
                
                if organization_result.get('success'):
                    # Accept the invitation
                    invitation.accept(user)
                    
                    # Log the acceptance
                    self.audit_service.log_user_action(
                        user=user,
                        action='user_invitation_accepted',
                        resource_type='invitation',
                        resource_id=str(invitation.id),
                        details={
                            'organization_id': str(invitation.organization.id),
                            'organization_name': invitation.organization.name,
                            'role': invitation.invited_role,
                            'inviter': invitation.inviter.username
                        }
                    )
                    
                    return {
                        'success': True,
                        'message': f'Successfully joined {invitation.organization.name}',
                        'organization': {
                            'id': str(invitation.organization.id),
                            'name': invitation.organization.name,
                            'role': invitation.invited_role
                        }
                    }
                else:
                    return organization_result
                    
        except Exception as e:
            logger.error(f"Failed to accept invitation: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to accept invitation. Please try again later.'
            }
    
    def list_invitations(self, organization: Organization, status: str = None) -> List[Dict[str, Any]]:
        """
        List invitations for an organization
        
        Args:
            organization: Organization to list invitations for
            status: Optional status filter
            
        Returns:
            List of invitation data
        """
        try:
            queryset = UserInvitation.objects.filter(organization=organization)
            
            if status:
                queryset = queryset.filter(status=status)
            
            invitations = []
            for invitation in queryset.order_by('-created_at'):
                # Auto-expire old invitations
                if invitation.is_expired and invitation.status == 'pending':
                    invitation.expire()
                
                invitations.append({
                    'id': str(invitation.id),
                    'email': invitation.email,
                    'invited_role': invitation.invited_role,
                    'status': invitation.status,
                    'inviter': {
                        'username': invitation.inviter.username,
                        'full_name': invitation.inviter.get_full_name()
                    },
                    'created_at': invitation.created_at.isoformat(),
                    'expires_at': invitation.expires_at.isoformat(),
                    'accepted_at': invitation.accepted_at.isoformat() if invitation.accepted_at else None,
                    'message': invitation.message,
                    'is_expired': invitation.is_expired
                })
            
            return invitations
            
        except Exception as e:
            logger.error(f"Failed to list invitations: {str(e)}")
            return []
    
    def cancel_invitation(self, invitation_id: str, cancelling_user: CustomUser) -> Dict[str, Any]:
        """
        Cancel a pending invitation
        
        Args:
            invitation_id: ID of invitation to cancel
            cancelling_user: User cancelling the invitation
            
        Returns:
            Dictionary with cancellation result
        """
        try:
            invitation = UserInvitation.objects.filter(id=invitation_id).first()
            
            if not invitation:
                return {
                    'success': False,
                    'message': 'Invitation not found'
                }
            
            # Check permissions
            if not self._can_manage_invitation(cancelling_user, invitation):
                return {
                    'success': False,
                    'message': 'You do not have permission to cancel this invitation'
                }
            
            if invitation.status != 'pending':
                return {
                    'success': False,
                    'message': 'Only pending invitations can be cancelled'
                }
            
            invitation.cancel()
            
            # Log the cancellation
            self.audit_service.log_user_action(
                user=cancelling_user,
                action='user_invitation_cancelled',
                resource_type='invitation',
                resource_id=str(invitation.id),
                details={
                    'invitee_email': invitation.email,
                    'organization_id': str(invitation.organization.id),
                    'organization_name': invitation.organization.name
                }
            )
            
            return {
                'success': True,
                'message': 'Invitation cancelled successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel invitation: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to cancel invitation. Please try again later.'
            }
    
    def _can_invite_users(self, user: CustomUser, organization: Organization) -> bool:
        """Check if user can invite others to the organization"""
        # BlueVision admins can invite to any organization
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Publishers can invite to their own organization
        if user.role == 'publisher' and user.organization == organization:
            return True
        
        return False
    
    def _user_exists_in_organization(self, email: str, organization: Organization) -> bool:
        """Check if user with email already exists in organization"""
        return CustomUser.objects.filter(
            email__iexact=email,
            organization=organization,
            is_active=True
        ).exists()
    
    def _add_user_to_organization(self, user: CustomUser, organization: Organization, role: str) -> Dict[str, Any]:
        """Add user to organization with specified role"""
        try:
            # Check if user is already in another organization
            if user.organization and user.organization != organization:
                return {
                    'success': False,
                    'message': 'User is already a member of another organization'
                }
            
            # Update user organization and role
            user.organization = organization
            user.role = role
            user.save(update_fields=['organization', 'role'])
            
            return {
                'success': True,
                'message': f'User added to {organization.name} as {role}'
            }
            
        except Exception as e:
            logger.error(f"Failed to add user to organization: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to add user to organization'
            }
    
    def _can_manage_invitation(self, user: CustomUser, invitation: UserInvitation) -> bool:
        """Check if user can manage (cancel) the invitation"""
        # BlueVision admins can manage any invitation
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Inviter can cancel their own invitations
        if invitation.inviter == user:
            return True
        
        # Organization publishers can cancel invitations to their organization
        if (user.role == 'publisher' and 
            user.organization == invitation.organization):
            return True
        
        return False
    
    def _generate_invitation_token(self) -> str:
        """Generate a secure invitation token"""
        return secrets.token_urlsafe(32)


class PasswordResetService:
    """
    Service for managing password reset functionality (SRS R1.1.3)
    """
    
    def __init__(self):
        self.email_service = GmailSMTPService()
        self.audit_service = AuditService()
    
    def request_password_reset(self, email: str, ip_address: str = None, 
                              user_agent: str = None) -> Dict[str, Any]:
        """
        Request a password reset email
        
        Args:
            email: Email address requesting reset
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            Dictionary with request result
        """
        try:
            user = CustomUser.objects.filter(email__iexact=email, is_active=True).first()
            
            # Always return success message to prevent email enumeration
            success_message = 'If an account with this email exists, password reset instructions have been sent.'
            
            if not user:
                return {
                    'success': True,
                    'message': success_message
                }
            
            # Generate secure reset token
            reset_token = self._generate_reset_token()
            
            with transaction.atomic():
                # Invalidate any existing reset tokens for this user
                PasswordResetToken.objects.filter(
                    user=user,
                    used_at__isnull=True
                ).update(used_at=timezone.now())
                
                # Create new reset token
                token_obj = PasswordResetToken.objects.create(
                    user=user,
                    token=reset_token,
                    ip_address=ip_address,
                    user_agent=user_agent or ''
                )
                
                # Send reset email
                email_result = self.email_service.send_password_reset_email(
                    user=user,
                    reset_token=reset_token
                )
                
                if email_result.get('success'):
                    # Log the request
                    self.audit_service.log_user_action(
                        user=user,
                        action='password_reset_requested',
                        resource_type='password_reset',
                        resource_id=str(token_obj.id),
                        details={
                            'ip_address': ip_address,
                            'user_agent': user_agent
                        }
                    )
                    
                    return {
                        'success': True,
                        'message': success_message
                    }
                else:
                    # Email failed, cleanup token
                    token_obj.delete()
                    logger.error(f"Failed to send password reset email to {email}")
                    return {
                        'success': False,
                        'message': 'Failed to send password reset email. Please try again later.'
                    }
                    
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to process password reset request. Please try again later.'
            }
    
    def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a password reset token
        
        Args:
            token: Reset token to validate
            
        Returns:
            Dictionary with validation result
        """
        try:
            token_obj = PasswordResetToken.objects.filter(token=token).first()
            
            if not token_obj:
                return {
                    'success': False,
                    'message': 'Invalid reset token'
                }
            
            if not token_obj.is_valid:
                if token_obj.is_used:
                    message = 'This reset token has already been used'
                else:
                    message = 'This reset token has expired'
                    
                return {
                    'success': False,
                    'message': message
                }
            
            return {
                'success': True,
                'message': 'Reset token is valid',
                'user_id': str(token_obj.user.id)
            }
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to validate reset token'
            }
    
    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password using token
        
        Args:
            token: Reset token
            new_password: New password
            
        Returns:
            Dictionary with reset result
        """
        try:
            token_obj = PasswordResetToken.objects.filter(token=token).first()
            
            if not token_obj or not token_obj.is_valid:
                return {
                    'success': False,
                    'message': 'Invalid or expired reset token'
                }
            
            with transaction.atomic():
                user = token_obj.user
                
                # Update password
                user.set_password(new_password)
                user.failed_login_attempts = 0  # Reset login attempts
                user.save(update_fields=['password', 'failed_login_attempts'])
                
                # Mark token as used
                token_obj.mark_as_used()
                
                # Log the reset
                self.audit_service.log_user_action(
                    user=user,
                    action='password_reset_completed',
                    resource_type='password_reset',
                    resource_id=str(token_obj.id)
                )
                
                return {
                    'success': True,
                    'message': 'Password has been reset successfully'
                }
                
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to reset password. Please try again later.'
            }
    
    def _generate_reset_token(self) -> str:
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)