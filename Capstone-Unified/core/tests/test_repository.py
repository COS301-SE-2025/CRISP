"""
Unit tests for Repository pattern implementations
"""
import unittest
import uuid
from django.test import TransactionTestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

from core.repositories.threat_feed_repository import ThreatFeedRepository
from core.repositories.indicator_repository import IndicatorRepository
from core.repositories.ttp_repository import TTPRepository
from core.models.models import ThreatFeed, Indicator, TTPData, Institution, Organization
from core.tests.test_data_fixtures import (
    create_test_organization, create_test_threat_feed, 
    create_test_indicator, create_test_ttp
)
from core.tests.test_helpers import (
    get_unique_username, get_unique_org_name, get_unique_identifier,
    get_unique_email, get_unique_collection_alias
)


class ThreatFeedRepositoryTestCase(TransactionTestCase):
    """Test cases for the ThreatFeedRepository - Using TransactionTestCase for better isolation"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()
        
        self.repository = ThreatFeedRepository()
        
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create test user for organization ownership
        self.user = User.objects.create_user(
            username=get_unique_username('repo_test'),
            password='testpass123',
            email=get_unique_email('repo_test')
        )
        
        # Create Organizations first with unique names
        self.organization1 = create_test_organization(
            name_suffix=f"repo_test_1_{self.unique_suffix}",
            created_by=self.user,
            unique=True
        )
        
        self.organization2 = create_test_organization(
            name_suffix=f"repo_test_2_{self.unique_suffix}",
            created_by=self.user,
            unique=True
        )
        
        # Create test threat feeds with Organizations as owners
        self.feed1 = create_test_threat_feed(
            owner=self.organization1,
            name_suffix=f"feed_1_{self.unique_suffix}",
            is_external=True,
            is_public=False,
            taxii_server_url="https://test1.example.com/taxii",
            taxii_collection_id=f"collection-1-{self.unique_suffix}",
            unique=True
        )
        
        self.feed2 = create_test_threat_feed(
            owner=self.organization1,
            name_suffix=f"feed_2_{self.unique_suffix}",
            is_external=False,
            is_public=True,
            taxii_server_url="https://test2.example.com/taxii",
            taxii_collection_id=f"collection-2-{self.unique_suffix}",
            unique=True
        )
        
        self.feed3 = create_test_threat_feed(
            owner=self.organization2,
            name_suffix=f"feed_3_{self.unique_suffix}",
            is_external=True,
            is_public=False,
            taxii_server_url="https://test3.example.com/taxii",
            taxii_collection_id=f"collection-3-{self.unique_suffix}",
            unique=True
        )

    def tearDown(self):
        """Clean up after each test"""
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()

    def test_get_all(self):
        """Test retrieving all threat feeds"""
        feeds = self.repository.get_all()
        
        # Should return all 3 feeds
        self.assertEqual(len(feeds), 3)
        
        # Check that all feeds are returned
        feed_ids = [feed.id for feed in feeds]
        self.assertIn(self.feed1.id, feed_ids)
        self.assertIn(self.feed2.id, feed_ids)
        self.assertIn(self.feed3.id, feed_ids)

    def test_get_by_id(self):
        """Test retrieving a threat feed by ID"""
        # Get the first feed by ID
        feed = self.repository.get_by_id(self.feed1.id)
        
        # Check that the correct feed was retrieved
        self.assertEqual(feed.id, self.feed1.id)
        self.assertEqual(feed.name, self.feed1.name)
        
        # Test with non-existent ID
        feed = self.repository.get_by_id(999999)
        self.assertIsNone(feed)

    def test_get_external_feeds(self):
        """Test retrieving only external threat feeds"""
        external_feeds = self.repository.get_external_feeds()
        
        # Should return 2 external feeds (feed1 and feed3)
        self.assertEqual(len(external_feeds), 2)
        
        # Check that all returned feeds are external
        for feed in external_feeds:
            self.assertTrue(feed.is_external)
        
        # Check that the correct feeds are returned
        external_feed_ids = [feed.id for feed in external_feeds]
        self.assertIn(self.feed1.id, external_feed_ids)
        self.assertIn(self.feed3.id, external_feed_ids)
        self.assertNotIn(self.feed2.id, external_feed_ids)

    def test_get_public_feeds(self):
        """Test retrieving only public threat feeds"""
        public_feeds = self.repository.get_public_feeds()
        
        # Should return 1 public feed (feed2)
        self.assertEqual(len(public_feeds), 1)
        
        # Check that all returned feeds are public
        for feed in public_feeds:
            self.assertTrue(feed.is_public)
        
        # Check that the correct feed is returned
        self.assertEqual(public_feeds[0].id, self.feed2.id)

    def test_get_by_owner(self):
        """Test retrieving feeds by owner organization"""
        # Get feeds owned by organization1
        org1_feeds = self.repository.get_by_owner(self.organization1)
        
        # Should return 2 feeds (feed1 and feed2)
        self.assertEqual(len(org1_feeds), 2)
        
        # Check that all feeds belong to organization1
        for feed in org1_feeds:
            self.assertEqual(feed.owner.id, self.organization1.id)
        
        # Get feeds owned by organization2
        org2_feeds = self.repository.get_by_owner(self.organization2)
        
        # Should return 1 feed (feed3)
        self.assertEqual(len(org2_feeds), 1)
        self.assertEqual(org2_feeds[0].id, self.feed3.id)

    def test_create(self):
        """Test creating a new threat feed"""
        feed_data = {
            'name': f'New Feed {self.unique_suffix}',
            'description': 'A new test feed',
            'owner': self.organization1,
            'is_external': True,
            'is_public': False,
            'taxii_server_url': 'https://new.example.com/taxii',
            'taxii_collection_id': f'new-collection-{get_unique_identifier()}'  # Add unique collection ID
        }
        
        new_feed = self.repository.create(feed_data)
        
        # Check that the feed was created correctly
        self.assertIsNotNone(new_feed.id)
        self.assertEqual(new_feed.name, feed_data['name'])
        self.assertEqual(new_feed.description, 'A new test feed')
        self.assertEqual(new_feed.owner.id, self.organization1.id)
        self.assertTrue(new_feed.is_external)
        self.assertFalse(new_feed.is_public)
        
        # Check that it was saved to the database
        feed_in_db = ThreatFeed.objects.get(id=new_feed.id)
        self.assertEqual(feed_in_db.name, feed_data['name'])

    def test_update(self):
        """Test updating an existing threat feed"""
        # Update the first feed
        update_data = {
            'name': f'Updated Feed 1 - {self.unique_suffix}',
            'description': 'Updated description',
            'is_public': True,
            'taxii_server_url': 'https://test1.example.com/taxii'
        }
        
        updated_feed = self.repository.update(self.feed1.id, update_data)
        
        # Check that the feed was updated correctly
        self.assertEqual(updated_feed.id, self.feed1.id)
        self.assertEqual(updated_feed.name, update_data['name'])
        self.assertEqual(updated_feed.description, 'Updated description')
        self.assertTrue(updated_feed.is_public)
        
        # URL should be updated
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
        Organization.objects.all().delete()
        User.objects.all().delete()
        
        self.repository = IndicatorRepository()
        
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create test user
        self.user = User.objects.create_user(
            username=get_unique_username('indicator_test'),
            password='testpass123',
            email=get_unique_email('indicator_test')
        )
        
        # Create Organization first
        self.organization = create_test_organization(
            name_suffix=f"indicator_test_{self.unique_suffix}",
            created_by=self.user,
            unique=True
        )
        
        # Create a test threat feed
        self.feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"indicator_feed_{self.unique_suffix}",
            taxii_collection_id=f"indicator-collection-{self.unique_suffix}",  # Added unique collection ID
            unique=True
        )
        
        # Create test indicators with unique values
        self.indicator1 = create_test_indicator(
            threat_feed=self.feed,
            value=f'192.168.1.{get_unique_identifier()[:3]}',  # More unique IP
            type='ip',
            confidence=70,
            unique=True
        )
        
        self.indicator2 = create_test_indicator(
            threat_feed=self.feed,
            value=f'malicious-{get_unique_identifier()}.example.com',  # More unique domain
            type='domain',
            confidence=80,
            unique=True
        )
        
        self.indicator3 = create_test_indicator(
            threat_feed=self.feed,
            value=f'http://bad-{get_unique_identifier()}.example.com/malware',  # More unique URL
            type='url',
            confidence=90,
            unique=True
        )

    def tearDown(self):
        """Clean up after each test"""
        Indicator.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()

    def test_get_all(self):
        """Test retrieving all indicators"""
        indicators = self.repository.get_all()
        
        # Should return all 3 indicators
        self.assertEqual(len(indicators), 3)
        
        # Check that all indicators are returned by ID
        indicator_ids = [ind.id for ind in indicators]
        self.assertIn(self.indicator1.id, indicator_ids)
        self.assertIn(self.indicator2.id, indicator_ids)
        self.assertIn(self.indicator3.id, indicator_ids)

    def test_get_by_feed(self):
        """Test retrieving indicators by threat feed"""
        indicators = self.repository.get_by_feed(self.feed)
        
        # Should return all 3 indicators from this feed
        self.assertEqual(len(indicators), 3)
        
        # Check that all indicators belong to the feed
        for indicator in indicators:
            self.assertEqual(indicator.threat_feed.id, self.feed.id)

    def test_get_by_type(self):
        """Test retrieving indicators by type"""
        # Get IP indicators
        ip_indicators = self.repository.get_by_type('ip')
        self.assertEqual(len(ip_indicators), 1)
        self.assertEqual(ip_indicators[0].type, 'ip')
        
        # Get domain indicators
        domain_indicators = self.repository.get_by_type('domain')
        self.assertEqual(len(domain_indicators), 1)
        self.assertEqual(domain_indicators[0].type, 'domain')

    def test_get_high_confidence(self):
        """Test retrieving high-confidence indicators"""
        # Get indicators with confidence >= 80
        high_conf_indicators = self.repository.get_high_confidence(80)
        
        # Should return 2 indicators (domain and URL with 80 and 90 confidence)
        self.assertEqual(len(high_conf_indicators), 2)
        
        # Check that all returned indicators have confidence >= 80
        for indicator in high_conf_indicators:
            self.assertGreaterEqual(indicator.confidence, 80)


class TTPRepositoryTestCase(TransactionTestCase):
    """Test cases for the TTPRepository - Using TransactionTestCase for better isolation"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()
        
        self.repository = TTPRepository()
        
        # Create unique suffix for this test
        self.unique_suffix = get_unique_identifier()
        
        # Create test user
        self.user = User.objects.create_user(
            username=get_unique_username('ttp_test'),
            password='testpass123',
            email=get_unique_email('ttp_test')
        )
        
        # Create an Organization first
        self.organization = create_test_organization(
            name_suffix=f"ttp_test_{self.unique_suffix}",
            created_by=self.user,
            unique=True
        )
        
        # Create a test threat feed
        self.feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"ttp_feed_{self.unique_suffix}",
            taxii_collection_id=f"ttp-collection-{self.unique_suffix}",  # Added unique collection ID
            unique=True
        )
        
        # Create test TTPs with specific data that tests expect
        self.ttp1 = create_test_ttp(
            threat_feed=self.feed,
            name=f'Phishing Attack {self.unique_suffix}',
            description='Test Phishing TTP',
            mitre_technique_id='T1566.001',
            mitre_tactic='initial-access',
            unique=True
        )
        
        self.ttp2 = create_test_ttp(
            threat_feed=self.feed,
            name=f'Credential Dumping {self.unique_suffix}',
            description='Test Credential Dumping TTP',
            mitre_technique_id='T1003',
            mitre_tactic='credential-access',
            unique=True
        )
        
        self.ttp3 = create_test_ttp(
            threat_feed=self.feed,
            name=f'Data Exfiltration {self.unique_suffix}',
            description='Test Data Exfiltration TTP',
            mitre_technique_id='T1041',
            mitre_tactic='exfiltration',
            unique=True
        )

    def tearDown(self):
        """Clean up after each test"""
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()

    def test_get_all(self):
        """Test retrieving all TTPs"""
        ttps = self.repository.get_all()
        
        # Should return all 3 TTPs
        self.assertEqual(len(ttps), 3)
        
        # Check that all TTPs are returned by ID
        ttp_ids = [ttp.id for ttp in ttps]
        self.assertIn(self.ttp1.id, ttp_ids)
        self.assertIn(self.ttp2.id, ttp_ids)
        self.assertIn(self.ttp3.id, ttp_ids)

    def test_get_by_feed(self):
        """Test retrieving TTPs by threat feed"""
        ttps = self.repository.get_by_feed(self.feed)
        
        # Should return all 3 TTPs from this feed
        self.assertEqual(len(ttps), 3)
        
        # Check that all TTPs belong to the feed
        for ttp in ttps:
            self.assertEqual(ttp.threat_feed.id, self.feed.id)

    def test_get_by_tactic(self):
        """Test retrieving TTPs by MITRE tactic"""
        # Get initial-access TTPs
        initial_access_ttps = self.repository.get_by_tactic('initial-access')
        self.assertEqual(len(initial_access_ttps), 1)
        self.assertEqual(initial_access_ttps[0].mitre_tactic, 'initial-access')
        
        # Get credential-access TTPs
        cred_access_ttps = self.repository.get_by_tactic('credential-access')
        self.assertEqual(len(cred_access_ttps), 1)
        self.assertEqual(cred_access_ttps[0].mitre_tactic, 'credential-access')

    def test_get_by_technique(self):
        """Test retrieving TTPs by MITRE technique ID"""
        # Get T1566.001 TTPs (Phishing)
        phishing_ttps = self.repository.get_by_technique('T1566.001')
        self.assertEqual(len(phishing_ttps), 1)
        self.assertEqual(phishing_ttps[0].mitre_technique_id, 'T1566.001')
        
        # Get T1003 TTPs (Credential Dumping)
        cred_dump_ttps = self.repository.get_by_technique('T1003')
        self.assertEqual(len(cred_dump_ttps), 1)
        self.assertEqual(cred_dump_ttps[0].mitre_technique_id, 'T1003')

    def test_search_by_name(self):
        """Test searching TTPs by name"""
        # Search for TTPs containing "Phishing"
        phishing_ttps = self.repository.search_by_name('Phishing')
        self.assertEqual(len(phishing_ttps), 1)
        self.assertEqual(phishing_ttps[0].id, self.ttp1.id)  
        
        # Search for TTPs containing part of the unique suffix
        suffix_ttps = self.repository.search_by_name(self.unique_suffix[:5])
        self.assertEqual(len(suffix_ttps), 3) 
        
        # Search for non-existent name
        no_results = self.repository.search_by_name('NonExistent12345')
        self.assertEqual(len(no_results), 0)


if __name__ == '__main__':
    unittest.main()