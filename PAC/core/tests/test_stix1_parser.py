"""
Unit tests for STIX 1.x parser functionality
"""
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
import xml.etree.ElementTree as ET
from django.test import TestCase
from django.utils import timezone

from core.parsers.stix1_parser import STIX1Parser
from core.models.models import ThreatFeed
from core.models.models import Indicator
from core.models.models import TTPData
from core.models.models import Institution
from core.models.models import Organization
from core.tests.test_data_fixtures import create_test_threat_feed
from core.tests.test_stix_mock_data import STIX1_INDICATOR_XML, STIX1_TTP_XML, TAXII1_CONTENT_BLOCK, INVALID_XML


class STIX1ParserTestCase(TestCase):
    """Test cases for the STIX 1.x parser functionality"""

    def setUp(self):
        """Set up the test environment"""
        # Clear any existing data  
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()

        # Create Organization first to satisfy owner constraint
        self.organization = Organization.objects.create(
            name=f"Test Organization - {timezone.now().timestamp()}",
            description="Test Organization for STIX1 Parser",
            identity_class="organization",
            organization_type="university",
            contact_email="test@example.com"
        )

        from core.tests.test_data_fixtures import create_test_threat_feed
        #Ensure ThreatFeed has proper owner to avoid constraint violation
        self.threat_feed = create_test_threat_feed(owner=self.organization)
        
        # Create parser
        self.parser = STIX1Parser()

    def test_update_existing_indicator(self):
        """Test updating an existing indicator"""
        # Create ThreatFeed with owner to avoid constraint violation
        threat_feed = create_test_threat_feed(
            owner=self.organization, 
            name='Test Feed Update'
        )
        
        # Create initial indicator
        original_indicator = Indicator.objects.create(
            threat_feed=threat_feed,
            value='192.168.1.1',
            type='ip',
            confidence=50,
            stix_id='indicator--12345',
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        # Parse content block with updated indicator
        parser = STIX1Parser()
        stats = parser.parse_content_block(TAXII1_CONTENT_BLOCK, threat_feed)
        
        # Check that indicator was updated
        updated_indicator = Indicator.objects.get(stix_id='indicator--12345')
        self.assertNotEqual(updated_indicator.confidence, 50)

    def test_parse_stix1_ttp(self):
        """Test parsing a STIX 1.x TTP from XML content"""
        # Parse the mock content
        stats = self.parser.parse_content_block(STIX1_TTP_XML, self.threat_feed)
        
        # Check the statistics
        self.assertEqual(stats['ttp_created'], 1)
        self.assertEqual(stats['ttp_updated'], 0)
        self.assertEqual(stats['errors'], 0)
        
        # Verify that a TTP was created in the database
        ttps = TTPData.objects.filter(threat_feed=self.threat_feed)
        self.assertEqual(ttps.count(), 1)
        
        # Check TTP properties
        ttp = ttps.first()
        self.assertIsNotNone(ttp.stix_id)
        self.assertEqual(ttp.name, 'Common Ransomware Delivery Method')
        self.assertIn('spear phishing', ttp.description.lower())

    def test_parse_content_block(self):
        """Test parsing a TAXII 1.x content block"""
        # Create a mock content block similar to what would be received from TAXII 1.x
        from core.tests.test_stix_mock_data import TAXII1_CONTENT_BLOCK
        content_block = TAXII1_CONTENT_BLOCK
        
        # Parse the content block - FIX: Use .content instead of ['content']
        stats = self.parser.parse_content_block(content_block.content, self.threat_feed)
        
        # Check the statistics
        self.assertEqual(stats['indicators_created'], 1)
        self.assertEqual(stats['errors'], 0)
        
        # Verify indicator was created successfully
        indicators = Indicator.objects.filter(threat_feed=self.threat_feed)
        self.assertEqual(indicators.count(), 1)

    def test_update_existing_indicator(self):
        """Test updating an existing indicator"""
        # Create a threat feed
        threat_feed = self.threat_feed
        
        # Create an indicator first
        indicator = Indicator.objects.create(
            threat_feed=self.threat_feed,
            value='192.168.1.1',
            type='ip',
            description='Original description',
            confidence=50,
            stix_id='example:indicator-1',
            first_seen=timezone.now(),
            last_seen=timezone.now()  
        )
        
        parser = STIX1Parser()
        stats = parser.parse_content_block(STIX1_INDICATOR_XML, threat_feed)
        
        # Refresh the indicator from database
        indicator.refresh_from_db()
        
        # Assert it was updated
        self.assertEqual(stats['indicators_updated'], 1)
        self.assertEqual(stats['indicators_created'], 0)
        self.assertEqual(indicator.description, 'This is a test indicator')

    def test_parse_invalid_xml(self):
        """Test handling of invalid XML content"""
        parser = STIX1Parser()
        stats = parser.parse_content_block(INVALID_XML)
        
        print(f"INVALID XML TEST STATS: {stats}")
        
        self.assertEqual(stats['errors'], 1)

    def test_parse_without_threat_feed(self):
        """Test parsing content without providing a threat feed."""
        # Parse without a threat feed (should skip creation but not error)
        stats = self.parser.parse_content_block(STIX1_INDICATOR_XML, None)
        
        # Check that it was skipped
        self.assertEqual(stats['skipped'], 1)
        self.assertEqual(stats['indicators_created'], 0)
        
        # No indicators should be created
        self.assertEqual(Indicator.objects.count(), 0)

    @patch('core.parsers.stix1_parser.ET.parse')
    def test_handle_parse_exception(self, mock_parse):
        """Test handling of exceptions during parsing."""
        # Mock the ET.parse to raise an exception
        mock_parse.side_effect = ET.ParseError("Test parse error")
        
        # Attempt to parse
        stats = self.parser.parse_content_block(STIX1_INDICATOR_XML, self.threat_feed)
        
        # Check that the error was handled
        self.assertEqual(stats['errors'], 1)


if __name__ == '__main__':
    unittest.main()