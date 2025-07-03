"""
Quick test script for the CRISP Anonymization System
"""

import sys
import os
import json

# Add the parent directory to the Python path to import our package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Direct imports
from core.patterns.strategy.enums import AnonymizationLevel, DataType
from core.patterns.strategy.context import AnonymizationContext

def test_basic_anonymization():
    """Test basic anonymization functionality"""
    print("Testing CRISP Anonymization...")
    context = AnonymizationContext()
    
    # Test IP address anonymization
    ip_result = context.execute_anonymization("192.168.1.1", DataType.IP_ADDRESS, AnonymizationLevel.MEDIUM)
    print(f"IP anonymization: 192.168.1.1 → {ip_result}")
    
    # Test domain anonymization
    domain_result = context.execute_anonymization("malicious.example.com", DataType.DOMAIN, AnonymizationLevel.LOW)
    print(f"Domain anonymization: malicious.example.com → {domain_result}")
    
    # Test email anonymization
    email_result = context.execute_anonymization("user@example.com", DataType.EMAIL, AnonymizationLevel.HIGH)
    print(f"Email anonymization: user@example.com → {email_result}")
    
    # Test URL anonymization
    url_result = context.execute_anonymization("https://example.com/page", DataType.URL, AnonymizationLevel.MEDIUM)
    print(f"URL anonymization: https://example.com/page → {url_result}")

def test_auto_detection():
    """Test auto-detection functionality"""
    print("\nTesting auto-detection...")
    context = AnonymizationContext()
    
    test_data = [
        "192.168.1.1",
        "2001:db8::1",
        "example.com", 
        "user@example.com",
        "https://example.com"
    ]
    
    for data in test_data:
        result = context.auto_detect_and_anonymize(data, AnonymizationLevel.MEDIUM)
        data_type = context._detect_data_type(data)
        print(f"Auto-detect: {data} → {result} (detected as {data_type.value})")

def test_stix_anonymization():
    """Test STIX anonymization"""
    print("\nTesting STIX anonymization...")
    context = AnonymizationContext()
    
    # Simple STIX indicator
    stix_indicator = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": "indicator--a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
        "created": "2021-01-01T00:00:00.000Z",
        "modified": "2021-01-01T00:00:00.000Z",
        "name": "Test Indicator with IP 192.168.1.1",
        "description": "This is a test indicator with IP 192.168.1.1",
        "indicator_types": ["malicious-activity"],
        "pattern_type": "stix",
        "pattern": "[ipv4-addr:value = '192.168.1.1']",
        "valid_from": "2021-01-01T00:00:00.000Z"
    }
    
    try:
        anonymized = context.anonymize_stix_object(stix_indicator, AnonymizationLevel.MEDIUM)
        print("STIX anonymization successful:")
        parsed = json.loads(anonymized)
        print(f"  - Original ID: {stix_indicator['id']}")
        print(f"  - Anonymized ID: {parsed['id']}")
        print(f"  - Original pattern: {stix_indicator['pattern']}")
        print(f"  - Anonymized pattern: {parsed['pattern']}")
        print(f"  - Original description: {stix_indicator['description']}")
        print(f"  - Anonymized description: {parsed['description']}")
    except Exception as e:
        print(f"STIX anonymization error: {e}")

if __name__ == "__main__":
    test_basic_anonymization()
    test_auto_detection()
    test_stix_anonymization()