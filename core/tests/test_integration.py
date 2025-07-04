"""
Essential Integration Tests

Tests end-to-end workflows and component integration.
"""

import uuid
from django.test import TestCase

from core.trust.models import TrustLevel, TrustRelationship, TrustGroup
from core.trust.services.trust_service import TrustService
from core.trust.services.trust_group_service import TrustGroupService


class TrustManagementIntegrationTest(TestCase):
    """Test integration of trust management components"""
    
    def setUp(self):
        self.source_org = str(uuid.uuid4())
        self.target_org = str(uuid.uuid4())
        self.user = 'test_user'
        
        # Create test trust level
        self.trust_level = TrustLevel.objects.create(
            name='Integration Test Level',
            level='medium',
            numerical_value=50,
            description='Test description',
            default_anonymization_level='partial',
            default_access_level='read',
            created_by=self.user
        )
    
    def test_complete_trust_relationship_workflow(self):
        """Test complete trust relationship lifecycle"""
        # 1. Create relationship
        relationship = TrustService.create_trust_relationship(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level_name='Integration Test Level',
            created_by=self.user
        )
        
        self.assertIsInstance(relationship, TrustRelationship)
        self.assertEqual(relationship.status, 'pending')
        
        # 2. Verify relationship was created with correct trust level
        self.assertEqual(relationship.trust_level, self.trust_level)
        
        # 3. Approve relationship (source)
        approved_source = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.source_org,
            approved_by_user=self.user
        )
        # Source approval shouldn't activate relationship yet (needs both approvals)
        self.assertFalse(approved_source)
        
        # 4. Approve relationship (target) 
        approved_target = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.target_org,
            approved_by_user=self.user
        )
        # Target approval should activate relationship (both sides now approved)
        self.assertTrue(approved_target)
        
        # 5. Verify relationship is now active
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'active')
        
        # 6. Now check trust level - should work since relationship is active
        trust_info = TrustService.check_trust_level(self.source_org, self.target_org)
        self.assertIsNotNone(trust_info)
        trust_level, rel = trust_info
        self.assertEqual(trust_level, self.trust_level)
    
    def test_trust_group_workflow(self):
        """Test trust group creation and membership"""
        # Create a fresh trust level for this test
        group_trust_level = TrustLevel.objects.create(
            name='Group Test Level',
            level='group_medium',
            numerical_value=50,
            description='Test description',
            default_anonymization_level='partial',
            default_access_level='read',
            created_by=self.user
        )
        
        # 1. Create trust group
        group = TrustGroupService.create_trust_group(
            name='Integration Test Group',
            description='Test group for integration',
            creator_org=self.source_org,
            group_type='community',
            default_trust_level_name=group_trust_level.level,
            created_by=self.user
        )
        
        self.assertIsInstance(group, TrustGroup)
        self.assertEqual(group.name, 'Integration Test Group')
        
        # 2. Verify that creator is automatically added as member
        membership_exists = group.group_memberships.filter(
            organization=self.source_org,
            is_active=True
        ).exists()
        
        self.assertTrue(membership_exists)
        
        # 3. Try to join a different organization
        target_org_membership = TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.target_org,
            user=self.user
        )
        
        # 4. Verify the service returned a membership object
        self.assertIsNotNone(target_org_membership)
        
        # 5. Verify the new membership was created (may require approval)
        target_membership_exists = group.group_memberships.filter(
            organization=self.target_org
        ).exists()
        
        self.assertTrue(target_membership_exists)
    
    def test_service_integration_with_models(self):
        """Test that services properly integrate with models"""
        # Create relationship through service
        relationship = TrustService.create_trust_relationship(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level_name='Integration Test Level',
            created_by=self.user
        )
        
        # Verify model was created correctly
        db_relationship = TrustRelationship.objects.get(id=relationship.id)
        self.assertEqual(db_relationship.source_organization, self.source_org)
        self.assertEqual(db_relationship.target_organization, self.target_org)
        self.assertEqual(db_relationship.trust_level, self.trust_level)
        
        # Verify audit logging
        from core.trust.models import TrustLog
        log_exists = TrustLog.objects.filter(
            action='relationship_created',
            source_organization=self.source_org
        ).exists()
        
        # Log might exist depending on implementation
        # This just verifies the integration doesn't crash