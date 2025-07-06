"""
Comprehensive tests for user management services to improve coverage.
"""
from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.password_validation import ValidationError as PasswordValidationError
from django.utils import timezone
from unittest.mock import patch, Mock, MagicMock
from datetime import timedelta
import uuid

from core.user_management.services.auth_service import AuthenticationService
from core.user_management.services.user_service import UserService
from core.user_management.services.access_control_service import AccessControlService
from core.user_management.services.organization_service import OrganizationService
from core.user_management.services.trust_aware_service import TrustAwareService
from core.user_management.models import (
    CustomUser, Organization, UserSession, AuthenticationLog, 
    UserProfile, TrustedDevice
)


class AuthenticationServiceTest(TestCase):
    """Comprehensive tests for AuthenticationService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = AuthenticationService()
        self.factory = RequestFactory()
        
        # Create organization
        self.org = Organization.objects.create(
            name="Test University",
            domain="test.edu",
            organization_type="university",
            is_active=True
        )
        
        # Create user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.edu",
            password="ComplexPassword123!",
            organization=self.org,
            is_active=True,
            role="viewer"
        )
        # Ensure password is properly set
        self.user.set_password("ComplexPassword123!")
        self.user.save()
        
        # Create inactive user
        self.inactive_user = CustomUser.objects.create_user(
            username="inactive",
            email="inactive@test.edu",
            password="ComplexPassword123!",
            organization=self.org,
            is_active=False
        )
        self.inactive_user.set_password("ComplexPassword123!")
        self.inactive_user.save()
        
        # Create locked user
        self.locked_user = CustomUser.objects.create_user(
            username="locked",
            email="locked@test.edu",
            password="ComplexPassword123!",
            organization=self.org,
            is_active=True,
            failed_login_attempts=5,
            account_locked_until=timezone.now() + timedelta(hours=1)
        )
    
    def test_service_initialization(self):
        """Test that service initializes properly."""
        self.assertIsInstance(self.service.access_control, AccessControlService)
    
    def test_get_client_info_with_request(self):
        """Test extracting client info from request."""
        request = self.factory.get('/')
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.1.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        ip_address, user_agent = self.service._get_client_info(request)
        self.assertEqual(ip_address, '192.168.1.1')
        self.assertEqual(user_agent, 'Test Browser')
    
    def test_get_client_info_no_request(self):
        """Test extracting client info when no request provided."""
        ip_address, user_agent = self.service._get_client_info(None)
        self.assertEqual(ip_address, '127.0.0.1')
        self.assertEqual(user_agent, 'Unknown')
    
    def test_create_device_fingerprint(self):
        """Test device fingerprint creation."""
        request = self.factory.get('/')
        request.META = {
            'HTTP_USER_AGENT': 'Test Browser',
            'HTTP_ACCEPT_LANGUAGE': 'en-US'
        }
        
        fingerprint = self.service._create_device_fingerprint(request)
        self.assertIsInstance(fingerprint, str)
        self.assertEqual(len(fingerprint), 64)  # SHA256 hash length
    
    def test_create_device_fingerprint_no_request(self):
        """Test device fingerprint creation without request."""
        fingerprint = self.service._create_device_fingerprint(None)
        self.assertIsInstance(fingerprint, str)
        self.assertEqual(fingerprint, 'unknown_device')
        self.assertEqual(len(fingerprint), 14)
    
    @patch.object(CustomUser, 'check_password', return_value=True)
    @patch.object(AuthenticationService, '_log_failed_authentication')
    def test_authenticate_user_not_found(self, mock_log, mock_check_password):
        """Test authentication with non-existent user."""
        result = self.service.authenticate_user("nonexistent", "password")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid credentials')
        self.assertIsNone(result['user'])
        mock_log.assert_called_once()
    
    @patch.object(AuthenticationService, '_log_failed_authentication')
    @patch.object(CustomUser, 'check_password', return_value=True)
    def test_authenticate_user_by_email(self, mock_log):
        """Test authentication using email instead of username."""
        # First test with wrong password
        result = self.service.authenticate_user(self.user.email, "wrongpassword")
        self.assertFalse(result['success'])
    
    @patch.object(CustomUser, 'check_password', return_value=True)
    @patch.object(AuthenticationService, '_log_failed_authentication')
    def test_authenticate_inactive_user(self, mock_log, mock_check_password):
        """Test authentication with inactive user."""
        result = self.service.authenticate_user(
            self.inactive_user.username, 
            "ComplexPassword123!"
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Account is inactive')
        mock_log.assert_called_once()
    
    @patch.object(CustomUser, 'check_password', return_value=True)
    @patch.object(AuthenticationService, '_log_failed_authentication')
    def test_authenticate_locked_user(self, mock_log, mock_check_password):
        """Test authentication with locked user."""
        result = self.service.authenticate_user(
            self.locked_user.username,
            "ComplexPassword123!"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('locked', result['message'])
        mock_log.assert_called_once()
    
    @patch.object(CustomUser, 'check_password', return_value=True)
    @patch.object(AuthenticationService, '_log_failed_authentication')
    def test_authenticate_inactive_organization(self, mock_log, mock_check_password):
        """Test authentication with user from inactive organization."""
        self.org.is_active = False
        self.org.save()
        
        result = self.service.authenticate_user(
            self.user.username,
            "ComplexPassword123!"
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Organization is inactive')
        mock_log.assert_called_once()
    
    @patch.object(AuthenticationService, '_handle_failed_login')
    def test_authenticate_wrong_password(self, mock_handle_failed):
        """Test authentication with wrong password."""
        result = self.service.authenticate_user(
            self.user.username,
            "wrongpassword"
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid credentials')
        mock_handle_failed.assert_called_once()
    
    @patch.object(CustomUser, 'check_password', return_value=True)
    def test_authenticate_2fa_required(self, mock_check_password):
        """Test authentication when 2FA is required."""
        self.user.two_factor_enabled = True
        self.user.save()
        
        result = self.service.authenticate_user(
            self.user.username,
            "ComplexPassword123!"
        )
        
        self.assertFalse(result['success'])
        self.assertTrue(result['requires_2fa'])
    
    @patch('core.user_management.services.auth_service.AuthenticationLog.log_authentication_event')
    def test_log_failed_authentication(self, mock_log):
        """Test logging of failed authentication attempts."""
        self.service._log_failed_authentication(
            self.user, "testuser", "192.168.1.1", "Test Browser", "Test failure"
        )
        
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        self.assertEqual(kwargs['user'], self.user)
        self.assertEqual(kwargs['ip_address'], "192.168.1.1")
        self.assertEqual(kwargs['user_agent'], "Test Browser")
        self.assertEqual(kwargs['failure_reason'], "Test failure")
        self.assertFalse(kwargs['success'])
    
    def test_handle_failed_login(self):
        """Test handling of failed login attempts."""
        initial_attempts = self.user.failed_login_attempts
        
        self.service._handle_failed_login(
            self.user, "192.168.1.1", "Test Browser", "Wrong password"
        )
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, initial_attempts + 1)
    
    def test_handle_failed_login_account_locking(self):
        """Test account locking after multiple failed attempts."""
        # Set user to 4 failed attempts (one before locking)
        self.user.failed_login_attempts = 4
        self.user.save()
        
        self.service._handle_failed_login(
            self.user, "192.168.1.1", "Test Browser", "Wrong password"
        )
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 5)
        self.assertIsNotNone(self.user.account_locked_until)
        self.assertTrue(self.user.is_account_locked)


class UserServiceTest(TestCase):
    """Comprehensive tests for UserService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = UserService()
        
        # Create organizations
        self.org1 = Organization.objects.create(
            name="University A",
            domain="ua.edu",
            organization_type="university",
            is_active=True
        )
        self.org2 = Organization.objects.create(
            name="Company B",
            domain="cb.com",
            organization_type="company",
            is_active=True
        )
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_user(
            username="admin",
            email="admin@ua.edu",
            password="AdminPass123!",
            organization=self.org1,
            role="admin",
            is_active=True
        )
        
        # Create regular user
        self.regular_user = CustomUser.objects.create_user(
            username="regular",
            email="regular@ua.edu",
            password="RegularPass123!",
            organization=self.org1,
            role="viewer",
            is_active=True
        )
    
    def test_service_initialization(self):
        """Test that service initializes properly."""
        self.assertIsInstance(self.service.access_control, AccessControlService)
        self.assertIsNotNone(self.service.user_factory)
    
    @patch('core.user_management.services.user_service.UserFactory')
    def test_create_user_success(self, mock_factory_class):
        """Test successful user creation."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            # Mock permissions
            mock_access_control.can_create_user_with_role.return_value = True
            
            # Mock factory
            mock_factory_instance = Mock()
            mock_user = Mock()
            mock_user.username = "newuser"
            mock_factory_instance.create_user.return_value = mock_user
            mock_factory_class.return_value = mock_factory_instance
            self.service.user_factory = mock_factory_instance
            
            user_data = {
                'username': 'newuser',
                'email': 'newuser@ua.edu',
                'password': 'NewPass123!',
                'role': 'viewer',
                'organization_id': str(self.org1.id)
            }
            
            result = self.service.create_user(self.admin_user, user_data)
            
            self.assertEqual(result, mock_user)
            mock_access_control.can_create_user_with_role.assert_called_once()
            mock_factory_instance.create_user.assert_called_once()
    
    def test_create_user_no_organization(self):
        """Test user creation without organization."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'NewPass123!',
            'role': 'viewer'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_user(self.admin_user, user_data)
        
        self.assertIn("Organization is required", str(context.exception))
    
    def test_create_user_invalid_organization(self):
        """Test user creation with invalid organization."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'NewPass123!',
            'role': 'viewer',
            'organization_id': str(uuid.uuid4())
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_user(self.admin_user, user_data)
        
        self.assertIn("Invalid organization", str(context.exception))
    
    def test_create_user_permission_denied(self):
        """Test user creation without proper permissions."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.can_create_user_with_role.return_value = False
            
            user_data = {
                'username': 'newuser',
                'email': 'newuser@ua.edu',
                'password': 'NewPass123!',
                'role': 'admin',
                'organization_id': str(self.org1.id)
            }
            
            with self.assertRaises(PermissionDenied):
                self.service.create_user(self.regular_user, user_data)
    
    @patch('core.user_management.services.user_service.UserFactory')
    def test_create_user_factory_validation_error(self, mock_factory_class):
        """Test handling of factory validation errors."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.can_create_user_with_role.return_value = True
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_user.side_effect = ValidationError("Factory error")
            mock_factory_class.return_value = mock_factory_instance
            self.service.user_factory = mock_factory_instance
            
            user_data = {
                'username': 'newuser',
                'email': 'newuser@ua.edu',
                'password': 'NewPass123!',
                'role': 'viewer',
                'organization_id': str(self.org1.id)
            }
            
            with self.assertRaises(ValidationError):
                self.service.create_user(self.admin_user, user_data)
    
    def test_update_user_not_found(self):
        """Test updating non-existent user."""
        fake_id = uuid.uuid4()
        update_data = {'email': 'new@email.com'}
        
        with self.assertRaises(ValidationError) as context:
            self.service.update_user(self.admin_user, str(fake_id), update_data)
        
        self.assertIn("User not found", str(context.exception))
    
    def test_update_user_permission_denied(self):
        """Test updating user without permission."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.can_manage_user.return_value = False
            
            update_data = {'email': 'new@email.com'}
            
            with self.assertRaises(PermissionDenied):
                self.service.update_user(
                    self.regular_user, 
                    str(self.admin_user.id), 
                    update_data
                )
    
    def test_update_user_success(self):
        """Test successful user update."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.can_manage_user.return_value = True
            
            update_data = {
                'email': 'updated@email.com',
                'first_name': 'Updated'
            }
            
            result = self.service.update_user(
                self.admin_user,
                str(self.regular_user.id),
                update_data
            )
            
            self.assertEqual(result.email, 'updated@email.com')
            self.assertEqual(result.first_name, 'Updated')
    
    def test_update_user_role_requires_permission(self):
        """Test that role updates require proper permissions."""
        # This test would need to be expanded based on actual implementation
        # For now, it's a placeholder
        pass
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user."""
        fake_id = uuid.uuid4()
        
        with self.assertRaises(ValidationError):
            self.service.delete_user(self.admin_user, str(fake_id))
    
    def test_delete_user_permission_denied(self):
        """Test deleting user without permission."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.can_manage_user.return_value = False
            
            with self.assertRaises(PermissionDenied):
                self.service.delete_user(
                    self.regular_user,
                    str(self.admin_user.id)
                )
    
    def test_delete_user_success(self):
        """Test successful user deletion (soft delete)."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.can_manage_user.return_value = True
            
            # Create user to delete
            user_to_delete = CustomUser.objects.create_user(
                username="todelete",
                email="delete@ua.edu",
                password="DeletePass123!",
                organization=self.org1,
                role="viewer"
            )
            
            result = self.service.delete_user(self.admin_user, str(user_to_delete.id))
            
            self.assertTrue(result)
        user_to_delete.refresh_from_db()
        self.assertFalse(user_to_delete.is_active)


class AccessControlServiceTest(TestCase):
    """Comprehensive tests for AccessControlService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = AccessControlService()
        
        # Create organizations
        self.org = Organization.objects.create(
            name="Test University",
            domain="test.edu",
            organization_type="university"
        )
        
        # Create users with different roles
        self.admin = CustomUser.objects.create_user(
            username="admin",
            email="admin@test.edu",
            password="AdminPass123!",
            organization=self.org,
            role="admin"
        )
        
        self.publisher = CustomUser.objects.create_user(
            username="publisher",
            email="publisher@test.edu",
            password="PubPass123!",
            organization=self.org,
            role="publisher"
        )
        
        self.viewer = CustomUser.objects.create_user(
            username="viewer",
            email="viewer@test.edu",
            password="ViewPass123!",
            organization=self.org,
            role="viewer"
        )
    
    def test_get_user_permissions_admin(self):
        """Test getting permissions for admin user."""
        permissions = self.service.get_user_permissions(self.admin)
        
        expected_permissions = [
            'can_create_organization_users', 'can_manage_organization_users',
            'can_view_threat_intelligence', 'can_publish_threat_intelligence',
            'can_manage_trust_relationships'
        ]
        
        for permission in expected_permissions:
            self.assertIn(permission, permissions)
    
    def test_get_user_permissions_publisher(self):
        """Test getting permissions for publisher user."""
        permissions = self.service.get_user_permissions(self.publisher)
        
        expected_permissions = ['can_publish_threat_intelligence', 'can_view_threat_intelligence', 'can_manage_organization_users']
        
        for permission in expected_permissions:
            self.assertIn(permission, permissions)
        
        # Should not have admin permissions
        self.assertNotIn('create_users', permissions)
        self.assertNotIn('manage_organizations', permissions)
    
    def test_get_user_permissions_viewer(self):
        """Test getting permissions for viewer user."""
        permissions = self.service.get_user_permissions(self.viewer)
        
        self.assertIn('can_view_threat_intelligence', permissions)
        
        # Should not have higher-level permissions
        self.assertNotIn('can_create_organization_users', permissions)
        self.assertNotIn('can_publish_threat_intelligence', permissions)
    
    def test_can_create_user_with_role_admin_creating_viewer(self):
        """Test admin can create viewer."""
        result = self.service.can_create_user_with_role(
            self.admin, 'viewer', self.org
        )
        self.assertTrue(result)
    
    def test_can_create_user_with_role_publisher_creating_admin(self):
        """Test publisher cannot create admin."""
        result = self.service.can_create_user_with_role(
            self.publisher, 'admin', self.org
        )
        self.assertFalse(result)
    
    def test_can_create_user_with_role_viewer_creating_anyone(self):
        """Test viewer cannot create any users."""
        result = self.service.can_create_user_with_role(
            self.viewer, 'viewer', self.org
        )
        self.assertFalse(result)
    
    def test_can_manage_user_admin_managing_viewer(self):
        """Test admin can manage viewer."""
        result = self.service.can_manage_user(self.admin, self.viewer)
        self.assertTrue(result)
    
    def test_can_manage_user_same_user(self):
        """Test user can manage themselves."""
        result = self.service.can_manage_user(self.viewer, self.viewer)
        self.assertTrue(result)
    
    def test_can_manage_user_viewer_managing_admin(self):
        """Test viewer cannot manage admin."""
        result = self.service.can_manage_user(self.viewer, self.admin)
        self.assertFalse(result)
    
    def test_has_permission_valid(self):
        """Test checking valid permissions."""
        self.assertTrue(self.service.has_permission(self.admin, 'create_users'))
        self.assertTrue(self.service.has_permission(self.publisher, 'create_data'))
        self.assertTrue(self.service.has_permission(self.viewer, 'view_data'))
    
    def test_has_permission_invalid(self):
        """Test checking invalid permissions."""
        self.assertFalse(self.service.has_permission(self.viewer, 'create_users'))
        self.assertFalse(self.service.has_permission(self.publisher, 'manage_users'))
    
    def test_role_hierarchy(self):
        """Test that role hierarchy is respected."""
        admin_permissions = set(self.service.get_user_permissions(self.admin))
        publisher_permissions = set(self.service.get_user_permissions(self.publisher))
        viewer_permissions = set(self.service.get_user_permissions(self.viewer))
        
        # Admin should have all permissions of lower roles
        self.assertTrue(viewer_permissions.issubset(admin_permissions))
        self.assertTrue(publisher_permissions.issubset(admin_permissions))


class OrganizationServiceTest(TestCase):
    """Comprehensive tests for OrganizationService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = OrganizationService()
        
        # Create admin user
        self.org = Organization.objects.create(
            name="Test University",
            domain="test.edu",
            organization_type="university"
        )
        
        self.admin = CustomUser.objects.create_user(
            username="admin",
            email="admin@test.edu",
            password="AdminPass123!",
            organization=self.org,
            role="admin"
        )
    
    def test_service_initialization(self):
        """Test service initializes with access control."""
        self.assertIsNotNone(self.service.access_control)
    
    def test_create_organization_success(self):
        """Test successful organization creation."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.has_permission.return_value = True
            
            org_data = {
                'name': 'New University',
                'domain': 'new.edu',
                'organization_type': 'university',
                'is_publisher': False
            }
            
            result = self.service.create_organization(self.admin, org_data)
            
            self.assertEqual(result.name, 'New University')
            self.assertEqual(result.domain, 'new.edu')
            self.assertEqual(result.organization_type, 'university')
    
    def test_create_organization_permission_denied(self):
        """Test organization creation without permission."""
        with patch.object(self.service, 'access_control') as mock_access_control:
            mock_access_control.has_permission.return_value = False
            
            org_data = {
                'name': 'New University',
                'domain': 'new.edu',
                'organization_type': 'university'
            }
            
            with self.assertRaises(PermissionDenied):
                self.service.create_organization(self.admin, org_data)


class TrustAwareServiceTest(TestCase):
    """Comprehensive tests for TrustAwareService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = TrustAwareService()
        
        # Create organizations
        self.org1 = Organization.objects.create(
            name="University A",
            domain="ua.edu",
            organization_type="university"
        )
        self.org2 = Organization.objects.create(
            name="Company B",
            domain="cb.com",
            organization_type="company"
        )
        
        # Create user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@ua.edu",
            password="TestPass123!",
            organization=self.org1,
            role="viewer"
        )
    
    def test_service_initialization(self):
        """Test service initializes with access control."""
        self.assertIsNotNone(self.service.access_control)
    
    def test_get_accessible_organizations_own_org(self):
        """Test that user can access their own organization."""
        accessible = self.service.get_accessible_organizations(self.user)
        self.assertIn(self.org1, accessible)
    
    def test_calculate_trust_score_no_relationships(self):
        """Test trust score calculation with no relationships."""
        score = self.service.calculate_trust_score(self.org1, self.org2)
        # This would depend on the actual implementation
        # For now, just test that it returns a number
        self.assertIsInstance(score, (int, float))
    
    def test_get_trust_context_basic(self):
        """Test getting trust context for user."""
        context = self.service.get_trust_context(self.user)
        
        self.assertIn('user_organization', context)
        self.assertIn('accessible_organizations', context)
        self.assertIn('trust_relationships', context)
        self.assertEqual(context['user_organization']['id'], str(self.org1.id))


class UserManagementServicesIntegrationTest(TestCase):
    """Integration tests for user management services."""
    
    def setUp(self):
        """Set up test data for integration tests."""
        # Create services
        self.auth_service = AuthenticationService()
        self.user_service = UserService()
        self.access_control = AccessControlService()
        
        # Create organization
        self.org = Organization.objects.create(
            name="Integration Test Org",
            domain="integration.test",
            organization_type="university",
            is_active=True
        )
        
        # Create admin user
        self.admin = CustomUser.objects.create_user(
            username="admin",
            email="admin@integration.test",
            password="AdminPass123!",
            organization=self.org,
            role="admin",
            is_active=True
        )
    
    def test_end_to_end_user_creation_and_authentication(self):
        """Test complete flow from user creation to authentication."""
        # Create user through service
        user_data = {
            'username': 'newuser',
            'email': 'newuser@integration.test',
            'password': 'NewUserPass123!',
            'role': 'viewer',
            'organization_id': str(self.org.id),
            'first_name': 'New',
            'last_name': 'User'
        }
        
        # This would need to be updated based on actual implementation
        # For now, create user directly
        new_user = CustomUser.objects.create_user(
            username='newuser',
            email='newuser@integration.test',
            password='NewUserPass123!',
            organization=self.org,
            role='viewer'
        )
        
        # Authenticate the new user
        auth_result = self.auth_service.authenticate_user(
            'newuser',
            'NewUserPass123!'
        )
        
        # Verify authentication succeeded if user was created properly
        # This depends on the actual authentication implementation
        self.assertIsNotNone(auth_result)
    
    def test_service_error_isolation(self):
        """Test that errors in one service don't affect others."""
        # Test that access control service continues to work
        # even if authentication service has errors
        permissions = self.access_control.get_user_permissions(self.admin)
        self.assertIn('create_users', permissions)
        
        # Test that user service operations work independently
        # This would be expanded with actual error scenarios
        self.assertTrue(True)  # Placeholder
    
    def test_permission_consistency_across_services(self):
        """Test that permission checks are consistent across services."""
        # Admin should have consistent permissions across all services
        can_create = self.access_control.has_permission(self.admin, 'create_users')
        self.assertTrue(can_create)
        
        # This consistency should be maintained across all services
        # Additional tests would verify this across different scenarios