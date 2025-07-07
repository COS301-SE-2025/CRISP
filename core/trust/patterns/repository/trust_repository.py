from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from django.db import models, transaction
from django.db.models import Q, Count, Avg
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from ...models import (
    TrustRelationship, TrustGroup, TrustGroupMembership, 
    TrustLevel, TrustLog, SharingPolicy
)

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """
    Abstract base repository implementing common repository patterns.
    Provides common CRUD operations and query patterns.
    """
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    @abstractmethod
    def get_by_id(self, entity_id: str):
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self, include_inactive: bool = False):
        """Get all entities."""
        pass
    
    @abstractmethod
    def create(self, **kwargs):
        """Create new entity."""
        pass
    
    @abstractmethod
    def update(self, entity_id: str, **kwargs):
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str):
        """Delete entity."""
        pass
    
    def exists(self, **kwargs) -> bool:
        """Check if entity exists with given criteria."""
        return self.model_class.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        """Count entities matching criteria."""
        return self.model_class.objects.filter(**kwargs).count()


class TrustRelationshipRepository(BaseRepository):
    """
    Repository for TrustRelationship entities.
    Implements the Repository pattern from CRISP domain model.
    """
    
    def __init__(self):
        super().__init__(TrustRelationship)
    
    def get_by_id(self, relationship_id: str) -> Optional[TrustRelationship]:
        """
        Get trust relationship by ID.
        
        Args:
            relationship_id: UUID of the trust relationship
            
        Returns:
            TrustRelationship or None if not found
        """
        try:
            return self.model_class.objects.select_related('trust_level', 'trust_group').get(
                id=relationship_id
            )
        except ObjectDoesNotExist:
            return None
    
    def get_all(self, include_inactive: bool = False) -> models.QuerySet:
        """
        Get all trust relationships.
        
        Args:
            include_inactive: Whether to include inactive relationships
            
        Returns:
            QuerySet of TrustRelationship objects
        """
        queryset = self.model_class.objects.select_related('trust_level', 'trust_group')
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-created_at')
    
    def create(self, source_org: str, target_org: str, trust_level: TrustLevel,
               created_by: str, **kwargs) -> TrustRelationship:
        """
        Create new trust relationship.
        
        Args:
            source_org: Source organization UUID
            target_org: Target organization UUID  
            trust_level: TrustLevel instance
            created_by: User creating the relationship
            **kwargs: Additional relationship properties
            
        Returns:
            Created TrustRelationship
            
        Raises:
            ValidationError: If creation fails validation
        """
        try:
            with transaction.atomic():
                # Check for existing relationship
                existing = self.get_by_organizations(source_org, target_org, active_only=True)
                if existing:
                    raise ValidationError(
                        f"Active trust relationship already exists between {source_org} and {target_org}"
                    )
                
                relationship = self.model_class.objects.create(
                    source_organization=source_org,
                    target_organization=target_org,
                    trust_level=trust_level,
                    anonymization_level=trust_level.default_anonymization_level,
                    access_level=trust_level.default_access_level,
                    created_by=created_by,
                    last_modified_by=created_by,
                    **kwargs
                )
                
                logger.info(f"Trust relationship created: {relationship.id}")
                return relationship
                
        except Exception as e:
            logger.error(f"Failed to create trust relationship: {str(e)}")
            raise
    
    def update(self, relationship_id: str, updated_by: str, **kwargs) -> Optional[TrustRelationship]:
        """
        Update trust relationship.
        
        Args:
            relationship_id: UUID of relationship to update
            updated_by: User performing the update
            **kwargs: Fields to update
            
        Returns:
            Updated TrustRelationship or None if not found
        """
        try:
            with transaction.atomic():
                relationship = self.model_class.objects.select_for_update().get(
                    id=relationship_id
                )
                
                # Update fields
                for field, value in kwargs.items():
                    if hasattr(relationship, field):
                        setattr(relationship, field, value)
                
                relationship.last_modified_by = updated_by
                relationship.save()
                
                logger.info(f"Trust relationship updated: {relationship_id}")
                return relationship
                
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Failed to update trust relationship {relationship_id}: {str(e)}")
            raise
    
    def delete(self, relationship_id: str, deleted_by: str = None) -> bool:
        """
        Soft delete trust relationship (mark as inactive).
        
        Args:
            relationship_id: UUID of relationship to delete
            deleted_by: User performing the deletion
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            with transaction.atomic():
                relationship = self.model_class.objects.select_for_update().get(
                    id=relationship_id
                )
                
                relationship.is_active = False
                relationship.status = 'revoked'
                relationship.revoked_at = timezone.now()
                if deleted_by:
                    relationship.revoked_by = deleted_by
                    relationship.last_modified_by = deleted_by
                
                relationship.save()
                
                logger.info(f"Trust relationship soft deleted: {relationship_id}")
                return True
                
        except ObjectDoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Failed to delete trust relationship {relationship_id}: {str(e)}")
            raise
    
    def get_by_organizations(self, source_org: str, target_org: str, 
                           active_only: bool = True) -> Optional[TrustRelationship]:
        """
        Get trust relationship between two organizations.
        
        Args:
            source_org: Source organization UUID
            target_org: Target organization UUID
            active_only: Only return active relationships
            
        Returns:
            TrustRelationship or None if not found
        """
        queryset = self.model_class.objects.select_related('trust_level', 'trust_group').filter(
            source_organization=source_org,
            target_organization=target_org
        )
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return queryset.first()
    
    def get_for_organization(self, organization: str, include_inactive: bool = False,
                           relationship_type: str = None) -> models.QuerySet:
        """
        Get all trust relationships for an organization.
        
        Args:
            organization: Organization UUID
            include_inactive: Include inactive relationships
            relationship_type: Filter by relationship type
            
        Returns:
            QuerySet of TrustRelationship objects
        """
        queryset = self.model_class.objects.select_related('trust_level', 'trust_group').filter(
            Q(source_organization=organization) | Q(target_organization=organization)
        )
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        if relationship_type:
            queryset = queryset.filter(relationship_type=relationship_type)
        
        return queryset.order_by('-created_at')
    
    def get_by_trust_level(self, trust_level: TrustLevel, 
                          include_inactive: bool = False) -> models.QuerySet:
        """
        Get relationships by trust level.
        
        Args:
            trust_level: TrustLevel instance
            include_inactive: Include inactive relationships
            
        Returns:
            QuerySet of TrustRelationship objects
        """
        queryset = self.model_class.objects.filter(trust_level=trust_level)
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-created_at')
    
    def get_effective_relationships(self, organization: str) -> models.QuerySet:
        """
        Get all effective (active and approved) trust relationships for an organization.
        
        Args:
            organization: Organization UUID
            
        Returns:
            QuerySet of effective TrustRelationship objects
        """
        now = timezone.now()
        
        return self.model_class.objects.select_related('trust_level', 'trust_group').filter(
            Q(source_organization=organization) | Q(target_organization=organization),
            is_active=True,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            valid_from__lte=now
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gt=now)
        ).order_by('-created_at')
    
    def get_pending_approvals(self, organization: str) -> models.QuerySet:
        """
        Get relationships pending approval from an organization.
        
        Args:
            organization: Organization UUID
            
        Returns:
            QuerySet of TrustRelationship objects pending approval
        """
        return self.model_class.objects.select_related('trust_level', 'trust_group').filter(
            Q(
                Q(source_organization=organization, approved_by_source=False) |
                Q(target_organization=organization, approved_by_target=False)
            ),
            is_active=True,
            status='pending'
        ).order_by('created_at')
    
    def get_expiring_soon(self, days_ahead: int = 30) -> models.QuerySet:
        """
        Get relationships expiring within specified days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            QuerySet of TrustRelationship objects expiring soon
        """
        expiry_threshold = timezone.now() + timedelta(days=days_ahead)
        
        return self.model_class.objects.select_related('trust_level', 'trust_group').filter(
            is_active=True,
            status='active',
            valid_until__isnull=False,
            valid_until__lte=expiry_threshold,
            valid_until__gt=timezone.now()
        ).order_by('valid_until')
    
    def get_relationships_by_trust_score(self, min_score: int = 0, 
                                       max_score: int = 100) -> models.QuerySet:
        """
        Get relationships by trust score range.
        
        Args:
            min_score: Minimum trust score
            max_score: Maximum trust score
            
        Returns:
            QuerySet of TrustRelationship objects
        """
        return self.model_class.objects.select_related('trust_level', 'trust_group').filter(
            trust_level__numerical_value__gte=min_score,
            trust_level__numerical_value__lte=max_score,
            is_active=True
        ).order_by('-trust_level__numerical_value')
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get trust relationship statistics.
        
        Returns:
            Dictionary with relationship statistics
        """
        total = self.model_class.objects.count()
        active = self.model_class.objects.filter(is_active=True).count()
        pending = self.model_class.objects.filter(status='pending').count()
        
        # Trust level distribution
        trust_level_stats = self.model_class.objects.filter(is_active=True).values(
            'trust_level__level'
        ).annotate(count=Count('id')).order_by('trust_level__level')
        
        # Relationship type distribution
        type_stats = self.model_class.objects.filter(is_active=True).values(
            'relationship_type'
        ).annotate(count=Count('id')).order_by('relationship_type')
        
        # Average trust score
        avg_trust_score = self.model_class.objects.filter(is_active=True).aggregate(
            avg_score=Avg('trust_level__numerical_value')
        )['avg_score'] or 0
        
        return {
            'total_relationships': total,
            'active_relationships': active,
            'pending_relationships': pending,
            'inactive_relationships': total - active,
            'trust_level_distribution': list(trust_level_stats),
            'relationship_type_distribution': list(type_stats),
            'average_trust_score': round(avg_trust_score, 2)
        }


class TrustGroupRepository:
    """Repository for trust group operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_class = TrustGroup  # Add this line
    
    def can_administer(self, group_id: str, user_id: str) -> bool:
        """Check if user can administer the trust group."""
        try:
            from ...models import TrustGroupMembership  # Fix import path
            
            # Check if user is an admin member of the group
            membership = TrustGroupMembership.objects.filter(
                trust_group_id=group_id,
                organization__users__id=user_id,
                membership_type='administrator',
                is_active=True
            ).first()
            
            return membership is not None
            
        except Exception as e:
            self.logger.error(f"Error checking administration rights: {str(e)}")
            return False
    
    def get_by_id(self, group_id: str) -> Optional[TrustGroup]:
        """Get trust group by ID."""
        try:
            return self.model_class.objects.select_related('default_trust_level').get(
                id=group_id
            )
        except ObjectDoesNotExist:
            return None
    
    def get_all(self, include_inactive: bool = False) -> models.QuerySet:
        """Get all trust groups."""
        queryset = self.model_class.objects.select_related('default_trust_level')
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('name')
    
    def create(self, name: str, description: str, creator_org: str, 
               created_by: str, **kwargs) -> TrustGroup:
        """Create new trust group."""
        try:
            with transaction.atomic():
                group = self.model_class.objects.create(
                    name=name,
                    description=description,
                    created_by=created_by,
                    administrators=[creator_org],
                    **kwargs
                )
                
                logger.info(f"Trust group created: {group.id}")
                return group
                
        except Exception as e:
            logger.error(f"Failed to create trust group: {str(e)}")
            raise
    
    def update(self, group_id: str, **kwargs) -> Optional[TrustGroup]:
        """Update trust group."""
        try:
            with transaction.atomic():
                group = self.model_class.objects.select_for_update().get(id=group_id)
                
                for field, value in kwargs.items():
                    if hasattr(group, field):
                        setattr(group, field, value)
                
                group.save()
                
                logger.info(f"Trust group updated: {group_id}")
                return group
                
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Failed to update trust group {group_id}: {str(e)}")
            raise
    
    def delete(self, group_id: str) -> bool:
        """Soft delete trust group."""
        try:
            with transaction.atomic():
                group = self.model_class.objects.select_for_update().get(id=group_id)
                group.is_active = False
                group.save()
                
                logger.info(f"Trust group soft deleted: {group_id}")
                return True
                
        except ObjectDoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Failed to delete trust group {group_id}: {str(e)}")
            raise
    
    def get_public_groups(self) -> models.QuerySet:
        """Get public trust groups."""
        return self.model_class.objects.filter(
            is_public=True,
            is_active=True
        ).order_by('name')
    
    def get_groups_for_organization(self, organization: str, 
                                  include_inactive: bool = False) -> models.QuerySet:
        """Get trust groups for an organization."""
        membership_filter = Q(organization=organization)
        if not include_inactive:
            membership_filter &= Q(is_active=True)
        
        group_ids = TrustGroupMembership.objects.filter(
            membership_filter
        ).values_list('trust_group_id', flat=True)
        
        groups_filter = Q(id__in=group_ids)
        if not include_inactive:
            groups_filter &= Q(is_active=True)
        
        return self.model_class.objects.filter(groups_filter).order_by('name')
    

class TrustLevelRepository:
    """Repository for trust level operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_class = TrustLevel  # Add this line
    
    def get_all(self, include_inactive: bool = False) -> 'QuerySet':
        """Get all trust levels."""
        try:
            queryset = self.model_class.objects.all()
            
            if not include_inactive:
                queryset = queryset.filter(is_active=True)
            
            # Order by numerical value
            return queryset.order_by('numerical_value')
            
        except Exception as e:
            self.logger.error(f"Error getting trust levels: {str(e)}")
            return self.model_class.objects.none()
    
    def get_by_id(self, level_id: str) -> Optional[TrustLevel]:
        """Get trust level by ID."""
        try:
            return self.model_class.objects.get(id=level_id)
        except ObjectDoesNotExist:
            return None
    
    def create(self, name: str, level: str, numerical_value: int,
               description: str, created_by: str, **kwargs) -> TrustLevel:
        """Create new trust level."""
        try:
            trust_level = self.model_class.objects.create(
                name=name,
                level=level,
                numerical_value=numerical_value,
                description=description,
                created_by=created_by,
                **kwargs
            )
            
            logger.info(f"Trust level created: {trust_level.id}")
            return trust_level
            
        except Exception as e:
            logger.error(f"Failed to create trust level: {str(e)}")
            raise
    
    def update(self, level_id: str, **kwargs) -> Optional[TrustLevel]:
        """Update trust level."""
        try:
            trust_level = self.model_class.objects.get(id=level_id)
            
            for field, value in kwargs.items():
                if hasattr(trust_level, field):
                    setattr(trust_level, field, value)
            
            trust_level.save()
            
            logger.info(f"Trust level updated: {level_id}")
            return trust_level
            
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Failed to update trust level {level_id}: {str(e)}")
            raise
    
    def delete(self, level_id: str) -> bool:
        """Soft delete trust level."""
        try:
            trust_level = self.model_class.objects.get(id=level_id)
            trust_level.is_active = False
            trust_level.save()
            
            logger.info(f"Trust level soft deleted: {level_id}")
            return True
            
        except ObjectDoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Failed to delete trust level {level_id}: {str(e)}")
            raise
    
    def get_by_name(self, name: str) -> Optional[TrustLevel]:
        """Get trust level by name."""
        try:
            return self.model_class.objects.get(name=name, is_active=True)
        except ObjectDoesNotExist:
            return None
    
    def get_default(self) -> Optional[TrustLevel]:
        """Get default trust level."""
        return self.model_class.objects.filter(
            is_system_default=True,
            is_active=True
        ).first()
    
    def get_by_score_range(self, min_score: int, max_score: int) -> models.QuerySet:
        """Get trust levels by numerical score range."""
        return self.model_class.objects.filter(
            numerical_value__gte=min_score,
            numerical_value__lte=max_score,
            is_active=True
        ).order_by('numerical_value')
    
    def get_by_minimum_value(self, min_value: int) -> models.QuerySet:
        """Get trust levels with numerical value >= min_value."""
        return self.model_class.objects.filter(
            numerical_value__gte=min_value,
            is_active=True
        ).order_by('numerical_value')


class TrustLogRepository(BaseRepository):
    """
    Repository for TrustLog entities (audit logs).
    """
    
    def __init__(self):
        super().__init__(TrustLog)
    
    def get_by_id(self, log_id: str) -> Optional[TrustLog]:
        """Get trust log by ID."""
        try:
            return self.model_class.objects.select_related(
                'trust_relationship', 'trust_group'
            ).get(id=log_id)
        except ObjectDoesNotExist:
            return None
    
    def get_all(self, include_inactive: bool = False) -> models.QuerySet:
        """Get all trust logs."""
        return self.model_class.objects.select_related(
            'trust_relationship', 'trust_group'
        ).order_by('-timestamp')
    
    def create(self, action: str, source_organization: str, user: str, **kwargs) -> TrustLog:
        """Create new trust log entry."""
        try:
            log_entry = self.model_class.objects.create(
                action=action,
                source_organization=source_organization,
                user=user,
                **kwargs
            )
            
            return log_entry
            
        except Exception as e:
            logger.error(f"Failed to create trust log: {str(e)}")
            raise
    
    def update(self, log_id: str, **kwargs):
        """Trust logs are immutable - no updates allowed."""
        raise NotImplementedError("Trust logs are immutable and cannot be updated")
    
    def delete(self, log_id: str) -> bool:
        """Trust logs are immutable - no deletion allowed."""
        raise NotImplementedError("Trust logs are immutable and cannot be deleted")
    
    def get_for_organization(self, organization: str, 
                           start_date: datetime = None,
                           end_date: datetime = None) -> models.QuerySet:
        """Get logs for an organization within date range."""
        queryset = self.model_class.objects.filter(
            Q(source_organization=organization) | Q(target_organization=organization)
        ).order_by('-timestamp')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset
    
    def get_by_organization(self, organization: str, 
                           start_date: datetime = None,
                           end_date: datetime = None) -> models.QuerySet:
        """Alias for get_for_organization."""
        return self.get_for_organization(organization, start_date, end_date)
    
    def get_by_action(self, action: str, 
                     start_date: datetime = None,
                     end_date: datetime = None) -> models.QuerySet:
        """Get logs by action type within date range."""
        queryset = self.model_class.objects.filter(action=action).order_by('-timestamp')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset
    
    def get_failed_actions(self, start_date: datetime = None,
                          end_date: datetime = None) -> models.QuerySet:
        """Get failed trust actions within date range."""
        queryset = self.model_class.objects.filter(success=False).order_by('-timestamp')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset


# Repository manager for unified access
class TrustRepositoryManager:
    """
    Manager class providing unified access to all trust repositories.
    Implements the Repository pattern facade.
    """
    
    def __init__(self):
        self.relationships = TrustRelationshipRepository()
        self.groups = TrustGroupRepository()
        self.levels = TrustLevelRepository()
        self.logs = TrustLogRepository()
    
    def get_repository(self, entity_type: str):
        """Get repository for specific entity type."""
        repositories = {
            'relationship': self.relationships,
            'group': self.groups,
            'level': self.levels,
            'log': self.logs
        }
        
        if entity_type not in repositories:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        return repositories[entity_type]
    
    def create_with_logging(self, entity_type: str, user: str, **kwargs):
        """Create entity with automatic logging."""
        repository = self.get_repository(entity_type)
        
        try:
            entity = repository.create(**kwargs)
            
            # Log the creation
            action_mapping = {
                'relationship': 'relationship_created',
                'group': 'group_created',
                'level': 'trust_level_created'
            }
            
            if entity_type in action_mapping:
                self.logs.create(
                    action=action_mapping[entity_type],
                    source_organization=kwargs.get('source_organization', ''),
                    user=user,
                    success=True,
                    details={'entity_id': str(entity.id)}
                )
            
            return entity
            
        except Exception as e:
            # Log the failure
            if entity_type in action_mapping:
                self.logs.create(
                    action=action_mapping[entity_type],
                    source_organization=kwargs.get('source_organization', ''),
                    user=user,
                    success=False,
                    failure_reason=str(e)
                )
            
            raise


# Singleton instance for global use
trust_repository_manager = TrustRepositoryManager()