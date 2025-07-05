#!/usr/bin/env python3
import os
import sys
import django
import time
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.settings.integrated')
django.setup()

from apps.trust_management.models import TrustLevel
from apps.core.services import CRISPIntegrationService
from apps.user_management.models import Organization
from django.contrib.auth import get_user_model

print("=== Manual Integration Test ===")

User = get_user_model()

# Generate unique identifiers for this test run
timestamp = str(int(time.time()))
print(f"Test run timestamp: {timestamp}")

# Clean up existing test data
print("\nCleaning up existing test data...")
try:
    # Delete existing test organizations and related data
    test_orgs = Organization.objects.filter(name__icontains='Test')
    if test_orgs.exists():
        print(f"  Deleting {test_orgs.count()} existing test organizations...")
        test_orgs.delete()
    
    # Delete existing test users
    test_users = User.objects.filter(email__icontains='testorg')
    if test_users.exists():
        print(f"  Deleting {test_users.count()} existing test users...")
        test_users.delete()
    
    print("  Cleanup completed successfully")
except Exception as e:
    print(f"  Cleanup warning: {e}")
    # Continue with test even if cleanup fails

# Test organization creation
print("\nStep 1: Creating test organization...")
admin_data = {
    'username': f'testadmin_{timestamp}',
    'email': f'admin_{timestamp}@testorg.edu',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'Admin'
}

try:
    test_org = CRISPIntegrationService.create_organization_with_trust_setup(
        name=f'Test Integration University {timestamp}',
        domain=f'testintegration{timestamp}.edu',
        contact_email=f'contact_{timestamp}@testintegration.edu',
        admin_user_data=admin_data,
        institution_type='university',
        default_trust_level='public'
    )
    print(f"  SUCCESS: Created organization: {test_org.name}")
    
    # Verify admin user
    admin_user = User.objects.get(email=f'admin_{timestamp}@testorg.edu')
    print(f"  SUCCESS: Created admin user: {admin_user.email}")
    
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test trust level lookup
print("\nStep 2: Testing trust level lookup...")
try:
    # Check trust levels
    print("  All trust levels:")
    for tl in TrustLevel.objects.all():
        print(f"    - {tl.name}: active={tl.is_active}, value={tl.numerical_value}")
    
    # Try to get trusted partners
    trusted_partners = TrustLevel.objects.get(name='Trusted Partners', is_active=True)
    print(f"  SUCCESS: Found Trusted Partners: {trusted_partners.name}")
    
    # Test creating second organization
    print("\nStep 3: Creating second organization...")
    admin_data_2 = {
        'username': f'testadmin2_{timestamp}',
        'email': f'admin2_{timestamp}@testorg2.edu',
        'password': 'testpass123',
        'first_name': 'Test2',
        'last_name': 'Admin'
    }
    
    test_org_2 = CRISPIntegrationService.create_organization_with_trust_setup(
        name=f'Test Partner University {timestamp}',
        domain=f'testpartner{timestamp}.edu',
        contact_email=f'contact2_{timestamp}@testpartner.edu',
        admin_user_data=admin_data_2,
        institution_type='university',
        default_trust_level='trusted'
    )
    print(f"  SUCCESS: Created second organization: {test_org_2.name}")
    
    admin_user_2 = User.objects.get(email=f'admin2_{timestamp}@testorg2.edu')
    print(f"  SUCCESS: Created second admin user: {admin_user_2.email}")
    
    # Test trust relationship creation
    print("\nStep 4: Creating trust relationship...")
    
    relationship = CRISPIntegrationService.create_trust_relationship(
        source_org=test_org,
        target_org=test_org_2,
        trust_level_name='Trusted Partners',
        created_by_user=admin_user
    )
    
    print(f"  SUCCESS: Created trust relationship: {relationship.id}")
    print(f"  Trust level: {relationship.trust_level.name}")
    
    # Additional verification
    print("\nStep 5: Integration verification...")
    print(f"  Organization 1: {test_org.name} (ID: {test_org.id})")
    print(f"  Organization 2: {test_org_2.name} (ID: {test_org_2.id})")
    print(f"  Trust relationship: {relationship.source_organization} -> {relationship.target_organization}")
    print(f"  Trust level: {relationship.trust_level.name} (value: {relationship.trust_level.numerical_value})")
    print(f"  Status: {relationship.status}")
    
    print("\n  SUCCESS: All integration tests completed successfully!")
    print("  The UserManagement and TrustManagement systems are properly integrated.")
    
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
