"""
Debug test for authentication issues
"""
import os
import django
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
django.setup()

from core.models import CustomUser, Organization
from core.factories.user_factory import UserFactory


class AuthDebugTestCase(APITestCase):
    """Debug authentication issues"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com',
            description='Test organization for auth debug'
        )
        
        # Create test user directly
        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='ComplexTestPass2024!@#$',
            first_name='Test',
            last_name='User',
            organization=self.organization,
            is_verified=True,
            role='viewer'
        )
        
        print(f"Created user: {self.test_user.username}")
        print(f"User verified: {self.test_user.is_verified}")
        print(f"User active: {self.test_user.is_active}")
        print(f"User role: {self.test_user.role}")
    
    def test_user_exists(self):
        """Test that user was created correctly"""
        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('ComplexTestPass2024!@#$'))
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_active)
    
    def test_login_endpoint_exists(self):
        """Test that login endpoint responds"""
        response = self.client.get('/api/auth/login/')
        # Should be 405 Method Not Allowed for GET, not 404
        self.assertNotEqual(response.status_code, 404)
    
    def test_simple_login(self):
        """Test basic login functionality"""
        login_data = {
            'username': 'testuser',
            'password': 'ComplexTestPass2024!@#$'
        }
        
        response = self.client.post('/api/auth/login/', login_data, format='json')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Just check it's not a 404 or 500 for now
        self.assertIn(response.status_code, [200, 400, 401])


if __name__ == '__main__':
    import unittest
    unittest.main()