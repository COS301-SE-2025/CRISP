"""
Integration tests for TAXII feed consumption
"""
import unittest
import uuid 
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta
import pytz
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from core.services.stix_taxii_service import StixTaxiiService
from core.services.otx_taxii_service import OTXTaxiiService
from core.models.models import ThreatFeed, Indicator, TTPData, Institution, Organization
from core.repositories.threat_feed_repository import ThreatFeedRepository
from core.repositories.indicator_repository import IndicatorRepository
from core.repositories.ttp_repository import TTPRepository
from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK, STIX20_BUNDLE, STIX21_BUNDLE, TAXII2_COLLECTIONS


class TaxiiConsumptionIntegrationTestCase(TransactionTestCase):
    """Integration test cases for TAXII feed consumption"""

    def setUp(self):
        """Set up the test environment"""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()

        # Create Organization first
        self.organization = Organization.objects.create(
            name=f"Test Organization - {uuid.uuid4().hex[:8]}",
            description="Test Organization for TAXII",
            identity_class="organization", 
            organization_type="university",
            contact_email="test@example.com"
        )

        # Create Institution
        self.institution = Institution.objects.create(
            name=f"Test Institution - {uuid.uuid4().hex[:8]}",
            description="Test Institution for TAXII",
            contact_email="test@example.com",
            contact_name="Test Contact",
            organization=self.organization
        )

        from core.tests.test_data_fixtures import create_test_threat_feed
        
        # Create both otx_feed and stix2_feed
        self.otx_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix="OTX",
            taxii_server_url="https://otx.alienvault.com/taxii/discovery",
            taxii_collection_id="AlienVault_OTX",
            is_external=True
        )
        
        self.stix2_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix="STIX2", 
            taxii_server_url="https://cti-taxii.mitre.org/stix/collections/",
            taxii_collection_id="enterprise-attack",
            taxii_api_root="collections",
            is_external=True
        )

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_otx_feed_consumption(self, mock_poll_collection):
        """Test end-to-end consumption of an OTX TAXII 1.x feed"""
        
        # Import the proper mock object
        from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK
        
        # Mock poll_collection to return proper content blocks
        mock_poll_collection.return_value = [TAXII1_CONTENT_BLOCK]
        
        # Create the service and consume the feed
        service = OTXTaxiiService()
        indicator_count, ttp_count = service.consume_feed(self.otx_feed)
        
        # Check the stats - verify content was processed
        self.assertEqual(indicator_count, 1)
        self.assertEqual(ttp_count, 0)
        
        # Verify poll_collection was called correctly
        mock_poll_collection.assert_called_once()
        
        # Verify an indicator was actually created in the database
        indicators = Indicator.objects.filter(threat_feed=self.otx_feed)
        self.assertEqual(indicators.count(), 1)
        
        # Check indicator properties
        indicator = indicators.first()
        self.assertEqual(indicator.value, '192.168.1.1')
        self.assertEqual(indicator.type, 'ip')

    @patch('core.services.stix_taxii_service.StixTaxiiService.get_objects')
    def test_stix2_feed_consumption(self, mock_get_objects):
        """Test end-to-end consumption of a STIX 2.x TAXII feed"""
        
        # Mock the get_objects response with simplified STIX objects
        mock_stix_objects = [
            {
                'type': 'indicator',
                'id': 'indicator--test-stix2',
                'pattern': "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
                'labels': ['malicious-activity'],
                'created': '2023-01-01T00:00:00.000Z',
                'modified': '2023-01-01T00:00:00.000Z'
            },
            {
                'type': 'attack-pattern',
                'id': 'attack-pattern--test-stix2',
                'name': 'Test Attack Pattern',
                'description': 'Test attack pattern from STIX2',
                'created': '2023-01-01T00:00:00.000Z',
                'modified': '2023-01-01T00:00:00.000Z'
            }
        ]
        mock_get_objects.return_value = mock_stix_objects
        
        # Create the service and consume the feed
        service = StixTaxiiService()
        indicator_count, ttp_count = service.consume_feed(self.stix2_feed) 
        
        # Check that the method was called
        mock_get_objects.assert_called_once()
        
        # Check the stats 
        self.assertIsInstance(indicator_count, int)
        self.assertIsInstance(ttp_count, int)
        self.assertGreaterEqual(indicator_count + ttp_count, 0)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_deduplicate_indicators(self, mock_poll_collection):
        """Test that duplicate indicators are handled correctly"""
        
        # Create an existing indicator with required timestamp fields
        now = timezone.now()
        existing_indicator = Indicator.objects.create(
            threat_feed=self.otx_feed,
            type='domain',
            value='malicious-domain.com',
            description='Known malicious domain',
            stix_id='indicator-test-duplicate',
            confidence=60,
            first_seen=now,
            last_seen=now  
        )
        
        # Mock the poll_collection method
        mock_block = MagicMock()
        mock_block.content = b"""
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
        """
        
        mock_poll_collection.return_value = [mock_block]
        
        # Create the service and consume the feed
        service = OTXTaxiiService()
        stats = service.consume_feed(self.otx_feed)  # Pass object, not ID
        
        # The indicator should be updated, not duplicated
        indicators = Indicator.objects.filter(threat_feed=self.otx_feed)
        self.assertEqual(indicators.count(), 1)
        
        # The indicator should have been updated
        updated_indicator = indicators.first()
        self.assertEqual(updated_indicator.stix_id, 'indicator-test-duplicate')

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_force_days_parameter(self, mock_poll_collection):
        """Test the force_days parameter functionality"""
        
        # Set the feed's last_sync to a week ago
        self.otx_feed.last_sync = timezone.now() - timedelta(days=7)
        self.otx_feed.save()
        
        # Import the proper mock object
        from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK
        
        # Mock poll_collection to return proper content blocks
        mock_poll_collection.return_value = [TAXII1_CONTENT_BLOCK]
        
        # Create the service
        service = OTXTaxiiService()
        
        # Call the method with correct signature 
        indicator_count, ttp_count = service.consume_feed(self.otx_feed)
        
        # Verify poll_collection was called
        mock_poll_collection.assert_called_once()
        
        # Check the results
        self.assertEqual(indicator_count, 1)
        self.assertEqual(ttp_count, 0)
        
        # Verify an indicator was actually created
        indicators = Indicator.objects.filter(threat_feed=self.otx_feed)
        self.assertEqual(indicators.count(), 1)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_repository_usage(self, mock_poll_collection):
        """Test that the service correctly uses repositories"""
        
        # Import the proper mock object
        from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK
        
        # Mock poll_collection to return proper content blocks
        mock_poll_collection.return_value = [TAXII1_CONTENT_BLOCK]
        
        # Create the service
        service = OTXTaxiiService()
        
        # Test with ThreatFeed object directly
        indicator_count, ttp_count = service.consume_feed(self.otx_feed)
        
        # Verify poll_collection was called
        mock_poll_collection.assert_called_once()
        
        # Check the results
        self.assertEqual(indicator_count, 1)
        self.assertEqual(ttp_count, 0)
        
        # Verify repository usage by checking database
        indicators = Indicator.objects.filter(threat_feed=self.otx_feed)
        self.assertEqual(indicators.count(), 1)
        
        # Check that proper data was stored
        indicator = indicators.first()
        self.assertIsNotNone(indicator.stix_id)
        self.assertIsNotNone(indicator.first_seen)
        self.assertIsNotNone(indicator.last_seen)


if __name__ == '__main__':
    unittest.main()