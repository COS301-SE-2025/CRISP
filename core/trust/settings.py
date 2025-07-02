"""
Trust Management Settings

Configuration settings for the CRISP Trust Management system.
These settings can be overridden in the main Django settings.
"""

from django.conf import settings

# STIX/TAXII Integration Settings
CRISP_TAXII_SERVER_URL = getattr(settings, 'CRISP_TAXII_SERVER_URL', None)
CRISP_TAXII_API_ROOT = getattr(settings, 'CRISP_TAXII_API_ROOT', '/taxii2/')
CRISP_TRUST_COLLECTION_ID = getattr(settings, 'CRISP_TRUST_COLLECTION_ID', 'trust-intelligence')
CRISP_TAXII_USERNAME = getattr(settings, 'CRISP_TAXII_USERNAME', None)
CRISP_TAXII_PASSWORD = getattr(settings, 'CRISP_TAXII_PASSWORD', None)

# Trust-based Access Control Settings
TRUST_PROTECTED_ENDPOINTS = getattr(settings, 'TRUST_PROTECTED_ENDPOINTS', [
    '/api/threat-intelligence/',
    '/api/indicators/',
    '/api/ttps/',
    '/taxii2/',
])

TRUST_BYPASS_PATHS = getattr(settings, 'TRUST_BYPASS_PATHS', [
    '/api/auth/',
    '/api/trust/',
    '/admin/',
])

# Default Trust Settings
DEFAULT_TRUST_LEVEL = getattr(settings, 'DEFAULT_TRUST_LEVEL', 'medium')
DEFAULT_ANONYMIZATION_LEVEL = getattr(settings, 'DEFAULT_ANONYMIZATION_LEVEL', 'partial')
DEFAULT_ACCESS_LEVEL = getattr(settings, 'DEFAULT_ACCESS_LEVEL', 'read')

# Trust Relationship Expiration Settings
DEFAULT_RELATIONSHIP_DURATION_DAYS = getattr(settings, 'DEFAULT_RELATIONSHIP_DURATION_DAYS', 365)
EXPIRATION_WARNING_DAYS = getattr(settings, 'EXPIRATION_WARNING_DAYS', 30)

# Observer Pattern Settings
ENABLE_TRUST_NOTIFICATIONS = getattr(settings, 'ENABLE_TRUST_NOTIFICATIONS', True)
ENABLE_TRUST_METRICS = getattr(settings, 'ENABLE_TRUST_METRICS', True)
ENABLE_TRUST_AUDIT = getattr(settings, 'ENABLE_TRUST_AUDIT', True)
ENABLE_TRUST_SECURITY_MONITORING = getattr(settings, 'ENABLE_TRUST_SECURITY_MONITORING', True)

# Performance Settings
TRUST_CACHE_TIMEOUT = getattr(settings, 'TRUST_CACHE_TIMEOUT', 300)  # 5 minutes
MAX_TRUST_RELATIONSHIPS_PER_ORG = getattr(settings, 'MAX_TRUST_RELATIONSHIPS_PER_ORG', 1000)
MAX_TRUST_GROUP_MEMBERS = getattr(settings, 'MAX_TRUST_GROUP_MEMBERS', 500)

# Logging Settings
TRUST_LOG_LEVEL = getattr(settings, 'TRUST_LOG_LEVEL', 'INFO')
TRUST_AUDIT_LOG_RETENTION_DAYS = getattr(settings, 'TRUST_AUDIT_LOG_RETENTION_DAYS', 90)

# Security Settings
REQUIRE_BILATERAL_APPROVAL = getattr(settings, 'REQUIRE_BILATERAL_APPROVAL', True)
ALLOW_SELF_TRUST_RELATIONSHIPS = getattr(settings, 'ALLOW_SELF_TRUST_RELATIONSHIPS', False)
ENFORCE_TLP_MARKINGS = getattr(settings, 'ENFORCE_TLP_MARKINGS', True)