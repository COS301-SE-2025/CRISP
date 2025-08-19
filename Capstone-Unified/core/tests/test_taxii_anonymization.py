"""
TAXII Anonymization Integration Tests
Tests TAXII 2.x endpoints with anonymization capabilities
"""

import json
import uuid
from datetime import datetime, timedelta
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

User = get_user_model()
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from core.models.models import (
    Organization, STIXObject, Collection, CollectionObject,
    TrustLevel, TrustRelationship, Feed
)
from core.patterns.strategy.enums import AnonymizationLevel
from core.patterns.strategy.context import AnonymizationContext
from core.taxii.views import TAXIIBaseView


class TAXIIAnonymizationTestCase(TransactionTestCase):
    """Base test case for TAXII anonymization tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]

        self.user1 = User.objects.create_user(
            username=f'user1_{unique_suffix}',
            email=f'user1_{unique_suffix}@example.com', 
            password='testpass'
        )

        self.user2 = User.objects.create_user(
            username=f'user2_{unique_suffix}',
            email=f'user2_{unique_suffix}@example.com',
            password='testpass'
        )
        
        # Create test organizations
        self.org1 = Organization.objects.create(
            name=f'Test Org 1 {unique_suffix}',        
            organization_type='university',
            contact_email=f'security1_{unique_suffix}@test.edu',
            created_by=self.user1
        )
        
        self.org2 = Organization.objects.create(
            name=f'Test Org 2 {unique_suffix}',     
            organization_type='commercial', 
            contact_email=f'security2_{unique_suffix}@test.com',
            created_by=self.user2
        )

        # Explicitly set organization for users
        self.user1.organization = self.org1
        self.user1.save()
        self.user2.organization = self.org2
        self.user2.save()
        
        # Create a TrustLevel for the relationship
        self.medium_trust_level = TrustLevel.objects.create(
            name=f'Medium Trust {unique_suffix}',
            level='trusted',
            description='Medium trust level for testing anonymization',
            numerical_value=50, # Corresponds to MEDIUM anonymization
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='system'
        )

        # Create an active TrustRelationship between org1 and org2
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust_level,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            anonymization_level='partial', # Explicitly set for clarity
            access_level='read',
            created_by=self.user1
        )
        
        # Create sample STIX objects
        self.indicator_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[domain-name:value = 'malicious.example.com'] AND [email-addr:value = 'attacker@evil.org']",
            'labels': ['malicious-activity'],
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'description': 'Malicious domain and email used in phishing campaign targeting student@university.edu'
        }
        
        self.stix_object = STIXObject.objects.create(
            stix_id=self.indicator_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=self.indicator_data,
            source_organization=self.org1,
            created_by=self.user1
        )
        
        # Create collection with UNIQUE alias
        self.collection = Collection.objects.create(
            title='Test Collection',
            description='Test collection for TAXII anonymization',
            alias=f'test-collection-{unique_suffix}',
            owner=self.org1,
            default_anonymization_level=AnonymizationLevel.MEDIUM.value
        )
        
        # Add object to collection
        CollectionObject.objects.create(
            collection=self.collection,
            stix_object=self.stix_object
        )
        
        # Set up API clients
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)


class TAXIIBaseViewTests(TAXIIAnonymizationTestCase):
    """Test the TAXIIBaseView anonymization methods."""
    
    def setUp(self):
        super().setUp()
        self.view = TAXIIBaseView()
    
    def test_get_requesting_organization(self):
        """Test getting the requesting organization from the user."""
        # Test with authenticated user
        self.view.request = MagicMock()
        self.view.request.user = self.user1
        
        org = self.view.get_requesting_organization()
        self.assertEqual(org, self.org1)
        
        # Test with unauthenticated user
        self.view.request.user = MagicMock()
        self.view.request.user.is_authenticated = False
        
        org = self.view.get_requesting_organization()
        self.assertIsNone(org)
    
    def test_apply_anonymization(self):
        """Test applying anonymization to STIX objects."""
        # Create test data with sensitive information
        stix_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'pattern': "[email-addr:value = 'student@university.edu']",
            'labels': ['malicious-activity']
        }
        
        stix_object = STIXObject.objects.create(
            stix_id=stix_data['id'],
            stix_type='indicator',
            raw_data=stix_data,
            source_organization=self.org1,
            created_by=self.user1
        )
        
        # Apply anonymization for external organization
        anonymized_data = self.view.apply_anonymization(
            stix_object, 
            requesting_org=self.org2
        )
        
        # Check that anonymization was applied
        self.assertIn('[ANON:', str(anonymized_data))
        self.assertIn('x_crisp_anonymized', str(anonymized_data))


class TAXIIDiscoveryTests(TAXIIAnonymizationTestCase):
    """Test TAXII discovery endpoint."""
    
    def test_discovery_endpoint(self):
        """Test the TAXII discovery endpoint returns proper structure."""
        response = self.client1.get('/taxii2/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check required TAXII 2.x discovery fields
        self.assertIn('title', data)
        self.assertIn('description', data)
        self.assertIn('api_roots', data)
        self.assertIn('contact', data)


class TAXIICollectionsTests(TAXIIAnonymizationTestCase):
    """Test TAXII collections endpoint with anonymization."""
    
    def test_collections_list_authenticated(self):
        """Test collections list for authenticated user."""
        response = self.client1.get('/taxii2/collections/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should see collections owned by same org
        self.assertIn('collections', data)
        collections = data['collections']
        self.assertTrue(len(collections) > 0)
        
        # Verify collection structure
        collection = collections[0]
        self.assertIn('id', collection)
        self.assertIn('title', collection)
        self.assertIn('can_read', collection)
        self.assertIn('can_write', collection)
    
    def test_collections_list_different_org(self):
        """Test collections list for different organization."""
        response = self.client2.get('/taxii2/collections/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have limited access to other org's collections
        collections = data['collections']
        # Verify access control is applied
        for collection in collections:
            self.assertTrue(collection.get('can_read', False))


class TAXIICollectionObjectsTests(TAXIIAnonymizationTestCase):
    """Test TAXII collection objects endpoint with anonymization."""
    
    def test_get_objects_same_org(self):
        """Test getting objects from same organization."""
        response = self.client1.get(f'/taxii2/collections/{self.collection.id}/objects/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should see all objects without anonymization
        self.assertIn('objects', data)
        objects = data['objects']
        self.assertTrue(len(objects) > 0)
        
        # Verify no anonymization applied for same org
        indicator = objects[0]
        original_pattern = self.indicator_data['pattern']
        self.assertEqual(indicator['pattern'], original_pattern)
    
    def test_get_objects_different_org(self):
        """Test getting objects from different organization."""
        response = self.client2.get(f'/taxii2/collections/{self.collection.id}/objects/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should see anonymized objects
        objects = data['objects']
        if len(objects) > 0:
            indicator = objects[0]
            # Pattern should be anonymized for different org
            self.assertNotEqual(indicator['pattern'], self.indicator_data['pattern'])
    
    def test_get_objects_with_filters(self):
        """Test getting objects with TAXII filters."""
        # Test with type filter
        response = self.client1.get(
            f'/taxii2/collections/{self.collection.id}/objects/',
            {'match[type]': 'indicator'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # All returned objects should be indicators
        objects = data['objects']
        for obj in objects:
            self.assertEqual(obj['type'], 'indicator')
    
    def test_get_objects_with_anonymization_failure(self):
        """Test handling of anonymization failures."""
        # Create object with complex anonymization requirements
        complex_data = {
            'type': 'malware',
            'id': f'malware--{uuid.uuid4()}',
            'labels': ['trojan'],
            'name': 'StudentGradeHacker',
            'description': 'Targets university.edu email systems'
        }
        
        complex_object = STIXObject.objects.create(
            stix_id=complex_data['id'],
            stix_type='malware',
            raw_data=complex_data,
            source_organization=self.org1,
            created_by=self.user1
        )
        
        self.collection.stix_objects.add(complex_object)
        
        response = self.client2.get(f'/taxii2/collections/{self.collection.id}/objects/')
        
        # Should handle gracefully even if anonymization fails
        self.assertIn(response.status_code, [200, 207])  # 207 for partial success


class TAXIIObjectTests(TAXIIAnonymizationTestCase):
    """Test TAXII individual object endpoint."""
    
    def test_get_object_same_org(self):
        """Test getting single object from same organization."""
        response = self.client1.get(
            f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        if 'objects' in data:
            # TAXII objects endpoint returns objects array
            objects = data['objects']
            self.assertGreater(len(objects), 0)
            obj = objects[0]
        else:
            # Single object response
            obj = data
        
        self.assertEqual(obj['id'], self.stix_object.stix_id)
        self.assertEqual(obj['pattern'], self.indicator_data['pattern'])
    
    def test_get_object_different_org(self):
        """Test getting single object from different organization."""
        response = self.client2.get(
            f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        

        if 'objects' in data:
            # TAXII objects endpoint returns objects array
            objects = data['objects']
            self.assertGreater(len(objects), 0)
            obj = objects[0]
        else:
            # Single object response
            obj = data
        
        self.assertEqual(obj['id'], self.stix_object.stix_id)
        self.assertNotEqual(obj['pattern'], self.indicator_data['pattern'])
    
    def test_get_nonexistent_object(self):
        """Test getting non-existent object."""
        fake_id = f'indicator--{uuid.uuid4()}'
        response = self.client1.get(
            f'/taxii2/collections/{self.collection.id}/objects/{fake_id}/'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_object_anonymization_failure(self):
        """Test handling anonymization failure for single object."""
        # Mock anonymization failure
        with patch('core.patterns.strategy.context.AnonymizationContext.anonymize') as mock_anonymize:
            mock_anonymize.side_effect = Exception("Anonymization failed")
            
            response = self.client2.get(
                f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
            )
            
            self.assertIn(response.status_code, [200, 500])


class TAXIIManifestTests(TAXIIAnonymizationTestCase):
    """Test TAXII manifest endpoint."""
    
    def test_get_manifest(self):
        """Test getting collection manifest."""
        response = self.client1.get(f'/taxii2/collections/{self.collection.id}/manifest/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return manifest structure
        self.assertIn('objects', data)
        objects = data['objects']
        
        # Should include our test object
        object_ids = [obj['id'] for obj in objects]
        self.assertIn(self.stix_object.stix_id, object_ids)


class TAXIISecurityTests(TAXIIAnonymizationTestCase):
    """Test TAXII security and access control."""
    
    def test_unauthenticated_access(self):
        """Test unauthenticated access to TAXII endpoints."""
        client = APIClient()  # No authentication
        
        response = client.get('/taxii2/collections/')
        # Should either redirect to login or return 401/403
        self.assertIn(response.status_code, [401, 403, 302])
    
    def test_cross_org_data_protection(self):
        """Test that organizations cannot access each other's private data."""
        # Create private collection for org1
        unique_suffix = str(uuid.uuid4())[:8]
        private_collection = Collection.objects.create(
            title='Private Collection',
            description='Private collection for org1',
            alias=f'private-collection-{unique_suffix}',
            owner=self.org1,
            can_read=False,
            can_write=False
        )
        
        # Org2 should not be able to access
        response = self.client2.get(f'/taxii2/collections/{private_collection.id}/')
        self.assertIn(response.status_code, [403, 404])


class TAXIIPerformanceTests(TAXIIAnonymizationTestCase):
    """Test TAXII performance with anonymization."""
    
    def test_large_collection_performance(self):
        """Test performance with large collections."""
        # Create multiple objects
        for i in range(10):
            stix_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'pattern': f"[ipv4-addr:value = '192.168.1.{i}']",
                'labels': ['malicious-activity']
            }
            
            stix_object = STIXObject.objects.create(
                stix_id=stix_data['id'],
                stix_type='indicator',
                raw_data=stix_data,
                source_organization=self.org1,
                created_by=self.user1
            )
            
            self.collection.stix_objects.add(stix_object)
        
        # Test response time
        import time
        start_time = time.time()
        
        response = self.client2.get(f'/taxii2/collections/{self.collection.id}/objects/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 5.0)


class TAXIIIntegrationValidationTests(TAXIIAnonymizationTestCase):
    """Test TAXII integration validation."""
    
    def test_stix_compliance_in_responses(self):
        """Test that TAXII responses contain valid STIX objects."""
        response = self.client1.get(f'/taxii2/collections/{self.collection.id}/objects/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Validate STIX compliance
        for stix_object in data['objects']:
            # Every STIX object must have these fields
            self.assertIn('type', stix_object)
            self.assertIn('id', stix_object)
            self.assertIn('spec_version', stix_object)
            
            # ID should follow STIX format
            self.assertTrue(stix_object['id'].startswith(f"{stix_object['type']}--"))
    
    def test_anonymization_metadata_consistency(self):
        """Test that anonymization metadata is consistent."""
        response = self.client2.get(f'/taxii2/collections/{self.collection.id}/objects/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that anonymized objects maintain metadata consistency
        for stix_object in data['objects']:
            # Basic structure should be preserved
            self.assertIn('type', stix_object)
            self.assertIn('id', stix_object)
            
            # Anonymization should not break STIX compliance
            if 'pattern' in stix_object:
                # Pattern should still be valid STIX pattern format
                pattern = stix_object['pattern']
                self.assertTrue(pattern.startswith('['))
                self.assertTrue(pattern.endswith(']'))
    
    def test_content_type_headers(self):
        """Test that TAXII endpoints return correct content types."""
        response = self.client1.get('/taxii2/')
        self.assertIn('application/', response['Content-Type'])
        
        response = self.client1.get('/taxii2/collections/')
        self.assertIn('application/', response['Content-Type'])
        
        response = self.client1.get(f'/taxii2/collections/{self.collection.id}/objects/')
        # TAXII endpoints return STIX-specific content types
        self.assertIn('application/', response['Content-Type'])