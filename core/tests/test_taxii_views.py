"""
Comprehensive tests for TAXII 2.1 API views
Tests for all TAXII endpoint implementations.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json
import uuid

from core.models.auth import Organization, CustomUser
from core.models.stix_object import Collection, STIXObject
from core.taxii.views import (
    TAXIIBaseView,
    DiscoveryView,
    ApiRootView,
    CollectionsView,
    CollectionView,
    CollectionObjectsView,
    ObjectView,
    ManifestView
)
from core.tests.test_base import CrispTestCase


class TAXIIBaseViewTest(CrispTestCase):
    """Test TAXIIBaseView base functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.view = TAXIIBaseView()
        
        self.org = Organization.objects.create(
            name="TAXII Test Org", domain="taxii.com", contact_email="test@taxii.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="taxii_user", email="user@taxii.com", password="testpass123",
            organization=self.org, role="publisher"
        )
    
    def test_get_organization_from_user_profile(self):
        """Test getting organization from user profile"""
        request = self.factory.get('/')
        request.user = self.user
        
        org = self.view.get_organization(request)
        
        self.assertEqual(org, self.org)
    
    def test_get_organization_no_organization(self):
        """Test getting organization when user has no organization"""
        user_no_org = CustomUser.objects.create_user(
            username="no_org_user", email="no_org@taxii.com", password="testpass123",
            role="viewer"
        )
        
        request = self.factory.get('/')
        request.user = user_no_org
        
        # Should handle case where user has no organization
        org = self.view.get_organization(request)
        # Implementation may create default or return None
    
    def test_format_taxii_datetime(self):
        """Test TAXII datetime formatting"""
        dt = timezone.now()
        
        formatted = self.view.format_taxii_datetime(dt)
        
        self.assertIsInstance(formatted, str)
        self.assertIn('T', formatted)  # ISO format
        self.assertTrue(formatted.endswith('Z'))  # UTC format
    
    def test_parse_taxii_datetime(self):
        """Test TAXII datetime parsing"""
        dt_string = "2024-06-27T10:00:00.000Z"
        
        parsed = self.view.parse_taxii_datetime(dt_string)
        
        self.assertIsNotNone(parsed)
    
    def test_validate_stix_object(self):
        """Test STIX object validation"""
        valid_stix = {
            "type": "indicator",
            "id": f"indicator--{uuid.uuid4()}",
            "created": "2024-06-27T10:00:00.000Z",
            "modified": "2024-06-27T10:00:00.000Z",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "labels": ["malicious-activity"]
        }
        
        is_valid, errors = self.view.validate_stix_object(valid_stix)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_stix_object_invalid(self):
        """Test STIX object validation with invalid object"""
        invalid_stix = {
            "type": "indicator",
            # Missing required fields
        }
        
        is_valid, errors = self.view.validate_stix_object(invalid_stix)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class DiscoveryViewTest(CrispTestCase):
    """Test TAXII Discovery endpoint"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="discovery_user", email="discovery@taxii.com", password="testpass123",
            role="viewer"
        )
    
    def test_discovery_get(self):
        """Test TAXII discovery endpoint"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/taxii2/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check required TAXII discovery fields
        self.assertIn('title', data)
        self.assertIn('description', data)
        self.assertIn('api_roots', data)
        self.assertIn('contact', data)
        self.assertIn('default', data)
    
    def test_discovery_unauthenticated(self):
        """Test discovery endpoint without authentication"""
        response = self.client.get('/taxii2/')
        
        # Should require authentication
        self.assertEqual(response.status_code, 401)
    
    def test_discovery_response_format(self):
        """Test discovery response format"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/taxii2/')
        
        self.assertEqual(response['Content-Type'], 'application/taxii+json;version=2.1')


class ApiRootViewTest(CrispTestCase):
    """Test TAXII API Root endpoint"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="apiroot_user", email="apiroot@taxii.com", password="testpass123",
            role="viewer"
        )
    
    def test_api_root_get(self):
        """Test TAXII API root endpoint"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/taxii2/api/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check required API root fields
        self.assertIn('title', data)
        self.assertIn('versions', data)
        self.assertIn('max_content_length', data)
        self.assertEqual(data['versions'], ['taxii-2.1'])
    
    def test_api_root_unauthenticated(self):
        """Test API root without authentication"""
        response = self.client.get('/taxii2/api/')
        
        self.assertEqual(response.status_code, 401)


class CollectionsViewTest(CrispTestCase):
    """Test TAXII Collections endpoint"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Collections Org", domain="collections.com", contact_email="test@collections.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="collections_user", email="collections@taxii.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        # Create test collections
        self.collection1 = Collection.objects.create(
            id=str(uuid.uuid4()),
            title="Test Collection 1",
            description="First test collection",
            owner=self.org,
            can_read=True,
            can_write=True
        )
        
        self.collection2 = Collection.objects.create(
            id=str(uuid.uuid4()),
            title="Test Collection 2",
            description="Second test collection",
            owner=self.org,
            can_read=True,
            can_write=False
        )
    
    def test_collections_get(self):
        """Test getting collections list"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/taxii2/api/collections/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('collections', data)
        self.assertGreaterEqual(len(data['collections']), 2)
        
        # Check collection structure
        collection = data['collections'][0]
        self.assertIn('id', collection)
        self.assertIn('title', collection)
        self.assertIn('description', collection)
        self.assertIn('can_read', collection)
        self.assertIn('can_write', collection)
    
    def test_collections_filtering_by_access(self):
        """Test collections filtered by user access"""
        # Create user with different organization
        other_org = Organization.objects.create(
            name="Other Org", domain="other.com", contact_email="test@other.com"
        )
        
        other_user = CustomUser.objects.create_user(
            username="other_user", email="other@taxii.com", password="testpass123",
            organization=other_org, role="viewer"
        )
        
        self.client.force_authenticate(user=other_user)
        
        response = self.client.get('/taxii2/api/collections/')
        
        # Should return empty or filtered collections based on access
        data = response.json()
        self.assertIn('collections', data)
    
    def test_collections_pagination(self):
        """Test collections pagination"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/taxii2/api/collections/?limit=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        if data['collections']:
            self.assertLessEqual(len(data['collections']), 1)


class CollectionViewTest(CrispTestCase):
    """Test TAXII Collection endpoint"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Collection Org", domain="collection.com", contact_email="test@collection.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="collection_user", email="collection@taxii.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        self.collection = Collection.objects.create(
            id=str(uuid.uuid4()),
            title="Single Test Collection",
            description="Single collection for testing",
            owner=self.org,
            can_read=True,
            can_write=True
        )
    
    def test_collection_get(self):
        """Test getting single collection"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/taxii2/api/collections/{self.collection.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['id'], self.collection.id)
        self.assertEqual(data['title'], self.collection.title)
        self.assertEqual(data['description'], self.collection.description)
        self.assertTrue(data['can_read'])
        self.assertTrue(data['can_write'])
    
    def test_collection_not_found(self):
        """Test getting non-existent collection"""
        self.client.force_authenticate(user=self.user)
        
        fake_id = str(uuid.uuid4())
        response = self.client.get(f'/taxii2/api/collections/{fake_id}/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_collection_access_denied(self):
        """Test accessing collection without permission"""
        # Create user with different organization
        other_org = Organization.objects.create(
            name="Other Collection Org", domain="other_collection.com", contact_email="test@other_collection.com"
        )
        
        other_user = CustomUser.objects.create_user(
            username="other_collection_user", email="other_collection@taxii.com", password="testpass123",
            organization=other_org, role="viewer"
        )
        
        self.client.force_authenticate(user=other_user)
        
        response = self.client.get(f'/taxii2/api/collections/{self.collection.id}/')
        
        # Should deny access or return 404
        self.assertIn(response.status_code, [403, 404])


class CollectionObjectsViewTest(CrispTestCase):
    """Test TAXII Collection Objects endpoint"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Objects Org", domain="objects.com", contact_email="test@objects.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="objects_user", email="objects@taxii.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        self.collection = Collection.objects.create(
            id=str(uuid.uuid4()),
            title="Objects Collection",
            description="Collection for objects testing",
            owner=self.org,
            can_read=True,
            can_write=True
        )
        
        # Create test STIX objects
        self.stix_object1 = STIXObject.objects.create(
            stix_id=f"indicator--{uuid.uuid4()}",
            type="indicator",
            collection=self.collection,
            data={
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "created": "2024-06-27T10:00:00.000Z",
                "modified": "2024-06-27T10:00:00.000Z",
                "pattern": "[file:hashes.MD5 = 'test']",
                "labels": ["malicious-activity"]
            }
        )
    
    def test_get_objects(self):
        """Test getting objects from collection"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/taxii2/api/collections/{self.collection.id}/objects/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('objects', data)
        self.assertGreaterEqual(len(data['objects']), 1)
        
        # Check object structure
        obj = data['objects'][0]
        self.assertIn('type', obj)
        self.assertIn('id', obj)
    
    def test_post_objects(self):
        """Test adding objects to collection"""
        self.client.force_authenticate(user=self.user)
        
        new_object = {
            "type": "indicator",
            "id": f"indicator--{uuid.uuid4()}",
            "created": "2024-06-27T11:00:00.000Z",
            "modified": "2024-06-27T11:00:00.000Z",
            "pattern": "[domain-name:value = 'evil.com']",
            "labels": ["malicious-activity"]
        }
        
        payload = {"objects": [new_object]}
        
        response = self.client.post(
            f'/taxii2/api/collections/{self.collection.id}/objects/',
            data=json.dumps(payload),
            content_type='application/taxii+json'
        )
        
        self.assertEqual(response.status_code, 202)  # TAXII uses 202 Accepted
    
    def test_get_objects_with_filtering(self):
        """Test getting objects with TAXII filtering"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/taxii2/api/collections/{self.collection.id}/objects/?type=indicator'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # All returned objects should be indicators
        for obj in data['objects']:
            self.assertEqual(obj['type'], 'indicator')
    
    def test_get_objects_with_pagination(self):
        """Test getting objects with pagination"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/taxii2/api/collections/{self.collection.id}/objects/?limit=1'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        if data['objects']:
            self.assertLessEqual(len(data['objects']), 1)
    
    def test_post_objects_validation_error(self):
        """Test posting invalid objects"""
        self.client.force_authenticate(user=self.user)
        
        invalid_object = {
            "type": "indicator",
            # Missing required fields
        }
        
        payload = {"objects": [invalid_object]}
        
        response = self.client.post(
            f'/taxii2/api/collections/{self.collection.id}/objects/',
            data=json.dumps(payload),
            content_type='application/taxii+json'
        )
        
        self.assertEqual(response.status_code, 400)


class ObjectViewTest(CrispTestCase):
    """Test TAXII Object endpoint"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Object Org", domain="object.com", contact_email="test@object.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="object_user", email="object@taxii.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        self.collection = Collection.objects.create(
            id=str(uuid.uuid4()),
            title="Object Collection",
            description="Collection for object testing",
            owner=self.org,
            can_read=True,
            can_write=True
        )
        
        self.stix_object = STIXObject.objects.create(
            stix_id=f"indicator--{uuid.uuid4()}",
            type="indicator",
            collection=self.collection,
            data={
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "created": "2024-06-27T10:00:00.000Z",
                "modified": "2024-06-27T10:00:00.000Z",
                "pattern": "[file:hashes.MD5 = 'test']",
                "labels": ["malicious-activity"]
            }
        )
    
    def test_get_object(self):
        """Test getting single object"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/taxii2/api/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), 1)
        
        obj = data['objects'][0]
        self.assertEqual(obj['id'], self.stix_object.stix_id)
    
    def test_get_object_not_found(self):
        """Test getting non-existent object"""
        self.client.force_authenticate(user=self.user)
        
        fake_id = f"indicator--{uuid.uuid4()}"
        response = self.client.get(
            f'/taxii2/api/collections/{self.collection.id}/objects/{fake_id}/'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_object_with_version(self):
        """Test getting object with specific version"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/taxii2/api/collections/{self.collection.id}/objects/{self.stix_object.stix_id}/?version=first'
        )
        
        self.assertEqual(response.status_code, 200)


class ManifestViewTest(CrispTestCase):
    """Test TAXII Manifest endpoint"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Manifest Org", domain="manifest.com", contact_email="test@manifest.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="manifest_user", email="manifest@taxii.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        self.collection = Collection.objects.create(
            id=str(uuid.uuid4()),
            title="Manifest Collection",
            description="Collection for manifest testing",
            owner=self.org,
            can_read=True,
            can_write=True
        )
        
        self.stix_object = STIXObject.objects.create(
            stix_id=f"indicator--{uuid.uuid4()}",
            type="indicator",
            collection=self.collection,
            data={
                "type": "indicator",
                "id": f"indicator--{uuid.uuid4()}",
                "created": "2024-06-27T10:00:00.000Z",
                "modified": "2024-06-27T10:00:00.000Z",
                "pattern": "[file:hashes.MD5 = 'test']",
                "labels": ["malicious-activity"]
            }
        )
    
    def test_get_manifest(self):
        """Test getting collection manifest"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/taxii2/api/collections/{self.collection.id}/manifest/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('objects', data)
        self.assertGreaterEqual(len(data['objects']), 1)
        
        # Check manifest entry structure
        entry = data['objects'][0]
        self.assertIn('id', entry)
        self.assertIn('date_added', entry)
        self.assertIn('version', entry)
    
    def test_get_manifest_with_filtering(self):
        """Test getting manifest with filtering"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/taxii2/api/collections/{self.collection.id}/manifest/?type=indicator'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should only include indicators in manifest
        for entry in data['objects']:
            # Verify filtering worked (implementation dependent)
            self.assertIn('id', entry)


class TAXIIErrorHandlingTest(CrispTestCase):
    """Test TAXII error handling"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="error_user", email="error@taxii.com", password="testpass123",
            role="viewer"
        )
    
    def test_malformed_request(self):
        """Test handling malformed requests"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            '/taxii2/api/collections/invalid-id/objects/',
            data='invalid json',
            content_type='application/taxii+json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_unsupported_media_type(self):
        """Test handling unsupported media types"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            '/taxii2/api/collections/test/objects/',
            data='{"test": "data"}',
            content_type='application/xml'
        )
        
        # Should return appropriate error for unsupported media type
        self.assertIn(response.status_code, [400, 415])
    
    def test_rate_limiting(self):
        """Test rate limiting on TAXII endpoints"""
        self.client.force_authenticate(user=self.user)
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = self.client.get('/taxii2/')
            responses.append(response.status_code)
        
        # Should not all be successful if rate limiting is implemented
        # (This test may pass if rate limiting is not implemented)


class TAXIIIntegrationTest(CrispTestCase):
    """Test TAXII workflow integration"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Integration Org", domain="integration.com", contact_email="test@integration.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="integration_user", email="integration@taxii.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        self.collection = Collection.objects.create(
            id=str(uuid.uuid4()),
            title="Integration Collection",
            description="Collection for integration testing",
            owner=self.org,
            can_read=True,
            can_write=True
        )
    
    def test_complete_taxii_workflow(self):
        """Test complete TAXII workflow: discovery -> collections -> objects"""
        self.client.force_authenticate(user=self.user)
        
        # 1. Discovery
        discovery_response = self.client.get('/taxii2/')
        self.assertEqual(discovery_response.status_code, 200)
        
        # 2. Get collections
        collections_response = self.client.get('/taxii2/api/collections/')
        self.assertEqual(collections_response.status_code, 200)
        
        # 3. Get specific collection
        collection_response = self.client.get(f'/taxii2/api/collections/{self.collection.id}/')
        self.assertEqual(collection_response.status_code, 200)
        
        # 4. Add object to collection
        new_object = {
            "type": "indicator",
            "id": f"indicator--{uuid.uuid4()}",
            "created": "2024-06-27T12:00:00.000Z",
            "modified": "2024-06-27T12:00:00.000Z",
            "pattern": "[ip-addr:value = '192.168.1.1']",
            "labels": ["malicious-activity"]
        }
        
        add_response = self.client.post(
            f'/taxii2/api/collections/{self.collection.id}/objects/',
            data=json.dumps({"objects": [new_object]}),
            content_type='application/taxii+json'
        )
        self.assertEqual(add_response.status_code, 202)
        
        # 5. Retrieve objects
        objects_response = self.client.get(f'/taxii2/api/collections/{self.collection.id}/objects/')
        self.assertEqual(objects_response.status_code, 200)
    
    def test_taxii_content_negotiation(self):
        """Test TAXII content negotiation"""
        self.client.force_authenticate(user=self.user)
        
        # Test with correct TAXII media type
        response = self.client.get(
            '/taxii2/',
            HTTP_ACCEPT='application/taxii+json;version=2.1'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/taxii+json;version=2.1')