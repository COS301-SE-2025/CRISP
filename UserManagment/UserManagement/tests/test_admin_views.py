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
from ..factories.user_factory import UserFactory

User = get_user_model()


class AdminViewsTestCase(APITestCase):
    """Test admin views functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com',
            description='Test organization for admin views'
        )
        
        # Create test users with different roles
        self.admin_user = UserFactory.create_user('BlueVisionAdmin', {
            'username': 'admin',
            'email': 'admin@test.com',
            'password': 'AdminPassword123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'organization': self.organization,
            'is_verified': True
        })
        
        self.publisher_user = UserFactory.create_user('publisher', {
            'username': 'publisher',
            'email': 'publisher@test.com',
            'password': 'PublisherPassword123!',
            'first_name': 'Publisher',
            'last_name': 'User',
            'organization': self.organization,
            'is_verified': True
        })
        
        self.viewer_user = UserFactory.create_user('viewer', {
            'username': 'viewer',
            'email': 'viewer@test.com',
            'password': 'ViewerPassword123!',
            'first_name': 'Viewer',
            'last_name': 'User',
            'organization': self.organization,
            'is_verified': True
        })
    
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
            'password': 'NewUserPassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'viewer',
            'organization': str(self.organization.id)
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
            'organization': str(self.organization.id),
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
            'password': 'ToDeletePassword123!',
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
    
    def test_publisher_can_manage_org_users(self):
        """Test that publishers can manage users in their organization"""
        self.client.force_authenticate(user=self.publisher_user)
        
        # Create user in same organization
        user_data = {
            'username': 'pubcreated',
            'email': 'pubcreated@test.com',
            'password': 'PubCreatedPassword123!',
            'first_name': 'Pub',
            'last_name': 'Created',
            'role': 'viewer',
            'organization': str(self.organization.id)
        }
        
        response = self.client.post('/api/admin/users/', user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_publisher_cannot_create_admin(self):
        """Test that publishers cannot create BlueVisionAdmin users"""
        self.client.force_authenticate(user=self.publisher_user)
        
        user_data = {
            'username': 'badmin',
            'email': 'badmin@test.com',
            'password': 'BadminPassword123!',
            'first_name': 'Bad',
            'last_name': 'Admin',
            'role': 'BlueVisionAdmin',
            'organization': str(self.organization.id)
        }
        
        response = self.client.post('/api/admin/users/', user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminViewPermissionsTestCase(TestCase):
    """Test admin view permission helpers"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Org',
            domain='test.com'
        )
        
        self.admin_user = UserFactory.create_user('BlueVisionAdmin', {
            'username': 'admin',
            'email': 'admin@test.com',
            'password': 'AdminPassword123!',
            'organization': self.organization
        })
        
        self.publisher_user = UserFactory.create_user('publisher', {
            'username': 'publisher',
            'email': 'publisher@test.com',
            'password': 'PublisherPassword123!',
            'organization': self.organization
        })
        
        self.viewer_user = UserFactory.create_user('viewer', {
            'username': 'viewer',
            'email': 'viewer@test.com',
            'password': 'ViewerPassword123!',
            'organization': self.organization
        })
    
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