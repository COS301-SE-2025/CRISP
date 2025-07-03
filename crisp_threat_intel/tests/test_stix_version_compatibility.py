#!/usr/bin/env python3
"""
Comprehensive STIX 2.0 and 2.1 version compatibility unit tests.
Tests all aspects of STIX version handling, validation, and conversion.
"""

import os
import sys
import unittest
from datetime import datetime
import uuid

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')

import django
django.setup()

from crisp_threat_intel.factories.stix_factory import STIXObjectFactory
from crisp_threat_intel.validators.stix_validators import STIXValidator, STIXVersionConverter


class TestSTIXVersionCompatibility(unittest.TestCase):
    """Test STIX 2.0 and 2.1 version compatibility."""
    
    def setUp(self):
        """Set up test data."""
        self.test_timestamp = "2025-06-23T06:00:00.000Z"
        self.test_uuid = str(uuid.uuid4())
        
        # Base indicator data
        self.base_indicator_data = {
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity'],
            'name': 'Test Indicator'
        }
        
        # Base malware data
        self.base_malware_data = {
            'name': 'Test Malware',
            'malware_types': ['trojan'],
            'is_family': False
        }
        
        # Base attack pattern data
        self.base_attack_pattern_data = {
            'name': 'Test Attack Pattern',
            'description': 'Test attack pattern for version compatibility'
        }
        
        # Base identity data
        self.base_identity_data = {
            'name': 'Test Organization',
            'identity_class': 'organization'
        }
    
    def test_stix_20_indicator_creation(self):
        """Test creating STIX 2.0 indicator."""
        indicator = STIXObjectFactory.create_object('indicator', self.base_indicator_data, "2.0")
        
        # Basic structure assertions
        self.assertEqual(indicator['type'], 'indicator')
        self.assertEqual(indicator['spec_version'], '2.0')
        self.assertIn('pattern', indicator)
        self.assertIn('labels', indicator)
        
        # STIX 2.0 should not have pattern_type
        self.assertNotIn('pattern_type', indicator)
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(indicator, "2.0")
        self.assertTrue(is_valid, f"STIX 2.0 indicator validation failed: {errors}")
    
    def test_stix_21_indicator_creation(self):
        """Test creating STIX 2.1 indicator."""
        indicator = STIXObjectFactory.create_object('indicator', self.base_indicator_data, "2.1")
        
        # Basic structure assertions
        self.assertEqual(indicator['type'], 'indicator')
        self.assertEqual(indicator['spec_version'], '2.1')
        self.assertIn('pattern', indicator)
        self.assertIn('labels', indicator)
        self.assertIn('pattern_type', indicator)  # STIX 2.1 has pattern_type
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(indicator, "2.1")
        self.assertTrue(is_valid, f"STIX 2.1 indicator validation failed: {errors}")
    
    def test_stix_20_malware_creation(self):
        """Test creating STIX 2.0 malware."""
        # For STIX 2.0, provide labels instead of malware_types
        malware_data_20 = {
            'name': 'Test Malware',
            'labels': ['trojan']
        }
        
        malware = STIXObjectFactory.create_object('malware', malware_data_20, "2.0")
        
        # Basic structure assertions
        self.assertEqual(malware['type'], 'malware')
        self.assertEqual(malware['spec_version'], '2.0')
        self.assertIn('name', malware)
        self.assertIn('labels', malware)
        
        # STIX 2.0 should not have malware_types or is_family
        self.assertNotIn('malware_types', malware)
        self.assertNotIn('is_family', malware)
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(malware, "2.0")
        self.assertTrue(is_valid, f"STIX 2.0 malware validation failed: {errors}")
    
    def test_stix_21_malware_creation(self):
        """Test creating STIX 2.1 malware."""
        malware = STIXObjectFactory.create_object('malware', self.base_malware_data, "2.1")
        
        # Basic structure assertions
        self.assertEqual(malware['type'], 'malware')
        self.assertEqual(malware['spec_version'], '2.1')
        self.assertIn('name', malware)
        self.assertIn('malware_types', malware)
        self.assertIn('is_family', malware)
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(malware, "2.1")
        self.assertTrue(is_valid, f"STIX 2.1 malware validation failed: {errors}")
    
    def test_stix_20_attack_pattern_creation(self):
        """Test creating STIX 2.0 attack pattern."""
        attack_pattern = STIXObjectFactory.create_object('attack-pattern', self.base_attack_pattern_data, "2.0")
        
        # Basic structure assertions
        self.assertEqual(attack_pattern['type'], 'attack-pattern')
        self.assertEqual(attack_pattern['spec_version'], '2.0')
        self.assertIn('name', attack_pattern)
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(attack_pattern, "2.0")
        self.assertTrue(is_valid, f"STIX 2.0 attack pattern validation failed: {errors}")
    
    def test_stix_21_attack_pattern_creation(self):
        """Test creating STIX 2.1 attack pattern."""
        attack_pattern = STIXObjectFactory.create_object('attack-pattern', self.base_attack_pattern_data, "2.1")
        
        # Basic structure assertions
        self.assertEqual(attack_pattern['type'], 'attack-pattern')
        self.assertEqual(attack_pattern['spec_version'], '2.1')
        self.assertIn('name', attack_pattern)
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(attack_pattern, "2.1")
        self.assertTrue(is_valid, f"STIX 2.1 attack pattern validation failed: {errors}")
    
    def test_stix_20_identity_creation(self):
        """Test creating STIX 2.0 identity."""
        identity = STIXObjectFactory.create_object('identity', self.base_identity_data, "2.0")
        
        # Basic structure assertions
        self.assertEqual(identity['type'], 'identity')
        self.assertEqual(identity['spec_version'], '2.0')
        self.assertIn('name', identity)
        self.assertIn('identity_class', identity)
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(identity, "2.0")
        self.assertTrue(is_valid, f"STIX 2.0 identity validation failed: {errors}")
    
    def test_stix_21_identity_creation(self):
        """Test creating STIX 2.1 identity."""
        identity = STIXObjectFactory.create_object('identity', self.base_identity_data, "2.1")
        
        # Basic structure assertions
        self.assertEqual(identity['type'], 'identity')
        self.assertEqual(identity['spec_version'], '2.1')
        self.assertIn('name', identity)
        self.assertIn('identity_class', identity)
        
        # Validate with STIX validator
        is_valid, errors = STIXValidator.validate_stix_object(identity, "2.1")
        self.assertTrue(is_valid, f"STIX 2.1 identity validation failed: {errors}")
    
    def test_invalid_spec_version_rejection(self):
        """Test that invalid spec versions are rejected."""
        with self.assertRaises(ValueError):
            STIXObjectFactory.create_object('indicator', self.base_indicator_data, "1.0")
        
        with self.assertRaises(ValueError):
            STIXObjectFactory.create_object('indicator', self.base_indicator_data, "3.0")
        
        with self.assertRaises(ValueError):
            STIXObjectFactory.create_object('indicator', self.base_indicator_data, "2.2")
    
    def test_version_specific_field_differences(self):
        """Test that version-specific fields are handled correctly."""
        # Test indicator pattern_type differences
        indicator_20 = STIXObjectFactory.create_object('indicator', self.base_indicator_data, "2.0")
        indicator_21 = STIXObjectFactory.create_object('indicator', self.base_indicator_data, "2.1")
        
        self.assertNotIn('pattern_type', indicator_20)
        self.assertIn('pattern_type', indicator_21)
        
        # Test malware field differences
        malware_data_20 = {'name': 'Test Malware', 'labels': ['trojan']}
        malware_20 = STIXObjectFactory.create_object('malware', malware_data_20, "2.0")
        malware_21 = STIXObjectFactory.create_object('malware', self.base_malware_data, "2.1")
        
        self.assertNotIn('malware_types', malware_20)
        self.assertNotIn('is_family', malware_20)
        self.assertIn('malware_types', malware_21)
        self.assertIn('is_family', malware_21)
    
    def test_common_fields_across_versions(self):
        """Test that common fields are present in both versions."""
        for spec_version in ["2.0", "2.1"]:
            indicator = STIXObjectFactory.create_object('indicator', self.base_indicator_data, spec_version)
            
            # Common required fields
            self.assertIn('type', indicator)
            self.assertIn('id', indicator)
            self.assertIn('created', indicator)
            self.assertIn('modified', indicator)
            self.assertIn('pattern', indicator)
            self.assertIn('labels', indicator)
            
            # Version-specific spec_version field
            self.assertEqual(indicator['spec_version'], spec_version)


class TestSTIXValidator(unittest.TestCase):
    """Test comprehensive STIX validation."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_indicator_20 = {
            'type': 'indicator',
            'id': 'indicator--' + str(uuid.uuid4()),
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'pattern': "[domain-name:value = 'test.com']",
            'labels': ['malicious-activity']
        }
        
        self.valid_indicator_21 = {
            'type': 'indicator',
            'id': 'indicator--' + str(uuid.uuid4()),
            'spec_version': '2.1',
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'pattern': "[domain-name:value = 'test.com']",
            'pattern_type': 'stix',
            'valid_from': '2025-06-23T06:00:00.000Z',
            'labels': ['malicious-activity']
        }
    
    def test_valid_stix_20_validation(self):
        """Test validation of valid STIX 2.0 objects."""
        is_valid, errors = STIXValidator.validate_stix_object(self.valid_indicator_20, "2.0")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_valid_stix_21_validation(self):
        """Test validation of valid STIX 2.1 objects."""
        is_valid, errors = STIXValidator.validate_stix_object(self.valid_indicator_21, "2.1")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_missing_required_fields_validation(self):
        """Test validation fails for missing required fields."""
        invalid_indicator = self.valid_indicator_21.copy()
        del invalid_indicator['pattern']
        
        is_valid, errors = STIXValidator.validate_stix_object(invalid_indicator, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('pattern' in error for error in errors))
    
    def test_invalid_stix_id_validation(self):
        """Test validation fails for invalid STIX IDs."""
        invalid_indicator = self.valid_indicator_21.copy()
        invalid_indicator['id'] = 'invalid-id'
        
        is_valid, errors = STIXValidator.validate_stix_object(invalid_indicator, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid STIX ID' in error for error in errors))
    
    def test_invalid_timestamp_validation(self):
        """Test validation fails for invalid timestamps."""
        invalid_indicator = self.valid_indicator_21.copy()
        invalid_indicator['created'] = 'invalid-timestamp'
        
        is_valid, errors = STIXValidator.validate_stix_object(invalid_indicator, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('timestamp' in error for error in errors))
    
    def test_cross_field_validation(self):
        """Test cross-field validation rules."""
        invalid_indicator = self.valid_indicator_21.copy()
        invalid_indicator['created'] = '2025-06-24T06:00:00.000Z'
        invalid_indicator['modified'] = '2025-06-23T06:00:00.000Z'  # Earlier than created
        
        is_valid, errors = STIXValidator.validate_stix_object(invalid_indicator, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('Created timestamp cannot be later than modified' in error for error in errors))
    
    def test_version_specific_validation(self):
        """Test version-specific validation rules."""
        # Test STIX 2.0 object with spec_version field (should be allowed)
        indicator_20_with_spec = self.valid_indicator_20.copy()
        indicator_20_with_spec['spec_version'] = '2.0'
        
        is_valid, errors = STIXValidator.validate_stix_object(indicator_20_with_spec, "2.0")
        self.assertTrue(is_valid)  # Should be valid with correct spec_version
        
        # Test STIX 2.1 object without spec_version (should fail)
        indicator_21_no_spec = self.valid_indicator_21.copy()
        del indicator_21_no_spec['spec_version']
        
        is_valid, errors = STIXValidator.validate_stix_object(indicator_21_no_spec, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('spec_version' in error for error in errors))
    
    def test_malware_type_validation(self):
        """Test malware-specific validation."""
        valid_malware_21 = {
            'type': 'malware',
            'id': 'malware--' + str(uuid.uuid4()),
            'spec_version': '2.1',
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'name': 'Test Malware',
            'malware_types': ['trojan'],
            'is_family': False
        }
        
        is_valid, errors = STIXValidator.validate_stix_object(valid_malware_21, "2.1")
        self.assertTrue(is_valid)
        
        # Test invalid malware type
        invalid_malware = valid_malware_21.copy()
        invalid_malware['malware_types'] = ['invalid-type']
        
        is_valid, errors = STIXValidator.validate_stix_object(invalid_malware, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid malware_types' in error for error in errors))
    
    def test_bundle_validation(self):
        """Test STIX bundle validation."""
        valid_bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': [self.valid_indicator_21]
        }
        
        is_valid, errors = STIXValidator.validate_stix_bundle(valid_bundle, "2.1")
        self.assertTrue(is_valid)
        
        # Test bundle with invalid object
        invalid_bundle = valid_bundle.copy()
        invalid_obj = self.valid_indicator_21.copy()
        del invalid_obj['pattern']
        invalid_bundle['objects'] = [invalid_obj]
        
        is_valid, errors = STIXValidator.validate_stix_bundle(invalid_bundle, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('Object 0' in error for error in errors))
    
    def test_validation_summary(self):
        """Test validation summary generation."""
        summary = STIXValidator.get_validation_summary(self.valid_indicator_21, "2.1")
        
        self.assertTrue(summary['is_valid'])
        self.assertEqual(summary['spec_version'], '2.1')
        self.assertEqual(summary['object_type'], 'indicator')
        self.assertEqual(summary['object_count'], 1)
        self.assertEqual(summary['error_count'], 0)
        self.assertIn('validation_timestamp', summary)


class TestSTIXVersionConverter(unittest.TestCase):
    """Test STIX version conversion functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.stix_20_indicator = {
            'type': 'indicator',
            'id': 'indicator--' + str(uuid.uuid4()),
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'pattern': "[domain-name:value = 'test.com']",
            'labels': ['malicious-activity']
        }
        
        self.stix_21_indicator = {
            'type': 'indicator',
            'id': 'indicator--' + str(uuid.uuid4()),
            'spec_version': '2.1',
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'pattern': "[domain-name:value = 'test.com']",
            'pattern_type': 'stix',
            'valid_from': '2025-06-23T06:00:00.000Z',
            'labels': ['malicious-activity']
        }
        
        self.stix_20_malware = {
            'type': 'malware',
            'id': 'malware--' + str(uuid.uuid4()),
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'name': 'Test Malware',
            'labels': ['trojan']
        }
        
        self.stix_21_malware = {
            'type': 'malware',
            'id': 'malware--' + str(uuid.uuid4()),
            'spec_version': '2.1',
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'name': 'Test Malware',
            'malware_types': ['trojan'],
            'is_family': False
        }
    
    def test_convert_indicator_20_to_21(self):
        """Test converting STIX 2.0 indicator to 2.1."""
        converted = STIXVersionConverter.convert_to_21(self.stix_20_indicator)
        
        # Should have added spec_version
        self.assertEqual(converted['spec_version'], '2.1')
        
        # Should have added pattern_type
        self.assertIn('pattern_type', converted)
        self.assertEqual(converted['pattern_type'], 'stix')
        
        # Should have added valid_from
        self.assertIn('valid_from', converted)
        self.assertEqual(converted['valid_from'], converted['created'])
        
        # Should validate as STIX 2.1
        is_valid, errors = STIXValidator.validate_stix_object(converted, "2.1")
        self.assertTrue(is_valid, f"Converted indicator validation failed: {errors}")
    
    def test_convert_indicator_21_to_20(self):
        """Test converting STIX 2.1 indicator to 2.0."""
        converted = STIXVersionConverter.convert_to_20(self.stix_21_indicator)
        
        # Should have removed spec_version
        self.assertNotIn('spec_version', converted)
        
        # Should have removed pattern_type
        self.assertNotIn('pattern_type', converted)
        
        # Should have removed valid_from
        self.assertNotIn('valid_from', converted)
        
        # Should validate as STIX 2.0
        is_valid, errors = STIXValidator.validate_stix_object(converted, "2.0")
        self.assertTrue(is_valid, f"Converted indicator validation failed: {errors}")
    
    def test_convert_malware_20_to_21(self):
        """Test converting STIX 2.0 malware to 2.1."""
        converted = STIXVersionConverter.convert_to_21(self.stix_20_malware)
        
        # Should have added spec_version
        self.assertEqual(converted['spec_version'], '2.1')
        
        # Should have converted labels to malware_types
        self.assertIn('malware_types', converted)
        self.assertEqual(converted['malware_types'], ['trojan'])
        
        # Should have added is_family
        self.assertIn('is_family', converted)
        self.assertEqual(converted['is_family'], False)
        
        # Should validate as STIX 2.1
        is_valid, errors = STIXValidator.validate_stix_object(converted, "2.1")
        self.assertTrue(is_valid, f"Converted malware validation failed: {errors}")
    
    def test_convert_malware_21_to_20(self):
        """Test converting STIX 2.1 malware to 2.0."""
        converted = STIXVersionConverter.convert_to_20(self.stix_21_malware)
        
        # Should have removed spec_version
        self.assertNotIn('spec_version', converted)
        
        # Should have converted malware_types to labels
        self.assertIn('labels', converted)
        self.assertEqual(converted['labels'], ['trojan'])
        
        # Should have removed malware_types and is_family
        self.assertNotIn('malware_types', converted)
        self.assertNotIn('is_family', converted)
        
        # Should validate as STIX 2.0
        is_valid, errors = STIXValidator.validate_stix_object(converted, "2.0")
        self.assertTrue(is_valid, f"Converted malware validation failed: {errors}")
    
    def test_round_trip_conversion(self):
        """Test that round-trip conversion maintains essential data."""
        # 2.0 -> 2.1 -> 2.0
        converted_to_21 = STIXVersionConverter.convert_to_21(self.stix_20_indicator)
        converted_back_to_20 = STIXVersionConverter.convert_to_20(converted_to_21)
        
        # Essential fields should be preserved
        self.assertEqual(converted_back_to_20['type'], self.stix_20_indicator['type'])
        self.assertEqual(converted_back_to_20['id'], self.stix_20_indicator['id'])
        self.assertEqual(converted_back_to_20['pattern'], self.stix_20_indicator['pattern'])
        self.assertEqual(converted_back_to_20['labels'], self.stix_20_indicator['labels'])
        
        # 2.1 -> 2.0 -> 2.1
        converted_to_20 = STIXVersionConverter.convert_to_20(self.stix_21_indicator)
        converted_back_to_21 = STIXVersionConverter.convert_to_21(converted_to_20)
        
        # Essential fields should be preserved
        self.assertEqual(converted_back_to_21['type'], self.stix_21_indicator['type'])
        self.assertEqual(converted_back_to_21['id'], self.stix_21_indicator['id'])
        self.assertEqual(converted_back_to_21['pattern'], self.stix_21_indicator['pattern'])
        self.assertEqual(converted_back_to_21['labels'], self.stix_21_indicator['labels'])


class TestSTIXVersionEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for STIX version handling."""
    
    def test_empty_object_validation(self):
        """Test validation of empty objects."""
        empty_obj = {}
        
        is_valid, errors = STIXValidator.validate_stix_object(empty_obj, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)
    
    def test_non_dict_object_validation(self):
        """Test validation of non-dictionary objects."""
        non_dict = "not a dictionary"
        
        is_valid, errors = STIXValidator.validate_stix_object(non_dict, "2.1")
        self.assertFalse(is_valid)
        self.assertIn("must be a dictionary", errors[0])
    
    def test_unsupported_stix_type_validation(self):
        """Test validation of unsupported STIX types."""
        invalid_obj = {
            'type': 'unsupported-type',
            'id': 'unsupported-type--' + str(uuid.uuid4()),
            'spec_version': '2.1',
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z'
        }
        
        is_valid, errors = STIXValidator.validate_stix_object(invalid_obj, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid STIX type' in error for error in errors))
    
    def test_malformed_stix_id_validation(self):
        """Test validation of various malformed STIX IDs."""
        malformed_ids = [
            'indicator-missing-dashes',
            'indicator--not-a-uuid',
            'wrong-type--' + str(uuid.uuid4()),
            'indicator--' + str(uuid.uuid4()).upper(),  # Uppercase UUID
            '',
            None
        ]
        
        for malformed_id in malformed_ids:
            test_obj = {
                'type': 'indicator',
                'id': malformed_id,
                'spec_version': '2.1',
                'created': '2025-06-23T06:00:00.000Z',
                'modified': '2025-06-23T06:00:00.000Z',
                'pattern': "[domain-name:value = 'test.com']",
                'pattern_type': 'stix',
                'valid_from': '2025-06-23T06:00:00.000Z',
                'labels': ['malicious-activity']
            }
            
            is_valid, errors = STIXValidator.validate_stix_object(test_obj, "2.1")
            self.assertFalse(is_valid, f"Should have failed for ID: {malformed_id}")
    
    def test_invalid_confidence_values(self):
        """Test validation of invalid confidence values."""
        invalid_confidences = [-1, 101, 'high', None, [50]]
        
        for confidence in invalid_confidences:
            test_obj = {
                'type': 'indicator',
                'id': 'indicator--' + str(uuid.uuid4()),
                'spec_version': '2.1',
                'created': '2025-06-23T06:00:00.000Z',
                'modified': '2025-06-23T06:00:00.000Z',
                'pattern': "[domain-name:value = 'test.com']",
                'pattern_type': 'stix',
                'valid_from': '2025-06-23T06:00:00.000Z',
                'labels': ['malicious-activity'],
                'confidence': confidence
            }
            
            is_valid, errors = STIXValidator.validate_stix_object(test_obj, "2.1")
            self.assertFalse(is_valid, f"Should have failed for confidence: {confidence}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)