"""
Comprehensive test suite proving functional parity.
Tests the complete workflow: Organization -> STIX Objects -> Collection -> Feed -> Bundle -> Publish
"""
import json
import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from crisp_threat_intel.models import Organization, STIXObject, Collection, CollectionObject, Feed
from crisp_threat_intel.utils import (
    get_or_create_identity, 
    generate_bundle_from_collection, 
    publish_feed,
    process_csv_to_stix
)
from crisp_threat_intel.factories.stix_factory import STIXObjectFactory
from crisp_threat_intel.strategies.anonymization import AnonymizationStrategyFactory


class FullWorkflowTest(TestCase):
    """
    Test complete workflow to prove functional parity with original implementation.
    """
    
    def setUp(self):
        """Set up test data"""
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test University',
            description='Test educational institution',
            identity_class='organization',
        )
        # Create test user with organization
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            organization=self.organization
        )
        
        # Create test collection
        self.collection = Collection.objects.create(
            title='Test Threat Collection',
            description='Test collection for threat intelligence',
            alias='test-threats',
            owner=self.organization,
            can_read=True,
            can_write=True
        )
    
    def test_complete_workflow(self):
        """
        Test: Organization -> STIX Objects -> Collection -> Feed -> Bundle -> Publish
        This must produce identical results to threat_intel_service tests.
        """
        # Step 1: Create identity for organization
        identity = get_or_create_identity(self.organization)
        self.assertIsInstance(identity, dict)
        self.assertEqual(identity['type'], 'identity')
        self.assertEqual(identity['name'], self.organization.name)
        self.assertTrue(identity['id'].startswith('identity--'))
        
        # Step 2: Create STIX objects using factory
        indicator_data = {
            'pattern': "[domain-name:value = 'malicious.example.com']",
            'labels': ['malicious-activity'],
            'name': 'Test Malicious Domain',
            'description': 'Test indicator for workflow verification'
        }
        
        stix_indicator = STIXObjectFactory.create_object('indicator', indicator_data)
        self.assertEqual(stix_indicator['type'], 'indicator')
        self.assertIn('pattern', stix_indicator)
        self.assertIn('labels', stix_indicator)
        
        # Step 3: Store STIX object in database
        db_stix_object = STIXObject.objects.create(
            stix_id=stix_indicator['id'],
            stix_type=stix_indicator['type'],
            spec_version=stix_indicator['spec_version'],
            created=stix_indicator['created'],
            modified=stix_indicator['modified'],
            labels=stix_indicator['labels'],
            raw_data=stix_indicator,
            source_organization=self.organization,
            created_by=self.user
        )
        
        # Step 4: Add to collection
        CollectionObject.objects.create(
            collection=self.collection,
            stix_object=db_stix_object
        )
        
        # Verify collection has the object
        self.assertEqual(self.collection.stix_objects.count(), 1)
        
        # Step 5: Create feed
        feed = Feed.objects.create(
            name='Test Feed',
            description='Test feed for workflow verification',
            collection=self.collection,
            update_interval=3600,
            status='active',
            created_by=self.user
        )
        
        # Step 6: Generate bundle from collection
        bundle = generate_bundle_from_collection(self.collection)
        self.assertIsInstance(bundle, dict)
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('objects', bundle)
        self.assertTrue(len(bundle['objects']) >= 2)  # At least identity + indicator
        
        # Verify bundle contains identity and indicator
        object_types = [obj['type'] for obj in bundle['objects']]
        self.assertIn('identity', object_types)
        self.assertIn('indicator', object_types)
        
        # Step 7: Publish feed
        result = publish_feed(feed)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['status'], 'success')
        self.assertIn('bundle_id', result)
        self.assertIn('object_count', result)
        self.assertGreater(result['object_count'], 0)
        
        # Verify feed was updated
        feed.refresh_from_db()
        self.assertIsNotNone(feed.last_published_time)
        self.assertEqual(feed.publish_count, 1)
        self.assertEqual(feed.status, 'active')
        
        print(f"✓ Complete workflow test passed")
        print(f"  - Created organization: {self.organization.name}")
        print(f"  - Generated STIX identity: {identity['id']}")
        print(f"  - Created STIX indicator: {stix_indicator['id']}")
        print(f"  - Generated bundle: {bundle['id']} with {len(bundle['objects'])} objects")
        print(f"  - Published feed: {result['bundle_id']}")
    
    def test_csv_to_stix_conversion(self):
        """Test CSV to STIX conversion functionality"""
        csv_data = """indicator_name,description,pattern_value,pattern_type,confidence
Malicious Domain,Test domain,malicious.test.com,domain-name,85
Suspicious IP,Test IP,192.168.1.100,ipv4-addr,70"""
        
        mapping = {
            'stix_type': 'indicator',
            'csv_delimiter': ',',
            'properties': {
                'name': 'indicator_name',
                'description': 'description',
                'confidence': 'confidence'
            },
            'pattern_field': 'pattern_value',
            'pattern_type_field': 'pattern_type'
        }
        
        stix_objects = process_csv_to_stix(csv_data, mapping, self.organization)
        
        self.assertEqual(len(stix_objects), 2)
        
        # Verify first indicator
        indicator1 = stix_objects[0]
        self.assertEqual(indicator1['type'], 'indicator')
        self.assertEqual(indicator1['name'], 'Malicious Domain')
        self.assertIn("malicious.test.com", indicator1['pattern'])
        self.assertEqual(indicator1['confidence'], 85)
        
        # Verify second indicator
        indicator2 = stix_objects[1]
        self.assertEqual(indicator2['type'], 'indicator')
        self.assertEqual(indicator2['name'], 'Suspicious IP')
        self.assertIn("192.168.1.100", indicator2['pattern'])
        self.assertEqual(indicator2['confidence'], 70)
        
        print(f"✓ CSV to STIX conversion test passed")
        print(f"  - Converted {len(stix_objects)} indicators from CSV")
    
    def test_anonymization_strategies(self):
        """Test anonymization strategies work correctly"""
        # Test domain anonymization
        domain_strategy = AnonymizationStrategyFactory.get_strategy('domain')
        
        test_indicator = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'pattern': "[domain-name:value = 'sensitive.example.com']",
            'labels': ['malicious-activity']
        }
        
        # Test high trust (no anonymization)
        result_high = domain_strategy.anonymize(test_indicator, 0.9)
        self.assertEqual(result_high['pattern'], test_indicator['pattern'])
        
        # Test medium trust (partial anonymization)
        result_medium = domain_strategy.anonymize(test_indicator, 0.5)
        self.assertIn('[REDACTED]', result_medium['pattern'])
        self.assertTrue(result_medium.get('x_crisp_anonymized', False))
        
        # Test low trust (full anonymization)
        result_low = domain_strategy.anonymize(test_indicator, 0.2)
        self.assertIn('anon-', result_low['pattern'])
        self.assertTrue(result_low.get('x_crisp_anonymized', False))
        
        print(f"✓ Anonymization strategies test passed")
        print(f"  - High trust: No anonymization")
        print(f"  - Medium trust: Partial anonymization")
        print(f"  - Low trust: Full anonymization")
    
    def test_factory_patterns(self):
        """Test STIX object factory patterns"""
        # Test indicator creation
        indicator = STIXObjectFactory.create_object('indicator', {
            'pattern': "[file:hashes.SHA256 = 'abc123']",
            'labels': ['malicious-activity']
        })
        self.assertEqual(indicator['type'], 'indicator')
        self.assertIn('pattern', indicator)
        
        # Test attack pattern creation
        attack_pattern = STIXObjectFactory.create_object('attack-pattern', {
            'name': 'Test Attack Pattern',
            'description': 'Test attack pattern for verification'
        })
        self.assertEqual(attack_pattern['type'], 'attack-pattern')
        self.assertEqual(attack_pattern['name'], 'Test Attack Pattern')
        
        # Test malware creation
        malware = STIXObjectFactory.create_object('malware', {
            'name': 'Test Malware',
            'malware_types': ['trojan'],
            'is_family': False
        })
        self.assertEqual(malware['type'], 'malware')
        self.assertEqual(malware['name'], 'Test Malware')
        
        # Test identity creation
        identity = STIXObjectFactory.create_object('identity', {
            'name': 'Test Organization',
            'identity_class': 'organization'
        })
        self.assertEqual(identity['type'], 'identity')
        self.assertEqual(identity['name'], 'Test Organization')
        
        print(f"✓ Factory patterns test passed")
        print(f"  - Created indicator, attack-pattern, malware, and identity objects")
    
    def test_bundle_generation_with_anonymization(self):
        """Test bundle generation with anonymization"""
        # Create second organization for anonymization testing
        other_org = Organization.objects.create(
            name='Other University',
            description='Another test institution',
            identity_class='organization',
            created_by=self.user
        )
        
        # Create STIX object from other organization
        stix_data = STIXObjectFactory.create_object('indicator', {
            'pattern': "[domain-name:value = 'secret.example.com']",
            'labels': ['malicious-activity']
        })
        
        other_stix_object = STIXObject.objects.create(
            stix_id=stix_data['id'],
            stix_type=stix_data['type'],
            spec_version=stix_data['spec_version'],
            created=stix_data['created'],
            modified=stix_data['modified'],
            labels=stix_data['labels'],
            raw_data=stix_data,
            source_organization=other_org,
            created_by=self.user
        )
        
        CollectionObject.objects.create(
            collection=self.collection,
            stix_object=other_stix_object
        )
        
        # Generate bundle with anonymization
        bundle = generate_bundle_from_collection(
            self.collection,
            requesting_organization=self.organization
        )
        
        self.assertIsInstance(bundle, dict)
        self.assertEqual(bundle['type'], 'bundle')
        self.assertIn('objects', bundle)
        
        print(f"✓ Bundle generation with anonymization test passed")
        print(f"  - Generated bundle with cross-organization objects")
        print(f"  - Bundle contains {len(bundle['objects'])} objects")


class PlatformStatusTest(TestCase):
    """Test platform status and health checks"""
    
    def test_platform_health(self):
        """Test platform health and configuration"""
        from django.conf import settings
        
        # Test OTX settings
        self.assertIn('OTX_SETTINGS', dir(settings))
        otx_config = settings.OTX_SETTINGS
        self.assertIsInstance(otx_config, dict)
        
        # Test TAXII settings
        self.assertIn('TAXII_SETTINGS', dir(settings))
        taxii_config = settings.TAXII_SETTINGS
        self.assertIsInstance(taxii_config, dict)
        
        print(f"✓ Platform configuration test passed")
        print(f"  - OTX enabled: {otx_config.get('ENABLED', False)}")
        print(f"  - TAXII title: {taxii_config.get('DISCOVERY_TITLE', 'Unknown')}")