import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from ..models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership,
    TrustLog, SharingPolicy
)


class TrustLevelModelTest(TestCase):
    """Test cases for TrustLevel model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Test Trust Level',
            level='medium',
            description='Test trust level description',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
    
    def test_trust_level_creation(self):
        """Test trust level creation."""
        self.assertEqual(self.trust_level.name, 'Test Trust Level')
        self.assertEqual(self.trust_level.level, 'medium')
        self.assertEqual(self.trust_level.numerical_value, 50)
        self.assertTrue(self.trust_level.is_active)
        self.assertFalse(self.trust_level.is_system_default)
    
    def test_trust_level_str_representation(self):
        """Test string representation."""
        expected = f"{self.trust_level.name} ({self.trust_level.level})"
        self.assertEqual(str(self.trust_level), expected)
    
    def test_trust_level_validation(self):
        """Test trust level validation."""
        # Test invalid numerical value
        with self.assertRaises(ValidationError):
            trust_level = TrustLevel(
                name='Invalid Trust Level',
                level='high',
                description='Invalid numerical value',
                numerical_value=150,  # Invalid: > 100
                created_by='test_user'
            )
            trust_level.full_clean()
    
    def test_get_default_trust_level(self):
        """Test getting default trust level."""
        # Create system default
        default_level = TrustLevel.objects.create(
            name='Default Level',
            level='low',
            description='Default trust level',
            numerical_value=25,
            is_system_default=True,
            created_by='system'
        )
        
        result = TrustLevel.get_default_trust_level()
        self.assertEqual(result, default_level)


class TrustGroupModelTest(TestCase):
    """Test cases for TrustGroup model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Group Trust Level',
            level='medium',
            description='Trust level for groups',
            numerical_value=50,
            created_by='test_user'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Test Trust Group',
            description='Test group description',
            group_type='community',
            is_public=True,
            requires_approval=True,
            default_trust_level=self.trust_level,
            created_by='org_1',
            administrators=['org_1']
        )
    
    def test_trust_group_creation(self):
        """Test trust group creation."""
        self.assertEqual(self.trust_group.name, 'Test Trust Group')
        self.assertEqual(self.trust_group.group_type, 'community')
        self.assertTrue(self.trust_group.is_public)
        self.assertTrue(self.trust_group.requires_approval)
        self.assertTrue(self.trust_group.is_active)
    
    def test_trust_group_str_representation(self):
        """Test string representation."""
        self.assertEqual(str(self.trust_group), self.trust_group.name)
    
    def test_can_administer(self):
        """Test administrator check."""
        self.assertTrue(self.trust_group.can_administer('org_1'))
        self.assertFalse(self.trust_group.can_administer('org_2'))
    
    def test_get_member_count(self):
        """Test member count calculation."""
        # Initially no members
        self.assertEqual(self.trust_group.get_member_count(), 0)
        
        # Add a member
        TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization='org_2',
            is_active=True
        )
        
        self.assertEqual(self.trust_group.get_member_count(), 1)


class TrustRelationshipModelTest(TestCase):
    """Test cases for TrustRelationship model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Relationship Trust Level',
            level='high',
            description='Trust level for relationships',
            numerical_value=75,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization='org_1',
            target_organization='org_2',
            relationship_type='bilateral',
            trust_level=self.trust_level,
            status='pending',
            anonymization_level='partial',
            access_level='read',
            created_by='test_user',
            last_modified_by='test_user'
        )
    
    def test_trust_relationship_creation(self):
        """Test trust relationship creation."""
        self.assertEqual(self.relationship.source_organization, 'org_1')
        self.assertEqual(self.relationship.target_organization, 'org_2')
        self.assertEqual(self.relationship.relationship_type, 'bilateral')
        self.assertEqual(self.relationship.status, 'pending')
        self.assertTrue(self.relationship.is_bilateral)
        self.assertTrue(self.relationship.is_active)
    
    def test_trust_relationship_str_representation(self):
        """Test string representation."""
        expected = f"Trust: {self.relationship.source_organization} -> {self.relationship.target_organization} ({self.trust_level.name})"
        self.assertEqual(str(self.relationship), expected)
    
    def test_trust_relationship_validation(self):
        """Test trust relationship validation."""
        # Test same source and target organization
        with self.assertRaises(ValidationError):
            relationship = TrustRelationship(
                source_organization='org_1',
                target_organization='org_1',  # Same as source
                trust_level=self.trust_level,
                created_by='test_user',
                last_modified_by='test_user'
            )
            relationship.full_clean()
        
        # Test invalid date range
        with self.assertRaises(ValidationError):
            relationship = TrustRelationship(
                source_organization='org_3',
                target_organization='org_4',
                trust_level=self.trust_level,
                valid_from=timezone.now(),
                valid_until=timezone.now() - timedelta(days=1),  # Invalid: before valid_from
                created_by='test_user',
                last_modified_by='test_user'
            )
            relationship.full_clean()
    
    def test_is_expired_property(self):
        """Test expiration check."""
        # Not expired (no expiration date)
        self.assertFalse(self.relationship.is_expired)
        
        # Set expiration in future
        self.relationship.valid_until = timezone.now() + timedelta(days=1)
        self.assertFalse(self.relationship.is_expired)
        
        # Set expiration in past
        self.relationship.valid_until = timezone.now() - timedelta(days=1)
        self.assertTrue(self.relationship.is_expired)
    
    def test_is_fully_approved_property(self):
        """Test approval status check."""
        # Initially not approved
        self.assertFalse(self.relationship.is_fully_approved)
        
        # Approve source only
        self.relationship.approved_by_source = True
        self.assertFalse(self.relationship.is_fully_approved)
        
        # Approve both
        self.relationship.approved_by_target = True
        self.assertTrue(self.relationship.is_fully_approved)
        
        # Test community relationship (only needs source approval)
        community_rel = TrustRelationship(
            source_organization='org_3',
            target_organization='org_4',
            relationship_type='community',
            trust_level=self.trust_level,
            approved_by_source=True,
            created_by='test_user',
            last_modified_by='test_user'
        )
        self.assertTrue(community_rel.is_fully_approved)
    
    def test_is_effective_property(self):
        """Test effective status check."""
        # Initially not effective (not approved, wrong status)
        self.assertFalse(self.relationship.is_effective)
        
        # Make it fully approved and active
        self.relationship.approved_by_source = True
        self.relationship.approved_by_target = True
        self.relationship.status = 'active'
        self.assertTrue(self.relationship.is_effective)
        
        # Test with expiration
        self.relationship.valid_until = timezone.now() - timedelta(days=1)
        self.assertFalse(self.relationship.is_effective)  # Expired
    
    def test_activate_method(self):
        """Test relationship activation."""
        # Cannot activate without approval
        result = self.relationship.activate()
        self.assertFalse(result)
        self.assertEqual(self.relationship.status, 'pending')
        
        # Approve and activate
        self.relationship.approved_by_source = True
        self.relationship.approved_by_target = True
        result = self.relationship.activate()
        self.assertTrue(result)
        self.assertEqual(self.relationship.status, 'active')
        self.assertIsNotNone(self.relationship.activated_at)
    
    def test_revoke_method(self):
        """Test relationship revocation."""
        self.relationship.revoke('test_user', 'Test revocation')
        
        self.assertEqual(self.relationship.status, 'revoked')
        self.assertFalse(self.relationship.is_active)
        self.assertIsNotNone(self.relationship.revoked_at)
        self.assertEqual(self.relationship.revoked_by, 'test_user')
        self.assertIn('Test revocation', self.relationship.notes)
    
    def test_suspend_method(self):
        """Test relationship suspension."""
        self.relationship.suspend('test_user', 'Test suspension')
        
        self.assertEqual(self.relationship.status, 'suspended')
        self.assertEqual(self.relationship.last_modified_by, 'test_user')
        self.assertIn('Test suspension', self.relationship.notes)
    
    def test_get_effective_anonymization_level(self):
        """Test effective anonymization level calculation."""
        # Standard level
        self.assertEqual(self.relationship.get_effective_anonymization_level(), 'partial')
        
        # Custom level defaults to trust level
        self.relationship.anonymization_level = 'custom'
        self.assertEqual(self.relationship.get_effective_anonymization_level(), self.trust_level.default_anonymization_level)


class TrustGroupMembershipModelTest(TestCase):
    """Test cases for TrustGroupMembership model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Membership Trust Level',
            level='medium',
            description='Trust level for memberships',
            numerical_value=50,
            created_by='test_user'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Membership Test Group',
            description='Test group for memberships',
            default_trust_level=self.trust_level,
            created_by='org_1'
        )
        
        self.membership = TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization='org_2',
            membership_type='member',
            invited_by='org_1'
        )
    
    def test_membership_creation(self):
        """Test membership creation."""
        self.assertEqual(self.membership.organization, 'org_2')
        self.assertEqual(self.membership.membership_type, 'member')
        self.assertTrue(self.membership.is_active)
        self.assertEqual(self.membership.invited_by, 'org_1')
    
    def test_membership_str_representation(self):
        """Test string representation."""
        expected = f"{self.membership.organization} in {self.trust_group.name}"
        self.assertEqual(str(self.membership), expected)


class TrustLogModelTest(TestCase):
    """Test cases for TrustLog model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Log Trust Level',
            level='medium',
            description='Trust level for logs',
            numerical_value=50,
            created_by='test_user'
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization='org_1',
            target_organization='org_2',
            trust_level=self.trust_level,
            created_by='test_user',
            last_modified_by='test_user'
        )
    
    def test_log_trust_event(self):
        """Test trust event logging."""
        log_entry = TrustLog.log_trust_event(
            action='relationship_created',
            source_organization='org_1',
            target_organization='org_2',
            trust_relationship=self.relationship,
            user='test_user',
            success=True,
            details={'test': 'data'}
        )
        
        self.assertEqual(log_entry.action, 'relationship_created')
        self.assertEqual(log_entry.source_organization, 'org_1')
        self.assertEqual(log_entry.target_organization, 'org_2')
        self.assertEqual(log_entry.trust_relationship, self.relationship)
        self.assertEqual(log_entry.user, 'test_user')
        self.assertTrue(log_entry.success)
        self.assertEqual(log_entry.details['test'], 'data')
    
    def test_log_str_representation(self):
        """Test log string representation."""
        log_entry = TrustLog.objects.create(
            action='relationship_created',
            source_organization='org_1',
            user='test_user',
            success=True
        )
        
        expected = f"relationship_created - org_1 - SUCCESS - {log_entry.timestamp}"
        self.assertEqual(str(log_entry), expected)


class SharingPolicyModelTest(TestCase):
    """Test cases for SharingPolicy model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.policy = SharingPolicy.objects.create(
            name='Test Sharing Policy',
            description='Test policy description',
            allowed_stix_types=['indicator', 'malware'],
            blocked_stix_types=['vulnerability'],
            max_tlp_level='green',
            max_age_days=30,
            require_anonymization=True,
            allow_attribution=False,
            created_by='test_user'
        )
    
    def test_policy_creation(self):
        """Test sharing policy creation."""
        self.assertEqual(self.policy.name, 'Test Sharing Policy')
        self.assertEqual(self.policy.max_tlp_level, 'green')
        self.assertEqual(self.policy.max_age_days, 30)
        self.assertTrue(self.policy.require_anonymization)
        self.assertFalse(self.policy.allow_attribution)
        self.assertTrue(self.policy.is_active)
    
    def test_policy_str_representation(self):
        """Test string representation."""
        self.assertEqual(str(self.policy), self.policy.name)
    
    def test_applies_to_stix_object(self):
        """Test STIX object applicability check."""
        # Allowed type
        self.assertTrue(self.policy.applies_to_stix_object('indicator'))
        
        # Blocked type
        self.assertFalse(self.policy.applies_to_stix_object('vulnerability'))
        
        # Type not in allowed list (but not blocked)
        self.assertFalse(self.policy.applies_to_stix_object('campaign'))
        
        # Test with no allowed types (allow all except blocked)
        policy_no_allowed = SharingPolicy.objects.create(
            name='No Allowed Types Policy',
            description='Policy with no allowed types',
            blocked_stix_types=['vulnerability'],
            created_by='test_user'
        )
        
        self.assertTrue(policy_no_allowed.applies_to_stix_object('indicator'))
        self.assertFalse(policy_no_allowed.applies_to_stix_object('vulnerability'))
    
    def test_get_anonymization_requirements(self):
        """Test anonymization requirements retrieval."""
        requirements = self.policy.get_anonymization_requirements()
        
        self.assertTrue(requirements['required'])
        self.assertEqual(requirements['rules'], self.policy.anonymization_rules)