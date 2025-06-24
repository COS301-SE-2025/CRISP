"""
Unit tests for STIX decorator pattern implementations in the CRISP platform.
"""
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase

from core.patterns.decorator.stix_object_component import StixObjectComponent
from core.patterns.decorator.stix_decorator import StixDecorator


# Create a concrete implementation of StixObjectComponent for testing
class ConcreteStixObject(StixObjectComponent):
    """Concrete implementation of StixObjectComponent for testing."""
    
    def __init__(self, stix_obj=None):
        """Initialize with an optional STIX object."""
        self.stix_obj = stix_obj or MagicMock()
        self.validated = False
        self.enriched = False
        self.exported = False
    
    def validate(self):
        """Validate the STIX object."""
        self.validated = True
        return True
    
    def export_to_taxii(self, collection_url, api_root, username=None, password=None):
        """Export the STIX object to a TAXII collection."""
        self.exported = True
        return {'status': 'success', 'url': collection_url, 'api_root': api_root}
    
    def enrich(self):
        """Enrich the STIX object."""
        self.enriched = True
        return self
    
    def get_stix_object(self):
        """Get the underlying STIX object."""
        return self.stix_obj


# Create concrete decorator implementations for testing
class StixValidationDecorator(StixDecorator):
    """Decorator for STIX validation."""
    
    def validate(self):
        """Extended validation with additional checks."""
        # First validate with the component
        base_result = self._component.validate()
        
        # Additional validation logic
        if base_result:
            # Perform additional validation
            stix_obj = self._component.get_stix_object()
            if hasattr(stix_obj, 'type') and stix_obj.type:
                return True
            return False  # Invalid if no type or empty type
        
        return False  # Invalid if base validation failed


class StixTaxiiExportDecorator(StixDecorator):
    """Decorator for TAXII export."""
    
    def export_to_taxii(self, collection_url, api_root, username=None, password=None):
        """Extended export with additional functionality."""
        # First export with the component
        result = self._component.export_to_taxii(collection_url, api_root, username, password)
        
        # Additional export logic
        result['format_version'] = '2.1'
        result['timestamp'] = 'test-timestamp'
        
        return result


class StixEnrichmentDecorator(StixDecorator):
    """Decorator for STIX enrichment."""
    
    def enrich(self):
        """Extended enrichment with additional information."""
        # First enrich with the component
        component = self._component.enrich()
        
        # Additional enrichment logic
        stix_obj = component.get_stix_object()
        if hasattr(stix_obj, 'description') and stix_obj.description:
            stix_obj.description += " (Enriched with additional context)"
        
        return component


class StixDecoratorTestCase(TestCase):
    """Test cases for STIX decorator pattern."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock STIX object
        self.mock_stix_obj = MagicMock()
        self.mock_stix_obj.type = 'indicator'
        self.mock_stix_obj.description = 'Test indicator'
        
        # Create a concrete STIX object component
        self.concrete_component = ConcreteStixObject(self.mock_stix_obj)

    def test_base_decorator(self):
        """Test the base decorator functionality."""
        # Create a decorator
        decorator = StixDecorator(self.concrete_component)
        
        # Test validation
        self.assertTrue(decorator.validate())
        self.assertTrue(self.concrete_component.validated)
        
        # Test export
        result = decorator.export_to_taxii('https://test.taxii/collection', 'api1')
        self.assertTrue(self.concrete_component.exported)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['url'], 'https://test.taxii/collection')
        
        # Test enrichment
        enriched = decorator.enrich()
        self.assertTrue(self.concrete_component.enriched)
        
        # Test get_stix_object
        stix_obj = decorator.get_stix_object()
        self.assertEqual(stix_obj, self.mock_stix_obj)

    def test_validation_decorator(self):
        """Test the validation decorator functionality."""
        # Create a decorator
        decorator = StixValidationDecorator(self.concrete_component)
        
        # Test validation with valid object
        self.assertTrue(decorator.validate())
        
        # Test validation with invalid object (no type)
        invalid_stix_obj = MagicMock()
        del invalid_stix_obj.type  # Remove the type attribute
        invalid_component = ConcreteStixObject(invalid_stix_obj)
        invalid_decorator = StixValidationDecorator(invalid_component)
        self.assertFalse(invalid_decorator.validate())

    def test_taxii_export_decorator(self):
        """Test the TAXII export decorator functionality."""
        # Create a decorator
        decorator = StixTaxiiExportDecorator(self.concrete_component)
        
        # Test export
        result = decorator.export_to_taxii('https://test.taxii/collection', 'api1', 'testuser', 'testpass')
        
        # Check base result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['url'], 'https://test.taxii/collection')
        
        # Check added fields
        self.assertEqual(result['format_version'], '2.1')
        self.assertEqual(result['timestamp'], 'test-timestamp')

    def test_enrichment_decorator(self):
        """Test the enrichment decorator functionality."""
        # Create a decorator
        decorator = StixEnrichmentDecorator(self.concrete_component)
        
        # Test enrichment
        enriched = decorator.enrich()
        
        # Check that the component was enriched
        self.assertTrue(self.concrete_component.enriched)
        
        # Check that the description was updated
        stix_obj = enriched.get_stix_object()
        self.assertEqual(stix_obj.description, 'Test indicator (Enriched with additional context)')

    def test_combined_decorators(self):
        """Test combining multiple decorators."""
        # Create a chain of decorators
        validator = StixValidationDecorator(self.concrete_component)
        exporter = StixTaxiiExportDecorator(validator)
        enricher = StixEnrichmentDecorator(exporter)
        
        # Validate
        self.assertTrue(enricher.validate())
        
        # Export
        result = enricher.export_to_taxii('https://test.taxii/collection', 'api1')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['format_version'], '2.1')
        
        # Enrich
        enriched = enricher.enrich()
        stix_obj = enriched.get_stix_object()
        self.assertEqual(stix_obj.description, 'Test indicator (Enriched with additional context)')
        
        # The base component should have been called for all operations
        self.assertTrue(self.concrete_component.validated)
        self.assertTrue(self.concrete_component.exported)
        self.assertTrue(self.concrete_component.enriched)


if __name__ == '__main__':
    unittest.main()