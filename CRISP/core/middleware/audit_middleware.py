"""
Audit Middleware - Comprehensive audit logging for all requests and responses
Logs user activities, API calls, data access, and security events
"""

import json
import time
import logging
from typing import Dict, Any, Optional
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from core.models.models import CustomUser
from core.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class AuditMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive audit logging of all requests and responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.audit_service = AuditService()
        
        # Paths that should be excluded from detailed logging
        self.excluded_paths = {
            '/api/auth/verify-token/',
            '/api/health/',
            '/admin/jsi18n/',
            '/static/',
            '/media/',
            '/favicon.ico'
        }
        
        # Sensitive fields that should be redacted in logs
        self.sensitive_fields = {
            'password', 'token', 'secret', 'key', 'csrf_token',
            'csrfmiddlewaretoken', 'authorization', 'x-api-key'
        }
        
        # API endpoints that involve data access
        self.data_access_patterns = {
            '/api/indicators/',
            '/api/ttps/',
            '/api/feeds/',
            '/api/stix/',
            '/api/taxii/'
        }
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming request - start timing and log request details"""
        try:
            # Skip excluded paths
            if self._should_exclude_path(request.path):
                return None
            
            # Record start time
            request._audit_start_time = time.time()
            
            # Extract request metadata
            request._audit_data = {
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'content_type': request.content_type,
                'is_ajax': request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest',
                'is_api_call': request.path.startswith('/api/'),
                'session_key': request.session.session_key if hasattr(request, 'session') else None
            }
            
            # Log request body for API calls (with sensitive data redacted)
            if request._audit_data['is_api_call'] and request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body') and request.body:
                        if request.content_type == 'application/json':
                            body_data = json.loads(request.body.decode('utf-8'))
                            request._audit_data['request_body'] = self._redact_sensitive_data(body_data)
                        else:
                            request._audit_data['request_body'] = '<non-json-data>'
                except (json.JSONDecodeError, UnicodeDecodeError):
                    request._audit_data['request_body'] = '<invalid-json>'
            
            # Determine if this is a data access request
            request._is_data_access = any(
                pattern in request.path for pattern in self.data_access_patterns
            )
            
        except Exception as e:
            logger.error(f"Error in audit middleware process_request: {str(e)}")
        
        return None
    
    def process_response(self, request, response):
        """Process response - log complete audit trail"""
        try:
            # Skip excluded paths
            if self._should_exclude_path(request.path):
                return response
            
            # Skip if audit data wasn't set (shouldn't happen)
            if not hasattr(request, '_audit_data'):
                return response
            
            # Calculate response time
            response_time = None
            if hasattr(request, '_audit_start_time'):
                response_time = (time.time() - request._audit_start_time) * 1000  # Convert to milliseconds
            
            # Get user information
            user = None
            user_id = None
            username = None
            organization_id = None
            
            if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                user = request.user
                user_id = str(user.id)
                username = user.username
                organization_id = str(user.organization.id) if user.organization else None
            
            # Determine action type
            action_type = self._determine_action_type(request, response)
            
            # Check for authentication/authorization events
            auth_event = self._detect_auth_event(request, response)
            
            # Log the audit event
            audit_data = {
                **request._audit_data,
                'response_status': response.status_code,
                'response_time_ms': response_time,
                'user_id': user_id,
                'username': username,
                'organization_id': organization_id,
                'action_type': action_type,
                'auth_event': auth_event,
                'success': 200 <= response.status_code < 400,
                'timestamp': timezone.now().isoformat()
            }
            
            # Add response data for certain types of requests
            if request._audit_data['is_api_call'] and response.status_code in [200, 201]:
                audit_data['response_size'] = len(response.content) if hasattr(response, 'content') else 0
            
            # Log data access events separately
            if getattr(request, '_is_data_access', False):
                self._log_data_access_event(request, response, user, audit_data)
            
            # Log security events
            if self._is_security_event(request, response):
                self._log_security_event(request, response, user, audit_data)
            
            # Log general audit event
            self.audit_service.log_request_audit(
                user=user,
                action=action_type,
                success=audit_data['success'],
                additional_data=audit_data
            )
            
            # Log performance issues
            if response_time and response_time > 5000:  # Log slow requests (>5 seconds)
                logger.warning(f"Slow request detected: {request.method} {request.path} took {response_time:.2f}ms")
                self.audit_service.log_performance_event(
                    action='slow_request',
                    user=user,
                    additional_data={
                        'path': request.path,
                        'method': request.method,
                        'response_time_ms': response_time,
                        'status_code': response.status_code
                    }
                )
            
        except Exception as e:
            logger.error(f"Error in audit middleware process_response: {str(e)}")
        
        return response
    
    def process_exception(self, request, exception):
        """Process exceptions - log error events"""
        try:
            if hasattr(request, '_audit_data'):
                user = None
                if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                    user = request.user
                
                # Calculate response time
                response_time = None
                if hasattr(request, '_audit_start_time'):
                    response_time = (time.time() - request._audit_start_time) * 1000
                
                # Log the exception
                self.audit_service.log_security_event(
                    action='request_exception',
                    user=user,
                    success=False,
                    failure_reason=str(exception),
                    severity='medium',
                    additional_data={
                        **request._audit_data,
                        'exception_type': type(exception).__name__,
                        'response_time_ms': response_time,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                logger.error(f"Request exception: {type(exception).__name__}: {str(exception)} for {request.method} {request.path}")
        
        except Exception as e:
            logger.error(f"Error in audit middleware process_exception: {str(e)}")
        
        return None
    
    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from audit logging"""
        return any(excluded in path for excluded in self.excluded_paths)
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address, handling proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _redact_sensitive_data(self, data: Any) -> Any:
        """Recursively redact sensitive data from request/response"""
        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    redacted[key] = '[REDACTED]'
                else:
                    redacted[key] = self._redact_sensitive_data(value)
            return redacted
        elif isinstance(data, list):
            return [self._redact_sensitive_data(item) for item in data]
        else:
            return data
    
    def _determine_action_type(self, request, response) -> str:
        """Determine the type of action based on request/response"""
        path = request.path.lower()
        method = request.method.upper()
        
        # Authentication actions
        if '/auth/' in path:
            if 'login' in path:
                return 'user_login'
            elif 'logout' in path:
                return 'user_logout'
            elif 'register' in path:
                return 'user_registration'
            elif 'password' in path:
                return 'password_operation'
            else:
                return 'authentication'
        
        # User management actions
        if '/users/' in path:
            if method == 'GET':
                return 'user_view'
            elif method in ['POST']:
                return 'user_create'
            elif method in ['PUT', 'PATCH']:
                return 'user_update'
            elif method == 'DELETE':
                return 'user_delete'
        
        # Trust management actions
        if '/trust/' in path:
            if 'request' in path:
                return 'trust_request'
            elif 'respond' in path:
                return 'trust_response'
            elif method in ['PUT', 'PATCH']:
                return 'trust_update'
            elif method == 'DELETE':
                return 'trust_revoke'
            else:
                return 'trust_view'
        
        # Organization actions
        if '/organizations/' in path:
            if method == 'GET':
                return 'organization_view'
            elif method == 'POST':
                return 'organization_create'
            elif method in ['PUT', 'PATCH']:
                return 'organization_update'
            elif method == 'DELETE':
                return 'organization_delete'
        
        # Data access actions
        if any(pattern.rstrip('/') in path for pattern in self.data_access_patterns):
            if method == 'GET':
                return 'data_access'
            elif method == 'POST':
                return 'data_create'
            elif method in ['PUT', 'PATCH']:
                return 'data_update'
            elif method == 'DELETE':
                return 'data_delete'
        
        # Default action type
        return f"{method.lower()}_request"
    
    def _detect_auth_event(self, request, response) -> Optional[str]:
        """Detect authentication/authorization events"""
        if response.status_code == 401:
            return 'unauthorized_access'
        elif response.status_code == 403:
            return 'forbidden_access'
        elif '/auth/' in request.path:
            if response.status_code in [200, 201]:
                return 'successful_auth'
            else:
                return 'failed_auth'
        return None
    
    def _is_security_event(self, request, response) -> bool:
        """Determine if this is a security-relevant event"""
        return (
            response.status_code in [401, 403, 429] or  # Security status codes
            '/auth/' in request.path or  # Authentication endpoints
            request.method in ['DELETE'] or  # Destructive operations
            'admin' in request.path.lower() or  # Admin operations
            self._detect_suspicious_activity(request, response)
        )
    
    def _detect_suspicious_activity(self, request, response) -> bool:
        """Detect potentially suspicious activity"""
        # Multiple failed attempts (would need session/cache to track)
        # Unusual request patterns
        # Large response sizes
        # etc.
        return False
    
    def _log_data_access_event(self, request, response, user, audit_data):
        """Log data access events with additional context"""
        try:
            self.audit_service.log_data_access_event(
                user=user,
                resource_type=self._extract_resource_type(request.path),
                resource_id=self._extract_resource_id(request.path),
                action=audit_data['action_type'],
                success=audit_data['success'],
                additional_data={
                    'path': request.path,
                    'method': request.method,
                    'ip_address': audit_data['ip_address'],
                    'user_agent': audit_data['user_agent'],
                    'response_status': response.status_code,
                    'response_time_ms': audit_data.get('response_time_ms')
                }
            )
        except Exception as e:
            logger.error(f"Error logging data access event: {str(e)}")
    
    def _log_security_event(self, request, response, user, audit_data):
        """Log security events with appropriate severity"""
        try:
            severity = 'low'
            if response.status_code in [401, 403]:
                severity = 'medium'
            elif request.method == 'DELETE':
                severity = 'high'
            
            self.audit_service.log_security_event(
                action=audit_data.get('auth_event', 'security_event'),
                user=user,
                success=audit_data['success'],
                severity=severity,
                additional_data=audit_data
            )
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
    
    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from URL path"""
        if '/indicators/' in path:
            return 'indicator'
        elif '/ttps/' in path:
            return 'ttp'
        elif '/feeds/' in path:
            return 'feed'
        elif '/users/' in path:
            return 'user'
        elif '/organizations/' in path:
            return 'organization'
        elif '/trust/' in path:
            return 'trust_relationship'
        else:
            return 'unknown'
    
    def _extract_resource_id(self, path: str) -> Optional[str]:
        """Extract resource ID from URL path"""
        try:
            # Look for UUID patterns in the path
            import re
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            match = re.search(uuid_pattern, path)
            return match.group(0) if match else None
        except Exception:
            return None