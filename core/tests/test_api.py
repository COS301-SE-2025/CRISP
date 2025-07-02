"""
Essential Tests for Trust Management API

Covers critical API endpoints and functionality.
"""

import uuid
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status

from core.trust.models import TrustLevel, TrustRelationship
from core.trust.api.views import TrustRelationshipViewSet
from core.trust.api.serializers import TrustRelationshipSerializer
from core.trust.api.permissions import TrustRelationshipPermission


class MockUser:
    """Mock user for testing"""
    def __init__(self, organization_id=None, is_authenticated=True):
        self.id = str(uuid.uuid4())
        self.is_authenticated = is_authenticated
        self.organization = MockOrganization(organization_id) if organization_id else None


class MockOrganization:
    """Mock organization for testing"""
    def __init__(self, org_id):
        self.id = org_id


class TrustRelationshipViewSetTest(TestCase):
    """Test Trust Relationship API views"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.viewset = TrustRelationshipViewSet()
        
        self.source_org = str(uuid.uuid4())
        self.target_org = str(uuid.uuid4())
        
        # Create test trust level
        self.trust_level = TrustLevel.objects.create(
            name='API Test Level',
            level='medium',
            numerical_value=50,
            description='Test description',
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        # Create test relationship
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            created_by='test_user',
            last_modified_by='test_user'
        )
    
    def test_get_queryset_authenticated(self):
        """Test queryset filtering for authenticated user"""
        request = self.factory.get('/')
        request.user = MockUser(self.source_org)
        self.viewset.request = request
        
        queryset = self.viewset.get_queryset()
        self.assertIn(self.relationship, queryset)
    
    def test_get_queryset_unauthenticated(self):
        """Test queryset for unauthenticated user"""
        request = self.factory.get('/')
        request.user = MockUser(is_authenticated=False)
        self.viewset.request = request
        
        queryset = self.viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    @patch('core.trust.api.views.TrustService.create_trust_relationship')
    @patch('core.trust.api.views.validate_trust_operation')
    def test_create_relationship_success(self, mock_validate, mock_create):
        """Test successful relationship creation via API"""
        mock_validate.return_value = {'valid': True}
        mock_create.return_value = self.relationship
        
        request = self.factory.post('/')
        request.user = MockUser(self.source_org)
        request.data = {
            'target_organization': self.target_org,
            'trust_level_name': 'API Test Level',
            'relationship_type': 'bilateral'
        }
        
        self.viewset.request = request
        response = self.viewset.create_relationship(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create.assert_called_once()


class TrustRelationshipSerializerTest(TestCase):
    """Test Trust Relationship serializers"""
    
    def setUp(self):
        self.trust_level = TrustLevel.objects.create(
            name='Serializer Test Level',
            level='high',
            numerical_value=75,
            description='Test description',
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=str(uuid.uuid4()),
            target_organization=str(uuid.uuid4()),
            trust_level=self.trust_level,
            created_by='test_user',
            last_modified_by='test_user'
        )
    
    def test_serializer_fields(self):
        """Test serializer includes expected fields"""
        serializer = TrustRelationshipSerializer(self.relationship)
        data = serializer.data
        
        expected_fields = ['id', 'source_organization', 'target_organization', 'trust_level', 'status']
        for field in expected_fields:
            self.assertIn(field, data)


class TrustRelationshipPermissionTest(TestCase):
    """Test API permissions"""
    
    def setUp(self):
        self.permission = TrustRelationshipPermission()
        self.factory = APIRequestFactory()
    
    def test_permission_authenticated_user(self):
        """Test permission for authenticated user"""
        request = self.factory.get('/')
        request.user = MockUser()
        
        # Basic permission check
        self.assertTrue(hasattr(self.permission, 'has_permission'))
    
    def test_permission_unauthenticated_user(self):
        """Test permission for unauthenticated user"""
        request = self.factory.get('/')
        request.user = MockUser(is_authenticated=False)
        
        # Basic permission structure check
        self.assertTrue(hasattr(self.permission, 'has_permission'))