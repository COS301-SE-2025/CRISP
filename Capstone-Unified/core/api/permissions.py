"""
Unified Permission Classes for CRISP API Integration

These permission classes work across both Core and Trust systems, preserving ALL
existing authentication methods while providing unified access control.
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class UnifiedAuthentication(BasePermission):
    """
    Base permission class that handles both JWT and session authentication.
    Preserves ALL existing authentication methods from both systems.
    """
    
    def has_permission(self, request, view):
        # Allow access if user is authenticated through any method
        return request.user and request.user.is_authenticated
    
    def authenticate_request(self, request, view):
        """Enhance request with unified authentication context"""
        if hasattr(request.user, 'organization') and request.user.organization:
            request.user_organization = request.user.organization
        else:
            request.user_organization = None
        
        # Add user permissions context
        if hasattr(request.user, 'role'):
            request.user_role = request.user.role
        else:
            request.user_role = 'staff' if request.user.is_staff else 'user'


class IsPublisherOrAdmin(UnifiedAuthentication):
    """
    Permission for Publisher role users and administrators.
    Preserves existing Trust system role-based access control.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        user = request.user
        
        # BlueVisionAdmin has full access
        if hasattr(user, 'role') and user.role == 'BlueVisionAdmin':
            return True
        
        # Django superuser has full access (Core system compatibility)
        if user.is_superuser:
            return True
        
        # Publisher role has access
        if hasattr(user, 'role') and user.role == 'publisher':
            return True
        
        # Staff users have access (Core system compatibility)
        if user.is_staff:
            return True
        
        return False


class IsAdminOnly(UnifiedAuthentication):
    """
    Permission for administrators only.
    Supports both BlueVisionAdmin (Trust) and Django superuser (Core) roles.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        user = request.user
        
        # BlueVisionAdmin has full access
        if hasattr(user, 'role') and user.role == 'BlueVisionAdmin':
            return True
        
        # Django superuser has full access (Core system compatibility)
        if user.is_superuser:
            return True
        
        return False


class IsViewerOrAbove(UnifiedAuthentication):
    """
    Permission for Viewer role and above.
    Allows access to any authenticated user with proper role.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        user = request.user
        
        # All Trust system roles have at least viewer access
        if hasattr(user, 'role') and user.role in ['viewer', 'publisher', 'BlueVisionAdmin']:
            return True
        
        # Django authenticated users have viewer access (Core system compatibility)
        if user.is_authenticated:
            return True
        
        return False


class OrganizationBasedPermission(UnifiedAuthentication):
    """
    Permission class that enforces organization-based access control.
    Users can only access data from their own organization unless they're admins.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        user = request.user
        
        # BlueVisionAdmins and superusers can access all organization data
        if (hasattr(user, 'role') and user.role == 'BlueVisionAdmin') or user.is_superuser:
            return True
        
        # Regular users need an organization
        if hasattr(user, 'organization') and user.organization:
            return True
        
        # Core system users without organization get limited access
        return user.is_staff or user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        user = request.user
        
        # BlueVisionAdmins and superusers can access all objects
        if (hasattr(user, 'role') and user.role == 'BlueVisionAdmin') or user.is_superuser:
            return True
        
        # Check if object has organization relationship
        if hasattr(obj, 'organization'):
            if user.organization and obj.organization == user.organization:
                return True
        
        # Check if object has source_organization relationship
        if hasattr(obj, 'source_organization'):
            if user.organization and obj.source_organization == user.organization:
                return True
        
        # Check if object has owner relationship
        if hasattr(obj, 'owner'):
            if user.organization and obj.owner == user.organization:
                return True
        
        # For Core system compatibility, allow staff access
        if user.is_staff:
            return True
        
        return False


class ThreatIntelligencePermission(OrganizationBasedPermission):
    """
    Specialized permission for threat intelligence data.
    Preserves Core system threat feed access patterns while adding Trust system controls.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Read access for viewers and above
        if request.method in permissions.SAFE_METHODS:
            return self._has_read_permission(request.user)
        
        # Write access for publishers and above
        return self._has_write_permission(request.user)
    
    def _has_read_permission(self, user):
        """Check read permissions for threat intelligence"""
        # All authenticated users can read within their organization
        if hasattr(user, 'role') and user.role in ['viewer', 'publisher', 'BlueVisionAdmin']:
            return True
        
        # Core system users can read
        if user.is_authenticated:
            return True
        
        return False
    
    def _has_write_permission(self, user):
        """Check write permissions for threat intelligence"""
        # Publishers and admins can write
        if hasattr(user, 'role') and user.role in ['publisher', 'BlueVisionAdmin']:
            return True
        
        # Core system staff can write
        if user.is_staff or user.is_superuser:
            return True
        
        return False


class TrustManagementPermission(UnifiedAuthentication):
    """
    Permission for trust relationship management.
    Only users with trust management capabilities can modify trust relationships.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        user = request.user
        
        # Read access for anyone with an organization
        if request.method in permissions.SAFE_METHODS:
            return (hasattr(user, 'organization') and user.organization) or user.is_superuser
        
        # Write access requires trust management permission
        if hasattr(user, 'can_manage_trust_relationships') and user.can_manage_trust_relationships:
            return True
        
        # BlueVisionAdmins can manage trust
        if hasattr(user, 'role') and user.role == 'BlueVisionAdmin':
            return True
        
        # Django superusers can manage trust
        if user.is_superuser:
            return True
        
        return False


class UserManagementPermission(OrganizationBasedPermission):
    """
    Permission for user management within organizations.
    Publishers can manage users in their organization, admins can manage all users.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        user = request.user
        
        # Read access for all authenticated users (to see their own data)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access for publishers and admins
        if hasattr(user, 'role') and user.role in ['publisher', 'BlueVisionAdmin']:
            return True
        
        # Core system staff can manage users
        if user.is_staff or user.is_superuser:
            return True
        
        return False


# Convenience permission classes for common use cases
IsAuthenticated = UnifiedAuthentication
IsPublisher = IsPublisherOrAdmin  
IsAdmin = IsAdminOnly
IsViewer = IsViewerOrAbove