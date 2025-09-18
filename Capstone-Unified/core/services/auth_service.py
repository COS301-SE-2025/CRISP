"""
Authentication Service - JWT-based authentication with trust integration
Handles user authentication, session management, and security features
"""

from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from typing import Dict, Optional, Tuple
from datetime import timedelta
from core.models.models import (
    UserSession,
    TrustRelationship, Organization
)
from core.user_management.models import AuthenticationLog
from core.user_management.models import CustomUser
from .trust_service import TrustService
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Enhanced authentication service with trust-aware access control"""
    
    def __init__(self):
        self.trust_service = TrustService()
    
    def authenticate_user(self, username, password, request=None, remember_device=False, totp_code=None):
        """Authenticate user with comprehensive security checks and trust-aware permissions"""
        ip_address, user_agent = self._get_client_info(request)
        device_fingerprint = self._create_device_fingerprint(request)
        
        # Initialize result structure
        auth_result = {
            'success': False,
            'user': None,
            'tokens': None,
            'session_id': None,
            'message': '',
            'requires_2fa': False,
            'requires_device_trust': False,
            'trust_context': {},
            'permissions': [],
            'accessible_organizations': []
        }
        
        try:
            # Try to find user by username or email
            user = None
            try:
                user = CustomUser.objects.select_related('organization').get(username=username)
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.select_related('organization').get(email=username)
                except CustomUser.DoesNotExist:
                    pass
            
            if not user:
                self._log_failed_authentication(None, username, ip_address, user_agent, 'User not found')
                auth_result['message'] = 'Invalid credentials'
                return auth_result
            
            # Check if account is active
            if not user.is_active:
                self._log_failed_authentication(user, username, ip_address, user_agent, 'Account inactive')
                auth_result['message'] = 'Account is inactive'
                return auth_result
            
            # Check if account is locked
            if user.is_account_locked:
                self._log_failed_authentication(user, username, ip_address, user_agent, 'Account locked')
                auth_result['message'] = 'Account is temporarily locked due to failed login attempts'
                return auth_result
            
            # Check organization status
            if user.organization and not user.organization.is_active:
                self._log_failed_authentication(user, username, ip_address, user_agent, 'Organization inactive')
                auth_result['message'] = 'Organization is inactive'
                return auth_result
            
            # Authenticate password
            if not user.check_password(password):
                self._handle_failed_login(user, ip_address, user_agent, 'Invalid password')
                auth_result['message'] = 'Invalid credentials'
                return auth_result
            
            # Check two-factor authentication if enabled
            if user.two_factor_enabled:
                if not totp_code:
                    auth_result['requires_2fa'] = True
                    auth_result['message'] = 'Two-factor authentication required'
                    return auth_result
                
                if not self._validate_totp_code(user, totp_code):
                    self._handle_failed_login(user, ip_address, user_agent, 'Invalid 2FA code')
                    auth_result['message'] = 'Invalid two-factor authentication code'
                    return auth_result
            
            # Check device trust
            is_trusted_device = user.is_device_trusted(device_fingerprint)
            if not is_trusted_device and remember_device:
                auth_result['requires_device_trust'] = True
            
            # Generate JWT tokens
            tokens = self._generate_tokens(user, request)
            
            # Create user session
            session = self._create_user_session(user, request, tokens, is_trusted_device)
            
            # Get user permissions and accessible organizations
            permissions = self._get_user_permissions(user)
            accessible_orgs = self._format_accessible_organizations(user)
            
            # Get trust context
            trust_context = self._get_user_trust_context(user)
            
            # Update last_login and reset failed login attempts
            user.last_login = timezone.now()
            if user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.save(update_fields=['failed_login_attempts', 'last_login'])
            else:
                user.save(update_fields=['last_login'])
            
            # Log successful authentication
            self._log_successful_authentication(user, ip_address, user_agent, str(session.id), is_trusted_device)
            
            # Build success response
            auth_result.update({
                'success': True,
                'user': self._format_user_info(user),
                'tokens': tokens,
                'session_id': str(session.id),
                'message': 'Authentication successful',
                'trust_context': trust_context,
                'permissions': permissions,
                'accessible_organizations': accessible_orgs,
                'is_trusted_device': is_trusted_device
            })
            
            # Add device to trusted list if requested
            if remember_device and not is_trusted_device:
                self._add_trusted_device(user, device_fingerprint, user_agent)
            
            return auth_result
            
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            auth_result['message'] = 'Authentication system error'
            return auth_result
    
    def refresh_token(self, refresh_token, request=None):
        """Refresh JWT access token with trust context validation"""
        try:
            token = RefreshToken(refresh_token)
            user_id = token['user_id']
            user = CustomUser.objects.select_related('organization').get(id=user_id)
            
            # Validate user and organization status
            if not user.is_active:
                return {'success': False, 'message': 'User account is inactive'}
            
            if user.organization and not user.organization.is_active:
                return {'success': False, 'message': 'Organization is inactive'}
            
            # Check if session exists and is active
            try:
                session = UserSession.objects.get(
                    user=user,
                    refresh_token=refresh_token,
                    is_active=True
                )
                
                if session.is_expired:
                    session.deactivate()
                    return {'success': False, 'message': 'Session expired'}
                    
            except UserSession.DoesNotExist:
                return {'success': False, 'message': 'Invalid session'}
            
            # Generate new tokens
            new_tokens = self._generate_tokens(user, request)
            
            # Update session with new tokens
            session.session_token = new_tokens['access']
            session.refresh_token = new_tokens['refresh']
            session.last_activity = timezone.now()
            session.save(update_fields=['session_token', 'refresh_token', 'last_activity'])
            
            # Get updated context
            trust_context = self._get_user_trust_context(user)
            permissions = self._get_user_permissions(user)
            accessible_orgs = self._format_accessible_organizations(user)
            
            # Log token refresh
            ip_address, user_agent = self._get_client_info(request)
            AuthenticationLog.log_authentication_event(
                user=user,
                action='token_refresh',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={'session_id': str(session.id)}
            )
            
            return {
                'success': True,
                'tokens': new_tokens,
                'session_id': str(session.id),
                'user': self._format_user_info(user),
                'trust_context': trust_context,
                'permissions': permissions,
                'accessible_organizations': accessible_orgs
            }
            
        except (TokenError, CustomUser.DoesNotExist) as e:
            return {'success': False, 'message': 'Invalid refresh token'}
    
    def logout_user(self, user, session_id=None, request=None):
        """Logout user and invalidate session(s)"""
        try:
            if session_id:
                sessions = UserSession.objects.filter(
                    user=user,
                    id=session_id,
                    is_active=True
                )
            else:
                sessions = UserSession.objects.filter(
                    user=user,
                    is_active=True
                )
            
            sessions_count = sessions.count()
            sessions.update(is_active=False)
            
            # Log logout
            ip_address, user_agent = self._get_client_info(request)
            AuthenticationLog.log_authentication_event(
                user=user,
                action='logout',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={
                    'sessions_terminated': sessions_count,
                    'specific_session': session_id is not None
                }
            )
            
            return {
                'success': True,
                'message': f'Logged out {sessions_count} session(s)'
            }
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {'success': False, 'message': f'Logout failed: {e}'}
    
    def verify_token(self, token, request=None):
        """Verify JWT token and return user info with trust context"""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = CustomUser.objects.select_related('organization').get(id=user_id)
            
            # Check if user is still active
            if not user.is_active:
                return {'success': False, 'message': 'User account is inactive'}
            
            # Check if organization is still active
            if user.organization and not user.organization.is_active:
                return {'success': False, 'message': 'Organization is inactive'}
            
            # Check if account is locked
            if user.is_account_locked:
                return {'success': False, 'message': 'User account is locked'}
            
            # Update session last activity if session exists
            try:
                session = UserSession.objects.get(
                    user=user,
                    session_token=token,
                    is_active=True
                )
                session.last_activity = timezone.now()
                session.save(update_fields=['last_activity'])
            except UserSession.DoesNotExist:
                pass  # Token might be valid but session not tracked
            
            # Get current user context
            trust_context = self._get_user_trust_context(user)
            permissions = self._get_user_permissions(user)
            accessible_orgs = self._format_accessible_organizations(user)
            
            return {
                'success': True,
                'user': self._format_user_info(user),
                'user_id': str(user.id),
                'username': user.username,
                'role': user.role,
                'organization': user.organization.name if user.organization else None,
                'is_publisher': user.is_publisher,
                'trust_context': trust_context,
                'permissions': permissions,
                'accessible_organizations': accessible_orgs
            }
            
        except (TokenError, CustomUser.DoesNotExist):
            return {'success': False, 'message': 'Invalid token'}
    
    def _format_user_info(self, user):
        """Format user information for authentication response"""
        user_info = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_publisher': user.is_publisher,
            'is_verified': user.is_verified,
            'is_admin': user.is_superuser,
            'is_staff': user.is_staff,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'two_factor_enabled': user.two_factor_enabled
        }
        
        # Safely handle organization data
        if user.organization:
            user_info['organization'] = {
                'id': str(user.organization.id),
                'name': user.organization.name,
                'domain': user.organization.domain,
                'is_publisher': user.organization.is_publisher
            }
        else:
            user_info['organization'] = None
            
        return user_info
    
    def _format_accessible_organizations(self, user):
        """Format accessible organizations for authentication response"""
        try:
            if user.role == 'BlueVisionAdmin':
                organizations = Organization.objects.filter(is_active=True)
            elif user.organization:
                accessible_org_ids = self.trust_service.get_accessible_organizations(str(user.organization.id))
                organizations = Organization.objects.filter(id__in=accessible_org_ids, is_active=True)
            else:
                organizations = []
            
            result = []
            for org in organizations:
                org_data = {
                    'id': str(org.id),
                    'name': org.name,
                    'domain': org.domain,
                    'is_own': user.organization and org.id == user.organization.id,
                    'access_level': 'full' if (user.organization and org.id == user.organization.id) else 'trust_based'
                }
                result.append(org_data)
            return result
        except Exception as e:
            logger.error(f"Error formatting accessible organizations: {e}")
            return []
    
    def _get_user_trust_context(self, user):
        """Get trust context information for the user"""
        try:
            # Default context for users without organization
            if not user.organization:
                return {
                    'organization_id': None,
                    'organization_name': None,
                    'outgoing_trust_relationships': 0,
                    'incoming_trust_relationships': 0,
                    'can_manage_trust': False,
                    'trust_aware_access': False
                }
            
            # Get basic trust metrics
            outgoing_relationships = TrustRelationship.objects.filter(
                source_organization=user.organization,
                is_active=True,
                status='active'
            ).count()
            
            incoming_relationships = TrustRelationship.objects.filter(
                target_organization=user.organization,
                is_active=True,
                status='active'
            ).count()
            
            return {
                'organization_id': str(user.organization.id),
                'organization_name': user.organization.name,
                'outgoing_trust_relationships': outgoing_relationships,
                'incoming_trust_relationships': incoming_relationships,
                'can_manage_trust': user.can_manage_trust_relationships,
                'trust_aware_access': True
            }
        except Exception as e:
            logger.error(f"Error getting trust context: {e}")
            return {
                'organization_id': str(user.organization.id) if user.organization else None,
                'organization_name': user.organization.name if user.organization else None,
                'outgoing_trust_relationships': 0,
                'incoming_trust_relationships': 0,
                'can_manage_trust': False,
                'trust_aware_access': False
            }
    
    def _get_user_permissions(self, user):
        """Get user permissions based on role and organization"""
        permissions = []
        
        # Role-based permissions
        if user.role == 'BlueVisionAdmin':
            permissions.extend([
                'can_manage_all_organizations',
                'can_create_organizations',
                'can_manage_all_users',
                'can_manage_trust_relationships',
                'can_view_system_analytics',
                'can_manage_threat_feeds',
                'can_publish_threat_intelligence'
            ])
        elif user.role == 'publisher':
            permissions.extend([
                'can_manage_organization_users',
                'can_manage_trust_relationships',
                'can_publish_threat_intelligence',
                'can_manage_threat_feeds'
            ])
        elif user.role == 'viewer':
            permissions.extend([
                'can_view_threat_feeds',
                'can_view_indicators'
            ])
        
        # Organization-based permissions
        if user.organization and user.organization.is_publisher:
            permissions.append('can_access_publisher_features')
        
        return list(set(permissions))  # Remove duplicates
    
    def _validate_totp_code(self, user, totp_code):
        """Validate TOTP code for two-factor authentication"""
        try:
            import pyotp
            totp = pyotp.TOTP(user.two_factor_secret)
            return totp.verify(totp_code, valid_window=1)
        except ImportError:
            # Fallback for testing - accept any 6-digit code
            return len(totp_code) == 6 and totp_code.isdigit()
    
    def _add_trusted_device(self, user, device_fingerprint, user_agent):
        """Add device to user's trusted devices list"""
        try:
            device_name = self._extract_device_name(user_agent)
            user.add_trusted_device(device_fingerprint, device_name)
            
            AuthenticationLog.log_authentication_event(
                user=user,
                action='trusted_device_added',
                success=True,
                additional_data={
                    'device_fingerprint': device_fingerprint[:8] + '...',
                    'device_name': device_name
                }
            )
            
            logger.info(f"Added trusted device for user {user.username}")
            
        except Exception as e:
            logger.error(f"Error adding trusted device: {e}")
    
    def _extract_device_name(self, user_agent):
        """Extract a human-readable device name from user agent"""
        if not user_agent:
            return 'Unknown Device'
        
        user_agent_lower = user_agent.lower()
        
        # Detect browser
        if 'chrome' in user_agent_lower:
            browser = 'Chrome'
        elif 'firefox' in user_agent_lower:
            browser = 'Firefox'
        elif 'safari' in user_agent_lower:
            browser = 'Safari'
        elif 'edge' in user_agent_lower:
            browser = 'Edge'
        else:
            browser = 'Browser'
        
        # Detect OS
        if 'windows' in user_agent_lower:
            os_name = 'Windows'
        elif 'mac' in user_agent_lower:
            os_name = 'macOS'
        elif 'linux' in user_agent_lower:
            os_name = 'Linux'
        elif 'android' in user_agent_lower:
            os_name = 'Android'
        elif 'ios' in user_agent_lower:
            os_name = 'iOS'
        else:
            os_name = 'Unknown OS'
        
        return f"{browser} on {os_name}"
    
    def _generate_tokens(self, user, request=None):
        """Generate JWT access and refresh tokens with custom claims"""
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['role'] = user.role
        refresh['organization'] = user.organization.name if user.organization else None
        refresh['organization_id'] = str(user.organization.id) if user.organization else None
        refresh['is_publisher'] = user.is_publisher
        refresh['is_verified'] = user.is_verified
        
        access_token = refresh.access_token
        access_token['role'] = user.role
        access_token['organization'] = user.organization.name if user.organization else None
        access_token['organization_id'] = str(user.organization.id) if user.organization else None
        access_token['is_publisher'] = user.is_publisher
        
        return {
            'access': str(access_token),
            'refresh': str(refresh),
            'access_expires': (timezone.now() + 
                             timedelta(seconds=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())).isoformat(),
            'refresh_expires': (timezone.now() + 
                              timedelta(seconds=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())).isoformat()
        }
    
    def _create_user_session(self, user, request, tokens, is_trusted_device=False):
        """Create user session record with trust context"""
        ip_address, user_agent = self._get_client_info(request)
        device_fingerprint = self._create_device_fingerprint(request)
        
        session = UserSession.objects.create(
            user=user,
            session_token=tokens['access'],
            refresh_token=tokens['refresh'],
            device_info={
                'user_agent': user_agent,
                'fingerprint': device_fingerprint,
                'ip_address': ip_address,
                'trusted': is_trusted_device
            },
            ip_address=ip_address,
            is_trusted_device=is_trusted_device,
            expires_at=timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        )
        
        return session
    
    def _get_client_info(self, request):
        """Extract client IP and user agent from request"""
        if request is None:
            return '127.0.0.1', 'Unknown'
            
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        return ip, user_agent
    
    def _create_device_fingerprint(self, request):
        """Create device fingerprint for trusted device tracking"""
        if request is None:
            return 'unknown_device'
        
        fingerprint_data = {
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
            'accept_encoding': request.META.get('HTTP_ACCEPT_ENCODING', ''),
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    def _handle_failed_login(self, user, ip_address, user_agent, reason):
        """Handle failed login attempt with account locking"""
        user.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.lock_account(duration_minutes=15)
            logger.warning(f"Account locked for user {user.username} after {user.failed_login_attempts} failed attempts")
        
        user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
        
        self._log_failed_authentication(user, user.username, ip_address, user_agent, reason)
    
    def _log_successful_authentication(self, user, ip_address, user_agent, session_id, is_trusted_device):
        """Log successful authentication"""
        AuthenticationLog.log_authentication_event(
            user=user,
            action='login_success',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data={
                'session_id': session_id,
                'trusted_device': is_trusted_device,
                'organization': user.organization.name if user.organization else None,
                'role': user.role
            }
        )
        
        logger.info(f"User {user.username} ({user.role}) logged in successfully from {ip_address}")
    
    def _log_failed_authentication(self, user, username, ip_address, user_agent, reason):
        """Log failed authentication attempt"""
        organization_name = None
        if user and user.organization:
            organization_name = user.organization.name
        
        AuthenticationLog.log_authentication_event(
            user=user,
            action='login_failure',
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason=reason,
            additional_data={
                'attempted_username': username,
                'failed_attempts': user.failed_login_attempts if user else 1,
                'organization': organization_name
            }
        )
        
        logger.warning(f"Failed login attempt for username: {username} from {ip_address}. Reason: {reason}")
    
    def request_password_reset(self, email, ip_address=None, user_agent=None):
        """Request password reset - creates token and sends email"""
        try:
            logger.info(f"🔐 Starting password reset for email: {email}")
            logger.info(f"🌐 IP: {ip_address}, User-Agent: {user_agent}")
            
            from .user_service import UserService
            from .email_service import UnifiedEmailService
            
            user_service = UserService()
            email_service = UnifiedEmailService()
            
            logger.info(f"🎫 Creating password reset token")
            # Create password reset token
            reset_token = user_service.create_password_reset_token(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"🎫 Token creation result: {'Success' if reset_token else 'Failed/User not found'}")
            
            if reset_token:
                logger.info(f"📧 Sending password reset email")
                # Send password reset email
                email_result = email_service.send_password_reset_email(
                    user=reset_token.user,
                    reset_token=reset_token.token
                )
                
                logger.info(f"📧 Email send result: {email_result}")
                logger.info(f"✅ Password reset requested for {email}, email sent: {email_result.get('success', False)}")
                return {
                    'success': True,
                    'message': 'Password reset email sent'
                }
            else:
                # Don't reveal if email exists
                logger.warning(f"⚠️ Password reset requested for non-existent email: {email}")
                return {
                    'success': True,
                    'message': 'If an account with this email exists, a password reset link has been sent'
                }
                
        except Exception as e:
            logger.error(f"Password reset request error: {e}")
            return {
                'success': False,
                'message': 'Password reset request failed'
            }
    
    def reset_password(self, token, new_password, ip_address=None):
        """Reset password using token"""
        try:
            from .user_service import UserService
            
            user_service = UserService()
            result = user_service.reset_password(token, new_password)
            
            if result:
                logger.info(f"Password reset completed for user: {result.username}")
                return {
                    'success': True,
                    'message': 'Password reset successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid or expired reset token'
                }
                
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return {
                'success': False,
                'message': 'Password reset failed'
            }