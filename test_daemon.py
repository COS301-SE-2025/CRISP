#!/usr/bin/env python3
"""
Test script for the CRISP Anonymization Daemon

This script demonstrates how to send STIX data to the daemon and receive anonymized results.
"""

import json
import time
import redis
from datetime import datetime, timezone


def test_daemon_integration():
    """Test the daemon by sending sample STIX data"""
    
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
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
            "valid_from": "2024-01-01T00:00:00.000Z",
            "metadata": {
                "trust_level": "high",
                "institution": "partner_institution_1"
            }
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
            "valid_from": "2024-01-01T00:00:00.000Z",
            "metadata": {
                "trust_level": "low",
                "institution": "external_feed"
            }
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
            "valid_from": "2024-01-01T00:00:00.000Z",
            "metadata": {
                "trust_level": "untrusted",
                "institution": "untrusted_source"
            }
        }
    ]
    
    print("Testing CRISP Anonymization Daemon")
    print("=" * 50)
    
    # Send test data to input queue
    print(f"Sending {len(test_stix_objects)} STIX objects to input queue...")
    
    for i, stix_obj in enumerate(test_stix_objects):
        message = {
            "stix_data": stix_obj,
            "metadata": stix_obj.get("metadata", {}),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        r.rpush("stix_input", json.dumps(message))
        print(f"  Sent object {i+1}: {stix_obj['id']}")
    
    print("\nWaiting for daemon to process objects...")
    time.sleep(5)
    
    # Check output queue
    print("\nChecking output queue for anonymized results...")
    output_count = r.llen("stix_anonymized")
    print(f"Found {output_count} anonymized objects")
    
    for i in range(output_count):
        result = r.lpop("stix_anonymized")
        if result:
            result_data = json.loads(result)
            print(f"\nAnonymized object {i+1}:")
            print(f"  Original ID: {result_data.get('original_id')}")
            print(f"  Trust level: {result_data.get('metadata', {}).get('trust_level')}")
            print(f"  Anonymization level: {result_data.get('metadata', {}).get('anonymization_level')}")
            print(f"  Processing time: {result_data.get('metadata', {}).get('processing_time'):.3f}s")
            
            # Show example of anonymized pattern
            stix_data = result_data.get('stix_data', {})
            if 'pattern' in stix_data:
                print(f"  Anonymized pattern: {stix_data['pattern']}")
    
    # Check error queue
    error_count = r.llen("stix_errors")
    if error_count > 0:
        print(f"\nFound {error_count} errors:")
        for i in range(error_count):
            error = r.lpop("stix_errors")
            if error:
                error_data = json.loads(error)
                print(f"  Error {i+1}: {error_data.get('error')}")
    
    print("\nTest completed!")


def monitor_queues():
    """Monitor queue lengths"""
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    print("Queue Monitor")
    print("=" * 30)
    
    while True:
        input_len = r.llen("stix_input")
        output_len = r.llen("stix_anonymized")
        error_len = r.llen("stix_errors")
        
        print(f"\rInput: {input_len:3d} | Output: {output_len:3d} | Errors: {error_len:3d}", end="")
        time.sleep(1)


def clear_queues():
    """Clear all queues"""
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    queues = ["stix_input", "stix_anonymized", "stix_errors"]
    
    for queue in queues:
        count = r.delete(queue)
        print(f"Cleared queue '{queue}': {count} items removed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_daemon_integration()
        elif sys.argv[1] == "monitor":
            try:
                monitor_queues()
            except KeyboardInterrupt:
                print("\nMonitoring stopped")
        elif sys.argv[1] == "clear":
            clear_queues()
        else:
            print("Usage: python test_daemon.py [test|monitor|clear]")
    else:
        test_daemon_integration()