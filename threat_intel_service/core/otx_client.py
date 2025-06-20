import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class OTXAPIError(Exception):
    """Custom exception for OTX API errors"""
    pass

class OTXClient:
    """
    Client for interacting with AlienVault OTX (Open Threat Exchange) API.
    Handles authentication, rate limiting, and data retrieval.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OTX client with API key.
        
        Args:
            api_key: OTX API key. If not provided, will use settings.OTX_API_KEY
        """
        self.api_key = api_key or getattr(settings, 'OTX_API_KEY', None)
        if not self.api_key:
            raise ValueError("OTX API key is required. Set OTX_API_KEY in settings or pass as parameter.")
        
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.headers = {
            'X-OTX-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'ThreatIntelService/1.0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting settings
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.last_request_time = None
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to OTX API with rate limiting.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            OTXAPIError: If request fails
        """
        # Rate limiting
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                time_to_wait = self.rate_limit_delay - elapsed
                logger.debug(f"Rate limiting: waiting {time_to_wait:.2f} seconds")
                import time
                time.sleep(time_to_wait)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making OTX API request to: {url}")
            response = self.session.get(url, params=params, timeout=30)
            self.last_request_time = datetime.now()
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
                
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                raise OTXAPIError("Invalid API key or insufficient permissions")
            elif response.status_code == 429:
                raise OTXAPIError("Rate limit exceeded. Please try again later.")
            else:
                raise OTXAPIError(f"HTTP error {response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            raise OTXAPIError(f"Request failed: {e}")
        except ValueError as e:
            raise OTXAPIError(f"Invalid JSON response: {e}")
    
    def get_pulses(self, modified_since: Optional[datetime] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get threat intelligence pulses from OTX.
        
        Args:
            modified_since: Only get pulses modified since this date
            limit: Maximum number of pulses to retrieve (max 50 per request)
            
        Returns:
            List of pulse dictionaries
        """
        params = {'limit': min(limit, 50)}  # OTX API limit is 50
        
        if modified_since:
            # Convert to ISO format expected by OTX API
            params['modified_since'] = modified_since.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        try:
            response = self._make_request('/pulses/subscribed', params)
            pulses = response.get('results', [])
            logger.info(f"Retrieved {len(pulses)} pulses from OTX")
            return pulses
            
        except OTXAPIError as e:
            logger.error(f"Failed to retrieve pulses: {e}")
            raise
    
    def get_pulse_details(self, pulse_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific pulse.
        
        Args:
            pulse_id: OTX pulse ID
            
        Returns:
            Pulse details dictionary
        """
        try:
            response = self._make_request(f'/pulses/{pulse_id}')
            logger.debug(f"Retrieved pulse details for {pulse_id}")
            return response
            
        except OTXAPIError as e:
            logger.error(f"Failed to retrieve pulse details for {pulse_id}: {e}")
            raise
    
    def get_pulse_indicators(self, pulse_id: str) -> List[Dict[str, Any]]:
        """
        Get indicators from a specific pulse.
        
        Args:
            pulse_id: OTX pulse ID
            
        Returns:
            List of indicator dictionaries
        """
        try:
            response = self._make_request(f'/pulses/{pulse_id}/indicators')
            indicators = response.get('results', [])
            logger.debug(f"Retrieved {len(indicators)} indicators for pulse {pulse_id}")
            return indicators
            
        except OTXAPIError as e:
            logger.error(f"Failed to retrieve indicators for pulse {pulse_id}: {e}")
            raise
    
    def get_recent_indicators(self, types: Optional[List[str]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent indicators across all subscribed pulses.
        
        Args:
            types: List of indicator types to filter by (e.g., ['IPv4', 'domain', 'URL'])
            limit: Maximum number of indicators to retrieve
            
        Returns:
            List of indicator dictionaries
        """
        params = {'limit': limit}
        
        if types:
            params['types'] = ','.join(types)
        
        try:
            response = self._make_request('/indicators/export', params)
            indicators = response.get('results', [])
            logger.info(f"Retrieved {len(indicators)} recent indicators")
            return indicators
            
        except OTXAPIError as e:
            logger.error(f"Failed to retrieve recent indicators: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test connection to OTX API and validate API key.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get user info to test authentication
            self._make_request('/user/me')
            logger.info("OTX API connection test successful")
            return True
            
        except OTXAPIError as e:
            logger.error(f"OTX API connection test failed: {e}")
            return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            User information dictionary
        """
        try:
            response = self._make_request('/user/me')
            logger.debug("Retrieved OTX user information")
            return response
            
        except OTXAPIError as e:
            logger.error(f"Failed to retrieve user info: {e}")
            raise
    
    def search_pulses(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for pulses matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching pulse dictionaries
        """
        params = {
            'q': query,
            'limit': limit
        }
        
        try:
            response = self._make_request('/search/pulses', params)
            pulses = response.get('results', [])
            logger.info(f"Found {len(pulses)} pulses matching query: {query}")
            return pulses
            
        except OTXAPIError as e:
            logger.error(f"Failed to search pulses for query '{query}': {e}")
            raise