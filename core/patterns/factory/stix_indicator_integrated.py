import logging
from datetime import datetime
from typing import Dict, Any
import pytz
import stix2
from django.utils import timezone
from .stix_base_factory import StixObjectCreator, STIXObjectFactory

logger = logging.getLogger(__name__)


class StixIndicatorCreator(StixObjectCreator):
    """
    Integrated factory for creating STIX Indicator objects
    """
    
    def create_from_stix(self, stix_obj) -> Dict[str, Any]:
        """
        Create a CRISP Indicator entity from a STIX Indicator object
        """
        try:
            # Check for None object
            if stix_obj is None:
                raise ValueError("STIX object cannot be None")
            
            # Extract indicator type from pattern
            pattern = stix_obj.pattern if hasattr(stix_obj, 'pattern') else ''
            indicator_type = self._extract_indicator_type_from_pattern(pattern)
            indicator_value = self._extract_value_from_pattern(pattern)
            
            # Convert STIX timestamps to datetime objects
            created = stix_obj.created.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'created') else None
            modified = stix_obj.modified.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'modified') else None
            valid_from = stix_obj.valid_from.replace(tzinfo=pytz.UTC) if hasattr(stix_obj, 'valid_from') else created
            
            # Map STIX Indicator to CRISP Indicator
            indicator_data = {
                'value': indicator_value,
                'type': indicator_type,
                'description': stix_obj.name if hasattr(stix_obj, 'name') else getattr(stix_obj, 'description', ''),
                'confidence': getattr(stix_obj, 'confidence', 50),
                'stix_id': stix_obj.id if hasattr(stix_obj, 'id') else f"indicator--{timezone.now().isoformat()}",
                'first_seen': valid_from,
                'last_seen': modified or valid_from,
                'created_at': created,
                'updated_at': modified,
                'is_anonymized': False,
            }
            
            return indicator_data
            
        except Exception as e:
            logger.error(f"Error creating indicator from STIX: {str(e)}")
            raise
    
    def create_stix_object(self, crisp_entity):
        """
        Create a STIX Indicator object from a CRISP Indicator entity
        """
        try:
            pattern = self._create_stix_pattern(crisp_entity.type, crisp_entity.value)
            
            # Create the STIX Indicator object
            stix_indicator = stix2.Indicator(
                pattern=pattern,
                labels=['malicious-activity'],
                pattern_type='stix',
                valid_from=crisp_entity.first_seen,
                confidence=crisp_entity.confidence or 50,
                description=crisp_entity.description or '',
                created=crisp_entity.created_at,
                modified=crisp_entity.updated_at or crisp_entity.created_at
            )
            
            return stix_indicator
            
        except Exception as e:
            logger.error(f"Error creating STIX object from indicator: {str(e)}")
            raise
    
    def create_object(self, data: Dict[str, Any], spec_version: str = "2.1") -> Dict[str, Any]:
        """
        Create a STIX Indicator object from input data dictionary
        """
        try:
            # Handle different input formats
            if 'pattern' in data:
                # Direct pattern provided
                pattern = data['pattern']
            elif 'indicator_type' in data and 'value' in data:
                # Type and value provided
                pattern = self._create_stix_pattern(data['indicator_type'], data['value'])
            elif 'type' in data and 'value' in data:
                # Alternative format
                pattern = self._create_stix_pattern(data['type'], data['value'])
            else:
                raise ValueError("Indicator data must include either 'pattern' or 'type'/'value' fields")
            
            # Create base STIX object
            stix_obj = {
                'type': 'indicator',
                'pattern': pattern,
                'pattern_type': data.get('pattern_type', 'stix'),
                'labels': data.get('labels', ['malicious-activity']),
            }
            
            if spec_version == "2.1":
                stix_obj['valid_from'] = data.get('valid_from', timezone.now().isoformat() + 'Z')
            
            # Add optional properties
            if 'name' in data:
                stix_obj['name'] = data['name']
            
            if 'description' in data:
                stix_obj['description'] = data['description']
            
            if 'confidence' in data:
                stix_obj['confidence'] = int(data['confidence'])
            
            if 'external_references' in data:
                stix_obj['external_references'] = data['external_references']
            
            if 'created_by_ref' in data:
                stix_obj['created_by_ref'] = data['created_by_ref']
            
            if 'valid_until' in data:
                stix_obj['valid_until'] = data['valid_until']
            
            stix_obj = self._ensure_common_properties(stix_obj, spec_version)
            
            # Validate required fields for indicators
            if not stix_obj.get('pattern'):
                raise ValueError("Indicator objects must have a pattern")
            
            if not stix_obj.get('labels'):
                raise ValueError("Indicator objects must have labels")
            
            # Version-specific validation
            if spec_version == "2.1":
                if 'valid_from' not in stix_obj:
                    raise ValueError("STIX 2.1 Indicator objects must have valid_from")
                if 'pattern_type' not in stix_obj:
                    raise ValueError("STIX 2.1 Indicator objects must have pattern_type")
            
            logger.debug(f"Created STIX Indicator: {stix_obj['id']}")
            return stix_obj
            
        except Exception as e:
            logger.error(f"Error creating STIX object from data: {str(e)}")
            raise
    
    def _extract_indicator_type_from_pattern(self, pattern: str) -> str:
        """Extract indicator type from STIX pattern."""
        if not pattern:
            return 'other'
        
        # Map STIX observable types to our indicator types
        type_mapping = {
            'ipv4-addr': 'ip',
            'ipv6-addr': 'ip',
            'domain-name': 'domain',
            'url': 'url',
            'file': 'file_hash',
            'email-addr': 'email',
            'user-account': 'user_agent',
            'windows-registry-key': 'registry',
            'mutex': 'mutex',
            'process': 'process'
        }
        
        for stix_type, crisp_type in type_mapping.items():
            if stix_type in pattern:
                return crisp_type
        
        return 'other'
    
    def _extract_value_from_pattern(self, pattern: str) -> str:
        """Extract the actual indicator value from STIX pattern."""
        if not pattern:
            return ''
        
        # Extract value from pattern like [ipv4-addr:value = '192.168.1.1']
        import re
        match = re.search(r"= '([^']+)'", pattern)
        if match:
            return match.group(1)
        
        # Fallback: try to extract any quoted value
        match = re.search(r"'([^']+)'", pattern)
        if match:
            return match.group(1)
        
        return pattern  # Return pattern as-is if can't extract
    
    def _create_stix_pattern(self, indicator_type: str, value: str) -> str:
        """Create STIX pattern from indicator type and value."""
        # Map CRISP indicator types to STIX observable types
        type_mapping = {
            'ip': 'ipv4-addr:value',
            'domain': 'domain-name:value',
            'url': 'url:value',
            'file_hash': 'file:hashes.SHA256',
            'email': 'email-addr:value',
            'user_agent': 'user-account:display_name',
            'registry': 'windows-registry-key:key',
            'mutex': 'mutex:name',
            'process': 'process:name'
        }
        
        # Handle special cases for file hashes
        if indicator_type == 'ip':
            return f"[ipv4-addr:value = '{value}']"
        elif indicator_type == 'domain':
            return f"[domain-name:value = '{value}']"
        elif indicator_type == 'url':
            return f"[url:value = '{value}']"
        elif indicator_type == 'hash':
            return f"[file:hashes.MD5 = '{value}']" 
        else:
            return f"[file:name = '{value}']"
    
    def _parse_indicator_pattern(self, pattern):
        """Parse STIX pattern to extract indicator type and value."""
        import re
        
        # IPv4 pattern
        ipv4_match = re.search(r"\[ipv4-addr:value = '([^']+)'\]", pattern)
        if ipv4_match:
            return ('ip', ipv4_match.group(1))
        
        # Domain pattern
        domain_match = re.search(r"\[domain-name:value = '([^']+)'\]", pattern)
        if domain_match:
            return ('domain', domain_match.group(1))
        
        # URL pattern
        url_match = re.search(r"\[url:value = '([^']+)'\]", pattern)
        if url_match:
            return ('url', url_match.group(1))
        
        # Hash pattern
        hash_match = re.search(r"\[file:hashes\.MD5 = '([^']+)'\]", pattern)
        if hash_match:
            return ('hash', hash_match.group(1))
        
        return ('unknown', '')


# Register the Indicator creator
STIXObjectFactory.register_creator('indicator', StixIndicatorCreator)