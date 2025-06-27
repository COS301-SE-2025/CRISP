"""
Unit tests for STIX factory pattern implementations
"""
import os
import sys
import django
import unittest

# Add the project root to Python path for standalone execution
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, project_root)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
    django.setup()

from unittest.mock import patch, MagicMock
import json
from datetime import datetime
import pytz
from django.test import TestCase
from django.utils import timezone

try:
    from ..patterns.factory.stix_indicator_creator import StixIndicatorCreator
    from ..patterns.factory.stix_ttp_creator import StixTTPCreator
    from ..models.indicator import Indicator
    from ..models.ttp_data import TTPData
    from ..models.threat_feed import ThreatFeed
    from ..tests.test_stix_mock_data import STIX20_BUNDLE, STIX21_BUNDLE
except ImportError:
    # Fallback for standalone execution
    from core.patterns.factory.stix_indicator_creator import StixIndicatorCreator
    from core.patterns.factory.stix_ttp_creator import StixTTPCreator
    from core.models.indicator import Indicator
    from core.models.ttp_data import TTPData
    from core.models.threat_feed import ThreatFeed
    from core.tests.test_stix_mock_data import STIX20_BUNDLE, STIX21_BUNDLE


class StixIndicatorCreatorTestCase(TestCase):
    """Test cases for the StixIndicatorCreator factory"""

    def setUp(self):
        """Set up the test environment"""
        self.indicator_creator = StixIndicatorCreator()
        
        # Create a mock ThreatFeed for testing
        self.threat_feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Factory",
            is_external=True
        )
        
        # Create a mock Indicator for testing
        self.indicator = Indicator.objects.create(
            threat_feed=self.threat_feed,
            type='domain',
            value='malicious-domain.com',
            description='Test Indicator',
            confidence=80,
            stix_id='indicator--test-123',
            created_at=timezone.now(),
            is_anonymized=False
        )
        
        # Parse a STIX 2.0 indicator from the mock data
        self.stix20_indicator = next(obj for obj in STIX20_BUNDLE['objects'] if obj['type'] == 'indicator')
        
        # Parse a STIX 2.1 indicator from the mock data
        self.stix21_indicator = next(obj for obj in STIX21_BUNDLE['objects'] if obj['type'] == 'indicator')

    def test_create_from_stix20_indicator(self):
        """Test creating a CRISP Indicator from a STIX 2.0 indicator"""
        # Create a MagicMock STIX object with the properties from our JSON
        mock_stix_obj = MagicMock()
        for key, value in self.stix20_indicator.items():
            setattr(mock_stix_obj, key, value)
        
        # Convert timestamp strings to datetime objects
        mock_stix_obj.created = datetime.strptime(mock_stix_obj.created, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        mock_stix_obj.modified = datetime.strptime(mock_stix_obj.modified, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        
        # Create Indicator from STIX object
        indicator_data = self.indicator_creator.create_from_stix(mock_stix_obj)
        
        # Check the created indicator data
        self.assertEqual(indicator_data['type'], 'domain')
        self.assertEqual(indicator_data['value'], 'evil-domain.com')
        self.assertEqual(indicator_data['stix_id'], 'indicator--29aba82c-5393-42a8-9edb-6a2cb1df0a2c')
        self.assertEqual(indicator_data['description'], 'Domain associated with recent phishing campaign')
        self.assertEqual(indicator_data['confidence'], 85)
        self.assertFalse(indicator_data['is_anonymized'])

    def test_create_from_stix21_indicator(self):
        """Test creating a CRISP Indicator from a STIX 2.1 indicator"""
        # Create a MagicMock STIX object with the properties from our JSON
        mock_stix_obj = MagicMock()
        for key, value in self.stix21_indicator.items():
            setattr(mock_stix_obj, key, value)
        
        # Convert timestamp strings to datetime objects
        mock_stix_obj.created = datetime.strptime(mock_stix_obj.created, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        mock_stix_obj.modified = datetime.strptime(mock_stix_obj.modified, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        
        # Create Indicator from STIX object
        indicator_data = self.indicator_creator.create_from_stix(mock_stix_obj)
        
        # Check the created indicator data
        self.assertEqual(indicator_data['type'], 'file_hash')
        self.assertEqual(indicator_data['stix_id'], 'indicator--8d12f4d7-e50d-4535-aab9-f017a534cc75')
        self.assertEqual(indicator_data['description'], 'SHA-256 hash of a malicious executable file')
        self.assertEqual(indicator_data['confidence'], 90)
        self.assertFalse(indicator_data['is_anonymized'])

    def test_create_stix_object_from_indicator(self):
        """Test creating a STIX object from a CRISP Indicator"""
        # Create a STIX object from our indicator
        stix_obj = self.indicator_creator.create_stix_object(self.indicator)
        
        # Check the created STIX object
        self.assertEqual(stix_obj.type, 'indicator')
        self.assertEqual(stix_obj.pattern, "[domain-name:value = 'malicious-domain.com']")
        self.assertEqual(stix_obj.description, 'Test Indicator')
        self.assertEqual(stix_obj.confidence, 80)
        
    def test_parse_indicator_pattern(self):
        """Test parsing indicator patterns correctly"""
        # Test IPv4 pattern
        type_value = self.indicator_creator._parse_indicator_pattern("[ipv4-addr:value = '192.168.1.1']")
        self.assertEqual(type_value[0], 'ip')
        self.assertEqual(type_value[1], '192.168.1.1')
        
        # Test domain pattern
        type_value = self.indicator_creator._parse_indicator_pattern("[domain-name:value = 'evil.com']")
        self.assertEqual(type_value[0], 'domain')
        self.assertEqual(type_value[1], 'evil.com')
        
        # Test URL pattern
        type_value = self.indicator_creator._parse_indicator_pattern("[url:value = 'https://malicious.com/path']")
        self.assertEqual(type_value[0], 'url')
        self.assertEqual(type_value[1], 'https://malicious.com/path')
        
        # Test file hash pattern
        type_value = self.indicator_creator._parse_indicator_pattern("[file:hashes.MD5 = '5eb63bbbe01eeed093cb22bb8f5acdc3']")
        self.assertEqual(type_value[0], 'file_hash')
        self.assertEqual(type_value[1], '5eb63bbbe01eeed093cb22bb8f5acdc3')
        
    def test_create_stix_pattern(self):
        """Test creating STIX patterns correctly"""
        # Test IP pattern
        pattern = self.indicator_creator._create_stix_pattern('ip', '192.168.1.1')
        self.assertEqual(pattern, "[ipv4-addr:value = '192.168.1.1']")
        
        # Test domain pattern
        pattern = self.indicator_creator._create_stix_pattern('domain', 'evil.com')
        self.assertEqual(pattern, "[domain-name:value = 'evil.com']")
        
        # Test URL pattern
        pattern = self.indicator_creator._create_stix_pattern('url', 'https://malicious.com')
        self.assertEqual(pattern, "[url:value = 'https://malicious.com']")
        
        # Test file hash pattern
        pattern = self.indicator_creator._create_stix_pattern('file_hash', 'abcdef123456')
        self.assertEqual(pattern, "[file:hashes.MD5 = 'abcdef123456']")
        
        # Test unknown type
        pattern = self.indicator_creator._create_stix_pattern('unknown', 'some-value')
        self.assertEqual(pattern, "[x-custom-indicator:value = 'some-value']")


class StixTTPCreatorTestCase(TestCase):
    """Test cases for the StixTTPCreator factory"""

    def setUp(self):
        """Set up the test environment."""
        self.ttp_creator = StixTTPCreator()
        
        # Create a mock ThreatFeed for testing
        self.threat_feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Factory",
            is_external=True
        )
        
        # Create a mock TTPData for testing
        self.ttp = TTPData.objects.create(
            threat_feed=self.threat_feed,
            name='Phishing Attack',
            description='Test TTP',
            mitre_technique_id='T1566.001',
            mitre_tactic='initial_access',
            stix_id='attack-pattern--test-123',
            created_at=timezone.now(),
            is_anonymized=False
        )
        
        # Parse a STIX 2.0 attack pattern from the mock data
        self.stix20_ttp = next(obj for obj in STIX20_BUNDLE['objects'] if obj['type'] == 'attack-pattern')
        
        # Parse a STIX 2.1 attack pattern from the mock data
        self.stix21_ttp = next(obj for obj in STIX21_BUNDLE['objects'] if obj['type'] == 'attack-pattern')

    def test_create_from_stix20_ttp(self):
        """Test creating a CRISP TTP from a STIX 2.0 attack pattern"""
        # Create a MagicMock STIX object with the properties from our JSON
        mock_stix_obj = MagicMock()
        for key, value in self.stix20_ttp.items():
            setattr(mock_stix_obj, key, value)
        
        # Convert timestamp strings to datetime objects
        mock_stix_obj.created = datetime.strptime(mock_stix_obj.created, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        mock_stix_obj.modified = datetime.strptime(mock_stix_obj.modified, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        
        # Create TTP from STIX object
        ttp_data = self.ttp_creator.create_from_stix(mock_stix_obj)
        
        # Check the created TTP data
        self.assertEqual(ttp_data['name'], 'Spear Phishing with Malicious Attachment')
        self.assertEqual(ttp_data['stix_id'], 'attack-pattern--7e33a43e-e34b-40ec-89da-36c9bb2caff5')
        self.assertIn('spear phishing', ttp_data['description'].lower())
        self.assertEqual(ttp_data['mitre_technique_id'], 'T1566.001')
        self.assertEqual(ttp_data['mitre_tactic'], 'initial_access')
        self.assertFalse(ttp_data['is_anonymized'])

    def test_create_from_stix21_ttp(self):
        """Test creating a CRISP TTP from a STIX 2.1 attack pattern"""
        # Create a MagicMock STIX object with the properties from our JSON
        mock_stix_obj = MagicMock()
        for key, value in self.stix21_ttp.items():
            setattr(mock_stix_obj, key, value)
        
        # Convert timestamp strings to datetime objects
        mock_stix_obj.created = datetime.strptime(mock_stix_obj.created, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        mock_stix_obj.modified = datetime.strptime(mock_stix_obj.modified, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        
        # Create TTP from STIX object
        ttp_data = self.ttp_creator.create_from_stix(mock_stix_obj)
        
        # Check the created TTP data
        self.assertEqual(ttp_data['name'], 'Drive-by Compromise')
        self.assertEqual(ttp_data['stix_id'], 'attack-pattern--d18f4181-1782-4202-9141-d47d3cc9f95a')
        self.assertIn('compromised website', ttp_data['description'].lower())
        self.assertEqual(ttp_data['mitre_technique_id'], 'T1189')
        self.assertEqual(ttp_data['mitre_tactic'], 'initial_access')
        self.assertFalse(ttp_data['is_anonymized'])

    def test_create_stix_object_from_ttp(self):
        """Test creating a STIX attack pattern from a CRISP TTP."""
        # Create a STIX object from our TTP
        stix_obj = self.ttp_creator.create_stix_object(self.ttp)
        
        # Check the created STIX object
        self.assertEqual(stix_obj.type, 'attack-pattern')
        self.assertEqual(stix_obj.name, 'Phishing Attack')
        self.assertEqual(stix_obj.description, 'Test TTP')
        
        # Check external references (MITRE ATT&CK)
        self.assertTrue(hasattr(stix_obj, 'external_references'))
        self.assertEqual(len(stix_obj.external_references), 1)
        self.assertEqual(stix_obj.external_references[0]['source_name'], 'mitre-attack')
        self.assertEqual(stix_obj.external_references[0]['external_id'], 'T1566.001')
        
        # Check kill chain phases
        self.assertTrue(hasattr(stix_obj, 'kill_chain_phases'))
        self.assertEqual(len(stix_obj.kill_chain_phases), 1)
        self.assertEqual(stix_obj.kill_chain_phases[0]['kill_chain_name'], 'mitre-attack')
        self.assertEqual(stix_obj.kill_chain_phases[0]['phase_name'], 'initial_access')


if __name__ == '__main__':
    unittest.main()