"""
Comprehensive tests for admin views
Tests for all admin view functionality including user management, permissions, and audit trails.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.core.paginator import Paginator
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from core.models.auth import Organization, CustomUser, AuthenticationLog, UserSession
from core.views.admin_views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminUserUnlockView,
    AdminAuthenticationLogView,
    AdminUserSessionView
)
from core.tests.test_base import CrispTestCase


class AdminUserListViewTest(CrispTestCase):
    """Test AdminUserListView functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.view = AdminUserListView()
        
        self.org1 = Organization.objects.create(
            name="Admin Test Org 1", domain="admin1.com", contact_email="test@admin1.com"
        )
        self.org2 = Organization.objects.create(
            name="Admin Test Org 2", domain="admin2.com", contact_email="test@admin2.com"
        )
        
        self.system_admin = CustomUser.objects.create_user(
            username="system_admin", email="sysadmin@admin1.com", password="testpass123",
            organization=self.org1, role="BlueVisionAdmin"
        )
        
        self.org_admin = CustomUser.objects.create_user(
            username="org_admin", email="orgadmin@admin1.com", password="testpass123",
            organization=self.org1, role="admin"
        )
        
        self.regular_user = CustomUser.objects.create_user(
            username="regular_user", email="user@admin1.com", password="testpass123",
            organization=self.org1, role="viewer"
        )
        
        self.other_org_user = CustomUser.objects.create_user(
            username="other_user", email="user@admin2.com", password="testpass123",
            organization=self.org2, role="publisher"
        )
    
    def test_get_system_admin_sees_all_users(self):
        """Test system admin can see all users"""
        request = self.factory.get('/admin/users/')
        request.user = self.system_admin
        request.query_params = {}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.system_admin, self.org_admin, self.regular_user, self.other_org_user]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 4
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
            data = response.data
            self.assertIn('users', data)
            self.assertIn('pagination', data)
    
    def test_get_org_admin_sees_org_users_only(self):
        """Test organization admin sees only their org users"""
        request = self.factory.get('/admin/users/')
        request.user = self.org_admin
        request.query_params = {}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.system_admin, self.org_admin, self.regular_user]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 3
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
    
    def test_get_with_role_filter(self):
        """Test filtering users by role"""
        request = self.factory.get('/admin/users/?role=viewer')
        request.user = self.system_admin
        request.query_params = {'role': 'viewer'}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.regular_user]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 1
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
    
    def test_get_with_search_filter(self):
        """Test searching users"""
        request = self.factory.get('/admin/users/?search=regular')
        request.user = self.system_admin
        request.query_params = {'search': 'regular'}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.regular_user]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 1
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
    
    def test_get_with_active_filter(self):
        """Test filtering by active status"""
        request = self.factory.get('/admin/users/?is_active=true')
        request.user = self.system_admin
        request.query_params = {'is_active': 'true'}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.system_admin, self.org_admin, self.regular_user]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 3
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
    
    def test_get_with_pagination(self):
        """Test pagination parameters"""
        request = self.factory.get('/admin/users/?page=1&page_size=2')
        request.user = self.system_admin
        request.query_params = {'page': '1', 'page_size': '2'}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.system_admin, self.org_admin]
            mock_page.has_next.return_value = True
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 2
            mock_paginator_instance.count = 4
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
            data = response.data
            self.assertEqual(data['pagination']['page'], 1)
            self.assertEqual(data['pagination']['page_size'], 2)
            self.assertTrue(data['pagination']['has_next'])
    
    @patch('core.factories.user_factory.UserFactory.create_user')
    def test_post_create_user_success(self, mock_create_user):
        """Test successful user creation"""
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_create_user.return_value = mock_user
        
        request = self.factory.post('/admin/users/')
        request.user = self.system_admin
        request.data = {
            'username': 'new_user',
            'email': 'new@admin1.com',
            'password': 'newpass123',
            'organization': str(self.org1.id),
            'role': 'publisher'
        }
        request.META = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'TestAgent'}
        
        with patch('core.api.serializers.serializers.AdminUserCreateSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = request.data.copy()
            mock_serializer_class.return_value = mock_serializer
            
            response = self.view.post(request)
            
            self.assertEqual(response.status_code, 201)
            self.assertTrue(response.data['success'])
    
    @patch('core.factories.user_factory.UserFactory.create_user_with_auto_password')
    def test_post_create_user_with_auto_password(self, mock_create_user):
        """Test user creation with auto-generated password"""
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_create_user.return_value = (mock_user, 'generated_password_123')
        
        request = self.factory.post('/admin/users/')
        request.user = self.system_admin
        request.data = {
            'username': 'auto_user',
            'email': 'auto@admin1.com',
            'organization': str(self.org1.id),
            'role': 'viewer',
            'auto_generate_password': True
        }
        request.META = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'TestAgent'}
        
        with patch('core.api.serializers.serializers.AdminUserCreateSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = request.data.copy()
            mock_serializer_class.return_value = mock_serializer
            
            response = self.view.post(request)
            
            self.assertEqual(response.status_code, 201)
            self.assertTrue(response.data['success'])
            self.assertIn('generated_password', response.data)
    
    def test_post_create_user_validation_error(self):
        """Test user creation with validation errors"""
        request = self.factory.post('/admin/users/')
        request.user = self.system_admin
        request.data = {
            'username': '',  # Invalid username
            'email': 'invalid-email',  # Invalid email
        }
        
        with patch('core.api.serializers.serializers.AdminUserCreateSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.is_valid.return_value = False
            mock_serializer.errors = {'username': ['This field is required.']}
            mock_serializer_class.return_value = mock_serializer
            
            response = self.view.post(request)
            
            self.assertEqual(response.status_code, 400)
    
    def test_post_create_user_exception(self):
        """Test user creation with exception"""
        request = self.factory.post('/admin/users/')
        request.user = self.system_admin
        request.data = {
            'username': 'exception_user',
            'email': 'exception@admin1.com',
            'password': 'testpass123',
            'organization': str(self.org1.id),
            'role': 'publisher'
        }
        request.META = {'REMOTE_ADDR': '192.168.1.100'}
        
        with patch('core.api.serializers.serializers.AdminUserCreateSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = request.data.copy()
            mock_serializer_class.return_value = mock_serializer
            
            with patch('core.factories.user_factory.UserFactory.create_user', side_effect=Exception('Database error')):
                response = self.view.post(request)
                
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.data)
    
    def test_get_client_ip_forwarded(self):
        """Test getting client IP from forwarded header"""
        request = self.factory.get('/admin/users/')
        request.META = {'HTTP_X_FORWARDED_FOR': '192.168.1.100, 10.0.0.1'}
        
        ip = self.view._get_client_ip(request)
        
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_remote_addr(self):
        """Test getting client IP from remote addr"""
        request = self.factory.get('/admin/users/')
        request.META = {'REMOTE_ADDR': '192.168.1.200'}
        
        ip = self.view._get_client_ip(request)
        
        self.assertEqual(ip, '192.168.1.200')
    
    def test_get_client_ip_default(self):
        """Test getting default client IP"""
        request = self.factory.get('/admin/users/')
        request.META = {}
        
        ip = self.view._get_client_ip(request)
        
        self.assertEqual(ip, '127.0.0.1')


class AdminUserDetailViewTest(CrispTestCase):
    """Test AdminUserDetailView functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.view = AdminUserDetailView()
        
        self.org = Organization.objects.create(
            name="Detail Org", domain="detail.com", contact_email="test@detail.com"
        )
        
        self.system_admin = CustomUser.objects.create_user(
            username="detail_admin", email="admin@detail.com", password="testpass123",
            organization=self.org, role="BlueVisionAdmin"
        )
        
        self.target_user = CustomUser.objects.create_user(
            username="target_user", email="target@detail.com", password="testpass123",
            organization=self.org, role="publisher"
        )
    
    def test_get_user_system_admin(self):
        """Test system admin can access any user"""
        request = self.factory.get(f'/admin/users/{self.target_user.id}/')
        request.user = self.system_admin
        
        user = self.view.get_user(request, self.target_user.id)
        
        self.assertEqual(user, self.target_user)
    
    def test_get_user_org_admin_same_org(self):
        """Test org admin can access users in same organization"""
        org_admin = CustomUser.objects.create_user(
            username="org_admin_detail", email="orgadmin@detail.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        request = self.factory.get(f'/admin/users/{self.target_user.id}/')
        request.user = org_admin
        
        user = self.view.get_user(request, self.target_user.id)
        
        self.assertEqual(user, self.target_user)
    
    def test_get_user_different_org(self):
        """Test user cannot access users from different organization"""
        other_org = Organization.objects.create(
            name="Other Detail Org", domain="other_detail.com", contact_email="test@other_detail.com"
        )
        
        other_admin = CustomUser.objects.create_user(
            username="other_admin", email="admin@other_detail.com", password="testpass123",
            organization=other_org, role="publisher"
        )
        
        request = self.factory.get(f'/admin/users/{self.target_user.id}/')
        request.user = other_admin
        
        user = self.view.get_user(request, self.target_user.id)
        
        self.assertIsNone(user)
    
    def test_get_user_not_found(self):
        """Test getting non-existent user"""
        request = self.factory.get('/admin/users/99999/')
        request.user = self.system_admin
        
        user = self.view.get_user(request, 99999)
        
        self.assertIsNone(user)
    
    def test_get_user_detail_success(self):
        """Test getting user details successfully"""
        request = self.factory.get(f'/admin/users/{self.target_user.id}/')
        request.user = self.system_admin
        
        with patch('core.api.serializers.serializers.AdminUserListSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.data = {'id': str(self.target_user.id), 'username': 'target_user'}
            mock_serializer_class.return_value = mock_serializer
            
            response = self.view.get(request, self.target_user.id)
            
            self.assertEqual(response.status_code, 200)
    
    def test_get_user_detail_not_found(self):
        """Test getting user details for non-existent user"""
        request = self.factory.get('/admin/users/99999/')
        request.user = self.system_admin
        
        response = self.view.get(request, 99999)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
    
    def test_put_user_update_success(self):
        """Test updating user successfully"""
        request = self.factory.put(f'/admin/users/{self.target_user.id}/')
        request.user = self.system_admin
        request.data = {'role': 'viewer', 'is_verified': True}
        request.META = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'TestAgent'}
        
        with patch('core.api.serializers.serializers.AdminUserUpdateSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = {'role': 'viewer', 'is_verified': True}
            mock_serializer.save.return_value = None
            mock_serializer_class.return_value = mock_serializer
            
            with patch('core.models.auth.AuthenticationLog.log_authentication_event'):
                response = self.view.put(request, self.target_user.id)
                
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data['success'])
    
    def test_put_user_update_insufficient_permissions(self):
        """Test updating user with insufficient permissions"""
        org_admin = CustomUser.objects.create_user(
            username="limited_admin", email="limited@detail.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        request = self.factory.put(f'/admin/users/{self.target_user.id}/')
        request.user = org_admin
        request.data = {'role': 'BlueVisionAdmin'}  # Cannot assign this role
        
        with patch('core.api.serializers.serializers.AdminUserUpdateSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = {'role': 'BlueVisionAdmin'}
            mock_serializer_class.return_value = mock_serializer
            
            response = self.view.put(request, self.target_user.id)
            
            self.assertEqual(response.status_code, 403)
    
    def test_put_user_update_validation_error(self):
        """Test updating user with validation errors"""
        request = self.factory.put(f'/admin/users/{self.target_user.id}/')
        request.user = self.system_admin
        request.data = {'role': 'invalid_role'}
        
        with patch('core.api.serializers.serializers.AdminUserUpdateSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.is_valid.return_value = False
            mock_serializer.errors = {'role': ['Invalid role']}
            mock_serializer_class.return_value = mock_serializer
            
            response = self.view.put(request, self.target_user.id)
            
            self.assertEqual(response.status_code, 400)
    
    def test_delete_user_success(self):
        """Test deleting user successfully"""
        request = self.factory.delete(f'/admin/users/{self.target_user.id}/')
        request.user = self.system_admin
        request.META = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'TestAgent'}
        
        with patch('core.models.auth.UserSession.objects.filter') as mock_sessions:
            mock_sessions.return_value.update.return_value = None
            
            with patch('core.models.auth.AuthenticationLog.log_authentication_event'):
                response = self.view.delete(request, self.target_user.id)
                
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data['success'])
    
    def test_delete_user_self_deletion(self):
        """Test preventing self-deletion"""
        request = self.factory.delete(f'/admin/users/{self.system_admin.id}/')
        request.user = self.system_admin
        
        response = self.view.delete(request, self.system_admin.id)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('cannot_delete_self', response.data['error'])
    
    def test_delete_user_insufficient_permissions(self):
        """Test deleting user with insufficient permissions"""
        other_org = Organization.objects.create(
            name="Other Org", domain="other.com", contact_email="test@other.com"
        )
        
        other_admin = CustomUser.objects.create_user(
            username="other_admin_delete", email="admin@other.com", password="testpass123",
            organization=other_org, role="publisher"
        )
        
        request = self.factory.delete(f'/admin/users/{self.target_user.id}/')
        request.user = other_admin
        
        response = self.view.delete(request, self.target_user.id)
        
        self.assertEqual(response.status_code, 403)
    
    def test_can_assign_role_system_admin(self):
        """Test system admin can assign any role"""
        can_assign = self.view._can_assign_role(self.system_admin, 'BlueVisionAdmin')
        
        self.assertTrue(can_assign)
    
    def test_can_assign_role_publisher_limited(self):
        """Test publisher can assign limited roles"""
        publisher = CustomUser.objects.create_user(
            username="publisher_role", email="publisher@detail.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        can_assign_viewer = self.view._can_assign_role(publisher, 'viewer')
        can_assign_publisher = self.view._can_assign_role(publisher, 'publisher')
        can_assign_admin = self.view._can_assign_role(publisher, 'BlueVisionAdmin')
        
        self.assertTrue(can_assign_viewer)
        self.assertTrue(can_assign_publisher)
        self.assertFalse(can_assign_admin)
    
    def test_can_delete_user_system_admin(self):
        """Test system admin can delete any user"""
        can_delete = self.view._can_delete_user(self.system_admin, self.target_user)
        
        self.assertTrue(can_delete)
    
    def test_can_delete_user_publisher_same_org(self):
        """Test publisher can delete non-admin users in same org"""
        publisher = CustomUser.objects.create_user(
            username="publisher_delete", email="publisher@detail.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        can_delete = self.view._can_delete_user(publisher, self.target_user)
        
        self.assertTrue(can_delete)
    
    def test_can_delete_user_publisher_cannot_delete_admin(self):
        """Test publisher cannot delete admin users"""
        publisher = CustomUser.objects.create_user(
            username="publisher_delete2", email="publisher2@detail.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        can_delete = self.view._can_delete_user(publisher, self.system_admin)
        
        self.assertFalse(can_delete)


class AdminUserUnlockViewTest(CrispTestCase):
    """Test AdminUserUnlockView functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.view = AdminUserUnlockView()
        
        self.org = Organization.objects.create(
            name="Unlock Org", domain="unlock.com", contact_email="test@unlock.com"
        )
        
        self.admin = CustomUser.objects.create_user(
            username="unlock_admin", email="admin@unlock.com", password="testpass123",
            organization=self.org, role="BlueVisionAdmin"
        )
        
        self.locked_user = CustomUser.objects.create_user(
            username="locked_user", email="locked@unlock.com", password="testpass123",
            organization=self.org, role="viewer"
        )
    
    def test_unlock_user_success(self):
        """Test unlocking user successfully"""
        request = self.factory.post(f'/admin/users/{self.locked_user.id}/unlock/')
        request.user = self.admin
        request.META = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'TestAgent'}
        
        with patch.object(self.locked_user, 'unlock_account') as mock_unlock:
            with patch('core.models.auth.AuthenticationLog.log_authentication_event'):
                response = self.view.post(request, self.locked_user.id)
                
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data['success'])
                mock_unlock.assert_called_once()
    
    def test_unlock_user_not_found(self):
        """Test unlocking non-existent user"""
        request = self.factory.post('/admin/users/99999/unlock/')
        request.user = self.admin
        
        response = self.view.post(request, 99999)
        
        self.assertEqual(response.status_code, 404)
    
    def test_unlock_user_insufficient_permissions(self):
        """Test unlocking user with insufficient permissions"""
        other_org = Organization.objects.create(
            name="Other Unlock Org", domain="other_unlock.com", contact_email="test@other_unlock.com"
        )
        
        other_user = CustomUser.objects.create_user(
            username="other_unlock_user", email="other@unlock.com", password="testpass123",
            organization=other_org, role="publisher"
        )
        
        request = self.factory.post(f'/admin/users/{self.locked_user.id}/unlock/')
        request.user = other_user
        
        response = self.view.post(request, self.locked_user.id)
        
        self.assertEqual(response.status_code, 403)


class AdminAuthenticationLogViewTest(CrispTestCase):
    """Test AdminAuthenticationLogView functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.view = AdminAuthenticationLogView()
        
        self.org = Organization.objects.create(
            name="Log Org", domain="log.com", contact_email="test@log.com"
        )
        
        self.admin = CustomUser.objects.create_user(
            username="log_admin", email="admin@log.com", password="testpass123",
            organization=self.org, role="BlueVisionAdmin"
        )
        
        self.user = CustomUser.objects.create_user(
            username="log_user", email="user@log.com", password="testpass123",
            organization=self.org, role="viewer"
        )
        
        # Create test logs
        self.log1 = AuthenticationLog.objects.create(
            user=self.user,
            username=self.user.username,
            action='login_success',
            ip_address='192.168.1.100',
            user_agent='TestAgent',
            success=True
        )
        
        self.log2 = AuthenticationLog.objects.create(
            user=None,
            username='failed_user',
            action='login_failed',
            ip_address='192.168.1.101',
            user_agent='TestAgent',
            success=False,
            failure_reason='invalid_credentials'
        )
    
    def test_get_logs_system_admin(self):
        """Test system admin can see all logs"""
        request = self.factory.get('/admin/logs/')
        request.user = self.admin
        request.query_params = {}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.log1, self.log2]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 2
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
            data = response.data
            self.assertIn('logs', data)
            self.assertIn('pagination', data)
    
    def test_get_logs_org_admin(self):
        """Test org admin sees only org user logs"""
        org_admin = CustomUser.objects.create_user(
            username="org_log_admin", email="orgadmin@log.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        request = self.factory.get('/admin/logs/')
        request.user = org_admin
        request.query_params = {}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.log1]  # Only logs for org users
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 1
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
    
    def test_get_logs_with_filters(self):
        """Test getting logs with various filters"""
        request = self.factory.get('/admin/logs/?user_id=1&action=login_success&success=true')
        request.user = self.admin
        request.query_params = {
            'user_id': '1',
            'action': 'login_success',
            'success': 'true',
            'ip_address': '192.168.1.100',
            'from_date': '2024-06-01',
            'to_date': '2024-06-30'
        }
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.log1]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 1
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)


class AdminUserSessionViewTest(CrispTestCase):
    """Test AdminUserSessionView functionality"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.view = AdminUserSessionView()
        
        self.org = Organization.objects.create(
            name="Session Org", domain="session.com", contact_email="test@session.com"
        )
        
        self.admin = CustomUser.objects.create_user(
            username="session_admin", email="admin@session.com", password="testpass123",
            organization=self.org, role="BlueVisionAdmin"
        )
        
        self.user = CustomUser.objects.create_user(
            username="session_user", email="user@session.com", password="testpass123",
            organization=self.org, role="viewer"
        )
        
        # Create test session
        self.session = UserSession.objects.create(
            user=self.user,
            session_token='test_token_123',
            ip_address='192.168.1.200',
            expires_at=timezone.now() + timezone.timedelta(hours=1),
            is_active=True
        )
    
    def test_get_sessions_system_admin(self):
        """Test system admin can see all active sessions"""
        request = self.factory.get('/admin/sessions/')
        request.user = self.admin
        request.query_params = {}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.session]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 1
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
            data = response.data
            self.assertIn('sessions', data)
            self.assertIn('pagination', data)
    
    def test_get_sessions_with_user_filter(self):
        """Test getting sessions filtered by user"""
        request = self.factory.get(f'/admin/sessions/?user_id={self.user.id}')
        request.user = self.admin
        request.query_params = {'user_id': str(self.user.id)}
        
        with patch('core.views.admin_views.Paginator') as mock_paginator:
            mock_page = Mock()
            mock_page.object_list = [self.session]
            mock_page.has_next.return_value = False
            mock_page.has_previous.return_value = False
            
            mock_paginator_instance = Mock()
            mock_paginator_instance.get_page.return_value = mock_page
            mock_paginator_instance.num_pages = 1
            mock_paginator_instance.count = 1
            mock_paginator.return_value = mock_paginator_instance
            
            response = self.view.get(request)
            
            self.assertEqual(response.status_code, 200)
    
    def test_delete_session_success(self):
        """Test terminating session successfully"""
        request = self.factory.delete(f'/admin/sessions/{self.session.id}/')
        request.user = self.admin
        request.META = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'TestAgent'}
        
        with patch.object(self.session, 'deactivate') as mock_deactivate:
            with patch('core.models.auth.AuthenticationLog.log_authentication_event'):
                response = self.view.delete(request, self.session.id)
                
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data['success'])
                mock_deactivate.assert_called_once()
    
    def test_delete_session_not_found(self):
        """Test terminating non-existent session"""
        request = self.factory.delete('/admin/sessions/99999/')
        request.user = self.admin
        
        response = self.view.delete(request, 99999)
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_session_insufficient_permissions(self):
        """Test terminating session with insufficient permissions"""
        other_org = Organization.objects.create(
            name="Other Session Org", domain="other_session.com", contact_email="test@other_session.com"
        )
        
        other_user = CustomUser.objects.create_user(
            username="other_session_user", email="other@session.com", password="testpass123",
            organization=other_org, role="publisher"
        )
        
        request = self.factory.delete(f'/admin/sessions/{self.session.id}/')
        request.user = other_user
        
        response = self.view.delete(request, self.session.id)
        
        self.assertEqual(response.status_code, 403)