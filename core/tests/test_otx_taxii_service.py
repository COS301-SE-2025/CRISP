"""
Comprehensive tests for OTX TAXII Service
Tests for all OTX TAXII service functionality including client creation, collections, polling, and feed consumption.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from core.models.auth import Organization
from core.models.threat_feed import ThreatFeed
from core.services.otx_taxii_service import OTXTaxiiService
from core.tests.test_base import CrispTestCase


class OTXTaxiiServiceTest(CrispTestCase):
    """Test OTXTaxiiService functionality"""
    
    def setUp(self):
        super().setUp()
        self.service = OTXTaxiiService()
        
        self.org = Organization.objects.create(
            name="OTX Test Org", domain="otx.com", contact_email="test@otx.com"
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name="OTX Test Feed",
            description="Test feed for OTX TAXII",
            owner=self.org,
            is_external=True,
            taxii_server_url="https://otx.alienvault.com",
            taxii_api_root="/taxii/",
            taxii_collection_id="test-collection"
        )
    
    def test_init(self):
        """Test service initialization"""
        self.assertEqual(self.service.discovery_url, 'https://otx.alienvault.com/taxii/discovery')
        self.assertEqual(self.service.poll_url, 'https://otx.alienvault.com/taxii/poll')
        self.assertEqual(self.service.collections_url, 'https://otx.alienvault.com/taxii/collections')
        self.assertIsNotNone(self.service.stix1_parser)
    
    @patch('core.services.otx_taxii_service.create_client')
    def test_get_client_success(self, mock_create_client):
        """Test creating TAXII client successfully"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        client = self.service.get_client()
        
        mock_create_client.assert_called_once_with(
            discovery_path=self.service.discovery_url,
            use_https=True
        )
        mock_client.set_auth.assert_called_once()
        self.assertEqual(client, mock_client)
    
    @patch('core.services.otx_taxii_service.create_client')
    def test_get_client_exception(self, mock_create_client):
        """Test client creation with exception"""
        mock_create_client.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            self.service.get_client()
    
    @patch.object(OTXTaxiiService, 'get_client')
    def test_get_collections_success(self, mock_get_client):
        """Test getting collections successfully"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.name = 'test-collection'
        mock_collection.description = 'Test collection'
        mock_collection.type = 'DATA_FEED'
        mock_collection.available = True
        
        mock_client.get_collections.return_value = [mock_collection]
        mock_get_client.return_value = mock_client
        
        result = self.service.get_collections()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test-collection')
        self.assertEqual(result[0]['description'], 'Test collection')
        self.assertEqual(result[0]['type'], 'DATA_FEED')
        self.assertTrue(result[0]['available'])
    
    @patch.object(OTXTaxiiService, 'get_client')
    def test_get_collections_exception(self, mock_get_client):
        """Test getting collections with exception"""
        mock_client = Mock()
        mock_client.get_collections.side_effect = Exception("Collection fetch failed")
        mock_get_client.return_value = mock_client
        
        with self.assertLogs('core.services.otx_taxii_service', level='ERROR'):
            result = self.service.get_collections()
            
            self.assertEqual(result, [])
    
    @patch.object(OTXTaxiiService, 'get_client')
    def test_poll_collection_success(self, mock_get_client):
        """Test polling collection successfully"""
        mock_client = Mock()
        mock_content_block = Mock()
        mock_content_block.content = '<stix:STIX_Package>test content</stix:STIX_Package>'
        mock_content_block.timestamp_label = timezone.now()
        
        mock_client.poll.return_value = [mock_content_block]
        mock_get_client.return_value = mock_client
        
        result = self.service.poll_collection('test-collection')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'], mock_content_block.content)
        self.assertIn('timestamp', result[0])
    
    @patch.object(OTXTaxiiService, 'get_client')
    def test_poll_collection_with_date_range(self, mock_get_client):
        """Test polling collection with date range"""
        mock_client = Mock()
        mock_content_block = Mock()
        mock_content_block.content = '<stix:STIX_Package>dated content</stix:STIX_Package>'
        mock_content_block.timestamp_label = timezone.now()
        
        mock_client.poll.return_value = [mock_content_block]
        mock_get_client.return_value = mock_client
        
        begin_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        result = self.service.poll_collection(
            'test-collection',
            begin_date=begin_date,
            end_date=end_date
        )
        
        self.assertEqual(len(result), 1)
        mock_client.poll.assert_called_once()
    
    @patch.object(OTXTaxiiService, 'get_client')
    def test_poll_collection_with_limit(self, mock_get_client):
        """Test polling collection with limit"""
        mock_client = Mock()
        mock_content_blocks = []
        for i in range(5):
            mock_block = Mock()
            mock_block.content = f'<stix:STIX_Package>content {i}</stix:STIX_Package>'
            mock_block.timestamp_label = timezone.now()
            mock_content_blocks.append(mock_block)
        
        mock_client.poll.return_value = mock_content_blocks
        mock_get_client.return_value = mock_client
        
        result = self.service.poll_collection('test-collection', limit=3)
        
        self.assertEqual(len(result), 3)  # Should be limited to 3
    
    @patch.object(OTXTaxiiService, 'get_client')
    def test_poll_collection_retry_on_failure(self, mock_get_client):
        """Test polling collection with retry on failure"""
        mock_client = Mock()
        mock_client.poll.side_effect = [
            Exception("Temporary failure"),
            Exception("Temporary failure"),
            []  # Success on third try
        ]
        mock_get_client.return_value = mock_client
        
        result = self.service.poll_collection('test-collection', max_retries=3)
        
        self.assertEqual(len(result), 0)
        self.assertEqual(mock_client.poll.call_count, 3)
    
    @patch.object(OTXTaxiiService, 'get_client')
    def test_poll_collection_max_retries_exceeded(self, mock_get_client):
        """Test polling collection when max retries exceeded"""
        mock_client = Mock()
        mock_client.poll.side_effect = Exception("Persistent failure")
        mock_get_client.return_value = mock_client
        
        with self.assertLogs('core.services.otx_taxii_service', level='ERROR'):
            result = self.service.poll_collection('test-collection', max_retries=2)
            
            self.assertEqual(result, [])
            self.assertEqual(mock_client.poll.call_count, 2)
    
    @patch.object(OTXTaxiiService, 'poll_collection')
    @patch.object(OTXTaxiiService, '_process_block_batch')
    def test_consume_feed_by_id(self, mock_process_batch, mock_poll):
        """Test consuming feed by threat feed ID"""
        mock_poll.return_value = [
            {'content': '<stix:STIX_Package>test1</stix:STIX_Package>', 'timestamp': timezone.now()},
            {'content': '<stix:STIX_Package>test2</stix:STIX_Package>', 'timestamp': timezone.now()}
        ]
        mock_process_batch.return_value = {
            'indicators_created': 2,
            'indicators_updated': 0,
            'ttp_created': 1,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        result = self.service.consume_feed(threat_feed_id=self.threat_feed.id)
        
        self.assertEqual(result['indicators_created'], 2)
        self.assertEqual(result['ttp_created'], 1)
        mock_poll.assert_called_once()
        mock_process_batch.assert_called_once()
    
    @patch.object(OTXTaxiiService, 'poll_collection')
    @patch.object(OTXTaxiiService, '_process_block_batch')
    def test_consume_feed_by_collection_name(self, mock_process_batch, mock_poll):
        """Test consuming feed by collection name"""
        mock_poll.return_value = [
            {'content': '<stix:STIX_Package>test</stix:STIX_Package>', 'timestamp': timezone.now()}
        ]
        mock_process_batch.return_value = {
            'indicators_created': 1,
            'indicators_updated': 0,
            'ttp_created': 0,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        result = self.service.consume_feed(collection_name='test-collection')
        
        self.assertEqual(result['indicators_created'], 1)
        mock_poll.assert_called_once_with(
            'test-collection',
            begin_date=None,
            end_date=None,
            limit=None
        )
    
    @patch.object(OTXTaxiiService, 'poll_collection')
    def test_consume_feed_with_date_range(self, mock_poll):
        """Test consuming feed with specific date range"""
        mock_poll.return_value = []
        
        begin_date = timezone.now() - timedelta(days=7)
        
        self.service.consume_feed(
            collection_name='test-collection',
            begin_date=begin_date,
            limit=100
        )
        
        mock_poll.assert_called_once_with(
            'test-collection',
            begin_date=begin_date,
            end_date=None,
            limit=100
        )
    
    @patch.object(OTXTaxiiService, 'poll_collection')
    def test_consume_feed_with_force_days(self, mock_poll):
        """Test consuming feed with force_days parameter"""
        mock_poll.return_value = []
        
        self.service.consume_feed(
            collection_name='test-collection',
            force_days=30
        )
        
        # Should calculate begin_date based on force_days
        mock_poll.assert_called_once()
        call_args = mock_poll.call_args[1]
        self.assertIsNotNone(call_args['begin_date'])
    
    @patch.object(OTXTaxiiService, 'poll_collection')
    @patch.object(OTXTaxiiService, '_process_block_batch')
    def test_consume_feed_batching(self, mock_process_batch, mock_poll):
        """Test consuming feed with batching"""
        # Create more blocks than batch size
        mock_blocks = []
        for i in range(250):  # More than default batch_size of 100
            mock_blocks.append({
                'content': f'<stix:STIX_Package>test{i}</stix:STIX_Package>',
                'timestamp': timezone.now()
            })
        
        mock_poll.return_value = mock_blocks
        mock_process_batch.return_value = {
            'indicators_created': 10,
            'indicators_updated': 0,
            'ttp_created': 5,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        result = self.service.consume_feed(
            collection_name='test-collection',
            batch_size=100
        )
        
        # Should be called 3 times (250 / 100 = 2.5, rounded up to 3)
        self.assertEqual(mock_process_batch.call_count, 3)
        
        # Results should be aggregated
        self.assertEqual(result['indicators_created'], 30)  # 10 * 3
        self.assertEqual(result['ttp_created'], 15)  # 5 * 3
    
    def test_consume_feed_no_params(self):
        """Test consuming feed without required parameters"""
        with self.assertRaises(ValueError):
            self.service.consume_feed()
    
    def test_consume_feed_invalid_threat_feed_id(self):
        """Test consuming feed with invalid threat feed ID"""
        with self.assertRaises(Exception):
            self.service.consume_feed(threat_feed_id=99999)
    
    @patch('core.parsers.stix1_parser.STIX1Parser.parse_stix_content')
    @patch('core.repositories.threat_feed_repository.ThreatFeedRepository.store_indicators')
    @patch('core.repositories.threat_feed_repository.ThreatFeedRepository.store_ttps')
    def test_process_block_batch_success(self, mock_store_ttps, mock_store_indicators, mock_parse):
        """Test processing block batch successfully"""
        # Mock parser results
        mock_indicators = [
            {'type': 'indicator', 'pattern': 'test1'},
            {'type': 'indicator', 'pattern': 'test2'}
        ]
        mock_ttps = [
            {'type': 'attack-pattern', 'name': 'test-ttp'}
        ]
        
        mock_parse.return_value = {
            'indicators': mock_indicators,
            'ttps': mock_ttps,
            'parsing_errors': []
        }
        
        mock_store_indicators.return_value = {
            'created': 2,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        
        mock_store_ttps.return_value = {
            'created': 1,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        
        blocks = [
            {'content': '<stix:STIX_Package>test1</stix:STIX_Package>'},
            {'content': '<stix:STIX_Package>test2</stix:STIX_Package>'}
        ]
        
        stats = {
            'indicators_created': 0,
            'indicators_updated': 0,
            'ttp_created': 0,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        result = self.service._process_block_batch(blocks, self.threat_feed, stats)
        
        self.assertEqual(result['indicators_created'], 2)
        self.assertEqual(result['ttp_created'], 1)
        self.assertEqual(mock_parse.call_count, 2)
        mock_store_indicators.assert_called_once()
        mock_store_ttps.assert_called_once()
    
    @patch('core.parsers.stix1_parser.STIX1Parser.parse_stix_content')
    def test_process_block_batch_parsing_errors(self, mock_parse):
        """Test processing block batch with parsing errors"""
        mock_parse.return_value = {
            'indicators': [],
            'ttps': [],
            'parsing_errors': ['Invalid STIX format']
        }
        
        blocks = [
            {'content': 'invalid xml content'}
        ]
        
        stats = {
            'indicators_created': 0,
            'indicators_updated': 0,
            'ttp_created': 0,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        with self.assertLogs('core.services.otx_taxii_service', level='WARNING'):
            result = self.service._process_block_batch(blocks, self.threat_feed, stats)
            
            self.assertEqual(result['errors'], 1)
    
    @patch('core.parsers.stix1_parser.STIX1Parser.parse_stix_content')
    def test_process_block_batch_exception(self, mock_parse):
        """Test processing block batch with exception"""
        mock_parse.side_effect = Exception("Parser failed")
        
        blocks = [
            {'content': '<stix:STIX_Package>test</stix:STIX_Package>'}
        ]
        
        stats = {
            'indicators_created': 0,
            'indicators_updated': 0,
            'ttp_created': 0,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        with self.assertLogs('core.services.otx_taxii_service', level='ERROR'):
            result = self.service._process_block_batch(blocks, self.threat_feed, stats)
            
            self.assertEqual(result['errors'], 1)
    
    @patch('core.repositories.threat_feed_repository.ThreatFeedRepository.store_indicators')
    @patch('core.parsers.stix1_parser.STIX1Parser.parse_stix_content')
    def test_process_block_batch_storage_errors(self, mock_parse, mock_store_indicators):
        """Test processing block batch with storage errors"""
        mock_parse.return_value = {
            'indicators': [{'type': 'indicator', 'pattern': 'test'}],
            'ttps': [],
            'parsing_errors': []
        }
        
        mock_store_indicators.return_value = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': ['Storage failed']
        }
        
        blocks = [
            {'content': '<stix:STIX_Package>test</stix:STIX_Package>'}
        ]
        
        stats = {
            'indicators_created': 0,
            'indicators_updated': 0,
            'ttp_created': 0,
            'ttp_updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        result = self.service._process_block_batch(blocks, self.threat_feed, stats)
        
        self.assertEqual(result['errors'], 1)
    
    @patch.object(OTXTaxiiService, 'poll_collection')
    def test_consume_feed_empty_response(self, mock_poll):
        """Test consuming feed with empty response"""
        mock_poll.return_value = []
        
        result = self.service.consume_feed(collection_name='empty-collection')
        
        self.assertEqual(result['indicators_created'], 0)
        self.assertEqual(result['ttp_created'], 0)
        self.assertEqual(result['errors'], 0)
    
    @patch.object(OTXTaxiiService, 'poll_collection')
    def test_consume_feed_polling_exception(self, mock_poll):
        """Test consuming feed when polling raises exception"""
        mock_poll.side_effect = Exception("Polling failed")
        
        with self.assertLogs('core.services.otx_taxii_service', level='ERROR'):
            result = self.service.consume_feed(collection_name='error-collection')
            
            self.assertEqual(result['errors'], 1)


class OTXTaxiiServiceIntegrationTest(CrispTestCase):
    """Integration tests for OTX TAXII Service"""
    
    def setUp(self):
        super().setUp()
        self.service = OTXTaxiiService()
        
        self.org = Organization.objects.create(
            name="Integration Org", domain="integration.com", contact_email="test@integration.com"
        )
    
    @patch('core.services.otx_taxii_service.create_client')
    def test_full_workflow_mock(self, mock_create_client):
        """Test full workflow with mocked external dependencies"""
        # Mock TAXII client
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.name = 'integration-collection'
        mock_collection.description = 'Integration test collection'
        mock_collection.type = 'DATA_FEED'
        mock_collection.available = True
        
        mock_content_block = Mock()
        mock_content_block.content = '''
        <stix:STIX_Package>
            <stix:Indicators>
                <stix:Indicator>
                    <stix:Type>Domain Watchlist</stix:Type>
                    <stix:Observable>
                        <cybox:Object>
                            <cybox:Properties>
                                <DomainNameObj:Value>evil.com</DomainNameObj:Value>
                            </cybox:Properties>
                        </cybox:Object>
                    </stix:Observable>
                </stix:Indicator>
            </stix:Indicators>
        </stix:STIX_Package>
        '''
        mock_content_block.timestamp_label = timezone.now()
        
        mock_client.get_collections.return_value = [mock_collection]
        mock_client.poll.return_value = [mock_content_block]
        mock_create_client.return_value = mock_client
        
        # Test getting collections
        collections = self.service.get_collections()
        self.assertEqual(len(collections), 1)
        self.assertEqual(collections[0]['name'], 'integration-collection')
        
        # Test polling collection
        with patch('core.parsers.stix1_parser.STIX1Parser.parse_stix_content') as mock_parse:
            mock_parse.return_value = {
                'indicators': [{'type': 'indicator', 'pattern': 'domain:evil.com'}],
                'ttps': [],
                'parsing_errors': []
            }
            
            with patch('core.repositories.threat_feed_repository.ThreatFeedRepository.store_indicators') as mock_store:
                mock_store.return_value = {
                    'created': 1,
                    'updated': 0,
                    'skipped': 0,
                    'errors': []
                }
                
                result = self.service.consume_feed(collection_name='integration-collection')
                
                self.assertEqual(result['indicators_created'], 1)
                self.assertEqual(result['errors'], 0)
    
    def test_service_configuration(self):
        """Test service configuration and settings"""
        self.assertIsNotNone(self.service.api_key)
        self.assertTrue(self.service.discovery_url.startswith('https://'))
        self.assertTrue(self.service.poll_url.startswith('https://'))
        self.assertTrue(self.service.collections_url.startswith('https://'))
    
    def test_service_error_recovery(self):
        """Test service error recovery mechanisms"""
        with patch.object(self.service, 'get_client', side_effect=Exception("Connection failed")):
            with self.assertLogs('core.services.otx_taxii_service', level='ERROR'):
                collections = self.service.get_collections()
                self.assertEqual(collections, [])
    
    def test_service_logging(self):
        """Test service logging functionality"""
        with patch.object(self.service, 'get_client', side_effect=Exception("Test error")):
            with self.assertLogs('core.services.otx_taxii_service', level='ERROR') as log:
                self.service.get_collections()
                
                self.assertTrue(any('Test error' in record.message for record in log.records))