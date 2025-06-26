"""
Anonymization strategies implementation for the CRISP platform.
Implements the Strategy pattern for different data anonymization approaches.
"""
import hashlib
import re
from abc import ABC, abstractmethod
from .enums import AnonymizationLevel, DataType
from .exceptions import DataValidationError


class AnonymizationStrategy(ABC):
    """Abstract base class for anonymization strategies."""
    
    @abstractmethod
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize the given data according to the specified level."""
        pass
    
    @abstractmethod
    def validate_data(self, data: str) -> bool:
        """Validate that the data format is correct for this strategy."""
        pass


class IPAddressAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing IP addresses."""
    
    def validate_data(self, data: str) -> bool:
        """Validate IP address format."""
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        
        if re.match(ipv4_pattern, data) or re.match(ipv6_pattern, data):
            return True
        return False
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize IP address based on level."""
        if not self.validate_data(data):
            raise DataValidationError(f"Invalid IP address format: {data}")
        
        if level == AnonymizationLevel.NONE:
            return data
        elif level == AnonymizationLevel.PARTIAL:
            # For IPv4, mask last octet
            if '.' in data:
                parts = data.split('.')
                return f"{parts[0]}.{parts[1]}.{parts[2]}.XXX"
            # For IPv6, mask last 4 groups
            elif ':' in data:
                parts = data.split(':')
                return ':'.join(parts[:4]) + ':XXXX:XXXX:XXXX:XXXX'
        elif level == AnonymizationLevel.FULL:
            # Hash the IP address
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        
        return data


class DomainAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing domain names."""
    
    def validate_data(self, data: str) -> bool:
        """Validate domain name format."""
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, data))
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize domain based on level."""
        if not self.validate_data(data):
            raise DataValidationError(f"Invalid domain format: {data}")
        
        if level == AnonymizationLevel.NONE:
            return data
        elif level == AnonymizationLevel.PARTIAL:
            # Keep TLD, anonymize subdomain
            parts = data.split('.')
            if len(parts) > 1:
                return 'XXXX.' + '.'.join(parts[-2:])
            return 'XXXX'
        elif level == AnonymizationLevel.FULL:
            # Hash the domain
            return hashlib.sha256(data.encode()).hexdigest()[:16] + '.example'
        
        return data


class EmailAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing email addresses."""
    
    def validate_data(self, data: str) -> bool:
        """Validate email address format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, data))
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize email based on level."""
        if not self.validate_data(data):
            raise DataValidationError(f"Invalid email format: {data}")
        
        if level == AnonymizationLevel.NONE:
            return data
        elif level == AnonymizationLevel.PARTIAL:
            # Keep domain, anonymize username
            username, domain = data.split('@', 1)
            return f"XXXX@{domain}"
        elif level == AnonymizationLevel.FULL:
            # Hash the email
            return hashlib.sha256(data.encode()).hexdigest()[:16] + '@example.com'
        
        return data


class URLAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing URLs."""
    
    def validate_data(self, data: str) -> bool:
        """Validate URL format."""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, data))
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize URL based on level."""
        if not self.validate_data(data):
            raise DataValidationError(f"Invalid URL format: {data}")
        
        if level == AnonymizationLevel.NONE:
            return data
        elif level == AnonymizationLevel.PARTIAL:
            # Keep protocol and TLD, anonymize subdomain and path
            if '://' in data:
                protocol, rest = data.split('://', 1)
                domain_part = rest.split('/')[0]
                path_part = '/' + '/'.join(rest.split('/')[1:]) if '/' in rest else ''
                
                # Anonymize domain
                domain_strategy = DomainAnonymizationStrategy()
                anon_domain = domain_strategy.anonymize(domain_part, AnonymizationLevel.PARTIAL)
                
                return f"{protocol}://{anon_domain}/XXXX"
        elif level == AnonymizationLevel.FULL:
            # Hash the URL
            return 'https://' + hashlib.sha256(data.encode()).hexdigest()[:16] + '.example.com'
        
        return data


class FileHashAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing file hashes."""
    
    def validate_data(self, data: str) -> bool:
        """Validate file hash format."""
        # Support MD5, SHA1, SHA256
        md5_pattern = r'^[a-fA-F0-9]{32}$'
        sha1_pattern = r'^[a-fA-F0-9]{40}$'
        sha256_pattern = r'^[a-fA-F0-9]{64}$'
        
        return bool(re.match(md5_pattern, data) or 
                   re.match(sha1_pattern, data) or 
                   re.match(sha256_pattern, data))
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize file hash based on level."""
        if not self.validate_data(data):
            raise DataValidationError(f"Invalid file hash format: {data}")
        
        if level == AnonymizationLevel.NONE:
            return data
        elif level == AnonymizationLevel.PARTIAL:
            # Keep first 8 characters, mask the rest
            return data[:8] + 'X' * (len(data) - 8)
        elif level == AnonymizationLevel.FULL:
            # Generate new hash
            return hashlib.sha256(data.encode()).hexdigest()
        
        return data