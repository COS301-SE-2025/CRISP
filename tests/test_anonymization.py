"""
Simple test script for testing STIX anonymization in the CRISP system
"""

import sys
import os
import json

# Add the parent directory to the Python path to import our package
sys.path.insert(0, os.path.abspath('.'))

# Import from crisp_anonymization
from crisp_anonymization.enums import AnonymizationLevel
from crisp_anonymization.context import AnonymizationContext

def test_stix_anonymization():
    """Test STIX object anonymization with different trust levels"""
    print("\n=== STIX Anonymization Test ===\n")
    
    # Create the anonymization context
    context = AnonymizationContext()
    
    # Create a mock STIX indicator object
    stix_indicator = {
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
    
    # Display the original STIX object
    print("Original STIX Indicator:")
    print(json.dumps(stix_indicator, indent=2))
    print()
    
    # Test anonymization at different levels
    levels = [
        ("LOW", AnonymizationLevel.LOW),
        ("MEDIUM", AnonymizationLevel.MEDIUM),
        ("HIGH", AnonymizationLevel.HIGH)
    ]
    
    for level_name, level in levels:
        print(f"=== Anonymization Level: {level_name} ===")
        
        try:
            # Anonymize the STIX object
            anonymized = context.anonymize_stix_object(stix_indicator, level)
            anonymized_obj = json.loads(anonymized)
            
            # Display key parts that should be anonymized
            print(f"ID: {anonymized_obj['id']}")
            print(f"Name: {anonymized_obj['name']}")
            print(f"Description: {anonymized_obj['description']}")
            print(f"Pattern: {anonymized_obj['pattern']}")
            print(f"Custom field (x_analyst_notes): {anonymized_obj['x_analyst_notes']}")
            print()
            
            # Check if sensitive data was properly anonymized
            if "192.168.1.100" in anonymized:
                print("WARNING: Original IP address still present in anonymized data!")
            
            if "evil-domain.com" in anonymized:
                print("WARNING: Original domain still present in anonymized data!")
            
            if "user@example.com" in anonymized:
                print("WARNING: Original email still present in anonymized data!")
            
        except Exception as e:
            print(f"Error during anonymization: {e}")
    
    print("\n=== STIX Bundle Test ===\n")
    
    # Create a mock STIX bundle with multiple objects
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
                "type": "domain-name",
                "spec_version": "2.1",
                "id": "domain-name--5e29b5e5-8a26-4a04-9c1d-56bc22d90ded",
                "value": "evil-domain.com"
            },
            {
                "type": "relationship",
                "spec_version": "2.1",
                "id": "relationship--87654321-4321-8765-cba9-876543210987",
                "created": "2021-03-01T15:30:00.000Z",
                "modified": "2021-03-01T15:30:00.000Z",
                "relationship_type": "indicates",
                "source_ref": "indicator--d81f86b8-975b-4c0b-875e-810c5ad40ac2",
                "target_ref": "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd"
            }
        ]
    }
    
    # Test bundle anonymization at MEDIUM level
    try:
        print("Anonymizing STIX Bundle at MEDIUM level...")
        anonymized = context.anonymize_stix_object(stix_bundle, AnonymizationLevel.MEDIUM)
        anonymized_obj = json.loads(anonymized)
        
        # Check the bundle ID
        print(f"Original Bundle ID: {stix_bundle['id']}")
        print(f"Anonymized Bundle ID: {anonymized_obj['id']}")
        print()
        
        # Check the objects
        print(f"Number of objects: {len(anonymized_obj['objects'])}")
        
        # Check each object type
        for obj in anonymized_obj['objects']:
            obj_type = obj['type']
            
            if obj_type == 'ipv4-addr':
                print(f"IPv4 Address Object: {obj['value']}")
            elif obj_type == 'domain-name':
                print(f"Domain Name Object: {obj['value']}")
            elif obj_type == 'relationship':
                print(f"Relationship Object: {obj['relationship_type']}")
                print(f"  Source Ref: {obj['source_ref']}")
                print(f"  Target Ref: {obj['target_ref']}")
        
        # Check referential integrity
        print("\nChecking referential integrity...")
        
        # Find all object IDs
        object_ids = [obj['id'] for obj in anonymized_obj['objects']]
        
        # Check if relationship references valid objects
        for obj in anonymized_obj['objects']:
            if obj['type'] == 'relationship':
                source_ref = obj['source_ref']
                target_ref = obj['target_ref']
                
                if source_ref in object_ids:
                    print(f"Source reference {source_ref} is valid ✓")
                else:
                    print(f"Source reference {source_ref} is INVALID ✗")
                
                if target_ref in object_ids:
                    print(f"Target reference {target_ref} is valid ✓")
                else:
                    print(f"Target reference {target_ref} is INVALID ✗")
        
    except Exception as e:
        print(f"Error during bundle anonymization: {e}")

if __name__ == "__main__":
    test_stix_anonymization()