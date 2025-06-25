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
from TrustManagement.tests.test_trust_services import TrustServiceTest

print("=== TRUST LEVEL DEBUG ===")

# Test the test setup itself
test_case = TrustServiceTest()
test_case.setUp()
print(f"Test trust levels: low={test_case.trust_level_low.name}, high={test_case.trust_level_high.name}")

# Check if trust levels exist  
levels = TrustLevel.objects.all()
print('Available trust levels:')
for level in levels:
    print(f'  - name: "{level.name}", level: "{level.level}", value: {level.numerical_value}, active: {level.is_active}')

# Try to find 'low' trust level
low_trust = TrustLevel.objects.filter(
    models.Q(name='low') | models.Q(level='low'),
    is_active=True
).first()
print(f'\nFound low trust level: {low_trust}')

if low_trust:
    print(f'Low trust level details: name="{low_trust.name}", level="{low_trust.level}", value={low_trust.numerical_value}')

print("\n=== RELATIONSHIP DEBUG ===")

# Create test trust levels if they don't exist
if not TrustLevel.objects.filter(level='low').exists():
    print("Creating low trust level...")
    TrustLevel.objects.create(
        name='Low Trust',
        level='low',
        description='Low trust level',
        numerical_value=25,
        default_anonymization_level='partial',
        default_access_level='read',
        created_by='debug_user'
    )

if not TrustLevel.objects.filter(level='high').exists():
    print("Creating high trust level...")
    TrustLevel.objects.create(
        name='High Trust',
        level='high',
        description='High trust level',
        numerical_value=75,
        default_anonymization_level='minimal',
        default_access_level='contribute',
        created_by='debug_user'
    )

# Test creating relationships
org1 = str(uuid.uuid4())
org2 = str(uuid.uuid4())
org3 = str(uuid.uuid4())

print(f"Creating relationships for orgs: {org1}, {org2}, {org3}")

try:
    rel1 = TrustService.create_trust_relationship(
        source_org=org1,
        target_org=org2,
        trust_level_name='High Trust',  # This name exists
        created_by='debug_user'
    )
    print(f"Created rel1: {rel1.id}, status: {rel1.status}")
    
    rel2 = TrustService.create_trust_relationship(
        source_org=org1,
        target_org=org3,
        trust_level_name='Basic Trust',  # Use the correct name from database
        created_by='debug_user'
    )
    print(f"Created rel2: {rel2.id}, status: {rel2.status}")
    
    # Activate relationships
    for rel in [rel1, rel2]:
        rel.approved_by_source = True
        rel.approved_by_target = True
        rel.save()
        activated = rel.activate()
        print(f"Relationship {rel.id}: approved_source={rel.approved_by_source}, approved_target={rel.approved_by_target}, is_fully_approved={rel.is_fully_approved}, activated={activated}, status={rel.status}")
    
    # Test get_sharing_organizations
    print(f"\nTesting get_sharing_organizations for org {org1} with min_trust_level='low'")
    sharing_orgs = TrustService.get_sharing_organizations(
        source_org=org1,
        min_trust_level='low'
    )
    
    print(f"Found {len(sharing_orgs)} sharing organizations:")
    for org_id, trust_level, relationship in sharing_orgs:
        print(f"  - org: {org_id}, trust_level: {trust_level.name}, relationship: {relationship.id}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()