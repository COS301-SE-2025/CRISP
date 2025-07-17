"""
Comprehensive tests for audit service to increase coverage
"""

from django.test import TestCase
from unittest.mock import patch, Mock
from core.services.audit_service import AuditService
from core.user_management.models import CustomUser, Organization
from django.utils import timezone
from datetime import timedelta
import json


class AuditServiceComprehensiveTest(TestCase):
    """Comprehensive test suite for audit service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test organization
        self.organization = Organization.objects.create(
            name='Audit Test Org',
            domain='audittest.com',
            contact_email='admin@audittest.com',
            is_active=True,
            is_verified=True
        )
        
        # Create test users
        self.admin_user = CustomUser.objects.create_user(
            username='auditadmin@example.com',
            email='auditadmin@example.com',
            password='TestPassword123',
            first_name='Audit',
            last_name='Admin',
            role='BlueVisionAdmin',
            organization=self.organization,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        
        self.regular_user = CustomUser.objects.create_user(
            username='audituser@example.com',
            email='audituser@example.com',
            password='TestPassword123',
            first_name='Audit',
            last_name='User',
            role='viewer',
            organization=self.organization,
            is_active=True,
            is_verified=True
        )
        
        self.service = AuditService()
    
    def test_log_user_action_success(self):
        """Test successful user action logging"""
        action_details = {
            'target_resource': 'user_profile',
            'changes': {'email': 'new@example.com'},
            'metadata': {'source': 'web_interface'}
        }
        
        result = self.service.log_user_action(
            user=self.regular_user,
            action='profile_update',
            resource_type='user',
            resource_id=str(self.regular_user.id),
            details=action_details,
            ip_address='192.168.1.100'
        )
        
        self.assertTrue(result)
    
    def test_log_user_action_with_success_flag(self):
        """Test user action logging with success flag"""
        result = self.service.log_user_action(
            user=self.regular_user,
            action='login_attempt',
            resource_type='auth',
            resource_id='session_123',
            details={'method': '2FA'},
            ip_address='192.168.1.100',
            success=True
        )
        
        self.assertTrue(result)
    
    def test_log_user_action_failure(self):
        """Test user action logging for failure"""
        result = self.service.log_user_action(
            user=self.regular_user,
            action='unauthorized_access',
            resource_type='admin_panel',
            resource_id='dashboard',
            details={'reason': 'insufficient_permissions'},
            ip_address='192.168.1.100',
            success=False
        )
        
        self.assertTrue(result)
    
    def test_log_security_event_high_severity(self):
        """Test security event logging with high severity"""
        event_details = {
            'event_type': 'brute_force_attempt',
            'failed_attempts': 10,
            'time_window': '5_minutes',
            'blocked': True
        }
        
        result = self.service.log_security_event(
            event_type='authentication_anomaly',
            severity='high',
            details=event_details,
            user=self.regular_user,
            ip_address='192.168.1.100'
        )
        
        self.assertTrue(result)
    
    def test_log_security_event_medium_severity(self):
        """Test security event logging with medium severity"""
        event_details = {
            'event_type': 'suspicious_login_location',
            'location': 'Unknown Country',
            'previous_locations': ['USA', 'Canada']
        }
        
        result = self.service.log_security_event(
            event_type='location_anomaly',
            severity='medium',
            details=event_details,
            user=self.regular_user,
            ip_address='192.168.1.100'
        )
        
        self.assertTrue(result)
    
    def test_log_security_event_without_user(self):
        """Test security event logging without associated user"""
        event_details = {
            'event_type': 'port_scan',
            'source_ip': '192.168.1.100',
            'target_ports': [22, 80, 443, 3389]
        }
        
        result = self.service.log_security_event(
            event_type='network_scan',
            severity='medium',
            details=event_details,
            ip_address='192.168.1.100'
        )
        
        self.assertTrue(result)
    
    def test_log_system_event_startup(self):
        """Test system event logging for startup"""
        event_details = {
            'version': '1.0.0',
            'environment': 'production',
            'startup_time': '2.5s'
        }
        
        result = self.service.log_system_event(
            event_type='system_startup',
            details=event_details,
            severity='info'
        )
        
        self.assertTrue(result)
    
    def test_log_system_event_error(self):
        """Test system event logging for errors"""
        event_details = {
            'error_type': 'database_connection_failed',
            'error_message': 'Connection timeout after 30s',
            'component': 'postgresql_adapter'
        }
        
        result = self.service.log_system_event(
            event_type='system_error',
            details=event_details,
            severity='high'
        )
        
        self.assertTrue(result)
    
    def test_get_user_activity_recent(self):
        """Test retrieving recent user activity"""
        # First log some activities
        self.service.log_user_action(
            user=self.regular_user,
            action='profile_view',
            resource_type='user',
            resource_id=str(self.regular_user.id),
            details={},
            ip_address='192.168.1.100'
        )
        
        activities = self.service.get_user_activity(
            user_id=str(self.regular_user.id),
            days=7
        )
        
        self.assertIsInstance(activities, list)
    
    def test_get_user_activity_with_limit(self):
        """Test retrieving user activity with limit"""
        # Log multiple activities
        for i in range(5):
            self.service.log_user_action(
                user=self.regular_user,
                action=f'test_action_{i}',
                resource_type='test',
                resource_id=f'resource_{i}',
                details={'iteration': i},
                ip_address='192.168.1.100'
            )
        
        activities = self.service.get_user_activity(
            user_id=str(self.regular_user.id),
            days=7,
            limit=3
        )
        
        self.assertIsInstance(activities, list)
        self.assertLessEqual(len(activities), 3)
    
    def test_get_security_events_recent(self):
        """Test retrieving recent security events"""
        # First log some security events
        self.service.log_security_event(
            event_type='failed_login',
            severity='medium',
            details={'attempts': 3},
            user=self.regular_user,
            ip_address='192.168.1.100'
        )
        
        events = self.service.get_security_events(hours=24)
        
        self.assertIsInstance(events, list)
    
    def test_get_security_events_high_severity_only(self):
        """Test retrieving only high severity security events"""
        # Log events with different severities
        self.service.log_security_event(
            event_type='brute_force',
            severity='high',
            details={'blocked': True},
            ip_address='192.168.1.100'
        )
        
        self.service.log_security_event(
            event_type='info_event',
            severity='low',
            details={'info': 'test'},
            ip_address='192.168.1.100'
        )
        
        events = self.service.get_security_events(
            hours=24,
            severity_filter='high'
        )
        
        self.assertIsInstance(events, list)
    
    def test_get_system_events_recent(self):
        """Test retrieving recent system events"""
        # First log some system events
        self.service.log_system_event(
            event_type='database_maintenance',
            details={'duration': '30min', 'tables_optimized': 15},
            severity='info'
        )
        
        events = self.service.get_system_events(hours=24)
        
        self.assertIsInstance(events, list)
    
    def test_get_audit_statistics_basic(self):
        """Test retrieving basic audit statistics"""
        # Log some test data
        self.service.log_user_action(
            user=self.regular_user,
            action='test_action',
            resource_type='test',
            resource_id='test_resource',
            details={},
            ip_address='192.168.1.100'
        )
        
        stats = self.service.get_audit_statistics(days=7)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_events', stats)
        self.assertIn('user_actions', stats)
        self.assertIn('security_events', stats)
        self.assertIn('system_events', stats)
    
    def test_get_audit_statistics_by_user(self):
        """Test retrieving audit statistics by user"""
        # Log some test data
        self.service.log_user_action(
            user=self.regular_user,
            action='test_action',
            resource_type='test',
            resource_id='test_resource',
            details={},
            ip_address='192.168.1.100'
        )
        
        stats = self.service.get_audit_statistics(
            days=7,
            user_id=str(self.regular_user.id)
        )
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_events', stats)
    
    def test_search_audit_logs_by_action(self):
        """Test searching audit logs by action"""
        # Log some test data
        self.service.log_user_action(
            user=self.regular_user,
            action='profile_update',
            resource_type='user',
            resource_id=str(self.regular_user.id),
            details={'field': 'email'},
            ip_address='192.168.1.100'
        )
        
        results = self.service.search_audit_logs(
            query='profile_update',
            days=7
        )
        
        self.assertIsInstance(results, list)
    
    def test_search_audit_logs_by_ip(self):
        """Test searching audit logs by IP address"""
        # Log some test data
        self.service.log_user_action(
            user=self.regular_user,
            action='test_action',
            resource_type='test',
            resource_id='test_resource',
            details={},
            ip_address='192.168.1.100'
        )
        
        results = self.service.search_audit_logs(
            query='192.168.1.100',
            days=7
        )
        
        self.assertIsInstance(results, list)
    
    def test_search_audit_logs_with_filters(self):
        """Test searching audit logs with multiple filters"""
        # Log some test data
        self.service.log_user_action(
            user=self.regular_user,
            action='test_action',
            resource_type='user',
            resource_id=str(self.regular_user.id),
            details={},
            ip_address='192.168.1.100'
        )
        
        results = self.service.search_audit_logs(
            query='test',
            days=7,
            user_id=str(self.regular_user.id),
            event_type='user_action'
        )
        
        self.assertIsInstance(results, list)
    
    def test_cleanup_old_logs_dry_run(self):
        """Test cleanup old logs in dry run mode"""
        result = self.service.cleanup_old_logs(
            older_than_days=90,
            dry_run=True
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('would_delete', result)
        self.assertIn('dry_run', result)
        self.assertTrue(result['dry_run'])
    
    def test_cleanup_old_logs_actual(self):
        """Test actual cleanup of old logs"""
        # This test would be more meaningful with old data, but tests the method
        result = self.service.cleanup_old_logs(
            older_than_days=1,  # Very short period for testing
            dry_run=False
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('deleted_count', result)
        self.assertFalse(result.get('dry_run', True))
    
    def test_export_audit_logs_json(self):
        """Test exporting audit logs in JSON format"""
        # Log some test data
        self.service.log_user_action(
            user=self.regular_user,
            action='test_export',
            resource_type='test',
            resource_id='test_resource',
            details={'test': 'data'},
            ip_address='192.168.1.100'
        )
        
        export_data = self.service.export_audit_logs(
            days=7,
            format='json'
        )
        
        self.assertIsInstance(export_data, (str, dict))
    
    def test_export_audit_logs_csv(self):
        """Test exporting audit logs in CSV format"""
        # Log some test data
        self.service.log_user_action(
            user=self.regular_user,
            action='test_export_csv',
            resource_type='test',
            resource_id='test_resource',
            details={},
            ip_address='192.168.1.100'
        )
        
        export_data = self.service.export_audit_logs(
            days=7,
            format='csv'
        )
        
        self.assertIsInstance(export_data, str)
    
    def test_validate_log_data_valid(self):
        """Test log data validation with valid data"""
        log_data = {
            'action': 'test_action',
            'resource_type': 'test',
            'resource_id': 'test_resource',
            'ip_address': '192.168.1.100'
        }
        
        is_valid = self.service._validate_log_data(log_data)
        self.assertTrue(is_valid)
    
    def test_validate_log_data_invalid(self):
        """Test log data validation with invalid data"""
        log_data = {
            'action': '',  # Empty action
            'resource_type': 'test',
            # Missing resource_id
            'ip_address': 'invalid_ip'  # Invalid IP
        }
        
        is_valid = self.service._validate_log_data(log_data)
        self.assertFalse(is_valid)
    
    def test_sanitize_details_basic(self):
        """Test details sanitization"""
        details = {
            'password': 'secret123',
            'token': 'abc123def456',
            'safe_data': 'this is safe',
            'email': 'user@example.com'
        }
        
        sanitized = self.service._sanitize_details(details)
        
        self.assertIn('safe_data', sanitized)
        self.assertEqual(sanitized['safe_data'], 'this is safe')
        self.assertNotEqual(sanitized.get('password'), 'secret123')
        self.assertNotEqual(sanitized.get('token'), 'abc123def456')
    
    def test_sanitize_details_nested(self):
        """Test details sanitization with nested data"""
        details = {
            'user_data': {
                'username': 'testuser',
                'password': 'secret123',
                'profile': {
                    'email': 'user@example.com',
                    'api_key': 'secret_key_123'
                }
            },
            'session_token': 'session_abc123'
        }
        
        sanitized = self.service._sanitize_details(details)
        
        self.assertIn('user_data', sanitized)
        self.assertIn('username', sanitized['user_data'])
        self.assertNotEqual(
            sanitized['user_data'].get('password'),
            'secret123'
        )
    
    def test_format_log_entry_basic(self):
        """Test basic log entry formatting"""
        from datetime import datetime
        
        # Mock log entry (simulating database object)
        mock_log = Mock()
        mock_log.timestamp = timezone.now()
        mock_log.user_id = str(self.regular_user.id)
        mock_log.action = 'test_action'
        mock_log.resource_type = 'test'
        mock_log.resource_id = 'test_resource'
        mock_log.success = True
        mock_log.ip_address = '192.168.1.100'
        mock_log.details = {'test': 'data'}
        
        formatted = self.service._format_log_entry(mock_log)
        
        self.assertIsInstance(formatted, dict)
        self.assertIn('timestamp', formatted)
        self.assertIn('action', formatted)
        self.assertIn('success', formatted)
    
    def test_get_log_level_for_severity(self):
        """Test log level determination for different severities"""
        self.assertEqual(
            self.service._get_log_level_for_severity('low'),
            'INFO'
        )
        self.assertEqual(
            self.service._get_log_level_for_severity('medium'),
            'WARNING'
        )
        self.assertEqual(
            self.service._get_log_level_for_severity('high'),
            'ERROR'
        )
        self.assertEqual(
            self.service._get_log_level_for_severity('critical'),
            'CRITICAL'
        )
    
    def test_exception_handling(self):
        """Test service exception handling"""
        # Test with invalid user (should handle gracefully)
        result = self.service.log_user_action(
            user=None,
            action='test_action',
            resource_type='test',
            resource_id='test_resource',
            details={},
            ip_address='192.168.1.100'
        )
        
        # Should handle None user gracefully
        self.assertIsInstance(result, bool)
    
    def test_logging_integration(self):
        """Test integration with Python logging"""
        with patch.object(self.service, 'logger') as mock_logger:
            self.service.log_security_event(
                event_type='test_event',
                severity='high',
                details={'test': 'data'},
                ip_address='192.168.1.100'
            )
            
            # Verify that the logger was called
            mock_logger.error.assert_called()
    
    def test_performance_with_large_details(self):
        """Test performance with large details object"""
        large_details = {
            f'key_{i}': f'value_{i}' * 100
            for i in range(100)
        }
        
        result = self.service.log_user_action(
            user=self.regular_user,
            action='performance_test',
            resource_type='test',
            resource_id='test_resource',
            details=large_details,
            ip_address='192.168.1.100'
        )
        
        self.assertTrue(result)
    
    def test_concurrent_logging(self):
        """Test concurrent logging operations"""
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def log_action(action_id):
            return self.service.log_user_action(
                user=self.regular_user,
                action=f'concurrent_test_{action_id}',
                resource_type='test',
                resource_id=f'resource_{action_id}',
                details={'thread_id': action_id},
                ip_address='192.168.1.100'
            )
        
        # Use ThreadPoolExecutor for better thread management
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            futures = [executor.submit(log_action, i) for i in range(5)]
            
            # Collect results
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.fail(f"Concurrent logging failed: {e}")
        
        # Verify all operations succeeded
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))