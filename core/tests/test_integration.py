import json
from django.test import TestCase, TransactionTestCase
from .test_base import CrispTestCase, CrispAPITestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import MagicMock, patch

from ..models import CustomUser, UserSession, AuthenticationLog, STIXObjectPermission, Organization
from ..services.auth_service import AuthenticationService
from ..factories.user_factory import UserFactory


class AuthenticationAPIIntegrationTestCase(CrispAPITestCase):
    """Integration tests for authentication API endpoints"""
    
    def setUp(self):
        super().setUp()
        
        # Create test users
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin',
            is_verified=True
        )
        
        self.regular_user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            role='viewer',
            is_verified=True
        )
    
    
    def test_protected_endpoint_access(self):
        """Test accessing protected endpoints with authentication"""
        # Set up authentication
        self.client.force_authenticate(user=self.regular_user)
        
        # Mock the profile endpoint
        with patch('core.views.auth_views.UserProfileSerializer') as mock_serializer:
            mock_serializer.return_value.data = {
                'id': str(self.regular_user.id),
                'username': self.regular_user.username,
                'email': self.regular_user.email,
                'role': self.regular_user.role
            }
            
            response = self.client.get('/api/auth/profile/')
            self.assertEqual(response.status_code, 200)
    
    def test_admin_endpoint_access_control(self):
        """Test admin endpoint access control"""
        # Regular user should not access admin endpoints
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, 403)
        
        # Admin user should access admin endpoints
        self.client.force_authenticate(user=self.admin_user)
        
        with patch('core.views.admin_views.CustomUser.objects') as mock_objects:
            # Create a mock queryset that supports order_by
            mock_queryset = MagicMock()
            mock_queryset.order_by.return_value = CustomUser.objects.filter(id=self.regular_user.id)
            mock_objects.all.return_value = mock_queryset
            mock_objects.filter.return_value = mock_queryset
            
            response = self.client.get('/api/admin/users/')
            self.assertEqual(response.status_code, 200)
    
    
    def test_logout_flow(self):
        """Test logout flow"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Create a session
        from django.utils import timezone
        from datetime import datetime
        
        session = UserSession.objects.create(
            user=self.regular_user,
            session_token='test_token',
            refresh_token='test_refresh',
            ip_address='127.0.0.1',
            expires_at=timezone.make_aware(datetime(2024, 12, 31, 23, 59, 59))
        )
        
        logout_data = {
            'session_id': str(session.id)
        }
        
        with patch('core.views.auth_views.AuthenticationService') as mock_service:
            mock_service_instance = mock_service.return_value
            mock_service_instance.logout_user.return_value = {
                'success': True,
                'message': 'Logged out successfully'
            }
            
            response = self.client.post('/api/auth/logout/', logout_data)
            self.assertEqual(response.status_code, 200)


class UserManagementAPIIntegrationTestCase(CrispAPITestCase):
    """Integration tests for user management API endpoints"""
    
    def setUp(self):
        super().setUp()
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin',
            is_verified=True
        )
        
        self.client.force_authenticate(user=self.admin_user)
    
    
    def test_user_list_filtering(self):
        """Test user list with filtering"""
        # Create test users
        test_users = []
        for i in range(3):
            user = CustomUser.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password=f'User{i}Password123!',
                organization=self.organization,
                role='viewer'
            )
            test_users.append(user)
        
        # Test filtering by role
        response = self.client.get('/api/admin/users/?role=viewer')
        self.assertEqual(response.status_code, 200)
        
        # Test search functionality
        response = self.client.get('/api/admin/users/?search=user1')
        self.assertEqual(response.status_code, 200)
        
        # Test pagination
        response = self.client.get('/api/admin/users/?page=1&page_size=2')
        self.assertEqual(response.status_code, 200)
    
    def test_user_update_via_api(self):
        """Test user update through API"""
        test_user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            role='viewer'
        )
        
        update_data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'is_verified': True
        }
        
        response = self.client.put(f'/api/admin/users/{test_user.id}/', update_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        test_user.refresh_from_db()
        self.assertEqual(test_user.email, 'updated@example.com')
        self.assertEqual(test_user.first_name, 'Updated')
        self.assertTrue(test_user.is_verified)
    
    def test_user_deletion_via_api(self):
        """Test user deletion through API"""
        test_user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            organization=self.organization,
            role='viewer'
        )
        
        response = self.client.delete(f'/api/admin/users/{test_user.id}/')
        self.assertEqual(response.status_code, 200)
        
        # Verify soft deletion
        test_user.refresh_from_db()
        self.assertFalse(test_user.is_active)


class OrganizationIntegrationTestCase(CrispTestCase):
    """Integration tests with organization model"""
    
    def setUp(self):
        super().setUp()
    
    def test_user_organization_relationship(self):
        """Test user-organization relationship"""
        user = CustomUser.objects.create_user(
            username='orguser',
            email='orguser@example.com',
            password='OrgUserPassword123!',
            organization=self.organization
        )
        
        self.assertEqual(user.organization, self.organization)
        self.assertEqual(str(user), f"orguser ({self.organization.name})")
    
    def test_organization_admin_permissions(self):
        """Test organization admin permissions"""
        admin = CustomUser.objects.create_user(
            username='orgadmin',
            email='orgadmin@example.com',
            password='OrgAdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin'
        )
        
        regular_user = CustomUser.objects.create_user(
            username='user',
            email='user@example.com',
            password='UserPassword123!',
            organization=self.organization,
            role='viewer'
        )
        
        # Admin should be able to manage users in their organization
        self.assertTrue(admin.is_organization_admin())
        
        # Users in same organization should be manageable by admin
        from ..permissions import IsSameUserOrAdmin
        permission = IsSameUserOrAdmin()
        
        mock_request = MagicMock()
        mock_request.user = admin
        
        self.assertTrue(permission.has_object_permission(mock_request, None, regular_user))


class STIXObjectIntegrationTestCase(CrispTestCase):
    """Integration tests with STIX objects"""
    
    def setUp(self):
        super().setUp()
        
        self.user = CustomUser.objects.create_user(
            username='stixuser',
            email='stixuser@example.com',
            password='StixUserPassword123!',
            organization=self.organization,
            role='publisher',
            is_publisher=True,
            is_verified=True
        )
        
        self.admin = CustomUser.objects.create_user(
            username='stixadmin',
            email='stixadmin@example.com',
            password='StixAdminPassword123!',
            organization=self.organization,
            role='BlueVisionAdmin',
            is_verified=True
        )
    
    def test_stix_object_permission_creation(self):
        """Test creating STIX object permissions"""
        stix_object_id = '123e4567-e89b-12d3-a456-426614174001'
        
        permission = STIXObjectPermission.objects.create(
            user=self.user,
            stix_object_id=stix_object_id,
            permission_level='read',
            granted_by=self.admin
        )
        
        self.assertEqual(permission.user, self.user)
        self.assertEqual(permission.stix_object_id, stix_object_id)
        self.assertEqual(permission.permission_level, 'read')
        self.assertEqual(permission.granted_by, self.admin)
        self.assertFalse(permission.is_expired)
    
    def test_stix_object_permission_checking(self):
        """Test STIX object permission checking"""
        stix_object_id = '123e4567-e89b-12d3-a456-426614174001'
        
        # Create permission
        STIXObjectPermission.objects.create(
            user=self.user,
            stix_object_id=stix_object_id,
            permission_level='write',
            granted_by=self.admin
        )
        
        # Mock STIX object
        stix_object = MagicMock()
        stix_object.id = stix_object_id
        
        # Test permission checking
        from ..permissions import check_stix_object_permission
        
        self.assertTrue(check_stix_object_permission(self.user, stix_object, 'read'))
        self.assertTrue(check_stix_object_permission(self.user, stix_object, 'write'))
        self.assertFalse(check_stix_object_permission(self.user, stix_object, 'admin'))
    
    def test_organization_based_stix_access(self):
        """Test organization-based STIX object access"""
        # Mock STIX object created by user in same organization
        stix_object = MagicMock()
        stix_object.id = '123e4567-e89b-12d3-a456-426614174001'
        stix_object.created_by = self.user
        stix_object.created_by.organization = self.organization
        
        # Test organization-based access
        from ..permissions import check_stix_object_permission
        
        # User should have read access to objects from their organization
        self.assertTrue(check_stix_object_permission(self.user, stix_object, 'read'))
        
        # Publisher should have write access to objects from their organization
        self.assertTrue(check_stix_object_permission(self.user, stix_object, 'write'))


class FeedPublishingIntegrationTestCase(CrispTestCase):
    """Integration tests with feed publishing"""
    
    def setUp(self):
        super().setUp()
        
        self.publisher = CustomUser.objects.create_user(
            username='publisher',
            email='publisher@example.com',
            password='PublisherPassword123!',
            organization=self.organization,
            role='publisher',
            is_publisher=True,
            is_verified=True
        )
        
        self.viewer = CustomUser.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='ViewerPassword123!',
            organization=self.organization,
            role='viewer',
            is_verified=True
        )
    
    def test_feed_publishing_permissions(self):
        """Test feed publishing permissions"""
        # Mock feed object
        feed = MagicMock()
        feed.organization = self.organization
        feed.created_by = self.publisher
        
        # Test publisher permissions
        from ..permissions import check_feed_publish_permission
        
        self.assertTrue(check_feed_publish_permission(self.publisher, feed))
        self.assertFalse(check_feed_publish_permission(self.viewer, feed))
    
    def test_publisher_user_methods(self):
        """Test publisher-specific user methods"""
        self.assertTrue(self.publisher.can_publish_feeds())
        self.assertFalse(self.viewer.can_publish_feeds())
        
        # Test role-based publishing
        self.assertEqual(self.publisher.role, 'publisher')
        self.assertTrue(self.publisher.is_publisher)


class AuthenticationEventIntegrationTestCase(TransactionTestCase):
    """Integration tests for authentication events and observers"""
    
    def setUp(self):
        super().setUp()
        # Create unique organization for this test  
        from .test_base import CrispTestMixin
        self.organization = CrispTestMixin.create_unique_organization("Event Test Org")
        
        self.user = CustomUser.objects.create_user(
            username='eventuser',
            email='eventuser@example.com',
            password='EventUserPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def test_authentication_logging(self):
        """Test authentication event logging"""
        # Log authentication event
        log_entry = AuthenticationLog.log_authentication_event(
            user=self.user,
            action='login_success',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            success=True
        )
        
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.user, self.user)
        self.assertEqual(log_entry.action, 'login_success')
        self.assertTrue(log_entry.success)
    
    def test_failed_login_tracking(self):
        """Test failed login attempt tracking"""
        initial_attempts = self.user.failed_login_attempts
        
        # Simulate failed login
        self.user.increment_failed_login()
        
        self.assertEqual(self.user.failed_login_attempts, initial_attempts + 1)
        
        # Test account lockout after threshold
        for _ in range(4):  # Total of 5 attempts
            self.user.increment_failed_login()
        
        self.assertTrue(self.user.is_account_locked)
    
    def test_observer_pattern_integration(self):
        """Test observer pattern integration with authentication events"""
        from ..observers.auth_observers import auth_event_subject
        
        # Mock observer
        mock_observer = MagicMock()
        auth_event_subject.attach(mock_observer)
        
        # Trigger event
        auth_event_subject.notify_observers(
            event_type='login_success',
            user=self.user,
            event_data={
                'ip_address': '127.0.0.1',
                'user_agent': 'Test Browser',
                'success': True
            }
        )
        
        # Verify observer was called
        mock_observer.notify.assert_called_once()
        
        # Clean up
        auth_event_subject.detach(mock_observer)


class MiddlewareIntegrationTestCase(CrispTestCase):
    """Integration tests for middleware stack"""
    
    def setUp(self):
        super().setUp()
        self.user = CustomUser.objects.create_user(
            username='middlewareuser',
            email='middlewareuser@example.com',
            password='MiddlewareUserPassword123!',
            organization=self.organization,
            is_verified=True
        )
    
    def test_middleware_stack_integration(self):
        """Test middleware stack working together"""
        from django.test import RequestFactory
        from ..middleware import (
            SecurityHeadersMiddleware, RateLimitMiddleware, 
            SecurityAuditMiddleware
        )
        
        factory = RequestFactory()
        request = factory.get('/api/test/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test Browser'
        
        # Test security headers middleware
        headers_middleware = SecurityHeadersMiddleware(lambda req: MagicMock())
        response = headers_middleware.process_response(request, MagicMock())
        
        # Test rate limiting middleware
        rate_limit_middleware = RateLimitMiddleware(lambda req: MagicMock())
        rate_limit_response = rate_limit_middleware.process_request(request)
        self.assertIsNone(rate_limit_response)  # Should not be rate limited
        
        # Test security audit middleware
        audit_middleware = SecurityAuditMiddleware(lambda req: MagicMock())
        audit_response = audit_middleware.process_request(request)
        self.assertIsNone(audit_response)  # Should pass through
    
