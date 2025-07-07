"""
Test script for STIX anonymization with custom input
Allows testing with your own STIX objects from files
"""

import sys
import os
import json
import argparse

# Add the project root directory to the Python path to import our package
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'core'))

# Import from core.patterns.strategy
try:
    from core.patterns.strategy.enums import AnonymizationLevel
    from core.patterns.strategy.context import AnonymizationContext
except ImportError:
    print("Error: Could not import CRISP Anonymization System")
    print("Make sure you're running this script from the project directory")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    sys.exit(1)

def load_stix_from_file(file_path):
    """Load STIX object or bundle from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            stix_data = json.load(f)
        return stix_data
    except Exception as e:
        print(f"Error loading STIX data from {file_path}: {e}")
        sys.exit(1)

def save_anonymized_stix(stix_data, output_path):
    """Save anonymized STIX data to a file"""
    try:
        with open(output_path, 'w') as f:
            f.write(stix_data)
        print(f"Anonymized STIX data saved to {output_path}")
    except Exception as e:
        print(f"Error saving anonymized STIX data: {e}")

def get_level_from_trust(trust_level):
    """Convert trust level string to AnonymizationLevel"""
    trust_map = {
        "high": AnonymizationLevel.LOW,
        "medium": AnonymizationLevel.MEDIUM,
        "low": AnonymizationLevel.HIGH,
        "untrusted": AnonymizationLevel.FULL
    }
    
    return trust_map.get(trust_level.lower(), AnonymizationLevel.MEDIUM)

def anonymize_stix_data(stix_data, level, output_file=None):
    """Anonymize STIX object with specified level"""
    print("\n=== STIX Anonymization Test ===\n")
    
    # Create the anonymization context
    context = AnonymizationContext()
    
    # Display information about the input STIX data
    print("Input STIX data type:", stix_data.get("type", "unknown"))
    
    if stix_data.get("type") == "bundle" and "objects" in stix_data:
        print(f"Bundle contains {len(stix_data['objects'])} objects")
        object_types = {}
        for obj in stix_data["objects"]:
            obj_type = obj.get("type", "unknown")
            object_types[obj_type] = object_types.get(obj_type, 0) + 1
        
        print("Object types in bundle:")
        for obj_type, count in object_types.items():
            print(f"  - {obj_type}: {count}")
    
    print(f"\nAnonymizing at {level.value.upper()} level...")
    
    try:
        # Anonymize the STIX object
        anonymized = context.anonymize_stix_object(stix_data, level)
        anonymized_obj = json.loads(anonymized)
        
        # Save to output file if specified
        if output_file:
            save_anonymized_stix(anonymized, output_file)
        
        # Display key differences for individual objects
        if stix_data.get("type") != "bundle":
            print("\nKey field anonymization:")
            
            # Check for common sensitive fields
            fields_to_check = ["id", "name", "description", "pattern"]
            for field in fields_to_check:
                if field in stix_data and field in anonymized_obj:
                    print(f"{field}:")
                    print(f"  Original: {stix_data[field]}")
                    print(f"  Anonymized: {anonymized_obj[field]}")
                    print()
            
            # Check for cyber observable values
            if stix_data.get("type") in ["ipv4-addr", "ipv6-addr", "domain-name", "url", "email-addr"] and "value" in stix_data:
                print("value:")
                print(f"  Original: {stix_data['value']}")
                print(f"  Anonymized: {anonymized_obj['value']}")
                print()
        
        # Display bundle statistics for bundles
        else:
            print("\nBundle anonymization summary:")
            print(f"Original bundle ID: {stix_data['id']}")
            print(f"Anonymized bundle ID: {anonymized_obj['id']}")
            print(f"Object count: {len(anonymized_obj['objects'])}")
            
            # Check referential integrity
            print("\nChecking referential integrity...")
            ref_fields = ["source_ref", "target_ref", "sighting_of_ref", "observed_data_ref"]
            ref_count = 0
            valid_refs = 0
            
            # Get all object IDs
            object_ids = [obj["id"] for obj in anonymized_obj["objects"]]
            
            # Check references
            for obj in anonymized_obj["objects"]:
                for field in ref_fields:
                    if field in obj:
                        ref_count += 1
                        ref_value = obj[field]
                        if ref_value in object_ids:
                            valid_refs += 1
                        else:
                            print(f"WARNING: Invalid reference {field}={ref_value} in object {obj['id']}")
            
            if ref_count > 0:
                print(f"Reference integrity: {valid_refs}/{ref_count} valid references")
            else:
                print("No references found to check")
        
        print("\nAnonymization completed successfully.")
        
    except Exception as e:
        print(f"Error during anonymization: {e}")
        raise

def main():
    """Main function to parse arguments and run the test"""
    parser = argparse.ArgumentParser(description="Test STIX anonymization with custom input")
    parser.add_argument("--file", "-f", help="Path to a STIX JSON file to anonymize")
    parser.add_argument("--trust", "-t", choices=["high", "medium", "low", "untrusted"],
                        default="medium", help="Trust level (default: medium)")
    parser.add_argument("--output", "-o", help="Output file for anonymized STIX data")
    
    args = parser.parse_args()
    
    # Use default STIX object if no file is provided
    if args.file:
        stix_data = load_stix_from_file(args.file)
    else:
        # Create a mock STIX indicator object
        stix_data = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--d81f86b8-975b-4c0b-875e-810c5ad40ac2",
            "created": "2021-03-01T15:30:00.000Z",
            "modified": "2021-03-01T15:30:00.000Z",
            "name": "Malicious IP and Domain",
            "description": "This IP address 192.168.1.100 and domain evil-domain.com were observed in malicious activity",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[ipv4-addr:value = '192.168.1.100'] AND [domain-name:value = 'evil-domain.com']",
            "valid_from": "2021-03-01T15:30:00.000Z",
            "x_organization": "Security Org",
            "x_analyst_notes": "Contacted by user@example.com about this threat"
        }
        print("Using default STIX indicator (no file provided)")
    
    # Get anonymization level from trust level
    level = get_level_from_trust(args.trust)
    
    # Run the anonymization
    anonymize_stix_data(stix_data, level, args.output)

if __name__ == "__main__":
    main()