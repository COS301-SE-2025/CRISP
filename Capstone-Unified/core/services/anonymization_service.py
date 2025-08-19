"""
Anonymization Service - Anonymizes threat intelligence data based on trust levels
"""

import re
import logging

logger = logging.getLogger(__name__)


class AnonymizationService:
    """Service for anonymizing threat intelligence data"""
    
    def __init__(self):
        self.strategies = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default anonymization strategies"""
        self.strategies['email'] = EmailAnonymizationStrategy()
        self.strategies['domain'] = DomainAnonymizationStrategy()
        self.strategies['ip'] = IPAnonymizationStrategy()
        self.strategies['none'] = NoneAnonymizationStrategy()
    
    def register_strategy(self, name, strategy):
        """Register a new anonymization strategy"""
        self.strategies[name] = strategy
    
    def anonymize_stix_object(self, stix_obj, anonymization_level='partial'):
        """Anonymize a STIX object based on anonymization level"""
        if anonymization_level == 'none' or anonymization_level == 'minimal':
            return stix_obj
        
        # Make a copy to avoid modifying the original
        if isinstance(stix_obj, dict):
            anonymized = stix_obj.copy()
        else:
            anonymized = dict(stix_obj)
        
        # Anonymize pattern field for indicators
        if anonymized.get('type') == 'indicator' and 'pattern' in anonymized:
            pattern = anonymized['pattern']
            
            # Apply email anonymization
            if 'email-addr:value' in pattern:
                pattern = self.strategies['email'].anonymize(pattern)
            
            # Apply domain anonymization  
            if 'domain-name:value' in pattern:
                pattern = self.strategies['domain'].anonymize(pattern)
            
            # Apply IP anonymization
            if 'ipv4-addr:value' in pattern or 'ipv6-addr:value' in pattern:
                pattern = self.strategies['ip'].anonymize(pattern)
            
            anonymized['pattern'] = pattern
            
            # Keep original ID for object-specific requests but mark as anonymized
            # anonymized['id'] = f"indicator--{uuid.uuid4()}" # Disabled to maintain ID consistency
        
        # Add anonymization metadata
        anonymized['x_crisp_anonymized'] = True
        anonymized['x_anonymized_by'] = 'CRISP Anonymization Service'
        
        return anonymized


class EmailAnonymizationStrategy:
    """Strategy for anonymizing email addresses"""
    
    def anonymize(self, pattern):
        """Anonymize email addresses in STIX patterns"""
        # Pattern to match email addresses in STIX patterns
        email_pattern = r"email-addr:value\s*=\s*'([^']+)'"
        
        def anonymize_email(match):
            email = match.group(1)
            # Generate anonymized email
            domain_part = email.split('@')[-1] if '@' in email else 'unknown.com'
            return f"email-addr:value = '[ANON:email@{domain_part}]'"
        
        return re.sub(email_pattern, anonymize_email, pattern)


class DomainAnonymizationStrategy:
    """Strategy for anonymizing domain names"""
    
    def anonymize(self, pattern):
        """Anonymize domain names in STIX patterns"""
        # Pattern to match domain names in STIX patterns
        domain_pattern = r"domain-name:value\s*=\s*'([^']+)'"
        
        def anonymize_domain(match):
            domain = match.group(1)
            # Generate anonymized domain
            return f"domain-name:value = '[ANON:{domain[:3]}****]'"
        
        return re.sub(domain_pattern, anonymize_domain, pattern)


class IPAnonymizationStrategy:
    """Strategy for anonymizing IP addresses"""
    
    def anonymize(self, pattern):
        """Anonymize IP addresses in STIX patterns"""
        # Pattern to match IPv4 addresses in STIX patterns
        ipv4_pattern = r"ipv4-addr:value\s*=\s*'([^']+)'"
        
        def anonymize_ipv4(match):
            ip = match.group(1)
            # Anonymize last octet
            parts = ip.split('.')
            if len(parts) == 4:
                return f"ipv4-addr:value = '[ANON:{parts[0]}.{parts[1]}.{parts[2]}.XXX]'"
            return f"ipv4-addr:value = '[ANON:IP]'"
        
        return re.sub(ipv4_pattern, anonymize_ipv4, pattern)


class NoneAnonymizationStrategy:
    """Strategy that does not anonymize data"""
    
    def anonymize(self, data):
        """Return data unchanged"""
        return data