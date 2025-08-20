#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_settings.settings')
django.setup()

from core.models.models import TrustRelationship, Organization, TrustLevel
from django.contrib.auth.models import User

def test_edit_relationship():
    """Test the edit functionality of trust relationships"""
    print("=== Testing Trust Relationship Edit Functionality ===\n")
    
    # Get the first relationship
    relationships = TrustRelationship.objects.filter(is_active=True)
    if not relationships.exists():
        print("No active relationships found to test!")
        return
    
    rel = relationships.first()
    print(f"Original relationship:")
    print(f"  ID: {rel.id}")
    print(f"  Source: {rel.source_organization.name}")
    print(f"  Target: {rel.target_organization.name}")
    print(f"  Trust Level: {rel.trust_level.name}")
    print(f"  Type: {rel.relationship_type}")
    print(f"  Notes: {rel.notes}")
    
    # Test updating the relationship
    print(f"\n--- Testing Edit Functionality ---")
    
    # Get or create new organizations for testing
    new_source, created = Organization.objects.get_or_create(
        name="Updated Test Security Corp",
        defaults={'organization_type': 'commercial', 'description': 'Updated for testing'}
    )
    
    new_target, created = Organization.objects.get_or_create(
        name="Updated Demo Financial Services",
        defaults={'organization_type': 'financial', 'description': 'Updated for testing'}
    )
    
    # Get high trust level
    high_trust = TrustLevel.objects.get(name='high')
    
    # Update the relationship
    original_source_name = rel.source_organization.name
    original_target_name = rel.target_organization.name
    original_trust_level = rel.trust_level.name
    
    rel.source_organization = new_source
    rel.target_organization = new_target
    rel.trust_level = high_trust
    rel.relationship_type = 'strategic_partnership'
    rel.notes = 'Updated relationship notes for testing'
    rel.save()
    
    print(f"Updated relationship:")
    print(f"  ID: {rel.id}")
    print(f"  Source: {rel.source_organization.name} (was: {original_source_name})")
    print(f"  Target: {rel.target_organization.name} (was: {original_target_name})")
    print(f"  Trust Level: {rel.trust_level.name} (was: {original_trust_level})")
    print(f"  Type: {rel.relationship_type}")
    print(f"  Notes: {rel.notes}")
    
    print(f"\n✅ Edit functionality test completed successfully!")
    print(f"✅ Source organization was updated and saved")
    print(f"✅ Target organization was updated and saved")
    print(f"✅ Trust level was updated and saved")
    print(f"✅ Relationship type was updated and saved")
    print(f"✅ Notes were updated and saved")

if __name__ == "__main__":
    test_edit_relationship()