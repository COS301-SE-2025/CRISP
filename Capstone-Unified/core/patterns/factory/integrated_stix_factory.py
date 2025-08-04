"""
Complete Integrated STIX Object Factory
"""

from typing import Dict, Any, Optional, Union
import logging

# Import all the integrated creators
from .stix_base_factory import STIXObjectFactory
from .stix_indicator_integrated import StixIndicatorCreator
from .stix_ttp_integrated import StixTTPCreator
from .stix_additional_creators import StixMalwareCreator, StixIdentityCreator

logger = logging.getLogger(__name__)


# Convenience functions for backward compatibility and ease of use
def create_indicator(data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
    """
    Create a STIX indicator object from data dictionary
    
    Args:
        data: Indicator data (pattern, labels, confidence, etc.)
        spec_version: STIX specification version (2.0 or 2.1)
        
    Returns:
        STIX Indicator object dictionary
    """
    return STIXObjectFactory.create_object('indicator', data, spec_version)


def create_attack_pattern(data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
    """
    Create a STIX attack pattern object from data dictionary
    
    Args:
        data: Attack pattern data (name, description, mitre_technique_id, etc.)
        spec_version: STIX specification version (2.0 or 2.1)
        
    Returns:
        STIX Attack Pattern object dictionary
    """
    return STIXObjectFactory.create_object('attack-pattern', data, spec_version)


def create_malware(data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
    """
    Create a STIX malware object from data dictionary
    
    Args:
        data: Malware data (name, malware_types, description, etc.)
        spec_version: STIX specification version (2.0 or 2.1)
        
    Returns:
        STIX Malware object dictionary
    """
    return STIXObjectFactory.create_object('malware', data, spec_version)


def create_identity(data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
    """
    Create a STIX identity object from data dictionary
    
    Args:
        data: Identity data (name, identity_class, sectors, etc.)
        spec_version: STIX specification version (2.0 or 2.1)
        
    Returns:
        STIX Identity object dictionary
    """
    return STIXObjectFactory.create_object('identity', data, spec_version)


# Helper functions
def create_indicator_from_ioc(
    indicator_type: str, 
    value: str, 
    confidence: int = 50,
    description: str = "",
    spec_version: str = "2.1"
) -> Dict[str, Any]:
    """
    Create a STIX indicator from IOC components
    """
    data = {
        'indicator_type': indicator_type,
        'value': value,
        'confidence': confidence,
        'labels': ['malicious-activity']
    }
    
    if description:
        data['description'] = description
    
    return create_indicator(data, spec_version)


def create_mitre_attack_pattern(
    technique_id: str,
    name: str,
    tactic: str,
    description: str = "",
    spec_version: str = "2.1"
) -> Dict[str, Any]:
    """
    Create a STIX attack pattern for MITRE ATT&CK technique
    """
    data = {
        'name': name,
        'mitre_technique_id': technique_id,
        'mitre_tactic': tactic
    }
    
    if description:
        data['description'] = description
    
    return create_attack_pattern(data, spec_version)


def convert_crisp_to_stix(crisp_entity, object_type: str):
    """
    Convert a CRISP entity to a STIX object
    """
    return STIXObjectFactory.create_stix_object(object_type, crisp_entity)


def convert_stix_to_crisp(stix_obj) -> Dict[str, Any]:
    """
    Convert a STIX object to CRISP entity data
    """
    return STIXObjectFactory.create_from_stix(stix_obj)


def batch_create_stix_objects(
    objects_data: list,
    default_spec_version: str = "2.1"
) -> list:
    """
    Create multiple STIX objects from a list of data dictionaries
    """
    results = []
    
    for obj_info in objects_data:
        try:
            obj_type = obj_info['type']
            obj_data = obj_info['data']
            spec_version = obj_info.get('spec_version', default_spec_version)
            
            stix_obj = STIXObjectFactory.create_object(obj_type, obj_data, spec_version)
            results.append(stix_obj)
            
        except Exception as e:
            logger.error(f"Error creating STIX object: {str(e)}")
            continue
    
    return results


def get_factory_info() -> Dict[str, Any]:
    """
    Get information about the current factory configuration
    """
    return {
        'supported_types': STIXObjectFactory.get_supported_types(),
        'creators': {
            obj_type: creator_class.__name__ 
            for obj_type, creator_class in STIXObjectFactory._creators.items()
        },
        'version': '1.0.0-integrated'
    }


# Export commonly used items
__all__ = [
    'STIXObjectFactory',
    'create_indicator',
    'create_attack_pattern', 
    'create_malware',
    'create_identity',
    'create_indicator_from_ioc',
    'create_mitre_attack_pattern',
    'convert_crisp_to_stix',
    'convert_stix_to_crisp',
    'batch_create_stix_objects',
    'get_factory_info'
]


# Migration helper
class LegacyStixIndicatorCreator:
    """
    Legacy compatibility wrapper for existing code using the old interface
    """
    
    def __init__(self):
        self._creator = StixIndicatorCreator()
    
    def create_from_stix(self, stix_obj, threat_feed):
        return self._creator.create_from_stix(stix_obj)
    
    def create_stix_object(self, crisp_entity):
        return self._creator.create_stix_object(crisp_entity)


class LegacyStixTTPCreator:
    """
    Legacy compatibility wrapper for existing code using the old interface
    """
    
    def __init__(self):
        self._creator = StixTTPCreator()
    
    def create_from_stix(self, stix_obj, threat_feed):
        return self._creator.create_from_stix(stix_obj)
    
    def create_stix_object(self, crisp_entity):
        return self._creator.create_stix_object(crisp_entity)


# Initialize the factory with all creators
logger.info("Integrated STIX Factory initialized with supported types: %s", 
           STIXObjectFactory.get_supported_types())