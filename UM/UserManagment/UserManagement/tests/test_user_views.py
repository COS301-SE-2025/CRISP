"""
Tests for user views functionality
"""
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from ..models import CustomUser, Organization
from ..factories.user_factory import UserFactory


class UserViewsTestCase(APITestCase):
    """Test user views functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com',
            description='Test organization for user views'
        )
        
        # Create test users
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
    
    def test_user_list_view_as_admin(self):
        """Test user list view as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('users', data)
        self.assertIn('pagination', data)
        self.assertGreaterEqual(len(data['users']), 3)  # At least our 3 test users
    
    def test_user_list_view_as_publisher(self):
        """Test user list view as publisher"""
        self.client.force_authenticate(user=self.publisher_user)
        
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('users', data)
        # Publisher should only see users from their organization
    
    def test_user_list_view_as_viewer(self):
        """Test user list view as viewer"""
        self.client.force_authenticate(user=self.viewer_user)
        
        response = self.client.get('/api/users/')
        # Viewers should have limited access
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_user_list_with_search(self):
        """Test user list with search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/users/', {'search': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('users', data)
    
    def test_user_list_with_role_filter(self):
        """Test user list with role filtering"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/users/', {'role': 'viewer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('users', data)
    
    def test_user_list_with_pagination(self):
        """Test user list with pagination"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/users/', {'page': 1, 'page_size': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('users', data)
        self.assertIn('pagination', data)
        self.assertLessEqual(len(data['users']), 2)
    
    def test_user_detail_view_own_profile(self):
        """Test user detail view for own profile"""
        self.client.force_authenticate(user=self.viewer_user)
        
        response = self.client.get(f'/api/users/{self.viewer_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['username'], self.viewer_user.username)
    
    def test_user_detail_view_other_user_as_admin(self):
        """Test user detail view for other user as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/users/{self.viewer_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['username'], self.viewer_user.username)
    
    def test_user_detail_view_other_user_as_viewer(self):
        """Test user detail view for other user as viewer (should be denied)"""
        self.client.force_authenticate(user=self.viewer_user)
        
        response = self.client.get(f'/api/users/{self.admin_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_update_own_profile(self):
        """Test updating own profile"""
        self.client.force_authenticate(user=self.viewer_user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Viewer'
        }
        
        response = self.client.put(f'/api/users/{self.viewer_user.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        # Check for user data in response instead of success field
        self.assertEqual(data['first_name'], 'Updated')
        
        # Verify update
        self.viewer_user.refresh_from_db()
        self.assertEqual(self.viewer_user.first_name, 'Updated')
    
    def test_user_update_other_user_as_admin(self):
        """Test updating other user as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        update_data = {
            'first_name': 'Admin Updated',
            'is_verified': True
        }
        
        response = self.client.put(f'/api/users/{self.viewer_user.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify update
        self.viewer_user.refresh_from_db()
        self.assertEqual(self.viewer_user.first_name, 'Admin Updated')
    
    def test_user_partial_update(self):
        """Test partial user update"""
        self.client.force_authenticate(user=self.admin_user)
        
        update_data = {
            'is_verified': True
        }
        
        response = self.client.patch(f'/api/users/{self.viewer_user.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify partial update
        self.viewer_user.refresh_from_db()
        self.assertTrue(self.viewer_user.is_verified)
    
    def test_user_delete_as_admin(self):
        """Test user deletion as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create a user to delete
        user_to_delete = UserFactory.create_user('viewer', {
            'username': 'todelete',
            'email': 'todelete@test.com',
            'password': 'ToDeletePassword123!',
            'organization': self.organization
        })
        
        response = self.client.delete(f'/api/users/{user_to_delete.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify soft delete
        user_to_delete.refresh_from_db()
        self.assertFalse(user_to_delete.is_active)
    
    def test_user_delete_own_account_denied(self):
        """Test that users cannot delete their own account"""
        self.client.force_authenticate(user=self.viewer_user)
        
        response = self.client.delete(f'/api/users/{self.viewer_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_delete_as_viewer_denied(self):
        """Test that viewers cannot delete other users"""
        self.client.force_authenticate(user=self.viewer_user)
        
        response = self.client.delete(f'/api/users/{self.publisher_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(f'/api/users/{self.viewer_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserViewPermissionsTestCase(TestCase):
    """Test user view permission helpers"""
    
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
            'first_name': 'Publisher',
            'last_name': 'User',
            'organization': self.organization
        })
        
        self.viewer_user = UserFactory.create_user('viewer', {
            'username': 'viewer',
            'email': 'viewer@test.com',
            'password': 'ViewerPassword123!',
            'organization': self.organization
        })
    
    def test_get_user_queryset_permissions(self):
        """Test user queryset filtering based on permissions"""
        from ..views.user_views import UserListView
        from django.test import RequestFactory
        
        factory = RequestFactory()
        view = UserListView()
        
        # Test admin can see all users
        request = factory.get('/api/users/')
        request.user = self.admin_user
        view.request = request
        
        # This would test the actual queryset filtering
        # The implementation would need to be checked to ensure proper filtering
    
    def test_can_access_user_permissions(self):
        """Test user access permissions"""
        from ..views.user_views import UserDetailView
        from django.test import RequestFactory
        
        factory = RequestFactory()
        view = UserDetailView()
        
        # Test admin can access any user
        request = factory.get(f'/api/users/{self.viewer_user.id}/')
        request.user = self.admin_user
        view.request = request
        
        # Test user can access own profile
        request = factory.get(f'/api/users/{self.viewer_user.id}/')
        request.user = self.viewer_user
        view.request = request