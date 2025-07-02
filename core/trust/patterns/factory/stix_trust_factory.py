from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json
from django.utils import timezone

from ...models import TrustRelationship, TrustGroup, TrustGroupMembership, TrustLevel


class StixTrustObject:
    """
    Represents a STIX object created from trust management entities.
    Product of the Factory pattern.
    """
    
    def __init__(self, stix_type: str, stix_id: str, spec_version: str = "2.1"):
        self.type = stix_type
        self.id = stix_id
        self.spec_version = spec_version
        self.created = timezone.now().isoformat()
        self.modified = self.created
        self.properties = {}
    
    def add_property(self, key: str, value: Any):
        """Add a property to the STIX object."""
        self.properties[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to STIX-compliant dictionary."""
        result = {
            "type": self.type,
            "spec_version": self.spec_version,
            "id": self.id,
            "created": self.created,
            "modified": self.modified,
        }
        result.update(self.properties)
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class StixTrustObjectCreator(ABC):
    """
    Abstract factory for creating STIX objects from trust management entities.
    Implements the Factory Method pattern from CRISP domain model.
    """
    
    @abstractmethod
    def create_stix_object(self, trust_entity: Any, **kwargs) -> StixTrustObject:
        """
        Create a STIX object from a trust management entity.
        
        Args:
            trust_entity: Trust management entity (TrustRelationship, TrustGroup, etc.)
            **kwargs: Additional parameters for object creation
            
        Returns:
            StixTrustObject: Created STIX object
        """
        pass
    
    @abstractmethod
    def get_stix_type(self) -> str:
        """Get the STIX object type this factory creates."""
        pass
    
    def _generate_stix_id(self, stix_type: str, unique_identifier: str = None) -> str:
        """Generate a STIX-compliant ID."""
        if unique_identifier:
            return f"{stix_type}--{unique_identifier}"
        else:
            return f"{stix_type}--{uuid.uuid4()}"
    
    def _format_timestamp(self, dt: datetime) -> str:
        """Format datetime to STIX timestamp format."""
        if hasattr(dt, 'isoformat'):
            return dt.isoformat()
        return timezone.now().isoformat()


class StixTrustRelationshipCreator(StixTrustObjectCreator):
    """
    Factory for creating STIX objects from TrustRelationship entities.
    Creates custom STIX extension objects for trust relationships.
    """
    
    def create_stix_object(self, trust_relationship: TrustRelationship, **kwargs) -> StixTrustObject:
        """
        Create STIX object representing a trust relationship.
        Uses custom STIX extension for trust relationships.
        """
        stix_id = self._generate_stix_id(
            self.get_stix_type(), 
            str(trust_relationship.id)
        )
        
        stix_obj = StixTrustObject(self.get_stix_type(), stix_id)
        stix_obj.created = self._format_timestamp(trust_relationship.created_at)
        stix_obj.modified = self._format_timestamp(trust_relationship.updated_at)
        
        # Core trust relationship properties
        stix_obj.add_property("name", f"Trust Relationship: {trust_relationship.source_organization} -> {trust_relationship.target_organization}")
        stix_obj.add_property("description", f"Trust relationship with {trust_relationship.trust_level.name} level trust")
        
        # Trust-specific extension properties
        trust_extension = {
            "extension-type": "property-extension",
            "source_organization": trust_relationship.source_organization,
            "target_organization": trust_relationship.target_organization,
            "trust_level": {
                "name": trust_relationship.trust_level.name,
                "level": trust_relationship.trust_level.level,
                "numerical_value": trust_relationship.trust_level.numerical_value
            },
            "relationship_type": trust_relationship.relationship_type,
            "status": trust_relationship.status,
            "is_bilateral": trust_relationship.is_bilateral,
            "is_active": trust_relationship.is_active,
            "anonymization_level": trust_relationship.anonymization_level,
            "access_level": trust_relationship.access_level,
            "valid_from": self._format_timestamp(trust_relationship.valid_from),
            "valid_until": self._format_timestamp(trust_relationship.valid_until) if trust_relationship.valid_until else None,
            "approved_by_source": trust_relationship.approved_by_source,
            "approved_by_target": trust_relationship.approved_by_target,
            "sharing_preferences": trust_relationship.sharing_preferences,
            "metadata": trust_relationship.metadata
        }
        
        # Add trust group information if applicable
        if trust_relationship.trust_group:
            trust_extension["trust_group"] = {
                "id": str(trust_relationship.trust_group.id),
                "name": trust_relationship.trust_group.name,
                "type": trust_relationship.trust_group.group_type
            }
        
        stix_obj.add_property("x_crisp_trust_relationship", trust_extension)
        
        # Add labels for categorization
        labels = [
            "trust-relationship", 
            trust_relationship.relationship_type,
            trust_relationship.trust_level.level,
            trust_relationship.status
        ]
        stix_obj.add_property("labels", labels)
        
        # Add external references if needed
        external_refs = []
        if kwargs.get('include_source_reference', False):
            external_refs.append({
                "source_name": "CRISP Trust Management",
                "description": f"Trust relationship {trust_relationship.id}",
                "url": f"urn:crisp:trust:relationship:{trust_relationship.id}"
            })
        
        if external_refs:
            stix_obj.add_property("external_references", external_refs)
        
        return stix_obj
    
    def get_stix_type(self) -> str:
        return "x-crisp-trust-relationship"


class StixTrustGroupCreator(StixTrustObjectCreator):
    """
    Factory for creating STIX objects from TrustGroup entities.
    Creates STIX grouping objects for trust groups.
    """
    
    def create_stix_object(self, trust_group: TrustGroup, **kwargs) -> StixTrustObject:
        """
        Create STIX grouping object representing a trust group.
        """
        stix_id = self._generate_stix_id(
            self.get_stix_type(),
            str(trust_group.id)
        )
        
        stix_obj = StixTrustObject(self.get_stix_type(), stix_id)
        stix_obj.created = self._format_timestamp(trust_group.created_at)
        stix_obj.modified = self._format_timestamp(trust_group.updated_at)
        
        # Core grouping properties
        stix_obj.add_property("name", trust_group.name)
        stix_obj.add_property("description", trust_group.description)
        stix_obj.add_property("context", "trust-community")
        
        # Get member organizations
        members = []
        if kwargs.get('include_members', True):
            memberships = TrustGroupMembership.objects.filter(
                trust_group=trust_group,
                is_active=True
            )
            for membership in memberships:
                members.append({
                    "organization": membership.organization,
                    "membership_type": membership.membership_type,
                    "joined_at": self._format_timestamp(membership.joined_at)
                })
        
        # Trust group extension properties
        trust_group_extension = {
            "extension-type": "property-extension",
            "group_type": trust_group.group_type,
            "is_public": trust_group.is_public,
            "requires_approval": trust_group.requires_approval,
            "is_active": trust_group.is_active,
            "administrators": trust_group.administrators,
            "member_count": len(members),
            "members": members if kwargs.get('include_member_details', False) else [],
            "group_policies": trust_group.group_policies,
            "created_by": trust_group.created_by
        }
        
        # Add default trust level information
        if trust_group.default_trust_level:
            trust_group_extension["default_trust_level"] = {
                "name": trust_group.default_trust_level.name,
                "level": trust_group.default_trust_level.level,
                "numerical_value": trust_group.default_trust_level.numerical_value,
                "anonymization_level": trust_group.default_trust_level.default_anonymization_level,
                "access_level": trust_group.default_trust_level.default_access_level
            }
        
        stix_obj.add_property("x_crisp_trust_group", trust_group_extension)
        
        # Add object references to member relationships
        object_refs = []
        if kwargs.get('include_relationship_refs', False):
            # This would reference trust relationships between members
            # Implementation would depend on how relationships are structured
            pass
        
        if object_refs:
            stix_obj.add_property("object_refs", object_refs)
        
        # Add labels
        labels = [
            "trust-group",
            trust_group.group_type,
            "community" if trust_group.is_public else "private"
        ]
        stix_obj.add_property("labels", labels)
        
        return stix_obj
    
    def get_stix_type(self) -> str:
        return "grouping"


class StixTrustLevelCreator(StixTrustObjectCreator):
    """
    Factory for creating STIX objects from TrustLevel entities.
    Creates custom STIX extension objects for trust levels.
    """
    
    def create_stix_object(self, trust_level: TrustLevel, **kwargs) -> StixTrustObject:
        """
        Create STIX object representing a trust level configuration.
        """
        stix_id = self._generate_stix_id(
            self.get_stix_type(),
            str(trust_level.id)
        )
        
        stix_obj = StixTrustObject(self.get_stix_type(), stix_id)
        stix_obj.created = self._format_timestamp(trust_level.created_at)
        stix_obj.modified = self._format_timestamp(trust_level.updated_at)
        
        # Core properties
        stix_obj.add_property("name", trust_level.name)
        stix_obj.add_property("description", trust_level.description)
        
        # Trust level extension properties
        trust_level_extension = {
            "extension-type": "property-extension",
            "level": trust_level.level,
            "numerical_value": trust_level.numerical_value,
            "default_anonymization_level": trust_level.default_anonymization_level,
            "default_access_level": trust_level.default_access_level,
            "sharing_policies": trust_level.sharing_policies,
            "is_active": trust_level.is_active,
            "is_system_default": trust_level.is_system_default,
            "created_by": trust_level.created_by
        }
        
        stix_obj.add_property("x_crisp_trust_level", trust_level_extension)
        
        # Add labels
        labels = [
            "trust-level",
            trust_level.level,
            "system-default" if trust_level.is_system_default else "custom",
            "active" if trust_level.is_active else "inactive"
        ]
        stix_obj.add_property("labels", labels)
        
        return stix_obj
    
    def get_stix_type(self) -> str:
        return "x-crisp-trust-level"


class StixTrustBundleCreator(StixTrustObjectCreator):
    """
    Factory for creating STIX bundle objects containing multiple trust entities.
    """
    
    def create_stix_object(self, trust_entities: List[Any], **kwargs) -> StixTrustObject:
        """
        Create STIX bundle containing multiple trust management objects.
        
        Args:
            trust_entities: List of trust management entities
            **kwargs: Additional parameters
            
        Returns:
            StixTrustObject: STIX bundle containing all objects
        """
        stix_id = self._generate_stix_id(self.get_stix_type())
        
        stix_obj = StixTrustObject(self.get_stix_type(), stix_id)
        
        objects = []
        factories = {
            TrustRelationship: StixTrustRelationshipCreator(),
            TrustGroup: StixTrustGroupCreator(),
            TrustLevel: StixTrustLevelCreator()
        }
        
        # Create STIX objects for each entity
        for entity in trust_entities:
            entity_type = type(entity)
            if entity_type in factories:
                factory = factories[entity_type]
                stix_entity = factory.create_stix_object(entity, **kwargs)
                objects.append(stix_entity.to_dict())
        
        stix_obj.add_property("objects", objects)
        
        # Add bundle metadata
        bundle_metadata = {
            "created": stix_obj.created,
            "entity_count": len(objects),
            "entity_types": list(set(obj["type"] for obj in objects)),
            "created_by": kwargs.get("created_by", "CRISP Trust Management System")
        }
        
        stix_obj.add_property("x_crisp_bundle_metadata", bundle_metadata)
        
        return stix_obj
    
    def get_stix_type(self) -> str:
        return "bundle"


class StixTrustFactory:
    """
    Main factory class for creating STIX objects from trust management entities.
    Provides a unified interface for all trust-related STIX object creation.
    """
    
    def __init__(self):
        self._creators = {
            TrustRelationship: StixTrustRelationshipCreator(),
            TrustGroup: StixTrustGroupCreator(),
            TrustLevel: StixTrustLevelCreator()
        }
        self._bundle_creator = StixTrustBundleCreator()
    
    def create_stix_object(self, trust_entity: Any, **kwargs) -> StixTrustObject:
        """
        Create STIX object from trust management entity using appropriate factory.
        
        Args:
            trust_entity: Trust management entity
            **kwargs: Additional parameters for object creation
            
        Returns:
            StixTrustObject: Created STIX object
            
        Raises:
            ValueError: If entity type is not supported
        """
        entity_type = type(trust_entity)
        if entity_type not in self._creators:
            raise ValueError(f"Unsupported trust entity type: {entity_type}")
        
        creator = self._creators[entity_type]
        return creator.create_stix_object(trust_entity, **kwargs)
    
    def create_bundle(self, trust_entities: List[Any], **kwargs) -> StixTrustObject:
        """
        Create STIX bundle containing multiple trust entities.
        
        Args:
            trust_entities: List of trust management entities
            **kwargs: Additional parameters for bundle creation
            
        Returns:
            StixTrustObject: STIX bundle object
        """
        return self._bundle_creator.create_stix_object(trust_entities, **kwargs)
    
    def get_supported_types(self) -> List[type]:
        """Get list of supported trust entity types."""
        return list(self._creators.keys())
    
    def register_creator(self, entity_type: type, creator: StixTrustObjectCreator):
        """Register a custom creator for a trust entity type."""
        self._creators[entity_type] = creator
    
    def create_from_query(self, queryset, **kwargs) -> StixTrustObject:
        """
        Create STIX bundle from Django queryset.
        
        Args:
            queryset: Django queryset of trust entities
            **kwargs: Additional parameters
            
        Returns:
            StixTrustObject: STIX bundle containing all queried entities
        """
        entities = list(queryset)
        return self.create_bundle(entities, **kwargs)


# Singleton instance for global use
stix_trust_factory = StixTrustFactory()