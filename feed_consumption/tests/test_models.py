import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from feed_consumption.models import ExternalFeedSource, FeedConsumptionLog


class ExternalFeedSourceModelTests(TestCase):
    """Test the ExternalFeedSource model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='password123'
        )
        
        self.feed_source = ExternalFeedSource.objects.create(
            name='Test Feed',
            discovery_url='https://example.com/taxii2/',
            categories=['malware', 'indicators'],
            poll_interval=ExternalFeedSource.PollInterval.DAILY,
            auth_type=ExternalFeedSource.AuthType.API_KEY,
            auth_credentials={'key': 'test-api-key', 'header_name': 'X-API-Key'},
            added_by=self.user
        )
    
    def test_feed_source_creation(self):
        """Test creating a feed source."""
        self.assertEqual(self.feed_source.name, 'Test Feed')
        self.assertEqual(self.feed_source.discovery_url, 'https://example.com/taxii2/')
        self.assertEqual(self.feed_source.categories, ['malware', 'indicators'])
        self.assertEqual(self.feed_source.poll_interval, ExternalFeedSource.PollInterval.DAILY)
        self.assertEqual(self.feed_source.auth_type, ExternalFeedSource.AuthType.API_KEY)
        self.assertEqual(self.feed_source.auth_credentials, {'key': 'test-api-key', 'header_name': 'X-API-Key'})
        self.assertEqual(self.feed_source.added_by, self.user)
        self.assertTrue(self.feed_source.is_active)
        self.assertIsNone(self.feed_source.last_poll_time)
    
    def test_feed_source_str(self):
        """Test the string representation."""
        self.assertEqual(str(self.feed_source), 'Test Feed (Daily)')
    
    def test_get_auth_config_api_key(self):
        """Test getting auth config for API key auth type."""
        auth_config = self.feed_source.get_auth_config()
        self.assertEqual(auth_config['type'], 'api_key')
        self.assertEqual(auth_config['header_name'], 'X-API-Key')
        self.assertEqual(auth_config['key'], 'test-api-key')
    
    def test_get_auth_config_jwt(self):
        """Test getting auth config for JWT auth type."""
        self.feed_source.auth_type = ExternalFeedSource.AuthType.JWT
        self.feed_source.auth_credentials = {'token': 'test-jwt-token'}
        self.feed_source.save()
        
        auth_config = self.feed_source.get_auth_config()
        self.assertEqual(auth_config['type'], 'jwt')
        self.assertEqual(auth_config['token'], 'test-jwt-token')
    
    def test_get_auth_config_basic(self):
        """Test getting auth config for basic auth type."""
        self.feed_source.auth_type = ExternalFeedSource.AuthType.BASIC
        self.feed_source.auth_credentials = {'username': 'testuser', 'password': 'testpass'}
        self.feed_source.save()
        
        auth_config = self.feed_source.get_auth_config()
        self.assertEqual(auth_config['type'], 'basic')
        self.assertEqual(auth_config['username'], 'testuser')
        self.assertEqual(auth_config['password'], 'testpass')
    
    def test_get_auth_config_none(self):
        """Test getting auth config with no auth."""
        self.feed_source.auth_type = ExternalFeedSource.AuthType.NONE
        self.feed_source.auth_credentials = {}  # Use empty dict instead of None
        self.feed_source.save()
        
        auth_config = self.feed_source.get_auth_config()
        self.assertIsNone(auth_config)
    
    def test_categories_validation(self):
        """Test categories field validation."""
        # Valid categories
        self.feed_source.categories = ['malware', 'indicators', 'ttps']
        self.feed_source.save()
        
        # Invalid category (should pass since ArrayField doesn't validate choices)
        self.feed_source.categories = ['invalid_category']
        self.feed_source.save()
        
        # Empty list is valid
        self.feed_source.categories = []
        self.feed_source.save()


class FeedConsumptionLogModelTests(TestCase):
    """Test the FeedConsumptionLog model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='password123'
        )
        
        self.feed_source = ExternalFeedSource.objects.create(
            name='Test Feed',
            discovery_url='https://example.com/taxii2/',
            categories=['malware'],
            poll_interval=ExternalFeedSource.PollInterval.DAILY,
            added_by=self.user
        )
        
        self.log_entry = FeedConsumptionLog.objects.create(
            feed_source=self.feed_source,
            status='completed',  # This maps to ConsumptionStatus.SUCCESS
            objects_retrieved=100,
            objects_processed=95,
            objects_failed=5
        )
    
    def test_log_creation(self):
        """Test creating a log entry."""
        self.assertEqual(self.log_entry.feed_source, self.feed_source)
        self.assertEqual(self.log_entry.status, 'completed')  # This maps to ConsumptionStatus.SUCCESS
        self.assertEqual(self.log_entry.objects_retrieved, 100)
        self.assertEqual(self.log_entry.objects_processed, 95)
        self.assertEqual(self.log_entry.objects_failed, 5)
        self.assertEqual(self.log_entry.error_message, '')
        self.assertIsNotNone(self.log_entry.start_time)
        self.assertIsNone(self.log_entry.end_time)
    
    def test_log_str(self):
        """Test the string representation."""
        # Since start_time is auto_now_add, it should be set
        start_time_str = self.log_entry.start_time.strftime('%Y-%m-%d %H:%M')
        expected_str = f"{self.feed_source.name} - {start_time_str} - Success"
        self.assertEqual(str(self.log_entry), expected_str)
    
    def test_add_error(self):
        """Test adding an error message."""
        # Add first error
        self.log_entry.add_error("Test error message")
        self.assertEqual(self.log_entry.error_message, "Test error message")
        self.assertEqual(self.log_entry.status, 'partial')  # This maps to ConsumptionStatus.PARTIAL
        
        # Add second error
        self.log_entry.add_error("Another error message")
        self.assertEqual(self.log_entry.error_message, "Test error message\nAnother error message")
        
        # Set objects_processed to 0 and add error
        self.log_entry.objects_processed = 0
        self.log_entry.add_error("Complete failure")
        self.assertEqual(self.log_entry.status, 'failed')  # This maps to ConsumptionStatus.FAILURE
    
    def test_status_transitions(self):
        """Test status transitions based on processing counts."""
        # Initially successful
        self.assertEqual(self.log_entry.status, 'completed')  # This maps to ConsumptionStatus.SUCCESS
        
        # Add error with some processed objects -> partial success
        self.log_entry.add_error("Some error occurred")
        self.assertEqual(self.log_entry.status, 'partial')  # This maps to ConsumptionStatus.PARTIAL
        
        # No processed objects -> failure
        self.log_entry.objects_processed = 0
        self.log_entry.add_error("Complete failure")
        self.assertEqual(self.log_entry.status, 'failed')  # This maps to ConsumptionStatus.FAILURE