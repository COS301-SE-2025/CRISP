from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from typing import Dict, Optional, Tuple
import secrets
import hashlib
from datetime import timedelta
from ..models import CustomUser, UserSession, AuthenticationLog
from ..strategies.authentication_strategies import (
    AuthenticationContext, 
    StandardAuthenticationStrategy,
    TwoFactorAuthenticationStrategy,
    TrustedDeviceAuthenticationStrategy
)
from ..observers.auth_observers import auth_event_subject
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status


class AuthenticationService:
    """Core authentication service with JWT and security features"""
    
    def __init__(self):
        self.auth_context = AuthenticationContext(StandardAuthenticationStrategy())
    
    def authenticate_user(self, username: str, password: str, request=None, 
                         remember_device: bool = False, totp_code: str = None) -> Dict:
        """
        Authenticate user with comprehensive security checks
        
        Args:
            username: User's username
            password: User's password
            request: HTTP request object
            remember_device: Whether to remember this device
            totp_code: Two-factor authentication code (if applicable)
            
        Returns:
            dict: Authentication result with tokens and user info
        """
        # Determine authentication strategy based on user preferences
        try:
            user = CustomUser.objects.get(username=username)
            if user.two_factor_enabled:
                self.auth_context.set_strategy(TwoFactorAuthenticationStrategy())
        except CustomUser.DoesNotExist:
            pass  # Will be handled by strategy
        
        if remember_device:
            self.auth_context.set_strategy(TrustedDeviceAuthenticationStrategy())
        
        # Perform authentication
        auth_result = self.auth_context.authenticate(
            username=username,
            password=password,
            request=request,
            remember_device=remember_device,
            totp_code=totp_code
        )
        
        if not auth_result['success']:
            return auth_result
        
        user = auth_result['user']
        
        # Generate JWT tokens
        tokens = self._generate_tokens(user, request)
        
        # Create user session
        session = self._create_user_session(user, request, tokens)
        
        # Notify observers
        ip_address, user_agent = self._get_client_info(request)
        auth_event_subject.notify_observers(
            event_type='login_success',
            user=user,
            event_data={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'success': True,
                'additional_data': {
                    'session_id': str(session.id),
                    'trusted_device': not auth_result['requires_device_trust']
                }
            }
        )
        
        return {
            'success': True,
            'user': user,
            'tokens': tokens,
            'session_id': str(session.id),
            'message': 'Authentication successful',
            'requires_2fa': auth_result['requires_2fa'],
            'requires_device_trust': auth_result['requires_device_trust']
        }
    
    def refresh_token(self, refresh_token: str, request=None) -> Dict:
        """
        Refresh JWT access token
        
        Args:
            refresh_token: JWT refresh token
            request: HTTP request object
            
        Returns:
            dict: New tokens or error
        """
        try:
            # Verify refresh token
            token = RefreshToken(refresh_token)
            user_id = token['user_id']
            user = CustomUser.objects.get(id=user_id)
            
            # Check if session exists and is active
            try:
                session = UserSession.objects.get(
                    user=user,
                    refresh_token=refresh_token,
                    is_active=True
                )
                
                if session.is_expired:
                    session.deactivate()
                    return {
                        'success': False,
                        'message': 'Session expired'
                    }
                    
            except UserSession.DoesNotExist:
                return {
                    'success': False,
                    'message': 'Invalid session'
                }
            
            # Generate new tokens
            new_tokens = self._generate_tokens(user, request)
            
            # Update session with new tokens
            session.session_token = new_tokens['access']
            session.refresh_token = new_tokens['refresh']
            session.last_activity = timezone.now()
            session.save(update_fields=['session_token', 'refresh_token', 'last_activity'])
            
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
                'session_id': str(session.id)
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
            
            return {
                'success': False,
                'message': 'Invalid refresh token'
            }
    
    def logout_user(self, user: CustomUser, session_id: str = None, request=None) -> Dict:
        """
        Logout user and invalidate session
        
        Args:
            user: User to logout
            session_id: Specific session to logout (optional)
            request: HTTP request object
            
        Returns:
            dict: Logout result
        """
        try:
            if session_id:
                # Logout specific session
                sessions = UserSession.objects.filter(
                    user=user,
                    id=session_id,
                    is_active=True
                )
            else:
                # Logout all active sessions
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
            return {
                'success': False,
                'message': f'Logout failed: {str(e)}'
            }
    
    def verify_token(self, token: str, request=None) -> Dict:
        """
        Verify JWT token and return user info
        
        Args:
            token: JWT access token
            request: HTTP request object
            
        Returns:
            dict: Verification result with user info
        """
        try:
            # Verify token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = CustomUser.objects.get(id=user_id)
            
            # Check if user is still active
            if not user.is_active:
                return {
                    'success': False,
                    'message': 'User account is inactive'
                }
            
            # Check if account is locked
            if user.is_account_locked:
                return {
                    'success': False,
                    'message': 'User account is locked'
                }
            
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
            
            return {
                'success': True,
                'user': user,
                'user_id': str(user.id),
                'username': user.username,
                'role': user.role,
                'organization': user.organization.name if user.organization else None,
                'is_publisher': user.is_publisher
            }
            
        except (TokenError, CustomUser.DoesNotExist) as e:
            return {
                'success': False,
                'message': 'Invalid token'
            }
    
    def _generate_tokens(self, user: CustomUser, request=None) -> Dict:
        """Generate JWT access and refresh tokens"""
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['role'] = user.role
        refresh['organization'] = user.organization.name if user.organization else None
        refresh['is_publisher'] = user.is_publisher
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'access_expires': (timezone.now() + 
                             timedelta(seconds=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())).isoformat(),
            'refresh_expires': (timezone.now() + 
                              timedelta(seconds=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())).isoformat()
        }
    
    def _create_user_session(self, user: CustomUser, request, tokens: Dict) -> UserSession:
        """Create user session record"""
        ip_address, user_agent = self._get_client_info(request)
        device_fingerprint = self._create_device_fingerprint(request)
        
        session = UserSession.objects.create(
            user=user,
            session_token=tokens['access'],
            refresh_token=tokens['refresh'],
            device_info={
                'user_agent': user_agent,
                'fingerprint': device_fingerprint
            },
            ip_address=ip_address,
            is_trusted_device=device_fingerprint in user.trusted_devices,
            expires_at=timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        )
        
        return session
    
    def _get_client_info(self, request) -> Tuple[str, str]:
        """Extract client IP and user agent from request"""
        if not request:
            return '127.0.0.1', 'Unknown'
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        return ip, user_agent
    
    def _create_device_fingerprint(self, request) -> str:
        """Create device fingerprint for trusted device tracking"""
        if not request:
            return 'unknown_device'
        
        fingerprint_data = {
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
            'accept_encoding': request.META.get('HTTP_ACCEPT_ENCODING', ''),
        }
        
        import json
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = UserSession.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        
        count = expired_sessions.count()
        expired_sessions.update(is_active=False)
        
        return count


# End of auth_service.py