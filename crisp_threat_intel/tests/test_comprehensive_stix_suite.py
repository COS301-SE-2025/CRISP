#!/usr/bin/env python3
"""
Comprehensive STIX test suite covering all remaining functionality.
Tests anonymization, database operations, TAXII integration, and OTX integration.
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
from django.test import TestCase
from crisp_threat_intel.models import Organization, STIXObject, Collection, CollectionObject, Feed
from crisp_threat_intel.factories.stix_factory import STIXObjectFactory
from crisp_threat_intel.validators.stix_validators import STIXValidator
from crisp_threat_intel.utils import generate_bundle_from_collection, publish_feed
from crisp_threat_intel.strategies.anonymization import AnonymizationStrategyFactory


class TestSTIXAnonymization(TestCase):
    """Test STIX anonymization functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.test_user = User.objects.create_user(
            username='test_anon_user',
            password='testpass123'
        )
        
        self.source_org = Organization.objects.create(
            name='Source Organization',
            description='Source organization for anonymization testing',
            identity_class='organization',
            created_by=self.test_user
        )
        
        self.target_org = Organization.objects.create(
            name='Target Organization', 
            description='Target organization for anonymization testing',
            identity_class='organization',
            created_by=self.test_user
        )
        
        # Create test STIX object
        indicator_data = STIXObjectFactory.create_object('indicator', {
            'pattern': "[domain-name:value = 'sensitive-internal.company.com']",
            'labels': ['malicious-activity'],
            'name': 'Sensitive Internal Indicator'
        }, "2.1")
        
        self.test_stix_obj = STIXObject.objects.create(
            stix_id=indicator_data['id'],
            stix_type='indicator',
            spec_version='2.1',
            created=indicator_data['created'],
            modified=indicator_data['modified'],
            labels=indicator_data['labels'],
            raw_data=indicator_data,
            source_organization=self.source_org,
            created_by=self.test_user
        )
    
    def test_anonymization_strategy_factory(self):
        """Test anonymization strategy factory."""
        # Test getting none strategy
        none_strategy = AnonymizationStrategyFactory.get_strategy('none')
        self.assertIsNotNone(none_strategy)
        
        # Test getting domain strategy
        domain_strategy = AnonymizationStrategyFactory.get_strategy('domain')
        self.assertIsNotNone(domain_strategy)
        
        # Test invalid strategy
        with self.assertRaises(ValueError):
            AnonymizationStrategyFactory.get_strategy('invalid_strategy')
    
    def test_none_anonymization_strategy(self):
        """Test that 'none' strategy doesn't modify data."""
        none_strategy = AnonymizationStrategyFactory.get_strategy('none')
        original_data = self.test_stix_obj.raw_data.copy()
        
        anonymized_data = none_strategy.anonymize(original_data, trust_level=1.0)
        
        # Data should be unchanged
        self.assertEqual(anonymized_data, original_data)
    
    def test_domain_anonymization_strategy(self):
        """Test domain anonymization strategy."""
        domain_strategy = AnonymizationStrategyFactory.get_strategy('domain')
        original_data = self.test_stix_obj.raw_data.copy()
        
        anonymized_data = domain_strategy.anonymize(original_data, trust_level=0.5)
        
        # Should be a dictionary
        self.assertIsInstance(anonymized_data, dict)
        
        # Should maintain STIX structure
        self.assertEqual(anonymized_data['type'], original_data['type'])
        self.assertEqual(anonymized_data['id'], original_data['id'])
        
        # Should still validate as STIX
        is_valid, errors = STIXValidator.validate_stix_object(anonymized_data, "2.1")
        self.assertTrue(is_valid, f"Anonymized object failed validation: {errors}")
    
    def test_high_trust_anonymization(self):
        """Test anonymization with high trust level."""
        domain_strategy = AnonymizationStrategyFactory.get_strategy('domain')
        original_data = self.test_stix_obj.raw_data.copy()
        
        # High trust should apply minimal anonymization
        anonymized_data = domain_strategy.anonymize(original_data, trust_level=0.9)
        
        # Should maintain most original data
        self.assertEqual(anonymized_data['type'], original_data['type'])
        self.assertEqual(anonymized_data['labels'], original_data['labels'])
    
    def test_low_trust_anonymization(self):
        """Test anonymization with low trust level."""
        domain_strategy = AnonymizationStrategyFactory.get_strategy('domain')
        original_data = self.test_stix_obj.raw_data.copy()
        
        # Low trust should apply more anonymization
        anonymized_data = domain_strategy.anonymize(original_data, trust_level=0.1)
        
        # Should still be valid STIX but with more anonymization
        is_valid, errors = STIXValidator.validate_stix_object(anonymized_data, "2.1")
        self.assertTrue(is_valid, f"Low trust anonymized object failed validation: {errors}")


class TestSTIXDatabaseOperations(TestCase):
    """Test STIX database operations."""
    
    def setUp(self):
        """Set up test data."""
        self.test_user = User.objects.create_user(
            username='test_db_user',
            password='testpass123'
        )
        
        self.test_org = Organization.objects.create(
            name='Test DB Organization',
            description='Test organization for database testing',
            identity_class='organization',
            created_by=self.test_user
        )
    
    def test_stix_object_creation_and_retrieval(self):
        """Test creating and retrieving STIX objects from database."""
        # Create STIX object data
        indicator_data = STIXObjectFactory.create_object('indicator', {
            'pattern': "[domain-name:value = 'test-db.com']",
            'labels': ['malicious-activity'],
            'name': 'Test DB Indicator'
        }, "2.1")
        
        # Store in database
        db_obj = STIXObject.objects.create(
            stix_id=indicator_data['id'],
            stix_type='indicator',
            spec_version='2.1',
            created=indicator_data['created'],
            modified=indicator_data['modified'],
            labels=indicator_data['labels'],
            raw_data=indicator_data,
            source_organization=self.test_org,
            created_by=self.test_user
        )
        
        # Retrieve from database
        retrieved_obj = STIXObject.objects.get(stix_id=indicator_data['id'])
        
        # Verify data integrity
        self.assertEqual(retrieved_obj.stix_id, indicator_data['id'])
        self.assertEqual(retrieved_obj.stix_type, 'indicator')
        self.assertEqual(retrieved_obj.spec_version, '2.1')
        self.assertEqual(retrieved_obj.raw_data, indicator_data)
        
        # Test to_stix() method
        stix_dict = retrieved_obj.to_stix()
        self.assertEqual(stix_dict, indicator_data)
        
        # Test to_json() method
        json_str = retrieved_obj.to_json()
        parsed_json = json.loads(json_str)
        self.assertEqual(parsed_json, indicator_data)
    
    def test_stix_object_querying(self):
        """Test querying STIX objects by various criteria."""
        created_objects = []
        
        # Create multiple STIX objects
        for i in range(5):
            indicator_data = STIXObjectFactory.create_object('indicator', {
                'pattern': f"[domain-name:value = 'test{i}.com']",
                'labels': ['malicious-activity'],
                'name': f'Test Indicator {i}'
            }, "2.1")
            
            obj = STIXObject.objects.create(
                stix_id=indicator_data['id'],
                stix_type='indicator',
                spec_version='2.1',
                created=indicator_data['created'],
                modified=indicator_data['modified'],
                labels=indicator_data['labels'],
                raw_data=indicator_data,
                source_organization=self.test_org,
                created_by=self.test_user
            )
            created_objects.append(obj)
        
        try:
            # Query by type and organization to isolate our test data
            indicators = STIXObject.objects.filter(
                stix_type='indicator',
                source_organization=self.test_org
            )
            self.assertEqual(indicators.count(), 5)
            
            # Query by organization
            org_objects = STIXObject.objects.filter(source_organization=self.test_org)
            self.assertEqual(org_objects.count(), 5)
            
            # Query by spec version and organization
            v21_objects = STIXObject.objects.filter(
                spec_version='2.1',
                source_organization=self.test_org
            )
            self.assertEqual(v21_objects.count(), 5)
        finally:
            # Clean up test objects
            for obj in created_objects:
                obj.delete()
    
    def test_collection_stix_object_relationship(self):
        """Test many-to-many relationship between collections and STIX objects."""
        # Create collection
        collection = Collection.objects.create(
            title='Test DB Collection',
            description='Test collection for database testing',
            alias='test-db-collection',
            owner=self.test_org,
            can_read=True,
            can_write=True
        )
        
        # Create STIX objects
        stix_objects = []
        for i in range(3):
            indicator_data = STIXObjectFactory.create_object('indicator', {
                'pattern': f"[domain-name:value = 'collection-test{i}.com']",
                'labels': ['malicious-activity']
            }, "2.1")
            
            stix_obj = STIXObject.objects.create(
                stix_id=indicator_data['id'],
                stix_type='indicator',
                spec_version='2.1',
                created=indicator_data['created'],
                modified=indicator_data['modified'],
                labels=indicator_data['labels'],
                raw_data=indicator_data,
                source_organization=self.test_org,
                created_by=self.test_user
            )
            stix_objects.append(stix_obj)
        
        # Add objects to collection
        for stix_obj in stix_objects:
            CollectionObject.objects.create(
                collection=collection,
                stix_object=stix_obj
            )
        
        # Test relationship
        self.assertEqual(collection.stix_objects.count(), 3)
        self.assertEqual(stix_objects[0].collections.count(), 1)
        
        # Test querying through relationship
        collection_indicators = collection.stix_objects.filter(stix_type='indicator')
        self.assertEqual(collection_indicators.count(), 3)
    
    def test_stix_object_version_support(self):
        """Test database support for both STIX 2.0 and 2.1."""
        test_objects = []
        
        try:
            # Create STIX 2.0 object
            indicator_20_data = STIXObjectFactory.create_object('indicator', {
                'pattern': "[domain-name:value = 'test-20.com']",
                'labels': ['malicious-activity']
            }, "2.0")
            
            db_obj_20 = STIXObject.objects.create(
                stix_id=indicator_20_data['id'],
                stix_type='indicator',
                spec_version='2.0',
                created=indicator_20_data['created'],
                modified=indicator_20_data['modified'],
                labels=indicator_20_data['labels'],
                raw_data=indicator_20_data,
                source_organization=self.test_org,
                created_by=self.test_user
            )
            test_objects.append(db_obj_20)
            
            # Create STIX 2.1 object
            indicator_21_data = STIXObjectFactory.create_object('indicator', {
                'pattern': "[domain-name:value = 'test-21.com']",
                'labels': ['malicious-activity']
            }, "2.1")
            
            db_obj_21 = STIXObject.objects.create(
                stix_id=indicator_21_data['id'],
                stix_type='indicator',
                spec_version='2.1',
                created=indicator_21_data['created'],
                modified=indicator_21_data['modified'],
                labels=indicator_21_data['labels'],
                raw_data=indicator_21_data,
                source_organization=self.test_org,
                created_by=self.test_user
            )
            test_objects.append(db_obj_21)
            
            # Query by version and organization to isolate test data
            v20_objects = STIXObject.objects.filter(
                spec_version='2.0',
                source_organization=self.test_org
            )
            v21_objects = STIXObject.objects.filter(
                spec_version='2.1',
                source_organization=self.test_org
            )
            
            self.assertEqual(v20_objects.count(), 1)
            self.assertEqual(v21_objects.count(), 1)
            
            # Verify version-specific data
            self.assertEqual(v20_objects.first().spec_version, '2.0')
            self.assertEqual(v21_objects.first().spec_version, '2.1')
            
            # Verify raw data maintains version differences
            v20_raw = v20_objects.first().raw_data
            v21_raw = v21_objects.first().raw_data
            
            self.assertEqual(v20_raw['spec_version'], '2.0')
            self.assertEqual(v21_raw['spec_version'], '2.1')
            self.assertNotIn('pattern_type', v20_raw)
            self.assertIn('pattern_type', v21_raw)
            
        finally:
            # Clean up test objects
            for obj in test_objects:
                obj.delete()


class TestSTIXFeedIntegration(TestCase):
    """Test STIX feed and publishing integration."""
    
    def setUp(self):
        """Set up test data."""
        self.test_user = User.objects.create_user(
            username='test_feed_user',
            password='testpass123'
        )
        
        self.test_org = Organization.objects.create(
            name='Test Feed Organization',
            description='Test organization for feed testing',
            identity_class='organization',
            created_by=self.test_user
        )
        
        self.test_collection = Collection.objects.create(
            title='Test Feed Collection',
            description='Test collection for feed testing',
            alias='test-feed-collection',
            owner=self.test_org,
            can_read=True,
            can_write=True
        )
        
        # Create test STIX objects
        indicator_data = STIXObjectFactory.create_object('indicator', {
            'pattern': "[domain-name:value = 'feed-test.com']",
            'labels': ['malicious-activity'],
            'name': 'Test Feed Indicator'
        }, "2.1")
        
        stix_obj = STIXObject.objects.create(
            stix_id=indicator_data['id'],
            stix_type='indicator',
            spec_version='2.1',
            created=indicator_data['created'],
            modified=indicator_data['modified'],
            labels=indicator_data['labels'],
            raw_data=indicator_data,
            source_organization=self.test_org,
            created_by=self.test_user
        )
        
        CollectionObject.objects.create(
            collection=self.test_collection,
            stix_object=stix_obj
        )
    
    def test_feed_creation_and_publishing(self):
        """Test feed creation and publishing functionality."""
        # Create feed
        feed = Feed.objects.create(
            name='Test STIX Feed',
            description='Test feed for STIX publishing',
            collection=self.test_collection,
            update_interval=3600,
            status='active',
            created_by=self.test_user
        )
        
        # Test feed publishing
        result = publish_feed(feed)
        
        # Verify publishing result
        self.assertIsInstance(result, dict)
        self.assertEqual(result['status'], 'success')
        self.assertIn('bundle_id', result)
        self.assertIn('object_count', result)
        self.assertTrue(result['object_count'] > 0)
        
        # Verify feed metadata updated
        feed.refresh_from_db()
        self.assertIsNotNone(feed.last_published_time)
        self.assertIsNotNone(feed.last_bundle_id)
        self.assertEqual(feed.publish_count, 1)
        self.assertIsNone(feed.last_error)
    
    def test_feed_publication_status(self):
        """Test feed publication status tracking."""
        feed = Feed.objects.create(
            name='Test Status Feed',
            description='Test feed for status tracking',
            collection=self.test_collection,
            update_interval=3600,
            status='active',
            created_by=self.test_user
        )
        
        # Get initial status
        status = feed.get_publication_status()
        
        self.assertEqual(status['name'], feed.name)
        self.assertEqual(status['status'], 'active')
        self.assertIsNone(status['last_published'])
        self.assertEqual(status['publish_count'], 0)
        self.assertEqual(status['error_count'], 0)
        self.assertEqual(status['collection'], self.test_collection.title)
        self.assertTrue(status['object_count'] > 0)
        
        # Publish feed
        publish_feed(feed)
        
        # Get updated status
        updated_status = feed.get_publication_status()
        self.assertIsNotNone(updated_status['last_published'])
        self.assertEqual(updated_status['publish_count'], 1)


class TestSTIXValidationIntegration(TestCase):
    """Test STIX validation integration throughout the system."""
    
    def test_factory_created_objects_validate(self):
        """Test that factory-created objects always validate."""
        test_cases = [
            ('indicator', {'pattern': "[domain-name:value = 'test.com']", 'labels': ['malicious-activity']}, "2.1"),
            ('indicator', {'pattern': "[domain-name:value = 'test.com']", 'labels': ['malicious-activity']}, "2.0"),
            ('malware', {'name': 'Test Malware', 'malware_types': ['trojan'], 'is_family': False}, "2.1"),
            ('malware', {'name': 'Test Malware', 'labels': ['trojan']}, "2.0"),
            ('attack-pattern', {'name': 'Test Attack Pattern'}, "2.1"),
            ('attack-pattern', {'name': 'Test Attack Pattern'}, "2.0"),
            ('identity', {'name': 'Test Identity', 'identity_class': 'organization'}, "2.1"),
            ('identity', {'name': 'Test Identity', 'identity_class': 'organization'}, "2.0"),
        ]
        
        for obj_type, data, spec_version in test_cases:
            with self.subTest(obj_type=obj_type, spec_version=spec_version):
                obj = STIXObjectFactory.create_object(obj_type, data, spec_version)
                is_valid, errors = STIXValidator.validate_stix_object(obj, spec_version)
                self.assertTrue(is_valid, f"Factory object failed validation: {errors}")
    
    def test_bundle_generation_validation(self):
        """Test that generated bundles always validate."""
        # Set up test data
        test_user = User.objects.create_user(username='bundle_test', password='test123')
        test_org = Organization.objects.create(
            name='Bundle Test Org',
            identity_class='organization',
            created_by=test_user
        )
        collection = Collection.objects.create(
            title='Bundle Test Collection',
            alias='bundle-test',
            owner=test_org
        )
        
        # Create STIX objects
        for i in range(3):
            indicator_data = STIXObjectFactory.create_object('indicator', {
                'pattern': f"[domain-name:value = 'bundle{i}.com']",
                'labels': ['malicious-activity']
            }, "2.1")
            
            stix_obj = STIXObject.objects.create(
                stix_id=indicator_data['id'],
                stix_type='indicator',
                spec_version='2.1',
                created=indicator_data['created'],
                modified=indicator_data['modified'],
                labels=indicator_data['labels'],
                raw_data=indicator_data,
                source_organization=test_org,
                created_by=test_user
            )
            
            CollectionObject.objects.create(collection=collection, stix_object=stix_obj)
        
        # Generate bundle
        bundle = generate_bundle_from_collection(collection)
        
        # Validate bundle
        is_valid, errors = STIXValidator.validate_stix_bundle(bundle, "2.1")
        self.assertTrue(is_valid, f"Generated bundle failed validation: {errors}")
        
        # Cleanup
        CollectionObject.objects.filter(collection=collection).delete()
        STIXObject.objects.filter(source_organization=test_org).delete()
        collection.delete()
        test_org.delete()
        test_user.delete()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)