import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..domain.models import Institution, ThreatFeed, User, Indicator, TTPData
from ..repositories.threat_feed_repository import ThreatFeedRepository
from .otx_client import OTXClient, OTXAPIError
from .otx_processor import OTXProcessor
from .threat_feed_service import ThreatFeedService

logger = logging.getLogger(__name__)

class OTXIntegrationError(Exception):
    """Custom exception for OTX integration errors"""
    pass

class OTXService:
    """
    High-level service for OTX integration with the CRISP threat intelligence platform.
    
    This service orchestrates the fetching, processing, and storage of OTX threat data
    using the new architecture's domain models, repositories, and services.
    """
    
    def __init__(self):
        """Initialize the OTX service with required dependencies."""
        self.client = OTXClient()
        self.threat_feed_service = ThreatFeedService()
        self.threat_feed_repository = ThreatFeedRepository()
        
        # Default configuration
        self.config = {
            'enabled': True,
            'fetch_interval': 3600,  # 1 hour
            'batch_size': 50,
            'max_age_days': 30,
            'indicator_types': [
                'IPv4', 'IPv6', 'domain', 'hostname', 'URL', 'URI',
                'FileHash-MD5', 'FileHash-SHA1', 'FileHash-SHA256',
                'email', 'Mutex', 'CVE'
            ],
            'auto_create_feed': True,
            'feed_name_template': 'OTX Feed - {institution_name}',
            'feed_description_template': 'AlienVault OTX threat intelligence for {institution_name}'
        }
        
        # Statistics tracking
        self.stats = {
            'last_fetch_time': None,
            'total_fetches': 0,
            'successful_fetches': 0,
            'failed_fetches': 0,
            'total_indicators_processed': 0,
            'total_ttps_processed': 0,
            'errors': []
        }
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the OTX service.
        
        Args:
            config: Configuration dictionary
        """
        self.config.update(config)
        
        # Configure the client with relevant settings
        client_config = {
            'batch_size': self.config.get('batch_size', 50),
            'max_age_days': self.config.get('max_age_days', 30),
            'supported_indicator_types': self.config.get('indicator_types', [])
        }
        self.client.configure(client_config)
        
        logger.info(f"OTX service configured with: {config}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to OTX API.
        
        Returns:
            Connection test results
        """
        try:
            if self.client.test_connection():
                user_info = self.client.get_user_info()
                stats = self.client.get_statistics()
                
                return {
                    'status': 'success',
                    'message': 'OTX connection successful',
                    'user_info': user_info,
                    'client_stats': stats
                }
            else:
                return {
                    'status': 'error',
                    'message': 'OTX connection failed'
                }
        except Exception as e:
            logger.error(f"OTX connection test failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def setup_otx_feed_for_institution(self, institution: Institution, user: User, 
                                     custom_config: Optional[Dict[str, Any]] = None) -> ThreatFeed:
        """
        Set up an OTX threat feed for an institution.
        
        Args:
            institution: Institution to create feed for
            user: User creating the feed
            custom_config: Custom feed configuration
            
        Returns:
            Created threat feed
        """
        try:
            with transaction.atomic():
                # Check if OTX feed already exists for this institution
                existing_feeds = self.threat_feed_repository.get_by_institution(institution)
                otx_feed = None
                
                for feed in existing_feeds:
                    if 'otx' in feed.name.lower():
                        otx_feed = feed
                        logger.info(f"Found existing OTX feed for {institution.name}: {feed.name}")
                        break
                
                if not otx_feed:
                    # Create new OTX feed
                    feed_data = {
                        'name': self.config['feed_name_template'].format(institution_name=institution.name),
                        'description': self.config['feed_description_template'].format(institution_name=institution.name),
                        'query_parameters': {
                            'source': 'alienvault_otx',
                            'indicator_types': self.config['indicator_types'],
                            'max_age_days': self.config['max_age_days']
                        },
                        'update_interval': self.config['fetch_interval']
                    }
                    
                    # Apply custom configuration if provided
                    if custom_config:
                        feed_data.update(custom_config)
                    
                    otx_feed = self.threat_feed_service.create_threat_feed(
                        institution=institution,
                        user=user,
                        feed_data=feed_data
                    )
                    
                    logger.info(f"Created new OTX feed for {institution.name}: {otx_feed.name}")
                
                return otx_feed
                
        except Exception as e:
            logger.error(f"Failed to setup OTX feed for {institution.name}: {e}")
            raise OTXIntegrationError(f"Failed to setup OTX feed: {e}")
    
    def fetch_and_process_otx_data(self, institution: Institution, user: User, 
                                 days_back: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch and process OTX data for an institution.
        
        Args:
            institution: Institution to fetch data for
            user: User performing the fetch
            days_back: Number of days to look back (uses config default if None)
            
        Returns:
            Processing results
        """
        if not self.config.get('enabled', True):
            return {
                'status': 'disabled',
                'message': 'OTX integration is disabled'
            }
        
        try:
            self.stats['total_fetches'] += 1
            self.stats['last_fetch_time'] = timezone.now()
            
            # Get or create OTX feed for the institution
            threat_feed = self.setup_otx_feed_for_institution(institution, user)
            
            # Initialize processor
            processor = OTXProcessor(institution, threat_feed)
            processor.configure_client({
                'batch_size': self.config.get('batch_size', 50),
                'max_age_days': self.config.get('max_age_days', 30)
            })
            
            # Fetch and process data
            if days_back is None:
                days_back = self.config.get('max_age_days', 7)
            
            results = processor.fetch_and_process_recent_pulses(days_back, user)
            
            if 'error' in results:
                self.stats['failed_fetches'] += 1
                self.stats['errors'].append(f"Fetch failed for {institution.name}: {results['error']}")
                return {
                    'status': 'error',
                    'message': results['error'],
                    'institution': institution.name,
                    'threat_feed': threat_feed.name
                }
            
            # Update statistics
            self.stats['successful_fetches'] += 1
            self.stats['total_indicators_processed'] += results.get('created_indicators', 0)
            self.stats['total_ttps_processed'] += results.get('created_ttps', 0)
            
            # Update threat feed metadata
            threat_feed.last_published_time = timezone.now()
            threat_feed.publish_count += 1
            threat_feed.save()
            
            # Notify observers
            threat_feed.notify_observers('otx_update', {
                'source': 'otx_service',
                'results': results,
                'user': user.django_user.username
            })
            
            logger.info(f"Successfully processed OTX data for {institution.name}: {results}")
            
            return {
                'status': 'success',
                'institution': institution.name,
                'threat_feed': threat_feed.name,
                'results': results,
                'processing_stats': processor.get_processing_statistics()
            }
            
        except OTXAPIError as e:
            self.stats['failed_fetches'] += 1
            error_msg = f"OTX API error for {institution.name}: {e}"
            self.stats['errors'].append(error_msg)
            logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }
        except Exception as e:
            self.stats['failed_fetches'] += 1
            error_msg = f"Unexpected error processing OTX data for {institution.name}: {e}"
            self.stats['errors'].append(error_msg)
            logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }
    
    def fetch_otx_data_for_all_institutions(self, user: User) -> List[Dict[str, Any]]:
        """
        Fetch OTX data for all institutions that have OTX feeds.
        
        Args:
            user: User performing the fetch
            
        Returns:
            List of processing results for each institution
        """
        results = []
        
        # Get all institutions that have threat feeds
        all_feeds = self.threat_feed_repository.get_all()
        otx_institutions = set()
        
        for feed in all_feeds:
            if 'otx' in feed.name.lower():
                otx_institutions.add(feed.institution)
        
        logger.info(f"Found {len(otx_institutions)} institutions with OTX feeds")
        
        for institution in otx_institutions:
            try:
                result = self.fetch_and_process_otx_data(institution, user)
                results.append(result)
            except Exception as e:
                error_result = {
                    'status': 'error',
                    'institution': institution.name,
                    'message': str(e)
                }
                results.append(error_result)
                logger.error(f"Failed to process OTX data for {institution.name}: {e}")
        
        return results
    
    def search_otx_pulses(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search OTX pulses.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching pulses
        """
        try:
            return self.client.search_pulses(query, limit)
        except OTXAPIError as e:
            logger.error(f"OTX pulse search failed: {e}")
            raise OTXIntegrationError(f"Pulse search failed: {e}")
    
    def get_otx_pulse_details(self, pulse_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific OTX pulse.
        
        Args:
            pulse_id: OTX pulse ID
            
        Returns:
            Pulse details
        """
        try:
            return self.client.get_pulse_details(pulse_id)
        except OTXAPIError as e:
            logger.error(f"Failed to get OTX pulse details: {e}")
            raise OTXIntegrationError(f"Failed to get pulse details: {e}")
    
    def import_specific_otx_pulse(self, pulse_id: str, institution: Institution, 
                                user: User) -> Dict[str, Any]:
        """
        Import a specific OTX pulse.
        
        Args:
            pulse_id: OTX pulse ID to import
            institution: Institution to import for
            user: User performing the import
            
        Returns:
            Import results
        """
        try:
            # Get pulse details
            pulse = self.client.get_pulse_by_id(pulse_id)
            if not pulse:
                return {
                    'status': 'error',
                    'message': f'Pulse {pulse_id} not found'
                }
            
            # Get or create threat feed
            threat_feed = self.setup_otx_feed_for_institution(institution, user)
            
            # Process the pulse
            processor = OTXProcessor(institution, threat_feed)
            results = processor.process_otx_pulses([pulse], user)
            
            logger.info(f"Imported OTX pulse {pulse_id} for {institution.name}")
            
            return {
                'status': 'success',
                'pulse_id': pulse_id,
                'pulse_name': pulse.get('name', 'Unknown'),
                'institution': institution.name,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed to import OTX pulse {pulse_id}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_otx_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive OTX service statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            client_stats = self.client.get_statistics()
            
            return {
                'service_stats': self.stats.copy(),
                'client_stats': client_stats,
                'configuration': self.config.copy(),
                'connection_status': self.test_connection()
            }
        except Exception as e:
            logger.error(f"Failed to get OTX statistics: {e}")
            return {
                'error': str(e),
                'service_stats': self.stats.copy(),
                'configuration': self.config.copy()
            }
    
    def reset_statistics(self) -> None:
        """Reset service statistics."""
        self.stats = {
            'last_fetch_time': None,
            'total_fetches': 0,
            'successful_fetches': 0,
            'failed_fetches': 0,
            'total_indicators_processed': 0,
            'total_ttps_processed': 0,
            'errors': []
        }
        logger.info("OTX service statistics reset")
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the current OTX service configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required configuration
        if not self.config.get('enabled'):
            return ['OTX integration is disabled']
        
        # Check API key
        try:
            if not self.client.test_connection():
                errors.append("OTX API connection failed - check API key")
        except Exception as e:
            errors.append(f"OTX API connection error: {e}")
        
        # Validate configuration values
        if self.config.get('fetch_interval', 0) < 60:
            errors.append("Fetch interval must be at least 60 seconds")
        
        if self.config.get('batch_size', 0) <= 0 or self.config.get('batch_size', 0) > 50:
            errors.append("Batch size must be between 1 and 50")
        
        if self.config.get('max_age_days', 0) <= 0:
            errors.append("Max age days must be greater than 0")
        
        # Check indicator types
        indicator_types = self.config.get('indicator_types', [])
        if not indicator_types:
            errors.append("At least one indicator type must be configured")
        
        supported_types = self.client.get_supported_indicator_types()
        for itype in indicator_types:
            if itype not in supported_types:
                errors.append(f"Unsupported indicator type: {itype}")
        
        return errors
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def is_enabled(self) -> bool:
        """Check if OTX integration is enabled."""
        return self.config.get('enabled', False)