"""TAXII 2.1 client implementation for feed consumption"""
import logging
from typing import Dict, List, Optional, Union
import requests
from requests.auth import HTTPBasicAuth
from taxii2client.v21 import Server, ApiRoot, Collection, as_pages
from django.conf import settings

logger = logging.getLogger(__name__)

class TaxiiClient:
    """TAXII 2.1 Client for retrieving threat intelligence from external sources"""
    
    def __init__(self, discovery_url: str, auth_type: str = None, auth_credentials: Dict = None, 
                headers: Dict = None, verify_ssl: bool = None):
        """
        Initialize TAXII client
        
        Args:
            discovery_url: The TAXII discovery endpoint URL
            auth_type: Authentication type (none, basic, api_key, jwt)
            auth_credentials: Authentication credentials as dict
            headers: Additional HTTP headers to include
            verify_ssl: Whether to verify SSL certificates
        """
        self.discovery_url = discovery_url
        self.auth_type = auth_type
        self.auth_credentials = auth_credentials or {}
        self.headers = headers or {}
        
        # Default verify_ssl to settings value if not explicitly provided
        if verify_ssl is None:
            self.verify_ssl = getattr(settings, 'TAXII_VERIFY_SSL', True)
        else:
            self.verify_ssl = verify_ssl
            
        # Always set User-Agent
        version = getattr(settings, 'CRISP_VERSION', '1.0.0')
        self.headers['User-Agent'] = f'CRISP-TAXII-Client/{version}'
    
    def _get_auth(self):
        """Get authentication based on auth_type"""
        if not self.auth_type or self.auth_type == 'none':
            return None
            
        if self.auth_type == 'basic':
            return HTTPBasicAuth(
                self.auth_credentials.get('username', ''),
                self.auth_credentials.get('password', '')
            )
        
        return None
    
    def _prepare_headers(self):
        """Prepare request headers with authentication"""
        headers = self.headers.copy()
        
        # Add API key to headers if that's the auth type
        if self.auth_type == 'api_key' and self.auth_credentials:
            key_value = self.auth_credentials.get('key', '')
            header_name = self.auth_credentials.get('header_name', 'Authorization')
            headers[header_name] = key_value
            
        # Add JWT token if that's the auth type
        if self.auth_type == 'jwt' and self.auth_credentials:
            token = self.auth_credentials.get('token', '')
            headers['Authorization'] = f'Bearer {token}'
            
        return headers
    
    def get_discovery(self) -> Dict:
        """
        Perform TAXII discovery to get API roots
        
        Returns:
            Dictionary containing discovery information
        """
        try:
            server = Server(
                url=self.discovery_url,
                auth=self._get_auth(),
                verify=self.verify_ssl,
                headers=self._prepare_headers()
            )
            
            # Access the server property to ensure connection works
            # and discovery endpoint can be reached
            title = server.title
            
            return {
                'title': server.title,
                'description': server.description,
                'api_roots': [api_root for api_root in server.api_roots],
                'default_api_root': server.default
            }
        except Exception as e:
            logger.error(f"TAXII discovery failed: {str(e)}")
            raise
    
    def get_api_root(self, api_root_url: str) -> Dict:
        """
        Get information about an API root
        
        Args:
            api_root_url: The URL of the API root
            
        Returns:
            Dictionary with API root information
        """
        try:
            api_root = ApiRoot(
                url=api_root_url,
                auth=self._get_auth(),
                verify=self.verify_ssl,
                headers=self._prepare_headers()
            )
            
            return {
                'title': api_root.title,
                'description': api_root.description,
                'max_content_length': api_root.max_content_length,
                'versions': api_root.versions
            }
        except Exception as e:
            logger.error(f"Failed to get API root info: {str(e)}")
            raise
    
    def get_collections(self, api_root_url: str) -> List[Dict]:
        """
        Get available collections from an API root
        
        Args:
            api_root_url: The URL of the API root
            
        Returns:
            List of collections
        """
        try:
            api_root = ApiRoot(
                url=api_root_url,
                auth=self._get_auth(),
                verify=self.verify_ssl,
                headers=self._prepare_headers()
            )
            
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
            
            return collections
        except Exception as e:
            logger.error(f"Failed to get collections: {str(e)}")
            raise
    
    def get_objects(self, api_root_url: str, collection_id: str, params: Dict = None) -> List:
        """
        Get objects from a collection
        
        Args:
            api_root_url: The URL of the API root
            collection_id: ID of the collection
            params: Additional filter parameters
            
        Returns:
            List of STIX objects
        """
        try:
            collection = Collection(
                url=f"{api_root_url}/collections/{collection_id}/",
                auth=self._get_auth(),
                verify=self.verify_ssl,
                headers=self._prepare_headers()
            )
            
            filters = params or {}
            page_size = getattr(settings, 'TAXII_PAGE_SIZE', 100)
            
            all_objects = []
            for envelope in as_pages(collection.get_objects, per_request=page_size, **filters):
                # Extract objects from the envelope and add to our list
                if hasattr(envelope, 'objects') and envelope.objects:
                    all_objects.extend(envelope.objects)
            
            return all_objects
        except Exception as e:
            logger.error(f"Failed to get objects: {str(e)}")
            raise
