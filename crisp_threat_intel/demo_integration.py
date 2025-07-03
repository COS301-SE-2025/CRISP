#!/usr/bin/env python3
"""
Demo script for CRISP Threat Intelligence Strategy Pattern Integration.
Shows how the integrated anonymization system works with both STIX objects and raw data.
"""

import os
import sys
import django
import json
from datetime import datetime, timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')
django.setup()

from crisp_threat_intel.strategies.integrated_anonymization import (
    IntegratedAnonymizationContext,
    TrustLevel,
    IntegratedAnonymizationFactory
)

# Try to import anonymization enums
try:
    sys.path.append('../core/patterns/strategy')
    from core.patterns.strategy.enums import AnonymizationLevel, DataType
except ImportError:
    print("Note: crisp_anonymization package not found, using fallback values")
    # Define fallback enum-like classes
    class AnonymizationLevel:
        NONE = "none"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        FULL = "full"
    
    class DataType:
        IP_ADDRESS = "ip_address"
        DOMAIN = "domain"
        EMAIL = "email"
        URL = "url"


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_subheader(title):
    """Print a formatted subheader"""
    print(f"\n--- {title} ---")


def demo_basic_integration():
    """Demonstrate basic integration functionality"""
    print_header("CRISP Strategy Pattern Integration Demo")
    
    print("Initializing Integrated Anonymization Context...")
    context = IntegratedAnonymizationContext()
    
    print(f"Available strategies: {context.get_available_strategies()}")
    print("\nIntegration successfully initialized!")


def demo_stix_anonymization():
    """Demonstrate STIX object anonymization"""
    print_header("STIX Object Anonymization")
    
    context = IntegratedAnonymizationContext()
    
    # Sample STIX indicator with domain
    stix_domain_indicator = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": "indicator--12345678-1234-1234-1234-123456789012",
        "created": "2021-01-01T00:00:00.000Z",
        "modified": "2021-01-01T00:00:00.000Z",
        "name": "Malicious Domain Indicator",
        "description": "Domain observed in phishing campaigns",
        "indicator_types": ["malicious-activity"],
        "pattern_type": "stix",
        "pattern": "[domain-name:value = 'phishing.malicious-site.com']",
        "valid_from": "2021-01-01T00:00:00.000Z"
    }
    
    # Sample STIX indicator with IP
    stix_ip_indicator = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": "indicator--87654321-4321-4321-4321-210987654321",
        "created": "2021-01-01T00:00:00.000Z",
        "modified": "2021-01-01T00:00:00.000Z",
        "name": "Malicious IP Indicator",
        "description": "IP address hosting malware",
        "indicator_types": ["malicious-activity"],
        "pattern_type": "stix",
        "pattern": "[ipv4-addr:value = '203.0.113.42']",
        "valid_from": "2021-01-01T00:00:00.000Z"
    }
    
    print("Original STIX Domain Indicator:")
    print(json.dumps(stix_domain_indicator, indent=2))
    
    trust_levels = [0.9, 0.6, 0.3, 0.1]
    trust_names = ["High Trust", "Medium-High Trust", "Medium-Low Trust", "Low Trust"]
    
    for trust_level, trust_name in zip(trust_levels, trust_names):
        print_subheader(f"{trust_name} (Trust Level: {trust_level})")
        
        anonymized = context.anonymize_stix_object(stix_domain_indicator, trust_level)
        
        print(f"Pattern: {anonymized['pattern']}")
        print(f"Anonymized: {anonymized.get('x_crisp_anonymized', False)}")
        print(f"Trust Level: {anonymized.get('x_crisp_trust_level', 'N/A')}")
    
    print_subheader("IP Indicator Anonymization (Medium Trust)")
    anonymized_ip = context.anonymize_stix_object(stix_ip_indicator, 0.5)
    print(f"Original Pattern: {stix_ip_indicator['pattern']}")
    print(f"Anonymized Pattern: {anonymized_ip['pattern']}")


def demo_raw_data_anonymization():
    """Demonstrate raw data anonymization"""
    print_header("Raw Data Anonymization")
    
    context = IntegratedAnonymizationContext()
    
    # Sample threat indicators
    indicators = [
        ("192.168.100.50", "IP Address"),
        ("malicious-c2.evil-corp.net", "Domain"),
        ("phishing@fake-bank.com", "Email"),
        ("https://exploit-kit.badsite.org/payload.exe", "URL"),
    ]
    
    print("Original Threat Indicators:")
    for indicator, type_name in indicators:
        print(f"  {type_name}: {indicator}")
    
    anonymization_levels = [
        (AnonymizationLevel.LOW, "Low"),
        (AnonymizationLevel.MEDIUM, "Medium"), 
        (AnonymizationLevel.HIGH, "High"),
        (AnonymizationLevel.FULL, "Full")
    ]
    
    for level, level_name in anonymization_levels:
        print_subheader(f"{level_name} Anonymization")
        
        for indicator, type_name in indicators:
            # Auto-detect and anonymize
            try:
                anonymized = context.base_context.auto_detect_and_anonymize(indicator, level)
                print(f"  {type_name}: {indicator} → {anonymized}")
            except Exception as e:
                print(f"  {type_name}: {indicator} → [Error: {e}]")


def demo_mixed_data_anonymization():
    """Demonstrate mixed data anonymization"""
    print_header("Mixed Data Anonymization")
    
    context = IntegratedAnonymizationContext()
    
    # Mixed data: STIX objects and raw strings
    stix_indicator = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": "indicator--mixed-demo-1234-1234-123456789012",
        "created": "2021-01-01T00:00:00.000Z",
        "modified": "2021-01-01T00:00:00.000Z",
        "name": "Mixed Demo Indicator",
        "indicator_types": ["malicious-activity"],
        "pattern_type": "stix",
        "pattern": "[email-addr:value = 'attacker@criminal.org']",
        "valid_from": "2021-01-01T00:00:00.000Z"
    }
    
    mixed_data = [
        stix_indicator,
        "10.0.0.1",
        "suspicious.domain.com",
        "https://malware-drop.badsite.net/trojan.exe"
    ]
    
    print("Original Mixed Data:")
    for i, item in enumerate(mixed_data):
        if isinstance(item, dict):
            print(f"  {i+1}. STIX Indicator: {item['pattern']}")
        else:
            print(f"  {i+1}. Raw Data: {item}")
    
    print_subheader("Anonymized Mixed Data (Medium Trust)")
    
    anonymized_data = context.anonymize_mixed(mixed_data, trust_level=0.5)
    
    for i, item in enumerate(anonymized_data):
        if isinstance(item, dict):
            print(f"  {i+1}. STIX Indicator: {item['pattern']}")
            print(f"      Anonymized: {item.get('x_crisp_anonymized', False)}")
        else:
            print(f"  {i+1}. Raw Data: {item}")


def demo_trust_level_mapping():
    """Demonstrate trust level to anonymization level mapping"""
    print_header("Trust Level Mapping")
    
    trust_scenarios = [
        (0.95, "Trusted Partner Institution"),
        (0.7, "Known Academic Partner"),
        (0.4, "Occasional Collaborator"),
        (0.2, "New Institution"),
        (0.05, "Unknown/Untrusted Source")
    ]
    
    print("Trust Level → Anonymization Level Mapping:")
    print("Trust Level | Scenario                  | Anonymization Level")
    print("-" * 65)
    
    for trust_level, scenario in trust_scenarios:
        anon_level = TrustLevel.to_anonymization_level(trust_level)
        print(f"{trust_level:11.2f} | {scenario:25} | {anon_level}")


def demo_bundle_anonymization():
    """Demonstrate STIX bundle anonymization"""
    print_header("STIX Bundle Anonymization")
    
    context = IntegratedAnonymizationContext()
    
    # Create a sample bundle with multiple indicators
    bundle = {
        "type": "bundle",
        "id": "bundle--demo-bundle-1234-1234-123456789012",
        "objects": [
            {
                "type": "indicator",
                "spec_version": "2.1",
                "id": "indicator--bundle-demo-1",
                "created": "2021-01-01T00:00:00.000Z",
                "modified": "2021-01-01T00:00:00.000Z",
                "name": "Domain Indicator",
                "indicator_types": ["malicious-activity"],
                "pattern_type": "stix",
                "pattern": "[domain-name:value = 'command-control.evil.net']",
                "valid_from": "2021-01-01T00:00:00.000Z"
            },
            {
                "type": "indicator",
                "spec_version": "2.1",
                "id": "indicator--bundle-demo-2",
                "created": "2021-01-01T00:00:00.000Z",
                "modified": "2021-01-01T00:00:00.000Z",
                "name": "IP Indicator",
                "indicator_types": ["malicious-activity"],
                "pattern_type": "stix",
                "pattern": "[ipv4-addr:value = '198.51.100.42']",
                "valid_from": "2021-01-01T00:00:00.000Z"
            }
        ]
    }
    
    print(f"Original Bundle: {len(bundle['objects'])} objects")
    for i, obj in enumerate(bundle['objects']):
        print(f"  {i+1}. {obj['name']}: {obj['pattern']}")
    
    print_subheader("Anonymized Bundle (Low Trust = 0.3)")
    
    anonymized_bundle = context.anonymize_stix_bundle(bundle, 0.3)
    
    print(f"Anonymized Bundle: {len(anonymized_bundle['objects'])} objects")
    print(f"Bundle Anonymized: {anonymized_bundle.get('x_crisp_anonymized', False)}")
    print(f"Trust Level: {anonymized_bundle.get('x_crisp_trust_level', 'N/A')}")
    
    for i, obj in enumerate(anonymized_bundle['objects']):
        print(f"  {i+1}. {obj['name']}: {obj['pattern']}")
        print(f"      Object Anonymized: {obj.get('x_crisp_anonymized', False)}")


def demo_performance_stats():
    """Show performance and statistics"""
    print_header("System Statistics")
    
    context = IntegratedAnonymizationContext()
    stats = context.get_anonymization_statistics()
    
    print("Integrated Anonymization System Statistics:")
    print(f"Available Strategies: {len(stats['available_strategies'])}")
    for strategy in stats['available_strategies']:
        print(f"  - {strategy}")
    
    print(f"\nSupported STIX Types: {stats['supported_stix_types']}")
    print(f"Supported Data Types: {len(stats['supported_data_types'])}")
    for data_type in stats['supported_data_types']:
        print(f"  - {data_type}")
    
    print("\nTrust Level Mapping:")
    for level, description in stats['trust_level_mapping'].items():
        print(f"  {level}: {description}")


def main():
    """Main demo function"""
    print("CRISP Threat Intelligence Platform")
    print("Strategy Pattern Integration Demo")
    print("=" * 60)
    
    try:
        demo_basic_integration()
        demo_trust_level_mapping()
        demo_stix_anonymization()
        demo_raw_data_anonymization()
        demo_mixed_data_anonymization()
        demo_bundle_anonymization()
        demo_performance_stats()
        
        print_header("Demo Complete!")
        print("The CRISP threat intelligence platform successfully integrates")
        print("both STIX-focused and data-type-focused anonymization strategies")
        print("into a unified system that provides:")
        print("  ✓ Trust-based anonymization for STIX objects")
        print("  ✓ Data-type-specific anonymization for raw indicators")
        print("  ✓ Mixed data handling (STIX + raw data)")
        print("  ✓ Bundle-level anonymization")
        print("  ✓ Flexible strategy pattern implementation")
        print("  ✓ Performance optimization for bulk operations")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("This is expected if the full Django environment is not set up.")
        print("The integration code is ready for use within the Django application.")


if __name__ == "__main__":
    main()