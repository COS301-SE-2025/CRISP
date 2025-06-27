"""
Tests for admin views functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from ..models import CustomUser, Organization, UserSession, AuthenticationLog
from ..models.threat_feed import ThreatFeed
from ..models.indicator import Indicator
from ..models.ttp_data import TTPData
from ..models.stix_object import STIXObject, Collection, Feed, Identity
from ..models.trust_models.models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership,
    TrustLog, SharingPolicy
)
from ..factories.user_factory import UserFactory
from .test_base import CrispAPITestCase, CrispTestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class AdminViewsTestCase(CrispAPITestCase):
    """Test admin views functionality"""
    
    def setUp(self):
        super().setUp()
        
        # Create test users with different roles using the base class method
        self.admin_user = self.create_test_user(
            role='BlueVisionAdmin',
            first_name='Admin',
            last_name='User'
        )
        
        self.publisher_user = self.create_test_user(
            role='publisher',
            first_name='Publisher',
            last_name='User'
        )
        
        self.viewer_user = self.create_test_user(
            role='viewer',
            first_name='Viewer',
            last_name='User'
        )
    
    def test_admin_user_list_as_admin(self):
        """Test admin user list view as BlueVisionAdmin"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('users', data)
        self.assertIn('pagination', data)
        self.assertGreaterEqual(len(data['users']), 3)  # At least our 3 test users
    
    def test_admin_user_list_as_publisher(self):
        """Test admin user list view as publisher"""
        self.client.force_authenticate(user=self.publisher_user)
        
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('users', data)
        # Publisher should only see users from their organization
    
    def test_admin_user_list_with_filters(self):
        """Test admin user list with filtering"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test role filter
        response = self.client.get('/api/admin/users/', {'role': 'viewer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test search
        response = self.client.get('/api/admin/users/', {'search': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test pagination
        response = self.client.get('/api/admin/users/', {'page': 1, 'page_size': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_user_create(self):
        """Test creating user through admin interface"""
        self.client.force_authenticate(user=self.admin_user)
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'NewUserComplexSecurePass2024!@#$',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'viewer',
            'organization_id': str(self.organization.id)
        }
        
        response = self.client.post('/api/admin/users/', user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('user', data)
    
    def test_admin_user_create_with_auto_password(self):
        """Test creating user with auto-generated password"""
        self.client.force_authenticate(user=self.admin_user)
        
        user_data = {
            'username': 'autouser',
            'email': 'autouser@test.com',
            'first_name': 'Auto',
            'last_name': 'User',
            'role': 'viewer',
            'organization_id': str(self.organization.id),
            'auto_generate_password': True
        }
        
        response = self.client.post('/api/admin/users/', user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('generated_password', data)
    
    def test_admin_user_detail_get(self):
        """Test getting user details"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/admin/users/{self.viewer_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['username'], self.viewer_user.username)
    
    def test_admin_user_update(self):
        """Test updating user"""
        self.client.force_authenticate(user=self.admin_user)
        
        update_data = {
            'first_name': 'Updated',
            'is_verified': True
        }
        
        response = self.client.put(f'/api/admin/users/{self.viewer_user.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify update
        self.viewer_user.refresh_from_db()
        self.assertEqual(self.viewer_user.first_name, 'Updated')
    
    def test_admin_user_delete(self):
        """Test deleting (deactivating) user"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create a user to delete
        user_to_delete = UserFactory.create_user('viewer', {
            'username': 'todelete',
            'email': 'todelete@test.com',
            'password': 'ToDeleteComplexSecurePass2024!@#$',
            'organization': self.organization
        })
        
        response = self.client.delete(f'/api/admin/users/{user_to_delete.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify soft delete
        user_to_delete.refresh_from_db()
        self.assertFalse(user_to_delete.is_active)
    
    def test_admin_user_unlock(self):
        """Test unlocking user account"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Lock the viewer user
        self.viewer_user.lock_account()
        self.assertTrue(self.viewer_user.is_account_locked)
        
        response = self.client.post(f'/api/admin/users/{self.viewer_user.id}/unlock/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify unlock
        self.viewer_user.refresh_from_db()
        self.assertFalse(self.viewer_user.is_account_locked)
    
    def test_admin_authentication_logs(self):
        """Test viewing authentication logs"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/admin/auth-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('logs', data)
        self.assertIn('pagination', data)
    
    def test_admin_authentication_logs_with_filters(self):
        """Test authentication logs with filters"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test user filter
        response = self.client.get('/api/admin/auth-logs/', {'user_id': str(self.viewer_user.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test action filter
        response = self.client.get('/api/admin/auth-logs/', {'action': 'user_created'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test success filter
        response = self.client.get('/api/admin/auth-logs/', {'success': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_user_sessions(self):
        """Test viewing user sessions"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/admin/sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('sessions', data)
        self.assertIn('pagination', data)
    
    def test_admin_terminate_session(self):
        """Test terminating user session"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create a session for the viewer user
        from django.utils import timezone
        from datetime import timedelta
        
        session = UserSession.objects.create(
            user=self.viewer_user,
            session_token='test_token',
            refresh_token='test_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        response = self.client.delete(f'/api/admin/sessions/{session.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify session termination
        session.refresh_from_db()
        self.assertFalse(session.is_active)
    
    def test_permission_denied_for_viewer(self):
        """Test that viewers cannot access admin endpoints"""
        self.client.force_authenticate(user=self.viewer_user)
        
        # Should be denied
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    
    def test_publisher_cannot_create_admin(self):
        """Test that publishers cannot create BlueVisionAdmin users"""
        self.client.force_authenticate(user=self.publisher_user)
        
        user_data = {
            'username': 'badmin',
            'email': 'badmin@test.com',
            'password': 'BadminComplexSecurePass2024!@#$',
            'first_name': 'Bad',
            'last_name': 'Admin',
            'role': 'BlueVisionAdmin',
            'organization_id': str(self.organization.id)
        }
        
        response = self.client.post('/api/admin/users/', user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminViewPermissionsTestCase(CrispTestCase):
    """Test admin view permission helpers"""
    
    def setUp(self):
        super().setUp()
        
        self.admin_user = self.create_test_user(role='BlueVisionAdmin')
        
        self.publisher_user = self.create_test_user(
            role='publisher',
            first_name='Publisher',
            last_name='User'
        )
        
        self.viewer_user = self.create_test_user(role='viewer')
    
    def test_can_assign_role_permissions(self):
        """Test _can_assign_role method"""
        from ..views.admin_views import AdminUserDetailView
        
        view = AdminUserDetailView()
        
        # Admin can assign any role
        self.assertTrue(view._can_assign_role(self.admin_user, 'BlueVisionAdmin'))
        self.assertTrue(view._can_assign_role(self.admin_user, 'publisher'))
        self.assertTrue(view._can_assign_role(self.admin_user, 'viewer'))
        
        # Publisher can assign viewer and publisher roles
        self.assertFalse(view._can_assign_role(self.publisher_user, 'BlueVisionAdmin'))
        self.assertTrue(view._can_assign_role(self.publisher_user, 'publisher'))
        self.assertTrue(view._can_assign_role(self.publisher_user, 'viewer'))
        
        # Viewer cannot assign any roles
        self.assertFalse(view._can_assign_role(self.viewer_user, 'BlueVisionAdmin'))
        self.assertFalse(view._can_assign_role(self.viewer_user, 'publisher'))
        self.assertFalse(view._can_assign_role(self.viewer_user, 'viewer'))
    
    def test_can_delete_user_permissions(self):
        """Test _can_delete_user method"""
        from ..views.admin_views import AdminUserDetailView
        
        view = AdminUserDetailView()
        
        # Admin can delete any user
        self.assertTrue(view._can_delete_user(self.admin_user, self.publisher_user))
        self.assertTrue(view._can_delete_user(self.admin_user, self.viewer_user))
        
        # Publisher can delete non-admin users in their org
        self.assertFalse(view._can_delete_user(self.publisher_user, self.admin_user))
        self.assertTrue(view._can_delete_user(self.publisher_user, self.viewer_user))
        
        # Viewer cannot delete anyone
        self.assertFalse(view._can_delete_user(self.viewer_user, self.admin_user))
        self.assertFalse(view._can_delete_user(self.viewer_user, self.publisher_user))


class AdminModelDisplayTestCase(CrispTestCase):
    """Test admin model display methods and filters"""
    
    def setUp(self):
        super().setUp()
        from ..admin import (
            OrganizationAdmin, CustomUserAdmin, UserSessionAdmin, AuthenticationLogAdmin,
            ThreatFeedAdmin, IndicatorAdmin, TTPDataAdmin, STIXObjectAdmin,
            CollectionAdmin, FeedAdmin, IdentityAdmin, TrustLevelAdmin,
            TrustGroupAdmin, TrustRelationshipAdmin, TrustLogAdmin
        )
        
        self.site = AdminSite()
        self.request = HttpRequest()
        self.request.user = self.create_test_user(role='BlueVisionAdmin')
        
        # Initialize admin instances
        self.org_admin = OrganizationAdmin(Organization, self.site)
        self.user_admin = CustomUserAdmin(CustomUser, self.site)
        self.session_admin = UserSessionAdmin(UserSession, self.site)
        self.auth_log_admin = AuthenticationLogAdmin(AuthenticationLog, self.site)
        self.threat_feed_admin = ThreatFeedAdmin(ThreatFeed, self.site)
        self.indicator_admin = IndicatorAdmin(Indicator, self.site)
        self.ttp_admin = TTPDataAdmin(TTPData, self.site)
        self.stix_admin = STIXObjectAdmin(STIXObject, self.site)
        self.collection_admin = CollectionAdmin(Collection, self.site)
        self.feed_admin = FeedAdmin(Feed, self.site)
        self.identity_admin = IdentityAdmin(Identity, self.site)
        self.trust_level_admin = TrustLevelAdmin(TrustLevel, self.site)
        self.trust_group_admin = TrustGroupAdmin(TrustGroup, self.site)
        self.trust_rel_admin = TrustRelationshipAdmin(TrustRelationship, self.site)
        self.trust_log_admin = TrustLogAdmin(TrustLog, self.site)
    
    def test_organization_admin_display_methods(self):
        """Test OrganizationAdmin display methods"""
        org = self.organization
        
        # Test user_count method
        count = self.org_admin.user_count(org)
        self.assertIsInstance(count, int)
        
        # Test user_count_display method
        display = self.org_admin.user_count_display(org)
        self.assertIn('Total:', display)
        self.assertIn('Active:', display)
        self.assertIn('Verified:', display)
        
        # Test created_at_display method
        created_display = self.org_admin.created_at_display(org)
        self.assertIsInstance(created_display, str)
        self.assertTrue(len(created_display) > 0)
        
        # Test get_queryset method
        queryset = self.org_admin.get_queryset(self.request)
        self.assertTrue(hasattr(queryset.first(), 'user_count') if queryset.exists() else True)
    
    def test_custom_user_admin_display_methods(self):
        """Test CustomUserAdmin display methods"""
        user = self.create_test_user(role='viewer')
        
        # Test account_status_display method
        status_display = self.user_admin.account_status_display(user)
        self.assertIn('Active', status_display)
        
        # Test with inactive user
        user.is_active = False
        user.save()
        status_display = self.user_admin.account_status_display(user)
        self.assertIn('Inactive', status_display)
        
        # Test with locked user
        user.is_active = True
        user.account_locked_until = timezone.now() + timedelta(hours=1)
        user.save()
        status_display = self.user_admin.account_status_display(user)
        self.assertIn('Locked', status_display)
        
        # Test with unverified user
        user.account_locked_until = None
        user.is_verified = False
        user.save()
        status_display = self.user_admin.account_status_display(user)
        self.assertIn('Unverified', status_display)
        
        # Test last_login_display method
        user.last_login = timezone.now()
        user.save()
        login_display = self.user_admin.last_login_display(user)
        self.assertNotEqual(login_display, 'Never')
        
        # Test with no last login
        user.last_login = None
        user.save()
        login_display = self.user_admin.last_login_display(user)
        self.assertEqual(login_display, 'Never')
        
        # Test get_queryset method
        queryset = self.user_admin.get_queryset(self.request)
        self.assertTrue(queryset.exists())
    
    def test_user_session_admin_display_methods(self):
        """Test UserSessionAdmin display methods"""
        user = self.create_test_user(role='viewer')
        session = UserSession.objects.create(
            user=user,
            session_token='test_token_12345678901234567890',
            refresh_token='test_refresh',
            device_info={'browser': 'test'},
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Test session_token_short method
        short_token = self.session_admin.session_token_short(session)
        self.assertIn('test_tok', short_token)
        self.assertIn('...', short_token)
        
        # Test with no session token
        session.session_token = None
        session.save()
        short_token = self.session_admin.session_token_short(session)
        self.assertEqual(short_token, 'None')
        
        # Reset token for other tests
        session.session_token = 'test_token_12345678901234567890'
        session.save()
        
        # Test created_at_display method
        created_display = self.session_admin.created_at_display(session)
        self.assertIsInstance(created_display, str)
        
        # Test expires_at_display method
        expires_display = self.session_admin.expires_at_display(session)
        self.assertIsInstance(expires_display, str)
        
        # Test get_queryset method
        queryset = self.session_admin.get_queryset(self.request)
        self.assertTrue(queryset.exists())
    
    def test_auth_log_admin_display_methods(self):
        """Test AuthenticationLogAdmin display methods"""
        user = self.create_test_user(role='viewer')
        auth_log = AuthenticationLog.objects.create(
            user=user,
            action='login',
            success=True,
            ip_address='127.0.0.1',
            user_agent='test_agent'
        )
        
        # Test timestamp_display method
        timestamp_display = self.auth_log_admin.timestamp_display(auth_log)
        self.assertIsInstance(timestamp_display, str)
        
        # Test has_add_permission method
        can_add = self.auth_log_admin.has_add_permission(self.request)
        self.assertFalse(can_add)
        
        # Test has_change_permission method
        can_change = self.auth_log_admin.has_change_permission(self.request, auth_log)
        self.assertFalse(can_change)
        
        # Test get_queryset method
        queryset = self.auth_log_admin.get_queryset(self.request)
        self.assertTrue(queryset.exists())
    
    def test_trust_level_admin_display_methods(self):
        """Test TrustLevelAdmin display methods"""
        trust_level = TrustLevel.objects.create(
            name='Test Trust Level',
            level='HIGH',
            numerical_value=4,
            description='Test description',
            default_access_level='FULL',
            default_anonymization_level='LOW'
        )
        
        # Test that the trust level is properly displayed
        self.assertEqual(trust_level.name, 'Test Trust Level')
        self.assertEqual(trust_level.level, 'HIGH')
    
    def test_trust_group_admin_display_methods(self):
        """Test TrustGroupAdmin display methods"""
        trust_group = TrustGroup.objects.create(
            name='Test Group',
            group_type='SECTOR',
            description='Test group description',
            created_by=self.request.user,
            default_trust_level=TrustLevel.objects.create(
                name='Default Level',
                level='MEDIUM',
                numerical_value=3,
                description='Default level',
                default_access_level='MEDIUM',
                default_anonymization_level='MEDIUM'
            )
        )
        
        # Test member_count method
        member_count = self.trust_group_admin.member_count(trust_group)
        self.assertIsInstance(member_count, int)
    
    def test_trust_relationship_admin_display_methods(self):
        """Test TrustRelationshipAdmin display methods"""
        trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='HIGH',
            numerical_value=4,
            description='Test level',
            default_access_level='FULL',
            default_anonymization_level='LOW'
        )
        
        org2 = Organization.objects.create(
            name='Test Org 2',
            domain='testorg2.com',
            identity_class='organization'
        )
        
        trust_rel = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=org2,
            trust_level=trust_level,
            status='ACTIVE',
            relationship_type='DIRECT',
            created_by=self.request.user
        )
        
        # Test relationship_summary method
        summary = self.trust_rel_admin.relationship_summary(trust_rel)
        self.assertIn('→', summary)
        self.assertIn('...', summary)
        
        # Test is_effective_display method
        effective_display = self.trust_rel_admin.is_effective_display(trust_rel)
        self.assertIn('span', effective_display)
    
    def test_trust_log_admin_display_methods(self):
        """Test TrustLogAdmin display methods"""
        trust_log = TrustLog.objects.create(
            action='CREATE_RELATIONSHIP',
            source_organization=self.organization,
            target_organization=self.organization,
            user=self.request.user,
            success=True,
            details={'test': 'data'}
        )
        
        # Test source_organization_short method
        source_short = self.trust_log_admin.source_organization_short(trust_log)
        self.assertIn('...', source_short)
        
        # Test target_organization_short method
        target_short = self.trust_log_admin.target_organization_short(trust_log)
        self.assertIn('...', target_short)
        
        # Test with None organizations
        trust_log.source_organization = None
        trust_log.target_organization = None
        trust_log.save()
        
        source_short = self.trust_log_admin.source_organization_short(trust_log)
        self.assertEqual(source_short, '-')
        
        target_short = self.trust_log_admin.target_organization_short(trust_log)
        self.assertEqual(target_short, '-')
        
        # Test has_add_permission method
        can_add = self.trust_log_admin.has_add_permission(self.request)
        self.assertFalse(can_add)
        
        # Test has_change_permission method
        can_change = self.trust_log_admin.has_change_permission(self.request, trust_log)
        self.assertFalse(can_change)


class AdminFilterTestCase(CrispTestCase):
    """Test admin filter functionality"""
    
    def setUp(self):
        super().setUp()
        from ..admin import AccountStatusFilter
        
        self.filter = AccountStatusFilter(
            None,  # request
            {},    # params
            CustomUser,  # model
            None   # model_admin
        )
        
        # Create test users with different statuses
        self.active_user = self.create_test_user(
            role='viewer',
            username='active_user',
            is_active=True,
            is_verified=True
        )
        
        self.inactive_user = self.create_test_user(
            role='viewer',
            username='inactive_user',
            is_active=False
        )
        
        self.locked_user = self.create_test_user(
            role='viewer',
            username='locked_user',
            is_active=True
        )
        self.locked_user.account_locked_until = timezone.now() + timedelta(hours=1)
        self.locked_user.save()
        
        self.unverified_user = self.create_test_user(
            role='viewer',
            username='unverified_user',
            is_active=True,
            is_verified=False
        )
    
    def test_account_status_filter_lookups(self):
        """Test AccountStatusFilter lookups method"""
        lookups = self.filter.lookups(None, None)
        
        expected_lookups = [
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('locked', 'Locked'),
            ('unverified', 'Unverified'),
        ]
        
        self.assertEqual(list(lookups), expected_lookups)
    
    def test_account_status_filter_queryset_active(self):
        """Test AccountStatusFilter queryset method for active users"""
        queryset = CustomUser.objects.all()
        
        # Mock the filter value
        self.filter.value = lambda: 'active'
        filtered_queryset = self.filter.queryset(None, queryset)
        
        # Should include active, verified, unlocked users
        self.assertIn(self.active_user, filtered_queryset)
        self.assertNotIn(self.inactive_user, filtered_queryset)
        self.assertNotIn(self.locked_user, filtered_queryset)
        self.assertNotIn(self.unverified_user, filtered_queryset)
    
    def test_account_status_filter_queryset_inactive(self):
        """Test AccountStatusFilter queryset method for inactive users"""
        queryset = CustomUser.objects.all()
        
        # Mock the filter value
        self.filter.value = lambda: 'inactive'
        filtered_queryset = self.filter.queryset(None, queryset)
        
        # Should include inactive users
        self.assertNotIn(self.active_user, filtered_queryset)
        self.assertIn(self.inactive_user, filtered_queryset)
    
    def test_account_status_filter_queryset_locked(self):
        """Test AccountStatusFilter queryset method for locked users"""
        queryset = CustomUser.objects.all()
        
        # Mock the filter value
        self.filter.value = lambda: 'locked'
        filtered_queryset = self.filter.queryset(None, queryset)
        
        # Should include locked users
        self.assertIn(self.locked_user, filtered_queryset)
        self.assertNotIn(self.active_user, filtered_queryset)
    
    def test_account_status_filter_queryset_unverified(self):
        """Test AccountStatusFilter queryset method for unverified users"""
        queryset = CustomUser.objects.all()
        
        # Mock the filter value
        self.filter.value = lambda: 'unverified'
        filtered_queryset = self.filter.queryset(None, queryset)
        
        # Should include unverified users
        self.assertIn(self.unverified_user, filtered_queryset)
        self.assertNotIn(self.active_user, filtered_queryset)
    
    def test_account_status_filter_queryset_no_filter(self):
        """Test AccountStatusFilter queryset method with no filter value"""
        queryset = CustomUser.objects.all()
        
        # Mock the filter value to return None
        self.filter.value = lambda: None
        filtered_queryset = self.filter.queryset(None, queryset)
        
        # Should return None (no filtering)
        self.assertIsNone(filtered_queryset)


class AdminIntegrationTestCase(CrispTestCase):
    """Test admin integration with Django admin site"""
    
    def setUp(self):
        super().setUp()
        self.admin_user = self.create_test_user(
            role='BlueVisionAdmin',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test data for various models
        self.threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            description='Test feed description',
            owner=self.organization
        )
        
        self.indicator = Indicator.objects.create(
            type='ip',
            value='192.168.1.1',
            threat_feed=self.threat_feed,
            confidence=85,
            source_organization=self.organization
        )
        
        self.ttp_data = TTPData.objects.create(
            name='Test TTP',
            description='Test TTP description',
            mitre_technique_id='T1001',
            mitre_tactic='Defense Evasion',
            threat_feed=self.threat_feed,
            source_organization=self.organization
        )
    
    def test_admin_site_registration(self):
        """Test that all models are properly registered with admin site"""
        from django.contrib import admin
        
        # Test that key models are registered
        self.assertIn(Organization, admin.site._registry)
        self.assertIn(CustomUser, admin.site._registry)
        self.assertIn(UserSession, admin.site._registry)
        self.assertIn(AuthenticationLog, admin.site._registry)
        self.assertIn(ThreatFeed, admin.site._registry)
        self.assertIn(Indicator, admin.site._registry)
        self.assertIn(TTPData, admin.site._registry)
        self.assertIn(STIXObject, admin.site._registry)
        self.assertIn(Collection, admin.site._registry)
        self.assertIn(Feed, admin.site._registry)
        self.assertIn(Identity, admin.site._registry)
        self.assertIn(TrustLevel, admin.site._registry)
        self.assertIn(TrustGroup, admin.site._registry)
        self.assertIn(TrustRelationship, admin.site._registry)
        self.assertIn(TrustLog, admin.site._registry)
    
    def test_admin_site_customization(self):
        """Test admin site customization"""
        from django.contrib import admin
        
        self.assertEqual(admin.site.site_header, 'CRISP Integrated Platform Administration')
        self.assertEqual(admin.site.site_title, 'CRISP Admin')
        self.assertEqual(admin.site.index_title, 'CRISP Platform Administration')
    
    def test_admin_model_configurations(self):
        """Test that admin model configurations are properly set"""
        from django.contrib import admin
        from ..admin import (
            OrganizationAdmin, CustomUserAdmin, ThreatFeedAdmin,
            IndicatorAdmin, TTPDataAdmin
        )
        
        # Test OrganizationAdmin configuration
        org_admin = admin.site._registry[Organization]
        self.assertIsInstance(org_admin, OrganizationAdmin)
        self.assertIn('name', org_admin.list_display)
        self.assertIn('domain', org_admin.list_display)
        
        # Test CustomUserAdmin configuration
        user_admin = admin.site._registry[CustomUser]
        self.assertIsInstance(user_admin, CustomUserAdmin)
        self.assertIn('username', user_admin.list_display)
        self.assertIn('role', user_admin.list_display)
        
        # Test ThreatFeedAdmin configuration
        feed_admin = admin.site._registry[ThreatFeed]
        self.assertIsInstance(feed_admin, ThreatFeedAdmin)
        self.assertIn('name', feed_admin.list_display)
        self.assertIn('owner', feed_admin.list_display)
        
        # Test IndicatorAdmin configuration
        indicator_admin = admin.site._registry[Indicator]
        self.assertIsInstance(indicator_admin, IndicatorAdmin)
        self.assertIn('type', indicator_admin.list_display)
        self.assertIn('value', indicator_admin.list_display)
        
        # Test TTPDataAdmin configuration
        ttp_admin = admin.site._registry[TTPData]
        self.assertIsInstance(ttp_admin, TTPDataAdmin)
        self.assertIn('name', ttp_admin.list_display)
        self.assertIn('mitre_technique_id', ttp_admin.list_display)