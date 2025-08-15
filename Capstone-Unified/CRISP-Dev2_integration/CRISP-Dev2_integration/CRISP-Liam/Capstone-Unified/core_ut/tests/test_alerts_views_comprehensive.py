"""
Comprehensive tests for alerts views to increase coverage
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from core_ut.user_management.models import CustomUser, Organization


class AlertsViewsComprehensiveTest(APITestCase):
    """Comprehensive test suite for alerts views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Alerts Org',
            domain='testalerts.com',
            contact_email='admin@testalerts.com',
            is_active=True,
            is_verified=True
        )
        
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='alertsuser@example.com',
            email='alertsuser@example.com',
            password='TestPassword123',
            first_name='Alerts',
            last_name='User',
            role='publisher',
            organization=self.organization,
            is_active=True,
            is_verified=True
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_get_alerts_list_success(self):
        """Test successful alerts list retrieval"""
        response = self.client.get('/api/v1/alerts/list/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsInstance(response.data['data'], list)
    
    def test_get_alerts_list_unauthenticated(self):
        """Test alerts list requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/alerts/list/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_send_threat_alert_email_success(self, mock_gmail_service):
        """Test successful threat alert sending"""
        # Mock Gmail service
        mock_service_instance = Mock()
        mock_service_instance.send_threat_alert_email.return_value = {
            'success': True,
            'message': 'Alert sent successfully',
            'recipients': 2
        }
        mock_gmail_service.return_value = mock_service_instance
        
        alert_data = {
            'recipient_emails': ['user1@example.com', 'user2@example.com'],
            'threat_type': 'malware',
            'threat_level': 'high',
            'description': 'Test threat alert',
            'indicators': ['192.168.1.100', 'malware.exe']
        }
        
        response = self.client.post('/api/v1/alerts/threat/', alert_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_service_instance.send_threat_alert_email.assert_called_once()
    
    def test_send_threat_alert_email_no_recipients(self):
        """Test threat alert with no recipients"""
        alert_data = {
            'threat_type': 'malware',
            'threat_level': 'high',
            'description': 'Test threat alert'
        }
        
        response = self.client.post('/api/v1/alerts/threat/', alert_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_send_threat_alert_email_service_failure(self, mock_gmail_service):
        """Test threat alert service failure"""
        # Mock Gmail service failure
        mock_service_instance = Mock()
        mock_service_instance.send_threat_alert_email.return_value = {
            'success': False,
            'message': 'SMTP connection failed',
            'error': 'Connection timeout'
        }
        mock_gmail_service.return_value = mock_service_instance
        
        alert_data = {
            'recipient_emails': ['user1@example.com'],
            'threat_type': 'malware',
            'threat_level': 'high',
            'description': 'Test threat alert'
        }
        
        response = self.client.post('/api/v1/alerts/threat/', alert_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_send_threat_alert_email_exception(self, mock_gmail_service):
        """Test threat alert with exception"""
        # Mock Gmail service exception
        mock_gmail_service.side_effect = Exception('Gmail service error')
        
        alert_data = {
            'recipient_emails': ['user1@example.com'],
            'threat_type': 'malware',
            'threat_level': 'high',
            'description': 'Test threat alert'
        }
        
        response = self.client.post('/api/v1/alerts/threat/', alert_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_send_feed_notification_email_success(self, mock_gmail_service):
        """Test successful feed notification sending"""
        # Mock Gmail service
        mock_service_instance = Mock()
        mock_service_instance.send_feed_notification_email.return_value = {
            'success': True,
            'message': 'Notification sent successfully',
            'recipients': 1
        }
        mock_gmail_service.return_value = mock_service_instance
        
        feed_data = {
            'recipient_emails': ['user1@example.com'],
            'feed_name': 'MITRE ATT&CK',
            'update_type': 'new_techniques',
            'summary': 'New attack techniques added',
            'items': ['T1234', 'T5678']
        }
        
        response = self.client.post('/api/v1/alerts/feed/', feed_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_service_instance.send_feed_notification_email.assert_called_once()
    
    def test_send_feed_notification_email_no_recipients(self):
        """Test feed notification with no recipients"""
        feed_data = {
            'feed_name': 'MITRE ATT&CK',
            'update_type': 'new_techniques',
            'summary': 'New attack techniques added'
        }
        
        response = self.client.post('/api/v1/alerts/feed/', feed_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_test_connection_success(self, mock_gmail_service):
        """Test successful Gmail connection test"""
        # Mock Gmail service
        mock_service_instance = Mock()
        mock_service_instance.test_connection.return_value = {
            'success': True,
            'status': 'online',
            'message': 'Gmail SMTP connection successful'
        }
        mock_gmail_service.return_value = mock_service_instance
        
        response = self.client.get('/api/v1/alerts/test-connection/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['status'], 'online')
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_test_connection_failure(self, mock_gmail_service):
        """Test Gmail connection test failure"""
        # Mock Gmail service failure
        mock_service_instance = Mock()
        mock_service_instance.test_connection.return_value = {
            'success': False,
            'status': 'offline',
            'message': 'SMTP connection failed'
        }
        mock_gmail_service.return_value = mock_service_instance
        
        response = self.client.get('/api/v1/alerts/test-connection/')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_get_email_statistics_success(self, mock_gmail_service):
        """Test successful email statistics retrieval"""
        # Mock Gmail service
        mock_service_instance = Mock()
        mock_service_instance.test_connection.return_value = {
            'success': True,
            'status': 'online'
        }
        mock_gmail_service.return_value = mock_service_instance
        
        response = self.client.get('/api/v1/alerts/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_emails_sent', response.data)
        self.assertIn('configuration_status', response.data)
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_get_email_statistics_exception(self, mock_gmail_service):
        """Test email statistics with exception"""
        # Mock Gmail service exception
        mock_gmail_service.side_effect = Exception('Service error')
        
        response = self.client.get('/api/v1/alerts/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_send_threat_alert_email_success(self, mock_gmail_service):
        """Test successful test email sending"""
        # Mock Gmail service
        mock_service_instance = Mock()
        mock_service_instance.send_threat_alert_email.return_value = {
            'success': True,
            'message': 'Test email sent successfully',
            'recipients': 1
        }
        mock_gmail_service.return_value = mock_service_instance
        
        test_data = {
            'recipient_email': 'test@example.com'
        }
        
        response = self.client.post('/api/v1/alerts/test-email/', test_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_service_instance.send_threat_alert_email.assert_called_once()
    
    def test_send_threat_alert_email_no_recipient(self):
        """Test test email with no recipient"""
        response = self.client.post('/api/v1/alerts/test-email/', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('core.services.alerts_views.GmailSMTPService')
    def test_send_threat_alert_email_service_failure(self, mock_gmail_service):
        """Test test email service failure"""
        # Mock Gmail service failure
        mock_service_instance = Mock()
        mock_service_instance.send_threat_alert_email.return_value = {
            'success': False,
            'message': 'Failed to send test email',
            'error': 'SMTP error'
        }
        mock_gmail_service.return_value = mock_service_instance
        
        test_data = {
            'recipient_email': 'test@example.com'
        }
        
        response = self.client.post('/api/v1/alerts/test-email/', test_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
    
    def test_unauthenticated_access_all_endpoints(self):
        """Test that all endpoints require authentication"""
        self.client.force_authenticate(user=None)
        
        endpoints = [
            '/api/v1/alerts/list/',
            '/api/v1/alerts/test-connection/',
            '/api/v1/alerts/statistics/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        post_endpoints = [
            ('/api/v1/alerts/threat/', {'recipient_emails': ['test@example.com']}),
            ('/api/v1/alerts/feed/', {'recipient_emails': ['test@example.com']}),
            ('/api/v1/alerts/test-email/', {'recipient_email': 'test@example.com'}),
        ]
        
        for endpoint, data in post_endpoints:
            response = self.client.post(endpoint, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)