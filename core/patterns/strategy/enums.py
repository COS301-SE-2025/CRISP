from enum import Enum

class AnonymizationLevel(Enum):
    """Enumeration for anonymization levels"""
    NONE = "none"
    BASIC = "basic"
    MINIMAL = "minimal"
    PARTIAL = "partial"
    MEDIUM = "medium"
    HIGH = "high"
    FULL = "full"
    CUSTOM = "custom"

class DataType(Enum):
    """Enumeration for data types that can be anonymized"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    EMAIL = "email"
    URL = "url"
    FILE_HASH = "file_hash"
    USER_AGENT = "user_agent"
    TIMESTAMP = "timestamp"
    ORGANIZATION = "organization"
    OTHER = "other"