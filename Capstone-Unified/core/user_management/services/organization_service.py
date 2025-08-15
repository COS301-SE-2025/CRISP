from typing import Dict, List, Optional, Any, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from ..models import CustomUser, Organization, AuthenticationLog
from core.trust_management.models import TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership
from .access_control_service import AccessControlService
import logging

logger = logging.getLogger(__name__)


class OrganizationService:
    """
    Service for managing organizations with integrated trust relationship support.
    Handles CRUD operations and trust-related functionality for organizations.
    """
    
    def __init__(self):
        self.access_control = AccessControlService()
    
    def create_organization(self, creating_user: CustomUser = None, org_data: Dict = None, 
                          primary_user_data: Dict = None, name: str = None, 
                          organization_type: str = None, **kwargs) -> Tuple[Organization, CustomUser]:
        """
        Create a new organization with its primary publisher user.
        
        Support for multiple calling patterns:
        1. create_organization(creating_user, org_data) - org_data contains primary_user
        2. create_organization(creating_user, org_data, primary_user_data) - separate args
        3. create_organization(name, organization_type, primary_user_data, **kwargs) - direct args
        
        Returns:
            Tuple[Organization, CustomUser]: Created organization and primary user
            
        Raises:
            PermissionDenied: If user doesn't have permission to create organizations
            ValidationError: If organization data is invalid
        """
        # Handle different calling patterns
        if name and organization_type and primary_user_data:
            # Pattern 3: Direct arguments
            org_data = {
                'name': name,
                'organization_type': organization_type,
                'domain': kwargs.get('domain', f"{name.lower().replace(' ', '')}.com"),
                'contact_email': kwargs.get('contact_email', primary_user_data.get('email')),
                **kwargs
            }
            # Don't require permissions check for this pattern (used internally)
        else:
            # Patterns 1 & 2: creating_user and org_data based
            if not creating_user or not org_data:
                raise ValidationError("creating_user and org_data are required")
                
            # Check permissions
            if not self.access_control.has_permission(creating_user, 'can_create_organizations'):
                raise PermissionDenied("No permission to create organizations")
            
            # Handle pattern 2: separate primary_user_data
            if primary_user_data:
                pass  # primary_user_data is already provided
            # Handle pattern 1: primary_user inside org_data
            elif 'primary_user' in org_data:
                primary_user_data = org_data['primary_user']
            else:
                raise ValidationError("primary_user_data is required")
        
        # Validate organization data
        if not org_data.get('name'):
            raise ValidationError("Organization name is required")
        if not org_data.get('organization_type'):
            raise ValidationError("Organization type is required")
            
        # Validate primary user data
        if not primary_user_data:
            raise ValidationError("Primary user data is required")
            
        required_user_fields = ['username', 'email', 'password']
        for field in required_user_fields:
            if field not in primary_user_data or not primary_user_data[field]:
                raise ValidationError(f"Primary user '{field}' is required")
        
        # Check if organization name already exists
        if Organization.objects.filter(name=org_data['name']).exists():
            raise ValidationError("Organization name already exists")
        
        # Check domain if provided
        if org_data.get('domain') and Organization.objects.filter(domain=org_data['domain']).exists():
            raise ValidationError("Organization domain already exists")
        
        # Check if primary user username or email already exists
        if CustomUser.objects.filter(username=primary_user_data['username']).exists():
            raise ValidationError("Primary user username already exists")
        
        if CustomUser.objects.filter(email=primary_user_data['email']).exists():
            raise ValidationError("Primary user email already exists")
        
        try:
            with transaction.atomic():
                # Generate domain if not provided
                domain = org_data.get('domain', '')
                if not domain:
                    # Generate a unique domain based on organization name
                    import re
                    import uuid
                    base_domain = re.sub(r'[^a-zA-Z0-9]', '', org_data['name'].lower())
                    if not base_domain:
                        base_domain = 'org'
                    domain = f"{base_domain}-{str(uuid.uuid4())[:8]}.com"
                    
                    # Ensure domain is unique
                    while Organization.objects.filter(domain=domain).exists():
                        domain = f"{base_domain}-{str(uuid.uuid4())[:8]}.com"
                
                # Create organization
                organization = Organization.objects.create(
                    name=org_data['name'],
                    description=org_data.get('description', ''),
                    domain=domain,
                    contact_email=org_data.get('contact_email', primary_user_data.get('email', '')),
                    website=org_data.get('website', ''),
                    organization_type=org_data.get('organization_type', 'educational'),
                    is_publisher=org_data.get('is_publisher', True),
                    is_verified=org_data.get('is_verified', True),
                    is_active=True,
                    created_by=creating_user.username if creating_user else 'system'
                )
                
                # Create primary user
                primary_user = CustomUser.objects.create_user(
                    username=primary_user_data['username'],
                    email=primary_user_data['email'],
                    password=primary_user_data['password'],
                    first_name=primary_user_data['first_name'],
                    last_name=primary_user_data['last_name'],
                    organization=organization,
                    role='publisher',
                    is_publisher=True,
                    is_verified=True,
                    is_active=True
                )
                
                # Log organization creation
                if creating_user:
                    AuthenticationLog.log_authentication_event(
                        user=creating_user,
                        action='organization_created',
                        ip_address=org_data.get('created_from_ip', '127.0.0.1'),
                        user_agent=org_data.get('user_agent', 'System'),
                        success=True,
                        additional_data={
                            'organization_id': str(organization.id),
                            'organization_name': organization.name,
                            'primary_user_id': str(primary_user.id),
                            'primary_user_username': primary_user.username
                        }
                    )
                
                logger.info(
                    f"Organization '{organization.name}' created by {creating_user.username if creating_user else 'system'} "
                    f"with primary user {primary_user.username}"
                )
                
                return organization, primary_user
                
        except Exception as e:
            logger.error(f"Error creating organization: {str(e)}")
            raise ValidationError(f"Failed to create organization: {str(e)}")
    
    def update_organization(self, updating_user: CustomUser, organization_id: str,
                          update_data: Dict) -> Organization:
        """
        Update an organization's information.
        
        Args:
            updating_user: User performing the update
            organization_id: ID of organization to update
            update_data: Data to update
            
        Returns:
            Organization: Updated organization
            
        Raises:
            PermissionDenied: If user doesn't have permission to update organization
            ValidationError: If update data is invalid
        """
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        # Check permissions - allow admins and publishers to update organizations
        can_update = (
            updating_user.role in ['BlueVisionAdmin', 'admin'] or
            (updating_user.role == 'publisher' and 
             updating_user.organization.id == organization.id) or
            # Allow admins from any organization to update organizations
            (updating_user.role == 'admin')
        )
        
        if not can_update:
            raise PermissionDenied("No permission to update this organization")
        
        # Validate updates
        updatable_fields = {
            'description', 'contact_email', 'website', 'organization_type'
        }
        
        # BlueVision admins and regular admins can update additional fields
        if updating_user.role in ['BlueVisionAdmin', 'admin']:
            updatable_fields.update({
                'name', 'domain', 'is_publisher', 'is_verified', 'is_active'
            })
        
        # Apply updates
        updated_fields = []
        logger.info(f"Update data received: {update_data}")
        logger.info(f"Updatable fields for user {updating_user.role}: {updatable_fields}")
        
        for field, value in update_data.items():
            logger.info(f"Processing field '{field}' with value '{value}'")
            if field in updatable_fields and hasattr(organization, field):
                old_value = getattr(organization, field)
                logger.info(f"Field '{field}': old='{old_value}', new='{value}'")
                if old_value != value:
                    setattr(organization, field, value)
                    updated_fields.append(field)
                    logger.info(f"Updated field '{field}' from '{old_value}' to '{value}'")
                else:
                    logger.info(f"Field '{field}' unchanged")
            elif field not in updatable_fields:
                logger.warning(f"Field '{field}' not in updatable_fields: {updatable_fields}")
            elif not hasattr(organization, field):
                logger.warning(f"Organization does not have field '{field}'")
        
        if updated_fields:
            organization.save(update_fields=updated_fields + ['updated_at'])
            
            # Log organization update
            AuthenticationLog.log_authentication_event(
                user=updating_user,
                action='organization_updated',
                ip_address=update_data.get('updated_from_ip', '127.0.0.1'),
                user_agent=update_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'organization_id': str(organization.id),
                    'organization_name': organization.name,
                    'updated_fields': updated_fields
                }
            )
            
            logger.info(
                f"Organization '{organization.name}' updated by {updating_user.username}. "
                f"Fields: {', '.join(updated_fields)}"
            )
        
        return organization
    
    def get_organization_details(self, requesting_user: CustomUser,
                               organization_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an organization.
        
        Args:
            requesting_user: User requesting the information
            organization_id: ID of organization to get details for
            
        Returns:
            dict: Organization details including trust information
            
        Raises:
            PermissionDenied: If user doesn't have access to organization
        """
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        # Check if user can access this organization
        if not self.access_control.can_access_organization(requesting_user, organization):
            raise PermissionDenied("No access to this organization")
        
        org_details = {
            'id': str(organization.id),
            'name': organization.name,
            'description': organization.description,
            'domain': organization.domain,
            'contact_email': organization.contact_email,
            'website': organization.website,
            'organization_type': organization.organization_type,
            'is_publisher': organization.is_publisher,
            'is_verified': organization.is_verified,
            'is_active': organization.is_active,
            'created_at': organization.created_at.isoformat(),
            'updated_at': organization.updated_at.isoformat(),
            'user_count': organization.user_count,
            'publisher_count': organization.publisher_count,
            'can_publish_threat_intelligence': organization.can_publish_threat_intelligence(),
        }
        
        # Add trust information if user has appropriate permissions
        if requesting_user.can_manage_trust_relationships:
            org_details['trust_info'] = self._get_organization_trust_info(
                requesting_user, organization
            )
        
        # Add user list if user can manage users
        if (requesting_user.role == 'BlueVisionAdmin' or
            (requesting_user.role == 'publisher' and 
             requesting_user.organization.id == organization.id)):
            org_details['users'] = self._get_organization_users(organization)
        
        return org_details
    
    def _get_organization_trust_info(self, requesting_user: CustomUser,
                                   organization: Organization) -> Dict[str, Any]:
        """Get trust information for an organization"""
        trust_info = {
            'trust_relationships': {
                'outgoing': [],
                'incoming': [],
                'summary': {
                    'total_outgoing': 0,
                    'total_incoming': 0,
                    'active_outgoing': 0,
                    'active_incoming': 0
                }
            },
            'trust_groups': [],
            'trust_metrics': {}
        }
        
        try:
            # Get outgoing trust relationships
            outgoing_rels = TrustRelationship.objects.filter(
                source_organization=organization
            ).select_related('target_organization', 'trust_level')
            
            for rel in outgoing_rels:
                trust_info['trust_relationships']['outgoing'].append({
                    'id': str(rel.id),
                    'target_organization': {
                        'id': str(rel.target_organization.id),
                        'name': rel.target_organization.name
                    },
                    'trust_level': rel.trust_level.name,
                    'status': rel.status,
                    'is_effective': rel.is_effective,
                    'created_at': rel.created_at.isoformat()
                })
            
            # Get incoming trust relationships
            incoming_rels = TrustRelationship.objects.filter(
                target_organization=organization
            ).select_related('source_organization', 'trust_level')
            
            for rel in incoming_rels:
                trust_info['trust_relationships']['incoming'].append({
                    'id': str(rel.id),
                    'source_organization': {
                        'id': str(rel.source_organization.id),
                        'name': rel.source_organization.name
                    },
                    'trust_level': rel.trust_level.name,
                    'status': rel.status,
                    'is_effective': rel.is_effective,
                    'created_at': rel.created_at.isoformat()
                })
            
            # Update summary
            trust_info['trust_relationships']['summary'].update({
                'total_outgoing': len(trust_info['trust_relationships']['outgoing']),
                'total_incoming': len(trust_info['trust_relationships']['incoming']),
                'active_outgoing': len([r for r in trust_info['trust_relationships']['outgoing'] 
                                      if r['is_effective']]),
                'active_incoming': len([r for r in trust_info['trust_relationships']['incoming'] 
                                      if r['is_effective']])
            })
            
            # Get trust group memberships
            memberships = TrustGroupMembership.objects.filter(
                organization=organization,
                is_active=True
            ).select_related('trust_group')
            
            for membership in memberships:
                trust_info['trust_groups'].append({
                    'id': str(membership.trust_group.id),
                    'name': membership.trust_group.name,
                    'membership_type': membership.membership_type,
                    'joined_at': membership.joined_at.isoformat()
                })
            
        except Exception as e:
            logger.error(f"Error getting trust info for organization {organization.id}: {str(e)}")
        
        return trust_info
    
    def _get_organization_users(self, organization: Organization) -> List[Dict]:
        """Get list of users in the organization"""
        users = []
        
        try:
            org_users = CustomUser.objects.filter(
                organization=organization
            ).order_by('username')
            
            for user in org_users:
                users.append({
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_publisher': user.is_publisher,
                    'is_verified': user.is_verified,
                    'is_active': user.is_active,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'date_joined': user.date_joined.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error getting users for organization {organization.id}: {str(e)}")
        
        return users
    
    def list_organizations(self, requesting_user: CustomUser,
                         filters: Optional[Dict] = None) -> List[Dict]:
        """
        List organizations the user can access.
        
        Args:
            requesting_user: User requesting the list
            filters: Optional filters to apply
            
        Returns:
            List[Dict]: List of organizations with basic information
        """
        # Get organizations user can access
        accessible_orgs = self.access_control.get_accessible_organizations(requesting_user)
        
        # Apply filters if provided
        if filters:
            if 'is_active' in filters:
                accessible_orgs = [org for org in accessible_orgs 
                                 if org.is_active == filters['is_active']]
            
            if 'is_publisher' in filters:
                accessible_orgs = [org for org in accessible_orgs 
                                 if org.is_publisher == filters['is_publisher']]
            
            if 'organization_type' in filters:
                accessible_orgs = [org for org in accessible_orgs 
                                 if org.organization_type == filters['organization_type']]
            
            if 'search' in filters:
                search_term = filters['search'].lower()
                accessible_orgs = [org for org in accessible_orgs 
                                 if (search_term in org.name.lower() or 
                                     search_term in org.domain.lower())]
        
        # Format organization data
        org_list = []
        for org in accessible_orgs:
            org_data = {
                'id': str(org.id),
                'name': org.name,
                'domain': org.domain,
                'organization_type': org.organization_type,
                'is_publisher': org.is_publisher,
                'is_verified': org.is_verified,
                'is_active': org.is_active,
                'user_count': org.user_count,
                'created_at': org.created_at.isoformat(),
                'is_own_organization': requesting_user.organization and org.id == requesting_user.organization.id
            }
            
            # Add access level information
            if requesting_user.organization and org.id != requesting_user.organization.id:
                access_info = self.access_control.get_trust_aware_data_access(
                    requesting_user, 'organization_data', org
                )
                org_data['access_level'] = access_info.get('access_level', 'none')
                org_data['trust_level'] = access_info.get('trust_level', 'none')
            else:
                org_data['access_level'] = 'full'
                org_data['trust_level'] = 'internal'
            
            org_list.append(org_data)
        
        return org_list
    
    def deactivate_organization(self, deactivating_user: CustomUser,
                              organization_id: str, reason: str = '') -> Organization:
        """
        Deactivate an organization (soft delete).
        
        Args:
            deactivating_user: User performing the deactivation
            organization_id: ID of organization to deactivate
            reason: Reason for deactivation
            
        Returns:
            Organization: Deactivated organization
            
        Raises:
            PermissionDenied: If user doesn't have permission
        """
        # Only BlueVision admins can deactivate organizations
        self.access_control.require_permission(deactivating_user, 'can_manage_all_organizations')
        
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        if not organization.is_active:
            raise ValidationError("Organization is already deactivated")
        
        try:
            with transaction.atomic():
                # Deactivate organization
                organization.is_active = False
                organization.save(update_fields=['is_active', 'updated_at'])
                
                # Deactivate all users in the organization
                CustomUser.objects.filter(organization=organization).update(
                    is_active=False
                )
                
                # Revoke all trust relationships
                TrustRelationship.objects.filter(
                    source_organization=organization
                ).update(
                    status='revoked',
                    is_active=False,
                    revoked_at=timezone.now(),
                    revoked_by=deactivating_user
                )
                
                TrustRelationship.objects.filter(
                    target_organization=organization
                ).update(
                    status='revoked',
                    is_active=False,
                    revoked_at=timezone.now(),
                    revoked_by=deactivating_user
                )
                
                # Remove from trust groups
                TrustGroupMembership.objects.filter(
                    organization=organization
                ).update(
                    is_active=False,
                    left_at=timezone.now()
                )
                
                # Log organization deactivation
                AuthenticationLog.log_authentication_event(
                    user=deactivating_user,
                    action='organization_deactivated',
                    ip_address='127.0.0.1',
                    user_agent='System',
                    success=True,
                    additional_data={
                        'organization_id': str(organization.id),
                        'organization_name': organization.name,
                        'reason': reason,
                        'users_deactivated': organization.user_count
                    }
                )
                
                logger.warning(
                    f"Organization '{organization.name}' deactivated by {deactivating_user.username}. "
                    f"Reason: {reason}"
                )
                
                return organization
                
        except Exception as e:
            logger.error(f"Error deactivating organization: {str(e)}")
            raise ValidationError(f"Failed to deactivate organization: {str(e)}")
    
    def reactivate_organization(self, reactivating_user: CustomUser, 
                               organization_id: str, reason: str = "") -> Organization:
        """
        Reactivate a previously deactivated organization.
        
        Args:
            reactivating_user: User performing the reactivation
            organization_id: ID of the organization to reactivate
            reason: Reason for reactivation
            
        Returns:
            Organization: The reactivated organization
            
        Raises:
            ValidationError: If reactivation fails
            PermissionDenied: If user lacks permission
        """
        try:
            # Check permissions
            self.access_control.require_permission(reactivating_user, 'can_manage_organizations')
            
            # Get organization
            organization = Organization.objects.get(id=organization_id)
            
            # Check if organization is already active
            if organization.is_active:
                raise ValidationError("Organization is already active")
            
            # Reactivate the organization
            organization.is_active = True
            organization.save()
            
            # Log organization reactivation
            AuthenticationLog.log_authentication_event(
                user=reactivating_user,
                action='organization_reactivated',
                ip_address='127.0.0.1',
                user_agent='System',
                success=True,
                additional_data={
                    'organization_id': str(organization.id),
                    'organization_name': organization.name,
                    'reason': reason
                }
            )
            
            logger.info(f"Organization {organization.name} reactivated by {reactivating_user.username}")
            
            return organization
            
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        except Exception as e:
            logger.error(f"Error reactivating organization: {str(e)}")
            raise ValidationError(f"Failed to reactivate organization: {str(e)}")
    
    def get_organization_statistics(self, requesting_user: CustomUser) -> Dict[str, Any]:
        """
        Get platform-wide organization statistics.
        
        Args:
            requesting_user: User requesting statistics
            
        Returns:
            dict: Organization statistics
        """
        self.access_control.require_permission(requesting_user, 'can_view_system_analytics')
        
        stats = {
            'total_organizations': Organization.objects.count(),
            'active_organizations': Organization.objects.filter(is_active=True).count(),
            'publisher_organizations': Organization.objects.filter(
                is_publisher=True, is_active=True
            ).count(),
            'verified_organizations': Organization.objects.filter(
                is_verified=True, is_active=True
            ).count(),
            'by_type': {},
            'recent_registrations': [],
            'trust_metrics': {
                'total_relationships': TrustRelationship.objects.count(),
                'active_relationships': TrustRelationship.objects.filter(
                    status='active', is_active=True
                ).count(),
                'pending_relationships': TrustRelationship.objects.filter(
                    status='pending'
                ).count()
            }
        }
        
        try:
            # Get organization breakdown by type
            from django.db.models import Count
            type_breakdown = Organization.objects.filter(
                is_active=True
            ).values('organization_type').annotate(
                count=Count('id')
            )
            
            for item in type_breakdown:
                stats['by_type'][item['organization_type']] = item['count']
            
            # Get recent registrations (last 30 days)
            from datetime import timedelta
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_orgs = Organization.objects.filter(
                created_at__gte=thirty_days_ago
            ).order_by('-created_at')[:10]
            
            for org in recent_orgs:
                stats['recent_registrations'].append({
                    'id': str(org.id),
                    'name': org.name,
                    'domain': org.domain,
                    'organization_type': org.organization_type,
                    'created_at': org.created_at.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error getting organization statistics: {str(e)}")
        
        return stats

