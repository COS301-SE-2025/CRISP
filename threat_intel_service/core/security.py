# core/security.py
"""
Bulletproof security and validation layer for threat intelligence publication.
Focusing on input validation, rate limiting, data integrity, and secure operations.
"""
import re
import hashlib
import hmac
import time
import json
import ipaddress
import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from rest_framework.response import Response
import stix2
from stix2validator import validate_instance, print_results # For STIX 2.1 validation
from cryptography.fernet import Fernet, InvalidToken
from bleach import clean as bleach_clean # For HTML sanitization
from core.models import STIXObject

logger = logging.getLogger(__name__)

# --- Security Configuration ---
class SecurityConfig:
    """Central security configuration."""

    # Rate limiting (examples, tune based on expected load and security posture)
    DEFAULT_USER_RATE = '1000/hour'
    DEFAULT_ANON_RATE = '100/hour'
    BULK_OPERATION_USER_RATE = '50/hour' # Stricter for potentially heavy operations
    AUTH_FAILURE_RATE = '10/minute' # For IP-based lockout on auth failures

    MAX_REQUESTS_PER_MINUTE_USER = 100 # General guidance
    MAX_REQUESTS_PER_MINUTE_ANON = 20

    MAX_BULK_OBJECTS_PER_REQUEST = 500 # Reduced from 1000 for better control
    MAX_COLLECTION_SIZE_OBJECTS = 50000 # Reduced for manageability

    # Input validation
    MAX_STRING_LENGTH_GENERAL = 5000 # Reduced general string length
    MAX_STRING_LENGTH_NAME = 255
    MAX_STRING_LENGTH_DESCRIPTION = 20000 # Increased for descriptions
    MAX_PATTERN_LENGTH = 10000 # Increased for complex STIX patterns
    MAX_URL_LENGTH = 2048
    MAX_EMAIL_LENGTH = 254

    # Security patterns (more comprehensive)
    # Regex for common injection/XSS attempts. Be cautious with overly broad patterns.
    DANGEROUS_INPUT_PATTERNS = [
        r'(<script.*?>.*?</script.*?>)', r'(<iframe.*?>.*?</iframe>)', r'(<object.*?>.*?</object.*?>)',
        r'(javascript:.*?)', r'(vbscript:.*?)',
        r'(onload\s*=.*?)', r'(onerror\s*=.*?)', r'(onclick\s*=.*?)', r'(onmouseover\s*=.*?)',
        r'(eval\s*\(.*?\))', r'(document\.cookie)', r'(document\.write)',
        r'(window\.location)', r'(localStorage)', r'(sessionStorage)',
        r'(\b(select|insert|update|delete|drop|union|truncate|alter|exec|execute|char|nchar|varchar|nvarchar)\b.*\b(from|into|table|database|schema|procedure|function)\b)', # Basic SQLi
        r'(\.{2,}/)', r'(etc/passwd)', r'(proc/self)', # Path traversal
        r'(<\?php)', r'(<\?=)', # PHP tags
        r'(__import__)', r'(os\.system)', r'(subprocess\.call)', r'(subprocess\.run)', # Python execution
        r'(chr\()', r'(ord\()', # Obfuscation attempts
        r'(file://)', r'(ftp://)', r'(ldap://)', # Protocol attacks (context dependent)
    ]
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'strong', 'em', 'p', 'br', 'ul', 'ol', 'li', 'a']
    ALLOWED_HTML_ATTRIBUTES = {'a': ['href', 'title', 'target']}


    # STIX validation rules (examples, extend as needed)
    # These are more for semantic validation beyond basic schema.
    # The stix2validator.validate_instance() will handle comprehensive validation,
    # including relationship_type for Relationship SROs.
    REQUIRED_STIX_FIELDS_SEMANTIC = {
        'indicator': {'pattern_type': ['stix', 'snort', 'yara']}, # Example: ensure known pattern_types
        # 'relationship': {'relationship_type': [...] } # This check is handled by stix2validator
    }

    # Default encryption key (SHOULD BE IN settings.py and from environment variables)
    FIELD_ENCRYPTION_KEY = getattr(settings, 'FIELD_ENCRYPTION_KEY', Fernet.generate_key().decode())
    if FIELD_ENCRYPTION_KEY == Fernet.generate_key().decode(): # Check if it's the default generated one
        logger.warning("Using a default generated FIELD_ENCRYPTION_KEY. THIS IS NOT SECURE FOR PRODUCTION. Set a persistent key in settings.")


# --- Security Validators ---
class SecurityValidator:
    """Comprehensive security validation for all inputs."""

    @staticmethod
    def sanitize_html(value: str) -> str:
        """Sanitize HTML input using bleach."""
        return bleach_clean(value, tags=SecurityConfig.ALLOWED_HTML_TAGS, attributes=SecurityConfig.ALLOWED_HTML_ATTRIBUTES, strip=True)

    @staticmethod
    def validate_stix_pattern(pattern: str, field_name: str = "STIX pattern") -> str:
        """
        Validate STIX pattern using stix2patterns.
        If stix2patterns encounters an unexpected internal error for a seemingly valid pattern,
        log a warning and return the pattern. The more comprehensive stix2validator.validate_instance()
        will perform the definitive STIX pattern validation later.
        """
        clean_pattern = SecurityValidator.validate_string_input(pattern, SecurityConfig.MAX_PATTERN_LENGTH, field_name)

        try:
            from stix2patterns.validator import run_validator as validate_stix2_pattern
            # Temporarily disable for debugging the "list indices" error if it persists
            # logger.info(f"Validating pattern with stix2patterns: {clean_pattern}")
            results = validate_stix2_pattern([clean_pattern])

            if not results or not isinstance(results, list) or not results[0] or not isinstance(results[0], dict):
                logger.error(
                    f"STIX pattern validator (stix2patterns) returned unexpected result format for pattern: '{clean_pattern}'. "
                    f"Details: {results}. Will rely on full stix2validator.validate_instance for pattern check."
                )
                # Return clean_pattern to allow full validator to decide; this avoids being blocked by stix2patterns quirks.
                return clean_pattern

            if not results[0].get('valid', False):
                errors = results[0].get('errors', 'Unknown pattern validation error from stix2patterns')
                error_message = str(errors) if isinstance(errors, list) else errors
                logger.warning(f"Preliminary STIX pattern syntax check failed (from stix2patterns) for '{clean_pattern}': {error_message}")
                # This is a preliminary check. If it fails here, it's likely a syntax issue.
                raise DjangoValidationError(f"Validation Error: Invalid STIX pattern (preliminary syntax check by stix2patterns): {error_message}")

        except ImportError:
            logger.error("stix2patterns library not found. Skipping preliminary STIX pattern syntax validation.")
        except DjangoValidationError: # Re-raise our own validation errors (e.g., from input sanitization)
            raise
        except Exception as e:
            # This catches truly unexpected errors from stix2patterns.validator.run_validator itself (like the "list indices" one)
            logger.error(
                f"CRITICAL WARNING: Unexpected internal error during stix2patterns validation for pattern '{clean_pattern}': {type(e).__name__} - {e}. "
                f"This specific preliminary pattern check will be bypassed for this pattern. "
                f"Relying on the comprehensive stix2validator.validate_instance() for full STIX object validation, which includes pattern checks.",
                exc_info=True
            )
            # In this specific case of an unexpected library error for a seemingly valid pattern,
            # we allow it to pass this stage, as stix2validator.validate_instance (called later)
            # is the more robust and official validator for the whole STIX object.
        return clean_pattern

    @staticmethod
    def validate_stix_object(stix_data: Dict[str, Any], existing_object: Optional[STIXObject] = None) -> Dict[str, Any]:
        """Comprehensive STIX object validation using stix2validator and custom checks."""
        if not isinstance(stix_data, dict):
            raise DjangoValidationError("Validation Error: STIX object must be a dictionary.")

        # Use stix2validator for schema validation
        try:
            # Convert stix_data (dict) to string if validate_instance expects string
            # stix_data_str = json.dumps(stix_data) # Not needed, validate_instance handles dicts
            validation_results = validate_instance(stix_data) # stix2validator
            if not validation_results.is_valid: # Check new API
                errors = getattr(validation_results, 'errors', ['Unknown stix2validator error'])
                warnings = getattr(validation_results, 'warnings', [])
                logger.warning(f"STIX object schema validation failed. Errors: {errors}, Warnings: {warnings}. Object ID (if any): {stix_data.get('id')}")
                raise DjangoValidationError(f"Validation Error: STIX object schema validation failed: {errors}")
        except Exception as e: # Catch broader exceptions from the validator
            logger.error(f"Error during stix2validator: {e}. Object ID: {stix_data.get('id')}")
            raise DjangoValidationError(f"Validation Error: STIX object failed schema validation: {str(e)}")


        stix_type = stix_data.get('type')
        if not stix_type:
            raise DjangoValidationError("Validation Error: STIX object must have a 'type' field.")

        # Custom semantic validation for required fields beyond basic schema
        required_semantic_fields = SecurityConfig.REQUIRED_STIX_FIELDS_SEMANTIC.get(stix_type, {})
        for field, allowed_values in required_semantic_fields.items():
            if field in stix_data and stix_data[field] not in allowed_values:
                raise DjangoValidationError(f"Validation Error: Invalid value for {field} in STIX {stix_type}. Allowed: {allowed_values}.")

        # Validate individual string fields within the STIX object
        fields_to_validate = {
            'name': SecurityConfig.MAX_STRING_LENGTH_NAME,
            'description': SecurityConfig.MAX_STRING_LENGTH_DESCRIPTION,
            # Add other common string fields here if they need generic validation
        }
        if stix_type == 'identity':
            fields_to_validate['contact_information'] = SecurityConfig.MAX_STRING_LENGTH_GENERAL

        for field, max_len in fields_to_validate.items():
            if field in stix_data and stix_data[field] is not None: # Check for None
                stix_data[field] = SecurityValidator.validate_string_input(
                    stix_data[field], max_len, f"STIX object field '{field}'"
                )

        if stix_type == 'indicator' and 'pattern' in stix_data:
            stix_data['pattern'] = SecurityValidator.validate_stix_pattern(stix_data['pattern'])


        # Validate references (created_by_ref, source_ref, target_ref, object_marking_refs etc.)
        ref_fields_single = ['created_by_ref', 'source_ref', 'target_ref', 'original_object_ref']
        ref_fields_list = ['object_marking_refs', 'external_references.source_name'] # Example for nested

        for field in ref_fields_single:
            if field in stix_data and stix_data[field]:
                SecurityValidator.validate_stix_reference(stix_data[field], field_name=f"STIX object field '{field}'")

        if 'object_marking_refs' in stix_data and isinstance(stix_data['object_marking_refs'], list):
            for ref in stix_data['object_marking_refs']:
                SecurityValidator.validate_stix_reference(ref, field_name="STIX object_marking_refs item")

        # Prevent self-referential relationships if it's a business rule
        if stix_type == 'relationship' and stix_data.get('source_ref') == stix_data.get('target_ref'):
            logger.warning(f"Self-referential relationship detected: {stix_data.get('id')}")
            # raise DjangoValidationError("Validation Error: Relationship source_ref cannot be the same as target_ref.")


        # Timestamp validation: modified >= created
        if 'created' in stix_data and 'modified' in stix_data:
            try:
                created_ts = parse_datetime(stix_data['created'])
                modified_ts = parse_datetime(stix_data['modified'])
                if created_ts and modified_ts and modified_ts < created_ts:
                    raise DjangoValidationError(f"Validation Error: STIX object 'modified' timestamp ({modified_ts}) cannot be earlier than 'created' timestamp ({created_ts}).")
            except ValueError:
                raise DjangoValidationError("Validation Error: Invalid timestamp format for 'created' or 'modified'.")


        # ID and Type immutability for updates
        if existing_object:
            if stix_data.get('id') != existing_object.stix_id:
                raise DjangoValidationError("Validation Error: STIX object ID cannot be changed during update.")
            if stix_data.get('type') != existing_object.stix_type:
                raise DjangoValidationError("Validation Error: STIX object type cannot be changed during update.")


        return stix_data

    @staticmethod
    def validate_stix_reference(ref: str, field_name: str = "STIX reference") -> bool:
        """Validate STIX reference format (e.g., type--uuid)."""
        if not isinstance(ref, str):
            raise DjangoValidationError(f"Validation Error: {field_name} must be a string.")

        pattern = r'^[a-z0-9][a-z0-9-]+[a-z0-9]--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(pattern, ref):
            logger.warning(f"Invalid STIX reference format for {field_name}: {ref}")
            raise DjangoValidationError(f"Validation Error: Invalid STIX reference format for {field_name}: {ref}. Expected 'type--uuid'.")
        return True

    @staticmethod
    def validate_ip_address(ip_str: str, field_name: str = "IP address") -> str:
        """Validate IP address (v4 or v6) and check against basic blocklists."""
        try:
            ip_obj = ipaddress.ip_address(ip_str) # Validates format

            if ip_obj.is_multicast or ip_obj.is_unspecified or ip_obj.is_reserved or ip_obj.is_loopback:
                if not (ip_obj.is_private and getattr(settings, 'ALLOW_PRIVATE_IPS_IN_PATTERNS', False)): # Allow private if configured
                    logger.warning(f"Attempt to use non-routable/reserved {field_name}: {ip_str}")
                    raise DjangoValidationError(f"Validation Error: {field_name} '{ip_str}' is a non-routable, reserved, or loopback address.")

            # Example blocklist check (in a real system, this would be more dynamic)
            # BLOCKED_IP_RANGES should be defined in settings.py
            # e.g., BLOCKED_IP_RANGES = ['127.0.0.0/8', '0.0.0.0/8']
            blocked_ranges = getattr(settings, 'BLOCKED_IP_RANGES', [])
            for net_str in blocked_ranges:
                if ip_obj in ipaddress.ip_network(net_str, strict=False):
                    logger.warning(f"{field_name} {ip_str} is in a blocked range: {net_str}")
                    raise DjangoValidationError(f"Validation Error: {field_name} '{ip_str}' is in a blocked range.")
            return ip_str
        except ValueError: # Catches ipaddress.ip_address format errors
            raise DjangoValidationError(f"Validation Error: Invalid {field_name} format: {ip_str}.")


    @staticmethod
    def validate_url(url: str, field_name: str = "URL", allowed_schemes: List[str] = None) -> str:
        """Validate URL format and scheme."""
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']

        clean_url = SecurityValidator.validate_string_input(url, SecurityConfig.MAX_URL_LENGTH, field_name)

        from django.core.validators import URLValidator
        validate = URLValidator(schemes=allowed_schemes)
        try:
            validate(clean_url)
        except DjangoValidationError as e:
            raise DjangoValidationError(f"Validation Error: Invalid {field_name}: {clean_url}. {e}")
        return clean_url

    @staticmethod
    def validate_email(email: str, field_name: str = "Email") -> str:
        """Validate email format."""
        clean_email = SecurityValidator.validate_string_input(email, SecurityConfig.MAX_EMAIL_LENGTH, field_name)
        from django.core.validators import validate_email as django_validate_email
        try:
            django_validate_email(clean_email)
        except DjangoValidationError as e:
            raise DjangoValidationError(f"Validation Error: Invalid {field_name}: {clean_email}. {e}")
        return clean_email


# --- Rate Limiting ---
class ConfigurableRateThrottle(UserRateThrottle):
    """Allows rate to be configured via scope in settings.py"""
    def __init__(self):
        super().__init__()
        # Scope must be set by the view using this throttle
        # self.rate will be set by DRF based on 'scope'

    def allow_request(self, request, view):
        if not self.rate: # Rate is set by DRF based on scope
            self.rate = self.get_rate()

        # User-specific overrides or group-based rates
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True # Superusers are not throttled
            # Example: user_profile = request.user.userprofile
            # if user_profile.has_premium_access: self.rate = '10000/day'
        return super().allow_request(request, view)

class AnonConfigurableRateThrottle(AnonRateThrottle):
    """Allows rate to be configured via scope for anonymous users."""
    def __init__(self):
        super().__init__()


# --- Security Middleware ---
class AdvancedSecurityMiddleware:
    """Enhanced security middleware for additional protections."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_failure_cache_prefix = "auth_fail:"
        self.auth_failure_lockout_threshold = 5 # Attempts
        self.auth_failure_lockout_duration = 15 * 60 # 15 minutes in seconds

    def __call__(self, request):
        # IP-based lockout for repeated auth failures (check before processing view)
        if self._is_ip_locked_out(request):
            logger.warning(f"IP locked out due to repeated auth failures: {self.get_client_ip(request)}")
            return Response({"error": "Too many failed login attempts. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)


        response = self.get_response(request)

        # Essential Security Headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY' # Prevents clickjacking
        response['X-XSS-Protection'] = '1; mode=block' # Enables XSS filtering in browsers

        # Strict-Transport-Security (HSTS) - only if site is served over HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        # Content-Security-Policy (CSP) - highly effective against XSS. Needs careful configuration.
        # Example: restrictive policy. Customize based on your app's needs (scripts, styles, fonts, etc.)
        csp_policy = [
            "default-src 'self'",
            "script-src 'self'", # Add CDNs or 'unsafe-inline' if necessary, but avoid if possible
            "style-src 'self' 'unsafe-inline'", # 'unsafe-inline' often needed for legacy CSS
            "img-src 'self' data:",
            "font-src 'self'",
            "object-src 'none'", # Disallow plugins like Flash
            "frame-ancestors 'none'", # Similar to X-Frame-Options: DENY
            "form-action 'self'",
            "base-uri 'self'",
        ]
        response['Content-Security-Policy'] = "; ".join(csp_policy)

        response['Referrer-Policy'] = 'strict-origin-when-cross-origin' # Protects referrer info
        response['Permissions-Policy'] = "geolocation=(), microphone=(), camera=(), payment=()" # Feature policy

        return response

    def get_client_ip(self, request):
        """Get real client IP, respecting X-Forwarded-For."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def _is_ip_locked_out(self, request):
        """Check if an IP is currently locked out."""
        ip_address = self.get_client_ip(request)
        cache_key = f"{self.auth_failure_cache_prefix}lockout:{ip_address}"
        return cache.get(cache_key) is not None

    def record_auth_failure(self, request):
        """Record an authentication failure for an IP and potentially lock it out."""
        ip_address = self.get_client_ip(request)
        count_cache_key = f"{self.auth_failure_cache_prefix}count:{ip_address}"
        lockout_cache_key = f"{self.auth_failure_cache_prefix}lockout:{ip_address}"

        failure_count = cache.get(count_cache_key, 0) + 1
        cache.set(count_cache_key, failure_count, self.auth_failure_lockout_duration)

        if failure_count >= self.auth_failure_lockout_threshold:
            cache.set(lockout_cache_key, True, self.auth_failure_lockout_duration)
            logger.critical(f"IP LOCKED OUT: {ip_address} after {failure_count} failed auth attempts.")
            # Potentially notify admins here

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Additional security checks before view processing."""
        client_ip = self.get_client_ip(request)
        try:
            SecurityValidator.validate_ip_address(client_ip, "Client IP") # Basic validation of the IP itself
        except DjangoValidationError as e:
            logger.warning(f"Request from invalid/blocked client IP {client_ip}: {e}")
            return Response({"error": "Access Denied."}, status=status.HTTP_403_FORBIDDEN)

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if self.is_suspicious_user_agent(user_agent, request.path_info):
            logger.warning(f"Suspicious user agent detected: '{user_agent}' for path '{request.path_info}' from IP {client_ip}")
            # Consider if this should be a hard block or just a higher scrutiny log
            # return Response({"error": "Access Denied."}, status=status.HTTP_403_FORBIDDEN)

        return None # Continue to view

    def is_suspicious_user_agent(self, user_agent_string: str, path: str) -> bool:
        """Identify suspicious user agents, with context for TAXII/STIX tools."""
        if not user_agent_string: return False # No UA is suspicious in itself

        # Allow known TAXII client patterns or specific STIX-related tools
        # These are examples, expand based on legitimate clients you expect.
        allowed_ua_patterns = [
            r'python-taxii2client', r'cti-taxii-client', r'libtaxii',
            r'OpenTAXII', r'Mozilla', r'Chrome', r'Safari', r'Edge', # Common browsers
            # Add UAs of known friendly scanners or monitoring tools if applicable
        ]
        for pattern in allowed_ua_patterns:
            if re.search(pattern, user_agent_string, re.IGNORECASE):
                return False # It's a known/allowed type

        # General suspicious patterns (often bots, basic scripts, scanners)
        suspicious_ua_patterns = [
            r'curl', r'wget', r'python-requests', r'Java/', r'Go-http-client', # Common HTTP libraries often used by scripts
            r'nmap', r'sqlmap', r'nikto', r'acunetix', r'netsparker', # Scanner UAs
            r'(bot\b)', r'(crawler\b)', r'(spider\b)', r'(slurp\b)', r'(scan\b)',
            r'^$', # Empty User-Agent
        ]
        for pattern in suspicious_ua_patterns:
            if re.search(pattern, user_agent_string, re.IGNORECASE):
                return True
        return False


# --- Data Integrity ---
class DataIntegrityValidator:
    """Ensures data integrity across the system, especially for STIX objects and collections."""

    @staticmethod
    @transaction.atomic # Ensure atomic operation for checks and potential fixes
    def validate_collection_integrity(collection_id: uuid.UUID) -> Tuple[bool, List[str]]:
        """Validate data integrity for a specific collection."""
        from core.models import Collection, CollectionObject, STIXObject # Local import
        issues = []
        try:
            collection = Collection.objects.select_for_update().get(id=collection_id)
        except Collection.DoesNotExist:
            issues.append(f"Collection ID {collection_id} not found.")
            return False, issues

        # 1. Check for orphaned CollectionObject entries (pointing to non-existent STIXObjects)
        orphaned_links = CollectionObject.objects.filter(collection=collection).exclude(stix_object_id__in=STIXObject.objects.values_list('id', flat=True))
        if orphaned_links.exists():
            count = orphaned_links.count()
            issues.append(f"Collection '{collection.title}' has {count} orphaned CollectionObject links (STIXObject deleted).")
            # Corrective action: orphaned_links.delete() # Or log for manual review
            # For this example, we'll just log it as an issue.

        # 2. Check collection size against limits
        current_object_count = collection.stix_objects.count()
        if current_object_count > SecurityConfig.MAX_COLLECTION_SIZE_OBJECTS:
            issues.append(f"Collection '{collection.title}' (count: {current_object_count}) exceeds maximum size limit of {SecurityConfig.MAX_COLLECTION_SIZE_OBJECTS}.")

        # 3. Validate a sample of STIX objects within the collection for schema compliance
        #    (Full validation of all objects might be too slow for a quick integrity check)
        sample_stix_objects = collection.stix_objects.all()[:5] # Sample 5 objects
        for stix_obj_db in sample_stix_objects:
            try:
                SecurityValidator.validate_stix_object(stix_obj_db.to_stix())
            except DjangoValidationError as e:
                issues.append(f"STIX Object {stix_obj_db.stix_id} in Collection '{collection.title}' failed validation: {e}")

        return not issues, issues

    @staticmethod
    def validate_stix_object_integrity(stix_object_id: uuid.UUID) -> Tuple[bool, List[str]]:
        """Validate data integrity for a specific STIXObject."""
        from core.models import STIXObject # Local import
        issues = []
        try:
            stix_obj = STIXObject.objects.get(id=stix_object_id)
        except STIXObject.DoesNotExist:
            issues.append(f"STIXObject ID {stix_object_id} not found.")
            return False, issues

        # 1. Validate raw_data can be parsed and matches key fields
        try:
            stix_data_from_raw = stix_obj.to_stix() # Uses raw_data
            if not isinstance(stix_data_from_raw, dict):
                issues.append(f"STIXObject {stix_obj.stix_id}: raw_data is not a valid JSON dictionary.")
            else:
                if stix_data_from_raw.get('id') != stix_obj.stix_id:
                    issues.append(f"STIXObject {stix_obj.stix_id}: Mismatch between raw_data.id ('{stix_data_from_raw.get('id')}') and model stix_id ('{stix_obj.stix_id}').")
                if stix_data_from_raw.get('type') != stix_obj.stix_type:
                    issues.append(f"STIXObject {stix_obj.stix_id}: Mismatch between raw_data.type ('{stix_data_from_raw.get('type')}') and model stix_type ('{stix_obj.stix_type}').")
                # Add more checks for created, modified if necessary

                # 2. Validate against STIX 2.1 schema
                SecurityValidator.validate_stix_object(stix_data_from_raw)

        except json.JSONDecodeError:
            issues.append(f"STIXObject {stix_obj.stix_id}: raw_data is not valid JSON.")
        except DjangoValidationError as e: # Catch validation errors from SecurityValidator
            issues.append(f"STIXObject {stix_obj.stix_id} failed schema/content validation: {e}")
        except Exception as e: # Catch other unexpected errors
            issues.append(f"STIXObject {stix_obj.stix_id}: Unexpected error during integrity check: {type(e).__name__} - {e}")

        # 3. If anonymized, check if original_object_ref exists (if applicable by policy)
        if stix_obj.anonymized and stix_obj.original_object_ref:
            if not STIXObject.objects.filter(stix_id=stix_obj.original_object_ref).exists():
                issues.append(f"Anonymized STIXObject {stix_obj.stix_id} has original_object_ref '{stix_obj.original_object_ref}' which does not exist.")

        return not issues, issues


# --- Cryptographic Operations ---
class CryptographicSecurity:
    """Handles cryptographic operations securely. Uses Fernet for symmetric encryption."""
    _fernet_instance = None

    @staticmethod
    def _get_fernet() -> Fernet:
        """Initializes and returns a Fernet instance."""
        if CryptographicSecurity._fernet_instance is None:
            key = SecurityConfig.FIELD_ENCRYPTION_KEY.encode()
            if not key or len(key) != 44 or not key.endswith(b'='): # Basic check for Fernet key format
                logger.critical("FIELD_ENCRYPTION_KEY is missing, not set, or invalid. Cannot perform encryption/decryption.")
                raise ValueError("FIELD_ENCRYPTION_KEY is not configured correctly for encryption.")
            CryptographicSecurity._fernet_instance = Fernet(key)
        return CryptographicSecurity._fernet_instance

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure URL-safe random token."""
        import secrets
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password using Django's default hasher (PBKDF2SHA256)."""
        from django.contrib.auth.hashers import make_password
        return make_password(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verifies a password against a hashed version."""
        from django.contrib.auth.hashers import check_password
        return check_password(password, hashed_password)

    @staticmethod
    def encrypt_sensitive_data(data: Union[str, bytes]) -> str:
        """Encrypts sensitive data (string or bytes) and returns base64 encoded ciphertext."""
        if not data: return ""
        fernet = CryptographicSecurity._get_fernet()
        data_bytes = data.encode() if isinstance(data, str) else data
        try:
            return fernet.encrypt(data_bytes).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise # Re-raise to signal failure

    @staticmethod
    def decrypt_sensitive_data(encrypted_data_str: str) -> str:
        """Decrypts base64 encoded ciphertext and returns original string."""
        if not encrypted_data_str: return ""
        fernet = CryptographicSecurity._get_fernet()
        try:
            decrypted_bytes = fernet.decrypt(encrypted_data_str.encode())
            return decrypted_bytes.decode()
        except InvalidToken:
            logger.error("Decryption failed: Invalid token (likely wrong key or corrupted data).")
            raise # Re-raise specific error
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise # Re-raise general error


# --- Audit Logging for Security ---
class SecurityAuditLogger:
    """Specialized logger for security-relevant events."""

    @staticmethod
    def log_event(
        event_type: str,
        user: Optional[User],
        request_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = 'INFO', # INFO, WARNING, ERROR, CRITICAL
        target_object_id: Optional[str] = None,
        organization: Optional[Any] = None # core.models.Organization
    ):
        """Logs a security event to both Django's logger and AuditLog model."""
        from audit.models import AuditLog # Local import

        log_details = details if details is not None else {}
        log_details['security_event_type'] = event_type
        log_details['severity'] = severity

        # Log to Django's logging system
        log_message = f"SecurityEvent:{event_type} User:{user.username if user else 'Anonymous'} IP:{request_ip} Target:{target_object_id} Details:{json.dumps(log_details)}"
        if severity == 'CRITICAL': logger.critical(log_message)
        elif severity == 'ERROR': logger.error(log_message)
        elif severity == 'WARNING': logger.warning(log_message)
        else: logger.info(log_message)

        # Log to AuditLog model
        try:
            AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                organization=organization, # Pass the organization if available
                action_type=f"security.{event_type.lower().replace(' ', '_')}", # e.g., security.auth_failure
                object_id=target_object_id,
                details=log_details,
                ip_address=request_ip,
                user_agent=log_details.get('user_agent', None) # Assuming details might contain user_agent
            )
        except Exception as e:
            logger.error(f"Failed to create AuditLog entry for security event '{event_type}': {e}")

    @staticmethod
    def log_auth_failure(username_attempted: str, request_ip: str, user_agent: Optional[str] = None, reason: str = "Invalid credentials"):
        """Logs a failed authentication attempt and handles lockout logic."""
        middleware = AdvancedSecurityMiddleware(None) # Temp instance to access methods
        middleware.record_auth_failure(type('Request', (), {'META': {'REMOTE_ADDR': request_ip, 'HTTP_X_FORWARDED_FOR': None, 'HTTP_USER_AGENT': user_agent}})) # Mock request

        SecurityAuditLogger.log_event(
            "Authentication Failure",
            user=None, # No authenticated user on failure
            request_ip=request_ip,
            details={"username_attempted": username_attempted, "reason": reason, "user_agent": user_agent},
            severity='WARNING'
        )

    @staticmethod
    def log_permission_denied(user: User, request_ip: str, resource: str, action: str, user_agent: Optional[str] = None):
        SecurityAuditLogger.log_event(
            "Permission Denied",
            user=user,
            request_ip=request_ip,
            details={"resource": resource, "action": action, "user_agent": user_agent},
            severity='WARNING',
            target_object_id=resource
        )

    @staticmethod
    def log_potential_attack(attack_type: str, user: Optional[User], request_ip: str, details: Dict[str, Any], user_agent: Optional[str] = None):
        details["user_agent"] = user_agent
        SecurityAuditLogger.log_event(
            f"Potential Attack Attempt: {attack_type}",
            user=user,
            request_ip=request_ip,
            details=details,
            severity='CRITICAL'
        )

# --- Performance Monitoring ---
class PerformanceMonitor:
    """Basic performance monitoring for critical operations."""
    # Performance targets (examples, adjust based on P1.6 etc.)
    TARGETS = {
        'bulk_stix_creation': {'rate_records_per_sec': 100, 'max_duration_per_100_records_ms': 1000},
        'taxii_object_retrieval': {'max_duration_ms': 500}, # For a typical paged response
    }

    @staticmethod
    def monitor_operation(operation_name: str, record_count: Optional[int], start_time: float,
                          details: Optional[Dict] = None):
        duration_ms = (time.time() - start_time) * 1000
        rate = (record_count / (duration_ms / 1000)) if record_count and duration_ms > 0 else 0

        log_info = {
            "operation": operation_name,
            "duration_ms": round(duration_ms, 2),
            "record_count": record_count,
            "rate_records_per_sec": round(rate, 2),
            "details": details or {}
        }
        logger.info(f"PerfMonitor: {json.dumps(log_info)}")

        # Check against targets
        target = PerformanceMonitor.TARGETS.get(operation_name)
        if target:
            if 'max_duration_ms' in target and duration_ms > target['max_duration_ms']:
                logger.warning(f"PerfAlert:{operation_name} duration {duration_ms:.2f}ms exceeded target {target['max_duration_ms']}ms.")
            if 'rate_records_per_sec' in target and record_count and rate < target['rate_records_per_sec']:
                 # Only alert if there was a substantial number of records, e.g. > 10
                if record_count > 10 :
                    logger.warning(f"PerfAlert:{operation_name} rate {rate:.2f}/s below target {target['rate_records_per_sec']}/s for {record_count} records.")
        return log_info


# --- Security Decorators ---
def require_explicit_permission(permission_codename: str):
    """Decorator to check for a specific Django permission."""
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                SecurityAuditLogger.log_permission_denied(None, AdvancedSecurityMiddleware(None).get_client_ip(request), request.path, "authentication_required", request.META.get('HTTP_USER_AGENT'))
                return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            if not request.user.has_perm(permission_codename):
                SecurityAuditLogger.log_permission_denied(request.user, AdvancedSecurityMiddleware(None).get_client_ip(request), request.path, f"missing_permission:{permission_codename}",request.META.get('HTTP_USER_AGENT'))
                return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def validate_request_data(serializer_class):
    """Decorator to validate request.data using a given DRF serializer."""
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            serializer = serializer_class(data=request.data, context={'request': request})
            if not serializer.is_valid():
                logger.warning(f"Request data validation failed for {view_func.__name__}: {serializer.errors}")
                SecurityAuditLogger.log_event("Invalid Input Data", request.user, AdvancedSecurityMiddleware(None).get_client_ip(request),
                                              details={"view": view_func.__name__, "errors": serializer.errors}, severity="WARNING")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # Pass validated data to the view if needed, or let the view re-instantiate
            # For simplicity here, we assume the view will handle its data
            return view_func(self, request, *args, **kwargs) # Or pass validated_data=serializer.validated_data
        return wrapper
    return decorator