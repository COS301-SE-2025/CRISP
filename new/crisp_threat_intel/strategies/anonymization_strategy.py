from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Set, Optional, Union
import re
import uuid
import ipaddress
import hashlib
import copy
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def anonymize_ip_address(ip_str: str, level: str = 'partial') -> str:
    """Anonymize an IP address"""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if level == 'full':
            return '10.0.0.1' if ip_obj.version == 4 else '2001:db8::1'

        if ip_obj.version == 4:
            network = ipaddress.IPv4Network(f"{ip_str}/24", strict=False)
            return str(network.network_address)
        elif ip_obj.version == 6:
            network = ipaddress.IPv6Network(f"{ip_str}/64", strict=False)
            return str(network.network_address)
    except ValueError:
        return "invalid_ip_format"
    return ip_str


def anonymize_domain_name(domain: str, level: str = 'partial') -> str:
    """Anonymize a domain name"""
    if level == 'full':
        return "anonymized.example.com"

    parts = domain.split('.')
    if len(parts) > 2:
        subdomain_hash = hashlib.md5(parts[0].encode()).hexdigest()[:6]
        return f"anon-{subdomain_hash}.{'.'.join(parts[1:])}"
    elif len(parts) == 2:
        return domain
    return "anonymized.domain"


def anonymize_email_address(email: str, level: str = 'partial') -> str:
    """Anonymize an email address"""
    if level == 'full':
        return "user@anonymized.example.com"

    parts = email.split('@')
    if len(parts) == 2:
        local_part, domain_part = parts
        local_hash = hashlib.md5(local_part.encode()).hexdigest()[:8]
        return f"anonuser-{local_hash}@{anonymize_domain_name(domain_part, level='partial')}"
    return "anonymized.email"


def anonymize_url(url_str: str, level: str = 'partial') -> str:
    """Anonymize a URL"""
    if level == 'full':
        return "https://anonymized.example.com/path"
    try:
        from urllib.parse import urlparse, urlunparse
        parsed_url = urlparse(url_str)
        anonymized_netloc = anonymize_domain_name(parsed_url.hostname, level='partial') if parsed_url.hostname else "anonymized.host"
        return urlunparse((parsed_url.scheme, anonymized_netloc, "/anonymized_path", "", "", ""))
    except Exception:
        return "https://anonymized.example.com/invalid_url_format"


def anonymize_file_hash(hash_value: str, hash_type: Optional[str] = None, level: str = 'partial') -> str:
    """Anonymize a file hash"""
    if level == 'full':
        ht = hash_type.upper() if hash_type else "HASH"
        return f"anon:[{ht}_VALUE_REMOVED]"

    if not hash_value:
        return ""
    derived_hash = hashlib.sha256(f"SALT_FOR_ANON_{hash_value}".encode()).hexdigest()
    return f"anon:{derived_hash[:len(hash_value)]}"


def redact_text_field(text: str, level: str = 'partial') -> str:
    """Redact sensitive information from text"""
    if not text or not isinstance(text, str):
        return ""

    if level == 'full':
        return "[REDACTED CONTENT]"

    # Partial redaction
    text = re.sub(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)", 
                  lambda m: anonymize_ip_address(m.group(1), level='partial'), text)
    text = re.sub(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", 
                  lambda m: anonymize_email_address(m.group(1), level='partial'), text)
    text = re.sub(r"(?:https?|ftp)://[^\s/$.?#].[^\s]*", 
                  lambda m: anonymize_url(m.group(1), level='partial'), text)
    return text


def anonymize_stix_pattern(pattern: str, level: str = 'partial') -> str:
    """Anonymize a STIX pattern"""
    if not pattern or not isinstance(pattern, str):
        return ""

    # Anonymize IPs
    pattern = re.sub(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)",
                     lambda m: anonymize_ip_address(m.group(1), level), pattern)
    
    # Anonymize Domains
    pattern = re.sub(r"([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.(?:[a-zA-Z]{2,6}|[a-zA-Z0-9\-]{2,}\.[a-zA-Z]{2,}))",
                     lambda m: anonymize_domain_name(m.group(1), level), pattern)
    
    # Anonymize Emails
    pattern = re.sub(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                     lambda m: anonymize_email_address(m.group(1), level), pattern)
    
    # Anonymize Hashes
    pattern = re.sub(r"SHA256\s*=\s*'([a-fA-F0-9]{64})'",
                     lambda m: f"SHA256 = '{anonymize_file_hash(m.group(1), 'SHA256', level)}'", pattern)
    pattern = re.sub(r"MD5\s*=\s*'([a-fA-F0-9]{32})'",
                     lambda m: f"MD5 = '{anonymize_file_hash(m.group(1), 'MD5', level)}'", pattern)

    return pattern


class AnonymizationStrategy(ABC):
    """
    Abstract base class for anonymization strategies (Strategy Pattern)
    """
    
    SENSITIVE_FIELD_HANDLERS = {
        "name": lambda val, level: f"Anonymized Object ({str(uuid.uuid4())[:8]})" if level == 'full' else f"Redacted Name ({hashlib.md5(str(val).encode()).hexdigest()[:6]})",
        "description": lambda val, level: redact_text_field(val, level),
        "contact_information": lambda val, level: "[CONTACT_INFO_REDACTED]",
        "aliases": lambda val_list, level: [f"Alias-{i+1}" for i in range(len(val_list))] if isinstance(val_list, list) else "[REDACTED_ALIAS]",
        "pattern": lambda val, level: anonymize_stix_pattern(val, level),
        "created_by_ref": lambda val, level: f"identity--{hashlib.sha256(str(val).encode()).hexdigest()[:32]}" if level == 'full' else val,
    }

    @abstractmethod
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5, strategy_level: str = 'partial') -> Dict[str, Any]:
        """Anonymize a STIX object"""
        pass

    def get_effectiveness_score(self) -> float:
        """Returns analytical value preservation score (0.0 to 1.0)"""
        raise NotImplementedError

    def _get_stix_dict(self, stix_input: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """Converts STIX input to a dictionary if it's a JSON string"""
        if isinstance(stix_input, str):
            try:
                return json.loads(stix_input)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse STIX JSON string: {e}")
                raise ValueError(f"Invalid STIX JSON input: {e}")
        elif isinstance(stix_input, dict):
            return stix_input
        else:
            raise TypeError(f"STIX input must be a dictionary or JSON string, got {type(stix_input)}.")

    def _anonymize_field_value(self, field_name: str, original_value: Any, stix_type: str, strategy_level: str) -> Any:
        """Anonymizes a single field's value based on its name and the strategy level"""
        handler = self.SENSITIVE_FIELD_HANDLERS.get(field_name)
        if handler:
            return handler(original_value, strategy_level)

        if isinstance(original_value, str):
            return redact_text_field(original_value, strategy_level)
        elif isinstance(original_value, list) and strategy_level == 'full':
            return [f"[ANON_LIST_ITEM_{i+1}]" for i in range(len(original_value))]
        return original_value


class DomainAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing domains"""
    
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5, strategy_level: str = 'partial') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        anonymized_stix_object = copy.deepcopy(stix_object_dict)
        
        # Focus on domain-specific anonymization
        for field_name, original_value in anonymized_stix_object.items():
            if 'domain' in field_name.lower() or 'hostname' in field_name.lower():
                if isinstance(original_value, str):
                    anonymized_stix_object[field_name] = anonymize_domain_name(original_value, strategy_level)
        
        return anonymized_stix_object

    def get_effectiveness_score(self) -> float:
        return 0.90


class IPAddressAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing IP addresses"""
    
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5, strategy_level: str = 'partial') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        anonymized_stix_object = copy.deepcopy(stix_object_dict)
        
        # Focus on IP address anonymization
        for field_name, original_value in anonymized_stix_object.items():
            if 'ip' in field_name.lower() or 'address' in field_name.lower():
                if isinstance(original_value, str):
                    anonymized_stix_object[field_name] = anonymize_ip_address(original_value, strategy_level)
        
        return anonymized_stix_object

    def get_effectiveness_score(self) -> float:
        return 0.85


class EmailAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing email addresses"""
    
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5, strategy_level: str = 'partial') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        anonymized_stix_object = copy.deepcopy(stix_object_dict)
        
        # Focus on email anonymization
        for field_name, original_value in anonymized_stix_object.items():
            if 'email' in field_name.lower() or 'mail' in field_name.lower():
                if isinstance(original_value, str):
                    anonymized_stix_object[field_name] = anonymize_email_address(original_value, strategy_level)
        
        return anonymized_stix_object

    def get_effectiveness_score(self) -> float:
        return 0.88


class NoAnonymizationStrategy(AnonymizationStrategy):
    """Strategy that performs no anonymization"""
    
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 1.0, strategy_level: str = 'none') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        return copy.deepcopy(stix_object_dict)

    def get_effectiveness_score(self) -> float:
        return 1.0


class PartialAnonymizationStrategy(AnonymizationStrategy):
    """Strategy that selectively anonymizes fields"""
    
    PARTIAL_ANON_TARGET_FIELDS = [
        "name", "description", "pattern", "created_by_ref", "external_references",
        "contact_information", "aliases", "sample_refs", "goals",
        "primary_motivation", "secondary_motivations"
    ]

    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5, strategy_level: str = 'partial') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        anonymized_stix_object = copy.deepcopy(stix_object_dict)
        stix_type = anonymized_stix_object.get('type', 'unknown')

        for field_name, original_value in anonymized_stix_object.items():
            if field_name in self.PARTIAL_ANON_TARGET_FIELDS:
                anonymized_stix_object[field_name] = self._anonymize_field_value(
                    field_name, original_value, stix_type, strategy_level='partial'
                )
        return anonymized_stix_object

    def get_effectiveness_score(self) -> float:
        return 0.95


class FullAnonymizationStrategy(AnonymizationStrategy):
    """Strategy that aggressively anonymizes most fields"""
    
    def anonymize(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.0, strategy_level: str = 'full') -> Dict[str, Any]:
        stix_object_dict = self._get_stix_dict(stix_input)
        anonymized_stix_object = {}
        stix_type = stix_object_dict.get('type', 'unknown')

        # Preserve essential STIX structural fields
        for essential_field in ['id', 'type', 'spec_version', 'created', 'modified']:
            if essential_field in stix_object_dict:
                anonymized_stix_object[essential_field] = stix_object_dict[essential_field]

        # Handle type-specific structural fields
        if stix_type == "indicator":
            anonymized_stix_object["pattern_type"] = stix_object_dict.get("pattern_type", "stix")
            anonymized_stix_object["pattern"] = self._anonymize_field_value(
                "pattern", stix_object_dict.get("pattern", "[PATTERN_UNAVAILABLE]"), stix_type, strategy_level='full'
            )
            anonymized_stix_object["valid_from"] = stix_object_dict.get("valid_from", anonymized_stix_object["created"])
            if "valid_until" in stix_object_dict:
                anonymized_stix_object["valid_until"] = stix_object_dict["valid_until"]

        elif stix_type == "malware":
            anonymized_stix_object["is_family"] = stix_object_dict.get("is_family", False)

        elif stix_type == "identity":
            anonymized_stix_object["identity_class"] = stix_object_dict.get("identity_class", "unknown")
            anonymized_stix_object["name"] = self._anonymize_field_value(
                "name", stix_object_dict.get("name", "Unknown Identity"), stix_type, strategy_level='full'
            )

        # Anonymize remaining fields
        for field_name, original_value in stix_object_dict.items():
            if field_name not in anonymized_stix_object:
                anonymized_stix_object[field_name] = self._anonymize_field_value(
                    field_name, original_value, stix_type, strategy_level='full'
                )
        
        return anonymized_stix_object

    def get_effectiveness_score(self) -> float:
        return 0.80


class AnonymizationContext:
    """
    Context class that uses anonymization strategies
    """
    
    def __init__(self, strategy: AnonymizationStrategy = None):
        self._strategy = strategy or PartialAnonymizationStrategy()
    
    def set_strategy(self, strategy: AnonymizationStrategy):
        """Set the anonymization strategy"""
        self._strategy = strategy
    
    def anonymize_data(self, stix_input: Union[Dict[str, Any], str], trust_level: float = 0.5) -> Dict[str, Any]:
        """Anonymize data using the current strategy"""
        # Determine strategy level based on trust level
        if trust_level >= 0.8:
            strategy_level = 'none'
            if not isinstance(self._strategy, NoAnonymizationStrategy):
                self._strategy = NoAnonymizationStrategy()
        elif trust_level >= 0.4:
            strategy_level = 'partial'
            if not isinstance(self._strategy, PartialAnonymizationStrategy):
                self._strategy = PartialAnonymizationStrategy()
        else:
            strategy_level = 'full'
            if not isinstance(self._strategy, FullAnonymizationStrategy):
                self._strategy = FullAnonymizationStrategy()
        
        return self._strategy.anonymize(stix_input, trust_level, strategy_level)
    
    def get_effectiveness_score(self) -> float:
        """Get the effectiveness score of the current strategy"""
        return self._strategy.get_effectiveness_score()


class AnonymizationStrategyFactory:
    """Factory for creating anonymization strategies"""
    
    _strategies = {
        'none': NoAnonymizationStrategy,
        'partial': PartialAnonymizationStrategy,
        'full': FullAnonymizationStrategy,
        'domain': DomainAnonymizationStrategy,
        'ip': IPAddressAnonymizationStrategy,
        'email': EmailAnonymizationStrategy,
    }

    @classmethod
    def get_strategy(cls, strategy_name: str) -> AnonymizationStrategy:
        """Gets an instance of the specified anonymization strategy"""
        strategy_name_lower = strategy_name.lower()
        strategy_class = cls._strategies.get(strategy_name_lower)
        if not strategy_class:
            logger.warning(f"Unknown anonymization strategy requested: '{strategy_name}'. Falling back to default.")
            return cls.get_default_strategy()
        return strategy_class()

    @classmethod
    def get_default_strategy(cls) -> AnonymizationStrategy:
        """Gets the default anonymization strategy"""
        return PartialAnonymizationStrategy()

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """Registers a new anonymization strategy"""
        if not issubclass(strategy_class, AnonymizationStrategy):
            raise ValueError("Strategy class must inherit from AnonymizationStrategy.")
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def get_strategy_for_trust_level(cls, trust_level: float) -> AnonymizationStrategy:
        """Get appropriate strategy based on trust level"""
        if trust_level >= 0.8:
            return cls.get_strategy('none')
        elif trust_level >= 0.4:
            return cls.get_strategy('partial')
        else:
            return cls.get_strategy('full')