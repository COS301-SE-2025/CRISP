"""
Essential Tests for Trust Management Models

Covers critical model functionality and relationships.
"""

import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.trust.models import TrustLevel, TrustRelationship, TrustGroup, TrustLog


class TrustLevelTest(TestCase):
    """Test TrustLevel model"""
    
    def test_create_trust_level(self):
        """Test creating a trust level"""
        level = TrustLevel.objects.create(
            name='Test Level',
            level='medium',
            numerical_value=50,
            description='Test description',
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.assertEqual(level.name, 'Test Level')
        self.assertEqual(level.level, 'medium')
        self.assertEqual(level.numerical_value, 50)
    
    def test_str_representation(self):
        """Test string representation"""
        level = TrustLevel.objects.create(
            name='Test Level',
            level='high',
            numerical_value=75,
            description='Test',
            created_by='test_user'
        )
        
        # Check that string representation includes the name
        self.assertIn('Test Level', str(level))


class TrustRelationshipTest(TestCase):
    """Test TrustRelationship model"""
    
    def setUp(self):
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='medium',
            numerical_value=50,
            description='Test',
            created_by='test_user'
        )
        
        self.source_org = str(uuid.uuid4())
        self.target_org = str(uuid.uuid4())
    
    def test_create_trust_relationship(self):
        """Test creating a trust relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            created_by='test_user',
            last_modified_by='test_user'
        )
        
        self.assertEqual(relationship.source_organization, self.source_org)
        self.assertEqual(relationship.target_organization, self.target_org)
        self.assertEqual(relationship.trust_level, self.trust_level)
        self.assertEqual(relationship.status, 'pending')  # Default status
    
    def test_same_organization_validation(self):
        """Test validation prevents same source and target"""
        relationship = TrustRelationship(
            source_organization=self.source_org,
            target_organization=self.source_org,  # Same as source
            trust_level=self.trust_level,
            created_by='test_user',
            last_modified_by='test_user'
        )
        
        with self.assertRaises(ValidationError):
            relationship.clean()
    
    def test_unique_together_constraint(self):
        """Test unique constraint on source/target organizations"""
        # Create first relationship
        TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            created_by='test_user',
            last_modified_by='test_user'
        )
        
        # Try to create duplicate
        with self.assertRaises(ValidationError):
            duplicate = TrustRelationship(
                source_organization=self.source_org,
                target_organization=self.target_org,
                trust_level=self.trust_level,
                created_by='test_user2',
                last_modified_by='test_user2'
            )
            duplicate.full_clean()


class TrustGroupTest(TestCase):
    """Test TrustGroup model"""
    
    def setUp(self):
        self.trust_level = TrustLevel.objects.create(
            name='Group Level',
            level='medium',
            numerical_value=50,
            description='Test',
            created_by='test_user'
        )
    
    def test_create_trust_group(self):
        """Test creating a trust group"""
        group = TrustGroup.objects.create(
            name='Test Group',
            description='Test description',
            group_type='community',
            default_trust_level=self.trust_level,
            created_by='test_user'
        )
        
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.group_type, 'community')
    
    def test_str_representation(self):
        """Test string representation"""
        group = TrustGroup.objects.create(
            name='Test Group',
            description='Test description',
            group_type='community',
            default_trust_level=self.trust_level,
            created_by='test_user'
        )
        
        self.assertEqual(str(group), 'Test Group (community)')


class TrustLogTest(TestCase):
    """Test TrustLog model"""
    
    def test_create_trust_log(self):
        """Test creating a trust log entry"""
        log = TrustLog.objects.create(
            action='relationship_created',
            source_organization=str(uuid.uuid4()),
            user='test_user',
            details={'test': 'data'},
            success=True
        )
        
        self.assertEqual(log.action, 'relationship_created')
        self.assertTrue(log.success)
        self.assertEqual(log.details, {'test': 'data'})
    
    def test_str_representation(self):
        """Test string representation"""
        log = TrustLog.objects.create(
            action='relationship_created',
            source_organization=str(uuid.uuid4()),
            user='test_user',
            success=True
        )
        
        self.assertIn('relationship_created', str(log))
        self.assertIn('SUCCESS', str(log))