"""
Comprehensive test suite for Trust Management module.

This package contains all tests for the Trust Management module,
ensuring 96%+ code coverage across all components.
"""

# Test discovery configuration
default_app_config = 'TrustManagement.apps.TrustManagementConfig'

# Import all test modules to ensure discovery
from .test_models import *
from .test_services import *
from .test_views import *
from .test_api import *
from .test_management_commands import *
from .test_access_control import *
from .test_anonymization import *
from .test_utils import *
from .test_integrations import *
from .test_performance import *

__all__ = [
    'test_models',
    'test_services', 
    'test_views',
    'test_api',
    'test_management_commands',
    'test_access_control',
    'test_anonymization',
    'test_utils',
    'test_integrations',
    'test_performance'
]