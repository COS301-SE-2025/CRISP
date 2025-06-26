"""
Unit tests for STIX 1.x parser functionality
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
from unittest.mock import patch, MagicMock
from io import BytesIO
import xml.etree.ElementTree as ET
from django.test import TestCase
from django.utils import timezone

try:
    from ..parsers.stix1_parser import STIX1Parser
except ImportError:
    # Fallback for standalone execution
    from core.parsers.stix1_parser import STIX1Parser
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
    from ..tests.test_stix_mock_data import STIX1_INDICATOR_XML, STIX1_TTP_XML, TAXII1_CONTENT_BLOCK, INVALID_XML
except ImportError:
    # Fallback for standalone execution
    from core.tests.test_stix_mock_data import STIX1_INDICATOR_XML, STIX1_TTP_XML, TAXII1_CONTENT_BLOCK, INVALID_XML


class STIX1ParserTestCase(TestCase):
    """Test cases for the STIX 1.x parser functionality"""

    def setUp(self):
        """Set up the test environment"""
        # Clear any existing data to ensure clean tests
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        
        self.parser = STIX1Parser()
        self.threat_feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Parser",
            is_external=True,
            taxii_server_url="https://test.taxii.server/taxii",
            taxii_api_root="api",
            taxii_collection_id="test-collection"
        )

    def test_parse_stix1_indicator(self):
        """Test parsing a STIX 1.x indicator from XML content"""
        # Parse the mock content
        stats = self.parser.parse_content_block(STIX1_INDICATOR_XML, self.threat_feed)
        
        # Check the statistics
        self.assertEqual(stats['indicators_created'], 1)
        self.assertEqual(stats['indicators_updated'], 0)
        self.assertEqual(stats['errors'], 0)
        
        # Verify that an indicator was created in the database
        indicators = Indicator.objects.filter(threat_feed=self.threat_feed)
        self.assertEqual(indicators.count(), 1)
        
        # Check indicator properties
        indicator = indicators.first()
        self.assertIsNotNone(indicator.stix_id)
        self.assertEqual(indicator.type, 'ip')

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
        content_block = TAXII1_CONTENT_BLOCK
        
        # Parse the content block
        stats = self.parser.parse_content_block(content_block['content'], self.threat_feed)
        
        # Check the statistics
        self.assertEqual(stats['indicators_created'], 1)
        self.assertEqual(stats['errors'], 0)
        
        # Verify indicator was created
        indicators = Indicator.objects.filter(threat_feed=self.threat_feed)
        self.assertEqual(indicators.count(), 1)

    def test_update_existing_indicator(self):
        """Test updating an existing indicator"""
        # Create a threat feed
        threat_feed = ThreatFeed.objects.create(name='Test Feed')
        
        # Create an indicator first
        indicator = Indicator.objects.create(
            threat_feed=threat_feed,
            type='ip',
            value='192.168.1.1',
            stix_id='example:indicator-1',
            description='Original description'
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

    @patch('core.parsers.stix1_parser.ET.fromstring')
    def test_handle_parse_exception(self, mock_fromstring):
        """Test handling of exceptions during parsing."""
        # Mock the ET.fromstring to raise an exception
        mock_fromstring.side_effect = ET.ParseError("Test parse error")
        
        # Attempt to parse
        stats = self.parser.parse_content_block(STIX1_INDICATOR_XML, self.threat_feed)
        
        # Check that the error was handled
        self.assertEqual(stats['errors'], 1)


if __name__ == '__main__':
    unittest.main()