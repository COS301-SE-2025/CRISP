"""
Test file for CRISP Anonymization System
Comprehensive unit tests for all components
"""

import unittest
import sys
import os

# Add the current directory to Python path to import our package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crisp_anonymization import (
    AnonymizationContext, 
    AnonymizationLevel, 
    DataType,
    IPAddressAnonymizationStrategy,
    DomainAnonymizationStrategy,
    EmailAnonymizationStrategy,
    URLAnonymizationStrategy
)
from crisp_anonymization.utils import AnonymizationUtils
from crisp_anonymization.exceptions import AnonymizationError


class TestAnonymizationStrategies(unittest.TestCase):
    """Test individual anonymization strategies"""

    def setUp(self):
        self.ip_strategy = IPAddressAnonymizationStrategy()
        self.domain_strategy = DomainAnonymizationStrategy()
        self.email_strategy = EmailAnonymizationStrategy()
        self.url_strategy = URLAnonymizationStrategy()

    def test_ip_address_anonymization(self):
        """Test IP address anonymization at different levels"""
        ipv4 = "192.168.1.100"
        ipv6 = "2001:db8::1"
        
        # IPv4 tests
        self.assertEqual(
            self.ip_strategy.anonymize(ipv4, AnonymizationLevel.NONE), 
            "192.168.1.100"
        )
        self.assertEqual(
            self.ip_strategy.anonymize(ipv4, AnonymizationLevel.LOW), 
            "192.168.1.x"
        )
        self.assertEqual(
            self.ip_strategy.anonymize(ipv4, AnonymizationLevel.MEDIUM), 
            "192.168.x.x"
        )
        self.assertEqual(
            self.ip_strategy.anonymize(ipv4, AnonymizationLevel.HIGH), 
            "192.x.x.x"
        )
        
        # IPv6 tests
        self.assertEqual(
            self.ip_strategy.anonymize(ipv6, AnonymizationLevel.LOW), 
            "2001:db8::xxxx"
        )
        
        # FULL anonymization should be consistent
        full_anon1 = self.ip_strategy.anonymize(ipv4, AnonymizationLevel.FULL)
        full_anon2 = self.ip_strategy.anonymize(ipv4, AnonymizationLevel.FULL)
        self.assertEqual(full_anon1, full_anon2)
        self.assertTrue(full_anon1.startswith("anon-ipv4-"))

    def test_domain_anonymization(self):
        """Test domain anonymization at different levels"""
        domain = "malicious.example.com"
        
        self.assertEqual(
            self.domain_strategy.anonymize(domain, AnonymizationLevel.NONE), 
            "malicious.example.com"
        )
        self.assertEqual(
            self.domain_strategy.anonymize(domain, AnonymizationLevel.LOW), 
            "*.example.com"
        )
        self.assertEqual(
            self.domain_strategy.anonymize(domain, AnonymizationLevel.MEDIUM), 
            "*.com"
        )
        self.assertEqual(
            self.domain_strategy.anonymize(domain, AnonymizationLevel.HIGH), 
            "*.commercial"
        )
        
        full_anon = self.domain_strategy.anonymize(domain, AnonymizationLevel.FULL)
        self.assertTrue(full_anon.startswith("anon-domain-"))
        self.assertTrue(full_anon.endswith(".example"))

    def test_email_anonymization(self):
        """Test email anonymization at different levels"""
        email = "admin@company.edu"
        
        self.assertEqual(
            self.email_strategy.anonymize(email, AnonymizationLevel.NONE), 
            "admin@company.edu"
        )
        
        low_anon = self.email_strategy.anonymize(email, AnonymizationLevel.LOW)
        self.assertTrue(low_anon.startswith("user-"))
        self.assertTrue(low_anon.endswith("@company.edu"))
        
        medium_anon = self.email_strategy.anonymize(email, AnonymizationLevel.MEDIUM)
        self.assertTrue(medium_anon.startswith("user-"))
        self.assertTrue("*.edu" in medium_anon)
        
        high_anon = self.email_strategy.anonymize(email, AnonymizationLevel.HIGH)
        self.assertEqual(high_anon, "user@*.educational")
        
        full_anon = self.email_strategy.anonymize(email, AnonymizationLevel.FULL)
        self.assertTrue(full_anon.startswith("anon-user-"))
        self.assertTrue(full_anon.endswith("@example.com"))

    def test_url_anonymization(self):
        """Test URL anonymization at different levels"""
        url = "https://evil.example.org/malware.exe"
        
        self.assertEqual(
            self.url_strategy.anonymize(url, AnonymizationLevel.NONE), 
            url
        )
        
        low_anon = self.url_strategy.anonymize(url, AnonymizationLevel.LOW)
        self.assertTrue(low_anon.startswith("https://"))
        self.assertTrue("*.example.org" in low_anon)
        self.assertTrue("[path-removed]" in low_anon)
        
        medium_anon = self.url_strategy.anonymize(url, AnonymizationLevel.MEDIUM)
        self.assertEqual(medium_anon, "https://*.org")
        
        full_anon = self.url_strategy.anonymize(url, AnonymizationLevel.FULL)
        self.assertTrue(full_anon.startswith("https://anon-url-"))
        self.assertTrue(full_anon.endswith(".example"))

    def test_strategy_can_handle(self):
        """Test that strategies correctly identify their data types"""
        self.assertTrue(self.ip_strategy.can_handle(DataType.IP_ADDRESS))
        self.assertFalse(self.ip_strategy.can_handle(DataType.DOMAIN))
        
        self.assertTrue(self.domain_strategy.can_handle(DataType.DOMAIN))
        self.assertFalse(self.domain_strategy.can_handle(DataType.EMAIL))
        
        self.assertTrue(self.email_strategy.can_handle(DataType.EMAIL))
        self.assertFalse(self.email_strategy.can_handle(DataType.URL))
        
        self.assertTrue(self.url_strategy.can_handle(DataType.URL))
        self.assertFalse(self.url_strategy.can_handle(DataType.IP_ADDRESS))


class TestAnonymizationContext(unittest.TestCase):
    """Test the main AnonymizationContext class"""

    def setUp(self):
        self.context = AnonymizationContext()

    def test_execute_anonymization(self):
        """Test direct anonymization execution"""
        result = self.context.execute_anonymization(
            "192.168.1.100", 
            DataType.IP_ADDRESS, 
            AnonymizationLevel.MEDIUM
        )
        self.assertEqual(result, "192.168.x.x")

    def test_auto_detect_and_anonymize(self):
        """Test automatic data type detection and anonymization"""
        # Test IP detection
        result = self.context.auto_detect_and_anonymize(
            "10.0.0.1", 
            AnonymizationLevel.LOW
        )
        self.assertEqual(result, "10.0.0.x")
        
        # Test email detection
        result = self.context.auto_detect_and_anonymize(
            "user@domain.com", 
            AnonymizationLevel.HIGH
        )
        self.assertEqual(result, "user@*.commercial")
        
        # Test URL detection
        result = self.context.auto_detect_and_anonymize(
            "https://example.com", 
            AnonymizationLevel.MEDIUM
        )
        self.assertEqual(result, "https://*.com")
        
        # Test domain detection
        result = self.context.auto_detect_and_anonymize(
            "suspicious.domain.net", 
            AnonymizationLevel.LOW
        )
        self.assertEqual(result, "*.domain.net")

    def test_bulk_anonymize(self):
        """Test bulk anonymization functionality"""
        data_items = [
            ("192.168.1.1", DataType.IP_ADDRESS),
            ("evil.com", DataType.DOMAIN),
            ("attacker@malicious.org", DataType.EMAIL),
        ]
        
        results = self.context.bulk_anonymize(data_items, AnonymizationLevel.MEDIUM)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], "192.168.x.x")
        self.assertEqual(results[1], "*.com")
        self.assertTrue(results[2].startswith("user-"))
        self.assertTrue("*.org" in results[2])

    def test_invalid_data_type_handling(self):
        """Test handling of invalid data types"""
        with self.assertRaises(ValueError):
            # This should raise an error for an unregistered data type
            self.context.execute_anonymization(
                "test", 
                DataType.HASH,  # Not registered by default
                AnonymizationLevel.LOW
            )

    def test_consistency(self):
        """Test that same input produces same output"""
        data = "192.168.1.100"
        result1 = self.context.execute_anonymization(
            data, DataType.IP_ADDRESS, AnonymizationLevel.FULL
        )
        result2 = self.context.execute_anonymization(
            data, DataType.IP_ADDRESS, AnonymizationLevel.FULL
        )
        self.assertEqual(result1, result2)


class TestAnonymizationUtils(unittest.TestCase):
    """Test utility functions"""

    def test_generate_consistent_hash(self):
        """Test consistent hash generation"""
        hash1 = AnonymizationUtils.generate_consistent_hash("test")
        hash2 = AnonymizationUtils.generate_consistent_hash("test")
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 8)  # Default length

    def test_mask_string(self):
        """Test string masking functionality"""
        result = AnonymizationUtils.mask_string("sensitive", 3)
        self.assertEqual(result, "senxxxxx")
        
        result = AnonymizationUtils.mask_string("ab", 3)
        self.assertEqual(result, "xx")

    def test_categorize_tld(self):
        """Test TLD categorization"""
        self.assertEqual(AnonymizationUtils.categorize_tld("com"), "commercial")
        self.assertEqual(AnonymizationUtils.categorize_tld("edu"), "educational")
        self.assertEqual(AnonymizationUtils.categorize_tld("gov"), "government")
        self.assertEqual(AnonymizationUtils.categorize_tld("org"), "organization")
        self.assertEqual(AnonymizationUtils.categorize_tld("xyz"), "other")

    def test_validate_data_format(self):
        """Test data format validation"""
        self.assertTrue(
            AnonymizationUtils.validate_data_format("192.168.1.1", DataType.IP_ADDRESS)
        )
        self.assertFalse(
            AnonymizationUtils.validate_data_format("not-an-ip", DataType.IP_ADDRESS)
        )
        self.assertTrue(
            AnonymizationUtils.validate_data_format("user@domain.com", DataType.EMAIL)
        )
        self.assertFalse(
            AnonymizationUtils.validate_data_format("not-an-email", DataType.EMAIL)
        )


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""

    def setUp(self):
        self.context = AnonymizationContext()

    def test_threat_intelligence_scenario(self):
        """Test a realistic threat intelligence sharing scenario"""
        # Simulate threat indicators from a feed
        threat_indicators = [
            ("203.0.113.42", DataType.IP_ADDRESS),
            ("malware-c2.evil-domain.org", DataType.DOMAIN),
            ("phishing@fake-bank.net", DataType.EMAIL),
            ("https://exploit-kit.badsite.com/payload.exe", DataType.URL),
        ]
        
        # Test different trust levels (anonymization levels)
        # High trust = LOW anonymization
        high_trust_results = self.context.bulk_anonymize(
            threat_indicators, AnonymizationLevel.LOW
        )
        
        # Low trust = HIGH anonymization
        low_trust_results = self.context.bulk_anonymize(
            threat_indicators, AnonymizationLevel.HIGH
        )
        
        # Verify that high trust preserves more information
        self.assertTrue("203.0.113.x" in high_trust_results[0])
        self.assertTrue("203.x.x.x" in low_trust_results[0])
        
        # Verify consistent anonymization
        consistent_results = self.context.bulk_anonymize(
            threat_indicators, AnonymizationLevel.FULL
        )
        consistent_results_2 = self.context.bulk_anonymize(
            threat_indicators, AnonymizationLevel.FULL
        )
        self.assertEqual(consistent_results, consistent_results_2)

    def test_mixed_data_auto_detection(self):
        """Test auto-detection with mixed data types"""
        mixed_data = [
            "192.168.1.100",
            "suspicious.example.com",
            "attacker@evil.org",
            "https://malware.badsite.net/trojan",
            "2001:db8::1",
        ]
        
        results = []
        for data in mixed_data:
            result = self.context.auto_detect_and_anonymize(
                data, AnonymizationLevel.MEDIUM
            )
            results.append(result)
        
        # Verify each was processed correctly
        self.assertEqual(results[0], "192.168.x.x")  # IP
        self.assertEqual(results[1], "*.com")        # Domain
        self.assertTrue("*.org" in results[2])       # Email
        self.assertEqual(results[3], "https://*.net") # URL
        self.assertTrue("xxxxxxxx" in results[4])    # IPv6


def run_performance_test():
    """Simple performance test for bulk operations"""
    print("\n=== Performance Test ===")
    import time
    
    context = AnonymizationContext()
    
    # Generate test data
    test_data = []
    for i in range(1000):
        test_data.extend([
            (f"192.168.1.{i % 255}", DataType.IP_ADDRESS),
            (f"domain{i}.com", DataType.DOMAIN),
            (f"user{i}@company.org", DataType.EMAIL),
        ])
    
    start_time = time.time()
    results = context.bulk_anonymize(test_data, AnonymizationLevel.MEDIUM)
    end_time = time.time()
    
    print(f"Processed {len(test_data)} items in {end_time - start_time:.4f} seconds")
    print(f"Rate: {len(test_data) / (end_time - start_time):.0f} items/second")


if __name__ == "__main__":
    # Run unit tests
    print("Running CRISP Anonymization System Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance test
    run_performance_test()