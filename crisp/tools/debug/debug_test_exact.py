#!/usr/bin/env python3

import os
import sys
import django

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from TrustManagement.models import TrustLevel, TrustRelationship
from TrustManagement.services.trust_service import TrustService
import uuid

print("=== EXACT TEST SCENARIO ===")

# Setup like the test
trust_level_low, _ = TrustLevel.objects.get_or_create(
    level='low',
    defaults={
        'name': 'Basic Trust',
        'description': 'Low trust level',
        'numerical_value': 25,
        'default_anonymization_level': 'partial',
        'default_access_level': 'read',
        'created_by': 'test_user'
    }
)

trust_level_high, _ = TrustLevel.objects.get_or_create(
    level='high',
    defaults={
        'name': 'High Trust',
        'description': 'High trust level',
        'numerical_value': 75,
        'default_anonymization_level': 'minimal',
        'default_access_level': 'contribute',
        'created_by': 'test_user'
    }
)

org_1 = str(uuid.uuid4())
org_2 = str(uuid.uuid4())
org_3 = str(uuid.uuid4())

print(f"Trust levels: low={trust_level_low.name}, high={trust_level_high.name}")
print(f"Organizations: {org_1}, {org_2}, {org_3}")

try:
    # Create relationships exactly like the test
    print("Creating relationships...")
    rel1 = TrustService.create_trust_relationship(
        source_org=org_1,
        target_org=org_2,
        trust_level_name=trust_level_high.name,
        created_by='test_user'
    )
    
    rel2 = TrustService.create_trust_relationship(
        source_org=org_1,
        target_org=org_3,
        trust_level_name=trust_level_low.name,
        created_by='test_user'
    )
    
    print(f"Created relationships: {rel1.id}, {rel2.id}")
    
    # Activate relationships exactly like the test
    print("Activating relationships...")
    for rel in [rel1, rel2]:
        print(f"Before activation: rel {rel.id}: status={rel.status}, approved_source={rel.approved_by_source}, approved_target={rel.approved_by_target}")
        rel.approved_by_source = True
        rel.approved_by_target = True
        activated = rel.activate()
        print(f"After activation: rel {rel.id}: status={rel.status}, activated={activated}, is_effective={rel.is_effective if hasattr(rel, 'is_effective') else 'N/A'}")
    
    # Get sharing organizations exactly like the test
    print("Getting sharing organizations...")
    sharing_orgs = TrustService.get_sharing_organizations(
        source_org=org_1,
        min_trust_level='low'
    )
    
    print(f"Found {len(sharing_orgs)} sharing organizations (expected: 2)")
    for org_id, trust_level, relationship in sharing_orgs:
        print(f"  - org: {org_id}, trust_level: {trust_level.name}, relationship: {relationship.id}")
    
    # Debug the relationships in the database
    print("\nDirect database query:")
    db_relationships = TrustRelationship.objects.filter(source_organization=org_1)
    print(f"Found {db_relationships.count()} relationships from {org_1}")
    for rel in db_relationships:
        print(f"  - to {rel.target_organization}: status={rel.status}, active={rel.is_active}, trust_level={rel.trust_level.name}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()