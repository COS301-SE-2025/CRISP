import json
import re
import time
from django.conf import settings
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

from audit.models import AuditLog
from core.models import Organization

class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log TAXII API access and other activities.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns for matching TAXII endpoints
        self.taxii_discovery_pattern = re.compile(r'^/taxii2/?$')
        self.taxii_api_root_pattern = re.compile(r'^/taxii2/$')
        self.taxii_collections_pattern = re.compile(r'^/taxii2/collections/?$')
        self.taxii_collection_pattern = re.compile(r'^/taxii2/collections/[^/]+/?$')
        self.taxii_objects_pattern = re.compile(r'^/taxii2/collections/[^/]+/objects/?$')
        self.taxii_object_pattern = re.compile(r'^/taxii2/collections/[^/]+/objects/[^/]+/?$')
        self.taxii_manifest_pattern = re.compile(r'^/taxii2/collections/[^/]+/manifest/?$')
    
    def process_request(self, request):
        """Store start time on request."""
        request.start_time = time.time()
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_action_type(self, request, path):
        """
        Determine the action type based on the request path and method.
        """
        if self.taxii_discovery_pattern.match(path):
            return 'discovery'
        elif self.taxii_api_root_pattern.match(path):
            return 'api_root'
        elif self.taxii_collections_pattern.match(path):
            return 'list_collections'
        elif self.taxii_collection_pattern.match(path):
            return 'get_collection'
        elif self.taxii_objects_pattern.match(path):
            if request.method == 'GET':
                return 'get_collection_objects'
            elif request.method == 'POST':
                return 'add_collection_objects'
        elif self.taxii_object_pattern.match(path):
            return 'get_object'
        elif self.taxii_manifest_pattern.match(path):
            return 'get_manifest'
        
        # Non-TAXII endpoints
        if '/api/stix/' in path:
            if request.method == 'POST':
                return 'create_stix_object'
            elif request.method == 'PUT' or request.method == 'PATCH':
                return 'update_stix_object'
            elif request.method == 'DELETE':
                return 'delete_stix_object'
        
        if '/api/collections/' in path:
            if request.method == 'POST':
                return 'create_collection'
            elif request.method == 'PUT' or request.method == 'PATCH':
                return 'update_collection'
            elif request.method == 'DELETE':
                return 'delete_collection'
        
        if '/api/trust/' in path:
            if request.method == 'POST':
                return 'create_trust_relationship'
            elif request.method == 'PUT' or request.method == 'PATCH':
                return 'update_trust_relationship'
            elif request.method == 'DELETE':
                return 'delete_trust_relationship'
        
        if '/api/feeds/' in path:
            if '/publish/' in path:
                return 'publish_feed'
            elif request.method == 'POST':
                return 'create_feed'
            elif request.method == 'PUT' or request.method == 'PATCH':
                return 'update_feed'
            elif request.method == 'DELETE':
                return 'delete_feed'
                
        return None
    
    def get_organization(self, user):
        """
        Get the organization associated with the authenticated user.
        """
        if user.is_anonymous:
            return None
            
        # In a real implementation, you would link users to organizations
        # For now, we'll use a dummy approach to get an organization
        try:
            return Organization.objects.filter(
                id__in=user.groups.values_list('name', flat=True)
            ).first()
        except:
            return None
    
    def extract_object_id(self, path, action_type):
        """
        Extract object ID from the request path based on action type.
        """
        if action_type in ['get_collection', 'get_collection_objects', 'add_collection_objects', 'get_manifest']:
            # Extract collection ID
            match = re.search(r'/collections/([^/]+)', path)
            if match:
                return match.group(1)
        
        elif action_type == 'get_object':
            # Extract object ID
            match = re.search(r'/objects/([^/]+)', path)
            if match:
                return match.group(1)
                
        return None
    
    def extract_details(self, request, action_type):
        """
        Extract relevant details from the request based on action type.
        """
        details = {}
        
        # Add query parameters for GET requests
        if request.method == 'GET' and request.GET:
            details['query_params'] = dict(request.GET)
        
        # Add request body for POST/PUT/PATCH requests
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
            try:
                # Only include top-level structure, not full objects for STIX
                if request.content_type and 'json' in request.content_type:
                    body = json.loads(request.body)
                    # For STIX objects, just include count
                    if 'objects' in body and isinstance(body['objects'], list):
                        details['object_count'] = len(body['objects'])
                        # Include types of objects
                        object_types = {}
                        for obj in body['objects']:
                            if 'type' in obj:
                                object_type = obj['type']
                                object_types[object_type] = object_types.get(object_type, 0) + 1
                        details['object_types'] = object_types
            except:
                pass
        
        # Extract URL info
        path_info = request.META.get('PATH_INFO', '')
        if action_type == 'get_collection':
            match = re.search(r'/collections/([^/]+)', path_info)
            if match:
                details['collection_id'] = match.group(1)
        
        elif action_type == 'get_object':
            match = re.search(r'/collections/([^/]+)/objects/([^/]+)', path_info)
            if match:
                details['collection_id'] = match.group(1)
                details['object_id'] = match.group(2)
        
        return details
    
    def process_response(self, request, response):
        """
        Process response and log the activity if needed.
        """
        # Skip logging if disabled in settings
        if not getattr(settings, 'AUDIT_SETTINGS', {}).get('ENABLED', True):
            return response
            
        # Only log actions for authenticated users
        if not hasattr(request, 'user') or request.user.is_anonymous:
            return response
        
        # Calculate processing time
        if hasattr(request, 'start_time'):
            processing_time = time.time() - request.start_time
        else:
            processing_time = None
        
        # Determine action type
        path = request.path
        action_type = self.get_action_type(request, path)
        
        # Skip if not a tracked action
        if not action_type:
            return response
        
        # Get organization
        organization = self.get_organization(request.user)
        
        # Extract object ID
        object_id = self.extract_object_id(path, action_type)
        
        # Extract details
        details = self.extract_details(request, action_type)
        
        # Add response info to details
        details['status_code'] = response.status_code
        if processing_time:
            details['processing_time'] = processing_time
        
        # Create audit log entry
        try:
            AuditLog.objects.create(
                user=request.user,
                organization=organization,
                action_type=action_type,
                object_id=object_id,
                details=details,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
        except Exception as e:
            # Log error but don't disrupt the response
            if settings.DEBUG:
                print(f"Error creating audit log: {e}")
        
        return response