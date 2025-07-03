#!/usr/bin/env python3
"""
Test script for anonymizing the complex STIX 2.0 test file
"""

import json
import sys
import os
from typing import Dict, Any, List
import argparse

# Add the parent directory to the Python path to import our package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.patterns.strategy.enums import AnonymizationLevel, DataType
    from core.patterns.strategy.context import AnonymizationContext
except ImportError:
    print("Error: Could not import CRISP Anonymization System")
    print("Make sure you're running this script from the project directory")
    sys.exit(1)


def load_stix_data(file_path: str) -> Dict[str, Any]:
    """Load STIX data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading STIX data from {file_path}: {e}")
        sys.exit(1)


def save_stix_data(file_path: str, data: str) -> None:
    """Save STIX data to JSON file"""
    try:
        with open(file_path, 'w') as f:
            f.write(data)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")


def verify_stix_data(data: Dict[str, Any]) -> bool:
    """Verify basic STIX structure"""
    if not isinstance(data, dict):
        print("Error: STIX data is not a dictionary")
        return False
    
    if 'type' not in data:
        print("Error: STIX data missing 'type' field")
        return False
    
    if data['type'] == 'bundle' and ('objects' not in data or not isinstance(data['objects'], list)):
        print("Error: STIX bundle missing 'objects' array")
        return False
    
    return True


def find_sensitive_data(data: Dict[str, Any]) -> List[str]:
    """Find sensitive data patterns in STIX data for verification"""
    sensitive_patterns = []
    json_str = json.dumps(data)
    
    # IP addresses
    import re
    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    ip_matches = re.findall(ip_pattern, json_str)
    sensitive_patterns.extend([f"IP: {ip}" for ip in set(ip_matches)])
    
    # Domains
    domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    domain_matches = re.findall(domain_pattern, json_str)
    sensitive_patterns.extend([f"Domain: {domain}" for domain in set(domain_matches) if 'example' in domain])
    
    # Email addresses
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    email_matches = re.findall(email_pattern, json_str)
    sensitive_patterns.extend([f"Email: {email}" for email in set(email_matches)])
    
    # URLs
    url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    url_matches = re.findall(url_pattern, json_str)
    sensitive_patterns.extend([f"URL: {url}" for url in set(url_matches)])
    
    return sensitive_patterns


def check_anonymization(original_data: Dict[str, Any], anonymized_str: str) -> bool:
    """Check if sensitive data has been properly anonymized"""
    # Get sensitive data from original
    sensitive_data = find_sensitive_data(original_data)
    
    # Check if any sensitive data still exists in anonymized data
    success = True
    for item in sensitive_data:
        data_type, value = item.split(': ', 1)
        
        # Skip example.com domains as they may be used in anonymized output
        if data_type == "Domain" and "example.com" in value:
            continue
            
        if value in anonymized_str:
            print(f"WARNING: Sensitive data still present: {item}")
            success = False
    
    return success


def check_reference_integrity(anonymized_data: Dict[str, Any]) -> bool:
    """Check if object references are still valid after anonymization"""
    if anonymized_data.get('type') != 'bundle' or 'objects' not in anonymized_data:
        print("Not a bundle, skipping reference integrity check")
        return True
    
    # Extract all object IDs
    object_ids = set()
    for obj in anonymized_data['objects']:
        if 'id' in obj:
            object_ids.add(obj['id'])
    
    # Check all reference fields
    ref_fields = ['created_by_ref', 'object_marking_refs', 'source_ref', 'target_ref', 'sighting_of_ref']
    
    success = True
    for obj in anonymized_data['objects']:
        for field in ref_fields:
            if field in obj:
                if isinstance(obj[field], list):
                    for ref in obj[field]:
                        if ref not in object_ids:
                            print(f"Invalid reference: {field}={ref} in object {obj.get('id')}")
                            success = False
                else:
                    if obj[field] not in object_ids:
                        print(f"Invalid reference: {field}={obj[field]} in object {obj.get('id')}")
                        success = False
    
    return success


def analyze_stix_version(data: Dict[str, Any]) -> None:
    """Analyze and print STIX version information"""
    context = AnonymizationContext()
    version = context._detect_stix_version(data)
    
    print(f"Detected STIX version: {version}")
    print(f"Has 'spec_version' field: {'spec_version' in data}")
    
    if data.get('type') == 'bundle' and 'objects' in data:
        print(f"Bundle contains {len(data['objects'])} objects")
        
        # Count object types
        object_types = {}
        for obj in data['objects']:
            obj_type = obj.get('type', 'unknown')
            object_types[obj_type] = object_types.get(obj_type, 0) + 1
        
        print("Object types:")
        for obj_type, count in sorted(object_types.items()):
            print(f"  - {obj_type}: {count}")
        
        # Check for spec_version in objects
        objects_with_spec_version = sum(1 for obj in data['objects'] if 'spec_version' in obj)
        print(f"Objects with 'spec_version' field: {objects_with_spec_version}/{len(data['objects'])}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test STIX 2.0 Anonymization')
    parser.add_argument('--file', '-f', default='test_complex_stix_2_0.json',
                      help='Path to STIX 2.0 JSON file (default: test_complex_stix_2_0.json)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--level', '-l', choices=['low', 'medium', 'high', 'full'],
                       default='medium', help='Anonymization level (default: medium)')
    parser.add_argument('--analyze', '-a', action='store_true',
                       help='Only analyze STIX version without anonymizing')
    
    args = parser.parse_args()
    
    # Load STIX data
    print(f"Loading STIX data from {args.file}")
    stix_data = load_stix_data(args.file)
    
    # Verify STIX structure
    if not verify_stix_data(stix_data):
        print("Invalid STIX data structure")
        sys.exit(1)
    
    # Create anonymization context
    context = AnonymizationContext()
    
    # Analyze STIX version
    analyze_stix_version(stix_data)
    
    if args.analyze:
        # Only version analysis was requested
        sys.exit(0)
    
    # Map level string to enum
    level_map = {
        'low': AnonymizationLevel.LOW,
        'medium': AnonymizationLevel.MEDIUM,
        'high': AnonymizationLevel.HIGH,
        'full': AnonymizationLevel.FULL
    }
    level = level_map.get(args.level.lower(), AnonymizationLevel.MEDIUM)
    
    print(f"\nAnonymizing with {level.value.upper()} level...")
    
    # Anonymize the data
    try:
        anonymized = context.anonymize_stix_object(stix_data, level)
        anonymized_obj = json.loads(anonymized)
        
        # Check anonymization
        print("\nChecking anonymization...")
        if check_anonymization(stix_data, anonymized):
            print("All sensitive data has been properly anonymized!")
        
        # Check reference integrity
        print("\nChecking reference integrity...")
        if check_reference_integrity(anonymized_obj):
            print("All object references are valid!")
        
        # Save to output file
        output_path = args.output
        if not output_path:
            output_path = args.file.replace('.json', f'_anonymized_{level.value}.json')
        
        save_stix_data(output_path, anonymized)
        
        print("\nAnonymization completed successfully!")
        
    except Exception as e:
        print(f"Error during anonymization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()