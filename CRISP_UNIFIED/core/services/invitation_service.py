"""
User Invitation Service - User invitation and email integration
Handles sending and managing organization invitations
"""

import logging
import secrets
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from core.models.models import (
    CustomUser, Organization, UserInvitation, PasswordResetToken,
    AuthenticationLog
)
import logging

logger = logging.getLogger(__name__)

class UserInvitationService:
    """Service for managing user invitations with email integration"""
    
    def __init__(self):
        pass
    
    def send_invitation(self, inviter, organization, email, role='viewer', message=''):
        """Send a user invitation email"""
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
                
                # Log invitation creation
                AuthenticationLog.log_authentication_event(
                    user=inviter,
                    action='user_created',
                    success=True,
                    additional_data={
                        'action_type': 'invitation_sent',
                        'invited_email': email,
                        'organization_id': str(organization.id),
                        'invited_role': role,
                        'invitation_id': str(invitation.id)
                    }
                )
                
                logger.info(f"Invitation sent by {inviter.username} to {email} for {organization.name}")
                
                return {
                    'success': True,
                    'message': 'Invitation sent successfully',
                    'invitation_id': str(invitation.id),
                    'invitation_token': invitation_token,
                    'expires_at': invitation.expires_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error sending invitation: {e}")
            return {
                'success': False,
                'message': f'Failed to send invitation: {e}'
            }
    
    def accept_invitation(self, token, username, password, first_name='', last_name=''):
        """Accept a user invitation and create account"""
        try:
            with transaction.atomic():
                # Find and validate invitation
                try:
                    invitation = UserInvitation.objects.get(token=token, status='pending')
                except UserInvitation.DoesNotExist:
                    return {
                        'success': False,
                        'message': 'Invalid or expired invitation token'
                    }
                
                if invitation.is_expired:
                    return {
                        'success': False,
                        'message': 'Invitation has expired'
                    }
                
                # Check if username already exists
                if CustomUser.objects.filter(username=username).exists():
                    return {
                        'success': False,
                        'message': 'Username is already taken'
                    }
                
                # Create user account
                user = CustomUser.objects.create_user(
                    username=username,
                    email=invitation.email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    organization=invitation.organization,
                    role=invitation.invited_role,
                    is_verified=True,  # Auto-verify invited users
                    is_active=True
                )
                
                # Accept invitation
                invitation.accept(user)
                
                # Log invitation acceptance
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='user_created',
                    success=True,
                    additional_data={
                        'action_type': 'invitation_accepted',
                        'invitation_id': str(invitation.id),
                        'organization_id': str(invitation.organization.id),
                        'invited_by': invitation.inviter.username
                    }
                )
                
                logger.info(f"Invitation accepted: {username} joined {invitation.organization.name}")
                
                return {
                    'success': True,
                    'message': 'Account created successfully',
                    'user_id': str(user.id),
                    'username': user.username,
                    'organization': invitation.organization.name
                }
                
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            return {
                'success': False,
                'message': f'Failed to accept invitation: {e}'
            }
    
    def cancel_invitation(self, cancelling_user, invitation_id):
        """Cancel a pending invitation"""
        try:
            invitation = UserInvitation.objects.get(id=invitation_id, status='pending')
            
            # Check permissions
            if not self._can_cancel_invitation(cancelling_user, invitation):
                return {
                    'success': False,
                    'message': 'You do not have permission to cancel this invitation'
                }
            
            invitation.cancel()
            
            # Log invitation cancellation
            AuthenticationLog.log_authentication_event(
                user=cancelling_user,
                action='user_modified',
                success=True,
                additional_data={
                    'action_type': 'invitation_cancelled',
                    'invitation_id': str(invitation.id),
                    'invited_email': invitation.email,
                    'organization_id': str(invitation.organization.id)
                }
            )
            
            logger.info(f"Invitation cancelled by {cancelling_user.username} for {invitation.email}")
            
            return {
                'success': True,
                'message': 'Invitation cancelled successfully'
            }
            
        except UserInvitation.DoesNotExist:
            return {
                'success': False,
                'message': 'Invitation not found or already processed'
            }
        except Exception as e:
            logger.error(f"Error cancelling invitation: {e}")
            return {
                'success': False,
                'message': f'Failed to cancel invitation: {e}'
            }
    
    def list_organization_invitations(self, requesting_user, organization_id, status=None):
        """List invitations for an organization"""
        try:
            organization = Organization.objects.get(id=organization_id)
            
            # Check permissions
            if not self._can_view_invitations(requesting_user, organization):
                return {
                    'success': False,
                    'message': 'You do not have permission to view invitations for this organization'
                }
            
            # Filter invitations
            invitations = UserInvitation.objects.filter(organization=organization)
            
            if status:
                invitations = invitations.filter(status=status)
            
            invitations = invitations.order_by('-created_at')
            
            # Format results
            invitation_list = []
            for invitation in invitations:
                invitation_data = {
                    'id': str(invitation.id),
                    'email': invitation.email,
                    'invited_role': invitation.invited_role,
                    'status': invitation.status,
                    'created_at': invitation.created_at.isoformat(),
                    'expires_at': invitation.expires_at.isoformat(),
                    'inviter': {
                        'id': str(invitation.inviter.id),
                        'username': invitation.inviter.username,
                        'first_name': invitation.inviter.first_name,
                        'last_name': invitation.inviter.last_name
                    },
                    'is_expired': invitation.is_expired,
                    'message': invitation.message
                }
                
                if invitation.accepted_at:
                    invitation_data['accepted_at'] = invitation.accepted_at.isoformat()
                
                if invitation.accepted_by:
                    invitation_data['accepted_by'] = {
                        'id': str(invitation.accepted_by.id),
                        'username': invitation.accepted_by.username
                    }
                
                invitation_list.append(invitation_data)
            
            return {
                'success': True,
                'invitations': invitation_list,
                'total_count': len(invitation_list)
            }
            
        except Organization.DoesNotExist:
            return {
                'success': False,
                'message': 'Organization not found'
            }
        except Exception as e:
            logger.error(f"Error listing invitations: {e}")
            return {
                'success': False,
                'message': f'Failed to list invitations: {e}'
            }
    
    def get_invitation_details(self, token):
        """Get invitation details by token for acceptance page"""
        try:
            invitation = UserInvitation.objects.select_related(
                'organization', 'inviter'
            ).get(token=token, status='pending')
            
            if invitation.is_expired:
                return {
                    'success': False,
                    'message': 'Invitation has expired'
                }
            
            return {
                'success': True,
                'invitation': {
                    'id': str(invitation.id),
                    'email': invitation.email,
                    'invited_role': invitation.invited_role,
                    'organization': {
                        'id': str(invitation.organization.id),
                        'name': invitation.organization.name,
                        'domain': invitation.organization.domain,
                        'organization_type': invitation.organization.organization_type
                    },
                    'inviter': {
                        'first_name': invitation.inviter.first_name,
                        'last_name': invitation.inviter.last_name,
                        'username': invitation.inviter.username
                    },
                    'message': invitation.message,
                    'created_at': invitation.created_at.isoformat(),
                    'expires_at': invitation.expires_at.isoformat()
                }
            }
            
        except UserInvitation.DoesNotExist:
            return {
                'success': False,
                'message': 'Invalid or expired invitation token'
            }
        except Exception as e:
            logger.error(f"Error getting invitation details: {e}")
            return {
                'success': False,
                'message': f'Failed to get invitation details: {e}'
            }
    
    def cleanup_expired_invitations(self):
        """Clean up expired invitations"""
        try:
            expired_invitations = UserInvitation.objects.filter(
                status='pending',
                expires_at__lt=timezone.now()
            )
            
            count = expired_invitations.count()
            expired_invitations.update(status='expired')
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired invitations")
            
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired invitations: {e}")
            return 0
    
    def _can_invite_users(self, user, organization):
        """Check if user can invite others to the organization"""
        # BlueVision admins can invite to any organization
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Publishers can invite to their own organization
        if (user.role == 'publisher' and 
            user.organization and 
            user.organization.id == organization.id):
            return True
        
        return False
    
    def _can_cancel_invitation(self, user, invitation):
        """Check if user can cancel an invitation"""
        # BlueVision admins can cancel any invitation
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Inviter can cancel their own invitations
        if invitation.inviter.id == user.id:
            return True
        
        # Publishers can cancel invitations to their organization
        if (user.role == 'publisher' and 
            user.organization and 
            user.organization.id == invitation.organization.id):
            return True
        
        return False
    
    def _can_view_invitations(self, user, organization):
        """Check if user can view invitations for an organization"""
        # BlueVision admins can view all invitations
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Publishers can view invitations to their organization
        if (user.role == 'publisher' and 
            user.organization and 
            user.organization.id == organization.id):
            return True
        
        return False
    
    def _user_exists_in_organization(self, email, organization):
        """Check if user with email already exists in organization"""
        return CustomUser.objects.filter(
            email=email,
            organization=organization,
            is_active=True
        ).exists()
    
    def _generate_invitation_token(self):
        """Generate secure invitation token"""
        return secrets.token_urlsafe(32)