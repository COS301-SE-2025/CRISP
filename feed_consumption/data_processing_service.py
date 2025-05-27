"""Data processing service for STIX objects from TAXII feeds"""
import logging
from typing import Dict, List, Set, Tuple, Optional
import hashlib
import json
from datetime import datetime
from django.utils import timezone
from stix2 import parse
from stix2.exceptions import STIXError

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process STIX data from TAXII feeds"""
    
    # Common education sector indicators/keywords
    EDUCATION_KEYWORDS = {
        'university', 'college', 'school', 'education', 'academic', 'student',
        'faculty', 'campus', 'research', 'learning', 'classroom', 'teacher',
        'professor', 'lecture', 'alumni', 'scholarship', 'course'
    }
    
    def __init__(self):
        """Initialize the data processor"""
        self.processed_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.failed_count = 0
        self.error_messages = []
    
    def process_objects(self, stix_objects: List[Dict]) -> Tuple[int, int, int, int, List[str]]:
        """
        Process a list of STIX objects
        
        Args:
            stix_objects: List of STIX objects (raw dictionaries or strings)
            
        Returns:
            Tuple of (processed, added, updated, failed, error_messages)
        """
        self.processed_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.failed_count = 0
        self.error_messages = []
        
        for stix_object in stix_objects:
            try:
                # Parse the object if it's a string
                if isinstance(stix_object, str):
                    stix_object = json.loads(stix_object)
                
                # Validate and normalize the object
                normalized = self._validate_and_normalize(stix_object)
                
                # Check for duplicates
                is_duplicate = self._check_for_duplicate(normalized)
                
                # Tag relevance to education sector
                self._tag_education_relevance(normalized)
                
                # Store the object (in a real implementation, this would insert into a database)
                # For now, we'll just simulate storage and count objects
                if is_duplicate:
                    self.updated_count += 1
                else:
                    self.added_count += 1
                
                self.processed_count += 1
                
            except Exception as e:
                self.failed_count += 1
                error_msg = f"Failed to process object: {str(e)}"
                logger.error(error_msg)
                self.error_messages.append(error_msg)
        
        return (
            self.processed_count, 
            self.added_count, 
            self.updated_count, 
            self.failed_count,
            self.error_messages
        )
    
    def _validate_and_normalize(self, stix_object: Dict) -> Dict:
        """
        Validate and normalize a STIX object
        
        Args:
            stix_object: Raw STIX object dictionary
            
        Returns:
            Normalized STIX object
            
        Raises:
            ValueError: If the object is invalid
        """
        # Make sure we have a proper STIX object
        if not isinstance(stix_object, dict):
            raise ValueError("STIX object must be a dictionary")
            
        if 'id' not in stix_object:
            raise ValueError("STIX object must have an ID")
            
        if 'type' not in stix_object:
            raise ValueError("STIX object must have a type")
            
        # Try parsing with stix2 library to validate
        try:
            parsed = parse(stix_object)
            # Return the parsed object as a dictionary
            return parsed.serialize()
        except STIXError as e:
            raise ValueError(f"Invalid STIX object: {str(e)}")
    
    def _check_for_duplicate(self, stix_object: Dict) -> bool:
        """
        Check if a STIX object is a duplicate
        
        Args:
            stix_object: Normalized STIX object
            
        Returns:
            True if duplicate, False otherwise
        """
        # In a real implementation, this would query a database
        # For now, we'll just simulate and return False
        return False
    
    def _tag_education_relevance(self, stix_object: Dict) -> Dict:
        """
        Tag an object with education sector relevance
        
        Args:
            stix_object: STIX object to tag
            
        Returns:
            Tagged STIX object
        """
        # Check if this object contains education-related keywords
        is_relevant = False
        
        # Check description and name fields for education keywords
        if 'description' in stix_object:
            if any(keyword in stix_object['description'].lower() for keyword in self.EDUCATION_KEYWORDS):
                is_relevant = True
                
        if 'name' in stix_object:
            if any(keyword in stix_object['name'].lower() for keyword in self.EDUCATION_KEYWORDS):
                is_relevant = True
        
        # For indicators, check pattern
        if stix_object.get('type') == 'indicator' and 'pattern' in stix_object:
            if any(keyword in stix_object['pattern'].lower() for keyword in self.EDUCATION_KEYWORDS):
                is_relevant = True
        
        # Add custom property for education relevance
        if 'x_crisp' not in stix_object:
            stix_object['x_crisp'] = {}
            
        stix_object['x_crisp']['education_relevant'] = is_relevant
        
        return stix_object
