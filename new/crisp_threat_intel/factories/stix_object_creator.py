import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
from django.utils import timezone
from ..domain.models import Indicator, TTPData


class StixObjectCreator(ABC):
    """
    Abstract creator for STIX objects (Factory Method pattern)
    """
    
    @abstractmethod
    def create_stix_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a STIX object from provided data"""
        pass
    
    def _prepare_common_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare common fields for all STIX objects"""
        current_time = timezone.now().isoformat()
        
        # Set spec_version if not provided
        if 'spec_version' not in data:
            data['spec_version'] = '2.1'
            
        # Set created/modified if not provided
        if 'created' not in data:
            data['created'] = current_time
        if 'modified' not in data:
            data['modified'] = current_time
            
        return data


class StixIndicatorCreator(StixObjectCreator):
    """
    Concrete creator for STIX Indicator objects
    """
    
    def create_stix_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a STIX Indicator from provided data"""
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'indicator'
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = f"indicator--{str(uuid.uuid4())}"
        
        # Ensure required fields are present
        if 'pattern' not in data:
            raise ValueError("Indicator requires a 'pattern' field")
        if 'valid_from' not in data:
            data['valid_from'] = timezone.now().isoformat()
        if 'labels' not in data:
            data['labels'] = ['malicious-activity']  # Default label
            
        return data
    
    def create_from_domain_model(self, indicator: Indicator) -> Dict[str, Any]:
        """Create STIX object from domain model"""
        return {
            'type': 'indicator',
            'id': indicator.stix_id,
            'created': indicator.created.isoformat(),
            'modified': indicator.modified.isoformat(),
            'name': indicator.name,
            'description': indicator.description,
            'pattern': indicator.pattern,
            'labels': indicator.labels,
            'valid_from': indicator.valid_from.isoformat(),
            'valid_until': indicator.valid_until.isoformat() if indicator.valid_until else None,
            'confidence': indicator.confidence,
            'created_by_ref': indicator.created_by_ref,
            'revoked': indicator.revoked,
            'external_references': indicator.external_references,
            'object_marking_refs': indicator.object_marking_refs,
            'granular_markings': indicator.granular_markings,
            'spec_version': '2.1'
        }


class StixTTPCreator(StixObjectCreator):
    """
    Concrete creator for STIX Attack Pattern objects from TTP data
    """
    
    def create_stix_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a STIX Attack Pattern from provided data"""
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'attack-pattern'
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = f"attack-pattern--{str(uuid.uuid4())}"
            
        return data
    
    def create_from_domain_model(self, ttp_data: TTPData) -> Dict[str, Any]:
        """Create STIX object from domain model"""
        stix_obj = {
            'type': 'attack-pattern',
            'id': ttp_data.stix_id,
            'created': ttp_data.created.isoformat(),
            'modified': ttp_data.modified.isoformat(),
            'name': ttp_data.name,
            'description': ttp_data.description,
            'kill_chain_phases': ttp_data.kill_chain_phases,
            'created_by_ref': ttp_data.created_by_ref,
            'revoked': ttp_data.revoked,
            'external_references': ttp_data.external_references,
            'object_marking_refs': ttp_data.object_marking_refs,
            'granular_markings': ttp_data.granular_markings,
            'spec_version': '2.1'
        }
        
        # Add MITRE ATT&CK specific fields if available
        if ttp_data.x_mitre_platforms:
            stix_obj['x_mitre_platforms'] = ttp_data.x_mitre_platforms
        if ttp_data.x_mitre_tactics:
            stix_obj['x_mitre_tactics'] = ttp_data.x_mitre_tactics
        if ttp_data.x_mitre_techniques:
            stix_obj['x_mitre_techniques'] = ttp_data.x_mitre_techniques
            
        return stix_obj


class StixMalwareCreator(StixObjectCreator):
    """
    Concrete creator for STIX Malware objects
    """
    
    def create_stix_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a STIX Malware from provided data"""
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'malware'
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = f"malware--{str(uuid.uuid4())}"
        
        # Ensure required fields are present
        if 'is_family' not in data:
            data['is_family'] = False  # Default to single malware instance
        if 'malware_types' not in data:
            data['malware_types'] = ['unknown']  # Default type
            
        return data


class StixThreatActorCreator(StixObjectCreator):
    """
    Concrete creator for STIX Threat Actor objects
    """
    
    def create_stix_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a STIX Threat Actor from provided data"""
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'threat-actor'
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = f"threat-actor--{str(uuid.uuid4())}"
        
        # Ensure required fields are present
        if 'threat_actor_types' not in data:
            data['threat_actor_types'] = ['unknown']  # Default type
            
        return data


class StixIdentityCreator(StixObjectCreator):
    """
    Concrete creator for STIX Identity objects
    """
    
    def create_stix_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a STIX Identity from provided data"""
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'identity'
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = f"identity--{str(uuid.uuid4())}"
        
        # Ensure required fields are present
        if 'name' not in data:
            raise ValueError("Identity requires a 'name' field")
        if 'identity_class' not in data:
            data['identity_class'] = 'organization'  # Default to organization
            
        return data


class StixRelationshipCreator(StixObjectCreator):
    """
    Concrete creator for STIX Relationship objects
    """
    
    def create_stix_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a STIX Relationship from provided data"""
        data = self._prepare_common_fields(data)
        
        # Set type if not provided
        data['type'] = 'relationship'
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = f"relationship--{str(uuid.uuid4())}"
        
        # Ensure required fields are present
        if 'relationship_type' not in data:
            raise ValueError("Relationship requires a 'relationship_type' field")
        if 'source_ref' not in data:
            raise ValueError("Relationship requires a 'source_ref' field")
        if 'target_ref' not in data:
            raise ValueError("Relationship requires a 'target_ref' field")
            
        return data


class StixObject:
    """
    Product class representing STIX objects
    """
    
    def __init__(self, stix_data: Dict[str, Any]):
        self.stix_data = stix_data
        self.object_type = stix_data.get('type')
        self.object_id = stix_data.get('id')
    
    def to_dict(self) -> Dict[str, Any]:
        """Return STIX object as dictionary"""
        return self.stix_data
    
    def to_json(self) -> str:
        """Return STIX object as JSON string"""
        import json
        return json.dumps(self.stix_data, indent=2)
    
    def get_type(self) -> str:
        """Get the STIX object type"""
        return self.object_type
    
    def get_id(self) -> str:
        """Get the STIX object ID"""
        return self.object_id


class StixObjectFactory:
    """
    Factory registry for creating STIX objects
    """
    
    _creators: Dict[str, Type[StixObjectCreator]] = {
        'indicator': StixIndicatorCreator,
        'attack-pattern': StixTTPCreator,
        'malware': StixMalwareCreator,
        'threat-actor': StixThreatActorCreator,
        'identity': StixIdentityCreator,
        'relationship': StixRelationshipCreator,
    }
    
    @classmethod
    def register_creator(cls, object_type: str, creator_class: Type[StixObjectCreator]):
        """Register a new creator for a specific STIX object type"""
        cls._creators[object_type] = creator_class
    
    @classmethod
    def get_creator(cls, object_type: str) -> StixObjectCreator:
        """Get the appropriate creator for the given STIX object type"""
        creator_class = cls._creators.get(object_type)
        if not creator_class:
            raise ValueError(f"No creator registered for STIX object type: {object_type}")
        return creator_class()
    
    @classmethod
    def create_stix_object(cls, data: Dict[str, Any]) -> StixObject:
        """Create a STIX object based on the 'type' field in the provided data"""
        object_type = data.get('type')
        if not object_type:
            raise ValueError("Data must include a 'type' field to determine the appropriate creator")
        
        creator = cls.get_creator(object_type)
        stix_data = creator.create_stix_object(data)
        return StixObject(stix_data)
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of supported STIX object types"""
        return list(cls._creators.keys())