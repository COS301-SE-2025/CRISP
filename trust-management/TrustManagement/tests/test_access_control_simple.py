"""
Simple Test Suite for Access Control Strategies

This module provides tests for the actual access control strategy implementation.
"""

import uuid
from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from ..models import TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership
from ..strategies.access_control_strategies import (
    AccessControlStrategy, TrustLevelAccessStrategy, CommunityAccessStrategy,
    TimeBasedAccessStrategy, AnonymizationStrategy, NoAnonymizationStrategy,
    MinimalAnonymizationStrategy, PartialAnonymizationStrategy, FullAnonymizationStrategy,
    CustomAnonymizationStrategy, AnonymizationContext, AccessControlContext
)


class AccessControlContextTest(TestCase):
    """Test AccessControlContext class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.requesting_org = str(uuid.uuid4())
        self.target_org = str(uuid.uuid4())
        self.context = AccessControlContext(
            requesting_org=self.requesting_org,
            target_org=self.target_org,
            resource_type='indicator'
        )
    
    def test_context_creation(self):
        """Test creating access control context"""
        self.assertIsInstance(self.context, AccessControlContext)
        self.assertEqual(self.context.resource_type, 'indicator')
        self.assertEqual(self.context.requesting_org, self.requesting_org)
        self.assertEqual(self.context.target_org, self.target_org)
    
    def test_context_strategies(self):
        """Test adding strategies to context"""
        strategy = TrustLevelAccessStrategy(minimum_trust_level=50)
        self.context.add_strategy(strategy)
        
        self.assertEqual(len(self.context._strategies), 1)
        self.assertIn(strategy, self.context._strategies)
    
    def test_context_can_access(self):
        """Test access checking functionality"""
        strategy = TrustLevelAccessStrategy(minimum_trust_level=50)
        self.context.add_strategy(strategy)
        
        # Test without trust relationship
        allowed, reasons = self.context.can_access()
        self.assertFalse(allowed)
        self.assertIsInstance(reasons, list)
        self.assertGreater(len(reasons), 0)
    
    def test_context_get_access_level(self):
        """Test getting access level"""
        strategy = TrustLevelAccessStrategy(minimum_trust_level=50)
        self.context.add_strategy(strategy)
        
        access_level = self.context.get_access_level()
        self.assertIsInstance(access_level, str)
        self.assertIn(access_level, ['none', 'read', 'subscribe', 'contribute', 'full'])


class AnonymizationStrategyTest(TestCase):
    """Test Anonymization Strategy classes"""
    
    def test_no_anonymization_strategy(self):
        """Test NoAnonymizationStrategy"""
        strategy = NoAnonymizationStrategy()
        
        test_data = {'field1': 'value1', 'field2': 'value2'}
        result = strategy.anonymize(test_data, {})
        
        self.assertEqual(result, test_data)
        self.assertEqual(strategy.get_anonymization_level(), 'none')
    
    def test_minimal_anonymization_strategy(self):
        """Test MinimalAnonymizationStrategy"""
        strategy = MinimalAnonymizationStrategy()
        
        test_data = {
            'created_by_ref': 'identity--12345',
            'x_attribution': 'test attribution',
            'other_field': 'value'
        }
        
        result = strategy.anonymize(test_data, {})
        
        self.assertNotEqual(result.get('created_by_ref'), 'identity--12345')
        self.assertNotIn('x_attribution', result)
        self.assertEqual(result['other_field'], 'value')
        self.assertEqual(strategy.get_anonymization_level(), 'minimal')
    
    def test_partial_anonymization_strategy(self):
        """Test PartialAnonymizationStrategy"""
        strategy = PartialAnonymizationStrategy()
        
        test_data = {
            'type': 'indicator',
            'pattern': "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            'created_by_ref': 'identity--12345'
        }
        
        result = strategy.anonymize(test_data, {})
        
        self.assertIn('pattern', result)
        self.assertEqual(strategy.get_anonymization_level(), 'partial')
    
    def test_full_anonymization_strategy(self):
        """Test FullAnonymizationStrategy"""
        strategy = FullAnonymizationStrategy()
        
        test_data = {
            'type': 'indicator',
            'pattern': "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            'external_references': [{'url': 'http://example.com'}],
            'x_custom_field': 'custom value',
            'source_name': 'test source'
        }
        
        result = strategy.anonymize(test_data, {})
        
        self.assertNotIn('external_references', result)
        self.assertNotIn('x_custom_field', result)
        self.assertNotIn('source_name', result)
        self.assertEqual(strategy.get_anonymization_level(), 'full')
    
    def test_custom_anonymization_strategy(self):
        """Test CustomAnonymizationStrategy"""
        rules = {
            'base_level': 'minimal',
            'field_rules': {
                'sensitive_field': 'remove',
                'hash_field': 'hash',
                'mask_field': 'mask'
            }
        }
        
        strategy = CustomAnonymizationStrategy(rules)
        
        test_data = {
            'sensitive_field': 'secret',
            'hash_field': 'to_be_hashed',
            'mask_field': 'to_be_masked',
            'normal_field': 'normal_value'
        }
        
        result = strategy.anonymize(test_data, {})
        
        self.assertNotIn('sensitive_field', result)
        self.assertNotEqual(result['hash_field'], 'to_be_hashed')
        self.assertEqual(result['mask_field'], 'xxx')
        self.assertEqual(result['normal_field'], 'normal_value')
        self.assertEqual(strategy.get_anonymization_level(), 'custom')


class TrustLevelAccessStrategyTest(TestCase):
    """Test TrustLevelAccessStrategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.trust_level = TrustLevel.objects.create(
            name='Strategy Test Trust Level',
            level='high',
            description='High trust level for strategy testing',
            numerical_value=75,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        # Create mock relationship
        self.relationship = Mock()
        self.relationship.is_effective = True
        self.relationship.trust_level = self.trust_level
        
        self.strategy = TrustLevelAccessStrategy(minimum_trust_level=50)
    
    def test_can_access_with_sufficient_trust(self):
        """Test access with sufficient trust level"""
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        
        self.assertTrue(allowed)
        self.assertIn('trust level', reason.lower())
    
    def test_can_access_with_insufficient_trust(self):
        """Test access with insufficient trust level"""
        # Create strategy with high minimum trust
        high_trust_strategy = TrustLevelAccessStrategy(minimum_trust_level=90)
        
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        allowed, reason = high_trust_strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('too low', reason.lower())
    
    def test_can_access_no_relationship(self):
        """Test access with no trust relationship"""
        context_dict = {}
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('no trust relationship', reason.lower())
    
    def test_can_access_ineffective_relationship(self):
        """Test access with ineffective relationship"""
        self.relationship.is_effective = False
        self.relationship.status = 'pending'
        
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('not effective', reason.lower())
    
    def test_get_access_level(self):
        """Test getting access level"""
        # Mock get_effective_access_level method
        self.relationship.get_effective_access_level = Mock(return_value='contribute')
        
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        access_level = self.strategy.get_access_level(context_dict)
        self.assertEqual(access_level, 'contribute')
    
    def test_get_access_level_no_relationship(self):
        """Test getting access level with no relationship"""
        context_dict = {}
        
        access_level = self.strategy.get_access_level(context_dict)
        self.assertEqual(access_level, 'none')


class CommunityAccessStrategyTest(TestCase):
    """Test CommunityAccessStrategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = CommunityAccessStrategy()
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
    
    def test_can_access_missing_org_info(self):
        """Test access with missing organization information"""
        context_dict = {}
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('missing organization', reason.lower())
    
    @patch('TrustManagement.strategies.access_control_strategies.TrustService.check_trust_level')
    def test_can_access_no_trust_relationship(self, mock_check_trust):
        """Test access with no trust relationship"""
        mock_check_trust.return_value = None
        
        context_dict = {
            'requesting_organization': self.org_1,
            'target_organization': self.org_2
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('no trust relationship', reason.lower())
    
    @patch('TrustManagement.strategies.access_control_strategies.TrustService.check_trust_level')
    def test_can_access_community_relationship(self, mock_check_trust):
        """Test access with community relationship"""
        mock_trust_level = Mock()
        mock_relationship = Mock()
        mock_relationship.relationship_type = 'community'
        mock_relationship.trust_group.name = 'Test Community'
        
        mock_check_trust.return_value = (mock_trust_level, mock_relationship)
        
        context_dict = {
            'requesting_organization': self.org_1,
            'target_organization': self.org_2
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertTrue(allowed)
        self.assertIn('community trust group', reason.lower())
    
    @patch('TrustManagement.strategies.access_control_strategies.TrustService.check_trust_level')
    def test_can_access_non_community_relationship(self, mock_check_trust):
        """Test access with non-community relationship"""
        mock_trust_level = Mock()
        mock_relationship = Mock()
        mock_relationship.relationship_type = 'bilateral'
        
        mock_check_trust.return_value = (mock_trust_level, mock_relationship)
        
        context_dict = {
            'requesting_organization': self.org_1,
            'target_organization': self.org_2
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('not a community-based', reason.lower())


class TimeBasedAccessStrategyTest(TestCase):
    """Test TimeBasedAccessStrategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = TimeBasedAccessStrategy()
        
        # Create mock relationship
        self.relationship = Mock()
        self.relationship.valid_from = timezone.now() - timedelta(days=1)
        self.relationship.valid_until = timezone.now() + timedelta(days=1)
        self.relationship.get_effective_access_level = Mock(return_value='read')
    
    def test_can_access_no_relationship(self):
        """Test access with no trust relationship"""
        context_dict = {}
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('no trust relationship', reason.lower())
    
    def test_can_access_valid_time_window(self):
        """Test access within valid time window"""
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertTrue(allowed)
        self.assertIn('valid time window', reason.lower())
    
    def test_can_access_not_yet_valid(self):
        """Test access before valid time"""
        self.relationship.valid_from = timezone.now() + timedelta(days=1)
        
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('not yet valid', reason.lower())
    
    def test_can_access_expired(self):
        """Test access after expiration"""
        self.relationship.valid_until = timezone.now() - timedelta(days=1)
        
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        allowed, reason = self.strategy.can_access(context_dict)
        self.assertFalse(allowed)
        self.assertIn('expired', reason.lower())
    
    def test_get_access_level(self):
        """Test getting access level"""
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        access_level = self.strategy.get_access_level(context_dict)
        self.assertEqual(access_level, 'read')
    
    def test_get_access_level_invalid_time(self):
        """Test getting access level with invalid time"""
        self.relationship.valid_until = timezone.now() - timedelta(days=1)
        
        context_dict = {
            'trust_relationship': self.relationship
        }
        
        access_level = self.strategy.get_access_level(context_dict)
        self.assertEqual(access_level, 'none')


class AnonymizationContextTest(TestCase):
    """Test AnonymizationContext"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.context = AnonymizationContext()
    
    def test_set_strategy(self):
        """Test setting anonymization strategy"""
        strategy = NoAnonymizationStrategy()
        self.context.set_strategy(strategy)
        
        self.assertEqual(self.context._strategy, strategy)
    
    def test_get_strategy_for_trust_level(self):
        """Test getting strategy for trust level"""
        strategy = self.context.get_strategy_for_trust_level('minimal')
        
        self.assertIsInstance(strategy, MinimalAnonymizationStrategy)
    
    def test_get_strategy_for_different_trust_levels(self):
        """Test getting strategies for different trust levels"""
        test_cases = [
            ('none', NoAnonymizationStrategy),
            ('minimal', MinimalAnonymizationStrategy),
            ('partial', PartialAnonymizationStrategy),
            ('full', FullAnonymizationStrategy),
            ('custom', CustomAnonymizationStrategy)
        ]
        
        for trust_level, expected_strategy_class in test_cases:
            with self.subTest(trust_level=trust_level):
                strategy = self.context.get_strategy_for_trust_level(trust_level)
                self.assertIsInstance(strategy, expected_strategy_class)
    
    def test_anonymize_data(self):
        """Test anonymizing data"""
        test_data = {'field1': 'value1', 'field2': 'value2'}
        
        result = self.context.anonymize_data(test_data)
        
        self.assertIsInstance(result, dict)
        # Default should be partial anonymization strategy
        self.assertIsNotNone(result)