"""
Tests for observer pattern implementation
"""
from django.test import TestCase
from unittest.mock import Mock, patch
import io
import sys

from ..models import CustomUser, Organization
from ..observers.auth_observers import (
    AuthenticationObserver, SecurityAuditObserver, AccountLockoutObserver, 
    NotificationObserver, auth_event_subject, ConsoleLoggingObserver,
    SecurityAlertObserver, NewLocationAlertObserver
)
from ..factories.user_factory import UserFactory


class AuthEventObserverTestCase(TestCase):
    """Test auth event observer base class"""
    
    def test_observer_interface(self):
        """Test observer interface implementation"""
        # Base observer should raise NotImplementedError
        with self.assertRaises(TypeError):
            # Can't instantiate abstract class
            observer = AuthenticationObserver()


class ConsoleLoggingObserverTestCase(TestCase):
    """Test console logging observer"""
    
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
        
        self.observer = ConsoleLoggingObserver()
    
    def test_login_success_logging(self):
        """Test logging of successful login"""
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('login_success', self.test_user, {
                'ip_address': '127.0.0.1',
                'user_agent': 'Test User Agent'
            })
            
            output = captured_output.getvalue()
            self.assertIn('✅ Login successful', output)
            self.assertIn('testuser', output)
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__
    
    def test_login_failed_logging(self):
        """Test logging of failed login"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('login_failed', self.test_user, {
                'ip_address': '127.0.0.1',
                'failure_reason': 'Invalid password'
            })
            
            output = captured_output.getvalue()
            self.assertIn('❌ Login failed', output)
            self.assertIn('testuser', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_password_changed_logging(self):
        """Test logging of password change"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('password_changed', self.test_user, {
                'ip_address': '127.0.0.1'
            })
            
            output = captured_output.getvalue()
            self.assertIn('🔑 Password changed', output)
            self.assertIn('testuser', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_unknown_event_logging(self):
        """Test logging of unknown events"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('unknown_event', self.test_user, {})
            
            output = captured_output.getvalue()
            self.assertIn('📝 Authentication event', output)
            self.assertIn('unknown_event', output)
        finally:
            sys.stdout = sys.__stdout__


class SecurityAlertObserverTestCase(TestCase):
    """Test security alert observer"""
    
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
        
        self.observer = SecurityAlertObserver()
    
    def test_account_locked_alert(self):
        """Test security alert for account lockout"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('account_locked', self.test_user, {
                'ip_address': '127.0.0.1',
                'failure_reason': 'Multiple failed login attempts'
            })
            
            output = captured_output.getvalue()
            self.assertIn('SECURITY ALERT', output)
            self.assertIn('Account locked', output)
            self.assertIn('testuser', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_password_reset_alert(self):
        """Test security alert for password reset"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('password_reset', self.test_user, {
                'ip_address': '192.168.1.100'
            })
            
            output = captured_output.getvalue()
            self.assertIn('SECURITY ALERT', output)
            self.assertIn('Password reset requested', output)
            self.assertIn('192.168.1.100', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_non_security_event_ignored(self):
        """Test that non-security events are ignored"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('login_success', self.test_user, {})
            
            output = captured_output.getvalue()
            # Should not generate security alert for normal login
            self.assertEqual(output.strip(), '')
        finally:
            sys.stdout = sys.__stdout__


class NewLocationAlertObserverTestCase(TestCase):
    """Test new location alert observer"""
    
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
        
        self.observer = NewLocationAlertObserver()
    
    def test_new_location_detection(self):
        """Test detection of login from new location"""
        # Set last known IP
        self.test_user.last_login_ip = '127.0.0.1'
        self.test_user.save()
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Login from different IP
            self.observer.notify('login_success', self.test_user, {
                'ip_address': '192.168.1.100'
            })
            
            output = captured_output.getvalue()
            self.assertIn('New location alert', output)
            self.assertIn('testuser', output)
            self.assertIn('192.168.1.100', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_same_location_no_alert(self):
        """Test that same location doesn't trigger alert"""
        # Set last known IP
        self.test_user.last_login_ip = '127.0.0.1'
        self.test_user.save()
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Login from same IP
            self.observer.notify('login_success', self.test_user, {
                'ip_address': '127.0.0.1'
            })
            
            output = captured_output.getvalue()
            # Should not generate new location alert
            self.assertEqual(output.strip(), '')
        finally:
            sys.stdout = sys.__stdout__
    
    def test_first_login_no_alert(self):
        """Test that first login doesn't trigger new location alert"""
        # User with no previous login IP
        self.test_user.last_login_ip = None
        self.test_user.save()
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.notify('login_success', self.test_user, {
                'ip_address': '127.0.0.1'
            })
            
            output = captured_output.getvalue()
            # Should not generate alert for first login
            self.assertEqual(output.strip(), '')
        finally:
            sys.stdout = sys.__stdout__


class AuthEventSubjectTestCase(TestCase):
    """Test auth event subject (observable)"""
    
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
    
    def test_observer_registration(self):
        """Test observer registration and deregistration"""
        mock_observer = Mock()
        
        # Register observer
        auth_event_subject.register_observer(mock_observer)
        self.assertIn(mock_observer, auth_event_subject._observers)
        
        # Unregister observer
        auth_event_subject.unregister_observer(mock_observer)
        self.assertNotIn(mock_observer, auth_event_subject._observers)
    
    def test_observer_notification(self):
        """Test that observers are notified of events"""
        mock_observer = Mock()
        auth_event_subject.register_observer(mock_observer)
        
        try:
            # Notify observers
            auth_event_subject.notify_observers('test_event', self.test_user, {'test': 'data'})
            
            # Check that observer was called
            mock_observer.notify.assert_called_once_with('test_event', self.test_user, {'test': 'data'})
        finally:
            auth_event_subject.unregister_observer(mock_observer)
    
    def test_multiple_observers_notification(self):
        """Test that multiple observers are notified"""
        mock_observer1 = Mock()
        mock_observer2 = Mock()
        
        auth_event_subject.register_observer(mock_observer1)
        auth_event_subject.register_observer(mock_observer2)
        
        try:
            # Notify observers
            auth_event_subject.notify_observers('test_event', self.test_user, {})
            
            # Check that both observers were called
            mock_observer1.notify.assert_called_once()
            mock_observer2.notify.assert_called_once()
        finally:
            auth_event_subject.unregister_observer(mock_observer1)
            auth_event_subject.unregister_observer(mock_observer2)
    
    def test_observer_exception_handling(self):
        """Test that exceptions in observers don't break notification"""
        mock_observer1 = Mock()
        mock_observer2 = Mock()
        
        # Make first observer raise exception
        mock_observer1.notify.side_effect = Exception("Test exception")
        
        auth_event_subject.register_observer(mock_observer1)
        auth_event_subject.register_observer(mock_observer2)
        
        try:
            # Notify observers - should not raise exception
            auth_event_subject.notify_observers('test_event', self.test_user, {})
            
            # Second observer should still be called despite first one failing
            mock_observer2.notify.assert_called_once()
        finally:
            auth_event_subject.unregister_observer(mock_observer1)
            auth_event_subject.unregister_observer(mock_observer2)


class ObserverIntegrationTestCase(TestCase):
    """Test observer integration with the system"""
    
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
    
    def test_observers_receive_auth_events(self):
        """Test that observers receive authentication events from the system"""
        # This would test the actual integration with auth service
        # For now, we'll test the manual notification
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Simulate a login event
            auth_event_subject.notify_observers('login_success', self.test_user, {
                'ip_address': '127.0.0.1',
                'user_agent': 'Test User Agent',
                'success': True
            })
            
            output = captured_output.getvalue()
            # Should see output from default observers
            self.assertIn('testuser', output)
        finally:
            sys.stdout = sys.__stdout__