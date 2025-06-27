"""
Enumeration definitions for the CRISP Anonymization System
"""

from enum import Enum


class AnonymizationLevel(Enum):
    """
    Enum for defining anonymization levels.
    """
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


class TrustLevelEnum(Enum):
    """
    Enum for defining trust levels in relationships.
    """
    UNKNOWN = 'unknown'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    ABSOLUTE = 'absolute'


class SharingScopeEnum(Enum):
    """
    Enum for defining sharing scopes for intelligence.
    """
    PRIVATE = 'private'
    GROUP = 'group'
    COMMUNITY = 'community'
    PUBLIC = 'public'