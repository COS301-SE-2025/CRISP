#!/usr/bin/env python3
import os
import sys
import django
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

# Test organization creation
print("\nStep 1: Creating test organization...")
admin_data = {
    'username': 'testadmin',
    'email': 'admin@testorg.edu',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'Admin'
}

try:
    test_org = CRISPIntegrationService.create_organization_with_trust_setup(
        name='Test Integration University',
        domain='testintegration.edu',
        contact_email='contact@testintegration.edu',
        admin_user_data=admin_data,
        institution_type='university',
        default_trust_level='public'
    )
    print(f"  SUCCESS: Created organization: {test_org.name}")
    
    # Verify admin user
    admin_user = User.objects.get(email='admin@testorg.edu')
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
        'username': 'testadmin2',
        'email': 'admin@testorg2.edu',
        'password': 'testpass123',
        'first_name': 'Test2',
        'last_name': 'Admin'
    }
    
    test_org_2 = CRISPIntegrationService.create_organization_with_trust_setup(
        name='Test Partner University',
        domain='testpartner.edu',
        contact_email='contact@testpartner.edu',
        admin_user_data=admin_data_2,
        institution_type='university',
        default_trust_level='trusted'
    )
    print(f"  SUCCESS: Created second organization: {test_org_2.name}")
    
    admin_user_2 = User.objects.get(email='admin@testorg2.edu')
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
    
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
