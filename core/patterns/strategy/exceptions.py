"""
Custom exceptions for the anonymization strategy pattern.
"""


class AnonymizationError(Exception):
    """Base exception for anonymization errors."""
    pass


class DataValidationError(AnonymizationError):
    """Raised when data doesn't match expected format for anonymization."""
    pass


class UnsupportedDataTypeError(AnonymizationError):
    """Raised when trying to anonymize an unsupported data type."""
    pass


class InvalidAnonymizationLevelError(AnonymizationError):
    """Raised when an invalid anonymization level is specified."""
    pass