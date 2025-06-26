"""
AlienVault OTX Integration Service
Complete OTX client and processor implementation.
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import stix2
from stix2 import Report, Bundle, Indicator, Identity
from dateutil.parser import isoparse

from core.models.stix_object import STIXObject, Collection, CollectionObject
from core.models import Organization
from core.patterns.factory.stix_object_creator import STIXObjectCreator as STIXObjectFactory

logger = logging.getLogger(__name__)


class OTXAPIError(Exception):
    """Custom exception for OTX API errors"""
    pass


def _clean_and_parse_timestamp(timestamp_str: str) -> datetime:
    """
    Safely converts an ISO format string from OTX to a timezone-aware datetime object
    using the robust dateutil.parser.
    """
    if not timestamp_str:
        return timezone.now()
    try:
        # isoparse is very flexible and handles various ISO 8601 formats,
        # including 'Z' suffix and variable-length fractional seconds.
        dt = isoparse(timestamp_str)
        # Ensure the datetime object is timezone-aware for consistency
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse timestamp '{timestamp_str}' with dateutil: {e}. Using current time.")
        return timezone.now()


class OTXClient:
    """
    Client for interacting with AlienVault OTX (Open Threat Exchange) API.
    Handles authentication, rate limiting, and data retrieval.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OTX client with API key.
        
        Args:
            api_key: OTX API key. If not provided, will use settings.OTX_SETTINGS['API_KEY']
        """
        self.api_key = api_key or settings.OTX_SETTINGS.get('API_KEY')
        if not self.api_key:
            raise ValueError("OTX API key is required. Set OTX_API_KEY in settings or pass as parameter.")
        
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
        """Get user information"""
        return self._make_request('user/me')


class OTXProcessor:
    """
    Processes OTX threat intelligence data and converts it to STIX format.
    """
    
    def __init__(self, organization: Organization, collection: Collection):
        self.organization = organization
        self.collection = collection
        self.client = OTXClient(settings.OTX_SETTINGS.get('API_KEY'))

    def convert_otx_pulse_to_stix(self, pulse: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert an OTX pulse to STIX objects.
        
        Args:
            pulse: OTX pulse data
            
        Returns:
            List of STIX objects created from the pulse
        """
        stix_objects = []
        
        try:
            # The current factory does not support 'report' objects, which causes errors.
            # We will skip creating a report and only process the indicators from the pulse.
            
            # Process indicators from the pulse
            indicators = pulse.get('indicators', [])
            
            for indicator_data in indicators:
                stix_indicator = self._convert_otx_indicator_to_stix(indicator_data, pulse)
                if stix_indicator:
                    stix_objects.append(stix_indicator)
            
            if stix_objects:
                logger.info(f"Converted {len(stix_objects)} indicators from OTX pulse '{pulse.get('name')}'")
            
        except Exception as e:
            logger.error(f"Error converting OTX pulse to STIX: {e}")
            
        return stix_objects

    def _convert_otx_indicator_to_stix(self, indicator: Dict[str, Any], pulse: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert an OTX indicator to a STIX indicator.
        
        Args:
            indicator: OTX indicator data
            pulse: Parent pulse data for context
            
        Returns:
            STIX Indicator object or None if conversion fails
        """
        try:
            indicator_type = indicator.get('type', '').lower()
            indicator_value = indicator.get('indicator', '')
            
            if not indicator_value:
                logger.warning("Skipping indicator with no value")
                return None
            
            # Create STIX pattern based on indicator type
            pattern = self._create_stix_pattern(indicator_type, indicator_value)
            if not pattern:
                logger.warning(f"Could not create STIX pattern for indicator type: {indicator_type}")
                return None
            
            # Prepare indicator data
            indicator_data = {
                'pattern': pattern,
                'pattern_type': 'stix',
                'valid_from': pulse.get('created', timezone.now().isoformat()),
                'labels': ['malicious-activity'],
                'description': f"Indicator from OTX pulse: {pulse.get('name', 'Unknown')}",
            }
            
            # Add confidence if available
            if indicator.get('confidence'):
                indicator_data['confidence'] = indicator['confidence']
            
            # Add external references
            indicator_data['external_references'] = [
                {
                    'source_name': 'AlienVault OTX',
                    'url': f"https://otx.alienvault.com/pulse/{pulse.get('id', '')}"
                }
            ]
            
            # Create STIX indicator using factory
            stix_indicator = STIXObjectFactory.create_object('indicator', indicator_data)
            return stix_indicator
            
        except Exception as e:
            logger.error(f"Error converting OTX indicator to STIX: {e}")
            return None
    
    def _create_stix_pattern(self, indicator_type: str, value: str) -> Optional[str]:
        """
        Create a STIX pattern from OTX indicator type and value.
        
        Args:
            indicator_type: OTX indicator type
            value: Indicator value
            
        Returns:
            STIX pattern string or None if type not supported
        """
        # Mapping of OTX types to STIX patterns
        pattern_mapping = {
            'ipv4': f"[ipv4-addr:value = '{value}']",
            'ipv6': f"[ipv6-addr:value = '{value}']",
            'domain': f"[domain-name:value = '{value}']",
            'hostname': f"[domain-name:value = '{value}']",
            'url': f"[url:value = '{value}']",
            'uri': f"[url:value = '{value}']",
            'filehash-md5': f"[file:hashes.MD5 = '{value}']",
            'filehash-sha1': f"[file:hashes.SHA1 = '{value}']",
            'filehash-sha256': f"[file:hashes.SHA256 = '{value}']",
            'email': f"[email-addr:value = '{value}']",
            'mutex': f"[mutex:name = '{value}']",
            'cve': f"[vulnerability:name = '{value}']",
        }
        
        return pattern_mapping.get(indicator_type.lower())
    
    def process_otx_pulses(self, pulses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple OTX pulses and store as STIX objects.
        
        Args:
            pulses: List of OTX pulse data
            
        Returns:
            Processing results summary
        """
        results = {
            'total_pulses': len(pulses),
            'processed_pulses': 0,
            'created_objects': 0,
            'errors': []
        }
        
        for pulse in pulses:
            try:
                with transaction.atomic():
                    # Convert pulse to STIX objects
                    stix_objects = self.convert_otx_pulse_to_stix(pulse)
                    
                    # Store STIX objects in database
                    for stix_obj in stix_objects:
                        db_obj = self._store_stix_object(stix_obj)
                        if db_obj:
                            # Add to collection
                            CollectionObject.objects.get_or_create(
                                collection=self.collection,
                                stix_object=db_obj
                            )
                            results['created_objects'] += 1
                    
                    results['processed_pulses'] += 1
                    
            except Exception as e:
                error_msg = f"Error processing pulse '{pulse.get('name', 'Unknown')}': {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        logger.info(f"OTX processing complete. Processed {results['processed_pulses']}/{results['total_pulses']} pulses, "
                   f"created {results['created_objects']} objects")
        
        return results
    
    def _store_stix_object(self, stix_obj: Dict[str, Any]) -> Optional[STIXObject]:
        """
        Store a STIX object in the database.
        
        Args:
            stix_obj: STIX object dictionary to store
            
        Returns:
            Created STIXObject instance or None if creation fails
        """
        try:
            # Check if object already exists
            if STIXObject.objects.filter(stix_id=stix_obj['id']).exists():
                logger.debug(f"STIX object {stix_obj['id']} already exists, skipping")
                return None
            
            # Create database object
            db_obj = STIXObject(
                stix_id=stix_obj['id'],
                stix_type=stix_obj['type'],
                spec_version=stix_obj.get('spec_version', '2.1'),
                created=_clean_and_parse_timestamp(stix_obj['created']),
                modified=_clean_and_parse_timestamp(stix_obj['modified']),
                created_by_ref=stix_obj.get('created_by_ref', ''),
                revoked=stix_obj.get('revoked', False),
                labels=stix_obj.get('labels', []),
                confidence=stix_obj.get('confidence', 0),
                external_references=stix_obj.get('external_references', []),
                object_marking_refs=stix_obj.get('object_marking_refs', []),
                granular_markings=stix_obj.get('granular_markings', []),
                raw_data=stix_obj,
                source_organization=self.organization,
            )
            
            db_obj.save()
            logger.debug(f"Stored STIX object: {stix_obj['id']}")
            return db_obj
            
        except Exception as e:
            logger.error(f"Error storing STIX object: {e}")
            return None
    
    def fetch_and_process_recent_pulses(self, days_back: int = 1) -> Dict[str, Any]:
        """
        Fetch recent pulses from OTX and process them.
        
        Args:
            days_back: Number of days back to fetch pulses
            
        Returns:
            Processing results summary
        """
        try:
            # Calculate date threshold
            since_date = timezone.now() - timedelta(days=days_back)
            
            # Fetch pulses from OTX
            logger.info(f"Fetching OTX pulses modified since {since_date}")
            pulses = self.client.get_pulses(
                modified_since=since_date,
                limit=settings.OTX_SETTINGS.get('BATCH_SIZE', 50)
            )
            
            # Process the pulses
            results = self.process_otx_pulses(pulses)
            
            return results
            
        except OTXAPIError as e:
            logger.error(f"OTX API error: {e}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error processing OTX feeds: {e}")
            return {'error': str(e)}


class OTXService:
    """
    High-level OTX service for managing OTX integration.
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.OTX_SETTINGS.get('API_KEY')
        self.client = OTXClient(self.api_key)
    
    def fetch_recent_indicators(self, days_back=7):
        """Fetch recent indicators from OTX"""
        try:
            since_date = timezone.now() - timedelta(days=days_back)
            pulses = self.client.get_pulses(modified_since=since_date)
            return pulses
        except OTXAPIError as e:
            logger.error(f"Failed to fetch OTX indicators: {e}")
            return []
    
    def convert_to_stix(self, otx_data, organization):
        """Convert OTX data to STIX objects"""
        # This would use the processor
        pass
        
    def publish_to_collection(self, collection, days_back=7):
        """Fetch OTX data and publish to collection"""
        try:
            processor = OTXProcessor(collection.owner, collection)
            return processor.fetch_and_process_recent_pulses(days_back)
        except Exception as e:
            logger.error(f"Failed to publish OTX data to collection: {e}")
            return {'error': str(e)}