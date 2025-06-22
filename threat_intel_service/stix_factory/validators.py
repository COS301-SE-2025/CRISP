import json
import re
import uuid
from typing import Dict, List, Any, Union, Optional
import stix2
from stix2.base import _STIXBase
from stix2.exceptions import InvalidValueError, MissingPropertiesError, ExtraPropertiesError
from stix2patterns.validator import run_validator as validate_pattern
from django.conf import settings
from .version_handler import STIXVersionHandler, STIXVersion, STIXVersionDetector

class STIXValidator:
    """
    Multi-version STIX validator supporting STIX 1.x and 2.x.
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
        
        self.version_detector = STIXVersionDetector()
        self.version_handler = STIXVersionHandler()
    
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
    
    def validate_multi_version(self, stix_data: Union[str, Dict[str, Any], bytes]) -> Dict[str, Any]:
        """
        Validate STIX data of any supported version.
        
        Args:
            stix_data: STIX data in any supported format/version
            
        Returns:
            Dictionary with validation results including version information
        """
        try:
            # Detect version first
            detected_version = self.version_detector.detect_version(stix_data)
            
            if detected_version == STIXVersion.UNKNOWN:
                return {
                    'valid': False,
                    'errors': ["Unable to detect STIX version from input data"],
                    'warnings': [],
                    'detected_version': 'unknown',
                    'converted_to_stix21': False
                }
            
            # For STIX 1.x, validate basic structure then convert
            if detected_version in [STIXVersion.STIX_1_0, STIXVersion.STIX_1_1, STIXVersion.STIX_1_2]:
                return self._validate_stix1x(stix_data, detected_version)
            
            # For STIX 2.0, validate then convert to 2.1
            elif detected_version == STIXVersion.STIX_2_0:
                return self._validate_stix20(stix_data)
            
            # For STIX 2.1, validate directly
            elif detected_version == STIXVersion.STIX_2_1:
                if isinstance(stix_data, str):
                    stix_data = json.loads(stix_data)
                elif isinstance(stix_data, bytes):
                    stix_data = json.loads(stix_data.decode('utf-8'))
                
                validation_result = self.validate(stix_data)
                validation_result.update({
                    'detected_version': detected_version.value,
                    'converted_to_stix21': False
                })
                return validation_result
            
            else:
                return {
                    'valid': False,
                    'errors': [f"Unsupported STIX version: {detected_version.value}"],
                    'warnings': [],
                    'detected_version': detected_version.value,
                    'converted_to_stix21': False
                }
                
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error during validation: {str(e)}"],
                'warnings': [],
                'detected_version': 'unknown',
                'converted_to_stix21': False
            }
    
    def _validate_stix1x(self, stix_data: Union[str, Dict[str, Any], bytes], version: STIXVersion) -> Dict[str, Any]:
        """
        Validate STIX 1.x data.
        
        Args:
            stix_data: STIX 1.x data
            version: Detected STIX 1.x version
            
        Returns:
            Validation results
        """
        errors = []
        warnings = []
        
        try:
            # Basic XML structure validation for STIX 1.x
            if isinstance(stix_data, (str, bytes)):
                if isinstance(stix_data, bytes):
                    stix_data = stix_data.decode('utf-8')
                
                # Check for basic XML structure
                if not stix_data.strip().startswith('<?xml') and not stix_data.strip().startswith('<stix'):
                    errors.append("STIX 1.x data must be valid XML")
                    return {
                        'valid': False,
                        'errors': errors,
                        'warnings': warnings,
                        'detected_version': version.value,
                        'converted_to_stix21': False
                    }
                
                # Check for STIX namespace
                if 'stix' not in stix_data.lower():
                    warnings.append("STIX namespace not found in XML")
            
            # Try to convert to STIX 2.1 and validate
            try:
                processed_data = self.version_handler.process_stix_data(stix_data)
                stix21_data = processed_data['stix_data']
                
                # Validate converted STIX 2.1 data
                if stix21_data.get('type') == 'bundle':
                    bundle_errors = []
                    bundle_warnings = []
                    
                    for obj in stix21_data.get('objects', []):
                        obj_validation = self.validate(obj)
                        bundle_errors.extend(obj_validation['errors'])
                        bundle_warnings.extend(obj_validation['warnings'])
                    
                    errors.extend(bundle_errors)
                    warnings.extend(bundle_warnings)
                else:
                    validation_result = self.validate(stix21_data)
                    errors.extend(validation_result['errors'])
                    warnings.extend(validation_result['warnings'])
                
                # Add conversion notes as warnings
                warnings.extend(processed_data.get('conversion_notes', []))
                
                return {
                    'valid': len(errors) == 0,
                    'errors': errors,
                    'warnings': warnings,
                    'detected_version': version.value,
                    'converted_to_stix21': True,
                    'conversion_notes': processed_data.get('conversion_notes', [])
                }
                
            except Exception as e:
                errors.append(f"Error converting STIX 1.x to 2.1: {str(e)}")
                return {
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings,
                    'detected_version': version.value,
                    'converted_to_stix21': False
                }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error validating STIX 1.x data: {str(e)}"],
                'warnings': warnings,
                'detected_version': version.value,
                'converted_to_stix21': False
            }
    
    def _validate_stix20(self, stix_data: Union[str, Dict[str, Any], bytes]) -> Dict[str, Any]:
        """
        Validate STIX 2.0 data.
        
        Args:
            stix_data: STIX 2.0 data
            
        Returns:
            Validation results
        """
        errors = []
        warnings = []
        
        try:
            # Parse data if string/bytes
            if isinstance(stix_data, (str, bytes)):
                if isinstance(stix_data, bytes):
                    stix_data = stix_data.decode('utf-8')
                stix_data = json.loads(stix_data)
            
            # Basic STIX 2.0 validation
            if not isinstance(stix_data, dict):
                return {
                    'valid': False,
                    'errors': ["STIX 2.0 data must be a JSON object"],
                    'warnings': [],
                    'detected_version': '2.0',
                    'converted_to_stix21': False
                }
            
            # Check spec_version
            if stix_data.get('spec_version') != '2.0':
                warnings.append(f"Expected spec_version '2.0', found '{stix_data.get('spec_version')}'")
            
            # Try to convert to STIX 2.1 and validate
            try:
                processed_data = self.version_handler.process_stix_data(stix_data)
                stix21_data = processed_data['stix_data']
                
                # Validate converted STIX 2.1 data
                if stix21_data.get('type') == 'bundle':
                    for obj in stix21_data.get('objects', []):
                        obj_validation = self.validate(obj)
                        errors.extend(obj_validation['errors'])
                        warnings.extend(obj_validation['warnings'])
                else:
                    validation_result = self.validate(stix21_data)
                    errors.extend(validation_result['errors'])
                    warnings.extend(validation_result['warnings'])
                
                # Add conversion notes as warnings
                warnings.extend(processed_data.get('conversion_notes', []))
                
                return {
                    'valid': len(errors) == 0,
                    'errors': errors,
                    'warnings': warnings,
                    'detected_version': '2.0',
                    'converted_to_stix21': True,
                    'conversion_notes': processed_data.get('conversion_notes', [])
                }
                
            except Exception as e:
                errors.append(f"Error converting STIX 2.0 to 2.1: {str(e)}")
                return {
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings,
                    'detected_version': '2.0',
                    'converted_to_stix21': False
                }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error validating STIX 2.0 data: {str(e)}"],
                'warnings': warnings,
                'detected_version': '2.0',
                'converted_to_stix21': False
            }