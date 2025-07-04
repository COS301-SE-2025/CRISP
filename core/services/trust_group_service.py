from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
import logging

from ..models.models import (
    TrustGroup, TrustGroupMembership, TrustLevel, TrustLog
)

logger = logging.getLogger(__name__)


class TrustGroupService:
    """
    Service for managing trust groups and community-based trust relationships.
    Handles group creation, membership management, and group-based sharing policies.
    """

    @staticmethod
    def create_trust_group(
        name: str,
        description: str,
        creator_org: str,
        group_type: str = 'community',
        is_public: bool = False,
        requires_approval: bool = True,
        default_trust_level_name: str = 'medium',
        group_policies: Dict = None,
        created_by: str = None,
        **kwargs
    ) -> TrustGroup:
        """
        Create a new trust group.
        
        Args:
            name: Name of the trust group
            description: Description of the group's purpose
            creator_org: UUID of the organization creating the group
            group_type: Type of trust group
            is_public: Whether the group is publicly visible
            requires_approval: Whether membership requires approval
            default_trust_level_name: Default trust level for group members
            group_policies: Group-specific policies
            
        Returns:
            TrustGroup: The created trust group
        """
        try:
            with transaction.atomic():
                # Get default trust level
                try:
                    default_trust_level = TrustLevel.objects.get(
                        name=default_trust_level_name,
                        is_active=True
                    )
                except TrustLevel.DoesNotExist:
                    raise ValidationError(f"Trust level '{default_trust_level_name}' not found or inactive")
                
                # Create the trust group
                trust_group = TrustGroup.objects.create(
                    name=name,
                    description=description,
                    group_type=group_type,
                    is_public=is_public,
                    requires_approval=requires_approval,
                    default_trust_level=default_trust_level,
                    group_policies=group_policies or {},
                    created_by=created_by or creator_org,
                    administrators=[creator_org],
                    **kwargs
                )
                
                # Add creator as administrator member
                TrustGroupMembership.objects.create(
                    trust_group=trust_group,
                    organization=creator_org,
                    membership_type='administrator',
                    is_active=True
                )
                
                # Log the creation
                TrustLog.log_trust_event(
                    action='group_created',
                    source_organization=creator_org,
                    trust_group=trust_group,
                    user=created_by or 'system',
                    details={
                        'group_name': name,
                        'group_type': group_type,
                        'is_public': is_public
                    }
                )
                
                logger.info(f"Trust group created: {name} by {creator_org}")
                return trust_group
                
        except Exception as e:
            logger.error(f"Failed to create trust group: {str(e)}")
            raise

    @staticmethod
    def join_trust_group(
        group_id: str,
        organization: str,
        membership_type: str = 'member',
        invited_by: str = None,
        user: str = None
    ) -> TrustGroupMembership:
        """
        Add an organization to a trust group.
        
        Args:
            group_id: UUID of the trust group
            organization: UUID of the organization joining
            membership_type: Type of membership
            invited_by: Organization that invited this member
            user: User performing the action
            
        Returns:
            TrustGroupMembership: The created membership
        """
        try:
            with transaction.atomic():
                trust_group = TrustGroup.objects.select_for_update().get(
                    id=group_id,
                    is_active=True
                )
                
                # Check if organization is already a member
                existing_membership = TrustGroupMembership.objects.filter(
                    trust_group=trust_group,
                    organization=organization,
                    is_active=True
                ).first()
                
                if existing_membership:
                    raise ValidationError("Organization is already a member of this group")
                
                # Create membership
                membership = TrustGroupMembership.objects.create(
                    trust_group=trust_group,
                    organization=organization,
                    membership_type=membership_type,
                    invited_by=invited_by,
                    is_active=True
                )
                
                # Log the join
                TrustLog.log_trust_event(
                    action='group_joined',
                    source_organization=organization,
                    trust_group=trust_group,
                    user=user or 'system',
                    details={
                        'membership_type': membership_type,
                        'invited_by': invited_by
                    }
                )
                
                logger.info(f"Organization {organization} joined trust group {trust_group.name}")
                return membership
                
        except TrustGroup.DoesNotExist:
            raise ValidationError("Trust group not found")
        except Exception as e:
            logger.error(f"Failed to join trust group: {str(e)}")
            raise

    @staticmethod
    def leave_trust_group(
        group_id: str,
        organization: str,
        user: str = None,
        reason: str = None
    ) -> bool:
        """
        Remove an organization from a trust group.
        
        Args:
            group_id: UUID of the trust group
            organization: UUID of the organization leaving
            user: User performing the action
            reason: Optional reason for leaving
            
        Returns:
            bool: True if successful
        """
        try:
            with transaction.atomic():
                membership = TrustGroupMembership.objects.select_for_update().get(
                    trust_group_id=group_id,
                    organization=organization,
                    is_active=True
                )
                
                # Deactivate membership
                membership.is_active = False
                membership.left_at = timezone.now()
                membership.save()
                
                # If this was an administrator, update group administrators list
                trust_group = membership.trust_group
                if membership.membership_type == 'administrator':
                    administrators = trust_group.administrators.copy()
                    if organization in administrators:
                        administrators.remove(organization)
                        trust_group.administrators = administrators
                        trust_group.save()
                
                # Log the departure
                TrustLog.log_trust_event(
                    action='group_left',
                    source_organization=organization,
                    trust_group=trust_group,
                    user=user or 'system',
                    details={'reason': reason or 'No reason provided'}
                )
                
                logger.info(f"Organization {organization} left trust group {trust_group.name}")
                return True
                
        except TrustGroupMembership.DoesNotExist:
            raise ValidationError("Membership not found")
        except Exception as e:
            logger.error(f"Failed to leave trust group: {str(e)}")
            raise

    @staticmethod
    def get_trust_groups_for_organization(
        organization: str,
        include_inactive: bool = False
    ) -> List[TrustGroup]:
        """
        Get all trust groups that an organization is a member of.
        
        Args:
            organization: UUID of the organization
            include_inactive: Whether to include inactive memberships
            
        Returns:
            List of TrustGroup objects
        """
        memberships_filter = Q(organization=organization)
        if not include_inactive:
            memberships_filter &= Q(is_active=True)
        
        group_ids = TrustGroupMembership.objects.filter(
            memberships_filter
        ).values_list('trust_group_id', flat=True)
        
        groups_filter = Q(id__in=group_ids)
        if not include_inactive:
            groups_filter &= Q(is_active=True)
        
        return TrustGroup.objects.filter(groups_filter).order_by('name')

    @staticmethod
    def get_public_trust_groups() -> List[TrustGroup]:
        """
        Get all public trust groups that organizations can request to join.
        
        Returns:
            List of public TrustGroup objects
        """
        return TrustGroup.objects.filter(
            is_public=True,
            is_active=True
        ).order_by('name')

    @staticmethod
    def can_administer_group(
        group_id: str,
        organization: str
    ) -> bool:
        """
        Check if an organization can administer a trust group.
        
        Args:
            group_id: UUID of the trust group
            organization: UUID of the organization
            
        Returns:
            bool: True if organization can administer the group
        """
        try:
            trust_group = TrustGroup.objects.get(id=group_id, is_active=True)
            return trust_group.can_administer(organization)
        except TrustGroup.DoesNotExist:
            return False

    @staticmethod
    def update_group_policies(
        group_id: str,
        updating_org: str,
        new_policies: Dict,
        user: str = None
    ) -> bool:
        """
        Update trust group policies.
        
        Args:
            group_id: UUID of the trust group
            updating_org: UUID of the organization updating policies
            new_policies: New group policies
            user: User performing the update
            
        Returns:
            bool: True if successful
        """
        try:
            with transaction.atomic():
                trust_group = TrustGroup.objects.select_for_update().get(
                    id=group_id,
                    is_active=True
                )
                
                # Check if organization can administer the group
                if not trust_group.can_administer(updating_org):
                    raise ValidationError("Organization cannot administer this group")
                
                old_policies = trust_group.group_policies.copy()
                trust_group.group_policies = new_policies
                trust_group.save()
                
                # Log the update
                TrustLog.log_trust_event(
                    action='group_modified',
                    source_organization=updating_org,
                    trust_group=trust_group,
                    user=user or 'system',
                    details={
                        'action': 'policies_updated',
                        'old_policies': old_policies,
                        'new_policies': new_policies
                    }
                )
                
                logger.info(f"Trust group policies updated for {trust_group.name} by {updating_org}")
                return True
                
        except TrustGroup.DoesNotExist:
            raise ValidationError("Trust group not found")
        except Exception as e:
            logger.error(f"Failed to update group policies: {str(e)}")
            raise

    @staticmethod
    def get_group_members(
        group_id: str,
        include_inactive: bool = False
    ) -> List[TrustGroupMembership]:
        """
        Get all members of a trust group.
        
        Args:
            group_id: UUID of the trust group
            include_inactive: Whether to include inactive members
            
        Returns:
            List of TrustGroupMembership objects
        """
        queryset = TrustGroupMembership.objects.filter(trust_group_id=group_id)
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('membership_type', 'joined_at')

    @staticmethod
    def promote_member(
        group_id: str,
        organization: str,
        promoting_org: str,
        new_membership_type: str,
        user: str = None
    ) -> bool:
        """
        Promote a group member to a different membership type.
        
        Args:
            group_id: UUID of the trust group
            organization: UUID of the organization to promote
            promoting_org: UUID of the organization doing the promotion
            new_membership_type: New membership type
            user: User performing the action
            
        Returns:
            bool: True if successful
        """
        try:
            with transaction.atomic():
                trust_group = TrustGroup.objects.get(id=group_id, is_active=True)
                
                # Check if promoting organization can administer the group
                if not trust_group.can_administer(promoting_org):
                    raise ValidationError("Organization cannot administer this group")
                
                # Get the membership to promote
                membership = TrustGroupMembership.objects.select_for_update().get(
                    trust_group=trust_group,
                    organization=organization,
                    is_active=True
                )
                
                old_type = membership.membership_type
                membership.membership_type = new_membership_type
                membership.save()
                
                # Update administrators list if promoting to/from administrator
                if new_membership_type == 'administrator' and organization not in trust_group.administrators:
                    administrators = trust_group.administrators.copy()
                    administrators.append(organization)
                    trust_group.administrators = administrators
                    trust_group.save()
                elif old_type == 'administrator' and new_membership_type != 'administrator':
                    administrators = trust_group.administrators.copy()
                    if organization in administrators:
                        administrators.remove(organization)
                        trust_group.administrators = administrators
                        trust_group.save()
                
                # Log the promotion
                TrustLog.log_trust_event(
                    action='group_modified',
                    source_organization=promoting_org,
                    target_organization=organization,
                    trust_group=trust_group,
                    user=user or 'system',
                    details={
                        'action': 'member_promoted',
                        'old_type': old_type,
                        'new_type': new_membership_type
                    }
                )
                
                logger.info(f"Member {organization} promoted from {old_type} to {new_membership_type} in group {trust_group.name}")
                return True
                
        except (TrustGroup.DoesNotExist, TrustGroupMembership.DoesNotExist):
            raise ValidationError("Group or membership not found")
        except Exception as e:
            logger.error(f"Failed to promote member: {str(e)}")
            raise

    @staticmethod
    def get_shared_intelligence_count(group_id: str) -> Dict[str, int]:
        """
        Get statistics about intelligence shared within a trust group.
        
        Args:
            group_id: UUID of the trust group
            
        Returns:
            Dictionary with sharing statistics
        """
        try:
            trust_group = TrustGroup.objects.get(id=group_id, is_active=True)
            
            # Get all active members
            member_orgs = list(TrustGroupMembership.objects.filter(
                trust_group=trust_group,
                is_active=True
            ).values_list('organization', flat=True))
            
            # This would integrate with the threat intelligence module
            # For now, return placeholder statistics
            return {
                'member_count': len(member_orgs),
                'intelligence_objects_shared': 0,  # Would query threat intel DB
                'indicators_shared': 0,  # Would query indicators
                'ttps_shared': 0,  # Would query TTPs
                'reports_shared': 0,  # Would query reports
            }
            
        except TrustGroup.DoesNotExist:
            return {'error': 'Trust group not found'}
        except Exception as e:
            logger.error(f"Failed to get sharing statistics: {str(e)}")
            return {'error': 'Failed to retrieve statistics'}