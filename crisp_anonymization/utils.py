import hashlib
import random
import string
from typing import List, Tuple
from .enums import AnonymizationLevel, DataType


class AnonymizationUtils:
    """Utility class for common anonymization operations"""
    
    @staticmethod
    def generate_consistent_hash(data: str, length: int = 8) -> str:
        """Generate a consistent hash for the given data"""
        return hashlib.md5(data.encode()).hexdigest()[:length]
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """Generate a random string of specified length"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def mask_string(data: str, visible_chars: int = 2, mask_char: str = 'x') -> str:
        """Mask a string, showing only the first N characters"""
        if len(data) <= visible_chars:
            return mask_char * len(data)
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)
    
    @staticmethod
    def categorize_tld(tld: str) -> str:
        """Categorize a top-level domain"""
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
        """Validate if data matches the expected format for its type"""
        import re
        import ipaddress
        
        try:
            if data_type == DataType.IP_ADDRESS:
                ipaddress.ip_address(data)
                return True
            elif data_type == DataType.EMAIL:
                return '@' in data and re.match(r'^[^@]+@[^@]+\.[^@]+$', data) is not None
            elif data_type == DataType.URL:
                return data.startswith(('http://', 'https://'))
            elif data_type == DataType.DOMAIN:
                return '.' in data and not data.startswith(('http://', 'https://'))
            else:
                return True  # For other types, assume valid
        except ValueError:
            return False