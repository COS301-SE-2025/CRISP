"""
Unit tests for Gmail SMTP email service functionality
"""
import unittest
from unittest.mock import patch, MagicMock, call
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from datetime import datetime

from core.services.gmail_smtp_service import GmailSMTPService


class GmailSMTPServiceTestCase(TestCase):
    """Test cases for the GmailSMTPService"""

    def setUp(self):
        """Set up the test environment"""
        self.service = GmailSMTPService()
        self.test_email = "test@example.com"
        self.test_subject = "Test Subject"
        self.test_html_content = "<h1>Test HTML Content</h1>"
        self.test_text_content = "Test text content"

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call send_email
        result = self.service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content=self.test_html_content,
            text_content=self.test_text_content
        )
        
        # Verify SMTP interactions
        mock_smtp.assert_called_once_with(self.service.email_host, self.service.email_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            self.service.email_host_user, 
            self.service.email_host_password
        )
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Email sent successfully')

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_send_email_authentication_error(self, mock_smtp):
        """Test email sending with authentication error"""
        # Mock SMTP server with authentication error
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp.return_value = mock_server
        
        # Call send_email
        result = self.service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content=self.test_html_content
        )
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('Authentication failed', result['message'])

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_send_email_connection_error(self, mock_smtp):
        """Test email sending with connection error"""
        # Mock SMTP with connection error
        mock_smtp.side_effect = smtplib.SMTPConnectError(421, "Connection failed")
        
        # Call send_email
        result = self.service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content=self.test_html_content
        )
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('Connection failed', result['message'])

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_send_email_multiple_recipients(self, mock_smtp):
        """Test sending email to multiple recipients"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        recipient_emails = ["test1@example.com", "test2@example.com", "test3@example.com"]
        
        # Call send_email
        result = self.service.send_email(
            to_emails=recipient_emails,
            subject=self.test_subject,
            html_content=self.test_html_content
        )
        
        # Verify SMTP interactions
        mock_server.send_message.assert_called_once()
        
        # Get the sent message to verify recipients
        sent_message = mock_server.send_message.call_args[0][0]
        self.assertEqual(sent_message['To'], ', '.join(recipient_emails))
        
        # Verify result
        self.assertTrue(result['success'])

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_send_threat_alert_email(self, mock_smtp):
        """Test sending threat alert email"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        alert_data = {
            'alert_type': 'high_severity_indicator',
            'priority': 'high',
            'generated_at': timezone.now(),
            'alert_id': 'ALERT-123',
            'data': {
                'feed_name': 'AlienVault OTX',
                'indicator_type': 'IP',
                'indicator_value': '192.168.1.100',
                'severity': 'High',
                'confidence': '85'
            }
        }
        
        # Call send_threat_alert_email
        result = self.service.send_threat_alert_email(
            recipient_emails=[self.test_email],
            alert_data=alert_data
        )
        
        # Verify SMTP interactions
        mock_server.send_message.assert_called_once()
        
        # Get the sent message to verify content
        sent_message = mock_server.send_message.call_args[0][0]
        self.assertIn('⚠️ HIGH', sent_message['Subject'])
        self.assertIn('high_severity_indicator', sent_message['Subject'])
        
        # Verify result
        self.assertTrue(result['success'])

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_send_feed_notification_email(self, mock_smtp):
        """Test sending feed notification email"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        notification_data = {
            'notification_type': 'Feed Update',
            'feed_name': 'AlienVault OTX',
            'timestamp': timezone.now(),
            'details': 'New indicators available'
        }
        
        # Call send_feed_notification_email
        result = self.service.send_feed_notification_email(
            recipient_emails=[self.test_email],
            notification_data=notification_data
        )
        
        # Verify SMTP interactions
        mock_server.send_message.assert_called_once()
        
        # Get the sent message to verify content
        sent_message = mock_server.send_message.call_args[0][0]
        self.assertIn('CRISP Feed Notification', sent_message['Subject'])
        self.assertIn('AlienVault OTX', sent_message['Subject'])
        
        # Verify result
        self.assertTrue(result['success'])

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_test_connection_success(self, mock_smtp):
        """Test successful SMTP connection test"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call test_connection
        result = self.service.test_connection()
        
        # Verify SMTP interactions
        mock_smtp.assert_called_once_with(self.service.email_host, self.service.email_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.quit.assert_called_once()
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'online')

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_test_connection_failure(self, mock_smtp):
        """Test failed SMTP connection test"""
        # Mock SMTP with connection error
        mock_smtp.side_effect = smtplib.SMTPConnectError(421, "Cannot connect")
        
        # Call test_connection
        result = self.service.test_connection()
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertEqual(result['status'], 'error')
        self.assertIn('Cannot connect', result['message'])

    def test_generate_threat_alert_html(self):
        """Test HTML generation for threat alerts"""
        alert_data = {
            'alert_type': 'critical_ttp',
            'priority': 'critical',
            'generated_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'alert_id': 'ALERT-456',
            'data': {
                'feed_name': 'MITRE ATT&CK',
                'ttp_name': 'Credential Dumping',
                'tactic': 'Credential Access',
                'technique': 'T1003',
                'mitre_technique': 'T1003 - OS Credential Dumping'
            }
        }
        
        html_content = self.service._generate_threat_alert_html(alert_data)
        
        # Verify HTML content contains expected elements
        self.assertIn('critical_ttp', html_content)
        self.assertIn('critical', html_content)
        self.assertIn('ALERT-456', html_content)
        self.assertIn('Credential Dumping', html_content)
        self.assertIn('T1003', html_content)
        self.assertIn('#dc3545', html_content)  # Critical priority color

    def test_generate_threat_alert_text(self):
        """Test text generation for threat alerts"""
        alert_data = {
            'alert_type': 'bulk_indicator_activity',
            'priority': 'medium',
            'generated_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'alert_id': 'ALERT-789',
            'data': {
                'feed_id': 'feed-123',
                'indicator_count': 150,
                'time_window_minutes': 30
            }
        }
        
        text_content = self.service._generate_threat_alert_text(alert_data)
        
        # Verify text content contains expected elements
        self.assertIn('bulk_indicator_activity', text_content)
        self.assertIn('MEDIUM', text_content)
        self.assertIn('ALERT-789', text_content)
        self.assertIn('150', text_content)
        self.assertIn('30 minutes', text_content)

    def test_configuration_validation(self):
        """Test service configuration validation"""
        # Test that service has required configuration
        self.assertIsNotNone(self.service.email_host)
        self.assertIsNotNone(self.service.email_port)
        self.assertIsNotNone(self.service.email_use_tls)
        self.assertIsNotNone(self.service.default_sender)

    def test_priority_color_mapping(self):
        """Test priority color mapping in HTML generation"""
        priorities = ['critical', 'high', 'medium', 'low', 'info']
        expected_colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#17a2b8']
        
        for priority, expected_color in zip(priorities, expected_colors):
            alert_data = {
                'alert_type': 'test_alert',
                'priority': priority,
                'generated_at': timezone.now(),
                'data': {}
            }
            
            html_content = self.service._generate_threat_alert_html(alert_data)
            self.assertIn(expected_color, html_content)

    @patch('core.services.gmail_smtp_service.smtplib.SMTP')
    def test_send_email_without_tls(self, mock_smtp):
        """Test email sending without TLS"""
        # Create service instance with TLS disabled
        service = GmailSMTPService()
        service.email_use_tls = False
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call send_email
        result = service.send_email(
            to_emails=[self.test_email],
            subject=self.test_subject,
            html_content=self.test_html_content
        )
        
        # Verify TLS was not started
        mock_server.starttls.assert_not_called()
        
        # Verify other SMTP interactions
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
        # Verify result
        self.assertTrue(result['success'])