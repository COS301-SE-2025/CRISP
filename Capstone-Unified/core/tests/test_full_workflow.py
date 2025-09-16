"""
Full Workflow Integration Tests
Tests complete end-to-end workflows in the CRISP system
"""

import json
import uuid
from datetime import datetime, timedelta
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

User = get_user_model()
from django.utils import timezone
from unittest.mock import patch, MagicMock

from core.models.models import (
    Organization, STIXObject, Collection, CollectionObject, Feed
)
from core.patterns.strategy.enums import AnonymizationLevel
from settings.utils import generate_bundle_from_collection


class FullWorkflowTestCase(TransactionTestCase):
    """Test complete end-to-end workflows."""
    
    def setUp(self):
        """Set up test data"""
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        # Create test user
        self.user = User.objects.create_user(
            username=f'testuser_{unique_suffix}',
            email=f'test_{unique_suffix}@example.com',
            password='testpass123'
        )
        
        # Create test organization
        self.organization = Organization.objects.create(
            name=f'Test University {unique_suffix}',
            description='Test educational institution',
            identity_class='organization',
            sectors=['education'],
            contact_email=f'security_{unique_suffix}@testuni.edu',
            created_by=self.user
        )
        
        # Create test collection
        self.collection = Collection.objects.create(
            title='Test Threat Collection',
            description='Test collection for threat intelligence',
            alias=f'test-threats-{unique_suffix}',
            owner=self.organization,
            can_read=True,
            can_write=True
        )
    
    def test_complete_workflow(self):
        """
        Test: Organization -> STIX Objects -> Collection -> Feed -> Bundle -> Publish
        This must produce identical results to threat_intel_service tests.
        """
        # Step 1: Create STIX Objects
        stix_objects = []
        
        # Create indicator
        indicator_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[domain-name:value = 'malicious.test.com']",
            'labels': ['malicious-activity'],
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'description': 'Test malicious domain for workflow testing'
        }
        
        indicator_object = STIXObject.objects.create(
            stix_id=indicator_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=indicator_data,
            source_organization=self.organization,
            created_by=self.user
        )
        stix_objects.append(indicator_object)
        
        # Create malware object
        malware_data = {
            'type': 'malware',
            'id': f'malware--{uuid.uuid4()}',
            'spec_version': '2.1',
            'labels': ['trojan'],
            'name': 'TestWorkflowMalware',
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'description': 'Test malware for workflow validation'
        }
        
        malware_object = STIXObject.objects.create(
            stix_id=malware_data['id'],
            stix_type='malware',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=malware_data,
            source_organization=self.organization,
            created_by=self.user
        )
        stix_objects.append(malware_object)
        
        # Step 2: Add objects to collection
        for stix_object in stix_objects:
            self.collection.stix_objects.add(stix_object)
        
        # Verify collection contains objects
        self.assertEqual(self.collection.stix_objects.count(), 2)
        
        # Step 3: Create feed from collection
        unique_suffix = str(uuid.uuid4())[:8]
        feed = Feed.objects.create(
            title='Workflow Test Feed',
            description='Feed created for workflow testing',
            alias=f'workflow-feed-{unique_suffix}',
            collection=self.collection,
            organization=self.organization,
            created_by=self.user,
            is_public=True,
            anonymization_level=AnonymizationLevel.LOW.value
        )
        
        # Verify feed creation
        self.assertEqual(feed.collection, self.collection)
        self.assertEqual(feed.organization, self.organization)
        
        # Step 4: Generate bundle from collection
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.organization
        )
        
        # Verify bundle structure
        self.assertIsNotNone(bundle)
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('id', bundle)
        self.assertIn('objects', bundle)
        
        # Verify bundle contains our objects (excluding owner identity)
        bundle_objects = [obj for obj in bundle['objects'] if obj['type'] not in ['bundle', 'identity']]
        self.assertEqual(len(bundle_objects), 2)
        
        # Verify object types (excluding identity objects)
        object_types = [obj['type'] for obj in bundle_objects]
        self.assertIn('indicator', object_types)
        self.assertIn('malware', object_types)
        
        # Verify owner identity is included in bundle
        identity_objects = [obj for obj in bundle['objects'] if obj['type'] == 'identity']
        self.assertEqual(len(identity_objects), 1)  # Should have exactly one owner identity
        
        # Step 5: Verify original data preservation (same organization)
        indicator_in_bundle = next(
            (obj for obj in bundle_objects if obj['type'] == 'indicator'), 
            None
        )
        self.assertIsNotNone(indicator_in_bundle)
        self.assertEqual(indicator_in_bundle['pattern'], indicator_data['pattern'])
        
        malware_in_bundle = next(
            (obj for obj in bundle_objects if obj['type'] == 'malware'), 
            None
        )
        self.assertIsNotNone(malware_in_bundle)
        self.assertEqual(malware_in_bundle['name'], malware_data['name'])
        
        # Step 6: Test external organization access (with anonymization)
        external_org = Organization.objects.create(
            name=f'External Org {unique_suffix}',
            description='External organization for testing',
            identity_class='organization',
            organization_type='commercial',
            contact_email=f'external_{unique_suffix}@test.com',
            created_by=self.user
        )
        
        external_bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=external_org
        )
        
        # Verify anonymization occurred
        self.assertIsNotNone(external_bundle)
        external_objects = [obj for obj in external_bundle['objects'] if obj['type'] not in ['bundle', 'identity']]
        self.assertEqual(len(external_objects), 2)
        
        # Check that sensitive data was anonymized
        external_indicator = next(
            (obj for obj in external_objects if obj['type'] == 'indicator'),
            None
        )
        
        if external_indicator:
            # Pattern should be different due to anonymization
            self.assertNotEqual(external_indicator['pattern'], indicator_data['pattern'])
    
    def test_multi_collection_workflow(self):
        """Test workflow with multiple collections."""
        unique_suffix = str(uuid.uuid4())[:8]
        
        # Create second collection
        collection2 = Collection.objects.create(
            title='Second Test Collection',
            description='Second collection for multi-collection testing',
            alias=f'test-threats-2-{unique_suffix}',
            owner=self.organization,
            can_read=True,
            can_write=True
        )
        
        # Create objects for each collection
        for i, collection in enumerate([self.collection, collection2]):
            stix_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'spec_version': '2.1',
                'pattern': f"[ipv4-addr:value = '10.0.{i}.1']",
                'labels': ['malicious-activity'],
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat(),
            }
            
            stix_object = STIXObject.objects.create(
                stix_id=stix_data['id'],
                stix_type='indicator',
                created=timezone.now(),
                modified=timezone.now(),
                raw_data=stix_data,
                source_organization=self.organization,
                created_by=self.user
            )
            
            collection.stix_objects.add(stix_object)
        
        # Generate bundles for each collection
        bundle1 = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.organization
        )
        
        bundle2 = generate_bundle_from_collection(
            collection2,
            requesting_organization=self.organization
        )
        
        # Verify both bundles are distinct
        self.assertIsNotNone(bundle1)
        self.assertIsNotNone(bundle2)
        self.assertNotEqual(bundle1['id'], bundle2['id'])
        
        # Each should contain their respective objects (excluding owner identity)
        bundle1_objects = [obj for obj in bundle1['objects'] if obj['type'] not in ['bundle', 'identity']]
        bundle2_objects = [obj for obj in bundle2['objects'] if obj['type'] not in ['bundle', 'identity']]
        
        self.assertEqual(len(bundle1_objects), 1)
        self.assertEqual(len(bundle2_objects), 1)
        
        # Objects should be different
        bundle1_pattern = bundle1_objects[0]['pattern']
        bundle2_pattern = bundle2_objects[0]['pattern']
        self.assertNotEqual(bundle1_pattern, bundle2_pattern)
    
    def test_feed_update_workflow(self):
        """Test updating feeds and collections."""
        # Create initial feed
        unique_suffix = str(uuid.uuid4())[:8]
        feed = Feed.objects.create(
            title='Updatable Feed',
            description='Feed that will be updated',
            alias=f'updatable-feed-{unique_suffix}',
            collection=self.collection,
            organization=self.organization,
            created_by=self.user,
            is_public=False,
            anonymization_level=AnonymizationLevel.MEDIUM.value
        )
        
        # Add initial object
        initial_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[url:value = 'http://initial.malware.com']",
            'labels': ['malicious-activity'],
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
        }
        
        initial_object = STIXObject.objects.create(
            stix_id=initial_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=initial_data,
            source_organization=self.organization,
            created_by=self.user
        )
        
        self.collection.stix_objects.add(initial_object)
        
        # Generate initial bundle
        initial_bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.organization
        )
        
        initial_count = len([obj for obj in initial_bundle['objects'] if obj['type'] != 'bundle'])
        
        # Add new object to collection
        new_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[url:value = 'http://updated.malware.com']",
            'labels': ['malicious-activity'],
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
        }
        
        new_object = STIXObject.objects.create(
            stix_id=new_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=new_data,
            source_organization=self.organization,
            created_by=self.user
        )
        
        self.collection.stix_objects.add(new_object)
        
        # Generate updated bundle
        updated_bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.organization
        )
        
        updated_count = len([obj for obj in updated_bundle['objects'] if obj['type'] != 'bundle'])
        
        # Should have one more object
        self.assertEqual(updated_count, initial_count + 1)
        
        # Update feed properties
        feed.description = 'Updated feed description'
        feed.is_public = True
        feed.anonymization_level = AnonymizationLevel.HIGH.value
        feed.save()
        
        # Verify updates
        updated_feed = Feed.objects.get(id=feed.id)
        self.assertEqual(updated_feed.description, 'Updated feed description')
        self.assertTrue(updated_feed.is_public)
        self.assertEqual(updated_feed.anonymization_level, AnonymizationLevel.HIGH.value)
    
    def test_error_recovery_workflow(self):
        """Test workflow error handling and recovery."""
        # Create collection with problematic data
        problematic_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[invalid:syntax = 'this will cause issues'",
            'labels': ['malicious-activity'],
        }
        
        problematic_object = STIXObject.objects.create(
            stix_id=problematic_data['id'],
            stix_type='indicator',
            raw_data=problematic_data,
            source_organization=self.organization,
            created_by=self.user
        )
        
        self.collection.stix_objects.add(problematic_object)
        
        # Add valid object as well
        valid_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[domain-name:value = 'valid.example.com']",
            'labels': ['malicious-activity'],
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
        }
        
        valid_object = STIXObject.objects.create(
            stix_id=valid_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=valid_data,
            source_organization=self.organization,
            created_by=self.user
        )
        
        self.collection.stix_objects.add(valid_object)
        
        try:
            bundle = generate_bundle_from_collection(
                self.collection,
                requesting_organization=self.organization
            )
            
            if bundle:
                bundle_objects = [obj for obj in bundle['objects'] if obj['type'] != 'bundle']
                self.assertGreaterEqual(len(bundle_objects), 1)
                
                # Should contain the valid object
                valid_in_bundle = any(
                    obj.get('id') == valid_data['id'] 
                    for obj in bundle_objects
                )
                self.assertTrue(valid_in_bundle)
                
        except Exception as e:
            # If it fails, should be a controlled failure
            self.assertIsInstance(e, (ValueError, TypeError, KeyError))
    
    def test_performance_workflow(self):
        """Test workflow performance with realistic data volumes."""
        # Create multiple objects
        object_count = 25
        stix_objects = []
        
        for i in range(object_count):
            stix_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'spec_version': '2.1',
                'pattern': f"[ipv4-addr:value = '192.168.{i // 256}.{i % 256}']",
                'labels': ['malicious-activity'],
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat(),
                'description': f'Test indicator {i} for performance testing'
            }
            
            stix_object = STIXObject.objects.create(
                stix_id=stix_data['id'],
                stix_type='indicator',
                created=timezone.now(),
                modified=timezone.now(),
                raw_data=stix_data,
                source_organization=self.organization,
                created_by=self.user
            )
            
            stix_objects.append(stix_object)
            self.collection.stix_objects.add(stix_object)
        
        # Measure bundle generation performance
        import time
        start_time = time.time()
        
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.organization
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify results (excluding owner identity)
        self.assertIsNotNone(bundle)
        bundle_objects = [obj for obj in bundle['objects'] if obj['type'] not in ['bundle', 'identity']]
        self.assertEqual(len(bundle_objects), object_count)
        
        # Performance should be reasonable
        self.assertLess(processing_time, 15.0)  # Should complete within 15 seconds
        
        # Test with anonymization (external org)
        unique_suffix = str(uuid.uuid4())[:8]
        external_org = Organization.objects.create(
            name=f'Performance Test External {unique_suffix}',
            organization_type='commercial',
            contact_email=f'perf_{unique_suffix}@test.com',
            created_by=self.user
        )
        
        start_time = time.time()
        
        anonymized_bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=external_org
        )
        
        end_time = time.time()
        anonymization_time = end_time - start_time
    
        self.assertLess(anonymization_time, 20.0) 
        self.assertIsNotNone(anonymized_bundle)
        
        anonymized_objects = [obj for obj in anonymized_bundle['objects'] if obj['type'] not in ['bundle', 'identity']]
        self.assertEqual(len(anonymized_objects), object_count)