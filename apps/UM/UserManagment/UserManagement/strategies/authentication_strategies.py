from abc import ABC, abstractmethod
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.hashers import check_password
import hashlib
import json
from typing import Dict, Optional, Tuple
from ..models import CustomUser, AuthenticationLog


class AuthenticationStrategy(ABC):
    """Abstract base for authentication strategies following CRISP design patterns"""
    
    @abstractmethod
    def authenticate(self, username: str, password: str, request=None) -> Dict:
        """
        Authenticate user with given credentials
        
        Returns:
            dict: {
                'success': bool,
                'user': CustomUser or None,
                'message': str,
                'requires_2fa': bool,
                'requires_device_trust': bool
            }
        """
        pass
    
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
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()


class StandardAuthenticationStrategy(AuthenticationStrategy):
    """Standard username/password authentication with security features"""
    
    def authenticate(self, username: str, password: str, request=None, **kwargs) -> Dict:
        ip_address, user_agent = self._get_client_info(request)
        
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            # Log failed attempt even if user doesn't exist
            AuthenticationLog.log_authentication_event(
                user=None,
                action='login_failed',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Invalid username'
            )
            return {
                'success': False,
                'user': None,
                'message': 'Invalid credentials',
                'requires_2fa': False,
                'requires_device_trust': False
            }
        
        # Check if account is locked
        if user.is_account_locked:
            AuthenticationLog.log_authentication_event(
                user=user,
                action='login_failed',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Account locked'
            )
            return {
                'success': False,
                'user': None,
                'message': 'Account is locked due to multiple failed login attempts',
                'requires_2fa': False,
                'requires_device_trust': False
            }
        
        # Check if user is active and verified
        if not user.is_active:
            AuthenticationLog.log_authentication_event(
                user=user,
                action='login_failed',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Account inactive'
            )
            return {
                'success': False,
                'user': None,
                'message': 'Account is inactive',
                'requires_2fa': False,
                'requires_device_trust': False
            }
        
        if not user.is_verified:
            AuthenticationLog.log_authentication_event(
                user=user,
                action='login_failed',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Account not verified'
            )
            return {
                'success': False,
                'user': None,
                'message': 'Account has not been verified by administrator',
                'requires_2fa': False,
                'requires_device_trust': False
            }
        
        # Verify password
        if not check_password(password, user.password):
            user.increment_failed_login()
            AuthenticationLog.log_authentication_event(
                user=user,
                action='login_failed',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Invalid password'
            )
            return {
                'success': False,
                'user': None,
                'message': 'Invalid credentials',
                'requires_2fa': False,
                'requires_device_trust': False
            }
        
        # Reset failed login attempts on successful authentication
        user.reset_failed_login_attempts()
        user.last_login_ip = ip_address
        user.save(update_fields=['last_login_ip'])
        
        # Check if device is trusted
        device_fingerprint = self._create_device_fingerprint(request)
        is_trusted_device = device_fingerprint in user.trusted_devices
        
        # Log successful authentication
        AuthenticationLog.log_authentication_event(
            user=user,
            action='login_success',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data={
                'device_fingerprint': device_fingerprint,
                'trusted_device': is_trusted_device
            }
        )
        
        return {
            'success': True,
            'user': user,
            'message': 'Authentication successful',
            'requires_2fa': user.two_factor_enabled and not is_trusted_device,
            'requires_device_trust': not is_trusted_device
        }


class TwoFactorAuthenticationStrategy(AuthenticationStrategy):
    """Two-factor authentication strategy"""
    
    def authenticate(self, username: str, password: str, request=None, totp_code: str = None, **kwargs) -> Dict:
        # First perform standard authentication
        standard_auth = StandardAuthenticationStrategy()
        result = standard_auth.authenticate(username, password, request)
        
        if not result['success']:
            return result
        
        user = result['user']
        ip_address, user_agent = self._get_client_info(request)
        
        # If 2FA is not enabled, return standard result
        if not user.two_factor_enabled:
            return result
        
        # Check if TOTP code is provided and valid
        if not totp_code:
            return {
                'success': False,
                'user': None,
                'message': 'Two-factor authentication code required',
                'requires_2fa': True,
                'requires_device_trust': result['requires_device_trust']
            }
        
        # Verify TOTP code (implementation would use pyotp or similar)
        if not self._verify_totp_code(user, totp_code):
            AuthenticationLog.log_authentication_event(
                user=user,
                action='login_failed',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Invalid 2FA code'
            )
            return {
                'success': False,
                'user': None,
                'message': 'Invalid two-factor authentication code',
                'requires_2fa': True,
                'requires_device_trust': result['requires_device_trust']
            }
        
        # Update result for successful 2FA
        result['requires_2fa'] = False
        
        AuthenticationLog.log_authentication_event(
            user=user,
            action='login_success',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data={'2fa_verified': True}
        )
        
        return result
    
    def _verify_totp_code(self, user: CustomUser, totp_code: str) -> bool:
        """
        Verify TOTP code for two-factor authentication
        This is a placeholder - would use pyotp or similar library
        """
        # Placeholder implementation
        # In real implementation, would verify against user's TOTP secret
        return len(totp_code) == 6 and totp_code.isdigit()


class TrustedDeviceAuthenticationStrategy(AuthenticationStrategy):
    """Trusted device authentication with reduced requirements"""
    
    def authenticate(self, username: str, password: str, request=None, remember_device: bool = False, **kwargs) -> Dict:
        # First perform standard authentication
        standard_auth = StandardAuthenticationStrategy()
        result = standard_auth.authenticate(username, password, request)
        
        if not result['success']:
            return result
        
        user = result['user']
        device_fingerprint = self._create_device_fingerprint(request)
        ip_address, user_agent = self._get_client_info(request)
        
        # If device should be remembered, add to trusted devices
        if remember_device and device_fingerprint not in user.trusted_devices:
            user.trusted_devices.append(device_fingerprint)
            user.save(update_fields=['trusted_devices'])
            
            AuthenticationLog.log_authentication_event(
                user=user,
                action='trusted_device_added',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={'device_fingerprint': device_fingerprint}
            )
        
        # Update result based on trusted device status
        is_trusted = device_fingerprint in user.trusted_devices
        result['requires_device_trust'] = not is_trusted
        
        if is_trusted:
            result['requires_2fa'] = False  # Skip 2FA for trusted devices
        
        return result


class AuthenticationContext:
    """Context for authentication strategies"""
    
    def __init__(self, strategy: AuthenticationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: AuthenticationStrategy):
        """Change authentication strategy"""
        self._strategy = strategy
    
    def authenticate(self, username: str, password: str, request=None, **kwargs) -> Dict:
        """Execute authentication using current strategy"""
        return self._strategy.authenticate(username, password, request, **kwargs)