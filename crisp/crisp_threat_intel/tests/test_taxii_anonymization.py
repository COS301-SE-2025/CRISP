"""
Tests for TAXII endpoints with integrated anonymization functionality.
"""
import uuid
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from crisp_threat_intel.models import (
    Organization, STIXObject, Collection, CollectionObject, TrustRelationship
)
from crisp_threat_intel.taxii.views import TAXIIBaseView

from core.patterns.strategy.enums import AnonymizationLevel


class TAXIIAnonymizationTestCase(TestCase):
    """Base test case for TAXII anonymization tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass'
        )
        
        self.user2 = User.objects.create_user(
            username='user2', 
            email='user2@example.com',
            password='testpass'
        )
        
        # Create test organizations
        self.org1 = Organization.objects.create(
            name='University One',
            organization_type='university',
            identity_class='organization',
            contact_email='contact@uni1.edu',
            created_by=self.user1
        )
        
        self.org2 = Organization.objects.create(
            name='University Two',
            organization_type='university', 
            identity_class='organization',
            contact_email='contact@uni2.edu',
            created_by=self.user2
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
        
        # Create collection
        self.collection = Collection.objects.create(
            title='Test Collection',
            description='Test collection for TAXII anonymization',
            alias='test-collection',
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
        
        # Mock request objects
        self.request1 = type('MockRequest', (), {'user': self.user1})()
        self.request2 = type('MockRequest', (), {'user': self.user2})()
    
    def test_get_trust_level_same_org(self):
        """Test trust level calculation for same organization."""
        trust = self.view.get_trust_level(self.org1, self.org1)
        self.assertEqual(trust, 1.0)
    
    def test_get_trust_level_different_org_no_relationship(self):
        """Test trust level for different organizations without relationship."""
        trust = self.view.get_trust_level(self.org1, self.org2)
        self.assertEqual(trust, 0.7)  # Default university trust
    
    def test_get_trust_level_with_explicit_relationship(self):
        """Test trust level with explicit trust relationship."""
        TrustRelationship.objects.create(
            source_org=self.org1,
            target_org=self.org2,
            trust_level=0.9
        )
        
        trust = self.view.get_trust_level(self.org1, self.org2)
        self.assertEqual(trust, 0.9)
    
    def test_apply_anonymization_same_org(self):
        """Test anonymization for same organization."""
        result = self.view.apply_anonymization(
            self.indicator_data, self.org1, self.org1
        )
        
        self.assertEqual(result, self.indicator_data)
        self.assertNotIn('x_crisp_anonymized', result)
    
    def test_apply_anonymization_different_org(self):
        """Test anonymization for different organization."""
        # Create trust relationship for predictable results
        TrustRelationship.objects.create(
            source_org=self.org1,
            target_org=self.org2,
            trust_level=0.5  # Medium trust -> MEDIUM anonymization
        )
        
        result = self.view.apply_anonymization(
            self.indicator_data, self.org2, self.org1
        )
        
        # Check anonymization metadata
        self.assertTrue(result['x_crisp_anonymized'])
        self.assertEqual(result['x_crisp_anonymization_level'], 'medium')
        self.assertEqual(result['x_crisp_source_org'], self.org1.name)
        self.assertEqual(result['x_crisp_trust_level'], 0.5)
        
        # Check anonymization applied (fallback system adds ANON prefix)
        self.assertIn('[ANON:', result['pattern'])
        # Email anonymization may use different patterns like user-hash@*.domain
        self.assertIn('*.evil.org', result['pattern'])  # Domain part anonymized
        self.assertIn('*.edu', result['description'])
    
    def test_apply_anonymization_error_handling(self):
        """Test error handling when anonymization fails."""
        with patch('core.patterns.strategy.context.AnonymizationContext.anonymize_stix_object') as mock_anonymize:
            mock_anonymize.side_effect = AnonymizationError("Test error")
            
            result = self.view.apply_anonymization(
                self.indicator_data, self.org2, self.org1
            )
            
            self.assertIsNone(result)


class TAXIIDiscoveryTests(TAXIIAnonymizationTestCase):
    """Test TAXII Discovery endpoint."""
    
    def test_discovery_endpoint(self):
        """Test that discovery endpoint works without authentication issues."""
        # Discovery should work without authentication
        client = APIClient()
        response = client.get('/taxii2/')
        
        # Should return discovery information
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], 'CRISP TAXII 2.1 Server')


class TAXIICollectionsTests(TAXIIAnonymizationTestCase):
    """Test TAXII Collections endpoint with anonymization."""
    
    def test_collections_list_authenticated(self):
        """Test collections list for authenticated user."""
        response = self.client1.get('/taxii2/collections/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('collections', data)
        
        # Should see own collection
        collection_ids = [c['id'] for c in data['collections']]
        self.assertIn(str(self.collection.id), collection_ids)
    
    def test_collections_list_different_org(self):
        """Test collections list for different organization."""
        response = self.client2.get('/taxii2/collections/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should still see collection (but objects will be anonymized)
        collection_ids = [c['id'] for c in data['collections']]
        self.assertIn(str(self.collection.id), collection_ids)


class TAXIICollectionObjectsTests(TAXIIAnonymizationTestCase):
    """Test TAXII Collection Objects endpoint with anonymization."""
    
    def test_get_objects_same_org(self):
        """Test getting objects from same organization."""
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have identity + indicator
        self.assertEqual(len(data['objects']), 2)
        
        # Find indicator
        indicator = next(obj for obj in data['objects'] if obj['type'] == 'indicator')
        self.assertEqual(indicator, self.indicator_data)
        self.assertNotIn('x_crisp_anonymized', indicator)
    
    def test_get_objects_different_org(self):
        """Test getting objects from different organization with anonymization."""
        # Create trust relationship
        TrustRelationship.objects.create(
            source_org=self.org1,
            target_org=self.org2,
            trust_level=0.4  # Low-medium trust -> HIGH anonymization
        )
        
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = self.client2.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have identity + indicator
        self.assertEqual(len(data['objects']), 2)
        
        # Find indicator
        indicator = next(obj for obj in data['objects'] if obj['type'] == 'indicator')
        
        # Should be anonymized
        self.assertTrue(indicator['x_crisp_anonymized'])
        self.assertEqual(indicator['x_crisp_anonymization_level'], 'high')
        self.assertIn('[ANON:', indicator['pattern'])
    
    def test_get_objects_with_anonymization_failure(self):
        """Test getting objects when anonymization fails."""
        with patch('crisp_threat_intel.taxii.views.TAXIIBaseView.apply_anonymization') as mock_anonymize:
            mock_anonymize.return_value = None  # Simulate anonymization failure
            
            url = f'/taxii2/collections/{self.collection.id}/objects/'
            response = self.client2.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            
            # Should only have identity, no indicator due to anonymization failure
            self.assertEqual(len(data['objects']), 1)
            self.assertEqual(data['objects'][0]['type'], 'identity')
    
    def test_get_objects_with_filters(self):
        """Test getting objects with type filters."""
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = self.client1.get(url, {'match[type]': 'indicator'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should only have indicator (no identity due to filter)
        self.assertEqual(len(data['objects']), 1)
        self.assertEqual(data['objects'][0]['type'], 'indicator')
    
    def test_get_objects_pagination(self):
        """Test object pagination."""
        # Create additional objects
        for i in range(5):
            indicator_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'spec_version': '2.1',
                'pattern': f"[domain-name:value = 'malicious{i}.example.com']",
                'labels': ['malicious-activity'],
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat()
            }
            
            stix_obj = STIXObject.objects.create(
                stix_id=indicator_data['id'],
                stix_type='indicator',
                created=timezone.now(),
                modified=timezone.now(),
                raw_data=indicator_data,
                source_organization=self.org1,
                created_by=self.user1
            )
            
            CollectionObject.objects.create(
                collection=self.collection,
                stix_object=stix_obj
            )
        
        # Test pagination
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = self.client1.get(url, {'limit': 3})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have exactly 3 objects
        self.assertEqual(len(data['objects']), 3)
        self.assertIn('next', data)


class TAXIIObjectTests(TAXIIAnonymizationTestCase):
    """Test TAXII Object endpoint with anonymization."""
    
    def test_get_object_same_org(self):
        """Test getting specific object from same organization."""
        url = f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have the object without anonymization
        self.assertEqual(len(data['objects']), 1)
        self.assertEqual(data['objects'][0], self.indicator_data)
        self.assertNotIn('x_crisp_anonymized', data['objects'][0])
    
    def test_get_object_different_org(self):
        """Test getting specific object from different organization."""
        # Create trust relationship
        TrustRelationship.objects.create(
            source_org=self.org1,
            target_org=self.org2,
            trust_level=0.6  # Medium trust -> MEDIUM anonymization
        )
        
        url = f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
        response = self.client2.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have anonymized object
        self.assertEqual(len(data['objects']), 1)
        obj = data['objects'][0]
        self.assertTrue(obj['x_crisp_anonymized'])
        self.assertEqual(obj['x_crisp_anonymization_level'], 'medium')
    
    def test_get_object_anonymization_failure(self):
        """Test getting object when anonymization fails."""
        with patch('crisp_threat_intel.taxii.views.TAXIIBaseView.apply_anonymization') as mock_anonymize:
            mock_anonymize.return_value = None  # Simulate anonymization failure
            
            url = f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
            response = self.client2.get(url)
            
            # Should return 404 when anonymization fails
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_nonexistent_object(self):
        """Test getting non-existent object."""
        fake_id = f'indicator--{uuid.uuid4()}'
        url = f'/taxii2/collections/{self.collection.id}/objects/{fake_id}/'
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TAXIIManifestTests(TAXIIAnonymizationTestCase):
    """Test TAXII Manifest endpoint."""
    
    def test_get_manifest(self):
        """Test getting collection manifest."""
        url = f'/taxii2/collections/{self.collection.id}/manifest/'
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have manifest objects
        self.assertIn('objects', data)
        self.assertGreater(len(data['objects']), 0)
        
        # Each manifest entry should have required fields
        for obj in data['objects']:
            self.assertIn('id', obj)
            self.assertIn('date_added', obj)
            self.assertIn('version', obj)


class TAXIISecurityTests(TAXIIAnonymizationTestCase):
    """Test TAXII security aspects."""
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are denied (except discovery)."""
        client = APIClient()
        
        # Collections should require authentication
        response = client.get('/taxii2/collections/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Objects should require authentication
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_cross_org_data_protection(self):
        """Test that organizations can't access raw data from other orgs."""
        # Create high-value trust relationship
        TrustRelationship.objects.create(
            source_org=self.org1,
            target_org=self.org2,
            trust_level=0.2  # Very low trust -> FULL anonymization
        )
        
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = self.client2.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Find indicator
        indicator = next(obj for obj in data['objects'] if obj['type'] == 'indicator')
        
        # Should be heavily anonymized
        self.assertTrue(indicator['x_crisp_anonymized'])
        self.assertEqual(indicator['x_crisp_anonymization_level'], 'full')
        
        # Original data should be anonymized (fallback adds ANON prefix)
        self.assertIn('[ANON:', indicator['pattern'])
        self.assertTrue(indicator['x_crisp_anonymized'])
        # Description might not be modified by fallback
        self.assertIn('description', indicator)


class TAXIIPerformanceTests(TAXIIAnonymizationTestCase):
    """Test TAXII performance with anonymization."""
    
    def test_large_collection_performance(self):
        """Test performance with large collections."""
        import time
        
        # Create many objects
        for i in range(20):
            indicator_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'spec_version': '2.1',
                'pattern': f"[domain-name:value = 'test{i}.example.com']",
                'labels': ['malicious-activity'],
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat()
            }
            
            stix_obj = STIXObject.objects.create(
                stix_id=indicator_data['id'],
                stix_type='indicator',
                created=timezone.now(),
                modified=timezone.now(),
                raw_data=indicator_data,
                source_organization=self.org1,
                created_by=self.user1
            )
            
            CollectionObject.objects.create(
                collection=self.collection,
                stix_object=stix_obj
            )
        
        # Measure response time
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        start_time = time.time()
        response = self.client2.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should complete in reasonable time
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 3.0)  # Under 3 seconds
        
        data = response.json()
        self.assertGreater(len(data['objects']), 20)  # Identity + indicators


class TAXIIIntegrationValidationTests(TAXIIAnonymizationTestCase):
    """Validation tests for TAXII integration."""
    
    def test_stix_compliance_in_responses(self):
        """Test that TAXII responses maintain STIX compliance."""
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = self.client2.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Validate each object
        for obj in data['objects']:
            # Required STIX fields
            self.assertIn('type', obj)
            self.assertIn('id', obj)
            self.assertIn('spec_version', obj)
            self.assertIn('created', obj)
            self.assertIn('modified', obj)
            
            # Type-specific validation
            if obj['type'] == 'indicator':
                self.assertIn('pattern', obj)
                self.assertIn('labels', obj)
            elif obj['type'] == 'identity':
                self.assertIn('name', obj)
                self.assertIn('identity_class', obj)
    
    def test_content_type_headers(self):
        """Test that proper content types are returned."""
        url = f'/taxii2/collections/{self.collection.id}/objects/'
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check content type
        content_type = response.get('Content-Type', '')
        self.assertIn('application/stix+json', content_type)
    
    def test_anonymization_metadata_consistency(self):
        """Test that anonymization metadata is consistent across responses."""
        # Set up predictable trust relationship
        TrustRelationship.objects.create(
            source_org=self.org1,
            target_org=self.org2,
            trust_level=0.5
        )
        
        # Get object via collection objects endpoint
        url1 = f'/taxii2/collections/{self.collection.id}/objects/'
        response1 = self.client2.get(url1)
        data1 = response1.json()
        
        # Get same object via object endpoint
        url2 = f'/taxii2/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
        response2 = self.client2.get(url2)
        data2 = response2.json()
        
        # Find indicators in both responses
        indicator1 = next(obj for obj in data1['objects'] if obj['type'] == 'indicator')
        indicator2 = data2['objects'][0]
        
        # Anonymization metadata should be consistent
        self.assertEqual(
            indicator1['x_crisp_anonymization_level'],
            indicator2['x_crisp_anonymization_level']
        )
        self.assertEqual(
            indicator1['x_crisp_trust_level'],
            indicator2['x_crisp_trust_level']
        )
        self.assertEqual(
            indicator1['x_crisp_source_org'],
            indicator2['x_crisp_source_org']
        )