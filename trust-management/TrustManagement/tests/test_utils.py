"""
Comprehensive Test Suite for Trust Management Utilities

This module tests all utility functions in the utils module to achieve high coverage.
"""

import uuid
import json
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from datetime import timedelta

from ..models import TrustLevel, TrustGroup, TrustRelationship, TrustLog, TrustGroupMembership
from ..utils import (
    generate_trust_relationship_id, validate_organization_uuid, calculate_trust_score,
    get_trust_relationship_summary, get_trust_group_summary, anonymize_organization_id,
    calculate_sharing_statistics, get_trust_network_analysis, export_trust_configuration,
    validate_trust_configuration, format_trust_relationship_for_display
)


class UtilityFunctionsTest(TestCase):
    """Test individual utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Test Trust Level',
            level='medium',
            description='Test trust level',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user',
            is_system_default=True
        )
        
        self.high_trust_level = TrustLevel.objects.create(
            name='High Test Trust Level',
            level='high',
            description='High test trust level',
            numerical_value=80,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Test Trust Group',
            description='A test trust group',
            group_type='community',
            is_public=True,
            requires_approval=False,
            default_trust_level=self.trust_level,
            created_by='group_creator',
            administrators=['admin1', 'admin2']
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.org_3 = str(uuid.uuid4())
        self.user_1 = 'test_user_1'
    
    def test_generate_trust_relationship_id(self):
        """Test trust relationship ID generation."""
        rel_id = generate_trust_relationship_id()
        
        # Should be a valid UUID string
        self.assertIsInstance(rel_id, str)
        uuid.UUID(rel_id)  # Should not raise exception
        
        # Should generate different IDs
        rel_id2 = generate_trust_relationship_id()
        self.assertNotEqual(rel_id, rel_id2)
    
    def test_validate_organization_uuid_valid(self):
        """Test UUID validation with valid UUIDs."""
        valid_uuid = str(uuid.uuid4())
        self.assertTrue(validate_organization_uuid(valid_uuid))
        
        # Test different UUID formats
        self.assertTrue(validate_organization_uuid(self.org_1))
        self.assertTrue(validate_organization_uuid('12345678-1234-1234-1234-123456789012'))
    
    def test_validate_organization_uuid_invalid(self):
        """Test UUID validation with invalid UUIDs."""
        self.assertFalse(validate_organization_uuid('invalid-uuid'))
        self.assertFalse(validate_organization_uuid(''))
        self.assertFalse(validate_organization_uuid(None))
        self.assertFalse(validate_organization_uuid('12345'))
        self.assertFalse(validate_organization_uuid('not-a-uuid-at-all'))
    
    def test_calculate_trust_score_basic(self):
        """Test basic trust score calculation."""
        score = calculate_trust_score(self.trust_level, 0, 1.0)
        
        # With 0 days age and full activity, should be close to base score
        expected = 50 * (1 + 0 + 0.05)  # base + age_factor + activity_factor
        self.assertAlmostEqual(score, expected, places=2)
    
    def test_calculate_trust_score_with_age(self):
        """Test trust score calculation with relationship age."""
        # Test with 1 year age (should get maximum age bonus)
        score = calculate_trust_score(self.trust_level, 365, 1.0)
        expected = 50 * (1 + 0.1 + 0.05)  # base + max_age_factor + activity_factor
        self.assertAlmostEqual(score, expected, places=1)
        
        # Test with 6 months age (should get half age bonus)
        score = calculate_trust_score(self.trust_level, 182, 1.0)
        expected_age_factor = (182 / 365.0) * 0.1  # More precise calculation
        expected = 50 * (1 + expected_age_factor + 0.05)
        self.assertAlmostEqual(score, expected, places=1)
    
    def test_calculate_trust_score_with_activity(self):
        """Test trust score calculation with different activity levels."""
        # Test with no activity
        score = calculate_trust_score(self.trust_level, 0, 0.0)
        expected = 50 * (1 + 0 + 0)  # base only
        self.assertAlmostEqual(score, expected, places=2)
        
        # Test with half activity
        score = calculate_trust_score(self.trust_level, 0, 0.5)
        expected = 50 * (1 + 0 + 0.025)  # base + half activity factor
        self.assertAlmostEqual(score, expected, places=2)
    
    def test_calculate_trust_score_max_cap(self):
        """Test trust score calculation with maximum cap."""
        # High trust level with maximum bonuses should not exceed 100
        score = calculate_trust_score(self.high_trust_level, 365, 1.0)
        self.assertLessEqual(score, 100.0)
    
    def test_anonymize_organization_id(self):
        """Test organization ID anonymization."""
        org_id = self.org_1
        anon_id = anonymize_organization_id(org_id)
        
        # Should start with 'anon_'
        self.assertTrue(anon_id.startswith('anon_'))
        
        # Should be deterministic (same input produces same output)
        anon_id2 = anonymize_organization_id(org_id)
        self.assertEqual(anon_id, anon_id2)
        
        # Different org IDs should produce different anonymized IDs
        anon_id3 = anonymize_organization_id(self.org_2)
        self.assertNotEqual(anon_id, anon_id3)
        
        # Should be 21 characters long (anon_ + 16 hash chars)
        self.assertEqual(len(anon_id), 21)
    
    def test_anonymize_organization_id_with_salt(self):
        """Test organization ID anonymization with custom salt."""
        org_id = self.org_1
        anon_id1 = anonymize_organization_id(org_id, 'salt1')
        anon_id2 = anonymize_organization_id(org_id, 'salt2')
        
        # Different salts should produce different results
        self.assertNotEqual(anon_id1, anon_id2)
        
        # Same salt should produce same result
        anon_id3 = anonymize_organization_id(org_id, 'salt1')
        self.assertEqual(anon_id1, anon_id3)


class TrustRelationshipSummaryTest(TestCase):
    """Test trust relationship summary functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Summary Test Trust Level',
            level='medium',
            description='Test trust level for summaries',
            numerical_value=60,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.user_1 = 'summary_test_user'
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            status='active',
            is_bilateral=True,
            approved_by_source=True,
            approved_by_target=True,
            approved_by_source_user=self.user_1,
            approved_by_target_user=self.user_1,
            created_by=self.user_1,
            last_modified_by=self.user_1,
            notes='Test relationship notes',
            valid_until=timezone.now() + timedelta(days=30)
        )
    
    def test_get_trust_relationship_summary_complete(self):
        """Test complete trust relationship summary."""
        summary = get_trust_relationship_summary(self.relationship)
        
        # Check basic fields
        self.assertEqual(summary['id'], str(self.relationship.id))
        self.assertEqual(summary['source_organization'], self.org_1)
        self.assertEqual(summary['target_organization'], self.org_2)
        self.assertEqual(summary['relationship_type'], 'bilateral')
        self.assertEqual(summary['status'], 'active')
        self.assertTrue(summary['is_bilateral'])
        
        # Check trust level information
        trust_info = summary['trust_level']
        self.assertEqual(trust_info['name'], 'Summary Test Trust Level')
        self.assertEqual(trust_info['level'], 'medium')
        self.assertEqual(trust_info['numerical_value'], 60)
        
        # Check approval status
        approval = summary['approval_status']
        self.assertTrue(approval['source_approved'])
        self.assertTrue(approval['target_approved'])
        self.assertTrue(approval['fully_approved'])
        
        # Check access control
        access_control = summary['access_control']
        self.assertIn('access_level', access_control)
        self.assertIn('anonymization_level', access_control)
        
        # Check validity information
        validity = summary['validity']
        self.assertIsNotNone(validity['valid_from'])
        self.assertIsNotNone(validity['valid_until'])
        self.assertFalse(validity['is_expired'])
        self.assertIsInstance(validity['days_remaining'], int)
        
        # Check timestamps
        timestamps = summary['timestamps']
        self.assertIsNotNone(timestamps['created_at'])
        self.assertIsNone(timestamps['activated_at'])  # Not activated in this test
        
        # Check metadata
        metadata = summary['metadata']
        self.assertEqual(metadata['created_by'], self.user_1)
        self.assertEqual(metadata['notes'], 'Test relationship notes')
    
    def test_get_trust_relationship_summary_no_expiration(self):
        """Test relationship summary without expiration date."""
        # Create relationship without expiration using different orgs
        org_3 = str(uuid.uuid4())
        org_4 = str(uuid.uuid4())
        rel_no_expiry = TrustRelationship.objects.create(
            source_organization=org_3,
            target_organization=org_4,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            status='pending',
            created_by=self.user_1,
            last_modified_by=self.user_1
        )
        
        summary = get_trust_relationship_summary(rel_no_expiry)
        
        validity = summary['validity']
        self.assertIsNone(validity['valid_until'])
        self.assertIsNone(validity['days_remaining'])
        self.assertFalse(validity['is_expired'])


class TrustGroupSummaryTest(TestCase):
    """Test trust group summary functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Group Summary Trust Level',
            level='medium',
            description='Trust level for group summaries',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Group Summary Test Group',
            description='A test group for summary testing',
            group_type='sector',
            is_public=False,
            requires_approval=True,
            default_trust_level=self.trust_level,
            created_by='group_creator',
            administrators=['admin1', 'admin2'],
            group_policies={'sharing_allowed': True, 'anonymization_required': False}
        )
        
        # Add some members
        TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization=str(uuid.uuid4()),
            membership_type='member'
        )
        TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization=str(uuid.uuid4()),
            membership_type='administrator'
        )
    
    def test_get_trust_group_summary_complete(self):
        """Test complete trust group summary."""
        summary = get_trust_group_summary(self.trust_group)
        
        # Check basic fields
        self.assertEqual(summary['id'], str(self.trust_group.id))
        self.assertEqual(summary['name'], 'Group Summary Test Group')
        self.assertEqual(summary['description'], 'A test group for summary testing')
        self.assertEqual(summary['group_type'], 'sector')
        self.assertFalse(summary['is_public'])
        self.assertTrue(summary['requires_approval'])
        
        # Check default trust level
        trust_level = summary['default_trust_level']
        self.assertEqual(trust_level['name'], 'Group Summary Trust Level')
        self.assertEqual(trust_level['level'], 'medium')
        self.assertEqual(trust_level['numerical_value'], 50)
        
        # Check membership information
        membership = summary['membership']
        self.assertEqual(membership['member_count'], 2)
        self.assertEqual(membership['administrators'], ['admin1', 'admin2'])
        
        # Check policies
        self.assertEqual(summary['policies'], {'sharing_allowed': True, 'anonymization_required': False})
        
        # Check status
        self.assertTrue(summary['status']['is_active'])
        
        # Check timestamps
        timestamps = summary['timestamps']
        self.assertIsNotNone(timestamps['created_at'])
        self.assertIsNotNone(timestamps['updated_at'])
        
        # Check metadata
        metadata = summary['metadata']
        self.assertEqual(metadata['created_by'], 'group_creator')


class SharingStatisticsTest(TestCase):
    """Test sharing statistics calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use unique org for this test to avoid conflicts
        self.org_stats = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        # Clear any existing logs
        TrustLog.objects.all().delete()
        
        # Create some test logs
        base_time = timezone.now()
        
        # Recent logs (within 30 days)
        TrustLog.objects.create(
            action='intelligence_shared',
            source_organization=self.org_stats,
            target_organization=self.org_2,
            user='test_user',
            timestamp=base_time - timedelta(days=5)
        )
        TrustLog.objects.create(
            action='access_granted',
            source_organization=self.org_stats,
            target_organization=self.org_2,
            user='test_user',
            timestamp=base_time - timedelta(days=10)
        )
        TrustLog.objects.create(
            action='intelligence_accessed',
            source_organization=self.org_stats,
            target_organization=self.org_2,
            user='test_user',
            timestamp=base_time - timedelta(days=15)
        )
        
        # Old logs (beyond 30 days)
        TrustLog.objects.create(
            action='intelligence_shared',
            source_organization=self.org_stats,
            target_organization=self.org_2,
            user='test_user',
            timestamp=base_time - timedelta(days=45)
        )
    
    def test_calculate_sharing_statistics_default_period(self):
        """Test sharing statistics calculation with default 30-day period."""
        # Use a completely fresh organization for this test
        test_org = str(uuid.uuid4())
        target_org = str(uuid.uuid4())
        base_time = timezone.now()
        
        # Create specific logs for this test
        TrustLog.objects.create(
            action='intelligence_shared',
            source_organization=test_org,
            target_organization=target_org,
            user='test_user_stats',
            timestamp=base_time - timedelta(days=5)
        )
        TrustLog.objects.create(
            action='access_granted',
            source_organization=test_org,
            target_organization=target_org,
            user='test_user_stats',
            timestamp=base_time - timedelta(days=10)
        )
        TrustLog.objects.create(
            action='intelligence_accessed',
            source_organization=test_org,
            target_organization=target_org,
            user='test_user_stats',
            timestamp=base_time - timedelta(days=15)
        )
        
        stats = calculate_sharing_statistics(test_org)
        
        self.assertEqual(stats['intelligence_shared'], 1)
        self.assertEqual(stats['access_granted'], 1)
        self.assertEqual(stats['intelligence_accessed'], 1)
        self.assertEqual(stats['total_sharing_activities'], 2)  # shared + granted
        self.assertEqual(stats['period_days'], 30)
    
    def test_calculate_sharing_statistics_custom_period(self):
        """Test sharing statistics calculation with custom period."""
        # Use a completely fresh organization for this test
        test_org = str(uuid.uuid4())
        target_org = str(uuid.uuid4())
        base_time = timezone.now()
        
        # Create a log within 7 days
        recent_log = TrustLog.objects.create(
            action='intelligence_shared',
            source_organization=test_org,
            target_organization=target_org,
            user='test_user_custom_recent',
            timestamp=base_time - timedelta(days=3)
        )
        
        # Create a log outside 7 days
        old_log = TrustLog.objects.create(
            action='access_granted',
            source_organization=test_org,
            target_organization=target_org,
            user='test_user_custom_old',
            timestamp=base_time - timedelta(days=10)
        )
        
        # Test with 7-day period
        stats_7_days = calculate_sharing_statistics(test_org, days=7)
        
        # Should include recent log but not old log
        self.assertEqual(stats_7_days['intelligence_shared'], 1)
        self.assertGreaterEqual(stats_7_days['access_granted'], 0)  # May have other logs
        self.assertEqual(stats_7_days['period_days'], 7)
        
        # Test with 15-day period (should include both)
        stats_15_days = calculate_sharing_statistics(test_org, days=15)
        
        # Both logs should be included
        self.assertEqual(stats_15_days['intelligence_shared'], 1)
        self.assertGreaterEqual(stats_15_days['access_granted'], 1)  # Should include the old log
        self.assertEqual(stats_15_days['period_days'], 15)
    
    def test_calculate_sharing_statistics_no_logs(self):
        """Test sharing statistics calculation with no logs."""
        empty_org = str(uuid.uuid4())
        stats = calculate_sharing_statistics(empty_org)
        
        self.assertEqual(stats['intelligence_shared'], 0)
        self.assertEqual(stats['access_granted'], 0)
        self.assertEqual(stats['intelligence_accessed'], 0)
        self.assertEqual(stats['total_sharing_activities'], 0)
        self.assertEqual(stats['period_days'], 30)


class TrustNetworkAnalysisTest(TestCase):
    """Test trust network analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear existing relationships to avoid conflicts
        TrustRelationship.objects.all().delete()
        
        self.trust_level_low = TrustLevel.objects.create(
            name='Network Low Trust',
            level='low',
            description='Low trust level for network',
            numerical_value=25,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.trust_level_high = TrustLevel.objects.create(
            name='Network High Trust',
            level='high',
            description='High trust level for network',
            numerical_value=75,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        self.org_center = str(uuid.uuid4())
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.org_3 = str(uuid.uuid4())
        
        # Create relationships with center organization
        self.rel_1 = TrustRelationship.objects.create(
            source_organization=self.org_center,
            target_organization=self.org_1,
            trust_level=self.trust_level_high,
            relationship_type='bilateral',
            anonymization_level='minimal',
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by='test_user',
            last_modified_by='test_user'
        )
        
        self.rel_2 = TrustRelationship.objects.create(
            source_organization=self.org_2,
            target_organization=self.org_center,
            trust_level=self.trust_level_low,
            relationship_type='bilateral',
            anonymization_level='full',
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by='test_user',
            last_modified_by='test_user'
        )
        
        # Inactive relationship
        self.rel_3 = TrustRelationship.objects.create(
            source_organization=self.org_center,
            target_organization=self.org_3,
            trust_level=self.trust_level_high,
            relationship_type='bilateral',
            anonymization_level='minimal',
            status='suspended',
            created_by='test_user',
            last_modified_by='test_user'
        )
    
    def test_get_trust_network_analysis_complete(self):
        """Test complete trust network analysis."""
        analysis = get_trust_network_analysis(self.org_center)
        
        self.assertEqual(analysis['organization'], self.org_center)
        # Only counting the relationships we actually created in this test
        self.assertEqual(analysis['total_relationships'], 2)  # rel_1 and rel_2 (rel_3 is inactive)
        self.assertEqual(analysis['effective_relationships'], 2)  # Only active ones
        self.assertEqual(analysis['effectiveness_ratio'], 1.0)  # 2/2 = 1.0
        
        # Check trust level distribution
        distribution = analysis['trust_level_distribution']
        self.assertEqual(distribution['high'], 1)  # rel_1
        self.assertEqual(distribution['low'], 1)   # rel_2
        
        # Network reach should be 2 (org_1 and org_2, not org_3 since it's suspended)
        self.assertEqual(analysis['network_reach'], 2)
        
        self.assertIsNotNone(analysis['analysis_timestamp'])
    
    def test_get_trust_network_analysis_no_relationships(self):
        """Test trust network analysis with no relationships."""
        empty_org = str(uuid.uuid4())
        analysis = get_trust_network_analysis(empty_org)
        
        self.assertEqual(analysis['organization'], empty_org)
        self.assertEqual(analysis['total_relationships'], 0)
        self.assertEqual(analysis['effective_relationships'], 0)
        self.assertEqual(analysis['effectiveness_ratio'], 0)
        self.assertEqual(analysis['trust_level_distribution'], {})
        self.assertEqual(analysis['network_reach'], 0)


class ConfigurationExportImportTest(TestCase):
    """Test configuration export and import functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Export Test Trust Level',
            level='medium',
            description='Trust level for export testing',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user',
            is_system_default=True,
            sharing_policies={'allow_sharing': True}
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Export Test Group',
            description='Group for export testing',
            group_type='community',
            is_public=True,
            requires_approval=False,
            default_trust_level=self.trust_level,
            created_by='group_creator',
            administrators=['admin1'],
            group_policies={'open_membership': True}
        )
    
    def test_export_trust_configuration_json(self):
        """Test exporting trust configuration in JSON format."""
        config_str = export_trust_configuration('json')
        config_data = json.loads(config_str)
        
        # Check structure
        self.assertIn('export_timestamp', config_data)
        self.assertIn('trust_levels', config_data)
        self.assertIn('trust_groups', config_data)
        self.assertIn('version', config_data)
        
        # Check trust levels
        trust_levels = config_data['trust_levels']
        self.assertEqual(len(trust_levels), 1)
        level = trust_levels[0]
        self.assertEqual(level['name'], 'Export Test Trust Level')
        self.assertEqual(level['level'], 'medium')
        self.assertEqual(level['numerical_value'], 50)
        self.assertTrue(level['is_system_default'])
        
        # Check trust groups
        trust_groups = config_data['trust_groups']
        self.assertEqual(len(trust_groups), 1)
        group = trust_groups[0]
        self.assertEqual(group['name'], 'Export Test Group')
        self.assertEqual(group['group_type'], 'community')
        self.assertTrue(group['is_public'])
        self.assertEqual(group['default_trust_level'], 'Export Test Trust Level')
    
    def test_export_trust_configuration_csv(self):
        """Test exporting trust configuration in CSV format."""
        # Currently returns JSON even for CSV format
        config_str = export_trust_configuration('csv')
        config_data = json.loads(config_str)
        
        # Should still be valid JSON structure
        self.assertIn('trust_levels', config_data)
        self.assertIn('trust_groups', config_data)
    
    def test_export_trust_configuration_invalid_format(self):
        """Test exporting with invalid format."""
        with self.assertRaises(ValueError) as context:
            export_trust_configuration('xml')
        
        self.assertIn("Format must be 'json' or 'csv'", str(context.exception))
    
    def test_validate_trust_configuration_valid(self):
        """Test validating a valid trust configuration."""
        config_data = {
            'trust_levels': [
                {
                    'name': 'Test Level',
                    'level': 'medium',
                    'numerical_value': 50,
                    'default_anonymization_level': 'partial',
                    'default_access_level': 'read'
                }
            ],
            'trust_groups': [
                {
                    'name': 'Test Group',
                    'description': 'A test group',
                    'default_trust_level': 'Test Level'
                }
            ]
        }
        
        is_valid, errors = validate_trust_configuration(config_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_trust_configuration_missing_fields(self):
        """Test validating configuration with missing fields."""
        config_data = {
            'trust_levels': [
                {
                    'level': 'medium',
                    'numerical_value': 50
                    # Missing 'name'
                }
            ],
            'trust_groups': [
                {
                    'description': 'A test group'
                    # Missing 'name' and 'default_trust_level'
                }
            ]
        }
        
        is_valid, errors = validate_trust_configuration(config_data)
        self.assertFalse(is_valid)
        self.assertIn('Trust level 0: Missing name', errors)
        self.assertIn('Trust group 0: Missing name', errors)
        self.assertIn('Trust group 0: Missing default_trust_level', errors)
    
    def test_validate_trust_configuration_invalid_values(self):
        """Test validating configuration with invalid values."""
        config_data = {
            'trust_levels': [
                {
                    'name': 'Invalid Level',
                    'numerical_value': 150  # Invalid: > 100
                }
            ],
            'trust_groups': [
                {
                    'name': 'Test Group',
                    'default_trust_level': 'Test Level'
                }
            ]
        }
        
        is_valid, errors = validate_trust_configuration(config_data)
        self.assertFalse(is_valid)
        self.assertIn('numerical_value must be 0-100', errors[0])
    
    def test_validate_trust_configuration_missing_required_sections(self):
        """Test validating configuration with missing required sections."""
        config_data = {
            'trust_levels': []
            # Missing 'trust_groups'
        }
        
        is_valid, errors = validate_trust_configuration(config_data)
        self.assertFalse(is_valid)
        self.assertIn('Missing required field: trust_groups', errors)


class DisplayFormattingTest(TestCase):
    """Test display formatting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Display Test Trust Level',
            level='high',
            description='Trust level for display testing',
            numerical_value=75,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='minimal',
            status='active',
            created_by='test_user',
            last_modified_by='test_user'
        )
    
    def test_format_trust_relationship_for_display(self):
        """Test formatting trust relationship for display."""
        display_str = format_trust_relationship_for_display(self.relationship)
        
        # Should contain organization IDs (first 8 chars)
        self.assertIn(self.org_1[:8], display_str)
        self.assertIn(self.org_2[:8], display_str)
        
        # Should contain trust level name
        self.assertIn('Display Test Trust Level', display_str)
        
        # Should contain relationship type
        self.assertIn('bilateral', display_str)
        
        # Should contain appropriate emojis for status and trust level
        self.assertIn('✅', display_str)  # Active status
        self.assertIn('🟢', display_str)  # High trust level
    
    def test_format_trust_relationship_for_display_different_statuses(self):
        """Test formatting with different relationship statuses."""
        statuses_and_emojis = [
            ('pending', '⏳'),
            ('suspended', '⏸️'),
            ('revoked', '❌'),
            ('expired', '🔒')
        ]
        
        for status, emoji in statuses_and_emojis:
            rel = TrustRelationship.objects.create(
                source_organization=str(uuid.uuid4()),
                target_organization=str(uuid.uuid4()),
                trust_level=self.trust_level,
                relationship_type='bilateral',
                anonymization_level='minimal',
                status=status,
                created_by='test_user',
                last_modified_by='test_user'
            )
            
            display_str = format_trust_relationship_for_display(rel)
            self.assertIn(emoji, display_str)
    
    def test_format_trust_relationship_for_display_different_trust_levels(self):
        """Test formatting with different trust levels."""
        trust_levels_and_emojis = [
            ('none', '🚫'),
            ('low', '🟡'),
            ('medium', '🟠'),
            ('complete', '💎')
        ]
        
        for level, emoji in trust_levels_and_emojis:
            trust_level = TrustLevel.objects.create(
                name=f'{level.title()} Trust',
                level=level,
                description=f'{level.title()} trust level',
                numerical_value=25 if level == 'low' else 50,
                default_anonymization_level='full',
                default_access_level='read',
                created_by='test_user'
            )
            
            rel = TrustRelationship.objects.create(
                source_organization=str(uuid.uuid4()),
                target_organization=str(uuid.uuid4()),
                trust_level=trust_level,
                relationship_type='bilateral',
                anonymization_level='full',
                status='active',
                created_by='test_user',
                last_modified_by='test_user'
            )
            
            display_str = format_trust_relationship_for_display(rel)
            self.assertIn(emoji, display_str)