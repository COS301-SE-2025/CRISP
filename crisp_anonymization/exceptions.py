class AnonymizationError(Exception):
    """Base exception for anonymization errors"""
    pass


class InvalidDataTypeError(AnonymizationError):
    """Raised when an invalid data type is provided"""
    pass


class StrategyNotFoundError(AnonymizationError):
    """Raised when no suitable strategy is found for a data type"""
    pass


class InvalidAnonymizationLevelError(AnonymizationError):
    """Raised when an invalid anonymization level is provided"""
    pass


class DataValidationError(AnonymizationError):
    """Raised when data doesn't match the expected format"""
    pass