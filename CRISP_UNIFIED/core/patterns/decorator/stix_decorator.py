from core.patterns.decorator.stix_object_component import StixObjectComponent

class StixDecorator(StixObjectComponent):
    """
    Base decorator class
    """
    
    def __init__(self, component):
        """
        Initialize the decorator
        
        Args:
            component: StixObjectComponent to decorate
        """
        self._component = component
    
    def validate(self):
        """
        Pass through validation to the decorated component.
        
        Returns:
            bool: Result of validation
        """
        return self._component.validate()
    
    def export_to_taxii(self, collection_url, api_root, username=None, password=None):
        """
        Pass through export to the decorated component.
        
        Args:
            collection_url: URL of the TAXII collection
            api_root: API root path
            username: Optional username
            password: Optional password for authentication
            
        Returns:
            dict: Result of the export operation
        """
        return self._component.export_to_taxii(collection_url, api_root, username, password)
    
    def enrich(self):
        """
        Pass through enrichment to the decorated component.
        
        Returns:
            StixObjectComponent: Enriched component
        """
        return self._component.enrich()
    
    def get_stix_object(self):
        """
        Pass through to get the underlying STIX object.
        
        Returns:
            object: STIX object
        """
        return self._component.get_stix_object()