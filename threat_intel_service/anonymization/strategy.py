from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Set, Optional
import re
import uuid
import ipaddress
import hashlib
import copy
import json
from django.conf import settings

class AnonymizationStrategy(ABC):
    """
    Abstract base class for anonymization strategies (Strategy Pattern - SRS 7.3.3).
    """
    @abstractmethod
    def anonymize(self, stix_input: Any, trust_level: float = 0.5) -> Dict[str, Any]: # Changed type hint for input
        """
        Anonymize a STIX object based on the specific strategy and trust level.
        
        Args:
            stix_object: Original STIX object as a dictionary
            trust_level: Trust level (0.0 to 1.0) that affects anonymization intensity
                         0.0 = full anonymization, 1.0 = no anonymization
        
        Returns:
            Anonymized STIX object as a dictionary
        """
        pass
    
    def get_effectiveness_score(self) -> float:
        """
        Return the effectiveness score of this anonymization strategy (0.0 to 1.0).
        
        This measures how much analytical value is preserved after anonymization.
        Target is 0.95 (95%) per SEC1.7 requirement.
        """
        pass
    
    def _get_fields_to_anonymize(self, stix_type: str) -> Dict[str, float]:
        """
        Get fields that should be anonymized for a specific STIX object type.
        
        Returns:
            Dictionary of field names and their sensitivity scores (0.0 to 1.0)
        """
        # Common fields across all STIX objects
        common_fields = {
            'created_by_ref': 0.7,
            'external_references': 0.8,
            'object_marking_refs': 0.3,
        }
        
        # Type-specific fields
        type_specific_fields = {
            'indicator': {
                'name': 0.5,
                'description': 0.9,
                'pattern': 0.6,  # Sensitive but critical for functionality
            },
            'malware': {
                'name': 0.4,
                'description': 0.8,
                'sample_refs': 0.9,
            },
            'attack-pattern': {
                'name': 0.3,
                'description': 0.7,
                'external_references': 0.5,
            },
            'threat-actor': {
                'name': 0.9,
                'description': 0.8,
                'aliases': 0.7,
                'roles': 0.5,
                'goals': 0.6,
                'sophistication': 0.3,
                'resource_level': 0.4,
                'primary_motivation': 0.5,
            },
            'identity': {
                'name': 0.9,
                'description': 0.8,
                'identity_class': 0.3,
                'sectors': 0.5,
                'contact_information': 1.0,  # Always anonymize contact info
            },
            'relationship': {
                'description': 0.7,
            },
        }
        
        # Combine common fields with type-specific fields
        result = copy.deepcopy(common_fields)
        if stix_type in type_specific_fields:
            result.update(type_specific_fields[stix_type])
            
        return result
    
    def _should_anonymize_field(self, field_name: str, sensitivity: float, trust_level: float) -> bool:
        """
        Determine if a field should be anonymized based on its sensitivity and trust level.
        
        Args:
            field_name: Name of the field
            sensitivity: Sensitivity score of the field (0.0 to 1.0)
            trust_level: Trust level (0.0 to 1.0)
        
        Returns:
            True if the field should be anonymized, False otherwise
        """
        # Higher sensitivity and lower trust means more likely to anonymize
        threshold = trust_level
        
        # Fields in preserved_patterns are exempted from anonymization
        preserved_patterns = settings.ANONYMIZATION_SETTINGS.get('PRESERVED_PATTERNS', [])
        for pattern in preserved_patterns:
            if re.match(pattern, field_name):
                return False
                
        return sensitivity > threshold


class NoAnonymizationStrategy(AnonymizationStrategy):
    """
    Strategy that performs no anonymization (used for high-trust relationships).
    """
    def anonymize(self, stix_input: Any, trust_level: float = 1.0) -> Dict[str, Any]:
        """
        Return the original object without anonymization.
        """
        stix_object_dict = {}
        if isinstance(stix_input, str):
            try:
                stix_object_dict = json.loads(stix_input)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode STIX input string in NoAnonymizationStrategy: {stix_input[:100]}")
                # Depending on desired behavior, you might return the input or raise an error
                return {} # Or raise an error
        elif isinstance(stix_input, dict):
            stix_object_dict = stix_input
        else:
            print(f"Warning: Unexpected STIX input type in NoAnonymizationStrategy: {type(stix_input)}")
            return {} # Or raise an error
            
        return copy.deepcopy(stix_object_dict)
    
    def get_effectiveness_score(self) -> float:
        """
        No anonymization preserves 100% of analytical value.
        """
        return 1.0


class PartialAnonymizationStrategy(AnonymizationStrategy):
    """
    Strategy that anonymizes only selected sensitive fields based on trust level.
    """
    def anonymize(self, stix_input: Any, trust_level: float = 0.5) -> Dict[str, Any]:
        print(f"\n[PartialAnonymizationStrategy DEBUG] === Entering anonymize ===")
        print(f"[PartialAnonymizationStrategy DEBUG] Input type to anonymize: {type(stix_input)}")
        if isinstance(stix_input, str):
            print(f"[PartialAnonymizationStrategy DEBUG] Input string (first 200 chars): {stix_input[:200]}")

        stix_object_dict = {}
        if isinstance(stix_input, str):
            try:
                stix_object_dict = json.loads(stix_input)
                print(f"[PartialAnonymizationStrategy DEBUG] Successfully parsed stix_input string to dict. Keys: {list(stix_object_dict.keys()) if isinstance(stix_object_dict, dict) else 'N/A'}")
            except json.JSONDecodeError as e:
                print(f"ERROR in [PartialAnonymizationStrategy DEBUG]: Could not decode STIX input string. Error: {e}. Input: {stix_input[:200]}")
                return {"error": "Failed to parse input STIX JSON string", "details": str(e)}
        elif isinstance(stix_input, dict):
            stix_object_dict = stix_input
            print(f"[PartialAnonymizationStrategy DEBUG] stix_input is already a dict. Keys: {list(stix_object_dict.keys())}")
        else:
            print(f"ERROR in [PartialAnonymizationStrategy DEBUG]: Unexpected STIX input type: {type(stix_input)}")
            return {"error": f"Unexpected STIX input type: {type(stix_input)}"}
            
        print(f"[PartialAnonymizationStrategy DEBUG] stix_object_dict type after parsing attempt: {type(stix_object_dict)}")
        result = copy.deepcopy(stix_object_dict) 
        print(f"[PartialAnonymizationStrategy DEBUG] 'result' type after deepcopy: {type(result)}")

        if not isinstance(result, dict):
            print(f"CRITICAL ERROR in [PartialAnonymizationStrategy DEBUG]: 'result' is NOT a dict before .get('type'). Type is: {type(result)}. Value (first 200): {str(result)[:200]}")
            return {"error": f"'result' became non-dict. Type: {type(result)}"}

        stix_type = result.get('type', 'unknown') 
        print(f"[PartialAnonymizationStrategy DEBUG] Determined stix_type: {stix_type}")
        
        # Get fields to potentially anonymize for this type
        fields_to_anonymize = self._get_fields_to_anonymize(stix_type)
        
        # Process each field
        for field_name, sensitivity in fields_to_anonymize.items():
            if field_name in result and self._should_anonymize_field(field_name, sensitivity, trust_level):
                result[field_name] = self._anonymize_field(field_name, result[field_name], stix_type)
        
        # Special handling for patterns in indicators
        if stix_type == 'indicator' and 'pattern' in result and self._should_anonymize_field('pattern', fields_to_anonymize.get('pattern', 0.6), trust_level):
            result['pattern'] = self._anonymize_pattern(result['pattern'])
            
        print(f"[PartialAnonymizationStrategy DEBUG] === Exiting anonymize ===\n")
        return result
    
    def _anonymize_field(self, field_name: str, field_value: Any, stix_type: str) -> Any:
        """
        Anonymize a specific field based on its name and value type.
        """
        if field_name == 'name':
            return f"Anonymized {stix_type.capitalize()} {str(uuid.uuid4())[:8]}"
        
        elif field_name == 'description':
            if isinstance(field_value, str):
                # Keep general info but remove specifics
                return f"Anonymized description: {self._redact_sensitive_info(field_value)}"
            return field_value
            
        elif field_name == 'created_by_ref':
            # Replace with a generic identity reference
            return f"identity--{hashlib.sha256(field_value.encode()).hexdigest()[:32]}"
            
        elif field_name == 'external_references':
            if isinstance(field_value, list):
                return self._anonymize_external_references(field_value)
            return field_value
            
        elif field_name == 'contact_information':
            # Always fully anonymize contact information
            return "Anonymized contact information"
            
        elif field_name == 'aliases' and isinstance(field_value, list):
            # Anonymize each alias
            return [f"Alias-{i}" for i in range(len(field_value))]
            
        elif field_name == 'sample_refs' and isinstance(field_value, list):
            # Hash the sample references
            return [f"anonymized-sample--{hashlib.sha256(ref.encode()).hexdigest()[:32]}" for ref in field_value]
            
        # Default: return the original value
        return field_value
    
    def _anonymize_external_references(self, references: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Anonymize external references while preserving critical information.
        """
        result = []
        for ref in references:
            if 'url' in ref:
                # Keep domain but anonymize path
                url_parts = ref['url'].split('/')
                if len(url_parts) >= 3:  # Has domain
                    domain = url_parts[2]
                    ref['url'] = f"{url_parts[0]}//{domain}/anonymized"
                    
            if 'description' in ref:
                ref['description'] = self._redact_sensitive_info(ref['description'])
                
            # Keep source_name but make it generic if it might identify the organization
            if 'source_name' in ref and len(ref['source_name'].split()) <= 2:  # Short names are likely org names
                ref['source_name'] = f"Anonymized Source {hashlib.md5(ref['source_name'].encode()).hexdigest()[:6]}"
                
            result.append(ref)
        return result
    
    def _anonymize_pattern(self, pattern: str) -> str:
        """
        Anonymize STIX pattern while preserving its structure and effectiveness.
        """
        # Anonymize IP addresses
        ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        
        def anonymize_ip(match):
            try:
                ip = match.group(1)
                ip_obj = ipaddress.ip_address(ip)
                
                if ip_obj.is_private:
                    # Keep private IPs but slightly modify them
                    ip_parts = ip.split('.')
                    ip_parts[-1] = 'x'
                    return '.'.join(ip_parts)
                else:
                    # For public IPs, preserve the first two octets
                    ip_parts = ip.split('.')
                    return f"{ip_parts[0]}.{ip_parts[1]}.x.x"
            except:
                return match.group(1)
                
        pattern = re.sub(ip_pattern, anonymize_ip, pattern)
        
        # Anonymize domain names but preserve TLDs
        domain_pattern = r'([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)'
        
        def anonymize_domain(match):
            domain = match.group(1)
            parts = domain.split('.')
            if len(parts) > 1:
                # Keep TLD and domain type, anonymize specific name
                return f"anon-{hashlib.md5(parts[0].encode()).hexdigest()[:6]}.{'.'.join(parts[1:])}"
            return domain
            
        pattern = re.sub(domain_pattern, anonymize_domain, pattern)
        
        # Anonymize file hashes but preserve type
        hash_pattern = r'(MD5|SHA-1|SHA-256|SHA-512|SHA3-256)=\'([a-fA-F0-9]+)\''
        
        def anonymize_hash(match):
            hash_type = match.group(1)
            hash_value = match.group(2)
            # Create a new hash of same length but derived from original
            new_hash = hashlib.sha256(hash_value.encode()).hexdigest()
            if len(hash_value) < len(new_hash):
                new_hash = new_hash[:len(hash_value)]
            return f"{hash_type}='{new_hash}'"
            
        pattern = re.sub(hash_pattern, anonymize_hash, pattern, flags=re.IGNORECASE)
        
        return pattern
    
    def _redact_sensitive_info(self, text: str) -> str:
        """
        Redact potentially sensitive information from text.
        """
        # Redact email addresses
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED EMAIL]', text)
        
        # Redact IP addresses
        text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[REDACTED IP]', text)
        
        # Redact URLs
        text = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+', '[REDACTED URL]', text)
        
        # Redact potential personally identifiable names (capitalized words that aren't at start of sentence)
        text = re.sub(r'(?<![.!?]\s)(?<!\n)(?<!\A)\b[A-Z][a-z]+\b', '[REDACTED NAME]', text)
        
        return text
    
    def get_effectiveness_score(self) -> float:
        """
        Partial anonymization preserves approximately 95% of analytical value.
        """
        return 0.95


class FullAnonymizationStrategy(AnonymizationStrategy):
    """
    Strategy that aggressively anonymizes all sensitive fields.
    """
    def anonymize(self, stix_input: Any, trust_level: float = 0.0) -> Dict[str, Any]:
        """
        Thoroughly anonymize the STIX object, preserving only essential structure.
        """
        stix_object_dict = {}
        if isinstance(stix_input, str):
            try:
                stix_object_dict = json.loads(stix_input)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode STIX input string in FullAnonymizationStrategy: {stix_input[:100]}")
                return {}
        elif isinstance(stix_input, dict):
            stix_object_dict = stix_input
        else:
            print(f"Warning: Unexpected STIX input type in FullAnonymizationStrategy: {type(stix_input)}")
            return {}

        result = copy.deepcopy(stix_object_dict) # 'result' is now a dictionary
        stix_type = result.get('type', 'unknown') # This should now work

        # Preserve critical fields
        preserved_fields = {'id', 'type', 'spec_version', 'created', 'modified'}
        
        # For indicators, preserve pattern structure but anonymize content
        if stix_type == 'indicator' and 'pattern' in result:
            result['pattern'] = self._fully_anonymize_pattern(result['pattern'])
            preserved_fields.add('pattern')
            preserved_fields.add('pattern_type')
            preserved_fields.add('valid_from')
            if 'valid_until' in result:
                preserved_fields.add('valid_until')
                
        # For relationships, preserve relationship structure
        if stix_type == 'relationship':
            preserved_fields.add('relationship_type')
            preserved_fields.add('source_ref')
            preserved_fields.add('target_ref')
            
            # Anonymize the references
            if 'source_ref' in result:
                parts = result['source_ref'].split('--')
                if len(parts) == 2:
                    result['source_ref'] = f"{parts[0]}--{hashlib.sha256(parts[1].encode()).hexdigest()[:32]}"
                    
            if 'target_ref' in result:
                parts = result['target_ref'].split('--')
                if len(parts) == 2:
                    result['target_ref'] = f"{parts[0]}--{hashlib.sha256(parts[1].encode()).hexdigest()[:32]}"
        
        # Process type-specific required fields
        if stix_type == 'malware':
            preserved_fields.add('is_family')
            
        if stix_type == 'identity':
            preserved_fields.add('identity_class')
            if 'name' in result:
                result['name'] = f"Anonymized Identity {hashlib.md5(result['name'].encode()).hexdigest()[:8]}"
                preserved_fields.add('name')
                
        # Replace all non-preserved fields with anonymized versions
        for field_name in list(result.keys()):
            if field_name not in preserved_fields:
                if field_name == 'name':
                    result[field_name] = f"Anonymized {stix_type.capitalize()} {str(uuid.uuid4())[:8]}"
                elif field_name == 'description':
                    result[field_name] = f"Anonymized {stix_type} description"
                elif isinstance(result[field_name], list):
                    # For lists, replace with placeholder list of same length
                    result[field_name] = [f"anonymized-item-{i}" for i in range(len(result[field_name]))]
                elif field_name.endswith('_ref') or field_name.endswith('_refs'):
                    # For references, create anonymized but valid references
                    if isinstance(result[field_name], list):
                        result[field_name] = [f"anonymized--{hashlib.sha256(str(i).encode()).hexdigest()[:32]}" 
                                             for i, _ in enumerate(result[field_name])]
                    else:
                        result[field_name] = f"anonymized--{hashlib.sha256(str(result[field_name]).encode()).hexdigest()[:32]}"
                else:
                    # For other fields, use a generic placeholder
                    result[field_name] = f"anonymized-{field_name}"
                    
        return result
    
    def _fully_anonymize_pattern(self, pattern: str) -> str:
        """
        Fully anonymize a STIX pattern while preserving its structure.
        """
        # Preserve pattern structure but replace all specific values
        
        # Replace IP addresses with anonymized versions
        pattern = re.sub(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', '10.0.0.x', pattern)
        
        # Replace domain names
        pattern = re.sub(r'([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)', 'anonymized.domain.tld', pattern)
        
        # Replace file hashes
        pattern = re.sub(r'(MD5|SHA-1|SHA-256|SHA-512|SHA3-256)=\'([a-fA-F0-9]+)\'', 
                        lambda m: f"{m.group(1)}='{'0' * len(m.group(2))}'", pattern, flags=re.IGNORECASE)
        
        # Replace email addresses
        pattern = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'anonymized@example.com', pattern)
        
        # Replace URL paths
        pattern = re.sub(r'https?://[^\s\'"]+', 'https://anonymized.example.com/path', pattern)
        
        return pattern
    
    def get_effectiveness_score(self) -> float:
        """
        Full anonymization preserves approximately 80% of analytical value.
        """
        return 0.8


class AnonymizationStrategyFactory:
    """
    Factory for creating anonymization strategies based on the specified strategy name.
    """
    _strategies = {
        'none': NoAnonymizationStrategy,
        'partial': PartialAnonymizationStrategy,
        'full': FullAnonymizationStrategy,
    }
    
    @classmethod
    def get_strategy(cls, strategy_name: str) -> AnonymizationStrategy:
        """
        Get an instance of the specified anonymization strategy.
        
        Args:
            strategy_name: Name of the strategy ('none', 'partial', or 'full')
            
        Returns:
            An instance of the appropriate AnonymizationStrategy
            
        Raises:
            ValueError: If the specified strategy name is not recognized
        """
        strategy_class = cls._strategies.get(strategy_name.lower())
        if not strategy_class:
            raise ValueError(f"Unknown anonymization strategy: {strategy_name}")
        return strategy_class()
    
    @classmethod
    def get_default_strategy(cls) -> AnonymizationStrategy:
        """
        Get the default anonymization strategy as configured in settings.
        """
        default_strategy = getattr(settings, 'ANONYMIZATION_SETTINGS', {}).get('DEFAULT_STRATEGY', 'partial')
        return cls.get_strategy(default_strategy)
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """
        Register a new anonymization strategy.
        
        Args:
            name: Name of the strategy
            strategy_class: Class implementing the strategy
        """
        if not issubclass(strategy_class, AnonymizationStrategy):
            raise ValueError("Strategy class must inherit from AnonymizationStrategy")
        cls._strategies[name.lower()] = strategy_class