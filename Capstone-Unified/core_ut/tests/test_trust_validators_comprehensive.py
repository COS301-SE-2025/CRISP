"""
Comprehensive tests for trust validators to improve coverage.
"""
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.utils import timezone
from unittest.mock import patch, Mock
from datetime import datetime, timedelta, time
import uuid
import hashlib
import hmac

from core_ut.trust.validators import (
    TrustRelationshipValidator,
    TrustGroupValidator,
    SecurityValidator,
    AccessControlValidator,
    validate_trust_operation
)


class TrustRelationshipValidatorTest(TestCase):
    """Comprehensive tests for TrustRelationshipValidator."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_org_id1 = str(uuid.uuid4())
        self.valid_org_id2 = str(uuid.uuid4())
        self.valid_relationship_id = str(uuid.uuid4())
        self.valid_user = "test_user"
    
    def test_validate_create_relationship_success(self):
        """Test successful validation of relationship creation."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.valid_org_id1,
            target_org=self.valid_org_id2,
            trust_level_name="medium",
            created_by=self.valid_user
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_create_relationship_missing_orgs(self):
        """Test validation failure when organizations are missing."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org="",
            target_org=None,
            trust_level_name="medium",
            created_by=self.valid_user
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Source and target organizations are required", result['errors'])
    
    def test_validate_create_relationship_same_org(self):
        """Test validation failure when source and target are same."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.valid_org_id1,
            target_org=self.valid_org_id1,
            trust_level_name="medium",
            created_by=self.valid_user
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Cannot create trust relationship with same organization", result['errors'])
    
    def test_validate_create_relationship_missing_trust_level(self):
        """Test validation failure when trust level is missing."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.valid_org_id1,
            target_org=self.valid_org_id2,
            trust_level_name="",
            created_by=self.valid_user
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Trust level is required", result['errors'])
    
    def test_validate_create_relationship_missing_created_by(self):
        """Test validation failure when created_by is missing."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.valid_org_id1,
            target_org=self.valid_org_id2,
            trust_level_name="medium",
            created_by=""
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Created by user is required", result['errors'])
    
    def test_validate_create_relationship_invalid_uuid(self):
        """Test validation failure with invalid UUIDs."""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org="invalid-uuid",
            target_org="also-invalid",
            trust_level_name="medium",
            created_by=self.valid_user
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any("Invalid organization UUID" in error for error in result['errors']))
    
    def test_validate_approve_relationship_success(self):
        """Test successful validation of relationship approval."""
        result = TrustRelationshipValidator.validate_approve_relationship(
            relationship_id=self.valid_relationship_id,
            approving_org=self.valid_org_id1,
            approved_by=self.valid_user
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_approve_relationship_missing_fields(self):
        """Test validation failure when required fields are missing."""
        result = TrustRelationshipValidator.validate_approve_relationship(
            relationship_id="",
            approving_org="",
            approved_by=""
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Relationship ID is required", result['errors'])
        self.assertIn("Approving organization is required", result['errors'])
        self.assertIn("Approved by user is required", result['errors'])
    
    def test_validate_approve_relationship_invalid_ids(self):
        """Test validation failure with invalid IDs."""
        result = TrustRelationshipValidator.validate_approve_relationship(
            relationship_id="invalid-id",
            approving_org="invalid-org",
            approved_by=self.valid_user
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Invalid relationship ID", result['errors'])
        self.assertIn("Invalid approving organization UUID", result['errors'])
    
    def test_validate_revoke_relationship_success(self):
        """Test successful validation of relationship revocation."""
        result = TrustRelationshipValidator.validate_revoke_relationship(
            relationship_id=self.valid_relationship_id,
            revoking_org=self.valid_org_id1,
            revoked_by=self.valid_user,
            reason="Security concern"
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_revoke_relationship_missing_fields(self):
        """Test validation failure when required fields are missing."""
        result = TrustRelationshipValidator.validate_revoke_relationship(
            relationship_id="",
            revoking_org="",
            revoked_by=""
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Relationship ID is required", result['errors'])
        self.assertIn("Revoking organization is required", result['errors'])
        self.assertIn("Revoked by user is required", result['errors'])
    
    def test_validate_revoke_relationship_invalid_ids(self):
        """Test validation failure with invalid IDs."""
        result = TrustRelationshipValidator.validate_revoke_relationship(
            relationship_id="invalid-id",
            revoking_org="invalid-org",
            revoked_by=self.valid_user
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Invalid relationship ID", result['errors'])
        self.assertIn("Invalid revoking organization UUID", result['errors'])


class TrustGroupValidatorTest(TestCase):
    """Comprehensive tests for TrustGroupValidator."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_org_id = str(uuid.uuid4())
        self.valid_group_id = str(uuid.uuid4())
    
    def test_validate_create_group_success(self):
        """Test successful validation of group creation."""
        result = TrustGroupValidator.validate_create_group(
            name="Valid Group Name",
            description="This is a valid group description that is long enough",
            creator_org=self.valid_org_id,
            group_type="community"
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_create_group_short_name(self):
        """Test validation failure with short group name."""
        result = TrustGroupValidator.validate_create_group(
            name="AB",
            description="Valid description that is long enough",
            creator_org=self.valid_org_id
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Group name must be at least 3 characters", result['errors'])
    
    def test_validate_create_group_whitespace_name(self):
        """Test validation failure with whitespace-only name."""
        result = TrustGroupValidator.validate_create_group(
            name="   ",
            description="Valid description that is long enough",
            creator_org=self.valid_org_id
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Group name must be at least 3 characters", result['errors'])
    
    def test_validate_create_group_short_description(self):
        """Test validation failure with short description."""
        result = TrustGroupValidator.validate_create_group(
            name="Valid Name",
            description="Too short",
            creator_org=self.valid_org_id
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Group description must be at least 10 characters", result['errors'])
    
    def test_validate_create_group_missing_creator(self):
        """Test validation failure with missing creator organization."""
        result = TrustGroupValidator.validate_create_group(
            name="Valid Name",
            description="Valid description that is long enough",
            creator_org=""
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Creator organization is required", result['errors'])
    
    def test_validate_create_group_invalid_creator_uuid(self):
        """Test validation failure with invalid creator organization UUID."""
        result = TrustGroupValidator.validate_create_group(
            name="Valid Name",
            description="Valid description that is long enough",
            creator_org="invalid-uuid"
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Invalid creator organization UUID", result['errors'])
    
    def test_validate_create_group_invalid_type(self):
        """Test validation failure with invalid group type."""
        result = TrustGroupValidator.validate_create_group(
            name="Valid Name",
            description="Valid description that is long enough",
            creator_org=self.valid_org_id,
            group_type="invalid_type"
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any("Invalid group type" in error for error in result['errors']))
    
    def test_validate_create_group_valid_types(self):
        """Test validation success with all valid group types."""
        valid_types = ['sector', 'geography', 'purpose', 'custom', 'community']
        
        for group_type in valid_types:
            result = TrustGroupValidator.validate_create_group(
                name="Valid Name",
                description="Valid description that is long enough",
                creator_org=self.valid_org_id,
                group_type=group_type
            )
            self.assertTrue(result['valid'], f"Failed for group type: {group_type}")
    
    def test_validate_join_group_success(self):
        """Test successful validation of group joining."""
        result = TrustGroupValidator.validate_join_group(
            group_id=self.valid_group_id,
            organization=self.valid_org_id,
            membership_type="member",
            joined_by="test_user"
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_join_group_missing_fields(self):
        """Test validation failure with missing required fields."""
        result = TrustGroupValidator.validate_join_group(
            group_id="",
            organization=""
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Group ID is required", result['errors'])
        self.assertIn("Organization is required", result['errors'])
    
    def test_validate_join_group_invalid_ids(self):
        """Test validation failure with invalid IDs."""
        result = TrustGroupValidator.validate_join_group(
            group_id="invalid-group-id",
            organization="invalid-org-id"
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Invalid group ID", result['errors'])
        self.assertIn("Invalid organization UUID", result['errors'])
    
    def test_validate_join_group_invalid_membership_type(self):
        """Test validation failure with invalid membership type."""
        result = TrustGroupValidator.validate_join_group(
            group_id=self.valid_group_id,
            organization=self.valid_org_id,
            membership_type="invalid_type"
        )
        
        self.assertFalse(result['valid'])
        self.assertTrue(any("Invalid membership type" in error for error in result['errors']))
    
    def test_validate_join_group_valid_membership_types(self):
        """Test validation success with all valid membership types."""
        valid_types = ['admin', 'member', 'observer']
        
        for membership_type in valid_types:
            result = TrustGroupValidator.validate_join_group(
                group_id=self.valid_group_id,
                organization=self.valid_org_id,
                membership_type=membership_type
            )
            self.assertTrue(result['valid'], f"Failed for membership type: {membership_type}")


class AccessControlValidatorTest(TestCase):
    """Comprehensive tests for AccessControlValidator."""
    
    def test_validate_sharing_policy_success(self):
        """Test successful validation of sharing policy."""
        policy_config = {
            'name': 'Test Policy',
            'trust_level_id': str(uuid.uuid4()),
            'resource_types': ['indicator', 'malware'],
            'allowed_actions': ['read', 'download']
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_config)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_sharing_policy_missing_required_fields(self):
        """Test validation failure with missing required fields."""
        policy_config = {
            'name': 'Test Policy'
            # Missing trust_level_id and resource_types
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_config)
        
        self.assertFalse(result['valid'])
        self.assertIn("Missing required field: trust_level_id", result['errors'])
        self.assertIn("Missing required field: resource_types", result['errors'])
    
    def test_validate_sharing_policy_invalid_resource_types(self):
        """Test validation failure with invalid resource types."""
        policy_config = {
            'name': 'Test Policy',
            'trust_level_id': str(uuid.uuid4()),
            'resource_types': ['indicator', 'invalid_type', 'malware', 'another_invalid']
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_config)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any("Invalid resource types" in error for error in result['errors']))
        error_msg = [e for e in result['errors'] if "Invalid resource types" in e][0]
        self.assertIn("invalid_type", error_msg)
        self.assertIn("another_invalid", error_msg)
    
    def test_validate_sharing_policy_invalid_actions(self):
        """Test validation failure with invalid actions."""
        policy_config = {
            'name': 'Test Policy',
            'trust_level_id': str(uuid.uuid4()),
            'resource_types': ['indicator'],
            'allowed_actions': ['read', 'invalid_action', 'download', 'another_invalid']
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_config)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any("Invalid actions" in error for error in result['errors']))
        error_msg = [e for e in result['errors'] if "Invalid actions" in e][0]
        self.assertIn("invalid_action", error_msg)
        self.assertIn("another_invalid", error_msg)
    
    def test_validate_sharing_policy_valid_resource_types(self):
        """Test validation success with all valid resource types."""
        valid_types = ['indicator', 'malware', 'attack-pattern', 'vulnerability', 'report']
        
        policy_config = {
            'name': 'Test Policy',
            'trust_level_id': str(uuid.uuid4()),
            'resource_types': valid_types
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_config)
        self.assertTrue(result['valid'])
    
    def test_validate_sharing_policy_valid_actions(self):
        """Test validation success with all valid actions."""
        valid_actions = ['read', 'download', 'share', 'modify', 'delete']
        
        policy_config = {
            'name': 'Test Policy',
            'trust_level_id': str(uuid.uuid4()),
            'resource_types': ['indicator'],
            'allowed_actions': valid_actions
        }
        
        result = AccessControlValidator.validate_sharing_policy(policy_config)
        self.assertTrue(result['valid'])


class SecurityValidatorTest(TestCase):
    """Comprehensive tests for SecurityValidator."""
    
    def setUp(self):
        self.validator = SecurityValidator()  # Create instance
        cache.clear()  # Clear cache before each test
    
    def tearDown(self):
        """Clean up after each test."""
        cache.clear()
    
    def test_validate_input_sanitization_clean_input(self):
        """Test input sanitization with clean input."""
        input_data = {
            'name': 'Clean Name',
            'description': 'Clean description'
        }
        
        result = self.validator.validate_input_sanitization(input_data)  # Use instance
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['sanitized_data']['name'], 'Clean Name')
    
    def test_validate_input_sanitization_dangerous_chars(self):
        """Test input sanitization removes dangerous characters."""
        input_data = {
            'name': 'Name with <script>alert("xss")</script>',
            'description': 'Clean description'
        }
        
        result = self.validator.validate_input_sanitization(input_data)  # Use instance
        
        self.assertFalse(result['valid'])
    
    def test_validate_input_sanitization_script_injection(self):
        """Test detection of script injection attempts."""
        input_data = {
            'malicious1': '<script>alert("xss")</script>',
            'malicious2': 'javascript:alert("xss")',
            'malicious3': 'data:text/html,<script>alert("xss")</script>',
            'clean': 'This is clean'
        }
        
        result = SecurityValidator.validate_input_sanitization(input_data)
        
        self.assertFalse(result['valid'])
        self.assertEqual(len(result['errors']), 3)
        for i in range(1, 4):
            self.assertTrue(any(f"malicious{i}" in error for error in result['errors']))
    
    def test_validate_rate_limiting_under_limit(self):
        """Test rate limiting when under the limit."""
        result = self.validator.validate_rate_limiting(
            user_id='user123',
            action='create_trust',  # Changed from 'operation'
            limit=5,
            window=60
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['current_count'], 1)
        self.assertEqual(result['limit'], 5)
    
    @patch('core.trust.validators.cache')
    def test_validate_rate_limiting_over_limit(self, mock_cache):
        """Test rate limiting when over the limit."""
        # Mock cache to return limit value
        mock_cache.get.return_value = 10
        
        result = SecurityValidator.validate_rate_limiting(
            operation="test_op",
            user_id="user1",
            organization_id="org1",
            limit=10,
            window_minutes=60
        )
        
        self.assertFalse(result['valid'])
        self.assertIn("Rate limit exceeded", result['errors'][0])
        self.assertEqual(result['current_count'], 10)
        self.assertEqual(result['limit'], 10)
    
    @patch('core.trust.validators.cache')
    def test_validate_rate_limiting_increments_counter(self, mock_cache):
        """Test that rate limiting properly increments the counter."""
        # Mock cache behavior for testing
        cache_data = {}
        
        def mock_get(key, default=0):
            return cache_data.get(key, default)
        
        def mock_set(key, value, timeout):
            cache_data[key] = value
        
        mock_cache.get.side_effect = mock_get
        mock_cache.set.side_effect = mock_set
        
        # Make first request
        result1 = SecurityValidator.validate_rate_limiting(
            operation="test_op",
            user_id="user1",
            organization_id="org1",
            limit=10
        )
        self.assertEqual(result1['current_count'], 1)
        
        # Make second request
        result2 = SecurityValidator.validate_rate_limiting(
            operation="test_op",
            user_id="user1",
            organization_id="org1",
            limit=10
        )
        self.assertEqual(result2['current_count'], 2)
    
    def test_validate_suspicious_patterns_normal_timing(self):
        """Test suspicious pattern detection with normal timing."""
        operation_data = {'timestamp': datetime.now().isoformat()}
        user_context = {'user_id': 'user123'}
        
        result = self.validator.validate_suspicious_patterns(
            user_context['user_id'], 
            operation_data
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_suspicious_patterns_outside_business_hours(self):
        """Test detection of operations outside business hours."""
        # Don't include timestamp to avoid timestamp validation issues
        # We're only testing business hours detection
        operation_data = {
            'operation': 'late_operation'
        }
        
        # Mock datetime.now().time() to return 3 AM for the business hours check
        with patch('core.trust.validators.datetime') as mock_datetime:
            mock_datetime.now.return_value.time.return_value = time(3, 0)  # 3 AM
            result = self.validator.validate_suspicious_patterns('user1', operation_data)
        
        self.assertTrue(result['valid'])  # Warnings don't make it invalid
        self.assertIn("Operation occurring outside business hours", result['warnings'])
    
    def test_validate_suspicious_patterns_old_timestamp(self):
        """Test detection of operations with old timestamps."""
        # Create timestamp 2 hours ago
        old_time = timezone.now() - timedelta(hours=2)
        operation_data = {
            'timestamp': old_time.isoformat(),
            'operation': 'old_operation'
        }
        user_context = {'user_id': 'user1'}
        
        result = self.validator.validate_suspicious_patterns('user1', operation_data)
        
        self.assertFalse(result['valid'])
        self.assertIn("Operation timestamp too old", result['errors'][0])
    
    def test_validate_suspicious_patterns_invalid_timestamp(self):
        """Test handling of invalid timestamp formats."""
        operation_data = {
            'timestamp': 'invalid-timestamp',
            'operation': 'invalid_operation'
        }
        user_context = {'user_id': 'user1'}
        
        result = self.validator.validate_suspicious_patterns('user1', operation_data)
        
        self.assertFalse(result['valid'])
        self.assertIn("Invalid timestamp format", result['errors'])
    
    @patch('core.trust.validators.cache')
    def test_validate_suspicious_patterns_rapid_operations(self, mock_cache):
        """Test detection of rapid-fire operations."""
        user_context = {'user_id': 'user1'}
        operation_data = {'timestamp': timezone.now().isoformat()}
        
        # Mock cache to return 25 recent operations (more than 5)
        recent_ops = [1, 2, 3, 4, 5, 6]  # 6 operations (more than 5)
        mock_cache.get.return_value = recent_ops
        
        result = self.validator.validate_suspicious_patterns('user1', operation_data)
        
        self.assertTrue(result['valid'])  # Warnings don't make it invalid
        self.assertIn("Unusually high operation frequency detected", result['warnings'])
    
    @override_settings(TRUST_MANAGEMENT_SECRET_KEY='test-secret-key')
    def test_validate_cryptographic_integrity_valid_signature(self):
        """Test cryptographic integrity validation with valid signature."""
        data = {'key1': 'value1', 'key2': 'value2'}
        secret_key = 'test-secret-key'
        
        # Calculate expected signature
        data_string = str(sorted(data.items()))
        expected_signature = hmac.new(
            secret_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        result = SecurityValidator.validate_cryptographic_integrity(data, expected_signature)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    @override_settings(TRUST_MANAGEMENT_SECRET_KEY='test-secret-key')
    def test_validate_cryptographic_integrity_invalid_signature(self):
        """Test cryptographic integrity validation with invalid signature."""
        data = {'key1': 'value1', 'key2': 'value2'}
        invalid_signature = 'invalid-signature'
        
        result = SecurityValidator.validate_cryptographic_integrity(data, invalid_signature)
        
        self.assertFalse(result['valid'])
        self.assertIn("Cryptographic signature validation failed", result['errors'])
    
    def test_validate_cryptographic_integrity_no_secret_key(self):
        """Test cryptographic integrity validation without secret key."""
        data = {'key1': 'value1', 'key2': 'value2'}
        signature = 'some-signature'
        
        with override_settings(TRUST_MANAGEMENT_SECRET_KEY=None):
            result = SecurityValidator.validate_cryptographic_integrity(data, signature)
        
        self.assertFalse(result['valid'])
        self.assertIn("Cannot validate signature: secret key not configured", result['errors'])
    
    def test_validate_temporal_security_valid_timestamp(self):
        """Test temporal security validation with valid timestamp."""
        operation_data = {
            'timestamp': timezone.now().isoformat()
        }
        
        result = SecurityValidator.validate_temporal_security(operation_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_temporal_security_replay_attack(self):
        """Test detection of potential replay attacks."""
        # Create timestamp 10 minutes ago
        old_time = timezone.now() - timedelta(minutes=10)
        operation_data = {
            'timestamp': old_time.isoformat()
        }
        
        result = SecurityValidator.validate_temporal_security(operation_data)
        
        self.assertFalse(result['valid'])
        self.assertIn("Operation timestamp too old (potential replay attack)", result['errors'])
    
    def test_validate_temporal_security_warning_threshold(self):
        """Test warning for operations with timestamps older than expected."""
        # Create timestamp 2 minutes ago
        old_time = timezone.now() - timedelta(minutes=2)
        operation_data = {
            'timestamp': old_time.isoformat()
        }
        
        result = SecurityValidator.validate_temporal_security(operation_data)
        
        self.assertTrue(result['valid'])  # Warnings don't make it invalid
        self.assertIn("Operation timestamp is older than expected", result['warnings'])
    
    def test_validate_trust_escalation_normal(self):
        """Test trust escalation validation for normal escalation."""
        result = SecurityValidator.validate_trust_escalation("low", "medium")
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertIn("Trust level escalation detected", result['warnings'])
    
    def test_validate_trust_escalation_large_jump(self):
        """Test trust escalation validation for large escalation."""
        result = SecurityValidator.validate_trust_escalation("low", "complete")
        
        self.assertFalse(result['valid'])
        self.assertIn("Trust escalation too large", result['errors'][0])
    
    def test_validate_trust_escalation_same_level(self):
        """Test trust escalation validation for same level."""
        result = SecurityValidator.validate_trust_escalation("medium", "medium")
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['warnings']), 0)
    
    def test_validate_trust_escalation_downgrade(self):
        """Test trust escalation validation for trust downgrade."""
        result = SecurityValidator.validate_trust_escalation("high", "low")
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['warnings']), 0)
    
    def test_validate_trust_escalation_invalid_levels(self):
        """Test trust escalation validation with invalid trust levels."""
        result = SecurityValidator.validate_trust_escalation("invalid", "unknown")
        
        # Should handle invalid levels gracefully
        self.assertTrue(result['valid'])


class ValidatorIntegrationTest(TestCase):
    """Integration tests for validator functionality."""
    
    def test_multiple_validators_consistency(self):
        """Test that multiple validators work consistently together."""
        # Test that validators don't interfere with each other
        valid_org_id = str(uuid.uuid4())
        
        # Test relationship validator
        rel_result = TrustRelationshipValidator.validate_create_relationship(
            source_org=valid_org_id,
            target_org=str(uuid.uuid4()),
            trust_level_name="medium",
            created_by="user1"
        )
        self.assertTrue(rel_result['valid'])
        
        # Test group validator
        group_result = TrustGroupValidator.validate_create_group(
            name="Test Group",
            description="Valid description for testing",
            creator_org=valid_org_id
        )
        self.assertTrue(group_result['valid'])
        
        # Test security validator
        security_result = SecurityValidator.validate_input_sanitization({
            'name': 'Clean input',
            'value': 123
        })
        self.assertTrue(security_result['valid'])
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across validators."""
        # All validators should return similar error structure
        rel_result = TrustRelationshipValidator.validate_create_relationship("", "", "", "")
        group_result = TrustGroupValidator.validate_create_group("", "", "")
        policy_result = AccessControlValidator.validate_sharing_policy({})
        
        # All should have 'valid' and 'errors' keys
        for result in [rel_result, group_result, policy_result]:
            self.assertIn('valid', result)
            self.assertIn('errors', result)
            self.assertFalse(result['valid'])
            self.assertIsInstance(result['errors'], list)
            self.assertGreater(len(result['errors']), 0)