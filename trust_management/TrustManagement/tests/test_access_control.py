import uuid
from django.test import TestCase
from unittest.mock import MagicMock, patch

from ..models import TrustLevel, TrustRelationship, TrustGroup
from ..strategies.access_control_strategies import (
    TrustLevelAccessStrategy, CommunityAccessStrategy, TimeBasedAccessStrategy,
    NoAnonymizationStrategy, MinimalAnonymizationStrategy, PartialAnonymizationStrategy,
    FullAnonymizationStrategy, CustomAnonymizationStrategy,
    AnonymizationContext, AccessControlContext
)


class TrustLevelAccessStrategyTest(TestCase):
    """Test cases for TrustLevelAccessStrategy."""
    
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
        
        self.relationship = TrustRelationship(
            source_organization=str(uuid.uuid4()),
            target_organization=str(uuid.uuid4()),
            trust_level=self.trust_level,
            status='active',
            is_active=True,
            approved_by_source=True,
            approved_by_target=True
        )
        
        self.strategy = TrustLevelAccessStrategy(minimum_trust_level=25)
    
    def test_can_access_with_sufficient_trust(self):
        """Test access with sufficient trust level."""
        context = {'trust_relationship': self.relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
        self.assertIn('Access granted via trust level', reason)
    
    def test_can_access_with_insufficient_trust(self):
        """Test access with insufficient trust level."""
        self.strategy = TrustLevelAccessStrategy(minimum_trust_level=75)
        context = {'trust_relationship': self.relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn('Trust level too low', reason)
    
    def test_can_access_no_relationship(self):
        """Test access with no trust relationship."""
        context = {'trust_relationship': None}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertEqual(reason, 'No trust relationship exists')
    
    def test_can_access_inactive_relationship(self):
        """Test access with inactive relationship."""
        self.relationship.status = 'suspended'
        context = {'trust_relationship': self.relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn('not effective', reason)
    
    def test_get_access_level(self):
        """Test getting access level."""
        context = {'trust_relationship': self.relationship}
        
        access_level = self.strategy.get_access_level(context)
        
        self.assertEqual(access_level, 'read')
    
    def test_get_access_level_no_relationship(self):
        """Test getting access level with no relationship."""
        context = {'trust_relationship': None}
        
        access_level = self.strategy.get_access_level(context)
        
        self.assertEqual(access_level, 'none')


class CommunityAccessStrategyTest(TestCase):
    """Test cases for CommunityAccessStrategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Community Trust Level',
            level='medium',
            description='Community trust level',
            numerical_value=50,
            default_access_level='read',
            created_by='test_user'
        )
        
        self.trust_group = TrustGroup.objects.create(
            name='Test Community',
            description='Test community group',
            default_trust_level=self.trust_level,
            created_by='org_1'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        self.strategy = CommunityAccessStrategy()
    
    @patch('TrustManagement.services.trust_service.TrustService')
    def test_can_access_community_relationship(self, mock_trust_service):
        """Test access with community relationship."""
        # Mock community relationship
        community_relationship = TrustRelationship(
            source_organization=self.org_1,
            target_organization=self.org_2,
            relationship_type='community',
            trust_group=self.trust_group,
            trust_level=self.trust_level
        )
        
        mock_trust_service.check_trust_level.return_value = (self.trust_level, community_relationship)
        
        context = {
            'requesting_organization': self.org_1,
            'target_organization': self.org_2
        }
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
        self.assertIn('community trust group', reason)
    
    @patch('TrustManagement.services.trust_service.TrustService')
    def test_can_access_non_community_relationship(self, mock_trust_service):
        """Test access with non-community relationship."""
        # Mock bilateral relationship
        bilateral_relationship = TrustRelationship(
            source_organization=self.org_1,
            target_organization=self.org_2,
            relationship_type='bilateral',
            trust_level=self.trust_level
        )
        
        mock_trust_service.check_trust_level.return_value = (self.trust_level, bilateral_relationship)
        
        context = {
            'requesting_organization': self.org_1,
            'target_organization': self.org_2
        }
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn('Not a community-based relationship', reason)
    
    @patch('TrustManagement.services.trust_service.TrustService')
    def test_can_access_no_relationship(self, mock_trust_service):
        """Test access with no relationship."""
        mock_trust_service.check_trust_level.return_value = None
        
        context = {
            'requesting_organization': self.org_1,
            'target_organization': self.org_2
        }
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertEqual(reason, 'No trust relationship exists')


class TimeBasedAccessStrategyTest(TestCase):
    """Test cases for TimeBasedAccessStrategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.trust_level = TrustLevel.objects.create(
            name='Time Test Trust Level',
            level='medium',
            description='Time-based trust level',
            numerical_value=50,
            default_access_level='read',
            created_by='test_user'
        )
        
        self.now = timezone.now()
        self.relationship = TrustRelationship(
            source_organization=str(uuid.uuid4()),
            target_organization=str(uuid.uuid4()),
            trust_level=self.trust_level,
            valid_from=self.now - timedelta(hours=1),
            valid_until=self.now + timedelta(hours=1)
        )
        
        self.strategy = TimeBasedAccessStrategy()
    
    def test_can_access_within_valid_window(self):
        """Test access within valid time window."""
        context = {'trust_relationship': self.relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
        self.assertIn('valid time window', reason)
    
    def test_can_access_before_valid_from(self):
        """Test access before valid_from date."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.relationship.valid_from = timezone.now() + timedelta(hours=1)
        context = {'trust_relationship': self.relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn('not yet valid', reason)
    
    def test_can_access_after_valid_until(self):
        """Test access after valid_until date."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.relationship.valid_until = timezone.now() - timedelta(hours=1)
        context = {'trust_relationship': self.relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertFalse(can_access)
        self.assertIn('expired', reason)
    
    def test_can_access_no_expiration(self):
        """Test access with no expiration date."""
        self.relationship.valid_until = None
        context = {'trust_relationship': self.relationship}
        
        can_access, reason = self.strategy.can_access(context)
        
        self.assertTrue(can_access)
        self.assertIn('valid time window', reason)


class AnonymizationStrategyTest(TestCase):
    """Test cases for anonymization strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = {
            'type': 'indicator',
            'id': 'indicator--12345',
            'pattern': "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e'] OR [network-traffic:src_ref.value = '192.168.1.100']",
            'created_by_ref': 'identity--org-123',
            'external_references': [
                {'source_name': 'test-source', 'url': 'https://example.com'}
            ],
            'x_attribution': 'Test Organization'
        }
        
        self.context = {}
    
    def test_no_anonymization_strategy(self):
        """Test no anonymization strategy."""
        strategy = NoAnonymizationStrategy()
        
        result = strategy.anonymize(self.sample_data, self.context)
        
        self.assertEqual(result, self.sample_data)
        self.assertEqual(strategy.get_anonymization_level(), 'none')
    
    def test_minimal_anonymization_strategy(self):
        """Test minimal anonymization strategy."""
        strategy = MinimalAnonymizationStrategy()
        
        result = strategy.anonymize(self.sample_data, self.context)
        
        # Should remove attribution but keep most data
        self.assertNotIn('x_attribution', result)
        self.assertNotEqual(result['created_by_ref'], self.sample_data['created_by_ref'])
        self.assertEqual(result['pattern'], self.sample_data['pattern'])  # Pattern unchanged
        self.assertEqual(strategy.get_anonymization_level(), 'minimal')
    
    def test_partial_anonymization_strategy(self):
        """Test partial anonymization strategy."""
        strategy = PartialAnonymizationStrategy()
        
        result = strategy.anonymize(self.sample_data, self.context)
        
        # Should anonymize indicators in pattern
        self.assertNotIn('x_attribution', result)
        self.assertNotEqual(result['pattern'], self.sample_data['pattern'])
        self.assertIn('xxx', result['pattern'])  # IP should be anonymized
        self.assertEqual(strategy.get_anonymization_level(), 'partial')
    
    def test_full_anonymization_strategy(self):
        """Test full anonymization strategy."""
        strategy = FullAnonymizationStrategy()
        
        result = strategy.anonymize(self.sample_data, self.context)
        
        # Should remove external references and custom properties
        self.assertNotIn('external_references', result)
        self.assertNotIn('x_attribution', result)
        self.assertEqual(strategy.get_anonymization_level(), 'full')
    
    def test_custom_anonymization_strategy(self):
        """Test custom anonymization strategy."""
        rules = {
            'base_level': 'minimal',
            'field_rules': {
                'pattern': 'remove',
                'id': 'hash'
            }
        }
        
        strategy = CustomAnonymizationStrategy(rules)
        
        result = strategy.anonymize(self.sample_data, self.context)
        
        # Should apply custom rules
        self.assertNotIn('pattern', result)  # Removed
        self.assertNotEqual(result['id'], self.sample_data['id'])  # Hashed
        self.assertEqual(strategy.get_anonymization_level(), 'custom')
    
    def test_ip_address_anonymization(self):
        """Test IP address anonymization."""
        strategy = PartialAnonymizationStrategy()
        
        # Test IPv4 anonymization
        ipv4_text = "network-traffic:src_ref.value = '192.168.1.100'"
        result = strategy._anonymize_ip_addresses(ipv4_text)
        self.assertIn('192.168.xxx.xxx', result)
        
        # Test IPv6 anonymization (simplified test)
        ipv6_text = "network-traffic:src_ref.value = '2001:0db8:85a3:0000:0000:8a2e:0370:7334'"
        result = strategy._anonymize_ip_addresses(ipv6_text)
        self.assertIn('::xxxx', result)
    
    def test_domain_anonymization(self):
        """Test domain name anonymization."""
        strategy = PartialAnonymizationStrategy()
        
        domain_text = "domain-name:value = 'malicious.example.com'"
        result = strategy._anonymize_domains(domain_text)
        
        # Should keep TLD and one level up
        self.assertIn('example.com', result)
        self.assertNotIn('malicious', result)
    
    def test_email_anonymization(self):
        """Test email address anonymization."""
        strategy = PartialAnonymizationStrategy()
        
        email_text = "email-addr:value = 'user@malicious.example.com'"
        result = strategy._anonymize_email_addresses(email_text)
        
        # Should anonymize local part and domain
        self.assertNotIn('user@malicious', result)
        self.assertIn('@', result)


class AnonymizationContextTest(TestCase):
    """Test cases for AnonymizationContext."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Context Trust Level',
            level='medium',
            description='Context trust level',
            numerical_value=50,
            default_anonymization_level='partial',
            created_by='test_user'
        )
        
        self.relationship = TrustRelationship(
            source_organization=str(uuid.uuid4()),
            target_organization=str(uuid.uuid4()),
            trust_level=self.trust_level,
            anonymization_level='partial'
        )
        
        self.context = AnonymizationContext(trust_relationship=self.relationship)
    
    def test_get_strategy_for_trust_level(self):
        """Test getting strategy for trust level."""
        # Test different anonymization levels
        strategies = {
            'none': NoAnonymizationStrategy,
            'minimal': MinimalAnonymizationStrategy,
            'partial': PartialAnonymizationStrategy,
            'full': FullAnonymizationStrategy,
            'custom': CustomAnonymizationStrategy
        }
        
        for level, expected_class in strategies.items():
            self.relationship.anonymization_level = level
            if level == 'custom':
                self.relationship.sharing_preferences = {'anonymization_rules': {}}
            
            strategy = self.context.get_strategy_for_trust_level(level)
            self.assertIsInstance(strategy, expected_class)
    
    def test_anonymize_data(self):
        """Test data anonymization through context."""
        sample_data = {
            'type': 'indicator',
            'pattern': "[network-traffic:src_ref.value = '192.168.1.100']",
            'x_attribution': 'Test Organization'
        }
        
        result = self.context.anonymize_data(sample_data)
        
        # Should apply partial anonymization
        self.assertNotIn('x_attribution', result)
        self.assertIn('xxx', result['pattern'])


class AccessControlContextTest(TestCase):
    """Test cases for AccessControlContext."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        self.trust_level = TrustLevel.objects.create(
            name='Access Trust Level',
            level='high',
            description='Access trust level',
            numerical_value=75,
            default_access_level='contribute',
            created_by='test_user'
        )
        
        self.relationship = TrustRelationship(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            status='active',
            is_active=True,
            approved_by_source=True,
            approved_by_target=True,
            access_level='contribute'
        )
        
        self.context = AccessControlContext(
            requesting_org=self.org_1,
            target_org=self.org_2,
            resource_type='indicator'
        )
    
    def test_can_access_with_strategies(self):
        """Test access control with multiple strategies."""
        # Add strategies
        self.context.add_strategy(TrustLevelAccessStrategy(minimum_trust_level=50))
        self.context.add_strategy(TimeBasedAccessStrategy())
        
        can_access, reasons = self.context.can_access(trust_relationship=self.relationship)
        
        self.assertTrue(can_access)
        self.assertEqual(len(reasons), 2)  # One reason per strategy
        
        # Each strategy should provide a reason
        for reason in reasons:
            self.assertIn(':', reason)  # Should contain strategy name
    
    def test_can_access_with_failing_strategy(self):
        """Test access control with one failing strategy."""
        # Add strategies with one that will fail
        self.context.add_strategy(TrustLevelAccessStrategy(minimum_trust_level=50))  # Will pass
        self.context.add_strategy(TrustLevelAccessStrategy(minimum_trust_level=90))  # Will fail
        
        can_access, reasons = self.context.can_access(trust_relationship=self.relationship)
        
        self.assertFalse(can_access)  # Should fail if any strategy fails
        self.assertEqual(len(reasons), 2)
    
    def test_get_access_level_most_restrictive(self):
        """Test getting most restrictive access level."""
        # Add strategies with different access levels
        self.context.add_strategy(TrustLevelAccessStrategy())  # Returns 'contribute'
        
        # Mock a strategy that returns 'read'
        restrictive_strategy = TrustLevelAccessStrategy()
        restrictive_strategy.get_access_level = lambda ctx: 'read'
        self.context.add_strategy(restrictive_strategy)
        
        access_level = self.context.get_access_level(trust_relationship=self.relationship)
        
        # Should return the most restrictive level
        self.assertEqual(access_level, 'read')