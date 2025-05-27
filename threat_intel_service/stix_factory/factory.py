import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
import stix2
from django.conf import settings
from django.utils import timezone

class STIXObjectFactory(ABC):
    """
    Abstract Factory for creating STIX 2.1 objects.
    This is the base class for the Factory Method pattern (SRS 7.3.1).
    """
    @abstractmethod
    def create_object(self, data: Dict[str, Any]) -> stix2.v21.base._STIXBase:
        """
        Create a STIX object from provided data.
        """
        pass
    
    def _prepare_common_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare common fields for all STIX objects.
        """
        # Use existing ID if provided, otherwise generate a new one
        if 'id' not in data:
            object_type = data.get('type', 'unknown')
            data['id'] = f"{object_type}--{str(uuid.uuid4())}"
        
        # Set created/modified if not provided
        current_time = stix2.utils.format_datetime(timezone.now())
        if 'created' not in data:
            data['created'] = current_time
        if 'modified' not in data:
            data['modified'] = current_time
            
        # Set spec_version if not provided
        if 'spec_version' not in data:
            data['spec_version'] = '2.1'
            
        # Set created_by_ref if not provided but default identity is configured
        if 'created_by_ref' not in data and hasattr(settings, 'STIX_SETTINGS'):
            # Use the organization's identity as creator if configured
            default_identity = settings.STIX_SETTINGS.get('DEFAULT_IDENTITY', {})
            if default_identity:
                identity_id = default_identity.get('id')
                if identity_id:
                    data['created_by_ref'] = identity_id
                    
        return data


class IndicatorFactory(STIXObjectFactory):
    """
    Factory for creating STIX Indicator objects.
    """
    def create_object(self, data: Dict[str, Any]) -> stix2.v21.Indicator:
        """
        Create a STIX Indicator from provided data.
        
        Required fields:
        - pattern: A STIX pattern
        - pattern_type: Type of pattern (e.g., 'stix')
        - valid_from: Start of validity time
        
        Optional fields:
        - name: Name of the indicator
        - description: Description of the indicator
        - indicator_types: List of indicator types
        - pattern_version: Version of the pattern syntax
        - valid_until: End of validity time
        - kill_chain_phases: List of kill chain phases
        - confidence: Level of confidence (0-100)
        """
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'indicator'
        
        # Ensure required fields are present
        if 'pattern' not in data:
            raise ValueError("Indicator requires a 'pattern' field")
        if 'pattern_type' not in data:
            data['pattern_type'] = 'stix'  # Default to STIX pattern
        if 'valid_from' not in data:
            data['valid_from'] = stix2.utils.format_datetime(timezone.now())
            
        # Create the Indicator object
        return stix2.v21.Indicator(**data)


class MalwareFactory(STIXObjectFactory):
    """
    Factory for creating STIX Malware objects.
    """
    def create_object(self, data: Dict[str, Any]) -> stix2.v21.Malware:
        """
        Create a STIX Malware from provided data.
        
        Required fields:
        - is_family: Whether this is a malware family
        
        Optional fields:
        - name: Name of the malware
        - description: Description of the malware
        - malware_types: List of malware types
        - kill_chain_phases: List of kill chain phases
        - first_seen: Time the malware was first seen
        - last_seen: Time the malware was last seen
        - operating_system_refs: List of operating systems the malware targets
        - architecture_execution_envs: List of architecture execution environments
        - implementation_languages: List of implementation languages
        - capabilities: List of capabilities
        - sample_refs: List of samples of the malware
        """
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'malware'
        
        # Ensure required fields are present
        if 'is_family' not in data:
            data['is_family'] = False  # Default to single malware instance
            
        # Create the Malware object
        return stix2.v21.Malware(**data)


class AttackPatternFactory(STIXObjectFactory):
    """
    Factory for creating STIX Attack Pattern objects.
    """
    def create_object(self, data: Dict[str, Any]) -> stix2.v21.AttackPattern:
        """
        Create a STIX Attack Pattern from provided data.
        
        Optional fields:
        - name: Name of the attack pattern
        - description: Description of the attack pattern
        - aliases: List of aliases for this attack pattern
        - kill_chain_phases: List of kill chain phases
        - external_references: List of external references
        """
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'attack-pattern'
            
        # Create the Attack Pattern object
        return stix2.v21.AttackPattern(**data)


class ThreatActorFactory(STIXObjectFactory):
    """
    Factory for creating STIX Threat Actor objects.
    """
    def create_object(self, data: Dict[str, Any]) -> stix2.v21.ThreatActor:
        """
        Create a STIX Threat Actor from provided data.
        
        Optional fields:
        - name: Name of the threat actor
        - description: Description of the threat actor
        - threat_actor_types: List of threat actor types
        - aliases: List of aliases
        - first_seen: Time the threat actor was first seen
        - last_seen: Time the threat actor was last seen
        - roles: List of roles the threat actor plays
        - goals: List of goals
        - sophistication: Level of sophistication
        - resource_level: Level of resources
        - primary_motivation: Primary motivation
        - secondary_motivations: List of secondary motivations
        """
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'threat-actor'
            
        # Create the Threat Actor object
        return stix2.v21.ThreatActor(**data)


class IdentityFactory(STIXObjectFactory):
    """
    Factory for creating STIX Identity objects.
    """
    def create_object(self, data: Dict[str, Any]) -> stix2.v21.Identity:
        """
        Create a STIX Identity from provided data.
        
        Required fields:
        - name: Name of the identity
        - identity_class: Class of this identity
        
        Optional fields:
        - description: Description of the identity
        - sectors: List of sectors
        - contact_information: Contact information
        """
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'identity'
        
        # Ensure required fields are present
        if 'name' not in data:
            raise ValueError("Identity requires a 'name' field")
        if 'identity_class' not in data:
            data['identity_class'] = 'organization'  # Default to organization
            
        # Create the Identity object
        return stix2.v21.Identity(**data)


class RelationshipFactory(STIXObjectFactory):
    """
    Factory for creating STIX Relationship objects.
    """
    def create_object(self, data: Dict[str, Any]) -> stix2.v21.Relationship:
        """
        Create a STIX Relationship from provided data.
        
        Required fields:
        - relationship_type: Type of relationship
        - source_ref: ID of source object
        - target_ref: ID of target object
        
        Optional fields:
        - description: Description of the relationship
        - start_time: Start time of the relationship
        - stop_time: Stop time of the relationship
        """
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'relationship'
        
        # Ensure required fields are present
        if 'relationship_type' not in data:
            raise ValueError("Relationship requires a 'relationship_type' field")
        if 'source_ref' not in data:
            raise ValueError("Relationship requires a 'source_ref' field")
        if 'target_ref' not in data:
            raise ValueError("Relationship requires a 'target_ref' field")
            
        # Create the Relationship object
        return stix2.v21.Relationship(**data)


class STIXObjectFactoryRegistry:
    """
    Registry for managing and retrieving STIX object factories based on object type.
    """
    _factories: Dict[str, Type[STIXObjectFactory]] = {
        'indicator': IndicatorFactory,
        'malware': MalwareFactory,
        'attack-pattern': AttackPatternFactory,
        'threat-actor': ThreatActorFactory,
        'identity': IdentityFactory,
        'relationship': RelationshipFactory,
    }
    
    @classmethod
    def register_factory(cls, object_type: str, factory_class: Type[STIXObjectFactory]):
        """
        Register a new factory for a specific STIX object type.
        """
        cls._factories[object_type] = factory_class
    
    @classmethod
    def get_factory(cls, object_type: str) -> STIXObjectFactory:
        """
        Get the appropriate factory for the given STIX object type.
        """
        factory_class = cls._factories.get(object_type)
        if not factory_class:
            raise ValueError(f"No factory registered for STIX object type: {object_type}")
        return factory_class()
    
    @classmethod
    def create_object(cls, data: Dict[str, Any]) -> stix2.v21.base._STIXBase:
        """
        Create a STIX object based on the 'type' field in the provided data.
        """
        object_type = data.get('type')
        if not object_type:
            raise ValueError("Data must include a 'type' field to determine the appropriate factory")
        
        factory = cls.get_factory(object_type)
        return factory.create_object(data)