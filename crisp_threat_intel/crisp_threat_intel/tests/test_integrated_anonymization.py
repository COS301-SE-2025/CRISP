"""
Test suite for integrated anonymization system.
Tests the integration between crisp_threat_intel and crisp_anonymization.
"""

import unittest
import json
import uuid
from datetime import datetime, timezone as dt_timezone
from django.test import TestCase
from django.contrib.auth.models import User

from crisp_threat_intel.models import Organization, STIXObject, Collection, TrustRelationship
from crisp_threat_intel.strategies.integrated_anonymization import (
    IntegratedAnonymizationContext,
    IntegratedDomainAnonymizationStrategy,
    IntegratedIPAnonymizationStrategy,
    IntegratedEmailAnonymizationStrategy,
    TrustLevel
)


class IntegratedAnonymizationTestCase(TestCase):
    """Test case for integrated anonymization functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user('testuser1', 'test1@example.com', 'password')
        self.user2 = User.objects.create_user('testuser2', 'test2@example.com', 'password')
        
        # Create test organizations
        self.org1 = Organization.objects.create(
            name="University A",
            description="Test University A",
            contact_email="admin@univa.edu",
            created_by=self.user1
        )
        
        self.org2 = Organization.objects.create(
            name="University B", 
            description="Test University B",
            contact_email="admin@univb.edu",
            created_by=self.user2
        )
        
        # Create trust relationship (medium trust)
        self.trust_rel = TrustRelationship.objects.create(
            source_organization=self.org1,
            target_organization=self.org2,
            trust_level=0.5,
            created_by=self.user1
        )
        
        # Create test STIX objects
        self.stix_domain_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--12345678-1234-1234-1234-123456789012",
            "created": "2021-01-01T00:00:00.000Z",
            "modified": "2021-01-01T00:00:00.000Z",
            "name": "Malicious Domain",
            "description": "Suspicious domain observed in attacks",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[domain-name:value = 'malicious.example.com']",
            "valid_from": "2021-01-01T00:00:00.000Z"
        }
        
        self.stix_ip_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--87654321-4321-4321-4321-210987654321",
            "created": "2021-01-01T00:00:00.000Z",
            "modified": "2021-01-01T00:00:00.000Z",
            "name": "Malicious IP",
            "description": "Suspicious IP address",
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": "[ipv4-addr:value = '192.168.1.100']",
            "valid_from": "2021-01-01T00:00:00.000Z"
        }
        
        # Create STIXObject instances
        self.domain_obj = STIXObject.objects.create(
            stix_id=self.stix_domain_indicator["id"],
            stix_type="indicator",
            created=datetime.now(dt_timezone.utc),
            modified=datetime.now(dt_timezone.utc),
            raw_data=self.stix_domain_indicator,
            source_organization=self.org1,
            created_by=self.user1
        )
        
        self.ip_obj = STIXObject.objects.create(
            stix_id=self.stix_ip_indicator["id"],
            stix_type="indicator",
            created=datetime.now(dt_timezone.utc),
            modified=datetime.now(dt_timezone.utc),
            raw_data=self.stix_ip_indicator,
            source_organization=self.org1,
            created_by=self.user1
        )
    
    def test_integrated_context_initialization(self):
        """Test that integrated context initializes properly"""
        context = IntegratedAnonymizationContext()
        
        # Check that strategies are available
        self.assertIn('domain', context.strategies)
        self.assertIn('ip', context.strategies)
        self.assertIn('email', context.strategies)
        self.assertIn('url', context.strategies)
        
        # Check strategy types
        self.assertIsInstance(context.strategies['domain'], IntegratedDomainAnonymizationStrategy)
        self.assertIsInstance(context.strategies['ip'], IntegratedIPAnonymizationStrategy)
        self.assertIsInstance(context.strategies['email'], IntegratedEmailAnonymizationStrategy)
    
    def test_trust_level_conversion(self):
        """Test trust level to anonymization level conversion"""
        from crisp_anonymization.enums import AnonymizationLevel
        
        # High trust -> No anonymization
        self.assertEqual(
            TrustLevel.to_anonymization_level(0.9),
            AnonymizationLevel.NONE
        )
        
        # Medium trust -> Low anonymization
        self.assertEqual(
            TrustLevel.to_anonymization_level(0.6),
            AnonymizationLevel.LOW
        )
        
        # Low trust -> Medium anonymization
        self.assertEqual(
            TrustLevel.to_anonymization_level(0.3),
            AnonymizationLevel.MEDIUM
        )
        
        # No trust -> Full anonymization
        self.assertEqual(
            TrustLevel.to_anonymization_level(0.1),
            AnonymizationLevel.FULL
        )
    
    def test_stix_domain_anonymization(self):
        """Test STIX domain indicator anonymization"""
        context = IntegratedAnonymizationContext()
        
        # Test different trust levels
        trust_levels = [0.9, 0.6, 0.3, 0.1]
        
        for trust_level in trust_levels:
            anonymized = context.anonymize_stix_object(self.stix_domain_indicator, trust_level)
            
            # Check that object structure is preserved
            self.assertEqual(anonymized['type'], 'indicator')
            self.assertEqual(anonymized['spec_version'], '2.1')
            self.assertEqual(anonymized['id'], self.stix_domain_indicator['id'])
            
            # Check anonymization metadata
            self.assertTrue(anonymized.get('x_crisp_anonymized', False))
            self.assertEqual(anonymized.get('x_crisp_trust_level'), trust_level)
            
            # Check pattern anonymization based on trust level
            if trust_level >= 0.8:
                # High trust - no anonymization
                self.assertEqual(
                    anonymized['pattern'],
                    "[domain-name:value = 'malicious.example.com']"
                )
            else:
                # Some level of anonymization applied
                self.assertNotEqual(
                    anonymized['pattern'],
                    "[domain-name:value = 'malicious.example.com']"
                )
                self.assertIn('domain-name:value', anonymized['pattern'])
    
    def test_stix_ip_anonymization(self):
        """Test STIX IP indicator anonymization"""
        context = IntegratedAnonymizationContext()
        
        # Test medium trust anonymization
        anonymized = context.anonymize_stix_object(self.stix_ip_indicator, 0.5)
        
        # Check that object structure is preserved
        self.assertEqual(anonymized['type'], 'indicator')
        self.assertEqual(anonymized['id'], self.stix_ip_indicator['id'])
        
        # Check anonymization metadata
        self.assertTrue(anonymized.get('x_crisp_anonymized', False))
        self.assertEqual(anonymized.get('x_crisp_trust_level'), 0.5)
        
        # Pattern should be anonymized but still contain ipv4-addr
        self.assertNotEqual(
            anonymized['pattern'],
            "[ipv4-addr:value = '192.168.1.100']"
        )
        self.assertIn('ipv4-addr:value', anonymized['pattern'])
    
    def test_raw_data_anonymization(self):
        """Test raw data anonymization using integrated strategies"""
        from crisp_anonymization.enums import DataType, AnonymizationLevel
        
        context = IntegratedAnonymizationContext()
        
        # Test domain anonymization
        domain = "malicious.example.com"
        anon_domain = context.anonymize_raw_data(domain, DataType.DOMAIN, AnonymizationLevel.MEDIUM)
        self.assertNotEqual(anon_domain, domain)
        self.assertIn('example.com', anon_domain)  # Should preserve TLD at medium level
        
        # Test IP anonymization
        ip = "192.168.1.100"
        anon_ip = context.anonymize_raw_data(ip, DataType.IP_ADDRESS, AnonymizationLevel.LOW)
        self.assertNotEqual(anon_ip, ip)
        self.assertTrue(anon_ip.startswith("192.168.1."))  # Should preserve subnet at low level
    
    def test_mixed_data_anonymization(self):
        """Test mixed data anonymization (auto-detection)"""
        context = IntegratedAnonymizationContext()
        
        # Test with STIX object
        stix_result = context.anonymize_mixed(self.stix_domain_indicator, trust_level=0.5)
        self.assertIsInstance(stix_result, dict)
        self.assertEqual(stix_result['type'], 'indicator')
        self.assertTrue(stix_result.get('x_crisp_anonymized', False))
        
        # Test with raw domain string
        domain_result = context.anonymize_mixed("evil.example.com", trust_level=0.5)
        self.assertIsInstance(domain_result, str)
        self.assertNotEqual(domain_result, "evil.example.com")
        
        # Test with list of mixed data
        mixed_list = [self.stix_domain_indicator, "192.168.1.1"]
        result_list = context.anonymize_mixed(mixed_list, trust_level=0.5)
        self.assertIsInstance(result_list, list)
        self.assertEqual(len(result_list), 2)
        self.assertIsInstance(result_list[0], dict)  # STIX object
        self.assertIsInstance(result_list[1], str)   # Anonymized IP
    
    def test_stix_bundle_anonymization(self):
        """Test STIX bundle anonymization"""
        context = IntegratedAnonymizationContext()
        
        # Create test bundle
        bundle = {
            'type': 'bundle',
            'id': f'bundle--{uuid.uuid4()}',
            'objects': [self.stix_domain_indicator, self.stix_ip_indicator]
        }
        
        # Anonymize bundle
        anonymized_bundle = context.anonymize_stix_bundle(bundle, 0.5)
        
        # Check bundle structure
        self.assertEqual(anonymized_bundle['type'], 'bundle')
        self.assertTrue(anonymized_bundle.get('x_crisp_anonymized', False))
        self.assertEqual(anonymized_bundle.get('x_crisp_trust_level'), 0.5)
        
        # Check that all objects are anonymized
        self.assertEqual(len(anonymized_bundle['objects']), 2)
        for obj in anonymized_bundle['objects']:
            self.assertTrue(obj.get('x_crisp_anonymized', False))
    
    def test_trust_relationship_integration(self):
        """Test trust relationship model integration"""
        # Test getting trust level between organizations
        trust_level = TrustRelationship.get_trust_level(self.org1, self.org2)
        self.assertEqual(trust_level, 0.5)
        
        # Test default trust level for non-existent relationship
        org3 = Organization.objects.create(
            name="University C",
            contact_email="admin@univc.edu"
        )
        default_trust = TrustRelationship.get_trust_level(self.org1, org3)
        self.assertEqual(default_trust, 0.3)  # Default low trust
    
    def test_collection_bundle_generation(self):
        """Test collection bundle generation with anonymization"""
        # Create collection
        collection = Collection.objects.create(
            title="Test Collection",
            description="Test collection for anonymization",
            alias="test-collection",
            owner=self.org1
        )
        
        # Add STIX objects to collection
        collection.stix_objects.add(self.domain_obj, self.ip_obj)
        
        # Generate bundle for same organization (no anonymization)
        bundle_owner = collection.generate_bundle(self.org1)
        self.assertEqual(len(bundle_owner['objects']), 2)
        self.assertEqual(bundle_owner['x_crisp_trust_level'], 1.0)
        
        # Generate bundle for different organization (with anonymization)
        bundle_other = collection.generate_bundle(self.org2)
        self.assertEqual(len(bundle_other['objects']), 2)
        self.assertEqual(bundle_other['x_crisp_trust_level'], 0.5)
        
        # Check that objects in the "other" bundle are anonymized
        for obj in bundle_other['objects']:
            if 'x_crisp_anonymized' in obj:
                self.assertTrue(obj['x_crisp_anonymized'])
    
    def test_stix_object_apply_anonymization(self):
        """Test STIXObject.apply_anonymization method"""
        # Apply anonymization to domain object
        anonymized_obj = self.domain_obj.apply_anonymization(0.5)
        
        # Check that a new object was created
        self.assertNotEqual(anonymized_obj.id, self.domain_obj.id)
        self.assertTrue(anonymized_obj.anonymized)
        self.assertEqual(anonymized_obj.anonymization_strategy, 'integrated')
        self.assertEqual(anonymized_obj.original_object_ref, self.domain_obj.stix_id)
        
        # Check that raw data was anonymized
        self.assertNotEqual(anonymized_obj.raw_data, self.domain_obj.raw_data)
        self.assertTrue(anonymized_obj.raw_data.get('x_crisp_anonymized', False))
    
    def test_strategy_selection(self):
        """Test automatic strategy selection based on STIX content"""
        context = IntegratedAnonymizationContext()
        
        # Test domain strategy selection
        domain_strategy = context._select_stix_strategy(self.stix_domain_indicator, 0.5)
        self.assertEqual(domain_strategy, context.strategies['domain'])
        
        # Test IP strategy selection
        ip_strategy = context._select_stix_strategy(self.stix_ip_indicator, 0.5)
        self.assertEqual(ip_strategy, context.strategies['ip'])
        
        # Test non-indicator object (should return None)
        identity_obj = {
            "type": "identity",
            "spec_version": "2.1",
            "id": "identity--12345678-1234-1234-1234-123456789012",
            "name": "Test Identity"
        }
        identity_strategy = context._select_stix_strategy(identity_obj, 0.5)
        self.assertIsNone(identity_strategy)
    
    def test_anonymization_statistics(self):
        """Test anonymization statistics method"""
        context = IntegratedAnonymizationContext()
        stats = context.get_anonymization_statistics()
        
        # Check expected statistics structure
        self.assertIn('available_strategies', stats)
        self.assertIn('trust_level_mapping', stats)
        self.assertIn('supported_stix_types', stats)
        self.assertIn('supported_data_types', stats)
        
        # Check strategy availability
        self.assertIn('domain', stats['available_strategies'])
        self.assertIn('ip', stats['available_strategies'])
        self.assertIn('email', stats['available_strategies'])
        self.assertIn('url', stats['available_strategies'])


class IntegratedAnonymizationPerformanceTestCase(TestCase):
    """Performance tests for integrated anonymization"""
    
    def setUp(self):
        """Set up performance test data"""
        self.user = User.objects.create_user('perfuser', 'perf@example.com', 'password')
        self.org = Organization.objects.create(
            name="Performance Test Org",
            contact_email="perf@example.com",
            created_by=self.user
        )
        
        # Create multiple STIX objects for performance testing
        self.stix_objects = []
        for i in range(100):
            stix_obj = {
                "type": "indicator",
                "spec_version": "2.1",
                "id": f"indicator--{uuid.uuid4()}",
                "created": "2021-01-01T00:00:00.000Z",
                "modified": "2021-01-01T00:00:00.000Z",
                "name": f"Test Indicator {i}",
                "indicator_types": ["malicious-activity"],
                "pattern_type": "stix",
                "pattern": f"[domain-name:value = 'malicious{i}.example.com']",
                "valid_from": "2021-01-01T00:00:00.000Z"
            }
            self.stix_objects.append(stix_obj)
    
    def test_bulk_anonymization_performance(self):
        """Test performance of bulk anonymization"""
        context = IntegratedAnonymizationContext()
        
        import time
        start_time = time.time()
        
        # Anonymize all objects
        anonymized_objects = []
        for obj in self.stix_objects:
            anonymized = context.anonymize_stix_object(obj, 0.5)
            anonymized_objects.append(anonymized)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertion (should complete within reasonable time)
        self.assertLess(duration, 5.0, "Bulk anonymization took too long")
        self.assertEqual(len(anonymized_objects), 100)
        
        # Check that all objects were anonymized
        for obj in anonymized_objects:
            self.assertTrue(obj.get('x_crisp_anonymized', False))


if __name__ == '__main__':
    unittest.main()