"""
Anonymization Strategy Pattern Implementation
Following CRISP design specification precisely.
"""
from abc import ABC, abstractmethod
import re
import hashlib
import ipaddress
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AnonymizationStrategy(ABC):
    """
    Abstract base class for anonymization strategies.
    Defines the interface for all anonymization implementations.
    """
    
    @abstractmethod
    def anonymize(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Anonymize a STIX object based on trust level.
        
        Args:
            stix_object: The STIX object to anonymize
            trust_level: Trust level between organizations (0.0 to 1.0)
            
        Returns:
            Anonymized STIX object
        """
        pass


class DomainAnonymizationStrategy(AnonymizationStrategy):
    """
    Strategy for anonymizing domain indicators based on trust level.
    """
    
    def anonymize(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Anonymize domain indicators in STIX objects.
        
        Trust levels:
        - High (0.8+): No anonymization
        - Medium (0.4-0.8): Partial anonymization (domain suffix)
        - Low (0.0-0.4): Full anonymization (hash)
        """
        if trust_level >= 0.8:
            return stix_object
        
        anonymized_obj = stix_object.copy()
        
        # Anonymize domain patterns in indicators
        if anonymized_obj.get('type') == 'indicator' and 'pattern' in anonymized_obj:
            pattern = anonymized_obj['pattern']
            
            # Find domain patterns: [domain-name:value = 'example.com']
            domain_pattern = r"\[domain-name:value\s*=\s*'([^']+)'\]"
            matches = re.findall(domain_pattern, pattern)
            
            for domain in matches:
                if trust_level >= 0.4:  # Medium trust - partial anonymization
                    anonymized_domain = self._partial_anonymize_domain(domain)
                else:  # Low trust - full anonymization
                    anonymized_domain = self._full_anonymize_domain(domain)
                
                pattern = pattern.replace(f"'{domain}'", f"'{anonymized_domain}'")
            
            anonymized_obj['pattern'] = pattern
        
        # Mark as anonymized
        anonymized_obj['x_crisp_anonymized'] = True
        anonymized_obj['x_crisp_trust_level'] = trust_level
        
        return anonymized_obj
    
    def _partial_anonymize_domain(self, domain: str) -> str:
        """
        Partially anonymize domain by keeping only the top-level domain.
        """
        parts = domain.split('.')
        if len(parts) > 2:
            return f"[REDACTED].{'.'.join(parts[-2:])}"
        elif len(parts) == 2:
            return f"[REDACTED].{parts[-1]}"
        else:
            return "[REDACTED]"
    
    def _full_anonymize_domain(self, domain: str) -> str:
        """
        Fully anonymize domain using hash.
        """
        hash_obj = hashlib.sha256(domain.encode())
        return f"anon-{hash_obj.hexdigest()[:16]}.example"


class IPAddressAnonymizationStrategy(AnonymizationStrategy):
    """
    Strategy for anonymizing IP address indicators based on trust level.
    """
    
    def anonymize(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Anonymize IP address indicators in STIX objects.
        
        Trust levels:
        - High (0.8+): No anonymization
        - Medium (0.4-0.8): Partial anonymization (subnet)
        - Low (0.0-0.4): Full anonymization (hash)
        """
        if trust_level >= 0.8:
            return stix_object
        
        anonymized_obj = stix_object.copy()
        
        # Anonymize IP patterns in indicators
        if anonymized_obj.get('type') == 'indicator' and 'pattern' in anonymized_obj:
            pattern = anonymized_obj['pattern']
            
            # Find IPv4 patterns: [ipv4-addr:value = '192.168.1.1']
            ipv4_pattern = r"\[ipv4-addr:value\s*=\s*'([^']+)'\]"
            matches = re.findall(ipv4_pattern, pattern)
            
            for ip in matches:
                if trust_level >= 0.4:  # Medium trust - partial anonymization
                    anonymized_ip = self._partial_anonymize_ipv4(ip)
                else:  # Low trust - full anonymization
                    anonymized_ip = self._full_anonymize_ipv4(ip)
                
                pattern = pattern.replace(f"'{ip}'", f"'{anonymized_ip}'")
            
            # Find IPv6 patterns: [ipv6-addr:value = '2001:db8::1']
            ipv6_pattern = r"\[ipv6-addr:value\s*=\s*'([^']+)'\]"
            matches = re.findall(ipv6_pattern, pattern)
            
            for ip in matches:
                if trust_level >= 0.4:  # Medium trust - partial anonymization
                    anonymized_ip = self._partial_anonymize_ipv6(ip)
                else:  # Low trust - full anonymization
                    anonymized_ip = self._full_anonymize_ipv6(ip)
                
                pattern = pattern.replace(f"'{ip}'", f"'{anonymized_ip}'")
            
            anonymized_obj['pattern'] = pattern
        
        # Mark as anonymized
        anonymized_obj['x_crisp_anonymized'] = True
        anonymized_obj['x_crisp_trust_level'] = trust_level
        
        return anonymized_obj
    
    def _partial_anonymize_ipv4(self, ip: str) -> str:
        """
        Partially anonymize IPv4 by zeroing out last octet.
        """
        try:
            addr = ipaddress.IPv4Address(ip)
            network = ipaddress.IPv4Network(f"{addr}/24", strict=False)
            return f"{network.network_address}/24"
        except ipaddress.AddressValueError:
            return "0.0.0.0/24"
    
    def _full_anonymize_ipv4(self, ip: str) -> str:
        """
        Fully anonymize IPv4 using hash.
        """
        hash_obj = hashlib.sha256(ip.encode())
        return f"10.{int(hash_obj.hexdigest()[:2], 16)}.{int(hash_obj.hexdigest()[2:4], 16)}.{int(hash_obj.hexdigest()[4:6], 16)}"
    
    def _partial_anonymize_ipv6(self, ip: str) -> str:
        """
        Partially anonymize IPv6 by keeping only prefix.
        """
        try:
            addr = ipaddress.IPv6Address(ip)
            network = ipaddress.IPv6Network(f"{addr}/64", strict=False)
            return f"{network.network_address}/64"
        except ipaddress.AddressValueError:
            return "::/64"
    
    def _full_anonymize_ipv6(self, ip: str) -> str:
        """
        Fully anonymize IPv6 using hash.
        """
        hash_obj = hashlib.sha256(ip.encode())
        return f"2001:db8::{hash_obj.hexdigest()[:4]}:{hash_obj.hexdigest()[4:8]}::{hash_obj.hexdigest()[8:12]}"


class EmailAnonymizationStrategy(AnonymizationStrategy):
    """
    Strategy for anonymizing email address indicators based on trust level.
    """
    
    def anonymize(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Anonymize email address indicators in STIX objects.
        
        Trust levels:
        - High (0.8+): No anonymization
        - Medium (0.4-0.8): Partial anonymization (domain only)
        - Low (0.0-0.4): Full anonymization (hash)
        """
        if trust_level >= 0.8:
            return stix_object
        
        anonymized_obj = stix_object.copy()
        
        # Anonymize email patterns in indicators
        if anonymized_obj.get('type') == 'indicator' and 'pattern' in anonymized_obj:
            pattern = anonymized_obj['pattern']
            
            # Find email patterns: [email-addr:value = 'user@example.com']
            email_pattern = r"\[email-addr:value\s*=\s*'([^']+)'\]"
            matches = re.findall(email_pattern, pattern)
            
            for email in matches:
                if trust_level >= 0.4:  # Medium trust - partial anonymization
                    anonymized_email = self._partial_anonymize_email(email)
                else:  # Low trust - full anonymization
                    anonymized_email = self._full_anonymize_email(email)
                
                pattern = pattern.replace(f"'{email}'", f"'{anonymized_email}'")
            
            anonymized_obj['pattern'] = pattern
        
        # Mark as anonymized
        anonymized_obj['x_crisp_anonymized'] = True
        anonymized_obj['x_crisp_trust_level'] = trust_level
        
        return anonymized_obj
    
    def _partial_anonymize_email(self, email: str) -> str:
        """
        Partially anonymize email by keeping only domain.
        """
        if '@' in email:
            domain = email.split('@')[1]
            return f"[REDACTED]@{domain}"
        else:
            return "[REDACTED]@example.com"
    
    def _full_anonymize_email(self, email: str) -> str:
        """
        Fully anonymize email using hash.
        """
        hash_obj = hashlib.sha256(email.encode())
        return f"anon-{hash_obj.hexdigest()[:16]}@example.com"


class NoAnonymizationStrategy(AnonymizationStrategy):
    """
    Strategy that performs no anonymization (for high trust scenarios).
    """
    
    def anonymize(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Return the object unchanged.
        """
        return stix_object


class AnonymizationContext:
    """
    Context class that uses strategies for anonymization.
    Implements the Strategy pattern context.
    """
    
    def __init__(self, strategy: AnonymizationStrategy):
        """
        Initialize with a specific anonymization strategy.
        
        Args:
            strategy: The anonymization strategy to use
        """
        self.strategy = strategy
    
    def set_strategy(self, strategy: AnonymizationStrategy):
        """
        Change the anonymization strategy at runtime.
        
        Args:
            strategy: The new anonymization strategy to use
        """
        self.strategy = strategy
    
    def anonymize_object(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Anonymize a STIX object using the current strategy.
        
        Args:
            stix_object: The STIX object to anonymize
            trust_level: Trust level between organizations
            
        Returns:
            Anonymized STIX object
        """
        return self.strategy.anonymize(stix_object, trust_level)


class AnonymizationStrategyFactory:
    """
    Factory for creating anonymization strategies.
    """
    
    _strategies = {
        'domain': DomainAnonymizationStrategy,
        'ip': IPAddressAnonymizationStrategy,
        'email': EmailAnonymizationStrategy,
        'none': NoAnonymizationStrategy,
    }
    
    @classmethod
    def get_strategy(cls, strategy_name: str) -> AnonymizationStrategy:
        """
        Get an anonymization strategy by name.
        
        Args:
            strategy_name: Name of the strategy to create
            
        Returns:
            AnonymizationStrategy instance
            
        Raises:
            ValueError: If strategy name is not recognized
        """
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown anonymization strategy: {strategy_name}")
        
        return cls._strategies[strategy_name]()
    
    @classmethod
    def create_composite_strategy(cls, stix_object: Dict[str, Any], trust_level: float) -> AnonymizationStrategy:
        """
        Create a composite strategy based on the STIX object type and content.
        
        Args:
            stix_object: The STIX object to determine strategy for
            trust_level: Trust level between organizations
            
        Returns:
            Appropriate AnonymizationStrategy instance
        """
        if trust_level >= 0.8:
            return cls.get_strategy('none')
        
        # Determine strategy based on object content
        if stix_object.get('type') == 'indicator' and 'pattern' in stix_object:
            pattern = stix_object['pattern'].lower()
            
            if 'domain-name' in pattern:
                return cls.get_strategy('domain')
            elif 'ipv4-addr' in pattern or 'ipv6-addr' in pattern:
                return cls.get_strategy('ip')
            elif 'email-addr' in pattern:
                return cls.get_strategy('email')
        
        # Default to no anonymization for unknown types
        return cls.get_strategy('none')