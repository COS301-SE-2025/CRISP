"""
Enumeration definitions for the CRISP Anonymization System
"""

from enum import Enum


class AnonymizationLevel(Enum):
    """Defines the levels of anonymization to apply to data"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    FULL = "full"


class DataType(Enum):
    """Defines the types of data that can be anonymized"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    EMAIL = "email"
    URL = "url"
    HASH = "hash"
    FILENAME = "filename"