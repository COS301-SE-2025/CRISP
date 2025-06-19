from abc import ABC, abstractmethod
import re
import hashlib
import ipaddress
try:
    from .enums import AnonymizationLevel, DataType
    from .exceptions import DataValidationError
except ImportError:
    from enums import AnonymizationLevel, DataType
    # If exceptions.py is not imported, define the exception here
    class DataValidationError(Exception):
        """Raised when data doesn't match the expected format"""
        pass

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
            
        Raises:
            DataValidationError: If the data is not valid for this strategy
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
    
    @abstractmethod
    def validate(self, data: str) -> bool:
        """
        Validate that the data is in the correct format for this strategy
        
        Args:
            data: The data to validate
            
        Returns:
            True if the data is valid, False otherwise
        """
        pass


class IPAddressAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing IP addresses"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """
        Anonymize IP address based on the level
        
        Args:
            data: IP address to anonymize
            level: Anonymization level
            
        Returns:
            Anonymized IP address
            
        Raises:
            DataValidationError: If the data is not a valid IP address
        """
        # Validate input first
        if not self.validate(data):
            raise DataValidationError(f"Invalid IP address format: {data}")
            
        # Handle zone identifiers in IPv6 (like fe80::1%eth0)
        zone_id = None
        ip_part = data
        
        if '%' in data and ':' in data:  # Likely IPv6 with zone ID
            ip_part, zone_id = data.split('%', 1)
        
        # Parse the IP address
        ip = ipaddress.ip_address(ip_part)
        
        if level == AnonymizationLevel.NONE:
            result = str(ip)
            if zone_id:
                result = f"{result}%{zone_id}"
            return result
        
        # Handle IPv4 addresses
        if ip.version == 4:
            octets = str(ip).split('.')
            
            if level == AnonymizationLevel.LOW:
                octets[-1] = 'x'
                return '.'.join(octets)
            elif level == AnonymizationLevel.MEDIUM:
                octets[-2:] = ['x', 'x']
                return '.'.join(octets)
            elif level == AnonymizationLevel.HIGH:
                return f"{octets[0]}.x.x.x"
            elif level == AnonymizationLevel.FULL:
                hash_obj = hashlib.md5(str(ip).encode())
                return f"anon-ipv4-{hash_obj.hexdigest()[:8]}"
        
        # Handle IPv6 addresses
        else:
            # Convert to canonical form
            canonical = ip.exploded
            segments = canonical.split(':')
            
            if level == AnonymizationLevel.LOW:
                # Anonymize last 16 bits (last segment)
                segments[-1] = 'xxxx'
                result = ':'.join(segments)
            elif level == AnonymizationLevel.MEDIUM:
                # Anonymize last 32 bits (last two segments)
                segments[-2:] = ['xxxx', 'xxxx']
                result = ':'.join(segments)
            elif level == AnonymizationLevel.HIGH:
                # Keep only first 64 bits (first four segments)
                result = ':'.join(segments[:4]) + '::xxxx'
            elif level == AnonymizationLevel.FULL:
                hash_obj = hashlib.md5(str(ip).encode())
                result = f"anon-ipv6-{hash_obj.hexdigest()[:8]}"
            else:
                result = str(ip)
            
            # Reattach zone identifier if present and not FULL anonymization
            if zone_id and level != AnonymizationLevel.FULL:
                result = f"{result}%{zone_id}"
            
            return result
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.IP_ADDRESS
    
    def validate(self, data: str) -> bool:
        """
        Validate that the data is a valid IP address
        
        Args:
            data: The data to validate
            
        Returns:
            True if the data is a valid IP address, False otherwise
        """
        try:
            # Handle IPv6 addresses with zone identifiers
            if '%' in data and ':' in data:
                ip_part, _ = data.split('%', 1)
                ipaddress.ip_address(ip_part)
            else:
                ipaddress.ip_address(data)
            return True
        except ValueError:
            return False


class DomainAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing domain names"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """
        Anonymize domain based on the level
        
        Args:
            data: Domain to anonymize
            level: Anonymization level
            
        Returns:
            Anonymized domain
            
        Raises:
            DataValidationError: If the data is not a valid domain
        """
        # Validate input first
        if not self.validate(data):
            raise DataValidationError(f"Invalid domain format: {data}")
            
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
        
        return domain
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.DOMAIN
    
    def validate(self, data: str) -> bool:
        """
        Validate that the data is a valid domain name
        
        Args:
            data: The data to validate
            
        Returns:
            True if the data is a valid domain name, False otherwise
        """
        # Basic domain validation
        domain = data.lower().strip()
        
        # Simple domain regex (can be made more comprehensive)
        domain_regex = r'^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
        
        # Special case for single-label domains like 'localhost'
        single_label_regex = r'^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
        
        return bool(re.match(domain_regex, domain) or re.match(single_label_regex, domain))


class EmailAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing email addresses"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """
        Anonymize email based on the level
        
        Args:
            data: Email to anonymize
            level: Anonymization level
            
        Returns:
            Anonymized email
            
        Raises:
            DataValidationError: If the data is not a valid email
        """
        # Validate input first
        if not self.validate(data):
            raise DataValidationError(f"Invalid email format: {data}")
            
        email = data.lower().strip()
        
        if level == AnonymizationLevel.NONE:
            return email
        
        local_part, domain_part = email.split('@', 1)
        
        if level == AnonymizationLevel.LOW:
            # Anonymize local part but keep domain
            return f"user-{hashlib.md5(local_part.encode()).hexdigest()[:6]}@{domain_part}"
        elif level == AnonymizationLevel.MEDIUM:
            # Anonymize local part and partially anonymize domain
            domain_strategy = DomainAnonymizationStrategy()
            try:
                anon_domain = domain_strategy.anonymize(domain_part, AnonymizationLevel.LOW)
                return f"user-{hashlib.md5(local_part.encode()).hexdigest()[:6]}@{anon_domain}"
            except DataValidationError:
                # If domain is invalid, just use a simplified approach
                return f"user-{hashlib.md5(local_part.encode()).hexdigest()[:6]}@*.domain"
        elif level == AnonymizationLevel.HIGH:
            # Keep only domain category
            domain_strategy = DomainAnonymizationStrategy()
            try:
                anon_domain = domain_strategy.anonymize(domain_part, AnonymizationLevel.HIGH)
                return f"user@{anon_domain}"
            except DataValidationError:
                # If domain is invalid, just use a simplified approach
                return "user@*.other"
        elif level == AnonymizationLevel.FULL:
            # Complete anonymization
            hash_obj = hashlib.md5(email.encode())
            return f"anon-user-{hash_obj.hexdigest()[:8]}@example.com"
        
        return email
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.EMAIL
    
    def validate(self, data: str) -> bool:
        """
        Validate that the data is a valid email address
        
        Args:
            data: The data to validate
            
        Returns:
            True if the data is a valid email address, False otherwise
        """
        # Basic email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, data.strip()))


class URLAnonymizationStrategy(AnonymizationStrategy):
    """Strategy for anonymizing URLs"""
    
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """
        Anonymize URL based on the level
        
        Args:
            data: URL to anonymize
            level: Anonymization level
            
        Returns:
            Anonymized URL
            
        Raises:
            DataValidationError: If the data is not a valid URL
        """
        # Validate input first
        if not self.validate(data):
            raise DataValidationError(f"Invalid URL format: {data}")
            
        url = data.strip()
        
        if level == AnonymizationLevel.NONE:
            return url
        
        # Extract domain from URL
        domain_match = re.search(r'https?://([^/]+)', url)
        domain = domain_match.group(1)  # We know this exists because validate() passed
        protocol = "https://" if url.startswith("https://") else "http://"
        
        domain_strategy = DomainAnonymizationStrategy()
        
        if level == AnonymizationLevel.LOW:
            try:
                anon_domain = domain_strategy.anonymize(domain, AnonymizationLevel.LOW)
                return f"{protocol}{anon_domain}/[path-removed]"
            except DataValidationError:
                # If domain is invalid, just use a simplified approach
                return f"{protocol}*.domain/[path-removed]"
        elif level == AnonymizationLevel.MEDIUM:
            try:
                anon_domain = domain_strategy.anonymize(domain, AnonymizationLevel.MEDIUM)
                return f"{protocol}{anon_domain}"
            except DataValidationError:
                # If domain is invalid, just use a simplified approach
                return f"{protocol}*.domain"
        elif level == AnonymizationLevel.HIGH:
            try:
                anon_domain = domain_strategy.anonymize(domain, AnonymizationLevel.HIGH)
                return f"{protocol}{anon_domain}"
            except DataValidationError:
                # If domain is invalid, just use a simplified approach
                return f"{protocol}*.other"
        elif level == AnonymizationLevel.FULL:
            # Complete anonymization
            hash_obj = hashlib.md5(url.encode())
            return f"https://anon-url-{hash_obj.hexdigest()[:8]}.example"
        
        return url
    
    def can_handle(self, data_type: DataType) -> bool:
        return data_type == DataType.URL
    
    def validate(self, data: str) -> bool:
        """
        Validate that the data is a valid URL
        
        Args:
            data: The data to validate
            
        Returns:
            True if the data is a valid URL, False otherwise
        """
        # Basic URL validation - require http/https protocol
        url_regex = r'^https?://[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*(/[^\s]*)?$'
        return bool(re.match(url_regex, data.strip()))


# Example usage for testing validation
if __name__ == "__main__":
    ip_strategy = IPAddressAnonymizationStrategy()
    
    # Test valid IPs
    valid_ips = [
        "192.168.1.1",
        "2001:db8::1",
        "fe80::1%eth0"
    ]
    
    # Test invalid IPs
    invalid_ips = [
        "256.256.256.256",
        "192.168.1",
        "not-an-ip",
        "192.168.1.1.1"
    ]
    
    print("Testing IP validation:")
    for ip in valid_ips:
        print(f"  {ip}: {'Valid' if ip_strategy.validate(ip) else 'Invalid'}")
    
    for ip in invalid_ips:
        print(f"  {ip}: {'Valid' if ip_strategy.validate(ip) else 'Invalid'}")
    
    print("\nTesting IP anonymization with validation:")
    for ip in valid_ips:
        try:
            result = ip_strategy.anonymize(ip, AnonymizationLevel.MEDIUM)
            print(f"  {ip} → {result}")
        except DataValidationError as e:
            print(f"  {ip} → Error: {e}")
    
    for ip in invalid_ips:
        try:
            result = ip_strategy.anonymize(ip, AnonymizationLevel.MEDIUM)
            print(f"  {ip} → {result}")
        except DataValidationError as e:
            print(f"  {ip} → Error: {e}")