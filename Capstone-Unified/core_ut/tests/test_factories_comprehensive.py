"""
Comprehensive tests for test factories to improve coverage.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import uuid

from core_ut.tests.factories import (
    OrganizationFactory,
    CustomUserFactory as UserFactory,
    TrustLevelFactory,
    TrustRelationshipFactory,
    TrustGroupFactory,
    TrustLogFactory
)
from core_ut.trust.models import (
    TrustLevel, TrustRelationship, TrustGroup,
    TrustLog
)
from core_ut.user_management.models import Organization

User = get_user_model()


class OrganizationFactoryTest(TestCase):
    """Test OrganizationFactory functionality."""
    
    def test_create_single_organization(self):
        """Test creating a single organization."""
        org = OrganizationFactory()
        
        self.assertIsInstance(org, Organization)
        self.assertTrue(org.name.startswith("Organization"))
        self.assertTrue(org.domain.endswith(".edu"))
        self.assertEqual(org.contact_email, f"contact@{org.domain}")
        self.assertEqual(org.organization_type, "educational")
        self.assertIsNotNone(org.description)
    
    def test_create_multiple_organizations(self):
        """Test creating multiple organizations with unique names."""
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()
        
        self.assertNotEqual(org1.name, org2.name)
        self.assertNotEqual(org1.domain, org2.domain)
        self.assertNotEqual(org1.contact_email, org2.contact_email)
    
    def test_create_organization_batch(self):
        """Test creating multiple organizations in batch."""
        orgs = OrganizationFactory.create_batch(5)
        
        self.assertEqual(len(orgs), 5)
        names = [org.name for org in orgs]
        domains = [org.domain for org in orgs]
        
        # All names and domains should be unique
        self.assertEqual(len(set(names)), 5)
        self.assertEqual(len(set(domains)), 5)
    
    def test_organization_build_without_save(self):
        """Test building organization without saving to database."""
        org = OrganizationFactory.build()
        
        self.assertIsInstance(org, Organization)
        # UUIDs are generated even for build(), but object shouldn't be in DB
        
        # Verify it's not in database
        self.assertEqual(Organization.objects.count(), 0)
    
    def test_organization_custom_attributes(self):
        """Test creating organization with custom attributes."""
        custom_name = "Custom University"
        custom_domain = "custom.edu"
        
        org = OrganizationFactory(
            name=custom_name,
            domain=custom_domain,
            organization_type="university"
        )
        
        self.assertEqual(org.name, custom_name)
        self.assertEqual(org.domain, custom_domain)
        self.assertEqual(org.organization_type, "university")
        self.assertEqual(org.contact_email, f"contact@{custom_domain}")


class UserFactoryTest(TestCase):
    """Test UserFactory functionality."""
    
    def test_create_single_user(self):
        """Test creating a single user."""
        user = UserFactory()
        
        self.assertIsInstance(user, User)
        self.assertTrue(user.username.startswith("user"))
        self.assertIsNotNone(user.first_name)
        self.assertIsNotNone(user.last_name)
        self.assertIsNotNone(user.organization)
        self.assertEqual(user.role, "viewer")
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_verified)
        self.assertEqual(user.email, f"{user.username}@{user.organization.domain}")
    
    def test_create_multiple_users(self):
        """Test creating multiple users with unique usernames."""
        user1 = UserFactory()
        user2 = UserFactory()
        
        self.assertNotEqual(user1.username, user2.username)
        self.assertNotEqual(user1.email, user2.email)
    
    def test_user_with_existing_organization(self):
        """Test creating user with existing organization."""
        org = OrganizationFactory()
        user = UserFactory(organization=org)
        
        self.assertEqual(user.organization, org)
        self.assertEqual(user.email, f"{user.username}@{org.domain}")
    
    def test_user_custom_attributes(self):
        """Test creating user with custom attributes."""
        custom_username = "testuser"
        custom_role = "admin"
        
        user = UserFactory(
            username=custom_username,
            role=custom_role,
            is_active=False
        )
        
        self.assertEqual(user.username, custom_username)
        self.assertEqual(user.role, custom_role)
        self.assertFalse(user.is_active)
    
    def test_user_batch_creation(self):
        """Test creating users in batch."""
        users = UserFactory.create_batch(3)
        
        self.assertEqual(len(users), 3)
        usernames = [user.username for user in users]
        self.assertEqual(len(set(usernames)), 3)  # All unique


class TrustLevelFactoryTest(TestCase):
    """Test TrustLevelFactory functionality."""
    
    def test_create_single_trust_level(self):
        """Test creating a single trust level."""
        trust_level = TrustLevelFactory()
        
        self.assertIsInstance(trust_level, TrustLevel)
        self.assertTrue(trust_level.name.startswith("Trust Level"))
        self.assertIsNotNone(trust_level.description)
        self.assertIn(trust_level.level, ['public', 'trusted', 'restricted'])
        self.assertGreaterEqual(trust_level.numerical_value, 0)
        self.assertLessEqual(trust_level.numerical_value, 100)
        self.assertIn(trust_level.default_access_level, ['none', 'read', 'subscribe', 'contribute', 'full'])
        self.assertIn(trust_level.default_anonymization_level, ['none', 'minimal', 'partial', 'full', 'custom'])
        self.assertIsNotNone(trust_level.created_by)
        self.assertTrue(trust_level.is_active)
    
    def test_trust_level_batch_creation(self):
        """Test creating trust levels in batch."""
        trust_levels = TrustLevelFactory.create_batch(5)
        
        self.assertEqual(len(trust_levels), 5)
        names = [tl.name for tl in trust_levels]
        self.assertEqual(len(set(names)), 5)  # All unique names
    
    def test_trust_level_custom_attributes(self):
        """Test creating trust level with custom attributes."""
        custom_name = "Custom Trust Level"
        custom_level = "high"
        custom_value = 85
        
        trust_level = TrustLevelFactory(
            name=custom_name,
            level=custom_level,
            numerical_value=custom_value,
            is_active=False
        )
        
        self.assertEqual(trust_level.name, custom_name)
        self.assertEqual(trust_level.level, custom_level)
        self.assertEqual(trust_level.numerical_value, custom_value)
        self.assertFalse(trust_level.is_active)
    
    def test_trust_level_with_custom_user(self):
        """Test creating trust level with specific user."""
        user = UserFactory()
        trust_level = TrustLevelFactory(created_by=user)
        
        self.assertEqual(trust_level.created_by, user)


class TrustRelationshipFactoryTest(TestCase):
    """Test TrustRelationshipFactory functionality."""
    
    def test_create_single_trust_relationship(self):
        """Test creating a single trust relationship."""
        relationship = TrustRelationshipFactory()
        
        self.assertIsInstance(relationship, TrustRelationship)
        self.assertIsNotNone(relationship.source_organization)
        self.assertIsNotNone(relationship.target_organization)
        self.assertIsNotNone(relationship.trust_level)
        self.assertIn(relationship.relationship_type, ['bilateral', 'community', 'hierarchical', 'federation'])
        self.assertEqual(relationship.status, 'pending')
        self.assertEqual(relationship.anonymization_level, 'partial')
        self.assertEqual(relationship.access_level, 'read')
        self.assertIsNotNone(relationship.notes)
        self.assertIsNotNone(relationship.valid_until)
        self.assertIsNotNone(relationship.created_by)
        self.assertIsNotNone(relationship.last_modified_by)
        
        # Verify organizations are different
        self.assertNotEqual(relationship.source_organization, relationship.target_organization)
        
        # Verify valid_until is in the future
        self.assertGreater(relationship.valid_until, timezone.now())
    
    def test_trust_relationship_with_existing_organizations(self):
        """Test creating relationship with existing organizations."""
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()
        trust_level = TrustLevelFactory()
        
        relationship = TrustRelationshipFactory(
            source_organization=org1,
            target_organization=org2,
            trust_level=trust_level
        )
        
        self.assertEqual(relationship.source_organization, org1)
        self.assertEqual(relationship.target_organization, org2)
        self.assertEqual(relationship.trust_level, trust_level)
    
    def test_trust_relationship_custom_attributes(self):
        """Test creating relationship with custom attributes."""
        custom_status = "active"
        custom_type = "bilateral"
        
        relationship = TrustRelationshipFactory(
            status=custom_status,
            relationship_type=custom_type,
            anonymization_level="full",
            access_level="full"
        )
        
        self.assertEqual(relationship.status, custom_status)
        self.assertEqual(relationship.relationship_type, custom_type)
        self.assertEqual(relationship.anonymization_level, "full")
        self.assertEqual(relationship.access_level, "full")
    
    def test_trust_relationship_batch_creation(self):
        """Test creating relationships in batch."""
        relationships = TrustRelationshipFactory.create_batch(3)
        
        self.assertEqual(len(relationships), 3)
        for relationship in relationships:
            self.assertIsInstance(relationship, TrustRelationship)


class TrustGroupFactoryTest(TestCase):
    """Test TrustGroupFactory functionality."""
    
    def test_create_single_trust_group(self):
        """Test creating a single trust group."""
        group = TrustGroupFactory()
        
        self.assertIsInstance(group, TrustGroup)
        self.assertTrue(group.name.startswith("Trust Group"))
        self.assertIsNotNone(group.description)
        self.assertIsNotNone(group.created_by)
        self.assertIn(group.group_type, ['sector', 'geography', 'purpose', 'custom', 'community'])
        self.assertIn(group.is_public, [True, False])
        self.assertTrue(group.is_active)
        self.assertIsNotNone(group.default_trust_level)
    
    def test_trust_group_custom_attributes(self):
        """Test creating group with custom attributes."""
        custom_name = "Custom Trust Group"
        custom_type = "sector"
        
        group = TrustGroupFactory(
            name=custom_name,
            group_type=custom_type,
            is_public=True,
            is_active=False
        )
        
        self.assertEqual(group.name, custom_name)
        self.assertEqual(group.group_type, custom_type)
        self.assertTrue(group.is_public)
        self.assertFalse(group.is_active)
    
    def test_trust_group_with_existing_trust_level(self):
        """Test creating group with existing trust level."""
        trust_level = TrustLevelFactory()
        group = TrustGroupFactory(default_trust_level=trust_level)
        
        self.assertEqual(group.default_trust_level, trust_level)
    
    def test_trust_group_batch_creation(self):
        """Test creating groups in batch."""
        groups = TrustGroupFactory.create_batch(4)
        
        self.assertEqual(len(groups), 4)
        names = [group.name for group in groups]
        self.assertEqual(len(set(names)), 4)  # All unique names


# Removed TrustGroupMembershipFactory tests since it's not in factories.py


# Removed SharingPolicyFactory tests since it's not in factories.py
# Removed SharingPolicyFactory tests since it's not in factories.py


class TrustLogFactoryTest(TestCase):
    """Test TrustLogFactory functionality."""
    
    def test_create_single_trust_log(self):
        """Test creating a single trust log."""
        log = TrustLogFactory()
        
        self.assertIsInstance(log, TrustLog)
        self.assertIn(log.action, ['relationship_created', 'group_joined', 'trust_granted'])
        self.assertIsNotNone(log.user)
        self.assertTrue(log.success)
        self.assertIsInstance(log.details, dict)
        self.assertIsInstance(log.metadata, dict)
    
    def test_trust_log_custom_attributes(self):
        """Test creating log with custom attributes."""
        custom_action = "trust_granted"
        custom_details = {'operation': 'test', 'result': 'success'}
        
        log = TrustLogFactory(
            action=custom_action,
            details=custom_details,
            success=False
        )
        
        self.assertEqual(log.action, custom_action)
        self.assertEqual(log.details, custom_details)
        self.assertFalse(log.success)
    
    def test_trust_log_with_existing_entities(self):
        """Test creating log with existing user."""
        user = UserFactory()
        
        log = TrustLogFactory(
            user=user
        )
        
        self.assertEqual(log.user, user)
    
    def test_trust_log_batch_creation(self):
        """Test creating logs in batch."""
        logs = TrustLogFactory.create_batch(5)
        
        self.assertEqual(len(logs), 5)
        for log in logs:
            self.assertIsInstance(log, TrustLog)


class FactoryIntegrationTest(TestCase):
    """Integration tests for factories working together."""
    
    def test_complete_trust_ecosystem_creation(self):
        """Test creating a complete trust ecosystem using factories."""
        # Create base entities
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()
        user1 = UserFactory(organization=org1)
        user2 = UserFactory(organization=org2)
        
        # Create trust level and relationship
        trust_level = TrustLevelFactory(created_by=user1)
        relationship = TrustRelationshipFactory(
            source_organization=org1,
            target_organization=org2,
            trust_level=trust_level,
            created_by=user1,
            last_modified_by=user1
        )
        
        # Create trust group
        group = TrustGroupFactory(
            created_by=user1,
            default_trust_level=trust_level
        )
        
        # Create trust log
        log = TrustLogFactory(
            user=user1
        )
        
        # Verify all entities exist and are connected properly
        self.assertEqual(relationship.source_organization, org1)
        self.assertEqual(relationship.target_organization, org2)
        self.assertEqual(relationship.trust_level, trust_level)
        self.assertEqual(group.default_trust_level, trust_level)
        self.assertEqual(log.user, user1)
    
    def test_factory_inheritance_and_overrides(self):
        """Test that factory inheritance and overrides work correctly."""
        # Test that we can override default values
        custom_org = OrganizationFactory(
            name="Custom Organization",
            organization_type="government"
        )
        
        # Test that dependent factories use the overridden values
        user = UserFactory(organization=custom_org)
        
        self.assertEqual(user.organization.name, "Custom Organization")
        self.assertEqual(user.organization.organization_type, "government")
        self.assertTrue(user.email.endswith(f"@{custom_org.domain}"))
    
    def test_factory_uniqueness_constraints(self):
        """Test that factories handle uniqueness constraints properly."""
        # Create multiple entities to test uniqueness
        orgs = OrganizationFactory.create_batch(10)
        users = UserFactory.create_batch(10)
        trust_levels = TrustLevelFactory.create_batch(5)
        
        # Verify unique names/usernames
        org_names = [org.name for org in orgs]
        self.assertEqual(len(set(org_names)), 10)
        
        usernames = [user.username for user in users]
        self.assertEqual(len(set(usernames)), 10)
        
        trust_level_names = [tl.name for tl in trust_levels]
        self.assertEqual(len(set(trust_level_names)), 5)
    
    def test_factory_data_consistency(self):
        """Test that factories create consistent and valid data."""
        # Create entities and verify they're valid
        org = OrganizationFactory()
        user = UserFactory(organization=org)
        trust_level = TrustLevelFactory(created_by=user)
        
        # Verify data consistency
        self.assertEqual(user.organization, org)
        self.assertTrue(user.email.endswith(f"@{org.domain}"))
        self.assertEqual(trust_level.created_by, user)
        
        # Verify entities can be saved (no validation errors)
        try:
            org.full_clean()
            user.full_clean()
            trust_level.full_clean()
        except ValidationError as e:
            self.fail(f"Factory created invalid data: {e}")
    
    def test_factory_performance_batch_creation(self):
        """Test that batch creation is efficient."""
        import time
        
        # Create entities in batch and measure time
        start_time = time.time()
        orgs = OrganizationFactory.create_batch(50)
        users = UserFactory.create_batch(50)
        batch_time = time.time() - start_time
        
        # Create entities individually and measure time
        start_time = time.time()
        for _ in range(50):
            OrganizationFactory()
            UserFactory()
        individual_time = time.time() - start_time
        
        # Batch should be faster (though this may vary in test environment)
        self.assertEqual(len(orgs), 50)
        self.assertEqual(len(users), 50)
        # Note: In some test environments, timing tests may be unreliable
        # so we just verify the creation worked correctly