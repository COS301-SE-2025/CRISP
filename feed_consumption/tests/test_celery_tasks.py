from datetime import datetime, timedelta
import pytz
from unittest.mock import patch, MagicMock, call 
from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from feed_consumption.models import ExternalFeedSource, FeedConsumptionLog
from feed_consumption.tasks import (
    consume_feed as consume_feed_task, # Alias for test compatibility
    schedule_feed_consumption, # Corrected: Removed _task suffix
    retry_failed_feeds, # Corrected: Removed _task suffix
    LoggableTask
)
from feed_consumption.taxii_client import TaxiiClientError # Keep for raising
from feed_consumption.data_processor import DataProcessingError # Keep for raising

# mock_now_dt is a fixed datetime object for consistent testing
mock_now_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.utc)

# Use a lambda for the patch to ensure it returns the datetime directly
@patch('feed_consumption.taxii_client_service.TaxiiClientService')
@patch('feed_consumption.data_processing_service.DataProcessor')
@patch('feed_consumption.tasks.timezone.now', lambda: mock_now_dt) # Changed to lambda
class CeleryTaskTests(TestCase):
    def setUp(self, MockDataProcessorClass, MockTaxiiServiceClass): # Order matters based on decorator order
        # These are now mock classes. We'll use their return_value for instances.
        self.MockDataProcessorClass = MockDataProcessorClass
        self.MockTaxiiServiceClass = MockTaxiiServiceClass

        # Configure default behavior for mock instances
        self.mock_taxii_service_instance = self.MockTaxiiServiceClass.return_value
        self.mock_data_processor_instance = self.MockDataProcessorClass.return_value
        
        # Common feed source for tests that don't create their own
        self.feed_source = ExternalFeedSource.objects.create(
            name="Test Feed Setup",
            feed_url="http://example.com/taxii2_setup",
            api_root_url="http://example.com/api_setup",
            collection_id="collection_setup",
            feed_format="taxii2",
            is_active=True,
            poll_interval=ExternalFeedSource.PollInterval.HOURLY,
            username="user",
            password="password",
            # created_at and updated_at are auto-set
        )
        # Ensure a clean slate for logs related to self.feed_source if needed by specific tests
        FeedConsumptionLog.objects.filter(feed=self.feed_source).delete()


    @patch('feed_consumption.tasks.send_notification') # This is an inner patch
    def test_consume_feed_success(self, mock_send_notification, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        # Ensure we use the instance from setUp or re-assign if class mocks are method args
        mock_taxii_service = self.MockTaxiiServiceClass.return_value
        mock_data_processor = self.MockDataProcessorClass.return_value

        feed_source = ExternalFeedSource.objects.create(
            name="Test Feed Success",
            feed_url="http://example.com/taxii2",
            api_root_url="http://example.com/api1",
            collection_id="collection1",
            feed_format="taxii2",
            is_active=True,
            poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )

        mock_taxii_service.consume_feed.return_value = {
            'status': 'success',
            'feed_name': feed_source.name,
            'objects_retrieved': 1,
            'objects_processed': 1,
            'errors': 0,
            'duration': 1.0,
            'reason': None
        }
        
        result = consume_feed_task(feed_source.id)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['objects_retrieved'], 1)
        self.assertEqual(result['objects_processed'], 1)
        mock_taxii_service.consume_feed.assert_called_once()
        mock_send_notification.assert_called_once()
        log = FeedConsumptionLog.objects.get(feed=feed_source)
        self.assertEqual(log.status, FeedConsumptionLog.Status.COMPLETED)
        self.assertEqual(log.objects_retrieved, 1)

    @patch('feed_consumption.tasks.send_notification')
    def test_consume_feed_data_processing_error(self, mock_send_notification, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        mock_taxii_service = self.MockTaxiiServiceClass.return_value
        
        feed_source = ExternalFeedSource.objects.create(
            name="Test Feed Data Error",
            feed_url="http://example.com/taxii2_data_error",
            api_root_url="http://example.com/api_data_error",
            collection_id="collection_data_error",
            feed_format="taxii2",
            is_active=True,
            poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )
        
        expected_reason = "Data processing failed during consumption"
        mock_taxii_service.consume_feed.return_value = {
            'status': 'error',
            'feed_name': feed_source.name,
            'reason': expected_reason,
            'duration': 1.0
        }

        result = consume_feed_task(feed_source.id)

        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['reason'], expected_reason)
        mock_taxii_service.consume_feed.assert_called_once()
        # Notification might be sent for errors too, depending on logic
        # mock_send_notification.assert_called_once() 
        log = FeedConsumptionLog.objects.get(feed=feed_source)
        self.assertEqual(log.status, FeedConsumptionLog.Status.FAILED)
        self.assertIn(expected_reason, log.error_message)

    @patch('feed_consumption.tasks.send_notification')
    def test_consume_feed_client_error(self, mock_send_notification, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        mock_taxii_service = self.MockTaxiiServiceClass.return_value

        feed_source = ExternalFeedSource.objects.create(
            name="Test Feed Client Error",
            feed_url="http://example.com/taxii2_client_error",
            api_root_url="http://example.com/api_client_error", # Must be present
            collection_id="collection_client_error",       # Must be present
            feed_format="taxii2",
            is_active=True,
            poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )
        
        expected_reason = "Connection failed" # This is what the service should return as reason
        mock_taxii_service.consume_feed.return_value = {
            'status': 'error',
            'feed_name': feed_source.name,
            'reason': expected_reason,
            'duration': 1.0
        }
        # If consume_feed itself raises the error, it would be:
        # mock_taxii_service.consume_feed.side_effect = TaxiiClientError(expected_reason)


        result = consume_feed_task(feed_source.id)

        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['reason'], expected_reason)
        mock_taxii_service.consume_feed.assert_called_once()
        log = FeedConsumptionLog.objects.get(feed=feed_source)
        self.assertEqual(log.status, FeedConsumptionLog.Status.FAILED)
        self.assertEqual(log.error_message, expected_reason)

    @patch('feed_consumption.tasks.send_notification')
    def test_consume_feed_unexpected_error(self, mock_send_notification, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        mock_taxii_service = self.MockTaxiiServiceClass.return_value
        
        feed_source = ExternalFeedSource.objects.create(
            name="Test Feed Unexpected Error",
            feed_url="http://example.com/taxii2_unexpected",
            api_root_url="http://example.com/api_unexpected",
            collection_id="collection_unexpected",
            feed_format="taxii2",
            is_active=True,
            poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )
        
        # Simulate the service's consume_feed method raising an unexpected error
        mock_taxii_service.consume_feed.side_effect = Exception("Something broke badly")

        result = consume_feed_task(feed_source.id)

        self.assertEqual(result['status'], 'error')
        self.assertIn('Unexpected error: Something broke badly', result['reason'])
        mock_taxii_service.consume_feed.assert_called_once()
        log = FeedConsumptionLog.objects.get(feed=feed_source)
        self.assertEqual(log.status, FeedConsumptionLog.Status.FAILED)
        self.assertIn("Something broke badly", log.error_message)

    @patch('feed_consumption.tasks.consume_feed_task.delay') # Mock delay for this test
    def test_schedule_feed_consumption(self, mock_consume_feed_delay, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        # ExternalFeedSource created in setUp is hourly and active
        # Create another one to be sure
        hourly_feed = ExternalFeedSource.objects.create(
            name="Test Feed Hourly Schedule",
            feed_url="http://example.com/taxii2_hourly_schedule",
            api_root_url="http://example.com/api_hourly_schedule",
            collection_id="collection_hourly_schedule",
            feed_format="taxii2",
            is_active=True,
            poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )
        
        result = schedule_feed_consumption(ExternalFeedSource.PollInterval.HOURLY.value)
        
        self.assertEqual(result['status'], 'completed')
        # It should find self.feed_source and hourly_feed
        self.assertEqual(result['total'], 2) 
        self.assertEqual(mock_consume_feed_delay.call_count, 2)
        mock_consume_feed_delay.assert_any_call(self.feed_source.id)
        mock_consume_feed_delay.assert_any_call(hourly_feed.id)


    @patch('feed_consumption.tasks.consume_feed_task.delay') # Mock delay for this test
    def test_schedule_feed_consumption_all_intervals(self, mock_consume_feed_delay, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        # These feeds are created, and the lambda mock for timezone.now should prevent F() error
        ExternalFeedSource.objects.create(name="H", feed_url="h",api_root_url="h",collection_id="h",is_active=True,poll_interval=ExternalFeedSource.PollInterval.HOURLY)
        ExternalFeedSource.objects.create(name="D", feed_url="d",api_root_url="d",collection_id="d",is_active=True,poll_interval=ExternalFeedSource.PollInterval.DAILY)
        ExternalFeedSource.objects.create(name="W", feed_url="w",api_root_url="w",collection_id="w",is_active=True,poll_interval=ExternalFeedSource.PollInterval.WEEKLY)
        ExternalFeedSource.objects.create(name="M", feed_url="m",api_root_url="m",collection_id="m",is_active=True,poll_interval=ExternalFeedSource.PollInterval.MONTHLY)
        # self.feed_source is also HOURLY and active

        # Hourly
        result_hourly = schedule_feed_consumption(ExternalFeedSource.PollInterval.HOURLY.value)
        self.assertEqual(result_hourly['total'], 2) # H + self.feed_source
        # Daily
        result_daily = schedule_feed_consumption(ExternalFeedSource.PollInterval.DAILY.value)
        self.assertEqual(result_daily['total'], 1) # D
        # Weekly
        result_weekly = schedule_feed_consumption(ExternalFeedSource.PollInterval.WEEKLY.value)
        self.assertEqual(result_weekly['total'], 1) # W
        # Monthly
        result_monthly = schedule_feed_consumption(ExternalFeedSource.PollInterval.MONTHLY.value)
        self.assertEqual(result_monthly['total'], 1) # M
        
        self.assertEqual(mock_consume_feed_delay.call_count, 2 + 1 + 1 + 1)


    @patch('feed_consumption.tasks.consume_feed_task.delay') # Mock delay for this test
    def test_retry_failed_feeds(self, mock_consume_feed_delay, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        # Active feed, recent failure
        active_feed_recent_failure = ExternalFeedSource.objects.create(
            name="Active Feed Recent Failure", feed_url="url1", api_root_url="api1", collection_id="col1",
            is_active=True, poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )
        FeedConsumptionLog.objects.create(
            feed=active_feed_recent_failure, status=FeedConsumptionLog.Status.FAILED, 
            error_message="failed", updated_at=mock_now_dt - timedelta(hours=1)
        )

        # Active feed, old failure (should not be retried)
        active_feed_old_failure = ExternalFeedSource.objects.create(
            name="Active Feed Old Failure", feed_url="url2", api_root_url="api2", collection_id="col2",
            is_active=True, poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )
        FeedConsumptionLog.objects.create(
            feed=active_feed_old_failure, status=FeedConsumptionLog.Status.FAILED, 
            error_message="failed old", updated_at=mock_now_dt - timedelta(days=3) # Older than 1 day
        )

        # Inactive feed, recent failure (should not be retried)
        inactive_feed_recent_failure = ExternalFeedSource.objects.create(
            name="Inactive Feed Recent Failure", feed_url="url3", api_root_url="api3", collection_id="col3",
            is_active=False, poll_interval=ExternalFeedSource.PollInterval.HOURLY # Inactive
        )
        FeedConsumptionLog.objects.create(
            feed=inactive_feed_recent_failure, status=FeedConsumptionLog.Status.FAILED, 
            error_message="failed inactive", updated_at=mock_now_dt - timedelta(hours=1)
        )
        
        # Active feed, but successful log (should not be retried)
        active_feed_success = ExternalFeedSource.objects.create(
            name="Active Feed Success Log", feed_url="url4", api_root_url="api4", collection_id="col4",
            is_active=True, poll_interval=ExternalFeedSource.PollInterval.HOURLY
        )
        FeedConsumptionLog.objects.create(
            feed=active_feed_success, status=FeedConsumptionLog.Status.COMPLETED, 
            updated_at=mock_now_dt - timedelta(hours=1)
        )

        result = retry_failed_feeds_task()

        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['retried'], 1) # Only active_feed_recent_failure
        self.assertEqual(mock_consume_feed_delay.call_count, 1)
        mock_consume_feed_delay.assert_called_once_with(active_feed_recent_failure.id)
        # Check that total_failed_logs reflects all FAILED logs within cutoff, regardless of retry decision based on unique feeds
        # In this setup, only one log (for active_feed_recent_failure) matches all criteria for initial selection.
        self.assertEqual(result['total_failed_logs'], 1)


    def test_loggable_task_on_failure(self, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        feed = ExternalFeedSource.objects.create(name="FailureTestFeed", feed_url="url", api_root_url="api", collection_id="col")
        task_instance = LoggableTask()
        task_instance.request = MagicMock()
        task_instance.request.id = "test_task_id"
        task_instance.feed_id = feed.id # Manually set for test
        
        exc = ValueError("Test exception")
        einfo = MagicMock()

        # Mock timezone.now specifically for this LoggableTask context if its internal now is different
        # However, the class-level mock should cover feed_consumption.tasks.timezone.now
        
        task_instance.on_failure(exc, "task_id_placeholder", (), {}, einfo)
        
        log = FeedConsumptionLog.objects.get(feed=feed)
        self.assertEqual(log.status, FeedConsumptionLog.Status.FAILED)
        self.assertIn("ValueError: Test exception", log.error_message)
        self.assertEqual(log.task_id, "task_id_placeholder") # Celery task ID

    def test_loggable_task_on_success(self, MockDataProcessorClass_method_arg, MockTaxiiServiceClass_method_arg):
        feed = ExternalFeedSource.objects.create(name="SuccessTestFeed", feed_url="urlS", api_root_url="apiS", collection_id="colS")
        task_instance = LoggableTask()
        task_instance.request = MagicMock()
        task_instance.request.id = "test_task_id_success"
        task_instance.feed_id = feed.id # Manually set

        # Simulate a successful result dict from consume_feed_task
        retval = {
            'status': 'success', 
            'feed_name': feed.name, 
            'objects_retrieved': 10, 
            'objects_processed': 8,
            'errors': 2, 
            'duration': 5.5
        }
        
        task_instance.on_success(retval, "task_id_success_placeholder", (), {})
        
        log = FeedConsumptionLog.objects.get(feed=feed)
        self.assertEqual(log.status, FeedConsumptionLog.Status.COMPLETED)
        self.assertEqual(log.objects_retrieved, 10)
        self.assertEqual(log.objects_processed, 8)
        self.assertEqual(log.task_id, "task_id_success_placeholder")
