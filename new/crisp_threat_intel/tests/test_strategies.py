import pytest
from django.test import TestCase
import json

from ..strategies.anonymization_strategy import (
    AnonymizationStrategy, NoAnonymizationStrategy, PartialAnonymizationStrategy,
    FullAnonymizationStrategy, DomainAnonymizationStrategy, IPAddressAnonymizationStrategy,
    EmailAnonymizationStrategy, AnonymizationContext, AnonymizationStrategyFactory,
    anonymize_ip_address, anonymize_domain_name, anonymize_email_address,
    anonymize_url, anonymize_file_hash, anonymize_stix_pattern
)


class TestAnonymizationAlgorithms(TestCase):
    """Test cases for anonymization algorithms"""
    
    def test_anonymize_ip_address(self):
        """Test IP address anonymization"""
        # Test IPv4 partial anonymization
        result = anonymize_ip_address('192.168.1.100', 'partial')
        self.assertEqual(result, '192.168.1.0')
        
        # Test IPv4 full anonymization
        result = anonymize_ip_address('192.168.1.100', 'full')
        self.assertEqual(result, '10.0.0.1')
        
        # Test IPv6 partial anonymization
        result = anonymize_ip_address('2001:db8:85a3::8a2e:370:7334', 'partial')
        self.assertEqual(result, '2001:db8:85a3::')
        
        # Test IPv6 full anonymization
        result = anonymize_ip_address('2001:db8:85a3::8a2e:370:7334', 'full')
        self.assertEqual(result, '2001:db8::1')
        
        # Test invalid IP
        result = anonymize_ip_address('invalid.ip', 'partial')
        self.assertEqual(result, 'invalid_ip_format')
    
    def test_anonymize_domain_name(self):
        """Test domain name anonymization"""
        # Test partial anonymization
        result = anonymize_domain_name('www.example.com', 'partial')
        self.assertTrue(result.startswith('anon-'))
        self.assertTrue(result.endswith('.example.com'))
        
        # Test full anonymization
        result = anonymize_domain_name('www.example.com', 'full')
        self.assertEqual(result, 'anonymized.example.com')
        
        # Test simple domain
        result = anonymize_domain_name('example.com', 'partial')
        self.assertEqual(result, 'example.com')  # Should be preserved
    
    def test_anonymize_email_address(self):
        """Test email address anonymization"""
        # Test partial anonymization
        result = anonymize_email_address('user@example.com', 'partial')
        self.assertTrue(result.startswith('anonuser-'))
        self.assertIn('@', result)
        
        # Test full anonymization
        result = anonymize_email_address('user@example.com', 'full')
        self.assertEqual(result, 'user@anonymized.example.com')
        
        # Test invalid email
        result = anonymize_email_address('invalid-email', 'partial')
        self.assertEqual(result, 'anonymized.email')
    
    def test_anonymize_url(self):
        """Test URL anonymization"""
        # Test partial anonymization
        result = anonymize_url('https://www.example.com/path?query=value', 'partial')
        self.assertTrue(result.startswith('https://'))
        self.assertIn('anon-', result)
        self.assertIn('/anonymized_path', result)
        
        # Test full anonymization
        result = anonymize_url('https://www.example.com/path', 'full')
        self.assertEqual(result, 'https://anonymized.example.com/path')
    
    def test_anonymize_file_hash(self):
        """Test file hash anonymization"""
        test_hash = 'abc123def456'
        
        # Test partial anonymization
        result = anonymize_file_hash(test_hash, 'MD5', 'partial')
        self.assertTrue(result.startswith('anon:'))
        self.assertEqual(len(result) - 5, len(test_hash))  # anon: prefix
        
        # Test full anonymization
        result = anonymize_file_hash(test_hash, 'MD5', 'full')
        self.assertEqual(result, 'anon:[MD5_VALUE_REMOVED]')
    
    def test_anonymize_stix_pattern(self):
        """Test STIX pattern anonymization"""
        # Test IP anonymization in pattern
        pattern = "[ipv4-addr:value = '192.168.1.100']"
        result = anonymize_stix_pattern(pattern, 'partial')
        self.assertIn('192.168.1.0', result)
        
        # Test domain anonymization in pattern
        pattern = "[domain-name:value = 'www.evil.com']"
        result = anonymize_stix_pattern(pattern, 'partial')
        self.assertIn('anon-', result)
        
        # Test email anonymization in pattern
        pattern = "[email-addr:value = 'bad@evil.com']"
        result = anonymize_stix_pattern(pattern, 'partial')
        self.assertIn('anonuser-', result)


class TestAnonymizationStrategies(TestCase):
    """Test cases for anonymization strategies"""
    
    def setUp(self):
        self.sample_stix_object = {
            'type': 'indicator',
            'id': 'indicator--12345678-1234-1234-1234-123456789012',
            'created': '2024-01-01T00:00:00.000Z',
            'modified': '2024-01-01T00:00:00.000Z',
            'spec_version': '2.1',
            'name': 'Malicious IP',
            'description': 'A known malicious IP address 192.168.1.100',
            'pattern': "[ipv4-addr:value = '192.168.1.100']",
            'labels': ['malicious-activity'],
            'valid_from': '2024-01-01T00:00:00.000Z',
            'confidence': 85,
            'created_by_ref': 'identity--test-org'
        }
    
    def test_no_anonymization_strategy(self):
        """Test no anonymization strategy"""
        strategy = NoAnonymizationStrategy()
        result = strategy.anonymize(self.sample_stix_object, trust_level=1.0)
        
        # Should be identical to original
        self.assertEqual(result, self.sample_stix_object)
        self.assertEqual(strategy.get_effectiveness_score(), 1.0)
    
    def test_partial_anonymization_strategy(self):
        """Test partial anonymization strategy"""
        strategy = PartialAnonymizationStrategy()
        result = strategy.anonymize(self.sample_stix_object, trust_level=0.5)
        
        # Should preserve structure but anonymize sensitive fields
        self.assertEqual(result['type'], 'indicator')
        self.assertEqual(result['id'], self.sample_stix_object['id'])
        self.assertNotEqual(result['name'], self.sample_stix_object['name'])
        self.assertNotEqual(result['description'], self.sample_stix_object['description'])
        self.assertNotEqual(result['pattern'], self.sample_stix_object['pattern'])
        
        # Should preserve non-sensitive fields
        self.assertEqual(result['labels'], self.sample_stix_object['labels'])
        self.assertEqual(result['confidence'], self.sample_stix_object['confidence'])
    
    def test_full_anonymization_strategy(self):
        """Test full anonymization strategy"""
        strategy = FullAnonymizationStrategy()
        result = strategy.anonymize(self.sample_stix_object, trust_level=0.0)
        
        # Should preserve essential STIX fields
        self.assertEqual(result['type'], 'indicator')
        self.assertEqual(result['id'], self.sample_stix_object['id'])
        self.assertEqual(result['spec_version'], '2.1')
        
        # Should anonymize most other fields
        self.assertNotEqual(result['name'], self.sample_stix_object['name'])
        self.assertNotEqual(result['pattern'], self.sample_stix_object['pattern'])
        
        # Should have indicator-specific fields
        self.assertIn('pattern_type', result)
        self.assertIn('valid_from', result)
    
    def test_domain_anonymization_strategy(self):
        """Test domain-specific anonymization strategy"""
        stix_object = {
            'type': 'indicator',
            'id': 'indicator--test',
            'domain_name': 'www.evil.com',
            'hostname': 'malicious.example.org',
            'other_field': 'should not change'
        }
        
        strategy = DomainAnonymizationStrategy()
        result = strategy.anonymize(stix_object, trust_level=0.5)
        
        self.assertNotEqual(result['domain_name'], stix_object['domain_name'])
        self.assertNotEqual(result['hostname'], stix_object['hostname'])
        self.assertEqual(result['other_field'], stix_object['other_field'])
    
    def test_ip_address_anonymization_strategy(self):
        """Test IP address-specific anonymization strategy"""
        stix_object = {
            'type': 'indicator',
            'id': 'indicator--test',
            'ip_address': '192.168.1.100',
            'source_ip': '10.0.0.1',
            'other_field': 'should not change'
        }
        
        strategy = IPAddressAnonymizationStrategy()
        result = strategy.anonymize(stix_object, trust_level=0.5)
        
        self.assertNotEqual(result['ip_address'], stix_object['ip_address'])
        self.assertNotEqual(result['source_ip'], stix_object['source_ip'])
        self.assertEqual(result['other_field'], stix_object['other_field'])
    
    def test_email_anonymization_strategy(self):
        """Test email-specific anonymization strategy"""
        stix_object = {
            'type': 'indicator',
            'id': 'indicator--test',
            'email_address': 'bad@evil.com',
            'sender_email': 'phish@malicious.org',
            'other_field': 'should not change'
        }
        
        strategy = EmailAnonymizationStrategy()
        result = strategy.anonymize(stix_object, trust_level=0.5)
        
        self.assertNotEqual(result['email_address'], stix_object['email_address'])
        self.assertNotEqual(result['sender_email'], stix_object['sender_email'])
        self.assertEqual(result['other_field'], stix_object['other_field'])
    
    def test_strategy_with_json_input(self):
        """Test strategy with JSON string input"""
        strategy = PartialAnonymizationStrategy()
        json_input = json.dumps(self.sample_stix_object)
        
        result = strategy.anonymize(json_input, trust_level=0.5)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'indicator')
    
    def test_strategy_with_invalid_input(self):
        """Test strategy with invalid input"""
        strategy = PartialAnonymizationStrategy()
        
        # Test invalid JSON
        with self.assertRaises(ValueError):
            strategy.anonymize('invalid json', trust_level=0.5)
        
        # Test invalid type
        with self.assertRaises(TypeError):
            strategy.anonymize(123, trust_level=0.5)


class TestAnonymizationContext(TestCase):
    """Test cases for anonymization context"""
    
    def setUp(self):
        self.sample_stix_object = {
            'type': 'indicator',
            'id': 'indicator--test',
            'name': 'Test Indicator',
            'pattern': "[ipv4-addr:value = '192.168.1.100']"
        }
    
    def test_context_strategy_setting(self):
        """Test setting anonymization strategy"""
        context = AnonymizationContext()
        strategy = NoAnonymizationStrategy()
        
        context.set_strategy(strategy)
        result = context.anonymize_data(self.sample_stix_object, trust_level=1.0)
        
        self.assertEqual(result, self.sample_stix_object)
    
    def test_context_trust_level_strategy_selection(self):
        """Test automatic strategy selection based on trust level"""
        context = AnonymizationContext()
        
        # High trust level should use no anonymization
        result = context.anonymize_data(self.sample_stix_object, trust_level=0.9)
        self.assertEqual(result['name'], self.sample_stix_object['name'])
        
        # Medium trust level should use partial anonymization
        result = context.anonymize_data(self.sample_stix_object, trust_level=0.6)
        self.assertNotEqual(result['name'], self.sample_stix_object['name'])
        
        # Low trust level should use full anonymization
        result = context.anonymize_data(self.sample_stix_object, trust_level=0.2)
        self.assertNotEqual(result['name'], self.sample_stix_object['name'])
    
    def test_context_effectiveness_score(self):
        """Test getting effectiveness score"""
        context = AnonymizationContext()
        context.set_strategy(NoAnonymizationStrategy())
        
        score = context.get_effectiveness_score()
        self.assertEqual(score, 1.0)


class TestAnonymizationStrategyFactory(TestCase):
    """Test cases for anonymization strategy factory"""
    
    def test_get_strategy_by_name(self):
        """Test getting strategy by name"""
        strategy = AnonymizationStrategyFactory.get_strategy('none')
        self.assertIsInstance(strategy, NoAnonymizationStrategy)
        
        strategy = AnonymizationStrategyFactory.get_strategy('partial')
        self.assertIsInstance(strategy, PartialAnonymizationStrategy)
        
        strategy = AnonymizationStrategyFactory.get_strategy('full')
        self.assertIsInstance(strategy, FullAnonymizationStrategy)
        
        strategy = AnonymizationStrategyFactory.get_strategy('domain')
        self.assertIsInstance(strategy, DomainAnonymizationStrategy)
        
        strategy = AnonymizationStrategyFactory.get_strategy('ip')
        self.assertIsInstance(strategy, IPAddressAnonymizationStrategy)
        
        strategy = AnonymizationStrategyFactory.get_strategy('email')
        self.assertIsInstance(strategy, EmailAnonymizationStrategy)
    
    def test_get_strategy_case_insensitive(self):
        """Test case-insensitive strategy retrieval"""
        strategy = AnonymizationStrategyFactory.get_strategy('NONE')
        self.assertIsInstance(strategy, NoAnonymizationStrategy)
        
        strategy = AnonymizationStrategyFactory.get_strategy('Partial')
        self.assertIsInstance(strategy, PartialAnonymizationStrategy)
    
    def test_get_unknown_strategy(self):
        """Test getting unknown strategy falls back to default"""
        strategy = AnonymizationStrategyFactory.get_strategy('unknown')
        self.assertIsInstance(strategy, PartialAnonymizationStrategy)
    
    def test_get_default_strategy(self):
        """Test getting default strategy"""
        strategy = AnonymizationStrategyFactory.get_default_strategy()
        self.assertIsInstance(strategy, PartialAnonymizationStrategy)
    
    def test_register_custom_strategy(self):
        """Test registering custom strategy"""
        class CustomStrategy(AnonymizationStrategy):
            def anonymize(self, stix_input, trust_level=0.5, strategy_level='custom'):
                stix_dict = self._get_stix_dict(stix_input)
                result = stix_dict.copy()
                result['x_custom_field'] = 'anonymized'
                return result
            
            def get_effectiveness_score(self):
                return 0.75
        
        AnonymizationStrategyFactory.register_strategy('custom', CustomStrategy)
        
        strategy = AnonymizationStrategyFactory.get_strategy('custom')
        self.assertIsInstance(strategy, CustomStrategy)
        
        # Test the custom strategy
        stix_obj = {'type': 'indicator', 'id': 'test'}
        result = strategy.anonymize(stix_obj)
        self.assertEqual(result['x_custom_field'], 'anonymized')
    
    def test_register_invalid_strategy(self):
        """Test registering invalid strategy class"""
        class InvalidStrategy:
            pass
        
        with self.assertRaises(ValueError):
            AnonymizationStrategyFactory.register_strategy('invalid', InvalidStrategy)
    
    def test_get_strategy_for_trust_level(self):
        """Test getting strategy based on trust level"""
        # High trust level
        strategy = AnonymizationStrategyFactory.get_strategy_for_trust_level(0.9)
        self.assertIsInstance(strategy, NoAnonymizationStrategy)
        
        # Medium trust level
        strategy = AnonymizationStrategyFactory.get_strategy_for_trust_level(0.6)
        self.assertIsInstance(strategy, PartialAnonymizationStrategy)
        
        # Low trust level
        strategy = AnonymizationStrategyFactory.get_strategy_for_trust_level(0.2)
        self.assertIsInstance(strategy, FullAnonymizationStrategy)


class TestAnonymizationFieldHandlers(TestCase):
    """Test cases for sensitive field handlers"""
    
    def test_name_field_handler(self):
        """Test name field anonymization"""
        strategy = PartialAnonymizationStrategy()
        
        original_name = "Suspicious File"
        anonymized = strategy._anonymize_field_value('name', original_name, 'indicator', 'partial')
        
        self.assertNotEqual(anonymized, original_name)
        self.assertIn('Redacted Name', anonymized)
    
    def test_pattern_field_handler(self):
        """Test pattern field anonymization"""
        strategy = PartialAnonymizationStrategy()
        
        original_pattern = "[ipv4-addr:value = '192.168.1.100']"
        anonymized = strategy._anonymize_field_value('pattern', original_pattern, 'indicator', 'partial')
        
        self.assertNotEqual(anonymized, original_pattern)
        self.assertNotIn('192.168.1.100', anonymized)
    
    def test_contact_information_handler(self):
        """Test contact information anonymization"""
        strategy = PartialAnonymizationStrategy()
        
        original_contact = "John Doe, john@example.com, +1-555-0123"
        anonymized = strategy._anonymize_field_value('contact_information', original_contact, 'identity', 'partial')
        
        self.assertEqual(anonymized, '[CONTACT_INFO_REDACTED]')
    
    def test_aliases_field_handler(self):
        """Test aliases field anonymization"""
        strategy = PartialAnonymizationStrategy()
        
        original_aliases = ['BadActor', 'EvilGroup', 'Threat123']
        anonymized = strategy._anonymize_field_value('aliases', original_aliases, 'threat-actor', 'partial')
        
        self.assertIsInstance(anonymized, list)
        self.assertEqual(len(anonymized), len(original_aliases))
        self.assertTrue(all(alias.startswith('Alias-') for alias in anonymized))