"""
Tests for authentication views functionality
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import json

from ..models import CustomUser, Organization, UserSession, AuthenticationLog
from ..factories.user_factory import UserFactory
from .test_base import CrispAPITestCase


class AuthViewsTestCase(CrispAPITestCase):
    """Test authentication views functionality"""
    
    def setUp(self):
        super().setUp()
        
        # Create test user with known password for auth tests
        test_password = 'ComplexTestViewerPassword123!'
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com',
            first_name='Test',
            last_name='User',
            password=test_password
        )
        self.test_user_password = test_password
    
    def test_custom_token_obtain_pair_view(self):
        """Test custom JWT token generation"""
        login_data = {
            'username': 'testuser',
            'password': self.test_user_password
        }
        
        response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('tokens', data)
        self.assertIn('user', data)
        self.assertIn('session_id', data)
        
        # Check custom claims in token
        self.assertEqual(data['user']['role'], 'viewer')
        self.assertEqual(data['user']['organization'], self.organization.name)
    
    
    
    
    
    def test_custom_token_refresh_view(self):
        """Test JWT token refresh"""
        # First login to get tokens
        login_data = {
            'username': 'testuser',
            'password': self.test_user_password
        }
        
        login_response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        login_data = login_response.json()
        refresh_token = login_data['tokens']['refresh']
        
        # Refresh token
        refresh_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post('/api/auth/refresh/', refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('tokens', data)
        self.assertIn('session_id', data)
    
    def test_token_refresh_with_invalid_token(self):
        """Test token refresh with invalid refresh token"""
        refresh_data = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post('/api/auth/refresh/', refresh_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        data = response.json()
        self.assertEqual(data['error'], 'token_refresh_failed')
    
    def test_token_refresh_missing_token(self):
        """Test token refresh with missing refresh token"""
        response = self.client.post('/api/auth/refresh/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = response.json()
        self.assertEqual(data['error'], 'invalid_request')
    
    def test_custom_token_verify_view(self):
        """Test JWT token verification"""
        # First login to get token
        login_data = {
            'username': 'testuser',
            'password': self.test_user_password
        }
        
        login_response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.json()
        
        # Handle different response formats
        if 'tokens' in login_data and 'access' in login_data['tokens']:
            access_token = login_data['tokens']['access']
        elif 'access_token' in login_data:
            access_token = login_data['access_token']
        elif 'access' in login_data:
            access_token = login_data['access']
        else:
            self.fail(f"No access token found in response: {login_data}")
        
        # Verify token
        verify_data = {
            'token': access_token
        }
        
        response = self.client.post('/api/auth/verify/', verify_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['valid'])
        self.assertIn('user', data)
    
    def test_token_verify_with_invalid_token(self):
        """Test token verification with invalid token"""
        verify_data = {
            'token': 'invalid_token'
        }
        
        response = self.client.post('/api/auth/verify/', verify_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        data = response.json()
        self.assertEqual(data['error'], 'token_invalid')
    
    
    def test_user_profile_view_get(self):
        """Test getting user profile"""
        self.client.force_authenticate(user=self.test_user)
        
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'testuser@test.com')
    
    def test_user_profile_view_update(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.test_user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.put('/api/auth/profile/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['first_name'], 'Updated')
        self.assertEqual(data['last_name'], 'Name')
        
        # Verify database update
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, 'Updated')
    
    
    def test_password_change_with_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.client.force_authenticate(user=self.test_user)
        
        password_data = {
            'old_password': 'WrongOldPassword',
            'new_password': 'NewComplexTestPass2024!@#$',
            'new_password_confirm': 'NewComplexTestPass2024!@#$'
        }
        
        response = self.client.post('/api/auth/change-password/', password_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_view(self):
        """Test password reset request"""
        reset_data = {
            'email': 'testuser@test.com'
        }
        
        response = self.client.post('/api/auth/reset-password/', reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify reset token was set
        self.test_user.refresh_from_db()
        self.assertIsNotNone(self.test_user.password_reset_token)
        self.assertIsNotNone(self.test_user.password_reset_expires)
    
    def test_password_reset_with_nonexistent_email(self):
        """Test password reset with nonexistent email"""
        reset_data = {
            'email': 'nonexistent@test.com'
        }
        
        response = self.client.post('/api/auth/reset-password/', reset_data)
        # Should still return success to prevent email enumeration
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
    
    
    
    def test_trusted_device_view_get(self):
        """Test getting trusted devices"""
        self.client.force_authenticate(user=self.test_user)
        
        response = self.client.get('/api/auth/trusted-devices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('trusted_devices', data)
    
    def test_trusted_device_view_add(self):
        """Test adding trusted device"""
        self.client.force_authenticate(user=self.test_user)
        
        device_data = {
            'device_fingerprint': 'test_device_fingerprint',
            'action': 'add'
        }
        
        response = self.client.post('/api/auth/trusted-devices/', device_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify device was added
        self.test_user.refresh_from_db()
        self.assertIn('test_device_fingerprint', self.test_user.trusted_devices)
    
    def test_trusted_device_view_remove(self):
        """Test removing trusted device"""
        # Add device first
        self.test_user.trusted_devices.append('test_device_fingerprint')
        self.test_user.save()
        
        self.client.force_authenticate(user=self.test_user)
        
        device_data = {
            'device_fingerprint': 'test_device_fingerprint',
            'action': 'remove'
        }
        
        response = self.client.post('/api/auth/trusted-devices/', device_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify device was removed
        self.test_user.refresh_from_db()
        self.assertNotIn('test_device_fingerprint', self.test_user.trusted_devices)


class AuthViewTemplateTestCase(TestCase):
    """Test authentication view templates"""
    
    def test_login_page_view(self):
        """Test login page template view"""
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'CRISP User Management - Login')
    
    def test_viewer_dashboard_view(self):
        """Test viewer dashboard template view"""
        response = self.client.get('/viewer/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'CRISP Viewer Dashboard')
    
    def test_debug_auth_view(self):
        """Test debug auth template view"""
        response = self.client.get('/debug/auth/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Debug Authentication')