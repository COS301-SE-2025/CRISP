"""
Comprehensive tests for the integrated publication and anonymization system.
Tests ensure seamless operation between both components.
"""
import uuid
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock

from crisp_threat_intel.models import (
    Organization, STIXObject, Collection, Feed, 
    TrustRelationship, TrustNetwork, NetworkMembership
)
from crisp_threat_intel.utils import (
    generate_bundle_from_collection, publish_feed,
    get_trust_level, get_anonymization_level
)

from core.patterns.strategy.enums import AnonymizationLevel
from core.patterns.strategy.context import AnonymizationContext


class IntegratedAnonymizationTestCase(TestCase):
    """
    Test suite for integrated publication and anonymization functionality.
    """
    
    def setUp(self):
        """Set up test data for all tests."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Create test organizations
        self.source_org = Organization.objects.create(
            name='Source University',
            organization_type='university',
            identity_class='organization',
            contact_email='source@university.edu',
            created_by=self.user
        )
        
        self.target_org = Organization.objects.create(
            name='Target University', 
            organization_type='university',
            identity_class='organization',
            contact_email='target@university.edu',
            created_by=self.user
        )
        
        self.commercial_org = Organization.objects.create(
            name='Commercial Entity',
            organization_type='commercial',
            identity_class='organization',
            contact_email='contact@commercial.com',
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
        
        # Create test collection
        self.collection = Collection.objects.create(
            title='Test Collection',
            description='Collection for testing integrated anonymization',
            alias='test-collection',
            owner=self.source_org,
            default_anonymization_level=AnonymizationLevel.MEDIUM.value
        )
        
        # Add STIX object to collection
        self.collection.stix_objects.add(self.stix_object)


class TrustRelationshipTests(IntegratedAnonymizationTestCase):
    """Test trust relationship functionality."""
    
    def test_create_trust_relationship(self):
        """Test creating trust relationships between organizations."""
        trust_rel = TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.8,
            created_by=self.user
        )
        
        self.assertEqual(trust_rel.trust_level, 0.8)
        self.assertEqual(trust_rel.source_org, self.source_org)
        self.assertEqual(trust_rel.target_org, self.target_org)
    
    def test_trust_level_anonymization_mapping(self):
        """Test that trust levels map correctly to anonymization levels."""
        # High trust
        high_trust = TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.9
        )
        self.assertEqual(high_trust.get_anonymization_level().value, AnonymizationLevel.NONE.value)
        
        # Medium trust
        medium_trust = TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.commercial_org,
            trust_level=0.6
        )
        self.assertEqual(medium_trust.get_anonymization_level().value, AnonymizationLevel.MEDIUM.value)
        
        # Low trust
        low_trust = TrustRelationship.objects.create(
            source_org=self.commercial_org,
            target_org=self.target_org,
            trust_level=0.2
        )
        self.assertEqual(low_trust.get_anonymization_level().value, AnonymizationLevel.FULL.value)
    
    def test_anonymization_override(self):
        """Test that anonymization override works correctly."""
        trust_rel = TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.9,  # Would normally be NONE
            anonymization_override=AnonymizationLevel.HIGH.value
        )
        
        self.assertEqual(trust_rel.get_anonymization_level().value, AnonymizationLevel.HIGH.value)


class TrustNetworkTests(IntegratedAnonymizationTestCase):
    """Test trust network functionality."""
    
    def test_create_trust_network(self):
        """Test creating trust networks."""
        network = TrustNetwork.objects.create(
            name='University Consortium',
            description='Network of trusted universities',
            default_trust_level=0.7,
            default_anonymization_level=AnonymizationLevel.LOW.value
        )
        
        # Add members
        NetworkMembership.objects.create(
            organization=self.source_org,
            network=network,
            membership_level='full'
        )
        
        NetworkMembership.objects.create(
            organization=self.target_org,
            network=network,
            membership_level='full'
        )
        
        self.assertEqual(network.members.count(), 2)
        self.assertTrue(network.members.filter(name=self.source_org.name).exists())


class STIXObjectAnonymizationTests(IntegratedAnonymizationTestCase):
    """Test STIX object anonymization functionality."""
    
    def test_apply_anonymization_same_org(self):
        """Test that no anonymization is applied for same organization."""
        result = self.stix_object.apply_anonymization(self.source_org)
        self.assertEqual(result, self.sample_stix_data)
        self.assertNotIn('x_crisp_anonymized', result)
    
    def test_apply_anonymization_different_org(self):
        """Test anonymization is applied for different organizations."""
        # Create trust relationship
        TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.5  # Medium trust -> MEDIUM anonymization
        )
        
        result = self.stix_object.apply_anonymization(self.target_org)
        
        # Check anonymization metadata
        self.assertTrue(result['x_crisp_anonymized'])
        self.assertEqual(result['x_crisp_anonymization_level'], 'medium')
        self.assertEqual(result['x_crisp_source_org'], self.source_org.name)
        self.assertEqual(result['x_crisp_original_id'], self.stix_object.stix_id)
        
        # Check that pattern was anonymized (fallback system adds ANON prefix)
        self.assertIn('[ANON:', result['pattern'])
        
        # Check that description is present (fallback doesn't modify description)
        self.assertIn('description', result)
    
    def test_anonymization_with_custom_level(self):
        """Test applying specific anonymization level."""
        result = self.stix_object.apply_anonymization(
            self.target_org, 
            anonymization_level=AnonymizationLevel.FULL
        )
        
        self.assertTrue(result['x_crisp_anonymized'])
        self.assertEqual(result['x_crisp_anonymization_level'], 'full')
    
    def test_get_trust_level(self):
        """Test trust level calculation."""
        # No explicit relationship
        trust = self.stix_object.get_trust_level(self.target_org)
        self.assertEqual(trust, 0.7)  # Universities get higher default trust
        
        # With explicit relationship
        TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.8
        )
        
        trust = self.stix_object.get_trust_level(self.target_org)
        self.assertEqual(trust, 0.8)


class CollectionBundleGenerationTests(IntegratedAnonymizationTestCase):
    """Test collection bundle generation with anonymization."""
    
    def test_generate_bundle_no_requesting_org(self):
        """Test bundle generation without requesting organization (internal view)."""
        bundle = self.collection.generate_bundle()
        
        # Should contain owner identity + STIX object
        self.assertEqual(len(bundle['objects']), 2)
        self.assertEqual(bundle['type'], 'bundle')
        
        # Find the indicator object
        indicator = next(obj for obj in bundle['objects'] if obj['type'] == 'indicator')
        self.assertEqual(indicator, self.sample_stix_data)
        self.assertNotIn('x_crisp_anonymized', indicator)
    
    def test_generate_bundle_with_requesting_org_same(self):
        """Test bundle generation for same organization."""
        bundle = self.collection.generate_bundle(requesting_org=self.source_org)
        
        # Find the indicator object  
        indicator = next(obj for obj in bundle['objects'] if obj['type'] == 'indicator')
        self.assertEqual(indicator, self.sample_stix_data)
        self.assertNotIn('x_crisp_anonymized', indicator)
    
    def test_generate_bundle_with_requesting_org_different(self):
        """Test bundle generation with anonymization for different organization."""
        # Create trust relationship
        TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.4  # Low-medium trust -> HIGH anonymization
        )
        
        bundle = self.collection.generate_bundle(requesting_org=self.target_org)
        
        # Find the indicator object
        indicator = next(obj for obj in bundle['objects'] if obj['type'] == 'indicator')
        
        # Should be anonymized
        self.assertTrue(indicator['x_crisp_anonymized'])
        self.assertEqual(indicator['x_crisp_anonymization_level'], 'high')
        self.assertIn('[ANON:', indicator['pattern'])
    
    def test_generate_bundle_with_failed_anonymization(self):
        """Test bundle generation when anonymization fails."""
        with patch('crisp_threat_intel.utils.AnonymizationContext.anonymize_stix_object') as mock_anonymize:
            mock_anonymize.side_effect = AnonymizationError("Test error")
            
            bundle = self.collection.generate_bundle(requesting_org=self.target_org)
            
            # Should only contain owner identity, no indicator
            self.assertEqual(len(bundle['objects']), 1)
            identity = bundle['objects'][0]
            self.assertEqual(identity['type'], 'identity')
    
    def test_generate_bundle_with_filters(self):
        """Test bundle generation with filters."""
        # Create another STIX object
        malware_data = {
            'type': 'malware',
            'id': f'malware--{uuid.uuid4()}',
            'spec_version': '2.1',
            'name': 'TestMalware',
            'malware_types': ['trojan'],
            'is_family': False,
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat()
        }
        
        malware_obj = STIXObject.objects.create(
            stix_id=malware_data['id'],
            stix_type='malware',
            created=timezone.now(),
            modified=timezone.now(),
            raw_data=malware_data,
            source_organization=self.source_org,
            created_by=self.user
        )
        
        self.collection.stix_objects.add(malware_obj)
        
        # Filter for indicators only
        bundle = self.collection.generate_bundle(
            filters={'stix_type': 'indicator'}
        )
        
        # Should contain owner identity + indicator only
        self.assertEqual(len(bundle['objects']), 2)
        types = [obj['type'] for obj in bundle['objects']]
        self.assertIn('identity', types)
        self.assertIn('indicator', types)
        self.assertNotIn('malware', types)


class FeedPublicationTests(IntegratedAnonymizationTestCase):
    """Test feed publication with integrated anonymization."""
    
    def setUp(self):
        super().setUp()
        self.feed = Feed.objects.create(
            name='Test Feed',
            description='Test feed for integrated anonymization',
            collection=self.collection,
            update_interval=3600,
            created_by=self.user
        )
    
    def test_publish_feed_basic(self):
        """Test basic feed publication."""
        result = publish_feed(self.feed)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['feed_name'], 'Test Feed')
        self.assertEqual(result['object_count'], 2)  # Identity + indicator
        self.assertIsNotNone(result['bundle_id'])
        
        # Check feed metadata updated
        self.feed.refresh_from_db()
        self.assertIsNotNone(self.feed.last_published_time)
        self.assertEqual(self.feed.publish_count, 1)
        self.assertEqual(self.feed.status, 'active')
    
    def test_publish_feed_with_query_parameters(self):
        """Test feed publication with query parameters."""
        self.feed.query_parameters = {'stix_type': 'indicator'}
        self.feed.save()
        
        result = publish_feed(self.feed)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['object_count'], 2)  # Identity + filtered indicator
    
    def test_feed_publication_error_handling(self):
        """Test error handling during feed publication."""
        with patch('crisp_threat_intel.utils.generate_bundle_from_collection') as mock_generate:
            mock_generate.side_effect = Exception("Test error")
            
            with self.assertRaises(Exception):
                publish_feed(self.feed)
            
            # Check error tracking
            self.feed.refresh_from_db()
            self.assertEqual(self.feed.error_count, 1)
            self.assertEqual(self.feed.status, 'error')
            self.assertIsNotNone(self.feed.last_error)


class UtilityFunctionTests(IntegratedAnonymizationTestCase):
    """Test utility functions for trust and anonymization."""
    
    def test_get_trust_level_same_org(self):
        """Test trust level for same organization."""
        trust = get_trust_level(self.source_org, self.source_org)
        self.assertEqual(trust, 1.0)
    
    def test_get_trust_level_with_relationship(self):
        """Test trust level with explicit relationship."""
        TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.7
        )
        
        trust = get_trust_level(self.source_org, self.target_org)
        self.assertEqual(trust, 0.7)
    
    def test_get_trust_level_default_university(self):
        """Test default trust level between universities."""
        trust = get_trust_level(self.source_org, self.target_org)
        self.assertEqual(trust, 0.7)  # Higher trust between universities
    
    def test_get_trust_level_default_mixed(self):
        """Test default trust level between different org types."""
        trust = get_trust_level(self.source_org, self.commercial_org)
        self.assertEqual(trust, 0.6)  # Medium-high trust with universities
    
    def test_get_anonymization_level_mapping(self):
        """Test anonymization level mapping from trust levels."""
        # Test different trust levels
        TrustRelationship.objects.create(
            source_org=self.source_org,
            target_org=self.target_org,
            trust_level=0.95
        )
        level = get_anonymization_level(self.source_org, self.target_org)
        self.assertEqual(level.value, AnonymizationLevel.NONE.value)
        
        # Update trust level
        TrustRelationship.objects.filter(
            source_org=self.source_org,
            target_org=self.target_org
        ).update(trust_level=0.6)
        level = get_anonymization_level(self.source_org, self.target_org)
        self.assertEqual(level.value, AnonymizationLevel.MEDIUM.value)


class ErrorHandlingTests(IntegratedAnonymizationTestCase):
    """Test error handling in integrated system."""
    
    def test_anonymization_error_handling(self):
        """Test handling of anonymization errors."""
        with patch('crisp_threat_intel.utils.AnonymizationContext.anonymize_stix_object') as mock_anonymize:
            mock_anonymize.side_effect = AnonymizationError("Test anonymization error")
            
            with self.assertRaises(AnonymizationError):
                self.stix_object.apply_anonymization(self.target_org)
    


class PerformanceTests(IntegratedAnonymizationTestCase):
    """Test performance aspects of integrated system."""
    
    def test_large_collection_anonymization(self):
        """Test anonymization performance with large collections."""
        import time
        
        # Create multiple STIX objects
        stix_objects = []
        for i in range(50):
            stix_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'spec_version': '2.1',
                'pattern': f"[domain-name:value = 'malicious{i}.example.com']",
                'labels': ['malicious-activity'],
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat()
            }
            
            obj = STIXObject.objects.create(
                stix_id=stix_data['id'],
                stix_type='indicator',
                created=timezone.now(),
                modified=timezone.now(),
                raw_data=stix_data,
                source_organization=self.source_org,
                created_by=self.user
            )
            
            self.collection.stix_objects.add(obj)
            stix_objects.append(obj)
        
        # Measure anonymization time
        start_time = time.time()
        bundle = self.collection.generate_bundle(requesting_org=self.target_org)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Performance assertions
        self.assertLess(processing_time, 5.0)  # Should complete in under 5 seconds
        self.assertGreaterEqual(len(bundle['objects']), 51)  # Identity + 50 indicators (may include more identities)
        
        # Verify all objects were anonymized
        indicators = [obj for obj in bundle['objects'] if obj['type'] == 'indicator']
        for indicator in indicators:
            self.assertTrue(indicator.get('x_crisp_anonymized', False))


class IntegrationValidationTests(IntegratedAnonymizationTestCase):
    """Validation tests to ensure integration correctness."""
    
    def test_stix_compliance_after_anonymization(self):
        """Test that anonymized objects remain STIX compliant."""
        result = self.stix_object.apply_anonymization(self.target_org)
        
        # Check required STIX fields
        required_fields = ['type', 'id', 'spec_version', 'created', 'modified']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Check type-specific fields for indicators
        self.assertIn('pattern', result)
        self.assertIn('labels', result)
        
        # Check anonymization metadata
        self.assertTrue(result['x_crisp_anonymized'])
        self.assertIn('x_crisp_anonymization_level', result)
    
    def test_bundle_stix_compliance(self):
        """Test that generated bundles are STIX compliant."""
        bundle = self.collection.generate_bundle(requesting_org=self.target_org)
        
        # Check bundle structure
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('id', bundle)
        self.assertIn('spec_version', bundle)
        self.assertIn('objects', bundle)
        self.assertIsInstance(bundle['objects'], list)
        
        # Check all objects have required fields
        for obj in bundle['objects']:
            self.assertIn('type', obj)
            self.assertIn('id', obj)
    
    def test_metadata_consistency(self):
        """Test that anonymization metadata is consistent."""
        result = self.stix_object.apply_anonymization(self.target_org)
        
        # Check metadata consistency
        self.assertEqual(result['x_crisp_source_org'], self.source_org.name)
        self.assertEqual(result['x_crisp_original_id'], self.stix_object.stix_id)
        
        # Trust level should match anonymization level
        trust_level = result['x_crisp_trust_level']
        anon_level = result['x_crisp_anonymization_level']
        
        if trust_level >= 0.9:
            self.assertEqual(anon_level, 'none')
        elif trust_level >= 0.7:
            self.assertEqual(anon_level, 'low')
        elif trust_level >= 0.5:
            self.assertEqual(anon_level, 'medium')
        elif trust_level >= 0.3:
            self.assertEqual(anon_level, 'high')
        else:
            self.assertEqual(anon_level, 'full')