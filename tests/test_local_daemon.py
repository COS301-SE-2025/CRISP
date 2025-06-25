#!/usr/bin/env python3
"""
Local test for CRISP Anonymization Daemon without Redis/RabbitMQ

This directly tests the anonymization functionality using the daemon's processing methods.
"""

import json
import time
from datetime import datetime, timezone
from crisp_anonymization_daemon import AnonymizationDaemon, DaemonConfig


def test_local_anonymization():
    """Test anonymization locally without message queues"""
    
    # Create daemon config for local testing
    config = DaemonConfig(
        log_level="INFO",
        default_trust_level="medium"
    )
    
    # Create daemon instance
    daemon = AnonymizationDaemon(config)
    daemon.local_mode = True  # Enable local mode
    
    # Sample STIX objects for testing
    test_stix_objects = [
        {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--test-001",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "Malicious IP Address",
            "description": "This IP address 192.168.1.100 was observed in malicious activity",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[ipv4-addr:value = '192.168.1.100']",
            "valid_from": "2024-01-01T00:00:00.000Z"
        },
        {
            "type": "indicator", 
            "spec_version": "2.1",
            "id": "indicator--test-002",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "Suspicious Domain",
            "description": "Domain malicious-site.evil-corp.net used for C2 communication",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[domain-name:value = 'malicious-site.evil-corp.net']",
            "valid_from": "2024-01-01T00:00:00.000Z"
        },
        {
            "type": "indicator",
            "spec_version": "2.1", 
            "id": "indicator--test-003",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "Phishing Email",
            "description": "Phishing email from attacker@phishing-campaign.org",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[email-addr:value = 'attacker@phishing-campaign.org']",
            "valid_from": "2024-01-01T00:00:00.000Z"
        }
    ]
    
    print("Testing CRISP Anonymization Daemon (Local Mode)")
    print("=" * 55)
    
    # Test different trust levels
    trust_levels = ["high", "medium", "low", "untrusted"]
    
    for trust_level in trust_levels:
        print(f"\n--- Testing with '{trust_level}' trust level ---")
        
        for i, stix_obj in enumerate(test_stix_objects):
            print(f"\nProcessing object {i+1}: {stix_obj['id']}")
            print(f"Original pattern: {stix_obj['pattern']}")
            
            # Process the STIX object
            result = daemon._process_stix_object(stix_obj, trust_level)
            
            if result.success:
                anonymized_pattern = result.anonymized_data.get('pattern', 'N/A')
                print(f"Anonymized pattern: {anonymized_pattern}")
                print(f"Trust level: {result.trust_level}")
                print(f"Anonymization level: {result.anonymization_level}")
                print(f"Processing time: {result.processing_time:.3f}s")
            else:
                print(f"Error: {result.error_message}")
    
    print(f"\nProcessing complete!")
    print(f"Total processed: {daemon.stats['processed']}")
    print(f"Total errors: {daemon.stats['errors']}")


def test_with_file_input():
    """Test with STIX data from a file"""
    
    # Create daemon config
    config = DaemonConfig(log_level="INFO")
    daemon = AnonymizationDaemon(config)
    daemon.local_mode = True
    
    # Try to load from existing test file
    test_files = [
        "tests/data/stix_test_bundle.json",
        "tests/data/test_stix.json"
    ]
    
    for test_file in test_files:
        try:
            with open(test_file, 'r') as f:
                stix_data = json.load(f)
            
            print(f"\nTesting with file: {test_file}")
            print("-" * 40)
            
            # Process the STIX data
            result = daemon._process_stix_object(stix_data, "medium")
            
            if result.success:
                print(f"Successfully anonymized: {result.original_id}")
                print(f"Anonymization level: {result.anonymization_level}")
                print(f"Processing time: {result.processing_time:.3f}s")
                
                # Save anonymized result
                output_file = f"anonymized_{test_file.split('/')[-1]}"
                with open(output_file, 'w') as f:
                    json.dump(result.anonymized_data, f, indent=2)
                print(f"Saved anonymized data to: {output_file}")
            else:
                print(f"Error processing file: {result.error_message}")
            
            break  # Use first available file
            
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error loading {test_file}: {e}")
    else:
        print("No test files found, using sample data instead")
        test_local_anonymization()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "file":
        test_with_file_input()
    else:
        test_local_anonymization()