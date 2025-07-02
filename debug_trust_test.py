#!/usr/bin/env python3

import os
import sys
import django
import uuid
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')

# Setup Django
django.setup()

from core.trust.models import TrustLevel, TrustRelationship
from core.trust.patterns.strategy.access_control_strategies import TrustBasedAccessControl, AccessControlContext

def debug_trust_test():
    print("=== Debugging Trust Test ===")
    
    # Create test data similar to the test
    strategy = TrustBasedAccessControl()
    
    # Configure strategy with action-specific requirements
    strategy.configure({
        'required_actions': {
            'read': 30,
            'write': 60,
            'admin': 90
        }
    })
    
    print(f"Strategy config: {strategy.config}")
    
    # Create organizations
    org_1 = str(uuid.uuid4())
    org_2 = str(uuid.uuid4())
    
    print(f"Org 1: {org_1}")
    print(f"Org 2: {org_2}")
    
    # Create trust levels
    high_trust_level = TrustLevel.objects.create(
        name='High Trust Strategy Test Level',
        level='high',
        description='High trust level for strategy testing',
        numerical_value=75,
        default_anonymization_level='minimal',
        default_access_level='contribute',
        created_by='test_user'
    )
    
    low_trust_level = TrustLevel.objects.create(
        name='Low Trust Strategy Test',
        level='low',
        description='Low trust level',
        numerical_value=20,
        default_anonymization_level='full',
        default_access_level='read',
        created_by='test_user'
    )
    
    print(f"High trust level: {high_trust_level.numerical_value}")
    print(f"Low trust level: {low_trust_level.numerical_value}")
    
    # Create relationship with low trust
    relationship = TrustRelationship.objects.create(
        source_organization=org_1,
        target_organization=org_2,
        trust_level=low_trust_level,
        relationship_type='bilateral',
        status='active',
        created_by='test_user',
        last_modified_by='test_user'
    )
    
    print(f"Created relationship: {relationship}")
    print(f"Relationship trust level: {relationship.trust_level.numerical_value}")
    print(f"Relationship status: {relationship.status}")
    
    # Test with write action requiring higher trust
    write_context = AccessControlContext(
        requesting_organization=org_1,
        target_organization=org_2,
        resource_type='indicator',
        action='write',
        user='test_user'
    )
    
    print(f"Context requesting_organization: {write_context.requesting_organization}")
    print(f"Context target_organization: {write_context.target_organization}")
    print(f"Context action: {getattr(write_context, 'action', 'NONE')}")
    
    # Query to see what relationships exist
    all_relationships = TrustRelationship.objects.filter(
        source_organization=write_context.requesting_organization,
        target_organization=write_context.target_organization,
        status='active'
    )
    
    print(f"Found relationships: {list(all_relationships)}")
    for rel in all_relationships:
        print(f"  - Trust level: {rel.trust_level.numerical_value}")
    
    # Evaluate access
    decision = strategy.evaluate(write_context)
    
    print(f"Decision allowed: {decision.allowed}")
    print(f"Decision reason: {decision.reason}")
    
    # Expected: False (trust level 20 < required 60)
    print(f"Expected: False (trust level 20 < required 60 for write)")
    print(f"Actual: {decision.allowed}")

if __name__ == "__main__":
    debug_trust_test()