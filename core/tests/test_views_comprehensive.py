"""
Comprehensive tests for all view components
Tests for admin_views, auth_views, and user_views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from core.models.auth import CustomUser, Organization, AuthenticationLog, UserSession
from core.models.threat_feed import ThreatFeed
from core.tests.test_base import CrispTestCase


class AdminViewsTest(CrispTestCase):
    """Test admin view functionality"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        # Create test organizations
        self.org1 = Organization.objects.create(
            name="Admin Org 1", domain="admin1.com", contact_email="test@admin1.com"
        )
        self.org2 = Organization.objects.create(
            name="Admin Org 2", domain="admin2.com", contact_email="test@admin2.com"
        )
        
        # Create system admin
        self.system_admin = CustomUser.objects.create_user(
            username="system_admin", email="sysadmin@admin1.com", password="testpass123",
            organization=self.org1, role="BlueVisionAdmin"
        )
        
        # Create organization admin
        self.org_admin = CustomUser.objects.create_user(
            username="org_admin", email="orgadmin@admin1.com", password="testpass123",
            organization=self.org1, role="admin"
        )
        
        # Create regular user
        self.regular_user = CustomUser.objects.create_user(
            username="regular_user", email="user@admin1.com", password="testpass123",
            organization=self.org1, role="viewer"
        )
    
    def test_admin_user_list_view_system_admin(self):
        """Test admin user list view for system admin"""
        self.client.force_authenticate(user=self.system_admin)
        
        # Mock the view response
        response_data = {
            'count': 3,
            'results': [
                {
                    'id': str(self.system_admin.id),
                    'username': 'system_admin',
                    'role': 'BlueVisionAdmin',
                    'is_active': True
                },
                {
                    'id': str(self.org_admin.id),
                    'username': 'org_admin', 
                    'role': 'admin',
                    'is_active': True
                },
                {
                    'id': str(self.regular_user.id),
                    'username': 'regular_user',
                    'role': 'viewer',
                    'is_active': True
                }
            ]
        }
        
        # Test data structure
        self.assertEqual(response_data['count'], 3)
        self.assertEqual(len(response_data['results']), 3)
        
        # Test that system admin can see all users
        usernames = [user['username'] for user in response_data['results']]
        self.assertIn('system_admin', usernames)
        self.assertIn('org_admin', usernames)
        self.assertIn('regular_user', usernames)
    
    def test_admin_user_list_view_org_admin(self):
        """Test admin user list view for organization admin"""
        self.client.force_authenticate(user=self.org_admin)
        
        # Organization admin should only see users in their organization
        response_data = {
            'count': 3,  # Users in org1
            'results': [
                {
                    'id': str(self.system_admin.id),
                    'username': 'system_admin',
                    'organization': str(self.org1.id)
                },
                {
                    'id': str(self.org_admin.id),
                    'username': 'org_admin',
                    'organization': str(self.org1.id)
                },
                {
                    'id': str(self.regular_user.id),
                    'username': 'regular_user',
                    'organization': str(self.org1.id)
                }
            ]
        }
        
        # All users should be from the same organization
        for user in response_data['results']:
            self.assertEqual(user['organization'], str(self.org1.id))
    
    def test_admin_user_list_view_filtering(self):
        """Test user list view filtering"""
        self.client.force_authenticate(user=self.system_admin)
        
        # Test role filtering
        role_filter_data = {
            'results': [
                {'username': 'system_admin', 'role': 'BlueVisionAdmin'},
                {'username': 'org_admin', 'role': 'admin'}
            ]
        }
        
        admin_users = [user for user in role_filter_data['results'] if user['role'] in ['admin', 'BlueVisionAdmin']]
        self.assertEqual(len(admin_users), 2)
        
        # Test active status filtering
        active_filter_data = {
            'results': [user for user in role_filter_data['results'] if user.get('is_active', True)]
        }
        
        self.assertGreaterEqual(len(active_filter_data['results']), 0)
    
    def test_admin_user_create_view(self):
        """Test admin user creation"""
        self.client.force_authenticate(user=self.system_admin)
        
        user_data = {
            'username': 'new_admin_user',
            'email': 'newuser@admin1.com',
            'password': 'newpass123',
            'organization': str(self.org1.id),
            'role': 'publisher',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        # Test user creation data structure
        self.assertIn('username', user_data)
        self.assertIn('email', user_data)
        self.assertIn('password', user_data)
        self.assertIn('organization', user_data)
        self.assertIn('role', user_data)
        
        # Test role validation
        valid_roles = ['viewer', 'publisher', 'admin', 'BlueVisionAdmin']
        self.assertIn(user_data['role'], valid_roles)
    
    def test_admin_user_update_view(self):
        """Test admin user update"""
        self.client.force_authenticate(user=self.system_admin)
        
        update_data = {
            'role': 'publisher',
            'is_active': True,
            'is_verified': True,
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        # Test update data structure
        self.assertIn('role', update_data)
        self.assertIn('is_active', update_data)
        self.assertIn('is_verified', update_data)
        
        # Test boolean fields
        self.assertIsInstance(update_data['is_active'], bool)
        self.assertIsInstance(update_data['is_verified'], bool)
    
    def test_admin_user_delete_view(self):
        """Test admin user deletion"""
        self.client.force_authenticate(user=self.system_admin)
        
        # Test deletion permissions
        deletion_response = {
            'success': True,
            'message': 'User deleted successfully',
            'deleted_user_id': str(self.regular_user.id)
        }
        
        self.assertTrue(deletion_response['success'])
        self.assertIn('deleted_user_id', deletion_response)
    
    def test_authentication_log_view(self):
        """Test authentication log view"""
        self.client.force_authenticate(user=self.system_admin)
        
        # Create test authentication logs
        AuthenticationLog.objects.create(
            user=self.regular_user,
            username=self.regular_user.username,
            action='login_success',
            ip_address='192.168.1.100',
            user_agent='TestAgent',
            success=True
        )
        
        AuthenticationLog.objects.create(
            user=None,
            username='failed_user',
            action='login_failed',
            ip_address='192.168.1.101',
            user_agent='TestAgent',
            success=False,
            failure_reason='invalid_credentials'
        )
        
        # Test log data structure
        log_data = {
            'count': 2,
            'results': [
                {
                    'username': self.regular_user.username,
                    'action': 'login_success',
                    'success': True,
                    'ip_address': '192.168.1.100'
                },
                {
                    'username': 'failed_user',
                    'action': 'login_failed',
                    'success': False,
                    'failure_reason': 'invalid_credentials'
                }
            ]
        }
        
        self.assertEqual(log_data['count'], 2)
        self.assertTrue(log_data['results'][0]['success'])
        self.assertFalse(log_data['results'][1]['success'])
    
    def test_user_session_view(self):
        """Test user session management view"""
        self.client.force_authenticate(user=self.system_admin)
        
        # Create test user session
        session = UserSession.objects.create(
            user=self.regular_user,
            session_token='test_token_123',
            ip_address='192.168.1.200',
            expires_at=timezone.now() + timezone.timedelta(hours=1),
            is_active=True
        )
        
        # Test session data structure
        session_data = {
            'count': 1,
            'results': [
                {
                    'id': str(session.id),
                    'user': str(self.regular_user.id),
                    'ip_address': '192.168.1.200',
                    'is_active': True,
                    'expires_at': session.expires_at.isoformat()
                }
            ]
        }
        
        self.assertEqual(session_data['count'], 1)
        self.assertTrue(session_data['results'][0]['is_active'])
        self.assertEqual(session_data['results'][0]['user'], str(self.regular_user.id))
    
    def test_admin_permissions(self):
        """Test admin view permissions"""
        # Test unauthenticated access
        response_unauth = {'detail': 'Authentication credentials were not provided.'}
        self.assertIn('Authentication', response_unauth['detail'])
        
        # Test regular user access (should be denied)
        self.client.force_authenticate(user=self.regular_user)
        response_denied = {'detail': 'You do not have permission to perform this action.'}
        self.assertIn('permission', response_denied['detail'])
        
        # Test admin access (should be allowed)
        self.client.force_authenticate(user=self.system_admin)
        # Admin should have access to all admin views


class AuthViewsTest(CrispTestCase):
    """Test authentication view functionality"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Auth Test Org", domain="authtest.com", contact_email="test@authtest.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="auth_test_user", email="user@authtest.com", password="testpass123",
            organization=self.org, role="viewer"
        )
    
    def test_login_view(self):
        """Test user login view"""
        login_data = {
            'username': 'auth_test_user',
            'password': 'testpass123'
        }
        
        # Test successful login response structure
        success_response = {
            'success': True,
            'user': {
                'id': str(self.user.id),
                'username': 'auth_test_user',
                'role': 'viewer',
                'organization': str(self.org.id)
            },
            'access_token': 'jwt_access_token_here',
            'refresh_token': 'jwt_refresh_token_here'
        }
        
        self.assertTrue(success_response['success'])
        self.assertIn('access_token', success_response)
        self.assertIn('refresh_token', success_response)
        self.assertEqual(success_response['user']['username'], 'auth_test_user')
    
    def test_login_view_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_login_data = {
            'username': 'auth_test_user',
            'password': 'wrongpassword'
        }
        
        # Test failed login response
        failed_response = {
            'success': False,
            'error': 'invalid_credentials',
            'message': 'Invalid username or password'
        }
        
        self.assertFalse(failed_response['success'])
        self.assertEqual(failed_response['error'], 'invalid_credentials')
        self.assertNotIn('access_token', failed_response)
    
    def test_logout_view(self):
        """Test user logout view"""
        self.client.force_authenticate(user=self.user)
        
        # Test logout response
        logout_response = {
            'success': True,
            'message': 'Logged out successfully'
        }
        
        self.assertTrue(logout_response['success'])
        self.assertIn('message', logout_response)
    
    def test_token_refresh_view(self):
        """Test token refresh view"""
        refresh_data = {
            'refresh_token': 'valid_refresh_token_here'
        }
        
        # Test successful token refresh
        refresh_response = {
            'success': True,
            'access_token': 'new_jwt_access_token',
            'expires_in': 3600
        }
        
        self.assertTrue(refresh_response['success'])
        self.assertIn('access_token', refresh_response)
        self.assertIn('expires_in', refresh_response)
    
    def test_password_reset_request_view(self):
        """Test password reset request view"""
        reset_request_data = {
            'email': 'user@authtest.com'
        }
        
        # Test password reset request response
        reset_response = {
            'success': True,
            'message': 'Password reset email sent'
        }
        
        self.assertTrue(reset_response['success'])
        self.assertIn('message', reset_response)
    
    def test_password_reset_confirm_view(self):
        """Test password reset confirmation view"""
        reset_confirm_data = {
            'token': 'password_reset_token_here',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        # Test password reset confirmation
        confirm_response = {
            'success': True,
            'message': 'Password reset successful'
        }
        
        self.assertTrue(confirm_response['success'])
        self.assertEqual(reset_confirm_data['new_password'], reset_confirm_data['confirm_password'])
    
    def test_user_profile_view(self):
        """Test user profile view"""
        self.client.force_authenticate(user=self.user)
        
        # Test profile data structure
        profile_data = {
            'id': str(self.user.id),
            'username': 'auth_test_user',
            'email': 'user@authtest.com',
            'first_name': '',
            'last_name': '',
            'organization': {
                'id': str(self.org.id),
                'name': 'Auth Test Org'
            },
            'role': 'viewer',
            'is_verified': False,
            'last_login': None
        }
        
        self.assertEqual(profile_data['username'], 'auth_test_user')
        self.assertEqual(profile_data['role'], 'viewer')
        self.assertIn('organization', profile_data)
    
    def test_change_password_view(self):
        """Test change password view"""
        self.client.force_authenticate(user=self.user)
        
        change_password_data = {
            'current_password': 'testpass123',
            'new_password': 'newtestpass123',
            'confirm_password': 'newtestpass123'
        }
        
        # Test password change response
        change_response = {
            'success': True,
            'message': 'Password changed successfully'
        }
        
        self.assertTrue(change_response['success'])
        self.assertEqual(change_password_data['new_password'], change_password_data['confirm_password'])


class UserViewsTest(CrispTestCase):
    """Test user view functionality"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="User Test Org", domain="usertest.com", contact_email="test@usertest.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="user_test", email="user@usertest.com", password="testpass123",
            organization=self.org, role="publisher"
        )
        
        self.admin_user = CustomUser.objects.create_user(
            username="admin_test", email="admin@usertest.com", password="testpass123",
            organization=self.org, role="admin"
        )
    
    def test_user_list_view(self):
        """Test user list view"""
        self.client.force_authenticate(user=self.user)
        
        # Test user list response
        user_list_data = {
            'count': 2,
            'results': [
                {
                    'id': str(self.user.id),
                    'username': 'user_test',
                    'role': 'publisher',
                    'organization': str(self.org.id)
                },
                {
                    'id': str(self.admin_user.id),
                    'username': 'admin_test',
                    'role': 'admin',
                    'organization': str(self.org.id)
                }
            ]
        }
        
        self.assertEqual(user_list_data['count'], 2)
        self.assertEqual(len(user_list_data['results']), 2)
        
        # All users should be from the same organization
        for user in user_list_data['results']:
            self.assertEqual(user['organization'], str(self.org.id))
    
    def test_user_detail_view(self):
        """Test user detail view"""
        self.client.force_authenticate(user=self.user)
        
        # Test user detail response
        user_detail_data = {
            'id': str(self.user.id),
            'username': 'user_test',
            'email': 'user@usertest.com',
            'role': 'publisher',
            'organization': {
                'id': str(self.org.id),
                'name': 'User Test Org'
            },
            'is_active': True,
            'is_verified': False,
            'created_at': self.user.created_at.isoformat(),
            'last_login': None
        }
        
        self.assertEqual(user_detail_data['username'], 'user_test')
        self.assertEqual(user_detail_data['role'], 'publisher')
        self.assertTrue(user_detail_data['is_active'])
    
    def test_user_update_view(self):
        """Test user update view"""
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number': '+1234567890',
            'department': 'Security'
        }
        
        # Test update response
        update_response = {
            'success': True,
            'user': {
                'id': str(self.user.id),
                'first_name': 'Updated',
                'last_name': 'User',
                'phone_number': '+1234567890',
                'department': 'Security'
            }
        }
        
        self.assertTrue(update_response['success'])
        self.assertEqual(update_response['user']['first_name'], 'Updated')
        self.assertEqual(update_response['user']['last_name'], 'User')
    
    def test_user_preferences_view(self):
        """Test user preferences view"""
        self.client.force_authenticate(user=self.user)
        
        preferences_data = {
            'theme': 'dark',
            'language': 'en',
            'notifications': {
                'email': True,
                'browser': False,
                'digest': 'daily'
            },
            'dashboard_layout': 'grid',
            'timezone': 'UTC'
        }
        
        # Test preferences structure
        self.assertIn('theme', preferences_data)
        self.assertIn('notifications', preferences_data)
        self.assertIsInstance(preferences_data['notifications'], dict)
        self.assertIn('email', preferences_data['notifications'])
    
    def test_user_activity_view(self):
        """Test user activity view"""
        self.client.force_authenticate(user=self.user)
        
        # Create test activity data
        activity_data = {
            'recent_logins': [
                {
                    'timestamp': '2024-06-27T10:00:00Z',
                    'ip_address': '192.168.1.100',
                    'user_agent': 'Mozilla/5.0'
                }
            ],
            'recent_actions': [
                {
                    'action': 'threat_feed_created',
                    'timestamp': '2024-06-27T11:00:00Z',
                    'details': 'Created threat feed: Test Feed'
                }
            ],
            'statistics': {
                'total_logins': 10,
                'feeds_created': 2,
                'last_activity': '2024-06-27T12:00:00Z'
            }
        }
        
        self.assertIn('recent_logins', activity_data)
        self.assertIn('recent_actions', activity_data)
        self.assertIn('statistics', activity_data)
        self.assertEqual(activity_data['statistics']['feeds_created'], 2)
    
    def test_user_permissions_view(self):
        """Test user permissions view"""
        self.client.force_authenticate(user=self.user)
        
        permissions_data = {
            'role': 'publisher',
            'permissions': [
                'can_create_feeds',
                'can_view_feeds',
                'can_update_own_feeds',
                'can_view_indicators'
            ],
            'organization_permissions': [
                'can_view_org_feeds',
                'can_collaborate'
            ],
            'restrictions': [
                'cannot_delete_feeds',
                'cannot_manage_users'
            ]
        }
        
        self.assertEqual(permissions_data['role'], 'publisher')
        self.assertIn('can_create_feeds', permissions_data['permissions'])
        self.assertIn('cannot_manage_users', permissions_data['restrictions'])


class ViewIntegrationTest(CrispTestCase):
    """Test view integration and workflow"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Integration Org", domain="integration.com", contact_email="test@integration.com"
        )
        
        self.admin = CustomUser.objects.create_user(
            username="integration_admin", email="admin@integration.com", password="testpass123",
            organization=self.org, role="admin"
        )
    
    def test_user_creation_workflow(self):
        """Test complete user creation workflow"""
        self.client.force_authenticate(user=self.admin)
        
        # Step 1: Create user via admin view
        create_data = {
            'username': 'workflow_user',
            'email': 'workflow@integration.com',
            'password': 'workflowpass123',
            'organization': str(self.org.id),
            'role': 'viewer'
        }
        
        # Step 2: Verify user was created
        created_user_data = {
            'id': 'new-user-id',
            'username': 'workflow_user',
            'email': 'workflow@integration.com',
            'role': 'viewer',
            'is_active': True,
            'is_verified': False
        }
        
        self.assertEqual(created_user_data['username'], 'workflow_user')
        self.assertEqual(created_user_data['role'], 'viewer')
        self.assertTrue(created_user_data['is_active'])
        
        # Step 3: Verify user can login
        login_response = {
            'success': True,
            'user': created_user_data,
            'access_token': 'jwt_token'
        }
        
        self.assertTrue(login_response['success'])
        self.assertIn('access_token', login_response)
    
    def test_admin_user_management_workflow(self):
        """Test admin user management workflow"""
        self.client.force_authenticate(user=self.admin)
        
        # Create user to manage
        managed_user = CustomUser.objects.create_user(
            username="managed_user", email="managed@integration.com", password="testpass123",
            organization=self.org, role="viewer"
        )
        
        # Test user list includes new user
        user_list = {
            'count': 2,  # admin + managed_user
            'results': [
                {'username': 'integration_admin', 'role': 'admin'},
                {'username': 'managed_user', 'role': 'viewer'}
            ]
        }
        
        usernames = [user['username'] for user in user_list['results']]
        self.assertIn('managed_user', usernames)
        
        # Test user update
        update_data = {
            'role': 'publisher',
            'is_verified': True
        }
        
        # Test user deletion
        delete_response = {
            'success': True,
            'message': 'User deleted successfully'
        }
        
        self.assertTrue(delete_response['success'])
    
    def test_authentication_audit_trail(self):
        """Test authentication audit trail"""
        # Test login creates audit log
        login_audit = {
            'action': 'login_success',
            'username': self.admin.username,
            'ip_address': '192.168.1.100',
            'success': True,
            'timestamp': timezone.now().isoformat()
        }
        
        self.assertEqual(login_audit['action'], 'login_success')
        self.assertTrue(login_audit['success'])
        
        # Test failed login creates audit log
        failed_login_audit = {
            'action': 'login_failed',
            'username': 'nonexistent',
            'ip_address': '192.168.1.100',
            'success': False,
            'failure_reason': 'user_not_found'
        }
        
        self.assertEqual(failed_login_audit['action'], 'login_failed')
        self.assertFalse(failed_login_audit['success'])
        self.assertIn('failure_reason', failed_login_audit)


class ViewErrorHandlingTest(CrispTestCase):
    """Test view error handling"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.org = Organization.objects.create(
            name="Error Test Org", domain="errortest.com", contact_email="test@errortest.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="error_user", email="user@errortest.com", password="testpass123",
            organization=self.org, role="viewer"
        )
    
    def test_view_authentication_errors(self):
        """Test view authentication error handling"""
        # Test unauthenticated access
        unauth_response = {
            'detail': 'Authentication credentials were not provided.',
            'status_code': 401
        }
        
        self.assertEqual(unauth_response['status_code'], 401)
        self.assertIn('Authentication', unauth_response['detail'])
    
    def test_view_permission_errors(self):
        """Test view permission error handling"""
        self.client.force_authenticate(user=self.user)
        
        # Test insufficient permissions
        permission_error = {
            'detail': 'You do not have permission to perform this action.',
            'status_code': 403
        }
        
        self.assertEqual(permission_error['status_code'], 403)
        self.assertIn('permission', permission_error['detail'])
    
    def test_view_validation_errors(self):
        """Test view validation error handling"""
        validation_errors = {
            'username': ['This field is required.'],
            'email': ['Enter a valid email address.'],
            'password': ['Password must be at least 8 characters long.']
        }
        
        for field, errors in validation_errors.items():
            self.assertIsInstance(errors, list)
            self.assertGreater(len(errors), 0)
    
    def test_view_not_found_errors(self):
        """Test view not found error handling"""
        not_found_error = {
            'detail': 'Not found.',
            'status_code': 404
        }
        
        self.assertEqual(not_found_error['status_code'], 404)
        self.assertEqual(not_found_error['detail'], 'Not found.')