"""
Essential Tests for Trust Management Services

Covers critical business logic and service operations.
"""

import uuid
from unittest.mock import patch, Mock
from django.test import TestCase
from core_ut.trust.models import TrustLevel, TrustRelationship, TrustGroup
from core_ut.trust.services.trust_service import TrustService
from core_ut.trust.services.trust_group_service import TrustGroupService
from core_ut.tests.test_fixtures import BaseTestCase


class TrustServiceTest(BaseTestCase):
    """Test core trust service functionality"""
    
    def test_create_trust_relationship(self):
        """Test creating a trust relationship"""
        relationship = TrustService.create_trust_relationship(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level_name='Medium Trust',
            created_by=self.admin_user
        )
        
        self.assertIsInstance(relationship, TrustRelationship)
        self.assertEqual(relationship.source_organization, self.source_org)
        self.assertEqual(relationship.target_organization, self.target_org)
    
    def test_check_trust_level(self):
        """Test checking trust level between organizations"""
        # Create active relationship first
        relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.medium_trust,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )
        
        result = TrustService.check_trust_level(self.source_org, self.target_org)
        self.assertIsNotNone(result)
        trust_level, rel = result
        self.assertEqual(trust_level, self.medium_trust)
        self.assertEqual(rel, relationship)
    
    def test_approve_trust_relationship(self):
        """Test approving a trust relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.medium_trust,
            status='pending',
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )
        
        result = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.source_org,
            approved_by_user=self.admin_user
        )
        
        # Should return False since only source approved (need both approvals to activate)
        self.assertFalse(result)
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)


class TrustGroupServiceTest(BaseTestCase):
    """Test trust group service functionality"""
    
    def test_create_trust_group(self):
        """Test creating a trust group"""
        group = TrustGroupService.create_trust_group(
            name='Test Group',
            description='Test description',
            creator_org=str(self.source_org.id),
            group_type='community',
            default_trust_level_name=self.medium_trust.level,
            created_by=self.admin_user
        )
        
        self.assertIsInstance(group, TrustGroup)
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.group_type, 'community')
    
    def test_join_trust_group(self):
        """Test joining a trust group"""
        group = TrustGroup.objects.create(
            name='Test Group',
            description='Test description',
            group_type='community',
            default_trust_level=self.medium_trust,
            created_by=self.admin_user
        )
        
        result = TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=str(self.target_org.id),
            user=self.publisher_user
        )
        
        self.assertIsNotNone(result)
        # Verify membership was created
        self.assertTrue(group.group_memberships.filter(
            organization=self.target_org
        ).exists())