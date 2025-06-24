import json
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import timedelta

from ..models import CustomUser, UserSession, AuthenticationLog, Organization
from ..services.auth_service import AuthenticationService
from ..strategies.authentication_strategies import (
    StandardAuthenticationStrategy, TwoFactorAuthenticationStrategy, 
    TrustedDeviceAuthenticationStrategy
)


class AuthenticationStrategyTestCase(TestCase):
    """Test authentication strategies"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_standard_authentication_success(self):
        """Test successful standard authentication"""
        strategy = StandardAuthenticationStrategy()
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = strategy.authenticate('testuser', 'TestPassword123!', request)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user'], self.user)
        self.assertFalse(result['requires_2fa'])
    
    def test_standard_authentication_invalid_username(self):
        """Test authentication with invalid username"""
        strategy = StandardAuthenticationStrategy()
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = strategy.authenticate('invaliduser', 'TestPassword123!', request)
        
        self.assertFalse(result['success'])
        self.assertIsNone(result['user'])
        self.assertEqual(result['message'], 'Invalid credentials')
    
    def test_standard_authentication_invalid_password(self):
        """Test authentication with invalid password"""
        strategy = StandardAuthenticationStrategy()
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = strategy.authenticate('testuser', 'wrongpassword', request)
        
        self.assertFalse(result['success'])
        self.assertIsNone(result['user'])
        
        # Check that failed login attempt was recorded
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 1)
    
    def test_authentication_account_locked(self):
        """Test authentication with locked account"""
        # Lock the account
        self.user.lock_account()
        
        strategy = StandardAuthenticationStrategy()
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = strategy.authenticate('testuser', 'TestPassword123!', request)
        
        self.assertFalse(result['success'])
        self.assertIn('locked', result['message'].lower())
    
    def test_authentication_inactive_user(self):
        """Test authentication with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        strategy = StandardAuthenticationStrategy()
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = strategy.authenticate('testuser', 'TestPassword123!', request)
        
        self.assertFalse(result['success'])
        self.assertIn('inactive', result['message'].lower())
    
    def test_authentication_unverified_user(self):
        """Test authentication with unverified user"""
        self.user.is_verified = False
        self.user.save()
        
        strategy = StandardAuthenticationStrategy()
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = strategy.authenticate('testuser', 'TestPassword123!', request)
        
        self.assertFalse(result['success'])
        self.assertIn('verified', result['message'].lower())
    
    def test_trusted_device_authentication(self):
        """Test trusted device authentication"""
        strategy = TrustedDeviceAuthenticationStrategy()
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser',
            'HTTP_ACCEPT_LANGUAGE': 'en-US',
            'HTTP_ACCEPT_ENCODING': 'gzip'
        }
        
        # Test with remember_device=True
        result = strategy.authenticate('testuser', 'TestPassword123!', request, remember_device=True)
        
        self.assertTrue(result['success'])
        
        # Check that device was added to trusted devices
        self.user.refresh_from_db()
        self.assertTrue(len(self.user.trusted_devices) > 0)


class AuthenticationServiceTestCase(TestCase):
    """Test authentication service"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            is_verified=True
        )
        self.auth_service = AuthenticationService()
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = self.auth_service.authenticate_user('testuser', 'TestPassword123!', request)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user'], self.user)
        self.assertIn('tokens', result)
        self.assertIn('session_id', result)
    
    def test_authenticate_user_failure(self):
        """Test failed user authentication"""
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = self.auth_service.authenticate_user('testuser', 'wrongpassword', request)
        
        self.assertFalse(result['success'])
        self.assertNotIn('tokens', result)
    
    @patch('UserManagement.services.auth_service.RefreshToken')
    def test_refresh_token_success(self, mock_refresh_token):
        """Test successful token refresh"""
        # Mock refresh token
        mock_token = MagicMock()
        mock_token.__getitem__.return_value = str(self.user.id)
        mock_refresh_token.return_value = mock_token
        
        # Create a session
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_access_token',
            refresh_token='test_refresh_token',
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = self.auth_service.refresh_token('test_refresh_token', request)
        
        self.assertTrue(result['success'])
        self.assertIn('tokens', result)
    
    def test_logout_user(self):
        """Test user logout"""
        # Create a session
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_access_token',
            refresh_token='test_refresh_token',
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        request = MagicMock()
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        result = self.auth_service.logout_user(self.user, str(session.id), request)
        
        self.assertTrue(result['success'])
        
        # Check that session was deactivated
        session.refresh_from_db()
        self.assertFalse(session.is_active)
    
    @patch('UserManagement.services.auth_service.AccessToken')
    def test_verify_token_success(self, mock_access_token):
        """Test successful token verification"""
        # Mock access token
        mock_token = MagicMock()
        mock_token.__getitem__.return_value = str(self.user.id)
        mock_access_token.return_value = mock_token
        
        request = MagicMock()
        
        result = self.auth_service.verify_token('test_token', request)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['username'], self.user.username)


class AccountLockoutTestCase(TestCase):
    """Test account lockout functionality"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_failed_login_increment(self):
        """Test that failed login attempts are incremented"""
        initial_attempts = self.user.failed_login_attempts
        
        self.user.increment_failed_login()
        
        self.assertEqual(self.user.failed_login_attempts, initial_attempts + 1)
        self.assertIsNotNone(self.user.last_failed_login)
    
    def test_account_lockout_after_threshold(self):
        """Test that account is locked after exceeding threshold"""
        # Increment failed attempts to threshold
        for _ in range(5):
            self.user.increment_failed_login()
        
        self.assertTrue(self.user.is_account_locked)
        self.assertIsNotNone(self.user.account_locked_until)
    
    def test_unlock_account(self):
        """Test account unlock functionality"""
        # Lock the account
        self.user.lock_account()
        self.assertTrue(self.user.is_account_locked)
        
        # Unlock the account
        self.user.unlock_account()
        
        self.assertFalse(self.user.is_account_locked)
        self.assertIsNone(self.user.account_locked_until)
        self.assertEqual(self.user.failed_login_attempts, 0)
    
    def test_reset_failed_attempts(self):
        """Test resetting failed login attempts"""
        # Set some failed attempts
        self.user.failed_login_attempts = 3
        self.user.last_failed_login = timezone.now()
        self.user.save()
        
        # Reset attempts
        self.user.reset_failed_login_attempts()
        
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.last_failed_login)


class AuthenticationLogTestCase(TestCase):
    """Test authentication logging"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_log_authentication_event(self):
        """Test logging authentication events"""
        log_entry = AuthenticationLog.log_authentication_event(
            user=self.user,
            action='login_success',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            success=True
        )
        
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.user, self.user)
        self.assertEqual(log_entry.username, self.user.username)
        self.assertEqual(log_entry.action, 'login_success')
        self.assertTrue(log_entry.success)
    
    def test_log_failed_authentication(self):
        """Test logging failed authentication"""
        log_entry = AuthenticationLog.log_authentication_event(
            user=self.user,
            action='login_failed',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            success=False,
            failure_reason='Invalid password'
        )
        
        self.assertFalse(log_entry.success)
        self.assertEqual(log_entry.failure_reason, 'Invalid password')
    
    def test_log_without_user(self):
        """Test logging events without user (e.g., invalid username)"""
        log_entry = AuthenticationLog.log_authentication_event(
            user=None,
            action='login_failed',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            success=False,
            failure_reason='Invalid username'
        )
        
        self.assertIsNone(log_entry.user)
        self.assertEqual(log_entry.username, 'unknown')


class UserSessionTestCase(TestCase):
    """Test user session management"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_create_session(self):
        """Test creating user session"""
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_token',
            refresh_token='test_refresh',
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
        self.assertFalse(session.is_expired)
    
    def test_session_expiry(self):
        """Test session expiry"""
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_token',
            refresh_token='test_refresh',
            ip_address='127.0.0.1',
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        
        self.assertTrue(session.is_expired)
    
    def test_deactivate_session(self):
        """Test session deactivation"""
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_token',
            refresh_token='test_refresh',
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        session.deactivate()
        
        self.assertFalse(session.is_active)
    
    def test_extend_session(self):
        """Test session extension"""
        original_expiry = timezone.now() + timedelta(minutes=30)
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_token',
            refresh_token='test_refresh',
            ip_address='127.0.0.1',
            expires_at=original_expiry
        )
        
        session.extend_session(hours=2)
        
        self.assertGreater(session.expires_at, original_expiry)


class TrustedDeviceTestCase(TestCase):
    """Test trusted device functionality"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_add_trusted_device(self):
        """Test adding trusted device"""
        device_fingerprint = 'test_device_123'
        
        self.user.trusted_devices.append(device_fingerprint)
        self.user.save()
        
        self.assertIn(device_fingerprint, self.user.trusted_devices)
    
    def test_remove_trusted_device(self):
        """Test removing trusted device"""
        device_fingerprint = 'test_device_123'
        self.user.trusted_devices = [device_fingerprint]
        self.user.save()
        
        self.user.trusted_devices.remove(device_fingerprint)
        self.user.save()
        
        self.assertNotIn(device_fingerprint, self.user.trusted_devices)


class PasswordSecurityTestCase(TestCase):
    """Test password security features"""
    
    def setUp(self):
        self.organization = self.create_test_organization()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def create_test_organization(self):
        """Create test organization"""
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for unit tests',
                'domain': 'test.example.com'
            }
        )
        return org
    
    def test_password_validation(self):
        """Test password validation"""
        from ..validators import CustomPasswordValidator
        
        validator = CustomPasswordValidator()
        
        # Test valid password
        try:
            validator.validate('SecurePhrase47B!', self.user)
        except Exception as e:
            self.fail(f"Valid password failed validation: {e}")
        
        # Test invalid passwords
        invalid_passwords = [
            'short',  # Too short
            'nouppercase123!',  # No uppercase
            'NOLOWERCASE123!',  # No lowercase
            'NoDigitsHere!',  # No digits
            'NoSpecialChars123',  # No special characters
            'testuser123!',  # Contains username
        ]
        
        for password in invalid_passwords:
            with self.assertRaises(Exception):
                validator.validate(password, self.user)