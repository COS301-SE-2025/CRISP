"""
Essential Tests for Trust Management Repositories

Covers critical CRUD operations and business logic.
"""

import uuid
from django.test import TestCase
from core.trust.models import TrustLevel, TrustRelationship, TrustLog
from core.trust.patterns.repository.trust_repository import (
    TrustRelationshipRepository,
    TrustLevelRepository, 
    TrustLogRepository
)


class TrustRelationshipRepositoryTest(TestCase):
    """Test trust relationship repository"""
    
    def setUp(self):
        self.repository = TrustRelationshipRepository()
        self.source_org = str(uuid.uuid4())
        self.target_org = str(uuid.uuid4())
        
        # Create test trust level
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='medium',
            numerical_value=50,
            description='Test description',
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        # Create test relationship
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            created_by='test_user',
            last_modified_by='test_user'
        )
    
    def test_get_by_id(self):
        """Test get relationship by ID"""
        result = self.repository.get_by_id(str(self.relationship.id))
        self.assertEqual(result, self.relationship)
    
    def test_get_by_organizations(self):
        """Test get relationship between organizations"""
        result = self.repository.get_by_organizations(self.source_org, self.target_org)
        self.assertEqual(result, self.relationship)
    
    def test_get_for_organization(self):
        """Test get relationships for organization"""
        results = self.repository.get_for_organization(self.source_org)
        self.assertIn(self.relationship, results)


class TrustLevelRepositoryTest(TestCase):
    """Test trust level repository"""
    
    def setUp(self):
        self.repository = TrustLevelRepository()
    
    def test_create_success(self):
        """Test creating a trust level"""
        level = self.repository.create(
            name='New Level',
            level='high',
            numerical_value=75,
            description='Test description',
            created_by='test_user'
        )
        self.assertIsInstance(level, TrustLevel)
        self.assertEqual(level.name, 'New Level')
    
    def test_get_by_name(self):
        """Test get level by name"""
        level = TrustLevel.objects.create(
            name='Test Level',
            level='medium',
            numerical_value=50,
            description='Test',
            created_by='test_user'
        )
        result = self.repository.get_by_name('Test Level')
        self.assertEqual(result, level)


class TrustLogRepositoryTest(TestCase):
    """Test trust log repository"""
    
    def setUp(self):
        self.repository = TrustLogRepository()
        self.org_id = str(uuid.uuid4())
        
        self.log = TrustLog.objects.create(
            source_organization=self.org_id,
            action='relationship_created',
            user='test_user',
            details={'test': 'data'},
            success=True
        )
    
    def test_get_by_id(self):
        """Test get log by ID"""
        result = self.repository.get_by_id(str(self.log.id))
        self.assertEqual(result, self.log)
    
    def test_create_log(self):
        """Test creating a log entry"""
        log = self.repository.create(
            action='group_created',
            source_organization=str(uuid.uuid4()),
            user='test_user',
            details={'test': 'data'}
        )
        self.assertIsInstance(log, TrustLog)
        self.assertEqual(log.action, 'group_created')