"""
Trust Management Permissions

Comprehensive permission system for trust relationship operations
based on Django REST Framework permissions and custom authorization logic.
"""

from typing import Dict, List, Any, Optional
from django.core.exceptions import PermissionDenied
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from ..models import TrustRelationship, TrustGroup, TrustGroupMembership, TrustLevel
from ..services.trust_service import TrustService


class BaseTrustPermission(permissions.BasePermission):
    """
    Base permission class for trust management operations.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user has permission to access the view.
        """
        # Require authentication
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has valid organization
        if not hasattr(request.user, 'organization') or not request.user.organization:
            return False
        
        return True
    
    def get_user_organization(self, request: Request) -> Optional[str]:
        """
        Get the organization UUID for the requesting user.
        """
        if (hasattr(request.user, 'organization') and 
            request.user.organization and 
            hasattr(request.user.organization, 'id')):
            return str(request.user.organization.id)
        return None


class TrustRelationshipPermission(BaseTrustPermission):
    """
    Permission class for trust relationship operations.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user has permission for trust relationship operations.
        """
        if not super().has_permission(request, view):
            return False
        
        # Check user role for different operations
        if request.method == 'POST':  # Create relationship
            return self.can_create_relationships(request)
        elif request.method in ['PUT', 'PATCH']:  # Modify relationship
            return self.can_modify_relationships(request)
        elif request.method == 'DELETE':  # Revoke relationship
            return self.can_revoke_relationships(request)
        elif request.method == 'GET':  # View relationships
            return self.can_view_relationships(request)
        
        return False
    
    def has_object_permission(self, request: Request, view: APIView, obj: TrustRelationship) -> bool:
        """
        Check if user has permission for specific trust relationship.
        """
        user_org = self.get_user_organization(request)
        if not user_org:
            return False
        
        # User must be part of the relationship
        if (obj.source_organization != user_org and 
            obj.target_organization != user_org):
            return False
        
        # Check operation-specific permissions
        if request.method == 'GET':
            return True  # Can view if part of relationship
        elif request.method in ['PUT', 'PATCH']:
            return self.can_modify_specific_relationship(request, obj)
        elif request.method == 'DELETE':
            return self.can_revoke_specific_relationship(request, obj)
        
        return False
    
    def can_create_relationships(self, request: Request) -> bool:
        """
        Check if user can create trust relationships.
        """
        # Must be admin or publisher
        return (hasattr(request.user, 'role') and 
                request.user.role in ['admin', 'system_admin', 'publisher'])
    
    def can_modify_relationships(self, request: Request) -> bool:
        """
        Check if user can modify trust relationships.
        """
        # Must be admin or publisher
        return (hasattr(request.user, 'role') and 
                request.user.role in ['admin', 'system_admin', 'publisher'])
    
    def can_revoke_relationships(self, request: Request) -> bool:
        """
        Check if user can revoke trust relationships.
        """
        # Must be admin
        return (hasattr(request.user, 'role') and 
                request.user.role in ['admin', 'system_admin'])
    
    def can_view_relationships(self, request: Request) -> bool:
        """
        Check if user can view trust relationships.
        """
        # All authenticated users can view (filtered by organization)
        return True
    
    def can_modify_specific_relationship(self, request: Request, obj: TrustRelationship) -> bool:
        """
        Check if user can modify specific relationship.
        """
        user_org = self.get_user_organization(request)
        
        # Can only approve if pending and user is admin
        if obj.status == 'pending':
            return (hasattr(request.user, 'role') and 
                    request.user.role in ['admin', 'system_admin'])
        
        # Can only modify active relationships in limited ways
        if obj.status == 'active':
            # Only allow trust level updates by admins
            return (hasattr(request.user, 'role') and 
                    request.user.role in ['admin', 'system_admin'])
        
        return False
    
    def can_revoke_specific_relationship(self, request: Request, obj: TrustRelationship) -> bool:
        """
        Check if user can revoke specific relationship.
        """
        # Must be admin and part of relationship
        return (hasattr(request.user, 'role') and 
                request.user.role in ['admin', 'system_admin'])


class TrustGroupPermission(BaseTrustPermission):
    """
    Permission class for trust group operations.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user has permission for trust group operations.
        """
        if not super().has_permission(request, view):
            return False
        
        if request.method == 'POST':  # Create group
            return self.can_create_groups(request)
        elif request.method in ['PUT', 'PATCH']:  # Modify group
            return self.can_modify_groups(request)
        elif request.method == 'DELETE':  # Delete group
            return self.can_delete_groups(request)
        elif request.method == 'GET':  # View groups
            return self.can_view_groups(request)
        
        return False
    
    def has_object_permission(self, request: Request, view: APIView, obj: TrustGroup) -> bool:
        """
        Check if user has permission for specific trust group.
        """
        user_org = self.get_user_organization(request)
        if not user_org:
            return False
        
        # Check if user's organization is a member or admin
        membership = TrustGroupMembership.objects.filter(
            trust_group=obj,
            organization=user_org,
            is_active=True
        ).first()
        
        if request.method == 'GET':
            # Can view if public group or member
            return obj.is_public or membership is not None
        elif request.method in ['PUT', 'PATCH']:
            # Can modify if administrator
            return obj.can_administer(user_org)
        elif request.method == 'DELETE':
            # Can delete if administrator
            return obj.can_administer(user_org)
        
        return False
    
    def can_create_groups(self, request: Request) -> bool:
        """
        Check if user can create trust groups.
        """
        # Must be admin or publisher
        return (hasattr(request.user, 'role') and 
                request.user.role in ['admin', 'system_admin', 'publisher'])
    
    def can_modify_groups(self, request: Request) -> bool:
        """
        Check if user can modify trust groups.
        """
        # Must be admin (specific group admin checked in object permission)
        return (hasattr(request.user, 'role') and 
                request.user.role in ['admin', 'system_admin'])
    
    def can_delete_groups(self, request: Request) -> bool:
        """
        Check if user can delete trust groups.
        """
        # Must be system admin
        return (hasattr(request.user, 'role') and 
                request.user.role == 'system_admin')
    
    def can_view_groups(self, request: Request) -> bool:
        """
        Check if user can view trust groups.
        """
        # All authenticated users can view (filtered appropriately)
        return True


class TrustGroupMembershipPermission(BaseTrustPermission):
    """
    Permission class for trust group membership operations.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user has permission for membership operations.
        """
        if not super().has_permission(request, view):
            return False
        
        if request.method == 'POST':  # Join group
            return self.can_join_groups(request)
        elif request.method in ['PUT', 'PATCH']:  # Modify membership
            return self.can_modify_membership(request)
        elif request.method == 'DELETE':  # Leave group
            return self.can_leave_groups(request)
        elif request.method == 'GET':  # View memberships
            return self.can_view_memberships(request)
        
        return False
    
    def has_object_permission(self, request: Request, view: APIView, obj: TrustGroupMembership) -> bool:
        """
        Check if user has permission for specific membership.
        """
        user_org = self.get_user_organization(request)
        if not user_org:
            return False
        
        if request.method == 'GET':
            # Can view if own membership or group admin
            return (obj.organization == user_org or 
                    obj.trust_group.can_administer(user_org))
        elif request.method in ['PUT', 'PATCH']:
            # Can modify if group admin or own membership (limited)
            return self.can_modify_specific_membership(request, obj)
        elif request.method == 'DELETE':
            # Can delete if own membership or group admin
            return (obj.organization == user_org or 
                    obj.trust_group.can_administer(user_org))
        
        return False
    
    def can_join_groups(self, request: Request) -> bool:
        """
        Check if user can join trust groups.
        """
        # All authenticated users can request to join groups
        return True
    
    def can_modify_membership(self, request: Request) -> bool:
        """
        Check if user can modify memberships.
        """
        # Must be admin to modify others' memberships
        return (hasattr(request.user, 'role') and 
                request.user.role in ['admin', 'system_admin'])
    
    def can_leave_groups(self, request: Request) -> bool:
        """
        Check if user can leave groups.
        """
        # All members can leave groups
        return True
    
    def can_view_memberships(self, request: Request) -> bool:
        """
        Check if user can view memberships.
        """
        # All authenticated users can view (filtered appropriately)
        return True
    
    def can_modify_specific_membership(self, request: Request, obj: TrustGroupMembership) -> bool:
        """
        Check if user can modify specific membership.
        """
        user_org = self.get_user_organization(request)
        
        # Group administrators can modify any membership
        if obj.trust_group.can_administer(user_org):
            return True
        
        # Users can only modify their own membership in limited ways
        if obj.organization == user_org:
            # Can only change certain fields like preferences
            allowed_fields = ['preferences', 'notification_settings']
            return any(field in request.data for field in allowed_fields)
        
        return False


class IntelligenceAccessPermission(BaseTrustPermission):
    """
    Permission class for intelligence access operations.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user has permission for intelligence access.
        """
        if not super().has_permission(request, view):
            return False
        
        # Must be analyst or above
        return (hasattr(request.user, 'role') and 
                request.user.role in ['analyst', 'publisher', 'admin', 'system_admin'])
    
    def can_access_intelligence(
        self, 
        request: Request, 
        intelligence_owner: str, 
        required_access_level: str = 'read'
    ) -> bool:
        """
        Check if user can access specific intelligence.
        """
        user_org = self.get_user_organization(request)
        if not user_org:
            return False
        
        # Check trust-based access
        can_access, reason, relationship = TrustService.can_access_intelligence(
            requesting_org=user_org,
            intelligence_owner=intelligence_owner,
            required_access_level=required_access_level
        )
        
        return can_access
    
    def get_access_level(self, request: Request, intelligence_owner: str) -> str:
        """
        Get the access level for user to specific intelligence.
        """
        user_org = self.get_user_organization(request)
        if not user_org:
            return 'none'
        
        trust_info = TrustService.check_trust_level(user_org, intelligence_owner)
        if not trust_info:
            return 'none'
        
        trust_level, relationship = trust_info
        return relationship.get_effective_access_level()


class SystemAdminPermission(BaseTrustPermission):
    """
    Permission class for system administration operations.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user has system admin permissions.
        """
        if not super().has_permission(request, view):
            return False
        
        # Must be system admin
        return (hasattr(request.user, 'role') and 
                request.user.role == 'system_admin')


def check_permission(permission_type: str, request: Request, **kwargs) -> bool:
    """
    Convenience function to check permissions.
    
    Args:
        permission_type: Type of permission to check
        request: HTTP request object
        **kwargs: Additional parameters for permission check
        
    Returns:
        Boolean indicating if permission is granted
    """
    permission_classes = {
        'trust_relationship': TrustRelationshipPermission,
        'trust_group': TrustGroupPermission,
        'trust_group_membership': TrustGroupMembershipPermission,
        'intelligence_access': IntelligenceAccessPermission,
        'system_admin': SystemAdminPermission,
    }
    
    permission_class = permission_classes.get(permission_type)
    if not permission_class:
        return False
    
    permission = permission_class()
    
    # Create a mock view for permission checking
    class MockView(APIView):
        pass
    
    view = MockView()
    
    return permission.has_permission(request, view)


def require_permission(permission_type: str, **permission_kwargs):
    """
    Decorator to require specific permissions for view functions.
    
    Args:
        permission_type: Type of permission required
        **permission_kwargs: Additional parameters for permission check
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not check_permission(permission_type, request, **permission_kwargs):
                raise PermissionDenied(
                    f"Insufficient permissions for {permission_type} operation"
                )
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


class PermissionChecker:
    """
    Utility class for checking permissions in service layer.
    """
    
    def __init__(self, user_org: str, user_role: str = None):
        self.user_org = user_org
        self.user_role = user_role
    
    def can_create_relationship(self, target_org: str) -> bool:
        """
        Check if user can create relationship with target organization.
        """
        if not self.user_role or self.user_role not in ['admin', 'system_admin', 'publisher']:
            return False
        
        # Cannot create relationship with self
        if self.user_org == target_org:
            return False
        
        return True
    
    def can_approve_relationship(self, relationship: TrustRelationship) -> bool:
        """
        Check if user can approve specific relationship.
        """
        if not self.user_role or self.user_role not in ['admin', 'system_admin']:
            return False
        
        # Must be part of the relationship
        if (relationship.source_organization != self.user_org and 
            relationship.target_organization != self.user_org):
            return False
        
        # Check if already approved
        if relationship.source_organization == self.user_org:
            return not relationship.approved_by_source
        else:
            return not relationship.approved_by_target
    
    def can_revoke_relationship(self, relationship: TrustRelationship) -> bool:
        """
        Check if user can revoke specific relationship.
        """
        if not self.user_role or self.user_role not in ['admin', 'system_admin']:
            return False
        
        # Must be part of the relationship
        if (relationship.source_organization != self.user_org and 
            relationship.target_organization != self.user_org):
            return False
        
        # Cannot revoke already revoked relationships
        return relationship.status not in ['revoked', 'expired']
    
    def can_administer_group(self, group: TrustGroup) -> bool:
        """
        Check if user can administer trust group.
        """
        return group.can_administer(self.user_org)
    
    def can_access_intelligence(
        self, 
        intelligence_owner: str, 
        required_access_level: str = 'read'
    ) -> bool:
        """
        Check if user can access intelligence from owner.
        """
        can_access, _, _ = TrustService.can_access_intelligence(
            requesting_org=self.user_org,
            intelligence_owner=intelligence_owner,
            required_access_level=required_access_level
        )
        
        return can_access