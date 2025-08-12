from django.utils import timezone
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
import uuid
import json
from typing import List, Dict, Optional, Tuple 
import hashlib
from datetime import timedelta
from ..models import CustomUser, UserSession, AuthenticationLog
from .access_control_service import AccessControlService
import logging

logger = logging.getLogger(__name__)

# Apply UUID JWT fix
try:
    from core.middleware.uuid_jwt_fix import apply_uuid_jwt_fix
    fix_applied = apply_uuid_jwt_fix()
    if fix_applied:
        logger.info("UUID JWT fix applied successfully")
    else:
        logger.warning("UUID JWT fix could not be applied")
except ImportError as e:
    logger.warning(f"UUID JWT fix import failed: {e}")
    pass


class UUIDSafeRefreshToken(RefreshToken):
    """Custom RefreshToken that handles UUID serialization properly"""
    
    @classmethod
    def for_user(cls, user):
        """Override to ensure UUID fields are converted to strings"""
        token = super().for_user(user)
        # Override the user_id with string version to prevent JSON serialization issues
        if hasattr(user, 'id') and isinstance(user.id, uuid.UUID):
            token.payload['user_id'] = str(user.id)
        return token
    
    def __setitem__(self, key, value):
        """Override to convert UUID values to strings"""
        if isinstance(value, uuid.UUID):
            value = str(value)
        super().__setitem__(key, value)


class AuthenticationService:
    """
    Enhanced authentication service with trust-aware access control.
    Provides comprehensive authentication, session management, and security features.
    """
    
    def __init__(self):
        self.access_control = AccessControlService()
    
    def authenticate_user(self, username: str, password: str, request=None, 
                         remember_device: bool = False, totp_code: str = None) -> Dict:
        """
        Authenticate user with comprehensive security checks and trust-aware permissions.
        
        Args:
            username: User's username
            password: User's password
            request: HTTP request object
            remember_device: Whether to remember this device
            totp_code: Two-factor authentication code (if applicable)
            
        Returns:
            dict: Authentication result with tokens, user info, and trust context
        """
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
                    auth_result['success'] = False
                    return auth_result
                
                # Validate TOTP code (placeholder - implement actual TOTP validation)
                if not self._validate_totp_code(user, totp_code):
                    self._handle_failed_login(user, ip_address, user_agent, 'Invalid 2FA code')
                    auth_result['message'] = 'Invalid two-factor authentication code'
                    auth_result['success'] = False
                    return auth_result
            
            # Check device trust
            is_trusted_device = user.is_device_trusted(device_fingerprint)
            # Note: Device trust checking only affects if we need verification, not authentication success
            if not is_trusted_device and remember_device:
                auth_result['requires_device_trust'] = True
                auth_result['message'] = 'Device trust verification required'
                # Continue with authentication but flag for device trust setup
            
            # Generate JWT tokens
            tokens = self._generate_tokens(user, request)
            
            # Create user session
            session = self._create_user_session(user, request, tokens, is_trusted_device)
            
            # Get user permissions and accessible organizations
            permissions = list(self.access_control.get_user_permissions(user))
            accessible_orgs = self._format_accessible_organizations(user)
            
            # Get trust context
            trust_context = self._get_user_trust_context(user)
            
            # Update last_login and reset failed login attempts on successful authentication
            user.last_login = timezone.now()
            if user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.save(update_fields=['failed_login_attempts', 'last_login'])
            else:
                user.save(update_fields=['last_login'])
            
            # Log successful authentication
            self._log_successful_authentication(user, ip_address, user_agent, session.id, is_trusted_device)
            
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
            
            # Add device to trusted list if requested and authentication successful
            if remember_device and not is_trusted_device:
                self._add_trusted_device(user, device_fingerprint, user_agent)
            
            # Ensure all UUID objects are converted to strings in the final result
            auth_result = self._ensure_json_serializable(auth_result)
            return auth_result
            
        except Exception as e:
            logger.error(f"Authentication error for {username}: {str(e)}")
            auth_result['message'] = 'Authentication system error'
            # Ensure error result is also JSON serializable
            auth_result = self._ensure_json_serializable(auth_result)
            return auth_result
    
    def _format_user_info(self, user: CustomUser) -> Dict:
        """Format user information for API responses, ensuring UUIDs are strings."""
        profile_info = {}
        try:
            profile = user.profile
            profile_info = {
                'bio': profile.bio,
                'department': profile.department,
                'job_title': profile.job_title,
                'phone': profile.phone_number,
                'email_notifications': profile.email_notifications,
                'threat_alerts': profile.threat_alerts,
                'security_notifications': profile.security_notifications,
                'profile_visibility': profile.profile_visibility,
            }
        except UserProfile.DoesNotExist:
            pass

        user_info = {
            'id': str(user.id),  # Ensure UUID is a string
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
                'id': str(user.organization.id),  # Ensure UUID is a string
                'name': user.organization.name,
                'domain': user.organization.domain,
                'is_publisher': user.organization.is_publisher,
            }
        else:
            user_info['organization'] = None
            
        return user_info

    def _format_accessible_organizations(self, user: CustomUser) -> List[Dict]:
        """Format accessible organizations for API responses, ensuring UUIDs are strings."""
        accessible_orgs = self.access_control.get_accessible_organizations(user)
        
        formatted_orgs = [
            {
                'id': str(org.id),  # Ensure UUID is a string
                'name': org.name,
                'domain': org.domain,
                'is_publisher': org.is_publisher,
                'is_verified': org.is_verified,
                'is_active': org.is_active,
            }
            for org in accessible_orgs
        ]
        return formatted_orgs

    def _get_user_trust_context(self, user: CustomUser) -> Dict:
        """Get user's trust context, ensuring UUIDs are strings."""
        try:
            from core_ut.trust.models import TrustRelationship
            
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
            
            can_manage_trust = user.role in ['admin', 'BlueVisionAdmin', 'publisher']
            
            return {
                'organization_id': str(user.organization.id),
                'organization_name': user.organization.name,
                'outgoing_trust_relationships': outgoing_relationships,
                'incoming_trust_relationships': incoming_relationships,
                'can_manage_trust': can_manage_trust,
                'trust_aware_access': True,
                'trust_metrics': {
                    'total_relationships': outgoing_relationships + incoming_relationships,
                    'bidirectional_relationships': min(outgoing_relationships, incoming_relationships)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user trust context: {str(e)}")
            # Return basic context on error instead of empty dict
            return {
                'organization_id': str(user.organization.id) if user.organization else None,
                'organization_name': user.organization.name if user.organization else None,
                'outgoing_trust_relationships': 0,
                'incoming_trust_relationships': 0,
                'can_manage_trust': False,
                'trust_aware_access': False,
                'error': 'Failed to load complete trust context'
            }
    
    def _validate_totp_code(self, user: CustomUser, totp_code: str) -> bool:
        """
        Validate TOTP code for two-factor authentication
        
        Args:
            user: User attempting authentication
            totp_code: TOTP code provided by user
            
        Returns:
            bool: True if code is valid
        """
        # Placeholder implementation - replace with actual TOTP validation
        # This would typically use libraries like pyotp
        try:
            import pyotp
            totp = pyotp.TOTP(user.two_factor_secret)
            return totp.verify(totp_code, valid_window=1)
        except ImportError:
            # Fallback for testing - accept any 6-digit code
            return len(totp_code) == 6 and totp_code.isdigit()
    
    def _add_trusted_device(self, user: CustomUser, device_fingerprint: str, user_agent: str) -> None:
        """Add device to user's trusted devices list"""
        try:
            device_name = self._extract_device_name(user_agent)
            user.add_trusted_device(device_fingerprint, device_name)
            
            AuthenticationLog.log_authentication_event(
                user=user,
                action='trusted_device_added',
                ip_address='127.0.0.1',
                user_agent=user_agent,
                success=True,
                additional_data={
                    'device_fingerprint': device_fingerprint[:8] + '...',
                    'device_name': device_name
                }
            )
            
            logger.info(f"Added trusted device for user {user.username}")
            
        except Exception as e:
            logger.error(f"Error adding trusted device: {str(e)}")
    
    def _extract_device_name(self, user_agent: str) -> str:
        """Extract a human-readable device name from user agent"""
        if not user_agent:
            return 'Unknown Device'
        
        user_agent_lower = user_agent.lower()
        
        # Detect common browsers
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
    
    def refresh_token(self, refresh_token: str, request=None) -> Dict:
        """
        Refresh JWT access token with trust context validation
        
        Args:
            refresh_token: JWT refresh token
            request: HTTP request object
            
        Returns:
            dict: New tokens or error
        """
        try:
            token = RefreshToken(refresh_token)
            user_id = token['user_id']
            user = CustomUser.objects.select_related('organization').get(id=user_id)
            
            # Validate user and organization status
            if not user.is_active:
                return {'success': False, 'message': 'User account is inactive'}
            
            if not user.organization.is_active:
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
            
            # Get updated trust context
            trust_context = self._get_user_trust_context(user)
            permissions = list(self.access_control.get_user_permissions(user))
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
            ip_address, user_agent = self._get_client_info(request)
            AuthenticationLog.log_authentication_event(
                user=None,
                action='token_refresh',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason=str(e)
            )
            
            return {'success': False, 'message': 'Invalid refresh token'}
    
    def logout_user(self, user: CustomUser, session_id: str = None, request=None) -> Dict:
        """
        Logout user and invalidate session(s)
        
        Args:
            user: User to logout
            session_id: Specific session to logout (optional)
            request: HTTP request object
            
        Returns:
            dict: Logout result
        """
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
            logger.error(f"Logout error: {str(e)}")
            return {'success': False, 'message': f'Logout failed: {str(e)}'}
    
    def verify_token(self, token: str, request=None) -> Dict:
        """
        Verify JWT token and return user info with trust context
        
        Args:
            token: JWT access token
            request: HTTP request object
            
        Returns:
            dict: Verification result with user info and trust context
        """
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = CustomUser.objects.select_related('organization').get(id=user_id)
            
            # Check if user is still active
            if not user.is_active:
                return {'success': False, 'message': 'User account is inactive'}
            
            # Check if organization is still active
            if not user.organization.is_active:
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
            permissions = list(self.access_control.get_user_permissions(user))
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
            
        except (TokenError, CustomUser.DoesNotExist) as e:
            return {'success': False, 'message': 'Invalid token'}
    
    def _ensure_json_serializable(self, obj):
        """Convert UUID and other non-serializable objects to JSON-safe formats"""
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        return obj
    
    def _generate_tokens(self, user: CustomUser, request=None) -> Dict:
        """Generate JWT access and refresh tokens with custom claims"""
        try:
            # Use the patched RefreshToken.for_user method
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims using the UUID-safe setitem method
            refresh['role'] = getattr(user, 'role', 'viewer')
            refresh['organization'] = user.organization.name if user.organization else None
            refresh['organization_id'] = str(user.organization.id) if user.organization else None
            refresh['is_publisher'] = getattr(user, 'is_publisher', False)
            refresh['is_verified'] = getattr(user, 'is_verified', True)
            
            # Create access token from refresh token
            access_token = refresh.access_token
            access_token['role'] = getattr(user, 'role', 'viewer')
            access_token['organization'] = user.organization.name if user.organization else None
            access_token['organization_id'] = str(user.organization.id) if user.organization else None
            access_token['is_publisher'] = getattr(user, 'is_publisher', False)
            
            logger.info(f"Successfully generated tokens for user {user.username}")
            
        except Exception as token_error:
            logger.error(f"Token generation error: {str(token_error)}")
            logger.error(f"User object: {user}, User ID: {user.id}, User type: {type(user.id)}")
            logger.error(f"Authentication error for {user.username}: {str(token_error)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to generate JWT tokens: {str(token_error)}")
        
        return {
            'access': str(access_token),
            'refresh': str(refresh),
            'access_expires': (timezone.now() + 
                             timedelta(seconds=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())).isoformat(),
            'refresh_expires': (timezone.now() + 
                              timedelta(seconds=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())).isoformat()
        }
    
    def _create_user_session(self, user: CustomUser, request, tokens: Dict, is_trusted_device: bool = False) -> UserSession:
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
    
    def _get_client_info(self, request) -> Tuple[str, str]:
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
    
    def _create_device_fingerprint(self, request) -> str:
        """Create device fingerprint for trusted device tracking"""
        if request is None:
            return 'unknown_device'
        
        fingerprint_data = {
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
            'accept_encoding': request.META.get('HTTP_ACCEPT_ENCODING', ''),
        }
        
        import json
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True, default=str)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    def _handle_failed_login(self, user: CustomUser, ip_address: str, user_agent: str, reason: str) -> None:
        """Handle failed login attempt with account locking"""
        user.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.lock_account(duration_minutes=15)
            logger.warning(f"Account locked for user {user.username} after {user.failed_login_attempts} failed attempts")
        
        user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
        
        self._log_failed_authentication(user, user.username, ip_address, user_agent, reason)
    
    def _log_successful_authentication(self, user: CustomUser, ip_address: str, user_agent: str, 
                                     session_id: str, is_trusted_device: bool) -> None:
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
    
    def _log_failed_authentication(self, user: Optional[CustomUser], username: str, 
                                 ip_address: str, user_agent: str, reason: str) -> None:
        """Log failed authentication attempt"""
        # Safely get organization name
        organization_name = None
        if user and hasattr(user, 'organization') and user.organization:
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
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = UserSession.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        
        count = expired_sessions.count()
        expired_sessions.update(is_active=False)
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")
        
        return count
    
    def _ensure_json_serializable(self, obj):
        """
        Recursively convert any UUID objects to strings to ensure JSON serialization works.
        This is a safety net to prevent UUID serialization errors.
        """
        import uuid
        import json
        
        def convert_uuids(item):
            if isinstance(item, uuid.UUID):
                return str(item)
            elif isinstance(item, dict):
                return {key: convert_uuids(value) for key, value in item.items()}
            elif isinstance(item, list):
                return [convert_uuids(value) for value in item]
            elif isinstance(item, tuple):
                return tuple(convert_uuids(value) for value in item)
            else:
                return item
        
        try:
            # Convert any UUID objects to strings
            converted_obj = convert_uuids(obj)
            # Test JSON serialization to make sure it works
            json.dumps(converted_obj, default=str)
            return converted_obj
        except Exception as e:
            logger.warning(f"Failed to ensure JSON serialization: {str(e)}")
            # Fallback: convert everything to string using default=str
            return json.loads(json.dumps(obj, default=str))
    
    def get_user_sessions(self, user: CustomUser) -> list:
        """Get active sessions for a user"""
        sessions = UserSession.objects.filter(
            user=user,
            is_active=True
        ).order_by('-created_at')
        
        session_list = []
        for session in sessions:
            session_list.append({
                'id': str(session.id),
                'device_info': session.device_info,
                'ip_address': session.ip_address,
                'is_trusted_device': session.is_trusted_device,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'is_current': False  # This would need to be determined by the calling code
            })
        
        return session_list
    
    def revoke_session(self, user: CustomUser, session_id: str) -> bool:
        """Revoke a specific user session"""
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=user,
                is_active=True
            )
            session.deactivate()
            
            AuthenticationLog.log_authentication_event(
                user=user,
                action='session_revoked',
                ip_address='127.0.0.1',
                user_agent='System',
                success=True,
                additional_data={'revoked_session_id': session_id}
            )
            
            logger.info(f"Session {session_id} revoked for user {user.username}")
            return True
            
        except UserSession.DoesNotExist:
            return False

