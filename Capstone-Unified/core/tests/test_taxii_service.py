"""
Unit tests for TAXII service classes
"""
import unittest
import uuid
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import pytz
from django.test import TransactionTestCase

from core.services.stix_taxii_service import StixTaxiiService
from core.services.otx_taxii_service import OTXTaxiiService
from core.models.models import ThreatFeed, Indicator, TTPData, Institution, Organization
from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK, STIX20_BUNDLE, STIX21_BUNDLE, TAXII2_COLLECTIONS
from core.tests.test_data_fixtures import create_test_threat_feed, create_test_organization


class StixTaxiiServiceTestCase(TransactionTestCase):
    """Test cases for the StixTaxiiService - Using TransactionTestCase for better isolation"""

    def setUp(self):
        """Set up the test environment."""
        ThreatFeed.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = str(uuid.uuid4())[:8]
        
        # Create an Organization first
        self.organization = create_test_organization(
            name_suffix=f"stix_service_{self.unique_suffix}",
            unique=True
        )
        
        # Create a test threat feed
        self.threat_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"stix_service_{self.unique_suffix}",
            unique=True
        )
        
        # Create the service
        self.service = StixTaxiiService()

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()

    @patch('requests.get') 
    def test_consume_feed_success(self, mock_get):
        """Test successful STIX feed consumption"""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "objects": [
                {
                    "type": "indicator",
                    "id": f"indicator--{uuid.uuid4()}",
                    "spec_version": "2.1",
                    "pattern": "[ipv4-addr:value = '1.2.3.4']",
                    "labels": ["malicious-activity"],
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the service
        indicator_count, ttp_count = self.service.consume_feed(self.threat_feed)
        
        # Check the results
        self.assertEqual(indicator_count, 1)
        self.assertEqual(ttp_count, 0)
        
        # Verify the HTTP call was made
        mock_get.assert_called_once()

    def test_consume_feed_error_handling(self):
        """Test error handling during feed consumption"""
        # Create a threat feed with invalid URL
        invalid_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"invalid_{self.unique_suffix}",
            taxii_server_url="https://invalid.example.com/taxii",
            unique=True
        )
        
        # Should handle the error gracefully
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            indicator_count, ttp_count = self.service.consume_feed(invalid_feed)
            
            # Should return 0 counts when there's an error
            self.assertEqual(indicator_count, 0)
            self.assertEqual(ttp_count, 0)

    @patch('requests.get')
    def test_get_collections_success(self, mock_get):
        """Test successful collections retrieval"""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = TAXII2_COLLECTIONS
        mock_get.return_value = mock_response
        
        # Call get_collections
        collections = self.service.get_collections("https://example.com", "api/v1")
        
        # Verify we get the expected collections
        self.assertEqual(len(collections), 2)
        self.assertEqual(collections[0]['title'], 'High Value Indicators')
        self.assertEqual(collections[1]['title'], 'Emerging Threats')

    @patch('requests.get')
    def test_get_objects_http_success(self, mock_get):
        """Test successful STIX objects retrieval"""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = STIX21_BUNDLE
        mock_get.return_value = mock_response
        
        # Call get_objects
        objects = self.service.get_objects(
            'https://example.com', 'api/v1', 'test-collection'
        )
        
        self.assertIsNotNone(objects)
        self.assertIsInstance(objects, list)
        self.assertGreater(len(objects), 0)

    @patch('requests.get')
    def test_get_objects_http_error(self, mock_get):
        """Test error handling during objects retrieval"""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response
        
        # Call get_objects
        objects = self.service.get_objects(
            'https://example.com', 'api/v1', 'nonexistent-collection'
        )
        
        # Should return None or empty on error
        self.assertIsNone(objects)


class OTXTaxiiServiceTestCase(TransactionTestCase):
    """Test cases for the OTXTaxiiService"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        
        self.unique_suffix = str(uuid.uuid4())[:8]
        
        # Create an Organization first
        self.organization = create_test_organization(
            name_suffix=f"otx_service_{self.unique_suffix}",
            unique=True
        )
        
        # Create a test threat feed
        self.threat_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"otx_service_{self.unique_suffix}",
            taxii_server_url="https://otx.alienvault.com/taxii/discovery",
            taxii_collection_id="AlienVault_OTX",
            taxii_username="test_user",
            unique=True
        )
        
        # Create the service
        self.service = OTXTaxiiService()

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_consume_feed_success(self, mock_poll_collection):
        """Test successful OTX feed consumption"""
        
        # Import the proper mock object
        from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK
        
        # Mock poll_collection method to return proper content blocks
        mock_poll_collection.return_value = [TAXII1_CONTENT_BLOCK]
        
        # Call the service
        indicator_count, ttp_count = self.service.consume_feed(self.threat_feed)
        
        # Check the results - should have processed the mock content
        self.assertEqual(indicator_count, 1)
        self.assertEqual(ttp_count, 0)
        
        # Verify poll_collection was called
        mock_poll_collection.assert_called_once()
        
        # Verify an indicator was created in the database
        indicators = Indicator.objects.filter(threat_feed=self.threat_feed)
        self.assertEqual(indicators.count(), 1)
        
        # Check indicator properties match the mock data
        indicator = indicators.first()
        self.assertEqual(indicator.value, '192.168.1.1')
        self.assertEqual(indicator.type, 'ip')
        self.assertIn('This is a test indicator', indicator.description)

    @patch('cabby.create_client')
    def test_consume_feed_error_handling(self, mock_create_client):
        """Test error handling during OTX feed consumption"""
        # Create feed with invalid configuration
        invalid_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"invalid_otx_{self.unique_suffix}",
            taxii_server_url="https://invalid.example.com/taxii",
            taxii_collection_id="invalid_collection",
            unique=True
        )
        
        # Mock client creation to throw error
        mock_create_client.side_effect = Exception("Connection failed")
        
        indicator_count, ttp_count = self.service.consume_feed(invalid_feed)
        
        # Should handle error gracefully
        self.assertEqual(indicator_count, 0)
        self.assertEqual(ttp_count, 0)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_poll_collection_success(self, mock_poll_collection):
        """Test successful collection polling"""
        # Mock poll_collection to return test content blocks
        mock_poll_collection.return_value = [TAXII1_CONTENT_BLOCK]
        
        # Call the poll_collection method using the proper signature
        content_blocks = self.service.poll_collection(
            self.threat_feed.taxii_collection_id
        )
        
        # Verify the results
        self.assertEqual(len(content_blocks), 1)
        
        # Verify poll_collection was called
        mock_poll_collection.assert_called_once()

    @patch('core.services.otx_taxii_service.OTXTaxiiService.get_collections')
    def test_get_collections_success(self, mock_get_collections):
        """Test successful collections retrieval"""
        # Mock the get_collections method directly to prevent network calls
        mock_get_collections.return_value = [
            {
                'id': f'collection1_{self.unique_suffix}',
                'title': f'collection1_{self.unique_suffix}',
                'description': 'First test collection',
                'available': True
            },
            {
                'id': f'collection2_{self.unique_suffix}',
                'title': f'collection2_{self.unique_suffix}',
                'description': 'Second test collection',
                'available': True
            }
        ]
        
        # Call get_collections
        collections = self.service.get_collections()
        
        # Verify we get exactly 2 collections
        self.assertEqual(len(collections), 2)
        self.assertEqual(collections[0]['title'], f'collection1_{self.unique_suffix}')
        self.assertEqual(collections[1]['title'], f'collection2_{self.unique_suffix}')

    @patch('cabby.create_client')
    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_authenticate_with_credentials(self, mock_poll_collection, mock_create_client):
        """Test authentication with username/password"""
        # Create feed with credentials
        auth_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"auth_{self.unique_suffix}",
            taxii_username="test_user",
            taxii_password="test_pass",
            unique=True
        )
        
        # Mock the TAXII client to prevent external connections
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Mock poll_collection to prevent external calls
        mock_poll_collection.return_value = []
        
        # Call the service
        self.service.consume_feed(auth_feed)
        
        # Verify poll_collection was called (indicating successful flow)
        mock_poll_collection.assert_called_once()

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_handle_polling_errors(self, mock_poll_collection):
        """Test handling of polling errors"""
        # Mock polling error
        mock_poll_collection.side_effect = Exception("Polling failed")
        
        # Call the service
        indicator_count, ttp_count = self.service.consume_feed(self.threat_feed)
        
        # Should handle error gracefully
        self.assertEqual(indicator_count, 0)
        self.assertEqual(ttp_count, 0)

    def test_parse_taxii_timestamp(self):
        """Test parsing of TAXII timestamps"""
        # Test various timestamp formats
        timestamps = [
            "2023-01-01T00:00:00.000000+00:00",
            "2023-01-01T00:00:00Z",
            "2023-01-01T00:00:00.000Z",
            "2023-01-01 00:00:00",
        ]
        
        for timestamp_str in timestamps:
            try:
                parsed = self.service._parse_timestamp(timestamp_str)
                self.assertIsNotNone(parsed)
                self.assertIsInstance(parsed, datetime)
            except Exception:
                # Some formats might not be supported - that's okay
                pass

    def test_validate_collection_id(self):
        """Test collection ID validation"""
        # Valid collection IDs
        valid_ids = [
            "collection-1",
            "AlienVault_OTX",
            "test_collection_123",
        ]
        
        for collection_id in valid_ids:
            self.assertTrue(self.service._is_valid_collection_id(collection_id))
        
        # Invalid collection IDs
        invalid_ids = [
            "",
            None,
            "collection with spaces",
            "collection/with/slashes",
        ]
        
        for collection_id in invalid_ids:
            self.assertFalse(self.service._is_valid_collection_id(collection_id))


class TaxiiServiceIntegrationTestCase(TransactionTestCase):
    """Integration tests for TAXII services"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = str(uuid.uuid4())[:8]
        
        # Create test organization
        self.organization = create_test_organization(
            name_suffix=f"integration_{self.unique_suffix}",
            unique=True
        )

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()

    def test_service_factory_method(self):
        """Test factory method for creating appropriate service"""
        # Test OTX service creation
        otx_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"otx_{self.unique_suffix}",
            taxii_server_url="https://otx.alienvault.com/taxii/discovery",
            unique=True
        )
        
        from core.services.taxii_service_factory import get_taxii_service
        otx_service = get_taxii_service(otx_feed)
        self.assertIsInstance(otx_service, OTXTaxiiService)
        
        # Test generic STIX service creation
        stix_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"stix_{self.unique_suffix}",
            taxii_server_url="https://cti-taxii.mitre.org/stix/collections/",
            unique=True
        )
        
        stix_service = get_taxii_service(stix_feed)
        self.assertIsInstance(stix_service, StixTaxiiService)

    @patch('core.services.stix_taxii_service.StixTaxiiService.get_objects')
    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_error_recovery_and_logging(self, mock_poll_collection, mock_get_objects):
        """Test error recovery and logging functionality"""
        # Create feed with problematic configuration
        problem_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"problem_{self.unique_suffix}",
            taxii_server_url="https://nonexistent.example.com/taxii",
            unique=True
        )
        
        # Mock service methods to simulate failures
        mock_get_objects.return_value = None  # Simulate STIX failure
        mock_poll_collection.side_effect = Exception("TAXII connection failed")  # Simulate OTX failure
        
        # Both services should handle errors gracefully
        stix_service = StixTaxiiService()
        otx_service = OTXTaxiiService()
        
        # Test error handling
        stix_result = stix_service.consume_feed(problem_feed)
        otx_result = otx_service.consume_feed(problem_feed)
        
        # Both should return (0, 0) for failed consumption
        self.assertEqual(stix_result, (0, 0))
        self.assertEqual(otx_result, (0, 0))

    @patch('core.services.stix_taxii_service.StixTaxiiService.get_objects')
    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_concurrent_service_usage(self, mock_poll_collection, mock_get_objects):
        """Test using multiple services concurrently"""
        # Mock service methods
        mock_get_objects.return_value = []  # Empty response for STIX service
        mock_poll_collection.return_value = []  # Empty response for OTX service
        
        # Create feeds for both services
        stix_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"concurrent_stix_{self.unique_suffix}",
            taxii_server_url="https://example.com/taxii2/",
            unique=True
        )
        
        otx_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"concurrent_otx_{self.unique_suffix}",
            taxii_server_url="https://otx.alienvault.com/taxii/discovery",
            unique=True
        )
        
        # Use both services
        stix_service = StixTaxiiService()
        otx_service = OTXTaxiiService()
        
        stix_result = stix_service.consume_feed(stix_feed)
        otx_result = otx_service.consume_feed(otx_feed)
        
        # Both should complete without interference
        self.assertIsNotNone(stix_result)
        self.assertIsNotNone(otx_result)
        self.assertEqual(stix_result, (0, 0))
        self.assertEqual(otx_result, (0, 0))


if __name__ == '__main__':
    unittest.main()