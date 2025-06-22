import logging
from datetime import datetime
import pytz
from stix2 import Indicator as StixIndicator
from core.patterns.factory.stix_object_creator import StixObjectCreator

logger = logging.getLogger(__name__)

class StixIndicatorCreator(StixObjectCreator):
    """
    Factory for creating STIX Indicator objects from CRISP Indicator entities and vice versa.
    """
    
    def create_from_stix(self, stix_obj):
        """
        Create a CRISP Indicator entity from a STIX Indicator object.
        
        Args:
            stix_obj: STIX Indicator object
            
        Returns:
            Dictionary with CRISP Indicator properties
        """
        try:
            # Extract the indicator type and value from the pattern
            indicator_type, value = self._parse_indicator_pattern(stix_obj.pattern)
            
            # Convert STIX timestamps to datetime objects
            created = stix_obj.created.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'created') else None
            modified = stix_obj.modified.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'modified') else None
            
            # Map STIX Indicator to CRISP Indicator
            indicator_data = {
                'type': indicator_type,
                'value': value,
                'stix_id': stix_obj.id,
                'created_at': created,
                'updated_at': modified,
                'first_seen': created,
                'last_seen': modified,
                'description': stix_obj.description if hasattr(stix_obj, 'description') else None,
                'confidence': int(stix_obj.confidence * 100) if hasattr(stix_obj, 'confidence') else 50,
                'is_anonymized': False,
            }
            
            return indicator_data
            
        except Exception as e:
            logger.error(f"Error creating indicator from STIX: {str(e)}")
            raise
    
    def create_stix_object(self, crisp_entity):
        """
        Create a STIX Indicator object from a CRISP Indicator entity.
        
        Args:
            crisp_entity: CRISP Indicator model instance
            
        Returns:
            STIX Indicator object
        """
        try:
            # Convert the CRISP Indicator type and value to a STIX pattern
            pattern = self._create_stix_pattern(crisp_entity.type, crisp_entity.value)
            
            # Create the STIX Indicator
            stix_indicator = StixIndicator(
                type="indicator",
                pattern=pattern,
                pattern_type="stix",
                valid_from=crisp_entity.first_seen or crisp_entity.created_at,
                description=crisp_entity.description,
                confidence=crisp_entity.confidence / 100 
            )
            
            return stix_indicator
            
        except Exception as e:
            logger.error(f"Error creating STIX object from indicator: {str(e)}")
            raise
    
    def _parse_indicator_pattern(self, pattern):
        """
        Parse a STIX indicator pattern to extract type and value.
        
        Example patterns:
        - [ipv4-addr:value = '192.168.1.1']
        - [domain-name:value = 'example.com']
        
        Args:
            pattern: STIX indicator pattern
            
        Returns:
            Tuple of (indicator_type, value)
        """
        try:
            pattern = pattern.strip('[]')
            parts = pattern.split(':')
            
            if len(parts) < 2:
                return 'other', pattern
            
            stix_type = parts[0].strip()
            value_part = ':'.join(parts[1:])
            
            value = value_part.split('=')[1].strip().strip("'\"")
            
            # Map STIX type to CRISP type
            type_mapping = {
                'ipv4-addr': 'ip',
                'ipv6-addr': 'ip',
                'domain-name': 'domain',
                'url': 'url',
                'file:hashes': 'file_hash',
                'email-addr': 'email',
                'user-agent': 'user_agent'
            }
            
            indicator_type = type_mapping.get(stix_type, 'other')
            
            # For file hashes, extract the hash type
            if indicator_type == 'file_hash':
                hash_part = value_part.lower()
                if 'md5' in hash_part:
                    hash_type = 'md5'
                elif 'sha-1' in hash_part or 'sha1' in hash_part:
                    hash_type = 'sha1'
                elif 'sha-256' in hash_part or 'sha256' in hash_part:
                    hash_type = 'sha256'
                else:
                    hash_type = 'other'
                
                return indicator_type, value, hash_type
            
            return indicator_type, value
            
        except Exception as e:
            logger.error(f"Error parsing indicator pattern: {str(e)}")
            return 'other', pattern
    
    def _create_stix_pattern(self, indicator_type, value):
        """
        Create a STIX pattern from a CRISP indicator type and value.
        
        Args:
            indicator_type: CRISP indicator type
            value: Indicator value
            
        Returns:
            STIX pattern string
        """
        # Map CRISP type to STIX type
        type_mapping = {
            'ip': 'ipv4-addr',  
            'domain': 'domain-name',
            'url': 'url',
            'file_hash': 'file:hashes.MD5', 
            'email': 'email-addr',
            'user_agent': 'user-agent',
            'other': 'x-custom-indicator'
        }
        
        stix_type = type_mapping.get(indicator_type, 'x-custom-indicator')
        
        # Create the pattern
        pattern = f"[{stix_type}:value = '{value}']"
        
        return pattern