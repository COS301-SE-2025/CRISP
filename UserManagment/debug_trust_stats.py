#!/usr/bin/env python3
"""
Debug script to test trust statistics functionality
"""
import os
import sys
import django

# Add the project path
sys.path.append('/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/UserManagment')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.test_settings')
django.setup()

from UserManagement.models import Organization
from trust_management_app.core.models.models import TrustLevel, TrustRelationship
from trust_management_app.core.services.trust_service import TrustService
from crisp_project.services import CRISPIntegrationService

def debug_trust_stats():
    """Debug trust statistics"""
    print("🔍 Debugging Trust Statistics")
    print("=" * 50)
    
    # Create test organizations
    org_a = Organization.objects.create(
        name='Debug Org A',
        description='Debug organization A',
        domain='debug-a.com'
    )
    
    org_b = Organization.objects.create(
        name='Debug Org B', 
        description='Debug organization B',
        domain='debug-b.com'
    )
    
    org_external = Organization.objects.create(
        name='Debug External',
        description='Debug external organization',
        domain='debug-external.com'
    )
    
    # Create trust levels
    medium_trust = TrustLevel.objects.create(
        name='Debug Medium Trust',
        level='medium',
        numerical_value=50,
        description='Medium trust level for debug',
        default_anonymization_level='minimal',
        default_access_level='subscribe'
    )
    
    high_trust = TrustLevel.objects.create(
        name='Debug High Trust',
        level='high',
        numerical_value=75,
        description='High trust level for debug',
        default_anonymization_level='minimal',
        default_access_level='contribute'
    )
    
    # Create trust relationships
    print("Creating trust relationships...")
    
    # A->B relationship
    rel_ab = TrustRelationship.objects.create(
        source_organization=org_a,
        target_organization=org_b,
        relationship_type='bilateral',
        trust_level=medium_trust,
        status='active',
        approved_by_source=True,
        approved_by_target=True,
        is_bilateral=True
    )
    print(f"Created A->B: {rel_ab.id}, is_active={rel_ab.is_active}")
    
    # B->A relationship  
    rel_ba = TrustRelationship.objects.create(
        source_organization=org_b,
        target_organization=org_a,
        relationship_type='bilateral',
        trust_level=high_trust,
        status='active',
        approved_by_source=True,
        approved_by_target=True,
        is_bilateral=True
    )
    print(f"Created B->A: {rel_ba.id}, is_active={rel_ba.is_active}")
    
    # A->External relationship
    rel_ae = TrustRelationship.objects.create(
        source_organization=org_a,
        target_organization=org_external,
        relationship_type='bilateral',
        trust_level=medium_trust,
        status='active',
        approved_by_source=True,
        approved_by_target=True
    )
    print(f"Created A->External: {rel_ae.id}, is_active={rel_ae.is_active}")
    
    # Check what exists in the database
    print("\nDatabase queries:")
    all_rels = TrustRelationship.objects.all()
    print(f"Total relationships in DB: {all_rels.count()}")
    
    initiated_by_a = TrustRelationship.objects.filter(
        source_organization=org_a,
        is_active=True
    )
    print(f"Relationships initiated by A (is_active=True): {initiated_by_a.count()}")
    for rel in initiated_by_a:
        print(f"  - {rel.source_organization.name} -> {rel.target_organization.name} (status: {rel.status}, is_active: {rel.is_active})")
    
    received_by_a = TrustRelationship.objects.filter(
        target_organization=org_a,
        is_active=True
    )
    print(f"Relationships received by A (is_active=True): {received_by_a.count()}")
    for rel in received_by_a:
        print(f"  - {rel.source_organization.name} -> {rel.target_organization.name} (status: {rel.status}, is_active: {rel.is_active})")
    
    # Test TrustService method
    print("\nTesting TrustService.get_organization_trust_summary:")
    summary = TrustService.get_organization_trust_summary(org_a)
    print(f"Summary: {summary}")
    
    # Test CRISPIntegrationService method
    print("\nTesting CRISPIntegrationService.get_trust_statistics:")
    stats = CRISPIntegrationService.get_trust_statistics(org_a)
    print(f"Stats: {stats}")
    
    print("\n" + "=" * 50)
    print("Debug complete!")

if __name__ == '__main__':
    debug_trust_stats()
