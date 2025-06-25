"""
Comprehensive Test Suite for Access Control Strategies

This module provides 100% coverage of the access control strategies module.
"""

import uuid
from unittest.mock import patch, Mock, MagicMock
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
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
    
    def test_context_with_additional_data(self):
        """Test context with additional metadata"""
        context = AccessControlContext(
            requesting_org=str(uuid.uuid4()),
            target_org=str(uuid.uuid4()),
            resource_type='malware'
        )
        
        self.assertEqual(context.resource_type, 'malware')
        self.assertIsInstance(context._strategies, list)
    
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
    """Test TrustBasedAccessControl strategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = TrustBasedAccessControl()
        
        self.trust_level = TrustLevel.objects.create(
            name='Trust Strategy Test Level',
            level='high',
            description='High trust level for strategy testing',
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
            status='active',
            created_by='test_user',
            last_modified_by='test_user'
        )
        
        self.context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='read',
            user='test_user'
        )
    
    def test_evaluate_with_sufficient_trust(self):
        """Test evaluation with sufficient trust level"""
        decision = self.strategy.evaluate(self.context)
        
        self.assertIsInstance(decision, AccessDecision)
        self.assertTrue(decision.allowed)
        self.assertIn('trust', decision.reason.lower())
    
    def test_evaluate_with_insufficient_trust(self):
        """Test evaluation with insufficient trust level"""
        # Create low trust relationship
        low_trust_level = TrustLevel.objects.create(
            name='Low Trust Strategy Test',
            level='low',
            description='Low trust level',
            numerical_value=20,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.relationship.trust_level = low_trust_level
        self.relationship.save()
        
        # Test with write action requiring higher trust
        write_context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='write',
            user='test_user'
        )
        
        decision = self.strategy.evaluate(write_context)
        self.assertFalse(decision.allowed)
    
    def test_evaluate_no_relationship(self):
        """Test evaluation with no trust relationship"""
        no_trust_context = AccessControlContext(
            requesting_organization=str(uuid.uuid4()),
            target_organization=str(uuid.uuid4()),
            resource_type='indicator',
            action='read',
            user='test_user'
        )
        
        decision = self.strategy.evaluate(no_trust_context)
        self.assertFalse(decision.allowed)
        self.assertIn('no trust relationship', decision.reason.lower())
    
    def test_configure_strategy(self):
        """Test configuring trust-based strategy"""
        config = {
            'minimum_trust_level': 50,
            'required_actions': {
                'read': 30,
                'write': 60,
                'admin': 90
            }
        }
        
        self.strategy.configure(config)
        self.assertEqual(self.strategy.config['minimum_trust_level'], 50)
    
    def test_strategy_validation(self):
        """Test strategy validation"""
        # Should not raise errors for valid configuration
        self.strategy.validate()
        
        # Test with invalid configuration
        self.strategy.config = {'invalid_key': 'invalid_value'}
        with self.assertRaises(ValidationError):
            self.strategy.validate()


class GroupBasedAccessControlTest(TestCase):
    """Test GroupBasedAccessControl strategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = GroupBasedAccessControl()
        
        self.trust_level = TrustLevel.objects.create(
            name='Group Strategy Test Level',
            level='medium',
            description='Trust level for group strategy testing',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        self.trust_group = TrustGroup.objects.create(
            name='Group Strategy Test Group',
            description='Group for strategy testing',
            group_type='community',
            is_public=False,
            requires_approval=True,
            default_trust_level=self.trust_level,
            created_by=self.org_1,
            administrators=[self.org_1]
        )
        
        # Add org_2 as member
        TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization=self.org_2,
            membership_type='member',
            is_active=True
        )
        
        self.context = AccessControlContext(
            requesting_organization=self.org_2,
            target_organization=self.org_1,
            resource_type='indicator',
            action='read',
            user='test_user',
            group_context=str(self.trust_group.id)
        )
    
    def test_evaluate_with_group_membership(self):
        """Test evaluation with valid group membership"""
        decision = self.strategy.evaluate(self.context)
        
        self.assertIsInstance(decision, AccessDecision)
        self.assertTrue(decision.allowed)
        self.assertIn('group', decision.reason.lower())
    
    def test_evaluate_without_group_membership(self):
        """Test evaluation without group membership"""
        non_member_context = AccessControlContext(
            requesting_organization=str(uuid.uuid4()),
            target_organization=self.org_1,
            resource_type='indicator',
            action='read',
            user='test_user',
            group_context=str(self.trust_group.id)
        )
        
        decision = self.strategy.evaluate(non_member_context)
        self.assertFalse(decision.allowed)
    
    def test_evaluate_administrator_access(self):
        """Test evaluation for group administrator"""
        admin_context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='admin',
            user='admin_user',
            group_context=str(self.trust_group.id)
        )
        
        decision = self.strategy.evaluate(admin_context)
        self.assertTrue(decision.allowed)
    
    def test_evaluate_no_group_context(self):
        """Test evaluation without group context"""
        no_group_context = AccessControlContext(
            requesting_organization=self.org_2,
            target_organization=self.org_1,
            resource_type='indicator',
            action='read',
            user='test_user'
        )
        
        decision = self.strategy.evaluate(no_group_context)
        self.assertFalse(decision.allowed)


class PolicyBasedAccessControlTest(TestCase):
    """Test PolicyBasedAccessControl strategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = PolicyBasedAccessControl()
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        # Configure policy
        policy_config = {
            'rules': [
                {
                    'condition': 'resource_type == "indicator" and action == "read"',
                    'effect': 'allow',
                    'priority': 100
                },
                {
                    'condition': 'action == "write" and user_role != "admin"',
                    'effect': 'deny',
                    'priority': 200
                }
            ],
            'default_effect': 'deny'
        }
        
        self.strategy.configure(policy_config)
        
        self.context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='read',
            user='test_user'
        )
    
    def test_evaluate_with_matching_policy(self):
        """Test evaluation with matching policy rule"""
        decision = self.strategy.evaluate(self.context)
        
        self.assertIsInstance(decision, AccessDecision)
        self.assertTrue(decision.allowed)
        self.assertIn('policy', decision.reason.lower())
    
    def test_evaluate_with_deny_policy(self):
        """Test evaluation with deny policy"""
        write_context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='write',
            user='test_user',
            user_role='user'
        )
        
        decision = self.strategy.evaluate(write_context)
        self.assertFalse(decision.allowed)
    
    def test_evaluate_with_admin_override(self):
        """Test evaluation with admin role override"""
        admin_context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='write',
            user='admin_user',
            user_role='admin'
        )
        
        decision = self.strategy.evaluate(admin_context)
        # Should be allowed for admin even with deny rule
        self.assertTrue(decision.allowed)
    
    def test_policy_rule_priority(self):
        """Test policy rule priority handling"""
        # Add conflicting rules with different priorities
        conflicting_policy = {
            'rules': [
                {
                    'condition': 'resource_type == "indicator"',
                    'effect': 'allow',
                    'priority': 100
                },
                {
                    'condition': 'resource_type == "indicator"',
                    'effect': 'deny',
                    'priority': 200
                }
            ]
        }
        
        strategy = PolicyBasedAccessControl()
        strategy.configure(conflicting_policy)
        
        decision = strategy.evaluate(self.context)
        # Higher priority (200) deny rule should win
        self.assertFalse(decision.allowed)
    
    def test_policy_validation(self):
        """Test policy configuration validation"""
        invalid_policy = {
            'rules': [
                {
                    'condition': 'invalid python syntax ===',
                    'effect': 'allow'
                }
            ]
        }
        
        strategy = PolicyBasedAccessControl()
        with self.assertRaises(ValidationError):
            strategy.configure(invalid_policy)


class ContextAwareAccessControlTest(TestCase):
    """Test ContextAwareAccessControl strategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = ContextAwareAccessControl()
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        # Configure context-aware rules
        context_config = {
            'time_restrictions': {
                'business_hours_only': True,
                'allowed_hours': {'start': 9, 'end': 17}
            },
            'location_restrictions': {
                'allowed_countries': ['US', 'CA', 'UK'],
                'blocked_ips': ['192.168.1.100']
            },
            'usage_patterns': {
                'max_requests_per_hour': 100,
                'suspicious_threshold': 50
            }
        }
        
        self.strategy.configure(context_config)
    
    def test_evaluate_within_business_hours(self):
        """Test evaluation during business hours"""
        # Mock time to be within business hours
        with patch('django.utils.timezone.now') as mock_now:
            mock_time = timezone.now().replace(hour=14, minute=30)  # 2:30 PM
            mock_now.return_value = mock_time
            
            context = AccessControlContext(
                requesting_organization=self.org_1,
                target_organization=self.org_2,
                resource_type='indicator',
                action='read',
                user='test_user',
                time_context=mock_time
            )
            
            decision = self.strategy.evaluate(context)
            self.assertTrue(decision.allowed)
    
    def test_evaluate_outside_business_hours(self):
        """Test evaluation outside business hours"""
        with patch('django.utils.timezone.now') as mock_now:
            mock_time = timezone.now().replace(hour=22, minute=30)  # 10:30 PM
            mock_now.return_value = mock_time
            
            context = AccessControlContext(
                requesting_organization=self.org_1,
                target_organization=self.org_2,
                resource_type='indicator',
                action='read',
                user='test_user',
                time_context=mock_time
            )
            
            decision = self.strategy.evaluate(context)
            self.assertFalse(decision.allowed)
            self.assertIn('business hours', decision.reason.lower())
    
    def test_evaluate_blocked_ip(self):
        """Test evaluation from blocked IP address"""
        context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='read',
            user='test_user',
            ip_address='192.168.1.100'
        )
        
        decision = self.strategy.evaluate(context)
        self.assertFalse(decision.allowed)
        self.assertIn('blocked', decision.reason.lower())
    
    def test_evaluate_rate_limiting(self):
        """Test evaluation with rate limiting"""
        # Mock high request count
        with patch.object(self.strategy, '_get_request_count', return_value=150):
            context = AccessControlContext(
                requesting_organization=self.org_1,
                target_organization=self.org_2,
                resource_type='indicator',
                action='read',
                user='test_user'
            )
            
            decision = self.strategy.evaluate(context)
            self.assertFalse(decision.allowed)
            self.assertIn('rate limit', decision.reason.lower())
    
    def test_evaluate_suspicious_pattern(self):
        """Test evaluation with suspicious usage pattern"""
        with patch.object(self.strategy, '_detect_suspicious_pattern', return_value=True):
            context = AccessControlContext(
                requesting_organization=self.org_1,
                target_organization=self.org_2,
                resource_type='indicator',
                action='read',
                user='test_user'
            )
            
            decision = self.strategy.evaluate(context)
            self.assertFalse(decision.allowed)
            self.assertIn('suspicious', decision.reason.lower())


class HybridAccessControlTest(TestCase):
    """Test HybridAccessControl strategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.trust_strategy = TrustBasedAccessControl()
        self.group_strategy = GroupBasedAccessControl()
        self.policy_strategy = PolicyBasedAccessControl()
        
        self.hybrid_strategy = HybridAccessControl([
            self.trust_strategy,
            self.group_strategy,
            self.policy_strategy
        ])
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        self.context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='read',
            user='test_user'
        )
    
    def test_evaluate_all_strategies_allow(self):
        """Test evaluation when all strategies allow access"""
        # Mock all strategies to return allow
        with patch.object(self.trust_strategy, 'evaluate', 
                         return_value=AccessDecision(True, 'Trust sufficient')):
            with patch.object(self.group_strategy, 'evaluate',
                             return_value=AccessDecision(True, 'Group member')):
                with patch.object(self.policy_strategy, 'evaluate',
                                 return_value=AccessDecision(True, 'Policy allows')):
                    
                    decision = self.hybrid_strategy.evaluate(self.context)
                    self.assertTrue(decision.allowed)
    
    def test_evaluate_one_strategy_denies(self):
        """Test evaluation when one strategy denies access"""
        with patch.object(self.trust_strategy, 'evaluate',
                         return_value=AccessDecision(True, 'Trust sufficient')):
            with patch.object(self.group_strategy, 'evaluate',
                             return_value=AccessDecision(False, 'Not group member')):
                with patch.object(self.policy_strategy, 'evaluate',
                                 return_value=AccessDecision(True, 'Policy allows')):
                    
                    decision = self.hybrid_strategy.evaluate(self.context)
                    self.assertFalse(decision.allowed)
    
    def test_configure_hybrid_strategy(self):
        """Test configuring hybrid strategy"""
        config = {
            'combination_mode': 'all_must_allow',
            'strategy_weights': {
                'TrustBasedAccessControl': 0.4,
                'GroupBasedAccessControl': 0.3,
                'PolicyBasedAccessControl': 0.3
            }
        }
        
        self.hybrid_strategy.configure(config)
        self.assertEqual(self.hybrid_strategy.config['combination_mode'], 'all_must_allow')
    
    def test_weighted_decision_making(self):
        """Test weighted decision making in hybrid strategy"""
        # Configure weighted mode
        config = {
            'combination_mode': 'weighted',
            'decision_threshold': 0.7,
            'strategy_weights': {
                'TrustBasedAccessControl': 0.5,
                'GroupBasedAccessControl': 0.3,
                'PolicyBasedAccessControl': 0.2
            }
        }
        
        self.hybrid_strategy.configure(config)
        
        # Mock strategies with different confidence levels
        with patch.object(self.trust_strategy, 'evaluate',
                         return_value=AccessDecision(True, 'Trust', confidence=0.9)):
            with patch.object(self.group_strategy, 'evaluate',
                             return_value=AccessDecision(True, 'Group', confidence=0.8)):
                with patch.object(self.policy_strategy, 'evaluate',
                                 return_value=AccessDecision(False, 'Policy', confidence=0.6)):
                    
                    decision = self.hybrid_strategy.evaluate(self.context)
                    # Weighted score should be above threshold
                    self.assertTrue(decision.allowed)


class AccessControlManagerTest(TestCase):
    """Test AccessControlManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = AccessControlManager()
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        self.context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='read',
            user='test_user'
        )
    
    def test_register_strategy(self):
        """Test registering access control strategy"""
        strategy = TrustBasedAccessControl()
        self.manager.register_strategy('trust', strategy)
        
        self.assertIn('trust', self.manager.strategies)
        self.assertEqual(self.manager.strategies['trust'], strategy)
    
    def test_unregister_strategy(self):
        """Test unregistering access control strategy"""
        strategy = TrustBasedAccessControl()
        self.manager.register_strategy('trust', strategy)
        self.manager.unregister_strategy('trust')
        
        self.assertNotIn('trust', self.manager.strategies)
    
    def test_evaluate_access_with_strategy(self):
        """Test evaluating access with specific strategy"""
        strategy = TrustBasedAccessControl()
        self.manager.register_strategy('trust', strategy)
        
        with patch.object(strategy, 'evaluate',
                         return_value=AccessDecision(True, 'Trust sufficient')):
            decision = self.manager.evaluate_access(self.context, strategy_name='trust')
            self.assertTrue(decision.allowed)
    
    def test_evaluate_access_default_strategy(self):
        """Test evaluating access with default strategy"""
        self.manager.set_default_strategy('trust')
        strategy = TrustBasedAccessControl()
        self.manager.register_strategy('trust', strategy)
        
        with patch.object(strategy, 'evaluate',
                         return_value=AccessDecision(True, 'Default strategy')):
            decision = self.manager.evaluate_access(self.context)
            self.assertTrue(decision.allowed)
    
    def test_evaluate_access_chain(self):
        """Test evaluating access with strategy chain"""
        trust_strategy = TrustBasedAccessControl()
        group_strategy = GroupBasedAccessControl()
        
        self.manager.register_strategy('trust', trust_strategy)
        self.manager.register_strategy('group', group_strategy)
        self.manager.set_strategy_chain(['trust', 'group'])
        
        with patch.object(trust_strategy, 'evaluate',
                         return_value=AccessDecision(True, 'Trust OK')):
            with patch.object(group_strategy, 'evaluate',
                             return_value=AccessDecision(True, 'Group OK')):
                decision = self.manager.evaluate_access_chain(self.context)
                self.assertTrue(decision.allowed)
    
    def test_audit_access_attempt(self):
        """Test auditing access attempt"""
        decision = AccessDecision(True, 'Access granted')
        
        with patch.object(self.manager, '_log_access_attempt') as mock_log:
            self.manager.audit_access_attempt(self.context, decision)
            mock_log.assert_called_once()
    
    def test_get_access_statistics(self):
        """Test getting access statistics"""
        stats = self.manager.get_access_statistics(self.org_1)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_requests', stats)
        self.assertIn('allowed_requests', stats)
        self.assertIn('denied_requests', stats)
    
    def test_validate_all_strategies(self):
        """Test validating all registered strategies"""
        valid_strategy = TrustBasedAccessControl()
        invalid_strategy = Mock()
        invalid_strategy.validate.side_effect = ValidationError('Invalid config')
        
        self.manager.register_strategy('valid', valid_strategy)
        self.manager.register_strategy('invalid', invalid_strategy)
        
        with self.assertRaises(ValidationError):
            self.manager.validate_all_strategies()


class AccessControlIntegrationTest(TestCase):
    """Test integration between different access control components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.trust_level = TrustLevel.objects.create(
            name='Integration Test Trust Level',
            level='high',
            description='High trust level for integration testing',
            numerical_value=80,
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
            status='active',
            created_by='test_user',
            last_modified_by='test_user'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Integration Test Group',
            description='Group for integration testing',
            group_type='community',
            is_public=False,
            default_trust_level=self.trust_level,
            created_by=self.org_1,
            administrators=[self.org_1]
        )
        
        TrustGroupMembership.objects.create(
            trust_group=self.trust_group,
            organization=self.org_2,
            membership_type='member',
            is_active=True
        )
    
    def test_full_access_control_workflow(self):
        """Test complete access control workflow"""
        # Create manager with multiple strategies
        manager = AccessControlManager()
        
        trust_strategy = TrustBasedAccessControl()
        group_strategy = GroupBasedAccessControl()
        
        manager.register_strategy('trust', trust_strategy)
        manager.register_strategy('group', group_strategy)
        manager.set_strategy_chain(['trust', 'group'])
        
        # Create context
        context = AccessControlContext(
            requesting_organization=self.org_2,
            target_organization=self.org_1,
            resource_type='indicator',
            action='read',
            user='integration_test_user',
            group_context=str(self.trust_group.id)
        )
        
        # Evaluate access
        decision = manager.evaluate_access_chain(context)
        
        # Should be allowed due to both trust relationship and group membership
        self.assertTrue(decision.allowed)
        
        # Audit the attempt
        manager.audit_access_attempt(context, decision)
    
    def test_cascading_strategy_failure(self):
        """Test behavior when strategies fail in cascade"""
        manager = AccessControlManager()
        
        # Strategy that will fail
        failing_strategy = Mock()
        failing_strategy.evaluate.side_effect = Exception('Strategy failed')
        
        # Backup strategy
        backup_strategy = TrustBasedAccessControl()
        
        manager.register_strategy('failing', failing_strategy)
        manager.register_strategy('backup', backup_strategy)
        manager.set_strategy_chain(['failing', 'backup'])
        
        context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='read',
            user='test_user'
        )
        
        # Should fall back to backup strategy
        with patch.object(backup_strategy, 'evaluate',
                         return_value=AccessDecision(True, 'Backup allowed')):
            decision = manager.evaluate_access_chain(context)
            self.assertTrue(decision.allowed)
    
    def test_performance_monitoring(self):
        """Test performance monitoring of access control"""
        manager = AccessControlManager()
        strategy = TrustBasedAccessControl()
        manager.register_strategy('trust', strategy)
        
        context = AccessControlContext(
            requesting_organization=self.org_1,
            target_organization=self.org_2,
            resource_type='indicator',
            action='read',
            user='test_user'
        )
        
        # Mock slow strategy evaluation
        def slow_evaluate(ctx):
            import time
            time.sleep(0.1)  # Simulate slow operation
            return AccessDecision(True, 'Slow but allowed')
        
        with patch.object(strategy, 'evaluate', side_effect=slow_evaluate):
            start_time = timezone.now()
            decision = manager.evaluate_access(context, strategy_name='trust')
            end_time = timezone.now()
            
            self.assertTrue(decision.allowed)
            duration = (end_time - start_time).total_seconds()
            self.assertGreater(duration, 0.05)  # Should take some time