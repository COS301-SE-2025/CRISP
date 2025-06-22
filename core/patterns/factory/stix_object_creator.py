from abc import ABC, abstractmethod

class StixObjectCreator(ABC):
    """
    Abstract factory
    """
    
    @abstractmethod
    def create_from_stix(self, stix_obj):
        """
        Create a CRISP entity from a STIX object.
        
        Args:
            stix_obj: STIX object
            
        Returns:
            Dictionary with CRISP entity properties
        """
        pass
    
    @abstractmethod
    def create_stix_object(self, crisp_entity):
        """
        Create a STIX object from a CRISP entity.
        
        Args:
            crisp_entity: CRISP entity model instance
            
        Returns:
            STIX object
        """
        pass