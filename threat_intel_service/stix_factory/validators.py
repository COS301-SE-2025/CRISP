import json
import re
import uuid
from typing import Dict, List, Any, Union, Optional
import stix2
from stix2.base import _STIXBase
from stix2.exceptions import InvalidValueError, MissingPropertiesError, ExtraPropertiesError
from stix2patterns.validator import run_validator as validate_pattern
from django.conf import settings

class STIXValidator:
    """
    Validator for STIX 2.1 objects.
    """
    def __init__(self):
        """
        Initialize the validator.
        """
        # Supported STIX types
        self.supported_types = {
            'indicator',
            'malware',
            'attack-pattern',
            'threat-actor',
            'identity',
            'relationship',
            'tool',
            'vulnerability',
            'observed-data',
            'report',
            'course-of-action',
            'campaign',
            'intrusion-set',
            'infrastructure',
            'location',
            'note',
            'opinion',
            'marking-definition'
        }
    
    def validate(self, stix_data: Union[Dict[str, Any], _STIXBase]) -> Dict[str, Any]:
        """
        Validate a STIX object against the STIX 2.1 specification.
        
        Args:
            stix_data: STIX object as a dictionary or a stix2 Python object
            
        Returns:
            Dictionary with validation results:
            {
                'valid': True/False,
                'errors': [list of error messages],
                'warnings': [list of warning messages]
            }
        """
        errors = []
        warnings = []
        
        # Convert to dictionary if a STIX object
        if isinstance(stix_data, _STIXBase):
            stix_data = json.loads(stix_data.serialize())
        
        # Check basic structure
        if not isinstance(stix_data, dict):
            return {
                'valid': False,
                'errors': ["STIX object must be a dictionary"],
                'warnings': []
            }
        
        # Check required fields
        for field in ['type', 'id', 'spec_version']:
            if field not in stix_data:
                errors.append(f"Missing required field: '{field}'")
        
        if errors:
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # Check if type is supported
        stix_type = stix_data.get('type')
        if stix_type not in self.supported_types:
            errors.append(f"Unsupported STIX type: '{stix_type}'")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # Check ID format
        stix_id = stix_data.get('id')
        if not self._validate_id(stix_id, stix_type):
            errors.append(f"Invalid STIX ID: '{stix_id}'. Must be in format: '{stix_type}--UUID'")
        
        # Check spec_version
        spec_version = stix_data.get('spec_version')
        if spec_version != '2.1':
            warnings.append(f"Non-standard spec_version: '{spec_version}'. Expected '2.1'")
        
        # Type-specific validation
        try:
            type_errors, type_warnings = self._validate_type_specific(stix_data)
            errors.extend(type_errors)
            warnings.extend(type_warnings)
        except Exception as e:
            errors.append(f"Error in type-specific validation: {str(e)}")
        
        # Validate using stix2 library
        try:
            self._validate_with_stix2_library(stix_data)
        except Exception as e:
            errors.append(f"STIX library validation error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_id(self, stix_id: str, stix_type: str) -> bool:
        """
        Validate a STIX ID.
        
        Args:
            stix_id: STIX ID to validate
            stix_type: STIX type to check against
            
        Returns:
            True if valid, False otherwise
        """
        if not stix_id or not isinstance(stix_id, str):
            return False
        
        # Check format: <type>--<uuid>
        id_pattern = re.compile(r'^' + re.escape(stix_type) + r'--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        return bool(id_pattern.match(stix_id))
    
    def _validate_with_stix2_library(self, stix_data: Dict[str, Any]) -> None:
        """
        Validate a STIX object using the stix2 library.
        
        Args:
            stix_data: STIX object as a dictionary
            
        Raises:
            Exception: If validation fails
        """
        stix_type = stix_data.get('type')
        
        # Get the appropriate class for the STIX type
        try:
            if stix_type == 'indicator':
                stix2.v21.Indicator(**stix_data)
            elif stix_type == 'malware':
                stix2.v21.Malware(**stix_data)
            elif stix_type == 'attack-pattern':
                stix2.v21.AttackPattern(**stix_data)
            elif stix_type == 'threat-actor':
                stix2.v21.ThreatActor(**stix_data)
            elif stix_type == 'identity':
                stix2.v21.Identity(**stix_data)
            elif stix_type == 'relationship':
                stix2.v21.Relationship(**stix_data)
            elif stix_type == 'tool':
                stix2.v21.Tool(**stix_data)
            elif stix_type == 'vulnerability':
                stix2.v21.Vulnerability(**stix_data)
            elif stix_type == 'observed-data':
                stix2.v21.ObservedData(**stix_data)
            elif stix_type == 'report':
                stix2.v21.Report(**stix_data)
            elif stix_type == 'course-of-action':
                stix2.v21.CourseOfAction(**stix_data)
            elif stix_type == 'campaign':
                stix2.v21.Campaign(**stix_data)
            elif stix_type == 'intrusion-set':
                stix2.v21.IntrusionSet(**stix_data)
            elif stix_type == 'infrastructure':
                stix2.v21.Infrastructure(**stix_data)
            elif stix_type == 'location':
                stix2.v21.Location(**stix_data)
            elif stix_type == 'note':
                stix2.v21.Note(**stix_data)
            elif stix_type == 'opinion':
                stix2.v21.Opinion(**stix_data)
            elif stix_type == 'marking-definition':
                stix2.v21.MarkingDefinition(**stix_data)
            # Add more types as needed
            
        except (InvalidValueError, MissingPropertiesError, ExtraPropertiesError) as e:
            raise ValueError(f"Invalid STIX object: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error validating STIX object: {str(e)}")
    
    def _validate_type_specific(self, stix_data: Dict[str, Any]) -> tuple:
        """
        Perform type-specific validation on a STIX object.
        
        Args:
            stix_data: STIX object as a dictionary
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        stix_type = stix_data.get('type')
        
        if stix_type == 'indicator':
            # Validate indicator pattern
            if 'pattern' not in stix_data:
                errors.append("Indicator missing required field: 'pattern'")
            elif not isinstance(stix_data['pattern'], str):
                errors.append("Indicator 'pattern' must be a string")
            else:
                # Validate pattern syntax if it's a STIX pattern
                pattern_type = stix_data.get('pattern_type', 'stix')
                if pattern_type == 'stix':
                    try:
                        pattern_results = validate_pattern(stix_data['pattern'])
                        if not pattern_results['valid']:
                            errors.append(f"Invalid STIX pattern: {pattern_results['errors']}")
                    except Exception as e:
                        errors.append(f"Error validating STIX pattern: {str(e)}")
            
            # Check valid_from
            if 'valid_from' not in stix_data:
                errors.append("Indicator missing required field: 'valid_from'")
            
        elif stix_type == 'malware':
            # Check is_family
            if 'is_family' not in stix_data:
                errors.append("Malware missing required field: 'is_family'")
            elif not isinstance(stix_data['is_family'], bool):
                errors.append("Malware 'is_family' must be a boolean")
                
        elif stix_type == 'relationship':
            # Check required fields
            for field in ['relationship_type', 'source_ref', 'target_ref']:
                if field not in stix_data:
                    errors.append(f"Relationship missing required field: '{field}'")
            
            # Check refs format
            if 'source_ref' in stix_data and not self._validate_ref(stix_data['source_ref']):
                errors.append(f"Invalid source_ref: '{stix_data['source_ref']}'")
                
            if 'target_ref' in stix_data and not self._validate_ref(stix_data['target_ref']):
                errors.append(f"Invalid target_ref: '{stix_data['target_ref']}'")
                
        elif stix_type == 'identity':
            # Check required fields
            if 'name' not in stix_data:
                errors.append("Identity missing required field: 'name'")
                
            if 'identity_class' not in stix_data:
                errors.append("Identity missing required field: 'identity_class'")
        
        # Common warnings for all types
        if 'created_by_ref' in stix_data and not self._validate_ref(stix_data['created_by_ref']):
            warnings.append(f"Invalid created_by_ref: '{stix_data['created_by_ref']}'")
            
        if 'object_marking_refs' in stix_data:
            if not isinstance(stix_data['object_marking_refs'], list):
                warnings.append("object_marking_refs must be a list")
            else:
                for ref in stix_data['object_marking_refs']:
                    if not self._validate_ref(ref):
                        warnings.append(f"Invalid object_marking_ref: '{ref}'")
        
        return errors, warnings
    
    def _validate_ref(self, ref: str) -> bool:
        """
        Validate a STIX reference.
        
        Args:
            ref: STIX reference to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not ref or not isinstance(ref, str):
            return False
        
        # Check format: <type>--<uuid>
        ref_pattern = re.compile(r'^[a-z0-9-]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        return bool(ref_pattern.match(ref))