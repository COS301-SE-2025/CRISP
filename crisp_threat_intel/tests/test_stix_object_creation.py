#!/usr/bin/env python3
"""
Comprehensive STIX object creation and validation unit tests.
Tests all aspects of STIX object factory patterns and creation logic.
"""

import os
import sys
import unittest
from datetime import datetime
import uuid
import json

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')

import django
django.setup()

from crisp_threat_intel.factories.stix_factory import (
    STIXObjectFactory,
    StixIndicatorCreator,
    StixTTPCreator,
    StixMalwareCreator,
    StixIdentityCreator,
    create_indicator,
    create_attack_pattern,
    create_malware,
    create_identity
)
from crisp_threat_intel.validators.stix_validators import STIXValidator


class TestSTIXObjectFactory(unittest.TestCase):
    """Test the main STIX object factory."""
    
    def test_factory_supported_types(self):
        """Test that factory reports correct supported types."""
        supported_types = STIXObjectFactory.get_supported_types()
        expected_types = ['indicator', 'attack-pattern', 'malware', 'identity']
        
        self.assertEqual(set(supported_types), set(expected_types))
    
    def test_factory_unsupported_type_error(self):
        """Test that factory raises error for unsupported types."""
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('unsupported-type', {})
        
        self.assertIn('Unsupported STIX object type', str(context.exception))
    
    def test_factory_creator_registration(self):
        """Test that new creators can be registered."""
        class TestCreator(StixIndicatorCreator):
            pass
        
        # Register new creator
        STIXObjectFactory.register_creator('test-type', TestCreator)
        
        try:
            # Should now be in supported types
            self.assertIn('test-type', STIXObjectFactory.get_supported_types())
            
            # Should be able to create objects of this type
            test_data = {
                'pattern': "[domain-name:value = 'test.com']",
                'labels': ['test']
            }
            obj = STIXObjectFactory.create_object('test-type', test_data)
            self.assertEqual(obj['type'], 'indicator')  # Since it inherits from indicator creator
        finally:
            # Clean up registered type
            STIXObjectFactory.unregister_creator('test-type')
    
    def test_factory_invalid_creator_registration(self):
        """Test that invalid creators cannot be registered."""
        class InvalidCreator:
            pass
        
        with self.assertRaises(ValueError):
            STIXObjectFactory.register_creator('invalid-type', InvalidCreator)


class TestSTIXIndicatorCreation(unittest.TestCase):
    """Test STIX Indicator object creation."""
    
    def setUp(self):
        """Set up test data."""
        self.base_indicator_data = {
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity'],
            'name': 'Test Indicator',
            'description': 'Test indicator for unit testing'
        }
    
    def test_basic_indicator_creation_21(self):
        """Test basic STIX 2.1 indicator creation."""
        indicator = STIXObjectFactory.create_object('indicator', self.base_indicator_data, "2.1")
        
        # Check required fields
        self.assertEqual(indicator['type'], 'indicator')
        self.assertEqual(indicator['spec_version'], '2.1')
        self.assertIn('id', indicator)
        self.assertIn('created', indicator)
        self.assertIn('modified', indicator)
        self.assertEqual(indicator['pattern'], self.base_indicator_data['pattern'])
        self.assertEqual(indicator['labels'], self.base_indicator_data['labels'])
        self.assertEqual(indicator['pattern_type'], 'stix')  # Default for 2.1
        
        # Check optional fields
        self.assertEqual(indicator['name'], self.base_indicator_data['name'])
        self.assertEqual(indicator['description'], self.base_indicator_data['description'])
        
        # Validate STIX ID format
        self.assertTrue(indicator['id'].startswith('indicator--'))
        self.assertEqual(len(indicator['id'].split('--')[1]), 36)  # UUID length
    
    def test_basic_indicator_creation_20(self):
        """Test basic STIX 2.0 indicator creation."""
        indicator = STIXObjectFactory.create_object('indicator', self.base_indicator_data, "2.0")
        
        # Check required fields
        self.assertEqual(indicator['type'], 'indicator')
        self.assertEqual(indicator['spec_version'], '2.0')
        self.assertNotIn('pattern_type', indicator)  # Not in STIX 2.0
        
        # Check that pattern and labels are present
        self.assertEqual(indicator['pattern'], self.base_indicator_data['pattern'])
        self.assertEqual(indicator['labels'], self.base_indicator_data['labels'])
    
    def test_indicator_with_all_optional_fields(self):
        """Test indicator creation with all optional fields."""
        extended_data = self.base_indicator_data.copy()
        extended_data.update({
            'confidence': 85,
            'pattern_type': 'sigma',
            'valid_from': '2025-06-23T06:00:00.000Z',
            'external_references': [
                {
                    'source_name': 'test-source',
                    'url': 'https://example.com/reference'
                }
            ],
            'kill_chain_phases': [
                {
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': 'reconnaissance'
                }
            ],
            'created_by_ref': 'identity--' + str(uuid.uuid4())
        })
        
        indicator = STIXObjectFactory.create_object('indicator', extended_data, "2.1")
        
        # Check all optional fields are present
        self.assertEqual(indicator['confidence'], 85)
        self.assertEqual(indicator['pattern_type'], 'sigma')
        self.assertEqual(indicator['valid_from'], extended_data['valid_from'])
        self.assertEqual(indicator['external_references'], extended_data['external_references'])
        self.assertEqual(indicator['kill_chain_phases'], extended_data['kill_chain_phases'])
        self.assertEqual(indicator['created_by_ref'], extended_data['created_by_ref'])
    
    def test_indicator_missing_required_pattern(self):
        """Test that indicator creation fails without pattern."""
        invalid_data = self.base_indicator_data.copy()
        del invalid_data['pattern']
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('indicator', invalid_data)
        
        self.assertIn('pattern', str(context.exception))
    
    def test_indicator_missing_required_labels(self):
        """Test that indicator creation fails without labels."""
        invalid_data = self.base_indicator_data.copy()
        del invalid_data['labels']
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('indicator', invalid_data)
        
        self.assertIn('labels', str(context.exception))
    
    def test_indicator_empty_pattern(self):
        """Test that indicator creation fails with empty pattern."""
        invalid_data = self.base_indicator_data.copy()
        invalid_data['pattern'] = ''
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('indicator', invalid_data)
        
        self.assertIn('pattern', str(context.exception))
    
    def test_indicator_empty_labels(self):
        """Test that indicator creation fails with empty labels."""
        invalid_data = self.base_indicator_data.copy()
        invalid_data['labels'] = []
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('indicator', invalid_data)
        
        self.assertIn('labels', str(context.exception))
    
    def test_indicator_convenience_function(self):
        """Test the convenience function for indicator creation."""
        indicator = create_indicator(self.base_indicator_data, "2.1")
        
        self.assertEqual(indicator['type'], 'indicator')
        self.assertEqual(indicator['spec_version'], '2.1')
        self.assertEqual(indicator['pattern'], self.base_indicator_data['pattern'])


class TestSTIXMalwareCreation(unittest.TestCase):
    """Test STIX Malware object creation."""
    
    def setUp(self):
        """Set up test data."""
        self.base_malware_data_21 = {
            'name': 'Test Malware',
            'malware_types': ['trojan', 'backdoor'],
            'is_family': False,
            'description': 'Test malware for unit testing'
        }
        
        self.base_malware_data_20 = {
            'name': 'Test Malware',
            'labels': ['trojan', 'backdoor'],
            'description': 'Test malware for unit testing'
        }
    
    def test_basic_malware_creation_21(self):
        """Test basic STIX 2.1 malware creation."""
        malware = STIXObjectFactory.create_object('malware', self.base_malware_data_21, "2.1")
        
        # Check required fields
        self.assertEqual(malware['type'], 'malware')
        self.assertEqual(malware['spec_version'], '2.1')
        self.assertIn('id', malware)
        self.assertIn('created', malware)
        self.assertIn('modified', malware)
        self.assertEqual(malware['name'], self.base_malware_data_21['name'])
        self.assertEqual(malware['malware_types'], self.base_malware_data_21['malware_types'])
        self.assertEqual(malware['is_family'], self.base_malware_data_21['is_family'])
        
        # Check optional fields
        self.assertEqual(malware['description'], self.base_malware_data_21['description'])
        
        # Validate STIX ID format
        self.assertTrue(malware['id'].startswith('malware--'))
    
    def test_basic_malware_creation_20(self):
        """Test basic STIX 2.0 malware creation."""
        malware = STIXObjectFactory.create_object('malware', self.base_malware_data_20, "2.0")
        
        # Check required fields
        self.assertEqual(malware['type'], 'malware')
        self.assertEqual(malware['spec_version'], '2.0')
        self.assertEqual(malware['name'], self.base_malware_data_20['name'])
        
        # STIX 2.0 should convert malware_types to labels if present
        self.assertNotIn('malware_types', malware)
        self.assertNotIn('is_family', malware)
    
    def test_malware_21_to_20_conversion(self):
        """Test that STIX 2.1 malware data converts properly to 2.0."""
        # Pass 2.1 style data to 2.0 creation
        malware = STIXObjectFactory.create_object('malware', self.base_malware_data_21, "2.0")
        
        # Should have converted malware_types to labels
        self.assertIn('labels', malware)
        self.assertEqual(malware['labels'], self.base_malware_data_21['malware_types'])
        self.assertNotIn('malware_types', malware)
        self.assertNotIn('is_family', malware)
    
    def test_malware_with_all_optional_fields(self):
        """Test malware creation with all optional fields."""
        extended_data = self.base_malware_data_21.copy()
        extended_data.update({
            'labels': ['additional-label'],
            'external_references': [
                {
                    'source_name': 'malware-db',
                    'url': 'https://example.com/malware'
                }
            ],
            'kill_chain_phases': [
                {
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': 'execution'
                }
            ],
            'created_by_ref': 'identity--' + str(uuid.uuid4())
        })
        
        malware = STIXObjectFactory.create_object('malware', extended_data, "2.1")
        
        # Check all optional fields are present
        self.assertEqual(malware['labels'], extended_data['labels'])
        self.assertEqual(malware['external_references'], extended_data['external_references'])
        self.assertEqual(malware['kill_chain_phases'], extended_data['kill_chain_phases'])
        self.assertEqual(malware['created_by_ref'], extended_data['created_by_ref'])
    
    def test_malware_missing_required_name(self):
        """Test that malware creation fails without name."""
        invalid_data = self.base_malware_data_21.copy()
        del invalid_data['name']
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('malware', invalid_data)
        
        self.assertIn('name', str(context.exception))
    
    def test_malware_missing_required_malware_types_21(self):
        """Test that STIX 2.1 malware creation fails without malware_types."""
        invalid_data = self.base_malware_data_21.copy()
        del invalid_data['malware_types']
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('malware', invalid_data, "2.1")
        
        self.assertIn('malware_types', str(context.exception))
    
    def test_malware_convenience_function(self):
        """Test the convenience function for malware creation."""
        malware = create_malware(self.base_malware_data_21, "2.1")
        
        self.assertEqual(malware['type'], 'malware')
        self.assertEqual(malware['spec_version'], '2.1')
        self.assertEqual(malware['name'], self.base_malware_data_21['name'])


class TestSTIXAttackPatternCreation(unittest.TestCase):
    """Test STIX Attack Pattern object creation."""
    
    def setUp(self):
        """Set up test data."""
        self.base_attack_pattern_data = {
            'name': 'Test Attack Pattern',
            'description': 'Test attack pattern for unit testing'
        }
    
    def test_basic_attack_pattern_creation_21(self):
        """Test basic STIX 2.1 attack pattern creation."""
        attack_pattern = STIXObjectFactory.create_object('attack-pattern', self.base_attack_pattern_data, "2.1")
        
        # Check required fields
        self.assertEqual(attack_pattern['type'], 'attack-pattern')
        self.assertEqual(attack_pattern['spec_version'], '2.1')
        self.assertIn('id', attack_pattern)
        self.assertIn('created', attack_pattern)
        self.assertIn('modified', attack_pattern)
        self.assertEqual(attack_pattern['name'], self.base_attack_pattern_data['name'])
        
        # Check optional fields
        self.assertEqual(attack_pattern['description'], self.base_attack_pattern_data['description'])
        
        # Validate STIX ID format
        self.assertTrue(attack_pattern['id'].startswith('attack-pattern--'))
    
    def test_basic_attack_pattern_creation_20(self):
        """Test basic STIX 2.0 attack pattern creation."""
        attack_pattern = STIXObjectFactory.create_object('attack-pattern', self.base_attack_pattern_data, "2.0")
        
        # Check required fields
        self.assertEqual(attack_pattern['type'], 'attack-pattern')
        self.assertEqual(attack_pattern['spec_version'], '2.0')
        self.assertEqual(attack_pattern['name'], self.base_attack_pattern_data['name'])
    
    def test_attack_pattern_with_mitre_data(self):
        """Test attack pattern creation with MITRE ATT&CK data."""
        mitre_data = self.base_attack_pattern_data.copy()
        mitre_data.update({
            'x_mitre_id': 'T1055',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1055',
                    'url': 'https://attack.mitre.org/techniques/T1055'
                }
            ],
            'kill_chain_phases': [
                {
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': 'defense-evasion'
                }
            ]
        })
        
        attack_pattern = STIXObjectFactory.create_object('attack-pattern', mitre_data, "2.1")
        
        # Check MITRE-specific fields
        self.assertEqual(attack_pattern['x_mitre_id'], 'T1055')
        self.assertEqual(attack_pattern['external_references'], mitre_data['external_references'])
        self.assertEqual(attack_pattern['kill_chain_phases'], mitre_data['kill_chain_phases'])
    
    def test_attack_pattern_missing_required_name(self):
        """Test that attack pattern creation fails without name."""
        invalid_data = self.base_attack_pattern_data.copy()
        del invalid_data['name']
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('attack-pattern', invalid_data)
        
        self.assertIn('name', str(context.exception))
    
    def test_attack_pattern_empty_name(self):
        """Test that attack pattern creation fails with empty name."""
        invalid_data = self.base_attack_pattern_data.copy()
        invalid_data['name'] = ''
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('attack-pattern', invalid_data)
        
        self.assertIn('name', str(context.exception))
    
    def test_attack_pattern_convenience_function(self):
        """Test the convenience function for attack pattern creation."""
        attack_pattern = create_attack_pattern(self.base_attack_pattern_data, "2.1")
        
        self.assertEqual(attack_pattern['type'], 'attack-pattern')
        self.assertEqual(attack_pattern['spec_version'], '2.1')
        self.assertEqual(attack_pattern['name'], self.base_attack_pattern_data['name'])


class TestSTIXIdentityCreation(unittest.TestCase):
    """Test STIX Identity object creation."""
    
    def setUp(self):
        """Set up test data."""
        self.base_identity_data = {
            'name': 'Test Organization',
            'identity_class': 'organization',
            'description': 'Test organization for unit testing'
        }
    
    def test_basic_identity_creation_21(self):
        """Test basic STIX 2.1 identity creation."""
        identity = STIXObjectFactory.create_object('identity', self.base_identity_data, "2.1")
        
        # Check required fields
        self.assertEqual(identity['type'], 'identity')
        self.assertEqual(identity['spec_version'], '2.1')
        self.assertIn('id', identity)
        self.assertIn('created', identity)
        self.assertIn('modified', identity)
        self.assertEqual(identity['name'], self.base_identity_data['name'])
        self.assertEqual(identity['identity_class'], self.base_identity_data['identity_class'])
        
        # Check optional fields
        self.assertEqual(identity['description'], self.base_identity_data['description'])
        
        # Validate STIX ID format
        self.assertTrue(identity['id'].startswith('identity--'))
    
    def test_basic_identity_creation_20(self):
        """Test basic STIX 2.0 identity creation."""
        identity = STIXObjectFactory.create_object('identity', self.base_identity_data, "2.0")
        
        # Check required fields
        self.assertEqual(identity['type'], 'identity')
        self.assertEqual(identity['spec_version'], '2.0')
        self.assertEqual(identity['name'], self.base_identity_data['name'])
        self.assertEqual(identity['identity_class'], self.base_identity_data['identity_class'])
    
    def test_identity_with_all_optional_fields(self):
        """Test identity creation with all optional fields."""
        extended_data = self.base_identity_data.copy()
        extended_data.update({
            'sectors': ['education', 'government'],
            'contact_information': 'contact@example.com',
            'external_references': [
                {
                    'source_name': 'website',
                    'url': 'https://example.com'
                }
            ],
            'created_by_ref': 'identity--' + str(uuid.uuid4())
        })
        
        identity = STIXObjectFactory.create_object('identity', extended_data, "2.1")
        
        # Check all optional fields are present
        self.assertEqual(identity['sectors'], extended_data['sectors'])
        self.assertEqual(identity['contact_information'], extended_data['contact_information'])
        self.assertEqual(identity['external_references'], extended_data['external_references'])
        self.assertEqual(identity['created_by_ref'], extended_data['created_by_ref'])
    
    def test_identity_different_classes(self):
        """Test identity creation with different identity classes."""
        identity_classes = ['individual', 'group', 'organization', 'class', 'unknown']
        
        for identity_class in identity_classes:
            test_data = self.base_identity_data.copy()
            test_data['identity_class'] = identity_class
            
            identity = STIXObjectFactory.create_object('identity', test_data, "2.1")
            self.assertEqual(identity['identity_class'], identity_class)
    
    def test_identity_missing_required_name(self):
        """Test that identity creation fails without name."""
        invalid_data = self.base_identity_data.copy()
        del invalid_data['name']
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('identity', invalid_data)
        
        self.assertIn('name', str(context.exception))
    
    def test_identity_missing_required_identity_class(self):
        """Test that identity creation fails without identity_class."""
        invalid_data = self.base_identity_data.copy()
        del invalid_data['identity_class']
        
        with self.assertRaises(ValueError) as context:
            STIXObjectFactory.create_object('identity', invalid_data)
        
        self.assertIn('identity_class', str(context.exception))
    
    def test_identity_convenience_function(self):
        """Test the convenience function for identity creation."""
        identity = create_identity(self.base_identity_data, "2.1")
        
        self.assertEqual(identity['type'], 'identity')
        self.assertEqual(identity['spec_version'], '2.1')
        self.assertEqual(identity['name'], self.base_identity_data['name'])


class TestSTIXObjectValidation(unittest.TestCase):
    """Test that created STIX objects pass validation."""
    
    def test_all_created_objects_validate(self):
        """Test that all objects created by factory pass STIX validation."""
        test_cases = [
            ('indicator', {
                'pattern': "[domain-name:value = 'test.com']",
                'labels': ['malicious-activity']
            }),
            ('malware', {
                'name': 'Test Malware',
                'malware_types': ['trojan'],
                'is_family': False
            }),
            ('attack-pattern', {
                'name': 'Test Attack Pattern'
            }),
            ('identity', {
                'name': 'Test Identity',
                'identity_class': 'organization'
            })
        ]
        
        for obj_type, data in test_cases:
            for spec_version in ["2.0", "2.1"]:
                with self.subTest(obj_type=obj_type, spec_version=spec_version):
                    # Adjust data for version compatibility
                    test_data = data.copy()
                    if obj_type == 'malware' and spec_version == "2.0":
                        test_data = {'name': 'Test Malware', 'labels': ['trojan']}
                    
                    obj = STIXObjectFactory.create_object(obj_type, test_data, spec_version)
                    is_valid, errors = STIXValidator.validate_stix_object(obj, spec_version)
                    
                    self.assertTrue(is_valid, 
                        f"Created {obj_type} (v{spec_version}) failed validation: {errors}")
    
    def test_created_objects_have_consistent_timestamps(self):
        """Test that created and modified timestamps are consistent."""
        indicator = STIXObjectFactory.create_object('indicator', {
            'pattern': "[domain-name:value = 'test.com']",
            'labels': ['malicious-activity']
        })
        
        self.assertIn('created', indicator)
        self.assertIn('modified', indicator)
        
        # Timestamps should be valid RFC 3339 format
        self.assertTrue(STIXValidator._validate_timestamp(indicator['created']))
        self.assertTrue(STIXValidator._validate_timestamp(indicator['modified']))
    
    def test_created_objects_have_unique_ids(self):
        """Test that created objects have unique IDs."""
        ids = set()
        
        for _ in range(100):  # Create many objects
            indicator = STIXObjectFactory.create_object('indicator', {
                'pattern': "[domain-name:value = 'test.com']",
                'labels': ['malicious-activity']
            })
            
            # ID should be unique
            self.assertNotIn(indicator['id'], ids)
            ids.add(indicator['id'])
            
            # ID should be valid format
            self.assertTrue(STIXValidator._validate_stix_id(indicator['id'], 'indicator'))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)