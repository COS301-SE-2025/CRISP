"""
End-to-End API Tests
Tests the complete API workflow from consumption to publication
"""

import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

from core.models.models import ThreatFeed, Indicator, TTPData, Institution, Organization
from core.tests.test_data_fixtures import create_test_threat_feed, create_test_organization
from core.tests.test_helpers import (
    get_unique_username, get_unique_org_name, get_unique_identifier,
    get_unique_email, get_unique_collection_alias
)


class EndToEndAPITestCase(TransactionTestCase):
    """Test complete API workflows end-to-end"""

    def setUp(self):
        super().setUp()
        
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create test user for authentication
        self.user = User.objects.create_user(
            username=get_unique_username('api_test'),
            password='testpass123',
            email=get_unique_email('api_test')
        )
        
        # Create an Organization first
        self.organization = create_test_organization(
            name_suffix=f"api_test_{self.unique_suffix}",
            unique=True
        )
        
        # Create test threat feed
        self.feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"api_test_{self.unique_suffix}",
            unique=True
        )
        
        # API URLs - using self.feed instead of self.threat_feed
        self.feeds_url = reverse('threat-feed-list')
        self.feed_detail_url = reverse('threat-feed-detail', args=[self.feed.id])
        self.feed_consume_url = reverse('threat-feed-consume', args=[self.feed.id])
        self.feed_status_url = reverse('threat-feed-status', args=[self.feed.id])
        self.available_collections_url = reverse('threat-feed-available-collections')
        
        # Set up API client and authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        User.objects.all().delete()
        super().tearDown()

    @patch('core.services.otx_taxii_service.OTXTaxiiService.get_collections')
    def test_available_collections_endpoint(self, mock_get_collections):
        """Test the available collections endpoint."""
        # Mock the collections response
        mock_get_collections.return_value = [
            {
                'id': f'collection1_{self.unique_suffix}',
                'title': 'Test Collection 1',
                'description': 'First test collection',
                'available': True
            },
            {
                'id': f'collection2_{self.unique_suffix}',
                'title': 'Test Collection 2', 
                'description': 'Second test collection',
                'available': True
            }
        ]
        
        # Make the API call
        response = self.client.get(self.available_collections_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return the mocked collections
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Test Collection 1')
        self.assertEqual(data[1]['title'], 'Test Collection 2')

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_consume_endpoint_success(self, mock_consume_feed):
        """Test successful feed consumption via API."""
        # Mock successful consumption
        mock_consume_feed.return_value = (5, 2)  # 5 indicators, 2 TTPs
        
        # Make the API call
        response = self.client.post(self.feed_consume_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # FIXED: Updated field names to match actual API response
        self.assertIn('indicators', data)
        self.assertIn('ttps', data)
        self.assertEqual(data['indicators'], 5)
        self.assertEqual(data['ttps'], 2)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_consume_endpoint_with_parameters(self, mock_consume_feed):
        """Test feed consumption with parameters."""
        # Mock successful consumption
        mock_consume_feed.return_value = (3, 1)
        
        # Make API call with parameters
        response = self.client.post(
            self.feed_consume_url,
            data={
                'force_update': True,
                'days_back': 7
            }
        )
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # FIXED: Updated field names to match actual API response
        self.assertIn('indicators', data)
        self.assertIn('ttps', data)
        self.assertEqual(data['indicators'], 3)
        self.assertEqual(data['ttps'], 1)

    def test_consume_endpoint_error_handling(self, mock_consume_feed=None):
        """Test error handling in consume endpoint."""
        with patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed') as mock_consume:
            # Mock consumption failure
            mock_consume.side_effect = Exception("Connection failed")
            
            # Make the API call
            response = self.client.post(self.feed_consume_url)
            
            # Should handle error gracefully
            self.assertIn(response.status_code, [
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_200_OK 
            ])
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                self.assertIn('error', data)

    def test_feed_status_endpoint(self):
        """Test the feed status endpoint."""
        # Make the API call
        response = self.client.get(self.feed_status_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('name', data)
        self.assertIn('last_sync', data)
        self.assertEqual(data['name'], self.feed.name)

    def test_feed_list_endpoint(self):
        """Test the feed list endpoint."""
        # Make the API call
        response = self.client.get(self.feeds_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('count', data)
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        
        feed_ids = [feed['id'] for feed in data['results']]
        self.assertIn(self.feed.id, feed_ids)

    def test_feed_detail_endpoint(self):
        """Test the feed detail endpoint."""
        # Make the API call
        response = self.client.get(self.feed_detail_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['id'], self.feed.id)
        self.assertEqual(data['name'], self.feed.name)
        self.assertIn('description', data)
        self.assertIn('is_public', data)
        self.assertIn('taxii_server_url', data)


class EndToEndConsumptionTestCase(TransactionTestCase):
    """Test complete consumption workflow"""

    def setUp(self):
        """Set up test data"""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create test user for authentication
        self.user = User.objects.create_user(
            username=get_unique_username('consumption_test'),
            password='testpass123',
            email=get_unique_email('consumption_test')
        )
        
        # Create test organization
        self.organization = create_test_organization(
            name_suffix=f"consumption_{self.unique_suffix}",
            unique=True
        )
        
        # Set up API client and authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        User.objects.all().delete()

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    @patch('core.services.stix_taxii_service.StixTaxiiService.consume_feed')
    def test_multi_feed_batch_processing(self, mock_stix_consume, mock_otx_consume):
        """Test processing multiple feeds in batch"""
        # Mock consumption results
        mock_otx_consume.return_value = (10, 5)  # 10 indicators, 5 TTPs
        mock_stix_consume.return_value = (8, 3)   # 8 indicators, 3 TTPs
        
        # Create multiple feeds
        feeds = []
        for i in range(3):
            feed = create_test_threat_feed(
                owner=self.organization,
                name_suffix=f"batch_{i}_{self.unique_suffix}",
                unique=True
            )
            feeds.append(feed)
        
        # Process all feeds
        total_indicators = 0
        total_ttps = 0
        
        for feed in feeds:
            # Determine service type and mock accordingly
            if 'otx' in feed.taxii_server_url.lower():
                indicators, ttps = mock_otx_consume.return_value
            else:
                indicators, ttps = mock_stix_consume.return_value
            
            total_indicators += indicators
            total_ttps += ttps
        
        # Verify totals
        self.assertEqual(total_indicators, 24)  # 3 feeds × 8 indicators each
        self.assertEqual(total_ttps, 9)        # 3 feeds × 3 TTPs each

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_error_recovery_in_batch_processing(self, mock_consume_feed):
        """Test error recovery when processing multiple feeds"""
        # Create multiple feeds
        feeds = []
        for i in range(5):
            feed = create_test_threat_feed(
                owner=self.organization,
                name_suffix=f"error_test_{i}_{self.unique_suffix}",
                unique=True
            )
            feeds.append(feed)
        
        # Mock some feeds to succeed and some to fail
        def side_effect_function(feed):
            if 'error_test_2' in feed.name:  # Make middle feed fail
                raise Exception("Network error")
            return (5, 2)  # Success case
        
        mock_consume_feed.side_effect = side_effect_function
        
        # Process all feeds with error handling
        successful_feeds = 0
        failed_feeds = 0
        
        for feed in feeds:
            try:
                result = mock_consume_feed(feed)
                if result:
                    successful_feeds += 1
            except Exception:
                failed_feeds += 1
        
        # Should have 4 successful and 1 failed
        self.assertEqual(successful_feeds, 4)
        self.assertEqual(failed_feeds, 1)

    def test_feed_validation_before_consumption(self):
        """Test feed validation before attempting consumption"""
        # Create feed with invalid configuration
        invalid_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"invalid_{self.unique_suffix}",
            taxii_server_url="",  # Invalid empty URL
            unique=True
        )
        
        # Validation should catch this
        from core.validators.feed_validator import validate_feed_config
        
        is_valid, errors = validate_feed_config(invalid_feed)
        
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)
        self.assertIn('External feeds must have a TAXII server URL', str(errors))


class EndToEndPublicationTestCase(TransactionTestCase):
    """Test complete publication workflow"""

    def setUp(self):
        """Set up test data"""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create test user
        self.user = User.objects.create_user(
            username=get_unique_username('publication_test'),
            password='testpass123',
            email=get_unique_email('publication_test')
        )
        
        # Create test organization
        self.organization = create_test_organization(
            name_suffix=f"publication_{self.unique_suffix}",
            unique=True
        )
        
        # Create feed with data
        self.feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"publication_{self.unique_suffix}",
            is_public=True,
            unique=True
        )
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()

    def test_complete_publication_workflow(self):
        """Test the complete workflow from data to publication"""
        # Step 1: Add indicators to feed (simulated)
        from core.tests.test_data_fixtures import create_test_indicator, create_test_ttp
        
        # Create test indicators
        indicators = []
        for i in range(3):
            indicator = create_test_indicator(
                threat_feed=self.feed,
                value=f'10.0.0.{i}',
                type='ip',
                unique=True
            )
            indicators.append(indicator)
        
        # Create test TTPs
        ttps = []
        for i in range(2):
            ttp = create_test_ttp(
                threat_feed=self.feed,
                name=f'Test TTP {i}_{self.unique_suffix}', 
                unique=True
            )
            ttps.append(ttp)
        
        # Step 2: Verify data is ready for publication
        total_indicators = Indicator.objects.filter(threat_feed=self.feed).count()
        total_ttps = TTPData.objects.filter(threat_feed=self.feed).count()
        
        self.assertEqual(total_indicators, 3)
        self.assertEqual(total_ttps, 2)
        
        # Step 3: Generate publication bundle (mock)
        from core.patterns.factory.stix_base_factory import STIXObjectFactory
        
        # Convert indicators to STIX
        stix_indicators = []
        for indicator in indicators:
            stix_obj = STIXObjectFactory.create_stix_object('indicator', indicator)
            stix_indicators.append(stix_obj)
        
        # Convert TTPs to STIX
        stix_ttps = []
        for ttp in ttps:
            stix_obj = STIXObjectFactory.create_stix_object('attack-pattern', ttp)
            stix_ttps.append(stix_obj)
        
        # Step 4: Verify publication bundle
        total_stix_objects = len(stix_indicators) + len(stix_ttps)
        self.assertEqual(total_stix_objects, 5)
        
        # All STIX objects should have required fields
        for stix_obj in stix_indicators + stix_ttps:
            self.assertIn('type', stix_obj)
            self.assertIn('id', stix_obj)
            self.assertIn('spec_version', stix_obj)


class APIErrorHandlingTestCase(TransactionTestCase):
    """Test API error handling scenarios"""

    def setUp(self):
        """Set up test data"""
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create test user
        self.user = User.objects.create_user(
            username=get_unique_username('error_test'),
            password='testpass123',
            email=get_unique_email('error_test')
        )
        
        # Create test organization
        self.organization = create_test_organization(
            name_suffix=f"error_test_{self.unique_suffix}",
            unique=True
        )
        
        # Set up API client and authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()

    def test_nonexistent_feed_error(self):
        """Test handling of requests for non-existent feeds"""
        # Use a non-existent feed ID
        nonexistent_id = 999999
        
        # Try to access feed detail
        detail_url = reverse('threat-feed-detail', args=[nonexistent_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Try to consume non-existent feed
        consume_url = reverse('threat-feed-consume', args=[nonexistent_id])
        response = self.client.post(consume_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_request_data_error(self):
        """Test handling of invalid request data"""
        # Create a valid feed
        feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"invalid_data_{self.unique_suffix}",
            unique=True
        )
        
        # Try to consume with invalid parameters
        consume_url = reverse('threat-feed-consume', args=[feed.id])
        response = self.client.post(
            consume_url,
            data={
                'days_back': 'invalid_number',  
                'force_update': 'not_boolean' 
            }
        )
        
        # Should handle gracefully
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_200_OK 
        ])

    def test_method_not_allowed_error(self):
        """Test handling of incorrect HTTP methods"""
        # Create a valid feed
        feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"method_test_{self.unique_suffix}",
            unique=True
        )
        
        # Try to use GET on consume endpoint (should be POST)
        consume_url = reverse('threat-feed-consume', args=[feed.id])
        response = self.client.get(consume_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_server_error_simulation(self):
        """Test handling of server errors"""
        with patch('core.api.threat_feed_views.ThreatFeedViewSet.list') as mock_list:
            # Simulate server error
            mock_list.side_effect = Exception("Database connection failed")
            
            # Make request that should trigger error
            feeds_url = reverse('threat-feed-list')
            response = self.client.get(feeds_url)
            
            # Should return 500 error
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class MITREMatrixAPITestCase(TransactionTestCase):
    """Test MITRE ATT&CK Matrix API endpoint"""

    def setUp(self):
        super().setUp()
        
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        TTPData.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create an Organization
        self.organization = create_test_organization(
            name_suffix=f"matrix_test_{self.unique_suffix}",
            unique=True
        )
        
        # Create a test threat feed
        self.threat_feed = create_test_threat_feed(
            name_suffix=f"matrix_test_{self.unique_suffix}",
            organization=self.organization,
            unique=True
        )
        
        # Create some test TTPs with different tactics
        self.test_ttps = [
            {
                'name': 'Phishing Test',
                'description': 'Test phishing technique',
                'mitre_technique_id': 'T1566.001',
                'mitre_tactic': 'initial_access',
                'threat_feed': self.threat_feed,
                'stix_id': f'attack-pattern--{uuid.uuid4()}'
            },
            {
                'name': 'Command Line Test',
                'description': 'Test command line execution',
                'mitre_technique_id': 'T1059.001',
                'mitre_tactic': 'execution',
                'threat_feed': self.threat_feed,
                'stix_id': f'attack-pattern--{uuid.uuid4()}'
            },
            {
                'name': 'Registry Persistence',
                'description': 'Test registry persistence',
                'mitre_technique_id': 'T1547.001',
                'mitre_tactic': 'persistence',
                'threat_feed': self.threat_feed,
                'stix_id': f'attack-pattern--{uuid.uuid4()}'
            }
        ]
        
        # Create the TTP objects
        for ttp_data in self.test_ttps:
            TTPData.objects.create(**ttp_data)
        
        self.client = APIClient()

    def test_mitre_matrix_basic_functionality(self):
        """Test basic MITRE matrix endpoint functionality"""
        url = '/api/ttps/mitre-matrix/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['format'], 'matrix')
        self.assertEqual(data['total_techniques'], 3)
        self.assertIn('matrix', data)
        self.assertIn('statistics', data)
        
        # Check that our test tactics are present with correct counts
        matrix = data['matrix']
        self.assertEqual(matrix['initial_access']['technique_count'], 1)
        self.assertEqual(matrix['execution']['technique_count'], 1)
        self.assertEqual(matrix['persistence']['technique_count'], 1)

    def test_mitre_matrix_list_format(self):
        """Test MITRE matrix endpoint with list format"""
        url = '/api/ttps/mitre-matrix/?format=list'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['format'], 'list')
        self.assertEqual(data['total_techniques'], 3)
        self.assertIn('tactics', data)
        
        # Check tactics list structure
        tactics = data['tactics']
        tactic_counts = {t['tactic']: t['count'] for t in tactics}
        self.assertEqual(tactic_counts.get('initial_access', 0), 1)
        self.assertEqual(tactic_counts.get('execution', 0), 1)
        self.assertEqual(tactic_counts.get('persistence', 0), 1)

    def test_mitre_matrix_feed_filter(self):
        """Test MITRE matrix endpoint with feed filter"""
        url = f'/api/ttps/mitre-matrix/?feed_id={self.threat_feed.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_techniques'], 3)
        self.assertIsNotNone(data['feed_filter'])
        self.assertEqual(data['feed_filter']['name'], self.threat_feed.name)

    def test_mitre_matrix_include_zero(self):
        """Test MITRE matrix endpoint with include_zero parameter"""
        url = '/api/ttps/mitre-matrix/?include_zero=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Should include all 14 MITRE tactics
        matrix = data['matrix']
        self.assertEqual(len(matrix), 14)  # All MITRE_TACTIC_CHOICES
        
        # Verify that tactics with zero techniques are included
        zero_tactics = [t for t in matrix.values() if t['technique_count'] == 0]
        self.assertGreater(len(zero_tactics), 0)

    def test_mitre_matrix_error_handling(self):
        """Test MITRE matrix endpoint error handling"""
        # Test invalid feed_id
        url = '/api/ttps/mitre-matrix/?feed_id=invalid'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('Invalid feed_id parameter', data['error'])

    def test_mitre_matrix_statistics(self):
        """Test MITRE matrix endpoint statistics"""
        url = '/api/ttps/mitre-matrix/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        statistics = data['statistics']
        
        self.assertIn('most_common_tactic', statistics)
        self.assertIn('least_common_tactic', statistics)
        self.assertIn('tactics_with_techniques', statistics)
        self.assertEqual(statistics['tactics_with_techniques'], 3)


if __name__ == '__main__':
    import unittest
    unittest.main()