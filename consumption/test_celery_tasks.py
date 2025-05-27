import uuid
from unittest import mock
from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from celery.exceptions import MaxRetriesExceededError

from feed_consumption.models import ExternalFeedSource, FeedConsumptionLog
from feed_consumption.tasks import (
    consume_feed, schedule_feed_consumption,
    retry_failed_feeds, manual_feed_refresh
)
from feed_consumption.taxii_client import TaxiiClientError
from feed_consumption.data_processor import DataProcessingError


class CeleryTaskTests(TestCase):
    """Test the Celery tasks implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='password123'
        )
        
        # Create active feed source
        self.active_feed = ExternalFeedSource.objects.create(
            name='Active Feed',
            discovery_url='https://example.com/taxii2/',
            categories=['malware', 'indicators'],
            poll_interval=ExternalFeedSource.PollInterval.DAILY,
            is_active=True,
            added_by=self.user
        )
        
        # Create inactive feed source
        self.inactive_feed = ExternalFeedSource.objects.create(
            name='Inactive Feed',
            discovery_url='https://example.com/taxii2/inactive/',
            categories=['ttps'],
            poll_interval=ExternalFeedSource.PollInterval.WEEKLY,
            is_active=False,
            added_by=self.user
        )
        
        # Create feed source with last poll time
        self.recently_polled_feed = ExternalFeedSource.objects.create(
            name='Recently Polled Feed',
            discovery_url='https://example.com/taxii2/recent/',
            categories=['indicators'],
            poll_interval=ExternalFeedSource.PollInterval.DAILY,
            is_active=True,
            last_poll_time=timezone.now() - timedelta(hours=12),
            added_by=self.user
        )
        
        # Create feed source that needs polling
        self.needs_polling_feed = ExternalFeedSource.objects.create(
            name='Needs Polling Feed',
            discovery_url='https://example.com/taxii2/needs-polling/',
            categories=['malware'],
            poll_interval=ExternalFeedSource.PollInterval.DAILY,
            is_active=True,
            last_poll_time=timezone.now() - timedelta(days=2),
            added_by=self.user
        )
    
    @mock.patch('feed_consumption.tasks.TaxiiClient')
    @mock.patch('feed_consumption.tasks.DataProcessor')
    def test_consume_feed_success(self, mock_processor_class, mock_client_class):
        """Test successful feed consumption task."""
        # Configure mocks
        mock_client = mock.MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_client.consume_feed.return_value = {
            'status': 'success',
            'objects': [{'id': 'indicator-1'}, {'id': 'malware-1'}],
            'objects_retrieved': 2
        }
        
        mock_processor = mock.MagicMock()
        mock_processor_class.return_value = mock_processor
        
        mock_processor.process_objects.return_value = {
            'processed': 2,
            'failed': 0,
            'duplicates': 0,
            'edu_relevant': 1
        }
        
        # Call the task
        result = consume_feed(str(self.active_feed.id))
        
        # Check task was successful
        self.assertEqual(result['status'], 'success')
        
        # Verify TaxiiClient was created and used
        mock_client_class.assert_called_once_with(self.active_feed)
        mock_client.consume_feed.assert_called_once()
        
        # Verify DataProcessor was created and used
        mock_processor_class.assert_called_once_with(self.active_feed, mock_client.log_entry)
        mock_processor.process_objects.assert_called_once_with([{'id': 'indicator-1'}, {'id': 'malware-1'}])
        
        # Check combined results
        self.assertEqual(result['processed'], 2)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['duplicates'], 0)
        self.assertEqual(result['edu_relevant'], 1)
    
    def test_consume_feed_inactive(self):
        """Test feed consumption task with inactive feed."""
        # Call the task with inactive feed
        result = consume_feed(str(self.inactive_feed.id))
        
        # Check task was skipped
        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'feed not active')
    
    def test_consume_feed_not_found(self):
        """Test feed consumption task with non-existent feed."""
        # Call the task with a random UUID
        result = consume_feed(str(uuid.uuid4()))
        
        # Check task failed
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['reason'], 'feed not found')
    
    @mock.patch('feed_consumption.tasks.TaxiiClient')
    def test_consume_feed_client_error(self, mock_client_class):
        """Test feed consumption task with client error."""
        # Configure mock to raise exception
        mock_client = mock.MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_client.consume_feed.side_effect = TaxiiClientError("Connection failed")
        
        # Mock the retry method
        consume_feed.retry = mock.MagicMock(side_effect=MaxRetriesExceededError)
        
        # Call the task
        result = consume_feed(str(self.active_feed.id))
        
        # Check task failed
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['reason'], 'Connection failed')
        
        # Verify retry was attempted
        consume_feed.retry.assert_called_once()
    
    @mock.patch('feed_consumption.tasks.TaxiiClient')
    def test_consume_feed_unexpected_error(self, mock_client_class):
        """Test feed consumption task with unexpected error."""
        # Configure mock to raise unexpected exception
        mock_client = mock.MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_client.consume_feed.side_effect = ValueError("Unexpected error")
        
        # Call the task
        result = consume_feed(str(self.active_feed.id))
        
        # Check task failed
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unexpected error', result['reason'])
    
    @mock.patch('feed_consumption.tasks.consume_feed.delay')
    def test_schedule_feed_consumption(self, mock_delay):
        """Test feed consumption scheduling task."""
        # Call the task
        result = schedule_feed_consumption()
        
        # Check only the feeds that need polling were scheduled
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['daily'], 1)  # Only the needs_polling_feed
        
        # Verify consume_feed.delay was called for the right feed
        mock_delay.assert_called_once_with(str(self.needs_polling_feed.id))
    
    @mock.patch('feed_consumption.tasks.timezone.now')
    @mock.patch('feed_consumption.tasks.consume_feed.delay')
    def test_schedule_feed_consumption_all_intervals(self, mock_delay, mock_now):
        """Test scheduling with different poll intervals."""
        # Set up mock for current time
        current_time = timezone.now()
        mock_now.return_value = current_time
        
        # Set up feeds with different intervals
        hourly_feed = ExternalFeedSource.objects.create(
            name='Hourly Feed',
            discovery_url='https://example.com/taxii2/hourly/',
            poll_interval=ExternalFeedSource.PollInterval.HOURLY,
            is_active=True,
            last_poll_time=current_time - timedelta(hours=2),
            added_by=self.user
        )
        
        weekly_feed = ExternalFeedSource.objects.create(
            name='Weekly Feed',
            discovery_url='https://example.com/taxii2/weekly/',
            poll_interval=ExternalFeedSource.PollInterval.WEEKLY,
            is_active=True,
            last_poll_time=current_time - timedelta(days=8),
            added_by=self.user
        )
        
        monthly_feed = ExternalFeedSource.objects.create(
            name='Monthly Feed',
            discovery_url='https://example.com/taxii2/monthly/',
            poll_interval=ExternalFeedSource.PollInterval.MONTHLY,
            is_active=True,
            last_poll_time=current_time - timedelta(days=31),
            added_by=self.user
        )
        
        # Call the task
        result = schedule_feed_consumption()
        
        # Check results
        self.assertEqual(result['total'], 4)  # needs_polling_feed + 3 new feeds
        self.assertEqual(result['hourly'], 1)
        self.assertEqual(result['daily'], 1)
        self.assertEqual(result['weekly'], 1)
        self.assertEqual(result['monthly'], 1)
        
        # Verify consume_feed.delay was called for each feed
        self.assertEqual(mock_delay.call_count, 4)
        call_args_list = [call_args[0][0] for call_args in mock_delay.call_args_list]
        self.assertIn(str(hourly_feed.id), call_args_list)
        self.assertIn(str(weekly_feed.id), call_args_list)
        self.assertIn(str(monthly_feed.id), call_args_list)
        self.assertIn(str(self.needs_polling_feed.id), call_args_list)
    
    @mock.patch('feed_consumption.tasks.consume_feed.delay')
    def test_retry_failed_feeds(self, mock_delay):
        """Test retrying failed feeds."""
        # Create failed log entries
        log1 = FeedConsumptionLog.objects.create(
            feed_source=self.active_feed,
            status=FeedConsumptionLog.ConsumptionStatus.FAILURE,
            start_time=timezone.now() - timedelta(hours=1),
            error_message="Test failure"
        )
        
        log2 = FeedConsumptionLog.objects.create(
            feed_source=self.needs_polling_feed,
            status=FeedConsumptionLog.ConsumptionStatus.FAILURE,
            start_time=timezone.now() - timedelta(hours=2),
            error_message="Another failure"
        )
        
        # Create a failed log for inactive feed (shouldn't be retried)
        log3 = FeedConsumptionLog.objects.create(
            feed_source=self.inactive_feed,
            status=FeedConsumptionLog.ConsumptionStatus.FAILURE,
            start_time=timezone.now() - timedelta(hours=3),
            error_message="Inactive feed failure"
        )
        
        # Create an old failed log (shouldn't be retried)
        log4 = FeedConsumptionLog.objects.create(
            feed_source=self.active_feed,
            status=FeedConsumptionLog.ConsumptionStatus.FAILURE,
            start_time=timezone.now() - timedelta(hours=25),
            error_message="Old failure"
        )
        
        # Call the task
        result = retry_failed_feeds()
        
        # Check results
        self.assertEqual(result['retried'], 2)  # Only the recent failures for active feeds
        
        # Verify consume_feed.delay was called for the right feeds
        self.assertEqual(mock_delay.call_count, 2)
        call_args_list = [call_args[0][0] for call_args in mock_delay.call_args_list]
        self.assertIn(str(self.active_feed.id), call_args_list)
        self.assertIn(str(self.needs_polling_feed.id), call_args_list)
    
    @mock.patch('feed_consumption.tasks.consume_feed')
    def test_manual_feed_refresh(self, mock_consume_feed):
        """Test manual feed refresh task."""
        # Configure mock
        mock_consume_feed.return_value = {'status': 'success', 'processed': 5}
        
        # Call the task
        result = manual_feed_refresh(str(self.active_feed.id))
        
        # Check task was successful
        self.assertEqual(result['status'], 'success')
        
        # Verify consume_feed was called with the right feed
        mock_consume_feed.assert_called_once_with(str(self.active_feed.id))
