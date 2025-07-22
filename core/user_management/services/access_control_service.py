from typing import Dict, List, Optional, Tuple, Any
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from ..models import CustomUser, Organization
from core.trust.models import TrustRelationship, TrustLevel, TrustGroup
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import time

class AccessControlService:
    """Service for managing access control and permissions"""
    
    ROLE_PERMISSIONS = {
        'viewer': ['view_organization', 'view_user'],
        'publisher': ['view_organization', 'view_user', 'create_trust_relationship', 'view_trust_relationship'],
        'admin': [
            'view_organization', 'view_user', 'create_trust_relationship', 'view_trust_relationship',
            'create_organization', 'create_user', 'delete_user', 'update_user', 'manage_trust_groups'
        ]
    }
    
    def user_has_permission(self, user, permission):
        """Check if user has specific permission"""
        if not user or not hasattr(user, 'role'):
            return False
        
        user_permissions = self.ROLE_PERMISSIONS.get(user.role, [])
        return permission in user_permissions
    
    def can_create_organization(self, user):
        """Check if user can create organizations"""
        return self.user_has_permission(user, 'create_organization')
    
    def can_manage_trust_groups(self, user):
        """Check if user can manage trust groups"""
        return self.user_has_permission(user, 'manage_trust_groups')
    
    def __init__(self):
        self._role_permissions = {
            'viewer': {
                'view_data',
                'can_view_threat_intelligence'
            },
            'publisher': {
                'view_data',
                'create_data',
                'create_trust_relationships',
                'can_publish_threat_intelligence',
                'can_view_threat_intelligence',
                'can_manage_organization_users',
                'can_create_organization_users',
                'can_manage_trust_relationships',
                'can_view_organization_analytics'
            },
            'admin': {
                'manage_users',
                'manage_organizations', 
                'can_manage_organizations',
                'delete_users',
                'view_all_data',
                'create_organizations',
                'create_users',
                'manage_trust_relationships',
                'can_create_organization_users',
                'can_manage_organization_users',
                'can_publish_threat_intelligence',
                'can_view_threat_intelligence',
                'can_manage_trust_relationships',
                'can_view_system_analytics',
                'can_manage_all_users',
                'can_create_organizations'
            },
            'BlueVisionAdmin': {
                'manage_users',
                'manage_organizations', 
                'can_manage_organizations',
                'delete_users',
                'view_all_data',
                'create_organizations',
                'create_users',
                'manage_trust_relationships',
                'can_create_organization_users',
                'can_manage_organization_users',
                'can_publish_threat_intelligence',
                'can_view_threat_intelligence',
                'can_manage_trust_relationships',
                'can_create_organizations',
                'can_view_system_analytics',
                'can_manage_all_users',
                'can_manage_all_organizations'
            }
        }

    def get_user_permissions(self, user):
        """Get all permissions for a user based on their role"""
        if not user:
            return set()
            
        role = user.role
        permissions = set()
        
        # Add role's direct permissions
        if role in self._role_permissions:
            permissions.update(self._role_permissions[role])
            
        # Add inherited permissions based on role hierarchy
        if role == 'BlueVisionAdmin':
            permissions.update(self._role_permissions['admin'])
            permissions.update(self._role_permissions['publisher'])
            permissions.update(self._role_permissions['viewer'])
        elif role == 'admin':
            permissions.update(self._role_permissions['publisher'])
            permissions.update(self._role_permissions['viewer'])
        elif role == 'publisher':
            permissions.update(self._role_permissions['viewer'])
            
        return permissions

    def has_permission(self, user, permission):
        """Check if user has specific permission"""
        return permission in self.get_user_permissions(user)

    def can_manage_user(self, managing_user, target_user):
        """Check if user can manage another user"""
        if not managing_user:
            return False
            
        # Users can manage themselves
        if managing_user == target_user:
            return True
            
        # BlueVision Admins can manage all users
        if managing_user.role == 'BlueVisionAdmin':
            return True
            
        # Superusers can manage all users
        if getattr(managing_user, 'is_superuser', False):
            return True
            
        # Admins can manage all users
        if managing_user.role == 'admin':
            return True
            
        # Publishers can manage viewers
        if managing_user.role == 'publisher' and target_user.role == 'viewer':
            return True
            
        return False

    def can_create_user_with_role(self, creating_user, role, organization=None):
        """Check if user can create another user with specified role"""
        # Allow anonymous registration for viewer role only
        if not creating_user:
            return role == 'viewer'
            
        if creating_user.role == 'BlueVisionAdmin':
            return True
            
        if creating_user.role == 'admin':
            return True
            
        if creating_user.role == 'publisher' and role in ['viewer', 'publisher']:
            return True
            
        return False

    def require_permission(self, user, permission):
        """Require specific permission or raise PermissionDenied"""
        if not self.has_permission(user, permission):
            raise PermissionDenied(f"User {user} does not have permission: {permission}")
    
    def get_accessible_organizations(self, user):
        """Get organizations accessible to the user"""
        accessible = []
        
        # User's own organization is always accessible
        if user.organization:
            accessible.append(user.organization)
        
        # BlueVisionAdmin can access all organizations
        if user.role == 'BlueVisionAdmin':
            all_orgs = Organization.objects.exclude(id=user.organization.id if user.organization else None)
            accessible.extend(all_orgs)
        elif user.organization:
            # Get organizations through trust relationships (only if user has organization)
            try:
                relationships = TrustRelationship.objects.filter(
                    source_organization=user.organization,
                    is_active=True,
                    status='active'
                )
                
                for rel in relationships:
                    try:
                        # target_organization should be an Organization object
                        if rel.target_organization not in accessible:
                            accessible.append(rel.target_organization)
                    except Exception:
                        continue
            except Exception:
                pass  # Handle gracefully in case of model issues
        
        return accessible
    
    def get_trust_aware_data_access(self, user, data_type, source_organization):
        """Get trust-aware data access information"""
        access_info = {
            'can_access': False,
            'access_level': 'none',
            'anonymization_level': 'full',
            'restrictions': []
        }
        
        # User's own organization data is fully accessible
        if source_organization == user.organization:
            access_info.update({
                'can_access': True,
                'access_level': 'full',
                'anonymization_level': 'none'
            })
            return access_info
        
        # Check trust relationships
        try:
            relationship = TrustRelationship.objects.filter(
                source_organization=user.organization,
                target_organization=source_organization,
                is_active=True,
                status='active'
            ).first()
            
            if relationship:
                access_info.update({
                    'can_access': True,
                    'access_level': relationship.access_level,
                    'anonymization_level': relationship.anonymization_level
                })
        except Exception:
            pass  # Handle gracefully
        
        return access_info
    
    def can_access_organization(self, user, organization):
        """Check if user can access an organization"""
        if not user or not organization:
            return False
            
        # User can access their own organization
        if user.organization == organization:
            return True
            
        # BlueVisionAdmin can access all organizations
        if user.role == 'BlueVisionAdmin':
            return True
            
        # Superusers can access all organizations
        if getattr(user, 'is_superuser', False):
            return True
            
        # Check trust relationships - only if user has an organization
        if user.organization:
            try:
                from core.trust.models import TrustRelationship
                relationship = TrustRelationship.objects.filter(
                    source_organization=user.organization,
                    target_organization=organization,
                    is_active=True,
                    status='active'
                ).exists()
                return relationship
            except Exception:
                # If trust models are not available or error occurs, allow basic access
                return False
        
        return False
    
    def get_role_hierarchy_level(self, role):
        """Get the hierarchy level of a role"""
        hierarchy = {
            'viewer': 1,
            'publisher': 2,
            'admin': 3,
            'BlueVisionAdmin': 4
        }
        return hierarchy.get(role, 0)

class AuditMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.audit_service = self.get_audit_service()
        super().__init__(get_response)
    
    def get_audit_service(self):
        """Get or create audit service instance"""
        try:
            from core.audit.services.audit_service import AuditService
            return AuditService()
        except ImportError:
            return logging.getLogger('audit')
    
    def process_request(self, request):
        if request.path.startswith('/api/'):
            request._audit_start_time = time.time()
            if hasattr(self.audit_service, 'log_request_start'):
                self.audit_service.log_request_start(request)
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_audit_start_time'):
            duration = time.time() - request._audit_start_time
            if hasattr(self.audit_service, 'log_request_complete'):
                self.audit_service.log_request_complete(request, response, duration)
        return response
    
    def process_exception(self, request, exception):
        if hasattr(request, '_audit_start_time'):
            duration = time.time() - request._audit_start_time
            if hasattr(self.audit_service, 'log_request_exception'):
                self.audit_service.log_request_exception(request, exception, duration)
        return None