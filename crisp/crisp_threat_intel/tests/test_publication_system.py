"""
Test Publication System - TAXII, Feeds, and Anonymization
Tests focused on threat intelligence publication and sharing functionality.
"""
import json
import uuid
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from crisp_threat_intel.models import (
    Organization, Collection, Feed, STIXObject, CollectionObject
)
from crisp_threat_intel.management.commands.publish_feeds import Command as PublishCommand
from core.patterns.strategy.context import AnonymizationContext
from core.patterns.strategy.enums import AnonymizationLevel
from core.patterns.strategy.strategies import AnonymizationStrategyFactory
from crisp_threat_intel.utils import publish_feed


class TAXIIEndpointsTest(TestCase):
    """Test TAXII 2.1 endpoints for publication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_publisher',
            password='testpass123',
            email='publisher@test.com'
        )
        
        self.org = Organization.objects.create(
            name='Test Publisher Org',
            identity_class='organization',
            stix_id=f'identity--{uuid.uuid4()}',
            created_by=self.user
        )
        
        self.collection = Collection.objects.create(
            title='Test TAXII Collection',
            description='Collection for TAXII testing',
            can_read=True,
            can_write=True,
            owner=self.org
        )
        
        stix_id = f'indicator--{uuid.uuid4()}'
        self.stix_object = STIXObject.objects.create(
            stix_id=stix_id,
            stix_type='indicator',
            spec_version='2.1',
            raw_data={
                'type': 'indicator',
                'id': stix_id,
                'created': '2023-01-01T00:00:00.000Z',
                'modified': '2023-01-01T00:00:00.000Z',
                'pattern': "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
                'labels': ['malicious-activity']
            },
            created_by=self.user,
            source_organization=self.org
        )
        
        CollectionObject.objects.create(
            collection=self.collection,
            stix_object=self.stix_object
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_discovery_endpoint(self):
        """Test TAXII discovery endpoint"""
        response = self.client.get('/taxii2/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('title', data)
        self.assertIn('api_roots', data)
        self.assertEqual(data['title'], 'CRISP Threat Intelligence Platform')
    
    def test_collections_endpoint(self):
        """Test collections listing endpoint"""
        response = self.client.get('/taxii2/collections/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('collections', data)
        self.assertEqual(len(data['collections']), 1)
        
        collection_data = data['collections'][0]
        self.assertEqual(collection_data['title'], 'Test TAXII Collection')
        self.assertTrue(collection_data['can_read'])
        self.assertTrue(collection_data['can_write'])
    
    def test_collection_detail_endpoint(self):
        """Test individual collection endpoint"""
        response = self.client.get(f'/taxii2/collections/{self.collection.id}/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['title'], 'Test TAXII Collection')
        self.assertTrue(data['can_read'])
    
    def test_collection_objects_endpoint(self):
        """Test collection objects retrieval"""
        response = self.client.get(f'/taxii2/collections/{self.collection.id}/objects/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), 1)
        
        obj = data['objects'][0]
        self.assertEqual(obj['type'], 'indicator')
        self.assertIn('pattern', obj)
    
    def test_collection_objects_with_filters(self):
        """Test collection objects with query filters"""
        # Test type filter
        response = self.client.get(f'/taxii2/collections/{self.collection.id}/objects/?type=indicator', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['objects']), 1)
        
        # Test type filter with no matches
        response = self.client.get(f'/taxii2/collections/{self.collection.id}/objects/?type=malware', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['objects']), 0)
    
    def test_collection_objects_pagination(self):
        """Test collection objects pagination"""
        response = self.client.get(f'/taxii2/collections/{self.collection.id}/objects/?limit=1', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('objects', data)
        self.assertIn('more', data)
    
    def test_collection_objects_post(self):
        """Test adding objects to collection via POST"""
        new_object = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'created': '2023-01-01T00:00:00.000Z',
            'modified': '2023-01-01T00:00:00.000Z',
            'pattern': "[file:hashes.SHA256 = 'abc123']",
            'labels': ['malicious-activity']
        }
        
        post_data = {'objects': [new_object]}
        
        response = self.client.post(
            f'/taxii2/collections/{self.collection.id}/objects/',
            data=json.dumps(post_data),
            content_type='application/json',
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['success_count'], 1)
        self.assertEqual(len(data['failures']), 0)
    
    def test_object_detail_endpoint(self):
        """Test individual object endpoint"""
        response = self.client.get(
            f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), 1)
        
        obj = data['objects'][0]
        self.assertEqual(obj['id'], self.stix_object.stix_id)
    
    def test_manifest_endpoint(self):
        """Test collection manifest endpoint"""
        response = self.client.get(f'/taxii2/collections/{self.collection.id}/manifest/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), 1)
        
        manifest_obj = data['objects'][0]
        self.assertEqual(manifest_obj['id'], self.stix_object.stix_id)
        self.assertIn('date_added', manifest_obj)
        self.assertIn('version', manifest_obj)


class FeedPublicationTest(TestCase):
    """Test feed publication functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='feed_publisher',
            password='testpass123'
        )
        
        self.org = Organization.objects.create(
            name='Feed Publisher Org',
            identity_class='organization',
            stix_id=f'identity--{uuid.uuid4()}',
            created_by=self.user
        )
        
        self.collection = Collection.objects.create(
            title='Test Feed Collection',
            description='Collection for feed testing',
            can_read=True,
            can_write=True,
            owner=self.org
        )
        
        self.feed = Feed.objects.create(
            name='Test Publication Feed',
            collection=self.collection,
            status='active',
            created_by=self.user
        )
        
        # Add STIX objects to collection
        for i in range(3):
            stix_obj = STIXObject.objects.create(
                stix_id=f'indicator--{uuid.uuid4()}',
                stix_type='indicator',
                spec_version='2.1',
                raw_data={
                    'type': 'indicator',
                    'id': f'indicator--{uuid.uuid4()}',
                    'created': '2023-01-01T00:00:00.000Z',
                    'modified': '2023-01-01T00:00:00.000Z',
                    'pattern': f"[file:hashes.MD5 = 'hash{i}']",
                    'labels': ['malicious-activity']
                },
                created_by=self.user,
                source_organization=self.org
            )
            
            CollectionObject.objects.create(
                collection=self.collection,
                stix_object=stix_obj
            )
    
    def test_feed_publication_via_utils(self):
        """Test feed publication using utility function"""
        result = publish_feed(self.feed)
        
        self.assertIn('bundle_id', result)
        self.assertIn('object_count', result)
        self.assertGreater(result['object_count'], 0)
        
        # Refresh feed from database
        self.feed.refresh_from_db()
        self.assertIsNotNone(self.feed.last_published_time)
        self.assertEqual(self.feed.publish_count, 1)
    
    def test_publish_feeds_management_command_specific_feed(self):
        """Test publish_feeds command for specific feed"""
        command = PublishCommand()
        
        # Capture stdout
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Pass proper options dict
            command.handle(**{'feed_id': str(self.feed.id), 'dry_run': False, 'all': False})
            output = captured_output.getvalue()
            
            self.assertIn('Published feed:', output)
            self.assertIn(self.feed.name, output)
            
            # Check feed was actually published
            self.feed.refresh_from_db()
            self.assertIsNotNone(self.feed.last_published_time)
            
        finally:
            sys.stdout = old_stdout
    
    def test_publish_feeds_management_command_all_feeds(self):
        """Test publish_feeds command for all feeds"""
        command = PublishCommand()
        
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Pass proper options dict
            command.handle(**{'all': True, 'dry_run': False, 'feed_id': None})
            output = captured_output.getvalue()
            
            self.assertIn('Found 1 active feeds', output)
            self.assertIn('Published:', output)
            
        finally:
            sys.stdout = old_stdout
    
    def test_publish_feeds_management_command_dry_run(self):
        """Test publish_feeds command dry run"""
        command = PublishCommand()
        
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Pass proper options dict
            command.handle(**{'feed_id': str(self.feed.id), 'dry_run': True, 'all': False})
            output = captured_output.getvalue()
            
            self.assertIn('Would publish feed:', output)
            self.assertIn(self.feed.name, output)
            
            # Check feed was NOT actually published
            self.feed.refresh_from_db()
            self.assertIsNone(self.feed.last_published_time)
            
        finally:
            sys.stdout = old_stdout
    
    def test_publish_feeds_command_status(self):
        """Test publish_feeds command status display"""
        command = PublishCommand()
        
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Pass proper options dict
            command.handle(**{'feed_id': None, 'all': False, 'dry_run': False})
            output = captured_output.getvalue()
            
            self.assertIn('Feed Status:', output)
            self.assertIn(self.feed.name, output)
            self.assertIn('active', output)
            
        finally:
            sys.stdout = old_stdout


class AnonymizationTest(TestCase):
    """Test anonymization strategies for publication"""
    
    def setUp(self):
        self.sample_indicator = {
            'type': 'indicator',
            'id': 'indicator--test',
            'created': '2023-01-01T00:00:00.000Z',
            'modified': '2023-01-01T00:00:00.000Z',
            'pattern': "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            'labels': ['malicious-activity'],
            'description': 'Malware found at user@domain.com and 192.168.1.1'
        }
    
    def test_none_anonymization_strategy(self):
        """Test no anonymization strategy"""
        strategy = AnonymizationStrategyFactory.get_strategy('none')
        result = strategy.anonymize(self.sample_indicator, 1.0)
        
        # Should be unchanged
        self.assertEqual(result, self.sample_indicator)
    
    def test_domain_anonymization_strategy(self):
        """Test domain anonymization strategy"""
        strategy = AnonymizationStrategyFactory.get_strategy('domain')
        result = strategy.anonymize(self.sample_indicator, 0.5)
        
        # Should anonymize email and IP in description
        self.assertNotEqual(result['description'], self.sample_indicator['description'])
        self.assertIn('user@XXX.com', result['description'])
        self.assertIn('192.168.1.XXX', result['description'])
    
    def test_anonymization_strategy_factory_registration(self):
        """Test anonymization strategy registration"""
        # Test getting existing strategy
        strategy = AnonymizationStrategyFactory.get_strategy('none')
        self.assertIsNotNone(strategy)
        
        # Test getting non-existent strategy
        with self.assertRaises(ValueError):
            AnonymizationStrategyFactory.get_strategy('nonexistent')
    
    def test_anonymization_preserves_structure(self):
        """Test that anonymization preserves STIX structure"""
        strategy = AnonymizationStrategyFactory.get_strategy('domain')
        result = strategy.anonymize(self.sample_indicator, 0.5)
        
        # Core STIX fields should be preserved
        self.assertEqual(result['type'], self.sample_indicator['type'])
        self.assertEqual(result['id'], self.sample_indicator['id'])
        self.assertEqual(result['pattern'], self.sample_indicator['pattern'])
        self.assertEqual(result['labels'], self.sample_indicator['labels'])


class TAXIIAuthenticationTest(TestCase):
    """Test TAXII authentication and authorization"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='auth_test_user',
            password='testpass123'
        )
        
        self.org = Organization.objects.create(
            name='Auth Test Org',
            identity_class='organization',
            stix_id=f'identity--{uuid.uuid4()}',
            created_by=self.user
        )
        
        self.collection = Collection.objects.create(
            title='Auth Test Collection',
            description='Collection for auth testing',
            can_read=True,
            can_write=True,
            owner=self.org
        )
        
        self.client = APIClient()
    
    def test_unauthenticated_access_blocked(self):
        """Test that unauthenticated access is blocked"""
        response = self.client.get('/taxii2/collections/', follow=True)
        self.assertIn(response.status_code, [401, 403])  # Either is acceptable for unauthorized access
    
    def test_authenticated_access_allowed(self):
        """Test that authenticated access is allowed"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/taxii2/collections/', follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_cross_organization_access_blocked(self):
        """Test that cross-organization access is blocked"""
        # Create another user and organization
        other_user = User.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        
        other_org = Organization.objects.create(
            name='Other Org',
            identity_class='organization',
            stix_id=f'identity--{uuid.uuid4()}',
            created_by=other_user
        )
        
        other_collection = Collection.objects.create(
            title='Other Collection',
            description='Collection for other org',
            can_read=True,
            can_write=True,
            owner=other_org,
            alias=f'other-collection-{uuid.uuid4().hex[:8]}'
        )
        
        # Try to access other org's collection
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/taxii2/collections/{other_collection.id}/', follow=True)
        self.assertEqual(response.status_code, 404)


class PublicationWorkflowTest(TestCase):
    """Test end-to-end publication workflow"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='workflow_user',
            password='testpass123'
        )
        
        self.org = Organization.objects.create(
            name='Workflow Test Org',
            identity_class='organization',
            stix_id=f'identity--{uuid.uuid4()}',
            created_by=self.user
        )
        
        self.collection = Collection.objects.create(
            title='Workflow Test Collection',
            description='Collection for workflow testing',
            can_read=True,
            can_write=True,
            owner=self.org
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_complete_publication_workflow(self):
        """Test complete publication workflow from creation to consumption"""
        # Step 1: Create and add STIX objects to collection
        stix_object = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'created': '2023-01-01T00:00:00.000Z',
            'modified': '2023-01-01T00:00:00.000Z',
            'pattern': "[file:hashes.MD5 = 'workflow_test_hash']",
            'labels': ['malicious-activity'],
            'description': 'Test workflow indicator'
        }
        
        post_data = {'objects': [stix_object]}
        
        response = self.client.post(
            f'/taxii2/collections/{self.collection.id}/objects/',
            data=json.dumps(post_data),
            content_type='application/json',
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Create and publish feed
        feed = Feed.objects.create(
            name='Workflow Test Feed',
            collection=self.collection,
            status='active',
            created_by=self.user
        )
        
        result = publish_feed(feed)
        self.assertIn('bundle_id', result)
        self.assertGreater(result['object_count'], 0)
        
        # Step 3: Verify objects can be retrieved via TAXII
        response = self.client.get(f'/taxii2/collections/{self.collection.id}/objects/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['objects']), 1)
        
        retrieved_obj = data['objects'][0]
        self.assertEqual(retrieved_obj['type'], 'indicator')
        self.assertIn('workflow_test_hash', retrieved_obj['pattern'])
        
        # Step 4: Verify feed publication statistics
        feed.refresh_from_db()
        self.assertEqual(feed.publish_count, 1)
        self.assertIsNotNone(feed.last_published_time)


class PublicationErrorHandlingTest(TestCase):
    """Test error handling in publication system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='error_test_user',
            password='testpass123'
        )
        
        self.org = Organization.objects.create(
            name='Error Test Org',
            identity_class='organization',
            stix_id=f'identity--{uuid.uuid4()}',
            created_by=self.user
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_json_post(self):
        """Test handling of invalid JSON in POST requests"""
        collection = Collection.objects.create(
            title='Error Test Collection',
            description='Collection for error testing',
            can_read=True,
            can_write=True,
            owner=self.org,
            alias=f'error-collection-{uuid.uuid4().hex[:8]}'
        )
        
        response = self.client.post(
            f'/taxii2/collections/{collection.id}/objects/',
            data='invalid json',
            content_type='application/json',
            follow=True
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Invalid JSON', data['error'])
    
    def test_missing_objects_in_post(self):
        """Test handling of POST without objects field"""
        collection = Collection.objects.create(
            title='Error Test Collection',
            description='Collection for error testing',
            can_read=True,
            can_write=True,
            owner=self.org,
            alias=f'error-collection2-{uuid.uuid4().hex[:8]}'
        )
        
        post_data = {'not_objects': []}
        
        response = self.client.post(
            f'/taxii2/collections/{collection.id}/objects/',
            data=json.dumps(post_data),
            content_type='application/json',
            follow=True
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('objects', data['error'])
    
    def test_invalid_object_data(self):
        """Test handling of invalid STIX object data"""
        collection = Collection.objects.create(
            title='Error Test Collection',
            description='Collection for error testing',
            can_read=True,
            can_write=True,
            owner=self.org,
            alias=f'error-collection3-{uuid.uuid4().hex[:8]}'
        )
        
        # Object missing required fields
        invalid_object = {
            'type': 'indicator',
            # Missing 'id', 'pattern', 'labels', etc.
        }
        
        post_data = {'objects': [invalid_object]}
        
        response = self.client.post(
            f'/taxii2/collections/{collection.id}/objects/',
            data=json.dumps(post_data),
            content_type='application/json',
            follow=True
        )
        
        self.assertEqual(response.status_code, 207)  # Multi-status
        
        data = response.json()
        self.assertEqual(data['success_count'], 0)
        self.assertGreater(len(data['failures']), 0)
    
    def test_nonexistent_collection_access(self):
        """Test accessing non-existent collection"""
        fake_id = str(uuid.uuid4())
        
        response = self.client.get(f'/taxii2/collections/{fake_id}/', follow=True)
        self.assertEqual(response.status_code, 404)
    
    def test_nonexistent_object_access(self):
        """Test accessing non-existent object"""
        collection = Collection.objects.create(
            title='Error Test Collection',
            description='Collection for error testing',
            can_read=True,
            can_write=True,
            owner=self.org,
            alias=f'error-collection4-{uuid.uuid4().hex[:8]}'
        )
        
        fake_object_id = f'indicator--{uuid.uuid4()}'
        
        response = self.client.get(
            f'/taxii2/collections/{collection.id}/objects/{fake_object_id}/',
            follow=True
        )
        self.assertEqual(response.status_code, 404)