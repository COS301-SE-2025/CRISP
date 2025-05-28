
from abc import ABC, abstractmethod
import re
import hashlib
import ipaddress
try:
    from .enums import AnonymizationLevel, DataType
except ImportError:
    from enums import AnonymizationLevel, DataType

class AnonymizationStrategy(ABC):
    """Abstract base class for anonymization strategies"""
    
    @abstractmethod
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """
        Anonymize the given data according to the specified level
        
        Args:
            data: The data to anonymize
            level: The level of anonymization to apply
            
        Returns:
            The anonymized data
        """
        pass
    
    @abstractmethod
    def can_handle(self, data_type: DataType) -> bool:
        """
        Check if this strategy can handle the given data type
        
        Args:
            data_type: The type of data to check
            
        Returns:
            True if this strategy can handle the data type
        """
        pass


class IPAddressAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing IP addresses"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize IP address based on the level"""
        try:
            ip = ipaddress.ip_address(data)
            
            if level == AnonymizationLevel.NONE:
                return str(ip)
            elif level == AnonymizationLevel.LOW:
                # Anonymize last octet for IPv4, last 16 bits for IPv6
                if ip.version == 4:
                    octets = str(ip).split('.')
                    octets[-1] = 'x'
                    return '.'.join(octets)
                else:  # IPv6
                    return str(ip)[:-1] + 'xxxx'

            elif level == AnonymizationLevel.MEDIUM:
                # Anonymize last two octets for IPv4, last 32 bits for IPv6
                if ip.version == 4:
                    octets = str(ip).split('.')
                    octets[-2:] = ['x', 'x']
                    return '.'.join(octets)
                else:  # IPv6
                    return str(ip)[:-8] + 'xxxxxxxx'
            elif level == AnonymizationLevel.HIGH:
                # Keep only first octet for IPv4, first 64 bits for IPv6
                if ip.version == 4:
                    octets = str(ip).split('.')
                    return f"{octets[0]}.x.x.x"
                else:  # IPv6
                    return str(ip)[:19] + '::xxxx'
            elif level == AnonymizationLevel.FULL:
                # Complete anonymization with consistent hash
                hash_obj = hashlib.md5(data.encode())
                if ip.version == 4:
                    return f"anon-ipv4-{hash_obj.hexdigest()[:8]}"
                else:
                    return f"anon-ipv6-{hash_obj.hexdigest()[:8]}"
                    
        except ValueError:
            # Not a valid IP address, return generic anonymization
            return self._generic_anonymize(data, level)
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.IP_ADDRESS
    
    def _generic_anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Fallback for invalid IP addresses"""
        if level == AnonymizationLevel.FULL:
            hash_obj = hashlib.md5(data.encode())
            return f"anon-invalid-ip-{hash_obj.hexdigest()[:8]}"
        return "invalid-ip"


class DomainAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing domain names"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize domain based on the level"""
        domain = data.lower().strip()
        
        if level == AnonymizationLevel.NONE:
            return domain
        elif level == AnonymizationLevel.LOW:
            # Keep TLD and one level up
            parts = domain.split('.')
            if len(parts) >= 2:
                return f"*.{'.'.join(parts[-2:])}"
            return f"*.{domain}"
        elif level == AnonymizationLevel.MEDIUM:
            # Keep only TLD
            parts = domain.split('.')
            if len(parts) >= 2:
                return f"*.{parts[-1]}"
            return "*.unknown"
        elif level == AnonymizationLevel.HIGH:
            # Keep only general category
            tld = domain.split('.')[-1] if '.' in domain else "unknown"
            category = "commercial" if tld in ['com', 'biz'] else \
                      "educational" if tld in ['edu', 'ac'] else \
                      "government" if tld in ['gov', 'mil'] else \
                      "organization" if tld in ['org', 'net'] else "other"
            return f"*.{category}"
        elif level == AnonymizationLevel.FULL:
            # Complete anonymization with consistent hash
            hash_obj = hashlib.md5(domain.encode())
            return f"anon-domain-{hash_obj.hexdigest()[:8]}.example"
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.DOMAIN


class EmailAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing email addresses"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize email based on the level"""
        email = data.lower().strip()
        
        if level == AnonymizationLevel.NONE:
            return email
        
        if '@' not in email:
            return self._generic_anonymize(email, level)
        
        local_part, domain_part = email.split('@', 1)
        
        if level == AnonymizationLevel.LOW:
            # Anonymize local part but keep domain
            return f"user-{hashlib.md5(local_part.encode()).hexdigest()[:6]}@{domain_part}"
        elif level == AnonymizationLevel.MEDIUM:
            # Anonymize local part and partially anonymize domain
            domain_strategy = DomainAnonymizationStrategy()
            anon_domain = domain_strategy.anonymize(domain_part, AnonymizationLevel.LOW)
            return f"user-{hashlib.md5(local_part.encode()).hexdigest()[:6]}@{anon_domain}"
        elif level == AnonymizationLevel.HIGH:
            # Keep only domain category
            domain_strategy = DomainAnonymizationStrategy()
            anon_domain = domain_strategy.anonymize(domain_part, AnonymizationLevel.HIGH)
            return f"user@{anon_domain}"
        elif level == AnonymizationLevel.FULL:
            # Complete anonymization
            hash_obj = hashlib.md5(email.encode())
            return f"anon-user-{hash_obj.hexdigest()[:8]}@example.com"
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.EMAIL
    
    def _generic_anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Fallback for invalid email addresses"""
        if level == AnonymizationLevel.FULL:
            hash_obj = hashlib.md5(data.encode())
            return f"anon-invalid-email-{hash_obj.hexdigest()[:8]}"
        return "invalid-email"


class URLAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing URLs"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize URL based on the level"""
        url = data.strip()
        
        if level == AnonymizationLevel.NONE:
            return url
        
        # Extract domain from URL
        domain_match = re.search(r'https?://([^/]+)', url)
        if not domain_match:
            return self._generic_anonymize(url, level)
        
        domain = domain_match.group(1)
        protocol = "https://" if url.startswith("https://") else "http://"
        
        domain_strategy = DomainAnonymizationStrategy()
        
        if level == AnonymizationLevel.LOW:
            anon_domain = domain_strategy.anonymize(domain, AnonymizationLevel.LOW)
            return f"{protocol}{anon_domain}/[path-removed]"
        elif level == AnonymizationLevel.MEDIUM:
            anon_domain = domain_strategy.anonymize(domain, AnonymizationLevel.MEDIUM)
            return f"{protocol}{anon_domain}"
        elif level == AnonymizationLevel.HIGH:
            anon_domain = domain_strategy.anonymize(domain, AnonymizationLevel.HIGH)
            return f"{protocol}{anon_domain}"
        elif level == AnonymizationLevel.FULL:
            hash_obj = hashlib.md5(url.encode())
            return f"https://anon-url-{hash_obj.hexdigest()[:8]}.example"
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.URL
    
    def _generic_anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Fallback for invalid URLs"""
        if level == AnonymizationLevel.FULL:
            hash_obj = hashlib.md5(data.encode())
            return f"anon-invalid-url-{hash_obj.hexdigest()[:8]}"
        return "invalid-url"