"""
TAXII Client Service for consuming TAXII 2.1 feeds.

This module provides a client for interacting with TAXII 2.1 servers
and retrieving threat intelligence objects.
"""
import time
import logging
import platform
import uuid
from typing import Dict, List, Optional, Tuple, Union, Callable, Any
from datetime import datetime

from django.utils import timezone
from django.conf import settings

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from requests.auth import HTTPBasicAuth
from taxii2client.v21 import Server, ApiRoot, Collection
from taxii2client.exceptions import TAXIIServiceException

from .models import ExternalFeedSource, FeedConsumptionLog
from .taxii_client import TaxiiClientError, TaxiiConnectionError, TaxiiAuthenticationError, TaxiiDataError

logger = logging.getLogger(__name__)

class TaxiiClient:
    """Client for interacting with TAXII 2.1 servers"""
    
    def __init__(self, feed_source: ExternalFeedSource):
        """
        Initialize the TAXII client with a feed source
        
        Args:
            feed_source: The ExternalFeedSource to connect to
        """
        self.feed_source = feed_source
        self.server = None
        self.api_root = None
        self.collection = None
        self.log_entry = None
        self.auth = None
        
        # Set up headers and authentication
        self.headers = {
            'Accept': 'application/taxii+json;version=2.1',
            'User-Agent': f'CRISP-TAXII-Client/{getattr(settings, "VERSION", "1.0.0")} (Python {platform.python_version()})'
        }
        
        # Apply authentication if configured
        auth_config = feed_source.get_auth_config()
        if auth_config:
            self._apply_authentication(auth_config)
    
    def _apply_authentication(self, auth_config: Dict):
        """
        Apply authentication to the client based on the auth type
        
        Args:
            auth_config: Dictionary containing auth configuration
        """
        auth_type = auth_config.get('type')
        
        if auth_type == 'api_key':
            header_name = auth_config.get('header_name', 'Authorization')
            self.headers[header_name] = auth_config.get('key')
        
        elif auth_type == 'jwt':
            token = auth_config.get('token', '')
            self.headers['Authorization'] = f'Bearer {token}'
        
        elif auth_type == 'basic':
            self.auth = (auth_config.get('username', ''), auth_config.get('password', ''))
    
    def discover(self) -> Dict:
        """
        Discover TAXII server capabilities and available API roots
        
        Returns:
            Dictionary containing server information and API roots
        """
        def _do_discover():
            server = Server(
                self.feed_source.discovery_url,
                verify=getattr(settings, 'TAXII_VERIFY_SSL', True),
                headers=self.headers,
                auth=self.auth
            )
            self.server = server
            
            # Extract API roots
            api_roots = [root.url for root in server.api_roots]
            
            # Save the first API root to the feed source if not already set
            if api_roots and not self.feed_source.api_root_url: # Corrected field name
                self.feed_source.api_root_url = api_roots[0]
                self.feed_source.save(update_fields=['api_root_url']) # Corrected field name
            
            return {
                'title': server.title,
                'description': server.description,
                'api_roots': api_roots
            }
        
        try:
            return self._with_retry(_do_discover)
        except Exception as e:
            error_msg = f"Failed to discover TAXII server: {str(e)}"
            logger.error(error_msg)
            
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                
            raise TaxiiClientError(error_msg) from e
    
    def get_collections(self) -> List[Dict]:
        """
        Get available collections from the API root
        
        Returns:
            List of dictionaries containing collection information
        """
        # If no API root is set, try to discover one
        if not self.feed_source.api_root_url: # Corrected field name
            discover_info = self.discover()
            if not self.feed_source.api_root_url and discover_info.get('api_roots'): # Corrected field name
                self.feed_source.api_root_url = discover_info['api_roots'][0]
                self.feed_source.save(update_fields=['api_root_url']) # Corrected field name
        
        def _do_get_collections():
            api_root = ApiRoot(
                self.feed_source.api_root_url, # Corrected field name
                verify=getattr(settings, 'TAXII_VERIFY_SSL', True),
                headers=self.headers,
                auth=self.auth
            )
            self.api_root = api_root
            
            collections = []
            for collection in api_root.collections:
                collections.append({
                    'id': collection.id,
                    'title': collection.title,
                    'description': collection.description,
                    'can_read': collection.can_read,
                    'can_write': collection.can_write,
                    'media_types': collection.media_types
                })
            
            # Save the first readable collection to the feed source if not already set
            readable_collections = [c for c in collections if c['can_read']]
            if readable_collections and not self.feed_source.collection_id:
                self.feed_source.collection_id = readable_collections[0]['id']
                self.feed_source.save(update_fields=['collection_id'])
            
            return collections
        
        try:
            return self._with_retry(_do_get_collections)
        except Exception as e:
            error_msg = f"Failed to get collections: {str(e)}"
            logger.error(error_msg)
            
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                
            raise TaxiiClientError(error_msg) from e
    
    def get_objects(self, added_after: Optional[datetime] = None, 
                   types: Optional[List[str]] = None,
                   max_objects: Optional[int] = None) -> Tuple[List[Dict], int]:
        """
        Get objects from the collection
        
        Args:
            added_after: Only get objects added after this time
            types: Only get objects of these types
            max_objects: Maximum number of objects to retrieve
        
        Returns:
            Tuple of (list of objects, count of objects)
        """
        if not self.feed_source.api_root_url or not self.feed_source.collection_id: # Corrected field name
            raise TaxiiClientError("API root or collection ID not set")
        
        def _do_get_objects():
            collection = Collection(
                f"{self.feed_source.api_root_url}collections/{self.feed_source.collection_id}/", # Corrected field name
                verify=getattr(settings, 'TAXII_VERIFY_SSL', True),
                headers=self.headers,
                auth=self.auth
            )
            self.collection = collection
            
            # Set up filters
            filters = {}
            if added_after:
                filters['added_after'] = added_after
            if types:
                filters['type'] = types
            
            # Get objects with pagination
            all_objects = []
            object_count = 0
            
            for envelope in collection.get_objects(**filters):
                if 'objects' in envelope:
                    objects = envelope['objects']
                    object_count += len(objects)
                    all_objects.extend(objects)
                    
                    # Check if we've hit the max limit
                    if max_objects and len(all_objects) >= max_objects:
                        all_objects = all_objects[:max_objects]
                        object_count = max_objects
                        break
            
            # Update the log with the number of objects retrieved
            if self.log_entry:
                self.log_entry.objects_retrieved = object_count
                self.log_entry.save(update_fields=['objects_retrieved'])
            
            return all_objects, object_count
        
        try:
            return self._with_retry(_do_get_objects)
        except Exception as e:
            error_msg = f"Failed to retrieve objects: {str(e)}"
            logger.error(error_msg)
            
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                
            raise TaxiiClientError(error_msg) from e
    
    def consume_feed(self) -> Dict:
        """
        Consume the feed and process the objects
        
        Returns:
            Dictionary with consumption results
        """
        # Create a log entry for this consumption
        self.log_entry = FeedConsumptionLog.objects.create(
            feed_source=self.feed_source,
            start_time=timezone.now(),
            status=FeedConsumptionLog.Status.PENDING  # Corrected Enum
        )
        
        try:
            # Get the last poll time or a default date
            last_poll = self.feed_source.last_poll_time or timezone.now() - timezone.timedelta(days=7)
            
            # Get objects from the feed
            objects, count = self.get_objects(added_after=last_poll)
            
            # Mark as success and update object count
            self.log_entry.status = FeedConsumptionLog.Status.COMPLETED # Corrected Enum
            self.log_entry.objects_retrieved = count
            self.log_entry.objects_processed = count
            self.log_entry.end_time = timezone.now()
            self.log_entry.save()
            
            # Update the feed source last poll time
            self.feed_source.last_poll_time = timezone.now()
            self.feed_source.save(update_fields=['last_poll_time'])
            
            # Return result dictionary
            return {
                'status': 'success',
                'feed_source': self.feed_source.name,
                'objects_retrieved': count,
                'poll_time': self.feed_source.last_poll_time,
                'objects': objects
            }
        except Exception as e:
            error_msg = f"Feed consumption failed: {str(e)}"
            logger.exception(error_msg)
            
            # Mark as failed
            self.log_entry.status = FeedConsumptionLog.Status.FAILED # Corrected Enum
            self.log_entry.error_message = error_msg
            self.log_entry.end_time = timezone.now()
            self.log_entry.save()
            
            raise TaxiiClientError(error_msg) from e
    
    def _with_retry(self, func: Callable, max_attempts: int = 3) -> Any:
        """
        Execute a function with retries for transient errors
        
        Args:
            func: Function to execute
            max_attempts: Maximum number of attempts
            
        Returns:
            Result of the function
        """
        attempt = 0
        last_error = None
        
        while attempt < max_attempts:
            try:
                return func()
            except (RequestException, TAXIIServiceException) as e:
                attempt += 1
                last_error = e
                
                # Check for specific error types
                if isinstance(e, (Timeout, ConnectionError)):
                    if attempt >= max_attempts:
                        error_msg = f"Connection error after {max_attempts} attempts: {str(e)}"
                        if self.log_entry:
                            self.log_entry.add_error(error_msg)
                        raise TaxiiConnectionError(error_msg) from e
                
                # Check for authentication errors
                if hasattr(e, 'response') and e.response and e.response.status_code == 401:
                    error_msg = f"Authentication failed: {str(e)}"
                    if self.log_entry:
                        self.log_entry.add_error(error_msg)
                    raise TaxiiAuthenticationError(error_msg) from e
                
                # For other errors, try again if we have attempts left
                if attempt < max_attempts:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Retry {attempt}/{max_attempts} in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    # Last attempt failed
                    error_msg = f"Failed after {max_attempts} attempts: {str(e)}"
                    if self.log_entry:
                        self.log_entry.add_error(error_msg)
                    raise TaxiiClientError(error_msg) from e
        
        # Should not reach here, but just in case
        raise TaxiiClientError(f"Unexpected error after {max_attempts} attempts: {last_error}")
