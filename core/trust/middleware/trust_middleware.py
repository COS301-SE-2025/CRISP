from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.urls import resolve
from django.conf import settings
import logging
import time
import json

from ..integrations.stix_taxii_integration import crisp_threat_intelligence_integration
from ..patterns.observer.trust_observers import trust_event_manager, notify_access_event

logger = logging.getLogger(__name__)


class TrustBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware that enforces trust-based access control for API endpoints.
    Integrates with CRISP's threat intelligence sharing system.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_endpoints = getattr(settings, 'TRUST_PROTECTED_ENDPOINTS', [
            '/api/threat-intelligence/',
            '/api/indicators/',
            '/api/ttps/',
            '/taxii2/',
        ])
        self.bypass_paths = getattr(settings, 'TRUST_BYPASS_PATHS', [
            '/api/auth/',
            '/api/trust/',
            '/admin/',
        ])
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming request for trust-based access control."""
        # Skip non-API requests and bypass paths
        if not self._should_check_trust_access(request):
            return None
        
        # Extract organization information from request
        requesting_org = self._get_requesting_organization(request)
        if not requesting_org:
            return JsonResponse({
                'error': 'Missing organization information',
                'details': 'Trust-based access requires organization identification'
            }, status=400)
        
        # Check if this is a threat intelligence access request
        if self._is_threat_intelligence_request(request):
            return self._check_threat_intelligence_access(request, requesting_org)
        
        return None
    
    def process_response(self, request, response):
        """Process response for trust-based access logging."""
        if hasattr(request, '_trust_access_check_performed'):
            # Log access event
            requesting_org = getattr(request, '_requesting_organization', None)
            target_org = getattr(request, '_target_organization', None)
            resource_type = getattr(request, '_resource_type', None)
            
            if requesting_org and target_org:
                access_granted = response.status_code < 400
                
                notify_access_event(
                    'access_granted' if access_granted else 'access_denied',
                    requesting_org,
                    target_org,
                    resource_type=resource_type,
                    access_level=getattr(request, '_access_level', 'read'),
                    reason=getattr(request, '_access_reason', 'Unknown'),
                    user=self._get_user_identifier(request),
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    http_method=request.method,
                    endpoint=request.path,
                    response_status=response.status_code
                )
        
        return response
    
    def _should_check_trust_access(self, request):
        """Determine if trust-based access control should be applied."""
        path = request.path
        
        # Skip bypass paths
        for bypass_path in self.bypass_paths:
            if path.startswith(bypass_path):
                return False
        
        # Check protected endpoints
        for protected_path in self.protected_endpoints:
            if path.startswith(protected_path):
                return True
        
        return False
    
    def _get_requesting_organization(self, request):
        """Extract requesting organization from request."""
        # Try multiple sources for organization identification
        org_id = None
        
        # Check headers
        org_id = request.META.get('HTTP_X_ORGANIZATION_ID')
        if org_id:
            return org_id
        
        # Check authentication token/user
        if hasattr(request, 'user') and request.user.is_authenticated:
            # This would integrate with user management system
            org_id = getattr(request.user, 'organization_id', None)
            if org_id:
                return org_id
        
        # Check query parameters (for development/testing)
        org_id = request.GET.get('org_id') or request.POST.get('org_id')
        if org_id:
            return org_id
        
        # Check request body for JSON requests
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                org_id = body.get('organization_id')
                if org_id:
                    return org_id
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return None
    
    def _is_threat_intelligence_request(self, request):
        """Check if request is for threat intelligence resources."""
        threat_intel_paths = [
            '/api/threat-intelligence/',
            '/api/indicators/',
            '/api/ttps/',
            '/api/reports/',
            '/taxii2/collections/',
        ]
        
        for path in threat_intel_paths:
            if request.path.startswith(path):
                return True
        
        return False
    
    def _check_threat_intelligence_access(self, request, requesting_org):
        """Check access to threat intelligence resources."""
        # Extract target organization and resource information
        target_org = self._extract_target_organization(request)
        resource_type = self._extract_resource_type(request)
        required_access_level = self._determine_required_access_level(request)
        
        if not target_org:
            # If no specific target, allow general access (like listing public resources)
            return None
        
        # Validate access using trust integration
        can_access, reason, trust_relationship = crisp_threat_intelligence_integration.validate_intelligence_access(
            requesting_org,
            target_org,
            resource_type,
            required_access_level
        )
        
        # Store information for response processing
        request._trust_access_check_performed = True
        request._requesting_organization = requesting_org
        request._target_organization = target_org
        request._resource_type = resource_type
        request._access_level = required_access_level
        request._access_reason = reason
        
        if not can_access:
            return JsonResponse({
                'error': 'Access denied',
                'details': reason,
                'requesting_organization': requesting_org,
                'target_organization': target_org,
                'resource_type': resource_type,
                'required_access_level': required_access_level
            }, status=403)
        
        # Store trust relationship for later use
        request._trust_relationship = trust_relationship
        
        return None
    
    def _extract_target_organization(self, request):
        """Extract target organization from request path/parameters."""
        # Try URL path parameters
        try:
            resolved = resolve(request.path)
            if 'org_id' in resolved.kwargs:
                return resolved.kwargs['org_id']
            if 'organization' in resolved.kwargs:
                return resolved.kwargs['organization']
        except Exception:
            pass
        
        # Try query parameters
        target_org = request.GET.get('target_org') or request.GET.get('owner')
        if target_org:
            return target_org
        
        # Try request body
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                return body.get('target_organization') or body.get('owner_organization')
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return None
    
    def _extract_resource_type(self, request):
        """Extract resource type from request path."""
        path = request.path
        
        if '/indicators/' in path:
            return 'indicator'
        elif '/ttps/' in path:
            return 'ttp'
        elif '/reports/' in path:
            return 'report'
        elif '/threat-feeds/' in path:
            return 'threat-feed'
        elif '/taxii2/' in path:
            return 'taxii-collection'
        else:
            return 'intelligence'
    
    def _determine_required_access_level(self, request):
        """Determine required access level based on HTTP method and path."""
        method = request.method.upper()
        
        if method == 'GET':
            return 'read'
        elif method in ['POST', 'PUT', 'PATCH']:
            if '/subscribe' in request.path:
                return 'subscribe'
            else:
                return 'contribute'
        elif method == 'DELETE':
            return 'full'
        else:
            return 'read'
    
    def _get_user_identifier(self, request):
        """Get user identifier for logging."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return str(request.user.id)
        return 'anonymous'
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TrustMetricsMiddleware(MiddlewareMixin):
    """
    Middleware that collects metrics about trust-based access patterns.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Record request start time."""
        request._trust_metrics_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Collect trust-related metrics."""
        if hasattr(request, '_trust_access_check_performed'):
            # Calculate response time
            start_time = getattr(request, '_trust_metrics_start_time', time.time())
            response_time = time.time() - start_time
            
            # Collect metrics
            metrics_data = {
                'request_path': request.path,
                'http_method': request.method,
                'response_status': response.status_code,
                'response_time_ms': round(response_time * 1000, 2),
                'requesting_organization': getattr(request, '_requesting_organization', None),
                'target_organization': getattr(request, '_target_organization', None),
                'resource_type': getattr(request, '_resource_type', None),
                'access_level': getattr(request, '_access_level', None),
                'trust_relationship_exists': hasattr(request, '_trust_relationship'),
                'timestamp': time.time()
            }
            
            # Send metrics to observers
            trust_event_manager.notify_observers('trust_access_metrics', {
                'metrics': metrics_data,
                'request_info': {
                    'user_agent': request.META.get('HTTP_USER_AGENT'),
                    'client_ip': self._get_client_ip(request),
                    'content_type': request.content_type
                }
            })
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip