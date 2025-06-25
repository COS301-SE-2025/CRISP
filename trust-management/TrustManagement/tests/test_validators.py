"""
Comprehensive Test Suite for Trust Management Validators

This module tests all validator classes and functions to ensure proper validation
of trust operations, security checks, and input sanitization.
"""

import uuid
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta

from ..models import TrustLevel, TrustGroup, TrustRelationship, SharingPolicy
from ..validators import validate_trust_operation
# Import validator classes directly from the module to avoid circular imports
import TrustManagement.validators as validators_module


class TrustRelationshipValidatorTest(TestCase):
    """Test TrustRelationshipValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Test Trust Level',
            level='medium',
            description='Test trust level',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.user_1 = 'test_user_1'
    
    def test_validate_create_relationship_success(self):
        """Test successful relationship creation validation."""
        result = validators_module.TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['trust_level'], self.trust_level)
    
    def test_validate_create_relationship_invalid_uuid(self):
        """Test validation with invalid UUID."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org='invalid-uuid',
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Invalid source organization UUID', result['errors'][0])
    
    def test_validate_create_relationship_same_orgs(self):
        """Test validation with same source and target organizations."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_1,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Source and target organizations cannot be the same', result['errors'])
    
    def test_validate_create_relationship_invalid_trust_level(self):
        """Test validation with invalid trust level."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Non-existent Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Trust level', result['errors'][0])
        self.assertIn('not found or inactive', result['errors'][0])
    
    def test_validate_create_relationship_invalid_type(self):
        """Test validation with invalid relationship type."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='invalid_type'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Invalid relationship type', result['errors'][0])
    
    def test_validate_create_relationship_expired_date(self):
        """Test validation with expiration date in the past."""
        past_date = timezone.now() - timedelta(days=1)
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral',
            valid_until=past_date
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Expiration date must be in the future', result['errors'])
    
    def test_validate_create_relationship_duplicate(self):
        """Test validation with existing relationship."""
        # Create existing relationship
        TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            created_by=self.user_1,
            last_modified_by=self.user_1
        )
        
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Active trust relationship already exists', result['errors'][0])
    
    def test_validate_trust_level_constraints(self):
        """Test trust level constraint validation."""
        # Test community relationship with high trust warning
        high_trust_level = TrustLevel.objects.create(
            name='High Trust Level',
            level='high',
            description='High trust level',
            numerical_value=85,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        result = TrustRelationshipValidator.validate_trust_level_constraints(
            high_trust_level, 'community'
        )
        
        self.assertEqual(len(result['errors']), 0)
        self.assertTrue(any('High trust levels are unusual for community' in w for w in result['warnings']))
    
    def test_validate_approval_request_success(self):
        """Test successful approval validation."""
        relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            status='pending',
            created_by=self.user_1,
            last_modified_by=self.user_1
        )
        
        result = TrustRelationshipValidator.validate_approval_request(
            relationship_id=str(relationship.id),
            approving_org=self.org_1,
            approved_by_user=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['relationship'], relationship)
    
    def test_validate_approval_request_invalid_org(self):
        """Test approval validation with invalid organization."""
        relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            status='pending',
            created_by=self.user_1,
            last_modified_by=self.user_1
        )
        
        invalid_org = str(uuid.uuid4())
        result = TrustRelationshipValidator.validate_approval_request(
            relationship_id=str(relationship.id),
            approving_org=invalid_org,
            approved_by_user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Organization is not part of this trust relationship', result['errors'])
    
    def test_validate_revocation_request_success(self):
        """Test successful revocation validation."""
        relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            status='active',
            created_by=self.user_1,
            last_modified_by=self.user_1
        )
        
        result = TrustRelationshipValidator.validate_revocation_request(
            relationship_id=str(relationship.id),
            revoking_org=self.org_1,
            revoked_by_user=self.user_1,
            reason='Test revocation'
        )
        
        self.assertTrue(result['valid'])
        self.assertTrue(any('will immediately stop intelligence sharing' in w for w in result['warnings']))


class TrustGroupValidatorTest(TestCase):
    """Test TrustGroupValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Group Test Trust Level',
            level='medium',
            description='Test trust level for groups',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user',
            is_system_default=True
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
    
    def test_validate_create_group_success(self):
        """Test successful group creation validation."""
        result = TrustGroupValidator.validate_create_group(
            name='Test Group',
            description='A test trust group',
            creator_org=self.org_1,
            group_type='community',
            default_trust_level_name='Group Test Trust Level'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['trust_level'], self.trust_level)
    
    def test_validate_create_group_invalid_name(self):
        """Test validation with invalid group name."""
        result = TrustGroupValidator.validate_create_group(
            name='',
            description='A test trust group',
            creator_org=self.org_1,
            group_type='community'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Group name is required', result['errors'])
    
    def test_validate_create_group_long_name(self):
        """Test validation with too long group name."""
        long_name = 'x' * 300
        result = TrustGroupValidator.validate_create_group(
            name=long_name,
            description='A test trust group',
            creator_org=self.org_1,
            group_type='community'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Group name is too long', result['errors'][0])
    
    def test_validate_create_group_duplicate_name(self):
        """Test validation with duplicate group name."""
        # Create existing group
        TrustGroup.objects.create(
            name='Existing Group',
            description='An existing group',
            created_by=self.org_1
        )
        
        result = TrustGroupValidator.validate_create_group(
            name='Existing Group',
            description='A test trust group',
            creator_org=self.org_1,
            group_type='community'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Trust group with name', result['errors'][0])
    
    def test_validate_create_group_special_characters(self):
        """Test validation with special characters in name."""
        result = TrustGroupValidator.validate_create_group(
            name='Test@Group#$%',
            description='A test trust group',
            creator_org=self.org_1,
            group_type='community'
        )
        
        self.assertTrue(result['valid'])
        self.assertTrue(any('special characters' in w for w in result['warnings']))
    
    def test_validate_join_group_success(self):
        """Test successful group join validation."""
        group = TrustGroup.objects.create(
            name='Test Join Group',
            description='A test group for joining',
            created_by=self.org_1
        )
        
        result = TrustGroupValidator.validate_join_group(
            group_id=str(group.id),
            organization=self.org_2,
            membership_type='member'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['group'], group)
    
    def test_validate_join_group_invalid_org(self):
        """Test group join validation with invalid organization UUID."""
        group = TrustGroup.objects.create(
            name='Test Join Group',
            description='A test group for joining',
            created_by=self.org_1
        )
        
        result = TrustGroupValidator.validate_join_group(
            group_id=str(group.id),
            organization='invalid-uuid',
            membership_type='member'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Invalid organization UUID', result['errors'][0])


class AccessControlValidatorTest(TestCase):
    """Test AccessControlValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
    
    def test_validate_intelligence_access_success(self):
        """Test successful intelligence access validation."""
        result = AccessControlValidator.validate_intelligence_access(
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='read'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_intelligence_access_invalid_uuid(self):
        """Test intelligence access validation with invalid UUID."""
        result = AccessControlValidator.validate_intelligence_access(
            requesting_org='invalid-uuid',
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='read'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Invalid requesting organization UUID', result['errors'][0])
    
    def test_validate_intelligence_access_invalid_level(self):
        """Test intelligence access validation with invalid access level."""
        result = AccessControlValidator.validate_intelligence_access(
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='invalid_level'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Invalid access level', result['errors'][0])
    
    def test_validate_sharing_policy_success(self):
        """Test successful sharing policy validation."""
        policy_data = {
            'name': 'Test Policy',
            'description': 'A test sharing policy',
            'allowed_stix_types': ['indicator', 'malware'],
            'max_tlp_level': 'green',
            'max_age_days': 30
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_sharing_policy_missing_required(self):
        """Test sharing policy validation with missing required fields."""
        policy_data = {
            'description': 'A test sharing policy'
            # Missing 'name'
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_data)
        
        self.assertFalse(result['valid'])
        self.assertIn("Field 'name' is required", result['errors'])
    
    def test_validate_sharing_policy_conflicting_types(self):
        """Test sharing policy validation with conflicting STIX types."""
        policy_data = {
            'name': 'Test Policy',
            'description': 'A test sharing policy',
            'allowed_stix_types': ['indicator', 'malware'],
            'blocked_stix_types': ['indicator', 'attack-pattern']
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_data)
        
        self.assertFalse(result['valid'])
        self.assertIn('STIX types cannot be both allowed and blocked', result['errors'][0])


class SecurityValidatorTest(TestCase):
    """Test SecurityValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.org_1 = str(uuid.uuid4())
        self.user_1 = 'security_test_user'
        cache.clear()
    
    def test_validate_bulk_operations_success(self):
        """Test successful bulk operations validation."""
        result = SecurityValidator.validate_bulk_operations(
            operation_count=50,
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_bulk_operations_too_many(self):
        """Test bulk operations validation with too many operations."""
        result = SecurityValidator.validate_bulk_operations(
            operation_count=150,
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Bulk operations limited to 100 items', result['errors'][0])
    
    def test_validate_bulk_operations_warning_threshold(self):
        """Test bulk operations validation with warning threshold."""
        result = SecurityValidator.validate_bulk_operations(
            operation_count=75,
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertTrue(any('Large bulk operation' in w for w in result['warnings']))
    
    def test_validate_trust_escalation_minor(self):
        """Test trust escalation validation with minor increase."""
        low_trust = TrustLevel.objects.create(
            name='Low Trust',
            level='low',
            description='Low trust level',
            numerical_value=25,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_user'
        )
        
        medium_trust = TrustLevel.objects.create(
            name='Medium Trust',
            level='medium',
            description='Medium trust level',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        result = SecurityValidator.validate_trust_escalation(
            current_trust_level=low_trust,
            new_trust_level=medium_trust,
            justification='Increased cooperation'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['trust_increase'], 25)
    
    def test_validate_trust_escalation_major_no_justification(self):
        """Test trust escalation validation with major increase and no justification."""
        low_trust = TrustLevel.objects.create(
            name='Low Trust',
            level='low',
            description='Low trust level',
            numerical_value=20,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_user'
        )
        
        high_trust = TrustLevel.objects.create(
            name='High Trust',
            level='high',
            description='High trust level',
            numerical_value=80,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        result = SecurityValidator.validate_trust_escalation(
            current_trust_level=low_trust,
            new_trust_level=high_trust
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('requires detailed justification', result['errors'][0])
    
    def test_validate_input_sanitization_clean(self):
        """Test input sanitization with clean data."""
        clean_data = {
            'name': 'Test Organization',
            'description': 'A legitimate organization description',
            'contact_email': 'contact@example.com'
        }
        
        result = SecurityValidator.validate_input_sanitization(clean_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_input_sanitization_sql_injection(self):
        """Test input sanitization with SQL injection attempt."""
        malicious_data = {
            'name': "'; DROP TABLE users; --",
            'description': 'A legitimate description'
        }
        
        result = SecurityValidator.validate_input_sanitization(malicious_data)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('SQL injection' in error for error in result['errors']))
    
    def test_validate_input_sanitization_xss(self):
        """Test input sanitization with XSS attempt."""
        malicious_data = {
            'name': '<script>alert("xss")</script>',
            'description': 'A legitimate description'
        }
        
        result = SecurityValidator.validate_input_sanitization(malicious_data)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('XSS' in error for error in result['errors']))
    
    def test_validate_input_sanitization_command_injection(self):
        """Test input sanitization with command injection attempt."""
        malicious_data = {
            'name': 'test; rm -rf /',
            'description': 'A legitimate description'
        }
        
        result = SecurityValidator.validate_input_sanitization(malicious_data)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Command injection' in error for error in result['errors']))
    
    def test_validate_input_sanitization_very_long_input(self):
        """Test input sanitization with very long input."""
        long_data = {
            'name': 'x' * 15000,
            'description': 'A legitimate description'
        }
        
        result = SecurityValidator.validate_input_sanitization(long_data)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('exceeds maximum length' in error for error in result['errors']))
    
    @override_settings(TRUST_MANAGEMENT_SECRET_KEY='test-secret-key')
    def test_validate_cryptographic_integrity_valid_signature(self):
        """Test cryptographic integrity validation with valid signature."""
        import hmac
        import hashlib
        
        data = {'test': 'data', 'value': 123}
        key = 'test-secret-key'
        message = str(sorted(data.items())).encode('utf-8')
        signature = hmac.new(key.encode('utf-8'), message, hashlib.sha256).hexdigest()
        
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            signature=signature,
            key=key
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    @override_settings(TRUST_MANAGEMENT_SECRET_KEY='test-secret-key')
    def test_validate_cryptographic_integrity_invalid_signature(self):
        """Test cryptographic integrity validation with invalid signature."""
        data = {'test': 'data', 'value': 123}
        invalid_signature = 'invalid_signature_hash'
        
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            signature=invalid_signature
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('HMAC signature verification failed', result['errors'])
    
    def test_validate_temporal_security_valid(self):
        """Test temporal security validation with valid timestamp."""
        current_time = time.time()
        
        result = SecurityValidator.validate_temporal_security(
            timestamp=current_time,
            max_age_minutes=5
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_temporal_security_too_old(self):
        """Test temporal security validation with old timestamp."""
        old_time = time.time() - 600  # 10 minutes ago
        
        result = SecurityValidator.validate_temporal_security(
            timestamp=old_time,
            max_age_minutes=5
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Request too old', result['errors'][0])
    
    def test_validate_temporal_security_future(self):
        """Test temporal security validation with future timestamp."""
        future_time = time.time() + 120  # 2 minutes in the future
        
        result = SecurityValidator.validate_temporal_security(
            timestamp=future_time,
            max_age_minutes=5
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('timestamp is in the future', result['errors'][0])
    
    def test_validate_rate_limiting_normal(self):
        """Test rate limiting validation under normal conditions."""
        result = SecurityValidator.validate_rate_limiting(
            operation_type='create_relationship',
            user=self.user_1,
            organization=self.org_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['current_count'], 0)
    
    def test_record_operation(self):
        """Test operation recording functionality."""
        # This should not raise any exceptions
        SecurityValidator.record_operation(
            operation_type='create_relationship',
            user=self.user_1,
            organization=self.org_1
        )
        
        # Verify operation was recorded by checking rate limiting
        result = SecurityValidator.validate_rate_limiting(
            operation_type='create_relationship',
            user=self.user_1,
            organization=self.org_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['current_count'], 1)


class ValidateTrustOperationTest(TestCase):
    """Test the main validate_trust_operation function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Operation Test Trust Level',
            level='medium',
            description='Test trust level for operations',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.user_1 = 'operation_test_user'
        cache.clear()
    
    def test_validate_trust_operation_create_relationship(self):
        """Test main validation function for create_relationship operation."""
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Operation Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['trust_level'], self.trust_level)
    
    def test_validate_trust_operation_unknown_type(self):
        """Test main validation function with unknown operation type."""
        result = validate_trust_operation(
            'unknown_operation',
            source_org=self.org_1,
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Unknown operation type', result['errors'][0])
    
    def test_validate_trust_operation_malicious_input(self):
        """Test main validation function with malicious input."""
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name="'; DROP TABLE trust_levels; --",
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('SQL injection' in error for error in result['errors']))
    
    @patch('TrustManagement.validators.logger')
    def test_validate_trust_operation_logging(self, mock_logger):
        """Test that validation errors are logged properly."""
        validate_trust_operation(
            'create_relationship',
            source_org='invalid-uuid',
            target_org=self.org_2,
            trust_level_name='Operation Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        # Verify logging was called
        self.assertTrue(mock_logger.warning.called)
    
    @patch('TrustManagement.validators.getattr')
    def test_validate_trust_operation_exception_handling(self, mock_getattr):
        """Test exception handling in validation function."""
        # Mock getattr to raise an exception
        mock_getattr.side_effect = Exception('Test exception')
        
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            created_by=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Validation error' in error for error in result['errors']))


class ValidatorIntegrationTest(TestCase):
    """Integration tests for validator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Integration Test Trust Level',
            level='medium',
            description='Test trust level for integration',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.group = TrustGroup.objects.create(
            name='Integration Test Group',
            description='Test group for integration',
            default_trust_level=self.trust_level,
            created_by=str(uuid.uuid4())
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.user_1 = 'integration_test_user'
        cache.clear()
    
    def test_end_to_end_relationship_validation(self):
        """Test end-to-end relationship creation validation."""
        # Test create validation
        create_result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Integration Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertTrue(create_result['valid'])
        
        # Create the relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            status='pending',
            created_by=self.user_1,
            last_modified_by=self.user_1
        )
        
        # Test approval validation
        approve_result = validate_trust_operation(
            'approve_relationship',
            relationship_id=str(relationship.id),
            approving_org=self.org_1,
            approved_by_user=self.user_1,
            user=self.user_1
        )
        
        self.assertTrue(approve_result['valid'])
        
        # Test revocation validation
        revoke_result = validate_trust_operation(
            'revoke_relationship',
            relationship_id=str(relationship.id),
            revoking_org=self.org_1,
            revoked_by_user=self.user_1,
            reason='Test revocation',
            user=self.user_1
        )
        
        self.assertTrue(revoke_result['valid'])
    
    def test_comprehensive_security_validation(self):
        """Test comprehensive security validation across multiple operations."""
        operations = [
            ('create_relationship', {
                'source_org': self.org_1,
                'target_org': self.org_2,
                'trust_level_name': 'Integration Test Trust Level',
                'relationship_type': 'bilateral',
                'created_by': self.user_1
            }),
            ('create_group', {
                'name': 'Security Test Group',
                'description': 'A group for security testing',
                'creator_org': self.org_1,
                'group_type': 'community',
                'user': self.user_1
            }),
            ('intelligence_access', {
                'requesting_org': self.org_1,
                'intelligence_owner': self.org_2,
                'resource_type': 'indicator',
                'required_access_level': 'read',
                'user': self.user_1
            })
        ]
        
        for operation_type, kwargs in operations:
            result = validate_trust_operation(operation_type, **kwargs)
            # Each operation should be valid individually
            self.assertTrue(result['valid'], f"Operation {operation_type} failed validation")