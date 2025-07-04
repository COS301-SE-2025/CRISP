import time
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
from .models import AuthenticationLog, UserSession
from .services.auth_service import AuthenticationService


logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        """Add security headers"""
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Type Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Frame Options
        response['X-Frame-Options'] = 'DENY'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none';"
        )
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HTTP Strict Transport Security (only in production)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware for API endpoints"""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.auth_service = AuthenticationService()
    
    def process_request(self, request):
        """Apply rate limiting"""
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return None
        
        # Get client IP
        ip = self._get_client_ip(request)
        
        # Apply different rate limits based on endpoint
        endpoint = request.path
        
        if '/api/auth/login/' in endpoint:
            if self._is_rate_limited(f'login:{ip}', 5, 300):  # 5 attempts per 5 minutes
                return self._rate_limit_response('Too many login attempts')
        
        elif '/api/auth/password-reset/' in endpoint:
            if self._is_rate_limited(f'password_reset:{ip}', 3, 3600):  # 3 attempts per hour
                return self._rate_limit_response('Too many password reset attempts')
        
        elif '/api/' in endpoint:
            if self._is_rate_limited(f'api:{ip}', 100, 60):  # 100 requests per minute
                return self._rate_limit_response('Rate limit exceeded')
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def _is_rate_limited(self, key, limit, window):
        """Check if rate limit is exceeded"""
        current_time = int(time.time())
        time_window = current_time // window
        
        # Get current count
        cache_key = f'ratelimit:{key}:{time_window}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return True
        
        # Increment count
        cache.set(cache_key, current_count + 1, window)
        return False
    
    def _rate_limit_response(self, message):
        """Return rate limit response"""
        return JsonResponse({
            'error': 'rate_limit_exceeded',
            'message': message
        }, status=429)


class AuthenticationMiddleware(MiddlewareMixin):
    """Custom authentication middleware for JWT"""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.auth_service = AuthenticationService()
    
    def process_request(self, request):
        """Process authentication for API requests"""
        # Skip authentication for certain paths
        skip_paths = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/password-reset/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Check for JWT token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Verify token
            verification_result = self.auth_service.verify_token(token, request)
            
            if verification_result['success']:
                # Set user in request
                from .models import CustomUser
                try:
                    user = CustomUser.objects.get(id=verification_result['user_id'])
                    request.user = user
                    request.auth = token
                except CustomUser.DoesNotExist:
                    request.user = AnonymousUser()
            else:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        return None


class SecurityAuditMiddleware(MiddlewareMixin):
    """Middleware for security auditing and monitoring"""
    
    def process_request(self, request):
        """Log security-relevant requests"""
        # Log suspicious patterns
        self._check_suspicious_patterns(request)
        
        # Log API access
        if request.path.startswith('/api/'):
            self._log_api_access(request)
        
        return None
    
    def _check_suspicious_patterns(self, request):
        """Check for suspicious request patterns"""
        suspicious_patterns = [
            'eval(', 'exec(', '<script', 'javascript:', 'vbscript:',
            'SELECT * FROM', 'DROP TABLE', 'UNION SELECT',
            '../../../', '..\\..\\..\\',
            'cmd.exe', '/bin/bash', '/bin/sh'
        ]
        
        # Check URL and parameters
        full_path = request.get_full_path()
        
        for pattern in suspicious_patterns:
            if pattern.lower() in full_path.lower():
                self._log_suspicious_activity(request, f'Suspicious pattern in URL: {pattern}')
                break
        
        # Check POST data
        if request.method == 'POST' and hasattr(request, 'body'):
            try:
                body_str = request.body.decode('utf-8', errors='ignore')
                for pattern in suspicious_patterns:
                    if pattern.lower() in body_str.lower():
                        self._log_suspicious_activity(request, f'Suspicious pattern in body: {pattern}')
                        break
            except Exception:
                pass  # Ignore errors in body inspection
    
    def _log_suspicious_activity(self, request, reason):
        """Log suspicious activity"""
        ip = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        logger.warning(f"SUSPICIOUS_ACTIVITY: {reason} | IP: {ip} | User-Agent: {user_agent} | Path: {request.path}")
        
        # Log to authentication log if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            from .models import CustomUser
            if isinstance(request.user, CustomUser):
                AuthenticationLog.log_authentication_event(
                    user=request.user,
                    action='suspicious_activity',
                    ip_address=ip,
                    user_agent=user_agent,
                    success=False,
                    failure_reason=reason,
                    additional_data={'path': request.path, 'method': request.method}
                )
    
    def _log_api_access(self, request):
        """Log API access for monitoring"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            from .models import CustomUser
            if isinstance(request.user, CustomUser):
                # Only log significant API calls to avoid log spam
                significant_endpoints = [
                    '/api/admin/',
                    '/api/stix/',
                    '/api/feeds/',
                    '/api/users/',
                    '/api/organizations/'
                ]
                
                if any(endpoint in request.path for endpoint in significant_endpoints):
                    ip = self._get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                    
                    logger.info(f"API_ACCESS: {request.user.username} | {request.method} {request.path} | IP: {ip}")
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class SessionTimeoutMiddleware(MiddlewareMixin):
    """Handle session timeout and cleanup"""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.auth_service = AuthenticationService()
    
    def process_request(self, request):
        """Check for session timeout"""
        # Clean up expired sessions periodically
        if hasattr(request, 'user') and request.user.is_authenticated:
            from .models import CustomUser
            if isinstance(request.user, CustomUser):
                # Check if current session is expired
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    
                    # Verify token is still valid
                    verification_result = self.auth_service.verify_token(token, request)
                    
                    if not verification_result['success']:
                        # Token is invalid/expired, return 401
                        return JsonResponse({
                            'error': 'token_expired',
                            'message': 'Your session has expired. Please log in again.'
                        }, status=401)
        
        return None


class SessionActivityMiddleware(MiddlewareMixin):
    """Middleware to track session activity and handle automatic cleanup"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Update session activity for authenticated users"""
        # Only process for authenticated API requests
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._update_session_activity(request)
            self._cleanup_expired_sessions_periodically()
        
        return None
    
    def _update_session_activity(self, request):
        """Update last activity for the current session"""
        try:
            # Get JWT token from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return
            
            token = auth_header.split(' ')[1]
            
            # Find the session with this token
            try:
                session = UserSession.objects.get(
                    session_token=token,
                    user=request.user,
                    is_active=True
                )
                
                # Update last activity
                now = timezone.now()
                
                # Check if session has been inactive for too long
                max_inactive_hours = getattr(settings, 'SESSION_MAX_INACTIVE_HOURS', 24)
                inactive_threshold = now - timedelta(hours=max_inactive_hours)
                
                if session.last_activity < inactive_threshold:
                    # Session has been inactive too long, deactivate it
                    session.is_active = False
                    session.save(update_fields=['is_active'])
                    
                    # Log the automatic deactivation
                    AuthenticationLog.log_authentication_event(
                        user=request.user,
                        action='session_auto_deactivated',
                        ip_address=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', 'Unknown'),
                        success=True,
                        additional_data={
                            'session_id': str(session.id),
                            'inactive_hours': max_inactive_hours,
                            'last_activity': session.last_activity.isoformat(),
                            'reason': 'max_inactive_time_exceeded'
                        }
                    )
                else:
                    # Update last activity timestamp
                    session.last_activity = now
                    session.save(update_fields=['last_activity'])
                
            except UserSession.DoesNotExist:
                pass
                
        except Exception as e:
            logger.error(f"Error updating session activity: {str(e)}")
    
    def _cleanup_expired_sessions_periodically(self):
        """Periodically clean up expired sessions"""
        try:
            cache_key = 'session_cleanup_last_run'
            last_cleanup = cache.get(cache_key)
            now = timezone.now()
            
            if not last_cleanup or (now - last_cleanup).total_seconds() > 300:  # 5 minutes
                expired_sessions = UserSession.objects.filter(
                    expires_at__lt=now,
                    is_active=True
                )
                
                expired_count = expired_sessions.count()
                if expired_count > 0:
                    expired_sessions.update(is_active=False)
                    logger.info(f"Cleaned up {expired_count} expired sessions")
                
                cache.set(cache_key, now, 600)
                
        except Exception as e:
            logger.error(f"Error during periodic session cleanup: {str(e)}")
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
