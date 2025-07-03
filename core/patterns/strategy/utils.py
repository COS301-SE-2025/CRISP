"""
Utility functions for the CRISP Anonymization System
"""

import hashlib
import random
import string
import re
from typing import List, Tuple

try:
    from .enums import AnonymizationLevel, DataType
except ImportError:
    from crisp_anonymization.enums import AnonymizationLevel, DataType


class AnonymizationUtils:
    """Utility class for common anonymization operations"""
    
    @staticmethod
    def generate_consistent_hash(data: str, length: int = 8) -> str:
        """
        Generate a consistent hash for the given data
        
        Args:
            data: The data to hash
            length: The length of the hash to return
            
        Returns:
            A consistent hash of the specified length
        """
        return hashlib.md5(data.encode()).hexdigest()[:length]
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """
        Generate a random string of specified length
        
        Args:
            length: The length of the string to generate
            
        Returns:
            A random string
        """
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def mask_string(data: str, visible_chars: int = 2, mask_char: str = 'x') -> str:
        """
        Mask a string, showing only the first N characters
        
        Args:
            data: The string to mask
            visible_chars: Number of characters to leave visible
            mask_char: Character to use for masking
            
        Returns:
            Masked string
        """
        if len(data) <= visible_chars:
            return mask_char * len(data)
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)
    
    @staticmethod
    def categorize_tld(tld: str) -> str:
        """
        Categorize a top-level domain
        
        Args:
            tld: The TLD to categorize
            
        Returns:
            Category of the TLD
        """
        commercial = ['com', 'biz', 'shop', 'store']
        educational = ['edu', 'ac', 'school']
        government = ['gov', 'mil', 'police']
        organization = ['org', 'net', 'ngo']
        
        tld = tld.lower()
        if tld in commercial:
            return "commercial"
        elif tld in educational:
            return "educational"
        elif tld in government:
            return "government"
        elif tld in organization:
            return "organization"
        else:
            return "other"
    
    @staticmethod
    def validate_data_format(data: str, data_type: DataType) -> bool:
        """
        Validate if data matches the expected format for its type
        
        Args:
            data: The data to validate
            data_type: The expected data type
            
        Returns:
            True if the data matches the expected format, False otherwise
        """
        import re
        import ipaddress
        
        try:
            if data_type == DataType.IP_ADDRESS:
                # Handle IPv6 addresses with zone identifiers
                if '%' in data and ':' in data:
                    ip_part, _ = data.split('%', 1)
                    ipaddress.ip_address(ip_part)
                else:
                    ipaddress.ip_address(data)
                return True
            elif data_type == DataType.EMAIL:
                return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data))
            elif data_type == DataType.URL:
                return data.startswith(('http://', 'https://'))
            elif data_type == DataType.DOMAIN:
                # Basic domain validation
                domain_regex = r'^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
                single_label_regex = r'^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
                return bool(re.match(domain_regex, data.lower().strip()) or 
                            re.match(single_label_regex, data.lower().strip()))
            else:
                return True  # For other types, assume valid
        except ValueError:
            return False