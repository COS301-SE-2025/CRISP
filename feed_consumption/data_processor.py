"""
Data Processor Exceptions and Import Compatibility Layer.

This file provides exception classes used in tests.
"""

class DataProcessingError(Exception):
    """Base class for data processing errors"""
    pass

class StixValidationError(DataProcessingError):
    """Error validating STIX object"""
    pass
