"""
Import all admin modules to ensure Django Admin registration
"""

# Import trust management admin
try:
    import core_ut.trust.admin_ut
except ImportError:
    pass

# Import user management admin
try:
    import core_ut.user_management.admin_ut
except ImportError:
    pass

# Import alerts admin (if it exists)
try:
    import core_ut.alerts.admin_ut
except ImportError:
    pass