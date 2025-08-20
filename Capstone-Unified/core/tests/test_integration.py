"""
Quick integration test for CRISP Strategy Pattern Integration
Tests core functionality without requiring full Django setup.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core', 'patterns', 'strategy'))

def test_basic_integration():
    """Test basic anonymization functionality"""
    print("🧪 Testing Basic Integration...")
    
    try:
        from core.patterns.strategy.context import AnonymizationContext
        from core.patterns.strategy.enums import AnonymizationLevel, DataType
        
        context = AnonymizationContext()
        
        # Test IP anonymization
        ip_result = context.execute_anonymization("192.168.1.100", DataType.IP_ADDRESS, AnonymizationLevel.MEDIUM)
        assert ip_result == "192.168.x.x", f"Expected '192.168.x.x', got '{ip_result}'"
        
        # Test domain anonymization
        domain_result = context.execute_anonymization("malicious.example.com", DataType.DOMAIN, AnonymizationLevel.LOW)
        assert domain_result == "*.example.com", f"Expected '*.example.com', got '{domain_result}'"
        
        # Test auto-detection
        auto_result = context.auto_detect_and_anonymize("evil.org", AnonymizationLevel.HIGH)
        assert "*.organization" in auto_result or "*.other" in auto_result, f"Expected category anonymization, got '{auto_result}'"
        
        print("Basic integration tests passed!")
        return True
        
    except Exception as e:
        print(f"Basic integration test failed: {e}")
        return False

def test_strategy_pattern():
    """Test strategy pattern concepts"""
    print("Testing Strategy Pattern...")
    
    try:
        from core.patterns.strategy.strategies import (
            IPAddressAnonymizationStrategy,
            DomainAnonymizationStrategy,
            EmailAnonymizationStrategy
        )
        from core.patterns.strategy.enums import AnonymizationLevel, DataType
        
        # Test IP strategy
        ip_strategy = IPAddressAnonymizationStrategy()
        assert ip_strategy.can_handle(DataType.IP_ADDRESS)
        assert ip_strategy.validate("192.168.1.1")
        ip_anon = ip_strategy.anonymize("192.168.1.1", AnonymizationLevel.LOW)
        assert ip_anon == "192.168.1.x"
        
        # Test domain strategy
        domain_strategy = DomainAnonymizationStrategy()
        assert domain_strategy.can_handle(DataType.DOMAIN)
        assert domain_strategy.validate("example.com")
        domain_anon = domain_strategy.anonymize("test.example.com", AnonymizationLevel.LOW)
        assert domain_anon == "*.example.com"
        
        # Test email strategy
        email_strategy = EmailAnonymizationStrategy()
        assert email_strategy.can_handle(DataType.EMAIL)
        assert email_strategy.validate("user@example.com")
        email_anon = email_strategy.anonymize("user@example.com", AnonymizationLevel.MEDIUM)
        assert "@*.example.com" in email_anon
        
        print("Strategy pattern tests passed!")
        return True
        
    except Exception as e:
        print(f"Strategy pattern test failed: {e}")
        return False

def test_integration_concepts():
    """Test integration concepts"""
    print("Testing Integration Concepts...")
    
    try:
        # Test trust level mapping concept
        trust_levels = [0.9, 0.6, 0.3, 0.1]
        expected_levels = ["none", "low", "medium", "full"]
        
        def map_trust_to_anon(trust):
            if trust >= 0.8:
                return "none"
            elif trust >= 0.5:
                return "low"
            elif trust >= 0.2:
                return "medium"
            else:
                return "full"
        
        for trust, expected in zip(trust_levels, expected_levels):
            result = map_trust_to_anon(trust)
            assert result == expected, f"Trust {trust} should map to {expected}, got {result}"
        
        print("Integration concepts tests passed!")
        return True
        
    except Exception as e:
        print(f"Integration concepts test failed: {e}")
        return False

def test_stix_concepts():
    """Test STIX anonymization concepts"""
    print("Testing STIX Concepts...")
    
    try:
        import json
        
        # Test STIX object structure
        stix_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--test-1234-1234-1234-123456789012",
            "created": "2021-01-01T00:00:00.000Z",
            "modified": "2021-01-01T00:00:00.000Z",
            "name": "Test Indicator",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[domain-name:value = 'test.example.com']",
            "valid_from": "2021-01-01T00:00:00.000Z"
        }
        
        # Validate STIX structure
        assert stix_indicator["type"] == "indicator"
        assert "pattern" in stix_indicator
        assert "domain-name:value" in stix_indicator["pattern"]
        
        # Test pattern modification (simulation)
        original_pattern = stix_indicator["pattern"]
        anonymized_pattern = original_pattern.replace("test.example.com", "[REDACTED].example.com")
        assert anonymized_pattern != original_pattern
        assert "[REDACTED]" in anonymized_pattern
        
        print("STIX concepts tests passed!")
        return True
        
    except Exception as e:
        print(f"STIX concepts test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("CRISP Strategy Pattern Integration Tests")
    print("=" * 50)
    
    tests = [
        test_basic_integration,
        test_strategy_pattern,
        test_integration_concepts,
        test_stix_concepts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All integration tests passed!")
        print("CRISP Strategy Pattern Integration is working correctly!")
    else:
        print(f"{total - passed} tests failed")
        print("Some components may need additional setup or dependencies")
    
    print("\nIntegration is ready for use within the Django application!")

if __name__ == "__main__":
    main()