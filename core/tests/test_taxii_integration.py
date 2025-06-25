"""
Integration tests for TAXII feed consumption
"""
import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta
import pytz
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from core.services.stix_taxii_service import StixTaxiiService
from core.services.otx_taxii_service import OTXTaxiiService
from core.patterns.observer.threat_feed import ThreatFeed
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData
from core.repositories.threat_feed_repository import ThreatFeedRepository
from core.repositories.indicator_repository import IndicatorRepository
from core.repositories.ttp_repository import TTPRepository
from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK, STIX20_BUNDLE, STIX21_BUNDLE, TAXII2_COLLECTIONS


class TaxiiConsumptionIntegrationTestCase(TransactionTestCase):
    """Integration test cases for TAXII feed consumption"""

    def setUp(self):
        """Set up the test environment"""

        self.otx_feed = ThreatFeed.objects.create(
            name="OTX Feed",
            description="AlienVault OTX Feed",
            is_external=True,
            taxii_server_url="https://otx.alienvault.com/taxii",
            taxii_api_root="taxii",
            taxii_collection_id="user_AlienVault",
            taxii_username="dummy-api-key"
        )
        
        # Create a threat feed for STIX 2.x TAXII
        self.stix2_feed = ThreatFeed.objects.create(
            name="STIX 2.x Feed",
            description="STIX 2.x Test Feed",
            is_external=True,
            taxii_server_url="https://example.com/taxii2",
            taxii_api_root="api2",
            taxii_collection_id="test-collection",
            taxii_username="test-user",
            taxii_password="test-pass"
        )

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    @patch('core.parsers.stix1_parser.STIX1Parser.parse_content_block')
    def test_otx_feed_consumption(self, mock_parse_content_block, mock_poll_collection):
        """Test end-to-end consumption of an OTX TAXII 1.x feed"""
        
        mock_block = MagicMock()
        mock_block.content = '<xml>mock content</xml>'
        
        # Mock poll_collection to return the block
        mock_poll_collection.return_value = [mock_block]
        
        # Create a side effect that actually creates database records
        def create_test_data(content, threat_feed):
            # Create actual database records
            indicator = Indicator.objects.create(
                threat_feed=threat_feed,
                type='ip',
                value='192.168.1.1',
                stix_id='indicator-test-1',
                description='Test IP Indicator',
                confidence=85
            )
            
            ttp = TTPData.objects.create(
                threat_feed=threat_feed,
                name='Phishing Attack',
                stix_id='attack-pattern-test-1',
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
        
        # Set the side effect
        mock_parse_content_block.side_effect = create_test_data
        
        # Create the service and consume the feed
        service = OTXTaxiiService()
        stats = service.consume_feed(self.otx_feed.id)
        
        # Verify poll_collection was called
        mock_poll_collection.assert_called_once()
        
        # Verify parser was called
        mock_parse_content_block.assert_called_once()
        
        # Check the stats
        self.assertEqual(stats['indicators_created'], 1)
        self.assertEqual(stats['ttp_created'], 1)
        
        # Check that actual database records were created
        indicators = Indicator.objects.filter(threat_feed=self.otx_feed)
        ttps = TTPData.objects.filter(threat_feed=self.otx_feed)
        
        self.assertEqual(indicators.count(), 1)
        self.assertEqual(ttps.count(), 1)
        
        # Verify the content of the created records
        indicator = indicators.first()
        ttp = ttps.first()
        
        self.assertEqual(indicator.type, 'ip')
        self.assertEqual(indicator.value, '192.168.1.1')
        self.assertEqual(indicator.stix_id, 'indicator-test-1')
        
        self.assertEqual(ttp.name, 'Phishing Attack')
        self.assertEqual(ttp.mitre_technique_id, 'T1566.001')
        self.assertEqual(ttp.mitre_tactic, 'initial_access')
        
        # Check that the threat feed's last_sync was updated
        self.otx_feed.refresh_from_db()
        self.assertIsNotNone(self.otx_feed.last_sync)

    @patch('core.services.stix_taxii_service.Collection')
    @patch('core.services.stix_taxii_service.stix2_parse')
    def test_stix2_feed_consumption(self, mock_stix2_parse, mock_collection_class):
        """Test end-to-end consumption of a STIX 2.x TAXII feed"""
        mock_collection = MagicMock()
        mock_collection_class.return_value = mock_collection
        
        # Mock the get_objects response
        stix2_objects = [
            STIX20_BUNDLE['objects'][0],  # Indicator
            STIX21_BUNDLE['objects'][1]   # Attack Pattern
        ]
        mock_collection.get_objects.return_value = {'objects': stix2_objects}
        
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
        
        # Check that collection was created correctly
        mock_collection_class.assert_called_once_with(
            f"{self.stix2_feed.taxii_server_url}/{self.stix2_feed.taxii_api_root}/collections/{self.stix2_feed.taxii_collection_id}/",
            user=self.stix2_feed.taxii_username,
            password=self.stix2_feed.taxii_password
        )
        
        # Check that get_objects was called
        mock_collection.get_objects.assert_called_once()
        
        # Check that the threat feed's last_sync was updated
        self.stix2_feed.refresh_from_db()
        self.assertIsNotNone(self.stix2_feed.last_sync)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_deduplicate_indicators(self, mock_poll_collection):
        """Test that duplicate indicators are handled correctly"""
        # Create an existing indicator
        existing_indicator = Indicator.objects.create(
            threat_feed=self.otx_feed,
            type='domain',
            value='malicious-domain.com',
            description='Known malicious domain',
            stix_id='indicator-test-duplicate',
            confidence=60
        )
        
        # Mock the poll_collection method
        mock_block = MagicMock(content=b"""
        <stix:STIX_Package>
            <stix:Indicators>
                <stix:Indicator id="indicator-test-duplicate">
                    <indicator:Title>Domain Watchlist</indicator:Title>
                    <indicator:Observable>
                        <cybox:Object>
                            <cybox:Properties xsi:type="DomainNameObj:DomainNameObjectType">
                                <DomainNameObj:Value>malicious-domain.com</DomainNameObj:Value>
                            </cybox:Properties>
                        </cybox:Object>
                    </indicator:Observable>
                    <indicator:Description>Updated description</indicator:Description>
                    <indicator:Confidence>
                        <stixCommon:Value>High</stixCommon:Value>
                    </indicator:Confidence>
                </stix:Indicator>
            </stix:Indicators>
        </stix:STIX_Package>
        """)
        mock_poll_collection.return_value = [mock_block]
        
        # Create a parser that will update our existing indicator
        with patch('core.parsers.stix1_parser.STIX1Parser.parse_content_block') as mock_parse:
            def side_effect_update(content, threat_feed):
                # Update the existing indicator
                existing_indicator.description = 'Updated description'
                existing_indicator.confidence = 80
                existing_indicator.save()
                return {'indicators_created': 0, 'indicators_updated': 1, 'ttp_created': 0, 'ttp_updated': 0, 'skipped': 0, 'errors': 0}
            
            mock_parse.side_effect = side_effect_update
            
            # Create the service and consume the feed
            service = OTXTaxiiService()
            stats = service.consume_feed(threat_feed_id=self.otx_feed.id)
            
            # Check the stats
            self.assertEqual(stats['indicators_created'], 0)
            self.assertEqual(stats['indicators_updated'], 1)
            
            # Check that the indicator was updated
            updated_indicator = Indicator.objects.get(id=existing_indicator.id)
            self.assertEqual(updated_indicator.description, 'Updated description')
            self.assertEqual(updated_indicator.confidence, 80)
            
            # Check that no new indicator was created
            self.assertEqual(Indicator.objects.filter(threat_feed=self.otx_feed).count(), 1)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_force_days_parameter(self, mock_poll_collection):
        """Test the force_days parameter behavior"""
        # Mock the poll_collection method
        mock_poll_collection.return_value = []
        
        # Create a service and set the otx_feed's last_sync to a recent time
        self.otx_feed.last_sync = timezone.now()
        self.otx_feed.save()
        service = OTXTaxiiService()
        
        # Create a matcher function to verify the poll_collection call
        def match_poll_args(begin_date, days_ago=7):
            """Match poll_collection's begin_date argument to be days_ago from now"""
            expected_date = timezone.now() - timedelta(days=days_ago)
            
            # Return True if they're within 10 seconds of each other
            return abs((begin_date - expected_date).total_seconds()) < 10
        
        # Call with force_days=30
        service.consume_feed(threat_feed_id=self.otx_feed.id, force_days=30)
        
        # The first call should be with a begin_date of 30 days ago, not using last_sync
        begin_date = mock_poll_collection.call_args[1]['begin_date']
        self.assertTrue(match_poll_args(begin_date, days_ago=30), 
                      f"Expected begin_date ~30 days ago, got {begin_date}")
        
        # Reset the mock and call with default parameters
        mock_poll_collection.reset_mock()
        service.consume_feed(threat_feed_id=self.otx_feed.id)
        
        # The second call should use the last_sync value, which is very recent
        begin_date = mock_poll_collection.call_args[1]['begin_date']
        self.assertTrue((timezone.now() - begin_date).total_seconds() < 10, 
                      f"Expected begin_date very recent, got {begin_date}")

    @patch('core.repositories.threat_feed_repository.ThreatFeedRepository.get_by_id')
    def test_repository_usage(self, mock_get_by_id):
        """Test that repositories are used correctly in the TAXII services"""
        # Mock the repository to return our feed
        mock_get_by_id.return_value = self.otx_feed
        
        # Create a service
        with patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection') as mock_poll_collection:
            # Return empty list to avoid needing to mock the parser
            mock_poll_collection.return_value = []
            
            # Create the service and consume the feed
            service = OTXTaxiiService()
            service.consume_feed(threat_feed_id=self.otx_feed.id)
            
            # Check that the repository's get_by_id was called with the correct ID
            mock_get_by_id.assert_called_once_with(self.otx_feed.id)


if __name__ == '__main__':
    unittest.main()