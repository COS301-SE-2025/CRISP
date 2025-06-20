"""
Comprehensive test suite for CRISP Threat Intelligence Platform

This test suite covers all major functionality including:
- Domain models and relationships
- CRISP design pattern implementations
- TAXII API functionality
- Security and anonymization
- OTX integration
- Audit logging
"""

import json
import uuid
import pytest
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock

from ..domain.models import (
    Institution, User, ThreatFeed, Indicator, TTPData,
    TrustRelationship, Collection, STIXObject, AuditLog,
    FeedSubscription, TrustGroup, TrustGroupMembership
)
from ..services.taxii_service import TAXIIService, TAXIIServiceError
from ..services.threat_feed_service import ThreatFeedService
from ..services.otx_service import OTXService
from ..strategies.anonymization_strategy import (
    AnonymizationContext, DomainAnonymizationStrategy,
    IPAddressAnonymizationStrategy, EmailAnonymizationStrategy
)
from ..factories.stix_object_creator import (
    STIXIndicatorCreator, STIXTTPCreator
)
from ..config.security import SecurityConfig
from ..observers.feed_observers import InstitutionObserver, AlertSystemObserver


class CRISPTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data"""
        # Create Django users
        self.django_user1 = DjangoUser.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        
        self.django_user2 = DjangoUser.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create institutions
        self.institution1 = Institution.objects.create(
            name='Test University',
            description='Test educational institution',
            sectors=['education'],
            contact_email='security@testuni.edu',
            trust_score=0.8
        )
        
        self.institution2 = Institution.objects.create(
            name='Security Corp',
            description='Security consulting company',
            sectors=['technology'],
            contact_email='info@securitycorp.com',
            trust_score=0.9
        )
        
        # Create CRISP users
        self.user1 = User.objects.create(
            django_user=self.django_user1,
            institution=self.institution1,
            role='admin'
        )
        
        self.user2 = User.objects.create(
            django_user=self.django_user2,
            institution=self.institution2,
            role='analyst'
        )
        
        # Create trust relationship
        self.trust_rel = TrustRelationship.objects.create(
            source_institution=self.institution1,
            target_institution=self.institution2,
            trust_level=0.7,
            established_by=self.user1
        )


class DomainModelsTestCase(CRISPTestCase):
    """Test domain model functionality"""
    
    def test_institution_creation(self):
        """Test institution model creation and methods"""
        self.assertEqual(self.institution1.name, 'Test University')
        self.assertTrue(self.institution1.stix_id.startswith('identity--'))
        self.assertEqual(self.institution1.trust_score, 0.8)
        
        # Test STIX conversion
        stix_data = self.institution1.to_stix()
        self.assertEqual(stix_data['type'], 'identity')
        self.assertEqual(stix_data['name'], 'Test University')
        self.assertEqual(stix_data['identity_class'], 'organization')
    
    def test_trust_relationships(self):
        """Test trust relationship functionality"""
        trust_level = self.institution1.get_trust_level_for(self.institution2)
        self.assertEqual(trust_level, 0.7)
        
        # Test reverse trust (should be 0.0 by default)
        reverse_trust = self.institution2.get_trust_level_for(self.institution1)
        self.assertEqual(reverse_trust, 0.0)
    
    def test_threat_feed_creation(self):
        """Test threat feed creation and observer pattern"""
        feed = ThreatFeed.objects.create(
            name='Test Feed',
            description='Test threat feed',
            institution=self.institution1,
            created_by=self.user1,
            update_interval=3600
        )
        
        self.assertEqual(feed.name, 'Test Feed')
        self.assertEqual(feed.status, 'active')
        
        # Test observer pattern
        observer = Mock()
        feed.add_observer(observer)
        
        # Test notification
        feed.notify_observers('test_event', {'data': 'test'})
        observer.update.assert_called_once()
    
    def test_indicator_creation(self):
        """Test indicator model creation and STIX conversion"""
        feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution1,
            created_by=self.user1
        )
        
        indicator = Indicator.objects.create(
            name='Malicious Domain',
            pattern="[domain-name:value = 'evil.com']",
            labels=['malicious-activity'],
            valid_from=timezone.now(),
            confidence=85,
            threat_feed=feed,
            created_by=self.user1
        )
        
        self.assertTrue(indicator.stix_id.startswith('indicator--'))
        self.assertEqual(indicator.confidence, 85)
        
        # Test STIX conversion
        stix_data = indicator.to_stix()
        self.assertEqual(stix_data['type'], 'indicator')
        self.assertEqual(stix_data['pattern'], "[domain-name:value = 'evil.com']")
        self.assertEqual(stix_data['confidence'], 85)
    
    def test_api_quota_management(self):
        """Test API quota functionality"""
        self.assertTrue(self.institution1.can_make_api_request())
        
        # Use up quota
        self.institution1.api_quota_daily = 2
        self.institution1.save()
        
        self.institution1.record_api_request()
        self.assertTrue(self.institution1.can_make_api_request())
        
        self.institution1.record_api_request()
        self.assertFalse(self.institution1.can_make_api_request())


class TAXIIServiceTestCase(CRISPTestCase):
    """Test TAXII service functionality"""
    
    def setUp(self):
        super().setUp()
        self.taxii_service = TAXIIService()
        
        # Create test collection
        self.collection = Collection.objects.create(
            title='Test Collection',
            description='Test TAXII collection',
            institution=self.institution1,
            can_read=True,
            can_write=True,
            created_by=self.user1
        )
        
        # Create test STIX object
        self.stix_data = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'pattern': "[domain-name:value = 'malicious.com']",
            'labels': ['malicious-activity'],
            'confidence': 90
        }
        
        self.stix_object = STIXObject.objects.create(
            stix_id=self.stix_data['id'],
            stix_type='indicator',
            raw_data=self.stix_data,
            institution=self.institution1,
            collection=self.collection,
            created_by=self.user1
        )
    
    def test_discovery_information(self):
        """Test TAXII discovery endpoint"""
        discovery = self.taxii_service.get_discovery_information(self.institution1)
        
        self.assertIn('title', discovery)
        self.assertIn('api_roots', discovery)
        self.assertEqual(len(discovery['api_roots']), 1)
    
    def test_collections_endpoint(self):
        """Test TAXII collections endpoint"""
        collections = self.taxii_service.get_collections(self.institution1, self.user1)
        
        self.assertIn('collections', collections)
        self.assertEqual(len(collections['collections']), 1)
        
        collection_data = collections['collections'][0]
        self.assertEqual(collection_data['title'], 'Test Collection')
        self.assertTrue(collection_data['can_read'])
        self.assertTrue(collection_data['can_write'])
    
    def test_objects_endpoint_with_anonymization(self):
        """Test TAXII objects endpoint with trust-based anonymization"""
        # Test with high trust (should get minimal anonymization)
        self.trust_rel.trust_level = 0.9
        self.trust_rel.save()
        
        objects_response = self.taxii_service.get_objects(
            self.collection.collection_id,
            self.institution2,
            request_user=self.user2
        )
        
        self.assertIn('objects', objects_response)
        self.assertEqual(len(objects_response['objects']), 1)
        
        # Object should be minimally anonymized due to high trust
        obj = objects_response['objects'][0]
        self.assertEqual(obj['type'], 'indicator')
        self.assertIn('pattern', obj)
    
    def test_objects_endpoint_low_trust(self):
        """Test objects endpoint with low trust anonymization"""
        # Set low trust level
        self.trust_rel.trust_level = 0.1
        self.trust_rel.save()
        
        objects_response = self.taxii_service.get_objects(
            self.collection.collection_id,
            self.institution2,
            request_user=self.user2
        )
        
        # Object should be heavily anonymized due to low trust
        obj = objects_response['objects'][0]
        self.assertEqual(obj['type'], 'indicator')
        # Pattern should be anonymized
        self.assertNotEqual(obj.get('pattern', ''), self.stix_data['pattern'])
    
    def test_add_objects(self):
        """Test adding objects to collection"""
        new_stix_object = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'created': timezone.now().isoformat(),
            'modified': timezone.now().isoformat(),
            'pattern': "[ipv4-addr:value = '192.168.1.1']",
            'labels': ['suspicious-activity'],
            'confidence': 75
        }
        
        response = self.taxii_service.add_objects(
            self.collection.collection_id,
            [new_stix_object],
            self.institution1,
            self.user1
        )
        
        self.assertEqual(response['status'], 'complete')
        self.assertEqual(response['success_count'], 1)
        self.assertEqual(response['failure_count'], 0)
        
        # Verify object was created
        created_obj = STIXObject.objects.get(stix_id=new_stix_object['id'])
        self.assertEqual(created_obj.stix_type, 'indicator')
    
    def test_manifest_endpoint(self):
        """Test TAXII manifest endpoint"""
        manifest = self.taxii_service.get_manifest(
            self.collection.collection_id,
            self.institution1,
            request_user=self.user1
        )
        
        self.assertIn('objects', manifest)
        self.assertEqual(len(manifest['objects']), 1)
        
        manifest_entry = manifest['objects'][0]
        self.assertEqual(manifest_entry['id'], self.stix_object.stix_id)
        self.assertIn('date_added', manifest_entry)
        self.assertIn('version', manifest_entry)


class AnonymizationTestCase(CRISPTestCase):
    """Test anonymization strategy pattern"""
    
    def setUp(self):
        super().setUp()
        self.context = AnonymizationContext()
    
    def test_domain_anonymization(self):
        """Test domain anonymization strategy"""
        strategy = DomainAnonymizationStrategy()
        
        # Test full anonymization
        original_domain = 'malicious.example.com'
        anonymized = strategy.anonymize(original_domain, 'full', self.institution1)
        
        self.assertNotEqual(anonymized, original_domain)
        self.assertTrue(anonymized.endswith('.com'))  # Should preserve TLD
    
    def test_ip_anonymization(self):
        """Test IP address anonymization strategy"""
        strategy = IPAddressAnonymizationStrategy()
        
        # Test partial anonymization
        original_ip = '192.168.1.100'
        anonymized = strategy.anonymize(original_ip, 'partial', self.institution1)
        
        self.assertNotEqual(anonymized, original_ip)
        self.assertTrue(anonymized.startswith('192.168'))  # Should preserve network
    
    def test_email_anonymization(self):
        """Test email anonymization strategy"""
        strategy = EmailAnonymizationStrategy()
        
        # Test partial anonymization
        original_email = 'attacker@malicious.com'
        anonymized = strategy.anonymize(original_email, 'partial', self.institution1)
        
        self.assertNotEqual(anonymized, original_email)
        self.assertIn('@', anonymized)  # Should still be valid email format
    
    def test_anonymization_context(self):
        """Test anonymization context with STIX objects"""
        stix_object = {
            'type': 'indicator',
            'id': f'indicator--{uuid.uuid4()}',
            'pattern': "[domain-name:value = 'evil.com' OR ipv4-addr:value = '192.168.1.1']",
            'labels': ['malicious-activity']
        }
        
        # Test partial anonymization
        anonymized = self.context.anonymize_stix_object(
            stix_object, 
            'partial', 
            self.institution1
        )
        
        self.assertEqual(anonymized['type'], 'indicator')
        self.assertNotEqual(anonymized['pattern'], stix_object['pattern'])
        self.assertIn('domain-name:value', anonymized['pattern'])  # Structure preserved


class FactoryPatternTestCase(CRISPTestCase):
    """Test factory pattern implementation"""
    
    def test_stix_indicator_creator(self):
        """Test STIX indicator creation using factory pattern"""
        feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution1,
            created_by=self.user1
        )
        
        indicator = Indicator.objects.create(
            name='Test Indicator',
            pattern="[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            labels=['malicious-activity'],
            valid_from=timezone.now(),
            threat_feed=feed,
            created_by=self.user1
        )
        
        factory = STIXIndicatorCreator()
        stix_object = factory.create_stix_object(indicator)
        
        self.assertEqual(stix_object['type'], 'indicator')
        self.assertEqual(stix_object['name'], 'Test Indicator')
        self.assertIn('pattern', stix_object)
        self.assertIn('labels', stix_object)
    
    def test_stix_ttp_creator(self):
        """Test STIX TTP creation using factory pattern"""
        feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution1,
            created_by=self.user1
        )
        
        ttp = TTPData.objects.create(
            name='Phishing',
            description='Email phishing technique',
            kill_chain_phases=[{
                'kill_chain_name': 'mitre-attack',
                'phase_name': 'initial-access'
            }],
            threat_feed=feed,
            created_by=self.user1
        )
        
        factory = STIXTTPCreator()
        stix_object = factory.create_stix_object(ttp)
        
        self.assertEqual(stix_object['type'], 'attack-pattern')
        self.assertEqual(stix_object['name'], 'Phishing')
        self.assertIn('kill_chain_phases', stix_object)


class ObserverPatternTestCase(CRISPTestCase):
    """Test observer pattern implementation"""
    
    def test_institution_observer(self):
        """Test institution observer functionality"""
        observer = InstitutionObserver(self.institution2)
        
        # Create threat feed and add observer
        feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution1,
            created_by=self.user1
        )
        
        feed.add_observer(observer)
        
        # Mock the notification method
        with patch.object(observer, 'notify_institution') as mock_notify:
            feed.notify_observers('published', {
                'bundle_id': 'test-bundle-123',
                'object_count': 5
            })
            
            mock_notify.assert_called_once()
    
    def test_alert_system_observer(self):
        """Test alert system observer functionality"""
        observer = AlertSystemObserver()
        
        feed = ThreatFeed.objects.create(
            name='Critical Feed',
            institution=self.institution1,
            created_by=self.user1
        )
        
        feed.add_observer(observer)
        
        # Mock the alert creation method
        with patch.object(observer, 'create_alert') as mock_alert:
            feed.notify_observers('published', {
                'bundle_id': 'critical-bundle-456',
                'object_count': 10,
                'criticality': 'high'
            })
            
            mock_alert.assert_called_once()


class SecurityTestCase(CRISPTestCase):
    """Test security configuration and audit logging"""
    
    def test_security_config(self):
        """Test security configuration management"""
        config = SecurityConfig()
        
        # Test default values
        self.assertEqual(config.get('session_timeout_minutes'), 30)
        self.assertEqual(config.get('max_login_attempts'), 5)
        
        # Test secret management
        test_secret = 'test-secret-key'
        config.set_secret('test_key', test_secret)
        retrieved = config.get_secret('test_key')
        
        # Secret should be encrypted when stored
        self.assertNotEqual(config._config.get('test_key'), test_secret)
    
    def test_audit_logging(self):
        """Test comprehensive audit logging"""
        # Log a test action
        AuditLog.log_action(
            user=self.user1,
            institution=self.institution1,
            action='create',
            resource_type='threat_feed',
            resource_id='test-feed-123',
            ip_address='192.168.1.100',
            details={'name': 'Test Feed'},
            success=True
        )
        
        # Verify log entry
        log_entry = AuditLog.objects.first()
        self.assertEqual(log_entry.user, self.user1)
        self.assertEqual(log_entry.action, 'create')
        self.assertEqual(log_entry.resource_type, 'threat_feed')
        self.assertTrue(log_entry.success)
        self.assertEqual(log_entry.details['name'], 'Test Feed')


class OTXIntegrationTestCase(CRISPTestCase):
    """Test OTX integration functionality"""
    
    def setUp(self):
        super().setUp()
        self.otx_service = OTXService()
    
    @patch('crisp_threat_intel.services.otx_service.OTXClient')
    def test_otx_connection(self, mock_client_class):
        """Test OTX connection and configuration"""
        # Mock the OTX client
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.get_user_info.return_value = {'username': 'test_user'}
        mock_client.get_statistics.return_value = {'requests_made': 100}
        mock_client_class.return_value = mock_client
        
        # Test connection
        result = self.otx_service.test_connection()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('user_info', result)
        self.assertIn('client_stats', result)
    
    @patch('crisp_threat_intel.services.otx_service.OTXProcessor')
    def test_otx_feed_creation(self, mock_processor_class):
        """Test OTX feed creation and data processing"""
        # Mock the OTX processor
        mock_processor = Mock()
        mock_processor.fetch_and_process_recent_pulses.return_value = {
            'created_indicators': 5,
            'created_ttps': 2,
            'errors': []
        }
        mock_processor_class.return_value = mock_processor
        
        # Test feed setup and data processing
        result = self.otx_service.fetch_and_process_otx_data(
            self.institution1,
            self.user1,
            days_back=7
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('results', result)
        self.assertEqual(result['results']['created_indicators'], 5)


class ThreatFeedServiceTestCase(CRISPTestCase):
    """Test threat feed service functionality"""
    
    def setUp(self):
        super().setUp()
        self.feed_service = ThreatFeedService()
    
    def test_create_threat_feed(self):
        """Test threat feed creation through service"""
        feed_data = {
            'name': 'Service Test Feed',
            'description': 'Feed created through service layer',
            'query_parameters': {'source': 'manual'},
            'update_interval': 7200
        }
        
        feed = self.feed_service.create_threat_feed(
            institution=self.institution1,
            user=self.user1,
            feed_data=feed_data
        )
        
        self.assertEqual(feed.name, 'Service Test Feed')
        self.assertEqual(feed.update_interval, 7200)
        self.assertEqual(feed.institution, self.institution1)
        self.assertEqual(feed.created_by, self.user1)
    
    def test_publish_feed(self):
        """Test feed publishing functionality"""
        feed = ThreatFeed.objects.create(
            name='Publish Test Feed',
            institution=self.institution1,
            created_by=self.user1
        )
        
        # Add some indicators to the feed
        Indicator.objects.create(
            name='Test Indicator 1',
            pattern="[domain-name:value = 'test1.com']",
            labels=['test'],
            valid_from=timezone.now(),
            threat_feed=feed,
            created_by=self.user1
        )
        
        # Test publishing
        result = self.feed_service.publish_feed(feed, self.user1)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('bundle_id', result)
        self.assertEqual(result['object_count'], 1)
        
        # Verify feed metadata updated
        feed.refresh_from_db()
        self.assertIsNotNone(feed.last_published_time)
        self.assertEqual(feed.publish_count, 1)


class PerformanceTestCase(CRISPTestCase):
    """Test system performance with larger datasets"""
    
    def test_large_collection_query(self):
        """Test querying large collections efficiently"""
        # Create large collection
        collection = Collection.objects.create(
            title='Large Test Collection',
            institution=self.institution1,
            created_by=self.user1
        )
        
        # Create many STIX objects
        objects_to_create = []
        for i in range(100):
            stix_data = {
                'type': 'indicator',
                'id': f'indicator--{uuid.uuid4()}',
                'created': timezone.now().isoformat(),
                'modified': timezone.now().isoformat(),
                'pattern': f"[domain-name:value = 'test{i}.com']",
                'labels': ['test']
            }
            
            objects_to_create.append(STIXObject(
                stix_id=stix_data['id'],
                stix_type='indicator',
                raw_data=stix_data,
                institution=self.institution1,
                collection=collection,
                created_by=self.user1
            ))
        
        STIXObject.objects.bulk_create(objects_to_create)
        
        # Test efficient querying
        taxii_service = TAXIIService()
        
        # Query with pagination
        response = taxii_service.get_objects(
            collection.collection_id,
            self.institution1,
            limit=20
        )
        
        self.assertEqual(len(response['objects']), 20)
        self.assertIn('next', response)  # Should have pagination
    
    def test_trust_calculation_performance(self):
        """Test trust relationship queries are efficient"""
        # Create many trust relationships
        institutions = []
        for i in range(20):
            inst = Institution.objects.create(
                name=f'Institution {i}',
                trust_score=0.5
            )
            institutions.append(inst)
        
        # Create trust relationships
        for i, inst in enumerate(institutions):
            if i < 19:
                TrustRelationship.objects.create(
                    source_institution=inst,
                    target_institution=institutions[i+1],
                    trust_level=0.6,
                    established_by=self.user1
                )
        
        # Test efficient trust lookup
        trust_level = self.institution1.get_trust_level_for(institutions[0])
        self.assertEqual(trust_level, 0.0)  # No relationship exists


class IntegrationTestCase(TransactionTestCase):
    """Test complete system integration scenarios"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Create test data similar to CRISPTestCase but in TransactionTestCase
        self.django_user = DjangoUser.objects.create_user(
            username='integrationuser',
            email='integration@test.com',
            password='testpass123'
        )
        
        self.institution = Institution.objects.create(
            name='Integration Test Org',
            description='Testing integration',
            sectors=['test']
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution,
            role='admin'
        )
    
    def test_end_to_end_threat_feed_workflow(self):
        """Test complete threat feed creation to publication workflow"""
        # 1. Create threat feed service
        feed_service = ThreatFeedService()
        
        # 2. Create threat feed
        feed_data = {
            'name': 'Integration Test Feed',
            'description': 'End-to-end test feed',
            'query_parameters': {'source': 'integration_test'},
            'update_interval': 3600
        }
        
        feed = feed_service.create_threat_feed(
            institution=self.institution,
            user=self.user,
            feed_data=feed_data
        )
        
        # 3. Add indicators to feed
        indicator_data = {
            'name': 'Integration Test Indicator',
            'pattern': "[domain-name:value = 'malicious-integration.com']",
            'labels': ['malicious-activity'],
            'valid_from': timezone.now(),
            'confidence': 85
        }
        
        indicator = Indicator.objects.create(
            threat_feed=feed,
            created_by=self.user,
            **indicator_data
        )
        
        # 4. Create TAXII collection
        taxii_service = TAXIIService()
        collection = taxii_service.create_collection(
            title='Integration Collection',
            description='Collection for integration testing',
            institution=self.institution,
            user=self.user,
            can_read=True,
            can_write=True
        )
        
        # 5. Publish indicator to collection via STIX object
        stix_data = indicator.to_stix()
        
        response = taxii_service.add_objects(
            collection.collection_id,
            [stix_data],
            self.institution,
            self.user
        )
        
        self.assertEqual(response['success_count'], 1)
        
        # 6. Retrieve objects from collection
        objects_response = taxii_service.get_objects(
            collection.collection_id,
            self.institution,
            request_user=self.user
        )
        
        self.assertEqual(len(objects_response['objects']), 1)
        retrieved_object = objects_response['objects'][0]
        self.assertEqual(retrieved_object['type'], 'indicator')
        
        # 7. Verify audit trail exists
        audit_logs = AuditLog.objects.filter(
            user=self.user,
            institution=self.institution
        )
        
        self.assertGreater(audit_logs.count(), 0)
        
        # Verify specific audit entries exist
        creation_logs = audit_logs.filter(action='create')
        read_logs = audit_logs.filter(action='read')
        
        self.assertGreater(creation_logs.count(), 0)
        self.assertGreater(read_logs.count(), 0)


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    # Configure Django settings for testing
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'crisp_threat_intel',
            ],
            SECRET_KEY='test-secret-key-for-testing-only',
            USE_TZ=True,
        )
        django.setup()
    
    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["crisp_threat_intel.tests.test_comprehensive"])
    
    if failures:
        exit(1)