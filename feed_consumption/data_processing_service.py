"""
Data processing service for STIX objects from TAXII feeds.

This module provides the implementation of the DataProcessor class
for processing, normalizing, validating, and storing STIX objects.
"""
import logging
import json
import hashlib
import re
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from datetime import datetime

from django.utils import timezone
from django.db import IntegrityError, transaction

import stix2
from stix2 import parse
from stix2.exceptions import STIXError
from stix2validator import validate_instance

from .models import ExternalFeedSource, FeedConsumptionLog
from .data_processor import DataProcessingError, StixValidationError

logger = logging.getLogger(__name__)

# Mock classes to support testing until real models are created
class ThreatIntelligence:
    """Mock ThreatIntelligence model for testing"""
    objects = type('Objects', (), {'create': lambda **kwargs: None})()

class StixObject:
    """Mock StixObject model for testing"""
    objects = type('Objects', (), {'create': lambda **kwargs: None, 'get': lambda **kwargs: None})()

class DuplicateTracker:
    """Mock DuplicateTracker model for testing"""
    objects = type('Objects', (), {'create': lambda **kwargs: None, 'filter': lambda **kwargs: type('QuerySet', (), {'exists': lambda: False})()})()


class DataProcessor:
    """
    Process STIX data from TAXII feeds
    
    This class handles validating, normalizing, de-duplicating, and storing
    STIX objects from TAXII feeds.
    """
    
    # Common education sector indicators/keywords
    EDUCATION_KEYWORDS = {
        'university', 'college', 'school', 'education', 'academic', 'student',
        'faculty', 'campus', 'research', 'learning', 'classroom', 'teacher',
        'professor', 'lecture', 'alumni', 'scholarship', 'course'
    }
    
    def __init__(self, feed_source: ExternalFeedSource, log_entry: FeedConsumptionLog):
        """
        Initialize the data processor
        
        Args:
            feed_source: The feed source being processed
            log_entry: The log entry for this processing run
        """
        self.feed_source = feed_source
        self.log_entry = log_entry
        
        # Initialize counters
        self.processed_count = 0
        self.duplicate_count = 0
        self.failed_count = 0
        self.edu_relevant_count = 0
    
    def validate_stix_object(self, stix_data: Dict) -> bool:
        """
        Validate a STIX 2.1 object
        
        Args:
            stix_data: The STIX object to validate
            
        Returns:
            True if valid, raises exception otherwise
            
        Raises:
            StixValidationError: If validation fails
        """
        try:
            # Try parsing with stix2 library
            parsed = stix2.parse(stix_data, allow_custom=True)
            
            # Validate against the STIX 2.1 schema
            results = validate_instance(stix_data)
            
            # Check validation results
            if not results.is_valid:
                error_msgs = "\n".join(results.errors)
                logger.warning(f"STIX validation failed: {error_msgs}")
                
                if self.log_entry:
                    self.log_entry.add_error(f"STIX validation failed: {error_msgs}")
                
                raise StixValidationError(f"STIX validation failed: {error_msgs}")
            
            return True
        
        except STIXError as e:
            error_msg = f"Invalid STIX format: {str(e)}"
            logger.warning(error_msg)
            
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                
            raise StixValidationError(error_msg)
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.warning(error_msg)
            
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                
            raise StixValidationError(error_msg)
    
    def generate_object_hash(self, stix_object: Dict) -> str:
        """
        Generate a hash for a STIX object for deduplication
        
        This hash ignores the `id` field and focuses on content
        to identify duplicates across different sources.
        
        Args:
            stix_object: The STIX object to hash
            
        Returns:
            A string hash of the object content
        """
        # Extract the type to determine which fields to use for hashing
        obj_type = stix_object.get('type', '')
        
        # Create a dictionary with the fields to hash
        hash_fields = {
            'type': obj_type
        }
        
        # Add fields based on object type
        if obj_type == 'indicator':
            # For indicators, hash pattern and pattern_type
            hash_fields['pattern'] = stix_object.get('pattern', '')
            hash_fields['pattern_type'] = stix_object.get('pattern_type', '')
            
        elif obj_type == 'malware':
            # For malware, hash name and types
            hash_fields['name'] = stix_object.get('name', '')
            hash_fields['malware_types'] = str(stix_object.get('malware_types', []))
            
        elif obj_type == 'attack-pattern':
            # For attack patterns, hash name and external references
            hash_fields['name'] = stix_object.get('name', '')
            if 'external_references' in stix_object:
                for ref in stix_object['external_references']:
                    if 'source_name' in ref and 'external_id' in ref:
                        hash_fields[f"ref_{ref['source_name']}"] = ref['external_id']
                        
        else:
            # For other types, use common identifiable fields
            hash_fields['name'] = stix_object.get('name', '')
            hash_fields['description'] = stix_object.get('description', '')
            
        # Create a stable string representation of the fields
        hash_str = json.dumps(hash_fields, sort_keys=True)
        
        # Generate a SHA-256 hash and return as hexdigest
        return hashlib.sha256(hash_str.encode()).hexdigest()
    
    def is_duplicate(self, object_hash: str) -> bool:
        """
        Check if an object with this hash already exists
        
        Args:
            object_hash: Hash of the STIX object
            
        Returns:
            True if a duplicate exists, False otherwise
        """
        # Check if the hash exists in the DuplicateTracker table
        return DuplicateTracker.objects.filter(object_hash=object_hash).exists()
    
    def is_education_relevant(self, stix_object: Dict) -> bool:
        """
        Check if a STIX object is relevant to the education sector
        
        Args:
            stix_object: The STIX object to check
            
        Returns:
            True if relevant to education, False otherwise
        """
        # Extract text fields to check
        texts_to_check = []
        
        # Add common fields that might contain education-related keywords
        for field in ['name', 'description']:
            if field in stix_object and isinstance(stix_object[field], str):
                texts_to_check.append(stix_object[field].lower())
        
        # For indicators, check pattern
        if stix_object.get('type') == 'indicator' and 'pattern' in stix_object:
            texts_to_check.append(stix_object['pattern'].lower())
        
        # Check if any education keywords are present in any of the texts
        for text in texts_to_check:
            if any(keyword in text for keyword in self.EDUCATION_KEYWORDS):
                return True
        
        # Check for education sectors in identity objects
        if stix_object.get('type') == 'identity' and 'sectors' in stix_object:
            if 'education' in stix_object['sectors']:
                return True
        
        # Check for victim references
        if 'victim_refs' in stix_object:
            # In a real implementation, we would resolve these references
            # For now, assume education relevance if any victim refs exist
            return True
        
        return False
    
    def normalize_to_internal(self, stix_object: Dict) -> Dict:
        """
        Normalize a STIX object to our internal format
        
        Args:
            stix_object: The STIX object to normalize
            
        Returns:
            Normalized internal representation
        """
        # Initialize the normalized object
        normalized = {
            'stix_id': stix_object['id'],
            'stix_type': stix_object['type'],
            'feed_source': self.feed_source,
            'raw_data': stix_object,
            'object_hash': self.generate_object_hash(stix_object)
        }
        
        # Add created and modified timestamps if available
        if 'created' in stix_object:
            normalized['created'] = stix_object['created']
        if 'modified' in stix_object:
            normalized['modified'] = stix_object['modified']
        
        # Check education relevance
        normalized['is_education_relevant'] = self.is_education_relevant(stix_object)
        
        # Add type-specific fields
        obj_type = stix_object['type']
        
        # Common fields across many types
        for field in ['name', 'description']:
            if field in stix_object:
                normalized[field] = stix_object[field]
        
        # Type-specific fields
        if obj_type == 'indicator':
            for field in ['pattern', 'pattern_type', 'indicator_types', 'valid_from']:
                if field in stix_object:
                    normalized[field] = stix_object[field]
                    
        elif obj_type == 'malware':
            for field in ['malware_types', 'is_family']:
                if field in stix_object:
                    normalized[field] = stix_object[field]
                    
        elif obj_type == 'attack-pattern':
            if 'external_references' in stix_object:
                normalized['external_references'] = stix_object['external_references']
        
        return normalized
    
    def save_to_database(self, normalized_object: Dict) -> Tuple[Any, bool]:
        """
        Save a normalized STIX object to the database
        
        Args:
            normalized_object: The normalized STIX object
            
        Returns:
            Tuple of (stix_object, created) where created is True if new
        """
        object_hash = normalized_object['object_hash']
        
        # Check for duplicates
        if self.is_duplicate(object_hash):
            self.duplicate_count += 1
            
            # Get the existing object
            stix_obj = StixObject.objects.get(object_hash=object_hash)
            return stix_obj, False
        
        # Create a new StixObject
        try:
            # Extract relevant fields for the StixObject model
            stix_obj = StixObject.objects.create(
                stix_id=normalized_object['stix_id'],
                stix_type=normalized_object['stix_type'],
                feed_source=normalized_object['feed_source'],
                raw_data=normalized_object['raw_data'],
                object_hash=object_hash,
                created_at=timezone.now(),
                is_education_relevant=normalized_object['is_education_relevant']
            )
            
            # Create a DuplicateTracker entry
            DuplicateTracker.objects.create(
                stix_object=stix_obj,
                object_hash=object_hash
            )
            
            # Create a ThreatIntelligence entry with type-specific fields
            threat_intel_data = {
                'stix_object': stix_obj
            }
            
            # Add fields from normalized_object to threat_intel_data
            for field in ['name', 'description', 'pattern', 'pattern_type',
                          'indicator_types', 'valid_from', 'malware_types', 
                          'is_family', 'external_references']:
                if field in normalized_object:
                    threat_intel_data[field] = normalized_object[field]
            
            # Create the ThreatIntelligence entry
            ThreatIntelligence.objects.create(**threat_intel_data)
            
            # Increment education relevance counter if needed
            if normalized_object['is_education_relevant']:
                self.edu_relevant_count += 1
            
            return stix_obj, True
            
        except IntegrityError as e:
            # Handle race conditions where another process created the object
            self.duplicate_count += 1
            logger.warning(f"IntegrityError saving STIX object: {str(e)}")
            return StixObject.objects.get(object_hash=object_hash), False
        
        except Exception as e:
            error_msg = f"Error saving STIX object to database: {str(e)}"
            logger.error(error_msg)
            if self.log_entry:
                self.log_entry.add_error(error_msg)
            raise DataProcessingError(error_msg)
    
    def process_object(self, stix_object: Dict) -> bool:
        """
        Process a single STIX object
        
        Args:
            stix_object: The STIX object to process
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the object
            self.validate_stix_object(stix_object)
            
            # Normalize the object
            normalized = self.normalize_to_internal(stix_object)
            
            # Save to database
            _, created = self.save_to_database(normalized)
            
            # Increment counters
            self.processed_count += 1
            
            return True
            
        except Exception as e:
            self.failed_count += 1
            error_msg = f"Failed to process object: {str(e)}"
            logger.error(error_msg)
            
            if self.log_entry:
                self.log_entry.add_error(error_msg)
                
            return False
    
    def process_objects(self, stix_objects: List[Dict]) -> Dict:
        """
        Process a list of STIX objects
        
        Args:
            stix_objects: List of STIX objects
            
        Returns:
            Dictionary with processing statistics
        """
        # Reset counters
        self.processed_count = 0
        self.duplicate_count = 0
        self.failed_count = 0
        self.edu_relevant_count = 0
        
        # Process each object
        for stix_object in stix_objects:
            try:
                # Process string objects (parse as JSON)
                if isinstance(stix_object, str):
                    stix_object = json.loads(stix_object)
                    
                # Process the object
                self.process_object(stix_object)
                
            except Exception as e:
                self.failed_count += 1
                error_msg = f"Failed to process object: {str(e)}"
                logger.error(error_msg)
                
                if self.log_entry:
                    self.log_entry.add_error(error_msg)
        
        # Update the log entry with statistics
        if self.log_entry:
            self.log_entry.objects_processed = self.processed_count
            # Update status based on success/failure ratio
            if self.failed_count > 0 and self.processed_count == 0:
                self.log_entry.status = FeedConsumptionLog.ConsumptionStatus.FAILURE
            elif self.failed_count > 0:
                self.log_entry.status = 'partial'  # ConsumptionStatus.PARTIAL
            self.log_entry.save()
        
        # Return statistics
        return {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'duplicates': self.duplicate_count,
            'edu_relevant': self.edu_relevant_count
        }
