"""
Trust-Aware Middleware - Enforces trust-based access control and data filtering
Validates trust relationships and applies appropriate data anonymization
"""

import json
import logging
from typing import Optional, Dict, Any
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve
from core.services.trust_service import TrustService
from core.services.access_control_service import AccessControlService
from core.patterns.strategy.context import AnonymizationContext

logger = logging.getLogger(__name__)

class TrustMiddleware(MiddlewareMixin):
    """
    Middleware for enforcing trust-based access control and data anonymization
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.trust_service = TrustService()
        self.access_control = AccessControlService()
        
        # API endpoints that require trust validation
        self.trust_protected_endpoints = {
            '/api/indicators/',
            '/api/ttps/', 
            '/api/feeds/',
            '/api/stix/',
            '/api/taxii/'
        }
        
        # Endpoints that require organization membership
        self.org_protected_endpoints = {
            '/api/organizations/',
            '/api/trust/',
            '/api/users/invite/'
        }
        
        # Cross-organization data sharing endpoints
        self.data_sharing_endpoints = {
            '/api/feeds/share/',
            '/api/indicators/share/',
            '/api/ttps/share/',
            '/api/stix/share/'
        }
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming request for trust validation"""
        try:
            # Skip non-API requests
            if not request.path.startswith('/api/'):
                return None
            
            # Skip authentication endpoints
            if '/auth/' in request.path:
                return None
            
            # Skip for anonymous users (handled by authentication middleware)
            if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
                return None
            
            # Add trust context to request
            request.trust_context = self._create_trust_context(request)
            
            # Validate organization membership for protected endpoints
            if self._requires_organization_membership(request.path):
                if not self._validate_organization_membership(request):
                    return JsonResponse({
                        'success': False,
                        'message': 'Organization membership required for this action',
                        'error_type': 'organization_required'
                    }, status=403)
            
            # Validate trust relationships for data access
            if self._requires_trust_validation(request.path):
                trust_validation = self._validate_trust_access(request)
                if not trust_validation['valid']:
                    return JsonResponse({
                        'success': False,
                        'message': trust_validation['message'],
                        'error_type': 'trust_validation_failed'
                    }, status=403)
                
                # Store trust level for data filtering
                request.trust_level = trust_validation['trust_level']
            
            # Validate cross-organization data sharing
            if self._is_data_sharing_request(request.path):
                sharing_validation = self._validate_data_sharing(request)
                if not sharing_validation['valid']:
                    return JsonResponse({
                        'success': False,
                        'message': sharing_validation['message'],
                        'error_type': 'data_sharing_denied'
                    }, status=403)
        
        except Exception as e:
            logger.error(f"Error in trust middleware process_request: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Trust validation error',
                'error_type': 'trust_middleware_error'
            }, status=500)
        
        return None
    
    def process_response(self, request, response):
        """Process response for trust-based data filtering"""
        try:
            # Skip non-API responses
            if not request.path.startswith('/api/'):
                return response
            
            # Skip for anonymous users
            if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
                return response
            
            # Skip if trust context wasn't set
            if not hasattr(request, 'trust_context'):
                return response
            
            # Apply trust-based data filtering for successful responses
            if (response.status_code == 200 and 
                hasattr(response, 'content') and 
                self._should_filter_response(request.path)):
                
                filtered_response = self._filter_response_data(request, response)
                if filtered_response:
                    response = filtered_response
        
        except Exception as e:
            logger.error(f"Error in trust middleware process_response: {str(e)}")
        
        return response
    
    def _create_trust_context(self, request) -> Dict[str, Any]:
        """Create trust context for the request"""
        context = {
            'user': request.user,
            'organization': request.user.organization,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_path': request.path,
            'request_method': request.method,
            'trust_relationships': {}
        }
        
        # Get trust relationships for user's organization
        if request.user.organization:
            try:
                relationships = self.trust_service.get_organization_trust_relationships(
                    request.user.organization
                )
                context['trust_relationships'] = {
                    str(rel['organization_id']): rel['trust_level'] 
                    for rel in relationships
                }
            except Exception as e:
                logger.error(f"Error getting trust relationships: {str(e)}")
        
        return context
    
    def _requires_organization_membership(self, path: str) -> bool:
        """Check if endpoint requires organization membership"""
        return any(endpoint in path for endpoint in self.org_protected_endpoints)
    
    def _requires_trust_validation(self, path: str) -> bool:
        """Check if endpoint requires trust validation"""
        return any(endpoint in path for endpoint in self.trust_protected_endpoints)
    
    def _is_data_sharing_request(self, path: str) -> bool:
        """Check if this is a data sharing request"""
        return any(endpoint in path for endpoint in self.data_sharing_endpoints)
    
    def _validate_organization_membership(self, request) -> bool:
        """Validate that user belongs to an organization"""
        return request.user.organization is not None
    
    def _validate_trust_access(self, request) -> Dict[str, Any]:
        """Validate trust-based access to resources"""
        try:
            # Extract target organization from request if present
            target_org_id = self._extract_target_organization(request)
            
            # If no target organization, allow access (internal data)
            if not target_org_id:
                return {
                    'valid': True,
                    'trust_level': 'full',
                    'message': 'Internal organization access'
                }
            
            # Check trust relationship
            trust_level = self.trust_service.get_trust_level_by_id(
                request.user.organization.id if request.user.organization else None,
                target_org_id
            )
            
            # Determine minimum required trust level based on action
            required_trust_level = self._get_required_trust_level(request)
            
            # Validate trust level
            if self._is_sufficient_trust_level(trust_level, required_trust_level):
                return {
                    'valid': True,
                    'trust_level': trust_level,
                    'message': 'Trust validation successful'
                }
            else:
                return {
                    'valid': False,
                    'trust_level': trust_level,
                    'message': f'Insufficient trust level. Required: {required_trust_level}, Current: {trust_level}'
                }
        
        except Exception as e:
            logger.error(f"Error validating trust access: {str(e)}")
            return {
                'valid': False,
                'trust_level': 'none',
                'message': 'Trust validation error'
            }
    
    def _validate_data_sharing(self, request) -> Dict[str, Any]:
        """Validate data sharing permissions"""
        try:
            # Extract recipient organization from request
            recipient_org_id = self._extract_recipient_organization(request)
            
            if not recipient_org_id:
                return {
                    'valid': False,
                    'message': 'Recipient organization not specified'
                }
            
            # Check if user can share data with target organization
            can_share = self.access_control.can_share_data_with_organization(
                request.user,
                recipient_org_id
            )
            
            if can_share:
                return {
                    'valid': True,
                    'message': 'Data sharing authorized'
                }
            else:
                return {
                    'valid': False,
                    'message': 'Data sharing not authorized with this organization'
                }
        
        except Exception as e:
            logger.error(f"Error validating data sharing: {str(e)}")
            return {
                'valid': False,
                'message': 'Data sharing validation error'
            }
    
    def _should_filter_response(self, path: str) -> bool:
        """Check if response should be filtered based on trust"""
        return any(endpoint in path for endpoint in self.trust_protected_endpoints)
    
    def _filter_response_data(self, request, response):
        """Filter response data based on trust level"""
        try:
            # Parse response content
            content_type = response.get('Content-Type', '')
            if 'application/json' not in content_type:
                return None
            
            try:
                data = json.loads(response.content.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
            
            # Get trust level for filtering
            trust_level = getattr(request, 'trust_level', 'minimal')
            
            # Apply trust-based anonymization
            filtered_data = self._apply_trust_anonymization(data, trust_level, request)
            
            # Create new response with filtered data
            if filtered_data != data:
                new_response = JsonResponse(filtered_data, status=response.status_code)
                
                # Copy headers
                for header, value in response.items():
                    if header.lower() not in ['content-length', 'content-type']:
                        new_response[header] = value
                
                return new_response
        
        except Exception as e:
            logger.error(f"Error filtering response data: {str(e)}")
        
        return None
    
    def _apply_trust_anonymization(self, data: Any, trust_level: str, request) -> Any:
        """Apply trust-based anonymization to response data"""
        try:
            # Create anonymization context
            anonymization_context = AnonymizationContext()
            
            # Set trust context
            anonymization_context.set_trust_context(
                trust_level=trust_level,
                requesting_org=request.user.organization,
                accessing_user=request.user
            )
            
            # Apply anonymization based on data type
            if isinstance(data, dict):
                return self._anonymize_dict(data, anonymization_context)
            elif isinstance(data, list):
                return [self._anonymize_dict(item, anonymization_context) if isinstance(item, dict) else item for item in data]
            else:
                return data
        
        except Exception as e:
            logger.error(f"Error applying trust anonymization: {str(e)}")
            return data
    
    def _anonymize_dict(self, data: dict, context: AnonymizationContext) -> dict:
        """Anonymize dictionary data based on trust context"""
        try:
            # Check if this is a STIX object
            if 'type' in data and 'id' in data:
                return context.anonymize_stix_with_trust(data)
            
            # Apply field-level anonymization for other data types
            anonymized = {}
            for key, value in data.items():
                if key in ['indicators', 'ttps', 'observables']:
                    # Anonymize nested threat data
                    if isinstance(value, list):
                        anonymized[key] = [
                            context.anonymize_with_trust_context(item) if isinstance(item, dict) else item
                            for item in value
                        ]
                    else:
                        anonymized[key] = context.anonymize_with_trust_context(value)
                elif key in ['description', 'pattern', 'value']:
                    # Anonymize potentially sensitive fields
                    anonymized[key] = context.anonymize_with_trust_context(value)
                else:
                    anonymized[key] = value
            
            return anonymized
        
        except Exception as e:
            logger.error(f"Error anonymizing dict: {str(e)}")
            return data
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _extract_target_organization(self, request) -> Optional[str]:
        """Extract target organization ID from request"""
        try:
            # Check URL parameters
            url_match = resolve(request.path_info)
            if 'organization_id' in url_match.kwargs:
                return url_match.kwargs['organization_id']
            
            # Check query parameters
            if 'organization' in request.GET:
                return request.GET['organization']
            
            # Check request body for POST/PUT requests
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
                try:
                    body_data = json.loads(request.body.decode('utf-8'))
                    if 'organization_id' in body_data:
                        return body_data['organization_id']
                    if 'target_organization' in body_data:
                        return body_data['target_organization']
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
        
        except Exception as e:
            logger.error(f"Error extracting target organization: {str(e)}")
        
        return None
    
    def _extract_recipient_organization(self, request) -> Optional[str]:
        """Extract recipient organization ID from data sharing request"""
        try:
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
                try:
                    body_data = json.loads(request.body.decode('utf-8'))
                    return (body_data.get('recipient_organization') or 
                           body_data.get('recipient_org_id') or
                           body_data.get('to_organization'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
        except Exception as e:
            logger.error(f"Error extracting recipient organization: {str(e)}")
        
        return None
    
    def _get_required_trust_level(self, request) -> str:
        """Determine required trust level based on request type"""
        if request.method == 'GET':
            # Read operations require minimal trust
            return 'minimal'
        elif request.method in ['POST', 'PUT', 'PATCH']:
            # Write operations require moderate trust
            return 'moderate'
        elif request.method == 'DELETE':
            # Delete operations require high trust
            return 'standard'
        else:
            return 'minimal'
    
    def _is_sufficient_trust_level(self, current_level: str, required_level: str) -> bool:
        """Check if current trust level meets requirement"""
        trust_hierarchy = {
            'none': 0,
            'minimal': 1,
            'moderate': 2, 
            'standard': 3,
            'full': 4
        }
        
        current_value = trust_hierarchy.get(current_level, 0)
        required_value = trust_hierarchy.get(required_level, 1)
        
        return current_value >= required_value