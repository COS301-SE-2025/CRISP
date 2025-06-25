import uuid
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from ..models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership, TrustLog
)
from ..services.trust_service import TrustService
from ..services.trust_group_service import TrustGroupService
from ..strategies.access_control_strategies import (
    AccessControlContext, TrustLevelAccessStrategy, AnonymizationContext
)
from ..observers.trust_observers import trust_event_manager, notify_access_event


class TrustIntegrationTest(TransactionTestCase):
    """Integration tests for the complete trust management system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create trust levels
        self.trust_level_low = TrustLevel.objects.create(
            name='Low Trust',
            level='low',
            description='Low trust level',
            numerical_value=25,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='system'
        )
        
        self.trust_level_medium = TrustLevel.objects.create(
            name='Medium Trust',
            level='medium',
            description='Medium trust level',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='system'
        )
        
        self.trust_level_high = TrustLevel.objects.create(
            name='High Trust',
            level='high',
            description='High trust level',
            numerical_value=75,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='system'
        )
        
        # Create organizations
        self.org_university_a = str(uuid.uuid4())
        self.org_university_b = str(uuid.uuid4())
        self.org_university_c = str(uuid.uuid4())
        self.org_government = str(uuid.uuid4())
        
        # Test users
        self.user_admin_a = 'admin_university_a'
        self.user_admin_b = 'admin_university_b'
        self.user_analyst_c = 'analyst_university_c'
    
    def test_complete_bilateral_trust_workflow(self):
        """Test complete bilateral trust relationship workflow."""
        # Step 1: University A creates trust relationship with University B
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_university_b,
            trust_level_name='Medium Trust',
            relationship_type='bilateral',
            created_by=self.user_admin_a,
            notes='Partnership for threat intelligence sharing'
        )
        
        self.assertEqual(relationship.status, 'pending')
        self.assertFalse(relationship.is_effective)
        
        # Step 2: University A approves the relationship
        activated_after_source = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.org_university_a,
            approved_by_user=self.user_admin_a
        )
        
        self.assertFalse(activated_after_source)  # Not fully approved yet
        
        # Step 3: University B approves the relationship
        activated_after_target = TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.org_university_b,
            approved_by_user=self.user_admin_b
        )
        
        self.assertTrue(activated_after_target)  # Now fully approved and activated
        
        # Step 4: Verify relationship is effective
        relationship.refresh_from_db()
        self.assertTrue(relationship.is_effective)
        self.assertEqual(relationship.status, 'active')
        
        # Step 5: Test intelligence access
        can_access, reason, rel = TrustService.can_access_intelligence(
            requesting_org=self.org_university_a,
            intelligence_owner=self.org_university_b,
            required_access_level='read'
        )
        
        self.assertTrue(can_access)
        self.assertIn('Authorized via trust relationship', reason)
        self.assertEqual(rel, relationship)
        
        # Step 6: Test bilateral access (reverse direction)
        can_access_reverse, _, _ = TrustService.can_access_intelligence(
            requesting_org=self.org_university_b,
            intelligence_owner=self.org_university_a,
            required_access_level='read'
        )
        
        self.assertTrue(can_access_reverse)
        
        # Step 7: Test insufficient access level
        can_access_contribute, reason_contribute, _ = TrustService.can_access_intelligence(
            requesting_org=self.org_university_a,
            intelligence_owner=self.org_university_b,
            required_access_level='contribute'
        )
        
        self.assertFalse(can_access_contribute)
        self.assertIn('Insufficient access level', reason_contribute)
    
    def test_complete_community_trust_workflow(self):
        """Test complete community trust group workflow."""
        # Step 1: Create trust group
        education_group = TrustGroupService.create_trust_group(
            name='Education Sector Sharing Group',
            description='Threat intelligence sharing for educational institutions',
            creator_org=self.org_university_a,
            group_type='sector',
            is_public=True,
            requires_approval=True,
            default_trust_level_name='Medium Trust'
        )
        
        self.assertTrue(education_group.is_active)
        self.assertIn(self.org_university_a, education_group.administrators)
        
        # Step 2: University B joins the group
        membership_b = TrustGroupService.join_trust_group(
            group_id=str(education_group.id),
            organization=self.org_university_b,
            membership_type='member',
            invited_by=self.org_university_a,
            user=self.user_admin_b
        )
        
        self.assertTrue(membership_b.is_active)
        
        # Step 3: University C joins the group
        membership_c = TrustGroupService.join_trust_group(
            group_id=str(education_group.id),
            organization=self.org_university_c,
            membership_type='member',
            user=self.user_analyst_c
        )
        
        self.assertTrue(membership_c.is_active)
        
        # Step 4: Test community trust relationships
        trust_info_b = TrustService.check_trust_level(
            self.org_university_a,
            self.org_university_b
        )
        
        self.assertIsNotNone(trust_info_b)
        trust_level_b, relationship_b = trust_info_b
        self.assertEqual(trust_level_b.name, 'Medium Trust')
        self.assertEqual(relationship_b.relationship_type, 'community')
        
        # Step 5: Test transitivity (A can access C's intelligence through group)
        trust_info_c = TrustService.check_trust_level(
            self.org_university_a,
            self.org_university_c
        )
        
        self.assertIsNotNone(trust_info_c)
        
        # Step 6: Test group statistics
        stats = TrustGroupService.get_shared_intelligence_count(str(education_group.id))
        self.assertEqual(stats['member_count'], 3)  # A (admin) + B + C
        
        # Step 7: Promote University B to moderator
        promoted = TrustGroupService.promote_member(
            group_id=str(education_group.id),
            organization=self.org_university_b,
            promoting_org=self.org_university_a,
            new_membership_type='moderator',
            user=self.user_admin_a
        )
        
        self.assertTrue(promoted)
        
        # Step 8: University C leaves the group
        left = TrustGroupService.leave_trust_group(
            group_id=str(education_group.id),
            organization=self.org_university_c,
            user=self.user_analyst_c,
            reason='Changed security policy'
        )
        
        self.assertTrue(left)
        
        # Step 9: Verify trust relationship with C is no longer available
        trust_info_c_after = TrustService.check_trust_level(
            self.org_university_a,
            self.org_university_c
        )
        
        self.assertIsNone(trust_info_c_after)
    
    def test_access_control_with_anonymization(self):
        """Test access control integration with anonymization strategies."""
        # Create high trust relationship
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_government,
            trust_level_name='High Trust',
            relationship_type='bilateral',
            created_by=self.user_admin_a
        )
        
        # Activate relationship
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.save()
        relationship.activate()
        
        # Test access control
        access_context = AccessControlContext(
            requesting_org=self.org_university_a,
            target_org=self.org_government,
            resource_type='indicator'
        )
        
        access_context.add_strategy(TrustLevelAccessStrategy(minimum_trust_level=50))
        
        can_access, reasons = access_context.can_access(trust_relationship=relationship)
        self.assertTrue(can_access)
        
        # Test anonymization
        sample_intelligence = {
            'type': 'indicator',
            'pattern': "[network-traffic:src_ref.value = '192.168.1.100']",
            'created_by_ref': 'identity--university-a',
            'x_attribution': 'University A Security Team'
        }
        
        anonymization_context = AnonymizationContext(trust_relationship=relationship)
        anonymized_data = anonymization_context.anonymize_data(sample_intelligence)
        
        # High trust should use minimal anonymization
        self.assertNotIn('x_attribution', anonymized_data)  # Attribution removed
        self.assertNotEqual(
            anonymized_data['created_by_ref'], 
            sample_intelligence['created_by_ref']
        )  # Identity anonymized
    
    def test_trust_revocation_and_cleanup(self):
        """Test trust revocation and its effects."""
        # Create and activate relationship
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_university_b,
            trust_level_name='High Trust',
            created_by=self.user_admin_a
        )
        
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.save()
        relationship.activate()
        
        # Verify access works
        can_access_before, _, _ = TrustService.can_access_intelligence(
            requesting_org=self.org_university_a,
            intelligence_owner=self.org_university_b,
            required_access_level='read'
        )
        self.assertTrue(can_access_before)
        
        # Revoke relationship
        revoked = TrustService.revoke_trust_relationship(
            relationship_id=str(relationship.id),
            revoking_org=self.org_university_a,
            revoked_by_user=self.user_admin_a,
            reason='Security policy change'
        )
        
        self.assertTrue(revoked)
        
        # Verify access is denied
        can_access_after, reason_after, _ = TrustService.can_access_intelligence(
            requesting_org=self.org_university_a,
            intelligence_owner=self.org_university_b,
            required_access_level='read'
        )
        
        self.assertFalse(can_access_after)
        self.assertIn('No trust relationship', reason_after)
        
        # Check relationship status
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'revoked')
        self.assertFalse(relationship.is_active)
        self.assertIsNotNone(relationship.revoked_at)
    
    def test_temporal_trust_relationships(self):
        """Test time-based trust relationships."""
        future_time = timezone.now() + timedelta(hours=1)
        past_time = timezone.now() - timedelta(hours=1)
        
        # Create relationship with future start time
        future_relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_university_b,
            trust_level_name='Medium Trust',
            created_by=self.user_admin_a,
            valid_until=future_time + timedelta(days=30)
        )
        
        future_relationship.valid_from = future_time
        future_relationship.approved_by_source = True
        future_relationship.approved_by_target = True
        future_relationship.save()
        future_relationship.status = 'active'
        future_relationship.save()
        
        # Should not be effective yet
        self.assertFalse(future_relationship.is_effective)
        
        # Create relationship that expires soon
        expiring_relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_b,
            target_org=self.org_university_c,
            trust_level_name='Medium Trust',
            created_by=self.user_admin_b,
            valid_until=past_time
        )
        
        expiring_relationship.approved_by_source = True
        expiring_relationship.approved_by_target = True
        expiring_relationship.save()
        expiring_relationship.status = 'active'
        expiring_relationship.save()
        
        # Should be expired
        self.assertTrue(expiring_relationship.is_expired)
        self.assertFalse(expiring_relationship.is_effective)
    
    @patch('TrustManagement.observers.trust_observers.logger')
    def test_observer_pattern_integration(self, mock_logger):
        """Test observer pattern integration with trust events."""
        # Create relationship (should trigger observers)
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_university_b,
            trust_level_name='Medium Trust',
            created_by=self.user_admin_a
        )
        
        # Verify creation was logged
        mock_logger.info.assert_called()
        
        # Test access event notification
        notify_access_event(
            event_type='access_granted',
            requesting_org=self.org_university_a,
            target_org=self.org_university_b,
            resource_type='indicator',
            access_level='read',
            user=self.user_admin_a
        )
        
        # Verify access event was processed
        self.assertTrue(mock_logger.info.called)
    
    def test_trust_level_hierarchies(self):
        """Test trust level hierarchies and upgrades."""
        # Start with low trust
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_university_b,
            trust_level_name='Low Trust',
            created_by=self.user_admin_a
        )
        
        relationship.approved_by_source = True
        relationship.approved_by_target = True
        relationship.save()
        relationship.activate()
        
        # Verify low trust access
        can_access_low, _, _ = TrustService.can_access_intelligence(
            requesting_org=self.org_university_a,
            intelligence_owner=self.org_university_b,
            required_access_level='read'
        )
        self.assertTrue(can_access_low)
        
        can_access_contribute, _, _ = TrustService.can_access_intelligence(
            requesting_org=self.org_university_a,
            intelligence_owner=self.org_university_b,
            required_access_level='contribute'
        )
        self.assertFalse(can_access_contribute)
        
        # Upgrade to high trust
        upgraded = TrustService.update_trust_level(
            relationship_id=str(relationship.id),
            new_trust_level_name='High Trust',
            updated_by=self.user_admin_a,
            reason='Successful collaboration history'
        )
        
        self.assertTrue(upgraded)
        
        # Verify high trust access
        can_access_contribute_after, _, _ = TrustService.can_access_intelligence(
            requesting_org=self.org_university_a,
            intelligence_owner=self.org_university_b,
            required_access_level='contribute'
        )
        self.assertTrue(can_access_contribute_after)
    
    def test_audit_log_completeness(self):
        """Test that all trust operations are properly audited."""
        initial_log_count = TrustLog.objects.count()
        
        # Perform various trust operations
        relationship = TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_university_b,
            trust_level_name='Medium Trust',
            created_by=self.user_admin_a
        )
        
        TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.org_university_a,
            approved_by_user=self.user_admin_a
        )
        
        TrustService.approve_trust_relationship(
            relationship_id=str(relationship.id),
            approving_org=self.org_university_b,
            approved_by_user=self.user_admin_b
        )
        
        group = TrustGroupService.create_trust_group(
            name='Audit Test Group',
            description='Group for audit testing',
            creator_org=self.org_university_a,
            default_trust_level_name='Medium Trust'
        )
        
        TrustGroupService.join_trust_group(
            group_id=str(group.id),
            organization=self.org_university_c,
            user=self.user_analyst_c
        )
        
        # Check that audit logs were created
        final_log_count = TrustLog.objects.count()
        self.assertGreater(final_log_count, initial_log_count)
        
        # Verify specific log entries exist
        creation_logs = TrustLog.objects.filter(action='relationship_created')
        self.assertGreater(creation_logs.count(), 0)
        
        approval_logs = TrustLog.objects.filter(action='relationship_approved')
        self.assertGreater(approval_logs.count(), 0)
        
        group_logs = TrustLog.objects.filter(action='group_created')
        self.assertGreater(group_logs.count(), 0)
    
    def test_error_handling_and_rollback(self):
        """Test error handling and database rollback."""
        # Test rollback on duplicate relationship creation
        TrustService.create_trust_relationship(
            source_org=self.org_university_a,
            target_org=self.org_university_b,
            trust_level_name='Medium Trust',
            created_by=self.user_admin_a
        )
        
        # This should fail and not create additional logs
        initial_log_count = TrustLog.objects.count()
        
        with self.assertRaises(Exception):
            TrustService.create_trust_relationship(
                source_org=self.org_university_a,
                target_org=self.org_university_b,  # Duplicate
                trust_level_name='High Trust',
                created_by=self.user_admin_a
            )
        
        # Verify no additional logs were created
        final_log_count = TrustLog.objects.count()
        self.assertEqual(final_log_count, initial_log_count)
    
    def test_performance_with_large_datasets(self):
        """Test performance with larger numbers of relationships."""
        # Create multiple organizations and relationships
        organizations = [str(uuid.uuid4()) for _ in range(10)]
        
        # Create relationships between organizations
        for i, source_org in enumerate(organizations):
            for j, target_org in enumerate(organizations[i+1:], i+1):
                relationship = TrustService.create_trust_relationship(
                    source_org=source_org,
                    target_org=target_org,
                    trust_level_name='Medium Trust',
                    created_by='test_user'
                )
                # Activate the relationship to make it effective
                relationship.approved_by_source = True
                relationship.approved_by_target = True
                relationship.save()
                relationship.activate()
        
        # Test querying relationships for one organization
        relationships = TrustService.get_trust_relationships_for_organization(
            organizations[0]
        )
        
        # Should find relationships where org is either source or target
        self.assertGreater(len(relationships), 0)
        
        # Test sharing organizations query
        sharing_orgs = TrustService.get_sharing_organizations(
            source_org=organizations[0],
            min_trust_level='low'
        )
        
        # Should find organizations that can receive intelligence
        self.assertGreater(len(sharing_orgs), 0)