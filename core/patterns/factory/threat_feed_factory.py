"""
Threat Feed Factory Pattern Implementation
Following CRISP design specification for threat feed creation.
"""
from typing import Dict, Any, Optional
import uuid
from django.utils import timezone
from core.patterns.factory.stix_factory import StixObjectCreator
import logging

logger = logging.getLogger(__name__)


class ThreatFeedFactory(StixObjectCreator):
    """
    Concrete factory for creating STIX objects from threat feeds.
    Implements the Factory pattern for threat feed to STIX conversion.
    """
    
    def create_object(self, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX object from threat feed data.
        
        Args:
            data: Threat feed data dictionary
            spec_version: STIX specification version (2.0 or 2.1)
            
        Returns:
            STIX object dictionary representing the threat feed
        """
        try:
            # Create base STIX object for threat feed
            stix_obj = {
                "type": "grouping",
                "id": f"grouping--{uuid.uuid4()}",
                "spec_version": spec_version,
                "name": data.get("name", "Unknown Threat Feed"),
                "description": data.get("description", ""),
                "context": "threat-feed",
                "object_refs": data.get("object_refs", []),
                "labels": data.get("labels", ["threat-feed"]),
                "external_references": self._create_external_references(data),
                "x_feed_metadata": self._create_feed_metadata(data)
            }
            
            # Ensure common STIX properties
            stix_obj = self._ensure_common_properties(stix_obj, spec_version)
            
            logger.info(f"Created STIX grouping object for threat feed: {data.get('name', 'Unknown')}")
            return stix_obj
            
        except Exception as e:
            logger.error(f"Failed to create STIX object from threat feed data: {str(e)}")
            raise
    
    def _create_external_references(self, data: Dict[str, Any]) -> list:
        """
        Create external references for the threat feed.
        
        Args:
            data: Threat feed data dictionary
            
        Returns:
            List of external reference objects
        """
        external_refs = []
        
        # Add TAXII server reference if available
        if data.get("taxii_server_url"):
            external_refs.append({
                "source_name": "TAXII Server",
                "url": data["taxii_server_url"],
                "description": f"TAXII server hosting this threat feed"
            })
        
        # Add collection reference if available
        if data.get("taxii_collection_id"):
            external_refs.append({
                "source_name": "TAXII Collection",
                "external_id": data["taxii_collection_id"],
                "description": f"TAXII collection ID for this threat feed"
            })
        
        return external_refs
    
    def _create_feed_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create custom metadata for the threat feed.
        
        Args:
            data: Threat feed data dictionary
            
        Returns:
            Dictionary containing feed-specific metadata
        """
        metadata = {
            "feed_id": data.get("id"),
            "is_public": data.get("is_public", False),
            "is_external": data.get("is_external", False),
            "owner_organization": data.get("owner_organization"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "last_sync": data.get("last_sync")
        }
        
        # Add TAXII configuration if available
        if data.get("taxii_api_root"):
            metadata["taxii_api_root"] = data["taxii_api_root"]
        
        return {k: v for k, v in metadata.items() if v is not None}
    
    def create_collection_object(self, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX collection object for threat feed management.
        
        Args:
            data: Collection data dictionary
            spec_version: STIX specification version (2.0 or 2.1)
            
        Returns:
            STIX collection object dictionary
        """
        try:
            collection_obj = {
                "type": "x-collection",
                "id": f"x-collection--{uuid.uuid4()}",
                "spec_version": spec_version,
                "name": data.get("name", "Unknown Collection"),
                "description": data.get("description", ""),
                "can_read": data.get("can_read", True),
                "can_write": data.get("can_write", False),
                "media_types": data.get("media_types", ["application/vnd.oasis.stix+json"]),
                "x_feed_reference": data.get("feed_reference")
            }
            
            # Ensure common STIX properties
            collection_obj = self._ensure_common_properties(collection_obj, spec_version)
            
            logger.info(f"Created STIX collection object: {data.get('name', 'Unknown')}")
            return collection_obj
            
        except Exception as e:
            logger.error(f"Failed to create STIX collection object: {str(e)}")
            raise


def create_threat_feed_stix(feed_data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
    """
    Convenience function to create STIX object from threat feed data.
    
    Args:
        feed_data: Threat feed data dictionary
        spec_version: STIX specification version (2.0 or 2.1)
        
    Returns:
        STIX object dictionary
    """
    factory = ThreatFeedFactory()
    return factory.create_object(feed_data, spec_version)


def create_collection_stix(collection_data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
    """
    Convenience function to create STIX collection object.
    
    Args:
        collection_data: Collection data dictionary
        spec_version: STIX specification version (2.0 or 2.1)
        
    Returns:
        STIX collection object dictionary
    """
    factory = ThreatFeedFactory()
    return factory.create_collection_object(collection_data, spec_version)