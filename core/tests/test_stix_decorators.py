"""
Essential Tests for STIX Trust Decorators

Covers core decorator functionality and patterns.
"""

import uuid
import json
from unittest.mock import Mock
from django.test import TestCase
from django.utils import timezone

from core.trust.patterns.decorator.stix_trust_decorators import (
    ConcreteStixTrustComponent,
    StixTrustValidationDecorator,
    StixTrustAnonymizationDecorator,
    StixTrustDecoratorChain
)
from core.trust.patterns.factory.stix_trust_factory import StixTrustObject
from core.trust.patterns.strategy.access_control_strategies import AnonymizationContext


class MockStixTrustObject(StixTrustObject):
    """Mock STIX trust object for testing"""
    
    def __init__(self, object_type='indicator', **kwargs):
        self.type = object_type
        self.id = f"{object_type}--{uuid.uuid4()}"
        self.created = timezone.now().isoformat()
        self.modified = timezone.now().isoformat()
        self.spec_version = "2.1"
        self.labels = ["malicious-activity"]
        self.pattern = "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']"
        self.valid_from = timezone.now().isoformat()
        self._data = {
            'type': self.type,
            'id': self.id,
            'created': self.created,
            'modified': self.modified,
            'spec_version': self.spec_version,
            'labels': self.labels,
            'pattern': self.pattern,
            'valid_from': self.valid_from,
            **kwargs
        }
    
    def to_dict(self):
        return self._data.copy()
    
    def to_json(self):
        return json.dumps(self._data)
    
    def get_type(self):
        return self.type
    
    def get_id(self):
        return self.id


class ConcreteStixTrustComponentTest(TestCase):
    """Test basic STIX component functionality"""
    
    def setUp(self):
        self.stix_object = MockStixTrustObject()
        self.component = ConcreteStixTrustComponent(self.stix_object)
    
    def test_basic_operations(self):
        """Test basic component operations"""
        self.assertEqual(self.component.get_type(), 'indicator')
        self.assertTrue(self.component.get_id().startswith('indicator--'))
        self.assertIsInstance(self.component.to_dict(), dict)
        self.assertIsInstance(self.component.to_json(), str)


class StixTrustValidationDecoratorTest(TestCase):
    """Test STIX validation decorator"""
    
    def setUp(self):
        self.stix_object = MockStixTrustObject()
        self.component = ConcreteStixTrustComponent(self.stix_object)
        self.decorator = StixTrustValidationDecorator(self.component)
    
    def test_validation_passes_for_valid_object(self):
        """Test validation passes for valid STIX object"""
        result = self.decorator.to_dict()
        
        self.assertIn('x_crisp_validation', result)
        self.assertTrue(result['x_crisp_validation']['is_valid'])
        self.assertEqual(len(result['x_crisp_validation']['errors']), 0)
    
    def test_validation_fails_for_invalid_object(self):
        """Test validation fails for invalid STIX object"""
        invalid_object = MockStixTrustObject()
        invalid_object._data = {'type': 'indicator'}  # Missing required fields
        component = ConcreteStixTrustComponent(invalid_object)
        decorator = StixTrustValidationDecorator(component, strict_mode=False)
        
        result = decorator.to_dict()
        
        self.assertIn('x_crisp_validation', result)
        self.assertFalse(result['x_crisp_validation']['is_valid'])
        self.assertGreater(len(result['x_crisp_validation']['errors']), 0)


class StixTrustAnonymizationDecoratorTest(TestCase):
    """Test STIX anonymization decorator"""
    
    def setUp(self):
        self.stix_object = MockStixTrustObject()
        self.component = ConcreteStixTrustComponent(self.stix_object)
        
        self.context = AnonymizationContext(
            anonymization_level='partial',
            access_level='read',
            target_organization='org123'
        )
        
        self.decorator = StixTrustAnonymizationDecorator(self.component, self.context)
    
    def test_anonymization_applied(self):
        """Test that anonymization is applied"""
        result = self.decorator.to_dict()
        
        self.assertIn('x_crisp_anonymization', result)
        self.assertEqual(result['x_crisp_anonymization']['anonymization_level'], 'partial')
        self.assertTrue(result['x_crisp_anonymization']['anonymized'])
    
    def test_different_anonymization_levels(self):
        """Test different anonymization levels"""
        for level in ['none', 'partial', 'full']:
            decorator = StixTrustAnonymizationDecorator(self.component, self.context, level)
            result = decorator.to_dict()
            
            self.assertIn('x_crisp_anonymization', result)
            self.assertEqual(result['x_crisp_anonymization']['anonymization_level'], level)


class StixTrustDecoratorChainTest(TestCase):
    """Test decorator chain builder"""
    
    def setUp(self):
        self.stix_object = MockStixTrustObject()
        self.chain = StixTrustDecoratorChain(self.stix_object)
    
    def test_chain_initialization(self):
        """Test chain initialization"""
        self.assertIsNotNone(self.chain._component)
        self.assertIsInstance(self.chain._component, ConcreteStixTrustComponent)
    
    def test_fluent_interface(self):
        """Test fluent interface methods"""
        result = self.chain.validate().anonymize().enrich()
        self.assertEqual(result, self.chain)
    
    def test_chained_decorators(self):
        """Test chaining multiple decorators"""
        context = AnonymizationContext(
            anonymization_level='partial',
            access_level='read',
            target_organization='org123'
        )
        
        component = (self.chain
                    .validate()
                    .anonymize(context)
                    .build())
        
        result = component.to_dict()
        
        # Should have all decorator metadata
        self.assertIn('x_crisp_validation', result)
        self.assertIn('x_crisp_anonymization', result)
    
    def test_build(self):
        """Test building the decorator chain"""
        result = self.chain.build()
        self.assertIsNotNone(result)