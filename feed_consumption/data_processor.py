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

# Import actual data processor implementation from service file
from feed_consumption.data_processing_service import DataProcessor
