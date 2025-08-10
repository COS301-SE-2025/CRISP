import logging
from typing import Union
from urllib.parse import urlparse

from core.services.otx_taxii_service import OTXTaxiiService
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)


class TaxiiServiceFactory:
    """
    Factory for creating appropriate TAXII service instances based on feed configuration.
    """
    
    @classmethod
    def create_service(cls, threat_feed):
        """
        Create appropriate TAXII service based on feed type.
        
        Args:
            threat_feed: ThreatFeed model instance or dict with feed configuration
            
        Returns:
            Appropriate TAXII service instance
            
        Raises:
            ValueError: If feed type cannot be determined or is unsupported
        """
        # Extract server URL for analysis
        if hasattr(threat_feed, 'taxii_server_url'):
            server_url = threat_feed.taxii_server_url
        elif isinstance(threat_feed, dict):
            server_url = threat_feed.get('taxii_server_url')
        else:
            raise ValueError("threat_feed must be ThreatFeed instance or dict")
        
        if not server_url:
            raise ValueError("No TAXII server URL provided")
        
        # Determine service type based on URL
        if cls._is_otx_feed(server_url):
            logger.info(f"Creating OTXTaxiiService for URL: {server_url}")
            return OTXTaxiiService()
        else:
            logger.info(f"Creating StixTaxiiService for URL: {server_url}")
            return StixTaxiiService()
    
    @classmethod
    def _is_otx_feed(cls, server_url: str) -> bool:
        """
        Determine if this is an OTX feed based on URL.
        
        Args:
            server_url: TAXII server URL
            
        Returns:
            True if this is an OTX feed
        """
        if not server_url:
            return False
        
        # Parse URL to get domain
        try:
            parsed = urlparse(server_url)
            domain = parsed.netloc.lower()
            
            # Check for OTX/AlienVault indicators
            otx_indicators = [
                'otx.alienvault.com',
                'alienvault.com',
                'otx.cymru.com'  # Add other OTX-style domains if needed
            ]
            
            return any(indicator in domain for indicator in otx_indicators)
            
        except Exception as e:
            logger.warning(f"Error parsing URL {server_url}: {e}")
            return False
    
    @classmethod
    def get_supported_service_types(cls) -> list:
        """
        Get list of supported service types.
        
        Returns:
            List of supported service type names
        """
        return ['otx', 'stix']
    
    @classmethod
    def create_service_by_type(cls, service_type: str):
        """
        Create service by explicit type.
        
        Args:
            service_type: 'otx' or 'stix'
            
        Returns:
            Appropriate TAXII service instance
            
        Raises:
            ValueError: If service type is not supported
        """
        if service_type.lower() == 'otx':
            return OTXTaxiiService()
        elif service_type.lower() == 'stix':
            return StixTaxiiService()
        else:
            raise ValueError(f"Unsupported service type: {service_type}. Must be 'otx' or 'stix'")


def get_taxii_service(threat_feed):
    """
    Convenience function to get appropriate TAXII service.
    
    Args:
        threat_feed: ThreatFeed model instance or dict with feed configuration
        
    Returns:
        Appropriate TAXII service instance
    """
    return TaxiiServiceFactory.create_service(threat_feed)