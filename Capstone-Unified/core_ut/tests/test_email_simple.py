"""
Simple Email Test - Basic Functionality Check
"""

import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from core_ut.notifications.services.gmail_smtp_service import GmailSMTPService

class SimpleEmailTest(TestCase):
    """Simple test to verify email service works"""
    
    def setUp(self):
        self.service = GmailSMTPService()
    
    def test_email_service_initialization(self):
        """Test that email service initializes correctly"""
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.email_host)
    
    def test_send_email_with_mock(self):
        """Test email sending with proper mocking"""
        with patch('core.notifications.services.gmail_smtp_service.smtplib') as mock_smtplib:
            # Mock the SMTP class
            mock_smtp = MagicMock()
            mock_smtplib.SMTP.return_value = mock_smtp
            
            # Test basic email sending
            result = self.service.send_email(
                to_emails=['test@example.com'],
                subject='Test Email',
                html_content='<h1>Test</h1>',
                text_content='Test'
            )
            
            # Should return a result dict
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)

if __name__ == '__main__':
    unittest.main()
