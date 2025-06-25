"""
Comprehensive service tests for Trust Management module.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch
import uuid

from TrustManagement.services.trust_service import TrustService
from TrustManagement.services.trust_group_service import TrustGroupService
from TrustManagement.models import (
    TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog
)
from .factories import (
    TrustLevelFactory, TrustRelationshipFactory, TrustGroupFactory,
    TrustGroupMembershipFactory
)


class TrustServiceTest(TestCase):
    """Test TrustService class."""
    
    def setUp(self):
        """Set up test data."""
        self.trust_levels = {
            'none': TrustLevelFactory(name="No Trust", trust_score=0, access_level='none'),
            'basic': TrustLevelFactory(name="Basic Trust", trust_score=25, access_level='read'),
            'standard': TrustLevelFactory(name="Standard Trust", trust_score=50, access_level='subscribe'),
            'high': TrustLevelFactory(name="High Trust", trust_score=75, access_level='contribute'),
            'complete': TrustLevelFactory(name="Complete Trust", trust_score=100, access_level='full')
        }
        
        self.org1 = str(uuid.uuid4())
        self.org2 = str(uuid.uuid4())
        self.org3 = str(uuid.uuid4())
        self.user_id = str(uuid.uuid4())
    
    def test_create_trust_relationship_success(self):
        """Test successful trust relationship creation."""
        relationship = TrustService.create_trust_relationship(
            source_org=self.org1,
            target_org=self.org2,
            trust_level_name="Standard Trust",
            relationship_type="bilateral",
            created_by=self.user_id,
            notes="Test relationship"
        )
        
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.source_organization, self.org1)
        self.assertEqual(relationship.target_organization, self.org2)
        self.assertEqual(relationship.trust_level.name, "Standard Trust")
        self.assertEqual(relationship.status, "pending")
        self.assertEqual(relationship.created_by, self.user_id)
    
    def test_create_trust_relationship_invalid_trust_level(self):
        """Test relationship creation with invalid trust level."""
        with self.assertRaises(ValueError):
            TrustService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org2,
                trust_level_name="Invalid Trust",
                relationship_type="bilateral",
                created_by=self.user_id
            )
    
    def test_create_trust_relationship_self_reference(self):
        """Test relationship creation with self-reference."""
        with self.assertRaises(ValueError):
            TrustService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org1,
                trust_level_name="Standard Trust",
                relationship_type="bilateral",
                created_by=self.user_id
            )
    
    def test_create_trust_relationship_existing_active(self):
        """Test creating relationship when active one exists."""
        # Create existing active relationship
        TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_levels['standard'],
            status='active'
        )
        
        with self.assertRaises(ValueError):
            TrustService.create_trust_relationship(
                source_org=self.org1,
                target_org=self.org2,
                trust_level_name="High Trust",
                relationship_type="bilateral",
                created_by=self.user_id
            )
    
    def test_approve_trust_relationship_success(self):
        """Test successful relationship approval."""
        relationship = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            status='pending'
        )
        
        result = TrustService.approve_trust_relationship(
            relationship_id=relationship.id,
            approving_org=self.org2,
            approved_by=self.user_id
        )
        
        self.assertTrue(result)
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'active')
        self.assertEqual(relationship.approved_by, self.user_id)
        self.assertIsNotNone(relationship.approved_at)
    
    def test_approve_trust_relationship_wrong_organization(self):
        """Test approval by wrong organization."""
        relationship = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            status='pending'
        )
        
        with self.assertRaises(ValueError):
            TrustService.approve_trust_relationship(
                relationship_id=relationship.id,
                approving_org=self.org3,  # Wrong org
                approved_by=self.user_id
            )
    
    def test_approve_trust_relationship_not_pending(self):
        """Test approving non-pending relationship."""
        relationship = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            status='active'
        )
        
        with self.assertRaises(ValueError):
            TrustService.approve_trust_relationship(
                relationship_id=relationship.id,
                approving_org=self.org2,
                approved_by=self.user_id
            )
    
    def test_deny_trust_relationship_success(self):
        """Test successful relationship denial."""
        relationship = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            status='pending'
        )
        
        result = TrustService.deny_trust_relationship(
            relationship_id=relationship.id,
            denying_org=self.org2,
            denied_by=self.user_id,
            reason="Security concerns"
        )
        
        self.assertTrue(result)
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'denied')
        self.assertEqual(relationship.denied_by, self.user_id)
        self.assertEqual(relationship.denial_reason, "Security concerns")
    
    def test_revoke_trust_relationship_success(self):
        """Test successful relationship revocation."""
        relationship = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            status='active'
        )
        
        result = TrustService.revoke_trust_relationship(
            relationship_id=relationship.id,
            revoking_org=self.org1,
            revoked_by=self.user_id,
            reason="Policy change"
        )
        
        self.assertTrue(result)
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'revoked')
        self.assertEqual(relationship.revoked_by, self.user_id)
        self.assertEqual(relationship.revocation_reason, "Policy change")
    
    def test_check_trust_level_direct_relationship(self):
        """Test checking trust level with direct relationship."""
        relationship = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_levels['high'],
            status='active'
        )
        
        result = TrustService.check_trust_level(self.org1, self.org2)
        
        self.assertIsNotNone(result)
        trust_level, rel = result
        self.assertEqual(trust_level.name, "High Trust")
        self.assertEqual(rel.id, relationship.id)
    
    def test_check_trust_level_no_relationship(self):
        """Test checking trust level with no relationship."""
        result = TrustService.check_trust_level(self.org1, self.org2)
        self.assertIsNone(result)
    
    def test_check_trust_level_expired_relationship(self):
        """Test checking trust level with expired relationship."""
        TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_levels['high'],
            status='active',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        result = TrustService.check_trust_level(self.org1, self.org2)
        self.assertIsNone(result)
    
    def test_can_access_intelligence_success(self):
        """Test intelligence access check success."""
        TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_levels['high'],  # contribute level
            status='active'
        )
        
        can_access, reason, rel = TrustService.can_access_intelligence(
            requesting_org=self.org1,
            intelligence_owner=self.org2,
            required_access_level='read'
        )
        
        self.assertTrue(can_access)
        self.assertIn("sufficient", reason.lower())
        self.assertIsNotNone(rel)
    
    def test_can_access_intelligence_insufficient_trust(self):
        """Test intelligence access with insufficient trust."""
        TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_levels['basic'],  # read level
            status='active'
        )
        
        can_access, reason, rel = TrustService.can_access_intelligence(
            requesting_org=self.org1,
            intelligence_owner=self.org2,
            required_access_level='contribute'
        )
        
        self.assertFalse(can_access)
        self.assertIn("insufficient", reason.lower())
        self.assertIsNotNone(rel)
    
    def test_can_access_intelligence_no_relationship(self):
        """Test intelligence access with no relationship."""
        can_access, reason, rel = TrustService.can_access_intelligence(
            requesting_org=self.org1,
            intelligence_owner=self.org2,
            required_access_level='read'
        )
        
        self.assertFalse(can_access)
        self.assertIn("no trust", reason.lower())
        self.assertIsNone(rel)
    
    def test_get_relationships_for_organization(self):
        """Test getting relationships for an organization."""
        # Create various relationships
        rel1 = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            status='active'
        )
        rel2 = TrustRelationshipFactory(
            source_organization=self.org2,
            target_organization=self.org1,
            status='active'
        )
        rel3 = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org3,
            status='pending'
        )
        
        # Test outgoing relationships
        outgoing = TrustService.get_relationships_for_organization(
            self.org1, direction='outgoing'
        )
        self.assertEqual(len(outgoing), 2)
        
        # Test incoming relationships
        incoming = TrustService.get_relationships_for_organization(
            self.org1, direction='incoming'
        )
        self.assertEqual(len(incoming), 1)
        
        # Test all relationships
        all_rels = TrustService.get_relationships_for_organization(
            self.org1, direction='all'
        )
        self.assertEqual(len(all_rels), 3)
        
        # Test active only
        active_rels = TrustService.get_relationships_for_organization(
            self.org1, status='active'
        )
        self.assertEqual(len(active_rels), 2)
    
    def test_calculate_trust_metrics(self):
        """Test trust metrics calculation."""
        # Create test relationships
        TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_levels['high'],
            status='active'
        )
        TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org3,
            trust_level=self.trust_levels['standard'],
            status='active'
        )
        
        metrics = TrustService.calculate_trust_metrics(self.org1)
        
        self.assertIn('total_relationships', metrics)
        self.assertIn('active_relationships', metrics)
        self.assertIn('average_trust_score', metrics)
        self.assertIn('trust_distribution', metrics)
        
        self.assertEqual(metrics['total_relationships'], 2)
        self.assertEqual(metrics['active_relationships'], 2)
        self.assertEqual(metrics['average_trust_score'], 62.5)  # (75+50)/2
    
    def test_cleanup_expired_relationships(self):
        """Test cleanup of expired relationships."""
        # Create expired relationship
        expired_rel = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org2,
            status='active',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Create non-expired relationship
        active_rel = TrustRelationshipFactory(
            source_organization=self.org1,
            target_organization=self.org3,
            status='active',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        count = TrustService.cleanup_expired_relationships()
        
        self.assertEqual(count, 1)
        
        expired_rel.refresh_from_db()
        active_rel.refresh_from_db()
        
        self.assertEqual(expired_rel.status, 'expired')
        self.assertEqual(active_rel.status, 'active')
    
    @patch('TrustManagement.services.trust_service.TrustLog.objects.create')
    def test_log_trust_activity(self, mock_log_create):
        """Test trust activity logging."""
        TrustService._log_activity(
            organization_id=self.org1,
            action='create',
            resource_type='relationship',
            resource_id=str(uuid.uuid4()),
            user_id=self.user_id,
            details={'test': 'data'}
        )
        
        mock_log_create.assert_called_once()
        args, kwargs = mock_log_create.call_args
        
        self.assertEqual(kwargs['organization_id'], self.org1)
        self.assertEqual(kwargs['action'], 'create')
        self.assertEqual(kwargs['resource_type'], 'relationship')


class TrustGroupServiceTest(TestCase):
    """Test TrustGroupService class."""
    
    def setUp(self):
        """Set up test data."""
        self.trust_level = TrustLevelFactory(name="Standard Trust")
        self.org1 = str(uuid.uuid4())
        self.org2 = str(uuid.uuid4())
        self.org3 = str(uuid.uuid4())
        self.user_id = str(uuid.uuid4())
    
    def test_create_trust_group_success(self):
        """Test successful trust group creation."""
        group = TrustGroupService.create_trust_group(
            name="Test Group",
            description="Test group description",
            creator_org=self.org1,
            group_type="sector",
            is_public=True,
            default_trust_level_name="Standard Trust"
        )
        
        self.assertIsNotNone(group)
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.creator_organization, self.org1)
        self.assertEqual(group.group_type, "sector")
        self.assertTrue(group.is_public)
        self.assertEqual(group.default_trust_level.name, "Standard Trust")
    
    def test_create_trust_group_invalid_trust_level(self):
        """Test group creation with invalid trust level."""
        with self.assertRaises(ValueError):
            TrustGroupService.create_trust_group(
                name="Test Group",
                description="Test description",
                creator_org=self.org1,
                default_trust_level_name="Invalid Trust"
            )
    
    def test_join_trust_group_success(self):
        """Test successful group joining."""
        group = TrustGroupFactory(is_public=True)
        
        membership = TrustGroupService.join_trust_group(
            group_id=group.id,
            organization_id=self.org1,
            membership_type="member",
            joined_by=self.user_id
        )
        
        self.assertIsNotNone(membership)
        self.assertEqual(membership.group, group)
        self.assertEqual(membership.organization_id, self.org1)
        self.assertEqual(membership.membership_type, "member")
        self.assertEqual(membership.status, "active")
    
    def test_join_trust_group_private_group(self):
        """Test joining private group."""
        group = TrustGroupFactory(is_public=False)
        
        membership = TrustGroupService.join_trust_group(
            group_id=group.id,
            organization_id=self.org1,
            membership_type="member",
            joined_by=self.user_id
        )
        
        self.assertEqual(membership.status, "pending")
    
    def test_join_trust_group_already_member(self):
        """Test joining group as existing member."""
        group = TrustGroupFactory()
        TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org1,
            status='active'
        )
        
        with self.assertRaises(ValueError):
            TrustGroupService.join_trust_group(
                group_id=group.id,
                organization_id=self.org1,
                membership_type="member",
                joined_by=self.user_id
            )
    
    def test_leave_trust_group_success(self):
        """Test successful group leaving."""
        group = TrustGroupFactory()
        membership = TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org1,
            status='active'
        )
        
        result = TrustGroupService.leave_trust_group(
            group_id=group.id,
            organization_id=self.org1,
            left_by=self.user_id
        )
        
        self.assertTrue(result)
        membership.refresh_from_db()
        self.assertEqual(membership.status, 'removed')
    
    def test_leave_trust_group_not_member(self):
        """Test leaving group when not a member."""
        group = TrustGroupFactory()
        
        with self.assertRaises(ValueError):
            TrustGroupService.leave_trust_group(
                group_id=group.id,
                organization_id=self.org1,
                left_by=self.user_id
            )
    
    def test_approve_membership_success(self):
        """Test successful membership approval."""
        group = TrustGroupFactory(creator_organization=self.org1)
        membership = TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org2,
            status='pending'
        )
        
        result = TrustGroupService.approve_membership(
            membership_id=membership.id,
            approving_org=self.org1,
            approved_by=self.user_id
        )
        
        self.assertTrue(result)
        membership.refresh_from_db()
        self.assertEqual(membership.status, 'active')
    
    def test_deny_membership_success(self):
        """Test successful membership denial."""
        group = TrustGroupFactory(creator_organization=self.org1)
        membership = TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org2,
            status='pending'
        )
        
        result = TrustGroupService.deny_membership(
            membership_id=membership.id,
            denying_org=self.org1,
            denied_by=self.user_id,
            reason="Security concerns"
        )
        
        self.assertTrue(result)
        membership.refresh_from_db()
        self.assertEqual(membership.status, 'removed')
    
    def test_get_group_members(self):
        """Test getting group members."""
        group = TrustGroupFactory()
        
        # Create various memberships
        active_member = TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org1,
            status='active'
        )
        pending_member = TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org2,
            status='pending'
        )
        removed_member = TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org3,
            status='removed'
        )
        
        # Test active members only
        active_members = TrustGroupService.get_group_members(
            group.id, status='active'
        )
        self.assertEqual(len(active_members), 1)
        self.assertEqual(active_members[0].organization_id, self.org1)
        
        # Test all members
        all_members = TrustGroupService.get_group_members(group.id)
        self.assertEqual(len(all_members), 3)
    
    def test_get_organization_groups(self):
        """Test getting organization's groups."""
        group1 = TrustGroupFactory()
        group2 = TrustGroupFactory()
        group3 = TrustGroupFactory()
        
        # Create memberships
        TrustGroupMembershipFactory(
            group=group1,
            organization_id=self.org1,
            status='active'
        )
        TrustGroupMembershipFactory(
            group=group2,
            organization_id=self.org1,
            status='pending'
        )
        TrustGroupMembershipFactory(
            group=group3,
            organization_id=self.org2,
            status='active'
        )
        
        # Test active memberships only
        active_groups = TrustGroupService.get_organization_groups(
            self.org1, status='active'
        )
        self.assertEqual(len(active_groups), 1)
        self.assertEqual(active_groups[0].id, group1.id)
        
        # Test all memberships
        all_groups = TrustGroupService.get_organization_groups(self.org1)
        self.assertEqual(len(all_groups), 2)
    
    def test_calculate_group_trust_network(self):
        """Test calculating group trust network."""
        group = TrustGroupFactory(default_trust_level=self.trust_level)
        
        # Create memberships
        TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org1,
            status='active'
        )
        TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org2,
            status='active'
        )
        TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org3,
            status='active'
        )
        
        network = TrustGroupService.calculate_group_trust_network(group.id)
        
        self.assertIn('total_members', network)
        self.assertIn('active_members', network)
        self.assertIn('trust_relationships', network)
        self.assertIn('default_trust_level', network)
        
        self.assertEqual(network['active_members'], 3)
        self.assertEqual(len(network['trust_relationships']), 3)  # 3 potential pairs
    
    def test_get_group_statistics(self):
        """Test getting group statistics."""
        group = TrustGroupFactory()
        
        # Create test data
        TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org1,
            status='active',
            membership_type='admin'
        )
        TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org2,
            status='active',
            membership_type='member'
        )
        TrustGroupMembershipFactory(
            group=group,
            organization_id=self.org3,
            status='pending',
            membership_type='member'
        )
        
        stats = TrustGroupService.get_group_statistics(group.id)
        
        self.assertIn('total_members', stats)
        self.assertIn('active_members', stats)
        self.assertIn('pending_members', stats)
        self.assertIn('membership_breakdown', stats)
        
        self.assertEqual(stats['active_members'], 2)
        self.assertEqual(stats['pending_members'], 1)
        self.assertEqual(stats['membership_breakdown']['admin'], 1)
        self.assertEqual(stats['membership_breakdown']['member'], 2)
