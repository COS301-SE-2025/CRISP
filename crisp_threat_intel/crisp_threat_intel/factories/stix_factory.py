"""
STIX Object Factory Pattern Implementation
Following CRISP design specification precisely.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import uuid
import stix2
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class StixObjectCreator(ABC):
    """
    Abstract factory for creating STIX objects.
    Defines the interface for all STIX object creation.
    """
    
    @abstractmethod
    def create_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a STIX object from input data.
        
        Args:
            data: Input data for creating the STIX object
            
        Returns:
            STIX object dictionary
        """
        pass
    
    def _ensure_common_properties(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure common STIX properties are set.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            STIX object with common properties ensured
        """
        current_time = stix2.utils.format_datetime(timezone.now())
        
        # Ensure required properties
        if 'id' not in stix_obj:
            stix_obj['id'] = f"{stix_obj['type']}--{str(uuid.uuid4())}"
        
        if 'spec_version' not in stix_obj:
            stix_obj['spec_version'] = '2.1'
        
        if 'created' not in stix_obj:
            stix_obj['created'] = current_time
        
        if 'modified' not in stix_obj:
            stix_obj['modified'] = current_time
        
        return stix_obj


class StixIndicatorCreator(StixObjectCreator):
    """
    Concrete factory for creating STIX Indicator objects.
    """
    
    def create_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a STIX Indicator object.
        
        Args:
            data: Input data containing indicator information
            
        Returns:
            STIX Indicator object dictionary
        """
        stix_obj = {
            'type': 'indicator',
            'pattern': data.get('pattern', ''),
            'pattern_type': data.get('pattern_type', 'stix'),
            'valid_from': data.get('valid_from', stix2.utils.format_datetime(timezone.now())),
            'labels': data.get('labels', ['malicious-activity']),
        }
        
        # Add optional properties
        if 'name' in data:
            stix_obj['name'] = data['name']
        
        if 'description' in data:
            stix_obj['description'] = data['description']
        
        if 'confidence' in data:
            stix_obj['confidence'] = data['confidence']
        
        if 'external_references' in data:
            stix_obj['external_references'] = data['external_references']
        
        if 'kill_chain_phases' in data:
            stix_obj['kill_chain_phases'] = data['kill_chain_phases']
        
        if 'created_by_ref' in data:
            stix_obj['created_by_ref'] = data['created_by_ref']
        
        # Ensure common properties
        stix_obj = self._ensure_common_properties(stix_obj)
        
        # Validate required fields for indicators
        if not stix_obj.get('pattern'):
            raise ValueError("Indicator objects must have a pattern")
        
        if not stix_obj.get('labels'):
            raise ValueError("Indicator objects must have labels")
        
        logger.debug(f"Created STIX Indicator: {stix_obj['id']}")
        return stix_obj


class StixTTPCreator(StixObjectCreator):
    """
    Concrete factory for creating STIX Attack Pattern objects (TTPs).
    """
    
    def create_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a STIX Attack Pattern object.
        
        Args:
            data: Input data containing TTP information
            
        Returns:
            STIX Attack Pattern object dictionary
        """
        stix_obj = {
            'type': 'attack-pattern',
            'name': data.get('name', 'Unknown Attack Pattern'),
        }
        
        # Add optional properties
        if 'description' in data:
            stix_obj['description'] = data['description']
        
        if 'external_references' in data:
            stix_obj['external_references'] = data['external_references']
        
        if 'kill_chain_phases' in data:
            stix_obj['kill_chain_phases'] = data['kill_chain_phases']
        
        if 'x_mitre_id' in data:
            stix_obj['x_mitre_id'] = data['x_mitre_id']
        
        if 'created_by_ref' in data:
            stix_obj['created_by_ref'] = data['created_by_ref']
        
        # Ensure common properties
        stix_obj = self._ensure_common_properties(stix_obj)
        
        # Validate required fields for attack patterns
        if not stix_obj.get('name'):
            raise ValueError("Attack Pattern objects must have a name")
        
        logger.debug(f"Created STIX Attack Pattern: {stix_obj['id']}")
        return stix_obj


class StixMalwareCreator(StixObjectCreator):
    """
    Concrete factory for creating STIX Malware objects.
    """
    
    def create_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a STIX Malware object.
        
        Args:
            data: Input data containing malware information
            
        Returns:
            STIX Malware object dictionary
        """
        stix_obj = {
            'type': 'malware',
            'name': data.get('name', 'Unknown Malware'),
            'is_family': data.get('is_family', False),
            'malware_types': data.get('malware_types', ['trojan']),
        }
        
        # Add optional properties
        if 'description' in data:
            stix_obj['description'] = data['description']
        
        if 'labels' in data:
            stix_obj['labels'] = data['labels']
        
        if 'external_references' in data:
            stix_obj['external_references'] = data['external_references']
        
        if 'kill_chain_phases' in data:
            stix_obj['kill_chain_phases'] = data['kill_chain_phases']
        
        if 'created_by_ref' in data:
            stix_obj['created_by_ref'] = data['created_by_ref']
        
        # Ensure common properties
        stix_obj = self._ensure_common_properties(stix_obj)
        
        # Validate required fields for malware
        if not stix_obj.get('name'):
            raise ValueError("Malware objects must have a name")
        
        if not stix_obj.get('malware_types'):
            raise ValueError("Malware objects must have malware_types")
        
        logger.debug(f"Created STIX Malware: {stix_obj['id']}")
        return stix_obj


class StixIdentityCreator(StixObjectCreator):
    """
    Concrete factory for creating STIX Identity objects.
    """
    
    def create_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a STIX Identity object.
        
        Args:
            data: Input data containing identity information
            
        Returns:
            STIX Identity object dictionary
        """
        stix_obj = {
            'type': 'identity',
            'name': data.get('name', 'Unknown Identity'),
            'identity_class': data.get('identity_class', 'organization'),
        }
        
        # Add optional properties
        if 'description' in data:
            stix_obj['description'] = data['description']
        
        if 'sectors' in data:
            stix_obj['sectors'] = data['sectors']
        
        if 'contact_information' in data:
            stix_obj['contact_information'] = data['contact_information']
        
        if 'external_references' in data:
            stix_obj['external_references'] = data['external_references']
        
        if 'created_by_ref' in data:
            stix_obj['created_by_ref'] = data['created_by_ref']
        
        # Ensure common properties
        stix_obj = self._ensure_common_properties(stix_obj)
        
        # Validate required fields for identity
        if not stix_obj.get('name'):
            raise ValueError("Identity objects must have a name")
        
        if not stix_obj.get('identity_class'):
            raise ValueError("Identity objects must have an identity_class")
        
        logger.debug(f"Created STIX Identity: {stix_obj['id']}")
        return stix_obj


class STIXObjectFactory:
    """
    Factory registry for creating STIX objects.
    Uses the Factory Method pattern.
    """
    
    _creators = {
        'indicator': StixIndicatorCreator,
        'attack-pattern': StixTTPCreator,
        'malware': StixMalwareCreator,
        'identity': StixIdentityCreator,
    }
    
    @classmethod
    def create_object(cls, object_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a STIX object using the appropriate factory.
        
        Args:
            object_type: Type of STIX object to create
            data: Input data for object creation
            
        Returns:
            STIX object dictionary
            
        Raises:
            ValueError: If object type is not supported
        """
        if object_type not in cls._creators:
            raise ValueError(f"Unsupported STIX object type: {object_type}")
        
        creator = cls._creators[object_type]()
        return creator.create_object(data)
    
    @classmethod
    def register_creator(cls, object_type: str, creator_class: type):
        """
        Register a new STIX object creator.
        
        Args:
            object_type: STIX object type
            creator_class: Creator class
        """
        if not issubclass(creator_class, StixObjectCreator):
            raise ValueError("Creator class must inherit from StixObjectCreator")
        
        cls._creators[object_type] = creator_class
        logger.info(f"Registered STIX creator for type: {object_type}")
    
    @classmethod
    def get_supported_types(cls) -> list:
        """
        Get list of supported STIX object types.
        
        Returns:
            List of supported object types
        """
        return list(cls._creators.keys())


# Convenience functions for backward compatibility
def create_indicator(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a STIX indicator object."""
    return STIXObjectFactory.create_object('indicator', data)


def create_attack_pattern(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a STIX attack pattern object."""
    return STIXObjectFactory.create_object('attack-pattern', data)


def create_malware(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a STIX malware object."""
    return STIXObjectFactory.create_object('malware', data)


def create_identity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a STIX identity object."""
    return STIXObjectFactory.create_object('identity', data)