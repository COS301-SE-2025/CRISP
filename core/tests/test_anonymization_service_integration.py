"""
Corrected integration tests for anonymization with services in the CRISP platform.
"""
import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from core.strategies.enums import AnonymizationLevel, DataType
from core.strategies.context import AnonymizationContext
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData
from core.models.threat_feed import ThreatFeed
from core.services.indicator_service import IndicatorService
from core.services.ttp_service import TTPService
from core.repositories.indicator_repository import IndicatorRepository
from core.repositories.ttp_repository import TTPRepository

class IndicatorServiceAnonymizationTestCase(TestCase):
    """Test cases for anonymization in IndicatorService."""
    def setUp(self):
        """Set up the test environment."""
        # Create repositories
        self.indicator_repository = IndicatorRepository()
        
        # Create the service with the corrected constructor
        self.service = IndicatorService(self.indicator_repository)
        
        # Create a test threat feed
        self.feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Anonymization"
        )
        
        # Create test indicators
        self.indicator1 = Indicator.objects.create(
            threat_feed=self.feed,
            type='ip',
            value='192.168.1.1',
            description='Test IP Indicator',
            stix_id='indicator-test-1'
        )
        
        self.indicator2 = Indicator.objects.create(
            threat_feed=self.feed,
            type='domain',
            value='malicious.example.com',
            description='Test Domain Indicator',
            stix_id='indicator-test-2'
        )
        
        self.indicator3 = Indicator.objects.create(
            threat_feed=self.feed,
            type='email',
            value='attacker@malicious.org',
            description='Test Email Indicator',
            stix_id='indicator-test-3'
        )
        
    @patch('core.strategies.context.AnonymizationContext.execute_anonymization')
    def test_create_anonymized_indicator(self, mock_execute_anonymization):
        """Test creating an anonymized indicator."""
        # Mock the anonymization function
        mock_execute_anonymization.side_effect = lambda data, data_type, level: f"anonymized-{data}"
        
        # Create indicator data
        indicator_data = {
            'threat_feed': self.feed,
            'type': 'ip',
            'value': '10.0.0.1',
            'description': 'Sensitive Indicator',
            'stix_id': 'indicator-new'
        }
        
        # Create the indicator with anonymization
        indicator = self.service.create_anonymized(indicator_data, AnonymizationLevel.MEDIUM)
        
        mock_execute_anonymization.assert_any_call('10.0.0.1', DataType.IP_ADDRESS, AnonymizationLevel.MEDIUM)
        
        # Check the indicator
        self.assertEqual(indicator.value, "anonymized-10.0.0.1")
        self.assertEqual(indicator.is_anonymized, True)
        
    @patch('core.strategies.context.AnonymizationContext.execute_anonymization')
    def test_share_indicator_with_anonymization(self, mock_execute_anonymization):
        """Test sharing an indicator with anonymization."""
        # Mock the anonymization function
        mock_execute_anonymization.side_effect = lambda data, data_type, level: f"anonymized-{data}"
        
        # Share the indicator with anonymization
        shared_indicator = self.service.share_with_anonymization(
            self.indicator1.id, 
            AnonymizationLevel.MEDIUM
        )
        
        # Check that anonymization was called for value
        mock_execute_anonymization.assert_any_call(
            '192.168.1.1', 
            DataType.IP_ADDRESS, 
            AnonymizationLevel.MEDIUM
        )
        
        # Check the shared indicator
        self.assertEqual(shared_indicator.value, "anonymized-192.168.1.1")
        self.assertEqual(shared_indicator.is_anonymized, True)
        self.assertNotEqual(shared_indicator.id, self.indicator1.id)  # Should be a new instance
        
    @patch('core.strategies.context.AnonymizationContext.auto_detect_and_anonymize')
    def test_anonymize_indicator_description(self, mock_auto_detect):
        """Test anonymizing the description of an indicator."""
        # Set up description with sensitive information
        description = "This indicator was observed from IP 10.0.0.1 and domain evil.com"
        self.indicator1.description = description
        self.indicator1.save()
        
        # Mock the auto-detection anonymization to replace IPs and domains
        mock_auto_detect.side_effect = lambda data, level: data.replace("10.0.0.1", "10.0.0.x").replace("evil.com", "*.com")
        
        # Anonymize the description
        updated_indicator = self.service.anonymize_description(
            self.indicator1.id,
            AnonymizationLevel.MEDIUM
        )
        
        # Check that auto-detection was called with the right parameters
        mock_auto_detect.assert_called_with(description, AnonymizationLevel.MEDIUM)
        
        # Check the updated description
        expected_description = "This indicator was observed from IP 10.0.0.x and domain *.com"
        self.assertEqual(updated_indicator.description, expected_description)
        
    @patch('core.strategies.context.AnonymizationContext.execute_anonymization')
    def test_bulk_anonymize_indicators(self, mock_execute_anonymization):
        """Test bulk anonymization of indicators."""
        # Mock the anonymization function
        mock_execute_anonymization.side_effect = lambda data, data_type, level: f"anonymized-{data}"
        
        # Get all indicators
        indicator_ids = [self.indicator1.id, self.indicator2.id, self.indicator3.id]
        
        # Bulk anonymize
        anonymized_indicators = self.service.bulk_anonymize(
            indicator_ids, 
            AnonymizationLevel.HIGH
        )
        
        self.assertEqual(mock_execute_anonymization.call_count, 6)
        
        # Check the anonymized indicators
        self.assertEqual(len(anonymized_indicators), 3)
        for indicator in anonymized_indicators:
            self.assertTrue(indicator.value.startswith("anonymized-"))
            self.assertEqual(indicator.is_anonymized, True)

class TTPServiceAnonymizationTestCase(TestCase):
    """Test cases for anonymization in TTPService."""
    def setUp(self):
        """Set up the test environment."""
        # Create repositories
        self.ttp_repository = TTPRepository()
        
        # Create the service with the corrected constructor
        self.service = TTPService(self.ttp_repository)
        
        # Create a test threat feed
        self.feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Anonymization"
        )
        
        # Create test TTPs
        self.ttp1 = TTPData.objects.create(
            threat_feed=self.feed,
            name='Phishing Attack',
            description='This TTP was used by attackers from 192.168.1.1',
            mitre_technique_id='T1566',
            mitre_tactic='initial_access',
            stix_id='ttp-test-1'
        )
        
        self.ttp2 = TTPData.objects.create(
            threat_feed=self.feed,
            name='Drive-by Compromise',
            description='This TTP was hosted on malicious.example.com',
            mitre_technique_id='T1189',
            mitre_tactic='initial_access',
            stix_id='ttp-test-2'
        )
        
    @patch('core.strategies.context.AnonymizationContext.auto_detect_and_anonymize')
    def test_anonymize_ttp_description(self, mock_auto_detect):
        """Test anonymizing the description of a TTP."""
        # Mock the auto-detection anonymization to replace IPs and domains
        mock_auto_detect.side_effect = lambda data, level: data.replace(
            "192.168.1.1", "192.168.1.x").replace(
            "malicious.example.com", "*.example.com")
        
        # Anonymize the description
        updated_ttp = self.service.anonymize_description(
            self.ttp1.id,
            AnonymizationLevel.MEDIUM
        )
        
        # Check that auto-detection was called with the right parameters
        mock_auto_detect.assert_called_with(
            'This TTP was used by attackers from 192.168.1.1', 
            AnonymizationLevel.MEDIUM
        )
        
        # Check the updated description
        expected_description = "This TTP was used by attackers from 192.168.1.x"
        self.assertEqual(updated_ttp.description, expected_description)
        
    @patch('core.strategies.context.AnonymizationContext.auto_detect_and_anonymize')
    def test_share_ttp_with_anonymization(self, mock_auto_detect):
        """Test sharing a TTP with anonymization."""
        # Mock the auto-detection anonymization to replace IPs and domains
        mock_auto_detect.side_effect = lambda data, level: data.replace(
            "192.168.1.1", "192.168.1.x").replace(
            "malicious.example.com", "*.example.com")
        
        # Share the TTP with anonymization
        shared_ttp = self.service.share_with_anonymization(
            self.ttp1.id, 
            AnonymizationLevel.HIGH
        )
        
        # Check that auto-detection was called
        mock_auto_detect.assert_called_with(
            'This TTP was used by attackers from 192.168.1.1', 
            AnonymizationLevel.HIGH
        )
        
        # Check the shared TTP
        self.assertEqual(shared_ttp.description, "This TTP was used by attackers from 192.168.1.x")
        self.assertEqual(shared_ttp.is_anonymized, True)
        self.assertNotEqual(shared_ttp.id, self.ttp1.id)  # Should be a new instance
        
    @patch('core.strategies.context.AnonymizationContext.auto_detect_and_anonymize')
    def test_bulk_anonymize_ttps(self, mock_auto_detect):
        """Test bulk anonymization of TTPs."""
        # Mock the auto-detection anonymization
        mock_auto_detect.side_effect = lambda data, level: data.replace(
            "192.168.1.1", "192.168.1.x").replace(
            "malicious.example.com", "*.example.com")
        
        # Get all TTPs
        ttp_ids = [self.ttp1.id, self.ttp2.id]
        
        # Bulk anonymize
        anonymized_ttps = self.service.bulk_anonymize(
            ttp_ids, 
            AnonymizationLevel.HIGH
        )
        
        # Check that anonymization was called for each TTP
        self.assertEqual(mock_auto_detect.call_count, 2)
        
        # Check the anonymized TTPs
        self.assertEqual(len(anonymized_ttps), 2)
        self.assertTrue("192.168.1.x" in anonymized_ttps[0].description)
        self.assertTrue("*.example.com" in anonymized_ttps[1].description)
        for ttp in anonymized_ttps:
            self.assertEqual(ttp.is_anonymized, True)

class EndToEndAnonymizationTestCase(TransactionTestCase):
    """End-to-end test cases for anonymization."""
    def setUp(self):
        """Set up the test environment."""
        # Create repositories
        self.indicator_repository = IndicatorRepository()
        self.ttp_repository = TTPRepository()
        
        # Create services with corrected constructors
        self.indicator_service = IndicatorService(self.indicator_repository)
        self.ttp_service = TTPService(self.ttp_repository)
        
        # Create a test institution and threat feed
        self.feed = ThreatFeed.objects.create(
            name="Confidential Feed",
            description="Feed with sensitive information"
        )
        
    def test_end_to_end_indicator_anonymization(self):
        """Test end-to-end anonymization flow for indicators."""
        # Create an indicator with sensitive data
        indicator_data = {
            'threat_feed': self.feed,
            'type': 'ip',
            'value': '10.10.10.10',
            'description': 'Malicious IP from organization X at malicious.example.com',
            'stix_id': 'indicator-e2e-test'
        }
        
        # Create and anonymize the indicator
        anonymized_indicator = self.indicator_service.create_anonymized(
            indicator_data, 
            AnonymizationLevel.MEDIUM
        )
        
        # Verify anonymization occurred
        self.assertNotEqual(anonymized_indicator.value, '10.10.10.10')
        self.assertTrue(anonymized_indicator.is_anonymized)
        
        # The description should also be anonymized
        self.assertNotEqual(anonymized_indicator.description, indicator_data['description'])
        
    def test_end_to_end_ttp_anonymization(self):
        """Test end-to-end anonymization flow for TTPs."""
        # Create a TTP with sensitive data
        ttp_data = {
            'threat_feed': self.feed,
            'name': 'Advanced Persistent Threat',
            'description': 'APT group used servers at 192.168.100.5 and contacted admin@victim.org',
            'mitre_technique_id': 'T1071',
            'mitre_tactic': 'command_and_control',
            'stix_id': 'ttp-e2e-test'
        }
        
        # Create and anonymize the TTP
        anonymized_ttp = self.ttp_service.create_anonymized(
            ttp_data, 
            AnonymizationLevel.HIGH
        )
        
        # Verify anonymization occurred
        self.assertTrue(anonymized_ttp.is_anonymized)
        
        # The description should be anonymized
        self.assertNotEqual(anonymized_ttp.description, ttp_data['description'])
        self.assertNotIn('192.168.100.5', anonymized_ttp.description)
        self.assertNotIn('admin@victim.org', anonymized_ttp.description)

if __name__ == '__main__':
    unittest.main()