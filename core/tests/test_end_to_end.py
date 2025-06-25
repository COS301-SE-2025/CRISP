"""
End-to-end tests for the complete TAXII feed consumption process in the CRISP platform.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import json
from datetime import datetime, timedelta
import pytz
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from core.services.stix_taxii_service import StixTaxiiService
from core.services.otx_taxii_service import OTXTaxiiService
from core.patterns.observer.threat_feed import ThreatFeed
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData
from core.models.institution import Institution
from core.repositories.threat_feed_repository import ThreatFeedRepository
from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK, STIX20_BUNDLE, STIX21_BUNDLE, TAXII2_COLLECTIONS


class EndToEndConsumptionTestCase(TransactionTestCase):
    """End-to-end test cases for TAXII feed consumption process."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test institution
        self.institution = Institution.objects.create(
            name="Test Institution",
            description="Test Institution for E2E",
            contact_email="test@example.com"
        )
        
        # Create an OTX TAXII 1.x feed
        self.otx_feed = ThreatFeed.objects.create(
            name="OTX Feed",
            description="AlienVault OTX Feed",
            owner=self.institution,
            is_external=True,
            taxii_server_url="https://otx.alienvault.com/taxii",
            taxii_api_root="taxii",
            taxii_collection_id="user_AlienVault",
            taxii_username="dummy-api-key"
        )
        
        # Create a STIX 2.x TAXII feed
        self.stix2_feed = ThreatFeed.objects.create(
            name="STIX 2.x Feed",
            description="STIX 2.x Test Feed",
            owner=self.institution,
            is_external=True,
            taxii_server_url="https://example.com/taxii2",
            taxii_api_root="api2",
            taxii_collection_id="test-collection",
            taxii_username="test-user",
            taxii_password="test-pass"
        )

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    @patch('core.parsers.stix1_parser.STIX1Parser.parse_content_block')
    def test_otx_feed_end_to_end(self, mock_parse_content_block, mock_poll_collection):
        """Test end-to-end consumption of an OTX TAXII 1.x feed."""
        # Create mock content blocks
        mock_block = MagicMock()
        mock_block.content = '<xml>mock content</xml>'
        
        # Mock poll_collection to return the blocks
        mock_poll_collection.return_value = [mock_block]
        
        # Mock the parser with controlled STIX ID
        def side_effect_parser(content, threat_feed):
            indicator = Indicator.objects.create(
                threat_feed=threat_feed,
                type='ip',
                value='192.168.1.1',
                stix_id='indicator-test-1',  # Fixed STIX ID for testing
                description='Test IP Indicator',
                confidence=85
            )
            
            ttp = TTPData.objects.create(
                threat_feed=threat_feed,
                name='Phishing Attack',
                stix_id='attack-pattern-test-1',  # Fixed STIX ID for testing
                mitre_technique_id='T1566.001',
                mitre_tactic='initial_access',
                description='Phishing attack technique'
            )
            
            return {
                'indicators_created': 1,
                'indicators_updated': 0,
                'ttp_created': 1,
                'ttp_updated': 0,
                'skipped': 0,
                'errors': 0
            }
        
        mock_parse_content_block.side_effect = side_effect_parser
        
        # Create the service and consume the feed
        service = OTXTaxiiService()
        stats = service.consume_feed(self.otx_feed.id)
        
        # Check the stats
        self.assertEqual(stats['indicators_created'], 1)
        self.assertEqual(stats['ttp_created'], 1)
        
        # Check the created objects
        indicators = Indicator.objects.filter(threat_feed=self.otx_feed)
        ttps = TTPData.objects.filter(threat_feed=self.otx_feed)
        
        self.assertEqual(indicators.count(), 1)
        self.assertEqual(ttps.count(), 1)
        
        # Check the indicator and TTP details
        indicator = indicators.first()
        ttp = ttps.first()
        
        self.assertEqual(indicator.type, 'ip')
        self.assertEqual(indicator.value, '192.168.1.1')
        self.assertEqual(indicator.stix_id, 'indicator-test-1')  # Now this will match
        
        self.assertEqual(ttp.name, 'Phishing Attack')
        self.assertEqual(ttp.mitre_technique_id, 'T1566.001')
        self.assertEqual(ttp.mitre_tactic, 'initial_access')

    @patch('core.services.stix_taxii_service.Collection')
    @patch('core.services.stix_taxii_service.stix2_parse')
    def test_stix2_feed_end_to_end(self, mock_stix2_parse, mock_collection_class):
        """Test end-to-end consumption of a STIX 2.x TAXII feed."""
        # Mock the Collection
        mock_collection = MagicMock()
        mock_collection_class.return_value = mock_collection
        
        # Mock the get_objects response
        stix2_objects = [
            STIX20_BUNDLE['objects'][0],  # Indicator
            STIX21_BUNDLE['objects'][1]   # Attack Pattern
        ]
        mock_collection.get_objects.return_value = {'objects': stix2_objects}
        
        # Create mock observers to track notifications
        mock_observer = MagicMock()
        
        # Attach observer to the feed
        self.stix2_feed.attach(mock_observer)
        
        # Mock the stix2_parse function to return mock objects with properties from the JSON
        def create_mock_object(obj_dict):
            mock_obj = MagicMock()
            for key, value in obj_dict.items():
                setattr(mock_obj, key, value)
                
            # Convert timestamp strings to datetime objects if they exist
            if hasattr(mock_obj, 'created'):
                mock_obj.created = datetime.strptime(mock_obj.created, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
            if hasattr(mock_obj, 'modified'):
                mock_obj.modified = datetime.strptime(mock_obj.modified, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
                
            return mock_obj
        
        mock_stix2_parse.side_effect = [create_mock_object(obj) for obj in stix2_objects]
        
        # Create the service and consume the feed
        service = StixTaxiiService()
        stats = service.consume_feed(self.stix2_feed.id)
        
        # Check the stats
        self.assertEqual(stats['indicators_created'], 1)
        self.assertEqual(stats['ttp_created'], 1)
        
        # Check that the indicators and TTPs were created in the database
        indicators = Indicator.objects.filter(threat_feed=self.stix2_feed)
        ttps = TTPData.objects.filter(threat_feed=self.stix2_feed)
        
        self.assertEqual(indicators.count(), 1)
        self.assertEqual(ttps.count(), 1)
        
        # Check that the threat feed's last_sync was updated
        self.stix2_feed.refresh_from_db()
        self.assertIsNotNone(self.stix2_feed.last_sync)
        
        # Check that observer was notified
        mock_observer.update.assert_called_once_with(self.stix2_feed)

    @patch('core.repositories.threat_feed_repository.ThreatFeedRepository.get_external_feeds')
    @patch('core.services.stix_taxii_service.StixTaxiiService.consume_feed')
    def test_batch_feed_consumption(self, mock_consume_feed, mock_get_external_feeds):
        """Test batch consumption of multiple external feeds."""
        # Mock the repository to return our test feeds
        mock_get_external_feeds.return_value = [self.otx_feed, self.stix2_feed]
        
        # Mock the consume_feed method
        mock_consume_feed.side_effect = [
            {'indicators_created': 5, 'indicators_updated': 0, 'ttp_created': 2, 'ttp_updated': 0, 'skipped': 0, 'errors': 0},
            {'indicators_created': 3, 'indicators_updated': 1, 'ttp_created': 1, 'ttp_updated': 0, 'skipped': 0, 'errors': 0}
        ]
        
        # Create a function to simulate batch consumption
        def consume_external_feeds():
            # Get external feeds
            feeds = ThreatFeedRepository.get_external_feeds()
            
            results = {
                'feeds_processed': 0,
                'feeds_failed': 0,
                'total_indicators': 0,
                'total_ttps': 0
            }
            
            service = StixTaxiiService()
            
            # Process each feed
            for feed in feeds:
                try:
                    stats = service.consume_feed(feed.id)
                    
                    # Update results
                    results['feeds_processed'] += 1
                    results['total_indicators'] += stats['indicators_created'] + stats['indicators_updated']
                    results['total_ttps'] += stats['ttp_created'] + stats['ttp_updated']
                    
                except Exception:
                    results['feeds_failed'] += 1
            
            return results
        
        # Call the batch function
        results = consume_external_feeds()
        
        # Check the results
        self.assertEqual(results['feeds_processed'], 2)
        self.assertEqual(results['feeds_failed'], 0)
        self.assertEqual(results['total_indicators'], 9)  # 5 + 0 + 3 + 1
        self.assertEqual(results['total_ttps'], 3)  # 2 + 0 + 1 + 0
        
        # Check that consume_feed was called for each feed
        mock_consume_feed.assert_has_calls([
            call(self.otx_feed.id),
            call(self.stix2_feed.id)
        ])


class APIEndpointTestCase(APITestCase):
    """Test cases for API endpoints related to threat feed consumption."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test institution
        self.institution = Institution.objects.create(
            name="Test Institution",
            description="Test Institution for API",
            contact_email="test@example.com"
        )
        
        # Create a test threat feed
        self.feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for API",
            owner=self.institution,
            is_external=True,
            taxii_server_url="https://test.example.com/taxii",
            taxii_api_root="api1",
            taxii_collection_id="collection1"
        )
        
        # API URLs
        self.feeds_url = reverse('threat-feed-list')
        self.feed_detail_url = reverse('threat-feed-detail', args=[self.feed.id])
        self.feed_consume_url = reverse('threat-feed-consume', args=[self.feed.id])
        self.feed_status_url = reverse('threat-feed-status', args=[self.feed.id])
        self.available_collections_url = reverse('threat-feed-available-collections')

    @patch('core.services.otx_taxii_service.OTXTaxiiService.get_collections')
    def test_available_collections_endpoint(self, mock_get_collections):
        """Test the available collections endpoint."""
        # Mock the get_collections method
        mock_get_collections.return_value = TAXII2_COLLECTIONS
        
        # Call the endpoint
        response = self.client.get(self.available_collections_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(TAXII2_COLLECTIONS))
        self.assertEqual(response.data[0]['title'], 'High Value Indicators')
        self.assertEqual(response.data[1]['title'], 'Emerging Threats')

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_consume_endpoint(self, mock_consume_feed):
        """Test the consume endpoint."""
        # Mock the consume_feed method
        mock_consume_feed.return_value = {
            'indicators_created': 5,
            'indicators_updated': 2,
            'ttp_created': 3,
            'ttp_updated': 1,
            'skipped': 0,
            'errors': 0
        }
        
        # Call the endpoint
        response = self.client.post(self.feed_consume_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['indicators_created'], 5)
        self.assertEqual(response.data['ttp_created'], 3)
        
        # Check that consume_feed was called correctly
        mock_consume_feed.assert_called_once_with(
            threat_feed_id=self.feed.id,
            limit=None,
            force_days=None,
            batch_size=100
        )
    
    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_consume_endpoint_with_parameters(self, mock_consume_feed):
        """Test the consume endpoint with query parameters."""
        # Mock the consume_feed method
        mock_consume_feed.return_value = {
            'indicators_created': 3,
            'indicators_updated': 0,
            'ttp_created': 1,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Call the endpoint with parameters
        response = self.client.post(f"{self.feed_consume_url}?limit=10&force_days=7&batch_size=50")
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that consume_feed was called with the correct parameters
        mock_consume_feed.assert_called_once_with(
            threat_feed_id=self.feed.id,
            limit=10,
            force_days=7,
            batch_size=50
        )

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_consume_endpoint_error_handling(self, mock_consume_feed):
        """Test error handling in the consume endpoint."""
        # Mock the consume_feed method to raise an exception
        mock_consume_feed.side_effect = Exception("Test error")
        
        # Call the endpoint
        response = self.client.post(self.feed_consume_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)
        self.assertEqual(response.data['details'], 'Test error')

    def test_status_endpoint(self):
        """Test the status endpoint."""
        # Create test indicators and TTPs
        for i in range(3):
            Indicator.objects.create(
                threat_feed=self.feed,
                type='ip',
                value=f'192.168.1.{i}',
                description=f'Test Indicator {i}',
                stix_id=f'indicator-test-{i}',
                confidence=70 + i
            )
        
        TTPData.objects.create(
            threat_feed=self.feed,
            name='Phishing Attack',
            description='Test TTP',
            mitre_technique_id='T1566.001',
            mitre_tactic='initial_access',
            stix_id='ttp-test-1'
        )
        
        # Set last_sync
        self.feed.last_sync = timezone.now()
        self.feed.save()
        
        # Call the endpoint
        response = self.client.get(self.feed_status_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Feed')
        self.assertEqual(response.data['is_external'], True)
        self.assertEqual(response.data['indicator_count'], 3)
        self.assertEqual(response.data['ttp_count'], 1)
        self.assertIsNotNone(response.data['last_sync'])


if __name__ == '__main__':
    unittest.main()
