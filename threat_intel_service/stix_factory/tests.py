import json
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from .version_handler import (
    STIXVersionDetector, 
    STIXVersionConverter, 
    STIXVersionHandler, 
    STIXVersion
)
from .validators import STIXValidator
from .factory import STIXObjectFactoryRegistry
import stix2

class STIXVersionDetectorTests(TestCase):
    """Test STIX version detection capabilities."""
    
    def setUp(self):
        self.detector = STIXVersionDetector()
    
    def test_detect_stix21_json(self):
        """Test detection of STIX 2.1 JSON objects."""
        stix21_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "pattern_type": "stix",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        version = self.detector.detect_version(stix21_indicator)
        self.assertEqual(version, STIXVersion.STIX_2_1)
        
        # Test JSON string
        json_string = json.dumps(stix21_indicator)
        version = self.detector.detect_version(json_string)
        self.assertEqual(version, STIXVersion.STIX_2_1)
    
    def test_detect_stix20_json(self):
        """Test detection of STIX 2.0 JSON objects."""
        stix20_indicator = {
            "type": "indicator",
            "spec_version": "2.0",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        version = self.detector.detect_version(stix20_indicator)
        self.assertEqual(version, STIXVersion.STIX_2_0)
    
    def test_detect_stix21_bundle(self):
        """Test detection of STIX 2.1 bundles."""
        stix21_bundle = {
            "type": "bundle",
            "id": "bundle--12345678-1234-5678-9abc-123456789012",
            "spec_version": "2.1",
            "objects": [
                {
                    "type": "indicator",
                    "spec_version": "2.1",
                    "id": "indicator--87654321-4321-8765-cba9-210987654321",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
                    "pattern_type": "stix",
                    "valid_from": "2023-01-01T00:00:00.000Z",
                    "labels": ["malicious-activity"]
                }
            ]
        }
        
        version = self.detector.detect_version(stix21_bundle)
        self.assertEqual(version, STIXVersion.STIX_2_1)
    
    def test_detect_stix1x_xml(self):
        """Test detection of STIX 1.x XML."""
        stix1x_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <stix:STIX_Package
            xmlns:stix="http://stix.mitre.org/stix-1"
            xmlns:stixCommon="http://stix.mitre.org/common-1"
            xmlns:indicator="http://stix.mitre.org/Indicator-2"
            version="1.2">
            <stix:Indicators>
                <stix:Indicator>
                    <indicator:Title>Test Indicator</indicator:Title>
                    <indicator:Description>Test STIX 1.x indicator</indicator:Description>
                </stix:Indicator>
            </stix:Indicators>
        </stix:STIX_Package>'''
        
        version = self.detector.detect_version(stix1x_xml)
        self.assertEqual(version, STIXVersion.STIX_1_2)
    
    def test_detect_unknown_format(self):
        """Test detection of unknown/invalid formats."""
        invalid_data = "This is not STIX data"
        version = self.detector.detect_version(invalid_data)
        self.assertEqual(version, STIXVersion.UNKNOWN)
        
        empty_dict = {}
        version = self.detector.detect_version(empty_dict)
        self.assertEqual(version, STIXVersion.UNKNOWN)

class STIXVersionConverterTests(TestCase):
    """Test STIX version conversion capabilities."""
    
    def setUp(self):
        self.converter = STIXVersionConverter()
    
    def test_convert_stix20_to_stix21(self):
        """Test conversion from STIX 2.0 to STIX 2.1."""
        stix20_indicator = {
            "type": "indicator",
            "spec_version": "2.0",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        converted = self.converter.convert_to_stix21(stix20_indicator, STIXVersion.STIX_2_0)
        
        self.assertEqual(converted['spec_version'], '2.1')
        self.assertEqual(converted['type'], 'indicator')
        self.assertEqual(converted['pattern_type'], 'stix')  # Should be added for 2.1
    
    def test_convert_stix20_malware_to_stix21(self):
        """Test conversion of STIX 2.0 malware to STIX 2.1."""
        stix20_malware = {
            "type": "malware",
            "spec_version": "2.0",
            "id": "malware--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "name": "Test Malware",
            "labels": ["trojan"]
        }
        
        converted = self.converter.convert_to_stix21(stix20_malware, STIXVersion.STIX_2_0)
        
        self.assertEqual(converted['spec_version'], '2.1')
        self.assertEqual(converted['type'], 'malware')
        self.assertTrue('is_family' in converted)  # Should be added for 2.1
    
    @patch('threat_intel_service.stix_factory.version_handler.xmltodict.parse')
    def test_convert_stix1x_to_stix21(self, mock_parse):
        """Test conversion from STIX 1.x to STIX 2.1."""
        # Mock XML parsing result
        mock_parse.return_value = {
            'stix:STIX_Package': {
                'stix:Indicators': {
                    'stix:Indicator': {
                        'indicator:Title': 'Test Indicator',
                        'indicator:Description': 'Test STIX 1.x indicator',
                        '@timestamp': '2023-01-01T00:00:00.000Z',
                        'indicator:Observable': {
                            'cybox:Object': {
                                'FileObj:File': {
                                    'FileObj:Hashes': {
                                        'Common:Hash': {
                                            'Common:Simple_Hash_Value': 'd41d8cd98f00b204e9800998ecf8427e',
                                            'Common:Type': 'MD5'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stix1x_xml = '''<?xml version="1.0"?>
        <stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1">
        </stix:STIX_Package>'''
        
        converted = self.converter.convert_to_stix21(stix1x_xml, STIXVersion.STIX_1_2)
        
        self.assertEqual(converted['type'], 'bundle')
        self.assertEqual(converted['spec_version'], '2.1')
        self.assertTrue('objects' in converted)
        self.assertTrue(len(converted['objects']) > 0)
        
        # Check first converted object
        first_obj = converted['objects'][0]
        self.assertEqual(first_obj['type'], 'indicator')
        self.assertEqual(first_obj['spec_version'], '2.1')

class STIXVersionHandlerTests(TestCase):
    """Test complete STIX version handling workflow."""
    
    def setUp(self):
        self.handler = STIXVersionHandler()
    
    def test_process_stix21_data(self):
        """Test processing of STIX 2.1 data."""
        stix21_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "pattern_type": "stix",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        result = self.handler.process_stix_data(stix21_indicator)
        
        self.assertEqual(result['original_version'], '2.1')
        self.assertEqual(result['converted_version'], '2.1')
        self.assertEqual(result['stix_data'], stix21_indicator)
    
    def test_process_stix20_data(self):
        """Test processing of STIX 2.0 data."""
        stix20_indicator = {
            "type": "indicator",
            "spec_version": "2.0",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        result = self.handler.process_stix_data(stix20_indicator)
        
        self.assertEqual(result['original_version'], '2.0')
        self.assertEqual(result['converted_version'], '2.1')
        self.assertEqual(result['stix_data']['spec_version'], '2.1')
    
    def test_process_invalid_data(self):
        """Test processing of invalid data."""
        invalid_data = "This is not STIX data"
        
        with self.assertRaises(ValueError) as context:
            self.handler.process_stix_data(invalid_data)
        
        self.assertIn("Unable to detect STIX version", str(context.exception))

class STIXValidatorTests(TestCase):
    """Test multi-version STIX validation."""
    
    def setUp(self):
        self.validator = STIXValidator()
    
    def test_validate_stix21_indicator(self):
        """Test validation of STIX 2.1 indicator."""
        stix21_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "pattern_type": "stix",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        result = self.validator.validate_multi_version(stix21_indicator)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['detected_version'], '2.1')
        self.assertFalse(result['converted_to_stix21'])
    
    def test_validate_stix20_indicator(self):
        """Test validation of STIX 2.0 indicator."""
        stix20_indicator = {
            "type": "indicator",
            "spec_version": "2.0",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        result = self.validator.validate_multi_version(stix20_indicator)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['detected_version'], '2.0')
        self.assertTrue(result['converted_to_stix21'])
    
    def test_validate_invalid_stix21(self):
        """Test validation of invalid STIX 2.1 object."""
        invalid_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "invalid-id-format",  # Invalid ID format
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            # Missing required pattern field
            "pattern_type": "stix",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        result = self.validator.validate_multi_version(invalid_indicator)
        
        self.assertFalse(result['valid'])
        self.assertTrue(len(result['errors']) > 0)
        self.assertEqual(result['detected_version'], '2.1')

class STIXFactoryIntegrationTests(TestCase):
    """Test integration between factory and version handling."""
    
    def setUp(self):
        self.factory_registry = STIXObjectFactoryRegistry()
    
    def test_process_stix21_input(self):
        """Test processing STIX 2.1 input through factory."""
        stix21_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "pattern_type": "stix",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        result = self.factory_registry.process_stix_input(stix21_indicator)
        
        self.assertEqual(result['original_version'], '2.1')
        self.assertEqual(result['total_objects'], 1)
        self.assertTrue(len(result['objects']) > 0)
        
        # Check created object
        created_obj = result['objects'][0]
        self.assertIsInstance(created_obj, stix2.v21.Indicator)
    
    def test_process_stix20_input(self):
        """Test processing STIX 2.0 input through factory."""
        stix20_malware = {
            "type": "malware",
            "spec_version": "2.0",
            "id": "malware--12345678-1234-5678-9abc-123456789012",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "name": "Test Malware",
            "labels": ["trojan"]
        }
        
        result = self.factory_registry.process_stix_input(stix20_malware)
        
        self.assertEqual(result['original_version'], '2.0')
        self.assertEqual(result['total_objects'], 1)
        self.assertTrue(len(result['objects']) > 0)
        
        # Check created object
        created_obj = result['objects'][0]
        self.assertIsInstance(created_obj, stix2.v21.Malware)
        self.assertTrue(hasattr(created_obj, 'is_family'))  # Should have 2.1 field
    
    def test_process_bundle_input(self):
        """Test processing STIX bundle input."""
        stix21_bundle = {
            "type": "bundle",
            "id": "bundle--12345678-1234-5678-9abc-123456789012",
            "spec_version": "2.1",
            "objects": [
                {
                    "type": "indicator",
                    "spec_version": "2.1",
                    "id": "indicator--87654321-4321-8765-cba9-210987654321",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
                    "pattern_type": "stix",
                    "valid_from": "2023-01-01T00:00:00.000Z",
                    "labels": ["malicious-activity"]
                },
                {
                    "type": "malware",
                    "spec_version": "2.1",
                    "id": "malware--11111111-2222-3333-4444-555555555555",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "name": "Test Malware",
                    "is_family": True,
                    "malware_types": ["trojan"]
                }
            ]
        }
        
        result = self.factory_registry.process_stix_input(stix21_bundle)
        
        self.assertEqual(result['original_version'], '2.1')
        self.assertEqual(result['total_objects'], 2)
        self.assertEqual(len(result['objects']), 2)
        
        # Check object types
        object_types = [obj.type for obj in result['objects']]
        self.assertIn('indicator', object_types)
        self.assertIn('malware', object_types)
    
    def test_create_stix_bundle(self):
        """Test creating STIX bundle from objects."""
        # Create some test objects first
        indicator_data = {
            "type": "indicator",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "pattern_type": "stix",
            "valid_from": "2023-01-01T00:00:00.000Z",
            "labels": ["malicious-activity"]
        }
        
        malware_data = {
            "type": "malware",
            "name": "Test Malware",
            "is_family": True,
            "malware_types": ["trojan"]
        }
        
        indicator = self.factory_registry.create_object(indicator_data)
        malware = self.factory_registry.create_object(malware_data)
        
        # Create bundle
        bundle = self.factory_registry.create_stix_bundle([indicator, malware])
        
        self.assertIsInstance(bundle, stix2.v21.Bundle)
        self.assertEqual(bundle.spec_version, '2.1')
        self.assertEqual(len(bundle.objects), 2)

class STIXVersionCompatibilityEndToEndTests(TestCase):
    """End-to-end tests for complete STIX version compatibility."""
    
    def setUp(self):
        self.factory_registry = STIXObjectFactoryRegistry()
        self.validator = STIXValidator()
    
    def test_full_workflow_stix20_to_stix21(self):
        """Test complete workflow from STIX 2.0 input to validated STIX 2.1 output."""
        # Input STIX 2.0 data
        stix20_bundle = {
            "type": "bundle",
            "id": "bundle--12345678-1234-5678-9abc-123456789012",
            "spec_version": "2.0",
            "objects": [
                {
                    "type": "indicator",
                    "spec_version": "2.0",
                    "id": "indicator--87654321-4321-8765-cba9-210987654321",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
                    "valid_from": "2023-01-01T00:00:00.000Z",
                    "labels": ["malicious-activity"]
                },
                {
                    "type": "malware",
                    "spec_version": "2.0",
                    "id": "malware--11111111-2222-3333-4444-555555555555",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "name": "Test Malware",
                    "labels": ["trojan"]
                }
            ]
        }
        
        # Step 1: Validate input
        validation_result = self.validator.validate_multi_version(stix20_bundle)
        self.assertTrue(validation_result['valid'])
        self.assertEqual(validation_result['detected_version'], '2.0')
        self.assertTrue(validation_result['converted_to_stix21'])
        
        # Step 2: Process through factory
        processing_result = self.factory_registry.process_stix_input(stix20_bundle)
        self.assertEqual(processing_result['original_version'], '2.0')
        self.assertEqual(processing_result['total_objects'], 2)
        
        # Step 3: Verify all objects are STIX 2.1
        for obj in processing_result['objects']:
            self.assertEqual(obj.spec_version, '2.1')
        
        # Step 4: Create new bundle and verify
        new_bundle = self.factory_registry.create_stix_bundle(processing_result['objects'])
        self.assertEqual(new_bundle.spec_version, '2.1')
        
        # Step 5: Final validation of new bundle
        final_validation = self.validator.validate_multi_version(json.loads(new_bundle.serialize()))
        self.assertTrue(final_validation['valid'])
        self.assertEqual(final_validation['detected_version'], '2.1')
    
    def test_error_handling_invalid_data(self):
        """Test error handling for invalid data throughout the workflow."""
        invalid_data = "This is completely invalid STIX data"
        
        # Validation should catch this
        validation_result = self.validator.validate_multi_version(invalid_data)
        self.assertFalse(validation_result['valid'])
        self.assertEqual(validation_result['detected_version'], 'unknown')
        
        # Factory processing should raise an exception
        with self.assertRaises(ValueError):
            self.factory_registry.process_stix_input(invalid_data)
    
    def test_partial_success_bundle_processing(self):
        """Test handling of bundles with some valid and some invalid objects."""
        mixed_bundle = {
            "type": "bundle",
            "id": "bundle--12345678-1234-5678-9abc-123456789012",
            "spec_version": "2.1",
            "objects": [
                {
                    "type": "indicator",
                    "spec_version": "2.1",
                    "id": "indicator--87654321-4321-8765-cba9-210987654321",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
                    "pattern_type": "stix",
                    "valid_from": "2023-01-01T00:00:00.000Z",
                    "labels": ["malicious-activity"]
                },
                {
                    "type": "invalid-type",  # Invalid type
                    "spec_version": "2.1",
                    "id": "invalid--11111111-2222-3333-4444-555555555555",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z"
                }
            ]
        }
        
        # Should process valid objects and skip invalid ones
        result = self.factory_registry.process_stix_input(mixed_bundle)
        
        # Should have processed only the valid indicator
        self.assertEqual(result['total_objects'], 1)
        self.assertEqual(result['objects'][0].type, 'indicator')

if __name__ == '__main__':
    unittest.main()