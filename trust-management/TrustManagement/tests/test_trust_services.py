import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from ..models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership, TrustLog
)
from ..services.trust_service import TrustService
from ..services.trust_group_service import TrustGroupService


class TrustServiceTest(TestCase):
    """Test cases for TrustService."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use existing trust levels or create if they don't exist
        self.trust_level_low, _ = TrustLevel.objects.get_or_create(
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
        
        self.trust_level_high, _ = TrustLevel.objects.get_or_create(
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
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.org_3 = str(uuid.uuid4())
    
    def test_create_trust_relationship_success(self):
        """Test successful trust relationship creation."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            relationship_type='bilateral',
            created_by='test_user',
            notes='Test relationship'
        )
        
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.source_organization, self.org_1)
        self.assertEqual(relationship.target_organization, self.org_2)
        self.assertEqual(relationship.trust_level, self.trust_level_low)
        self.assertEqual(relationship.relationship_type, 'bilateral')
        self.assertEqual(relationship.created_by, 'test_user')
        self.assertEqual(relationship.notes, 'Test relationship')
    
    def test_create_trust_relationship_same_orgs(self):
        """Test creating relationship with same source and target."""
        with self.assertRaises(ValidationError) as context:
            TrustService.create_trust_relationship(
                source_org=self.org_1,
                target_org=self.org_1,  # Same as source
                trust_level_name=self.trust_level_low.name,
                created_by='test_user'
            )
        
        self.assertIn("cannot be the same", str(context.exception))
    
    def test_create_trust_relationship_invalid_trust_level(self):
        """Test creating relationship with invalid trust level."""
        with self.assertRaises(ValidationError) as context:
            TrustService.create_trust_relationship(
                source_org=self.org_1,
                target_org=self.org_2,
                trust_level_name='Nonexistent Trust Level',
                created_by='test_user'
            )
        
        self.assertIn("not found or inactive", str(context.exception))
    
    def test_create_trust_relationship_duplicate(self):
        """Test creating duplicate relationship."""
        # Create first relationship
        TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            created_by='test_user'
        )
        
        # Try to create duplicate
        with self.assertRaises(ValidationError) as context:
            TrustService.create_trust_relationship(
                source_org=self.org_1,
                target_org=self.org_2,
                trust_level_name=self.trust_level_high.name,
                created_by='test_user'
            )
        
        self.assertIn("already exists", str(context.exception))
    
    def test_approve_trust_relationship_source(self):
        """Test approving relationship from source organization."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            created_by='test_user'
        )
        
        # Approve from source
        activated = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.org_1,
            approved_by_user='test_user'
        )
        
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)
        self.assertFalse(relationship.approved_by_target)
        self.assertFalse(activated)  # Not fully approved yet
    
    def test_approve_trust_relationship_both_sides(self):
        """Test approving relationship from both organizations."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            created_by='test_user'
        )
        
        # Approve from source
        TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.org_1,
            approved_by_user='test_user'
        )
        
        # Approve from target
        activated = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.org_2,
            approved_by_user='test_user'
        )
        
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)
        self.assertTrue(relationship.approved_by_target)
        self.assertTrue(activated)  # Now fully approved and activated
        self.assertEqual(relationship.status, 'active')
    
    def test_approve_trust_relationship_community(self):
        """Test approving community relationship."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            relationship_type='community',
            created_by='test_user'
        )
        
        # Community relationships are auto-approved by source
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)
        self.assertFalse(relationship.approved_by_target)
    
    def test_revoke_trust_relationship(self):
        """Test revoking trust relationship."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            created_by='test_user'
        )
        
        # Activate relationship first
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.activate()
        
        # Revoke relationship
        result = TrustService.revoke_trust_relationship(
            relationship_id=str(relationship.id),
            revoking_org=self.org_1,
            revoked_by_user='test_user',
            reason='Test revocation'
        )
        
        self.assertTrue(result)
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'revoked')
        self.assertFalse(relationship.is_active)
        self.assertIsNotNone(relationship.revoked_at)
    
    def test_get_trust_relationships_for_organization(self):
        """Test getting trust relationships for organization."""
        # Create relationships
        rel1 = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            created_by='test_user'
        )
        
        rel2 = TrustService.create_trust_relationship(
            source_org=self.org_3,
            target_org=self.org_1,
            trust_level_name=self.trust_level_high.name,
            created_by='test_user'
        )
        
        # Get relationships for org_1
        relationships = TrustService.get_trust_relationships_for_organization(self.org_1)
        
        # Should include both relationships (as source and target)
        self.assertEqual(len(relationships), 2)
        relationship_ids = {str(rel.id) for rel in relationships}
        self.assertIn(str(rel1.id), relationship_ids)
        self.assertIn(str(rel2.id), relationship_ids)
    
    def test_check_trust_level_direct(self):
        """Test checking trust level with direct relationship."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_high.name,
            created_by='test_user'
        )
        
        # Activate relationship
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.save()
        relationship.activate()
        
        # Check trust level
        trust_info = TrustService.check_trust_level(self.org_1, self.org_2)
        
        self.assertIsNotNone(trust_info)
        trust_level, rel = trust_info
        self.assertEqual(trust_level, self.trust_level_high)
        self.assertEqual(rel, relationship)
    
    def test_check_trust_level_bilateral_reverse(self):
        """Test checking trust level with bilateral reverse relationship."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_2,
            target_org=self.org_1,
            trust_level_name=self.trust_level_high.name,
            relationship_type='bilateral',
            created_by='test_user'
        )
        
        # Activate relationship
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.save()
        relationship.activate()
        
        # Check trust level in reverse direction
        trust_info = TrustService.check_trust_level(self.org_1, self.org_2)
        
        self.assertIsNotNone(trust_info)
        trust_level, rel = trust_info
        self.assertEqual(trust_level, self.trust_level_high)
        self.assertEqual(rel, relationship)
    
    def test_check_trust_level_no_relationship(self):
        """Test checking trust level with no relationship."""
        trust_info = TrustService.check_trust_level(self.org_1, self.org_2)
        self.assertIsNone(trust_info)
    
    def test_can_access_intelligence_own_org(self):
        """Test intelligence access for own organization."""
        can_access, reason, rel = TrustService.can_access_intelligence(
            requesting_org=self.org_1,
            intelligence_owner=self.org_1
        )
        
        self.assertTrue(can_access)
        self.assertEqual(reason, "Own organization")
        self.assertIsNone(rel)
    
    def test_can_access_intelligence_with_trust(self):
        """Test intelligence access with trust relationship."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_high.name,
            created_by='test_user'
        )
        
        # Activate relationship
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.save()
        relationship.activate()
        
        can_access, reason, rel = TrustService.can_access_intelligence(
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            required_access_level='read'
        )
        
        self.assertTrue(can_access)
        self.assertIn("Authorized via trust relationship", reason)
        self.assertEqual(rel, relationship)
    
    def test_can_access_intelligence_insufficient_access(self):
        """Test intelligence access with insufficient access level."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,  # Only provides 'read' access
            created_by='test_user'
        )
        
        # Activate relationship
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.save()
        relationship.activate()
        
        can_access, reason, rel = TrustService.can_access_intelligence(
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            required_access_level='contribute'  # Requires higher access
        )
        
        self.assertFalse(can_access)
        self.assertIn("Insufficient access level", reason)
        self.assertEqual(rel, relationship)
    
    def test_get_sharing_organizations(self):
        """Test getting organizations for sharing."""
        # Create relationships
        rel1 = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_high.name,
            created_by='test_user'
        )
        
        rel2 = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_3,
            trust_level_name=self.trust_level_low.name,
            created_by='test_user'
        )
        
        # Activate relationships
        for rel in [rel1, rel2]:
            rel.approved_by_source = True
            rel.approved_by_target = True
            rel.save()  # Must save before activate()
            rel.activate()
        
        # Get sharing organizations
        sharing_orgs = TrustService.get_sharing_organizations(
            source_org=self.org_1,
            min_trust_level='low'
        )
        
        self.assertEqual(len(sharing_orgs), 2)
        org_ids = {org_id for org_id, _, _ in sharing_orgs}
        self.assertIn(self.org_2, org_ids)
        self.assertIn(self.org_3, org_ids)
    
    def test_update_trust_level(self):
        """Test updating trust level of relationship."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name=self.trust_level_low.name,
            created_by='test_user'
        )
        
        # Update trust level
        result = TrustService.update_trust_level(
            relationship_id=str(relationship.id),
            new_trust_level_name='High Trust',
            updated_by='test_user',
            reason='Trust improvement'
        )
        
        self.assertTrue(result)
        relationship.refresh_from_db()
        self.assertEqual(relationship.trust_level, self.trust_level_high)
        self.assertIn('Trust improvement', relationship.notes)


class TrustGroupServiceTest(TestCase):
    """Test cases for TrustGroupService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Group Trust Level',
            level='medium',
            description='Trust level for groups',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.org_3 = str(uuid.uuid4())
    
    def test_create_trust_group(self):
        """Test trust group creation."""
        group = TrustGroupService.create_trust_group(
            name='Test Group',
            description='Test group description',
            creator_org=self.org_1,
            group_type='community',
            is_public=True,
            default_trust_level_name='Group Trust Level'
        )
        
        self.assertIsNotNone(group)
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.group_type, 'community')
        self.assertTrue(group.is_public)
        self.assertEqual(group.created_by, self.org_1)
        self.assertIn(self.org_1, group.administrators)
        
        # Check that creator is added as administrator member
        membership = TrustGroupMembership.objects.get(
            trust_group=group,
            organization=self.org_1
        )
        self.assertEqual(membership.membership_type, 'administrator')
    
    def test_join_trust_group(self):
        """Test joining trust group."""
        group = TrustGroupService.create_trust_group(
            name='Join Test Group',
            description='Test group for joining',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        # Join as member
        membership = TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_2,
            membership_type='member',
            invited_by=self.org_1,
            user='test_user'
        )
        
        self.assertIsNotNone(membership)
        self.assertEqual(membership.organization, self.org_2)
        self.assertEqual(membership.membership_type, 'member')
        self.assertEqual(membership.invited_by, self.org_1)
        self.assertTrue(membership.is_active)
    
    def test_join_trust_group_duplicate(self):
        """Test joining trust group when already a member."""
        group = TrustGroupService.create_trust_group(
            name='Duplicate Test Group',
            description='Test group for duplicate membership',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        # Join first time
        TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_2,
            user='test_user'
        )
        
        # Try to join again
        with self.assertRaises(ValidationError) as context:
            TrustGroupService.join_trust_group(
                group_id=str(group.id),
                organization=self.org_2,
                user='test_user'
            )
        
        self.assertIn("already a member", str(context.exception))
    
    def test_leave_trust_group(self):
        """Test leaving trust group."""
        group = TrustGroupService.create_trust_group(
            name='Leave Test Group',
            description='Test group for leaving',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        # Join first
        TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_2,
            user='test_user'
        )
        
        # Leave group
        result = TrustGroupService.leave_trust_group(
            group_id=str(group.id),
            organization=self.org_2,
            user='test_user',
            reason='Test leaving'
        )
        
        self.assertTrue(result)
        
        # Check membership is deactivated
        membership = TrustGroupMembership.objects.get(
            trust_group=group,
            organization=self.org_2
        )
        self.assertFalse(membership.is_active)
        self.assertIsNotNone(membership.left_at)
    
    def test_leave_trust_group_administrator(self):
        """Test administrator leaving trust group."""
        group = TrustGroupService.create_trust_group(
            name='Admin Leave Test Group',
            description='Test group for admin leaving',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        # Add another administrator
        TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_2,
            membership_type='administrator'
        )
        
        # Promote to administrator
        TrustGroupService.promote_member(
            group_id=str(group.id),
            organization=self.org_2,
            promoting_org=self.org_1,
            new_membership_type='administrator'
        )
        
        # Administrator leaves
        TrustGroupService.leave_trust_group(
            group_id=str(group.id),
            organization=self.org_2,
            user='test_user'
        )
        
        # Check that org_2 is removed from administrators
        group.refresh_from_db()
        self.assertNotIn(self.org_2, group.administrators)
    
    def test_get_trust_groups_for_organization(self):
        """Test getting trust groups for organization."""
        group1 = TrustGroupService.create_trust_group(
            name='Group 1',
            description='First group',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        group2 = TrustGroupService.create_trust_group(
            name='Group 2',
            description='Second group',
            creator_org=self.org_2,
            default_trust_level_name='Group Trust Level'
        )
        
        # Join group2
        TrustGroupService.join_trust_group(
            group_id=str(group2.id),
            organization=self.org_1
        )
        
        # Get groups for org_1
        groups = TrustGroupService.get_trust_groups_for_organization(self.org_1)
        
        self.assertEqual(len(groups), 2)
        group_ids = {str(group.id) for group in groups}
        self.assertIn(str(group1.id), group_ids)
        self.assertIn(str(group2.id), group_ids)
    
    def test_get_public_trust_groups(self):
        """Test getting public trust groups."""
        # Create public group
        public_group = TrustGroupService.create_trust_group(
            name='Public Group',
            description='Public group',
            creator_org=self.org_1,
            is_public=True,
            default_trust_level_name='Group Trust Level'
        )
        
        # Create private group
        TrustGroupService.create_trust_group(
            name='Private Group',
            description='Private group',
            creator_org=self.org_1,
            is_public=False,
            default_trust_level_name='Group Trust Level'
        )
        
        # Get public groups
        public_groups = TrustGroupService.get_public_trust_groups()
        
        self.assertEqual(len(public_groups), 1)
        self.assertEqual(public_groups[0], public_group)
    
    def test_can_administer_group(self):
        """Test group administration check."""
        group = TrustGroupService.create_trust_group(
            name='Admin Test Group',
            description='Test group for admin check',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        # Creator can administer
        self.assertTrue(TrustGroupService.can_administer_group(str(group.id), self.org_1))
        
        # Non-member cannot administer
        self.assertFalse(TrustGroupService.can_administer_group(str(group.id), self.org_2))
    
    def test_promote_member(self):
        """Test promoting group member."""
        group = TrustGroupService.create_trust_group(
            name='Promotion Test Group',
            description='Test group for promotion',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        # Join as member
        TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_2,
            membership_type='member'
        )
        
        # Promote to administrator
        result = TrustGroupService.promote_member(
            group_id=str(group.id),
            organization=self.org_2,
            promoting_org=self.org_1,
            new_membership_type='administrator',
            user='test_user'
        )
        
        self.assertTrue(result)
        
        # Check membership type updated
        membership = TrustGroupMembership.objects.get(
            trust_group=group,
            organization=self.org_2
        )
        self.assertEqual(membership.membership_type, 'administrator')
        
        # Check added to administrators list
        group.refresh_from_db()
        self.assertIn(self.org_2, group.administrators)
    
    def test_get_shared_intelligence_count(self):
        """Test getting shared intelligence statistics."""
        group = TrustGroupService.create_trust_group(
            name='Stats Test Group',
            description='Test group for statistics',
            creator_org=self.org_1,
            default_trust_level_name='Group Trust Level'
        )
        
        # Add members
        TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_2
        )
        
        TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_3
        )
        
        # Get statistics
        stats = TrustGroupService.get_shared_intelligence_count(str(group.id))
        
        self.assertEqual(stats['member_count'], 3)  # Creator + 2 members
        self.assertIn('intelligence_objects_shared', stats)
        self.assertIn('indicators_shared', stats)
        self.assertIn('ttps_shared', stats)
        self.assertIn('reports_shared', stats)