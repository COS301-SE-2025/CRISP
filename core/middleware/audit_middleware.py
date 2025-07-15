import json
import logging
import datetime
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import time

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log API requests and responses for audit purposes.
    
    This middleware captures:
    - All API requests with method, path, user, and IP
    - Request/response timing
    - Error conditions
    - Authentication failures
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.audit_service = self.get_audit_service()
        
        # Define which paths to audit
        self.audit_paths = [
            '/api/v1/auth/',
            '/api/v1/users/',
            '/api/v1/organizations/',
            '/api/v1/admin/',
            '/api/trust/'
        ]
        
        # Define sensitive endpoints that require special logging
        self.sensitive_endpoints = [
            '/api/v1/auth/login/',
            '/api/v1/auth/logout/',
            '/api/v1/auth/change-password/',
            '/api/v1/users/create/',
            '/api/v1/organizations/create/',
            '/api/v1/admin/'
        ]
        
        super().__init__(get_response)
    
    def get_audit_service(self):
        """Get or create audit service instance"""
        # Import here to avoid circular imports
        try:
            from core.services.audit_service import AuditService
            return AuditService()
        except ImportError:
            # Fallback to logging if service doesn't exist
            return logging.getLogger('audit')
    
    def process_request(self, request):
        """Process incoming requests."""
        # Only audit API endpoints
        if request.path.startswith('/api/'):
            request._audit_start_time = time.time()
        
        # Skip non-API requests
        if not self._should_audit_request(request):
            return None
        
        # Log request initiation for sensitive endpoints
        if self._is_sensitive_endpoint(request):
            try:
                self._log_request_start(request)
            except Exception as e:
                logger.error(f"Failed to log request start: {str(e)}")
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing responses."""
        # Skip non-API requests
        if not self._should_audit_request(request):
            return response
        
        try:
            self._log_request_complete(request, response)
        except Exception as e:
            logger.error(f"Failed to log request completion: {str(e)}")
        
        return response
    
    def process_exception(self, request, exception):
        """Process exceptions during request handling."""
        # Skip non-API requests
        if not self._should_audit_request(request):
            return None
        
        try:
            self._log_request_exception(request, exception)
        except Exception as e:
            logger.error(f"Failed to log request exception: {str(e)}")
        
        return None
    
    def _should_audit_request(self, request):
        """Determine if request should be audited."""
        path = request.path
        return any(path.startswith(audit_path) for audit_path in self.audit_paths)
    
    def _is_sensitive_endpoint(self, request):
        """Determine if endpoint is sensitive and requires detailed logging."""
        path = request.path
        return any(path.startswith(sensitive_path) for sensitive_path in self.sensitive_endpoints)
    
    def _log_request_start(self, request):
        """Log the start of a sensitive request."""
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        additional_data = {
            'method': request.method,
            'path': request.path,
            'content_type': request.content_type,
            'request_id': id(request),
            'event_type': 'request_start'
        }
        
        self.audit_service.log_user_event(
            user=user,
            action='api_request_start',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            additional_data=additional_data
        )
    
    def _log_request_complete(self, request, response):
        """Log completed request."""
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Calculate response time
        response_time = None
        if hasattr(request, '_audit_start_time'):
            start_time = request._audit_start_time
            if isinstance(start_time, datetime.datetime):
                start_time = start_time.timestamp()
            response_time = time.time() - start_time
        
        # Determine if this was a successful request
        success = 200 <= response.status_code < 400
        
        # Get action type based on endpoint and method
        action = self._get_action_from_request(request, response)
        
        additional_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'response_time_seconds': response_time,
            'content_type': request.content_type,
            'request_id': id(request),
            'event_type': 'request_complete'
        }
        
        # Add response size if available
        if hasattr(response, 'content'):
            additional_data['response_size_bytes'] = len(response.content)
        
        self.audit_service.log_user_event(
            user=user,
            action=action,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=success,
            failure_reason=f"HTTP {response.status_code}" if not success else None,
            additional_data=additional_data
        )
    
    def _log_request_exception(self, request, exception):
        """Log request that resulted in an exception."""
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Calculate response time
        response_time = None
        if hasattr(request, '_audit_start_time'):
            start_time = request._audit_start_time
            if isinstance(start_time, datetime.datetime):
                start_time = start_time.timestamp()
            response_time = time.time() - start_time
        
        additional_data = {
            'method': request.method,
            'path': request.path,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'response_time_seconds': response_time,
            'request_id': id(request),
            'event_type': 'request_exception'
        }
        
        self.audit_service.log_user_event(
            user=user,
            action='api_request_exception',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False,
            failure_reason=f"{type(exception).__name__}: {str(exception)}",
            additional_data=additional_data
        )
    
    def _get_action_from_request(self, request, response):
        """Determine audit action based on request details."""
        method = request.method.lower()
        path = request.path
        status_code = response.status_code
        
        # Map common patterns to actions
        if 'login' in path:
            return 'login_attempt' if status_code != 200 else 'login_success'
        elif 'logout' in path:
            return 'logout'
        elif 'password' in path:
            return 'password_change'
        elif 'users' in path:
            if method == 'post':
                return 'user_created'
            elif method in ['put', 'patch']:
                return 'user_modified'
            elif method == 'delete':
                return 'user_deleted'
            else:
                return 'user_accessed'
        elif 'organizations' in path:
            if method == 'post':
                return 'organization_created'
            elif method in ['put', 'patch']:
                return 'organization_modified'
            elif method == 'delete':
                return 'organization_deleted'
            else:
                return 'organization_accessed'
        elif 'admin' in path:
            return 'admin_access'
        elif 'trust' in path:
            return 'trust_accessed'
        else:
            return 'api_request'
    
    def _get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def _sanitize_request_data(self, data):
        """Sanitize request data to remove sensitive information."""
        if not data:
            return data
        
        # Remove sensitive fields
        sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = value
            return sanitized
        
        return data