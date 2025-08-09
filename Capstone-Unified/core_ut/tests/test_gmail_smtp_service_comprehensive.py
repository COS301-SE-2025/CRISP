"""
Comprehensive unit tests for Gmail SMTP email service functionality
Covers all email methods including new authentication and invitation emails
"""
import unittest
from unittest.mock import patch, MagicMock, call
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.test import TestCase, override_settings
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from core_ut.notifications.services.gmail_smtp_service import GmailSMTPService
from core_ut.user_management.models.user_models import CustomUser, Organization
from core_ut.alerts.models import EmailLog
from core_ut.tests.factories import CustomUserFactory, OrganizationFactory


class GmailSMTPServiceComprehensiveTestCase(TestCase):
    """Comprehensive test cases for the GmailSMTPService"""

    def setUp(self):
        """Set up the test environment"""
        self.service = GmailSMTPService()
        self.organization = OrganizationFactory()
        self.user = CustomUserFactory(organization=self.organization)
        self.test_email = "test@example.com"
        self.test_subject = "Test Subject"
        self.test_html_content = "<h1>Test HTML Content</h1>"
        self.test_text_content = "Test text content"

    @patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL')
    @patch('core.alerts.models.EmailLog.objects.create')
    def test_send_email_success(self, mock_email_log, mock_smtp_ssl):
        """Test successful email sending with logging"""
        # Setup mocks
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server
        mock_email_log.return_value = MagicMock(id=1)
        
        # Call send_email
        result = self.service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content=self.test_html_content,
            text_content=self.test_text_content,
            email_type='test_email',
            user=self.user
        )
        
        # Verify SMTP interactions
        mock_smtp_ssl.assert_called_once()
        mock_server.login.assert_called_once_with(
            self.service.email_host_user, 
            self.service.email_host_password
        )
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
        # Verify email logging
        mock_email_log.assert_called()
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('sent successfully', result['message'])

    @patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL')
    def test_send_email_authentication_failure(self, mock_smtp_ssl):
        """Test email sending with authentication failure"""
        # Setup mock to raise authentication error
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, 'Authentication failed')
        mock_smtp_ssl.return_value = mock_server
        
        # Call send_email
        result = self.service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content=self.test_html_content
        )
        
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertIn('Authentication failed', result['message'])
        self.assertEqual(result['error_type'], 'authentication')

    @patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL')
    def test_send_email_connection_failure(self, mock_smtp_ssl):
        """Test email sending with connection failure"""
        # Setup mock to raise connection error
        mock_smtp_ssl.side_effect = smtplib.SMTPConnectError(421, 'Service not available')
        
        # Call send_email
        result = self.service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content=self.test_html_content
        )
        
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertTrue('connection failed' in result['message'].lower())
        self.assertEqual(result['error_type'], 'connection')

    def test_send_email_invalid_recipients(self):
        """Test email sending with invalid recipients"""
        result = self.service.send_email(
            to_emails=[],
            subject=self.test_subject,
            html_content=self.test_html_content
        )
        
        # Service validates empty recipients upfront
        self.assertFalse(result['success']) 
        self.assertIn('No recipients provided', result['message'])

    def test_send_email_missing_content(self):
        """Test email sending with missing content"""
        result = self.service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content="",
            text_content=""
        )
        
        # Service validates content upfront
        self.assertFalse(result['success'])
        self.assertIn('No content provided', result['message'])

    @patch('core.notifications.services.gmail_smtp_service.GmailSMTPService.send_email')
    def test_send_password_reset_email_success(self, mock_send_email):
        """Test successful password reset email sending"""
        mock_send_email.return_value = {'success': True, 'message': 'Email sent'}
        reset_token = 'test_reset_token_123'
        
        result = self.service.send_password_reset_email(self.user, reset_token)
        
        # Verify send_email was called with correct parameters
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        
        self.assertEqual(call_args[1]['to_emails'], [self.user.email])
        self.assertEqual(call_args[1]['subject'], 'CRISP - Password Reset Request')
        self.assertEqual(call_args[1]['email_type'], 'password_reset')
        self.assertEqual(call_args[1]['user'], self.user)
        self.assertIn(reset_token, call_args[1]['html_content'])
        self.assertIn(self.user.username, call_args[1]['html_content'])
        
        self.assertTrue(result['success'])

    @patch('core.notifications.services.gmail_smtp_service.GmailSMTPService.send_email')
    def test_send_password_reset_email_with_custom_frontend_url(self, mock_send_email):
        """Test password reset email with custom frontend URL"""
        mock_send_email.return_value = {'success': True, 'message': 'Email sent'}
        reset_token = 'test_reset_token_123'
        
        with override_settings(FRONTEND_URL='https://custom.example.com'):
            result = self.service.send_password_reset_email(self.user, reset_token)
        
        call_args = mock_send_email.call_args
        self.assertIn('https://custom.example.com/reset-password/', call_args[1]['html_content'])

    @patch('core.notifications.services.gmail_smtp_service.GmailSMTPService.send_email')
    def test_send_user_invitation_email_success(self, mock_send_email):
        """Test successful user invitation email sending"""
        mock_send_email.return_value = {'success': True, 'message': 'Email sent'}
        inviter = CustomUserFactory(role='publisher', organization=self.organization)
        invitation_token = 'test_invitation_token_123'
        invitee_email = 'newuser@example.com'
        
        result = self.service.send_user_invitation_email(
            email=invitee_email,
            organization=self.organization,
            inviter=inviter,
            invitation_token=invitation_token
        )
        
        # Verify send_email was called with correct parameters
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        
        self.assertEqual(call_args[1]['to_emails'], [invitee_email])
        self.assertEqual(call_args[1]['subject'], f'Invitation to join {self.organization.name} on CRISP')
        self.assertEqual(call_args[1]['email_type'], 'user_invitation')
        self.assertIn(invitation_token, call_args[1]['html_content'])
        self.assertIn(inviter.get_full_name() or inviter.username, call_args[1]['html_content'])
        self.assertIn(self.organization.name, call_args[1]['html_content'])
        
        self.assertTrue(result['success'])

    @patch('core.notifications.services.gmail_smtp_service.GmailSMTPService.send_email')
    def test_send_account_locked_email_success(self, mock_send_email):
        """Test successful account locked email sending"""
        mock_send_email.return_value = {'success': True, 'message': 'Email sent'}
        
        result = self.service.send_account_locked_email(self.user)
        
        # Verify send_email was called with correct parameters
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        
        self.assertEqual(call_args[1]['to_emails'], [self.user.email])
        self.assertEqual(call_args[1]['subject'], 'CRISP - Account Temporarily Locked')
        self.assertEqual(call_args[1]['email_type'], 'security_alert')
        self.assertEqual(call_args[1]['user'], self.user)
        self.assertIn('30 minutes', call_args[1]['html_content'])
        self.assertIn(self.user.username, call_args[1]['html_content'])
        
        self.assertTrue(result['success'])

    @patch('core.notifications.services.gmail_smtp_service.GmailSMTPService.send_email')
    def test_send_feed_subscription_confirmation_success(self, mock_send_email):
        """Test successful feed subscription confirmation email sending"""
        mock_send_email.return_value = {'success': True, 'message': 'Email sent'}
        feed_name = 'Critical Threat Intelligence Feed'
        
        result = self.service.send_feed_subscription_confirmation(self.user, feed_name)
        
        # Verify send_email was called with correct parameters
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        
        self.assertEqual(call_args[1]['to_emails'], [self.user.email])
        self.assertEqual(call_args[1]['subject'], f'CRISP - Subscription Confirmed: {feed_name}')
        self.assertEqual(call_args[1]['email_type'], 'feed_subscription_confirmation')
        self.assertEqual(call_args[1]['user'], self.user)
        self.assertIn(feed_name, call_args[1]['html_content'])
        self.assertIn(self.user.username, call_args[1]['html_content'])
        
        self.assertTrue(result['success'])

    @patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL')
    def test_send_threat_alert_email_success(self, mock_smtp_ssl):
        """Test successful threat alert email sending"""
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server
    
        alert_data = {
        'alert_type': 'High Severity Indicators',
        'feed_name': 'Test Feed',
        'indicator_type': 'IP Address',
        'indicator_value': '192.168.1.100',
        'severity': 'high',
        'confidence': 'medium',
        'details': 'Test threat indicator'
        }
    
        result = self.service.send_threat_alert_email(
        recipient_emails=[self.test_email],
        alert_data=alert_data,
        user=self.user
        )
    
        # Verify SMTP interactions
        mock_smtp_ssl.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
        self.assertTrue(result['success'])

    @patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL')
    def test_send_feed_notification_email_success(self, mock_smtp_ssl):
        """Test successful feed notification email sending"""
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server
    
        notification_data = {
        'feed_name': 'Test Feed',
        'feed_id': 'test-feed-123',
        'update_type': 'New Indicators',
        'indicator_count': 5,
        'details': 'New threat indicators added'
        }
    
        result = self.service.send_feed_notification_email(
        recipient_emails=[self.test_email],
        notification_data=notification_data,
        user=self.user
        )
    
        # Verify SMTP interactions
        mock_smtp_ssl.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
        self.assertTrue(result['success'])

    @patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL')
    def test_test_connection_success(self, mock_smtp_ssl):
        """Test successful SMTP connection testing"""
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server
    
        result = self.service.test_connection()
    
        # Verify SMTP interactions (service adds context and timeout parameters)
        mock_smtp_ssl.assert_called_once_with(self.service.email_host, self.service.email_port, context=unittest.mock.ANY, timeout=30)
        mock_server.login.assert_called_once_with(
        self.service.email_host_user,
        self.service.email_host_password
        )
        mock_server.quit.assert_called_once()
    
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'online')

    @patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL')
    def test_test_connection_auth_failure(self, mock_smtp_ssl):
        """Test SMTP connection testing with authentication failure"""
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, 'Authentication failed')
        mock_smtp_ssl.return_value = mock_server
    
        result = self.service.test_connection()
    
        self.assertFalse(result['success'])
        self.assertEqual(result['status'], 'error')
        self.assertTrue('authentication failed' in result['message'].lower())

    def test_email_template_contains_required_elements(self):
        """Test that email templates contain required elements"""
        reset_token = 'test_token'
        
        with patch.object(self.service, 'send_email', return_value={'success': True}) as mock_send:
            self.service.send_password_reset_email(self.user, reset_token)
            
            call_args = mock_send.call_args
            html_content = call_args[1]['html_content']
            
            # Check for required elements
            self.assertIn('CRISP', html_content)
            self.assertIn('Password Reset', html_content)
            self.assertIn(reset_token, html_content)
            self.assertIn('24 hours', html_content)
            self.assertIn('Reset Password', html_content)

    def test_email_template_mobile_responsive(self):
        """Test that email templates are mobile responsive"""
        with patch.object(self.service, 'send_email', return_value={'success': True}) as mock_send:
            self.service.send_password_reset_email(self.user, 'test_token')
            
            call_args = mock_send.call_args
            html_content = call_args[1]['html_content']
            
            # Check for responsive design elements
            self.assertIn('max-width: 600px', html_content)
            self.assertIn('margin: 0 auto', html_content)
            self.assertIn('font-family: Arial', html_content)

    def test_email_priority_styling(self):
        """Test that threat alert emails have priority-based styling"""
        alert_data = {
            'alert_type': 'Critical TTPs',
            'severity': 'critical',
            'priority': 'critical'
        }
        
        with patch.object(self.service, 'send_email', return_value={'success': True}) as mock_send:
            self.service.send_threat_alert_email([self.test_email], alert_data)
            
            call_args = mock_send.call_args
            html_content = call_args[1]['html_content']
            
            # Check for critical priority styling
            self.assertIn('#dc3545', html_content)  # Red color for critical

    def test_service_initialization_with_custom_credentials(self):
        """Test service initialization with custom SMTP credentials"""
        custom_service = GmailSMTPService(
            email_host_user='custom@example.com',
            email_host_password='custom_password'
        )
        
        self.assertEqual(custom_service.email_host_user, 'custom@example.com')
        self.assertEqual(custom_service.email_host_password, 'custom_password')

    def test_email_logging_on_failure(self):
        """Test that failed emails are properly logged"""
        with patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL') as mock_smtp_ssl:
            mock_smtp_ssl.side_effect = Exception('Network error')
            
            with patch('core.alerts.models.EmailLog.objects.create') as mock_log:
                mock_email_log = MagicMock()
                mock_log.return_value = mock_email_log
                
                result = self.service.send_email(
                    to_emails=[self.test_email],
                    subject=self.test_subject,
                    html_content=self.test_html_content,
                    user=self.user
                )
                
                # Verify failure logging
                self.assertFalse(result['success'])
                mock_email_log.save.assert_called()

    def test_multiple_recipients_handling(self):
        """Test handling multiple email recipients"""
        recipients = ['user1@example.com', 'user2@example.com', 'user3@example.com']
        
        with patch('core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL') as mock_smtp_ssl:
            mock_server = MagicMock()
            mock_smtp_ssl.return_value = mock_server