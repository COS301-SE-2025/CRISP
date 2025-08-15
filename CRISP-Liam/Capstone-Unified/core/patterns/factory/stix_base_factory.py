from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import uuid
import stix2
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class StixObjectCreator(ABC):
    """
    Abstract factory for creating and converting STIX objects
    """
    
    @abstractmethod
    def create_from_stix(self, stix_obj) -> Dict[str, Any]:
        """
        Create a CRISP entity from a STIX object.
        
        Args:
            stix_obj: STIX object
            
        Returns:
            Dictionary with CRISP entity properties
        """
        pass
    
    @abstractmethod
    def create_stix_object(self, crisp_entity) -> Any:
        """
        Create a STIX object from a CRISP entity.
        
        Args:
            crisp_entity: CRISP entity model instance
            
        Returns:
            STIX object
        """
        pass
    
    @abstractmethod
    def create_object(self, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX object from input data dictionary.
        
        Args:
            data: Input data for creating the STIX object
            spec_version: STIX specification version (2.0 or 2.1)
            
        Returns:
            STIX object dictionary
        """
        pass
    
    def _ensure_common_properties(self, stix_obj: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Ensure common STIX properties are set.
        
        Args:
            stix_obj: STIX object dictionary
            spec_version: STIX specification version (2.0 or 2.1)
            
        Returns:
            STIX object with common properties ensured
        """
        # Validate spec_version
        if spec_version not in ["2.0", "2.1"]:
            raise ValueError(f"Unsupported STIX spec_version: {spec_version}. Must be '2.0' or '2.1'")
        
        current_time = stix2.utils.format_datetime(timezone.now())
        
        # Ensure required properties
        if 'id' not in stix_obj:
            stix_obj['id'] = f"{stix_obj['type']}--{str(uuid.uuid4())}"
        
        if 'spec_version' not in stix_obj:
            stix_obj['spec_version'] = spec_version
        
        if 'created' not in stix_obj:
            stix_obj['created'] = current_time
        
        if 'modified' not in stix_obj:
            stix_obj['modified'] = current_time
        
        return stix_obj


class STIXObjectFactory:
    """
    Factory registry for creating STIX objects
    """
    
    _creators = {}  # Will be populated by concrete implementations
    
    @classmethod
    def create_object(cls, object_type: str, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX object using the appropriate factory
        
        Args:
            object_type: Type of STIX object to create
            data: Input data for object creation
            spec_version: STIX specification version (2.0 or 2.1)
            
        Returns:
            STIX object dictionary
            
        Raises:
            ValueError: If object type is not supported
        """
        if object_type not in cls._creators:
            raise ValueError(f"Unsupported STIX object type: {object_type}")
        
        creator = cls._creators[object_type]()
        return creator.create_object(data, spec_version)
    
    @classmethod
    def create_from_stix(cls, stix_obj) -> Dict[str, Any]:
        """
        Create a CRISP entity from a STIX object.
        
        Args:
            stix_obj: STIX object
            
        Returns:
            Dictionary with CRISP entity properties
            
        Raises:
            ValueError: If object type is not supported
        """
        object_type = stix_obj.type.replace('_', '-')  # Handle type variations
        
        if object_type not in cls._creators:
            raise ValueError(f"Unsupported STIX object type: {object_type}")
        
        creator = cls._creators[object_type]()
        return creator.create_from_stix(stix_obj)
    
    @classmethod
    def create_stix_object(cls, object_type: str, crisp_entity) -> Any:
        """
        Create a STIX object from a CRISP entity.
        
        Args:
            object_type: Type of STIX object to create
            crisp_entity: CRISP entity model instance
            
        Returns:
            STIX object
            
        Raises:
            ValueError: If object type is not supported
        """
        if object_type not in cls._creators:
            raise ValueError(f"Unsupported STIX object type: {object_type}")
        
        creator = cls._creators[object_type]()
        return creator.create_stix_object(crisp_entity)
    
    @classmethod
    def register_creator(cls, object_type: str, creator_class: type):
        """
        Register a new STIX object creator.
        
        Args:
            object_type: STIX object type
            creator_class: Creator class
        """
        if not issubclass(creator_class, StixObjectCreator):
            raise ValueError("Creator class must inherit from StixObjectCreator")
        
        cls._creators[object_type] = creator_class
        logger.info(f"Registered STIX creator for type: {object_type}")
    
    @classmethod
    def get_supported_types(cls) -> list:
        """
        Get list of supported STIX object types.
        
        Returns:
            List of supported object types
        """
        return list(cls._creators.keys())
    
    @classmethod
    def unregister_creator(cls, object_type: str):
        """
        Unregister a STIX object creator.
        
        Args:
            object_type: STIX object type to unregister
        """
        if object_type in cls._creators:
            del cls._creators[object_type]
            logger.info(f"Unregistered STIX creator for type: {object_type}")