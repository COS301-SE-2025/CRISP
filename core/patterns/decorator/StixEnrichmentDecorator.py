from core.patterns.decorator.stix_decorator import StixDecorator
import logging

logger = logging.getLogger(__name__)

class StixEnrichmentDecorator(StixDecorator):
    """
    Concrete decorator that adds enrichment functionality to STIX objects.
    This decorator can enrich STIX objects with additional context from external sources.
    """
    
    def __init__(self, component, enrichment_sources=None):
        """
        Initialize the enrichment decorator
        
        Args:
            component: StixObjectComponent to decorate
            enrichment_sources: List of enrichment sources to use
        """
        super().__init__(component)
        self.enrichment_sources = enrichment_sources or []
        
    def enrich(self):
        """
        Enrich the STIX object with additional context from external sources.
        First calls the wrapped component's enrich method, then adds additional enrichment.
        
        Returns:
            StixObjectComponent: Enriched component
        """
        # First, call the wrapped component's enrich method
        enriched_component = self._component.enrich()
        
        # Then add our own enrichment
        stix_obj = enriched_component.get_stix_object()
        
        logger.info(f"Enriching STIX object with ID: {getattr(stix_obj, 'id', 'unknown')}")
        
        # Apply each enrichment source
        for source in self.enrichment_sources:
            try:
                logger.debug(f"Applying enrichment source: {source.__class__.__name__}")
                stix_obj = source.enrich_object(stix_obj)
            except Exception as e:
                logger.error(f"Error enriching STIX object: {str(e)}")
        
        return self
    
    def get_stix_object(self):
        """
        Get the enriched STIX object.
        
        Returns:
            object: Enriched STIX object
        """
        return self._component.get_stix_object()