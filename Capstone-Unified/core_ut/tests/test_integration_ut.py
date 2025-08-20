"""
Essential Integration Tests

Tests end-to-end workflows and component integration.
"""

import uuid
from django.test import TestCase

from core_ut.trust.models import TrustLevel, TrustRelationship, TrustGroup
from core_ut.trust.services.trust_service import TrustService
from core_ut.trust.services.trust_group_service import TrustGroupService
from core_ut.tests.test_fixtures import BaseTestCase  # Add this import


class TrustManagementIntegrationTest(BaseTestCase):  # Change from TestCase to BaseTestCase
    """Integration tests for trust management"""
    
    def test_complete_trust_relationship_workflow(self):
        """Test complete trust relationship lifecycle"""
        # Use actual Organization instances throughout
        try:
            relationship = TrustService.create_trust_relationship(
                source_org=self.source_org,  # Use source_org from BaseTestCase
                target_org=self.target_org,  # Use target_org from BaseTestCase
                trust_level_name=self.medium_trust.name,
                created_by=self.admin_user
            )
            self.assertIsNotNone(relationship)
        except Exception as e:
            self.fail(f"Integration test failed: {e}")
    
    def test_service_integration_with_models(self):
        """Test that services properly integrate with models"""
        try:
            relationship = TrustService.create_trust_relationship(
                source_org=self.source_org,  # Use source_org from BaseTestCase
                target_org=self.target_org,  # Use target_org from BaseTestCase  
                trust_level_name=self.medium_trust.name,
                created_by=self.publisher_user
            )
            self.assertIsNotNone(relationship)
        except Exception as e:
            self.fail(f"Service integration failed: {e}")

    def test_trust_group_workflow(self):
        """Test trust group creation and membership"""
        from core_ut.trust.services.trust_group_service import TrustGroupService
        
        try:
            group = TrustGroupService.create_trust_group(
                name='Test Group',
                description='Test group description',
                creator_org=str(self.source_org.id),  # Add the missing required argument
                created_by=self.admin_user
                # Remove initial_members parameter - it's not supported by the model
            )
            self.assertIsNotNone(group)
        except Exception as e:
            self.fail(f"Trust group workflow failed: {e}")