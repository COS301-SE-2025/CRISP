from abc import ABC, abstractmethod

class StixObjectComponent(ABC):
    """
    Interface for all STIX objects.
    """
    
    @abstractmethod
    def validate(self):
        """
        Validate the STIX object.
        
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def export_to_taxii(self, collection_url, api_root, username=None, password=None):
        """
        Export the STIX object to a TAXII collection.
        
        Args:
            collection_url: URL of the TAXII collection
            api_root: API root path
            username: Optional username
            password: Optional password for authentication
            
        Returns:
            dict: Result of the export operation
        """
        pass
    
    @abstractmethod
    def enrich(self):
        """
        Enrich the STIX object with additional context.
        
        Returns:
            StixObjectComponent: Enriched component
        """
        pass
    
    @abstractmethod
    def get_stix_object(self):
        """
        Get the underlying STIX object.
        
        Returns:
            object: STIX object
        """
        pass