"""
Trust Factory Pattern Implementation

Simple factory for creating trust management objects according to the domain model.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from django.utils import timezone

from ...models import TrustRelationship, TrustGroup, TrustLevel, TrustLog


class TrustObjectCreator(ABC):
    """
    Abstract factory for creating trust management objects.
    Implements the Factory Method pattern from CRISP domain model.
    """
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Create a trust management object."""
        pass


class TrustRelationshipCreator(TrustObjectCreator):
    """
    Factory for creating TrustRelationship objects with proper defaults.
    """
    
    def create(self, source_org: str, target_org: str, trust_level: TrustLevel, 
               created_by: str, **kwargs) -> TrustRelationship:
        """
        Create a new trust relationship with proper defaults.
        
        Args:
            source_org: Source organization UUID
            target_org: Target organization UUID  
            trust_level: TrustLevel instance
            created_by: User creating the relationship
            **kwargs: Additional parameters
            
        Returns:
            TrustRelationship: Created trust relationship
        """
        defaults = {
            'relationship_type': kwargs.get('relationship_type', 'bilateral'),
            'status': 'pending',
            'is_bilateral': kwargs.get('is_bilateral', True),
            'is_active': True,
            'anonymization_level': trust_level.default_anonymization_level,
            'access_level': trust_level.default_access_level,
            'sharing_preferences': kwargs.get('sharing_preferences', {}),
            'valid_from': timezone.now(),
            'approved_by_source': False,
            'approved_by_target': False,
            'last_modified_by': created_by,
            'notes': kwargs.get('notes', ''),
            'metadata': kwargs.get('metadata', {})
        }
        
        # Override defaults with any provided kwargs
        for key, value in kwargs.items():
            if key in defaults:
                defaults[key] = value
        
        return TrustRelationship.objects.create(
            source_organization=source_org,
            target_organization=target_org,
            trust_level=trust_level,
            created_by=created_by,
            **defaults
        )


class TrustGroupCreator(TrustObjectCreator):
    """
    Factory for creating TrustGroup objects with proper defaults.
    """
    
    def create(self, name: str, description: str, created_by: str, **kwargs) -> TrustGroup:
        """
        Create a new trust group with proper defaults.
        
        Args:
            name: Group name
            description: Group description
            created_by: User creating the group
            **kwargs: Additional parameters
            
        Returns:
            TrustGroup: Created trust group
        """
        defaults = {
            'group_type': kwargs.get('group_type', 'community'),
            'is_public': kwargs.get('is_public', False),
            'requires_approval': kwargs.get('requires_approval', True),
            'default_trust_level': kwargs.get('default_trust_level'),
            'group_policies': kwargs.get('group_policies', {}),
            'is_active': True,
            'administrators': kwargs.get('administrators', [created_by])
        }
        
        return TrustGroup.objects.create(
            name=name,
            description=description,
            created_by=created_by,
            **defaults
        )


class TrustLogCreator(TrustObjectCreator):
    """
    Factory for creating standardized TrustLog entries.
    """
    
    def create(self, action: str, source_organization: str, user: str, **kwargs) -> TrustLog:
        """
        Create a standardized trust log entry.
        
        Args:
            action: Action performed
            source_organization: Organization performing action
            user: User performing action
            **kwargs: Additional log parameters
            
        Returns:
            TrustLog: Created log entry
        """
        defaults = {
            'target_organization': kwargs.get('target_organization'),
            'trust_relationship': kwargs.get('trust_relationship'),
            'trust_group': kwargs.get('trust_group'),
            'ip_address': kwargs.get('ip_address'),
            'user_agent': kwargs.get('user_agent'),
            'success': kwargs.get('success', True),
            'failure_reason': kwargs.get('failure_reason'),
            'details': kwargs.get('details', {}),
            'metadata': kwargs.get('metadata', {})
        }
        
        return TrustLog.objects.create(
            action=action,
            source_organization=source_organization,
            user=user,
            **defaults
        )


class TrustFactory:
    """
    Main factory class for creating trust management objects.
    Provides a unified interface for all trust object creation.
    """
    
    def __init__(self):
        self._creators = {
            'relationship': TrustRelationshipCreator(),
            'group': TrustGroupCreator(),
            'log': TrustLogCreator()
        }
    
    def create_relationship(self, source_org: str, target_org: str, 
                          trust_level: TrustLevel, created_by: str, **kwargs) -> TrustRelationship:
        """Create a trust relationship."""
        return self._creators['relationship'].create(
            source_org=source_org,
            target_org=target_org,
            trust_level=trust_level,
            created_by=created_by,
            **kwargs
        )
    
    def create_group(self, name: str, description: str, created_by: str, **kwargs) -> TrustGroup:
        """Create a trust group."""
        return self._creators['group'].create(
            name=name,
            description=description,
            created_by=created_by,
            **kwargs
        )
    
    def create_log(self, action: str, source_organization: str, user: str, **kwargs) -> TrustLog:
        """Create a trust log entry."""
        return self._creators['log'].create(
            action=action,
            source_organization=source_organization,
            user=user,
            **kwargs
        )


# Global factory instance
trust_factory = TrustFactory()