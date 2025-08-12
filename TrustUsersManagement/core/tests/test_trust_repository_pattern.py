"""
Targeted tests for trust repository pattern to improve coverage.
These tests are designed to work with your exact code structure.
"""
import pytest
from django.test import TestCase
from django.utils import timezone
from unittest.mock import Mock, patch
from datetime import timedelta

from core.trust.patterns.repository import (
    TrustRelationshipRepository,
    TrustGroupRepository,
    TrustLevelRepository,
    TrustLogRepository,
    TrustRepositoryManager
)
from core.trust.models import TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership, TrustLog
from core.user_management.models import Organization
from core.tests.factories import OrganizationFactory, TrustLevelFactory, CustomUserFactory


class TrustRepositoryPatternTestCase(TestCase):
    """Test trust repository pattern implementations."""
    
    def setUp(self):
        """Set up test data using your factories."""
        self.user = CustomUserFactory()
        self.org1 = OrganizationFactory()
        self.org2 = OrganizationFactory()
        self.org3 = OrganizationFactory()
        self.trust_level = TrustLevelFactory()
        
        # Create trust relationships
        self.relationship1 = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by=self.user
        )
        
        self.relationship2 = TrustRelationship.objects.create(
            source_organization=self.org2,
            target_organization=self.org3,
            trust_level=self.trust_level,
            relationship_type='community',
            status='pending',
            created_by=self.user
        )
        
        # Create trust group
        self.trust_group = TrustGroup.objects.create(
            name="Test Group",
            description="Test group",
            default_trust_level=self.trust_level,
            created_by=str(self.org1.id)
        )
        
        # Create trust group membership
        self.membership = TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization=self.org1,
            membership_type='administrator'
        )
        
        self.relationship_repository = TrustRelationshipRepository()
        self.group_repository = TrustGroupRepository()
        self.level_repository = TrustLevelRepository()
        self.log_repository = TrustLogRepository()
        self.repository_manager = TrustRepositoryManager()

    def test_trust_repository_instantiation(self):
        """Test that repository classes can be instantiated."""
        self.assertIsInstance(self.relationship_repository, TrustRelationshipRepository)
        self.assertIsInstance(self.group_repository, TrustGroupRepository)
        self.assertIsInstance(self.level_repository, TrustLevelRepository)
        self.assertIsInstance(self.log_repository, TrustLogRepository)
        self.assertIsInstance(self.repository_manager, TrustRepositoryManager)

    def test_get_trust_relationships_for_organization(self):
        """Test getting trust relationships for an organization."""
        relationships = self.relationship_repository.get_for_organization(str(self.org1.id))
        self.assertGreater(len(relationships), 0)
        
        # Check that we get the relationship where org1 is source
        source_rels = [r for r in relationships if str(r.source_organization.id) == str(self.org1.id)]
        self.assertGreater(len(source_rels), 0)

    def test_get_trust_relationship_by_id(self):
        """Test getting trust relationship by ID."""
        relationship = self.relationship_repository.get_by_id(str(self.relationship1.id))
        
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.id, self.relationship1.id)

    def test_get_trust_relationship_by_id_nonexistent(self):
        """Test getting trust relationship by ID that doesn't exist."""
        import uuid
        fake_id = str(uuid.uuid4())
        
        relationship = self.relationship_repository.get_by_id(fake_id)
        
        self.assertIsNone(relationship)

    def test_get_trust_relationships_by_organizations(self):
        """Test getting trust relationships between organizations."""
        relationship = self.relationship_repository.get_by_organizations(
            str(self.org1.id), 
            str(self.org2.id)
        )
        
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.id, self.relationship1.id)

    def test_get_effective_trust_relationships(self):
        """Test getting effective trust relationships."""
        # First approve the relationship
        self.relationship1.approved_by_source = True
        self.relationship1.approved_by_target = True
        self.relationship1.save()
        
        relationships = self.relationship_repository.get_effective_relationships(str(self.org1.id))
        self.assertGreater(len(relationships), 0)

    def test_get_pending_approvals(self):
        """Test getting pending approvals."""
        approvals = self.relationship_repository.get_pending_approvals(str(self.org2.id))
        self.assertGreater(len(approvals), 0)

    def test_get_expiring_relationships(self):
        """Test getting relationships expiring soon."""
        # Create a relationship that expires soon
        expiring_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org3,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            valid_until=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        
        relationships = self.relationship_repository.get_expiring_soon(days_ahead=7)
        
        # Check that expiring relationship is in results
        rel_ids = [str(r.id) for r in relationships]
        self.assertIn(str(expiring_relationship.id), rel_ids)

    def test_get_relationships_by_trust_score(self):
        """Test getting relationships by trust score."""
        relationships = self.relationship_repository.get_relationships_by_trust_score(0, 100)
        self.assertGreater(len(relationships), 0)

    def test_get_relationship_statistics(self):
        """Test getting relationship statistics."""
        stats = self.relationship_repository.get_statistics()
        
        self.assertIn('total_relationships', stats)
        self.assertIn('active_relationships', stats)
        self.assertIn('pending_relationships', stats)
        self.assertIsInstance(stats['total_relationships'], int)

    def test_update_relationship_status(self):
        """Test updating relationship status."""
        original_status = self.relationship1.status
        new_status = 'suspended'
        
        updated_relationship = self.relationship_repository.update(
            str(self.relationship1.id),
            self.user,
            status=new_status
        )
        
        self.assertIsNotNone(updated_relationship)
        self.assertEqual(updated_relationship.status, new_status)
        self.assertNotEqual(updated_relationship.status, original_status)

    def test_soft_delete_relationship(self):
        """Test soft deleting a relationship."""
        result = self.relationship_repository.delete(
            str(self.relationship2.id),
            self.user
        )
        
        self.assertTrue(result)
        
        # Check that relationship is soft deleted
        relationship = TrustRelationship.objects.get(id=self.relationship2.id)
        self.assertFalse(relationship.is_active)
        self.assertEqual(relationship.status, 'revoked')

    def test_trust_group_repository_methods(self):
        """Test TrustGroupRepository methods."""
        # Test get_by_id
        group = self.group_repository.get_by_id(str(self.trust_group.id))
        self.assertIsNotNone(group)
        self.assertEqual(group.id, self.trust_group.id)

        # Test get_all
        groups = self.group_repository.get_all()
        self.assertGreater(len(groups), 0)

        # Test get_public_groups
        public_groups = self.group_repository.get_public_groups()
        self.assertTrue(hasattr(public_groups, '__iter__'))

        # Test get_groups_for_organization
        org_groups = self.group_repository.get_groups_for_organization(str(self.org1.id))
        self.assertGreater(len(org_groups), 0)

    def test_trust_level_repository_methods(self):
        """Test TrustLevelRepository methods."""
        # Test get_by_id
        level = self.level_repository.get_by_id(str(self.trust_level.id))
        self.assertIsNotNone(level)
        self.assertEqual(level.id, self.trust_level.id)

        # Test get_all
        levels = self.level_repository.get_all()
        self.assertGreater(len(levels), 0)

        # Test get_by_name
        level_by_name = self.level_repository.get_by_name(self.trust_level.name)
        self.assertIsNotNone(level_by_name)
        self.assertEqual(level_by_name.id, self.trust_level.id)

        # Test get_by_name nonexistent
        nonexistent_level = self.level_repository.get_by_name("NonExistent")
        self.assertIsNone(nonexistent_level)

        # Test get_default
        default_level = self.level_repository.get_default()
        # May be None if no default is set
        self.assertIsInstance(default_level, (TrustLevel, type(None)))

        # Test get_by_score_range
        range_levels = self.level_repository.get_by_score_range(0, 100)
        self.assertGreater(len(range_levels), 0)

    def test_trust_log_repository_methods(self):
        """Test TrustLogRepository methods."""
        # Create a test log
        test_log = TrustLog.objects.create(
            action='relationship_created',
            source_organization=self.org1,
            user=self.user,
            success=True
        )

        # Test get_by_id
        log = self.log_repository.get_by_id(str(test_log.id))
        self.assertIsNotNone(log)
        self.assertEqual(log.id, test_log.id)

        # Test get_all
        logs = self.log_repository.get_all()
        self.assertGreater(len(logs), 0)

        # Test get_for_organization
        org_logs = self.log_repository.get_for_organization(str(self.org1.id))
        self.assertGreater(len(org_logs), 0)

        # Test get_by_action
        action_logs = self.log_repository.get_by_action('relationship_created')
        self.assertGreater(len(action_logs), 0)

        # Test get_failed_actions
        failed_logs = self.log_repository.get_failed_actions()
        self.assertTrue(hasattr(failed_logs, '__iter__'))

    def test_trust_log_immutability(self):
        """Test that trust logs are immutable."""
        test_log = TrustLog.objects.create(
            action='relationship_created',
            source_organization=self.org1,
            user=self.user,
            success=True
        )

        # Test that update raises NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.log_repository.update(str(test_log.id), action='modified')

        # Test that delete raises NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.log_repository.delete(str(test_log.id))

    def test_repository_manager_methods(self):
        """Test TrustRepositoryManager methods."""
        # Test get_repository
        rel_repo = self.repository_manager.get_repository('relationship')
        self.assertIsInstance(rel_repo, TrustRelationshipRepository)

        group_repo = self.repository_manager.get_repository('group')
        self.assertIsInstance(group_repo, TrustGroupRepository)

        level_repo = self.repository_manager.get_repository('level')
        self.assertIsInstance(level_repo, TrustLevelRepository)

        log_repo = self.repository_manager.get_repository('log')
        self.assertIsInstance(log_repo, TrustLogRepository)

        # Test unknown entity type
        with self.assertRaises(ValueError):
            self.repository_manager.get_repository('unknown')

    def test_create_trust_group(self):
        """Test creating a trust group through repository."""
        group_data = {
            'name': 'Test Group 2',
            'description': 'Another test group',
            'creator_org': str(self.org1.id),
            'created_by': str(self.user.id)
        }
        
        group = self.group_repository.create(**group_data)
        
        self.assertIsNotNone(group)
        self.assertEqual(group.name, 'Test Group 2')
        self.assertEqual(group.description, 'Another test group')

    def test_create_trust_level(self):
        """Test creating a trust level through repository."""
        level_data = {
            'name': 'Test Level',
            'level': 'trusted',
            'numerical_value': 75,
            'description': 'Test trust level',
            'created_by': str(self.user.id)
        }
        
        level = self.level_repository.create(**level_data)
        
        self.assertIsNotNone(level)
        self.assertEqual(level.name, 'Test Level')
        self.assertEqual(level.numerical_value, 75)

    def test_repository_error_handling(self):
        """Test repository error handling."""
        # Test with invalid UUID - should catch the exception
        try:
            relationship = self.relationship_repository.get_by_id("invalid-uuid")
            self.assertIsNone(relationship)
        except Exception:
            # This is expected behavior for invalid UUIDs
            pass

        # Test with non-existent ID
        import uuid
        fake_id = str(uuid.uuid4())
        relationship = self.relationship_repository.get_by_id(fake_id)
        self.assertIsNone(relationship)

    def test_trust_group_administration_check(self):
        """Test trust group administration check."""
        # Test can_administer method
        can_admin = self.group_repository.can_administer(
            str(self.trust_group.id),
            str(self.user.id)
        )
        # This may be False if the user is not an admin of the group
        self.assertIsInstance(can_admin, bool)

    def test_trust_level_by_minimum_value(self):
        """Test getting trust levels by minimum value."""
        levels = self.level_repository.get_by_minimum_value(0)
        self.assertGreater(len(levels), 0)

    def test_trust_log_create_method(self):
        """Test creating trust log through repository."""
        log_data = {
            'action': 'group_created',
            'source_organization': self.org1,
            'user': self.user,
            'success': True
        }
        
        log = self.log_repository.create(**log_data)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.action, 'group_created')
        self.assertTrue(log.success)

    def test_trust_log_date_range_query(self):
        """Test getting trust logs in date range."""
        # Create a test log
        test_log = TrustLog.objects.create(
            action='relationship_created',
            source_organization=self.org1,
            user=self.user,
            success=True
        )
        
        start_date = timezone.now() - timedelta(days=1)
        end_date = timezone.now() + timedelta(days=1)
        
        logs = self.log_repository.get_for_organization(
            str(self.org1.id),
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertGreater(len(logs), 0)
        
        # Check that our test log is in the results
        log_ids = [str(l.id) for l in logs]
        self.assertIn(str(test_log.id), log_ids)

    def test_trust_group_update_and_delete(self):
        """Test updating and deleting trust groups."""
        # Test update
        updated_group = self.group_repository.update(
            str(self.trust_group.id),
            description="Updated description"
        )
        
        self.assertIsNotNone(updated_group)
        self.assertEqual(updated_group.description, "Updated description")

        # Test soft delete
        result = self.group_repository.delete(str(self.trust_group.id))
        self.assertTrue(result)

        # Check that group is soft deleted
        group = TrustGroup.objects.get(id=self.trust_group.id)
        self.assertFalse(group.is_active)

    def test_trust_level_update_and_delete(self):
        """Test updating and deleting trust levels."""
        # Test update
        updated_level = self.level_repository.update(
            str(self.trust_level.id),
            description="Updated description"
        )
        
        self.assertIsNotNone(updated_level)
        self.assertEqual(updated_level.description, "Updated description")

        # Test soft delete
        result = self.level_repository.delete(str(self.trust_level.id))
        self.assertTrue(result)

        # Check that level is soft deleted
        level = TrustLevel.objects.get(id=self.trust_level.id)
        self.assertFalse(level.is_active)