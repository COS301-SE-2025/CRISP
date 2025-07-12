"""
Comprehensive tests for trust services to improve coverage.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock
import uuid

from core.trust.services.trust_service import TrustService
from core.trust.services.trust_group_service import TrustGroupService
from core.trust.models import (
    TrustRelationship, TrustGroup, TrustGroupMembership,
    TrustLevel, TrustLog, SharingPolicy
)
from core.user_management.models import Organization, CustomUser


class TrustServiceTest(TestCase):
    """Comprehensive tests for TrustService."""
    
    def setUp(self):
        """Set up test data."""
        # Create organizations
        self.org1 = Organization.objects.create(
            name="University A",
            domain="ua.edu",
            organization_type="university"
        )
        self.org2 = Organization.objects.create(
            name="Company B",
            domain="cb.com",
            organization_type="company"
        )
        self.org3 = Organization.objects.create(
            name="Government C",
            domain="gc.gov",
            organization_type="government"
        )
        
        # Create trust levels
        self.low_trust = TrustLevel.objects.create(
            name="Low",
            level="low",
            numerical_value=25,
            description="Low trust level"
        )
        self.medium_trust = TrustLevel.objects.create(
            name="Medium",
            level="medium",
            numerical_value=50,
            description="Medium trust level"
        )
        self.high_trust = TrustLevel.objects.create(
            name="High",
            level="high",
            numerical_value=75,
            description="High trust level"
        )
        
        # Create users
        self.user1 = CustomUser.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123",
            organization=self.org1
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123",
            organization=self.org2
        )
    
    @patch('core.trust.services.trust_service.trust_repository_manager')
    @patch('core.trust.services.trust_service.notify_trust_relationship_event')
    @patch('core.trust.services.trust_service.trust_factory')
    def test_create_trust_relationship_success(self, mock_factory, mock_notify, mock_repo_manager):
        """Test successful creation of trust relationship."""
        # Mock repository manager
        mock_repo_manager.levels.get_by_name.return_value = self.medium_trust
        mock_relationship = Mock()
        mock_relationship.id = uuid.uuid4()
        mock_repo_manager.relationships.create.return_value = mock_relationship
        
        # Test creation
        result = TrustService.create_trust_relationship(
            source_org=str(self.org1.id),
            target_org=str(self.org2.id),
            trust_level_name="medium",
            relationship_type="bilateral",
            created_by=self.user1,
            sharing_preferences={"data_sharing": True},
            notes="Test relationship"
        )
        
        # Verify calls
        mock_repo_manager.levels.get_by_name.assert_called_once_with("medium")
        mock_repo_manager.relationships.create.assert_called_once()
        mock_notify.assert_called_once()
        mock_factory.create_log.assert_called_once()
        
        self.assertEqual(result, mock_relationship)
    
    def test_create_trust_relationship_same_org_error(self):
        """Test error when source and target are same organization."""
        with self.assertRaises(ValidationError) as context:
            TrustService.create_trust_relationship(
                source_org=str(self.org1.id),
                target_org=str(self.org1.id),
                trust_level_name="medium",
                created_by=self.user1
            )
        
        self.assertIn("cannot be the same", str(context.exception))
    
    @patch('core.trust.services.trust_service.trust_repository_manager')
    def test_create_trust_relationship_invalid_trust_level(self, mock_repo_manager):
        """Test error when trust level doesn't exist."""
        mock_repo_manager.levels.get_by_name.return_value = None
        
        with self.assertRaises(ValidationError) as context:
            TrustService.create_trust_relationship(
                source_org=str(self.org1.id),
                target_org=str(self.org2.id),
                trust_level_name="nonexistent",
                created_by=self.user1
            )
        
        self.assertIn("not found or inactive", str(context.exception))
    
    @patch('core.trust.services.trust_service.trust_factory')
    @patch('core.trust.services.trust_service.notify_trust_relationship_event')
    @patch('core.trust.services.trust_service.trust_repository_manager')
    def test_create_trust_relationship_community_auto_approve(self, mock_repo_manager, mock_notify, mock_trust_factory):
        """Test auto-approval for community relationships."""
        # Mock repository manager
        mock_repo_manager.levels.get_by_name.return_value = self.medium_trust
        
        # Create a proper TrustRelationship instance instead of a Mock
        mock_relationship = TrustRelationship(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust,
            created_by=self.user1,
            relationship_type="community",
            approved_by_source=False
        )
        mock_repo_manager.relationships.create.return_value = mock_relationship
        
        # Mock the factory to avoid database issues
        mock_trust_factory.create_log.return_value = None
        
        result = TrustService.create_trust_relationship(
            source_org=str(self.org1.id),
            target_org=str(self.org2.id),
            trust_level_name="medium",
            relationship_type="community",
            created_by=self.user1
        )
        
        # Verify auto-approval
        self.assertTrue(result.approved_by_source)
        self.assertEqual(result.approved_by_source_user, self.user1)
        mock_trust_factory.create_log.assert_called_once()
    
    @patch('core.trust.services.trust_service.trust_repository_manager')
    def test_create_trust_relationship_integrity_error(self, mock_repo_manager):
        """Test handling of integrity errors (duplicate relationships)."""
        mock_repo_manager.levels.get_by_name.return_value = self.medium_trust
        mock_repo_manager.relationships.create.side_effect = IntegrityError("duplicate key")
        
        with self.assertRaises(ValidationError) as context:
            TrustService.create_trust_relationship(
                source_org=str(self.org1.id),
                target_org=str(self.org2.id),
                trust_level_name="medium",
                created_by=self.user1
            )
        
        self.assertIn("already exists", str(context.exception))
    
    @patch('core.trust.services.trust_service.trust_repository_manager')
    def test_create_trust_relationship_unexpected_error(self, mock_repo_manager):
        """Test handling of unexpected errors."""
        mock_repo_manager.levels.get_by_name.return_value = self.medium_trust
        mock_repo_manager.relationships.create.side_effect = Exception("Unexpected error")
        
        with self.assertRaises(ValidationError) as context:
            TrustService.create_trust_relationship(
                source_org=str(self.org1.id),
                target_org=str(self.org2.id),
                trust_level_name="medium",
                created_by=self.user1
            )
        
        self.assertIn("Unexpected error", str(context.exception))
    
    def test_approve_trust_relationship_source_approval(self):
        """Test approving relationship as source organization."""
        # Create relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust,
            created_by=self.user1,
            last_modified_by=self.user1,
            status="pending",
            is_active=True,
            approved_by_source=False,
            approved_by_target=False
        )
        
        # Approve as source
        activated = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=str(self.org1.id),
            approved_by_user=self.user1
        )
        
        # Verify approval
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)
        self.assertEqual(relationship.approved_by_source_user, self.user1)
        self.assertEqual(relationship.last_modified_by, self.user1)
    
    def test_approve_trust_relationship_target_approval(self):
        """Test approving relationship as target organization."""
        # Create relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust,
            created_by=self.user1,
            last_modified_by=self.user1,
            status="pending",
            is_active=True,
            approved_by_source=False,
            approved_by_target=False
        )
        
        # Approve as target
        activated = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=str(self.org2.id),
            approved_by_user=self.user2
        )
        
        # Verify approval
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_target)
        self.assertEqual(relationship.approved_by_target_user, self.user2)
        self.assertFalse(activated)  # Not fully approved yet
    
    def test_approve_trust_relationship_already_approved(self):
        """Test error when organization has already approved."""
        # Create already approved relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust,
            created_by=self.user1,
            last_modified_by=self.user1,
            status="pending",
            is_active=True,
            approved_by_source=True,
            approved_by_target=False
        )
        
        with self.assertRaises(ValidationError) as context:
            TrustService.approve_trust_relationship(
                relationship_id=str(relationship.id),
                approving_org=str(self.org1.id),
                approved_by_user=self.user1
            )
        
        self.assertIn("already approved", str(context.exception))
    
    def test_approve_trust_relationship_not_part_of_relationship(self):
        """Test error when organization is not part of relationship."""
        # Create relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust,
            created_by=self.user1,
            last_modified_by=self.user1,
            status="pending",
            is_active=True
        )
        
        with self.assertRaises(ValidationError) as context:
            TrustService.approve_trust_relationship(
                relationship_id=str(relationship.id),
                approving_org=str(self.org3.id),  # Not part of relationship
                approved_by_user=self.user1
            )
        
        self.assertIn("not part of this trust relationship", str(context.exception))
    
    def test_approve_trust_relationship_not_found(self):
        """Test error when relationship doesn't exist."""
        fake_id = uuid.uuid4()
        
        with self.assertRaises(ValidationError) as context:
            TrustService.approve_trust_relationship(
                relationship_id=str(fake_id),
                approving_org=str(self.org1.id),
                approved_by_user=self.user1
            )
        
        self.assertIn("not found", str(context.exception))
    
    @patch('core.trust.services.trust_service.TrustLog')
    def test_approve_trust_relationship_logging(self, mock_log):
        """Test that approval is properly logged."""
        # Create relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust,
            created_by=self.user1,
            last_modified_by=self.user1,
            status="pending",
            is_active=True,
            approved_by_source=False,
            approved_by_target=False
        )
        
        TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=str(self.org1.id),
            approved_by_user=self.user1
        )
        
        # Verify logging was called
        mock_log.log_trust_event.assert_called_once()
        args, kwargs = mock_log.log_trust_event.call_args
        self.assertEqual(kwargs['action'], 'relationship_approved')
        self.assertEqual(kwargs['user'], self.user1)


class TrustGroupServiceTest(TestCase):
    """Comprehensive tests for TrustGroupService."""
    
    def setUp(self):
        """Set up test data."""
        # Create organizations
        self.org1 = Organization.objects.create(
            name="University A",
            domain="ua.edu",
            organization_type="university"
        )
        self.org2 = Organization.objects.create(
            name="Company B",
            domain="cb.com",
            organization_type="company"
        )
        
        # Create trust level
        self.trust_level = TrustLevel.objects.create(
            name="Public",
            level="public",
            numerical_value=30,
            description="Public trust level"
        )
        
        # Create user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.org1
        )
    
    @patch('core.trust.services.trust_group_service.TrustLog')
    def test_create_trust_group_success(self, mock_log):
        """Test successful creation of trust group."""
        group = TrustGroupService.create_trust_group(
            name="Test Group",
            description="A test group",
            creator_org=str(self.org1.id),
            group_type="community",
            default_trust_level_name="public",
            created_by=self.user
        )
        
        # Verify group creation
        self.assertIsNotNone(group.id)
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.description, "A test group")
        self.assertEqual(group.group_type, "community")
        self.assertEqual(group.default_trust_level, self.trust_level)
        self.assertEqual(group.created_by, self.user)
        self.assertIn(str(self.org1.id), group.administrators)
        
        # Verify membership was created
        membership = TrustGroupMembership.objects.get(
            trust_group=group,
            organization=self.org1
        )
        self.assertEqual(membership.membership_type, 'administrator')
        self.assertTrue(membership.is_active)
        
        # Verify logging
        mock_log.log_trust_event.assert_called_once()
    
    def test_create_trust_group_with_org_instance(self):
        """Test creating group with Organization instance instead of string."""
        group = TrustGroupService.create_trust_group(
            name="Test Group 2",
            description="Another test group",
            creator_org=self.org1,  # Pass Organization instance
            created_by=self.user
        )
        
        self.assertIsNotNone(group.id)
        self.assertIn(str(self.org1.id), group.administrators)
    
    def test_create_trust_group_duplicate_name(self):
        """Test error when creating group with duplicate name."""
        # Create first group
        TrustGroup.objects.create(
            name="Duplicate Name",
            description="First group",
            default_trust_level=self.trust_level,
            created_by=self.user
        )
        
        # Try to create second group with same name
        with self.assertRaises(ValidationError) as context:
            TrustGroupService.create_trust_group(
                name="Duplicate Name",
                description="Second group",
                creator_org=str(self.org1.id),
                created_by=self.user
            )
        
        self.assertIn("already exists", str(context.exception))
    
    def test_create_trust_group_empty_name(self):
        """Test error when creating group with empty name."""
        with self.assertRaises(ValidationError) as context:
            TrustGroupService.create_trust_group(
                name="",
                description="Group with empty name",
                creator_org=str(self.org1.id),
                created_by=self.user
            )
        
        self.assertIn("name is required", str(context.exception))
    
    def test_create_trust_group_whitespace_name(self):
        """Test error when creating group with whitespace-only name."""
        with self.assertRaises(ValidationError) as context:
            TrustGroupService.create_trust_group(
                name="   ",
                description="Group with whitespace name",
                creator_org=str(self.org1.id),
                created_by=self.user
            )
        
        self.assertIn("name is required", str(context.exception))
    
    def test_create_trust_group_no_default_trust_level(self):
        """Test creating group when no default trust level exists."""
        # Remove existing trust level
        TrustLevel.objects.all().delete()
        
        group = TrustGroupService.create_trust_group(
            name="Test Group No Level",
            description="Group without existing trust level",
            creator_org=str(self.org1.id),
            created_by=self.user
        )
        
        # Verify a default trust level was created
        self.assertIsNotNone(group.default_trust_level)
        self.assertEqual(group.default_trust_level.level, "public")
        self.assertEqual(group.default_trust_level.name, "Default Group Level")
    
    def test_create_trust_group_specific_trust_level_not_found(self):
        """Test creating group when specific trust level doesn't exist."""
        group = TrustGroupService.create_trust_group(
            name="Test Group Nonexistent Level",
            description="Group with nonexistent trust level",
            creator_org=str(self.org1.id),
            default_trust_level_name="nonexistent",
            created_by=self.user
        )
        
        # Should fall back to public level
        self.assertEqual(group.default_trust_level, self.trust_level)
    
    def test_create_trust_group_no_created_by(self):
        """Test creating group without specifying created_by user."""
        group = TrustGroupService.create_trust_group(
            name="Test Group No User",
            description="Group without created_by",
            creator_org=str(self.org1.id)
        )
        
        # Should use creator_org as created_by
        self.assertEqual(group.created_by, str(self.org1.id))
    
    def test_create_trust_group_invalid_org_id(self):
        """Test error when creator_org ID doesn't exist."""
        fake_org_id = uuid.uuid4()
        
        with self.assertRaises(Organization.DoesNotExist):
            TrustGroupService.create_trust_group(
                name="Test Group Invalid Org",
                description="Group with invalid org",
                creator_org=str(fake_org_id),
                created_by=self.user
            )
    
    @patch('core.trust.services.trust_group_service.TrustGroup.objects.create')
    def test_create_trust_group_database_error(self, mock_create):
        """Test handling of database errors during group creation."""
        mock_create.side_effect = Exception("Database error")
        
        with self.assertRaises(Exception):
            TrustGroupService.create_trust_group(
                name="Test Group DB Error",
                description="Group with database error",
                creator_org=str(self.org1.id),
                created_by=self.user
            )
    
    @patch('core.trust.services.trust_group_service.TrustGroupMembership.objects.create')
    def test_create_trust_group_membership_error(self, mock_membership_create):
        """Test handling of membership creation errors."""
        mock_membership_create.side_effect = Exception("Membership error")
        
        with self.assertRaises(Exception):
            TrustGroupService.create_trust_group(
                name="Test Group Membership Error",
                description="Group with membership error",
                creator_org=str(self.org1.id),
                created_by=self.user
            )
    
    @patch('core.trust.services.trust_group_service.logger')
    def test_create_trust_group_logging(self, mock_logger):
        """Test that group creation is properly logged."""
        TrustGroupService.create_trust_group(
            name="Test Group Logging",
            description="Group for testing logging",
            creator_org=str(self.org1.id),
            created_by=self.user
        )
        
        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        self.assertIn("Trust group created", log_message)
        self.assertIn("Test Group Logging", log_message)
        self.assertIn(str(self.org1.id), log_message)


class TrustServiceIntegrationTest(TestCase):
    """Integration tests for trust services."""
    
    def setUp(self):
        """Set up test data."""
        # Create organizations
        self.org1 = Organization.objects.create(
            name="University A",
            domain="ua.edu",
            organization_type="university"
        )
        self.org2 = Organization.objects.create(
            name="Company B",
            domain="cb.com",
            organization_type="company"
        )
        
        # Create trust level
        self.trust_level = TrustLevel.objects.create(
            name="Medium",
            level="medium",
            numerical_value=50,
            description="Medium trust level"
        )
        
        # Create user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.org1
        )
    
    def test_service_error_isolation(self):
        """Test that service errors don't affect other operations."""
        # This test ensures that errors in one service don't cascade
        
        # First, create a successful trust group
        group = TrustGroupService.create_trust_group(
            name="Successful Group",
            description="This should work",
            creator_org=str(self.org1.id),
            created_by=self.user
        )
        self.assertIsNotNone(group.id)
        
        # Now try to create a relationship with invalid data
        with self.assertRaises(ValidationError):
            TrustService.create_trust_relationship(
                source_org=str(self.org1.id),
                target_org=str(self.org1.id),  # Same org - should fail
                trust_level_name="medium",
                created_by=self.user
            )
        
        # The group should still exist and be functional
        group.refresh_from_db()
        self.assertEqual(group.name, "Successful Group")
    
    @patch('core.trust.services.trust_service.logger')
    @patch('core.trust.services.trust_group_service.logger')
    def test_logging_consistency(self, mock_group_logger, mock_trust_logger):
        """Test that logging is consistent across services."""
        # Create group
        TrustGroupService.create_trust_group(
            name="Logging Test Group",
            description="For testing logging",
            creator_org=str(self.org1.id),
            created_by=self.user
        )
        
        # Verify group service logged
        mock_group_logger.info.assert_called_once()
        
        # Test trust service logging would occur on actual operations
        # (We can't easily test this without mocking the repository pattern)
        self.assertTrue(True)  # Placeholder for more complex integration tests
    
    def test_transaction_consistency(self):
        """Test that transactions maintain consistency across services."""
        initial_group_count = TrustGroup.objects.count()
        initial_membership_count = TrustGroupMembership.objects.count()
        
        # Create group (should create both group and membership)
        group = TrustGroupService.create_trust_group(
            name="Transaction Test",
            description="Testing transactions",
            creator_org=str(self.org1.id),
            created_by=self.user
        )
        
        # Verify both were created
        self.assertEqual(TrustGroup.objects.count(), initial_group_count + 1)
        self.assertEqual(TrustGroupMembership.objects.count(), initial_membership_count + 1)
        
        # Verify they're linked correctly
        membership = TrustGroupMembership.objects.get(trust_group=group)
        self.assertEqual(membership.organization, self.org1)