from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StixObjectComponent(ABC):
    """
    Abstract component interface for STIX objects (Decorator Pattern)
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Return STIX object as dictionary"""
        pass
    
    @abstractmethod
    def to_json(self) -> str:
        """Return STIX object as JSON string"""
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Get the STIX object type"""
        pass
    
    @abstractmethod
    def get_id(self) -> str:
        """Get the STIX object ID"""
        pass


class StixObject(StixObjectComponent):
    """
    Concrete STIX object component
    """
    
    def __init__(self, stix_data: Dict[str, Any]):
        self.stix_data = stix_data.copy()
        self._validate_basic_structure()
    
    def _validate_basic_structure(self):
        """Validate basic STIX object structure"""
        required_fields = ['type', 'id', 'created', 'modified', 'spec_version']
        for field in required_fields:
            if field not in self.stix_data:
                raise ValueError(f"STIX object missing required field: {field}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return STIX object as dictionary"""
        return self.stix_data.copy()
    
    def to_json(self) -> str:
        """Return STIX object as JSON string"""
        return json.dumps(self.stix_data, indent=2)
    
    def get_type(self) -> str:
        """Get the STIX object type"""
        return self.stix_data.get('type', 'unknown')
    
    def get_id(self) -> str:
        """Get the STIX object ID"""
        return self.stix_data.get('id', 'unknown')


class StixDecorator(StixObjectComponent):
    """
    Abstract base decorator for STIX objects
    """
    
    def __init__(self, component: StixObjectComponent):
        self._component = component
    
    def to_dict(self) -> Dict[str, Any]:
        """Delegate to component"""
        return self._component.to_dict()
    
    def to_json(self) -> str:
        """Delegate to component"""
        return self._component.to_json()
    
    def get_type(self) -> str:
        """Delegate to component"""
        return self._component.get_type()
    
    def get_id(self) -> str:
        """Delegate to component"""
        return self._component.get_id()


class StixValidationDecorator(StixDecorator):
    """
    Decorator that adds validation capabilities to STIX objects
    """
    
    def __init__(self, component: StixObjectComponent, strict_validation: bool = True):
        super().__init__(component)
        self.strict_validation = strict_validation
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate(self) -> bool:
        """Validate the STIX object"""
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        stix_data = self._component.to_dict()
        object_type = stix_data.get('type')
        
        # Basic validation
        self._validate_basic_fields(stix_data)
        
        # Type-specific validation
        if object_type == 'indicator':
            self._validate_indicator(stix_data)
        elif object_type == 'attack-pattern':
            self._validate_attack_pattern(stix_data)
        elif object_type == 'malware':
            self._validate_malware(stix_data)
        elif object_type == 'threat-actor':
            self._validate_threat_actor(stix_data)
        elif object_type == 'identity':
            self._validate_identity(stix_data)
        elif object_type == 'relationship':
            self._validate_relationship(stix_data)
        
        return len(self.validation_errors) == 0
    
    def _validate_basic_fields(self, stix_data: Dict[str, Any]):
        """Validate basic STIX fields"""
        required_fields = ['type', 'id', 'created', 'modified', 'spec_version']
        
        for field in required_fields:
            if field not in stix_data:
                self.validation_errors.append(f"Missing required field: {field}")
        
        # Validate spec_version
        if stix_data.get('spec_version') != '2.1':
            self.validation_warnings.append("Spec version should be '2.1'")
        
        # Validate ID format
        object_id = stix_data.get('id', '')
        object_type = stix_data.get('type', '')
        if object_id and not object_id.startswith(f"{object_type}--"):
            self.validation_errors.append(f"ID should start with '{object_type}--'")
        
        # Validate timestamps
        for timestamp_field in ['created', 'modified']:
            if timestamp_field in stix_data:
                try:
                    datetime.fromisoformat(stix_data[timestamp_field].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    self.validation_errors.append(f"Invalid timestamp format in {timestamp_field}")
    
    def _validate_indicator(self, stix_data: Dict[str, Any]):
        """Validate STIX Indicator"""
        required_fields = ['pattern', 'labels', 'valid_from']
        
        for field in required_fields:
            if field not in stix_data:
                self.validation_errors.append(f"Indicator missing required field: {field}")
        
        # Validate labels
        labels = stix_data.get('labels', [])
        if not isinstance(labels, list) or not labels:
            self.validation_errors.append("Indicator must have at least one label")
        
        # Validate pattern
        pattern = stix_data.get('pattern', '')
        if not pattern or not isinstance(pattern, str):
            self.validation_errors.append("Indicator must have a valid pattern")
    
    def _validate_attack_pattern(self, stix_data: Dict[str, Any]):
        """Validate STIX Attack Pattern"""
        # Name is optional but recommended
        if 'name' not in stix_data:
            self.validation_warnings.append("Attack pattern should have a name")
    
    def _validate_malware(self, stix_data: Dict[str, Any]):
        """Validate STIX Malware"""
        required_fields = ['is_family']
        
        for field in required_fields:
            if field not in stix_data:
                self.validation_errors.append(f"Malware missing required field: {field}")
        
        # Validate malware_types
        if 'malware_types' in stix_data:
            malware_types = stix_data['malware_types']
            if not isinstance(malware_types, list) or not malware_types:
                self.validation_warnings.append("Malware should have at least one malware type")
    
    def _validate_threat_actor(self, stix_data: Dict[str, Any]):
        """Validate STIX Threat Actor"""
        # threat_actor_types is optional but recommended
        if 'threat_actor_types' not in stix_data:
            self.validation_warnings.append("Threat actor should have threat actor types")
    
    def _validate_identity(self, stix_data: Dict[str, Any]):
        """Validate STIX Identity"""
        required_fields = ['name', 'identity_class']
        
        for field in required_fields:
            if field not in stix_data:
                self.validation_errors.append(f"Identity missing required field: {field}")
    
    def _validate_relationship(self, stix_data: Dict[str, Any]):
        """Validate STIX Relationship"""
        required_fields = ['relationship_type', 'source_ref', 'target_ref']
        
        for field in required_fields:
            if field not in stix_data:
                self.validation_errors.append(f"Relationship missing required field: {field}")
    
    def get_validation_results(self) -> Dict[str, List[str]]:
        """Get validation results"""
        return {
            'errors': self.validation_errors.copy(),
            'warnings': self.validation_warnings.copy(),
            'is_valid': len(self.validation_errors) == 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Return validated STIX object as dictionary"""
        if self.strict_validation and not self.validate():
            raise ValueError(f"STIX object validation failed: {self.validation_errors}")
        return self._component.to_dict()


class StixTaxiiExportDecorator(StixDecorator):
    """
    Decorator that adds TAXII export functionality to STIX objects
    """
    
    def __init__(self, component: StixObjectComponent, collection_id: str = None):
        super().__init__(component)
        self.collection_id = collection_id
        self.export_metadata = {}
    
    def prepare_for_taxii_export(self, collection_id: str = None) -> Dict[str, Any]:
        """Prepare STIX object for TAXII export"""
        if collection_id:
            self.collection_id = collection_id
        
        stix_data = self._component.to_dict()
        
        # Add TAXII-specific metadata
        export_data = stix_data.copy()
        
        # Ensure proper TAXII media type compliance
        self._ensure_taxii_compliance(export_data)
        
        # Add collection metadata if available
        if self.collection_id:
            self.export_metadata['collection_id'] = self.collection_id
        
        self.export_metadata['exported_at'] = datetime.utcnow().isoformat() + 'Z'
        self.export_metadata['export_version'] = '1.0'
        
        return export_data
    
    def _ensure_taxii_compliance(self, stix_data: Dict[str, Any]):
        """Ensure STIX object is TAXII compliant"""
        # Ensure spec_version is set
        if 'spec_version' not in stix_data:
            stix_data['spec_version'] = '2.1'
        
        # Ensure timestamps are in proper format
        for timestamp_field in ['created', 'modified']:
            if timestamp_field in stix_data:
                timestamp = stix_data[timestamp_field]
                if isinstance(timestamp, str) and not timestamp.endswith('Z'):
                    # Ensure UTC timezone indicator
                    if '+' not in timestamp and 'Z' not in timestamp:
                        stix_data[timestamp_field] = timestamp + 'Z'
    
    def get_export_metadata(self) -> Dict[str, Any]:
        """Get export metadata"""
        return self.export_metadata.copy()
    
    def to_taxii_envelope(self) -> Dict[str, Any]:
        """Create TAXII envelope for this object"""
        stix_data = self.prepare_for_taxii_export()
        
        return {
            'id': f"bundle--{uuid.uuid4()}",
            'type': 'bundle',
            'spec_version': '2.1',
            'objects': [stix_data]
        }


class StixEnrichmentDecorator(StixDecorator):
    """
    Decorator that adds data enrichment capabilities to STIX objects
    """
    
    def __init__(self, component: StixObjectComponent):
        super().__init__(component)
        self.enrichments = {}
    
    def add_enrichment(self, enrichment_type: str, enrichment_data: Dict[str, Any]):
        """Add enrichment data to the STIX object"""
        if enrichment_type not in self.enrichments:
            self.enrichments[enrichment_type] = []
        
        enrichment_entry = {
            'data': enrichment_data,
            'added_at': datetime.utcnow().isoformat() + 'Z',
            'enrichment_id': str(uuid.uuid4())
        }
        
        self.enrichments[enrichment_type].append(enrichment_entry)
    
    def add_confidence_score(self, score: int, source: str = None):
        """Add confidence score enrichment"""
        enrichment_data = {'confidence': score}
        if source:
            enrichment_data['source'] = source
        
        self.add_enrichment('confidence', enrichment_data)
    
    def add_external_reference(self, source_name: str, url: str = None, external_id: str = None, description: str = None):
        """Add external reference enrichment"""
        enrichment_data = {'source_name': source_name}
        if url:
            enrichment_data['url'] = url
        if external_id:
            enrichment_data['external_id'] = external_id
        if description:
            enrichment_data['description'] = description
        
        self.add_enrichment('external_reference', enrichment_data)
    
    def add_context_information(self, context_type: str, context_data: Dict[str, Any]):
        """Add contextual information"""
        enrichment_data = {
            'context_type': context_type,
            'context_data': context_data
        }
        
        self.add_enrichment('context', enrichment_data)
    
    def get_enrichments(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all enrichments"""
        return self.enrichments.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Return enriched STIX object as dictionary"""
        stix_data = self._component.to_dict()
        
        # Apply enrichments to the STIX object
        if 'confidence' in self.enrichments:
            latest_confidence = self.enrichments['confidence'][-1]['data']['confidence']
            stix_data['confidence'] = latest_confidence
        
        if 'external_reference' in self.enrichments:
            if 'external_references' not in stix_data:
                stix_data['external_references'] = []
            
            for enrichment in self.enrichments['external_reference']:
                ref_data = enrichment['data'].copy()
                if ref_data not in stix_data['external_references']:
                    stix_data['external_references'].append(ref_data)
        
        # Add custom enrichment fields with x_ prefix
        if self.enrichments:
            stix_data['x_enrichments'] = self.enrichments
        
        return stix_data


class StixMarkingDecorator(StixDecorator):
    """
    Decorator that adds object marking capabilities to STIX objects
    """
    
    def __init__(self, component: StixObjectComponent):
        super().__init__(component)
        self.object_markings = []
        self.granular_markings = []
    
    def add_object_marking(self, marking_definition_ref: str):
        """Add object-level marking"""
        if marking_definition_ref not in self.object_markings:
            self.object_markings.append(marking_definition_ref)
    
    def add_granular_marking(self, selectors: List[str], marking_definition_ref: str):
        """Add granular marking for specific fields"""
        granular_marking = {
            'selectors': selectors,
            'marking_ref': marking_definition_ref
        }
        
        self.granular_markings.append(granular_marking)
    
    def add_tlp_marking(self, tlp_level: str):
        """Add TLP (Traffic Light Protocol) marking"""
        tlp_markings = {
            'white': 'marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9',
            'green': 'marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da',
            'amber': 'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82',
            'red': 'marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed'
        }
        
        tlp_ref = tlp_markings.get(tlp_level.lower())
        if tlp_ref:
            self.add_object_marking(tlp_ref)
        else:
            raise ValueError(f"Invalid TLP level: {tlp_level}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return marked STIX object as dictionary"""
        stix_data = self._component.to_dict()
        
        if self.object_markings:
            stix_data['object_marking_refs'] = self.object_markings.copy()
        
        if self.granular_markings:
            stix_data['granular_markings'] = self.granular_markings.copy()
        
        return stix_data