"""
Comprehensive tests for trust repository patterns.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock
import uuid

from core_ut.trust.patterns.repository.trust_repository import (
    BaseRepository, 
    TrustRelationshipRepository,
    TrustGroupRepository,
    TrustLevelRepository
)
from core_ut.trust.models import (
    TrustRelationship, TrustGroup, TrustGroupMembership, 
    TrustLevel, TrustLog, SharingPolicy
)
from core_ut.user_management.models import Organization, CustomUser


class BaseRepositoryTest(TestCase):
    """Test the abstract BaseRepository class."""
    
    def setUp(self):
        """Set up test data."""
        # Create a concrete implementation for testing
        class ConcreteRepository(BaseRepository):
            def get_by_id(self, entity_id):
                return self.model_class.objects.get(id=entity_id)
            
            def get_all(self, include_inactive=False):
                queryset = self.model_class.objects.all()
                if not include_inactive:
                    queryset = queryset.filter(is_active=True)
                return queryset
            
            def create(self, **kwargs):
                return self.model_class.objects.create(**kwargs)
            
            def update(self, entity_id, **kwargs):
                obj = self.model_class.objects.get(id=entity_id)
                for field, value in kwargs.items():
                    setattr(obj, field, value)
                obj.save()
                return obj
            
            def delete(self, entity_id):
                self.model_class.objects.get(id=entity_id).delete()
                return True
        
        self.repository = ConcreteRepository(TrustLevel)
        
        # Create test data
        self.trust_level = TrustLevel.objects.create(
            name="Test Level",
            level="test",
            numerical_value=50,
            description="Test description"
        )
    
    def test_model_class_initialization(self):
        """Test that repository is initialized with correct model class."""
        self.assertEqual(self.repository.model_class, TrustLevel)
    
    def test_exists_method(self):
        """Test the exists method."""
        self.assertTrue(self.repository.exists(name="Test Level"))
        self.assertFalse(self.repository.exists(name="Nonexistent"))
    
    def test_count_method(self):
        """Test the count method."""
        self.assertEqual(self.repository.count(), 1)
        self.assertEqual(self.repository.count(name="Test Level"), 1)
        self.assertEqual(self.repository.count(name="Nonexistent"), 0)
    
    def test_abstract_methods_implemented(self):
        """Test that abstract methods can be called on concrete implementation."""
        # These should work without raising NotImplementedError
        result = self.repository.get_by_id(self.trust_level.id)
        self.assertEqual(result, self.trust_level)
        
        all_items = self.repository.get_all()
        self.assertIn(self.trust_level, all_items)


class TrustRelationshipRepositoryTest(TestCase):
    """Test TrustRelationshipRepository functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = TrustRelationshipRepository()
        
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
        
        # Create user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.org1
        )
        
        # Create sample relationships
        self.relationship1 = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.medium_trust,
            created_by=self.user,
            last_modified_by=self.user,
            status="active",
            is_active=True
        )
        
        self.relationship2 = TrustRelationship.objects.create(
            source_organization=self.org2,
            target_organization=self.org3,
            trust_level=self.high_trust,
            created_by=self.user,
            last_modified_by=self.user,
            status="pending",
            is_active=True
        )
    
    def test_initialization(self):
        """Test repository initialization."""
        self.assertEqual(self.repository.model_class, TrustRelationship)
    
    def test_get_by_id_success(self):
        """Test getting relationship by ID."""
        result = self.repository.get_by_id(self.relationship1.id)
        self.assertEqual(result, self.relationship1)
        self.assertIsNotNone(result.trust_level)  # Test select_related
    
    def test_get_by_id_not_found(self):
        """Test getting relationship by non-existent ID."""
        fake_id = uuid.uuid4()
        result = self.repository.get_by_id(fake_id)
        self.assertIsNone(result)
    
    def test_get_all_active_only(self):
        """Test getting all active relationships."""
        # Create inactive relationship
        inactive_rel = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org3,
            trust_level=self.low_trust,
            created_by=self.user,
            last_modified_by=self.user,
            is_active=False
        )
        
        results = self.repository.get_all(include_inactive=False)
        self.assertEqual(results.count(), 2)
        self.assertNotIn(inactive_rel, results)
    
    def test_get_all_include_inactive(self):
        """Test getting all relationships including inactive."""
        # Create inactive relationship
        inactive_rel = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org3,
            trust_level=self.low_trust,
            created_by=self.user,
            last_modified_by=self.user,
            is_active=False
        )
        
        results = self.repository.get_all(include_inactive=True)
        self.assertEqual(results.count(), 3)
        self.assertIn(inactive_rel, results)
    
    def test_create_success(self):
        """Test creating new relationship."""
        new_relationship = self.repository.create(
            source_org=self.org1,
            target_org=self.org3,
            trust_level=self.high_trust,
            created_by=self.user,
            relationship_type="bilateral"
        )
        
        self.assertIsNotNone(new_relationship.id)
        self.assertEqual(new_relationship.source_organization, self.org1)
        self.assertEqual(new_relationship.target_organization, self.org3)
        self.assertEqual(new_relationship.trust_level, self.high_trust)
        self.assertEqual(new_relationship.created_by, self.user)
        self.assertEqual(new_relationship.last_modified_by, self.user)
    
    def test_create_duplicate_validation(self):
        """Test validation prevents duplicate active relationships."""
        with self.assertRaises(ValidationError) as context:
            self.repository.create(
                source_org=self.org1,
                target_org=self.org2,
                trust_level=self.high_trust,
                created_by=self.user
            )
        
        self.assertIn("already exists", str(context.exception))
    
    @patch('core.trust.patterns.repository.trust_repository.logger')
    def test_create_with_logging(self, mock_logger):
        """Test that creation logs appropriate messages."""
        self.repository.create(
            source_org=self.org1,
            target_org=self.org3,
            trust_level=self.high_trust,
            created_by=self.user
        )
        
        mock_logger.info.assert_called_once()
        self.assertIn("Trust relationship created", mock_logger.info.call_args[0][0])
    
    def test_create_exception_handling(self):
        """Test exception handling during creation."""
        with patch.object(self.repository.model_class.objects, 'create') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            with self.assertRaises(Exception):
                self.repository.create(
                    source_org=self.org1,
                    target_org=self.org3,
                    trust_level=self.high_trust,
                    created_by=self.user
                )
    
    def test_update_success(self):
        """Test updating relationship."""
        updated = self.repository.update(
            self.relationship1.id,
            self.user,
            status="approved",
            notes="Updated for testing"
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "approved")
        self.assertEqual(updated.last_modified_by, self.user)
    
    def test_update_not_found(self):
        """Test updating non-existent relationship."""
        fake_id = uuid.uuid4()
        result = self.repository.update(fake_id, self.user, status="updated")
        self.assertIsNone(result)
    
    def test_update_invalid_field(self):
        """Test updating with invalid field name."""
        updated = self.repository.update(
            self.relationship1.id,
            self.user,
            invalid_field="should_be_ignored",
            status="valid_update"
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "valid_update")
        self.assertFalse(hasattr(updated, 'invalid_field'))
    
    def test_delete_success(self):
        """Test soft deleting relationship."""
        result = self.repository.delete(self.relationship1.id, self.user)
        self.assertTrue(result)
        
        # Verify soft delete
        self.relationship1.refresh_from_db()
        self.assertFalse(self.relationship1.is_active)
        self.assertEqual(self.relationship1.status, 'revoked')
        self.assertIsNotNone(self.relationship1.revoked_at)
        self.assertEqual(self.relationship1.revoked_by, self.user)
    
    def test_delete_not_found(self):
        """Test deleting non-existent relationship."""
        fake_id = uuid.uuid4()
        result = self.repository.delete(fake_id)
        self.assertFalse(result)
    
    def test_delete_without_user(self):
        """Test deleting without specifying user."""
        result = self.repository.delete(self.relationship1.id)
        self.assertTrue(result)
        
        self.relationship1.refresh_from_db()
        self.assertFalse(self.relationship1.is_active)
        self.assertIsNone(self.relationship1.revoked_by)
    
    def test_get_by_organizations_found(self):
        """Test getting relationship between specific organizations."""
        result = self.repository.get_by_organizations(self.org1, self.org2)
        self.assertEqual(result, self.relationship1)
    
    def test_get_by_organizations_not_found(self):
        """Test getting relationship between organizations with no relationship."""
        result = self.repository.get_by_organizations(self.org1, self.org3)
        self.assertIsNone(result)
    
    def test_get_by_organizations_include_inactive(self):
        """Test getting relationship including inactive ones."""
        # Make relationship inactive
        self.relationship1.is_active = False
        self.relationship1.save()
        
        # Should not find with active_only=True (default)
        result = self.repository.get_by_organizations(self.org1, self.org2, active_only=True)
        self.assertIsNone(result)
        
        # Should find with active_only=False
        result = self.repository.get_by_organizations(self.org1, self.org2, active_only=False)
        self.assertEqual(result, self.relationship1)
    
    def test_get_for_organization(self):
        """Test getting all relationships for an organization."""
        results = self.repository.get_for_organization(self.org2)
        self.assertEqual(results.count(), 2)  # org2 is in both relationships
    
    def test_get_for_organization_with_type_filter(self):
        """Test getting relationships with type filter."""
        # Update relationship types
        self.relationship1.relationship_type = "bilateral"
        self.relationship1.save()
        self.relationship2.relationship_type = "unilateral"
        self.relationship2.save()
        
        results = self.repository.get_for_organization(
            self.org2, 
            relationship_type="bilateral"
        )
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.relationship1)
    
    def test_get_by_trust_level(self):
        """Test getting relationships by trust level."""
        results = self.repository.get_by_trust_level(self.medium_trust)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.relationship1)
    
    def test_get_effective_relationships(self):
        """Test getting effective relationships."""
        # Make relationship1 effective
        self.relationship1.status = "active"
        self.relationship1.approved_by_source = True
        self.relationship1.approved_by_target = True
        self.relationship1.valid_from = timezone.now() - timedelta(days=1)
        self.relationship1.save()
        
        results = self.repository.get_effective_relationships(self.org1)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.relationship1)
    
    def test_get_effective_relationships_with_expiry(self):
        """Test effective relationships with expiry dates."""
        # Set expiry in future
        self.relationship1.status = "active"
        self.relationship1.approved_by_source = True
        self.relationship1.approved_by_target = True
        self.relationship1.valid_from = timezone.now() - timedelta(days=1)
        self.relationship1.valid_until = timezone.now() + timedelta(days=1)
        self.relationship1.save()
        
        results = self.repository.get_effective_relationships(self.org1)
        self.assertEqual(results.count(), 1)
        
        # Set expiry in past
        self.relationship1.valid_until = timezone.now() - timedelta(days=1)
        self.relationship1.save()
        
        results = self.repository.get_effective_relationships(self.org1)
        self.assertEqual(results.count(), 0)
    
    def test_get_pending_approvals(self):
        """Test getting relationships pending approval."""
        # Set up pending relationship
        self.relationship2.status = "pending"
        self.relationship2.approved_by_source = False
        self.relationship2.approved_by_target = False
        self.relationship2.save()
        
        results = self.repository.get_pending_approvals(self.org2)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.relationship2)
    
    def test_get_expiring_soon(self):
        """Test getting relationships expiring soon."""
        # Set relationship to expire in 15 days
        self.relationship1.valid_until = timezone.now() + timedelta(days=15)
        self.relationship1.status = "active"
        self.relationship1.save()
        
        # Should find it with 30 days ahead
        results = self.repository.get_expiring_soon(days_ahead=30)
        self.assertEqual(results.count(), 1)
        
        # Should not find it with 10 days ahead
        results = self.repository.get_expiring_soon(days_ahead=10)
        self.assertEqual(results.count(), 0)
    
    def test_get_relationships_by_trust_score(self):
        """Test getting relationships by trust score range."""
        results = self.repository.get_relationships_by_trust_score(min_score=40, max_score=60)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.relationship1)
        
        results = self.repository.get_relationships_by_trust_score(min_score=80, max_score=100)
        self.assertEqual(results.count(), 0)
    
    def test_get_statistics(self):
        """Test getting relationship statistics."""
        # Create additional relationships for better statistics
        TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org3,
            trust_level=self.low_trust,
            created_by=self.user,
            last_modified_by=self.user,
            is_active=False
        )
        
        stats = self.repository.get_statistics()
        
        self.assertIn('total_relationships', stats)
        self.assertIn('active_relationships', stats)
        self.assertIn('pending_relationships', stats)
        self.assertIn('inactive_relationships', stats)
        self.assertIn('trust_level_distribution', stats)
        self.assertIn('relationship_type_distribution', stats)
        self.assertIn('average_trust_score', stats)
        
        self.assertEqual(stats['total_relationships'], 3)
        self.assertEqual(stats['active_relationships'], 2)
        self.assertEqual(stats['inactive_relationships'], 1)


class TrustGroupRepositoryTest(TestCase):
    """Test TrustGroupRepository functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = TrustGroupRepository()
        
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
        
        # Create trust groups
        self.group1 = TrustGroup.objects.create(
            name="Public Group",
            description="A public test group",
            default_trust_level=self.trust_level,
            is_public=True,
            is_active=True,
            created_by=self.user
        )
        
        self.group2 = TrustGroup.objects.create(
            name="Private Group",
            description="A private test group",
            default_trust_level=self.trust_level,
            is_public=False,
            is_active=True,
            created_by=self.user
        )
    
    def test_initialization(self):
        """Test repository initialization."""
        self.assertEqual(self.repository.model_class, TrustGroup)
    
    def test_get_by_id_success(self):
        """Test getting group by ID."""
        result = self.repository.get_by_id(self.group1.id)
        self.assertEqual(result, self.group1)
    
    def test_get_by_id_not_found(self):
        """Test getting group by non-existent ID."""
        fake_id = uuid.uuid4()
        result = self.repository.get_by_id(fake_id)
        self.assertIsNone(result)
    
    def test_get_all_active_only(self):
        """Test getting all active groups."""
        # Create inactive group
        inactive_group = TrustGroup.objects.create(
            name="Inactive Group",
            description="An inactive group",
            default_trust_level=self.trust_level,
            is_active=False,
            created_by=self.user
        )
        
        results = self.repository.get_all(include_inactive=False)
        self.assertEqual(results.count(), 2)
        self.assertNotIn(inactive_group, results)
    
    def test_get_all_include_inactive(self):
        """Test getting all groups including inactive."""
        # Create inactive group
        inactive_group = TrustGroup.objects.create(
            name="Inactive Group",
            description="An inactive group",
            default_trust_level=self.trust_level,
            is_active=False,
            created_by=self.user
        )
        
        results = self.repository.get_all(include_inactive=True)
        self.assertEqual(results.count(), 3)
        self.assertIn(inactive_group, results)
    
    def test_create_success(self):
        """Test creating new group."""
        new_group = self.repository.create(
            name="New Group",
            description="A new test group",
            creator_org=str(self.org1.id),
            created_by=self.user,
            default_trust_level=self.trust_level
        )
        
        self.assertIsNotNone(new_group.id)
        self.assertEqual(new_group.name, "New Group")
        self.assertEqual(new_group.created_by, self.user)
        self.assertIn(str(self.org1.id), new_group.administrators)
    
    @patch('core.trust.patterns.repository.trust_repository.logger')
    def test_create_with_logging(self, mock_logger):
        """Test that creation logs appropriate messages."""
        self.repository.create(
            name="Logged Group",
            description="A group with logging",
            creator_org=str(self.org1.id),
            created_by=self.user
        )
        
        mock_logger.info.assert_called_once()
        self.assertIn("Trust group created", mock_logger.info.call_args[0][0])
    
    def test_create_exception_handling(self):
        """Test exception handling during creation."""
        with patch.object(self.repository.model_class.objects, 'create') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            with self.assertRaises(Exception):
                self.repository.create(
                    name="Error Group",
                    description="This will fail",
                    creator_org=str(self.org1.id),
                    created_by=self.user
                )
    
    def test_update_success(self):
        """Test updating group."""
        updated = self.repository.update(
            self.group1.id,
            description="Updated description",
            is_public=False
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated.description, "Updated description")
        self.assertFalse(updated.is_public)
    
    def test_update_not_found(self):
        """Test updating non-existent group."""
        fake_id = uuid.uuid4()
        result = self.repository.update(fake_id, description="This will fail")
        self.assertIsNone(result)
    
    def test_update_invalid_field(self):
        """Test updating with invalid field name."""
        updated = self.repository.update(
            self.group1.id,
            invalid_field="should_be_ignored",
            description="valid_update"
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated.description, "valid_update")
        self.assertFalse(hasattr(updated, 'invalid_field'))
    
    def test_delete_success(self):
        """Test soft deleting group."""
        result = self.repository.delete(self.group1.id)
        self.assertTrue(result)
        
        # Verify soft delete
        self.group1.refresh_from_db()
        self.assertFalse(self.group1.is_active)
    
    def test_delete_not_found(self):
        """Test deleting non-existent group."""
        fake_id = uuid.uuid4()
        result = self.repository.delete(fake_id)
        self.assertFalse(result)
    
    def test_get_public_groups(self):
        """Test getting public groups."""
        results = self.repository.get_public_groups()
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.group1)
    
    def test_get_groups_for_organization(self):
        """Test getting groups for organization."""
        # Create membership
        TrustGroupMembership.objects.create(
            trust_group=self.group1,
            organization=self.org1,
            is_active=True
        )
        
        results = self.repository.get_groups_for_organization(self.org1)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.group1)
    
    def test_get_groups_for_organization_include_inactive_membership(self):
        """Test getting groups including inactive memberships."""
        # Create inactive membership
        TrustGroupMembership.objects.create(
            trust_group=self.group1,
            organization=self.org1,
            is_active=False
        )
        
        # Should not find with include_inactive=False (default)
        results = self.repository.get_groups_for_organization(self.org1, include_inactive=False)
        self.assertEqual(results.count(), 0)
        
        # Should find with include_inactive=True
        results = self.repository.get_groups_for_organization(self.org1, include_inactive=True)
        self.assertEqual(results.count(), 1)
    
    def test_can_administer_success(self):
        """Test checking administration rights."""
        # Create admin membership for the user
        from core_ut.trust.models import TrustGroupMembership
        membership = TrustGroupMembership.objects.create(
            trust_group=self.group1,
            organization=self.org1,
            membership_type='administrator',  # Use 'administrator' not 'admin'
            is_active=True
        )
        
        result = self.repository.can_administer(str(self.group1.id), str(self.user.id))
        self.assertTrue(result)
    
    def test_can_administer_failure(self):
        """Test checking administration rights when not allowed."""
        with patch.object(self.group1, 'can_administer', return_value=False):
            result = self.repository.can_administer(self.group1.id, str(self.org1.id))
            self.assertFalse(result)
    
    def test_can_administer_exception(self):
        """Test checking administration rights with exception."""
        result = self.repository.can_administer(uuid.uuid4(), str(self.org1.id))
        self.assertFalse(result)


class TrustLevelRepositoryTest(TestCase):
    """Test TrustLevelRepository functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = TrustLevelRepository()
        
        # Create user
        self.org = Organization.objects.create(
            name="Test Org",
            domain="test.com",
            organization_type="university"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            organization=self.org
        )
        
        # Create trust levels
        self.level1 = TrustLevel.objects.create(
            name="Low",
            level="low",
            numerical_value=25,
            description="Low trust level",
            is_active=True
        )
        
        self.level2 = TrustLevel.objects.create(
            name="High",
            level="high",
            numerical_value=75,
            description="High trust level",
            is_active=True
        )
    
    def test_initialization(self):
        """Test repository initialization."""
        self.assertEqual(self.repository.model_class, TrustLevel)
    
    def test_get_by_id_success(self):
        """Test getting level by ID."""
        result = self.repository.get_by_id(self.level1.id)
        self.assertEqual(result, self.level1)
    
    def test_get_by_id_not_found(self):
        """Test getting level by non-existent ID."""
        fake_id = uuid.uuid4()
        result = self.repository.get_by_id(fake_id)
        self.assertIsNone(result)
    
    def test_get_all_active_only(self):
        """Test getting all active levels."""
        # Create inactive level
        inactive_level = TrustLevel.objects.create(
            name="Inactive",
            level="inactive",
            numerical_value=0,
            description="Inactive level",
            is_active=False
        )
        
        results = self.repository.get_all(include_inactive=False)
        # Account for automatically created default trust levels
        self.assertGreaterEqual(results.count(), 2)
        self.assertNotIn(inactive_level, results)
    
    def test_get_all_include_inactive(self):
        """Test getting all levels including inactive."""
        # Create inactive level
        inactive_level = TrustLevel.objects.create(
            name="Inactive",
            level="inactive",
            numerical_value=0,
            description="Inactive level",
            is_active=False
        )
        
        results = self.repository.get_all(include_inactive=True)
        # Account for automatically created default trust levels
        self.assertGreaterEqual(results.count(), 3)
        self.assertIn(inactive_level, results)
    
    def test_get_all_ordering(self):
        """Test that levels are returned in correct order."""
        results = list(self.repository.get_all())
        # Check that our created levels exist in the results
        self.assertIn(self.level1, results)  # numerical_value=25
        self.assertIn(self.level2, results)  # numerical_value=75
        
        # Find our levels in the ordered results and verify relative order
        level1_index = next(i for i, level in enumerate(results) if level == self.level1)
        level2_index = next(i for i, level in enumerate(results) if level == self.level2)
        # level1 should come before level2 (25 < 75)
        self.assertLess(level1_index, level2_index)


class RepositoryErrorHandlingTest(TestCase):
    """Test error handling across repositories."""
    
    def setUp(self):
        """Set up test data."""
        self.trust_repo = TrustRelationshipRepository()
        self.group_repo = TrustGroupRepository()
        self.level_repo = TrustLevelRepository()
    
    @patch('core.trust.patterns.repository.trust_repository.logger')
    def test_database_transaction_rollback(self, mock_logger):
        """Test that database transactions are properly rolled back on errors."""
        # Create test data
        org1 = Organization.objects.create(
            name="Org 1", domain="org1.com", organization_type="university"
        )
        org2 = Organization.objects.create(
            name="Org 2", domain="org2.com", organization_type="company"
        )
        trust_level = TrustLevel.objects.create(
            name="Test", level="test", numerical_value=50, description="Test"
        )
        user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", 
            password="testpass123", organization=org1
        )
        
        # Mock save method to fail after creation but within transaction
        original_save = TrustRelationship.save
        def failing_save(self):
            if not self.pk:  # Only fail on creation
                original_save(self)
                raise Exception("Simulated database error")
            return original_save(self)
        
        with patch.object(TrustRelationship, 'save', failing_save):
            with self.assertRaises(Exception):
                self.trust_repo.create(
                    source_org=org1,
                    target_org=org2,
                    trust_level=trust_level,
                    created_by=user
                )
        
        # Verify no relationship was created due to rollback
        self.assertEqual(TrustRelationship.objects.count(), 0)
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    def test_concurrent_access_handling(self):
        """Test handling of concurrent access scenarios."""
        # This test simulates concurrent updates using select_for_update
        org1 = Organization.objects.create(
            name="Org 1", domain="org1.com", organization_type="university"
        )
        org2 = Organization.objects.create(
            name="Org 2", domain="org2.com", organization_type="company"
        )
        trust_level = TrustLevel.objects.create(
            name="Test", level="test", numerical_value=50, description="Test"
        )
        user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", 
            password="testpass123", organization=org1
        )
        
        relationship = TrustRelationship.objects.create(
            source_organization=org1,
            target_organization=org2,
            trust_level=trust_level,
            created_by=user,
            last_modified_by=user
        )
        
        # Test that update method uses select_for_update
        with patch.object(
            TrustRelationship.objects, 'select_for_update'
        ) as mock_select_for_update:
            mock_select_for_update.return_value.get.return_value = relationship
            
            self.trust_repo.update(relationship.id, user, status="updated")
            
            mock_select_for_update.assert_called_once()