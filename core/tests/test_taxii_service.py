"""
Unit tests for TAXII service functionality
"""
import os
import sys
import django

# Add the project root to Python path for standalone execution
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, project_root)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
    django.setup()

import unittest
from unittest.mock import patch, MagicMock, call
import json
from datetime import datetime, timedelta
import pytz
from django.test import TestCase
from django.utils import timezone

try:
    from ..services.stix_taxii_service import StixTaxiiService
except ImportError:
    # Fallback for standalone execution
    from core.services.stix_taxii_service import StixTaxiiService
try:
    from ..services.otx_taxii_service import OTXTaxiiService
except ImportError:
    # Fallback for standalone execution
    from core.services.otx_taxii_service import OTXTaxiiService
try:
    from ..models.threat_feed import ThreatFeed
except ImportError:
    # Fallback for standalone execution
    from core.models.threat_feed import ThreatFeed
try:
    from ..models.indicator import Indicator
except ImportError:
    # Fallback for standalone execution
    from core.models.indicator import Indicator
try:
    from ..models.ttp_data import TTPData
except ImportError:
    # Fallback for standalone execution
    from core.models.ttp_data import TTPData
try:
    from ..tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK, STIX20_BUNDLE, STIX21_BUNDLE, TAXII2_COLLECTIONS
except ImportError:
    # Fallback for standalone execution
    from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK, STIX20_BUNDLE, STIX21_BUNDLE, TAXII2_COLLECTIONS


class OTXTaxiiServiceTestCase(TestCase):
    """Test cases for the OTXTaxiiService"""

    def setUp(self):
        """Set up the test environment"""
        self.service = OTXTaxiiService()
        
        # Create a mock ThreatFeed for testing
        self.threat_feed = ThreatFeed.objects.create(
            name="OTX Feed",
            description="AlienVault OTX Feed",
            is_external=True,
            taxii_server_url="https://otx.alienvault.com/taxii",
            taxii_api_root="taxii",
            taxii_collection_id="user_AlienVault",
            taxii_username="dummy-api-key"
        )

    @patch('core.services.otx_taxii_service.create_client')
    def test_get_client(self, mock_create_client):
        """Test creating a TAXII client"""
        # Mock the client
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Get the client
        client = self.service.get_client()
        
        # Check that client was created and configured correctly
        mock_create_client.assert_called_once_with(
            discovery_path=self.service.discovery_url,
            use_https=True
        )
        mock_client.set_auth.assert_called_once_with(
            username=self.service.api_key,
            password='unused'
        )
        self.assertEqual(client, mock_client)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.get_client')
    def test_get_collections(self, mock_get_client):
        """Test retrieving TAXII collections"""
        # Mock the client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock collections
        mock_collection1 = MagicMock()
        mock_collection1.name = "User Collections"
        mock_collection1.description = "User defined collections"
        mock_collection1.available = True
        
        mock_collection2 = MagicMock()
        mock_collection2.name = "Emerging Threats"
        mock_collection2.description = "Emerging threat data"
        mock_collection2.available = True
        
        # Set up the mock client to return our collection objects
        mock_client.get_collections.return_value = [mock_collection1, mock_collection2]
        
        # Get collections
        collections = self.service.get_collections()
        
        # Check that collections were retrieved correctly
        mock_client.get_collections.assert_called_once_with(uri=self.service.collections_url)
        self.assertEqual(len(collections), 2)
        self.assertEqual(collections[0]['title'], "User Collections")
        self.assertEqual(collections[1]['title'], "Emerging Threats")

    @patch('core.services.otx_taxii_service.OTXTaxiiService.get_client')
    def test_poll_collection(self, mock_get_client):
        """Test polling a TAXII collection"""
        # Mock the client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock content blocks
        mock_block1 = MagicMock(content=TAXII1_CONTENT_BLOCK['content'])
        mock_block2 = MagicMock(content=b"<stix:STIX_Package>Test content 2</stix:STIX_Package>")
        mock_client.poll.return_value = [mock_block1, mock_block2]
        
        # Set up test parameters
        collection_name = "test_collection"
        begin_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        # Poll the collection
        blocks = self.service.poll_collection(collection_name, begin_date, end_date)
        
        # Check that poll was called correctly
        mock_client.poll.assert_called_once_with(
            collection_name=collection_name,
            uri=self.service.poll_url,
            begin_date=begin_date,
            end_date=end_date
        )
        self.assertEqual(len(blocks), 2)

    @patch('core.parsers.stix1_parser.STIX1Parser.parse_content_block')
    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_consume_feed(self, mock_poll_collection, mock_parser):
        """Test consuming a TAXII feed"""
        # Create mock content blocks
        mock_block1 = MagicMock()
        mock_block1.content = '<xml>content1</xml>'
        mock_block2 = MagicMock()
        mock_block2.content = '<xml>content2</xml>'
        
        # Mock poll_collection to return the blocks
        mock_poll_collection.return_value = [mock_block1, mock_block2]
        
        # Mock the parser to return stats
        mock_parser.return_value = {
            'indicators_created': 1,
            'indicators_updated': 0,
            'ttp_created': 1,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Create the service
        service = OTXTaxiiService()
        
        # Consume the feed
        stats = service.consume_feed(self.threat_feed.id)
        
        # Check that poll_collection was called
        mock_poll_collection.assert_called_once()
        
        # Check that the parser was called for each block
        self.assertEqual(mock_parser.call_count, 2)
        
        # Check the stats
        self.assertEqual(stats['indicators_created'], 2)
        self.assertEqual(stats['ttp_created'], 2)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.poll_collection')
    def test_consume_feed_error_handling(self, mock_poll_collection):
        """Test error handling when consuming a TAXII feed."""
        # Mock the poll_collection method to raise an exception
        mock_poll_collection.side_effect = Exception("Test error")
        
        # Attempt to consume the feed
        with self.assertRaises(Exception):
            self.service.consume_feed(threat_feed_id=self.threat_feed.id)
        
        # Check that poll_collection was called
        mock_poll_collection.assert_called_once()


class StixTaxiiServiceTestCase(TestCase):
    """Test cases for the StixTaxiiService"""

    def setUp(self):
        """Set up the test environment."""
        self.service = StixTaxiiService()
        
        # Create a mock ThreatFeed for testing
        self.threat_feed = ThreatFeed.objects.create(
            name="STIX Feed",
            description="STIX 2.x Feed",
            is_external=True,
            taxii_server_url="https://example.com/taxii2",
            taxii_api_root="api2",
            taxii_collection_id="test-collection",
            taxii_username="test-user",
            taxii_password="test-pass"
        )

    @patch('core.services.stix_taxii_service.Server')
    @patch('core.services.stix_taxii_service.ApiRoot')
    def test_discover_collections(self, mock_api_root_class, mock_server_class):
        """Test discovering TAXII 2.x collections"""
        # Mock the Server and ApiRoot
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        
        mock_api_root = MagicMock()
        mock_api_root_class.return_value = mock_api_root
        
        # Mock the collections
        mock_collection1 = MagicMock(id="collection1", title="Test Collection 1", 
                                    description="Collection 1 description", 
                                    can_read=True, can_write=False,
                                    media_types=["application/vnd.oasis.stix+json; version=2.1"])
        mock_collection2 = MagicMock(id="collection2", title="Test Collection 2", 
                                    description="Collection 2 description", 
                                    can_read=True, can_write=True,
                                    media_types=["application/vnd.oasis.stix+json; version=2.1"])
        mock_api_root.collections = [mock_collection1, mock_collection2]
        
        # Discover collections
        server_url = "https://example.com/taxii2"
        api_root_path = "api2"
        username = "test-user"
        password = "test-pass"
        
        collections = self.service.discover_collections(server_url, api_root_path, username, password)
        
        # Check that Server was created correctly
        mock_server_class.assert_called_once_with(
            server_url,
            user=username,
            password=password
        )
        
        # Check that ApiRoot was created correctly
        mock_api_root_class.assert_called_once_with(
            f"{server_url}/{api_root_path}/",
            user=username,
            password=password
        )
        
        # Check that collections were returned correctly
        self.assertEqual(len(collections), 2)
        self.assertEqual(collections[0]['id'], "collection1")
        self.assertEqual(collections[0]['title'], "Test Collection 1")
        self.assertEqual(collections[1]['id'], "collection2")
        self.assertEqual(collections[1]['title'], "Test Collection 2")

    @patch('core.services.stix_taxii_service.Collection')
    @patch('core.services.stix_taxii_service.stix2_parse')
    def test_consume_feed(self, mock_stix2_parse, mock_collection_class):
        """Test consuming a TAXII 2.x feed"""

        mock_collection = MagicMock()
        mock_collection_class.return_value = mock_collection
        
        # Mock the get_objects response
        mock_collection.get_objects.return_value = {
            'objects': [
                STIX20_BUNDLE['objects'][0],
                STIX21_BUNDLE['objects'][1] 
            ]
        }
        
        # Mock the stix2_parse function
        mock_indicator = MagicMock(type='indicator', id='indicator--29aba82c-5393-42a8-9edb-6a2cb1df0a2c')
        mock_attack_pattern = MagicMock(type='attack-pattern', id='attack-pattern--d18f4181-1782-4202-9141-d47d3cc9f95a')
        mock_stix2_parse.side_effect = [mock_indicator, mock_attack_pattern]
        
        # Mock the factory methods
        with patch.object(self.service.indicator_creator, 'create_from_stix') as mock_create_indicator:
            with patch.object(self.service.ttp_creator, 'create_from_stix') as mock_create_ttp:
                
                # Set up the mock return values
                mock_create_indicator.return_value = {
                    'type': 'domain',
                    'value': 'evil-domain.com',
                    'stix_id': 'indicator--29aba82c-5393-42a8-9edb-6a2cb1df0a2c',
                    'description': 'Test indicator',
                    'confidence': 85
                }
                
                mock_create_ttp.return_value = {
                    'name': 'Drive-by Compromise',
                    'description': 'Test TTP',
                    'stix_id': 'attack-pattern--d18f4181-1782-4202-9141-d47d3cc9f95a',
                    'mitre_technique_id': 'T1189',
                    'mitre_tactic': 'initial_access'
                }
                
                # Consume the feed
                stats = self.service.consume_feed(self.threat_feed.id)
                
                # Check that collection was created correctly
                mock_collection_class.assert_called_once_with(
                    f"{self.threat_feed.taxii_server_url}/{self.threat_feed.taxii_api_root}/collections/{self.threat_feed.taxii_collection_id}/",
                    user=self.threat_feed.taxii_username,
                    password=self.threat_feed.taxii_password
                )
                
                # Check that get_objects was called
                mock_collection.get_objects.assert_called_once()
                
                # Check that stix2_parse was called for each object
                self.assertEqual(mock_stix2_parse.call_count, 2)
                
                # Check that the factory methods were called
                mock_create_indicator.assert_called_once_with(mock_indicator)
                mock_create_ttp.assert_called_once_with(mock_attack_pattern)
                
                # Check the stats
                self.assertEqual(stats['indicators_created'], 1)
                self.assertEqual(stats['ttp_created'], 1)
                self.assertEqual(stats['errors'], 0)
                
                # Check that the threat feed's last_sync was updated
                self.threat_feed.refresh_from_db()
                self.assertIsNotNone(self.threat_feed.last_sync)
    
    @patch('core.services.stix_taxii_service.Collection')
    def test_consume_feed_error_handling(self, mock_collection_class):
        """Test error handling when consuming a TAXII 2.x feed"""
        mock_collection_class.side_effect = Exception("Test error")
        
        # Attempt to consume the feed
        with self.assertRaises(Exception):
            self.service.consume_feed(self.threat_feed.id)
        
        # Check that Collection was attempted to be created
        mock_collection_class.assert_called_once()


if __name__ == '__main__':
    unittest.main()