"""
Enumeration definitions for the CRISP Anonymization System
"""

from enum import Enum


class AnonymizationLevel(Enum):
    """Defines the levels of anonymization to apply to data"""
    NONE = "none"      # No anonymization, original data preserved
    LOW = "low"        # Minimal anonymization, most information preserved
    MEDIUM = "medium"  # Moderate anonymization, partial information preserved
    HIGH = "high"      # High anonymization, minimal information preserved
    FULL = "full"      # Complete anonymization, consistent hashing


class DataType(Enum):
    """Defines the types of data that can be anonymized"""
    IP_ADDRESS = "ip_address"  # IP addresses (IPv4/IPv6)
    DOMAIN = "domain"          # Domain names
    EMAIL = "email"            # Email addresses
    URL = "url"                # URLs
    HASH = "hash"              # Cryptographic hashes
    FILENAME = "filename"      # File names