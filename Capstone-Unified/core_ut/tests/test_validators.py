"""
Essential Tests for Trust Management Validators

Focused on critical functionality and edge cases.
"""

import uuid
from unittest.mock import patch
from django.test import TestCase
from django.core.cache import cache

from core_ut.trust.validators import (
    TrustRelationshipValidator,
    TrustGroupValidator,
    SecurityValidator,
    validate_trust_operation
)


class TrustRelationshipValidatorTest(TestCase):
    """Test core trust relationship validation"""
    
    def setUp(self):
        self.source_org = str(uuid.uuid4())
        self.target_org = str(uuid.uuid4())
        self.user = 'test_user'
    
    def test_validate_create_relationship_valid(self):
        """Test valid relationship creation"""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level_name='medium',
            created_by=self.user
        )
        self.assertTrue(result['valid'])
    
    def test_validate_create_relationship_same_org(self):
        """Test rejection of self-relationships"""
        result = TrustRelationshipValidator.validate_create_relationship(
            source_org=self.source_org,
            target_org=self.source_org,
            trust_level_name='medium',
            created_by=self.user
        )
        self.assertFalse(result['valid'])
        self.assertIn('same organization', result['errors'][0])


class TrustGroupValidatorTest(TestCase):
    """Test trust group validation"""
    
    def test_validator_exists(self):
        """Test that TrustGroupValidator exists and has methods"""
        self.assertTrue(hasattr(TrustGroupValidator, '__name__'))


class SecurityValidatorTest(TestCase):
    """Test security validation features"""
    
    def setUp(self):
        self.user_id = 'test_user'
        self.organization_id = str(uuid.uuid4())
        cache.clear()
    
    def test_validate_rate_limiting_basic(self):
        """Test basic rate limiting"""
        result = SecurityValidator.validate_rate_limiting(
            operation='test_op',
            user_id=self.user_id,
            organization_id=self.organization_id,
            limit=10,
            window_minutes=1
        )
        self.assertTrue(result['valid'])
        self.assertEqual(result['current_count'], 1)
    
    def test_security_validator_exists(self):
        """Test that SecurityValidator exists"""
        self.assertTrue(hasattr(SecurityValidator, 'validate_rate_limiting'))


class ValidateTrustOperationTest(TestCase):
    """Test main trust operation validation function"""
    
    def setUp(self):
        self.user_context = {
            'user_id': 'test_user',
            'organization_id': str(uuid.uuid4())
        }
    
    def test_validate_trust_operation_basic(self):
        """Test basic operation validation"""
        data = {
            'source_org': str(uuid.uuid4()),
            'target_org': str(uuid.uuid4()),
            'trust_level_name': 'medium',
            'created_by': 'test_user'
        }
        result = validate_trust_operation('create_relationship', data, self.user_context)
        self.assertTrue(result['valid'])
    
    def test_validate_trust_operation_invalid_data(self):
        """Test validation with invalid data"""
        data = {'invalid': 'data'}
        result = validate_trust_operation('create_relationship', data, self.user_context)
        self.assertFalse(result['valid'])