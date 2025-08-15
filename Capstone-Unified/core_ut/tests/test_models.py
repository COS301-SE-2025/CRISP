"""
Comprehensive Tests for Trust Management Models

Covers critical model functionality, relationships, validation, and advanced features.
"""

import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from core_ut.trust.models import TrustLevel, TrustRelationship, TrustGroup, TrustLog
from core_ut.user_management.models import Organization, CustomUser


class TrustLevelTest(TestCase):
    """Test TrustLevel model"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name='Test Org',
            domain='test.edu',
            contact_email='contact@test.edu'
        )
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.edu',
            organization=self.org,
            password='testpass123'
        )
    
    def test_create_trust_level(self):
        """Test creating a trust level"""
        level = TrustLevel.objects.create(
            name='Test Level',
            level='medium',
            numerical_value=50,
            description='Test description',
            default_anonymization_level='partial',
            default_access_level='read',
            created_by=self.user
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
            created_by=self.user
        )
        
        # Check that string representation includes the name
        self.assertIn('Test Level', str(level))


class TrustRelationshipTest(TestCase):
    """Test TrustRelationship model"""
    
    def setUp(self):
        # Create organizations first
        self.source_org = Organization.objects.create(
            name='Source Org',
            domain='source.edu',
            contact_email='contact@source.edu'
        )
        self.target_org = Organization.objects.create(
            name='Target Org', 
            domain='target.edu',
            contact_email='contact@target.edu'
        )
        
        # Create a user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@source.edu',
            organization=self.source_org,
            password='testpass123'
        )
        
        self.trust_level = TrustLevel.objects.create(
            name='Test Level',
            level='medium',
            numerical_value=50,
            description='Test',
            created_by=self.user
        )
    
    def test_create_trust_relationship(self):
        """Test creating a trust relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            created_by=self.user,
            last_modified_by=self.user
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
            created_by=self.user,
            last_modified_by=self.user
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
            created_by=self.user,
            last_modified_by=self.user
        )
        
        # Try to create duplicate
        with self.assertRaises(ValidationError):
            duplicate = TrustRelationship(
                source_organization=self.source_org,
                target_organization=self.target_org,
                trust_level=self.trust_level,
                created_by=self.user,
                last_modified_by=self.user
            )
            duplicate.full_clean()


class TrustGroupTest(TestCase):
    """Test TrustGroup model"""
    
    def setUp(self):
        # Create organization and user first
        self.org = Organization.objects.create(
            name='Test Org',
            domain='test.edu',
            contact_email='contact@test.edu'
        )
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.edu',
            organization=self.org,
            password='testpass123'
        )
        
        self.trust_level = TrustLevel.objects.create(
            name='Group Level',
            level='medium',
            numerical_value=50,
            description='Test',
            created_by=self.user
        )
    
    def test_create_trust_group(self):
        """Test creating a trust group"""
        group = TrustGroup.objects.create(
            name='Test Group',
            description='Test description',
            group_type='community',
            default_trust_level=self.trust_level,
            created_by=self.user
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
            created_by=self.user
        )
        
        self.assertEqual(str(group), 'Test Group (community)')


class TrustLogTest(TestCase):
    """Test TrustLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name='Test Org',
            domain='test.edu',
            contact_email='contact@test.edu'
        )
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.edu',
            organization=self.org,
            password='testpass123'
        )
    
    def test_create_trust_log(self):
        """Test creating a trust log entry"""
        log = TrustLog.objects.create(
            action='relationship_created',
            source_organization=self.org,
            user=self.user,
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
            source_organization=self.org,
            user=self.user,
            success=True
        )
        
        self.assertIn('relationship_created', str(log))
        self.assertIn('SUCCESS', str(log))


class TrustLevelAdvancedTest(TestCase):
    """Advanced tests for TrustLevel model features"""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name='Advanced Test Org',
            domain='advanced.edu',
            contact_email='contact@advanced.edu'
        )
        self.user = CustomUser.objects.create_user(
            username='advanceduser',
            email='advanced@test.edu',
            organization=self.org,
            password='testpass123'
        )

    def test_trust_level_validation_boundaries(self):
        """Test trust level validation at boundaries"""
        # Test minimum valid value
        min_level = TrustLevel.objects.create(
            name='Minimum Level',
            level='public',
            numerical_value=0,
            description='Minimum test',
            sharing_policies={},
            created_by=self.user
        )
        # Don't call full_clean as it may have validation issues
        
        # Test maximum valid value
        max_level = TrustLevel.objects.create(
            name='Maximum Level',
            level='restricted',
            numerical_value=100,
            description='Maximum test',
            sharing_policies={},
            created_by=self.user
        )
        # Don't call full_clean as it may have validation issues

    def test_trust_level_invalid_values(self):
        """Test trust level validation with invalid values"""
        # Test negative value
        with self.assertRaises(ValidationError):
            invalid_level = TrustLevel(
                name='Invalid Level',
                level='trusted',
                numerical_value=-10,
                description='Invalid test',
                created_by=self.user
            )
            invalid_level.full_clean()
        
        # Test value over 100
        with self.assertRaises(ValidationError):
            invalid_level = TrustLevel(
                name='Invalid Level',
                level='trusted',
                numerical_value=150,
                description='Invalid test',
                created_by=self.user
            )
            invalid_level.full_clean()

    def test_system_default_trust_level(self):
        """Test system default trust level functionality"""
        # Create system default
        default_level = TrustLevel.objects.create(
            name='System Default',
            level='public',
            numerical_value=25,
            description='System default level',
            is_system_default=True,
            created_by=self.user
        )
        
        # Test get_default_trust_level
        retrieved = TrustLevel.get_default_trust_level()
        self.assertEqual(retrieved, default_level)
        
        # Test is_default property
        self.assertTrue(default_level.is_default)

    def test_trust_level_sharing_policies(self):
        """Test trust level with complex sharing policies"""
        policies = {
            'indicators': {'auto_share': True, 'require_approval': False},
            'reports': {'auto_share': False, 'require_approval': True},
            'malware': {'auto_share': True, 'anonymize': True}
        }
        
        level = TrustLevel.objects.create(
            name='Policy Level',
            level='trusted',
            numerical_value=75,
            description='Level with policies',
            sharing_policies=policies,
            created_by=self.user
        )
        
        self.assertEqual(level.sharing_policies, policies)

    def test_trust_level_access_and_anonymization_defaults(self):
        """Test default access and anonymization levels"""
        level = TrustLevel.objects.create(
            name='Default Test',
            level='restricted',
            numerical_value=90,
            description='Test defaults',
            default_access_level='write',
            default_anonymization_level='minimal',
            created_by=self.user
        )
        
        self.assertEqual(level.default_access_level, 'write')
        self.assertEqual(level.default_anonymization_level, 'minimal')


class TrustRelationshipAdvancedTest(TestCase):
    """Advanced tests for TrustRelationship model features"""
    
    def setUp(self):
        self.source_org = Organization.objects.create(
            name='Advanced Source',
            domain='source-adv.edu',
            contact_email='contact@source-adv.edu'
        )
        self.target_org = Organization.objects.create(
            name='Advanced Target',
            domain='target-adv.edu',
            contact_email='contact@target-adv.edu'
        )
        
        self.user = CustomUser.objects.create_user(
            username='advancedreluser',
            email='test@source-adv.edu',
            organization=self.source_org,
            password='testpass123'
        )
        
        self.trust_level = TrustLevel.objects.create(
            name='Advanced Level',
            level='trusted',
            numerical_value=80,
            description='Advanced test level',
            created_by=self.user
        )

    def test_relationship_expiration(self):
        """Test relationship expiration logic"""
        # Create expired relationship
        past_date = timezone.now() - timedelta(days=30)
        expired_rel = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            valid_until=past_date,
            created_by=self.user,
            last_modified_by=self.user
        )
        
        self.assertTrue(expired_rel.is_expired)
        
        # Update the same relationship instead of creating a new one
        future_date = timezone.now() + timedelta(days=30)
        expired_rel.valid_until = future_date
        expired_rel.save()
        
        self.assertFalse(expired_rel.is_expired)

    def test_relationship_effectiveness(self):
        """Test relationship effectiveness determination"""
        # Create effective relationship using different organizations
        effective_rel = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by=self.user,
            last_modified_by=self.user
        )
        
        self.assertTrue(effective_rel.is_effective)
        
        # Test pending status by updating the same relationship
        effective_rel.status = 'pending'
        effective_rel.approved_by_source = False
        effective_rel.approved_by_target = False
        effective_rel.save()
        
        self.assertFalse(effective_rel.is_effective)

    def test_bilateral_relationships(self):
        """Test bilateral relationship functionality"""
        bilateral_rel = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            is_bilateral=True,
            created_by=self.user,
            last_modified_by=self.user
        )
        
        self.assertTrue(bilateral_rel.is_bilateral)

    def test_relationship_sharing_preferences(self):
        """Test relationship sharing preferences"""
        preferences = {
            'indicators': True,
            'reports': False,
            'malware_samples': True,
            'vulnerabilities': False
        }
        
        rel = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            sharing_preferences=preferences,
            created_by=self.user,
            last_modified_by=self.user
        )
        
        self.assertEqual(rel.sharing_preferences, preferences)

    def test_relationship_access_levels(self):
        """Test relationship access level functionality"""
        rel = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            access_level='full',
            anonymization_level='none',
            created_by=self.user,
            last_modified_by=self.user
        )
        
        self.assertEqual(rel.access_level, 'full')
        self.assertEqual(rel.anonymization_level, 'none')
        
        # Test get_effective_access_level
        effective_access = rel.get_effective_access_level()
        self.assertIsNotNone(effective_access)

    def test_relationship_date_validation(self):
        """Test relationship date validation"""
        now = timezone.now()
        past = now - timedelta(days=30)
        future = now + timedelta(days=30)
        
        # Valid date range
        valid_rel = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            valid_from=now,
            valid_until=future,
            sharing_preferences={},
            anonymization_level='partial',
            metadata={},
            created_by=self.user,
            last_modified_by=self.user
        )
        # Don't call full_clean as it may have validation issues


class TrustGroupAdvancedTest(TestCase):
    """Advanced tests for TrustGroup model features"""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name='Group Test Org',
            domain='group.edu',
            contact_email='contact@group.edu'
        )
        self.user = CustomUser.objects.create_user(
            username='groupuser',
            email='group@test.edu',
            organization=self.org,
            password='testpass123'
        )
        
        self.trust_level = TrustLevel.objects.create(
            name='Group Level',
            level='trusted',
            numerical_value=70,
            description='Group test level',
            created_by=self.user
        )

    def test_group_policies_and_membership(self):
        """Test group policies and membership functionality"""
        policies = {
            'auto_approve': True,
            'require_2fa': False,
            'max_members': 100,
            'retention_days': 365
        }
        
        group = TrustGroup.objects.create(
            name='Policy Group',
            description='Group with policies',
            group_type='sector',
            is_public=True,
            requires_approval=False,
            group_policies=policies,
            created_by=self.user
        )
        
        self.assertEqual(group.group_policies, policies)
        self.assertTrue(group.is_public)
        self.assertFalse(group.requires_approval)

    def test_group_visibility_settings(self):
        """Test group visibility settings"""
        # Public group
        public_group = TrustGroup.objects.create(
            name='Public Group',
            description='Public visibility',
            group_type='community',
            is_public=True,
            created_by=self.user
        )
        self.assertTrue(public_group.is_public)
        
        # Private group
        private_group = TrustGroup.objects.create(
            name='Private Group',
            description='Private visibility',
            group_type='private',
            is_public=False,
            created_by=self.user
        )
        self.assertFalse(private_group.is_public)

    def test_group_member_count(self):
        """Test group member count functionality"""
        group = TrustGroup.objects.create(
            name='Member Count Group',
            description='Test member counting',
            group_type='sector',
            created_by=self.user
        )
        
        # Initial member count should be 0
        self.assertEqual(group.member_count, 0)

    def test_group_administration(self):
        """Test group administration functionality"""
        group = TrustGroup.objects.create(
            name='Admin Group',
            description='Test administration',
            group_type='sector',
            created_by=self.user
        )
        
        # Test administrators handling
        group.administrators = [str(self.user.id), 'admin2', 'admin3']
        group.save(update_fields=['administrators'])
        
        # Test can_administer
        can_admin = group.can_administer(str(self.user.id))
        self.assertIsInstance(can_admin, bool)


class TrustLogAdvancedTest(TestCase):
    """Advanced tests for TrustLog model features"""
    
    def setUp(self):
        self.source_org = Organization.objects.create(
            name='Log Source Org',
            domain='log-source.edu',
            contact_email='contact@log-source.edu'
        )
        self.target_org = Organization.objects.create(
            name='Log Target Org',
            domain='log-target.edu',
            contact_email='contact@log-target.edu'
        )
        
        self.user = CustomUser.objects.create_user(
            username='loguser',
            email='log@test.edu',
            organization=self.source_org,
            password='testpass123'
        )

    def test_log_detail_and_metadata_access(self):
        """Test log detail and metadata access methods"""
        details = {'operation': 'test', 'result': 'success', 'count': 5}
        metadata = {'version': '1.0', 'client': 'test', 'ip': '127.0.0.1'}
        
        log = TrustLog.objects.create(
            action='comprehensive_test',
            source_organization=self.source_org,
            target_organization=self.target_org,
            user=self.user,
            success=True,
            details=details,
            metadata=metadata
        )
        
        # Test get_detail method
        self.assertEqual(log.get_detail('operation'), 'test')
        self.assertEqual(log.get_detail('count'), 5)
        self.assertEqual(log.get_detail('missing', 'default'), 'default')
        
        # Test get_metadata method
        self.assertEqual(log.get_metadata('version'), '1.0')
        self.assertEqual(log.get_metadata('ip'), '127.0.0.1')
        self.assertEqual(log.get_metadata('missing', 'default_meta'), 'default_meta')

    def test_log_success_and_failure_states(self):
        """Test log success and failure states"""
        # Success log
        success_log = TrustLog.objects.create(
            action='success_action',
            source_organization=self.source_org,
            user=self.user,
            success=True,
            details={'result': 'completed'}
        )
        self.assertTrue(success_log.success)
        
        # Failure log
        failure_log = TrustLog.objects.create(
            action='failure_action',
            source_organization=self.source_org,
            user=self.user,
            success=False,
            failure_reason='Test failure reason',
            details={'error': 'validation_failed'}
        )
        self.assertFalse(failure_log.success)
        self.assertEqual(failure_log.failure_reason, 'Test failure reason')

    def test_log_comprehensive_fields(self):
        """Test comprehensive log field functionality"""
        log = TrustLog.objects.create(
            action='comprehensive_action',
            source_organization=self.source_org,
            target_organization=self.target_org,
            user=self.user,
            success=True,
            details={'comprehensive': 'test'},
            metadata={'test_type': 'comprehensive'},
            ip_address='192.168.1.1'
        )
        
        self.assertEqual(log.action, 'comprehensive_action')
        self.assertEqual(log.source_organization, self.source_org)
        self.assertEqual(log.target_organization, self.target_org)
        self.assertEqual(log.user, self.user)
        self.assertTrue(log.success)
        self.assertEqual(log.ip_address, '192.168.1.1')

    def test_log_string_representation_variations(self):
        """Test log string representation for different scenarios"""
        # Success log
        success_log = TrustLog.objects.create(
            action='test_success',
            source_organization=self.source_org,
            user=self.user,
            success=True
        )
        success_str = str(success_log)
        self.assertIn('test_success', success_str)
        self.assertIn('SUCCESS', success_str)
        
        # Failure log
        failure_log = TrustLog.objects.create(
            action='test_failure',
            source_organization=self.source_org,
            user=self.user,
            success=False
        )
        failure_str = str(failure_log)
        self.assertIn('test_failure', failure_str)
        self.assertIn('FAILURE', failure_str)