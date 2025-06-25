#!/usr/bin/env python3
import os
import sys
sys.path.append('/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/UserManagment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.test_settings')

import django
django.setup()

from UserManagement.models import Organization
from trust_management_app.core.models.models import TrustLevel, TrustRelationship
from trust_management_app.core.services.trust_service import TrustService

print("Testing trust statistics...")

# Create simple test data
org = Organization.objects.create(name='Test Org', description='Test', domain='test.com')
trust_level = TrustLevel.objects.create(name='Test Trust', level='medium', numerical_value=50, default_anonymization_level='none', default_access_level='read')

# Create a relationship
rel = TrustRelationship.objects.create(
    source_organization=org,
    target_organization=org,  # self-reference for simplicity
    trust_level=trust_level,
    status='active'
)

print(f"Created relationship: {rel.id}")
print(f"is_active: {rel.is_active}")

# Test the count
count = TrustRelationship.objects.filter(source_organization=org, is_active=True).count()
print(f"Count for source_organization: {count}")

# Test the service method
summary = TrustService.get_organization_trust_summary(org)
print(f"Summary: {summary}")
