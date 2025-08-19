"""
Trust Service - Core trust management functionality
Handles trust relationships, groups, and access control decisions
"""

from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models.models import (
    TrustRelationship, TrustGroup, TrustGroupMembership, 
    TrustLevel, TrustLog, Organization, CustomUser
)
import uuid
import logging

logger = logging.getLogger(__name__)

class TrustService:
    """Service class for managing trust relationships and access control"""
    
    def create_trust_relationship(self, source_org_id, target_org_id, trust_level_id, 
                                 created_by_user, relationship_type='bilateral',
                                 anonymization_level='partial', access_level='read'):
        """Create a new trust relationship between organizations"""
        try:
            # Validate organizations exist
            source_org = Organization.objects.get(id=source_org_id)
            target_org = Organization.objects.get(id=target_org_id)
            trust_level = TrustLevel.objects.get(id=trust_level_id)
            
            # Check if relationship already exists
            existing = TrustRelationship.objects.filter(
                source_organization=source_org,
                target_organization=target_org
            ).first()
            
            if existing:
                raise ValidationError("Trust relationship already exists between these organizations")
            
            # Create the relationship
            relationship = TrustRelationship.objects.create(
                source_organization=source_org,
                target_organization=target_org,
                trust_level=trust_level,
                relationship_type=relationship_type,
                anonymization_level=anonymization_level,
                access_level=access_level,
                status='pending',
                created_by=created_by_user,
                is_active=True
            )
            
            # Log the creation
            TrustLog.log_trust_event(
                action='relationship_created',
                source_organization=source_org,
                target_organization=target_org,
                trust_relationship=relationship,
                user=created_by_user,
                success=True,
                details={'relationship_type': relationship_type}
            )
            
            logger.info(f"Trust relationship created: {source_org.name} -> {target_org.name}")
            return relationship
            
        except Exception as e:
            logger.error(f"Error creating trust relationship: {e}")
            raise
    
    def approve_trust_relationship(self, relationship_id, approving_org_id, approving_user):
        """Approve a trust relationship from an organization's perspective"""
        try:
            relationship = TrustRelationship.objects.get(id=relationship_id)
            approving_org = Organization.objects.get(id=approving_org_id)
            
            # Check if the user can approve on behalf of this organization
            if approving_user.organization != approving_org:
                raise ValidationError("User cannot approve on behalf of this organization")
            
            # Set approval status
            if approving_org == relationship.source_organization:
                relationship.approved_by_source = True
                relationship.approved_by_source_user = approving_user
                relationship.source_approval_status = 'approved'
            elif approving_org == relationship.target_organization:
                relationship.approved_by_target = True
                relationship.approved_by_target_user = approving_user
                relationship.target_approval_status = 'approved'
            else:
                raise ValidationError("Organization is not part of this trust relationship")
            
            # Check if fully approved and activate
            if relationship.approved_by_source and relationship.approved_by_target:
                relationship.status = 'active'
                relationship.activated_at = timezone.now()
            
            relationship.save()
            
            # Log the approval
            TrustLog.log_trust_event(
                action='relationship_approved',
                source_organization=relationship.source_organization,
                target_organization=relationship.target_organization,
                trust_relationship=relationship,
                user=approving_user,
                success=True,
                details={'approving_org': approving_org.name}
            )
            
            logger.info(f"Trust relationship approved by {approving_org.name}")
            return relationship
            
        except Exception as e:
            logger.error(f"Error approving trust relationship: {e}")
            raise
    
    def accept_bilateral_trust(self, trust_id, trust_level=None, message='', accepted_by=None):
        """Accept a bilateral trust request"""
        try:
            relationship = TrustRelationship.objects.get(id=trust_id)
            
            if not accepted_by or not accepted_by.organization:
                raise ValidationError("User must belong to an organization")
            
            # Check if user can accept this relationship
            # BlueVisionAdmin can accept any relationship, others can only accept for their own organization
            if accepted_by.role != 'BlueVisionAdmin':
                if accepted_by.organization != relationship.target_organization:
                    raise ValidationError("User can only accept requests for their own organization")
            
            # Update trust level if provided
            if trust_level:
                try:
                    trust_level_obj = TrustLevel.objects.get(level=trust_level)
                    relationship.trust_level = trust_level_obj
                except TrustLevel.DoesNotExist:
                    pass  # Keep existing trust level
            
            # Set approval status based on user's organization or admin status
            if accepted_by.role == 'BlueVisionAdmin':
                # BlueVisionAdmin can approve for both sides, so approve both
                relationship.approved_by_source = True
                relationship.approved_by_target = True
                relationship.approved_by_source_user = accepted_by
                relationship.approved_by_target_user = accepted_by
                relationship.source_approval_status = 'approved'
                relationship.target_approval_status = 'approved'
                relationship.status = 'active'
                relationship.activated_at = timezone.now()
            elif accepted_by.organization == relationship.target_organization:
                # Target organization accepting
                relationship.approved_by_target = True
                relationship.approved_by_target_user = accepted_by
                relationship.target_approval_status = 'approved'
                
                # Check if both sides have approved
                if relationship.approved_by_source and relationship.approved_by_target:
                    relationship.status = 'active'
                    relationship.activated_at = timezone.now()
                else:
                    relationship.status = 'pending'
            elif accepted_by.organization == relationship.source_organization:
                # Source organization accepting (shouldn't normally happen, but handle it)
                relationship.approved_by_source = True
                relationship.approved_by_source_user = accepted_by
                relationship.source_approval_status = 'approved'
                
                # Check if both sides have approved
                if relationship.approved_by_source and relationship.approved_by_target:
                    relationship.status = 'active'
                    relationship.activated_at = timezone.now()
                else:
                    relationship.status = 'pending'
            
            relationship.save()
            
            # Log the acceptance
            TrustLog.log_trust_event(
                action='relationship_approved',
                source_organization=relationship.source_organization,
                target_organization=relationship.target_organization,
                trust_relationship=relationship,
                user=accepted_by,
                success=True,
                details={'action': 'accepted', 'message': message}
            )
            
            logger.info(f"Trust relationship accepted by {accepted_by.organization.name}")
            
            return {
                'success': True,
                'message': f'Trust relationship accepted successfully',
                'relationship': relationship
            }
            
        except Exception as e:
            logger.error(f"Error accepting bilateral trust: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def reject_bilateral_trust(self, trust_id, message='', rejected_by=None):
        """Reject a bilateral trust request"""
        try:
            relationship = TrustRelationship.objects.get(id=trust_id)
            
            if not rejected_by or not rejected_by.organization:
                raise ValidationError("User must belong to an organization")
            
            # Check if user's organization is the target organization
            if rejected_by.organization != relationship.target_organization:
                raise ValidationError("User can only reject requests for their own organization")
            
            # Set rejection status
            relationship.status = 'rejected'
            relationship.approved_by_target = False
            relationship.target_approval_status = 'rejected'
            
            relationship.save()
            
            # Log the rejection
            TrustLog.log_trust_event(
                action='relationship_rejected',
                source_organization=relationship.source_organization,
                target_organization=relationship.target_organization,
                trust_relationship=relationship,
                user=rejected_by,
                success=True,
                details={'action': 'rejected', 'message': message}
            )
            
            logger.info(f"Trust relationship rejected by {rejected_by.organization.name}")
            
            return {
                'success': True,
                'message': f'Trust relationship rejected successfully',
                'relationship': relationship
            }
            
        except Exception as e:
            logger.error(f"Error rejecting bilateral trust: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def update_bilateral_trust(self, trust_id, trust_level=None, status=None, notes=None, message='', updated_by=None):
        """Update a bilateral trust relationship"""
        try:
            relationship = TrustRelationship.objects.get(id=trust_id)
            
            # Update trust level if provided
            if trust_level:
                try:
                    trust_level_obj = TrustLevel.objects.get(level=trust_level)
                    relationship.trust_level = trust_level_obj
                except TrustLevel.DoesNotExist:
                    return {
                        'success': False,
                        'message': f'Trust level "{trust_level}" not found'
                    }
            
            # Update status if provided
            if status:
                valid_statuses = ['pending', 'active', 'suspended', 'revoked', 'expired']
                if status not in valid_statuses:
                    return {
                        'success': False,
                        'message': f'Invalid status "{status}". Valid options: {", ".join(valid_statuses)}'
                    }
                relationship.status = status
            
            # Update notes if provided
            if notes is not None:  # Allow empty string to clear notes
                relationship.notes = notes
            
            # Update last modified info
            if updated_by:
                relationship.last_modified_by = updated_by
            
            relationship.save()
            
            # Log the update
            log_details = {'message': message}
            if trust_level:
                log_details['new_trust_level'] = trust_level
            if status:
                log_details['new_status'] = status
            if notes is not None:
                log_details['notes_updated'] = True
                
            TrustLog.log_trust_event(
                action='relationship_modified',
                source_organization=relationship.source_organization,
                target_organization=relationship.target_organization,
                trust_relationship=relationship,
                user=updated_by,
                success=True,
                details=log_details
            )
            
            logger.info(f"Trust relationship updated: {relationship.id}")
            
            return {
                'success': True,
                'message': 'Trust relationship updated successfully',
                'relationship': relationship
            }
            
        except Exception as e:
            logger.error(f"Error updating bilateral trust: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def revoke_bilateral_trust(self, trust_id, message='', revoked_by=None):
        """Revoke a bilateral trust relationship"""
        try:
            relationship = TrustRelationship.objects.get(id=trust_id)
            
            relationship.status = 'revoked'
            relationship.revoked_by = revoked_by
            relationship.revoked_at = timezone.now()
            relationship.is_active = False
            
            relationship.save()
            
            # Log the revocation
            TrustLog.log_trust_event(
                action='relationship_revoked',
                source_organization=relationship.source_organization,
                target_organization=relationship.target_organization,
                trust_relationship=relationship,
                user=revoked_by,
                success=True,
                details={'message': message}
            )
            
            logger.info(f"Trust relationship revoked: {relationship.id}")
            
            return {
                'success': True,
                'message': 'Trust relationship revoked successfully'
            }
            
        except Exception as e:
            logger.error(f"Error revoking bilateral trust: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_trust_level(self, org1, org2):
        """Get trust level between two organizations"""
        try:
            relationship = TrustRelationship.objects.filter(
                Q(source_organization=org1, target_organization=org2) |
                Q(source_organization=org2, target_organization=org1),
                status='active',
                is_active=True
            ).first()
            
            if relationship:
                return relationship.trust_level.level if relationship.trust_level else 'none'
            return 'none'
            
        except Exception as e:
            logger.error(f"Error getting trust level: {e}")
            return 'none'
    
    def get_trust_dashboard_data(self, organization):
        """Get trust dashboard data for an organization"""
        try:
            relationships = TrustRelationship.objects.filter(
                Q(source_organization=organization) | Q(target_organization=organization)
            )
            
            dashboard_data = {
                'total_relationships': relationships.count(),
                'active_relationships': relationships.filter(status='active').count(),
                'pending_relationships': relationships.filter(status='pending').count(),
                'trust_levels': {
                    'high': relationships.filter(trust_level__level='restricted').count(),
                    'medium': relationships.filter(trust_level__level='trusted').count(),
                    'low': relationships.filter(trust_level__level='public').count(),
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting trust dashboard data: {e}")
            return {}
    
    def can_access_organization_data(self, requesting_org_id, target_org_id):
        """Check if requesting organization can access target organization's data"""
        try:
            # Same organization always has access
            if str(requesting_org_id) == str(target_org_id):
                return True
            
            # Check for active trust relationship
            relationship = TrustRelationship.objects.filter(
                Q(source_organization_id=requesting_org_id, target_organization_id=target_org_id) |
                Q(source_organization_id=target_org_id, target_organization_id=requesting_org_id),
                status='active',
                is_active=True
            ).first()
            
            if relationship and relationship.is_effective:
                return True
            
            # Check for community trust through groups
            return self._check_community_trust(requesting_org_id, target_org_id)
            
        except Exception as e:
            logger.error(f"Error checking access: {e}")
            return False
    
    def get_accessible_organizations(self, requesting_org_id):
        """Get list of organizations that the requesting org can access"""
        try:
            accessible_org_ids = [requesting_org_id]  # Always include self
            
            # Get organizations through direct trust relationships
            direct_relationships = TrustRelationship.objects.filter(
                Q(source_organization_id=requesting_org_id) |
                Q(target_organization_id=requesting_org_id),
                status='active',
                is_active=True
            ).select_related('source_organization', 'target_organization')
            
            for rel in direct_relationships:
                if rel.is_effective:
                    other_org_id = (rel.target_organization.id 
                                  if str(rel.source_organization.id) == str(requesting_org_id)
                                  else rel.source_organization.id)
                    accessible_org_ids.append(str(other_org_id))
            
            # Get organizations through group memberships
            group_orgs = self._get_group_accessible_organizations(requesting_org_id)
            accessible_org_ids.extend(group_orgs)
            
            return list(set(accessible_org_ids))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting accessible organizations: {e}")
            return [requesting_org_id]
    
    def create_trust_group(self, name, description, group_type, created_by_org, 
                          is_public=False, requires_approval=True, default_trust_level_id=None):
        """Create a new trust group"""
        try:
            group_data = {
                'name': name,
                'description': description,
                'group_type': group_type,
                'is_public': is_public,
                'requires_approval': requires_approval,
                'created_by': str(created_by_org.id),
                'administrators': [str(created_by_org.id)],
                'is_active': True
            }
            
            if default_trust_level_id:
                group_data['default_trust_level_id'] = default_trust_level_id
            
            group = TrustGroup.objects.create(**group_data)
            
            # Add creating organization as administrator member
            TrustGroupMembership.objects.create(
                trust_group=group,
                organization=created_by_org,
                membership_type='administrator',
                is_active=True
            )
            
            # Log group creation
            TrustLog.log_trust_event(
                action='group_created',
                source_organization=created_by_org,
                trust_group=group,
                user=None,  # Organization-level action
                success=True,
                details={'group_type': group_type}
            )
            
            logger.info(f"Trust group created: {group.name}")
            return group
            
        except Exception as e:
            logger.error(f"Error creating trust group: {e}")
            raise
    
    def join_trust_group(self, group_id, organization_id, requesting_user=None):
        """Request to join a trust group"""
        try:
            group = TrustGroup.objects.get(id=group_id)
            organization = Organization.objects.get(id=organization_id)
            
            # Check if already a member
            existing = TrustGroupMembership.objects.filter(
                trust_group=group,
                organization=organization
            ).first()
            
            if existing and existing.is_active:
                raise ValidationError("Organization is already a member of this group")
            
            # Create membership
            membership = TrustGroupMembership.objects.create(
                trust_group=group,
                organization=organization,
                membership_type='member',
                is_active=not group.requires_approval,  # Active immediately if no approval needed
                invited_by=str(organization.id)
            )
            
            # Log group join
            TrustLog.log_trust_event(
                action='group_joined',
                source_organization=organization,
                trust_group=group,
                user=requesting_user,
                success=True,
                details={'requires_approval': group.requires_approval}
            )
            
            logger.info(f"Organization {organization.name} joined group {group.name}")
            return membership
            
        except Exception as e:
            logger.error(f"Error joining trust group: {e}")
            raise
    
    def get_trust_relationships_for_organization(self, org_id):
        """Get all trust relationships for an organization"""
        try:
            relationships = TrustRelationship.objects.filter(
                Q(source_organization_id=org_id) | Q(target_organization_id=org_id)
            ).select_related(
                'source_organization', 'target_organization', 'trust_level'
            ).order_by('-created_at')
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error getting trust relationships: {e}")
            return TrustRelationship.objects.none()
    
    def _check_community_trust(self, requesting_org_id, target_org_id):
        """Check if organizations have community trust through shared groups"""
        try:
            # Get groups that both organizations are members of
            requesting_groups = TrustGroupMembership.objects.filter(
                organization_id=requesting_org_id,
                is_active=True
            ).values_list('trust_group_id', flat=True)
            
            target_groups = TrustGroupMembership.objects.filter(
                organization_id=target_org_id,
                is_active=True,
                trust_group_id__in=requesting_groups
            ).exists()
            
            return target_groups
            
        except Exception as e:
            logger.error(f"Error checking community trust: {e}")
            return False
    
    def _get_group_accessible_organizations(self, requesting_org_id):
        """Get organizations accessible through group memberships"""
        try:
            # Get all groups the requesting org is a member of
            group_ids = TrustGroupMembership.objects.filter(
                organization_id=requesting_org_id,
                is_active=True
            ).values_list('trust_group_id', flat=True)
            
            # Get all other organizations in those groups
            group_org_ids = TrustGroupMembership.objects.filter(
                trust_group_id__in=group_ids,
                is_active=True
            ).exclude(
                organization_id=requesting_org_id
            ).values_list('organization_id', flat=True)
            
            return [str(org_id) for org_id in group_org_ids]
            
        except Exception as e:
            logger.error(f"Error getting group accessible organizations: {e}")
            return []