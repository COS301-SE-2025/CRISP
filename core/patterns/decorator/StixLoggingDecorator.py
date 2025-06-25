from core.patterns.decorator.stix_decorator import StixDecorator
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def log_method_execution(method):
    """
    Decorator for logging method execution time and results.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        method_name = method.__name__
        stix_obj = self._component.get_stix_object()
        stix_id = getattr(stix_obj, 'id', 'unknown')
        
        logger.info(f"Starting {method_name} for STIX object {stix_id}")
        start_time = time.time()
        
        try:
            result = method(self, *args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Completed {method_name} in {execution_time:.2f}s for STIX object {stix_id}")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed {method_name} after {execution_time:.2f}s for STIX object {stix_id}: {str(e)}")
            raise
    
    return wrapper

class StixLoggingDecorator(StixDecorator):
    """
    Concrete decorator that adds logging capabilities to STIX object operations.
    This decorator logs execution time and results of STIX object operations.
    """
    
    def __init__(self, component, log_level=logging.INFO):
        """
        Initialize the logging decorator
        
        Args:
            component: StixObjectComponent to decorate
            log_level: Logging level to use
        """
        super().__init__(component)
        self.log_level = log_level
        
    @log_method_execution
    def validate(self):
        """
        Validate the STIX object with logging.
        
        Returns:
            bool: Result of validation
        """
        return self._component.validate()
    
    @log_method_execution
    def export_to_taxii(self, collection_url, api_root, username=None, password=None):
        """
        Export the STIX object to TAXII with logging.
        
        Args:
            collection_url: URL of the TAXII collection
            api_root: API root path
            username: Optional username
            password: Optional password for authentication
            
        Returns:
            dict: Result of the export operation
        """
        return self._component.export_to_taxii(collection_url, api_root, username, password)
    
    @log_method_execution
    def enrich(self):
        """
        Enrich the STIX object with logging.
        
        Returns:
            StixObjectComponent: Enriched component
        """
        return self._component.enrich()