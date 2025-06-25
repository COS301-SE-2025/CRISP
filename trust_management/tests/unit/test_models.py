"""
Comprehensive model tests for Trust Management module.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
import uuid

from TrustManagement.models import (
    TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership,
    TrustLog, SharingPolicy
)
from .factories import (
    TrustLevelFactory, TrustRelationshipFactory, TrustGroupFactory,
    TrustGroupMembershipFactory, SharingPolicyFactory, TrustLogFactory
)


class TrustLevelModelTest(TestCase):
    """Test TrustLevel model."""
    
    def test_create_trust_level(self):
        """Test creating a trust level."""
        trust_level = TrustLevelFactory()
        self.assertTrue(trust_level.is_active)
        self.assertIsNotNone(trust_level.created_at)
        self.assertIsNotNone(trust_level.updated_at)
    
    def test_trust_level_str_representation(self):
        """Test string representation."""
        trust_level = TrustLevelFactory(name="High Trust")
        self.assertEqual(str(trust_level), "High Trust")
    
    def test_trust_score_validation(self):
        """Test trust score validation."""
        with self.assertRaises(ValidationError):
            trust_level = TrustLevelFactory(trust_score=101)
            trust_level.full_clean()
        
        with self.assertRaises(ValidationError):
            trust_level = TrustLevelFactory(trust_score=-1)
            trust_level.full_clean()
    
    def test_unique_name_constraint(self):
        """Test unique name constraint."""
        TrustLevelFactory(name="Unique Name")
        with self.assertRaises(IntegrityError):
            TrustLevelFactory(name="Unique Name")
    
    def test_unique_trust_score_constraint(self):
        """Test unique trust score constraint."""
        TrustLevelFactory(trust_score=50)
        with self.assertRaises(IntegrityError):
            TrustLevelFactory(trust_score=50)
    
    def test_access_level_choices(self):
        """Test access level choices validation."""
        valid_levels = ['none', 'read', 'subscribe', 'contribute', 'full']
        for level in valid_levels:
            trust_level = TrustLevelFactory(access_level=level)
            trust_level.full_clean()
    
    def test_anonymization_strategy_choices(self):
        """Test anonymization strategy choices."""
        valid_strategies = ['full', 'partial', 'minimal', 'none']
        for strategy in valid_strategies:
            trust_level = TrustLevelFactory(anonymization_strategy=strategy)
            trust_level.full_clean()
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        trust_level = TrustLevelFactory()
        trust_level.delete()
        self.assertFalse(trust_level.is_active)
        
        # Should still exist in database
        self.assertTrue(TrustLevel.objects.filter(id=trust_level.id).exists())
        
        # Should not appear in active queryset
        self.assertFalse(TrustLevel.active_objects.filter(id=trust_level.id).exists())


class TrustRelationshipModelTest(TestCase):
    """Test TrustRelationship model."""
    
    def test_create_relationship(self):
        """Test creating a trust relationship."""
        relationship = TrustRelationshipFactory()
        self.assertEqual(relationship.status, 'pending')
        self.assertIsNotNone(relationship.created_at)
    
    def test_relationship_str_representation(self):
        """Test string representation."""
        relationship = TrustRelationshipFactory(
            source_organization="org1",
            target_organization="org2"
        )
        expected = f"org1 -> org2 ({relationship.trust_level.name})"
        self.assertEqual(str(relationship), expected)
    
    def test_self_relationship_validation(self):
        """Test that self-relationships are not allowed."""
        org_id = str(uuid.uuid4())
        with self.assertRaises(ValidationError):
            relationship = TrustRelationshipFactory(
                source_organization=org_id,
                target_organization=org_id
            )
            relationship.full_clean()
    
    def test_unique_active_relationship_constraint(self):
        """Test unique active relationship constraint."""
        org1 = str(uuid.uuid4())
        org2 = str(uuid.uuid4())
        
        TrustRelationshipFactory(
            source_organization=org1,
            target_organization=org2,
            status='active'
        )
        
        with self.assertRaises(IntegrityError):
            TrustRelationshipFactory(
                source_organization=org1,
                target_organization=org2,
                status='active'
            )
    
    def test_relationship_type_choices(self):
        """Test relationship type choices."""
        valid_types = ['bilateral', 'unilateral', 'hierarchical', 'federation']
        for rel_type in valid_types:
            relationship = TrustRelationshipFactory(relationship_type=rel_type)
            relationship.full_clean()
    
    def test_status_choices(self):
        """Test status choices."""
        valid_statuses = ['pending', 'active', 'denied', 'revoked', 'expired']
        for status in valid_statuses:
            relationship = TrustRelationshipFactory(status=status)
            relationship.full_clean()
    
    def test_is_active_property(self):
        """Test is_active property."""
        relationship = TrustRelationshipFactory(status='active')
        self.assertTrue(relationship.is_active)
        
        relationship.status = 'denied'
        self.assertFalse(relationship.is_active)
    
    def test_is_expired_property(self):
        """Test is_expired property."""
        # Not expired
        relationship = TrustRelationshipFactory(
            expires_at=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(relationship.is_expired)
        
        # Expired
        relationship.expires_at = timezone.now() - timedelta(days=1)
        self.assertTrue(relationship.is_expired)
        
        # No expiration
        relationship.expires_at = None
        self.assertFalse(relationship.is_expired)
    
    def test_approve_method(self):
        """Test approve method."""
        relationship = TrustRelationshipFactory(status='pending')
        approver = str(uuid.uuid4())
        
        relationship.approve(approver)
        
        self.assertEqual(relationship.status, 'active')
        self.assertEqual(relationship.approved_by, approver)
        self.assertIsNotNone(relationship.approved_at)
    
    def test_deny_method(self):
        """Test deny method."""
        relationship = TrustRelationshipFactory(status='pending')
        denier = str(uuid.uuid4())
        reason = "Security concerns"
        
        relationship.deny(denier, reason)
        
        self.assertEqual(relationship.status, 'denied')
        self.assertEqual(relationship.denied_by, denier)
        self.assertEqual(relationship.denial_reason, reason)
        self.assertIsNotNone(relationship.denied_at)
    
    def test_revoke_method(self):
        """Test revoke method."""
        relationship = TrustRelationshipFactory(status='active')
        revoker = str(uuid.uuid4())
        reason = "Policy change"
        
        relationship.revoke(revoker, reason)
        
        self.assertEqual(relationship.status, 'revoked')
        self.assertEqual(relationship.revoked_by, revoker)
        self.assertEqual(relationship.revocation_reason, reason)
        self.assertIsNotNone(relationship.revoked_at)


class TrustGroupModelTest(TestCase):
    """Test TrustGroup model."""
    
    def test_create_trust_group(self):
        """Test creating a trust group."""
        group = TrustGroupFactory()
        self.assertTrue(group.is_active)
        self.assertIsNotNone(group.created_at)
    
    def test_group_str_representation(self):
        """Test string representation."""
        group = TrustGroupFactory(name="Test Group")
        self.assertEqual(str(group), "Test Group")
    
    def test_unique_name_constraint(self):
        """Test unique name constraint."""
        TrustGroupFactory(name="Unique Group")
        with self.assertRaises(IntegrityError):
            TrustGroupFactory(name="Unique Group")
    
    def test_group_type_choices(self):
        """Test group type choices."""
        valid_types = ['sector', 'geography', 'purpose', 'custom']
        for group_type in valid_types:
            group = TrustGroupFactory(group_type=group_type)
            group.full_clean()
    
    def test_member_count_property(self):
        """Test member_count property."""
        group = TrustGroupFactory()
        self.assertEqual(group.member_count, 0)
        
        TrustGroupMembershipFactory(group=group, status='active')
        TrustGroupMembershipFactory(group=group, status='active')
        TrustGroupMembershipFactory(group=group, status='pending')
        
        # Should only count active members
        self.assertEqual(group.member_count, 2)


class TrustGroupMembershipModelTest(TestCase):
    """Test TrustGroupMembership model."""
    
    def test_create_membership(self):
        """Test creating a membership."""
        membership = TrustGroupMembershipFactory()
        self.assertEqual(membership.status, 'active')
        self.assertIsNotNone(membership.created_at)
    
    def test_membership_str_representation(self):
        """Test string representation."""
        membership = TrustGroupMembershipFactory(
            organization_id="org1",
            membership_type="admin"
        )
        expected = f"org1 (admin) in {membership.group.name}"
        self.assertEqual(str(membership), expected)
    
    def test_unique_active_membership_constraint(self):
        """Test unique active membership constraint."""
        group = TrustGroupFactory()
        org_id = str(uuid.uuid4())
        
        TrustGroupMembershipFactory(
            group=group,
            organization_id=org_id,
            status='active'
        )
        
        with self.assertRaises(IntegrityError):
            TrustGroupMembershipFactory(
                group=group,
                organization_id=org_id,
                status='active'
            )
    
    def test_membership_type_choices(self):
        """Test membership type choices."""
        valid_types = ['admin', 'member', 'observer']
        for mem_type in valid_types:
            membership = TrustGroupMembershipFactory(membership_type=mem_type)
            membership.full_clean()
    
    def test_status_choices(self):
        """Test status choices."""
        valid_statuses = ['pending', 'active', 'suspended', 'removed']
        for status in valid_statuses:
            membership = TrustGroupMembershipFactory(status=status)
            membership.full_clean()
    
    def test_is_active_property(self):
        """Test is_active property."""
        membership = TrustGroupMembershipFactory(status='active')
        self.assertTrue(membership.is_active)
        
        membership.status = 'suspended'
        self.assertFalse(membership.is_active)


class SharingPolicyModelTest(TestCase):
    """Test SharingPolicy model."""
    
    def test_create_sharing_policy(self):
        """Test creating a sharing policy."""
        policy = SharingPolicyFactory()
        self.assertTrue(policy.is_active)
        self.assertIsNotNone(policy.created_at)
    
    def test_policy_str_representation(self):
        """Test string representation."""
        policy = SharingPolicyFactory(name="Test Policy")
        self.assertEqual(str(policy), "Test Policy")
    
    def test_json_field_defaults(self):
        """Test JSON field defaults."""
        policy = SharingPolicyFactory(
            resource_types=None,
            allowed_actions=None,
            anonymization_rules=None
        )
        self.assertEqual(policy.resource_types, [])
        self.assertEqual(policy.allowed_actions, [])
        self.assertEqual(policy.anonymization_rules, {})


class TrustLogModelTest(TestCase):
    """Test TrustLog model."""
    
    def test_create_trust_log(self):
        """Test creating a trust log entry."""
        log = TrustLogFactory()
        self.assertTrue(log.success)
        self.assertIsNotNone(log.timestamp)
    
    def test_log_str_representation(self):
        """Test string representation."""
        log = TrustLogFactory(
            action="create",
            resource_type="relationship"
        )
        expected = f"create relationship at {log.timestamp}"
        self.assertEqual(str(log), expected)
    
    def test_action_choices(self):
        """Test action choices."""
        valid_actions = ['create', 'approve', 'deny', 'revoke', 'access', 'join', 'leave']
        for action in valid_actions:
            log = TrustLogFactory(action=action)
            log.full_clean()
    
    def test_resource_type_choices(self):
        """Test resource type choices."""
        valid_types = ['relationship', 'group', 'membership', 'intelligence', 'policy']
        for res_type in valid_types:
            log = TrustLogFactory(resource_type=res_type)
            log.full_clean()
    
    def test_json_field_default(self):
        """Test JSON field default."""
        log = TrustLogFactory(details=None)
        self.assertEqual(log.details, {})


class ModelIntegrationTest(TestCase):
    """Test model interactions and complex scenarios."""
    
    def test_cascade_deletions(self):
        """Test cascade deletion behavior."""
        trust_level = TrustLevelFactory()
        relationship = TrustRelationshipFactory(trust_level=trust_level)
        group = TrustGroupFactory(default_trust_level=trust_level)
        
        # Soft delete trust level
        trust_level.delete()
        
        # Relationship should still exist but trust level marked inactive
        relationship.refresh_from_db()
        self.assertFalse(relationship.trust_level.is_active)
        
        # Group should still exist
        group.refresh_from_db()
        self.assertFalse(group.default_trust_level.is_active)
    
    def test_complex_query_scenarios(self):
        """Test complex query scenarios."""
        # Create test data
        high_trust = TrustLevelFactory(name="High Trust", trust_score=80)
        low_trust = TrustLevelFactory(name="Low Trust", trust_score=20)
        
        org1 = str(uuid.uuid4())
        org2 = str(uuid.uuid4())
        org3 = str(uuid.uuid4())
        
        # Active relationship
        TrustRelationshipFactory(
            source_organization=org1,
            target_organization=org2,
            trust_level=high_trust,
            status='active'
        )
        
        # Expired relationship
        TrustRelationshipFactory(
            source_organization=org1,
            target_organization=org3,
            trust_level=low_trust,
            status='active',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Test queries
        active_relationships = TrustRelationship.objects.filter(
            source_organization=org1,
            status='active'
        )
        self.assertEqual(active_relationships.count(), 2)
        
        # High trust relationships
        high_trust_rels = TrustRelationship.objects.filter(
            source_organization=org1,
            trust_level__trust_score__gte=50,
            status='active'
        )
        self.assertEqual(high_trust_rels.count(), 1)
