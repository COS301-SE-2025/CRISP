from core.patterns.decorator.stix_decorator import StixDecorator
import logging
import copy

logger = logging.getLogger(__name__)

class StixAnonymizationDecorator(StixDecorator):
    """
    Concrete decorator that adds anonymization capabilities to STIX objects.
    This decorator can anonymize sensitive fields in STIX objects before sharing.
    """
    
    def __init__(self, component, anonymization_strategy=None):
        """
        Initialize the anonymization decorator
        
        Args:
            component: StixObjectComponent to decorate
            anonymization_strategy: Strategy to use for anonymizing data
        """
        super().__init__(component)
        self.anonymization_strategy = anonymization_strategy
        self._is_anonymized = False
        
    def get_stix_object(self):
        """
        Get the potentially anonymized STIX object.
        
        Returns:
            object: STIX object (anonymized if anonymization has been applied)
        """
        stix_obj = self._component.get_stix_object()
        
        if not self._is_anonymized and self.anonymization_strategy:
            # Create a deep copy to avoid modifying the original
            stix_obj_copy = copy.deepcopy(stix_obj)
            
            # Apply anonymization
            try:
                stix_obj = self.anonymization_strategy.anonymize(stix_obj_copy)
                self._is_anonymized = True
                logger.info(f"Anonymized STIX object with ID: {getattr(stix_obj, 'id', 'unknown')}")
            except Exception as e:
                logger.error(f"Error anonymizing STIX object: {str(e)}")
        
        return stix_obj
    
    def export_to_taxii(self, collection_url, api_root, username=None, password=None):
        """
        Export the anonymized STIX object to a TAXII collection.
        
        Args:
            collection_url: URL of the TAXII collection
            api_root: API root path
            username: Optional username
            password: Optional password for authentication
            
        Returns:
            dict: Result of the export operation
        """
        # Ensure the object is anonymized before export
        if not self._is_anonymized and self.anonymization_strategy:
            self.get_stix_object()  # This will trigger anonymization
        
        # Now delegate to the wrapped component
        return self._component.export_to_taxii(collection_url, api_root, username, password)