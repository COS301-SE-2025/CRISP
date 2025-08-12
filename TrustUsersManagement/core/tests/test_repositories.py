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
from core.tests.test_fixtures import BaseTestCase


class TrustRelationshipRepositoryTest(BaseTestCase):
    """Test trust relationship repository"""
    
    def setUp(self):
        super().setUp()
        self.repository = TrustRelationshipRepository()
        
        # Create test relationship
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.medium_trust,
            created_by=self.admin_user,
            last_modified_by=self.admin_user
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


class TrustLevelRepositoryTest(BaseTestCase):
    """Test trust level repository"""
    
    def setUp(self):
        super().setUp()
        self.repository = TrustLevelRepository()
    
    def test_create_success(self):
        """Test creating a trust level"""
        level = self.repository.create(
            name='New Level',
            level='high',
            numerical_value=75,
            description='Test description',
            created_by=self.admin_user
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
            created_by=self.admin_user
        )
        result = self.repository.get_by_name('Test Level')
        self.assertEqual(result, level)


class TrustLogRepositoryTest(BaseTestCase):
    """Test trust log repository"""
    
    def setUp(self):
        super().setUp()
        self.repository = TrustLogRepository()
        
        self.log = TrustLog.objects.create(
            source_organization=self.test_org,
            action='relationship_created',
            user=self.test_user,
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
            source_organization=self.test_org,
            user=self.test_user,
            details={'test': 'data'}
        )
        self.assertIsInstance(log, TrustLog)
        self.assertEqual(log.action, 'group_created')