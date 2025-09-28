"""
Access Control Service - Comprehensive permission and access management
Handles role-based permissions, trust-aware access control, and organization management
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from core.models.models import (
    Organization, TrustRelationship, TrustLevel, TrustGroup
)
from core.user_management.models import CustomUser
import logging

logger = logging.getLogger(__name__)

class AccessControlService:
    """Service for managing access control and permissions with trust awareness"""
    
    def __init__(self):
        self._role_permissions = {
            'viewer': {
                'can_view_threat_feeds',
                'can_view_indicators',
                'can_view_organization_data',
                'can_view_user_profile'
            },
            'publisher': {
                'can_view_threat_feeds',
                'can_view_indicators',
                'can_view_organization_data',
                'can_view_user_profile',
                'can_publish_threat_intelligence',
                'can_manage_threat_feeds',
                'can_manage_organization_users',
                'can_create_organization_users',
                'can_manage_trust_relationships',
                'can_view_organization_analytics',
                'can_create_trust_relationships',
                'can_view_trust_relationships',
                'can_invite_users',
                'can_manage_user_invitations'
            },
            'admin': {
                'can_view_threat_feeds',
                'can_view_indicators',
                'can_view_organization_data',
                'can_view_user_profile',
                'can_publish_threat_intelligence',
                'can_manage_threat_feeds',
                'can_manage_organization_users',
                'can_create_organization_users',
                'can_manage_trust_relationships',
                'can_view_organization_analytics',
                'can_create_trust_relationships',
                'can_view_trust_relationships',
                'can_invite_users',
                'can_manage_user_invitations',
                'can_manage_organizations',
                'can_create_organizations',
                'can_manage_users',
                'can_delete_users',
                'can_view_all_data',
                'can_manage_trust_groups',
                'can_view_system_analytics'
            },
            'BlueVisionAdmin': {
                'can_view_threat_feeds',
                'can_view_indicators',
                'can_view_organization_data',
                'can_view_user_profile',
                'can_publish_threat_intelligence',
                'can_manage_threat_feeds',
                'can_manage_organization_users',
                'can_create_organization_users',
                'can_manage_trust_relationships',
                'can_view_organization_analytics',
                'can_create_trust_relationships',
                'can_view_trust_relationships',
                'can_invite_users',
                'can_manage_user_invitations',
                'can_manage_organizations',
                'can_create_organizations',
                'can_manage_users',
                'can_delete_users',
                'can_view_all_data',
                'can_manage_trust_groups',
                'can_view_system_analytics',
                'can_manage_all_organizations',
                'can_manage_all_users',
                'can_access_admin_panel',
                'can_manage_system_settings'
            }
        }
    
    def get_user_permissions(self, user) -> Set[str]:
        """Get all permissions for a user based on their role and hierarchy"""
        if not user or not hasattr(user, 'role'):
            return set()
            
        role = user.role
        permissions = set()
        
        # Add role's direct permissions
        if role in self._role_permissions:
            permissions.update(self._role_permissions[role])
            
        # Add inherited permissions based on role hierarchy
        if role == 'BlueVisionAdmin':
            # BlueVision admins inherit all permissions
            permissions.update(self._role_permissions.get('admin', set()))
            permissions.update(self._role_permissions.get('publisher', set()))
            permissions.update(self._role_permissions.get('viewer', set()))
        elif role == 'admin':
            # Admins inherit publisher and viewer permissions
            permissions.update(self._role_permissions.get('publisher', set()))
            permissions.update(self._role_permissions.get('viewer', set()))
        elif role == 'publisher':
            # Publishers inherit viewer permissions
            permissions.update(self._role_permissions.get('viewer', set()))
            
        return permissions
    
    def has_permission(self, user, permission: str) -> bool:
        """Check if user has specific permission"""
        if not user:
            return False
        return permission in self.get_user_permissions(user)
    
    def require_permission(self, user, permission: str):
        """Require specific permission or raise PermissionDenied"""
        if not self.has_permission(user, permission):
            username = getattr(user, 'username', 'Anonymous') if user else 'Anonymous'
            raise PermissionDenied(f"User {username} does not have permission: {permission}")
    
    def can_manage_users(self, user) -> bool:
        """Check if user can manage users in general (for listing/accessing user management)"""
        if not user:
            return False
            
        # Use the existing permission system
        return self.has_permission(user, 'can_manage_users')
    
    def can_create_users(self, user) -> bool:
        """Check if user can create new users"""
        if not user:
            return False
            
        # Use the existing permission system
        return self.has_permission(user, 'can_create_organization_users')
    
    def can_view_user(self, viewing_user, target_user) -> bool:
        """Check if user can view another user's details"""
        if not viewing_user or not target_user:
            return False
            
        # Users can view themselves
        if viewing_user.id == target_user.id:
            return True
            
        # BlueVision admins can view all users
        if viewing_user.role == 'BlueVisionAdmin':
            return True
            
        # Admins can view all users
        if viewing_user.role == 'admin':
            return True
            
        # Publishers can view users in their organization
        if (viewing_user.role == 'publisher' and 
            viewing_user.organization and 
            target_user.organization and
            viewing_user.organization.id == target_user.organization.id):
            return True
        
        return False
    
    def can_modify_user(self, modifying_user, target_user) -> bool:
        """Check if user can modify another user's details"""
        # This is essentially the same as can_manage_user but with different semantics
        return self.can_manage_user(modifying_user, target_user)
    
    def can_delete_user(self, deleting_user, target_user) -> bool:
        """Check if user can delete another user"""
        if not deleting_user or not target_user:
            return False
            
        # Users cannot delete themselves (handled separately in the API)
        if deleting_user.id == target_user.id:
            return False
            
        # BlueVision admins can delete all users
        if deleting_user.role == 'BlueVisionAdmin':
            return True
            
        # Admins can delete users except other admins and BlueVision admins
        if deleting_user.role == 'admin':
            return target_user.role not in ['admin', 'BlueVisionAdmin']
            
        # Publishers can delete viewers in their organization
        if (deleting_user.role == 'publisher' and 
            deleting_user.organization and 
            target_user.organization and
            deleting_user.organization.id == target_user.organization.id):
            return target_user.role == 'viewer'
        
        return False
    
    def can_manage_user(self, managing_user, target_user) -> bool:
        """Check if user can manage another user"""
        if not managing_user or not target_user:
            return False
            
        # Users can manage themselves (profile updates)
        if managing_user.id == target_user.id:
            return True
            
        # BlueVision admins can manage all users
        if managing_user.role == 'BlueVisionAdmin':
            return True
            
        # Superusers can manage all users
        if getattr(managing_user, 'is_superuser', False):
            return True
            
        # Admins can manage users in any organization
        if managing_user.role == 'admin':
            return True
            
        # Publishers can manage users in their own organization only
        if (managing_user.role == 'publisher' and 
            managing_user.organization and 
            target_user.organization and
            managing_user.organization.id == target_user.organization.id):
            # Publishers can manage viewers and other publishers in their org
            if target_user.role in ['viewer', 'publisher']:
                return True
            
        return False
    
    def can_create_user_with_role(self, creating_user, role: str, organization=None) -> bool:
        """Check if user can create another user with specified role"""
        # Anonymous users can only register as viewers
        if not creating_user:
            return role == 'viewer'
            
        # BlueVision admins can create users with any role
        if creating_user.role == 'BlueVisionAdmin':
            return True
            
        # Admins can create users with any role except BlueVisionAdmin
        if creating_user.role == 'admin':
            return role != 'BlueVisionAdmin'
            
        # Publishers can create viewers and publishers in their own organization
        if creating_user.role == 'publisher':
            if role in ['viewer', 'publisher'] and organization == creating_user.organization:
                return True
            return False
            
        return False
    
    def can_manage_organization(self, user, organization) -> bool:
        """Check if user can manage organization settings and members"""
        if not user or not organization:
            return False
        
        # BlueVision admins can manage any organization
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Superusers can manage any organization
        if getattr(user, 'is_superuser', False):
            return True
        
        # Admins and publishers can manage their own organization
        if (user.organization and 
            user.organization.id == organization.id and 
            user.role in ['admin', 'publisher']):
            return True
        
        return False
    
    def can_invite_to_organization(self, user, organization) -> bool:
        """Check if user can send invitations to an organization"""
        if not user or not organization:
            return False
        
        # BlueVision admins can invite to any organization
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Publishers can invite to their own organization
        if (user.role == 'publisher' and 
            user.organization and 
            user.organization.id == organization.id):
            return True
        
        return False
    
    def get_accessible_organizations(self, user) -> List[Organization]:
        """Get organizations accessible to the user through role or trust relationships"""
        accessible = []
        
        if not user:
            return accessible
        
        try:
            # BlueVision admins can access ALL organizations
            if user.role == 'BlueVisionAdmin':
                return list(Organization.objects.filter(is_active=True))
            
            # User's own organization is always accessible
            if user.organization:
                accessible.append(user.organization)
                
                # Get organizations through trust relationships
                try:
                    relationships = TrustRelationship.objects.filter(
                        source_organization=user.organization,
                        is_active=True,
                        status='active'
                    ).select_related('target_organization')
                    
                    for rel in relationships:
                        if (rel.target_organization and 
                            rel.target_organization.is_active and
                            rel.target_organization not in accessible):
                            accessible.append(rel.target_organization)
                            
                except Exception as e:
                    logger.error(f"Error getting trust relationships: {e}")
            
        except Exception as e:
            logger.error(f"Error getting accessible organizations: {e}")
        
        return accessible
    
    def get_manageable_organizations(self, user) -> List[Organization]:
        """Get organizations that the user can manage (for user invitations and management)"""
        manageable = []
        
        if not user:
            return manageable
        
        try:
            # BlueVision admins can manage ALL organizations
            if user.role == 'BlueVisionAdmin':
                return list(Organization.objects.filter(is_active=True))
            
            # Admins can manage all organizations
            if user.role == 'admin':
                return list(Organization.objects.filter(is_active=True))
            
            # Publishers can only manage their own organization
            if user.role == 'publisher' and user.organization:
                manageable.append(user.organization)
            
        except Exception as e:
            logger.error(f"Error getting manageable organizations: {e}")
        
        return manageable
    
    def can_access_organization(self, user, organization) -> bool:
        """Check if user can access an organization"""
        if not user or not organization:
            return False
            
        # User can access their own organization
        if user.organization and user.organization.id == organization.id:
            return True
            
        # BlueVision admins can access all organizations
        if user.role == 'BlueVisionAdmin':
            return True
            
        # Superusers can access all organizations
        if getattr(user, 'is_superuser', False):
            return True
            
        # Check trust relationships
        if user.organization:
            try:
                relationship = TrustRelationship.objects.filter(
                    source_organization=user.organization,
                    target_organization=organization,
                    is_active=True,
                    status='active'
                ).exists()
                return relationship
            except Exception as e:
                logger.error(f"Error checking trust relationship: {e}")
                return False
        
        return False
    
    def get_trust_aware_data_access(self, user, data_type: str, source_organization) -> Dict[str, Any]:
        """Get trust-aware data access information for anonymization decisions"""
        access_info = {
            'can_access': False,
            'access_level': 'none',
            'anonymization_level': 'full',
            'trust_level': None,
            'restrictions': []
        }
        
        if not user or not source_organization:
            return access_info
        
        # User's own organization data is fully accessible
        if user.organization and source_organization.id == user.organization.id:
            access_info.update({
                'can_access': True,
                'access_level': 'full',
                'anonymization_level': 'none',
                'trust_level': 'self'
            })
            return access_info
        
        # BlueVision admins have full access to all data
        if user.role == 'BlueVisionAdmin':
            access_info.update({
                'can_access': True,
                'access_level': 'full',
                'anonymization_level': 'minimal',
                'trust_level': 'admin'
            })
            return access_info
        
        # Check trust relationships for access level
        if user.organization:
            try:
                relationship = TrustRelationship.objects.filter(
                    source_organization=user.organization,
                    target_organization=source_organization,
                    is_active=True,
                    status='active'
                ).select_related('trust_level').first()
                
                if relationship:
                    # Map trust level to anonymization level
                    anonymization_mapping = {
                        'public': 'standard',
                        'standard': 'moderate',
                        'high': 'minimal',
                        'restricted': 'none'
                    }
                    
                    trust_level_name = relationship.trust_level.name.lower()
                    anonymization_level = anonymization_mapping.get(trust_level_name, 'full')
                    
                    access_info.update({
                        'can_access': True,
                        'access_level': 'trust_based',
                        'anonymization_level': anonymization_level,
                        'trust_level': trust_level_name
                    })
                    
            except Exception as e:
                logger.error(f"Error checking trust relationship for data access: {e}")
        
        return access_info
    
    def can_manage_trust_relationships(self, user, source_org=None, target_org=None) -> bool:
        """Check if user can manage trust relationships"""
        if not user:
            return False
        
        # BlueVision admins can manage all trust relationships
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Publishers and admins can manage trust relationships for their organization
        if user.role in ['publisher', 'admin'] and user.organization:
            # If specific organizations are provided, check if user can manage them
            if source_org and source_org.id != user.organization.id:
                return False
            if target_org and not self.can_access_organization(user, target_org):
                return False
            return True
        
        return False
    
    def can_manage_trust_groups(self, user) -> bool:
        """Check if user can manage trust groups"""
        if not user:
            return False
        
        # Only admins and BlueVision admins can manage trust groups
        return user.role in ['admin', 'BlueVisionAdmin']
    
    def can_view_trust_relationships(self, user) -> bool:
        """Check if user can view trust relationships"""
        if not user:
            return False
        
        # Publishers and above can view trust relationships
        return user.role in ['publisher', 'admin', 'BlueVisionAdmin']
    
    def can_respond_to_trust_request(self, user, trust_relationship) -> bool:
        """Check if user can respond to a trust request"""
        if not user or not trust_relationship:
            return False
        
        # BlueVision admins can respond to any trust request
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Publishers and admins can respond if the request is for their organization
        if user.role in ['publisher', 'admin'] and user.organization:
            return trust_relationship.target_organization.id == user.organization.id
        
        return False
    
    def can_modify_trust_relationship(self, user, trust_relationship) -> bool:
        """Check if user can modify a trust relationship"""
        if not user or not trust_relationship:
            return False
        
        # BlueVision admins can modify any trust relationship
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Publishers and admins can modify relationships involving their organization
        if user.role in ['publisher', 'admin'] and user.organization:
            return (trust_relationship.source_organization.id == user.organization.id or
                   trust_relationship.target_organization.id == user.organization.id)
        
        return False
    
    def can_revoke_trust_relationship(self, user, trust_relationship) -> bool:
        """Check if user can revoke a trust relationship"""
        # Same logic as modify for now
        return self.can_modify_trust_relationship(user, trust_relationship)
    
    def can_view_community_trusts(self, user) -> bool:
        """Check if user can view community trust groups"""
        if not user:
            return False
        
        # Publishers and above can view community trusts
        return user.role in ['publisher', 'admin', 'BlueVisionAdmin']
    
    def can_view_reports(self, user) -> bool:
        """Check if user can view threat intelligence reports"""
        if not user:
            return False
        
        # All authenticated users can view reports, but data access is filtered by trust relationships
        return user.role in ['viewer', 'publisher', 'admin', 'BlueVisionAdmin']
    
    def get_role_hierarchy_level(self, role: str) -> int:
        """Get the hierarchy level of a role (higher number = more permissions)"""
        hierarchy = {
            'viewer': 1,
            'publisher': 2,
            'admin': 3,
            'BlueVisionAdmin': 4
        }
        return hierarchy.get(role, 0)
    
    def can_escalate_to_role(self, managing_user, target_role: str) -> bool:
        """Check if user can escalate someone to a specific role"""
        if not managing_user:
            return False
        
        managing_level = self.get_role_hierarchy_level(managing_user.role)
        target_level = self.get_role_hierarchy_level(target_role)
        
        # Users can only escalate to roles at their level or below
        # Exception: BlueVision admins can escalate to any role
        if managing_user.role == 'BlueVisionAdmin':
            return True
        
        return managing_level > target_level
    
    def can_create_organizations(self, user) -> bool:
        """Check if user can create organizations"""
        return self.has_permission(user, 'can_create_organizations')
    
    def can_view_organization(self, user, organization) -> bool:
        """Check if user can view organization details"""
        if not user or not organization:
            return False
            
        # BlueVision admins can view all organizations
        if user.role == 'BlueVisionAdmin':
            return True
            
        # Users can view their own organization
        if user.organization and user.organization.id == organization.id:
            return True
            
        # Check trust relationships
        return self.can_access_organization(user, organization)
    
    def can_delete_organization(self, user, organization) -> bool:
        """Check if user can delete/deactivate organizations"""
        if not user or not organization:
            return False
            
        # Only BlueVision admins can delete organizations
        return user.role == 'BlueVisionAdmin'
    
    def get_accessible_data_sources(self, user) -> List[str]:
        """Get list of data source organization IDs accessible to user"""
        accessible_org_ids = []
        
        try:
            accessible_orgs = self.get_accessible_organizations(user)
            accessible_org_ids = [str(org.id) for org in accessible_orgs]
        except Exception as e:
            logger.error(f"Error getting accessible data sources: {e}")
        
        return accessible_org_ids
    
    def filter_data_by_access(self, user, queryset, organization_field='organization'):
        """Filter queryset based on user's accessible organizations"""
        if not user:
            return queryset.none()
        
        # BlueVision admins see everything
        if user.role == 'BlueVisionAdmin':
            return queryset
        
        accessible_org_ids = self.get_accessible_data_sources(user)
        if not accessible_org_ids:
            return queryset.none()
        
        # Filter by accessible organizations
        filter_kwargs = {f"{organization_field}__id__in": accessible_org_ids}
        return queryset.filter(**filter_kwargs)
    
    def can_manage_users(self, user) -> bool:
        """Check if user can manage users in general (for listing/accessing user management)"""
        if not user:
            return False
        return self.has_permission(user, 'can_manage_users') or self.has_permission(user, 'can_manage_organization_users')
    
    def can_create_users(self, user) -> bool:
        """Check if user can create new users"""
        if not user:
            return False
        return self.has_permission(user, 'can_create_organization_users')
    
    def can_view_user(self, viewing_user, target_user) -> bool:
        """Check if user can view another user's details"""
        if not viewing_user or not target_user:
            return False
        
        # Users can view themselves
        if viewing_user.id == target_user.id:
            return True
        
        # Use existing can_manage_user logic for viewing
        return self.can_manage_user(viewing_user, target_user)
    
    def can_modify_user(self, modifying_user, target_user) -> bool:
        """Check if user can modify another user's details"""
        return self.can_manage_user(modifying_user, target_user)
    
    def can_delete_user(self, deleting_user, target_user) -> bool:
        """Check if user can delete another user"""
        if not deleting_user or not target_user:
            return False
        
        # Cannot delete yourself
        if deleting_user.id == target_user.id:
            return False
        
        # BlueVision admins can delete any user except other BlueVision admins
        if deleting_user.role == 'BlueVisionAdmin':
            return target_user.role != 'BlueVisionAdmin'
        
        # Admins can delete users but not other admins or BlueVision admins
        if deleting_user.role == 'admin':
            return target_user.role not in ['admin', 'BlueVisionAdmin']
        
        # Publishers cannot delete users
        return False
    
    def get_manageable_organizations(self, user) -> List[Organization]:
        """Get organizations that the user can manage (for user invitations and management)"""
        manageable = []
        
        if not user:
            return manageable
        
        try:
            # BlueVision admins can manage all organizations
            if user.role == 'BlueVisionAdmin':
                return list(Organization.objects.filter(is_active=True))
            
            # Admins and publishers can manage their own organization
            if user.organization and user.role in ['admin', 'publisher']:
                manageable.append(user.organization)
                
        except Exception as e:
            logger.error(f"Error getting manageable organizations: {e}")
        
        return manageable
    
    def can_modify_organization(self, user, organization) -> bool:
        """Check if user can modify organization settings"""
        return self.can_manage_organization(user, organization)
    
    def can_view_organization_members(self, user, organization) -> bool:
        """Check if user can view organization member lists"""
        if not user or not organization:
            return False
        
        # BlueVision admins can view all organization members
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Users can view members of their own organization
        if user.organization and user.organization.id == organization.id:
            return True
        
        # Check trust relationships for viewing members
        return self.can_access_organization(user, organization)
    
    def can_view_organization_statistics(self, user, organization) -> bool:
        """Check if user can view organization statistics and metrics"""
        if not user or not organization:
            return False
        
        # BlueVision admins can view all organization statistics
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Admins and publishers can view their own organization statistics
        if (user.organization and 
            user.organization.id == organization.id and 
            user.role in ['admin', 'publisher']):
            return True
        
        # Check trust relationships for limited statistics viewing
        return self.can_access_organization(user, organization)
    
    def can_view_organization_trust_relationships(self, user, organization) -> bool:
        """Check if user can view organization trust relationships"""
        if not user or not organization:
            return False
        
        # BlueVision admins can view all trust relationships
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Admins and publishers can view their own organization's trust relationships
        if (user.organization and 
            user.organization.id == organization.id and 
            user.role in ['admin', 'publisher']):
            return True
        
        return False

    def can_share_indicator(self, user, indicator) -> bool:
        """Check if user can share an indicator"""
        if not user or not indicator:
            return False

        # BlueVision admins can share any indicator
        if user.role == 'BlueVisionAdmin':
            return True

        # Publishers and admins can share indicators from their organization's feeds
        if user.role in ['publisher', 'admin']:
            # Check if user's organization owns the threat feed
            if (user.organization and
                indicator.threat_feed and
                indicator.threat_feed.owner_id == user.organization.id):
                return True

        return False

    def log_access_attempt(self, user, resource_type: str, resource_id: str,
                          action: str, success: bool, details: Dict = None):
        """Log access attempts for auditing"""
        try:
            # This would integrate with the audit service
            logger.info(f"Access attempt: User {user.username if user else 'Anonymous'} "
                       f"attempted {action} on {resource_type}:{resource_id} - "
                       f"{'Success' if success else 'Denied'}")
            
            if details:
                logger.debug(f"Access details: {details}")
                
        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")