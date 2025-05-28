import uuid
import json
from unittest import mock
from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

from requests.exceptions import RequestException, Timeout, ConnectionError
from taxii2client.exceptions import TAXIIServiceException # Corrected import

from feed_consumption.models import ExternalFeedSource, FeedConsumptionLog
# Corrected import path for TaxiiClient
from feed_consumption.taxii_client_service import TaxiiClient 
from feed_consumption.taxii_client import (
    TaxiiClientError, TaxiiConnectionError, 
    TaxiiAuthenticationError, TaxiiDataError
)


class TaxiiClientTests(TestCase):
    """Test the TAXII client implementation."""
    
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
            added_by=self.user,
            # Corrected: Set created_at and updated_at to allow saving without F() expression error
            created_at=timezone.now(), 
            updated_at=timezone.now()
        )
        
        # Create the TAXII client
        self.client = TaxiiClient(self.feed_source)
    
    def test_client_initialization(self):
        """Test client initialization and header setup."""
        self.assertEqual(self.client.feed_source, self.feed_source)
        self.assertIsNone(self.client.server)
        self.assertIsNone(self.client.api_root)
        self.assertIsNone(self.client.collection)
        self.assertIsNone(self.client.log_entry)
        
        # Check headers
        self.assertEqual(self.client.headers['Accept'], 'application/taxii+json;version=2.1')
        self.assertIn('User-Agent', self.client.headers)
        self.assertEqual(self.client.headers['X-API-Key'], 'test-api-key')
    
    def test_apply_authentication_api_key(self):
        """Test applying API key authentication."""
        auth_config = {
            'type': 'api_key',
            'header_name': 'Authorization',
            'key': 'ApiKey test-key'
        }
        
        client = TaxiiClient(self.feed_source)
        client._apply_authentication(auth_config)
        
        self.assertEqual(client.headers['Authorization'], 'ApiKey test-key')
    
    def test_apply_authentication_jwt(self):
        """Test applying JWT authentication."""
        auth_config = {
            'type': 'jwt',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-token'
        }
        
        client = TaxiiClient(self.feed_source)
        client._apply_authentication(auth_config)
        
        self.assertEqual(client.headers['Authorization'], 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-token')
    
    def test_apply_authentication_basic(self):
        """Test applying basic authentication."""
        auth_config = {
            'type': 'basic',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        client = TaxiiClient(self.feed_source)
        client._apply_authentication(auth_config)
        
        self.assertEqual(client.auth, ('testuser', 'testpass'))
    
    @mock.patch('feed_consumption.taxii_client_service.Server') # Corrected patch path
    def test_discover_success(self, mock_server):
        """Test successful discovery."""
        # Configure mock
        mock_server_instance = mock.MagicMock()
        mock_server_instance.title = 'Test TAXII Server'
        mock_server_instance.description = 'Test server for unit tests'
        
        mock_api_root = mock.MagicMock()
        mock_api_root.url = 'https://example.com/taxii2/api1/'
        mock_server_instance.api_roots = [mock_api_root]
        
        mock_server.return_value = mock_server_instance
        
        # Call discover method
        result = self.client.discover()
        
        # Verify mock was called correctly
        mock_server.assert_called_once_with(
            self.feed_source.discovery_url,
            verify=settings.TAXII_VERIFY_SSL,
            headers=self.client.headers,
            auth=self.client.auth # Added auth parameter
        )
        
        # Check result
        self.assertEqual(result['title'], 'Test TAXII Server')
        self.assertEqual(result['description'], 'Test server for unit tests')
        self.assertEqual(result['api_roots'], ['https://example.com/taxii2/api1/'])
        
        # Check that API root was updated in feed source
        self.feed_source.refresh_from_db()
        self.assertEqual(self.feed_source.api_root_url, 'https://example.com/taxii2/api1/') # Corrected field name
    
    @mock.patch('feed_consumption.taxii_client_service.Server') # Corrected patch path
    def test_discover_error(self, mock_server):
        """Test discovery with error."""
        # Configure mock to raise exception
        mock_server.side_effect = TAXIIServiceException('Discovery failed')
        
        # Call discover method and check exception
        with self.assertRaises(TaxiiClientError):
            self.client.discover()
    
    @mock.patch('feed_consumption.taxii_client_service.ApiRoot') # Corrected patch path
    def test_get_collections_success(self, mock_api_root):
        """Test successful collection retrieval."""
        # Set up the feed source with an API root
        self.feed_source.api_root_url = 'https://example.com/taxii2/api1/' # Corrected field name
        self.feed_source.save()
        
        # Configure mock
        mock_api_root_instance = mock.MagicMock()
        
        mock_collection1 = mock.MagicMock()
        mock_collection1.id = 'collection-1'
        mock_collection1.title = 'Collection 1'
        mock_collection1.description = 'Test collection 1'
        mock_collection1.can_read = True
        mock_collection1.can_write = False
        mock_collection1.media_types = ['application/stix+json;version=2.1']
        
        mock_collection2 = mock.MagicMock()
        mock_collection2.id = 'collection-2'
        mock_collection2.title = 'Collection 2'
        mock_collection2.description = 'Test collection 2'
        mock_collection2.can_read = True
        mock_collection2.can_write = True
        mock_collection2.media_types = ['application/stix+json;version=2.1']
        
        mock_api_root_instance.collections = [mock_collection1, mock_collection2]
        mock_api_root.return_value = mock_api_root_instance
        
        # Call get_collections method
        result = self.client.get_collections()
        
        # Verify mock was called correctly
        mock_api_root.assert_called_once_with(
            self.feed_source.api_root_url, # Corrected field name
            verify=settings.TAXII_VERIFY_SSL,
            headers=self.client.headers,
            auth=self.client.auth # Added auth parameter
        )
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 'collection-1')
        self.assertEqual(result[0]['title'], 'Collection 1')
        self.assertEqual(result[1]['id'], 'collection-2')
        self.assertEqual(result[1]['title'], 'Collection 2')
        
        # Check that collection ID was updated in feed source (first readable collection)
        self.feed_source.refresh_from_db()
        self.assertEqual(self.feed_source.collection_id, 'collection-1')
    
    @mock.patch('feed_consumption.taxii_client_service.ApiRoot') # Corrected patch path
    def test_get_collections_error(self, mock_api_root):
        """Test collection retrieval with error."""
        # Set up the feed source with an API root
        self.feed_source.api_root_url = 'https://example.com/taxii2/api1/' # Corrected field name
        self.feed_source.save()
        
        # Configure mock to raise exception
        mock_api_root.side_effect = TAXIIServiceException('Collection retrieval failed')
        
        # Call get_collections method and check exception
        with self.assertRaises(TaxiiClientError):
            self.client.get_collections()
    
    @mock.patch('feed_consumption.taxii_client_service.TaxiiClient.discover') # Corrected patch path
    @mock.patch('feed_consumption.taxii_client_service.ApiRoot') # Corrected patch path
    def test_get_collections_no_api_root(self, mock_api_root, mock_discover):
        """Test collection retrieval when API root is not set."""
        # Set up the feed source with no API root
        self.feed_source.api_root_url = '' # Corrected field name
        self.feed_source.save()
        
        # Configure discover mock
        mock_discover.return_value = {
            'api_roots': ['https://example.com/taxii2/api1/']
        }
        
        # Configure API root mock
        mock_api_root_instance = mock.MagicMock()
        mock_api_root_instance.collections = []
        mock_api_root.return_value = mock_api_root_instance
        
        # Call get_collections method
        self.client.get_collections()
        
        # Verify discover was called
        mock_discover.assert_called_once()
    
    @mock.patch('feed_consumption.taxii_client_service.Collection') # Corrected patch path
    def test_get_objects_success(self, mock_collection):
        """Test successful object retrieval."""
        # Set up the feed source with API root and collection ID
        self.feed_source.api_root_url = 'https://example.com/taxii2/api1/' # Corrected field name
        self.feed_source.collection_id = 'collection-1'
        self.feed_source.save()
        
        # Configure mock
        mock_collection_instance = mock.MagicMock()
        
        # Mock the get_objects generator
        def mock_get_objects(**kwargs):
            yield {
                'objects': [
                    {'type': 'indicator', 'id': 'indicator--1', 'spec_version': '2.1'},
                    {'type': 'indicator', 'id': 'indicator--2', 'spec_version': '2.1'}
                ]
            }
            
            yield {
                'objects': [
                    {'type': 'malware', 'id': 'malware--1', 'spec_version': '2.1'}
                ]
            }
        
        mock_collection_instance.get_objects = mock_get_objects
        mock_collection.return_value = mock_collection_instance
        
        # Create a log entry for the client
        self.client.log_entry = FeedConsumptionLog.objects.create(
            feed_source=self.feed_source
        )
        
        # Call get_objects method
        objects, count = self.client.get_objects()
        
        # Verify mock was called correctly
        mock_collection.assert_called_once_with(
            f"{self.feed_source.api_root_url}collections/{self.feed_source.collection_id}/", # Corrected field name
            verify=settings.TAXII_VERIFY_SSL,
            headers=self.client.headers,
            auth=self.client.auth # Added auth parameter
        )
        
        # Check result
        self.assertEqual(count, 3)
        self.assertEqual(len(objects), 3)
        self.assertEqual(objects[0]['id'], 'indicator--1')
        self.assertEqual(objects[1]['id'], 'indicator--2')
        self.assertEqual(objects[2]['id'], 'malware--1')
        
        # Check that log entry was updated
        self.client.log_entry.refresh_from_db()
        self.assertEqual(self.client.log_entry.objects_retrieved, 3)
    
    @mock.patch('feed_consumption.taxii_client_service.Collection') # Corrected patch path
    def test_get_objects_with_filters(self, mock_collection):
        """Test object retrieval with filters."""
        # Set up the feed source with API root and collection ID
        self.feed_source.api_root_url = 'https://example.com/taxii2/api1/' # Corrected field name
        self.feed_source.collection_id = 'collection-1'
        self.feed_source.save()
        
        # Configure mock
        mock_collection_instance = mock.MagicMock()
        
        # Mock the get_objects generator
        def mock_get_objects(**kwargs):
            # Check that filter parameters were passed correctly
            self.assertEqual(kwargs['added_after'], datetime(2022, 1, 1))
            self.assertEqual(kwargs['type'], ['indicator', 'malware'])
            
            yield {
                'objects': [
                    {'type': 'indicator', 'id': 'indicator--1', 'spec_version': '2.1'}
                ]
            }
        
        mock_collection_instance.get_objects = mock_get_objects
        mock_collection.return_value = mock_collection_instance
        
        # Call get_objects method with filters
        objects, count = self.client.get_objects(
            added_after=datetime(2022, 1, 1),
            types=['indicator', 'malware']
        )
        
        # Check result
        self.assertEqual(count, 1)
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0]['id'], 'indicator--1')
    
    @mock.patch('feed_consumption.taxii_client_service.Collection') # Corrected patch path
    def test_get_objects_max_limit(self, mock_collection):
        """Test object retrieval with maximum limit."""
        # Set up the feed source with API root and collection ID
        self.feed_source.api_root_url = 'https://example.com/taxii2/api1/' # Corrected field name
        self.feed_source.collection_id = 'collection-1'
        self.feed_source.save()
        
        # Configure mock
        mock_collection_instance = mock.MagicMock()
        
        # Mock the get_objects generator to return more objects than the limit
        def mock_get_objects(**kwargs):
            yield {
                'objects': [{'type': 'indicator', 'id': f'indicator--{i}', 'spec_version': '2.1'} for i in range(10)]
            }
            
            yield {
                'objects': [{'type': 'indicator', 'id': f'indicator--{i+10}', 'spec_version': '2.1'} for i in range(10)]
            }
        
        mock_collection_instance.get_objects = mock_get_objects
        mock_collection.return_value = mock_collection_instance
        
        # Call get_objects method with a max limit
        objects, count = self.client.get_objects(max_objects=15)
        
        # Check result
        self.assertEqual(count, 15)  # Should be limited to 15
        self.assertEqual(len(objects), 15)
        self.assertEqual(objects[0]['id'], 'indicator--0')
        self.assertEqual(objects[14]['id'], 'indicator--14')
    
    @mock.patch('feed_consumption.taxii_client_service.Collection') # Corrected patch path
    def test_get_objects_error(self, mock_collection):
        """Test object retrieval with error."""
        # Set up the feed source with API root and collection ID
        self.feed_source.api_root_url = 'https://example.com/taxii2/api1/' # Corrected field name
        self.feed_source.collection_id = 'collection-1'
        self.feed_source.save()
        
        # Configure mock to raise exception
        mock_collection.side_effect = TAXIIServiceException('Object retrieval failed')
        
        # Create a log entry for the client
        self.client.log_entry = FeedConsumptionLog.objects.create(
            feed_source=self.feed_source
        )
        
        # Call get_objects method and check exception
        with self.assertRaises(TaxiiClientError):
            self.client.get_objects()
        
        # Check that log entry was updated with error
        self.client.log_entry.refresh_from_db()
        self.assertIn('Object retrieval failed', self.client.log_entry.error_message)
    
    @mock.patch('feed_consumption.taxii_client_service.TaxiiClient.get_objects') # Corrected patch path
    def test_consume_feed_success(self, mock_get_objects):
        """Test successful feed consumption."""
        # Configure mock
        mock_objects = [
            {'type': 'indicator', 'id': 'indicator--1', 'spec_version': '2.1'},
            {'type': 'malware', 'id': 'malware--1', 'spec_version': '2.1'}
        ]
        mock_get_objects.return_value = (mock_objects, 2)
        
        # Call consume_feed method
        result = self.client.consume_feed()
        
        # Verify get_objects was called
        mock_get_objects.assert_called_once()
        
        # Check result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['feed_source'], self.feed_source.name)
        self.assertEqual(result['objects_retrieved'], 2)
        self.assertIsNotNone(result['poll_time'])
        
        # Check that log entry was created and updated
        log_entry = self.client.log_entry
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.feed_source, self.feed_source)
        self.assertEqual(log_entry.status, FeedConsumptionLog.ConsumptionStatus.SUCCESS)
        self.assertEqual(log_entry.objects_retrieved, 2)
        self.assertEqual(log_entry.objects_processed, 2)
        self.assertIsNotNone(log_entry.end_time)
        
        # Check that feed source last_poll_time was updated
        self.feed_source.refresh_from_db()
        self.assertIsNotNone(self.feed_source.last_poll_time)
    
    @mock.patch('feed_consumption.taxii_client_service.TaxiiClient.get_objects') # Corrected patch path
    def test_consume_feed_error(self, mock_get_objects):
        """Test feed consumption with error."""
        # Configure mock to raise exception
        mock_get_objects.side_effect = TaxiiClientError('Feed consumption failed')
        
        # Call consume_feed method and check exception
        with self.assertRaises(TaxiiClientError):
            self.client.consume_feed()
        
        # Check that log entry was created and updated with error
        log_entry = self.client.log_entry
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.feed_source, self.feed_source)
        self.assertEqual(log_entry.status, FeedConsumptionLog.ConsumptionStatus.FAILURE)
        self.assertIn('Feed consumption failed', log_entry.error_message)
    
    def test_with_retry_success(self):
        """Test retry mechanism with successful function."""
        # Define a function that succeeds
        def success_func():
            return "success"
        
        # Call _with_retry
        result = self.client._with_retry(success_func)
        
        # Check result
        self.assertEqual(result, "success")
    
    @mock.patch('time.sleep')
    def test_with_retry_temporary_failure(self, mock_sleep):
        """Test retry mechanism with temporary failure."""
        # Define a counter to track attempts
        attempts = [0]
        
        # Define a function that fails twice then succeeds
        def temporary_failure():
            attempts[0] += 1
            if attempts[0] < 3:
                raise RequestException("Temporary failure")
            return "success after retry"
        
        # Call _with_retry
        result = self.client._with_retry(temporary_failure, max_attempts=3)
        
        # Check result
        self.assertEqual(result, "success after retry")
        self.assertEqual(attempts[0], 3)
        self.assertEqual(mock_sleep.call_count, 2)
    
    @mock.patch('time.sleep')
    def test_with_retry_permanent_failure(self, mock_sleep):
        """Test retry mechanism with permanent failure."""
        # Define a function that always fails
        def permanent_failure():
            raise RequestException("Permanent failure")
        
        # Create a log entry for the client
        self.client.log_entry = FeedConsumptionLog.objects.create(
            feed_source=self.feed_source
        )
        
        # Call _with_retry and check exception
        with self.assertRaises(TaxiiClientError):
            self.client._with_retry(permanent_failure, max_attempts=3)
        
        # Check that all retries were attempted
        self.assertEqual(mock_sleep.call_count, 2)
        
        # Check that log entry was updated with error
        self.client.log_entry.refresh_from_db()
        self.assertIn('Permanent failure', self.client.log_entry.error_message)
    
    @mock.patch('time.sleep')
    def test_with_retry_connection_error(self, mock_sleep):
        """Test retry mechanism with connection error."""
        # Define a function that raises ConnectionError
        def connection_error():
            raise ConnectionError("Connection error")
        
        # Call _with_retry and check exception
        with self.assertRaises(TaxiiConnectionError):
            self.client._with_retry(connection_error, max_attempts=2)
    
    @mock.patch('time.sleep')
    def test_with_retry_timeout(self, mock_sleep):
        """Test retry mechanism with timeout."""
        # Define a function that raises Timeout
        def timeout_error():
            raise Timeout("Timeout error")
        
        # Call _with_retry and check exception
        with self.assertRaises(TaxiiConnectionError):
            self.client._with_retry(timeout_error, max_attempts=2)
    
    @mock.patch('time.sleep')
    def test_with_retry_auth_error(self, mock_sleep):
        """Test retry mechanism with authentication error."""
        # Define a function that raises 401 error
        def auth_error():
            response = mock.MagicMock()
            response.status_code = 401
            exception = RequestException("Auth failed")
            exception.response = response
            raise exception
        
        # Call _with_retry and check exception
        with self.assertRaises(TaxiiAuthenticationError):
            self.client._with_retry(auth_error, max_attempts=2)
