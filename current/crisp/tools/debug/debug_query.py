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
import django.db.models as models
import uuid

print("=== QUERY DEBUG ===")

# Create test data
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

org_1 = str(uuid.uuid4())
org_2 = str(uuid.uuid4())

# Create and activate relationship
rel = TrustService.create_trust_relationship(
    source_org=org_1,
    target_org=org_2,
    trust_level_name=trust_level_low.name,
    created_by='test_user'
)

rel.approved_by_source = True
rel.approved_by_target = True
rel.save()
activated = rel.activate()

print(f"Created relationship: {rel.id}")
print(f"Status: {rel.status}, Active: {rel.is_active}, Activated: {activated}")
print(f"Approved source: {rel.approved_by_source}, target: {rel.approved_by_target}")
print(f"Trust level: {rel.trust_level.name} (value: {rel.trust_level.numerical_value})")

# Test the exact query used in get_sharing_organizations
min_trust_value = 25
print(f"\nTesting query with min_trust_value={min_trust_value}")

# Exact query from get_sharing_organizations
relationships = TrustRelationship.objects.filter(
    source_organization=org_1,
    is_active=True,
    status='active',
    trust_level__numerical_value__gte=min_trust_value
).select_related('trust_level')

print(f"Query found {relationships.count()} relationships")
for rel in relationships:
    print(f"  - {rel.id}: to {rel.target_organization}, trust_level={rel.trust_level.name}")

# Test is_effective property
rel_fresh = TrustRelationship.objects.get(id=rel.id)
print(f"\nFresh relationship from DB:")
print(f"  Status: {rel_fresh.status}")
print(f"  Is active: {rel_fresh.is_active}")
print(f"  Approved source: {rel_fresh.approved_by_source}")
print(f"  Approved target: {rel_fresh.approved_by_target}")
print(f"  Is fully approved: {rel_fresh.is_fully_approved}")
try:
    print(f"  Is effective: {rel_fresh.is_effective}")
except Exception as e:
    print(f"  Is effective error: {e}")

# Test get_sharing_organizations
print(f"\nTesting get_sharing_organizations...")
sharing_orgs = TrustService.get_sharing_organizations(
    source_org=org_1,
    min_trust_level='low'
)
print(f"Result: {len(sharing_orgs)} organizations")
for org_id, trust_level, relationship in sharing_orgs:
    print(f"  - {org_id}: {trust_level.name}")