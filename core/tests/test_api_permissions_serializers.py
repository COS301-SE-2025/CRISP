"""
Comprehensive tests for API permissions and serializers
"""
import uuid
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.views import APIView
from datetime import timedelta
from unittest.mock import Mock, patch

from ..models.auth import CustomUser, Organization
from ..models.trust_models.models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership,
    TrustLog, SharingPolicy
)
from ..api.permissions.permissions import (
    BaseTrustPermission, TrustRelationshipPermission, TrustGroupPermission,
    TrustGroupMembershipPermission, IntelligenceAccessPermission,
    SystemAdminPermission, check_permission, require_permission,
    PermissionChecker
)
from ..api.serializers.serializers import (
    TrustLevelSerializer, TrustGroupSerializer, TrustRelationshipSerializer,
    TrustGroupMembershipSerializer, TrustLogSerializer, SharingPolicySerializer,
    CreateTrustRelationshipSerializer, ApproveTrustRelationshipSerializer,
    RevokeTrustRelationshipSerializer, CreateTrustGroupSerializer,
    JoinTrustGroupSerializer, LeaveTrustGroupSerializer, CheckTrustSerializer,
    TestIntelligenceAccessSerializer, UpdateTrustLevelSerializer
)
from .test_base import CrispTestCase


class BaseTrustPermissionTestCase(CrispTestCase):
    """Test BaseTrustPermission class"""
    
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.permission = BaseTrustPermission()
        self.view = APIView()
        
        self.user = self.create_test_user(role='publisher')
        self.user_no_org = CustomUser.objects.create_user(
            username='noorg',
            email='noorg@test.com',
            password='NoOrgComplexSecurePass2024!@#$'
        )
    
    def test_has_permission_authenticated_user_with_org(self):
        """Test permission for authenticated user with organization"""
        request = self.factory.get('/')
        request.user = self.user
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_unauthenticated_user(self):
        """Test permission for unauthenticated user"""
        request = self.factory.get('/')
        request.user = None
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
    
    def test_has_permission_user_without_org(self):
        """Test permission for user without organization"""
        request = self.factory.get('/')
        request.user = self.user_no_org
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
    
    def test_get_user_organization_valid(self):
        """Test get_user_organization with valid user"""
        request = self.factory.get('/')
        request.user = self.user
        
        org_id = self.permission.get_user_organization(request)
        self.assertEqual(org_id, str(self.user.organization.id))
    
    def test_get_user_organization_invalid(self):
        """Test get_user_organization with invalid user"""
        request = self.factory.get('/')
        request.user = self.user_no_org
        
        org_id = self.permission.get_user_organization(request)
        self.assertIsNone(org_id)


class TrustRelationshipPermissionTestCase(CrispTestCase):
    """Test TrustRelationshipPermission class"""
    
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.permission = TrustRelationshipPermission()
        self.view = APIView()
        
        self.admin_user = self.create_test_user(role='admin')
        self.publisher_user = self.create_test_user(role='publisher')
        self.viewer_user = self.create_test_user(role='viewer')
        
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='HIGH',
            numerical_value=4,
            description='Test level',
            default_access_level='FULL',
            default_anonymization_level='LOW'
        )
        
        self.org2 = Organization.objects.create(
            name='Test Org 2',
            domain='testorg2.com',
            identity_class='organization'
        )
        
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status='ACTIVE',
            relationship_type='DIRECT',
            created_by=self.admin_user
        )
    
    def test_has_permission_create_as_admin(self):
        """Test POST permission as admin"""
        request = self.factory.post('/')
        request.user = self.admin_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_create_as_publisher(self):
        """Test POST permission as publisher"""
        request = self.factory.post('/')
        request.user = self.publisher_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_create_as_viewer(self):
        """Test POST permission as viewer"""
        request = self.factory.post('/')
        request.user = self.viewer_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
    
    def test_has_permission_modify_as_admin(self):
        """Test PUT permission as admin"""
        request = self.factory.put('/')
        request.user = self.admin_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_delete_as_admin(self):
        """Test DELETE permission as admin"""
        request = self.factory.delete('/')
        request.user = self.admin_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_delete_as_publisher(self):
        """Test DELETE permission as publisher"""
        request = self.factory.delete('/')
        request.user = self.publisher_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
    
    def test_has_permission_view_all_roles(self):
        """Test GET permission for all roles"""
        request = self.factory.get('/')
        
        # Admin
        request.user = self.admin_user
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
        
        # Publisher
        request.user = self.publisher_user
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
        
        # Viewer
        request.user = self.viewer_user
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_object_permission_part_of_relationship(self):
        """Test object permission when user is part of relationship"""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = self.permission.has_object_permission(request, self.view, self.trust_relationship)
        self.assertTrue(result)
    
    def test_has_object_permission_not_part_of_relationship(self):
        """Test object permission when user is not part of relationship"""
        other_user = self.create_test_user(
            role='admin',
            username='other_admin',
            organization=self.org2
        )
        
        request = self.factory.get('/')
        request.user = other_user
        
        result = self.permission.has_object_permission(request, self.view, self.trust_relationship)
        self.assertFalse(result)
    
    def test_can_assign_role_methods(self):
        """Test individual can_assign_role methods"""
        request = self.factory.post('/')
        
        # Admin can create
        request.user = self.admin_user
        self.assertTrue(self.permission.can_create_relationships(request))
        
        # Publisher can create
        request.user = self.publisher_user
        self.assertTrue(self.permission.can_create_relationships(request))
        
        # Viewer cannot create
        request.user = self.viewer_user
        self.assertFalse(self.permission.can_create_relationships(request))
    
    def test_can_modify_specific_relationship_pending(self):
        """Test can_modify_specific_relationship with pending relationship"""
        self.trust_relationship.status = 'pending'
        self.trust_relationship.save()
        
        request = self.factory.put('/')
        request.user = self.admin_user
        
        result = self.permission.can_modify_specific_relationship(request, self.trust_relationship)
        self.assertTrue(result)
    
    def test_can_revoke_specific_relationship(self):
        """Test can_revoke_specific_relationship"""
        request = self.factory.delete('/')
        request.user = self.admin_user
        
        result = self.permission.can_revoke_specific_relationship(request, self.trust_relationship)
        self.assertTrue(result)


class TrustGroupPermissionTestCase(CrispTestCase):
    """Test TrustGroupPermission class"""
    
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.permission = TrustGroupPermission()
        self.view = APIView()
        
        self.admin_user = self.create_test_user(role='admin')
        self.publisher_user = self.create_test_user(role='publisher')
        self.viewer_user = self.create_test_user(role='viewer')
        
        self.trust_level = TrustLevel.objects.create(
            name='Default Level',
            level='MEDIUM',
            numerical_value=3,
            description='Default level',
            default_access_level='MEDIUM',
            default_anonymization_level='MEDIUM'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Test Group',
            group_type='SECTOR',
            description='Test group description',
            created_by=self.admin_user,
            default_trust_level=self.trust_level
        )
    
    def test_has_permission_create_as_admin(self):
        """Test POST permission as admin"""
        request = self.factory.post('/')
        request.user = self.admin_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_create_as_viewer(self):
        """Test POST permission as viewer"""
        request = self.factory.post('/')
        request.user = self.viewer_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
    
    def test_has_permission_delete_as_system_admin(self):
        """Test DELETE permission as system admin"""
        system_admin = self.create_test_user(role='system_admin')
        request = self.factory.delete('/')
        request.user = system_admin
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_delete_as_admin(self):
        """Test DELETE permission as regular admin"""
        request = self.factory.delete('/')
        request.user = self.admin_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
    
    @patch('core.models.trust_models.models.TrustGroup.can_administer')
    def test_has_object_permission_with_admin_rights(self, mock_can_administer):
        """Test object permission when user can administer group"""
        mock_can_administer.return_value = True
        
        request = self.factory.put('/')
        request.user = self.admin_user
        
        result = self.permission.has_object_permission(request, self.view, self.trust_group)
        self.assertTrue(result)
    
    @patch('core.models.trust_models.models.TrustGroup.can_administer')
    def test_has_object_permission_without_admin_rights(self, mock_can_administer):
        """Test object permission when user cannot administer group"""
        mock_can_administer.return_value = False
        
        request = self.factory.put('/')
        request.user = self.admin_user
        
        result = self.permission.has_object_permission(request, self.view, self.trust_group)
        self.assertFalse(result)


class IntelligenceAccessPermissionTestCase(CrispTestCase):
    """Test IntelligenceAccessPermission class"""
    
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.permission = IntelligenceAccessPermission()
        self.view = APIView()
        
        self.analyst_user = self.create_test_user(role='analyst')
        self.viewer_user = self.create_test_user(role='viewer')
    
    def test_has_permission_as_analyst(self):
        """Test permission for analyst role"""
        request = self.factory.get('/')
        request.user = self.analyst_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_as_viewer(self):
        """Test permission for viewer role"""
        request = self.factory.get('/')
        request.user = self.viewer_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
    
    @patch('core.api.permissions.permissions.TrustService.can_access_intelligence')
    def test_can_access_intelligence(self, mock_can_access):
        """Test can_access_intelligence method"""
        mock_can_access.return_value = (True, 'Access granted', None)
        
        request = self.factory.get('/')
        request.user = self.analyst_user
        
        result = self.permission.can_access_intelligence(
            request, 
            str(self.organization.id),
            'read'
        )
        self.assertTrue(result)
        
        mock_can_access.assert_called_once_with(
            requesting_org=str(self.analyst_user.organization.id),
            intelligence_owner=str(self.organization.id),
            required_access_level='read'
        )
    
    @patch('core.api.permissions.permissions.TrustService.check_trust_level')
    def test_get_access_level(self, mock_check_trust):
        """Test get_access_level method"""
        mock_relationship = Mock()
        mock_relationship.get_effective_access_level.return_value = 'full'
        mock_check_trust.return_value = ('HIGH', mock_relationship)
        
        request = self.factory.get('/')
        request.user = self.analyst_user
        
        result = self.permission.get_access_level(request, str(self.organization.id))
        self.assertEqual(result, 'full')
    
    @patch('core.api.permissions.permissions.TrustService.check_trust_level')
    def test_get_access_level_no_trust(self, mock_check_trust):
        """Test get_access_level with no trust relationship"""
        mock_check_trust.return_value = None
        
        request = self.factory.get('/')
        request.user = self.analyst_user
        
        result = self.permission.get_access_level(request, str(self.organization.id))
        self.assertEqual(result, 'none')


class SystemAdminPermissionTestCase(CrispTestCase):
    """Test SystemAdminPermission class"""
    
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.permission = SystemAdminPermission()
        self.view = APIView()
        
        self.system_admin = self.create_test_user(role='system_admin')
        self.admin_user = self.create_test_user(role='admin')
    
    def test_has_permission_as_system_admin(self):
        """Test permission for system admin"""
        request = self.factory.get('/')
        request.user = self.system_admin
        
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
    
    def test_has_permission_as_regular_admin(self):
        """Test permission for regular admin"""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)


class PermissionUtilityTestCase(CrispTestCase):
    """Test permission utility functions"""
    
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.admin_user = self.create_test_user(role='admin')
    
    def test_check_permission_valid_type(self):
        """Test check_permission with valid permission type"""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = check_permission('trust_relationship', request)
        self.assertTrue(result)
    
    def test_check_permission_invalid_type(self):
        """Test check_permission with invalid permission type"""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = check_permission('invalid_permission', request)
        self.assertFalse(result)
    
    def test_require_permission_decorator(self):
        """Test require_permission decorator"""
        from django.core.exceptions import PermissionDenied
        
        @require_permission('trust_relationship')
        def test_view(request):
            return 'success'
        
        # Test with valid permission
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = test_view(request)
        self.assertEqual(result, 'success')
        
        # Test with invalid permission
        viewer = self.create_test_user(role='viewer')
        request.user = viewer
        
        with self.assertRaises(PermissionDenied):
            test_view(request)


class PermissionCheckerTestCase(CrispTestCase):
    """Test PermissionChecker utility class"""
    
    def setUp(self):
        super().setUp()
        self.org2 = Organization.objects.create(
            name='Test Org 2',
            domain='testorg2.com',
            identity_class='organization'
        )
        
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='HIGH',
            numerical_value=4,
            description='Test level',
            default_access_level='FULL',
            default_anonymization_level='LOW'
        )
        
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status='ACTIVE',
            relationship_type='DIRECT',
            created_by=self.create_test_user(role='admin')
        )
        
        self.checker = PermissionChecker(str(self.organization.id), 'admin')
    
    def test_can_create_relationship_valid(self):
        """Test can_create_relationship with valid target"""
        result = self.checker.can_create_relationship(str(self.org2.id))
        self.assertTrue(result)
    
    def test_can_create_relationship_self(self):
        """Test can_create_relationship with self as target"""
        result = self.checker.can_create_relationship(str(self.organization.id))
        self.assertFalse(result)
    
    def test_can_create_relationship_invalid_role(self):
        """Test can_create_relationship with invalid role"""
        checker = PermissionChecker(str(self.organization.id), 'viewer')
        result = checker.can_create_relationship(str(self.org2.id))
        self.assertFalse(result)
    
    def test_can_approve_relationship(self):
        """Test can_approve_relationship"""
        self.trust_relationship.status = 'pending'
        self.trust_relationship.approved_by_source = False
        self.trust_relationship.save()
        
        result = self.checker.can_approve_relationship(self.trust_relationship)
        self.assertTrue(result)
    
    def test_can_revoke_relationship(self):
        """Test can_revoke_relationship"""
        result = self.checker.can_revoke_relationship(self.trust_relationship)
        self.assertTrue(result)
    
    def test_can_revoke_relationship_already_revoked(self):
        """Test can_revoke_relationship with already revoked relationship"""
        self.trust_relationship.status = 'revoked'
        self.trust_relationship.save()
        
        result = self.checker.can_revoke_relationship(self.trust_relationship)
        self.assertFalse(result)
    
    @patch('core.services.trust_service.TrustService.can_access_intelligence')
    def test_can_access_intelligence(self, mock_can_access):
        """Test can_access_intelligence"""
        mock_can_access.return_value = (True, 'Access granted', None)
        
        result = self.checker.can_access_intelligence(str(self.org2.id))
        self.assertTrue(result)


class SerializerTestCase(CrispTestCase):
    """Test serializer functionality"""
    
    def setUp(self):
        super().setUp()
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='HIGH',
            numerical_value=4,
            description='Test level description',
            default_access_level='FULL',
            default_anonymization_level='LOW'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Test Group',
            group_type='SECTOR',
            description='Test group description',
            created_by=self.create_test_user(role='admin'),
            default_trust_level=self.trust_level
        )
        
        self.org2 = Organization.objects.create(
            name='Test Org 2',
            domain='testorg2.com',
            identity_class='organization'
        )
        
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status='ACTIVE',
            relationship_type='DIRECT',
            created_by=self.create_test_user(role='admin')
        )
        
        self.trust_membership = TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization=self.organization,
            membership_type='MEMBER'
        )
        
        self.trust_log = TrustLog.objects.create(
            action='CREATE_RELATIONSHIP',
            source_organization=self.organization,
            target_organization=self.org2,
            user=self.create_test_user(role='admin'),
            success=True,
            details={'test': 'data'}
        )
        
        self.sharing_policy = SharingPolicy.objects.create(
            name='Test Policy',
            description='Test policy description',
            max_tlp_level='WHITE',
            created_by=self.create_test_user(role='admin')
        )
    
    def test_trust_level_serializer(self):
        """Test TrustLevelSerializer"""
        serializer = TrustLevelSerializer(self.trust_level)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Level')
        self.assertEqual(data['level'], 'HIGH')
        self.assertEqual(data['numerical_value'], 4)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_trust_group_serializer(self):
        """Test TrustGroupSerializer"""
        serializer = TrustGroupSerializer(self.trust_group)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Group')
        self.assertEqual(data['group_type'], 'SECTOR')
        self.assertEqual(data['default_trust_level_name'], 'Test Level')
        self.assertIn('member_count', data)
    
    def test_trust_relationship_serializer(self):
        """Test TrustRelationshipSerializer"""
        serializer = TrustRelationshipSerializer(self.trust_relationship)
        data = serializer.data
        
        self.assertEqual(data['status'], 'ACTIVE')
        self.assertEqual(data['relationship_type'], 'DIRECT')
        self.assertEqual(data['trust_level_name'], 'Test Level')
        self.assertIn('is_effective', data)
        self.assertIn('is_expired', data)
        self.assertIn('effective_access_level', data)
    
    def test_trust_group_membership_serializer(self):
        """Test TrustGroupMembershipSerializer"""
        serializer = TrustGroupMembershipSerializer(self.trust_membership)
        data = serializer.data
        
        self.assertEqual(data['membership_type'], 'MEMBER')
        self.assertEqual(data['trust_group_name'], 'Test Group')
        self.assertIn('is_active', data)
    
    def test_trust_log_serializer(self):
        """Test TrustLogSerializer"""
        serializer = TrustLogSerializer(self.trust_log)
        data = serializer.data
        
        self.assertEqual(data['action'], 'CREATE_RELATIONSHIP')
        self.assertTrue(data['success'])
        self.assertEqual(data['details'], {'test': 'data'})
    
    def test_sharing_policy_serializer(self):
        """Test SharingPolicySerializer"""
        serializer = SharingPolicySerializer(self.sharing_policy)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Policy')
        self.assertEqual(data['max_tlp_level'], 'WHITE')
        self.assertIn('created_at', data)
    
    def test_create_trust_relationship_serializer(self):
        """Test CreateTrustRelationshipSerializer"""
        data = {
            'target_organization': str(self.org2.id),
            'trust_level_name': 'Test Level',
            'relationship_type': 'bilateral',
            'notes': 'Test notes'
        }
        
        serializer = CreateTrustRelationshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['target_organization'], self.org2.id)
    
    def test_create_trust_relationship_serializer_invalid(self):
        """Test CreateTrustRelationshipSerializer with invalid data"""
        data = {
            'target_organization': 'invalid-uuid',
            'trust_level_name': 'Test Level'
        }
        
        serializer = CreateTrustRelationshipSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('target_organization', serializer.errors)
    
    def test_approve_trust_relationship_serializer(self):
        """Test ApproveTrustRelationshipSerializer"""
        data = {
            'relationship_id': str(self.trust_relationship.id)
        }
        
        serializer = ApproveTrustRelationshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_revoke_trust_relationship_serializer(self):
        """Test RevokeTrustRelationshipSerializer"""
        data = {
            'relationship_id': str(self.trust_relationship.id),
            'reason': 'Test revocation reason'
        }
        
        serializer = RevokeTrustRelationshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_create_trust_group_serializer(self):
        """Test CreateTrustGroupSerializer"""
        data = {
            'name': 'New Group',
            'description': 'New group description',
            'group_type': 'community',
            'is_public': True,
            'requires_approval': False
        }
        
        serializer = CreateTrustGroupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_join_trust_group_serializer(self):
        """Test JoinTrustGroupSerializer"""
        data = {
            'group_id': str(self.trust_group.id),
            'membership_type': 'member'
        }
        
        serializer = JoinTrustGroupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_leave_trust_group_serializer(self):
        """Test LeaveTrustGroupSerializer"""
        data = {
            'group_id': str(self.trust_group.id),
            'reason': 'Leaving for testing'
        }
        
        serializer = LeaveTrustGroupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_check_trust_serializer(self):
        """Test CheckTrustSerializer"""
        data = {
            'target_organization': str(self.org2.id)
        }
        
        serializer = CheckTrustSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_test_intelligence_access_serializer(self):
        """Test TestIntelligenceAccessSerializer"""
        data = {
            'intelligence_owner': str(self.org2.id),
            'required_access_level': 'read',
            'resource_type': 'indicator'
        }
        
        serializer = TestIntelligenceAccessSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_update_trust_level_serializer(self):
        """Test UpdateTrustLevelSerializer"""
        data = {
            'relationship_id': str(self.trust_relationship.id),
            'new_trust_level_name': 'New Level',
            'reason': 'Updating for testing'
        }
        
        serializer = UpdateTrustLevelSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class SerializerMethodTestCase(CrispTestCase):
    """Test serializer method fields"""
    
    def setUp(self):
        super().setUp()
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='HIGH',
            numerical_value=4,
            description='Test level',
            default_access_level='FULL',
            default_anonymization_level='LOW'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Test Group',
            group_type='SECTOR',
            description='Test group description',
            created_by=self.create_test_user(role='admin'),
            default_trust_level=self.trust_level
        )
        
        self.org2 = Organization.objects.create(
            name='Test Org 2',
            domain='testorg2.com',
            identity_class='organization'
        )
        
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status='ACTIVE',
            relationship_type='DIRECT',
            created_by=self.create_test_user(role='admin')
        )
    
    @patch('core.models.trust_models.models.TrustGroup.get_member_count')
    def test_trust_group_serializer_get_member_count(self, mock_get_member_count):
        """Test TrustGroupSerializer get_member_count method"""
        mock_get_member_count.return_value = 5
        
        serializer = TrustGroupSerializer(self.trust_group)
        member_count = serializer.get_member_count(self.trust_group)
        
        self.assertEqual(member_count, 5)
        mock_get_member_count.assert_called_once()
    
    @patch.object(TrustRelationship, 'is_effective', new_callable=lambda: property(lambda self: True))
    def test_trust_relationship_serializer_get_is_effective(self):
        """Test TrustRelationshipSerializer get_is_effective method"""
        serializer = TrustRelationshipSerializer(self.trust_relationship)
        is_effective = serializer.get_is_effective(self.trust_relationship)
        
        self.assertTrue(is_effective)
    
    @patch.object(TrustRelationship, 'is_expired', new_callable=lambda: property(lambda self: False))
    def test_trust_relationship_serializer_get_is_expired(self):
        """Test TrustRelationshipSerializer get_is_expired method"""
        serializer = TrustRelationshipSerializer(self.trust_relationship)
        is_expired = serializer.get_is_expired(self.trust_relationship)
        
        self.assertFalse(is_expired)
    
    @patch.object(TrustRelationship, 'is_fully_approved', new_callable=lambda: property(lambda self: True))
    def test_trust_relationship_serializer_get_is_fully_approved(self):
        """Test TrustRelationshipSerializer get_is_fully_approved method"""
        serializer = TrustRelationshipSerializer(self.trust_relationship)
        is_fully_approved = serializer.get_is_fully_approved(self.trust_relationship)
        
        self.assertTrue(is_fully_approved)
    
    @patch.object(TrustRelationship, 'get_effective_access_level')
    def test_trust_relationship_serializer_get_effective_access_level(self, mock_get_access_level):
        """Test TrustRelationshipSerializer get_effective_access_level method"""
        mock_get_access_level.return_value = 'FULL'
        
        serializer = TrustRelationshipSerializer(self.trust_relationship)
        access_level = serializer.get_effective_access_level(self.trust_relationship)
        
        self.assertEqual(access_level, 'FULL')
        mock_get_access_level.assert_called_once()
    
    @patch.object(TrustRelationship, 'get_effective_anonymization_level')
    def test_trust_relationship_serializer_get_effective_anonymization_level(self, mock_get_anon_level):
        """Test TrustRelationshipSerializer get_effective_anonymization_level method"""
        mock_get_anon_level.return_value = 'LOW'
        
        serializer = TrustRelationshipSerializer(self.trust_relationship)
        anon_level = serializer.get_effective_anonymization_level(self.trust_relationship)
        
        self.assertEqual(anon_level, 'LOW')
        mock_get_anon_level.assert_called_once()