from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog
from core.tests.test_data_fixtures import create_test_user, create_test_organization


class TrustLevelModelTest(TestCase):
    """Test cases for TrustLevel model"""
    
    def test_create_trust_level(self):
        """Test creating a trust level"""
        trust_level = TrustLevel.objects.create(
            name='Test Trust Level',
            description='A test trust level',
            level='trusted',
            numerical_value=50,
            sharing_policies={'data': 'test'}
        )
        
        self.assertEqual(trust_level.name, 'Test Trust Level')
        self.assertEqual(trust_level.level, 'trusted')
        self.assertTrue(trust_level.is_active)
    
    def test_trust_level_str_representation(self):
        """Test string representation of trust level"""
        trust_level = TrustLevel.objects.create(
            name='Public Trust',
            description='A public trust level',
            level='public',
            numerical_value=30
        )
        self.assertEqual(str(trust_level), 'Public Trust (public)')


class TrustRelationshipModelTest(TestCase):
    """Test cases for TrustRelationship model"""
    
    def setUp(self):
        self.org1 = create_test_organization(name_suffix='Organization_1')
        self.org2 = create_test_organization(name_suffix='Organization_2')
        self.trust_level, _ = TrustLevel.objects.get_or_create(
            name='Basic Trust',
            defaults={
                'description': 'A basic trust level',
                'level': 'trusted',
                'numerical_value': 50
            }
        )
        self.user = create_test_user()
        self.user.organization = self.org1
        self.user.save()
    
    def test_create_trust_relationship(self):
        """Test creating a trust relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            created_by=self.user
        )
        
        self.assertEqual(relationship.source_organization, self.org1)
        self.assertEqual(relationship.target_organization, self.org2)
        self.assertEqual(relationship.trust_level, self.trust_level)
        self.assertEqual(relationship.status, 'pending')  # Default status
    
    def test_activate_relationship(self):
        """Test activating a trust relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            anonymization_level='partial',
            created_by=self.user
        )
        
        # Approve from both sides first
        relationship.approve(self.org1, self.user)
        relationship.approve(self.org2, self.user)
        
        # Now activation should work
        result = relationship.activate()
        self.assertTrue(result)
        self.assertEqual(relationship.status, 'active')
        self.assertIsNotNone(relationship.activated_at)
    
    def test_revoke_relationship(self):
        """Test revoking a trust relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            anonymization_level='partial',
            created_by=self.user
        )
        
        relationship.revoke(self.user, 'Testing revocation')
        self.assertEqual(relationship.status, 'revoked')
        self.assertIsNotNone(relationship.revoked_at)
    
    def test_trust_relationship_str_representation(self):
        """Test string representation of trust relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            anonymization_level='partial',
            created_by=self.user
        )
        expected = f"Trust: {self.org1.name} -> {self.org2.name} ({self.trust_level.name})"
        self.assertEqual(str(relationship), expected)


class TrustGroupModelTest(TestCase):
    """Test cases for TrustGroup model"""
    
    def setUp(self):
        self.trust_level, _ = TrustLevel.objects.get_or_create(
            name='Group Trust',
            defaults={
                'description': 'A group trust level',
                'level': 'trusted',
                'numerical_value': 60
            }
        )
        self.organization = create_test_organization(name_suffix='trust_group')
        self.user = create_test_user()
        self.user.organization = self.organization
        self.user.save()
    
    def test_create_trust_group(self):
        """Test creating a trust group"""
        group = TrustGroup.objects.create(
            name='Test Trust Group',
            description='A test trust group',
            default_trust_level=self.trust_level,
            created_by=str(self.user.organization.id)
        )
        
        self.assertEqual(group.name, 'Test Trust Group')
        self.assertEqual(group.default_trust_level, self.trust_level)
        self.assertFalse(group.is_public)  # Default value
        self.assertTrue(group.is_active)   # Default value
    
    def test_trust_group_membership(self):
        """Test trust group membership"""
        group = TrustGroup.objects.create(
            name='Test Group',
            description='Test',
            default_trust_level=self.trust_level,
            created_by=str(self.user.organization.id)
        )
        
        org = create_test_organization(name_suffix='membership')
        
        membership = TrustGroupMembership.objects.create(
            trust_group=group,
            organization=org,
            membership_type='member'
        )
        
        self.assertEqual(membership.trust_group, group)
        self.assertEqual(membership.organization, org)
        self.assertEqual(membership.membership_type, 'member')


class TrustLogModelTest(TestCase):
    """Test cases for TrustLog model"""
    
    def setUp(self):
        self.user = create_test_user()
        self.org1 = create_test_organization(name_suffix='org1')
        self.org2 = create_test_organization(name_suffix='org2')
        self.trust_level, _ = TrustLevel.objects.get_or_create(
            name='Test Trust',
            defaults={
                'description': 'A test trust level',
                'level': 'trusted',
                'numerical_value': 70
            }
        )
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            anonymization_level='partial',
            created_by=self.user
        )
    
    def test_create_trust_log(self):
        """Test creating a trust log entry"""
        log = TrustLog.objects.create(
            user=self.user,
            action='relationship_created',
            success=True,
            details='Created trust relationship',
            trust_relationship=self.relationship
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'relationship_created')
        self.assertTrue(log.success)
        self.assertEqual(log.trust_relationship, self.relationship)
    
    def test_trust_log_str_representation(self):
        """Test string representation of trust log"""
        log = TrustLog.objects.create(
            user=self.user,
            action='relationship_created',
            source_organization=self.org1,
            success=True,
            trust_relationship=self.relationship
        )
        expected = f"relationship_created - {self.org1.name} - SUCCESS"
        # Check that the string representation starts with the expected format
        # (excluding timestamp which varies)
        self.assertTrue(str(log).startswith(expected))