"""
OTX Configuration for CRISP Threat Intelligence Platform
"""

import os
from typing import Dict, Any
from .security import get_security_config

class OTXConfig:
    """Configuration class for OTX integration"""
    
    # Default configuration
    DEFAULT_CONFIG = {
        'enabled': True,
        'fetch_interval': 3600,  # 1 hour in seconds
        'batch_size': 50,
        'max_age_days': 30,
        'rate_limit_delay': 1.0,  # seconds between requests
        'request_timeout': 30,  # seconds
        'indicator_types': [
            'IPv4', 'IPv6', 'domain', 'hostname', 'URL', 'URI',
            'FileHash-MD5', 'FileHash-SHA1', 'FileHash-SHA256',
            'email', 'Mutex', 'CVE'
        ],
        'auto_create_feed': True,
        'feed_name_template': 'OTX Feed - {institution_name}',
        'feed_description_template': 'AlienVault OTX threat intelligence for {institution_name}',
        'user_agent': 'CRISP-ThreatIntel/1.0',
        'retry_attempts': 3,
        'retry_delay': 5.0,  # seconds
        'log_level': 'INFO'
    }
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        'OTX_API_KEY': 'api_key',
        'OTX_ENABLED': ('enabled', bool),
        'OTX_FETCH_INTERVAL': ('fetch_interval', int),
        'OTX_BATCH_SIZE': ('batch_size', int),
        'OTX_MAX_AGE_DAYS': ('max_age_days', int),
        'OTX_RATE_LIMIT_DELAY': ('rate_limit_delay', float),
        'OTX_AUTO_CREATE_FEED': ('auto_create_feed', bool),
        'OTX_LOG_LEVEL': 'log_level'
    }
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize OTX configuration.
        
        Args:
            config_dict: Optional configuration dictionary to override defaults
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from environment variables
        self._load_from_environment()
        
        # Apply custom configuration
        if config_dict:
            self.config.update(config_dict)
        
        # Validate configuration
        self._validate()
    
    def _load_from_environment(self):
        """Load configuration from environment variables and security config."""
        # Load from security config first
        security_config = get_security_config()
        api_key = security_config.get_secret('otx_api_key')
        if api_key:
            self.config['api_key'] = api_key
        
        # Then load from environment variables
        for env_var, config_key in self.ENV_MAPPINGS.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                if isinstance(config_key, tuple):
                    key, type_converter = config_key
                    try:
                        if type_converter == bool:
                            # Handle boolean environment variables
                            self.config[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            self.config[key] = type_converter(env_value)
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Invalid value for {env_var}: {env_value}. Error: {e}")
                else:
                    self.config[config_key] = env_value
    
    def _validate(self):
        """Validate configuration values."""
        errors = []
        
        # Check API key
        if not self.config.get('api_key'):
            errors.append("OTX API key is required. Set OTX_API_KEY environment variable.")
        
        # Validate intervals and limits
        if self.config.get('fetch_interval', 0) < 60:
            errors.append("Fetch interval must be at least 60 seconds")
        
        if not (1 <= self.config.get('batch_size', 0) <= 50):
            errors.append("Batch size must be between 1 and 50")
        
        if self.config.get('max_age_days', 0) <= 0:
            errors.append("Max age days must be greater than 0")
        
        if self.config.get('rate_limit_delay', 0) < 0:
            errors.append("Rate limit delay cannot be negative")
        
        if self.config.get('request_timeout', 0) <= 0:
            errors.append("Request timeout must be greater than 0")
        
        # Check indicator types
        if not self.config.get('indicator_types'):
            errors.append("At least one indicator type must be configured")
        
        if errors:
            raise ValueError(f"OTX configuration errors: {'; '.join(errors)}")
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self._validate()
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values."""
        self.config.update(updates)
        self._validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self.config.copy()
    
    def is_enabled(self) -> bool:
        """Check if OTX integration is enabled."""
        return self.config.get('enabled', False)
    
    def get_api_key(self) -> str:
        """Get API key."""
        return self.config.get('api_key', '')
    
    def get_client_config(self) -> Dict[str, Any]:
        """Get configuration for OTX client."""
        return {
            'batch_size': self.config['batch_size'],
            'max_age_days': self.config['max_age_days'],
            'supported_indicator_types': self.config['indicator_types'],
            'rate_limit_delay': self.config['rate_limit_delay'],
            'request_timeout': self.config['request_timeout'],
            'user_agent': self.config['user_agent'],
            'retry_attempts': self.config['retry_attempts'],
            'retry_delay': self.config['retry_delay']
        }
    
    def get_service_config(self) -> Dict[str, Any]:
        """Get configuration for OTX service."""
        return {
            'enabled': self.config['enabled'],
            'fetch_interval': self.config['fetch_interval'],
            'batch_size': self.config['batch_size'],
            'max_age_days': self.config['max_age_days'],
            'indicator_types': self.config['indicator_types'],
            'auto_create_feed': self.config['auto_create_feed'],
            'feed_name_template': self.config['feed_name_template'],
            'feed_description_template': self.config['feed_description_template']
        }
    
    @classmethod
    def from_file(cls, config_file: str) -> 'OTXConfig':
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to configuration file (JSON or Python dict)
            
        Returns:
            OTXConfig instance
        """
        import json
        
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    config_dict = json.load(f)
                else:
                    # Assume it's a Python file with a CONFIG dict
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("config", config_file)
                    config_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(config_module)
                    config_dict = getattr(config_module, 'CONFIG', {})
            
            return cls(config_dict)
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_file}: {e}")
    
    def save_to_file(self, config_file: str):
        """
        Save configuration to a file.
        
        Args:
            config_file: Path to save configuration
        """
        import json
        
        # Remove sensitive information from saved config
        safe_config = self.config.copy()
        if 'api_key' in safe_config:
            safe_config['api_key'] = '***masked***'
        
        try:
            with open(config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {config_file}: {e}")

# Global configuration instance
otx_config = None

def get_otx_config() -> OTXConfig:
    """Get global OTX configuration instance."""
    global otx_config
    if otx_config is None:
        otx_config = OTXConfig()
    return otx_config

def configure_otx(config_dict: Dict[str, Any] = None, config_file: str = None) -> OTXConfig:
    """
    Configure OTX integration.
    
    Args:
        config_dict: Configuration dictionary
        config_file: Configuration file path
        
    Returns:
        OTXConfig instance
    """
    global otx_config
    
    if config_file:
        otx_config = OTXConfig.from_file(config_file)
    elif config_dict:
        otx_config = OTXConfig(config_dict)
    else:
        otx_config = OTXConfig()
    
    return otx_config

# Sample configuration for development
DEVELOPMENT_CONFIG = {
    'enabled': True,
    'fetch_interval': 300,  # 5 minutes for development
    'batch_size': 10,       # Smaller batches for testing
    'max_age_days': 7,      # Only recent data
    'log_level': 'DEBUG'
}

# Sample configuration for production
PRODUCTION_CONFIG = {
    'enabled': True,
    'fetch_interval': 3600,  # 1 hour
    'batch_size': 50,
    'max_age_days': 30,
    'log_level': 'INFO'
}