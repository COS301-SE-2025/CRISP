"""
Security configuration for CRISP Threat Intelligence Platform

This module provides centralized security configuration management,
including credential handling, encryption settings, and security policies.
All sensitive data should be managed through this module.
"""

import os
import secrets
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Centralized security configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize security configuration.
        
        Args:
            config_file: Optional path to additional config file
        """
        self._config = self._load_default_config()
        self._encryption_key = None
        
        # Load from environment variables
        self._load_from_environment()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)
        
        # Validate configuration
        self._validate_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default security configuration"""
        return {
            # API Keys and Secrets
            'otx_api_key': None,
            'django_secret_key': None,
            'jwt_secret_key': None,
            
            # Database Configuration
            'database_encryption_key': None,
            'database_password': None,
            
            # OAuth Configuration
            'oauth_client_secret': None,
            'oauth_client_id': None,
            
            # TAXII Configuration
            'taxii_auth_token': None,
            'taxii_basic_auth_password': None,
            
            # Encryption Settings
            'encryption_algorithm': 'AES256',
            'hash_algorithm': 'SHA256',
            'password_salt_length': 32,
            
            # Security Policies
            'session_timeout_minutes': 30,
            'max_login_attempts': 5,
            'password_min_length': 12,
            'require_mfa': False,
            'allowed_origins': ['localhost', '127.0.0.1'],
            'rate_limit_per_minute': 60,
            
            # Audit Settings
            'audit_log_retention_days': 90,
            'sensitive_data_retention_days': 30,
            'log_level': 'INFO',
            
            # STIX/TAXII Security
            'stix_validation_strict': True,
            'taxii_require_auth': True,
            'taxii_enforce_https': True,
            
            # Anonymization Settings
            'default_anonymization_level': 'partial',
            'preserve_hash_prefixes': 8,
            'anonymize_timestamps': False,
        }
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            # API Keys
            'OTX_API_KEY': 'otx_api_key',
            'DJANGO_SECRET_KEY': 'django_secret_key',
            'JWT_SECRET_KEY': 'jwt_secret_key',
            
            # Database
            'DATABASE_ENCRYPTION_KEY': 'database_encryption_key',
            'DATABASE_PASSWORD': 'database_password',
            
            # OAuth
            'OAUTH_CLIENT_SECRET': 'oauth_client_secret',
            'OAUTH_CLIENT_ID': 'oauth_client_id',
            
            # TAXII
            'TAXII_AUTH_TOKEN': 'taxii_auth_token',
            'TAXII_BASIC_AUTH_PASSWORD': 'taxii_basic_auth_password',
            
            # Security Policies
            'SESSION_TIMEOUT_MINUTES': ('session_timeout_minutes', int),
            'MAX_LOGIN_ATTEMPTS': ('max_login_attempts', int),
            'PASSWORD_MIN_LENGTH': ('password_min_length', int),
            'REQUIRE_MFA': ('require_mfa', bool),
            'RATE_LIMIT_PER_MINUTE': ('rate_limit_per_minute', int),
            
            # Audit
            'AUDIT_LOG_RETENTION_DAYS': ('audit_log_retention_days', int),
            'SENSITIVE_DATA_RETENTION_DAYS': ('sensitive_data_retention_days', int),
            'LOG_LEVEL': 'log_level',
            
            # STIX/TAXII
            'STIX_VALIDATION_STRICT': ('stix_validation_strict', bool),
            'TAXII_REQUIRE_AUTH': ('taxii_require_auth', bool),
            'TAXII_ENFORCE_HTTPS': ('taxii_enforce_https', bool),
            
            # Anonymization
            'DEFAULT_ANONYMIZATION_LEVEL': 'default_anonymization_level',
            'PRESERVE_HASH_PREFIXES': ('preserve_hash_prefixes', int),
            'ANONYMIZE_TIMESTAMPS': ('anonymize_timestamps', bool),
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                if isinstance(config_key, tuple):
                    key, type_converter = config_key
                    try:
                        if type_converter == bool:
                            self._config[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            self._config[key] = type_converter(env_value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid value for {env_var}: {env_value}. Error: {e}")
                else:
                    self._config[config_key] = env_value
    
    def _load_from_file(self, config_file: str):
        """Load configuration from file"""
        try:
            import json
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self._config.update(file_config)
        except Exception as e:
            logger.error(f"Failed to load config from {config_file}: {e}")
    
    def _validate_config(self):
        """Validate security configuration"""
        errors = []
        
        # Check required secrets
        required_secrets = ['django_secret_key']
        for secret in required_secrets:
            if not self._config.get(secret):
                errors.append(f"Missing required secret: {secret}")
        
        # Validate security policies
        if self._config.get('password_min_length', 0) < 8:
            errors.append("Password minimum length must be at least 8 characters")
        
        if self._config.get('session_timeout_minutes', 0) <= 0:
            errors.append("Session timeout must be greater than 0")
        
        if self._config.get('max_login_attempts', 0) <= 0:
            errors.append("Max login attempts must be greater than 0")
        
        # Validate anonymization settings
        valid_anon_levels = ['none', 'partial', 'full']
        if self._config.get('default_anonymization_level') not in valid_anon_levels:
            errors.append(f"Invalid anonymization level. Must be one of: {valid_anon_levels}")
        
        if errors:
            raise ValueError(f"Security configuration errors: {'; '.join(errors)}")
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get a secret value (logs access for audit)"""
        value = self._config.get(key)
        if value:
            logger.debug(f"Secret '{key}' accessed")
        return value
    
    def set_secret(self, key: str, value: str, encrypt: bool = True):
        """Set a secret value"""
        if encrypt and value:
            value = self._encrypt_value(value)
        self._config[key] = value
        logger.info(f"Secret '{key}' updated")
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value"""
        if not self._encryption_key:
            self._encryption_key = self._generate_encryption_key()
        
        f = Fernet(self._encryption_key)
        encrypted_value = f.encrypt(value.encode())
        return base64.b64encode(encrypted_value).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        if not self._encryption_key:
            self._encryption_key = self._generate_encryption_key()
        
        f = Fernet(self._encryption_key)
        decoded_value = base64.b64decode(encrypted_value.encode())
        return f.decrypt(decoded_value).decode()
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from master password"""
        password = os.environ.get('CRISP_MASTER_PASSWORD', 'default-key-change-me')
        password_bytes = password.encode()
        
        salt = os.environ.get('CRISP_SALT', 'default-salt').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def generate_secret_key(self, length: int = 32) -> str:
        """Generate a new secret key"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_hex(self._config.get('password_salt_length', 32))
        
        # Use PBKDF2 for password hashing
        password_bytes = password.encode()
        salt_bytes = salt.encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
        )
        
        key = kdf.derive(password_bytes)
        hashed_password = base64.b64encode(key).decode()
        
        return hashed_password, salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify a password against its hash"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return computed_hash == hashed_password
        except Exception:
            return False
    
    def get_jwt_config(self) -> Dict[str, Any]:
        """Get JWT configuration"""
        return {
            'secret_key': self.get_secret('jwt_secret_key') or self.generate_secret_key(),
            'algorithm': 'HS256',
            'expiration_minutes': self._config.get('session_timeout_minutes', 30)
        }
    
    def get_oauth_config(self) -> Dict[str, Any]:
        """Get OAuth configuration"""
        return {
            'client_id': self.get_secret('oauth_client_id'),
            'client_secret': self.get_secret('oauth_client_secret'),
            'redirect_uri': self._config.get('oauth_redirect_uri'),
            'scopes': self._config.get('oauth_scopes', ['read', 'write'])
        }
    
    def get_taxii_auth_config(self) -> Dict[str, Any]:
        """Get TAXII authentication configuration"""
        return {
            'auth_token': self.get_secret('taxii_auth_token'),
            'basic_auth_password': self.get_secret('taxii_basic_auth_password'),
            'require_auth': self._config.get('taxii_require_auth', True),
            'enforce_https': self._config.get('taxii_enforce_https', True)
        }
    
    def get_anonymization_config(self) -> Dict[str, Any]:
        """Get anonymization configuration"""
        return {
            'default_level': self._config.get('default_anonymization_level', 'partial'),
            'preserve_hash_prefixes': self._config.get('preserve_hash_prefixes', 8),
            'anonymize_timestamps': self._config.get('anonymize_timestamps', False)
        }
    
    def get_audit_config(self) -> Dict[str, Any]:
        """Get audit configuration"""
        return {
            'log_retention_days': self._config.get('audit_log_retention_days', 90),
            'sensitive_data_retention_days': self._config.get('sensitive_data_retention_days', 30),
            'log_level': self._config.get('log_level', 'INFO')
        }
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.environ.get('CRISP_ENVIRONMENT', 'development').lower() == 'production'
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def save_config_template(self, file_path: str):
        """Save a configuration template file"""
        template_config = {
            "// NOTE": "This is a template file. Copy to config.json and fill in values",
            "otx_api_key": "your-otx-api-key-here",
            "django_secret_key": "your-django-secret-key-here",
            "jwt_secret_key": "your-jwt-secret-key-here",
            "database_password": "your-database-password-here",
            "oauth_client_id": "your-oauth-client-id-here",
            "oauth_client_secret": "your-oauth-client-secret-here",
            "session_timeout_minutes": 30,
            "max_login_attempts": 5,
            "password_min_length": 12,
            "require_mfa": False,
            "default_anonymization_level": "partial"
        }
        
        try:
            import json
            with open(file_path, 'w') as f:
                json.dump(template_config, f, indent=2)
            logger.info(f"Configuration template saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration template: {e}")

# Global security configuration instance
_security_config = None

def get_security_config() -> SecurityConfig:
    """Get global security configuration instance"""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config

def configure_security(config_file: Optional[str] = None) -> SecurityConfig:
    """Configure security settings"""
    global _security_config
    _security_config = SecurityConfig(config_file)
    return _security_config

# Environment-specific configurations
DEVELOPMENT_SECURITY_CONFIG = {
    'session_timeout_minutes': 120,  # Longer sessions for dev
    'max_login_attempts': 10,
    'log_level': 'DEBUG',
    'stix_validation_strict': False,
    'taxii_require_auth': False,
    'taxii_enforce_https': False
}

PRODUCTION_SECURITY_CONFIG = {
    'session_timeout_minutes': 30,
    'max_login_attempts': 5,
    'log_level': 'INFO',
    'stix_validation_strict': True,
    'taxii_require_auth': True,
    'taxii_enforce_https': True,
    'require_mfa': True
}