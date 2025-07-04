#!/usr/bin/env python3
"""
Working tests that demonstrate how to fix the MagicMock organization issues
"""

import os
import django
import unittest

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from django.test import TestCase
from UserManagement.models import CustomUser, Organization, AuthenticationLog
from UserManagement.services.auth_service import AuthenticationService
from UserManagement.factories.user_factory import UserFactory
from django.test import RequestFactory


class WorkingUserModelTestCase(TestCase):
    """Fixed user model tests with real Organization instances"""
    
    def setUp(self):
        """Create real organization instead of mock"""
        self.organization = Organization.objects.create(
            name='Test Organization',
            description='Test organization for unit tests',
            domain='test.example.com'
        )
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            organization=self.organization,  # Real organization instance
            role='viewer'
        )
    
    def test_user_creation_defaults(self):
        """Test user creation with proper defaults"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'viewer')
        self.assertEqual(self.user.organization, self.organization)
        self.assertFalse(self.user.is_publisher)
        self.assertFalse(self.user.is_verified)
        self.assertEqual(self.user.failed_login_attempts, 0)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        expected = f"{self.user.username} ({self.organization.name})"
        self.assertEqual(str(self.user), expected)
    
    def test_user_account_lock_check(self):
        """Test account lock checking"""
        # Initially not locked
        self.assertFalse(self.user.is_account_locked)
        
        # Lock account
        self.user.lock_account(duration_minutes=30)
        self.assertTrue(self.user.is_account_locked)
        
        # Unlock account
        self.user.unlock_account()
        self.assertFalse(self.user.is_account_locked)
        self.assertEqual(self.user.failed_login_attempts, 0)
    
    def test_user_role_hierarchy(self):
        """Test user role-based methods"""
        # Test viewer
        self.assertFalse(self.user.can_publish_feeds())
        self.assertFalse(self.user.is_organization_admin())
        
        # Test publisher
        self.user.role = 'publisher'
        self.user.is_publisher = True
        self.user.save()
        self.assertTrue(self.user.can_publish_feeds())
        self.assertFalse(self.user.is_organization_admin())
        
        # Test admin
        self.user.role = 'admin'
        self.user.save()
        self.assertTrue(self.user.is_organization_admin())


class WorkingAuthenticationTestCase(TestCase):
    """Fixed authentication tests with real Organization instances"""
    
    def setUp(self):
        """Setup with real organization"""
        self.organization = Organization.objects.create(
            name='Auth Test Org',
            description='Organization for auth tests',
            domain='auth.example.com'
        )
        
        self.user = CustomUser.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='AuthPass123!',
            organization=self.organization,
            role='analyst',
            is_verified=True
        )
        
        self.factory = RequestFactory()
    
    def test_authentication_service(self):
        """Test authentication service with real user"""
        request = self.factory.post('/api/auth/login/')
        request.META['HTTP_USER_AGENT'] = 'TestAgent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        auth_service = AuthenticationService()
        result = auth_service.authenticate_user(
            username='authuser',
            password='AuthPass123!',
            request=request
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user'], self.user)
        self.assertIn('tokens', result)
        self.assertIn('access', result['tokens'])
        self.assertIn('refresh', result['tokens'])
    
    def test_failed_login_increment(self):
        """Test failed login attempts are incremented"""
        initial_attempts = self.user.failed_login_attempts
        
        self.user.increment_failed_login()
        self.user.refresh_from_db()
        
        self.assertEqual(self.user.failed_login_attempts, initial_attempts + 1)
        self.assertIsNotNone(self.user.last_failed_login)
    
    def test_reset_failed_attempts(self):
        """Test resetting failed login attempts"""
        # Set some failed attempts
        self.user.failed_login_attempts = 3
        self.user.save()
        
        # Reset them
        self.user.reset_failed_login_attempts()
        self.user.refresh_from_db()
        
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.last_failed_login)


class WorkingUserFactoryTestCase(TestCase):
    """Fixed user factory tests with real Organization instances"""
    
    def setUp(self):
        """Setup with real organization and admin user"""
        self.organization = Organization.objects.create(
            name='Factory Test Org',
            description='Organization for factory tests',
            domain='factory.example.com'
        )
        
        self.admin_user = CustomUser.objects.create_user(
            username='factoryadmin',
            email='admin@factory.example.com',
            password='AdminPass123!',
            organization=self.organization,
            role='system_admin',
            is_superuser=True,
            is_staff=True
        )
    
    def test_standard_user_creation(self):
        """Test creating standard user via factory"""
        user_data = {
            'username': 'standarduser',
            'email': 'standard@example.com',
            'password': 'StandardPass123!',
            'first_name': 'Standard',
            'last_name': 'User',
            'organization': self.organization
        }
        
        user = UserFactory.create_user('viewer', user_data, created_by=self.admin_user)
        
        self.assertEqual(user.username, 'standarduser')
        self.assertEqual(user.role, 'viewer')
        self.assertEqual(user.organization, self.organization)
        self.assertFalse(user.is_publisher)
        self.assertTrue(user.is_verified)  # Created by admin
    
    def test_publisher_user_creation(self):
        """Test creating publisher user via factory"""
        user_data = {
            'username': 'publisheruser',
            'email': 'publisher@example.com',
            'password': 'PublisherPass123!',
            'organization': self.organization
        }
        
        user = UserFactory.create_user('publisher', user_data, created_by=self.admin_user)
        
        self.assertEqual(user.role, 'publisher')
        self.assertTrue(user.is_publisher)
        self.assertTrue(user.can_publish_feeds())
    
    def test_auto_password_generation(self):
        """Test user creation with auto-generated password"""
        user_data = {
            'username': 'autopassuser',
            'email': 'autopass@example.com',
            'organization': self.organization
        }
        
        user, password = UserFactory.create_user_with_auto_password(
            'analyst', 
            user_data, 
            created_by=self.admin_user
        )
        
        self.assertEqual(user.username, 'autopassuser')
        self.assertEqual(user.role, 'analyst')
        self.assertIsInstance(password, str)
        self.assertGreaterEqual(len(password), 12)  # Minimum password length


class WorkingAuthenticationLogTestCase(TestCase):
    """Test authentication logging with real data"""
    
    def setUp(self):
        """Setup with real organization and user"""
        self.organization = Organization.objects.create(
            name='Log Test Org',
            description='Organization for log tests',
            domain='log.example.com'
        )
        
        self.user = CustomUser.objects.create_user(
            username='loguser',
            email='log@example.com',
            password='LogPass123!',
            organization=self.organization
        )
    
    def test_authentication_log_creation(self):
        """Test creating authentication log entries"""
        log = AuthenticationLog.log_authentication_event(
            user=self.user,
            action='login_success',
            ip_address='127.0.0.1',
            user_agent='TestAgent',
            success=True
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.username, self.user.username)
        self.assertEqual(log.action, 'login_success')
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertTrue(log.success)
        self.assertIsNotNone(log.timestamp)
    
    def test_failed_login_logging(self):
        """Test logging failed login attempts"""
        log = AuthenticationLog.log_authentication_event(
            user=self.user,
            action='login_failed',
            ip_address='192.168.1.100',
            user_agent='BrowserAgent',
            success=False,
            failure_reason='Invalid password'
        )
        
        self.assertFalse(log.success)
        self.assertEqual(log.failure_reason, 'Invalid password')


if __name__ == '__main__':
    # Run the working tests
    unittest.main(verbosity=2)