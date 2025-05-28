
from typing import Dict, List, Optional
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
except ImportError:
    from enums import AnonymizationLevel, DataType
    from strategies import (
        AnonymizationStrategy,
        IPAddressAnonymizationStrategy,
        DomainAnonymizationStrategy,
        EmailAnonymizationStrategy,
        URLAnonymizationStrategy
    )


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
        return self.execute_anonymization(data, data_type, level)
    
    def _detect_data_type(self, data: str) -> DataType:
        """Detect the type of data based on patterns"""
        data = data.strip()
        
        # Check for IP address
        try:
            ipaddress.ip_address(data)
            return DataType.IP_ADDRESS
        except ValueError:
            pass
        
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
    
    def bulk_anonymize(self, data_items: List[tuple], level: AnonymizationLevel) -> List[str]:
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