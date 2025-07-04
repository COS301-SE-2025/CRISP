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

print("=== DEBUG: Trust Level Test ===")

# Check trust levels
print("\nAll trust levels:")
for tl in TrustLevel.objects.all():
    print(f"  - {tl.name}: active={tl.is_active}, value={tl.numerical_value}")

print("\nActive trust levels:")
active_levels = TrustLevel.objects.filter(is_active=True)
for tl in active_levels:
    print(f"  - {tl.name}: active={tl.is_active}, value={tl.numerical_value}")

# Test getting Trusted Partners
print("\nTesting 'Trusted Partners' lookup:")
try:
    trusted_partners = TrustLevel.objects.get(name='Trusted Partners', is_active=True)
    print(f"  Found: {trusted_partners.name} (active={trusted_partners.is_active})")
except TrustLevel.DoesNotExist:
    print("  NOT FOUND")

# Test organization creation
print("\nTesting organization creation:")
try:
    orgs = Organization.objects.all()
    print(f"  Total organizations: {orgs.count()}")
    
    for org in orgs:
        print(f"  - {org.name} (ID: {org.id})")
except Exception as e:
    print(f"  Error: {e}")
