"""
Unit tests for repository implementations
"""
import unittest
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from core.repositories.threat_feed_repository import ThreatFeedRepository
from core.repositories.indicator_repository import IndicatorRepository
from core.repositories.ttp_repository import TTPRepository
from core.patterns.observer.threat_feed import ThreatFeed
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData


class ThreatFeedRepositoryTestCase(TransactionTestCase):
    """Test cases for the ThreatFeedRepository - Using TransactionTestCase for better isolation"""

    def setUp(self):
        """Set up the test environment"""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        
        self.repository = ThreatFeedRepository()
        
        # Create test threat feeds with unique identifiers
        self.feed1 = ThreatFeed.objects.create(
            name=f"Feed 1 - {uuid.uuid4().hex[:8]}",
            description="Test Feed 1",
            is_external=True,
            taxii_server_url="https://test1.example.com/taxii",
            taxii_api_root="api1",
            taxii_collection_id="collection1"
        )
        
        self.feed2 = ThreatFeed.objects.create(
            name=f"Feed 2 - {uuid.uuid4().hex[:8]}",
            description="Test Feed 2",
            is_external=False
        )
        
        self.feed3 = ThreatFeed.objects.create(
            name=f"Feed 3 - {uuid.uuid4().hex[:8]}",
            description="External Feed without TAXII details",
            is_external=True
        )

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()

    def test_get_by_id(self):
        """Test retrieving a threat feed by ID"""
        feed = self.repository.get_by_id(self.feed1.id)
        
        # Check that the correct feed was retrieved
        self.assertEqual(feed.id, self.feed1.id)
        self.assertEqual(feed.name, self.feed1.name)
        
        # Test with non-existent ID
        feed = self.repository.get_by_id(999999)
        self.assertIsNone(feed)

    def test_get_all(self):
        """Test retrieving all threat feeds"""
        # Get all feeds
        feeds = self.repository.get_all()
        
        # Check that all feeds were retrieved
        self.assertEqual(feeds.count(), 3)
        feed_ids = [f.id for f in feeds]
        self.assertIn(self.feed1.id, feed_ids)
        self.assertIn(self.feed2.id, feed_ids)
        self.assertIn(self.feed3.id, feed_ids)

    def test_get_external_feeds(self):
        """Test retrieving external threat feeds with TAXII details"""
        # Get external feeds
        feeds = self.repository.get_external_feeds()
        
        # Check that only the external feed with TAXII details was retrieved
        self.assertEqual(feeds.count(), 1)
        self.assertEqual(feeds.first().id, self.feed1.id)

    def test_create(self):
        """Test creating a new threat feed"""
        # Create a new feed
        feed_data = {
            'name': f'New Feed - {uuid.uuid4().hex[:8]}',
            'description': 'New Test Feed',
            'is_external': True,
            'taxii_server_url': 'https://new.example.com/taxii',
            'taxii_api_root': 'api-new',
            'taxii_collection_id': 'new-collection'
        }
        
        new_feed = self.repository.create(feed_data)
        
        # Check that the feed was created correctly
        self.assertIsNotNone(new_feed.id)
        self.assertEqual(new_feed.name, feed_data['name'])
        self.assertEqual(new_feed.description, 'New Test Feed')
        self.assertTrue(new_feed.is_external)
        self.assertEqual(new_feed.taxii_server_url, 'https://new.example.com/taxii')
        
        # Check that it exists in the database
        feed_in_db = ThreatFeed.objects.get(id=new_feed.id)
        self.assertEqual(feed_in_db.name, feed_data['name'])

    def test_update(self):
        """Test updating an existing threat feed."""
        # Update the first feed
        update_data = {
            'name': f'Updated Feed 1 - {uuid.uuid4().hex[:8]}',
            'description': 'Updated description',
            'is_public': True
        }
        
        updated_feed = self.repository.update(self.feed1.id, update_data)
        
        # Check that the feed was updated correctly
        self.assertEqual(updated_feed.id, self.feed1.id)
        self.assertEqual(updated_feed.name, update_data['name'])
        self.assertEqual(updated_feed.description, 'Updated description')
        self.assertTrue(updated_feed.is_public)
        
        # Unchanged fields should remain the same
        self.assertEqual(updated_feed.taxii_server_url, 'https://test1.example.com/taxii')
        
        # Check that it was updated in the database
        feed_in_db = ThreatFeed.objects.get(id=self.feed1.id)
        self.assertEqual(feed_in_db.name, update_data['name'])

    def test_delete(self):
        """Test deleting a threat feed"""
        initial_count = ThreatFeed.objects.count()
        
        # Delete the first feed
        self.repository.delete(self.feed1.id)
        
        # Check that it was deleted from the database
        with self.assertRaises(ThreatFeed.DoesNotExist):
            ThreatFeed.objects.get(id=self.feed1.id)
        
        # The count should be reduced by 1
        self.assertEqual(ThreatFeed.objects.count(), initial_count - 1)


class IndicatorRepositoryTestCase(TransactionTestCase):
    """Test cases for the IndicatorRepository - Using TransactionTestCase for better isolation"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        Indicator.objects.all().delete()
        ThreatFeed.objects.all().delete()
        
        self.repository = IndicatorRepository()
        
        # Create a test threat feed
        self.feed = ThreatFeed.objects.create(
            name=f"Test Feed - {uuid.uuid4().hex[:8]}",
            description="Test Feed for Indicators"
        )
        
        # Create test indicators with unique STIX IDs
        self.indicator1 = Indicator.objects.create(
            threat_feed=self.feed,
            type='ip',
            value='192.168.1.1',
            description='Test IP Indicator',
            stix_id=f'indicator-test-{uuid.uuid4().hex[:8]}',
            confidence=75
        )
        
        self.indicator2 = Indicator.objects.create(
            threat_feed=self.feed,
            type='domain',
            value='malicious-domain.com',
            description='Test Domain Indicator',
            stix_id=f'indicator-test-{uuid.uuid4().hex[:8]}',
            confidence=80
        )
        
        self.indicator3 = Indicator.objects.create(
            threat_feed=self.feed,
            type='ip',
            value='10.0.0.1',
            description='Another Test IP Indicator',
            stix_id=f'indicator-test-{uuid.uuid4().hex[:8]}',
            confidence=65
        )

    def tearDown(self):
        """Clean up after each test"""
        Indicator.objects.all().delete()
        ThreatFeed.objects.all().delete()

    def test_get_by_id(self):
        """Test retrieving an indicator by ID"""
        # Get the first indicator
        indicator = self.repository.get_by_id(self.indicator1.id)
        
        # Check that the correct indicator was retrieved
        self.assertEqual(indicator.id, self.indicator1.id)
        self.assertEqual(indicator.value, '192.168.1.1')
        
        # Test with non-existent ID
        indicator = self.repository.get_by_id(999999)
        self.assertIsNone(indicator)

    def test_get_by_stix_id(self):
        """Test retrieving an indicator by STIX ID"""
        # Get by STIX ID
        indicator = self.repository.get_by_stix_id(self.indicator2.stix_id)
        
        # Check that the correct indicator was retrieved
        self.assertEqual(indicator.id, self.indicator2.id)
        self.assertEqual(indicator.value, 'malicious-domain.com')
        
        # Test with non-existent STIX ID
        indicator = self.repository.get_by_stix_id('non-existent-id')
        self.assertIsNone(indicator)

    def test_get_by_feed(self):
        """Test retrieving indicators by feed ID"""
        # Get by feed ID
        indicators = self.repository.get_by_feed(self.feed.id)
        
        # Check that all indicators for the feed were retrieved
        self.assertEqual(indicators.count(), 3)
        indicator_ids = [i.id for i in indicators]
        self.assertIn(self.indicator1.id, indicator_ids)
        self.assertIn(self.indicator2.id, indicator_ids)
        self.assertIn(self.indicator3.id, indicator_ids)

    def test_get_by_type(self):
        """Test retrieving indicators by type."""
        # Get by type
        indicators = self.repository.get_by_type('ip')
        
        # Check that all IP indicators were retrieved
        self.assertEqual(indicators.count(), 2)
        indicator_ids = [i.id for i in indicators]
        self.assertIn(self.indicator1.id, indicator_ids)
        self.assertIn(self.indicator3.id, indicator_ids)
        self.assertNotIn(self.indicator2.id, indicator_ids)

    def test_create(self):
        """Test creating a new indicator."""
        # Create a new indicator
        indicator_data = {
            'threat_feed': self.feed,
            'type': 'url',
            'value': 'https://malicious-site.com/page',
            'description': 'Test URL Indicator',
            'stix_id': f'indicator-test-{uuid.uuid4().hex[:8]}',
            'confidence': 70
        }
        
        new_indicator = self.repository.create(indicator_data)
        
        # Check that the indicator was created correctly
        self.assertIsNotNone(new_indicator.id)
        self.assertEqual(new_indicator.type, 'url')
        self.assertEqual(new_indicator.value, 'https://malicious-site.com/page')
        
        # Check that it exists in the database
        indicator_in_db = Indicator.objects.get(id=new_indicator.id)
        self.assertEqual(indicator_in_db.value, 'https://malicious-site.com/page')

    def test_update(self):
        """Test updating an existing indicator."""
        # Update the first indicator
        update_data = {
            'description': 'Updated IP Indicator',
            'confidence': 90
        }
        
        updated_indicator = self.repository.update(self.indicator1.id, update_data)
        
        # Check that the indicator was updated correctly
        self.assertEqual(updated_indicator.id, self.indicator1.id)
        self.assertEqual(updated_indicator.description, 'Updated IP Indicator')
        self.assertEqual(updated_indicator.confidence, 90)
        
        # Unchanged fields should remain the same
        self.assertEqual(updated_indicator.type, 'ip')
        self.assertEqual(updated_indicator.value, '192.168.1.1')
        
        # Check that it was updated in the database
        indicator_in_db = Indicator.objects.get(id=self.indicator1.id)
        self.assertEqual(indicator_in_db.description, 'Updated IP Indicator')

    def test_delete(self):
        """Test deleting an indicator"""
        initial_count = Indicator.objects.count()
        
        # Delete the first indicator
        self.repository.delete(self.indicator1.id)
        
        # Check that it was deleted from the database
        with self.assertRaises(Indicator.DoesNotExist):
            Indicator.objects.get(id=self.indicator1.id)
        
        # The count should be reduced by 1
        self.assertEqual(Indicator.objects.count(), initial_count - 1)


class TTPRepositoryTestCase(TransactionTestCase):
    """Test cases for the TTPRepository - Using TransactionTestCase for better isolation"""

    def setUp(self):
        """Set up the test environment"""
        # Clear any existing data
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()
        
        self.repository = TTPRepository()
        
        # Create a test threat feed
        self.feed = ThreatFeed.objects.create(
            name=f"Test Feed - {uuid.uuid4().hex[:8]}",
            description="Test Feed for TTPs"
        )
        
        # Create test TTPs with unique STIX IDs
        self.ttp1 = TTPData.objects.create(
            threat_feed=self.feed,
            name='Phishing Attack',
            description='Test Phishing TTP',
            mitre_technique_id='T1566.001',
            mitre_tactic='initial_access',
            stix_id=f'ttp-test-{uuid.uuid4().hex[:8]}'
        )
        
        self.ttp2 = TTPData.objects.create(
            threat_feed=self.feed,
            name='Drive-by Compromise',
            description='Test Drive-by TTP',
            mitre_technique_id='T1189',
            mitre_tactic='initial_access',
            stix_id=f'ttp-test-{uuid.uuid4().hex[:8]}'
        )
        
        self.ttp3 = TTPData.objects.create(
            threat_feed=self.feed,
            name='PowerShell',
            description='Test PowerShell TTP',
            mitre_technique_id='T1059.001',
            mitre_tactic='execution',
            stix_id=f'ttp-test-{uuid.uuid4().hex[:8]}'
        )

    def tearDown(self):
        """Clean up after each test"""
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()

    def test_get_by_id(self):
        """Test retrieving a TTP by ID"""
        # Get the first TTP
        ttp = self.repository.get_by_id(self.ttp1.id)
        
        # Check that the correct TTP was retrieved
        self.assertEqual(ttp.id, self.ttp1.id)
        self.assertEqual(ttp.name, 'Phishing Attack')
        
        # Test with non-existent ID
        ttp = self.repository.get_by_id(999999)
        self.assertIsNone(ttp)

    def test_get_by_stix_id(self):
        """Test retrieving a TTP by STIX ID"""
        # Get by STIX ID
        ttp = self.repository.get_by_stix_id(self.ttp2.stix_id)
        
        # Check that the correct TTP was retrieved
        self.assertEqual(ttp.id, self.ttp2.id)
        self.assertEqual(ttp.name, 'Drive-by Compromise')
        
        # Test with non-existent STIX ID
        ttp = self.repository.get_by_stix_id('non-existent-id')
        self.assertIsNone(ttp)

    def test_get_by_feed(self):
        """Test retrieving TTPs by feed ID"""
        # Get by feed ID
        ttps = self.repository.get_by_feed(self.feed.id)
        
        # Check that all TTPs for the feed were retrieved
        self.assertEqual(ttps.count(), 3)
        ttp_ids = [t.id for t in ttps]
        self.assertIn(self.ttp1.id, ttp_ids)
        self.assertIn(self.ttp2.id, ttp_ids)
        self.assertIn(self.ttp3.id, ttp_ids)

    def test_get_by_mitre_id(self):
        """Test retrieving TTPs by MITRE technique ID"""
        # Get by MITRE ID
        ttps = self.repository.get_by_mitre_id('T1566.001')
        
        # Check that the correct TTP was retrieved
        self.assertEqual(ttps.count(), 1)
        self.assertEqual(ttps.first().id, self.ttp1.id)

    def test_create(self):
        """Test creating a new TTP"""
        # Create a new TTP
        ttp_data = {
            'threat_feed': self.feed,
            'name': 'Data Exfiltration',
            'description': 'Test Data Exfiltration TTP',
            'mitre_technique_id': 'T1048',
            'mitre_tactic': 'exfiltration',
            'stix_id': f'ttp-test-{uuid.uuid4().hex[:8]}'
        }
        
        new_ttp = self.repository.create(ttp_data)
        
        # Check that the TTP was created correctly
        self.assertIsNotNone(new_ttp.id)
        self.assertEqual(new_ttp.name, 'Data Exfiltration')
        self.assertEqual(new_ttp.mitre_technique_id, 'T1048')
        
        # Check that it exists in the database
        ttp_in_db = TTPData.objects.get(id=new_ttp.id)
        self.assertEqual(ttp_in_db.name, 'Data Exfiltration')

    def test_update(self):
        """Test updating an existing TTP"""
        # Update the first TTP
        update_data = {
            'description': 'Updated Phishing TTP',
            'mitre_tactic': 'initial_access'
        }
        
        updated_ttp = self.repository.update(self.ttp1.id, update_data)
        
        # Check that the TTP was updated correctly
        self.assertEqual(updated_ttp.id, self.ttp1.id)
        self.assertEqual(updated_ttp.description, 'Updated Phishing TTP')
        
        # Unchanged fields should remain the same
        self.assertEqual(updated_ttp.name, 'Phishing Attack')
        self.assertEqual(updated_ttp.mitre_technique_id, 'T1566.001')
        
        # Check that it was updated in the database
        ttp_in_db = TTPData.objects.get(id=self.ttp1.id)
        self.assertEqual(ttp_in_db.description, 'Updated Phishing TTP')

    def test_delete(self):
        """Test deleting a TTP"""
        initial_count = TTPData.objects.count()
        
        # Delete the first TTP
        self.repository.delete(self.ttp1.id)
        
        # Check that it was deleted from the database
        with self.assertRaises(TTPData.DoesNotExist):
            TTPData.objects.get(id=self.ttp1.id)
        
        # The count should be reduced by 1
        self.assertEqual(TTPData.objects.count(), initial_count - 1)


if __name__ == '__main__':
    unittest.main()