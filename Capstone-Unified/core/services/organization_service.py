"""
Organization Service - Organization management and trust integration
Handles organization CRUD operations with trust relationship support
"""

from typing import Dict, List, Optional, Any, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.db.models import Count, Q
from core.models.models import (
    Organization,
    TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership
)
from core.user_management.models import CustomUser, AuthenticationLog
from .trust_service import TrustService
from datetime import timedelta
import re
import uuid
import logging

logger = logging.getLogger(__name__)

class OrganizationService:
    """Service for managing organizations with integrated trust relationship support"""
    
    def __init__(self):
        self.trust_service = TrustService()
    
    def create_organization(self, creating_user: CustomUser = None, org_data: Dict = None, 
                          primary_user_data: Dict = None, name: str = None, 
                          organization_type: str = None, **kwargs) -> Tuple[Organization, CustomUser]:
        """Create a new organization with primary user"""
        
        # Validate required fields
        contact_email = kwargs.get('contact_email') or (org_data and org_data.get('contact_email'))
        if not name or not organization_type or not contact_email:
            raise ValidationError("Name, organization type, and contact email are required")
        
        logger.info(f"OrganizationService.create_organization called with primary_user_data: {primary_user_data}")
        
        if not primary_user_data:
            raise ValidationError("Primary user data is required")
        
        # Validate primary user data
        required_user_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_user_fields:
            if field not in primary_user_data or not primary_user_data[field]:
                raise ValidationError(f"Primary user '{field}' is required")
        
        # Check if organization name already exists
        if Organization.objects.filter(name=name).exists():
            raise ValidationError("Organization name already exists")
        
        # Generate domain if not provided
        if not domain:
            base_domain = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
            if not base_domain:
                base_domain = 'org'
            domain = f"{base_domain}-{str(uuid.uuid4())[:8]}.com"
            
            # Ensure domain is unique
            while Organization.objects.filter(domain=domain).exists():
                domain = f"{base_domain}-{str(uuid.uuid4())[:8]}.com"
        
        # Check if domain already exists
        if Organization.objects.filter(domain=domain).exists():
            raise ValidationError("Organization domain already exists")
        
        # Check if primary user username or email already exists
        if CustomUser.objects.filter(username=primary_user_data['username']).exists():
            raise ValidationError("Primary user username already exists")
        
        if CustomUser.objects.filter(email=primary_user_data['email']).exists():
            raise ValidationError("Primary user email already exists")
        
        try:
            with transaction.atomic():
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
                    created_by=creating_user  # Pass the user object, not username string
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
                if created_by:
                    AuthenticationLog.log_authentication_event(
                        user=created_by,
                        action='user_created',
                        success=True,
                        additional_data={
                            'organization_id': str(organization.id),
                            'organization_name': organization.name,
                            'primary_user_id': str(primary_user.id),
                            'primary_user_username': primary_user.username,
                            'action_type': 'organization_created'
                        }
                    )
                
                logger.info(f"Organization '{organization.name}' created with primary user {primary_user.username}")
                return {
                    'success': True,
                    'message': f"Organization '{organization.name}' created successfully",
                    'organization_id': str(organization.id),
                    'organization': organization,
                    'primary_user_id': str(primary_user.id),
                    'primary_user': primary_user
                }
                
        except Exception as e:
            logger.error(f"Error creating organization: {e}")
            return {
                'success': False,
                'message': f"Failed to create organization: {str(e)}"
            }
    
    def update_organization(self, updating_user, organization_id, update_data):
        """Update an organization's information"""
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        # Check permissions
        can_update = (
            updating_user.role in ['BlueVisionAdmin'] or
            (updating_user.role == 'publisher' and 
             updating_user.organization.id == organization.id)
        )
        
        if not can_update:
            raise PermissionDenied("No permission to update this organization")
        
        # Define updatable fields based on user role
        if updating_user.role == 'BlueVisionAdmin':
            updatable_fields = {
                'name', 'description', 'contact_email', 'website', 
                'organization_type', 'domain', 'is_publisher', 
                'is_verified', 'is_active'
            }
        else:
            updatable_fields = {
                'description', 'contact_email', 'website'
            }
        
        # Apply updates
        updated_fields = []
        for field, value in update_data.items():
            if field in updatable_fields and hasattr(organization, field):
                if getattr(organization, field) != value:
                    setattr(organization, field, value)
                    updated_fields.append(field)
        
        if updated_fields:
            organization.save(update_fields=updated_fields + ['updated_at'])
            
            # Log organization update
            AuthenticationLog.log_authentication_event(
                user=updating_user,
                action='user_modified',
                success=True,
                additional_data={
                    'organization_id': str(organization.id),
                    'organization_name': organization.name,
                    'updated_fields': updated_fields,
                    'action_type': 'organization_updated'
                }
            )
            
            logger.info(f"Organization '{organization.name}' updated by {updating_user.username}")
        
        return organization
    
    def get_organization_details(self, requesting_user, organization_id):
        """Get detailed information about an organization"""
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        # Check if user can access this organization
        if not self.can_access_organization(requesting_user, organization):
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
            'can_publish_threat_intelligence': organization.can_publish_threat_intelligence(),
        }
        
        # Add trust information if user has appropriate permissions
        if requesting_user.can_manage_trust_relationships:
            org_details['trust_info'] = self._get_organization_trust_info(organization)
        
        # Add user list if user can manage users
        if (requesting_user.role == 'BlueVisionAdmin' or
            (requesting_user.role == 'publisher' and 
             requesting_user.organization.id == organization.id)):
            org_details['users'] = self._get_organization_users(organization)
        
        return org_details
    
    def list_organizations(self, requesting_user, filters=None):
        """List organizations the user can access"""
        # Get base queryset
        if requesting_user.role == 'BlueVisionAdmin':
            organizations = Organization.objects.all()
        else:
            # Get accessible organization IDs through trust relationships
            accessible_org_ids = self.trust_service.get_accessible_organizations(
                str(requesting_user.organization.id)
            )
            organizations = Organization.objects.filter(
                id__in=accessible_org_ids
            )
        
        # Apply filters
        if filters:
            if 'is_active' in filters:
                organizations = organizations.filter(is_active=filters['is_active'])
            
            if 'is_publisher' in filters:
                organizations = organizations.filter(is_publisher=filters['is_publisher'])
            
            if 'organization_type' in filters:
                organizations = organizations.filter(organization_type=filters['organization_type'])
            
            if 'search' in filters:
                search_term = filters['search']
                organizations = organizations.filter(
                    Q(name__icontains=search_term) |
                    Q(domain__icontains=search_term) |
                    Q(description__icontains=search_term)
                )
        
        # Format results
        org_list = []
        for org in organizations:
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
                'is_own_organization': (requesting_user.organization and 
                                      org.id == requesting_user.organization.id)
            }
            
            # Add access level information
            if requesting_user.organization and org.id != requesting_user.organization.id:
                has_trust = self.trust_service.can_access_organization_data(
                    str(requesting_user.organization.id), str(org.id)
                )
                org_data['access_level'] = 'read' if has_trust else 'none'
            else:
                org_data['access_level'] = 'full'
            
            org_list.append(org_data)
        
        return org_list
    
    def can_access_organization(self, user, organization):
        """Check if user can access organization data"""
        # BlueVision admins can access all organizations
        if user.role == 'BlueVisionAdmin':
            return True
        
        # Users can access their own organization
        if user.organization and user.organization.id == organization.id:
            return True
        
        # Check trust relationships
        if user.organization:
            return self.trust_service.can_access_organization_data(
                str(user.organization.id), str(organization.id)
            )
        
        return False
    
    def _get_organization_trust_info(self, organization):
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
            'trust_groups': []
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
                                      if r['status'] == 'active']),
                'active_incoming': len([r for r in trust_info['trust_relationships']['incoming'] 
                                      if r['status'] == 'active'])
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
            logger.error(f"Error getting trust info for organization {organization.id}: {e}")
        
        return trust_info
    
    def _get_organization_users(self, organization):
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
            logger.error(f"Error getting users for organization {organization.id}: {e}")
        
        return users
    
    def delete_organization(self, deleting_user, organization_id, reason=''):
        """Delete/deactivate an organization and handle related data"""
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        # Check permissions - only BlueVisionAdmin can delete organizations
        if deleting_user.role != 'BlueVisionAdmin':
            raise PermissionDenied("Only BlueVision administrators can delete organizations")
        
        # Prevent deletion of own organization
        if deleting_user.organization and deleting_user.organization.id == organization.id:
            raise PermissionDenied("Cannot delete your own organization")
        
        try:
            with transaction.atomic():
                # Get organization users before deletion
                org_users = CustomUser.objects.filter(organization=organization)
                user_count = org_users.count()
                
                # Deactivate all trust relationships involving this organization
                trust_relationships = TrustRelationship.objects.filter(
                    Q(source_organization=organization) | Q(target_organization=organization)
                )
                
                for relationship in trust_relationships:
                    relationship.status = 'revoked'
                    relationship.revoked_by = deleting_user
                    relationship.revoked_at = timezone.now()
                    relationship.is_active = False
                    relationship.save()
                
                # Remove from trust groups
                trust_memberships = TrustGroupMembership.objects.filter(
                    organization=organization
                )
                trust_memberships.update(is_active=False)
                
                # Deactivate all users in the organization
                org_users.update(
                    is_active=False,
                    organization=None  # Remove organization association
                )
                
                # Mark organization as inactive instead of hard delete
                organization.is_active = False
                organization.save()
                
                # Log the deletion
                AuthenticationLog.log_authentication_event(
                    user=deleting_user,
                    action='organization_delete',
                    success=True,
                    additional_data={
                        'organization_id': str(organization.id),
                        'organization_name': organization.name,
                        'user_count': user_count,
                        'reason': reason,
                        'action_type': 'organization_deactivated'
                    }
                )
                
                logger.info(f"Organization '{organization.name}' deleted by {deleting_user.username}")
                
                return {
                    'success': True,
                    'message': f"Organization '{organization.name}' has been deactivated successfully",
                    'organization_id': str(organization.id),
                    'users_affected': user_count
                }
                
        except Exception as e:
            logger.error(f"Error deleting organization {organization_id}: {e}")
            return {
                'success': False,
                'message': f"Failed to delete organization: {str(e)}"
            }
    
    def delete_organization_permanently(self, deleting_user, organization_id, reason=''):
        """Permanently delete an organization and all related data from the database"""
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        # Check permissions - only BlueVisionAdmin can permanently delete organizations
        if deleting_user.role != 'BlueVisionAdmin':
            raise PermissionDenied("Only BlueVision administrators can permanently delete organizations")
        
        # Prevent deletion of own organization
        if deleting_user.organization and deleting_user.organization.id == organization.id:
            raise PermissionDenied("Cannot delete your own organization")
        
        organization_name = organization.name
        
        try:
            with transaction.atomic():
                # Get organization users before deletion
                org_users = CustomUser.objects.filter(organization=organization)
                user_count = org_users.count()
                
                # Delete all trust relationships involving this organization
                trust_relationships = TrustRelationship.objects.filter(
                    Q(source_organization=organization) | Q(target_organization=organization)
                )
                trust_relationships.delete()
                
                # Remove from trust groups
                trust_memberships = TrustGroupMembership.objects.filter(
                    organization=organization
                )
                trust_memberships.delete()
                
                # Delete all users in the organization
                org_users.delete()
                
                # Log the permanent deletion before deleting the organization
                AuthenticationLog.log_authentication_event(
                    user=deleting_user,
                    action='organization_delete_permanent',
                    success=True,
                    additional_data={
                        'organization_id': str(organization.id),
                        'organization_name': organization_name,
                        'user_count': user_count,
                        'reason': reason,
                        'action_type': 'organization_permanently_deleted'
                    }
                )
                
                # Permanently delete the organization
                organization.delete()
                
                logger.info(f"Organization '{organization_name}' permanently deleted by {deleting_user.username}")
                
                return {
                    'success': True,
                    'message': f"Organization '{organization_name}' has been permanently deleted",
                    'organization_id': str(organization_id),
                    'users_affected': user_count
                }
                
        except Exception as e:
            logger.error(f"Error permanently deleting organization {organization_id}: {e}")
            return {
                'success': False,
                'message': f"Failed to permanently delete organization: {str(e)}"
            }
    
    def reactivate_organization(self, reactivating_user, organization_id, reason=''):
        """Reactivate a deactivated organization"""
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise ValidationError("Organization not found")
        
        # Check permissions - only BlueVisionAdmin can reactivate organizations
        if reactivating_user.role != 'BlueVisionAdmin':
            raise PermissionDenied("Only BlueVision administrators can reactivate organizations")
        
        # Check if organization is already active
        if organization.is_active:
            return {
                'success': False,
                'message': 'Organization is already active'
            }
        
        try:
            with transaction.atomic():
                # Reactivate the organization
                organization.is_active = True
                organization.save()
                
                # Reactivate all users in the organization (optional - could be selective)
                # For now, let's not automatically reactivate users - let them be reactivated individually
                
                # Log the reactivation
                AuthenticationLog.log_authentication_event(
                    user=reactivating_user,
                    action='organization_reactivate',
                    success=True,
                    additional_data={
                        'organization_id': str(organization.id),
                        'organization_name': organization.name,
                        'reason': reason,
                        'action_type': 'organization_reactivated'
                    }
                )
                
                logger.info(f"Organization '{organization.name}' reactivated by {reactivating_user.username}")
                
                return {
                    'success': True,
                    'message': f"Organization '{organization.name}' has been reactivated successfully",
                    'organization_id': str(organization.id)
                }
                
        except Exception as e:
            logger.error(f"Error reactivating organization {organization_id}: {e}")
            return {
                'success': False,
                'message': f"Failed to reactivate organization: {str(e)}"
            }