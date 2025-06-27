"""
Unit tests for anonymization strategies in the CRISP platform.
"""
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
import hashlib
import re
from core.strategies.enums import AnonymizationLevel, DataType

from core.strategies.strategies import (
    AnonymizationStrategy,
    IPAddressAnonymizationStrategy,
    DomainAnonymizationStrategy,
    EmailAnonymizationStrategy,
    URLAnonymizationStrategy
)

from core.strategies.context import AnonymizationContext
from core.strategies.exceptions import DataValidationError

class IPAddressAnonymizationStrategyTestCase(TestCase):
    """Test cases for the IPAddressAnonymizationStrategy."""
    def setUp(self):
        """Set up the test environment."""
        self.strategy = IPAddressAnonymizationStrategy()
        
    def test_validate_valid_ipv4(self):
        """Test validation of valid IPv4 addresses."""
        self.assertTrue(self.strategy.validate("192.168.1.1"))
        self.assertTrue(self.strategy.validate("10.0.0.1"))
        self.assertTrue(self.strategy.validate("172.16.0.1"))
        
    def test_validate_valid_ipv6(self):
        """Test validation of valid IPv6 addresses."""
        self.assertTrue(self.strategy.validate("2001:db8::1"))
        self.assertTrue(self.strategy.validate("::1"))
        
    def test_validate_invalid_ip(self):
        """Test validation of invalid IP addresses."""
        self.assertFalse(self.strategy.validate("not an ip"))
        self.assertFalse(self.strategy.validate("192.168.1"))
        self.assertFalse(self.strategy.validate("192.168.1.300"))
        
    def test_can_handle_ip_address(self):
        """Test that the strategy can handle IP_ADDRESS data type."""
        self.assertTrue(self.strategy.can_handle(DataType.IP_ADDRESS))
        
    def test_cannot_handle_other_types(self):
        """Test that the strategy cannot handle other data types."""
        self.assertFalse(self.strategy.can_handle(DataType.DOMAIN))
        self.assertFalse(self.strategy.can_handle(DataType.EMAIL))
        self.assertFalse(self.strategy.can_handle(DataType.URL))
        
    def test_anonymize_ipv4_none_level(self):
        """Test IPv4 anonymization at NONE level."""
        ip = "192.168.1.1"
        result = self.strategy.anonymize(ip, AnonymizationLevel.NONE)
        self.assertEqual(result, ip)
        
    def test_anonymize_ipv4_low_level(self):
        """Test IPv4 anonymization at LOW level."""
        ip = "192.168.1.1"
        result = self.strategy.anonymize(ip, AnonymizationLevel.LOW)
        # Should preserve first 3 octets
        self.assertTrue(result.startswith("192.168.1."))
        self.assertNotEqual(result, ip)
        
    def test_anonymize_ipv4_medium_level(self):
        """Test IPv4 anonymization at MEDIUM level."""
        ip = "192.168.1.1"
        result = self.strategy.anonymize(ip, AnonymizationLevel.MEDIUM)
        # Should preserve first 2 octets
        self.assertTrue(result.startswith("192.168."))
        self.assertFalse(result.startswith("192.168.1."))
        
    def test_anonymize_ipv4_high_level(self):
        """Test IPv4 anonymization at HIGH level."""
        ip = "192.168.1.1"
        result = self.strategy.anonymize(ip, AnonymizationLevel.HIGH)
        # Should preserve only first octet
        self.assertTrue(result.startswith("192."))
        self.assertFalse(result.startswith("192.168."))
        
    def test_anonymize_ipv4_full_level(self):
        """Test IPv4 anonymization at FULL level."""
        ip = "192.168.1.1"
        result = self.strategy.anonymize(ip, AnonymizationLevel.FULL)
        # Should be completely anonymized but consistent
        self.assertNotEqual(result, ip)
        self.assertTrue(result.startswith("anon-ip-"))
        
        # Check consistency (same input should produce same output)
        result2 = self.strategy.anonymize(ip, AnonymizationLevel.FULL)
        self.assertEqual(result, result2)
        
    def test_anonymize_ipv6(self):
        """Test IPv6 anonymization at different levels."""
        ip = "2001:db8::1"
        
        # Test LOW level
        result_low = self.strategy.anonymize(ip, AnonymizationLevel.LOW)
        self.assertNotEqual(result_low, ip)
        
        # Test MEDIUM level
        result_medium = self.strategy.anonymize(ip, AnonymizationLevel.MEDIUM)
        self.assertNotEqual(result_medium, ip)
        
        # Test HIGH level
        result_high = self.strategy.anonymize(ip, AnonymizationLevel.HIGH)
        self.assertNotEqual(result_high, ip)
        
        # Test FULL level
        result_full = self.strategy.anonymize(ip, AnonymizationLevel.FULL)
        self.assertNotEqual(result_full, ip)
        self.assertTrue(result_full.startswith("anon-ip-"))

class DomainAnonymizationStrategyTestCase(TestCase):
    """Test cases for the DomainAnonymizationStrategy."""
    def setUp(self):
        """Set up the test environment."""
        self.strategy = DomainAnonymizationStrategy()
        
    def test_validate_valid_domain(self):
        """Test validation of valid domain names."""
        self.assertTrue(self.strategy.validate("example.com"))
        self.assertTrue(self.strategy.validate("sub.example.com"))
        self.assertTrue(self.strategy.validate("sub-domain.example.co.uk"))
        
    def test_validate_invalid_domain(self):
        """Test validation of invalid domain names."""
        self.assertFalse(self.strategy.validate("not a domain"))
        self.assertFalse(self.strategy.validate("invalid domain.com"))
        self.assertFalse(self.strategy.validate(""))
        
    def test_can_handle_domain(self):
        """Test that the strategy can handle DOMAIN data type."""
        self.assertTrue(self.strategy.can_handle(DataType.DOMAIN))
        
    def test_anonymize_domain_none_level(self):
        """Test domain anonymization at NONE level."""
        domain = "sub.example.com"
        result = self.strategy.anonymize(domain, AnonymizationLevel.NONE)
        self.assertEqual(result, domain)
        
    def test_anonymize_domain_low_level(self):
        """Test domain anonymization at LOW level."""
        domain = "sub.example.com"
        result = self.strategy.anonymize(domain, AnonymizationLevel.LOW)
        # Should preserve second-level domain and TLD
        self.assertEqual(result, "*.example.com")
        
    def test_anonymize_domain_medium_level(self):
        """Test domain anonymization at MEDIUM level."""
        domain = "sub.example.com"
        result = self.strategy.anonymize(domain, AnonymizationLevel.MEDIUM)
        # Should preserve only TLD
        self.assertEqual(result, "*.com")
        
    def test_anonymize_domain_high_level(self):
        """Test domain anonymization at HIGH level."""
        domain = "sub.example.com"
        result = self.strategy.anonymize(domain, AnonymizationLevel.HIGH)
        # Should preserve only category
        self.assertIn(result, ["*.commercial", "*.other"])
        
    def test_anonymize_domain_full_level(self):
        """Test domain anonymization at FULL level."""
        domain = "sub.example.com"
        result = self.strategy.anonymize(domain, AnonymizationLevel.FULL)
        # Should be completely anonymized but consistent
        self.assertNotEqual(result, domain)
        self.assertTrue(result.startswith("anon-domain-"))
        self.assertTrue(result.endswith(".example"))
        
        # Check consistency
        result2 = self.strategy.anonymize(domain, AnonymizationLevel.FULL)
        self.assertEqual(result, result2)

class EmailAnonymizationStrategyTestCase(TestCase):
    """Test cases for the EmailAnonymizationStrategy."""
    def setUp(self):
        """Set up the test environment."""
        self.strategy = EmailAnonymizationStrategy()
        
    def test_validate_valid_email(self):
        """Test validation of valid email addresses."""
        self.assertTrue(self.strategy.validate("user@example.com"))
        self.assertTrue(self.strategy.validate("user.name@sub.example.com"))
        self.assertTrue(self.strategy.validate("user+tag@example.com"))
        
    def test_validate_invalid_email(self):
        """Test validation of invalid email addresses."""
        self.assertFalse(self.strategy.validate("not an email"))
        self.assertFalse(self.strategy.validate("user@"))
        self.assertFalse(self.strategy.validate("@example.com"))
        
    def test_can_handle_email(self):
        """Test that the strategy can handle EMAIL data type."""
        self.assertTrue(self.strategy.can_handle(DataType.EMAIL))
        
    def test_anonymize_email_none_level(self):
        """Test email anonymization at NONE level."""
        email = "user@example.com"
        result = self.strategy.anonymize(email, AnonymizationLevel.NONE)
        self.assertEqual(result, email)
        
    def test_anonymize_email_low_level(self):
        """Test email anonymization at LOW level."""
        email = "user@example.com"
        result = self.strategy.anonymize(email, AnonymizationLevel.LOW)
        # Should anonymize local part but keep domain
        self.assertTrue(result.endswith("@example.com"))
        self.assertFalse(result.startswith("user@"))
        
    def test_anonymize_email_medium_level(self):
        """Test email anonymization at MEDIUM level."""
        email = "user@example.com"
        result = self.strategy.anonymize(email, AnonymizationLevel.MEDIUM)
        # Should anonymize local part and partially anonymize domain
        self.assertFalse(result.endswith("@example.com"))
        self.assertFalse(result.startswith("user@"))
        
    def test_anonymize_email_high_level(self):
        """Test email anonymization at HIGH level."""
        email = "user@example.com"
        result = self.strategy.anonymize(email, AnonymizationLevel.HIGH)
        # Should keep minimal domain info
        self.assertTrue(result.startswith("user@"))
        self.assertNotEqual(result, email)
        
    def test_anonymize_email_full_level(self):
        """Test email anonymization at FULL level."""
        email = "user@example.com"
        result = self.strategy.anonymize(email, AnonymizationLevel.FULL)
        # Should be completely anonymized but consistent
        self.assertNotEqual(result, email)
        self.assertTrue(result.startswith("anon-user-"))
        self.assertTrue(result.endswith("@example.com"))
        
        # Check consistency
        result2 = self.strategy.anonymize(email, AnonymizationLevel.FULL)
        self.assertEqual(result, result2)

class URLAnonymizationStrategyTestCase(TestCase):
    """Test cases for the URLAnonymizationStrategy."""
    def setUp(self):
        """Set up the test environment."""
        self.strategy = URLAnonymizationStrategy()
        
    def test_validate_valid_url(self):
        """Test validation of valid URLs."""
        self.assertTrue(self.strategy.validate("https://example.com"))
        self.assertTrue(self.strategy.validate("http://example.com/path"))
        self.assertTrue(self.strategy.validate("https://sub.example.com/path?query=value"))
        
    def test_validate_invalid_url(self):
        """Test validation of invalid URLs."""
        self.assertFalse(self.strategy.validate("not a url"))
        self.assertFalse(self.strategy.validate("example.com"))  # No protocol
        self.assertFalse(self.strategy.validate("ftp://example.com"))  # Wrong protocol
        
    def test_can_handle_url(self):
        """Test that the strategy can handle URL data type."""
        self.assertTrue(self.strategy.can_handle(DataType.URL))
        
    def test_anonymize_url_none_level(self):
        """Test URL anonymization at NONE level."""
        url = "https://example.com/path?query=value"
        result = self.strategy.anonymize(url, AnonymizationLevel.NONE)
        self.assertEqual(result, url)
        
    def test_anonymize_url_low_level(self):
        """Test URL anonymization at LOW level."""
        url = "https://example.com/path?query=value"
        result = self.strategy.anonymize(url, AnonymizationLevel.LOW)
        # Should preserve domain (anonymized) but remove path details
        self.assertTrue(result.startswith("https://"))
        self.assertTrue("/[path-removed]" in result)
        
    def test_anonymize_url_medium_level(self):
        """Test URL anonymization at MEDIUM level."""
        url = "https://example.com/path?query=value"
        result = self.strategy.anonymize(url, AnonymizationLevel.MEDIUM)
        # Should preserve protocol and partial domain but remove path
        self.assertTrue(result.startswith("https://"))
        self.assertFalse("/path" in result)
        
    def test_anonymize_url_high_level(self):
        """Test URL anonymization at HIGH level."""
        url = "https://example.com/path?query=value"
        result = self.strategy.anonymize(url, AnonymizationLevel.HIGH)
        # Should preserve only protocol and minimal domain info
        self.assertTrue(result.startswith("https://"))
        self.assertFalse("example.com" in result)
        self.assertFalse("/path" in result)
        
    def test_anonymize_url_full_level(self):
        """Test URL anonymization at FULL level."""
        url = "https://example.com/path?query=value"
        result = self.strategy.anonymize(url, AnonymizationLevel.FULL)
        # Should be completely anonymized but consistent
        self.assertNotEqual(result, url)
        self.assertTrue(result.startswith("https://anon-url-"))
        
        # Check consistency
        result2 = self.strategy.anonymize(url, AnonymizationLevel.FULL)
        self.assertEqual(result, result2)

class AnonymizationContextTestCase(TestCase):
    """Test cases for the AnonymizationContext."""
    def setUp(self):
        """Set up the test environment."""
        self.context = AnonymizationContext()
        
    def test_register_strategy(self):
        """Test registering a strategy."""
        strategy = MagicMock()
        self.context.register_strategy(DataType.HASH, strategy)
        
        # Execute anonymization for this type
        self.context.execute_anonymization("abcdef", DataType.HASH, AnonymizationLevel.MEDIUM)
        
        # Check that the strategy was called
        strategy.anonymize.assert_called_once_with("abcdef", AnonymizationLevel.MEDIUM)
        
    def test_set_default_strategy(self):
        """Test setting a default strategy."""
        default_strategy = MagicMock()
        default_strategy.anonymize.return_value = "anonymized"
        
        self.context.set_default_strategy(default_strategy)
        
        # Try to anonymize a data type that doesn't have a specific strategy
        result = self.context.execute_anonymization("test", DataType.FILENAME, AnonymizationLevel.MEDIUM)
        
        # Check that the default strategy was used
        default_strategy.anonymize.assert_called_once_with("test", AnonymizationLevel.MEDIUM)
        self.assertEqual(result, "anonymized")
        
    def test_auto_detect_and_anonymize_ip(self):
        """Test auto-detecting and anonymizing an IP address."""
        ip = "192.168.1.1"
        result = self.context.auto_detect_and_anonymize(ip, AnonymizationLevel.MEDIUM)
        
        # Should be detected as an IP and anonymized accordingly
        self.assertNotEqual(result, ip)
        self.assertTrue(result.startswith("192.168."))
        
    def test_auto_detect_and_anonymize_domain(self):
        """Test auto-detecting and anonymizing a domain."""
        domain = "example.com"
        result = self.context.auto_detect_and_anonymize(domain, AnonymizationLevel.MEDIUM)
        
        # Should be detected as a domain and anonymized accordingly
        self.assertEqual(result, "*.com")
        
    def test_auto_detect_and_anonymize_email(self):
        """Test auto-detecting and anonymizing an email."""
        email = "user@example.com"
        result = self.context.auto_detect_and_anonymize(email, AnonymizationLevel.MEDIUM)
        
        # Should be detected as an email and anonymized accordingly
        self.assertNotEqual(result, email)
        self.assertFalse(result.startswith("user@"))
        
    def test_auto_detect_and_anonymize_url(self):
        """Test auto-detecting and anonymizing a URL."""
        url = "https://example.com/path"
        result = self.context.auto_detect_and_anonymize(url, AnonymizationLevel.MEDIUM)
        
        # Should be detected as a URL and anonymized accordingly
        self.assertTrue(result.startswith("https://"))
        self.assertFalse("/path" in result)
        
    def test_bulk_anonymize(self):
        """Test bulk anonymization of multiple data items."""
        data = [
            ("192.168.1.1", DataType.IP_ADDRESS),
            ("example.com", DataType.DOMAIN),
            ("user@example.com", DataType.EMAIL)
        ]
        
        results = self.context.bulk_anonymize(data, AnonymizationLevel.MEDIUM)
        
        # Check the results
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].startswith("192.168."))
        self.assertEqual(results[1], "*.com")
        self.assertFalse(results[2].startswith("user@"))
        
    def test_anonymize_stix_object(self):
        """Test anonymizing a STIX object."""
        stix_object = {
            "type": "indicator",
            "id": "indicator--12345678-1234-5678-9abc-123456789012",
            "name": "Malicious IP",
            "description": "This IP 192.168.1.1 was observed in malicious traffic",
            "pattern": "[ipv4-addr:value = '192.168.1.1']"
        }
        
        result = self.context.anonymize_stix_object(stix_object, AnonymizationLevel.MEDIUM)
        
        # Check that content was anonymized
        self.assertNotEqual(result["description"], stix_object["description"])
        self.assertNotEqual(result["pattern"], stix_object["pattern"])
        
        # The ID should be preserved (not anonymized)
        self.assertEqual(result["id"], stix_object["id"])