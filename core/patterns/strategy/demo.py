"""
Demonstration script for the CRISP Anonymization System

Shows basic usage examples and capabilities of the anonymization system.
"""

import json
from typing import Dict, Any

try:
    from .enums import AnonymizationLevel, DataType
    from .context import AnonymizationContext
except ImportError:
    from enums import AnonymizationLevel, DataType
    from context import AnonymizationContext


def demonstrate_anonymization():
    """Demonstrate the anonymization system with various data types"""
    print("=== CRISP Anonymization System Demo ===\n")
    
    # Create anonymization context
    context = AnonymizationContext()
    
    # Test data
    test_data = [
        ("192.168.1.100", DataType.IP_ADDRESS),
        ("2001:db8::1", DataType.IP_ADDRESS),
        ("malicious.example.com", DataType.DOMAIN),
        ("admin@company.edu", DataType.EMAIL),
        ("https://evil.example.org/malware.exe", DataType.URL),
    ]
    
    levels = [AnonymizationLevel.LOW, AnonymizationLevel.MEDIUM, 
              AnonymizationLevel.HIGH, AnonymizationLevel.FULL]
    
    for data, data_type in test_data:
        print(f"Original: {data} ({data_type.value})")
        for level in levels:
            anonymized = context.execute_anonymization(data, data_type, level)
            print(f"  {level.value.upper():6}: {anonymized}")
        print()
    
    # Test auto-detection
    print("=== Auto-Detection Demo ===")
    auto_test_data = [
        "10.0.0.1",
        "badguy@evil.com", 
        "suspicious.domain.net",
        "http://malware-site.com/payload"
    ]
    
    for data in auto_test_data:
        print(f"Auto-detecting: {data}")
        for level in [AnonymizationLevel.LOW, AnonymizationLevel.HIGH]:
            anonymized = context.auto_detect_and_anonymize(data, level)
            print(f"  {level.value.upper():4}: {anonymized}")
        print()


def test_bulk_anonymization():
    """Test bulk anonymization functionality"""
    print("=== Bulk Anonymization Demo ===\n")
    
    context = AnonymizationContext()
    
    # Bulk test data
    bulk_data = [
        ("192.168.1.1", DataType.IP_ADDRESS),
        ("192.168.1.2", DataType.IP_ADDRESS),
        ("evil1.com", DataType.DOMAIN),
        ("evil2.com", DataType.DOMAIN),
        ("attacker@malicious.org", DataType.EMAIL),
    ]
    
    print("Original data:")
    for data, data_type in bulk_data:
        print(f"  {data} ({data_type.value})")
    
    print(f"\nBulk anonymization at MEDIUM level:")
    results = context.bulk_anonymize(bulk_data, AnonymizationLevel.MEDIUM)
    for i, result in enumerate(results):
        print(f"  {bulk_data[i][0]} -> {result}")


def demonstrate_stix_anonymization():
    """Demonstrate STIX anonymization capabilities"""
    print("\n=== STIX Anonymization Demo ===\n")
    
    context = AnonymizationContext()
    
    # Sample STIX Indicator
    stix_indicator = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": "indicator--d81f86b8-975b-4c0b-875e-810c5ad40ac2",
        "created": "2021-03-01T15:30:00.000Z",
        "modified": "2021-03-01T15:30:00.000Z",
        "name": "Malicious IP Address 192.168.1.100",
        "description": "This IP address 192.168.1.100 was observed in malicious activity",
        "indicator_types": ["malicious-activity"],
        "pattern_type": "stix",
        "pattern": "[ipv4-addr:value = '192.168.1.100']",
        "valid_from": "2021-03-01T15:30:00.000Z",
        "x_internal_id": "ACME-2024-001",
        "external_references": [
            {
                "source_name": "internal-analysis",
                "url": "https://internal.example.com/report/123",
                "external_id": "REPORT-123"
            }
        ]
    }
    
    print("Original STIX Indicator:")
    print(json.dumps(stix_indicator, indent=2))
    
    # Anonymize at different levels
    for level in [AnonymizationLevel.LOW, AnonymizationLevel.HIGH]:
        print(f"\nAnonymized STIX Indicator ({level.value.upper()}):")
        anonymized = context.anonymize_stix_object(stix_indicator, level)
        print(anonymized)
    
    # Sample STIX Bundle with multiple objects
    stix_bundle = {
        "type": "bundle",
        "spec_version": "2.1",
        "id": "bundle--12345678-1234-5678-9abc-123456789012",
        "objects": [
            stix_indicator,
            {
                "type": "ipv4-addr",
                "spec_version": "2.1",
                "id": "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd",
                "value": "192.168.1.100"
            },
            {
                "type": "relationship",
                "spec_version": "2.1",
                "id": "relationship--87654321-4321-8765-cba9-876543210987",
                "created": "2021-01-01T00:00:00.000Z",
                "modified": "2021-01-01T00:00:00.000Z",
                "relationship_type": "indicates",
                "source_ref": "indicator--d81f86b8-975b-4c0b-875e-810c5ad40ac2",
                "target_ref": "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd"
            }
        ]
    }
    
    print("\n=== STIX Bundle Anonymization ===\n")
    print("Anonymized STIX Bundle (MEDIUM level):")
    anonymized_bundle = context.anonymize_stix_object(stix_bundle, AnonymizationLevel.MEDIUM)
    print(anonymized_bundle)


if __name__ == "__main__":
    demonstrate_anonymization()
    print("\n" + "="*50 + "\n")
    test_bulk_anonymization()
    print("\n" + "="*50 + "\n")
    demonstrate_stix_anonymization()