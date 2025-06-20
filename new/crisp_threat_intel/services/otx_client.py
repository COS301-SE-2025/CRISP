import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class OTXAPIError(Exception):
    """Custom exception for OTX API errors"""
    pass

class OTXClient:
    """
    Client for interacting with AlienVault OTX (Open Threat Exchange) API.
    Handles authentication, rate limiting, and data retrieval.
    
    This client is designed to work with the CRISP threat intelligence architecture.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OTX client with API key.
        
        Args:
            api_key: OTX API key. If not provided, will use environment variable
        """
        import os
        self.api_key = api_key or os.environ.get('OTX_API_KEY')
        if not self.api_key:
            raise ValueError("OTX API key is required. Set OTX_API_KEY environment variable or pass as parameter.")
        
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.headers = {
            'X-OTX-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'CRISP-ThreatIntel/1.0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting settings
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.last_request_time = None
        
        # Configuration
        self.config = {
            'batch_size': 50,
            'max_age_days': 30,
            'supported_indicator_types': [
                'IPv4', 'IPv6', 'domain', 'hostname', 'URL', 'URI',
                'FileHash-MD5', 'FileHash-SHA1', 'FileHash-SHA256',
                'email', 'Mutex', 'CVE'
            ]
        }
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the OTX client with custom settings.
        
        Args:
            config: Configuration dictionary
        """
        self.config.update(config)
        logger.debug(f"OTX client configured with: {config}")
    
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
    
    def get_pulses(self, modified_since: Optional[datetime] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get threat intelligence pulses from OTX.
        
        Args:
            modified_since: Only get pulses modified since this date
            limit: Maximum number of pulses to retrieve
            
        Returns:
            List of pulse dictionaries
        """
        if limit is None:
            limit = self.config['batch_size']
        
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
    
    def get_recent_indicators(self, types: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent indicators across all subscribed pulses.
        
        Args:
            types: List of indicator types to filter by
            limit: Maximum number of indicators to retrieve
            
        Returns:
            List of indicator dictionaries
        """
        if limit is None:
            limit = self.config['batch_size'] * 2  # More indicators than pulses
        
        if types is None:
            types = self.config['supported_indicator_types']
        
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
    
    def search_pulses(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for pulses matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching pulse dictionaries
        """
        if limit is None:
            limit = 20
        
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
    
    def get_pulse_by_id(self, pulse_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific pulse by its ID.
        
        Args:
            pulse_id: OTX pulse ID
            
        Returns:
            Pulse dictionary or None if not found
        """
        try:
            pulse = self.get_pulse_details(pulse_id)
            return pulse
        except OTXAPIError as e:
            if "404" in str(e):
                logger.warning(f"Pulse {pulse_id} not found")
                return None
            raise
    
    def get_recent_pulses_with_age_limit(self, days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent pulses within the specified age limit.
        
        Args:
            days_back: Number of days to look back (uses config default if None)
            
        Returns:
            List of pulse dictionaries
        """
        if days_back is None:
            days_back = self.config['max_age_days']
        
        since_date = datetime.now() - timedelta(days=days_back)
        return self.get_pulses(modified_since=since_date)
    
    def get_supported_indicator_types(self) -> List[str]:
        """
        Get list of supported indicator types.
        
        Returns:
            List of supported indicator types
        """
        return self.config['supported_indicator_types'].copy()
    
    def validate_indicator_type(self, indicator_type: str) -> bool:
        """
        Check if an indicator type is supported.
        
        Args:
            indicator_type: Type to validate
            
        Returns:
            True if supported, False otherwise
        """
        return indicator_type in self.config['supported_indicator_types']
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the OTX client usage.
        
        Returns:
            Statistics dictionary
        """
        try:
            user_info = self.get_user_info()
            recent_pulses = self.get_recent_pulses_with_age_limit(7)  # Last week
            
            stats = {
                'user': {
                    'username': user_info.get('username', 'Unknown'),
                    'member_since': user_info.get('member_since', 'Unknown'),
                    'follower_count': user_info.get('follower_count', 0),
                    'following_count': user_info.get('following_count', 0)
                },
                'recent_activity': {
                    'pulses_last_week': len(recent_pulses),
                    'total_indicators_last_week': sum(len(p.get('indicators', [])) for p in recent_pulses)
                },
                'configuration': self.config.copy()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get OTX statistics: {e}")
            return {'error': str(e)}