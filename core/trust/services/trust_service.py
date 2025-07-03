from typing import Dict, List, Optional, Tuple, Any
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from datetime import timedelta
import logging
import django.db.models

from ..models import (
    TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership,
    TrustLog, SharingPolicy, TRUST_STATUS_CHOICES, RELATIONSHIP_TYPE_CHOICES
)
from ..patterns.repository import trust_repository_manager
from ..patterns.observer import trust_event_manager, notify_trust_relationship_event
from ..patterns.factory import trust_factory

logger = logging.getLogger(__name__)


class TrustService:
    """
    Core service for managing trust relationships between organizations.
    Implements business logic for trust establishment, validation, and management.
    """

    @staticmethod
    def create_trust_relationship(
        source_org: str,
        target_org: str,
        trust_level_name: str,
        relationship_type: str = 'bilateral',
        created_by: str = None,
        sharing_preferences: Dict = None,
        valid_until: timezone.datetime = None,
        notes: str = None,
        export_to_stix: bool = True,
        **kwargs
    ) -> TrustRelationship:
        """
        Create a new trust relationship between two organizations.
        
        Args:
            source_org: UUID of the source organization
            target_org: UUID of the target organization
            trust_level_name: Name of the trust level to apply
            relationship_type: Type of relationship (bilateral, community, etc.)
            created_by: User creating the relationship
            sharing_preferences: Organization-specific sharing preferences
            valid_until: Optional expiration date
            notes: Optional notes about the relationship
            
        Returns:
            TrustRelationship: The created trust relationship
            
        Raises:
            ValidationError: If the relationship cannot be created
        """
        if source_org == target_org:
            raise ValidationError("Source and target organizations cannot be the same.")
        try:
            with transaction.atomic():
                # Use repository pattern for creation
                trust_level = trust_repository_manager.levels.get_by_name(trust_level_name)
                if not trust_level:
                    raise ValidationError(f"Trust level '{trust_level_name}' not found or inactive")
                
                # Create relationship using repository
                relationship = trust_repository_manager.relationships.create(
                    source_org=source_org,
                    target_org=target_org,
                    trust_level=trust_level,
                    created_by=created_by or 'system',
                    relationship_type=relationship_type,
                    sharing_preferences=sharing_preferences or {},
                    valid_until=valid_until,
                    notes=notes or '',
                    **kwargs
                )
                
                # Auto-approve for community relationships
                if relationship_type == 'community':
                    relationship.approved_by_source = True
                    relationship.approved_by_source_user = created_by
                    relationship.save()
                
                # Notify observers using observer pattern
                notify_trust_relationship_event(
                    'relationship_created',
                    relationship,
                    created_by or 'system',
                    trust_level=trust_level_name,
                    relationship_type=relationship_type
                )
                
                # Log relationship creation 
                trust_factory.create_log(
                    action='relationship_created',
                    source_organization=source_org,
                    user=created_by or 'system',
                    target_organization=target_org,
                    trust_relationship=relationship,
                    details={
                        'trust_level': trust_level_name,
                        'relationship_type': relationship_type
                    }
                )
                
                logger.info(f"Trust relationship created: {source_org} -> {target_org} ({trust_level_name})")
                return relationship
                
        except IntegrityError as e:
            if 'duplicate key' in str(e).lower():
                raise ValidationError("Active trust relationship already exists between these organizations")
            else:
                logger.error(f"Database integrity error creating trust relationship: {str(e)}")
                raise ValidationError(f"Database error: {str(e)}")
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Failed to create trust relationship: {str(e)}")
            raise ValidationError(f"Unexpected error: {str(e)}")

    @staticmethod
    def approve_trust_relationship(
        relationship_id: str,
        approving_org: str,
        approved_by_user: str,
        **kwargs
    ) -> bool:
        """
        Approve a trust relationship on behalf of an organization.
        
        Args:
            relationship_id: UUID of the trust relationship
            approving_org: UUID of the organization approving
            approved_by_user: User performing the approval
            
        Returns:
            bool: True if approval was successful and relationship is now active
        """
        try:
            with transaction.atomic():
                relationship = TrustRelationship.objects.select_for_update().get(
                    id=relationship_id,
                    is_active=True
                )
                
                # Determine which side is approving
                if relationship.source_organization == approving_org:
                    if relationship.approved_by_source:
                        raise ValidationError("Source organization has already approved this relationship")
                    relationship.approved_by_source = True
                    relationship.approved_by_source_user = approved_by_user
                    
                elif relationship.target_organization == approving_org:
                    if relationship.approved_by_target:
                        raise ValidationError("Target organization has already approved this relationship")
                    relationship.approved_by_target = True
                    relationship.approved_by_target_user = approved_by_user
                    
                else:
                    raise ValidationError("Organization is not part of this trust relationship")
                
                relationship.last_modified_by = approved_by_user
                relationship.save()
                
                # Check if relationship is now fully approved and can be activated
                activated = False
                if relationship.is_fully_approved and relationship.status == 'pending':
                    activated = relationship.activate()
                
                # Log the approval
                TrustLog.log_trust_event(
                    action='relationship_approved',
                    source_organization=approving_org,
                    target_organization=relationship.target_organization if approving_org == relationship.source_organization else relationship.source_organization,
                    trust_relationship=relationship,
                    user=approved_by_user,
                    details={'activated': activated}
                )
                
                logger.info(f"Trust relationship approved by {approving_org} (activated: {activated})")
                return activated
                
        except TrustRelationship.DoesNotExist:
            raise ValidationError("Trust relationship not found")
        except Exception as e:
            logger.error(f"Failed to approve trust relationship: {str(e)}")
            raise

    @staticmethod
    def revoke_trust_relationship(
        relationship_id: str,
        revoking_org: str,
        revoked_by_user: str,
        reason: str = None,
        **kwargs
    ) -> bool:
        """
        Revoke a trust relationship.
        
        Args:
            relationship_id: UUID of the trust relationship
            revoking_org: UUID of the organization revoking
            revoked_by_user: User performing the revocation
            reason: Optional reason for revocation
            
        Returns:
            bool: True if revocation was successful
        """
        try:
            with transaction.atomic():
                relationship = TrustRelationship.objects.select_for_update().get(
                    id=relationship_id,
                    is_active=True
                )
                
                # Verify organization can revoke this relationship
                if (relationship.source_organization != revoking_org and 
                    relationship.target_organization != revoking_org):
                    raise ValidationError("Organization is not part of this trust relationship")
                
                # Revoke the relationship
                relationship.revoke(revoked_by_user, reason)
                
                # Log the revocation
                TrustLog.log_trust_event(
                    action='relationship_revoked',
                    source_organization=revoking_org,
                    target_organization=relationship.target_organization if revoking_org == relationship.source_organization else relationship.source_organization,
                    trust_relationship=relationship,
                    user=revoked_by_user,
                    details={'reason': reason or 'No reason provided'}
                )
                
                logger.info(f"Trust relationship revoked by {revoking_org}: {reason or 'No reason'}")
                return True
                
        except TrustRelationship.DoesNotExist:
            raise ValidationError("Trust relationship not found")
        except Exception as e:
            logger.error(f"Failed to revoke trust relationship: {str(e)}")
            raise

    @staticmethod
    def get_trust_relationships_for_organization(
        organization: str,
        include_inactive: bool = False,
        relationship_type: str = None
    ) -> List[TrustRelationship]:
        """
        Get all trust relationships for an organization.
        
        Args:
            organization: UUID of the organization
            include_inactive: Whether to include inactive relationships
            relationship_type: Filter by relationship type
            
        Returns:
            List of TrustRelationship objects
        """
        queryset = TrustRelationship.objects.filter(
            django.db.models.Q(source_organization=organization) | 
            django.db.models.Q(target_organization=organization)
        )
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
            
        if relationship_type:
            queryset = queryset.filter(relationship_type=relationship_type)
            
        return queryset.select_related('trust_level', 'trust_group').order_by('-created_at')

    @staticmethod
    def check_trust_level(
        source_org: str,
        target_org: str
    ) -> Optional[Tuple[TrustLevel, TrustRelationship]]:
        """
        Check the trust level between two organizations.
        
        Args:
            source_org: UUID of the source organization
            target_org: UUID of the target organization
            
        Returns:
            Tuple of (TrustLevel, TrustRelationship) if trust exists, None otherwise
        """
        # Direct bilateral relationship
        relationship = TrustRelationship.objects.filter(
            source_organization=source_org,
            target_organization=target_org,
            is_active=True
        ).select_related('trust_level').first()
        
        if relationship:
            try:
                if relationship.is_effective:
                    return relationship.trust_level, relationship
            except AttributeError:
                # Fallback if is_effective method doesn't exist
                if (relationship.status == 'active' and 
                    getattr(relationship, 'approved_by_source', False) and 
                    getattr(relationship, 'approved_by_target', False)):
                    return relationship.trust_level, relationship
        
        # Check for bilateral reverse relationship
        reverse_relationship = TrustRelationship.objects.filter(
            source_organization=target_org,
            target_organization=source_org,
            is_active=True,
            is_bilateral=True
        ).select_related('trust_level').first()
        
        if reverse_relationship:
            try:
                if reverse_relationship.is_effective:
                    return reverse_relationship.trust_level, reverse_relationship
            except AttributeError:
                # Fallback if is_effective method doesn't exist
                if (reverse_relationship.status == 'active' and 
                    getattr(reverse_relationship, 'approved_by_source', False) and 
                    getattr(reverse_relationship, 'approved_by_target', False)):
                    return reverse_relationship.trust_level, reverse_relationship
        
        # Check for community relationships (both orgs in same trust group)
        source_groups = TrustGroupMembership.objects.filter(
            organization=source_org,
            is_active=True
        ).values_list('trust_group_id', flat=True)
        
        if source_groups:
            common_membership = TrustGroupMembership.objects.filter(
                organization=target_org,
                trust_group_id__in=source_groups,
                is_active=True
            ).select_related('trust_group__default_trust_level').first()
            
            if common_membership and common_membership.trust_group.is_active:
                # Create implicit community relationship
                community_relationship = TrustRelationship(
                    source_organization=source_org,
                    target_organization=target_org,
                    relationship_type='community',
                    trust_level=common_membership.trust_group.default_trust_level,
                    trust_group=common_membership.trust_group,
                    status='active',
                    is_active=True,
                    approved_by_source=True,
                    approved_by_target=True
                )
                
                return common_membership.trust_group.default_trust_level, community_relationship
        
        return None

    @staticmethod
    def can_access_intelligence(
        requesting_org: str,
        intelligence_owner: str,
        intelligence_type: str = None,
        required_access_level: str = 'read'
    ) -> Tuple[bool, str, Optional[TrustRelationship]]:
        """
        Check if an organization can access intelligence from another organization.
        
        Args:
            requesting_org: UUID of the requesting organization
            intelligence_owner: UUID of the intelligence owner
            intelligence_type: Type of intelligence being requested
            required_access_level: Required access level
            
        Returns:
            Tuple of (can_access, reason, trust_relationship)
        """
        if requesting_org == intelligence_owner:
            return True, "Own organization", None
        
        trust_info = TrustService.check_trust_level(requesting_org, intelligence_owner)
        if not trust_info:
            return False, "No trust relationship exists", None
        
        trust_level, relationship = trust_info
        
        # Ensure the relationship is properly approved and active
        try:
            if not relationship.is_effective:
                return False, "Trust relationship not effective", relationship
        except AttributeError:
            # Fallback if is_effective method doesn't exist
            if (relationship.status != 'active' or 
                not getattr(relationship, 'approved_by_source', False) or 
                not getattr(relationship, 'approved_by_target', False)):
                return False, "Trust relationship not fully approved", relationship
        
        # Map trust level to access level
        access_mapping = {
            'complete': 'full',
            'high': 'contribute',
            'medium': 'subscribe',
            'low': 'read',
            'none': 'none'
        }
        
        effective_access = access_mapping.get(trust_level.level, 'none')
        
        # Check if effective access meets required level
        access_levels = ['none', 'read', 'subscribe', 'contribute', 'full']
        
        try:
            effective_index = access_levels.index(effective_access)
            required_index = access_levels.index(required_access_level)
            
            if effective_index < required_index:
                return False, f"Insufficient access level (has: {effective_access}, needs: {required_access_level})", relationship
        except ValueError:
            # If access level not in standard list, assume insufficient
            return False, f"Invalid access level: {effective_access}", relationship
        
        return True, f"Authorized via trust relationship ({trust_level.name})", relationship

    @staticmethod
    def get_sharing_organizations(
        source_org: str,
        min_trust_level: str = 'low'
    ) -> List[Tuple[str, TrustLevel, TrustRelationship]]:
        """
        Get all organizations that can receive intelligence from a source organization.
        
        Args:
            source_org: UUID of the source organization
            min_trust_level: Minimum trust level required
            
        Returns:
            List of tuples (org_id, trust_level, relationship)
        """
        try:
            # Try to find by name first, then by level
            min_trust_obj = TrustLevel.objects.filter(
                django.db.models.Q(name=min_trust_level) | django.db.models.Q(level=min_trust_level),
                is_active=True
            ).first()
            
            if min_trust_obj:
                min_trust_value = min_trust_obj.numerical_value
            else:
                # Fallback - try to get any trust level and use a default value
                min_trust_obj = TrustLevel.objects.filter(is_active=True).first()
                min_trust_value = 25  # Default low trust value
                logger.warning(f"Trust level '{min_trust_level}' not found, using default minimum value")
                if not min_trust_obj:
                    return []
        except Exception as e:
            logger.error(f"Error retrieving trust level: {e}")
            return []
        
        # Get direct relationships
        relationships = TrustRelationship.objects.filter(
            source_organization=source_org,
            is_active=True,
            trust_level__numerical_value__gte=min_trust_value
        ).select_related('trust_level')
        
        logger.debug(f"Querying relationships for {source_org} with min_trust_value {min_trust_value}")
        logger.debug(f"Found {relationships.count()} direct relationships")
        
        sharing_orgs = []
        for rel in relationships:
            try:
                is_effective = rel.is_effective
            except AttributeError:
                is_effective = (getattr(rel, 'approved_by_source', False) and 
                              getattr(rel, 'approved_by_target', False) and
                              rel.is_active)
            
            logger.debug(f"Relationship {rel.id}: is_effective={is_effective}, status={rel.status}, approved_source={getattr(rel, 'approved_by_source', 'N/A')}, approved_target={getattr(rel, 'approved_by_target', 'N/A')}")
            
            if is_effective:
                sharing_orgs.append((rel.target_organization, rel.trust_level, rel))
        
        # Get bilateral relationships (reverse direction)
        reverse_relationships = TrustRelationship.objects.filter(
            target_organization=source_org,
            is_active=True,
            is_bilateral=True,
            trust_level__numerical_value__gte=min_trust_value
        ).select_related('trust_level')
        
        for rel in reverse_relationships:
            try:
                is_effective = rel.is_effective
            except AttributeError:
                is_effective = (getattr(rel, 'approved_by_source', False) and 
                              getattr(rel, 'approved_by_target', False) and
                              rel.is_active)
            
            if is_effective:
                sharing_orgs.append((rel.source_organization, rel.trust_level, rel))
        
        # Get community relationships
        group_memberships = TrustGroupMembership.objects.filter(
            organization=source_org,
            is_active=True
        ).select_related('trust_group__default_trust_level')
        
        for membership in group_memberships:
            if (membership.trust_group.is_active and 
                membership.trust_group.default_trust_level.numerical_value >= min_trust_value):
                
                # Get other members of this group
                other_members = TrustGroupMembership.objects.filter(
                    trust_group=membership.trust_group,
                    is_active=True
                ).exclude(organization=source_org)
                
                for other_member in other_members:
                    # Create implicit community relationship
                    community_rel = TrustRelationship(
                        source_organization=source_org,
                        target_organization=other_member.organization,
                        relationship_type='community',
                        trust_level=membership.trust_group.default_trust_level,
                        trust_group=membership.trust_group,
                        status='active',
                        is_active=True
                    )
                    
                    sharing_orgs.append((
                        other_member.organization,
                        membership.trust_group.default_trust_level,
                        community_rel
                    ))
        
        return sharing_orgs

    @staticmethod
    def update_trust_level(
        relationship_id: str,
        new_trust_level_name: str,
        updated_by: str,
        reason: str = None
    ) -> bool:
        """
        Update the trust level of an existing relationship.
        
        Args:
            relationship_id: UUID of the trust relationship
            new_trust_level_name: Name of the new trust level
            updated_by: User making the update
            reason: Optional reason for the update
            
        Returns:
            bool: True if update was successful
        """
        try:
            with transaction.atomic():
                relationship = TrustRelationship.objects.select_for_update().get(
                    id=relationship_id,
                    is_active=True
                )
                
                # Get new trust level
                new_trust_level = TrustLevel.objects.get(
                    name=new_trust_level_name,
                    is_active=True
                )
                
                old_trust_level = relationship.trust_level
                
                # Update the relationship
                relationship.trust_level = new_trust_level
                relationship.anonymization_level = new_trust_level.default_anonymization_level
                relationship.access_level = new_trust_level.default_access_level
                relationship.last_modified_by = updated_by
                
                if reason:
                    relationship.notes = f"{relationship.notes}\nTrust level updated: {reason}" if relationship.notes else f"Trust level updated: {reason}"
                
                relationship.save()
                
                # Log the update
                TrustLog.log_trust_event(
                    action='trust_level_modified',
                    source_organization=relationship.source_organization,
                    target_organization=relationship.target_organization,
                    trust_relationship=relationship,
                    user=updated_by,
                    details={
                        'old_trust_level': old_trust_level.name,
                        'new_trust_level': new_trust_level.name,
                        'reason': reason or 'No reason provided'
                    }
                )
                
                logger.info(f"Trust level updated for relationship {relationship_id}: {old_trust_level.name} -> {new_trust_level.name}")
                return True
                
        except (TrustRelationship.DoesNotExist, TrustLevel.DoesNotExist) as e:
            raise ValidationError(f"Update failed: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to update trust level: {str(e)}")
            raise

    @staticmethod
    def get_available_trust_levels() -> List[TrustLevel]:
        """
        Get all available active trust levels.
        
        Returns:
            List[TrustLevel]: List of active trust levels ordered by numerical value
        """
        return TrustLevel.objects.filter(is_active=True).order_by('numerical_value')