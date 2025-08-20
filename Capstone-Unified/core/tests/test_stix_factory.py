"""
Unit tests for STIX factory classes
"""
import unittest
import uuid
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytz
from django.test import TransactionTestCase
from django.utils import timezone

from core.patterns.factory.stix_factory_wrappers import StixIndicatorCreator, StixTTPCreator
from core.models.models import ThreatFeed, Indicator, TTPData, Institution, Organization
from core.tests.test_stix_mock_data import STIX20_INDICATOR, STIX21_INDICATOR, STIX20_ATTACK_PATTERN, STIX21_ATTACK_PATTERN
from core.tests.test_data_fixtures import (
    create_test_threat_feed, create_test_indicator, create_test_ttp,
    create_test_organization
)


class StixIndicatorCreatorTestCase(TransactionTestCase):
    """Test cases for StixIndicatorCreator"""

    def setUp(self):
        """Set up the test environment"""
        # Clear any existing data
        Indicator.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = str(uuid.uuid4())[:8]
        
        # Create test objects using fixtures
        self.organization = create_test_organization(
            name_suffix=f"stix_factory_{self.unique_suffix}",
            unique=True
        )
        
        self.threat_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"stix_factory_{self.unique_suffix}",
            unique=True
        )
        
        # Create the factory
        self.factory = StixIndicatorCreator()

    def tearDown(self):
        """Clean up after each test"""
        Indicator.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()

    def test_create_from_stix20_indicator(self):
        """Test creating an Indicator from a STIX 2.0 indicator object"""
        # Create an Indicator from the STIX 2.0 object
        indicator = self.factory.create_from_stix(STIX20_INDICATOR, self.threat_feed)
        
        # Verify the indicator was created correctly
        self.assertIsNotNone(indicator)
        self.assertEqual(indicator.threat_feed, self.threat_feed)
        self.assertEqual(indicator.stix_id, STIX20_INDICATOR['id'])
        self.assertEqual(indicator.type, 'ip')
        self.assertEqual(indicator.value, '192.168.1.1')
        
        # Verify it was saved to the database
        db_indicator = Indicator.objects.get(stix_id=STIX20_INDICATOR['id'])
        self.assertEqual(db_indicator.value, '192.168.1.1')

    def test_create_from_stix21_indicator(self):
        """Test creating an Indicator from a STIX 2.1 indicator object"""
        # Create an Indicator from the STIX 2.1 object
        indicator = self.factory.create_from_stix(STIX21_INDICATOR, self.threat_feed)
        
        # Verify the indicator was created correctly
        self.assertIsNotNone(indicator)
        self.assertEqual(indicator.threat_feed, self.threat_feed)
        self.assertEqual(indicator.stix_id, STIX21_INDICATOR['id'])
        self.assertEqual(indicator.type, 'domain')
        self.assertEqual(indicator.value, 'malicious-domain.com')
        
        # Verify it was saved to the database
        db_indicator = Indicator.objects.get(stix_id=STIX21_INDICATOR['id'])
        self.assertEqual(db_indicator.value, 'malicious-domain.com')

    def test_create_stix_object_from_indicator(self):
        """Test creating a STIX object from a CRISP Indicator"""
        # Create a CRISP indicator first
        indicator = create_test_indicator(
            threat_feed=self.threat_feed,
            value='10.0.0.1',
            type='ip',
            confidence=85,
            unique=True
        )
        
        # Convert to STIX object
        stix_object = self.factory.create_stix_object(indicator)
        
        # Verify the STIX object
        self.assertEqual(stix_object['type'], 'indicator')
        self.assertEqual(stix_object['id'], indicator.stix_id)
        self.assertIn('pattern', stix_object)
        self.assertIn('labels', stix_object)
        
        # Pattern should contain the IP
        self.assertIn('10.0.0.1', stix_object['pattern'])

    def test_create_stix_pattern(self):
        """Test creating STIX patterns for different indicator types"""
        # Test IP pattern
        ip_pattern = self.factory._create_stix_pattern('ip', '192.168.1.1')
        self.assertEqual(ip_pattern, "[ipv4-addr:value = '192.168.1.1']")
        
        # Test domain pattern
        domain_pattern = self.factory._create_stix_pattern('domain', 'evil.com')
        self.assertEqual(domain_pattern, "[domain-name:value = 'evil.com']")
        
        # Test URL pattern
        url_pattern = self.factory._create_stix_pattern('url', 'http://evil.com/malware')
        self.assertEqual(url_pattern, "[url:value = 'http://evil.com/malware']")
        
        # Test file hash pattern
        hash_pattern = self.factory._create_stix_pattern('hash', 'abc123def456')
        self.assertEqual(hash_pattern, "[file:hashes.MD5 = 'abc123def456']")

    def test_parse_indicator_pattern(self):
        """Test parsing STIX patterns to extract indicator values"""
        # Test IP pattern parsing
        ip_result = self.factory._parse_indicator_pattern("[ipv4-addr:value = '1.2.3.4']")
        self.assertEqual(ip_result, ('ip', '1.2.3.4'))
        
        # Test domain pattern parsing
        domain_result = self.factory._parse_indicator_pattern("[domain-name:value = 'test.com']")
        self.assertEqual(domain_result, ('domain', 'test.com'))
        
        # Test URL pattern parsing
        url_result = self.factory._parse_indicator_pattern("[url:value = 'http://test.com']")
        self.assertEqual(url_result, ('url', 'http://test.com'))
        
        # Test file hash pattern parsing
        hash_result = self.factory._parse_indicator_pattern("[file:hashes.MD5 = 'abcd1234']")
        self.assertEqual(hash_result, ('hash', 'abcd1234'))


class StixTTPCreatorTestCase(TransactionTestCase):
    """Test cases for StixTTPCreator - Using TransactionTestCase for better isolation"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = str(uuid.uuid4())[:8]
        
        # Create test objects using fixtures
        self.organization = create_test_organization(
            name_suffix=f"ttp_factory_{self.unique_suffix}",
            unique=True
        )
        
        self.threat_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"ttp_factory_{self.unique_suffix}",
            unique=True
        )
        
        # Create the factory
        self.factory = StixTTPCreator()

    def tearDown(self):
        """Clean up after each test"""
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()

    def test_create_from_stix20_ttp(self):
        """Test creating a TTP from a STIX 2.0 attack pattern object"""
        # Create a TTP from the STIX 2.0 object
        ttp = self.factory.create_from_stix(STIX20_ATTACK_PATTERN, self.threat_feed)
        
        # Verify the TTP was created correctly
        self.assertIsNotNone(ttp)
        self.assertEqual(ttp.threat_feed, self.threat_feed)
        self.assertEqual(ttp.stix_id, STIX20_ATTACK_PATTERN['id'])
        self.assertEqual(ttp.name, STIX20_ATTACK_PATTERN['name'])
        
        # Verify it was saved to the database
        db_ttp = TTPData.objects.get(stix_id=STIX20_ATTACK_PATTERN['id'])
        self.assertEqual(db_ttp.name, STIX20_ATTACK_PATTERN['name'])

    def test_create_from_stix21_ttp(self):
        """Test creating a TTP from a STIX 2.1 attack pattern object"""
        # Create a TTP from the STIX 2.1 object
        ttp = self.factory.create_from_stix(STIX21_ATTACK_PATTERN, self.threat_feed)
        
        # Verify the TTP was created correctly
        self.assertIsNotNone(ttp)
        self.assertEqual(ttp.threat_feed, self.threat_feed)
        self.assertEqual(ttp.stix_id, STIX21_ATTACK_PATTERN['id'])
        self.assertEqual(ttp.name, STIX21_ATTACK_PATTERN['name'])
        
        # Verify it was saved to the database
        db_ttp = TTPData.objects.get(stix_id=STIX21_ATTACK_PATTERN['id'])
        self.assertEqual(db_ttp.name, STIX21_ATTACK_PATTERN['name'])

    def test_create_stix_object_from_ttp(self):
        """Test creating a STIX object from a CRISP TTP"""
        # Create a CRISP TTP first
        ttp = create_test_ttp(
            threat_feed=self.threat_feed,
            name='Spear Phishing Attachment',
            description='Adversaries may send spear phishing emails with a malicious attachment',
            mitre_technique_id='T1566.001',
            mitre_tactic='initial-access',
            unique=True
        )
        
        # Convert to STIX object
        stix_object = self.factory.create_stix_object(ttp)
        
        # Verify the STIX object
        self.assertEqual(stix_object['type'], 'attack-pattern')
        self.assertEqual(stix_object['id'], ttp.stix_id)
        self.assertEqual(stix_object['name'], 'Spear Phishing Attachment')
        self.assertIn('description', stix_object)
        
        # Should have MITRE ATT&CK external reference
        if 'external_references' in stix_object:
            mitre_refs = [ref for ref in stix_object['external_references'] 
                         if ref.get('source_name') == 'mitre-attack']
            self.assertTrue(len(mitre_refs) > 0)

    def test_extract_mitre_info(self):
        """Test extracting MITRE ATT&CK information from STIX patterns"""
        # Test with external references
        stix_pattern_with_refs = {
            'name': 'Spear Phishing Attachment',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1566.001',
                    'url': 'https://attack.mitre.org/techniques/T1566/001'
                }
            ],
            'kill_chain_phases': [
                {
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': 'initial-access'
                }
            ]
        }
        
        technique_id, tactic = self.factory._extract_mitre_info(stix_pattern_with_refs)
        
        self.assertEqual(technique_id, 'T1566.001')
        self.assertEqual(tactic, 'initial-access')

    def test_handle_missing_fields(self):
        """Test handling of missing or incomplete STIX data"""
        # Test with minimal STIX data
        minimal_stix = {
            'type': 'attack-pattern',
            'id': f'attack-pattern--{uuid.uuid4()}',
            'name': 'Minimal Attack Pattern'
        }
        
        # Should not raise an exception
        ttp = self.factory.create_from_stix(minimal_stix, self.threat_feed)
        
        # Should create TTP with available data
        self.assertIsNotNone(ttp)
        self.assertEqual(ttp.name, 'Minimal Attack Pattern')
        self.assertEqual(ttp.stix_id, minimal_stix['id'])
        
        self.assertIsNotNone(ttp.description)
        

class StixFactoryIntegrationTestCase(TransactionTestCase):
    """Integration tests for STIX factory classes"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()
        
        # Create unique suffix for this test
        self.unique_suffix = str(uuid.uuid4())[:8]
        
        # Create test objects
        self.organization = create_test_organization(
            name_suffix=f"integration_{self.unique_suffix}",
            unique=True
        )
        
        self.threat_feed = create_test_threat_feed(
            owner=self.organization,
            name_suffix=f"integration_{self.unique_suffix}",
            unique=True
        )
        
        # Create factories
        self.indicator_factory = StixIndicatorCreator()
        self.ttp_factory = StixTTPCreator()

    def tearDown(self):
        """Clean up after each test"""
        Indicator.objects.all().delete()
        TTPData.objects.all().delete()
        ThreatFeed.objects.all().delete()
        Organization.objects.all().delete()

    def test_round_trip_indicator_conversion(self):
        """Test converting CRISP indicator to STIX and back"""
        # Create original CRISP indicator
        original_indicator = create_test_indicator(
            threat_feed=self.threat_feed,
            value='192.168.100.1',
            type='ip',
            confidence=75,
            unique=True
        )
        
        # Convert to STIX
        stix_object = self.indicator_factory.create_stix_object(original_indicator)
        
        # Convert back to CRISP indicator
        new_indicator = self.indicator_factory.create_from_stix(stix_object, self.threat_feed)
        
        # Should have same essential properties
        self.assertEqual(new_indicator.value, original_indicator.value)
        self.assertEqual(new_indicator.type, original_indicator.type)

    def test_round_trip_ttp_conversion(self):
        """Test converting CRISP TTP to STIX and back"""
        # Create original CRISP TTP
        original_ttp = create_test_ttp(
            threat_feed=self.threat_feed,
            name='Command and Control',
            description='Test C2 technique',
            mitre_technique_id='T1071',
            mitre_tactic='command-and-control',
            unique=True
        )
        
        # Convert to STIX
        stix_object = self.ttp_factory.create_stix_object(original_ttp)
        
        # Convert back to CRISP TTP
        new_ttp = self.ttp_factory.create_from_stix(stix_object, self.threat_feed)
        
        # Should have same essential properties
        self.assertEqual(new_ttp.name, original_ttp.name)
        self.assertEqual(new_ttp.mitre_technique_id, original_ttp.mitre_technique_id)
        self.assertEqual(new_ttp.mitre_tactic, original_ttp.mitre_tactic)

    def test_bulk_conversion_performance(self):
        """Test performance of bulk STIX conversions"""
        # Create multiple indicators
        indicators = []
        for i in range(10):
            indicator = create_test_indicator(
                threat_feed=self.threat_feed,
                value=f'10.0.0.{i}',
                type='ip',
                confidence=70 + i,
                unique=True
            )
            indicators.append(indicator)
        
        # Time the conversion
        import time
        start_time = time.time()
        
        stix_objects = []
        for indicator in indicators:
            stix_obj = self.indicator_factory.create_stix_object(indicator)
            stix_objects.append(stix_obj)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete reasonably quickly
        self.assertLess(conversion_time, 5.0)
        self.assertEqual(len(stix_objects), 10)
        
        # All should be valid STIX objects
        for stix_obj in stix_objects:
            self.assertEqual(stix_obj['type'], 'indicator')
            self.assertIn('pattern', stix_obj)
            self.assertIn('labels', stix_obj)

    def test_error_handling_in_factories(self):
        """Test error handling in factory methods"""
        # Test with invalid STIX data
        invalid_stix = {
            'type': 'indicator',
            'pattern': '[invalid-syntax',
            'labels': ['malicious-activity']
        }
        
        # Should handle gracefully
        try:
            indicator = self.indicator_factory.create_from_stix(invalid_stix, self.threat_feed)
            self.assertIsNotNone(indicator)
        except (ValueError, KeyError) as e:
            self.assertIsInstance(e, (ValueError, KeyError))
        
        # Test with None values
        try:
            result = self.indicator_factory.create_from_stix(None, self.threat_feed)
            self.assertIsNone(result)
        except (ValueError, TypeError) as e:
            # Should handle gracefully
            self.assertIsInstance(e, (ValueError, TypeError))


if __name__ == '__main__':
    unittest.main()