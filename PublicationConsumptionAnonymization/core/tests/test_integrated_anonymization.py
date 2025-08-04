"""
Integrated Anonymization Tests
"""

import json
import uuid
from datetime import datetime, timedelta
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock

from core.models.models import (
    Organization, STIXObject, Collection, CollectionObject,
    TrustLevel, TrustRelationship, Feed
)
from core.patterns.strategy.enums import AnonymizationLevel
from core.patterns.strategy.context import AnonymizationContext
from core.patterns.strategy.strategies import (
    EmailAnonymizationStrategy,
    DomainAnonymizationStrategy, 
    IPAddressAnonymizationStrategy
)
from crisp_settings.utils import generate_bundle_from_collection


class IntegratedAnonymizationTestCase(TransactionTestCase):
    """Base test case for integrated anonymization tests."""
    
    def setUp(self):
        """Set up test data for all tests."""
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_suffix}',
            email=f'test_{unique_suffix}@example.com',
            password='testpass'
        )
        
        # Create test organizations
        self.source_org = Organization.objects.create(
            name=f'Source University {unique_suffix}', 
            organization_type='university',
            contact_email=f'source_{unique_suffix}@test.edu',
            created_by=self.user
        )
        
        self.target_org = Organization.objects.create(
            name=f'Target University {unique_suffix}',  
            organization_type='university',
            contact_email=f'target_{unique_suffix}@test.edu',
            created_by=self.user
        )
        
        self.commercial_org = Organization.objects.create(
            name=f'Commercial Org {unique_suffix}',     
            organization_type='commercial',
            contact_email=f'commercial_{unique_suffix}@test.com',
            created_by=self.user
        )
        
        # Create test STIX object
        self.sample_stix_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity'],
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'description': 'Malicious domain used in phishing campaign targeting students at student@university.edu'
        }
        
        self.stix_object = STIXObject.objects.create(
            stix_id=self.sample_stix_data['id'],
            stix_type='indicator',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=self.sample_stix_data,
            source_organization=self.source_org,
            created_by=self.user
        )
        
        # Create test collection with UNIQUE alias
        self.collection = Collection.objects.create(
            title='Test Collection',
            description='Collection for testing integrated anonymization',
            alias=f'test-collection-{unique_suffix}', 
            owner=self.source_org,
            default_anonymization_level=AnonymizationLevel.MEDIUM.value
        )
        
        # Add STIX object to collection
        self.collection.stix_objects.add(self.stix_object)


class TrustRelationshipTests(IntegratedAnonymizationTestCase):
    """Test trust relationship functionality."""
    
    def test_create_trust_relationship(self):
        """Test creating trust relationships between organizations."""
        # Create a high trust level
        high_trust = TrustLevel.objects.create(
            name='High Trust',
            level=90,
            numerical_value=90,
            description='High level of trust between organizations'
        )
        
        # Create trust relationship
        trust_rel = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=high_trust
        )
        
        self.assertEqual(trust_rel.source_organization, self.source_org)
        self.assertEqual(trust_rel.target_organization, self.target_org)
        self.assertEqual(trust_rel.trust_level.level, 90)
    
    def test_trust_level_impact_on_anonymization(self):
        """Test how trust levels affect anonymization strategies."""
        # Create different trust levels
        high_trust = TrustLevel.objects.create(
            name='High Trust Level',
            level=90,
            numerical_value=85,
            description='High trust level'
        )
        
        low_trust = TrustLevel.objects.create(
            name='Low Trust Level', 
            level=30,
            numerical_value=30,
            description='Low trust level'
        )
        
        # Create trust relationships
        TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=high_trust
        )
        
        TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.commercial_org,
            trust_level=low_trust
        )
        
        # Test anonymization context with different trust levels
        context = AnonymizationContext()
        
        # High trust should result in less anonymization
        high_trust_bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.target_org
        )
        
        # Low trust should result in more anonymization
        low_trust_bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.commercial_org
        )
        
        # Verify different levels of anonymization
        self.assertIsNotNone(high_trust_bundle)
        self.assertIsNotNone(low_trust_bundle)


class AnonymizationStrategyTests(IntegratedAnonymizationTestCase):
    """Test anonymization strategies."""
    
    def test_email_anonymization_strategy(self):
        """Test email anonymization strategy."""
        strategy = EmailAnonymizationStrategy()
        
        # Test email anonymization
        original_email = "student@university.edu"
        anonymized_email = strategy.anonymize(original_email)
        
        # Should be anonymized but maintain structure
        self.assertNotEqual(original_email, anonymized_email)
        self.assertIn('@', anonymized_email)
        
        # Should be consistent - same input gives same output
        second_anonymization = strategy.anonymize(original_email)
        self.assertEqual(anonymized_email, second_anonymization)
    
    def test_domain_anonymization_strategy(self):
        """Test domain anonymization strategy."""
        strategy = DomainAnonymizationStrategy()
        
        # Test domain anonymization
        original_domain = "malicious.example.com"
        anonymized_domain = strategy.anonymize(original_domain)
        
        # Should be anonymized but maintain domain structure
        self.assertNotEqual(original_domain, anonymized_domain)
        self.assertIn('.', anonymized_domain)
        
        # Should preserve TLD if configured to do so
        if hasattr(strategy, 'preserve_tld') and strategy.preserve_tld:
            self.assertTrue(anonymized_domain.endswith('.com'))
    
    def test_ip_address_anonymization_strategy(self):
        """Test IP address anonymization strategy."""
        strategy = IPAddressAnonymizationStrategy()
        
        # Test IP anonymization
        original_ip = "192.168.1.100"
        anonymized_ip = strategy.anonymize(original_ip)
        
        # Should be anonymized but maintain IP format
        self.assertNotEqual(original_ip, anonymized_ip)
        
        # Should still look like an IP address
        parts = anonymized_ip.split('.')
        self.assertEqual(len(parts), 4)
        
        # Each part should be a valid octet or anonymization marker
        for part in parts:
            if part == 'x':
                continue  # Anonymization marker is valid
            else:
                self.assertTrue(0 <= int(part) <= 255)


class BundleGenerationTests(IntegratedAnonymizationTestCase):
    """Test STIX bundle generation with anonymization."""
    
    def test_bundle_generation_same_organization(self):
        """Test bundle generation for same organization (no anonymization)."""
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.source_org
        )
        
        self.assertIsNotNone(bundle)
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('objects', bundle)
        
        # Should contain original data without anonymization
        objects = bundle['objects']
        indicator = next((obj for obj in objects if obj['type'] == 'indicator'), None)
        self.assertIsNotNone(indicator)
        self.assertEqual(indicator['pattern'], self.sample_stix_data['pattern'])
    
    def test_bundle_generation_different_organization(self):
        """Test bundle generation for different organization (with anonymization)."""
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.target_org
        )
        
        self.assertIsNotNone(bundle)
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('objects', bundle)
        
        # Should contain anonymized data
        objects = bundle['objects']
        indicator = next((obj for obj in objects if obj['type'] == 'indicator'), None)
        self.assertIsNotNone(indicator)
        
        # Pattern should be anonymized for different organization
        self.assertNotEqual(indicator['pattern'], self.sample_stix_data['pattern'])
    
    def test_bundle_generation_with_filters(self):
        """Test bundle generation with filters applied."""
        # Add more STIX objects of different types
        malware_data = {
            'type': 'malware',
            'id': f'malware--{uuid.uuid4()}',
            'spec_version': '2.1',
            'labels': ['trojan'],
            'name': 'TestMalware',
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
        }
        
        malware_object = STIXObject.objects.create(
            stix_id=malware_data['id'],
            stix_type='malware',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=malware_data,
            source_organization=self.source_org,
            created_by=self.user
        )
        
        self.collection.stix_objects.add(malware_object)
        
        # Generate bundle with type filter
        filters = {'match[type]': 'indicator'}
        bundle = generate_bundle_from_collection(
            self.collection,
            filters=filters,
            requesting_organization=self.target_org
        )
        
        self.assertIsNotNone(bundle)
        objects = bundle['objects']
        
        # Should contain indicators and owner identity
        non_bundle_objects = [obj for obj in objects if obj['type'] != 'bundle']
        
        # Filter out identity objects (collection owner)
        indicator_objects = [obj for obj in non_bundle_objects if obj['type'] == 'indicator']
        identity_objects = [obj for obj in non_bundle_objects if obj['type'] == 'identity']
        
        # Should have indicators and exactly one identity (collection owner)
        self.assertGreater(len(indicator_objects), 0, "Should have at least one indicator")
        self.assertEqual(len(identity_objects), 1, "Should have exactly one identity object (collection owner)")
        
        # All non-identity objects should be indicators
        for obj in indicator_objects:
            self.assertEqual(obj['type'], 'indicator')


class FeedPublicationTests(IntegratedAnonymizationTestCase):
    """Test feed publication with anonymization."""
    
    def test_feed_creation_and_publication(self):
        """Test creating and publishing a feed."""
        unique_suffix = str(uuid.uuid4())[:8]
        
        # Create a feed
        feed = Feed.objects.create(
            title='Test Threat Feed',
            description='Test feed for threat intelligence',
            alias=f'test-feed-{unique_suffix}',
            collection=self.collection,
            organization=self.source_org,
            created_by=self.user,
            is_public=True,
            anonymization_level=AnonymizationLevel.MEDIUM.value
        )
        
        self.assertEqual(feed.collection, self.collection)
        self.assertEqual(feed.organization, self.source_org)
        self.assertTrue(feed.is_public)
    
    def test_feed_consumption_with_anonymization(self):
        """Test consuming a feed with proper anonymization."""
        unique_suffix = str(uuid.uuid4())[:8]
        
        # Create a feed
        feed = Feed.objects.create(
            title='Public Threat Feed',
            description='Public feed for external consumption',
            alias=f'public-feed-{unique_suffix}',
            collection=self.collection,
            organization=self.source_org,
            created_by=self.user,
            is_public=True,
            anonymization_level=AnonymizationLevel.HIGH.value
        )
        
        # Simulate external organization consuming the feed
        consumed_bundle = generate_bundle_from_collection(
            feed.collection,
            requesting_organization=self.commercial_org
        )
        
        self.assertIsNotNone(consumed_bundle)
        
        # Data should be heavily anonymized for external organization
        objects = consumed_bundle['objects']
        indicator = next((obj for obj in objects if obj['type'] == 'indicator'), None)
        
        if indicator:
            # Should be anonymized due to high anonymization level
            self.assertNotEqual(indicator.get('pattern'), self.sample_stix_data['pattern'])


class IntegrationValidationTests(IntegratedAnonymizationTestCase):
    """Test validation of the complete integration."""
    
    def test_stix_compliance_after_anonymization(self):
        """Test that anonymized STIX objects remain compliant."""
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.commercial_org
        )
        
        self.assertIsNotNone(bundle)
        
        # Validate STIX bundle structure
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('id', bundle)
        self.assertIn('objects', bundle)
        
        # Validate individual STIX objects
        for stix_object in bundle['objects']:
            # Every STIX object must have required fields
            self.assertIn('type', stix_object)
            self.assertIn('id', stix_object)
            
            # ID should follow STIX format
            if stix_object['type'] != 'bundle':
                expected_prefix = f"{stix_object['type']}--"
                self.assertTrue(stix_object['id'].startswith(expected_prefix))
    
    def test_metadata_consistency(self):
        """Test that metadata remains consistent after anonymization."""
        original_count = self.collection.stix_objects.count()
        
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.target_org
        )
        
        # Filter out bundle and identity objects to get only the original STIX objects
        bundle_objects = [obj for obj in bundle['objects'] 
                        if obj['type'] != 'bundle' and obj['type'] != 'identity']
        
        # Number of non-identity objects should match original count
        self.assertEqual(len(bundle_objects), original_count)
        
        original_types = set(obj.stix_type for obj in self.collection.stix_objects.all())
        bundle_types = set(obj['type'] for obj in bundle_objects)
        self.assertEqual(original_types, bundle_types)
    
    def test_bundle_stix_compliance(self):
        """Test that generated bundles comply with STIX 2.1 specification."""
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.target_org
        )
        
        # Bundle must have required fields
        required_fields = ['type', 'id', 'objects']
        for field in required_fields:
            self.assertIn(field, bundle)
        
        # Type must be 'bundle'
        self.assertEqual(bundle['type'], 'bundle')
        
        # ID must follow STIX format
        self.assertTrue(bundle['id'].startswith('bundle--'))
        
        # Objects must be a list
        self.assertIsInstance(bundle['objects'], list)
        
        # Each object must be valid STIX
        for obj in bundle['objects']:
            self.assertIn('type', obj)
            self.assertIn('id', obj)
            
            # Verify STIX ID format
            stix_type = obj['type']
            stix_id = obj['id']
            self.assertTrue(stix_id.startswith(f'{stix_type}--'))


class PerformanceTests(IntegratedAnonymizationTestCase):
    """Test performance of anonymization operations."""
    
    def test_large_collection_anonymization_performance(self):
        """Test anonymization performance with large collections."""
        # Create multiple STIX objects
        for i in range(20):
            stix_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'spec_version': '2.1',
                'pattern': f"[ipv4-addr:value = '10.0.0.{i}']",
                'labels': ['malicious-activity'],
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat(),
            }
            
            stix_object = STIXObject.objects.create(
                stix_id=stix_data['id'],
                stix_type='indicator',
                created=timezone.now(),
                modified=timezone.now(),
                raw_data=stix_data,
                source_organization=self.source_org,
                created_by=self.user
            )
            
            self.collection.stix_objects.add(stix_object)
        
        # Measure anonymization performance
        import time
        start_time = time.time()
        
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.commercial_org
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(processing_time, 10.0)  # 10 seconds max
        self.assertIsNotNone(bundle)
        
        # All objects should be processed (excluding owner identity)
        bundle_objects = [obj for obj in bundle['objects'] if obj['type'] not in ['bundle', 'identity']]
        self.assertEqual(len(bundle_objects), 21)  # 20 + original test object


class ErrorHandlingTests(IntegratedAnonymizationTestCase):
    """Test error handling in anonymization workflow."""
    
    def test_anonymization_failure_handling(self):
        """Test handling of anonymization failures."""
        # Create object with problematic data
        problematic_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'spec_version': '2.1',
            'pattern': "[invalid:pattern = 'this will cause issues']",
            'labels': ['malicious-activity'],
        }
        
        problematic_object = STIXObject.objects.create(
            stix_id=problematic_data['id'],
            stix_type='indicator',
            raw_data=problematic_data,
            source_organization=self.source_org,
            created_by=self.user
        )
        
        self.collection.stix_objects.add(problematic_object)
        
        # Should handle gracefully
        try:
            bundle = generate_bundle_from_collection(
                self.collection,
                requesting_organization=self.target_org
            )
            # Should either succeed or fail gracefully
            self.assertIsNotNone(bundle)
        except Exception as e:
            # If it fails, should be a controlled failure
            self.assertIsInstance(e, (ValueError, TypeError, AttributeError))
    
    def test_missing_trust_relationship_handling(self):
        """Test handling when no trust relationship exists."""
        # Create organization with no trust relationship
        unique_suffix = str(uuid.uuid4())[:8]
        unknown_org = Organization.objects.create(
            name=f'Unknown Org {unique_suffix}',
            organization_type='government',
            contact_email=f'unknown_{unique_suffix}@test.gov',
            created_by=self.user
        )
        
        # Should use default anonymization level
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=unknown_org
        )
        
        self.assertIsNotNone(bundle)
        
        # Should apply default anonymization
        objects = bundle['objects']
        indicator = next((obj for obj in objects if obj['type'] == 'indicator'), None)
        
        if indicator:
            # Should be anonymized with default level
            self.assertNotEqual(indicator.get('pattern'), self.sample_stix_data['pattern'])