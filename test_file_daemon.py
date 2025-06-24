#!/usr/bin/env python3
"""
Test script for file-based daemon
"""

import json
import os
import time
import shutil
from pathlib import Path


def setup_test_environment():
    """Set up test directories and sample files"""
    
    # Create test directories
    test_dirs = ["input", "output", "test_data"]
    for dir_name in test_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("Created test directories: input/, output/, test_data/")
    
    # Sample STIX objects with different trust levels
    test_files = {
        "stix_high_trust.json": {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--high-trust-001",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "High Trust IP",
            "description": "Malicious IP 10.0.0.1 from trusted partner",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[ipv4-addr:value = '10.0.0.1']",
            "valid_from": "2024-01-01T00:00:00.000Z"
        },
        
        "stix_medium_trust.json": {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--medium-trust-001",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "Medium Trust Domain",
            "description": "Suspicious domain malicious.example.com",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[domain-name:value = 'malicious.example.com']",
            "valid_from": "2024-01-01T00:00:00.000Z"
        },
        
        "stix_low_trust.json": {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--low-trust-001",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "Low Trust Email",
            "description": "Phishing email from attacker@evil.com",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[email-addr:value = 'attacker@evil.com']",
            "valid_from": "2024-01-01T00:00:00.000Z"
        },
        
        "stix_bundle.json": {
            "type": "bundle",
            "id": "bundle--test-001",
            "objects": [
                {
                    "type": "indicator",
                    "spec_version": "2.1",
                    "id": "indicator--bundle-001",
                    "created": "2024-01-01T00:00:00.000Z",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "name": "Bundle IP",
                    "description": "IP address 192.168.1.100 in bundle",
                    "indicator_types": ["malicious-activity"],
                    "pattern_type": "stix",
                    "pattern": "[ipv4-addr:value = '192.168.1.100']",
                    "valid_from": "2024-01-01T00:00:00.000Z"
                },
                {
                    "type": "indicator",
                    "spec_version": "2.1",
                    "id": "indicator--bundle-002",
                    "created": "2024-01-01T00:00:00.000Z",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "name": "Bundle URL",
                    "description": "Malicious URL https://evil.com/malware.exe",
                    "indicator_types": ["malicious-activity"],
                    "pattern_type": "stix",
                    "pattern": "[url:value = 'https://evil.com/malware.exe']",
                    "valid_from": "2024-01-01T00:00:00.000Z"
                }
            ]
        }
    }
    
    # Write test files to test_data directory
    for filename, data in test_files.items():
        file_path = Path("test_data") / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Created test file: {file_path}")
    
    print(f"\nCreated {len(test_files)} test files in test_data/")
    return test_files.keys()


def copy_files_to_input(filenames, delay=2):
    """Copy test files to input directory with delay"""
    print(f"\nCopying files to input/ directory...")
    
    for filename in filenames:
        src = Path("test_data") / filename
        dst = Path("input") / filename
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"Copied {filename} to input/")
            time.sleep(delay)  # Delay between files
        else:
            print(f"Warning: {src} not found")


def monitor_output():
    """Monitor output directory for results"""
    print("\nMonitoring output directory...")
    
    output_dir = Path("output")
    processed_dir = output_dir / "processed"
    error_dir = output_dir / "errors"
    
    while True:
        try:
            # Count files in each directory
            output_files = list(output_dir.glob("anonymized_*.json"))
            processed_files = list(processed_dir.glob("*.json")) if processed_dir.exists() else []
            error_files = list(error_dir.glob("*.json")) if error_dir.exists() else []
            
            print(f"\rOutput: {len(output_files)} | Processed: {len(processed_files)} | Errors: {len(error_files)}", end="")
            
            # Show latest output file
            if output_files:
                latest = max(output_files, key=lambda x: x.stat().st_mtime)
                with open(latest, 'r') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    print(f"\nLatest: {latest.name}")
                    print(f"  Trust: {metadata.get('trust_level')}")
                    print(f"  Anonymization: {metadata.get('anonymization_level')}")
                    print(f"  Time: {metadata.get('processing_time', 0):.3f}s")
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            break


def show_results():
    """Show processing results"""
    print("\n" + "="*50)
    print("PROCESSING RESULTS")
    print("="*50)
    
    output_dir = Path("output")
    
    # Show anonymized files
    anonymized_files = list(output_dir.glob("anonymized_*.json"))
    print(f"\nAnonymized files ({len(anonymized_files)}):")
    
    for file_path in sorted(anonymized_files):
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        metadata = data.get('metadata', {})
        anonymized_data = data.get('anonymized_data', {})
        
        print(f"\n{file_path.name}:")
        print(f"  Original file: {metadata.get('original_file')}")
        print(f"  Trust level: {metadata.get('trust_level')}")
        print(f"  Anonymization level: {metadata.get('anonymization_level')}")
        print(f"  Processing time: {metadata.get('processing_time', 0):.3f}s")
        
        # Show pattern anonymization example
        if anonymized_data.get('pattern'):
            print(f"  Anonymized pattern: {anonymized_data['pattern']}")
        elif anonymized_data.get('objects'):
            # Bundle case
            patterns = [obj.get('pattern') for obj in anonymized_data['objects'] if obj.get('pattern')]
            if patterns:
                print(f"  Bundle patterns: {patterns}")
    
    # Show errors if any
    error_dir = output_dir / "errors"
    if error_dir.exists():
        error_files = list(error_dir.glob("error_*.json"))
        if error_files:
            print(f"\nErrors ({len(error_files)}):")
            for error_file in error_files:
                with open(error_file, 'r') as f:
                    error_data = json.load(f)
                print(f"  {error_data.get('file')}: {error_data.get('error')}")


def cleanup():
    """Clean up test directories"""
    dirs_to_remove = ["input", "output", "test_data"]
    
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Removed {dir_name}/")


def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_test_environment()
        elif sys.argv[1] == "feed":
            filenames = setup_test_environment()
            print("\nStarting to feed files (start daemon in another terminal)...")
            copy_files_to_input(filenames)
        elif sys.argv[1] == "monitor":
            monitor_output()
        elif sys.argv[1] == "results":
            show_results()
        elif sys.argv[1] == "cleanup":
            cleanup()
        else:
            print("Usage: python test_file_daemon.py [setup|feed|monitor|results|cleanup]")
    else:
        # Full test sequence
        print("Setting up test environment...")
        filenames = setup_test_environment()
        
        print("\nTest files created. Now run the daemon in another terminal:")
        print("python file_daemon.py --input-dir input --output-dir output")
        print("\nThen run this script with 'feed' to send files:")
        print("python test_file_daemon.py feed")


if __name__ == "__main__":
    main()