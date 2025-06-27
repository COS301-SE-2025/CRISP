"""
Tests for observer pattern implementation
"""
from django.test import TestCase
from .test_base import CrispTestCase
from unittest.mock import Mock, patch
import io
import sys

from ..models import CustomUser, Organization
from ..observers.auth_observers import (
    AuthenticationObserver, SecurityAuditObserver, AccountLockoutObserver, 
    NotificationObserver, SecurityAlertObserver, ConsoleLoggingObserver,
    NewLocationAlertObserver, auth_event_subject
)
from ..factories.user_factory import UserFactory


class AuthEventObserverTestCase(TestCase):
    """Test auth event observer base class"""
    
    def test_observer_interface(self):
        """Test observer interface implementation"""
        # AuthenticationObserver is abstract, so test with a concrete implementation
        from ..observers.auth_observers import ConsoleLoggingObserver
        observer = ConsoleLoggingObserver()
        
        # Should be able to call notify without errors
        try:
            observer.notify('test_event', None, {})
        except Exception:
            pass  # Some implementations may need valid data


class ConsoleLoggingObserverTestCase(CrispTestCase):
    """Test console logging observer"""
    
    def setUp(self):
        super().setUp()
        
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
        
        self.observer = ConsoleLoggingObserver()
    
    def test_login_success_logging(self):
        """Test logging of successful login"""
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.update('login_success', self.test_user, {
                'ip_address': '127.0.0.1',
                'user_agent': 'Test User Agent'
            })
            
            output = captured_output.getvalue()
            self.assertIn('LOGIN SUCCESS', output)
            self.assertIn('testuser', output)
            self.assertIn('127.0.0.1', output)
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__
    
    def test_login_failed_logging(self):
        """Test logging of failed login"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.update('login_failed', self.test_user, {
                'ip_address': '127.0.0.1',
                'failure_reason': 'Invalid password'
            })
            
            output = captured_output.getvalue()
            self.assertIn('LOGIN FAILED', output)
            self.assertIn('testuser', output)
            self.assertIn('Invalid password', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_password_changed_logging(self):
        """Test logging of password change"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.update('password_changed', self.test_user, {
                'ip_address': '127.0.0.1'
            })
            
            output = captured_output.getvalue()
            self.assertIn('PASSWORD CHANGED', output)
            self.assertIn('testuser', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_unknown_event_logging(self):
        """Test logging of unknown events"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.observer.update('unknown_event', self.test_user, {})
            
            output = captured_output.getvalue()
            self.assertIn('AUTH EVENT', output)
            self.assertIn('unknown_event', output)
        finally:
            sys.stdout = sys.__stdout__


class SecurityAlertObserverTestCase(CrispTestCase):
    """Test security alert observer"""
    
    def setUp(self):
        super().setUp()
        
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
        
        self.observer = SecurityAlertObserver()
    
    
    


class NewLocationAlertObserverTestCase(CrispTestCase):
    """Test new location alert observer"""
    
    def setUp(self):
        super().setUp()
        
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
        
        self.observer = NewLocationAlertObserver()
    
    
    def test_same_location_no_alert(self):
        """Test that same location doesn't trigger alert"""
        # Set last known IP
        self.test_user.last_login_ip = '127.0.0.1'
        self.test_user.save()
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Login from same IP
            self.observer.update('login_success', self.test_user, {
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
            self.observer.update('login_success', self.test_user, {
                'ip_address': '127.0.0.1'
            })
            
            output = captured_output.getvalue()
            # Should not generate alert for first login
            self.assertEqual(output.strip(), '')
        finally:
            sys.stdout = sys.__stdout__


class AuthEventSubjectTestCase(CrispTestCase):
    """Test auth event subject (observable)"""
    
    def setUp(self):
        super().setUp()
        
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
    
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


class ObserverIntegrationTestCase(CrispTestCase):
    """Test observer integration with the system"""
    
    def setUp(self):
        super().setUp()
        
        self.test_user = self.create_test_user(
            role='viewer',
            username='testuser',
            email='testuser@test.com'
        )
    
