"""
TAXII Client Exceptions and Import Compatibility Layer.

This file provides exception classes and imports used in tests.
"""

class TaxiiClientError(Exception):
    """Base class for TAXII client errors"""
    pass

class TaxiiConnectionError(TaxiiClientError):
    """Error establishing connection to TAXII server"""
    pass

class TaxiiAuthenticationError(TaxiiClientError):
    """Authentication error with TAXII server"""
    pass

class TaxiiDataError(TaxiiClientError):
    """Error processing TAXII data"""
    pass

# Do not import TaxiiClient here to avoid circular imports
