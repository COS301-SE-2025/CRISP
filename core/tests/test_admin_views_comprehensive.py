"""
Comprehensive tests for admin views to increase coverage
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from django.utils import timezone
from datetime import timedelta
from core.user_management.views.admin_views import AdminViewSet
from core.user_management.models import CustomUser, Organization, AuthenticationLog
from core.trust.models import TrustRelationship, TrustLevel, TrustGroup, TrustLog


class AdminViewsComprehensiveTest(APITestCase):
    """Comprehensive test suite for admin views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Admin Test Org',
            domain='admintest.com',
            contact_email='admin@admintest.com',
            is_active=True,
            is_verified=True
        )
        
        # Create test users
        self.admin_user = CustomUser.objects.create_user(
            username='admin@admintest.com',
            email='admin@admintest.com',
            password='TestPassword123',
            first_name='Admin',
            last_name='User',
            role='BlueVisionAdmin',
            organization=self.organization,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        
        self.regular_user = CustomUser.objects.create_user(
            username='user@admintest.com',
            email='user@admintest.com',
            password='TestPassword123',
            first_name='Regular',
            last_name='User',
            role='viewer',
            organization=self.organization,
            is_active=True,
            is_verified=True
        )
        
        self.locked_user = CustomUser.objects.create_user(
            username='locked@admintest.com',
            email='locked@admintest.com',
            password='TestPassword123',
            first_name='Locked',
            last_name='User',
            role='viewer',
            organization=self.organization,
            is_active=True,
            is_verified=True,
            account_locked_until=timezone.now() + timedelta(hours=1)
        )
        
        # Create trust level
        self.trust_level = TrustLevel.objects.create(
            name='High Trust',
            level='trusted',
            numerical_value=80,
            description='High level of trust',
            created_by='system'
        )
        
        # Create authentication log entries
        AuthenticationLog.objects.create(
            user=self.regular_user,
            action='login_success',
            ip_address='192.168.1.100',
            user_agent='Test Browser',
            success=True,
            timestamp=timezone.now() - timedelta(hours=1)
        )
        
        AuthenticationLog.objects.create(
            user=self.regular_user,
            action='login_failure',
            ip_address='192.168.1.100',
            user_agent='Test Browser',
            success=False,
            failure_reason='Invalid credentials',
            timestamp=timezone.now() - timedelta(hours=2)
        )
        
        # Authenticate admin user
        self.client.force_authenticate(user=self.admin_user)
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_dashboard_success(self, mock_access_control):
        """Test successful admin dashboard access"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.UserService') as mock_user_service:
            with patch('core.user_management.views.admin_views.OrganizationService') as mock_org_service:
                mock_user_service_instance = Mock()
                mock_user_service_instance.get_user_statistics.return_value = {'total_users': 3}
                mock_user_service.return_value = mock_user_service_instance
                
                mock_org_service_instance = Mock()
                mock_org_service_instance.get_organization_statistics.return_value = {'total_organizations': 1}
                mock_org_service.return_value = mock_org_service_instance
                
                response = self.client.get('/api/v1/admin/dashboard/')
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(response.data['success'])
                self.assertIn('data', response.data)
                
                dashboard_data = response.data['data']
                self.assertIn('user_statistics', dashboard_data)
                self.assertIn('organization_statistics', dashboard_data)
                self.assertIn('recent_activities', dashboard_data)
                self.assertIn('system_health', dashboard_data)
    
    def test_dashboard_permission_denied(self):
        """Test dashboard access without permission"""
        # Use regular user
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get('/api/v1/admin/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    @patch('core.user_management.views.admin_views.UserService')
    def test_dashboard_exception_handling(self, mock_user_service):
        """Test dashboard with exception handling"""
        mock_user_service.side_effect = Exception('Service error')
        
        response = self.client.get('/api/v1/admin/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Failed to load admin dashboard')
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_system_health_success(self, mock_access_control):
        """Test successful system health retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.OrganizationService') as mock_org_service:
            mock_org_service_instance = Mock()
            mock_org_service_instance.get_organization_statistics.return_value = {'total_organizations': 1}
            mock_org_service.return_value = mock_org_service_instance
            
            response = self.client.get('/api/v1/admin/system_health/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            
            health_data = response.data['data']
            self.assertIn('database', health_data)
            self.assertIn('authentication', health_data)
            self.assertIn('trust_system', health_data)
            
            self.assertEqual(health_data['database']['status'], 'healthy')
            self.assertIsInstance(health_data['database']['total_users'], int)
    
    def test_system_health_permission_denied(self):
        """Test system health access without permission"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get('/api/v1/admin/system_health/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_audit_logs_success(self, mock_access_control):
        """Test successful audit logs retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        response = self.client.get('/api/v1/admin/audit_logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertIn('logs', data)
        self.assertIn('total_returned', data)
        self.assertIn('filters_applied', data)
        
        self.assertEqual(len(data['logs']), 2)  # Two log entries from setUp
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_audit_logs_with_filters(self, mock_access_control):
        """Test audit logs with various filters"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        # Test action filter
        response = self.client.get('/api/v1/admin/audit_logs/?action=login_success')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(len(data['logs']), 1)
        self.assertEqual(data['logs'][0]['action'], 'login_success')
        
        # Test success filter
        response = self.client.get('/api/v1/admin/audit_logs/?success=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(len(data['logs']), 1)
        self.assertFalse(data['logs'][0]['success'])
        
        # Test user_id filter
        response = self.client.get(f'/api/v1/admin/audit_logs/?user_id={self.regular_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(len(data['logs']), 2)
        
        # Test limit filter
        response = self.client.get('/api/v1/admin/audit_logs/?limit=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(len(data['logs']), 1)
        
        # Test date filters
        start_date = (timezone.now() - timedelta(hours=3)).isoformat()
        end_date = timezone.now().isoformat()
        response = self.client.get(f'/api/v1/admin/audit_logs/?start_date={start_date}&end_date={end_date}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_audit_logs_permission_denied(self):
        """Test audit logs access without permission"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get('/api/v1/admin/audit_logs/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_unlock_account_success(self, mock_access_control):
        """Test successful account unlock"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch.object(self.locked_user, 'unlock_account') as mock_unlock:
            response = self.client.post(f'/api/v1/admin/{self.locked_user.id}/unlock_account/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('message', response.data['data'])
            self.assertIn(self.locked_user.username, response.data['data']['message'])
            
            mock_unlock.assert_called_once()
    
    def test_unlock_account_user_not_found(self):
        """Test account unlock with non-existent user"""
        response = self.client.post('/api/v1/admin/00000000-0000-0000-0000-000000000000/unlock_account/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'User not found')
    
    def test_unlock_account_permission_denied(self):
        """Test account unlock without permission"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.post(f'/api/v1/admin/{self.locked_user.id}/unlock_account/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_cleanup_expired_sessions_success(self, mock_access_control):
        """Test successful session cleanup"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.services.auth_service.AuthenticationService') as mock_auth_service:
            mock_auth_service_instance = Mock()
            mock_auth_service_instance.cleanup_expired_sessions.return_value = 5
            mock_auth_service.return_value = mock_auth_service_instance
            
            response = self.client.post('/api/v1/admin/cleanup_expired_sessions/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertEqual(response.data['data']['sessions_cleaned'], 5)
    
    def test_cleanup_expired_sessions_permission_denied(self):
        """Test session cleanup without permission"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.post('/api/v1/admin/cleanup_expired_sessions/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_trust_overview_success(self, mock_access_control):
        """Test successful trust overview retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        # Create trust data
        trust_group = TrustGroup.objects.create(
            name='Test Trust Group',
            description='Test group',
            default_trust_level=self.trust_level,
            group_type='community',
            is_public=True,
            created_by=str(self.admin_user),
            is_active=True
        )
        
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.organization,
            target_organization=self.organization,  # Self for testing
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            created_by=self.admin_user
        )
        
        trust_log = TrustLog.objects.create(
            user=self.admin_user,
            action='relationship_created',
            success=True,
            details={'test': 'data'}
        )
        
        response = self.client.get('/api/v1/admin/trust_overview/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        trust_stats = response.data['data']
        self.assertIn('relationships', trust_stats)
        self.assertIn('groups', trust_stats)
        self.assertIn('recent_activities', trust_stats)
        
        self.assertEqual(trust_stats['relationships']['total'], 1)
        self.assertEqual(trust_stats['groups']['total'], 1)
        self.assertEqual(len(trust_stats['recent_activities']), 1)
    
    def test_trust_overview_permission_denied(self):
        """Test trust overview access without permission"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get('/api/v1/admin/trust_overview/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_comprehensive_audit_logs_success(self, mock_access_control):
        """Test successful comprehensive audit logs retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.AuditService') as mock_audit_service:
            mock_audit_service_instance = Mock()
            mock_audit_service_instance.get_audit_logs.return_value = {
                'logs': [{'id': '1', 'action': 'test_action'}],
                'total_count': 1
            }
            mock_audit_service.return_value = mock_audit_service_instance
            
            response = self.client.get('/api/v1/admin/comprehensive_audit_logs/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('data', response.data)
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_comprehensive_audit_logs_with_filters(self, mock_access_control):
        """Test comprehensive audit logs with all filters"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.AuditService') as mock_audit_service:
            mock_audit_service_instance = Mock()
            mock_audit_service_instance.get_audit_logs.return_value = {'logs': [], 'total_count': 0}
            mock_audit_service.return_value = mock_audit_service_instance
            
            # Test with all possible query parameters
            query_params = {
                'action': 'test_action',
                'user_id': str(self.regular_user.id),
                'success': 'true',
                'start_date': (timezone.now() - timedelta(days=1)).isoformat(),
                'end_date': timezone.now().isoformat(),
                'limit': '50',
                'offset': '10',
                'include_trust_logs': 'true',
                'include_user_logs': 'false',
                'severity': 'high'
            }
            
            query_string = '&'.join([f'{k}={v}' for k, v in query_params.items()])
            response = self.client.get(f'/api/v1/admin/comprehensive_audit_logs/?{query_string}')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            
            # Verify the service was called with correct parameters
            call_args = mock_audit_service_instance.get_audit_logs.call_args
            self.assertIn('filters', call_args[1])
            self.assertIn('limit', call_args[1])
            self.assertIn('offset', call_args[1])
            self.assertIn('include_trust_logs', call_args[1])
            self.assertIn('include_user_logs', call_args[1])
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_user_activity_summary_success(self, mock_access_control):
        """Test successful user activity summary retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.AuditService') as mock_audit_service:
            mock_audit_service_instance = Mock()
            mock_audit_service_instance.get_user_activity_summary.return_value = {
                'total_actions': 10,
                'successful_actions': 8,
                'failed_actions': 2
            }
            mock_audit_service.return_value = mock_audit_service_instance
            
            response = self.client.get(f'/api/v1/admin/{self.regular_user.id}/user_activity_summary/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('data', response.data)
            
            activity_data = response.data['data']
            self.assertEqual(activity_data['total_actions'], 10)
    
    def test_user_activity_summary_user_not_found(self):
        """Test user activity summary with non-existent user"""
        response = self.client.get('/api/v1/admin/00000000-0000-0000-0000-000000000000/user_activity_summary/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'User not found')
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_user_activity_summary_with_days_filter(self, mock_access_control):
        """Test user activity summary with days parameter"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.AuditService') as mock_audit_service:
            mock_audit_service_instance = Mock()
            mock_audit_service_instance.get_user_activity_summary.return_value = {'total_actions': 5}
            mock_audit_service.return_value = mock_audit_service_instance
            
            response = self.client.get(f'/api/v1/admin/{self.regular_user.id}/user_activity_summary/?days=7')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            
            # Verify the service was called with correct days parameter
            call_args = mock_audit_service_instance.get_user_activity_summary.call_args
            self.assertEqual(call_args[1]['days'], 7)
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_security_events_success(self, mock_access_control):
        """Test successful security events retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.AuditService') as mock_audit_service:
            mock_audit_service_instance = Mock()
            mock_audit_service_instance.get_security_events.return_value = [
                {'id': '1', 'severity': 'high', 'event': 'failed_login'},
                {'id': '2', 'severity': 'medium', 'event': 'suspicious_activity'}
            ]
            mock_audit_service.return_value = mock_audit_service_instance
            
            response = self.client.get('/api/v1/admin/security_events/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            
            data = response.data['data']
            self.assertIn('events', data)
            self.assertIn('total_count', data)
            self.assertIn('severity_filter', data)
            self.assertIn('days_lookback', data)
            
            self.assertEqual(len(data['events']), 2)
            self.assertEqual(data['total_count'], 2)
            self.assertEqual(data['severity_filter'], 'all')
            self.assertEqual(data['days_lookback'], 7)
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_security_events_with_filters(self, mock_access_control):
        """Test security events with severity and days filters"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        with patch('core.user_management.views.admin_views.AuditService') as mock_audit_service:
            mock_audit_service_instance = Mock()
            mock_audit_service_instance.get_security_events.return_value = [
                {'id': '1', 'severity': 'high', 'event': 'failed_login'}
            ]
            mock_audit_service.return_value = mock_audit_service_instance
            
            response = self.client.get('/api/v1/admin/security_events/?severity=high&days=14')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            
            data = response.data['data']
            self.assertEqual(data['severity_filter'], 'high')
            self.assertEqual(data['days_lookback'], 14)
            
            # Verify service was called with correct parameters
            call_args = mock_audit_service_instance.get_security_events.call_args
            self.assertEqual(call_args[1]['severity'], 'high')
            self.assertEqual(call_args[1]['days'], 14)
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_audit_statistics_success(self, mock_access_control):
        """Test successful audit statistics retrieval"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        # Create additional trust log
        TrustLog.objects.create(
            user=self.admin_user,
            action='trust_established',
            success=True,
            details={'partner': 'test_org'}
        )
        
        response = self.client.get('/api/v1/admin/audit_statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        stats = response.data['data']
        self.assertIn('analysis_period_days', stats)
        self.assertIn('user_activity_breakdown', stats)
        self.assertIn('trust_activity_breakdown', stats)
        self.assertIn('failure_breakdown', stats)
        self.assertIn('top_active_users', stats)
        self.assertIn('total_user_logs', stats)
        self.assertIn('total_trust_logs', stats)
        self.assertIn('total_failed_attempts', stats)
        
        self.assertEqual(stats['analysis_period_days'], 30)
        self.assertIsInstance(stats['user_activity_breakdown'], list)
        self.assertIsInstance(stats['trust_activity_breakdown'], list)
        self.assertIsInstance(stats['top_active_users'], list)
    
    @patch('core.user_management.views.admin_views.AccessControlService')
    def test_audit_statistics_with_days_filter(self, mock_access_control):
        """Test audit statistics with custom days parameter"""
        mock_access_control_instance = Mock()
        mock_access_control_instance.has_permission.return_value = True
        mock_access_control.return_value = mock_access_control_instance
        
        response = self.client.get('/api/v1/admin/audit_statistics/?days=7')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        stats = response.data['data']
        self.assertEqual(stats['analysis_period_days'], 7)
    
    def test_audit_statistics_permission_denied(self):
        """Test audit statistics access without permission"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get('/api/v1/admin/audit_statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
    
    def test_get_active_sessions_count(self):
        """Test _get_active_sessions_count method"""
        viewset = AdminViewSet()
        
        with patch('core.user_management.models.UserSession.objects.filter') as mock_filter:
            mock_filter.return_value.count.return_value = 5
            count = viewset._get_active_sessions_count()
            self.assertEqual(count, 5)
    
    def test_get_failed_logins_count(self):
        """Test _get_failed_logins_count method"""
        viewset = AdminViewSet()
        count = viewset._get_failed_logins_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 1)  # We have one failed login from setUp
    
    def test_get_locked_accounts_count(self):
        """Test _get_locked_accounts_count method"""
        viewset = AdminViewSet()
        count = viewset._get_locked_accounts_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 1)  # We have one locked user from setUp
    
    def test_get_average_session_duration(self):
        """Test _get_average_session_duration method"""
        viewset = AdminViewSet()
        duration = viewset._get_average_session_duration()
        self.assertEqual(duration, 45)  # Placeholder implementation
    
    def test_get_total_trust_relationships(self):
        """Test _get_total_trust_relationships method"""
        viewset = AdminViewSet()
        count = viewset._get_total_trust_relationships()
        self.assertIsInstance(count, int)
    
    def test_get_active_trust_relationships(self):
        """Test _get_active_trust_relationships method"""
        viewset = AdminViewSet()
        count = viewset._get_active_trust_relationships()
        self.assertIsInstance(count, int)
    
    def test_get_pending_trust_approvals(self):
        """Test _get_pending_trust_approvals method"""
        viewset = AdminViewSet()
        count = viewset._get_pending_trust_approvals()
        self.assertIsInstance(count, int)
    
    def test_get_trust_methods_exception_handling(self):
        """Test trust-related methods handle exceptions gracefully"""
        viewset = AdminViewSet()
        
        with patch('core.trust.models.TrustRelationship.objects.count', side_effect=Exception('DB Error')):
            count = viewset._get_total_trust_relationships()
            self.assertEqual(count, 0)
        
        with patch('core.trust.models.TrustRelationship.objects.filter', side_effect=Exception('DB Error')):
            count = viewset._get_active_trust_relationships()
            self.assertEqual(count, 0)
            
            count = viewset._get_pending_trust_approvals()
            self.assertEqual(count, 0)
    
    def test_get_client_ip_with_forwarded_header(self):
        """Test _get_client_ip method with X-Forwarded-For header"""
        viewset = AdminViewSet()
        
        mock_request = Mock()
        mock_request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.1.100, 10.0.0.1',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        ip = viewset._get_client_ip(mock_request)
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_without_forwarded_header(self):
        """Test _get_client_ip method without X-Forwarded-For header"""
        viewset = AdminViewSet()
        
        mock_request = Mock()
        mock_request.META = {
            'REMOTE_ADDR': '192.168.1.200'
        }
        
        ip = viewset._get_client_ip(mock_request)
        self.assertEqual(ip, '192.168.1.200')
    
    def test_get_client_ip_fallback(self):
        """Test _get_client_ip method fallback to default"""
        viewset = AdminViewSet()
        
        mock_request = Mock()
        mock_request.META = {}
        
        ip = viewset._get_client_ip(mock_request)
        self.assertEqual(ip, '127.0.0.1')
    
    def test_check_admin_permission_success(self):
        """Test _check_admin_permission method with valid permission"""
        viewset = AdminViewSet()
        
        with patch.object(viewset.access_control, 'has_permission', return_value=True):
            # Should not raise exception
            viewset._check_admin_permission(self.admin_user, 'test_permission')
    
    def test_check_admin_permission_denied(self):
        """Test _check_admin_permission method without permission"""
        viewset = AdminViewSet()
        
        with patch.object(viewset.access_control, 'has_permission', return_value=False):
            with self.assertRaises(PermissionDenied) as context:
                viewset._check_admin_permission(self.regular_user, 'test_permission')
            
            self.assertIn('Admin permission required: test_permission', str(context.exception))
    
    def test_viewset_initialization(self):
        """Test AdminViewSet initialization"""
        viewset = AdminViewSet()
        
        # Verify all services are initialized
        self.assertIsNotNone(viewset.user_service)
        self.assertIsNotNone(viewset.org_service)
        self.assertIsNotNone(viewset.trust_service)
        self.assertIsNotNone(viewset.access_control)
        self.assertIsNotNone(viewset.audit_service)
    
    def test_unauthenticated_access(self):
        """Test that all endpoints require authentication"""
        self.client.force_authenticate(user=None)
        
        endpoints = [
            '/api/v1/admin/dashboard/',
            '/api/v1/admin/system_health/',
            '/api/v1/admin/audit_logs/',
            '/api/v1/admin/trust_overview/',
            '/api/v1/admin/comprehensive_audit_logs/',
            '/api/v1/admin/security_events/',
            '/api/v1/admin/audit_statistics/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)