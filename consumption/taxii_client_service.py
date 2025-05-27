import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from taxii2client.v21 import Server, ApiRoot, Collection, as_pages
from taxii2client.v21.exceptions import TAXIIServiceException

from django.utils import timezone
from django.conf import settings

from .models import ExternalFeedSource, FeedConsumptionLog

logger = logging.getLogger(__name__)

class TaxiiClientError(Exception):
    """Base exception for TAXII client errors."""
    pass

class TaxiiConnectionError(TaxiiClientError):
    """Exception raised for connection errors to TAXII servers."""
    pass

class TaxiiAuthenticationError(TaxiiClientError):
    """Exception raised for authentication errors with TAXII servers."""
    pass

class TaxiiDataError(TaxiiClientError):
    """Exception raised for data parsing or validation errors."""
    pass

class TaxiiClient:
    """
    Client for consuming threat intelligence from TAXII 2.1 compliant servers.
    
    This class handles discovery, authentication, and retrieval of STIX objects
    from external TAXII servers, with appropriate error handling and retry logic.
    """
    
    def __init__(self, feed_source: ExternalFeedSource):
        """
        Initialize a TAXII client for the given feed source.
        
        Args:
            feed_source: ExternalFeedSource model instance containing connection details
        """
        self.feed_source = feed_source
        self.server = None
        self.api_root = None
        self.collection = None
        self.log_entry = None
        
        # Default headers for requests
        self.headers = {
            'Accept': 'application/taxii+json;version=2.1',
            'User-Agent': f'CRISP-Taxii-Client/{settings.CRISP_VERSION}'
        }
        
        # Apply authentication if configured
        auth_config = feed_source.get_auth_config()
        if auth_config:
            self._apply_authentication(auth_config)
    
    def _apply_authentication(self, auth_config: Dict[str, str]):
        """
        Apply authentication headers or parameters based on auth config.
        
        Args:
            auth_config: Authentication configuration dictionary
        """
        if auth_config['type'] == 'api_key':
            self.headers[auth_config['header_name']] = auth_config['key']
        elif auth_config['type'] == 'jwt':
            self.headers['Authorization'] = f'Bearer {auth_config["token"]}'
        elif auth_config['type'] == 'basic':
            self.auth = (auth_config['username'], auth_config['password'])
        else:
            self.auth = None
    
    def _with_retry(self, func, *args, max_attempts=3, **kwargs):
        """
        Execute a function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            max_attempts: Maximum number of retry attempts
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function if successful
            
        Raises:
            TaxiiClientError: If all retry attempts fail
        """
        attempt = 0
        last_error = None
        
        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except (RequestException, TAXIIServiceException) as e:
                attempt += 1
                last_error = e
                
                if attempt >= max_attempts:
                    break
                
                # Exponential backoff with jitter
                delay = min(30, (2 ** attempt) + (time.random() * 0.5))
                logger.warning(
                    f"TAXII request failed (attempt {attempt}/{max_attempts}), "
                    f"retrying in {delay:.2f}s: {str(e)}"
                )
                time.sleep(delay)
        
        # If we got here, all retries failed
        error_msg = f"Failed after {max_attempts} attempts: {str(last_error)}"
        if self.log_entry:
            self.log_entry.add_error(error_msg)
            self.log_entry.save()
        
        # Re-raise appropriate exception type
        if isinstance(last_error, ConnectionError):
            raise TaxiiConnectionError(error_msg)
        elif isinstance(last_error, Timeout):
            raise TaxiiConnectionError(f"Timeout: {error_msg}")
        elif last_error and hasattr(last_error, 'response') and last_error.response.status_code in (401, 403):
            raise TaxiiAuthenticationError(f"Authentication failed: {error_msg}")
        else:
            raise TaxiiClientError(error_msg)
    
    def discover(self) -> Dict[str, Any]:
        """
        Perform TAXII discovery to identify available API roots.
        
        Returns:
            Dict with discovery information including available API roots
            
        Raises:
            TaxiiClientError: If discovery fails
        """
        try:
            # Create server instance with authentication
            self.server = Server(
                self.feed_source.discovery_url,
                verify=settings.TAXII_VERIFY_SSL,
                headers=self.headers
            )
            
            # Perform discovery
            discovery_info = {
                'title': self.server.title,
                'description': self.server.description,
                'api_roots': [root.url for root in self.server.api_roots]
            }
            
            # If API root not specified, use the first one or default
            if not self.feed_source.api_root and discovery_info['api_roots']:
                self.feed_source.api_root = discovery_info['api_roots'][0]
                self.feed_source.save(update_fields=['api_root'])
            
            return discovery_info
            
        except TAXIIServiceException as e:
            error_msg = f"TAXII discovery failed: {str(e)}"
            logger.error(error_msg)
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                self.log_entry.save()
            raise TaxiiClientError(error_msg)
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """
        Get available collections from the configured API root.
        
        Returns:
            List of collection information dictionaries
            
        Raises:
            TaxiiClientError: If retrieving collections fails
        """
        try:
            # If no API root is configured, perform discovery first
            if not self.feed_source.api_root:
                self.discover()
            
            # Connect to API root
            self.api_root = ApiRoot(
                self.feed_source.api_root,
                verify=settings.TAXII_VERIFY_SSL,
                headers=self.headers
            )
            
            # Get available collections
            collections = []
            for collection in self.api_root.collections:
                collections.append({
                    'id': collection.id,
                    'title': collection.title,
                    'description': collection.description,
                    'can_read': collection.can_read,
                    'can_write': collection.can_write,
                    'media_types': collection.media_types
                })
            
            # If no collection_id is configured, use the first available
            if not self.feed_source.collection_id and collections:
                for collection in collections:
                    if collection['can_read']:
                        self.feed_source.collection_id = collection['id']
                        self.feed_source.save(update_fields=['collection_id'])
                        break
            
            return collections
            
        except TAXIIServiceException as e:
            error_msg = f"Failed to retrieve collections: {str(e)}"
            logger.error(error_msg)
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                self.log_entry.save()
            raise TaxiiClientError(error_msg)
    
    def get_objects(
        self, 
        added_after: Optional[datetime] = None, 
        types: Optional[List[str]] = None, 
        max_objects: int = 1000
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve STIX objects from the configured collection.
        
        Args:
            added_after: Only retrieve objects added after this time
            types: Only retrieve objects of these types
            max_objects: Maximum number of objects to retrieve
            
        Returns:
            Tuple of (retrieved objects list, total count)
            
        Raises:
            TaxiiClientError: If retrieving objects fails
        """
        retrieved_objects = []
        total_count = 0
        
        try:
            # Ensure we have an API root and collection ID
            if not self.feed_source.api_root or not self.feed_source.collection_id:
                self.get_collections()
            
            # Connect to the collection
            self.collection = Collection(
                f"{self.feed_source.api_root}collections/{self.feed_source.collection_id}/",
                verify=settings.TAXII_VERIFY_SSL,
                headers=self.headers
            )
            
            # Prepare filter parameters
            filter_kwargs = {}
            if added_after:
                filter_kwargs['added_after'] = added_after
            if types:
                filter_kwargs['type'] = types
            
            # Get objects with pagination
            for objects_page in as_pages(
                self.collection.get_objects,
                per_request=settings.TAXII_PAGE_SIZE,
                **filter_kwargs
            ):
                page_objects = objects_page.get('objects', [])
                retrieved_objects.extend(page_objects)
                total_count += len(page_objects)
                
                # Update log entry with progress
                if self.log_entry:
                    self.log_entry.objects_retrieved = total_count
                    self.log_entry.save(update_fields=['objects_retrieved'])
                
                # Stop if we've reached the maximum objects
                if max_objects and total_count >= max_objects:
                    retrieved_objects = retrieved_objects[:max_objects]
                    total_count = max_objects
                    break
            
            return retrieved_objects, total_count
            
        except TAXIIServiceException as e:
            error_msg = f"Failed to retrieve objects: {str(e)}"
            logger.error(error_msg)
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                self.log_entry.save()
            raise TaxiiClientError(error_msg)
    
    def consume_feed(self) -> Dict[str, Any]:
        """
        Consume threat intelligence from the configured feed source.
        
        This method orchestrates the full consumption process:
        1. Create a log entry
        2. Connect to the TAXII server
        3. Retrieve objects since last poll
        4. Update last poll time
        
        Returns:
            Dictionary with consumption results
            
        Raises:
            TaxiiClientError: If consumption fails
        """
        # Create log entry
        self.log_entry = FeedConsumptionLog.objects.create(
            feed_source=self.feed_source,
            status=FeedConsumptionLog.ConsumptionStatus.SUCCESS
        )
        
        try:
            # Determine time range for polling
            added_after = self.feed_source.last_poll_time if self.feed_source.last_poll_time else None
            
            # Retrieve objects
            objects, count = self._with_retry(
                self.get_objects,
                added_after=added_after,
                types=None  # Retrieve all types
            )
            
            # Update last poll time
            self.feed_source.last_poll_time = timezone.now()
            self.feed_source.save(update_fields=['last_poll_time'])
            
            # Update log entry
            self.log_entry.objects_retrieved = count
            self.log_entry.objects_processed = count
            self.log_entry.end_time = timezone.now()
            self.log_entry.save()
            
            return {
                'status': 'success',
                'feed_source': self.feed_source.name,
                'objects_retrieved': count,
                'poll_time': self.feed_source.last_poll_time
            }
            
        except TaxiiClientError as e:
            # Error already logged, just propagate
            raise
        except Exception as e:
            # Unexpected error
            error_msg = f"Unexpected error during feed consumption: {str(e)}"
            logger.exception(error_msg)
            
            if self.log_entry:
                self.log_entry.status = FeedConsumptionLog.ConsumptionStatus.FAILURE
                self.log_entry.add_error(error_msg)
                self.log_entry.end_time = timezone.now()
                self.log_entry.save()
                
            raise TaxiiClientError(error_msg)
