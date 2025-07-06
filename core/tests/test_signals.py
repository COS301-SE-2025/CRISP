"""
Comprehensive tests for core signals functionality.
"""
import django
from django.test import TestCase, RequestFactory
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from unittest.mock import patch, Mock, MagicMock
from threading import Thread
import time

from core.signals import (
    AuditSignalHandler,
    AuditSignalMiddleware,
    log_user_changes,
    log_organization_changes,
    log_trust_relationship_changes,
    log_trust_group_changes,
    log_user_deletion,
    log_trust_relationship_deletion,
    log_user_login,
    log_user_logout,
    log_user_login_failure,
    _thread_local
)
from core.user_management.models import CustomUser, Organization
from core.trust.models import TrustLevel, TrustGroup, TrustRelationship


class AuditSignalHandlerTest(TestCase):
    """Test the AuditSignalHandler utility class."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="university"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.organization
        )
    
    def test_set_and_get_current_user(self):
        """Test setting and getting current user in thread local storage."""
        # Initially no user
        self.assertIsNone(AuditSignalHandler.get_current_user())
        
        # Set user
        AuditSignalHandler.set_current_user(self.user)
        self.assertEqual(AuditSignalHandler.get_current_user(), self.user)
        
        # Clear user
        AuditSignalHandler.set_current_user(None)
        self.assertIsNone(AuditSignalHandler.get_current_user())
    
    def test_thread_isolation(self):
        """Test that thread local storage properly isolates users between threads."""
        results = {}
        
        def set_user_in_thread(user, thread_id):
            AuditSignalHandler.set_current_user(user)
            time.sleep(0.1)  # Small delay to ensure threads overlap
            results[thread_id] = AuditSignalHandler.get_current_user()
        
        # Create two users
        user2 = CustomUser.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="testpass123",
            organization=self.organization
        )
        
        # Run in separate threads
        thread1 = Thread(target=set_user_in_thread, args=(self.user, 'thread1'))
        thread2 = Thread(target=set_user_in_thread, args=(user2, 'thread2'))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Each thread should have its own user
        self.assertEqual(results['thread1'], self.user)
        self.assertEqual(results['thread2'], user2)


class UserSignalTest(TestCase):
    """Test user-related signal handlers."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="university"
        )
    
    @patch('core.services.audit_service.AuditService')
    def test_log_user_changes_created(self, mock_audit_service):
        """Test logging when a user is created."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Set current user
        admin_user = CustomUser.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            organization=self.organization,
            role="admin"
        )
        AuditSignalHandler.set_current_user(admin_user)
        
        # Create new user (this should trigger the signal)
        new_user = CustomUser.objects.create_user(
            username="newuser",
            email="new@test.com",
            password="testpass123",
            organization=self.organization
        )
        
        # Verify audit service was called
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertEqual(kwargs['user'], admin_user)
        self.assertEqual(kwargs['action'], 'user_created')
        self.assertTrue(kwargs['success'])
        self.assertEqual(kwargs['target_user'], new_user)
        self.assertIn('target_user_id', kwargs['additional_data'])
        self.assertEqual(kwargs['additional_data']['target_username'], 'newuser')
    
    @patch('core.services.audit_service.AuditService')
    def test_log_user_changes_modified(self, mock_audit_service):
        """Test logging when a user is modified."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create user first
        user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.organization
        )
        
        # Reset mock after creation
        mock_service_instance.reset_mock()
        
        # Set current user
        AuditSignalHandler.set_current_user(user)
        
        # Modify user (this should trigger the signal)
        user.email = "newemail@test.com"
        user.save()
        
        # Verify audit service was called for modification
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertEqual(kwargs['action'], 'user_modified')
        self.assertTrue(kwargs['success'])
    
    @patch('core.services.audit_service.AuditService')
    @patch('core.signals.logger')
    def test_log_user_changes_exception_handling(self, mock_logger, mock_audit_service):
        """Test exception handling in user change logging."""
        mock_audit_service.side_effect = Exception("Service error")
        
        # Create user (this should trigger the signal but catch exception)
        CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.organization
        )
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
        self.assertIn("Failed to log user changes", mock_logger.error.call_args[0][0])
    
    @patch('core.services.audit_service.AuditService')
    def test_log_user_deletion(self, mock_audit_service):
        """Test logging when a user is deleted."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create user
        user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.organization
        )
        user_id = user.id
        username = user.username
        
        # Set current user
        admin_user = CustomUser.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            organization=self.organization,
            role="admin"
        )
        AuditSignalHandler.set_current_user(admin_user)
        
        # Reset mock after user creation
        mock_service_instance.reset_mock()
        
        # Delete user (this should trigger the signal)
        user.delete()
        
        # Verify audit service was called
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertEqual(kwargs['user'], admin_user)
        self.assertEqual(kwargs['action'], 'user_deleted')
        self.assertTrue(kwargs['success'])
        self.assertEqual(kwargs['additional_data']['deleted_username'], username)


class OrganizationSignalTest(TestCase):
    """Test organization-related signal handlers."""
    
    @patch('core.services.audit_service.AuditService')
    def test_log_organization_changes_created(self, mock_audit_service):
        """Test logging when an organization is created."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create organization (this should trigger the signal)
        org = Organization.objects.create(
            name="New Org",
            domain="neworg.com",
            organization_type="company",
            is_publisher=True
        )
        
        # Verify audit service was called
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertEqual(kwargs['action'], 'organization_created')
        self.assertTrue(kwargs['success'])
        self.assertEqual(kwargs['target_organization'], org)
        self.assertIn('target_organization_name', kwargs['additional_data'])
        self.assertEqual(kwargs['additional_data']['target_organization_name'], 'New Org')
        self.assertTrue(kwargs['additional_data']['is_publisher'])
    
    @patch('core.services.audit_service.AuditService')
    def test_log_organization_changes_modified(self, mock_audit_service):
        """Test logging when an organization is modified."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create organization first
        org = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="university"
        )
        
        # Reset mock after creation
        mock_service_instance.reset_mock()
        
        # Modify organization (this should trigger the signal)
        org.name = "Modified Org"
        org.save()
        
        # Verify audit service was called for modification
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertEqual(kwargs['action'], 'organization_modified')
        self.assertTrue(kwargs['success'])


class TrustSignalTest(TestCase):
    """Test trust-related signal handlers."""
    
    def setUp(self):
        """Set up test data."""
        self.org1 = Organization.objects.create(
            name="Org 1",
            domain="org1.com",
            organization_type="university"
        )
        self.org2 = Organization.objects.create(
            name="Org 2",
            domain="org2.com",
            organization_type="company"
        )
        self.trust_level = TrustLevel.objects.create(
            name="High",
            level="trusted",
            numerical_value=80,
            description="High trust",
            created_by="system"
        )
    
    @patch('core.services.audit_service.AuditService')
    def test_log_trust_relationship_changes_created(self, mock_audit_service):
        """Test logging when a trust relationship is created."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create trust relationship (this should trigger the signal)
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status="pending"
        )
        
        # Verify audit service was called
        mock_service_instance.log_trust_event.assert_called_once()
        args, kwargs = mock_service_instance.log_trust_event.call_args
        
        self.assertEqual(kwargs['action'], 'relationship_created')
        self.assertTrue(kwargs['success'])
        self.assertEqual(kwargs['trust_relationship'], relationship)
        self.assertIn('source_organization', kwargs['additional_data'])
        self.assertEqual(kwargs['additional_data']['source_organization'], 'Org 1')
        self.assertEqual(kwargs['additional_data']['target_organization'], 'Org 2')
    
    @patch('core.services.audit_service.AuditService')
    def test_log_trust_relationship_deletion(self, mock_audit_service):
        """Test logging when a trust relationship is deleted."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create trust relationship first
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status="active"
        )
        
        # Reset mock after creation
        mock_service_instance.reset_mock()
        
        # Delete relationship (this should trigger the signal)
        relationship.delete()
        
        # Verify audit service was called
        mock_service_instance.log_trust_event.assert_called_once()
        args, kwargs = mock_service_instance.log_trust_event.call_args
        
        self.assertEqual(kwargs['action'], 'relationship_deleted')
        self.assertTrue(kwargs['success'])
        self.assertIn('deleted_relationship_id', kwargs['additional_data'])
    
    @patch('core.services.audit_service.AuditService')
    def test_log_trust_group_changes_created(self, mock_audit_service):
        """Test logging when a trust group is created."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create trust group (this should trigger the signal)
        group = TrustGroup.objects.create(
            name="Test Group",
            description="Test description",
            default_trust_level=self.trust_level,
            is_public=True
        )
        
        # Verify audit service was called
        mock_service_instance.log_trust_event.assert_called_once()
        args, kwargs = mock_service_instance.log_trust_event.call_args
        
        self.assertEqual(kwargs['action'], 'group_created')
        self.assertTrue(kwargs['success'])
        self.assertEqual(kwargs['trust_group'], group)
        self.assertIn('group_name', kwargs['additional_data'])
        self.assertEqual(kwargs['additional_data']['group_name'], 'Test Group')
        self.assertTrue(kwargs['additional_data']['is_public'])


class AuthenticationSignalTest(TestCase):
    """Test authentication-related signal handlers."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.organization = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="university"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.organization
        )
    
    @patch('core.services.audit_service.AuditService')
    def test_log_user_login(self, mock_audit_service):
        """Test logging successful user login."""
        mock_service_instance = Mock()
        mock_service_instance._get_client_ip.return_value = '127.0.0.1'
        mock_audit_service.return_value = mock_service_instance
        
        # Create mock request
        request = self.factory.post('/login/')
        request.session = Mock()
        request.session.session_key = 'test_session_key'
        request.META = {'HTTP_USER_AGENT': 'Test Agent'}
        
        # Trigger login signal
        user_logged_in.send(sender=self.user.__class__, request=request, user=self.user)
        
        # Verify audit service was called
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertEqual(kwargs['user'], self.user)
        self.assertEqual(kwargs['action'], 'login_success')
        self.assertTrue(kwargs['success'])
        self.assertEqual(kwargs['user_agent'], 'Test Agent')
        self.assertIn('login_method', kwargs['additional_data'])
    
    @patch('core.services.audit_service.AuditService')
    def test_log_user_logout(self, mock_audit_service):
        """Test logging user logout."""
        mock_service_instance = Mock()
        mock_service_instance._get_client_ip.return_value = '127.0.0.1'
        mock_audit_service.return_value = mock_service_instance
        
        # Create mock request
        request = self.factory.post('/logout/')
        request.session = Mock()
        request.session.session_key = 'test_session_key'
        request.META = {'HTTP_USER_AGENT': 'Test Agent'}
        
        # Trigger logout signal
        user_logged_out.send(sender=self.user.__class__, request=request, user=self.user)
        
        # Verify audit service was called
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertEqual(kwargs['user'], self.user)
        self.assertEqual(kwargs['action'], 'logout')
        self.assertTrue(kwargs['success'])
    
    @patch('core.services.audit_service.AuditService')
    def test_log_user_login_failure(self, mock_audit_service):
        """Test logging failed login attempts."""
        mock_service_instance = Mock()
        mock_service_instance._get_client_ip.return_value = '127.0.0.1'
        mock_audit_service.return_value = mock_service_instance
        
        # Create mock request
        request = self.factory.post('/login/')
        request.META = {'HTTP_USER_AGENT': 'Test Agent'}
        credentials = {'username': 'testuser', 'password': 'wrongpass'}
        
        # Trigger login failed signal
        user_login_failed.send(
            sender=None,
            credentials=credentials,
            request=request
        )
        
        # Verify audit service was called
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        
        self.assertIsNone(kwargs['user'])
        self.assertEqual(kwargs['action'], 'login_failure')
        self.assertFalse(kwargs['success'])
        self.assertEqual(kwargs['failure_reason'], 'Invalid credentials')
        self.assertIn('attempted_username', kwargs['additional_data'])
    
    @patch('core.services.audit_service.AuditService')
    def test_authentication_signal_without_get_client_ip(self, mock_audit_service):
        """Test authentication signals when audit service doesn't have _get_client_ip method."""
        mock_service_instance = Mock()
        # Don't add _get_client_ip method to simulate missing method
        delattr(mock_service_instance, '_get_client_ip') if hasattr(mock_service_instance, '_get_client_ip') else None
        mock_audit_service.return_value = mock_service_instance
        
        # Create mock request
        request = self.factory.post('/login/')
        request.session = Mock()
        request.session.session_key = 'test_session_key'
        request.META = {'HTTP_USER_AGENT': 'Test Agent'}
        
        # Trigger login signal
        user_logged_in.send(sender=self.user.__class__, request=request, user=self.user)
        
        # Should still work, just without IP address
        mock_service_instance.log_user_event.assert_called_once()
        args, kwargs = mock_service_instance.log_user_event.call_args
        self.assertIsNone(kwargs['ip_address'])


class AuditSignalMiddlewareTest(TestCase):
    """Test the AuditSignalMiddleware."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.organization = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="university"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.organization
        )
        
        # Mock get_response
        self.mock_get_response = Mock(return_value=Mock())
        self.middleware = AuditSignalMiddleware(self.mock_get_response)
    
    def test_middleware_with_authenticated_user(self):
        """Test middleware with authenticated user."""
        request = self.factory.get('/')
        request.user = self.user
        request.user.is_authenticated = True
        
        # Process request
        response = self.middleware(request)
        
        # Verify get_response was called
        self.mock_get_response.assert_called_once_with(request)
        
        # Current user should be cleared after request
        self.assertIsNone(AuditSignalHandler.get_current_user())
    
    def test_middleware_with_anonymous_user(self):
        """Test middleware with anonymous user."""
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        # Process request
        response = self.middleware(request)
        
        # Verify get_response was called
        self.mock_get_response.assert_called_once_with(request)
        
        # Current user should be None
        self.assertIsNone(AuditSignalHandler.get_current_user())
    
    def test_middleware_without_user_attribute(self):
        """Test middleware when request doesn't have user attribute."""
        request = self.factory.get('/')
        # Don't set request.user
        
        # Process request
        response = self.middleware(request)
        
        # Should handle gracefully
        self.mock_get_response.assert_called_once_with(request)
        self.assertIsNone(AuditSignalHandler.get_current_user())
    
    def test_middleware_clears_user_after_request(self):
        """Test that middleware clears user after request processing."""
        request = self.factory.get('/')
        request.user = self.user
        request.user.is_authenticated = True
        
        # Set a user manually first
        AuditSignalHandler.set_current_user(self.user)
        self.assertEqual(AuditSignalHandler.get_current_user(), self.user)
        
        # Process request
        response = self.middleware(request)
        
        # User should be cleared after request
        self.assertIsNone(AuditSignalHandler.get_current_user())


class SignalIntegrationTest(TestCase):
    """Integration tests for signal functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="university"
        )
        self.trust_level = TrustLevel.objects.create(
            name="Medium",
            level="trusted",
            numerical_value=50,
            description="Medium trust",
            created_by="system"
        )
    
    @patch('core.services.audit_service.AuditService')
    def test_end_to_end_signal_flow(self, mock_audit_service):
        """Test complete signal flow with real model operations."""
        mock_service_instance = Mock()
        mock_audit_service.return_value = mock_service_instance
        
        # Create admin user
        admin = CustomUser.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            organization=self.organization,
            role="admin"
        )
        AuditSignalHandler.set_current_user(admin)
        
        # Reset mock after admin creation
        mock_service_instance.reset_mock()
        
        # Create regular user (should trigger signal)
        user = CustomUser.objects.create_user(
            username="newuser",
            email="new@test.com",
            password="testpass123",
            organization=self.organization
        )
        
        # Create trust group (should trigger signal)
        group = TrustGroup.objects.create(
            name="Test Group",
            description="Test description",
            default_trust_level=self.trust_level
        )
        
        # Verify both signals were triggered
        self.assertEqual(mock_service_instance.log_user_event.call_count, 1)
        self.assertEqual(mock_service_instance.log_trust_event.call_count, 1)
    
    def test_signal_exception_isolation(self):
        """Test that signal exceptions don't affect normal model operations."""
        with patch('core.signals.AuditService') as mock_audit_service:
            mock_audit_service.side_effect = Exception("Service error")
            
            # Model operations should still work despite signal failures
            user = CustomUser.objects.create_user(
                username="testuser",
                email="test@test.com",
                password="testpass123",
                organization=self.organization
            )
            
            # User should be created successfully
            self.assertTrue(CustomUser.objects.filter(username="testuser").exists())
            
            # Modify user should also work
            user.email = "newemail@test.com"
            user.save()
            
            # Verify changes persisted
            user.refresh_from_db()
            self.assertEqual(user.email, "newemail@test.com")