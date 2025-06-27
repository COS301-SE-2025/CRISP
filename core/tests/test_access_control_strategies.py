"""
Comprehensive tests for access control strategies
Tests for all access control and anonymization strategy classes.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
import hashlib

from core.models.auth import Organization, CustomUser
from core.models.trust_models.models import TrustRelationship, TrustLevel, TrustGroup
from core.strategies.access_control_strategies import (
    AccessControlStrategy,
    TrustLevelAccessStrategy,
    CommunityAccessStrategy,
    TimeBasedAccessStrategy,
    AnonymizationStrategy,
    NoAnonymizationStrategy,
    MinimalAnonymizationStrategy,
    PartialAnonymizationStrategy,
    FullAnonymizationStrategy,
    CustomAnonymizationStrategy,
    AnonymizationContext,
    AccessControlContext
)
from core.tests.test_base import CrispTestCase


class TrustLevelAccessStrategyTest(CrispTestCase):
    """Test TrustLevelAccessStrategy"""
    
    def setUp(self):
        super().setUp()
        self.strategy = TrustLevelAccessStrategy(minimum_trust_level=3)
        
        # Create test organizations
        self.org1 = Organization.objects.create(
            name="Access Org 1", domain="access1.com", contact_email="test@access1.com"
        )
        self.org2 = Organization.objects.create(
            name="Access Org 2", domain="access2.com", contact_email="test@access2.com"
        )
        
        # Create trust level
        self.trust_level = TrustLevel.objects.create(
            name="High Trust",
            description="High level trust",
            numerical_value=5,
            default_access_level="full",
            default_anonymization_level="none"
        )
        
        # Create effective trust relationship
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status="approved",
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30)
        )
    
    def test_can_access_with_sufficient_trust(self):
        """Test access granted with sufficient trust level"""
        context = {'trust_relationship': self.trust_relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
        self.assertIn("Access granted via trust level", reason)
    
    def test_can_access_with_insufficient_trust(self):
        """Test access denied with insufficient trust level"""
        # Create low trust level
        low_trust = TrustLevel.objects.create(
            name="Low Trust",
            numerical_value=1,
            default_access_level="limited"
        )
        self.trust_relationship.trust_level = low_trust
        self.trust_relationship.save()
        
        context = {'trust_relationship': self.trust_relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn("Trust level too low", reason)
    
    def test_can_access_no_trust_relationship(self):
        """Test access denied with no trust relationship"""
        context = {}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertEqual(reason, "No trust relationship exists")
    
    def test_can_access_ineffective_relationship(self):
        """Test access denied with ineffective relationship"""
        self.trust_relationship.status = "pending"
        self.trust_relationship.save()
        
        context = {'trust_relationship': self.trust_relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn("Trust relationship is not effective", reason)
    
    def test_get_access_level_with_relationship(self):
        """Test getting access level from trust relationship"""
        with patch.object(self.trust_relationship, 'get_effective_access_level', return_value='full'):
            context = {'trust_relationship': self.trust_relationship}
            
            access_level = self.strategy.get_access_level(context)
            
            self.assertEqual(access_level, 'full')
    
    def test_get_access_level_no_relationship(self):
        """Test getting access level with no relationship"""
        context = {}
        
        access_level = self.strategy.get_access_level(context)
        
        self.assertEqual(access_level, 'none')


class CommunityAccessStrategyTest(CrispTestCase):
    """Test CommunityAccessStrategy"""
    
    def setUp(self):
        super().setUp()
        self.strategy = CommunityAccessStrategy()
        
        self.org1 = Organization.objects.create(
            name="Community Org 1", domain="comm1.com", contact_email="test@comm1.com"
        )
        self.org2 = Organization.objects.create(
            name="Community Org 2", domain="comm2.com", contact_email="test@comm2.com"
        )
        
        # Create trust group
        self.trust_group = TrustGroup.objects.create(
            name="Test Community",
            description="Test community group",
            administrator=self.org1
        )
    
    @patch('core.strategies.access_control_strategies.TrustService.check_trust_level')
    def test_can_access_community_relationship(self, mock_check_trust):
        """Test access granted for community relationship"""
        # Mock trust relationship
        mock_relationship = Mock()
        mock_relationship.relationship_type = 'community'
        mock_relationship.trust_group.name = 'Test Community'
        
        mock_check_trust.return_value = (5, mock_relationship)
        
        context = {
            'requesting_organization': self.org1,
            'target_organization': self.org2
        }
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
        self.assertIn("Access granted via community trust group", reason)
    
    @patch('core.strategies.access_control_strategies.TrustService.check_trust_level')
    def test_can_access_non_community_relationship(self, mock_check_trust):
        """Test access denied for non-community relationship"""
        mock_relationship = Mock()
        mock_relationship.relationship_type = 'bilateral'
        
        mock_check_trust.return_value = (3, mock_relationship)
        
        context = {
            'requesting_organization': self.org1,
            'target_organization': self.org2
        }
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertEqual(reason, "Not a community-based relationship")
    
    @patch('core.strategies.access_control_strategies.TrustService.check_trust_level')
    def test_can_access_no_trust_info(self, mock_check_trust):
        """Test access denied with no trust info"""
        mock_check_trust.return_value = None
        
        context = {
            'requesting_organization': self.org1,
            'target_organization': self.org2
        }
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertEqual(reason, "No trust relationship exists")
    
    def test_can_access_missing_organizations(self):
        """Test access denied with missing organization info"""
        context = {'requesting_organization': self.org1}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertEqual(reason, "Missing organization information")
    
    def test_get_access_level_community(self):
        """Test getting access level for community relationship"""
        mock_relationship = Mock()
        mock_relationship.relationship_type = 'community'
        mock_relationship.trust_group.default_trust_level.default_access_level = 'shared'
        
        context = {'trust_relationship': mock_relationship}
        
        access_level = self.strategy.get_access_level(context)
        
        self.assertEqual(access_level, 'shared')
    
    def test_get_access_level_non_community(self):
        """Test getting access level for non-community relationship"""
        mock_relationship = Mock()
        mock_relationship.relationship_type = 'bilateral'
        
        context = {'trust_relationship': mock_relationship}
        
        access_level = self.strategy.get_access_level(context)
        
        self.assertEqual(access_level, 'none')


class TimeBasedAccessStrategyTest(CrispTestCase):
    """Test TimeBasedAccessStrategy"""
    
    def setUp(self):
        super().setUp()
        self.strategy = TimeBasedAccessStrategy()
        
        self.org1 = Organization.objects.create(
            name="Time Org 1", domain="time1.com", contact_email="test@time1.com"
        )
        self.org2 = Organization.objects.create(
            name="Time Org 2", domain="time2.com", contact_email="test@time2.com"
        )
        
        self.trust_level = TrustLevel.objects.create(
            name="Time Trust",
            numerical_value=3,
            default_access_level="limited"
        )
    
    def test_can_access_valid_time_window(self):
        """Test access granted within valid time window"""
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30)
        )
        
        context = {'trust_relationship': trust_relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
        self.assertEqual(reason, "Access granted within valid time window")
    
    def test_can_access_not_yet_valid(self):
        """Test access denied before valid time"""
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            valid_from=timezone.now() + timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30)
        )
        
        context = {'trust_relationship': trust_relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn("Trust relationship not yet valid", reason)
    
    def test_can_access_expired(self):
        """Test access denied after expiration"""
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            valid_from=timezone.now() - timedelta(days=30),
            valid_until=timezone.now() - timedelta(days=1)
        )
        
        context = {'trust_relationship': trust_relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn("Trust relationship expired", reason)
    
    def test_can_access_no_expiry(self):
        """Test access granted with no expiry date"""
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=None
        )
        
        context = {'trust_relationship': trust_relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
    
    def test_get_access_level_valid(self):
        """Test getting access level when time is valid"""
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30)
        )
        
        with patch.object(trust_relationship, 'get_effective_access_level', return_value='limited'):
            context = {'trust_relationship': trust_relationship}
            
            access_level = self.strategy.get_access_level(context)
            
            self.assertEqual(access_level, 'limited')
    
    def test_get_access_level_invalid_time(self):
        """Test getting access level when time is invalid"""
        trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            valid_from=timezone.now() + timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30)
        )
        
        context = {'trust_relationship': trust_relationship}
        
        access_level = self.strategy.get_access_level(context)
        
        self.assertEqual(access_level, 'none')


class NoAnonymizationStrategyTest(CrispTestCase):
    """Test NoAnonymizationStrategy"""
    
    def setUp(self):
        super().setUp()
        self.strategy = NoAnonymizationStrategy()
    
    def test_anonymize_returns_copy(self):
        """Test that anonymize returns unchanged copy of data"""
        data = {'type': 'indicator', 'pattern': 'test', 'created_by_ref': 'identity--test'}
        context = {}
        
        result = self.strategy.anonymize(data, context)
        
        self.assertEqual(result, data)
        self.assertIsNot(result, data)  # Should be a copy
    
    def test_get_anonymization_level(self):
        """Test getting anonymization level"""
        level = self.strategy.get_anonymization_level()
        
        self.assertEqual(level, 'none')


class MinimalAnonymizationStrategyTest(CrispTestCase):
    """Test MinimalAnonymizationStrategy"""
    
    def setUp(self):
        super().setUp()
        self.strategy = MinimalAnonymizationStrategy()
    
    def test_anonymize_removes_attribution(self):
        """Test that anonymization removes attribution"""
        data = {
            'type': 'indicator',
            'pattern': 'test',
            'created_by_ref': 'identity--original',
            'x_attribution': 'sensitive info'
        }
        context = {}
        
        result = self.strategy.anonymize(data, context)
        
        self.assertNotEqual(result['created_by_ref'], 'identity--original')
        self.assertNotIn('x_attribution', result)
        self.assertEqual(result['type'], 'indicator')
        self.assertEqual(result['pattern'], 'test')
    
    def test_anonymize_identity_ref(self):
        """Test identity reference anonymization"""
        identity_ref = 'identity--test-123'
        
        result = self.strategy._anonymize_identity_ref(identity_ref)
        
        self.assertTrue(result.startswith('identity--'))
        self.assertNotEqual(result, identity_ref)
        self.assertEqual(len(result), len('identity--') + 8)  # 8-char hash
    
    def test_get_anonymization_level(self):
        """Test getting anonymization level"""
        level = self.strategy.get_anonymization_level()
        
        self.assertEqual(level, 'minimal')


class PartialAnonymizationStrategyTest(CrispTestCase):
    """Test PartialAnonymizationStrategy"""
    
    def setUp(self):
        super().setUp()
        self.strategy = PartialAnonymizationStrategy()
    
    def test_anonymize_indicator(self):
        """Test anonymizing indicator objects"""
        data = {
            'type': 'indicator',
            'pattern': '[file:hashes.MD5 = "test123"]',
            'created_by_ref': 'identity--original',
            'x_attribution': 'sensitive'
        }
        context = {}
        
        result = self.strategy.anonymize(data, context)
        
        # Should apply minimal anonymization
        self.assertNotIn('x_attribution', result)
        self.assertNotEqual(result['created_by_ref'], 'identity--original')
        
        # Should anonymize pattern
        self.assertNotEqual(result['pattern'], data['pattern'])
    
    def test_anonymize_observed_data(self):
        """Test anonymizing observed-data objects"""
        data = {
            'type': 'observed-data',
            'objects': {'0': {'type': 'file', 'hashes': {'MD5': 'test123'}}},
            'created_by_ref': 'identity--original'
        }
        context = {}
        
        result = self.strategy.anonymize(data, context)
        
        # Should apply minimal anonymization
        self.assertNotEqual(result['created_by_ref'], 'identity--original')
        
        # Should anonymize objects
        self.assertIn('objects', result)
    
    def test_get_anonymization_level(self):
        """Test getting anonymization level"""
        level = self.strategy.get_anonymization_level()
        
        self.assertEqual(level, 'partial')


class AnonymizationContextTest(CrispTestCase):
    """Test AnonymizationContext"""
    
    def setUp(self):
        super().setUp()
        self.org1 = Organization.objects.create(
            name="Context Org 1", domain="context1.com", contact_email="test@context1.com"
        )
        self.org2 = Organization.objects.create(
            name="Context Org 2", domain="context2.com", contact_email="test@context2.com"
        )
    
    def test_anonymization_context_creation(self):
        """Test creating anonymization context"""
        context = AnonymizationContext(
            source_organization=self.org1,
            target_organization=self.org2,
            anonymization_level='partial',
            preserve_patterns=['ip', 'domain']
        )
        
        self.assertEqual(context.source_organization, self.org1)
        self.assertEqual(context.target_organization, self.org2)
        self.assertEqual(context.anonymization_level, 'partial')
        self.assertEqual(context.preserve_patterns, ['ip', 'domain'])
    
    def test_anonymization_context_to_dict(self):
        """Test converting context to dictionary"""
        context = AnonymizationContext(
            source_organization=self.org1,
            target_organization=self.org2,
            anonymization_level='minimal'
        )
        
        context_dict = context.to_dict()
        
        self.assertIn('source_organization', context_dict)
        self.assertIn('target_organization', context_dict)
        self.assertEqual(context_dict['anonymization_level'], 'minimal')


class AccessControlContextTest(CrispTestCase):
    """Test AccessControlContext"""
    
    def setUp(self):
        super().setUp()
        self.org1 = Organization.objects.create(
            name="Access Context Org 1", domain="access_context1.com", contact_email="test@access_context1.com"
        )
        self.user = CustomUser.objects.create_user(
            username="access_user", email="user@access_context1.com", password="testpass123",
            organization=self.org1, role="viewer"
        )
    
    def test_access_control_context_creation(self):
        """Test creating access control context"""
        context = AccessControlContext(
            requesting_user=self.user,
            requesting_organization=self.org1,
            resource_type='threat_feed',
            action='read'
        )
        
        self.assertEqual(context.requesting_user, self.user)
        self.assertEqual(context.requesting_organization, self.org1)
        self.assertEqual(context.resource_type, 'threat_feed')
        self.assertEqual(context.action, 'read')
    
    def test_access_control_context_to_dict(self):
        """Test converting context to dictionary"""
        context = AccessControlContext(
            requesting_user=self.user,
            requesting_organization=self.org1,
            resource_type='indicator',
            action='create',
            ip_address='192.168.1.100'
        )
        
        context_dict = context.to_dict()
        
        self.assertIn('requesting_user', context_dict)
        self.assertIn('requesting_organization', context_dict)
        self.assertEqual(context_dict['resource_type'], 'indicator')
        self.assertEqual(context_dict['action'], 'create')
        self.assertEqual(context_dict['ip_address'], '192.168.1.100')


class FullAnonymizationStrategyTest(CrispTestCase):
    """Test FullAnonymizationStrategy"""
    
    def setUp(self):
        super().setUp()
        self.strategy = FullAnonymizationStrategy()
    
    def test_anonymize_removes_all_identifiers(self):
        """Test that full anonymization removes all identifiers"""
        data = {
            'type': 'indicator',
            'pattern': '[file:hashes.MD5 = "sensitive"]',
            'created_by_ref': 'identity--original',
            'x_attribution': 'sensitive',
            'external_references': [{'url': 'http://example.com'}]
        }
        context = {}
        
        result = self.strategy.anonymize(data, context)
        
        # Should remove all identifying information
        self.assertNotIn('x_attribution', result)
        self.assertNotIn('external_references', result)
        self.assertNotEqual(result['created_by_ref'], 'identity--original')
        self.assertNotEqual(result['pattern'], data['pattern'])
    
    def test_get_anonymization_level(self):
        """Test getting anonymization level"""
        level = self.strategy.get_anonymization_level()
        
        self.assertEqual(level, 'full')


class CustomAnonymizationStrategyTest(CrispTestCase):
    """Test CustomAnonymizationStrategy"""
    
    def setUp(self):
        super().setUp()
        custom_rules = {
            'preserve_fields': ['type', 'labels'],
            'hash_fields': ['pattern'],
            'remove_fields': ['external_references']
        }
        self.strategy = CustomAnonymizationStrategy(custom_rules)
    
    def test_anonymize_with_custom_rules(self):
        """Test anonymization with custom rules"""
        data = {
            'type': 'indicator',
            'pattern': 'sensitive_pattern',
            'labels': ['malicious-activity'],
            'external_references': [{'url': 'http://example.com'}],
            'created_by_ref': 'identity--test'
        }
        context = {}
        
        result = self.strategy.anonymize(data, context)
        
        # Should preserve specified fields
        self.assertEqual(result['type'], 'indicator')
        self.assertEqual(result['labels'], ['malicious-activity'])
        
        # Should remove specified fields
        self.assertNotIn('external_references', result)
        
        # Should hash specified fields
        self.assertNotEqual(result['pattern'], 'sensitive_pattern')
    
    def test_get_anonymization_level(self):
        """Test getting anonymization level"""
        level = self.strategy.get_anonymization_level()
        
        self.assertEqual(level, 'custom')


class StrategyIntegrationTest(CrispTestCase):
    """Test strategy integration and combinations"""
    
    def setUp(self):
        super().setUp()
        self.org1 = Organization.objects.create(
            name="Integration Org 1", domain="integration1.com", contact_email="test@integration1.com"
        )
        self.org2 = Organization.objects.create(
            name="Integration Org 2", domain="integration2.com", contact_email="test@integration2.com"
        )
        
        self.trust_level = TrustLevel.objects.create(
            name="Integration Trust",
            numerical_value=4,
            default_access_level="shared",
            default_anonymization_level="partial"
        )
        
        self.trust_relationship = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=self.trust_level,
            status="approved",
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30)
        )
    
    def test_combined_access_strategies(self):
        """Test combining multiple access control strategies"""
        trust_strategy = TrustLevelAccessStrategy(minimum_trust_level=3)
        time_strategy = TimeBasedAccessStrategy()
        
        context = {'trust_relationship': self.trust_relationship}
        
        # Both strategies should allow access
        trust_access, trust_reason = trust_strategy.can_access(context)
        time_access, time_reason = time_strategy.can_access(context)
        
        self.assertTrue(trust_access)
        self.assertTrue(time_access)
    
    def test_access_and_anonymization_integration(self):
        """Test integration between access control and anonymization"""
        access_strategy = TrustLevelAccessStrategy(minimum_trust_level=2)
        anon_strategy = PartialAnonymizationStrategy()
        
        context = {'trust_relationship': self.trust_relationship}
        data = {
            'type': 'indicator',
            'pattern': '[ip-addr:value = "192.168.1.1"]',
            'created_by_ref': 'identity--test'
        }
        
        # Check access first
        can_access, reason = access_strategy.can_access(context)
        self.assertTrue(can_access)
        
        # Then apply anonymization
        anonymized_data = anon_strategy.anonymize(data, context)
        self.assertNotEqual(anonymized_data['pattern'], data['pattern'])
    
    def test_strategy_error_handling(self):
        """Test strategy error handling"""
        strategy = TrustLevelAccessStrategy()
        
        # Test with invalid context
        invalid_context = {'invalid_key': 'invalid_value'}
        
        can_access, reason = strategy.can_access(invalid_context)
        
        self.assertFalse(can_access)
        self.assertIn("No trust relationship", reason)