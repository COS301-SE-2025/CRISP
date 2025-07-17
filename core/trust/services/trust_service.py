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
        requesting_user=None,
        relationship_data: Dict = None,
        source_org: str = None,
        target_org: str = None,
        trust_level_name: str = None,
        relationship_type: str = 'bilateral',
        created_by: str = None,
        sharing_preferences: Dict = None,
        valid_until: timezone.datetime = None,
        notes: str = None,
        export_to_stix: bool = True,
        **kwargs
    ):
        """
        Create a new trust relationship between two organizations.
        
        Support for multiple calling patterns:
        1. create_trust_relationship(requesting_user, relationship_data) - instance method for tests
        2. create_trust_relationship(source_org, target_org, trust_level_name, ...) - static method pattern
        
        Returns:
            TrustRelationship or Dict: The created trust relationship (or dict for test compatibility)
            
        Raises:
            ValidationError: If the relationship cannot be created
        """
        # Handle test pattern: create_trust_relationship(requesting_user, relationship_data)
        if requesting_user and relationship_data:
            try:
                # Validate required fields
                required_fields = ["source_organization", "target_organization", "trust_level"]
                for field in required_fields:
                    if field not in relationship_data:
                        return {"success": False, "message": f"Missing required field: {field}"}
                
                # Check permissions
                if requesting_user.role not in ["BlueVisionAdmin"] and str(requesting_user.organization.id) != str(relationship_data["source_organization"]):
                    return {"success": False, "message": "Insufficient permissions to create trust relationship for this organization"}
                
                # Check for same organization
                if str(relationship_data["source_organization"]) == str(relationship_data["target_organization"]):
                    return {"success": False, "message": "Cannot create trust relationship with same organization"}
                
                # Get the trust level object
                from core.trust.models import TrustLevel
                try:
                    trust_level = TrustLevel.objects.get(id=relationship_data["trust_level"])
                    trust_level_name = trust_level.name
                except TrustLevel.DoesNotExist:
                    return {"success": False, "message": "Invalid trust level"}
                
                # Extract parameters from relationship_data
                source_org = relationship_data["source_organization"]
                target_org = relationship_data["target_organization"]
                
                # Convert UUID strings to Organization objects if needed
                from core.user_management.models import Organization
                import uuid
                
                # Handle UUID objects or strings
                if isinstance(source_org, (str, uuid.UUID)):
                    source_org = Organization.objects.get(id=source_org)
                if isinstance(target_org, (str, uuid.UUID)):
                    target_org = Organization.objects.get(id=target_org)
                
                relationship_type = relationship_data.get("relationship_type", "bilateral")
                created_by = requesting_user
                sharing_preferences = relationship_data.get("sharing_preferences")
                valid_until = relationship_data.get("valid_until")
                notes = relationship_data.get("notes", relationship_data.get("description", ""))
                export_to_stix = relationship_data.get("export_to_stix", True)
                
            except Exception as e:
                return {"success": False, "message": f"Error processing relationship data: {str(e)}"}
        
        # Handle static method pattern: create_trust_relationship(source_org, target_org, trust_level_name, ...)
        elif source_org is not None and target_org is not None and trust_level_name is not None:
            # Convert string UUIDs to Organization objects if needed
            from core.user_management.models import Organization
            import uuid
            
            if isinstance(source_org, (str, uuid.UUID)):
                try:
                    source_org = Organization.objects.get(id=source_org)
                except Organization.DoesNotExist:
                    if requesting_user and relationship_data:
                        return {"success": False, "message": f"Source organization {source_org} not found"}
                    else:
                        raise ValidationError(f"Source organization {source_org} not found")
            if isinstance(target_org, (str, uuid.UUID)):
                try:
                    target_org = Organization.objects.get(id=target_org)
                except Organization.DoesNotExist:
                    if requesting_user and relationship_data:
                        return {"success": False, "message": f"Target organization {target_org} not found"}
                    else:
                        raise ValidationError(f"Target organization {target_org} not found")
        else:
            if requesting_user and relationship_data is not None:
                return {"success": False, "message": "Parameter error: provide either (requesting_user, relationship_data) or (source_org, target_org, trust_level_name)"}
            else:
                raise ValidationError("Parameter error: provide either (requesting_user, relationship_data) or (source_org, target_org, trust_level_name)")
            
        if source_org == target_org:
            error_msg = "Source and target organizations cannot be the same."
            if requesting_user and relationship_data:
                return {"success": False, "message": error_msg}
            else:
                raise ValidationError(error_msg)
        try:
            with transaction.atomic():
                # Get trust level
                trust_level = trust_repository_manager.levels.get_by_name(trust_level_name)
                if not trust_level:
                    raise ValidationError(f"Trust level '{trust_level_name}' not found or inactive")
                
                # Create relationship directly (bypassing repository for now due to UUID/object mismatch)
                relationship = TrustRelationship.objects.create(
                    source_organization=source_org,
                    target_organization=target_org,
                    trust_level=trust_level,
                    created_by=created_by if hasattr(created_by, 'username') else None,
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
                
                # Return format depends on calling pattern
                if requesting_user and relationship_data:
                    return {"success": True, "relationship": relationship}
                else:
                    return relationship
                
        except IntegrityError as e:
            error_msg = "Active trust relationship already exists between these organizations" if 'duplicate key' in str(e).lower() else f"Database error: {str(e)}"
            if requesting_user and relationship_data:
                return {"success": False, "message": error_msg}
            else:
                logger.error(f"Database integrity error creating trust relationship: {str(e)}")
                raise ValidationError(error_msg)
        except ValidationError as e:
            if requesting_user and relationship_data:
                return {"success": False, "message": str(e)}
            else:
                raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if requesting_user and relationship_data is not None:
                return {"success": False, "message": error_msg}
            else:
                logger.error(f"Failed to create trust relationship: {str(e)}")
                raise ValidationError(error_msg)

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
                
                # Convert approving_org string UUID to Organization object if needed
                if isinstance(approving_org, str):
                    try:
                        from core.user_management.models import Organization
                        approving_org = Organization.objects.get(id=approving_org)
                    except Organization.DoesNotExist:
                        raise ValidationError("Approving organization not found")
                
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

    def revoke_trust_relationship(
        self,
        requesting_user,
        relationship_id: str,
        reason: str = None,
        **kwargs
    ) -> Dict[str, Any]:
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
                
                # Verify user can revoke this relationship (must be from one of the organizations)
                user_org = requesting_user.organization
                if (relationship.source_organization != user_org and 
                    relationship.target_organization != user_org):
                    raise ValidationError("User's organization is not part of this trust relationship")
                
                # Update relationship status
                relationship.status = 'revoked'
                relationship.last_modified_by = requesting_user
                relationship.save()
                
                # Log the revocation
                TrustLog.log_trust_event(
                    action='relationship_revoked',
                    source_organization=user_org,
                    target_organization=relationship.target_organization if user_org == relationship.source_organization else relationship.source_organization,
                    trust_relationship=relationship,
                    user=requesting_user,
                    details={'reason': reason or 'No reason provided'}
                )
                
                logger.info(f"Trust relationship revoked by {user_org}: {reason or 'No reason'}")
                return {'success': True, 'message': 'Trust relationship revoked successfully'}
                
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
                # Handle both User object and username string
                if hasattr(updated_by, 'username'):
                    relationship.last_modified_by = updated_by
                else:
                    # Assume it's a username string, try to get the User object
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        user_obj = User.objects.get(username=updated_by)
                        relationship.last_modified_by = user_obj
                    except User.DoesNotExist:
                        # If user not found, leave last_modified_by unchanged
                        pass
                
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
            logger.warning(f"Update failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to update trust level: {str(e)}")
            return False

    @staticmethod
    def get_available_trust_levels() -> List[TrustLevel]:
        """
        Get all available active trust levels.
        
        Returns:
            List[TrustLevel]: List of active trust levels ordered by numerical value
        """
        return TrustLevel.objects.filter(is_active=True).order_by('numerical_value')
    
    # Additional instance methods for comprehensive test compatibility
    def create_trust_group(self, requesting_user, group_data: Dict) -> Dict[str, Any]:
        """Create a new trust group"""
        try:
            # Check permissions - only BlueVisionAdmin can create trust groups
            if requesting_user.role not in ["BlueVisionAdmin"]:
                return {"success": False, "message": "Insufficient permissions to create trust groups"}
            
            group = TrustGroup.objects.create(
                name=group_data["name"],
                description=group_data.get("description", ""),
                group_type=group_data.get("group_type", "community"),
                is_public=group_data.get("is_public", False),
                requires_approval=group_data.get("requires_approval", True),
                default_trust_level_id=group_data.get("default_trust_level_id"),
                created_by=str(requesting_user)
            )
            return {"success": True, "group": group}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_trust_relationships(self, requesting_user, organization_id: str = None) -> Dict[str, Any]:
        """Get trust relationships for a users organization"""
        try:
            org_id = organization_id or str(requesting_user.organization.id)
            
            # Check access permissions
            if not self._check_organization_access(requesting_user, org_id):
                return {"success": False, "message": "Insufficient access to organization data"}
            
            # Get relationships for the organization  
            relationships = TrustRelationship.objects.filter(
                source_organization_id=org_id,
                is_active=True
            ).select_related('trust_level', 'target_organization')
            
            formatted_relationships = []
            for rel in relationships:
                formatted_relationships.append({
                    "id": str(rel.id),
                    "source_organization": str(rel.source_organization.id),
                    "target_organization": str(rel.target_organization.id), 
                    "trust_level": rel.trust_level.name,
                    "status": rel.status,
                    "created_at": rel.created_at.isoformat()
                })
            
            return {"success": True, "relationships": formatted_relationships}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_trust_metrics(self, requesting_user, organization_id: str) -> Dict[str, Any]:
        """Get trust metrics for an organization"""
        try:
            # Check access permissions
            if not self._check_organization_access(requesting_user, organization_id):
                return {"success": False, "message": "Insufficient access to organization data"}
            
            total_count = TrustRelationship.objects.filter(
                source_organization_id=organization_id
            ).count()
            
            active_count = TrustRelationship.objects.filter(
                source_organization_id=organization_id, 
                status="active"
            ).count()
            
            pending_count = TrustRelationship.objects.filter(
                source_organization_id=organization_id, 
                status="pending"
            ).count()
            
            metrics = {
                "trust_score": self._calculate_trust_score(organization_id),
                "total_relationships": total_count,
                "active_relationships": active_count,
                "pending_relationships": pending_count
            }
            return {"success": True, "metrics": metrics}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_trust_history(self, requesting_user, organization_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get trust history for an organization"""
        try:
            if not self._check_organization_access(requesting_user, organization_id):
                return {"success": False, "error": "Access denied"}
            
            logs = TrustLog.objects.filter(
                source_organization_id=organization_id
            ).order_by("-timestamp")[:limit]
            return {"success": True, "history": list(logs)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def join_trust_group(self, requesting_user, group_id: str, organization_id: str = None) -> Dict[str, Any]:
        """Join a trust group"""
        try:
            from core.user_management.models import Organization
            group = TrustGroup.objects.get(id=group_id)
            
            # Use the specified organization or the user's organization
            if organization_id:
                organization = Organization.objects.get(id=organization_id)
            else:
                organization = requesting_user.organization
                
            membership, created = TrustGroupMembership.objects.get_or_create(
                trust_group=group,
                organization=organization,
                defaults={"membership_type": "member", "is_active": True}
            )
            if not created:
                return {"success": False, "message": "Already a member of this group"}
            return {"success": True, "membership": membership}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def leave_trust_group(self, requesting_user, group_id: str, organization_id: str = None) -> Dict[str, Any]:
        """Leave a trust group"""
        try:
            from core.user_management.models import Organization
            
            # Use the specified organization or the user's organization
            if organization_id:
                organization = Organization.objects.get(id=organization_id)
            else:
                organization = requesting_user.organization
                
            membership = TrustGroupMembership.objects.get(
                trust_group_id=group_id,
                organization=organization
            )
            membership.delete()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_trust_score(self, organization_id: str) -> float:
        """Calculate trust score for an organization"""
        active_rels = TrustRelationship.objects.filter(
            source_organization_id=organization_id,
            status="active"
        ).count()
        return min(100.0, active_rels * 10.0)  # Simple scoring

    def _check_organization_access(self, user, organization_id: str) -> bool:
        """Check if user has access to organization data"""
        if user.role == "BlueVisionAdmin":
            return True
        return str(user.organization.id) == organization_id

    def _format_trust_relationship(self, relationship) -> Dict[str, Any]:
        """Format trust relationship for API response"""
        return {
            "id": str(relationship.id),
            "source_organization": str(relationship.source_organization.id),
            "target_organization": str(relationship.target_organization.id),
            "trust_level": relationship.trust_level.name,
            "status": relationship.status,
            "created_at": relationship.created_at.isoformat()
        }

    def _log_trust_action(self, user, action: str, details: Dict = None, source_org=None, target_org=None, success: bool = True):
        """Log a trust-related action"""
        TrustLog.objects.create(
            action=action,
            user=user,
            source_organization=source_org or getattr(user, 'organization', None),
            target_organization=target_org,
            success=success,
            details=details or {}
        )

    def _validate_trust_relationship_data(self, data: Dict) -> bool:
        """Validate trust relationship data"""
        required_fields = ["source_organization", "target_organization", "trust_level"]
        return all(field in data for field in required_fields)


class TrustGroupService:
    """Service for managing trust groups."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_trust_group(self, data: Dict, user) -> TrustGroup:
        """Create a new trust group."""
        try:
            # Get or create default trust level if not specified
            trust_level_id = data.get('default_trust_level_id')
            if trust_level_id:
                try:
                    trust_level = TrustLevel.objects.get(id=trust_level_id)
                except TrustLevel.DoesNotExist:
                    # Create a default trust level if the specified one doesn't exist
                    trust_level = TrustLevel.objects.filter(is_system_default=True).first()
                    if not trust_level:
                        trust_level = TrustLevel.objects.create(
                            name='Default Group Level',
                            level='public',
                            numerical_value=25,
                            description='Default trust level for groups',
                            is_system_default=True,
                            created_by=str(user)
                        )
            else:
                # Get or create default trust level
                trust_level = TrustLevel.objects.filter(is_system_default=True).first()
                if not trust_level:
                    trust_level = TrustLevel.objects.create(
                        name='Default Public Trust',
                        level='public',
                        numerical_value=25,
                        description='Default public trust level',
                        is_system_default=True,
                        created_by=str(user)
                    )
            
            group = TrustGroup.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                group_type=data.get('group_type', 'community'),
                default_trust_level=trust_level,
                created_by=str(user)
            )
            
            return group
            
        except Exception as e:
            self.logger.error(f"Failed to create trust group: {str(e)}")
            raise
    
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
    def get_available_trust_levels() -> List[TrustLevel]:
        """
        Get all available active trust levels.
        
        Returns:
            List[TrustLevel]: List of active trust levels ordered by numerical value
        """
        return TrustLevel.objects.filter(is_active=True).order_by('numerical_value')
    # Additional instance methods for comprehensive test compatibility
    
    def get_trust_relationships(self, requesting_user, organization_id: str = None) -> Dict[str, Any]:
        """Get trust relationships for a users organization"""
        try:
            org_id = organization_id or str(requesting_user.organization.id)
            
            # Check access permissions
            if not self._check_organization_access(requesting_user, org_id):
                return {"success": False, "message": "Insufficient access to organization data"}
            
            # Get relationships for the organization  
            relationships = TrustRelationship.objects.filter(
                source_organization_id=org_id,
                is_active=True
            ).select_related('trust_level', 'target_organization')
            
            formatted_relationships = []
            for rel in relationships:
                formatted_relationships.append({
                    "id": str(rel.id),
                    "source_organization": str(rel.source_organization.id),
                    "target_organization": str(rel.target_organization.id), 
                    "trust_level": rel.trust_level.name,
                    "status": rel.status,
                    "created_at": rel.created_at.isoformat()
                })
            
            return {"success": True, "relationships": formatted_relationships}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_trust_metrics(self, requesting_user, organization_id: str) -> Dict[str, Any]:
        """Get trust metrics for an organization"""
        try:
            # Check access permissions
            if not self._check_organization_access(requesting_user, organization_id):
                return {"success": False, "message": "Insufficient access to organization data"}
            
            total_count = TrustRelationship.objects.filter(
                source_organization_id=organization_id
            ).count()
            
            active_count = TrustRelationship.objects.filter(
                source_organization_id=organization_id, 
                status="active"
            ).count()
            
            pending_count = TrustRelationship.objects.filter(
                source_organization_id=organization_id, 
                status="pending"
            ).count()
            
            metrics = {
                "trust_score": self._calculate_trust_score(organization_id),
                "total_relationships": total_count,
                "active_relationships": active_count,
                "pending_relationships": pending_count
            }
            return {"success": True, "metrics": metrics}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def create_trust_group(self, requesting_user, group_data: Dict) -> Dict[str, Any]:
        """Create a new trust group"""
        try:
            # Check permissions - only BlueVisionAdmin can create trust groups
            if requesting_user.role not in ["BlueVisionAdmin"]:
                return {"success": False, "message": "Insufficient permissions to create trust groups"}
            
            group = TrustGroup.objects.create(
                name=group_data["name"],
                description=group_data.get("description", ""),
                group_type=group_data.get("group_type", "community"),
                is_public=group_data.get("is_public", False),
                requires_approval=group_data.get("requires_approval", True),
                default_trust_level_id=group_data.get("default_trust_level_id"),
                created_by=str(requesting_user)
            )
            return {"success": True, "group": group}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def join_trust_group(self, requesting_user, group_id: str, organization_id: str = None) -> Dict[str, Any]:
        """Join a trust group"""
        try:
            from core.user_management.models import Organization
            group = TrustGroup.objects.get(id=group_id)
            
            # Use the specified organization or the user's organization
            if organization_id:
                organization = Organization.objects.get(id=organization_id)
            else:
                organization = requesting_user.organization
                
            membership, created = TrustGroupMembership.objects.get_or_create(
                trust_group=group,
                organization=organization,
                defaults={"membership_type": "member", "is_active": True}
            )
            if not created:
                return {"success": False, "message": "Already a member of this group"}
            return {"success": True, "membership": membership}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def leave_trust_group(self, requesting_user, group_id: str, organization_id: str = None) -> Dict[str, Any]:
        """Leave a trust group"""
        try:
            from core.user_management.models import Organization
            
            # Use the specified organization or the user's organization
            if organization_id:
                organization = Organization.objects.get(id=organization_id)
            else:
                organization = requesting_user.organization
                
            membership = TrustGroupMembership.objects.get(
                trust_group_id=group_id,
                organization=organization
            )
            membership.delete()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_trust_history(self, requesting_user, organization_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get trust history for an organization"""
        try:
            if not self._check_organization_access(requesting_user, organization_id):
                return {"success": False, "error": "Access denied"}
            
            logs = TrustLog.objects.filter(
                source_organization_id=organization_id
            ).order_by("-timestamp")[:limit]
            return {"success": True, "history": list(logs)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_organization_access(self, user, organization_id: str) -> bool:
        """Check if user has access to organization data"""
        if user.role == "BlueVisionAdmin":
            return True
        return str(user.organization.id) == organization_id
    
    def _calculate_trust_score(self, organization_id: str) -> float:
        """Calculate trust score for an organization"""
        active_rels = TrustRelationship.objects.filter(
            source_organization_id=organization_id,
            status="active"
        ).count()
        return min(100.0, active_rels * 10.0)  # Simple scoring
    
    def _format_trust_relationship(self, relationship) -> Dict[str, Any]:
        """Format trust relationship for API response"""
        return {
            "id": str(relationship.id),
            "source_organization": str(relationship.source_organization.id),
            "target_organization": str(relationship.target_organization.id),
            "trust_level": relationship.trust_level.name,
            "status": relationship.status,
            "created_at": relationship.created_at.isoformat()
        }
    
    def _log_trust_action(self, user, action: str, details: Dict = None, source_org=None, target_org=None, success: bool = True):
        """Log a trust-related action"""
        TrustLog.objects.create(
            action=action,
            user=user,
            source_organization=source_org or getattr(user, 'organization', None),
            target_organization=target_org,
            success=success,
            details=details or {}
        )
    
    def _validate_trust_relationship_data(self, data: Dict) -> bool:
        """Validate trust relationship data"""
        required_fields = ["source_organization", "target_organization", "trust_level"]
        return all(field in data for field in required_fields)
    
    def _check_organization_access(self, user, organization_id: str) -> bool:
        """Check if user has access to organization data"""
        if user.role == "BlueVisionAdmin":
            return True
        return str(user.organization.id) == organization_id
    
    def _format_trust_relationship(self, relationship) -> Dict[str, Any]:
        """Format trust relationship for API response"""
        return {
            "id": str(relationship.id),
            "source_organization": str(relationship.source_organization.id),
            "target_organization": str(relationship.target_organization.id),
            "trust_level": relationship.trust_level.name,
            "status": relationship.status,
            "created_at": relationship.created_at.isoformat()
        }
    
    def _log_trust_action(self, user, action: str, details: Dict = None, source_org=None, target_org=None, success: bool = True):
        """Log a trust-related action"""
        TrustLog.objects.create(
            action=action,
            user=user,
            source_organization=source_org or getattr(user, 'organization', None),
            target_organization=target_org,
            success=success,
            details=details or {}
        )

