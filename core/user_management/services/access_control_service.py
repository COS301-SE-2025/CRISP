from typing import Dict, List, Optional, Tuple, Any
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from ..models import CustomUser, Organization
from core.trust.models import TrustRelationship, TrustLevel, TrustGroup
import logging

logger = logging.getLogger(__name__)


class AccessControlService:
    """
    Comprehensive access control service that integrates user roles with trust levels.
    Implements role-based access control (RBAC) with trust-aware permissions.
    """
    
    # Define role hierarchy (higher number = more permissions)
    ROLE_HIERARCHY = {
        'viewer': 1,
        'publisher': 2,
        'BlueVisionAdmin': 3
    }
    
    # Define base permissions for each role
    ROLE_PERMISSIONS = {
        'viewer': {
            'can_view_threat_intelligence',
            'can_view_own_organization_data',
            'can_update_own_profile',
            'can_view_threat_feeds',
            'can_export_threat_data',
        },
        'publisher': {
            'can_view_threat_intelligence',
            'can_view_own_organization_data',
            'can_update_own_profile',
            'can_view_threat_feeds',
            'can_export_threat_data',
            'can_publish_threat_intelligence',
            'can_manage_organization_users',
            'can_create_organization_users',
            'can_manage_trust_relationships',
            'can_view_organization_analytics',
            'can_configure_threat_feeds',
            'can_manage_threat_sharing_policies',
        },
        'BlueVisionAdmin': {
            'can_view_threat_intelligence',
            'can_view_own_organization_data',
            'can_update_own_profile',
            'can_view_threat_feeds',
            'can_export_threat_data',
            'can_publish_threat_intelligence',
            'can_manage_organization_users',
            'can_create_organization_users',
            'can_manage_trust_relationships',
            'can_view_organization_analytics',
            'can_configure_threat_feeds',
            'can_manage_threat_sharing_policies',
            'can_view_all_organizations',
            'can_manage_all_organizations',
            'can_create_organizations',
            'can_manage_all_users',
            'can_view_system_analytics',
            'can_manage_system_settings',
            'can_manage_global_trust_policies',
            'can_access_admin_interface',
            'can_manage_trust_groups',
            'can_override_trust_decisions',
        }
    }
    
    def __init__(self):
        """Initialize the access control service"""
        self.trust_service = None  # Will be imported when needed to avoid circular imports
    
    def _get_trust_service(self):
        """Lazy load trust service to avoid circular imports"""
        if not self.trust_service:
            from core.trust.services.trust_service import TrustService
            self.trust_service = TrustService()
        return self.trust_service
    
    def has_permission(self, user: CustomUser, permission: str, 
                      resource_organization: Optional[Organization] = None,
                      resource_context: Optional[Dict] = None) -> bool:
        """
        Check if user has a specific permission, considering trust relationships.
        
        Args:
            user: User to check permissions for
            permission: Permission string to check
            resource_organization: Organization that owns the resource (optional)
            resource_context: Additional context about the resource (optional)
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        if isinstance(user, AnonymousUser) or not user.is_active:
            return False
        
        # Check if user account is locked
        if user.is_account_locked:
            return False
        
        # Get base permissions for user role
        base_permissions = self.ROLE_PERMISSIONS.get(user.role, set())
        
        # Check if user has the base permission
        if permission not in base_permissions:
            return False
        
        # If no resource organization specified, check base permission only
        if not resource_organization:
            return True
        
        # Check organization-specific access
        return self._check_organization_access(
            user, permission, resource_organization, resource_context
        )
    
    def _check_organization_access(self, user: CustomUser, permission: str,
                                 resource_organization: Organization,
                                 resource_context: Optional[Dict] = None) -> bool:
        """
        Check if user can access resources from a specific organization.
        
        Args:
            user: User requesting access
            permission: Permission being checked
            resource_organization: Organization that owns the resource
            resource_context: Additional context about the resource
            
        Returns:
            bool: True if access allowed, False otherwise
        """
        # Users always have access to their own organization
        if user.organization.id == resource_organization.id:
            return True
        
        # BlueVision admins have access to all organizations
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Check trust relationships for cross-organization access
        return self._check_trust_based_access(
            user, permission, resource_organization, resource_context
        )
    
    def _check_trust_based_access(self, user: CustomUser, permission: str,
                                resource_organization: Organization,
                                resource_context: Optional[Dict] = None) -> bool:
        """
        Check access based on trust relationships between organizations.
        
        Args:
            user: User requesting access
            permission: Permission being checked
            resource_organization: Organization that owns the resource
            resource_context: Additional context about the resource
            
        Returns:
            bool: True if access allowed through trust, False otherwise
        """
        try:
            trust_service = self._get_trust_service()
            
            # Get effective trust relationships
            trust_relationships = TrustRelationship.objects.filter(
                source_organization=user.organization,
                target_organization=resource_organization,
                is_active=True,
                status='active'
            ).select_related('trust_level')
            
            if not trust_relationships.exists():
                return False
            
            # Check if any trust relationship allows this permission
            for relationship in trust_relationships:
                if self._trust_allows_permission(relationship, permission, resource_context):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trust-based access: {str(e)}")
            return False
    
    def _trust_allows_permission(self, trust_relationship: TrustRelationship,
                               permission: str, resource_context: Optional[Dict] = None) -> bool:
        """
        Check if a trust relationship allows a specific permission.
        
        Args:
            trust_relationship: Trust relationship to check
            permission: Permission being requested
            resource_context: Additional context about the resource
            
        Returns:
            bool: True if trust relationship allows permission
        """
        trust_level = trust_relationship.trust_level
        access_level = trust_relationship.get_effective_access_level()
        
        # Map permissions to required access levels
        permission_access_requirements = {
            'can_view_threat_intelligence': ['read', 'subscribe', 'contribute', 'full'],
            'can_view_threat_feeds': ['read', 'subscribe', 'contribute', 'full'],
            'can_export_threat_data': ['subscribe', 'contribute', 'full'],
            'can_publish_threat_intelligence': ['contribute', 'full'],
            'can_manage_trust_relationships': ['full'],
        }
        
        required_access_levels = permission_access_requirements.get(permission, ['full'])
        
        if access_level not in required_access_levels:
            return False
        
        # Check trust level requirements
        if trust_level.level == 'restricted' and permission.startswith('can_publish'):
            return False
        
        # Check additional constraints from sharing policies
        if resource_context:
            return self._check_sharing_policy_constraints(
                trust_relationship, permission, resource_context
            )
        
        return True
    
    def _check_sharing_policy_constraints(self, trust_relationship: TrustRelationship,
                                        permission: str, resource_context: Dict) -> bool:
        """
        Check sharing policy constraints for the permission.
        
        Args:
            trust_relationship: Trust relationship to check
            permission: Permission being requested
            resource_context: Context about the resource
            
        Returns:
            bool: True if sharing policies allow access
        """
        sharing_preferences = trust_relationship.sharing_preferences
        
        # Check TLP (Traffic Light Protocol) constraints
        resource_tlp = resource_context.get('tlp_level', 'white')
        max_tlp = sharing_preferences.get('max_tlp_level', 'green')
        
        tlp_hierarchy = {'white': 0, 'green': 1, 'amber': 2, 'red': 3}
        
        if tlp_hierarchy.get(resource_tlp, 0) > tlp_hierarchy.get(max_tlp, 1):
            return False
        
        # Check temporal constraints
        max_age_days = sharing_preferences.get('max_age_days')
        if max_age_days and resource_context.get('age_days', 0) > max_age_days:
            return False
        
        # Check STIX object type constraints
        resource_type = resource_context.get('stix_type')
        if resource_type:
            blocked_types = sharing_preferences.get('blocked_stix_types', [])
            allowed_types = sharing_preferences.get('allowed_stix_types', [])
            
            if resource_type in blocked_types:
                return False
            
            if allowed_types and resource_type not in allowed_types:
                return False
        
        return True
    
    def get_user_permissions(self, user: CustomUser) -> set:
        """
        Get all permissions for a user.
        
        Args:
            user: User to get permissions for
            
        Returns:
            set: Set of permission strings
        """
        if isinstance(user, AnonymousUser) or not user.is_active:
            return set()
        
        return self.ROLE_PERMISSIONS.get(user.role, set()).copy()
    
    def get_accessible_organizations(self, user: CustomUser) -> List[Organization]:
        """
        Get list of organizations the user can access.
        
        Args:
            user: User to check access for
            
        Returns:
            List[Organization]: Organizations user can access
        """
        if isinstance(user, AnonymousUser) or not user.is_active:
            return []
        
        accessible_orgs = [user.organization]
        
        # BlueVision admins can access all organizations
        if user.role == 'BlueVisionAdmin':
            accessible_orgs.extend(
                Organization.objects.exclude(id=user.organization.id)
            )
        else:
            # Get organizations through trust relationships
            trust_relationships = TrustRelationship.objects.filter(
                source_organization=user.organization,
                is_active=True,
                status='active'
            ).select_related('target_organization')
            
            for relationship in trust_relationships:
                if relationship.get_effective_access_level() in ['read', 'subscribe', 'contribute', 'full']:
                    accessible_orgs.append(relationship.target_organization)
        
        return list(set(accessible_orgs))  # Remove duplicates
    
    def can_access_organization(self, user: CustomUser, organization: Organization) -> bool:
        """
        Check if user can access a specific organization's data.
        
        Args:
            user: User to check access for
            organization: Organization to check access to
            
        Returns:
            bool: True if user can access organization
        """
        return organization in self.get_accessible_organizations(user)
    
    def require_permission(self, user: CustomUser, permission: str,
                          resource_organization: Optional[Organization] = None,
                          resource_context: Optional[Dict] = None) -> None:
        """
        Require that a user has a specific permission, raise PermissionDenied if not.
        
        Args:
            user: User to check permissions for
            permission: Permission string to require
            resource_organization: Organization that owns the resource (optional)
            resource_context: Additional context about the resource (optional)
            
        Raises:
            PermissionDenied: If user doesn't have required permission
        """
        if not self.has_permission(user, permission, resource_organization, resource_context):
            raise PermissionDenied(
                f"User {user.username} does not have permission: {permission}"
            )
    
    def filter_queryset_by_access(self, user: CustomUser, queryset, 
                                organization_field: str = 'organization') -> Any:
        """
        Filter a queryset to only include objects the user can access.
        
        Args:
            user: User to filter for
            queryset: Django queryset to filter
            organization_field: Field name that contains the organization reference
            
        Returns:
            Filtered queryset
        """
        if isinstance(user, AnonymousUser) or not user.is_active:
            return queryset.none()
        
        accessible_org_ids = [
            org.id for org in self.get_accessible_organizations(user)
        ]
        
        filter_kwargs = {f"{organization_field}__id__in": accessible_org_ids}
        return queryset.filter(**filter_kwargs)
    
    def get_role_hierarchy_level(self, role: str) -> int:
        """
        Get the hierarchy level for a role.
        
        Args:
            role: Role name
            
        Returns:
            int: Hierarchy level (higher = more permissions)
        """
        return self.ROLE_HIERARCHY.get(role, 0)
    
    def can_manage_user(self, manager: CustomUser, target_user: CustomUser) -> bool:
        """
        Check if a user can manage another user.
        
        Args:
            manager: User who wants to manage
            target_user: User to be managed
            
        Returns:
            bool: True if manager can manage target_user
        """
        # Can't manage inactive users or yourself in certain operations
        if not manager.is_active or not target_user.is_active:
            return False
        
        # BlueVision admins can manage all users
        if manager.role == 'BlueVisionAdmin':
            return True
        
        # Publishers can manage users in their organization
        if (manager.role == 'publisher' and 
            manager.organization.id == target_user.organization.id):
            
            # Publishers can't manage other publishers or admins
            manager_level = self.get_role_hierarchy_level(manager.role)
            target_level = self.get_role_hierarchy_level(target_user.role)
            
            return manager_level > target_level
        
        return False
    
    def can_create_user_with_role(self, creator: CustomUser, target_role: str,
                                target_organization: Organization) -> bool:
        """
        Check if a user can create a new user with a specific role.
        
        Args:
            creator: User who wants to create a new user
            target_role: Role for the new user
            target_organization: Organization for the new user
            
        Returns:
            bool: True if creator can create user with target_role
        """
        if not creator.is_active:
            return False
        
        # BlueVision admins can create any user in any organization
        if creator.role == 'BlueVisionAdmin':
            return True
        
        # Publishers can create users in their organization
        if (creator.role == 'publisher' and 
            creator.organization.id == target_organization.id):
            
            # Publishers can create viewers and publishers, but not admins
            if target_role in ['viewer', 'publisher']:
                return True
        
        return False
    
    def get_trust_aware_data_access(self, user: CustomUser, data_type: str,
                                  source_organization: Organization) -> Dict[str, Any]:
        """
        Get trust-aware access information for specific data.
        
        Args:
            user: User requesting access
            data_type: Type of data being accessed
            source_organization: Organization that owns the data
            
        Returns:
            dict: Access information including anonymization level, restrictions, etc.
        """
        access_info = {
            'can_access': False,
            'anonymization_level': 'full',
            'access_level': 'none',
            'restrictions': [],
            'trust_level': None
        }
        
        # Own organization data - full access
        if user.organization.id == source_organization.id:
            access_info.update({
                'can_access': True,
                'anonymization_level': 'none',
                'access_level': 'full',
                'trust_level': 'internal'
            })
            return access_info
        
        # BlueVision admin access
        if user.role == 'BlueVisionAdmin':
            access_info.update({
                'can_access': True,
                'anonymization_level': 'minimal',
                'access_level': 'full',
                'trust_level': 'administrative'
            })
            return access_info
        
        # Check trust relationships
        try:
            trust_relationship = TrustRelationship.objects.filter(
                source_organization=user.organization,
                target_organization=source_organization,
                is_active=True,
                status='active'
            ).select_related('trust_level').first()
            
            if trust_relationship:
                access_info.update({
                    'can_access': True,
                    'anonymization_level': trust_relationship.get_effective_anonymization_level(),
                    'access_level': trust_relationship.get_effective_access_level(),
                    'trust_level': trust_relationship.trust_level.level,
                    'relationship_id': str(trust_relationship.id)
                })
                
                # Add restrictions based on sharing policies
                sharing_prefs = trust_relationship.sharing_preferences
                if sharing_prefs:
                    restrictions = []
                    
                    if sharing_prefs.get('max_tlp_level'):
                        restrictions.append(f"TLP ≤ {sharing_prefs['max_tlp_level'].upper()}")
                    
                    if sharing_prefs.get('max_age_days'):
                        restrictions.append(f"Age ≤ {sharing_prefs['max_age_days']} days")
                    
                    if sharing_prefs.get('blocked_stix_types'):
                        restrictions.append(f"Blocked types: {', '.join(sharing_prefs['blocked_stix_types'])}")
                    
                    access_info['restrictions'] = restrictions
        
        except Exception as e:
            logger.error(f"Error getting trust-aware access info: {str(e)}")
        
        return access_info