import pytest
from django.test import TestCase
from django.utils import timezone
import uuid

from ..factories.stix_object_creator import (
    StixObjectFactory, StixIndicatorCreator, StixTTPCreator,
    StixMalwareCreator, StixThreatActorCreator, StixIdentityCreator,
    StixRelationshipCreator, StixObject
)
from ..domain.models import Institution, User, ThreatFeed, Indicator, TTPData
from django.contrib.auth.models import User as DjangoUser


class TestStixObjectCreators(TestCase):
    """Test cases for STIX object creators (Factory Pattern)"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution = Institution.objects.create(
            name='Test University',
            created_by=self.django_user
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution,
            role='analyst'
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution,
            created_by=self.user
        )
    
    def test_stix_indicator_creator(self):
        """Test STIX indicator creator"""
        creator = StixIndicatorCreator()
        
        data = {
            'name': 'Test Indicator',
            'pattern': "[ipv4-addr:value = '192.0.2.1']",
            'labels': ['malicious-activity'],
            'valid_from': timezone.now().isoformat()
        }
        
        stix_data = creator.create_stix_object(data)
        
        self.assertEqual(stix_data['type'], 'indicator')
        self.assertEqual(stix_data['name'], 'Test Indicator')
        self.assertEqual(stix_data['pattern'], "[ipv4-addr:value = '192.0.2.1']")
        self.assertEqual(stix_data['labels'], ['malicious-activity'])
        self.assertEqual(stix_data['spec_version'], '2.1')
        self.assertIn('id', stix_data)
        self.assertTrue(stix_data['id'].startswith('indicator--'))
        self.assertIn('created', stix_data)
        self.assertIn('modified', stix_data)
    
    def test_stix_indicator_creator_missing_pattern(self):
        """Test STIX indicator creator with missing pattern"""
        creator = StixIndicatorCreator()
        
        data = {
            'name': 'Test Indicator',
            'labels': ['malicious-activity']
        }
        
        with self.assertRaises(ValueError) as context:
            creator.create_stix_object(data)
        
        self.assertIn('pattern', str(context.exception))
    
    def test_stix_indicator_creator_from_domain_model(self):
        """Test creating STIX object from domain model"""
        indicator = Indicator.objects.create(
            name='Domain Model Indicator',
            description='Test description',
            pattern="[domain-name:value = 'evil.com']",
            labels=['malicious-activity'],
            valid_from=timezone.now(),
            confidence=85,
            threat_feed=self.threat_feed,
            created_by=self.user
        )
        
        creator = StixIndicatorCreator()
        stix_data = creator.create_from_domain_model(indicator)
        
        self.assertEqual(stix_data['type'], 'indicator')
        self.assertEqual(stix_data['id'], indicator.stix_id)
        self.assertEqual(stix_data['name'], 'Domain Model Indicator')
        self.assertEqual(stix_data['pattern'], "[domain-name:value = 'evil.com']")
        self.assertEqual(stix_data['confidence'], 85)
    
    def test_stix_ttp_creator(self):
        """Test STIX TTP creator"""
        creator = StixTTPCreator()
        
        data = {
            'name': 'Spearphishing',
            'description': 'Spearphishing attack pattern',
            'kill_chain_phases': [
                {'kill_chain_name': 'mitre-attack', 'phase_name': 'initial-access'}
            ]
        }
        
        stix_data = creator.create_stix_object(data)
        
        self.assertEqual(stix_data['type'], 'attack-pattern')
        self.assertEqual(stix_data['name'], 'Spearphishing')
        self.assertEqual(stix_data['description'], 'Spearphishing attack pattern')
        self.assertEqual(len(stix_data['kill_chain_phases']), 1)
        self.assertIn('id', stix_data)
        self.assertTrue(stix_data['id'].startswith('attack-pattern--'))
    
    def test_stix_ttp_creator_from_domain_model(self):
        """Test creating STIX TTP from domain model"""
        ttp = TTPData.objects.create(
            name='Command Line Interface',
            description='Command-line interface usage',
            kill_chain_phases=[
                {'kill_chain_name': 'mitre-attack', 'phase_name': 'execution'}
            ],
            x_mitre_platforms=['Windows', 'Linux', 'macOS'],
            x_mitre_tactics=['execution'],
            x_mitre_techniques=['T1059'],
            threat_feed=self.threat_feed,
            created_by=self.user
        )
        
        creator = StixTTPCreator()
        stix_data = creator.create_from_domain_model(ttp)
        
        self.assertEqual(stix_data['type'], 'attack-pattern')
        self.assertEqual(stix_data['id'], ttp.stix_id)
        self.assertEqual(stix_data['name'], 'Command Line Interface')
        self.assertEqual(stix_data['x_mitre_platforms'], ['Windows', 'Linux', 'macOS'])
        self.assertEqual(stix_data['x_mitre_tactics'], ['execution'])
        self.assertEqual(stix_data['x_mitre_techniques'], ['T1059'])
    
    def test_stix_malware_creator(self):
        """Test STIX malware creator"""
        creator = StixMalwareCreator()
        
        data = {
            'name': 'Test Malware',
            'is_family': True,
            'malware_types': ['trojan']
        }
        
        stix_data = creator.create_stix_object(data)
        
        self.assertEqual(stix_data['type'], 'malware')
        self.assertEqual(stix_data['name'], 'Test Malware')
        self.assertTrue(stix_data['is_family'])
        self.assertEqual(stix_data['malware_types'], ['trojan'])
        self.assertIn('id', stix_data)
        self.assertTrue(stix_data['id'].startswith('malware--'))
    
    def test_stix_threat_actor_creator(self):
        """Test STIX threat actor creator"""
        creator = StixThreatActorCreator()
        
        data = {
            'name': 'APT Group',
            'threat_actor_types': ['nation-state']
        }
        
        stix_data = creator.create_stix_object(data)
        
        self.assertEqual(stix_data['type'], 'threat-actor')
        self.assertEqual(stix_data['name'], 'APT Group')
        self.assertEqual(stix_data['threat_actor_types'], ['nation-state'])
        self.assertIn('id', stix_data)
        self.assertTrue(stix_data['id'].startswith('threat-actor--'))
    
    def test_stix_identity_creator(self):
        """Test STIX identity creator"""
        creator = StixIdentityCreator()
        
        data = {
            'name': 'Test Organization',
            'identity_class': 'organization'
        }
        
        stix_data = creator.create_stix_object(data)
        
        self.assertEqual(stix_data['type'], 'identity')
        self.assertEqual(stix_data['name'], 'Test Organization')
        self.assertEqual(stix_data['identity_class'], 'organization')
        self.assertIn('id', stix_data)
        self.assertTrue(stix_data['id'].startswith('identity--'))
    
    def test_stix_identity_creator_missing_name(self):
        """Test STIX identity creator with missing name"""
        creator = StixIdentityCreator()
        
        data = {
            'identity_class': 'organization'
        }
        
        with self.assertRaises(ValueError) as context:
            creator.create_stix_object(data)
        
        self.assertIn('name', str(context.exception))
    
    def test_stix_relationship_creator(self):
        """Test STIX relationship creator"""
        creator = StixRelationshipCreator()
        
        data = {
            'relationship_type': 'indicates',
            'source_ref': 'indicator--12345678-1234-1234-1234-123456789012',
            'target_ref': 'malware--87654321-4321-4321-4321-210987654321'
        }
        
        stix_data = creator.create_stix_object(data)
        
        self.assertEqual(stix_data['type'], 'relationship')
        self.assertEqual(stix_data['relationship_type'], 'indicates')
        self.assertEqual(stix_data['source_ref'], 'indicator--12345678-1234-1234-1234-123456789012')
        self.assertEqual(stix_data['target_ref'], 'malware--87654321-4321-4321-4321-210987654321')
        self.assertIn('id', stix_data)
        self.assertTrue(stix_data['id'].startswith('relationship--'))
    
    def test_stix_relationship_creator_missing_fields(self):
        """Test STIX relationship creator with missing required fields"""
        creator = StixRelationshipCreator()
        
        # Missing relationship_type
        data = {
            'source_ref': 'indicator--12345678-1234-1234-1234-123456789012',
            'target_ref': 'malware--87654321-4321-4321-4321-210987654321'
        }
        
        with self.assertRaises(ValueError):
            creator.create_stix_object(data)
        
        # Missing source_ref
        data = {
            'relationship_type': 'indicates',
            'target_ref': 'malware--87654321-4321-4321-4321-210987654321'
        }
        
        with self.assertRaises(ValueError):
            creator.create_stix_object(data)
        
        # Missing target_ref
        data = {
            'relationship_type': 'indicates',
            'source_ref': 'indicator--12345678-1234-1234-1234-123456789012'
        }
        
        with self.assertRaises(ValueError):
            creator.create_stix_object(data)


class TestStixObject(TestCase):
    """Test cases for StixObject product class"""
    
    def test_stix_object_creation(self):
        """Test creating a StixObject"""
        stix_data = {
            'type': 'indicator',
            'id': 'indicator--12345678-1234-1234-1234-123456789012',
            'created': '2024-01-01T00:00:00.000Z',
            'modified': '2024-01-01T00:00:00.000Z',
            'pattern': "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            'labels': ['malicious-activity'],
            'valid_from': '2024-01-01T00:00:00.000Z'
        }
        
        stix_obj = StixObject(stix_data)
        
        self.assertEqual(stix_obj.get_type(), 'indicator')
        self.assertEqual(stix_obj.get_id(), 'indicator--12345678-1234-1234-1234-123456789012')
        self.assertEqual(stix_obj.to_dict(), stix_data)
        
        json_str = stix_obj.to_json()
        self.assertIn('indicator', json_str)
        self.assertIn('malicious-activity', json_str)


class TestStixObjectFactory(TestCase):
    """Test cases for StixObjectFactory registry"""
    
    def test_factory_registration(self):
        """Test factory registration"""
        # Test that default factories are registered
        creator = StixObjectFactory.get_creator('indicator')
        self.assertIsInstance(creator, StixIndicatorCreator)
        
        creator = StixObjectFactory.get_creator('attack-pattern')
        self.assertIsInstance(creator, StixTTPCreator)
        
        creator = StixObjectFactory.get_creator('malware')
        self.assertIsInstance(creator, StixMalwareCreator)
    
    def test_factory_unsupported_type(self):
        """Test factory with unsupported type"""
        with self.assertRaises(ValueError) as context:
            StixObjectFactory.get_creator('unsupported-type')
        
        self.assertIn('No creator registered', str(context.exception))
    
    def test_factory_create_stix_object(self):
        """Test factory create STIX object method"""
        data = {
            'type': 'indicator',
            'name': 'Test Indicator',
            'pattern': "[file:name = 'test.exe']",
            'labels': ['malicious-activity'],
            'valid_from': timezone.now().isoformat()
        }
        
        stix_obj = StixObjectFactory.create_stix_object(data)
        
        self.assertIsInstance(stix_obj, StixObject)
        self.assertEqual(stix_obj.get_type(), 'indicator')
        
        stix_data = stix_obj.to_dict()
        self.assertEqual(stix_data['type'], 'indicator')
        self.assertEqual(stix_data['name'], 'Test Indicator')
    
    def test_factory_missing_type(self):
        """Test factory with missing type"""
        data = {
            'name': 'Test Object',
            'pattern': "[file:name = 'test.exe']"
        }
        
        with self.assertRaises(ValueError) as context:
            StixObjectFactory.create_stix_object(data)
        
        self.assertIn('type', str(context.exception))
    
    def test_get_supported_types(self):
        """Test getting supported types"""
        supported_types = StixObjectFactory.get_supported_types()
        
        self.assertIn('indicator', supported_types)
        self.assertIn('attack-pattern', supported_types)
        self.assertIn('malware', supported_types)
        self.assertIn('threat-actor', supported_types)
        self.assertIn('identity', supported_types)
        self.assertIn('relationship', supported_types)
    
    def test_register_custom_creator(self):
        """Test registering a custom creator"""
        class CustomCreator(StixIndicatorCreator):
            def create_stix_object(self, data):
                stix_data = super().create_stix_object(data)
                stix_data['x_custom_field'] = 'custom_value'
                return stix_data
        
        StixObjectFactory.register_creator('custom-indicator', CustomCreator)
        
        creator = StixObjectFactory.get_creator('custom-indicator')
        self.assertIsInstance(creator, CustomCreator)
        
        data = {
            'type': 'custom-indicator',
            'name': 'Custom Indicator',
            'pattern': "[file:name = 'custom.exe']",
            'labels': ['custom']
        }
        
        stix_data = creator.create_stix_object(data)
        self.assertEqual(stix_data['x_custom_field'], 'custom_value')


class TestStixObjectCommonFields(TestCase):
    """Test cases for common STIX object field handling"""
    
    def test_prepare_common_fields(self):
        """Test preparation of common STIX fields"""
        creator = StixIndicatorCreator()
        
        data = {
            'type': 'indicator',
            'name': 'Test'
        }
        
        prepared_data = creator._prepare_common_fields(data)
        
        self.assertEqual(prepared_data['spec_version'], '2.1')
        self.assertIn('created', prepared_data)
        self.assertIn('modified', prepared_data)
        
        # Test that existing fields are preserved
        data_with_existing = {
            'type': 'indicator',
            'name': 'Test',
            'spec_version': '2.0',
            'created': '2024-01-01T00:00:00.000Z'
        }
        
        prepared_data = creator._prepare_common_fields(data_with_existing)
        
        self.assertEqual(prepared_data['spec_version'], '2.0')  # Existing preserved
        self.assertEqual(prepared_data['created'], '2024-01-01T00:00:00.000Z')  # Existing preserved
        self.assertIn('modified', prepared_data)  # New field added