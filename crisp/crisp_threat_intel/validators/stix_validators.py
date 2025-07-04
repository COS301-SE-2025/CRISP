"""
Comprehensive STIX 2.0 and 2.1 validation utilities.
Validates STIX objects against both specifications with detailed error reporting.
"""
import re
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class STIXValidationError(Exception):
    """Custom exception for STIX validation errors."""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(message)


class STIXValidator:
    """
    Comprehensive STIX validator supporting both 2.0 and 2.1 specifications.
    """
    
    # STIX 2.0 required fields by object type
    STIX_20_REQUIRED_FIELDS = {
        'indicator': ['type', 'id', 'created', 'modified', 'labels', 'pattern'],
        'malware': ['type', 'id', 'created', 'modified', 'labels', 'name'],
        'attack-pattern': ['type', 'id', 'created', 'modified', 'name'],
        'identity': ['type', 'id', 'created', 'modified', 'name', 'identity_class'],
        'bundle': ['type', 'id', 'objects'],
    }
    
    # STIX 2.1 required fields by object type
    STIX_21_REQUIRED_FIELDS = {
        'indicator': ['type', 'id', 'spec_version', 'created', 'modified', 'pattern', 'pattern_type', 'valid_from', 'labels'],
        'malware': ['type', 'id', 'spec_version', 'created', 'modified', 'name', 'malware_types', 'is_family'],
        'attack-pattern': ['type', 'id', 'spec_version', 'created', 'modified', 'name'],
        'identity': ['type', 'id', 'spec_version', 'created', 'modified', 'name', 'identity_class'],
        'bundle': ['type', 'id', 'objects'],  # Bundles don't require spec_version in STIX 2.1
    }
    
    # Valid STIX object types
    VALID_STIX_TYPES = {
        'indicator', 'malware', 'attack-pattern', 'threat-actor', 'identity',
        'relationship', 'tool', 'vulnerability', 'observed-data', 'report',
        'course-of-action', 'campaign', 'intrusion-set', 'infrastructure',
        'location', 'note', 'opinion', 'marking-definition', 'bundle'
    }
    
    # Valid identity classes
    VALID_IDENTITY_CLASSES = {
        'individual', 'group', 'organization', 'class', 'unknown'
    }
    
    # Valid malware types (STIX 2.1)
    VALID_MALWARE_TYPES = {
        'adware', 'backdoor', 'bot', 'bootkit', 'ddos', 'downloader',
        'dropper', 'exploit-kit', 'keylogger', 'ransomware', 'remote-access-trojan',
        'resource-exploitation', 'rogue-security-software', 'rootkit', 'screen-capture',
        'spyware', 'trojan', 'unknown', 'virus', 'webshell', 'wiper', 'worm'
    }
    
    @classmethod
    def validate_stix_object(cls, stix_obj: Dict[str, Any], spec_version: str = "2.1") -> Tuple[bool, List[str]]:
        """
        Validate a STIX object against the specified version.
        
        Args:
            stix_obj: STIX object dictionary
            spec_version: STIX specification version (2.0 or 2.1)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if spec_version not in ["2.0", "2.1"]:
            return False, [f"Unsupported spec_version: {spec_version}"]
        
        errors = []
        
        try:
            # Basic structure validation
            errors.extend(cls._validate_basic_structure(stix_obj, spec_version))
            
            # Type-specific validation
            obj_type = stix_obj.get('type')
            if obj_type in cls.STIX_20_REQUIRED_FIELDS or obj_type in cls.STIX_21_REQUIRED_FIELDS:
                errors.extend(cls._validate_type_specific(stix_obj, spec_version))
            
            # Field format validation
            errors.extend(cls._validate_field_formats(stix_obj, spec_version))
            
            # Cross-field validation
            errors.extend(cls._validate_cross_fields(stix_obj, spec_version))
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @classmethod
    def _validate_basic_structure(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate basic STIX object structure."""
        errors = []
        
        if not isinstance(stix_obj, dict):
            errors.append("STIX object must be a dictionary")
            return errors
        
        # Check required common fields
        if 'type' not in stix_obj:
            errors.append("Missing required field: type")
        elif stix_obj['type'] not in cls.VALID_STIX_TYPES:
            errors.append(f"Invalid STIX type: {stix_obj['type']}")
        
        if 'id' not in stix_obj:
            errors.append("Missing required field: id")
        elif not cls._validate_stix_id(stix_obj['id'], stix_obj.get('type')):
            errors.append(f"Invalid STIX ID format: {stix_obj['id']}")
        
        # spec_version is required in STIX 2.1 but not in 2.0
        # Exception: bundles don't require spec_version in either version
        if spec_version == "2.1" and stix_obj.get('type') != 'bundle':
            if 'spec_version' not in stix_obj:
                errors.append("Missing required field: spec_version")
            elif stix_obj['spec_version'] != "2.1":
                errors.append(f"Invalid spec_version: {stix_obj['spec_version']}")
        elif spec_version == "2.0" and 'spec_version' in stix_obj:
            # spec_version should not be present in STIX 2.0
            if stix_obj['spec_version'] != "2.0":
                errors.append(f"Invalid spec_version for STIX 2.0: {stix_obj['spec_version']}")
        
        return errors
    
    @classmethod
    def _validate_type_specific(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate type-specific required fields."""
        errors = []
        obj_type = stix_obj.get('type')
        
        # Get required fields for this type and version
        if spec_version == "2.0":
            required_fields = cls.STIX_20_REQUIRED_FIELDS.get(obj_type, [])
        else:
            required_fields = cls.STIX_21_REQUIRED_FIELDS.get(obj_type, [])
        
        # Check all required fields are present
        for field in required_fields:
            if field not in stix_obj:
                errors.append(f"Missing required field for {obj_type}: {field}")
        
        # Type-specific validation
        if obj_type == 'indicator':
            errors.extend(cls._validate_indicator(stix_obj, spec_version))
        elif obj_type == 'malware':
            errors.extend(cls._validate_malware(stix_obj, spec_version))
        elif obj_type == 'attack-pattern':
            errors.extend(cls._validate_attack_pattern(stix_obj, spec_version))
        elif obj_type == 'identity':
            errors.extend(cls._validate_identity(stix_obj, spec_version))
        elif obj_type == 'bundle':
            errors.extend(cls._validate_bundle(stix_obj, spec_version))
        
        return errors
    
    @classmethod
    def _validate_indicator(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate STIX Indicator object."""
        errors = []
        
        # Pattern validation
        if 'pattern' in stix_obj:
            if not isinstance(stix_obj['pattern'], str) or not stix_obj['pattern'].strip():
                errors.append("Indicator pattern must be a non-empty string")
        
        # Labels validation
        if 'labels' in stix_obj:
            if not isinstance(stix_obj['labels'], list) or not stix_obj['labels']:
                errors.append("Indicator labels must be a non-empty list")
        
        # STIX 2.1 specific validations
        if spec_version == "2.1":
            if 'pattern_type' in stix_obj:
                valid_pattern_types = ['stix', 'pcre', 'sigma', 'snort', 'suricata', 'yara']
                if stix_obj['pattern_type'] not in valid_pattern_types:
                    errors.append(f"Invalid pattern_type: {stix_obj['pattern_type']}")
            
            if 'valid_from' in stix_obj:
                if not cls._validate_timestamp(stix_obj['valid_from']):
                    errors.append("Invalid valid_from timestamp format")
        
        return errors
    
    @classmethod
    def _validate_malware(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate STIX Malware object."""
        errors = []
        
        # Name validation
        if 'name' in stix_obj:
            if not isinstance(stix_obj['name'], str) or not stix_obj['name'].strip():
                errors.append("Malware name must be a non-empty string")
        
        if spec_version == "2.0":
            # STIX 2.0 uses labels
            if 'labels' in stix_obj:
                if not isinstance(stix_obj['labels'], list) or not stix_obj['labels']:
                    errors.append("Malware labels must be a non-empty list")
        else:
            # STIX 2.1 uses malware_types and is_family
            if 'malware_types' in stix_obj:
                if not isinstance(stix_obj['malware_types'], list) or not stix_obj['malware_types']:
                    errors.append("Malware malware_types must be a non-empty list")
                else:
                    invalid_types = set(stix_obj['malware_types']) - cls.VALID_MALWARE_TYPES
                    if invalid_types:
                        errors.append(f"Invalid malware_types: {invalid_types}")
            
            if 'is_family' in stix_obj:
                if not isinstance(stix_obj['is_family'], bool):
                    errors.append("Malware is_family must be a boolean")
        
        return errors
    
    @classmethod
    def _validate_attack_pattern(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate STIX Attack Pattern object."""
        errors = []
        
        # Name validation
        if 'name' in stix_obj:
            if not isinstance(stix_obj['name'], str) or not stix_obj['name'].strip():
                errors.append("Attack Pattern name must be a non-empty string")
        
        return errors
    
    @classmethod
    def _validate_identity(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate STIX Identity object."""
        errors = []
        
        # Name validation
        if 'name' in stix_obj:
            if not isinstance(stix_obj['name'], str) or not stix_obj['name'].strip():
                errors.append("Identity name must be a non-empty string")
        
        # Identity class validation
        if 'identity_class' in stix_obj:
            if stix_obj['identity_class'] not in cls.VALID_IDENTITY_CLASSES:
                errors.append(f"Invalid identity_class: {stix_obj['identity_class']}")
        
        return errors
    
    @classmethod
    def _validate_bundle(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate STIX Bundle object."""
        errors = []
        
        # Objects validation
        if 'objects' in stix_obj:
            if not isinstance(stix_obj['objects'], list):
                errors.append("Bundle objects must be a list")
            else:
                for i, obj in enumerate(stix_obj['objects']):
                    if not isinstance(obj, dict):
                        errors.append(f"Bundle object at index {i} must be a dictionary")
                    elif 'type' not in obj:
                        errors.append(f"Bundle object at index {i} missing type field")
        
        return errors
    
    @classmethod
    def _validate_field_formats(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate field formats and values."""
        errors = []
        
        # Timestamp fields validation
        timestamp_fields = ['created', 'modified', 'valid_from', 'valid_until', 'first_seen', 'last_seen']
        for field in timestamp_fields:
            if field in stix_obj:
                if not cls._validate_timestamp(stix_obj[field]):
                    errors.append(f"Invalid timestamp format for {field}: {stix_obj[field]}")
        
        # Confidence validation
        if 'confidence' in stix_obj:
            if not isinstance(stix_obj['confidence'], int) or not (0 <= stix_obj['confidence'] <= 100):
                errors.append("Confidence must be an integer between 0 and 100")
        
        # External references validation
        if 'external_references' in stix_obj:
            if not isinstance(stix_obj['external_references'], list):
                errors.append("External references must be a list")
            else:
                for i, ref in enumerate(stix_obj['external_references']):
                    if not isinstance(ref, dict):
                        errors.append(f"External reference at index {i} must be a dictionary")
                    elif 'source_name' not in ref:
                        errors.append(f"External reference at index {i} missing source_name")
        
        return errors
    
    @classmethod
    def _validate_cross_fields(cls, stix_obj: Dict[str, Any], spec_version: str) -> List[str]:
        """Validate relationships between fields."""
        errors = []
        
        # created <= modified validation
        if 'created' in stix_obj and 'modified' in stix_obj:
            try:
                created = cls._parse_timestamp(stix_obj['created'])
                modified = cls._parse_timestamp(stix_obj['modified'])
                if created > modified:
                    errors.append("Created timestamp cannot be later than modified timestamp")
            except:
                pass  # Timestamp format errors already caught above
        
        # Pattern and pattern_type consistency (STIX 2.1)
        if spec_version == "2.1" and stix_obj.get('type') == 'indicator':
            if 'pattern' in stix_obj and 'pattern_type' not in stix_obj:
                errors.append("Indicator with pattern must have pattern_type in STIX 2.1")
        
        return errors
    
    @classmethod
    def _validate_stix_id(cls, stix_id: str, obj_type: str = None) -> bool:
        """Validate STIX ID format."""
        if not isinstance(stix_id, str):
            return False
        
        # STIX ID pattern: type--uuid
        pattern = r'^[a-z0-9-]+--[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if not re.match(pattern, stix_id):
            return False
        
        # If object type is provided, check consistency
        if obj_type:
            id_type = stix_id.split('--')[0]
            if id_type != obj_type:
                return False
        
        return True
    
    @classmethod
    def _validate_timestamp(cls, timestamp: str) -> bool:
        """Validate timestamp format (RFC 3339)."""
        if not isinstance(timestamp, str):
            return False
        
        try:
            cls._parse_timestamp(timestamp)
            return True
        except:
            return False
    
    @classmethod
    def _parse_timestamp(cls, timestamp: str) -> datetime:
        """Parse timestamp string to datetime object."""
        # Try different timestamp formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S%z'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Invalid timestamp format: {timestamp}")
    
    @classmethod
    def validate_stix_bundle(cls, bundle: Dict[str, Any], spec_version: str = "2.1") -> Tuple[bool, List[str]]:
        """
        Validate a complete STIX bundle.
        
        Args:
            bundle: STIX bundle dictionary
            spec_version: STIX specification version
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate bundle structure
        bundle_valid, bundle_errors = cls.validate_stix_object(bundle, spec_version)
        errors.extend(bundle_errors)
        
        # Validate each object in the bundle
        if 'objects' in bundle and isinstance(bundle['objects'], list):
            for i, obj in enumerate(bundle['objects']):
                obj_valid, obj_errors = cls.validate_stix_object(obj, spec_version)
                if not obj_valid:
                    for error in obj_errors:
                        errors.append(f"Object {i}: {error}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @classmethod
    def get_validation_summary(cls, stix_obj: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Get a comprehensive validation summary.
        
        Args:
            stix_obj: STIX object or bundle to validate
            spec_version: STIX specification version
            
        Returns:
            Validation summary dictionary
        """
        if stix_obj.get('type') == 'bundle':
            is_valid, errors = cls.validate_stix_bundle(stix_obj, spec_version)
            object_count = len(stix_obj.get('objects', []))
        else:
            is_valid, errors = cls.validate_stix_object(stix_obj, spec_version)
            object_count = 1
        
        return {
            'is_valid': is_valid,
            'spec_version': spec_version,
            'object_type': stix_obj.get('type', 'unknown'),
            'object_count': object_count,
            'error_count': len(errors),
            'errors': errors,
            'validation_timestamp': datetime.utcnow().isoformat() + 'Z'
        }


class STIXVersionConverter:
    """
    Utility class for converting between STIX 2.0 and 2.1 formats.
    """
    
    @classmethod
    def convert_to_21(cls, stix_20_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert STIX 2.0 object to STIX 2.1 format.
        
        Args:
            stix_20_obj: STIX 2.0 object
            
        Returns:
            STIX 2.1 object
        """
        stix_21_obj = stix_20_obj.copy()
        
        # Add spec_version
        stix_21_obj['spec_version'] = '2.1'
        
        obj_type = stix_21_obj.get('type')
        
        if obj_type == 'indicator':
            # Add pattern_type if not present
            if 'pattern_type' not in stix_21_obj:
                stix_21_obj['pattern_type'] = 'stix'
            
            # Add valid_from if not present
            if 'valid_from' not in stix_21_obj:
                stix_21_obj['valid_from'] = stix_21_obj.get('created')
        
        elif obj_type == 'malware':
            # Convert labels to malware_types and add is_family
            if 'labels' in stix_21_obj and 'malware_types' not in stix_21_obj:
                stix_21_obj['malware_types'] = stix_21_obj['labels']
            
            if 'is_family' not in stix_21_obj:
                stix_21_obj['is_family'] = False
        
        return stix_21_obj
    
    @classmethod
    def convert_to_20(cls, stix_21_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert STIX 2.1 object to STIX 2.0 format.
        
        Args:
            stix_21_obj: STIX 2.1 object
            
        Returns:
            STIX 2.0 object
        """
        stix_20_obj = stix_21_obj.copy()
        
        # Remove spec_version
        if 'spec_version' in stix_20_obj:
            del stix_20_obj['spec_version']
        
        obj_type = stix_20_obj.get('type')
        
        if obj_type == 'indicator':
            # Remove pattern_type and valid_from (not in STIX 2.0)
            if 'pattern_type' in stix_20_obj:
                del stix_20_obj['pattern_type']
            if 'valid_from' in stix_20_obj:
                del stix_20_obj['valid_from']
        
        elif obj_type == 'malware':
            # Convert malware_types to labels and remove is_family
            if 'malware_types' in stix_20_obj and 'labels' not in stix_20_obj:
                stix_20_obj['labels'] = stix_20_obj['malware_types']
            
            if 'malware_types' in stix_20_obj:
                del stix_20_obj['malware_types']
            if 'is_family' in stix_20_obj:
                del stix_20_obj['is_family']
        
        return stix_20_obj