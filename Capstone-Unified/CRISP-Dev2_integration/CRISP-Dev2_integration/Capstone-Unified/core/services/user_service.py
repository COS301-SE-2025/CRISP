"""
User Service - User management and authentication functionality
Handles user creation, authentication, profiles, and security features
"""

from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from core.models.models import (
    CustomUser, Organization, UserProfile, AuthenticationLog,
    UserSession, TrustedDevice, UserInvitation, PasswordResetToken
)
from datetime import timedelta
import secrets
import hashlib
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user management operations"""
    
    def create_user(self, username, email, password, organization_id, 
                   role='viewer', created_by=None, **extra_fields):
        """Create a new user with proper validation and setup"""
        try:
            with transaction.atomic():
                # Validate organization exists
                organization = Organization.objects.get(id=organization_id)
                
                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    organization=organization,
                    role=role,
                    **extra_fields
                )
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                # Log user creation
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='user_created',
                    success=True,
                    additional_data={
                        'created_by': created_by.username if created_by else 'System',
                        'organization': organization.name,
                        'role': role
                    }
                )
                
                logger.info(f"User created: {username} in {organization.name}")
                return user
                
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            raise
    
    def authenticate_user(self, username, password, ip_address=None, user_agent=None):
        """Authenticate user and log the attempt"""
        try:
            # Attempt authentication
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if account is locked
                if user.is_account_locked:
                    AuthenticationLog.log_authentication_event(
                        user=user,
                        action='login_failure',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        success=False,
                        failure_reason='Account locked'
                    )
                    raise ValidationError("Account is temporarily locked due to failed login attempts")
                
                # Check if account is active
                if not user.is_active:
                    AuthenticationLog.log_authentication_event(
                        user=user,
                        action='login_failure',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        success=False,
                        failure_reason='Account deactivated'
                    )
                    raise ValidationError("Account is deactivated")
                
                # Reset failed attempts on successful login
                if user.failed_login_attempts > 0:
                    user.failed_login_attempts = 0
                    user.save(update_fields=['failed_login_attempts'])
                
                # Log successful authentication
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='login_success',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                
                logger.info(f"Successful authentication: {username}")
                return user
            
            else:
                # Find user for failed attempt logging
                try:
                    user = CustomUser.objects.get(username=username)
                    # Increment failed attempts
                    user.failed_login_attempts += 1
                    
                    # Lock account if too many failed attempts (5 attempts)
                    if user.failed_login_attempts >= 5:
                        user.lock_account(duration_minutes=15)
                        failure_reason = 'Account locked due to multiple failed attempts'
                    else:
                        failure_reason = 'Invalid credentials'
                    
                    user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
                    
                    AuthenticationLog.log_authentication_event(
                        user=user,
                        action='login_failure',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        success=False,
                        failure_reason=failure_reason
                    )
                    
                except CustomUser.DoesNotExist:
                    # Log attempt with unknown user
                    AuthenticationLog.log_authentication_event(
                        user=None,
                        action='login_failure',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        success=False,
                        failure_reason='User not found',
                        additional_data={'attempted_username': username}
                    )
                
                logger.warning(f"Failed authentication attempt: {username}")
                raise ValidationError("Invalid username or password")
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            raise ValidationError("Authentication system error")
    
    def create_user_session(self, user, access_token, refresh_token, 
                           ip_address, device_info=None, expires_in=3600):
        """Create a new user session for JWT tracking"""
        try:
            # Check if device is trusted
            device_fingerprint = self._generate_device_fingerprint(device_info)
            is_trusted = user.is_device_trusted(device_fingerprint)
            
            # Create session
            session = UserSession.objects.create(
                user=user,
                session_token=access_token,
                refresh_token=refresh_token,
                device_info=device_info or {},
                ip_address=ip_address,
                is_trusted_device=is_trusted,
                expires_at=timezone.now() + timedelta(seconds=expires_in)
            )
            
            logger.info(f"Session created for user: {user.username}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
            raise
    
    def logout_user(self, user, session_token=None, ip_address=None, user_agent=None):
        """Logout user and invalidate session"""
        try:
            # Deactivate specific session if provided
            if session_token:
                UserSession.objects.filter(
                    user=user,
                    session_token=session_token,
                    is_active=True
                ).update(is_active=False)
            else:
                # Deactivate all sessions
                UserSession.objects.filter(
                    user=user,
                    is_active=True
                ).update(is_active=False)
            
            # Log logout
            AuthenticationLog.log_authentication_event(
                user=user,
                action='logout',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            logger.info(f"User logged out: {user.username}")
            
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise
    
    def create_user_invitation(self, email, organization, inviter, invited_role='viewer', message=''):
        """Create a user invitation to join an organization"""
        try:
            # Check if user already exists
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("User with this email already exists")
            
            # Check for existing pending invitation
            existing = UserInvitation.objects.filter(
                email=email,
                organization=organization,
                status='pending'
            ).first()
            
            if existing and not existing.is_expired:
                raise ValidationError("Pending invitation already exists for this email")
            
            # Generate secure token
            token = secrets.token_urlsafe(32)
            
            # Create invitation
            invitation = UserInvitation.objects.create(
                email=email,
                organization=organization,
                inviter=inviter,
                invited_role=invited_role,
                token=token,
                message=message
            )
            
            logger.info(f"User invitation created: {email} to {organization.name}")
            return invitation
            
        except Exception as e:
            logger.error(f"Error creating user invitation: {e}")
            raise
    
    def accept_invitation(self, token, username, password):
        """Accept a user invitation and create account"""
        try:
            with transaction.atomic():
                # Find and validate invitation
                invitation = UserInvitation.objects.get(token=token, status='pending')
                
                if invitation.is_expired:
                    raise ValidationError("Invitation has expired")
                
                # Create user account
                user = self.create_user(
                    username=username,
                    email=invitation.email,
                    password=password,
                    organization_id=invitation.organization.id,
                    role=invitation.invited_role,
                    is_verified=True  # Auto-verify invited users
                )
                
                # Accept invitation
                invitation.accept(user)
                
                logger.info(f"Invitation accepted: {username} joined {invitation.organization.name}")
                return user
                
        except UserInvitation.DoesNotExist:
            raise ValidationError("Invalid or expired invitation token")
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            raise
    
    def create_password_reset_token(self, email, ip_address=None, user_agent=None):
        """Create a password reset token for a user"""
        try:
            user = CustomUser.objects.get(email=email, is_active=True)
            
            # Invalidate existing tokens
            PasswordResetToken.objects.filter(
                user=user,
                used_at__isnull=True
            ).update(used_at=timezone.now())
            
            # Generate new token
            token = secrets.token_urlsafe(32)
            
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Log password reset request
            AuthenticationLog.log_authentication_event(
                user=user,
                action='password_reset',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            logger.info(f"Password reset token created for: {email}")
            return reset_token
            
        except CustomUser.DoesNotExist:
            # Don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return None
        except Exception as e:
            logger.error(f"Error creating password reset token: {e}")
            raise
    
    def reset_password(self, token, new_password):
        """Reset user password using a valid token"""
        try:
            with transaction.atomic():
                # Find and validate token
                reset_token = PasswordResetToken.objects.get(
                    token=token,
                    used_at__isnull=True
                )
                
                if not reset_token.is_valid:
                    raise ValidationError("Invalid or expired reset token")
                
                # Update password
                user = reset_token.user
                user.set_password(new_password)
                user.password_changed_at = timezone.now()
                user.failed_login_attempts = 0  # Reset failed attempts
                user.account_locked_until = None  # Unlock account
                user.save(update_fields=[
                    'password', 'password_changed_at', 
                    'failed_login_attempts', 'account_locked_until'
                ])
                
                # Mark token as used
                reset_token.mark_as_used()
                
                # Invalidate all user sessions
                UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
                
                # Log password change
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='password_change',
                    success=True
                )
                
                logger.info(f"Password reset completed for: {user.username}")
                return user
                
        except PasswordResetToken.DoesNotExist:
            raise ValidationError("Invalid or expired reset token")
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            raise
    
    def add_trusted_device(self, user, device_info, device_name=None):
        """Add a trusted device for a user"""
        try:
            device_fingerprint = self._generate_device_fingerprint(device_info)
            device_name = device_name or f"Device {timezone.now().strftime('%Y-%m-%d')}"
            
            # Create or update trusted device
            device, created = TrustedDevice.objects.get_or_create(
                user=user,
                device_fingerprint=device_fingerprint,
                defaults={
                    'device_name': device_name,
                    'device_type': device_info.get('type', 'unknown'),
                    'is_active': True
                }
            )
            
            if not created:
                device.last_used = timezone.now()
                device.is_active = True
                device.save(update_fields=['last_used', 'is_active'])
            
            # Log trusted device addition
            AuthenticationLog.log_authentication_event(
                user=user,
                action='trusted_device_added',
                success=True,
                additional_data={'device_name': device_name}
            )
            
            logger.info(f"Trusted device added for: {user.username}")
            return device
            
        except Exception as e:
            logger.error(f"Error adding trusted device: {e}")
            raise
    
    def _generate_device_fingerprint(self, device_info):
        """Generate a unique fingerprint for a device"""
        if not device_info:
            return 'unknown'
        
        # Create fingerprint from device characteristics
        fingerprint_data = f"{device_info.get('user_agent', '')}" \
                          f"{device_info.get('screen_resolution', '')}" \
                          f"{device_info.get('timezone', '')}" \
                          f"{device_info.get('language', '')}"
        
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]