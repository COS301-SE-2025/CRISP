import logging
import hashlib
import json
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from datetime import datetime

from django.utils import timezone
from django.db import transaction
from django.conf import settings

import stix2
from stix2.exceptions import STIXError
from stix2validator import validate_instance

from .models import ExternalFeedSource, FeedConsumptionLog

# Assuming we have models for storing processed threat intelligence
from threat_intel.models import ThreatIntelligence, StixObject, DuplicateTracker

logger = logging.getLogger(__name__)

class DataProcessingError(Exception):
    """Base exception for data processing errors."""
    pass


class StixValidationError(DataProcessingError):
    """Exception raised for STIX format validation errors."""
    pass


class DataProcessor:
    """
    Process STIX data from external feeds for storage in the internal database.
    
    This class handles:
    1. STIX format validation
    2. Normalization to internal schema
    3. Duplicate detection
    4. Education sector relevance tagging
    """
    
    EDUCATION_SECTOR_KEYWORDS = [
        "education", "university", "college", "school", "campus", "student",
        "academic", "research", "faculty", "learning", "teaching", "professor",
        "library", "scholarship", "edutech"
    ]
    
    def __init__(self, feed_source: ExternalFeedSource, log_entry: FeedConsumptionLog = None):
        """
        Initialize the data processor.
        
        Args:
            feed_source: The feed source for the data being processed
            log_entry: Optional log entry to update during processing
        """
        self.feed_source = feed_source
        self.log_entry = log_entry
        
        # Track processing statistics
        self.processed_count = 0
        self.failed_count = 0
        self.duplicate_count = 0
        self.edu_relevant_count = 0
    
    def validate_stix_object(self, stix_data: Dict[str, Any]) -> bool:
        """
        Validate a STIX object against the STIX 2.1 specification.
        
        Args:
            stix_data: Dictionary containing STIX data
            
        Returns:
            True if valid, False otherwise
        
        Raises:
            StixValidationError: If validation fails with details
        """
        try:
            # First, try to parse as a STIX object
            stix_obj = stix2.parse(stix_data, allow_custom=True)
            
            # Then validate against the STIX 2.1 specification
            results = validate_instance(stix_data)
            
            if results.is_valid:
                return True
            else:
                error_msg = "STIX validation failed: " + ", ".join(results.errors)
                if self.log_entry:
                    self.log_entry.add_error(error_msg)
                    self.log_entry.save()
                raise StixValidationError(error_msg)
                
        except STIXError as e:
            error_msg = f"Invalid STIX format: {str(e)}"
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                self.log_entry.save()
            raise StixValidationError(error_msg)
    
    def generate_object_hash(self, stix_data: Dict[str, Any]) -> str:
        """
        Generate a consistent hash for duplicate detection.
        
        Args:
            stix_data: Dictionary containing STIX data
            
        Returns:
            String hash representation of the object's essential properties
        """
        # Extract the core properties that define uniqueness based on type
        object_type = stix_data.get('type', '')
        
        # Different handling based on object type
        if object_type == 'indicator':
            # For indicators, pattern is the key
            key_parts = [
                object_type,
                stix_data.get('pattern', ''),
                stix_data.get('pattern_type', '')
            ]
        elif object_type == 'malware':
            # For malware, name is key
            key_parts = [
                object_type,
                stix_data.get('name', ''),
                json.dumps(stix_data.get('malware_types', []), sort_keys=True)
            ]
        elif object_type == 'attack-pattern':
            # For TTPs, name and external references
            key_parts = [
                object_type,
                stix_data.get('name', ''),
                json.dumps(stix_data.get('external_references', []), sort_keys=True)
            ]
        else:
            # Default case - use the id and modified fields
            key_parts = [
                object_type,
                stix_data.get('id', ''),
                stix_data.get('modified', '')
            ]
        
        # Create hash from key parts
        hash_key = '|'.join(str(part) for part in key_parts)
        return hashlib.sha256(hash_key.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, object_hash: str) -> bool:
        """
        Check if an object is a duplicate based on its hash.
        
        Args:
            object_hash: Hash value from generate_object_hash
            
        Returns:
            True if a duplicate exists, False otherwise
        """
        return DuplicateTracker.objects.filter(object_hash=object_hash).exists()
    
    def is_education_relevant(self, stix_data: Dict[str, Any]) -> bool:
        """
        Determine if a STIX object is relevant to the education sector.
        
        Args:
            stix_data: Dictionary containing STIX data
            
        Returns:
            True if relevant to education sector, False otherwise
        """
        # Extract text fields where keywords might appear
        text_fields = []
        
        # Common fields across object types
        text_fields.extend([
            stix_data.get('name', ''),
            stix_data.get('description', '')
        ])
        
        # Object-specific fields
        if stix_data.get('type') == 'indicator':
            text_fields.append(stix_data.get('pattern', ''))
        
        if stix_data.get('type') == 'malware':
            text_fields.extend(stix_data.get('malware_types', []))
        
        if stix_data.get('type') == 'attack-pattern':
            text_fields.extend(stix_data.get('kill_chain_phases', []))
            
        # Check for education sector keywords
        combined_text = ' '.join(str(field).lower() for field in text_fields)
        for keyword in self.EDUCATION_SECTOR_KEYWORDS:
            if keyword in combined_text:
                return True
                
        # Check if object references education sector in identity or sectors
        if stix_data.get('type') == 'identity':
            sectors = stix_data.get('sectors', [])
            if 'education' in map(str.lower, sectors):
                return True
                
        # Check if object is targeted at education sector in victim_refs
        victim_refs = stix_data.get('victim_refs', [])
        if victim_refs:
            # Ideally, we would look up these references to determine if they're education sector
            # For simplicity, we'll just check if any contain education keywords
            for ref in victim_refs:
                if any(keyword in ref.lower() for keyword in self.EDUCATION_SECTOR_KEYWORDS):
                    return True
        
        return False
    
    def normalize_to_internal(self, stix_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize STIX data to our internal schema structure.
        
        Args:
            stix_data: Dictionary containing STIX data
            
        Returns:
            Dictionary with normalized data for internal storage
        """
        # Basic normalization for common fields
        normalized = {
            'stix_id': stix_data.get('id'),
            'stix_type': stix_data.get('type'),
            'created': stix_data.get('created'),
            'modified': stix_data.get('modified'),
            'feed_source': self.feed_source,
            'raw_data': stix_data,
            'is_education_relevant': self.is_education_relevant(stix_data)
        }
        
        # Type-specific normalization
        if stix_data.get('type') == 'indicator':
            normalized.update({
                'name': stix_data.get('name', ''),
                'description': stix_data.get('description', ''),
                'pattern': stix_data.get('pattern', ''),
                'pattern_type': stix_data.get('pattern_type', ''),
                'indicator_types': stix_data.get('indicator_types', []),
                'valid_from': stix_data.get('valid_from'),
                'valid_until': stix_data.get('valid_until')
            })
        elif stix_data.get('type') == 'threat-actor':
            normalized.update({
                'name': stix_data.get('name', ''),
                'description': stix_data.get('description', ''),
                'threat_actor_types': stix_data.get('threat_actor_types', []),
                'aliases': stix_data.get('aliases', []),
                'roles': stix_data.get('roles', [])
            })
        elif stix_data.get('type') == 'vulnerability':
            normalized.update({
                'name': stix_data.get('name', ''),
                'description': stix_data.get('description', ''),
                'external_references': stix_data.get('external_references', [])
            })
        
        return normalized
    
    def save_to_database(self, normalized_data: Dict[str, Any]) -> Tuple[Any, bool]:
        """
        Save normalized data to the database.
        
        Args:
            normalized_data: Dictionary with normalized data
            
        Returns:
            Tuple of (saved object, created boolean)
        """
        # Generate hash for duplicate detection
        stix_data = normalized_data.get('raw_data', {})
        object_hash = self.generate_object_hash(stix_data)
        
        # Check for duplicates
        if self.is_duplicate(object_hash):
            self.duplicate_count += 1
            # Return existing object
            stix_obj = StixObject.objects.get(
                object_hash=object_hash
            )
            return stix_obj, False
        
        # Create new object with transaction to ensure consistency
        with transaction.atomic():
            # Create the STIX object
            stix_obj = StixObject.objects.create(
                stix_id=normalized_data.get('stix_id'),
                stix_type=normalized_data.get('stix_type'),
                object_hash=object_hash,
                feed_source=self.feed_source,
                raw_data=normalized_data.get('raw_data'),
                is_education_relevant=normalized_data.get('is_education_relevant', False),
                created=normalized_data.get('created'),
                modified=normalized_data.get('modified')
            )
            
            # Create duplicate tracker
            DuplicateTracker.objects.create(
                object_hash=object_hash,
                stix_object=stix_obj,
                first_seen=timezone.now()
            )
            
            # Create type-specific object based on stix_type
            stix_type = normalized_data.get('stix_type')
            
            if stix_type == 'indicator':
                ThreatIntelligence.objects.create(
                    stix_object=stix_obj,
                    name=normalized_data.get('name', ''),
                    description=normalized_data.get('description', ''),
                    pattern=normalized_data.get('pattern', ''),
                    pattern_type=normalized_data.get('pattern_type', ''),
                    indicator_types=normalized_data.get('indicator_types', []),
                    valid_from=normalized_data.get('valid_from'),
                    valid_until=normalized_data.get('valid_until')
                )
            elif stix_type in ('malware', 'attack-pattern', 'threat-actor', 'vulnerability'):
                # These types have similar schemas
                ThreatIntelligence.objects.create(
                    stix_object=stix_obj,
                    name=normalized_data.get('name', ''),
                    description=normalized_data.get('description', '')
                    # Additional fields would be stored in type-specific tables
                )
            
            # Track education sector relevance for analytics
            if normalized_data.get('is_education_relevant', False):
                self.edu_relevant_count += 1
            
            return stix_obj, True
    
    def process_object(self, stix_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single STIX object through the full pipeline.
        
        Args:
            stix_data: Dictionary containing STIX data
            
        Returns:
            Processed object if successful, None if failed
        """
        try:
            # Validate STIX format
            self.validate_stix_object(stix_data)
            
            # Normalize to internal schema
            normalized_data = self.normalize_to_internal(stix_data)
            
            # Save to database with duplicate detection
            obj, created = self.save_to_database(normalized_data)
            
            if created:
                self.processed_count += 1
            
            return normalized_data
            
        except (StixValidationError, DataProcessingError) as e:
            # Already logged in validation method
            self.failed_count += 1
            return None
        except Exception as e:
            # Unexpected error
            error_msg = f"Error processing object: {str(e)}"
            logger.exception(error_msg)
            
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                self.log_entry.save()
                
            self.failed_count += 1
            return None
    
    def process_objects(self, stix_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of STIX objects.
        
        Args:
            stix_objects: List of STIX objects to process
            
        Returns:
            Dictionary with processing statistics
        """
        # Reset counters
        self.processed_count = 0
        self.failed_count = 0
        self.duplicate_count = 0
        self.edu_relevant_count = 0
        
        for stix_data in stix_objects:
            self.process_object(stix_data)
            
            # Update log entry periodically
            if self.log_entry and (self.processed_count + self.failed_count) % 100 == 0:
                self.log_entry.objects_processed = self.processed_count
                self.log_entry.objects_failed = self.failed_count
                self.log_entry.save(update_fields=['objects_processed', 'objects_failed'])
        
        # Final log update
        if self.log_entry:
            self.log_entry.objects_processed = self.processed_count
            self.log_entry.objects_failed = self.failed_count
            
            # Determine overall status
            if self.failed_count > 0 and self.processed_count == 0:
                self.log_entry.status = FeedConsumptionLog.ConsumptionStatus.FAILURE
            elif self.failed_count > 0:
                self.log_entry.status = FeedConsumptionLog.ConsumptionStatus.PARTIAL
            else:
                self.log_entry.status = FeedConsumptionLog.ConsumptionStatus.SUCCESS
                
            self.log_entry.end_time = timezone.now()
            self.log_entry.save()
        
        return {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'duplicates': self.duplicate_count,
            'edu_relevant': self.edu_relevant_count
        }'malware':
            normalized.update({
                'name': stix_data.get('name', ''),
                'description': stix_data.get('description', ''),
                'malware_types': stix_data.get('malware_types', []),
                'is_family': stix_data.get('is_family', False)
            })
        elif stix_data.get('type') == 'attack-pattern':
            normalized.update({
                'name': stix_data.get('name', ''),
                'description': stix_data.get('description', ''),
                'external_references': stix_data.get('external_references', []),
                'kill_chain_phases': stix_data.get('kill_chain_phases', [])
            })
        elif stix_data.get('type') == 