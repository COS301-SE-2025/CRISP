"""
Tests to complete code coverage for remaining components
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from unittest.mock import Mock, patch

from ..models import CustomUser, Organization, UserSession, AuthenticationLog, STIXObjectPermission
from ..admin import CustomUserAdmin, OrganizationAdmin, UserSessionAdmin, AuthenticationLogAdmin
from ..serializers import (
    UserLoginSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer,
    TokenRefreshSerializer, TrustedDeviceSerializer, AdminUserListSerializer,
    AdminUserCreateSerializer, AdminUserUpdateSerializer, AuthenticationLogSerializer,
    UserSessionSerializer, OrganizationSerializer
)
from ..validators import UsernameValidator, EmailValidator, CustomPasswordValidator
# Skip signals import for now
from ..factories.user_factory import UserFactory
from ..permissions import (
    check_stix_object_permission, check_feed_publish_permission,
    RateLimitPermission
)

User = get_user_model()


class AdminTestCase(TestCase):
    """Test Django admin functionality"""
    
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.admin_user = UserFactory.create_user('BlueVisionAdmin', {
            'username': 'admin',
            'email': 'admin@test.com',
            'password': 'AdminPassword123!',
            'organization': self.organization,
            'is_staff': True,
            'is_superuser': True
        })
        
        self.test_user = UserFactory.create_user('viewer', {
            'username': 'testuser',
            'email': 'testuser@test.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        })
    
    def test_custom_user_admin(self):
        """Test CustomUserAdmin functionality"""
        admin = CustomUserAdmin(CustomUser, self.site)
        
        # Test list display
        self.assertIn('username', admin.list_display)
        self.assertIn('email', admin.list_display)
        self.assertIn('role', admin.list_display)
        
        # Test search fields
        self.assertIn('username', admin.search_fields)
        self.assertIn('email', admin.search_fields)
        
        # Test list filter
        self.assertIn('role', admin.list_filter)
        self.assertIn('is_verified', admin.list_filter)
        
        # Test readonly fields
        self.assertIn('id', admin.readonly_fields)
        self.assertIn('created_at', admin.readonly_fields)
    
    def test_organization_admin(self):
        """Test OrganizationAdmin functionality"""
        admin = OrganizationAdmin(Organization, self.site)
        
        # Test list display
        self.assertIn('name', admin.list_display)
        self.assertIn('domain', admin.list_display)
        
        # Test search fields
        self.assertIn('name', admin.search_fields)
        self.assertIn('domain', admin.search_fields)
    
    def test_user_session_admin(self):
        """Test UserSessionAdmin functionality"""
        admin = UserSessionAdmin(UserSession, self.site)
        
        # Test list display
        self.assertIn('user', admin.list_display)
        self.assertIn('ip_address', admin.list_display)
        self.assertIn('is_active', admin.list_display)
        
        # Test readonly fields
        self.assertIn('id', admin.readonly_fields)
        self.assertIn('created_at', admin.readonly_fields)
    
    def test_authentication_log_admin(self):
        """Test AuthenticationLogAdmin functionality"""
        admin = AuthenticationLogAdmin(AuthenticationLog, self.site)
        
        # Test list display
        self.assertIn('username', admin.list_display)
        self.assertIn('action', admin.list_display)
        self.assertIn('success', admin.list_display)
        
        # Test list filter
        self.assertIn('action', admin.list_filter)
        self.assertIn('success', admin.list_filter)


class SerializerTestCase(TestCase):
    """Test serializer functionality"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.test_user = UserFactory.create_user('viewer', {
            'username': 'testuser',
            'email': 'testuser@test.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        })
    
    def test_user_login_serializer(self):
        """Test UserLoginSerializer"""
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'testuser')
    
    def test_user_profile_serializer(self):
        """Test UserProfileSerializer"""
        serializer = UserProfileSerializer(instance=self.test_user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'testuser@test.com')
        self.assertIn('organization_name', data)
    
    def test_user_profile_update_serializer(self):
        """Test UserProfileUpdateSerializer"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        serializer = UserProfileUpdateSerializer(instance=self.test_user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Updated')
    
    def test_password_change_serializer(self):
        """Test PasswordChangeSerializer"""
        data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        request = Mock()
        request.user = self.test_user
        
        serializer = PasswordChangeSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
    
    def test_password_reset_serializer(self):
        """Test PasswordResetSerializer"""
        data = {
            'email': 'testuser@test.com'
        }
        
        serializer = PasswordResetSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_reset_confirm_serializer(self):
        """Test PasswordResetConfirmSerializer"""
        data = {
            'token': 'test_token',
            'new_password': 'NewPassword123!'
        }
        
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_trusted_device_serializer(self):
        """Test TrustedDeviceSerializer"""
        data = {
            'device_fingerprint': 'test_fingerprint',
            'action': 'add'
        }
        
        serializer = TrustedDeviceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_admin_user_list_serializer(self):
        """Test AdminUserListSerializer"""
        serializer = AdminUserListSerializer(instance=self.test_user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertIn('role', data)
        self.assertIn('organization_name', data)
    
    def test_admin_user_create_serializer(self):
        """Test AdminUserCreateSerializer"""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'NewUserPassword123!',
            'role': 'viewer',
            'organization': str(self.organization.id)
        }
        
        serializer = AdminUserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_organization_serializer(self):
        """Test OrganizationSerializer"""
        serializer = OrganizationSerializer(instance=self.organization)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Organization')
        self.assertEqual(data['domain'], 'test.com')


class ValidatorTestCase(TestCase):
    """Test validator functionality"""
    
    def setUp(self):
        self.username_validator = UsernameValidator()
        self.email_validator = EmailValidator()
        self.password_validator = CustomPasswordValidator()
    
    def test_username_validator_valid(self):
        """Test username validator with valid usernames"""
        valid_usernames = ['testuser', 'user123', 'test_user', 'user-name']
        
        for username in valid_usernames:
            try:
                self.username_validator.validate(username)
            except Exception:
                self.fail(f"Username '{username}' should be valid")
    
    def test_username_validator_invalid(self):
        """Test username validator with invalid usernames"""
        invalid_usernames = ['', 'a', 'user@name', 'user name', '123456789012345678901234567890123456789012345678901']
        
        for username in invalid_usernames:
            with self.assertRaises(Exception):
                self.username_validator.validate(username)
    
    def test_email_validator_valid(self):
        """Test email validator with valid emails"""
        valid_emails = ['test@example.com', 'user.name@domain.org', 'user+tag@example.co.uk']
        
        for email in valid_emails:
            try:
                self.email_validator.validate(email)
            except Exception:
                self.fail(f"Email '{email}' should be valid")
    
    def test_email_validator_invalid(self):
        """Test email validator with invalid emails"""
        invalid_emails = ['', 'notanemail', '@domain.com', 'user@', 'user@temp-mail.org']
        
        for email in invalid_emails:
            with self.assertRaises(Exception):
                self.email_validator.validate(email)
    
    def test_password_validator_valid(self):
        """Test password validator with valid passwords"""
        valid_passwords = ['Password123!', 'ValidPass1@', 'SecureP@ssw0rd']
        
        for password in valid_passwords:
            try:
                self.password_validator.validate(password)
            except Exception:
                self.fail(f"Password should be valid")
    
    def test_password_validator_invalid(self):
        """Test password validator with invalid passwords"""
        invalid_passwords = ['', '123', 'password', 'PASSWORD', '12345678']
        
        for password in invalid_passwords:
            with self.assertRaises(Exception):
                self.password_validator.validate(password)


# Signals are tested implicitly through user operations


class PermissionHelperTestCase(TestCase):
    """Test permission helper functions"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.admin_user = UserFactory.create_user('BlueVisionAdmin', {
            'username': 'admin',
            'email': 'admin@test.com',
            'password': 'AdminPassword123!',
            'organization': self.organization
        })
        
        self.viewer_user = UserFactory.create_user('viewer', {
            'username': 'viewer',
            'email': 'viewer@test.com',
            'password': 'ViewerPassword123!',
            'organization': self.organization
        })
    
    def test_check_stix_object_permission(self):
        """Test STIX object permission checking"""
        # Mock STIX object
        stix_object = Mock()
        stix_object.id = 'test_stix_id'
        stix_object.created_by = self.viewer_user
        
        # Admin should have access
        self.assertTrue(check_stix_object_permission(self.admin_user, stix_object, 'read'))
        self.assertTrue(check_stix_object_permission(self.admin_user, stix_object, 'write'))
        self.assertTrue(check_stix_object_permission(self.admin_user, stix_object, 'admin'))
        
        # User should have read access to own objects
        self.assertTrue(check_stix_object_permission(self.viewer_user, stix_object, 'read'))
    
    def test_check_feed_publish_permission(self):
        """Test feed publish permission checking"""
        # Mock feed object
        feed = Mock()
        feed.organization = self.organization
        feed.created_by = self.viewer_user
        
        # Admin should be able to publish
        self.assertTrue(check_feed_publish_permission(self.admin_user, feed))
        
        # Viewer cannot publish (not a publisher)
        self.assertFalse(check_feed_publish_permission(self.viewer_user, feed))
    
    def test_rate_limit_permission(self):
        """Test rate limit permission"""
        permission = RateLimitPermission()
        
        request = Mock()
        request.user = self.viewer_user
        
        # Should pass basic checks
        self.assertTrue(permission.has_permission(request, None))
        
        # Should fail if user is locked
        self.viewer_user.lock_account()
        self.assertFalse(permission.has_permission(request, None))


class FactoryTestCase(TestCase):
    """Test factory edge cases"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.admin_user = UserFactory.create_user('BlueVisionAdmin', {
            'username': 'admin',
            'email': 'admin@test.com',
            'password': 'AdminPassword123!',
            'organization': self.organization
        })
    
    def test_create_user_with_auto_password(self):
        """Test creating user with auto-generated password"""
        user_data = {
            'username': 'autouser',
            'email': 'autouser@test.com',
            'first_name': 'Auto',
            'last_name': 'User',
            'organization': self.organization
        }
        
        user, password = UserFactory.create_user_with_auto_password(
            'viewer', user_data, self.admin_user
        )
        
        self.assertIsNotNone(password)
        self.assertTrue(len(password) >= 16)
        self.assertTrue(user.check_password(password))
    
    def test_factory_validation_errors(self):
        """Test factory validation errors"""
        from django.core.exceptions import ValidationError
        
        # Missing required fields
        with self.assertRaises(ValidationError):
            UserFactory.create_user('viewer', {}, self.admin_user)
        
        # Invalid email
        with self.assertRaises(ValidationError):
            UserFactory.create_user('viewer', {
                'username': 'testuser',
                'email': 'invalid_email',
                'password': 'TestPassword123!',
                'organization': self.organization
            }, self.admin_user)


class ModelTestCase(TestCase):
    """Test model edge cases and methods"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        self.test_user = UserFactory.create_user('viewer', {
            'username': 'testuser',
            'email': 'testuser@test.com',
            'password': 'TestPassword123!',
            'organization': self.organization
        })
    
    def test_organization_str_method(self):
        """Test Organization __str__ method"""
        self.assertEqual(str(self.organization), 'Test Organization')
    
    def test_custom_user_str_method(self):
        """Test CustomUser __str__ method"""
        expected = f"testuser (Test Organization)"
        self.assertEqual(str(self.test_user), expected)
    
    def test_user_session_properties(self):
        """Test UserSession properties"""
        from django.utils import timezone
        from datetime import timedelta
        
        session = UserSession.objects.create(
            user=self.test_user,
            session_token='test_token',
            refresh_token='test_refresh',
            device_info={},
            ip_address='127.0.0.1',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        self.assertFalse(session.is_expired)
        self.assertIn('testuser', str(session))
        
        # Test session extension
        old_expires = session.expires_at
        session.extend_session(2)
        session.refresh_from_db()
        self.assertGreater(session.expires_at, old_expires)
    
    def test_authentication_log_class_method(self):
        """Test AuthenticationLog class method"""
        log = AuthenticationLog.log_authentication_event(
            user=self.test_user,
            action='test_action',
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            success=True,
            failure_reason=None,
            additional_data={'test': 'data'}
        )
        
        self.assertEqual(log.username, 'testuser')
        self.assertEqual(log.action, 'test_action')
        self.assertTrue(log.success)
        self.assertEqual(log.additional_data['test'], 'data')
        
        # Test string representation
        self.assertIn('testuser', str(log))
        self.assertIn('SUCCESS', str(log))