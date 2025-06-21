"""
Context class for the CRISP Anonymization System
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import re
import ipaddress
import json
import uuid
from datetime import datetime, timezone

try:
    from .enums import AnonymizationLevel, DataType
    from .strategies import (
        AnonymizationStrategy,
        IPAddressAnonymizationStrategy,
        DomainAnonymizationStrategy,
        EmailAnonymizationStrategy,
        URLAnonymizationStrategy
    )
    from .exceptions import AnonymizationError, DataValidationError
except ImportError:
    from enums import AnonymizationLevel, DataType
    from strategies import (
        AnonymizationStrategy,
        IPAddressAnonymizationStrategy,
        DomainAnonymizationStrategy,
        EmailAnonymizationStrategy,
        URLAnonymizationStrategy
    )
    # Define exceptions if not imported
    class AnonymizationError(Exception):
        """Base exception for anonymization errors"""
        pass
    
    class DataValidationError(AnonymizationError):
        """Raised when data doesn't match the expected format"""
        pass


class AnonymizationContext:
    """
    Context class that uses different anonymization strategies
    Implements the Strategy pattern for flexible anonymization
    """
    
    def __init__(self):
        """Initialize the anonymization context with default strategies"""
        self._strategies: Dict[DataType, AnonymizationStrategy] = {}
        self._default_strategy: Optional[AnonymizationStrategy] = None
        
        # Value mappings for consistent anonymization
        self._value_mappings: Dict[str, str] = {}
        self._id_mappings: Dict[str, str] = {}
        
        # Register default strategies
        self.register_strategy(DataType.IP_ADDRESS, IPAddressAnonymizationStrategy())
        self.register_strategy(DataType.DOMAIN, DomainAnonymizationStrategy())
        self.register_strategy(DataType.EMAIL, EmailAnonymizationStrategy())
        self.register_strategy(DataType.URL, URLAnonymizationStrategy())
    
    def register_strategy(self, data_type: DataType, strategy: AnonymizationStrategy):
        """
        Register a strategy for a specific data type
        
        Args:
            data_type: The data type to register the strategy for
            strategy: The strategy to register
        """
        self._strategies[data_type] = strategy
    
    def set_default_strategy(self, strategy: AnonymizationStrategy):
        """
        Set a default strategy for unknown data types
        
        Args:
            strategy: The default strategy to use
        """
        self._default_strategy = strategy
    
    def execute_anonymization(self, data: str, data_type: DataType, level: AnonymizationLevel) -> str:
        """
        Execute anonymization using the appropriate strategy
        
        Args:
            data: The data to anonymize
            data_type: The type of data
            level: The anonymization level to apply
            
        Returns:
            The anonymized data
            
        Raises:
            ValueError: If no suitable strategy is found
            DataValidationError: If the data doesn't match the expected format
        """
        strategy = self._strategies.get(data_type)
        
        if strategy is None:
            if self._default_strategy:
                strategy = self._default_strategy
            else:
                raise ValueError(f"No strategy registered for data type: {data_type}")
        
        if not strategy.can_handle(data_type):
            raise ValueError(f"Strategy cannot handle data type: {data_type}")
        
        return strategy.anonymize(data, level)
    
    def auto_detect_and_anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """
        Auto-detect data type and anonymize accordingly
        
        Args:
            data: The data to anonymize
            level: The anonymization level to apply
            
        Returns:
            The anonymized data
        """
        data_type = self._detect_data_type(data)
        
        try:
            return self.execute_anonymization(data, data_type, level)
        except Exception as e:
            # In case of any error, return a safe fallback
            return f"anonymized-data-{hash(data) % 10000}"
    
    def _detect_data_type(self, data: str) -> DataType:
        """
        Detect the type of data based on patterns
        
        Args:
            data: The data to detect the type of
            
        Returns:
            The detected data type
        """
        data = data.strip()
        
        # Check for IPv6-like pattern (most specific first)
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{0,4}:){1,7}:|^:((:[0-9a-fA-F]{1,4}){1,7}|:)$|^[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})$|^([0-9a-fA-F]{1,4}:){1,2}((:[0-9a-fA-F]{1,4}){1,5})$|^([0-9a-fA-F]{1,4}:){1,3}((:[0-9a-fA-F]{1,4}){1,4})$|^([0-9a-fA-F]{1,4}:){1,4}((:[0-9a-fA-F]{1,4}){1,3})$|^([0-9a-fA-F]{1,4}:){1,5}((:[0-9a-fA-F]{1,4}){1,2})$|^([0-9a-fA-F]{1,4}:){1,6}(:[0-9a-fA-F]{1,4})$'
        
        # Even more general IPv6-like pattern
        ipv6_simple_pattern = r'^[0-9a-fA-F:]+$'
        
        # IPv4 patterns
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        ipv4_like_pattern = r'^(\d{1,3}\.)[a-zA-Z0-9\.]+$'  # Catches 192.xxxx.158.1
        
        # Check if it looks like an IP address (even if invalid)
        if (re.match(ipv6_pattern, data) or 
            re.match(ipv6_simple_pattern, data) or 
            re.match(ipv4_pattern, data) or
            re.match(ipv4_like_pattern, data) or
            (data.count('.') == 3 and data[0].isdigit()) or  # Simple IPv4 heuristic
            (data.count(':') >= 2 and re.search(r'[0-9a-fA-F]', data))):  # Simple IPv6 heuristic
            return DataType.IP_ADDRESS
        
        # Check for email
        if '@' in data and re.match(r'^[^@]+@[^@]+\.[^@]+$', data):
            return DataType.EMAIL
        
        # Check for URL
        if data.startswith(('http://', 'https://')):
            return DataType.URL
        
        # Check for domain (contains dots but not other URL indicators)
        if '.' in data and not data.startswith(('http://', 'https://')) and '@' not in data:
            return DataType.DOMAIN
        
        # Default to domain if unsure
        return DataType.DOMAIN
    
    def bulk_anonymize(self, data_items: List[Tuple[str, DataType]], level: AnonymizationLevel) -> List[str]:
        """
        Anonymize multiple data items at once
        
        Args:
            data_items: List of tuples (data, data_type)
            level: The anonymization level to apply
            
        Returns:
            List of anonymized data
        """
        results = []
        for data, data_type in data_items:
            try:
                anonymized = self.execute_anonymization(data, data_type, level)
                results.append(anonymized)
            except Exception as e:
                # Log error in real implementation
                results.append(f"[ERROR: {str(e)}]")
        return results
    
    def anonymize_stix_object(self, stix_data: Union[str, Dict[str, Any]], 
                              level: AnonymizationLevel = AnonymizationLevel.MEDIUM,
                              preserve_timestamps: bool = False,
                              time_shift_days: int = 0) -> str:
        """
        Anonymize STIX 2.1 object or bundle
        
        Args:
            stix_data: STIX JSON string or dictionary
            level: Anonymization level to apply
            preserve_timestamps: Whether to preserve original timestamps
            time_shift_days: Days to shift timestamps (if not preserving)
            
        Returns:
            Anonymized STIX JSON string
        """
        try:
            # Parse input data
            if isinstance(stix_data, str):
                stix_obj = json.loads(stix_data)
            else:
                stix_obj = stix_data.copy()
            
            # Validate input as STIX
            self._validate_stix_input(stix_obj)
            
            # Handle Bundle objects
            if stix_obj.get('type') == 'bundle':
                anonymized_data = self._anonymize_stix_bundle(stix_obj, level, preserve_timestamps, time_shift_days)
            else:
                anonymized_data = self._anonymize_stix_single_object(stix_obj, level, preserve_timestamps, time_shift_days)
            
            return json.dumps(anonymized_data, indent=2, sort_keys=True)
            
        except Exception as e:
            raise ValueError(f"Failed to anonymize STIX data: {e}")
    
    def _validate_stix_input(self, data: Dict[str, Any]):
        """Validate input data is valid STIX format."""
        required_fields = ['type', 'spec_version']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required STIX field: {field}")
        
        if data.get('spec_version') != '2.1':
            raise ValueError(f"Unsupported STIX version: {data.get('spec_version')}")
    
    def _anonymize_stix_bundle(self, bundle_data: Dict[str, Any], level: AnonymizationLevel,
                              preserve_timestamps: bool, time_shift_days: int) -> Dict[str, Any]:
        """Anonymize STIX Bundle object."""
        anonymized_bundle = bundle_data.copy()
        
        # Anonymize bundle ID
        if 'id' in anonymized_bundle:
            anonymized_bundle['id'] = self._anonymize_stix_id(anonymized_bundle['id'])
        
        # Anonymize all objects in bundle
        if 'objects' in anonymized_bundle:
            anonymized_objects = []
            for obj in anonymized_bundle['objects']:
                anonymized_obj = self._anonymize_stix_single_object(obj, level, preserve_timestamps, time_shift_days)
                anonymized_objects.append(anonymized_obj)
            anonymized_bundle['objects'] = anonymized_objects
        
        return anonymized_bundle
    
    def _anonymize_stix_single_object(self, obj_data: Dict[str, Any], level: AnonymizationLevel,
                                     preserve_timestamps: bool, time_shift_days: int) -> Dict[str, Any]:
        """Anonymize single STIX object."""
        anonymized_obj = obj_data.copy()
        obj_type = obj_data.get('type')
        
        # Anonymize STIX ID
        if 'id' in anonymized_obj:
            anonymized_obj['id'] = self._anonymize_stix_id(anonymized_obj['id'])
        
        # Anonymize timestamps if not preserving
        if not preserve_timestamps:
            anonymized_obj = self._anonymize_stix_timestamps(anonymized_obj, time_shift_days)
        
        # Anonymize sensitive fields based on object type
        sensitive_sco_types = {
            'ipv4-addr', 'ipv6-addr', 'domain-name', 'url', 'email-addr',
            'file', 'process', 'user-account', 'windows-registry-key',
            'network-traffic', 'email-message', 'x509-certificate'
        }
        
        if obj_type in sensitive_sco_types:
            # Handle cyber observables
            anonymized_obj = self._anonymize_stix_cyber_observable(anonymized_obj, level)
        else:
            # Handle domain objects
            anonymized_obj = self._anonymize_stix_domain_object(anonymized_obj, level)
        
        # Anonymize custom properties (x_ prefixed)
        anonymized_obj = self._anonymize_stix_custom_properties(anonymized_obj, level)
        
        # Anonymize references
        anonymized_obj = self._anonymize_stix_references(anonymized_obj)
        
        return anonymized_obj
    
    def _anonymize_stix_id(self, stix_id: str) -> str:
        """Generate consistent anonymized STIX ID."""
        if stix_id in self._id_mappings:
            return self._id_mappings[stix_id]
        
        # Parse type and UUID
        if '--' in stix_id:
            obj_type, _ = stix_id.split('--', 1)
            new_uuid = str(uuid.uuid4())
            anonymized_id = f"{obj_type}--{new_uuid}"
        else:
            anonymized_id = f"unknown--{uuid.uuid4()}"
        
        self._id_mappings[stix_id] = anonymized_id
        return anonymized_id
    
    def _anonymize_stix_timestamps(self, obj: Dict[str, Any], time_shift_days: int) -> Dict[str, Any]:
        """Anonymize timestamp fields with consistent offset."""
        timestamp_fields = ['created', 'modified', 'first_seen', 'last_seen', 
                           'valid_from', 'valid_until', 'start_time', 'stop_time']
        
        for field in timestamp_fields:
            if field in obj and obj[field]:
                try:
                    # Parse timestamp and apply offset
                    dt = datetime.fromisoformat(obj[field].replace('Z', '+00:00'))
                    dt = dt.replace(tzinfo=timezone.utc)
                    # Shift by specified days
                    if time_shift_days:
                        from datetime import timedelta
                        dt = dt + timedelta(days=time_shift_days)
                    obj[field] = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
                except Exception:
                    # Keep original timestamp if parsing fails
                    pass
        
        return obj
    
    def _anonymize_stix_cyber_observable(self, sco: Dict[str, Any], level: AnonymizationLevel) -> Dict[str, Any]:
        """Anonymize STIX Cyber Observable Object."""
        sco_type = sco.get('type')
        
        if sco_type in ['ipv4-addr', 'ipv6-addr'] and 'value' in sco:
            # Anonymize IP address
            sco['value'] = self.execute_anonymization(
                sco['value'], DataType.IP_ADDRESS, level
            )
        
        elif sco_type == 'domain-name' and 'value' in sco:
            # Anonymize domain name
            sco['value'] = self.execute_anonymization(
                sco['value'], DataType.DOMAIN, level
            )
        
        elif sco_type == 'email-addr' and 'value' in sco:
            # Anonymize email address
            sco['value'] = self.execute_anonymization(
                sco['value'], DataType.EMAIL, level
            )
        
        elif sco_type == 'url' and 'value' in sco:
            # Anonymize URL
            sco['value'] = self.execute_anonymization(
                sco['value'], DataType.URL, level
            )
        
        elif sco_type == 'file':
            # Anonymize file object
            if 'name' in sco:
                # Anonymize filename while preserving extension
                filename = sco['name']
                if '.' in filename:
                    name, ext = filename.rsplit('.', 1)
                    sco['name'] = f"{self._get_consistent_value(name, f'file-{hash(name) % 10000}')}.{ext}"
                else:
                    sco['name'] = self._get_consistent_value(filename, f'file-{hash(filename) % 10000}')
            
            # Anonymize hashes but keep them consistent
            if 'hashes' in sco:
                hashes = {}
                for hash_type, hash_value in sco['hashes'].items():
                    # Generate consistent anonymized hash values
                    hashes[hash_type] = self._get_consistent_value(
                        hash_value, 
                        lambda: ''.join('0123456789abcdef'[hash(hash_value + str(i)) % 16] for i in range(len(hash_value)))
                    )
                sco['hashes'] = hashes
        
        elif sco_type == 'user-account':
            # Anonymize user account object
            for field in ['account_login', 'display_name', 'user_id']:
                if field in sco:
                    sco[field] = self._get_consistent_value(
                        sco[field], 
                        f"user-{hash(sco[field]) % 10000}"
                    )
        
        elif sco_type == 'process':
            # Anonymize process object
            if 'command_line' in sco:
                sco['command_line'] = self._anonymize_text_content(sco['command_line'], level)
            
            if 'cwd' in sco:
                sco['cwd'] = self._anonymize_file_path(sco['cwd'], level)
        
        elif sco_type == 'network-traffic':
            # Network traffic references are handled by reference anonymization
            pass
        
        return sco
    
    def _anonymize_stix_domain_object(self, sdo: Dict[str, Any], level: AnonymizationLevel) -> Dict[str, Any]:
        """Anonymize STIX Domain Object."""
        # Anonymize common fields
        text_fields = ['name', 'description']
        for field in text_fields:
            if field in sdo:
                if isinstance(sdo[field], list):
                    sdo[field] = [self._anonymize_text_content(item, level) for item in sdo[field]]
                else:
                    sdo[field] = self._anonymize_text_content(sdo[field], level)
        
        # Handle aliases
        if 'aliases' in sdo:
            aliases = []
            for alias in sdo['aliases']:
                aliases.append(self._get_consistent_value(alias, f"alias-{hash(alias) % 10000}"))
            sdo['aliases'] = aliases
        
        # Handle Indicator patterns specially
        if sdo.get('type') == 'indicator' and 'pattern' in sdo:
            sdo['pattern'] = self._anonymize_stix_pattern(sdo['pattern'], level)
        
        # Handle Identity objects
        if sdo.get('type') == 'identity' and 'contact_information' in sdo:
            sdo['contact_information'] = self._anonymize_text_content(sdo['contact_information'], level)
        
        # Handle external references
        if 'external_references' in sdo:
            anonymized_refs = []
            for ref in sdo['external_references']:
                anonymized_ref = ref.copy()
                
                if 'url' in anonymized_ref:
                    anonymized_ref['url'] = self.execute_anonymization(anonymized_ref['url'], DataType.URL, level)
                
                if 'source_name' in anonymized_ref:
                    anonymized_ref['source_name'] = self._get_consistent_value(
                        anonymized_ref['source_name'], f"Source-{hash(anonymized_ref['source_name']) % 10000}"
                    )
                
                if 'external_id' in anonymized_ref:
                    anonymized_ref['external_id'] = self._get_consistent_value(
                        anonymized_ref['external_id'], 
                        f"EXT-{hash(anonymized_ref['external_id']) % 10000}"
                    )
                
                anonymized_refs.append(anonymized_ref)
            
            sdo['external_references'] = anonymized_refs
        
        return sdo
    
    def _anonymize_stix_pattern(self, pattern: str, level: AnonymizationLevel) -> str:
        """Anonymize STIX pattern expressions while preserving structure."""
        # Pattern: [cyber-observable-object:property = 'value']
        pattern_regex = r"\[([^:]+):([^=]+)=\s*'([^']+)'\]"
        
        def replace_pattern(match):
            obj_type = match.group(1).strip()
            property_name = match.group(2).strip()
            value = match.group(3)
            
            # Anonymize based on observable type
            if obj_type in ['ipv4-addr', 'ipv6-addr'] and property_name == 'value':
                anonymized_value = self.execute_anonymization(value, DataType.IP_ADDRESS, level)
            elif obj_type == 'domain-name' and property_name == 'value':
                anonymized_value = self.execute_anonymization(value, DataType.DOMAIN, level)
            elif obj_type == 'email-addr' and property_name == 'value':
                anonymized_value = self.execute_anonymization(value, DataType.EMAIL, level)
            elif obj_type == 'url' and property_name == 'value':
                anonymized_value = self.execute_anonymization(value, DataType.URL, level)
            elif obj_type == 'file' and 'hashes' in property_name:
                anonymized_value = self._get_consistent_value(
                    value, 
                    lambda: ''.join('0123456789abcdef'[hash(value + str(i)) % 16] for i in range(len(value)))
                )
            else:
                anonymized_value = self._get_consistent_value(value, f"anon_{hash(value) % 10000}")
            
            return f"[{obj_type}:{property_name} = '{anonymized_value}']"
        
        return re.sub(pattern_regex, replace_pattern, pattern)
    
    def _anonymize_stix_custom_properties(self, obj: Dict[str, Any], level: AnonymizationLevel) -> Dict[str, Any]:
        """Anonymize custom properties (x_ prefixed)."""
        for key, value in list(obj.items()):
            if key.startswith('x_'):
                if isinstance(value, str):
                    obj[key] = self._anonymize_text_content(value, level)
                elif isinstance(value, dict):
                    # Recursively anonymize nested dictionaries
                    obj[key] = self._anonymize_nested_dict(value, level)
                elif isinstance(value, list):
                    # Anonymize list items if they're strings
                    obj[key] = [self._anonymize_text_content(item, level) if isinstance(item, str) 
                               else item for item in value]
        
        return obj
    
    def _anonymize_nested_dict(self, obj: Dict[str, Any], level: AnonymizationLevel) -> Dict[str, Any]:
        """Recursively anonymize values in a nested dictionary."""
        anonymized = {}
        for key, value in obj.items():
            if isinstance(value, str):
                anonymized[key] = self._anonymize_text_content(value, level)
            elif isinstance(value, dict):
                anonymized[key] = self._anonymize_nested_dict(value, level)
            elif isinstance(value, list):
                anonymized[key] = [self._anonymize_text_content(item, level) if isinstance(item, str) 
                                  else item for item in value]
            else:
                anonymized[key] = value
        
        return anonymized
    
    def _anonymize_stix_references(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize STIX object references."""
        ref_fields = []
        
        # Find all reference fields
        for key in obj.keys():
            if key.endswith('_ref') or key.endswith('_refs'):
                ref_fields.append(key)
        
        # Anonymize references while maintaining consistency
        for field in ref_fields:
            if field in obj:
                if isinstance(obj[field], list):
                    obj[field] = [self._anonymize_stix_id(ref) for ref in obj[field]]
                else:
                    obj[field] = self._anonymize_stix_id(obj[field])
        
        return obj
    
    def _anonymize_text_content(self, text: str, level: AnonymizationLevel) -> str:
        """
        Anonymize text content while preserving structure.
        Fixed version with improved indicator detection and consistent anonymization.
        
        Args:
            text: The text to anonymize
            level: The anonymization level
            
        Returns:
            Anonymized text
        """
        if not text:
            return text
        
        # Don't anonymize at NONE level
        if level == AnonymizationLevel.NONE:
            return text
        
        # Define patterns for different indicator types
        # IPv4 pattern - more precise to avoid false positives
        ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        
        # IPv6 pattern (simplified for brevity)
        ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
        
        # Email pattern - more precise
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        
        # URL pattern - more precise
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        
        # Domain pattern - apply last as it can match parts of other patterns
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        
        # Create a copy of the text to work with
        result = text
        
        # Process in order of most specific to least specific patterns
        
        # 1. Replace IPv6 addresses
        ipv6_matches = re.finditer(ipv6_pattern, result)
        for match in reversed(list(ipv6_matches)):  # Process in reverse to preserve positions
            start, end = match.span()
            original_ip = result[start:end]
            try:
                anonymized_ip = self.execute_anonymization(original_ip, DataType.IP_ADDRESS, level)
                result = result[:start] + anonymized_ip + result[end:]
            except Exception:
                # Skip if anonymization fails
                pass
        
        # 2. Replace IPv4 addresses
        ipv4_matches = re.finditer(ipv4_pattern, result)
        for match in reversed(list(ipv4_matches)):  # Process in reverse to preserve positions
            start, end = match.span()
            original_ip = result[start:end]
            try:
                anonymized_ip = self.execute_anonymization(original_ip, DataType.IP_ADDRESS, level)
                result = result[:start] + anonymized_ip + result[end:]
            except Exception:
                # Skip if anonymization fails
                pass
        
        # 3. Replace URLs (before domains, as URLs contain domains)
        url_matches = re.finditer(url_pattern, result)
        for match in reversed(list(url_matches)):
            start, end = match.span()
            original_url = result[start:end]
            try:
                anonymized_url = self.execute_anonymization(original_url, DataType.URL, level)
                result = result[:start] + anonymized_url + result[end:]
            except Exception:
                # Skip if anonymization fails
                pass
        
        # 4. Replace emails
        email_matches = re.finditer(email_pattern, result)
        for match in reversed(list(email_matches)):
            start, end = match.span()
            original_email = result[start:end]
            try:
                anonymized_email = self.execute_anonymization(original_email, DataType.EMAIL, level)
                result = result[:start] + anonymized_email + result[end:]
            except Exception:
                # Skip if anonymization fails
                pass
        
        # 5. Replace domains (only those not part of URLs or emails already processed)
        domain_matches = re.finditer(domain_pattern, result)
        for match in reversed(list(domain_matches)):
            start, end = match.span()
            original_domain = result[start:end]
            
            # Skip if this domain is already part of a processed URL or email
            if "@" + original_domain in result or "://" + original_domain in result:
                continue
                
            try:
                anonymized_domain = self.execute_anonymization(original_domain, DataType.DOMAIN, level)
                result = result[:start] + anonymized_domain + result[end:]
            except Exception:
                # Skip if anonymization fails
                pass
        
        return result
    
    def _anonymize_file_path(self, path: str, level: AnonymizationLevel) -> str:
        """Anonymize file path while preserving structure."""
        if level == AnonymizationLevel.NONE:
            return path
            
        parts = path.replace('\\', '/').split('/')
        anonymized_parts = []
        
        for part in parts:
            if part:
                anonymized_parts.append(self._get_consistent_value(part, f"dir-{hash(part) % 10000}"))
            else:
                anonymized_parts.append(part)
        
        return ('\\' if '\\' in path else '/').join(anonymized_parts)
    
    def _get_consistent_value(self, original: str, placeholder_or_func) -> str:
        """Get consistent anonymized value for original input."""
        if original in self._value_mappings:
            return self._value_mappings[original]
        
        if callable(placeholder_or_func):
            anonymized = placeholder_or_func()
        else:
            anonymized = placeholder_or_func
        
        self._value_mappings[original] = anonymized
        return anonymized