from core.patterns.decorator.stix_object_component import StixObjectComponent
import logging
import requests
from stix2 import parse as stix2_parse
from django.utils import timezone

logger = logging.getLogger(__name__)

class ConcreteStixComponent(StixObjectComponent):
    """
    Concrete implementation of the StixObjectComponent interface.
    This is the base component that can be decorated with additional functionality.
    """
    
    def __init__(self, stix_object=None, stix_data=None):
        """
        Initialize with either a STIX object or raw STIX data.
        
        Args:
            stix_object: STIX object instance
            stix_data: Raw STIX data (dict or JSON string)
        """
        if stix_object:
            self._stix_object = stix_object
        elif stix_data:
            try:
                self._stix_object = stix2_parse(stix_data, allow_custom=True)
            except Exception as e:
                logger.error(f"Error parsing STIX data: {str(e)}")
                raise
        else:
            raise ValueError("Either stix_object or stix_data must be provided")
            
        self._validation_errors = []
    
    def validate(self):
        """
        Validate the STIX object.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Clear previous validation errors
        self._validation_errors = []
        
        # Basic validation
        stix_obj = self._stix_object
        
        # Check for required fields
        required_fields = ['id', 'type', 'created']
        for field in required_fields:
            if not hasattr(stix_obj, field):
                self._validation_errors.append(f"Missing required field: {field}")
                return False
        
        # Additional type-specific validation could be added here
        if stix_obj.type == 'indicator':
            if not hasattr(stix_obj, 'pattern'):
                self._validation_errors.append("Indicator missing 'pattern' field")
                return False
        elif stix_obj.type == 'attack-pattern':
            if not hasattr(stix_obj, 'name'):
                self._validation_errors.append("Attack pattern missing 'name' field")
                return False
        
        return len(self._validation_errors) == 0
    
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
        # Validate before export
        if not self.validate():
            logger.error("Cannot export invalid STIX object")
            return {
                'success': False,
                'timestamp': timezone.now(),
                'errors': self._validation_errors
            }
        
        try:
            # Prepare the serialized STIX object
            stix_json = self._stix_object.serialize()
            
            # Construct the TAXII API URL
            full_url = f"{collection_url}/{api_root}/collections/{collection_url}/objects/"
            
            # Set up authentication
            auth = None
            if username and password:
                auth = (username, password)
            
            # Set up headers
            headers = {
                'Content-Type': 'application/vnd.oasis.stix+json; version=2.1',
                'Accept': 'application/vnd.oasis.taxii+json; version=2.1'
            }
            
            # Make the request
            response = requests.post(
                full_url,
                data=stix_json,
                headers=headers,
                auth=auth
            )
            
            # Handle the response
            if response.status_code == 202:
                return {
                    'success': True,
                    'timestamp': timezone.now(),
                    'message': 'STIX object successfully exported to TAXII collection'
                }
            else:
                return {
                    'success': False,
                    'timestamp': timezone.now(),
                    'message': f'Failed to export STIX object: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error exporting STIX object to TAXII: {str(e)}")
            return {
                'success': False,
                'timestamp': timezone.now(),
                'message': f'Error exporting STIX object: {str(e)}'
            }
    
    def enrich(self):
        """
        Basic enrichment of the STIX object (placeholder implementation).
        
        Returns:
            StixObjectComponent: Self, for method chaining
        """
        # This is a basic implementation that does nothing
        # Concrete decorators will enhance this with actual enrichment
        return self
    
    def get_stix_object(self):
        """
        Get the underlying STIX object.
        
        Returns:
            object: STIX object
        """
        return self._stix_object
    
    def get_validation_errors(self):
        """
        Get the validation errors from the last validation run.
        
        Returns:
            list: List of validation error messages
        """
        return self._validation_errors