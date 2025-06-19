from typing import Dict, List, Optional, Tuple
import re
import ipaddress
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
        self._strategies: Dict[DataType, AnonymizationStrategy] = {}
        self._default_strategy: Optional[AnonymizationStrategy] = None
        
        # Register default strategies
        self.register_strategy(DataType.IP_ADDRESS, IPAddressAnonymizationStrategy())
        self.register_strategy(DataType.DOMAIN, DomainAnonymizationStrategy())
        self.register_strategy(DataType.EMAIL, EmailAnonymizationStrategy())
        self.register_strategy(DataType.URL, URLAnonymizationStrategy())
    
    def register_strategy(self, data_type: DataType, strategy: AnonymizationStrategy):
        """Register a strategy for a specific data type"""
        self._strategies[data_type] = strategy
    
    def set_default_strategy(self, strategy: AnonymizationStrategy):
        """Set a default strategy for unknown data types"""
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
        
        # For IP addresses, validate before anonymizing
        if data_type == DataType.IP_ADDRESS:
            try:
                # Remove any zone identifier before validation
                ip_part = data.split('%')[0] if '%' in data else data
                ipaddress.ip_address(ip_part)
            except ValueError:
                # If it looks like an IP but isn't valid, return an error
                return f"INVALID IP ADDRESS: {data}"
        
        return self.execute_anonymization(data, data_type, level)
    
    def _detect_data_type(self, data: str) -> DataType:
        """Detect the type of data based on patterns"""
        data = data.strip()
        
        # Check for IPv6-like pattern (most specific first)
        # This catches addresses like 3393:3017:6301:1db6:9ebf:c2dc:bcf0:b99x
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