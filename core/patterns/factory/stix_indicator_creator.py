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
            # Check if pattern is available
            if not hasattr(stix_obj, 'pattern'):
                return {'type': 'other', 'value': 'Unknown', 'confidence': 50}
                
            # Parse the pattern - handle both 2-value and 3-value returns
            pattern_result = self._parse_indicator_pattern(stix_obj.pattern)
            
            if len(pattern_result) == 3:
                indicator_type, value, hash_type = pattern_result
            else:
                indicator_type, value = pattern_result
                hash_type = None
            
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
                'confidence': int(stix_obj.confidence) if hasattr(stix_obj, 'confidence') and stix_obj.confidence is not None else 50,
                'is_anonymized': False,
            }
            
            # Add hash_type if it's a file_hash
            if indicator_type == 'file_hash' and hash_type:
                indicator_data['hash_type'] = hash_type
            
            return indicator_data
            
        except Exception as e:
            logger.error(f"Error creating indicator from STIX: {str(e)}")
            raise
    
    def create_stix_object(self, crisp_entity):
        """
        Create a STIX Indicator object from a CRISP Indicator entity.
        
        Args:
            crisp_entity: CRISP Indicator entity
            
        Returns:
            STIX Indicator object
        """
        try:
            # Create the STIX pattern based on indicator type and value
            pattern = self._create_stix_pattern(crisp_entity.type, crisp_entity.value)
            
            # Keep confidence as integer (0-100) - STIX 2.1 expects integer percentage
            confidence_value = int(crisp_entity.confidence) if crisp_entity.confidence else 50
            
            # Create the STIX Indicator
            stix_indicator = StixIndicator(
                pattern=pattern,
                pattern_type="stix",
                labels=["malicious-activity"],
                confidence=confidence_value,  # Pass as integer (80, not 0.8)
                description=crisp_entity.description or "",
                created=crisp_entity.created_at,
                modified=crisp_entity.updated_at or crisp_entity.created_at,
                valid_from=crisp_entity.first_seen or crisp_entity.created_at
            )
            
            return stix_indicator
            
        except Exception as e:
            logger.error(f"Error creating STIX object from indicator: {str(e)}")
            raise
    
    def _parse_indicator_pattern(self, pattern):
        try:
            pattern = pattern.strip('[]')
            parts = pattern.split(':')
            
            # Special handling for file hash patterns
            if 'file' in parts[0] and 'hashes' in pattern:
                indicator_type = 'file_hash'
                
                # Extract hash type if possible
                hash_type = 'other'
                if '.' in pattern:
                    hash_type_section = pattern.split('.')[1].split(' ')[0]
                    if hash_type_section.lower() in ['md5', 'sha1', 'sha-1', 'sha256', 'sha-256']:
                        hash_type = hash_type_section
                
                # Extract value
                value = pattern.split("'")[1] if "'" in pattern else pattern.split('"')[1]
                
                return indicator_type, value, hash_type
            
            # Handle other pattern types
            stix_type = parts[0].strip()
            value_part = ':'.join(parts[1:])
            
            value = value_part.split('=')[1].strip().strip("'\"")
            
            # Map STIX type to CRISP type
            type_mapping = {
                'ipv4-addr': 'ip',
                'ipv6-addr': 'ip',
                'domain-name': 'domain',
                'url': 'url',
                'email-addr': 'email',
                'user-agent': 'user_agent'
            }
            
            indicator_type = type_mapping.get(stix_type, 'other')
            return indicator_type, value
            
        except Exception as e:
            logger.error(f"Error parsing indicator pattern: {str(e)}")
            return 'other', pattern
    
    def _create_stix_pattern(self, indicator_type, value, hash_type='MD5'):
        # Map CRISP type to STIX type
        type_mapping = {
            'ip': 'ipv4-addr',  
            'domain': 'domain-name',
            'url': 'url',
            'file_hash': 'file:hashes',
            'email': 'email-addr',
            'user_agent': 'user-agent',
            'other': 'x-custom-indicator'
        }
        
        stix_type = type_mapping.get(indicator_type, 'x-custom-indicator')
        
        # Create the pattern
        if indicator_type == 'file_hash':
            pattern = f"[file:hashes.{hash_type} = '{value}']"
        else:
            pattern = f"[{stix_type}:value = '{value}']"
        
        return pattern