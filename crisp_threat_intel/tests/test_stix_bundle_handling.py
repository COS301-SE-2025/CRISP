#!/usr/bin/env python3
"""
Comprehensive STIX bundle handling unit tests.
Tests all aspects of STIX bundle creation, validation, and processing.
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

from django.contrib.auth.models import User
from crisp_threat_intel.models import Organization, STIXObject, Collection, CollectionObject
from crisp_threat_intel.factories.stix_factory import STIXObjectFactory
from crisp_threat_intel.validators.stix_validators import STIXValidator
from crisp_threat_intel.utils import generate_bundle_from_collection, get_or_create_identity


class TestSTIXBundleCreation(unittest.TestCase):
    """Test STIX bundle creation functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.test_user = User.objects.create_user(
            username='test_bundle_user',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test organization
        self.test_org = Organization.objects.create(
            name='Test Bundle Organization',
            description='Test organization for bundle testing',
            identity_class='organization',
            sectors=['education'],
            contact_email='test@example.com',
            created_by=self.test_user
        )
        
        # Create test collection
        self.test_collection = Collection.objects.create(
            title='Test Bundle Collection',
            description='Test collection for bundle testing',
            alias='test-bundle-collection',
            owner=self.test_org,
            can_read=True,
            can_write=True
        )
        
        # Create test STIX objects
        self.create_test_stix_objects()
    
    def create_test_stix_objects(self):
        """Create test STIX objects in the database."""
        # Create indicator
        indicator_data = STIXObjectFactory.create_object('indicator', {
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity'],
            'name': 'Test Bundle Indicator'
        }, "2.1")
        
        self.indicator_obj = STIXObject.objects.create(
            stix_id=indicator_data['id'],
            stix_type=indicator_data['type'],
            spec_version=indicator_data['spec_version'],
            created=indicator_data['created'],
            modified=indicator_data['modified'],
            labels=indicator_data['labels'],
            raw_data=indicator_data,
            source_organization=self.test_org,
            created_by=self.test_user
        )
        
        # Create malware
        malware_data = STIXObjectFactory.create_object('malware', {
            'name': 'Test Bundle Malware',
            'malware_types': ['trojan'],
            'is_family': False
        }, "2.1")
        
        self.malware_obj = STIXObject.objects.create(
            stix_id=malware_data['id'],
            stix_type=malware_data['type'],
            spec_version=malware_data['spec_version'],
            created=malware_data['created'],
            modified=malware_data['modified'],
            raw_data=malware_data,
            source_organization=self.test_org,
            created_by=self.test_user
        )
        
        # Create attack pattern
        attack_pattern_data = STIXObjectFactory.create_object('attack-pattern', {
            'name': 'Test Bundle Attack Pattern',
            'description': 'Test attack pattern for bundle testing'
        }, "2.1")
        
        self.attack_pattern_obj = STIXObject.objects.create(
            stix_id=attack_pattern_data['id'],
            stix_type=attack_pattern_data['type'],
            spec_version=attack_pattern_data['spec_version'],
            created=attack_pattern_data['created'],
            modified=attack_pattern_data['modified'],
            raw_data=attack_pattern_data,
            source_organization=self.test_org,
            created_by=self.test_user
        )
        
        # Add objects to collection
        CollectionObject.objects.create(
            collection=self.test_collection,
            stix_object=self.indicator_obj
        )
        CollectionObject.objects.create(
            collection=self.test_collection,
            stix_object=self.malware_obj
        )
        CollectionObject.objects.create(
            collection=self.test_collection,
            stix_object=self.attack_pattern_obj
        )
    
    def test_basic_bundle_generation(self):
        """Test basic bundle generation from collection."""
        bundle = generate_bundle_from_collection(self.test_collection)
        
        # Check bundle structure
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('id', bundle)
        self.assertTrue(bundle['id'].startswith('bundle--'))
        self.assertEqual(bundle['spec_version'], '2.1')
        self.assertIn('objects', bundle)
        
        # Check bundle objects count (3 STIX objects + 1 identity)
        self.assertEqual(len(bundle['objects']), 4)
        
        # Check that owner identity is included
        identity_objects = [obj for obj in bundle['objects'] if obj['type'] == 'identity']
        self.assertEqual(len(identity_objects), 1)
        self.assertEqual(identity_objects[0]['name'], self.test_org.name)
        
        # Check that all STIX objects are included
        object_types = [obj['type'] for obj in bundle['objects']]
        self.assertIn('indicator', object_types)
        self.assertIn('malware', object_types)
        self.assertIn('attack-pattern', object_types)
        self.assertIn('identity', object_types)
        
        # Validate bundle
        is_valid, errors = STIXValidator.validate_stix_bundle(bundle, "2.1")
        self.assertTrue(is_valid, f"Generated bundle failed validation: {errors}")
    
    def test_bundle_with_filters(self):
        """Test bundle generation with filters."""
        # Filter by STIX type
        filters = {'stix_type': 'indicator'}
        bundle = generate_bundle_from_collection(self.test_collection, filters=filters)
        
        # Should contain indicator + identity
        self.assertEqual(len(bundle['objects']), 2)
        
        stix_objects = [obj for obj in bundle['objects'] if obj['type'] != 'identity']
        self.assertEqual(len(stix_objects), 1)
        self.assertEqual(stix_objects[0]['type'], 'indicator')
    
    def test_bundle_with_date_filters(self):
        """Test bundle generation with date filters."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Filter by creation date (future date - should return no objects)
        future_date = timezone.now() + timedelta(days=1)
        filters = {'created_after': future_date}
        bundle = generate_bundle_from_collection(self.test_collection, filters=filters)
        
        # Should only contain identity (no STIX objects match filter)
        self.assertEqual(len(bundle['objects']), 1)
        self.assertEqual(bundle['objects'][0]['type'], 'identity')
    
    def test_empty_collection_bundle(self):
        """Test bundle generation from empty collection."""
        empty_collection = Collection.objects.create(
            title='Empty Test Collection',
            description='Empty collection for testing',
            alias='empty-test-collection',
            owner=self.test_org,
            can_read=True,
            can_write=True
        )
        
        bundle = generate_bundle_from_collection(empty_collection)
        
        # Should only contain owner identity
        self.assertEqual(len(bundle['objects']), 1)
        self.assertEqual(bundle['objects'][0]['type'], 'identity')
        
        # Validate bundle
        is_valid, errors = STIXValidator.validate_stix_bundle(bundle, "2.1")
        self.assertTrue(is_valid, f"Empty bundle failed validation: {errors}")
    
    def test_bundle_id_uniqueness(self):
        """Test that generated bundles have unique IDs."""
        bundle_ids = set()
        
        for _ in range(10):
            bundle = generate_bundle_from_collection(self.test_collection)
            bundle_id = bundle['id']
            
            # ID should be unique
            self.assertNotIn(bundle_id, bundle_ids)
            bundle_ids.add(bundle_id)
            
            # ID should be valid format
            self.assertTrue(STIXValidator._validate_stix_id(bundle_id, 'bundle'))
    
    def test_bundle_object_integrity(self):
        """Test that bundle objects maintain integrity."""
        bundle = generate_bundle_from_collection(self.test_collection)
        
        # Find the indicator in the bundle
        indicator_in_bundle = None
        for obj in bundle['objects']:
            if obj['type'] == 'indicator':
                indicator_in_bundle = obj
                break
        
        self.assertIsNotNone(indicator_in_bundle)
        
        # Compare with original object
        original_indicator = self.indicator_obj.raw_data
        
        # Key fields should match
        self.assertEqual(indicator_in_bundle['id'], original_indicator['id'])
        self.assertEqual(indicator_in_bundle['type'], original_indicator['type'])
        self.assertEqual(indicator_in_bundle['pattern'], original_indicator['pattern'])
        self.assertEqual(indicator_in_bundle['labels'], original_indicator['labels'])
    
    def tearDown(self):
        """Clean up test data."""
        # Delete in reverse order to avoid foreign key constraints
        CollectionObject.objects.filter(collection=self.test_collection).delete()
        STIXObject.objects.filter(source_organization=self.test_org).delete()
        Collection.objects.filter(owner=self.test_org).delete()
        Organization.objects.filter(name__contains='Test Bundle').delete()
        User.objects.filter(username='test_bundle_user').delete()


class TestSTIXBundleValidation(unittest.TestCase):
    """Test STIX bundle validation functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': [
                {
                    'type': 'indicator',
                    'id': 'indicator--' + str(uuid.uuid4()),
                    'spec_version': '2.1',
                    'created': '2025-06-23T06:00:00.000Z',
                    'modified': '2025-06-23T06:00:00.000Z',
                    'pattern': "[domain-name:value = 'test.com']",
                    'pattern_type': 'stix',
                    'valid_from': '2025-06-23T06:00:00.000Z',
                    'labels': ['malicious-activity']
                },
                {
                    'type': 'identity',
                    'id': 'identity--' + str(uuid.uuid4()),
                    'spec_version': '2.1',
                    'created': '2025-06-23T06:00:00.000Z',
                    'modified': '2025-06-23T06:00:00.000Z',
                    'name': 'Test Organization',
                    'identity_class': 'organization'
                }
            ]
        }
    
    def test_valid_bundle_validation(self):
        """Test validation of valid bundle."""
        is_valid, errors = STIXValidator.validate_stix_bundle(self.valid_bundle, "2.1")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_bundle_missing_type(self):
        """Test validation fails for bundle missing type."""
        invalid_bundle = self.valid_bundle.copy()
        del invalid_bundle['type']
        
        is_valid, errors = STIXValidator.validate_stix_bundle(invalid_bundle, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('type' in error for error in errors))
    
    def test_bundle_missing_id(self):
        """Test validation fails for bundle missing ID."""
        invalid_bundle = self.valid_bundle.copy()
        del invalid_bundle['id']
        
        is_valid, errors = STIXValidator.validate_stix_bundle(invalid_bundle, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('id' in error for error in errors))
    
    def test_bundle_missing_objects(self):
        """Test validation fails for bundle missing objects."""
        invalid_bundle = self.valid_bundle.copy()
        del invalid_bundle['objects']
        
        is_valid, errors = STIXValidator.validate_stix_bundle(invalid_bundle, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('objects' in error for error in errors))
    
    def test_bundle_invalid_object_in_objects(self):
        """Test validation fails for invalid object in bundle."""
        invalid_bundle = self.valid_bundle.copy()
        # Add invalid object (missing required fields)
        invalid_bundle['objects'].append({
            'type': 'indicator',
            'id': 'indicator--' + str(uuid.uuid4())
            # Missing other required fields
        })
        
        is_valid, errors = STIXValidator.validate_stix_bundle(invalid_bundle, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('Object 2' in error for error in errors))
    
    def test_bundle_non_dict_object_in_objects(self):
        """Test validation fails for non-dict object in bundle."""
        invalid_bundle = self.valid_bundle.copy()
        invalid_bundle['objects'].append("not a dictionary")
        
        is_valid, errors = STIXValidator.validate_stix_bundle(invalid_bundle, "2.1")
        self.assertFalse(is_valid)
        self.assertTrue(any('Object 2' in error and 'dictionary' in error for error in errors))
    
    def test_bundle_empty_objects_list(self):
        """Test validation of bundle with empty objects list."""
        bundle_with_empty_objects = self.valid_bundle.copy()
        bundle_with_empty_objects['objects'] = []
        
        # Empty objects list should be valid (though unusual)
        is_valid, errors = STIXValidator.validate_stix_bundle(bundle_with_empty_objects, "2.1")
        self.assertTrue(is_valid)
    
    def test_bundle_mixed_spec_versions(self):
        """Test bundle with mixed spec versions."""
        mixed_bundle = self.valid_bundle.copy()
        
        # Add STIX 2.0 object to STIX 2.1 bundle
        stix_20_object = {
            'type': 'malware',
            'id': 'malware--' + str(uuid.uuid4()),
            'created': '2025-06-23T06:00:00.000Z',
            'modified': '2025-06-23T06:00:00.000Z',
            'name': 'Test Malware',
            'labels': ['trojan']
        }
        mixed_bundle['objects'].append(stix_20_object)
        
        # Validate as 2.1 bundle - should fail due to mixed versions
        is_valid, errors = STIXValidator.validate_stix_bundle(mixed_bundle, "2.1")
        self.assertFalse(is_valid)
        # The malware object should fail 2.1 validation
        self.assertTrue(any('Object 2' in error for error in errors))


class TestSTIXBundleProcessing(unittest.TestCase):
    """Test STIX bundle processing and manipulation."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_objects = [
            STIXObjectFactory.create_object('indicator', {
                'pattern': "[domain-name:value = 'test1.com']",
                'labels': ['malicious-activity']
            }, "2.1"),
            STIXObjectFactory.create_object('malware', {
                'name': 'Test Malware',
                'malware_types': ['trojan'],
                'is_family': False
            }, "2.1"),
            STIXObjectFactory.create_object('identity', {
                'name': 'Test Organization',
                'identity_class': 'organization'
            }, "2.1")
        ]
    
    def test_bundle_object_extraction(self):
        """Test extracting objects from bundle by type."""
        bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': self.sample_objects
        }
        
        # Extract indicators
        indicators = [obj for obj in bundle['objects'] if obj['type'] == 'indicator']
        self.assertEqual(len(indicators), 1)
        self.assertEqual(indicators[0]['type'], 'indicator')
        
        # Extract malware
        malware = [obj for obj in bundle['objects'] if obj['type'] == 'malware']
        self.assertEqual(len(malware), 1)
        self.assertEqual(malware[0]['type'], 'malware')
        
        # Extract identities
        identities = [obj for obj in bundle['objects'] if obj['type'] == 'identity']
        self.assertEqual(len(identities), 1)
        self.assertEqual(identities[0]['type'], 'identity')
    
    def test_bundle_object_counting(self):
        """Test counting objects in bundle by type."""
        bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': self.sample_objects
        }
        
        type_counts = {}
        for obj in bundle['objects']:
            obj_type = obj['type']
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        self.assertEqual(type_counts['indicator'], 1)
        self.assertEqual(type_counts['malware'], 1)
        self.assertEqual(type_counts['identity'], 1)
        self.assertEqual(len(type_counts), 3)
    
    def test_bundle_serialization(self):
        """Test bundle JSON serialization and deserialization."""
        bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': self.sample_objects
        }
        
        # Serialize to JSON
        json_str = json.dumps(bundle, indent=2)
        self.assertIsInstance(json_str, str)
        
        # Deserialize from JSON
        deserialized_bundle = json.loads(json_str)
        
        # Should match original
        self.assertEqual(deserialized_bundle['type'], bundle['type'])
        self.assertEqual(deserialized_bundle['id'], bundle['id'])
        self.assertEqual(len(deserialized_bundle['objects']), len(bundle['objects']))
        
        # Validate deserialized bundle
        is_valid, errors = STIXValidator.validate_stix_bundle(deserialized_bundle, "2.1")
        self.assertTrue(is_valid, f"Deserialized bundle failed validation: {errors}")
    
    def test_bundle_size_limits(self):
        """Test bundle handling with large numbers of objects."""
        # Create bundle with many objects
        many_objects = []
        for i in range(100):
            indicator = STIXObjectFactory.create_object('indicator', {
                'pattern': f"[domain-name:value = 'test{i}.com']",
                'labels': ['malicious-activity']
            }, "2.1")
            many_objects.append(indicator)
        
        large_bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': many_objects
        }
        
        # Should still validate correctly
        is_valid, errors = STIXValidator.validate_stix_bundle(large_bundle, "2.1")
        self.assertTrue(is_valid, f"Large bundle failed validation: {errors}")
        
        # Should have correct count
        self.assertEqual(len(large_bundle['objects']), 100)
    
    def test_bundle_duplicate_objects(self):
        """Test bundle with duplicate objects."""
        duplicate_indicator = STIXObjectFactory.create_object('indicator', {
            'pattern': "[domain-name:value = 'duplicate.com']",
            'labels': ['malicious-activity']
        }, "2.1")
        
        bundle_with_duplicates = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': [duplicate_indicator, duplicate_indicator]  # Same object twice
        }
        
        # Bundle should still be valid (STIX allows duplicates)
        is_valid, errors = STIXValidator.validate_stix_bundle(bundle_with_duplicates, "2.1")
        self.assertTrue(is_valid, f"Bundle with duplicates failed validation: {errors}")
        
        # Should have 2 objects (even though they're identical)
        self.assertEqual(len(bundle_with_duplicates['objects']), 2)


class TestSTIXBundleVersionCompatibility(unittest.TestCase):
    """Test STIX bundle version compatibility."""
    
    def test_stix_20_bundle_validation(self):
        """Test validation of STIX 2.0 bundle."""
        stix_20_bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': [
                {
                    'type': 'indicator',
                    'id': 'indicator--' + str(uuid.uuid4()),
                    'created': '2025-06-23T06:00:00.000Z',
                    'modified': '2025-06-23T06:00:00.000Z',
                    'pattern': "[domain-name:value = 'test.com']",
                    'labels': ['malicious-activity']
                }
            ]
        }
        
        # Should validate as STIX 2.0
        is_valid, errors = STIXValidator.validate_stix_bundle(stix_20_bundle, "2.0")
        self.assertTrue(is_valid, f"STIX 2.0 bundle failed validation: {errors}")
    
    def test_stix_21_bundle_validation(self):
        """Test validation of STIX 2.1 bundle."""
        stix_21_bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': [
                {
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
            ]
        }
        
        # Should validate as STIX 2.1
        is_valid, errors = STIXValidator.validate_stix_bundle(stix_21_bundle, "2.1")
        self.assertTrue(is_valid, f"STIX 2.1 bundle failed validation: {errors}")
    
    def test_bundle_spec_version_consistency(self):
        """Test that bundle spec versions are handled consistently."""
        # Create objects with explicit spec versions
        stix_21_objects = [
            STIXObjectFactory.create_object('indicator', {
                'pattern': "[domain-name:value = 'test.com']",
                'labels': ['malicious-activity']
            }, "2.1"),
            STIXObjectFactory.create_object('identity', {
                'name': 'Test Org',
                'identity_class': 'organization'
            }, "2.1")
        ]
        
        # All objects should have spec_version 2.1
        for obj in stix_21_objects:
            self.assertEqual(obj['spec_version'], '2.1')
        
        bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'objects': stix_21_objects
        }
        
        # Bundle should validate as 2.1
        is_valid, errors = STIXValidator.validate_stix_bundle(bundle, "2.1")
        self.assertTrue(is_valid, f"Bundle with consistent spec versions failed: {errors}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)