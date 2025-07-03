# CRISP Anonymization System

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Components](#core-components)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)
9. [Testing](#testing)
10. [Contributing](#contributing)

## Overview

The **CRISP (Cyber Risk Information Sharing Platform) Anonymization System** is a sophisticated Python framework designed for anonymizing cybersecurity threat intelligence data. The system enables secure sharing of threat intelligence between organizations while maintaining data utility through configurable anonymization levels.

### Key Features

- 🔒 **Multi-level Anonymization**: Five levels from minimal to complete anonymization
- 🎯 **Trust-based Processing**: Anonymization based on recipient trust relationships
- 📊 **STIX 2.0/2.1 Support**: Native support for structured threat intelligence
- 🤖 **Auto-detection**: Automatic identification of data types (IP, domain, email, URL)
- 🔄 **Consistent Anonymization**: Maintains consistency across multiple operations
- 📦 **Zero Dependencies**: Core functionality uses only Python standard library
- 🧪 **Comprehensive Testing**: Extensive test suite with detailed output
- ⚙️ **Configurable**: YAML-based configuration system

## System Architecture

The system implements the **Strategy Pattern** for flexible anonymization approaches:

```
CRISP Anonymization System
├── Core Context (AnonymizationContext)
├── Strategy Pattern Implementation
│   ├── IPAddressAnonymizationStrategy
│   ├── DomainAnonymizationStrategy
│   ├── EmailAnonymizationStrategy
│   └── URLAnonymizationStrategy
├── Enumeration Definitions
│   ├── AnonymizationLevel (NONE, LOW, MEDIUM, HIGH, FULL)
│   └── DataType (IP_ADDRESS, DOMAIN, EMAIL, URL, HASH, FILENAME)
├── STIX Intelligence Support
└── Configuration Management
```

## Installation

### Prerequisites
- Python 3.7 or higher

### Basic Installation
```bash
# Clone the repository
git clone https://github.com/COS301-SE-2025/CRISP.git
cd CRISP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package in development mode
pip install -e .
```

### Development Installation
```bash
# Install with development dependencies
pip install -e .[dev]

# Install with STIX support
pip install -e .[stix]

# Install all extras
pip install -e .[dev,stix,docs]
```

### Environment Setup
```bash
# Set Python path for testing
export PYTHONPATH=/path/to/CRISP:$PYTHONPATH
```

## Quick Start

### Basic Usage

```python
from crisp_anonymization import AnonymizationContext, AnonymizationLevel, DataType

# Initialize the anonymization context
context = AnonymizationContext()

# Anonymize an IP address
ip = "192.168.1.100"
anonymized_ip = context.execute_anonymization(ip, DataType.IP_ADDRESS, AnonymizationLevel.MEDIUM)
print(f"{ip} → {anonymized_ip}")  # 192.168.1.100 → 192.168.x.x

# Auto-detect and anonymize
data = "malicious.example.com"
result = context.auto_detect_and_anonymize(data, AnonymizationLevel.HIGH)
print(f"{data} → {result}")  # malicious.example.com → *.commercial
```

### Command Line Usage

```bash
# Run the main demonstration
python3 main.py

# Interactive mode
python3 main.py interactive

# Demo mode
python3 main.py demo

# Test mode
python3 main.py test
```

## Core Components

### 1. AnonymizationContext

The central orchestrator that manages strategies and executes anonymization operations.

```python
class AnonymizationContext:
    def __init__(self)
    def register_strategy(self, data_type: DataType, strategy: AnonymizationStrategy)
    def execute_anonymization(self, data: str, data_type: DataType, level: AnonymizationLevel) -> str
    def auto_detect_and_anonymize(self, data: str, level: AnonymizationLevel) -> str
    def bulk_anonymize(self, data_items: List[Tuple[str, DataType]], level: AnonymizationLevel) -> List[str]
    def anonymize_stix_object(self, stix_data: Union[str, Dict], level: AnonymizationLevel) -> str
```

### 2. Anonymization Strategies

#### IPAddressAnonymizationStrategy
Handles IPv4 and IPv6 address anonymization with zone identifier support.

**Anonymization Levels:**
- **LOW**: Mask last octet (IPv4) or last 16 bits (IPv6)
- **MEDIUM**: Mask last two octets (IPv4) or last 32 bits (IPv6)
- **HIGH**: Mask last three octets (IPv4) or preserve only first 64 bits (IPv6)
- **FULL**: Replace with hash-based anonymous identifier

```python
# Examples
"192.168.1.100" → "192.168.1.x"     # LOW
"192.168.1.100" → "192.168.x.x"     # MEDIUM
"192.168.1.100" → "192.x.x.x"       # HIGH
"192.168.1.100" → "anon-ipv4-d984a05f"  # FULL
```

#### DomainAnonymizationStrategy
Anonymizes domain names while preserving semantic meaning through TLD categorization.

**TLD Categories:**
- Commercial: `.com`, `.biz` → `*.commercial`
- Educational: `.edu`, `.ac.*` → `*.educational`
- Government: `.gov`, `.mil` → `*.government`
- Organization: `.org`, `.net` → `*.organization`
- Other: All others → `*.other`

```python
# Examples
"subdomain.example.com" → "*.example.com"     # LOW
"subdomain.example.com" → "*.com"             # MEDIUM
"subdomain.example.com" → "*.commercial"      # HIGH
"subdomain.example.com" → "anon-domain-85f5d183.example"  # FULL
```

#### EmailAnonymizationStrategy
Handles email address anonymization with domain integration.

```python
# Examples
"user@example.com" → "user-ee11cb@example.com"      # LOW
"user@example.com" → "user-ee11cb@*.example.com"    # MEDIUM
"user@example.com" → "user@*.commercial"            # HIGH
"user@example.com" → "anon-user-b58996c5@example.com"  # FULL
```

#### URLAnonymizationStrategy
Anonymizes URLs while preserving protocol information.

```python
# Examples
url = "https://example.com/path/to/resource?query=value"
# LOW: "https://*.example.com/[path-removed]"
# MEDIUM: "https://*.com"
# HIGH: "https://*.commercial"
# FULL: "https://anon-url-e0f989cc.example"
```

### 3. Enumeration Types

#### AnonymizationLevel
```python
class AnonymizationLevel(Enum):
    NONE = "none"        # No anonymization
    LOW = "low"          # Minimal anonymization
    MEDIUM = "medium"    # Moderate anonymization
    HIGH = "high"        # High anonymization
    FULL = "full"        # Complete anonymization
```

#### DataType
```python
class DataType(Enum):
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    EMAIL = "email"
    URL = "url"
    HASH = "hash"
    FILENAME = "filename"
```

### 4. Exception Hierarchy

```python
AnonymizationError                    # Base exception
├── InvalidDataTypeError              # Invalid data type
├── StrategyNotFoundError             # No suitable strategy
├── InvalidAnonymizationLevelError    # Invalid level
└── DataValidationError               # Format validation error
```

## API Reference

### Core Classes

#### AnonymizationContext

The main class for orchestrating anonymization operations.

**Constructor:**
```python
def __init__(self):
    """Initialize the anonymization context with default strategies."""
```

**Core Methods:**

```python
def execute_anonymization(self, data: str, data_type: DataType, level: AnonymizationLevel) -> str:
    """
    Execute anonymization for specific data type and level.
    
    Args:
        data: Input data to anonymize
        data_type: Type of data (IP_ADDRESS, DOMAIN, EMAIL, URL)
        level: Anonymization level (NONE, LOW, MEDIUM, HIGH, FULL)
    
    Returns:
        Anonymized data string
    
    Raises:
        StrategyNotFoundError: If no strategy found for data type
        DataValidationError: If data format is invalid
    """
```

```python
def auto_detect_and_anonymize(self, data: str, level: AnonymizationLevel) -> str:
    """
    Auto-detect data type and anonymize.
    
    Args:
        data: Input data to anonymize
        level: Anonymization level
    
    Returns:
        Anonymized data string
    """
```

```python
def bulk_anonymize(self, data_items: List[Tuple[str, DataType]], level: AnonymizationLevel) -> List[str]:
    """
    Anonymize multiple data items efficiently.
    
    Args:
        data_items: List of (data, data_type) tuples
        level: Anonymization level for all items
    
    Returns:
        List of anonymized strings
    """
```

```python
def anonymize_stix_object(self, stix_data: Union[str, Dict], level: AnonymizationLevel, 
                         preserve_timestamps: bool = True, time_shift_days: int = 0) -> str:
    """
    Anonymize STIX 2.0/2.1 threat intelligence objects.
    
    Args:
        stix_data: STIX object as JSON string or dictionary
        level: Anonymization level
        preserve_timestamps: Whether to preserve original timestamps
        time_shift_days: Days to shift timestamps (if not preserving)
    
    Returns:
        Anonymized STIX object as JSON string
    """
```

#### AnonymizationStrategy (Abstract Base)

Base class for all anonymization strategies.

```python
class AnonymizationStrategy(ABC):
    @abstractmethod
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        """Anonymize data at specified level."""
        
    @abstractmethod
    def can_handle(self, data_type: DataType) -> bool:
        """Check if strategy can handle data type."""
        
    @abstractmethod
    def validate(self, data: str) -> bool:
        """Validate data format."""
```

### Utility Classes

#### AnonymizationUtils

Static utility methods for common anonymization operations.

```python
class AnonymizationUtils:
    @staticmethod
    def generate_consistent_hash(data: str, length: int = 8) -> str:
        """Generate consistent hash for data (MD5-based)."""
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """Generate random string."""
    
    @staticmethod
    def mask_string(data: str, visible_chars: int = 2, mask_char: str = 'x') -> str:
        """Mask string with specified character."""
    
    @staticmethod
    def categorize_tld(tld: str) -> str:
        """Categorize TLD into semantic groups."""
    
    @staticmethod
    def validate_data_format(data: str, data_type: DataType) -> bool:
        """Validate data format for specified type."""
```

## Configuration

The system uses YAML-based configuration in `config.yaml`:

### Basic Configuration Structure

```yaml
anonymization:
  default_level: "medium"
  hash_algorithm: "md5"
  hash_length: 8
  preserve_structure: true
  
trust_relationships:
  institution_mappings:
    high_trust: "low"
    medium_trust: "medium"
    low_trust: "high"
    untrusted: "full"
    
data_types:
  ip_address:
    preserve_private_ranges: false
    zone_identifier_handling: "preserve"
  domain:
    tld_categorization: true
    subdomain_preservation: "smart"
  email:
    local_part_anonymization: "hash_suffix"
    domain_integration: true
  url:
    protocol_preservation: true
    path_removal_level: "low"

processing:
  batch_size: 1000
  enable_caching: true
  cache_ttl_seconds: 3600
  max_cache_entries: 10000
  error_handling: "log_and_continue"
  
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_logging: false
  log_file: "crisp_anonymization.log"
  
integration:
  stix:
    supported_versions: ["2.0", "2.1"]
    preserve_relationships: true
    anonymize_custom_properties: true
  taxii:
    endpoint_anonymization: "full"
    collection_id_handling: "preserve"
    
security:
  audit_logging: true
  data_retention_days: 30
  secure_delete: true
  access_control: false
  
development:
  debug_mode: false
  performance_monitoring: false
  test_data_generation: true
```

### Loading Configuration

```python
import yaml
from crisp_anonymization import AnonymizationContext

# Load custom configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Apply configuration to context
context = AnonymizationContext()
context.apply_config(config)
```

## Usage Examples

### Basic Anonymization

```python
from crisp_anonymization import AnonymizationContext, AnonymizationLevel, DataType

context = AnonymizationContext()

# Different data types
examples = [
    ("192.168.1.100", DataType.IP_ADDRESS),
    ("malicious.example.com", DataType.DOMAIN),
    ("attacker@evil.org", DataType.EMAIL),
    ("https://phishing.site.com/login", DataType.URL)
]

for data, data_type in examples:
    for level in [AnonymizationLevel.LOW, AnonymizationLevel.MEDIUM, 
                  AnonymizationLevel.HIGH, AnonymizationLevel.FULL]:
        result = context.execute_anonymization(data, data_type, level)
        print(f"{level.name:6}: {data} → {result}")
```

### Auto-Detection

```python
# Auto-detect data types
mixed_data = [
    "10.0.0.1",
    "2001:db8::1", 
    "suspicious.domain.com",
    "attacker@criminal.org",
    "https://malware-drop.badsite.net/trojan.exe"
]

for data in mixed_data:
    detected_type = context._detect_data_type(data)
    result = context.auto_detect_and_anonymize(data, AnonymizationLevel.MEDIUM)
    print(f"{data} ({detected_type.value}) → {result}")
```

### Bulk Processing

```python
# Bulk anonymization
threat_indicators = [
    ("203.0.113.42", DataType.IP_ADDRESS),
    ("malware-c2.evil-corp.net", DataType.DOMAIN),
    ("ceo@fake-company.com", DataType.EMAIL),
    ("https://phishing-site.badactor.org/login", DataType.URL)
]

anonymized = context.bulk_anonymize(threat_indicators, AnonymizationLevel.HIGH)
for original, result in zip(threat_indicators, anonymized):
    print(f"{original[0]} → {result}")
```

### STIX Anonymization

```python
# STIX threat intelligence
stix_indicator = {
    "type": "indicator",
    "spec_version": "2.1",
    "id": "indicator--d81f86b8-975b-4c0b-875e-810c5ad40ac2",
    "created": "2021-03-01T15:30:00.000Z",
    "modified": "2021-03-01T15:30:00.000Z",
    "name": "Malicious IP Address",
    "description": "This IP address 192.168.1.100 was observed in malicious activity",
    "indicator_types": ["malicious-activity"],
    "pattern_type": "stix",
    "pattern": "[ipv4-addr:value = '192.168.1.100']",
    "valid_from": "2021-03-01T15:30:00.000Z"
}

anonymized_stix = context.anonymize_stix_object(stix_indicator, AnonymizationLevel.MEDIUM)
print(anonymized_stix)
```

### Trust-Based Sharing

```python
from main import ThreatIntelligenceProcessor

processor = ThreatIntelligenceProcessor()

threat_data = [
    {
        "id": "TI-001",
        "ip": "203.0.113.42",
        "domain": "malware-c2.evil-corp.net",
        "severity": "high"
    }
]

# Share with different trust levels
trust_levels = ["high", "medium", "low", "untrusted"]
for trust in trust_levels:
    anonymized = processor.process_threat_feed(threat_data, trust)
    print(f"\nSharing with {trust} trust:")
    print(f"  IP: {anonymized[0]['ip']}")
    print(f"  Domain: {anonymized[0]['domain']}")
```

## Testing

### Running Tests

```bash
# Set Python path
export PYTHONPATH=/path/to/CRISP:$PYTHONPATH

# Run all tests
python3 core/tests/test_anonymization.py
python3 core/tests/test_strategies.py
python3 core/tests/additional_tests.py
python3 core/tests/quick_test.py

# Run with make
make test          # Basic tests
make test-all      # All test files
make quick-test    # Quick validation

# Run with pytest (if installed)
pytest core/tests/ -v
```

### Test Structure

The test suite includes:

- **test_anonymization.py**: Core anonymization functionality
- **test_strategies.py**: Individual strategy testing with detailed output
- **additional_tests.py**: Edge cases and error handling
- **quick_test.py**: Basic validation tests

### Detailed Test Output

The test suite provides comprehensive output showing:
- Input and output for each anonymization level
- Special case handling (loopback IPs, multicast, etc.)
- Domain categorization verification
- Error handling validation

```bash
=== Testing IPv4 anonymization for: 192.168.1.100 ===
NONE level:   192.168.1.100 → 192.168.1.100
LOW level:    192.168.1.100 → 192.168.1.x
MEDIUM level: 192.168.1.100 → 192.168.x.x
HIGH level:   192.168.1.100 → 192.x.x.x
FULL level:   192.168.1.100 → anon-ipv4-d984a05f
```

## Development

### Project Structure

```
CRISP/
├── crisp_anonymization/           # Main package
│   ├── __init__.py               # Package exports
│   ├── enums.py                  # Enumeration definitions
│   ├── exceptions.py             # Exception hierarchy
│   ├── strategies.py             # Strategy implementations
│   ├── context.py                # Main context manager
│   ├── utils.py                  # Utility functions
│   └── demo.py                   # Demo functions
├── core/                         # Alternative structure
│   ├── patterns/strategy/        # Strategy pattern implementation
│   └── tests/                    # Test suite
├── main.py                       # Main application
├── config.yaml                   # Configuration file
├── setup.py                      # Package setup
├── makefile                      # Build automation
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

### Adding New Strategies

1. Create a new strategy class inheriting from `AnonymizationStrategy`:

```python
from crisp_anonymization import AnonymizationStrategy, DataType, AnonymizationLevel

class CustomAnonymizationStrategy(AnonymizationStrategy):
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        # Implement anonymization logic
        pass
    
    def can_handle(self, data_type: DataType) -> bool:
        # Return True if strategy can handle data_type
        pass
    
    def validate(self, data: str) -> bool:
        # Validate data format
        pass
```

2. Register the strategy:

```python
context = AnonymizationContext()
context.register_strategy(DataType.CUSTOM, CustomAnonymizationStrategy())
```

### Adding New Data Types

1. Add to the `DataType` enum:

```python
class DataType(Enum):
    # ... existing types
    CUSTOM = "custom"
```

2. Implement detection logic in `context.py`:

```python
def _detect_data_type(self, data: str) -> DataType:
    # Add detection logic for custom type
    if self._is_custom_format(data):
        return DataType.CUSTOM
    # ... existing logic
```

### Code Style

The project follows Python PEP 8 standards:

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy crisp_anonymization/
```

## Contributing

### Development Setup

1. Fork the repository
2. Create a development branch
3. Install development dependencies:

```bash
pip install -e .[dev]
```

4. Make changes and add tests
5. Run the test suite:

```bash
make test-all
```

6. Submit a pull request

### Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure backward compatibility
- Add type hints to all functions

### Security Considerations

This system is designed for **defensive cybersecurity purposes only**:

- ✅ Anonymizing threat intelligence for sharing
- ✅ Privacy-preserving security research
- ✅ Compliance with data protection regulations
- ✅ Secure inter-organizational collaboration

The system should **NOT** be used for:
- ❌ Hiding malicious activities
- ❌ Evading security controls
- ❌ Facilitating unauthorized access
- ❌ Any illegal or harmful purposes

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](https://github.com/COS301-SE-2025/CRISP/issues)
- **Documentation**: [GitHub Wiki](https://github.com/COS301-SE-2025/CRISP/wiki)
- **Source Code**: [GitHub Repository](https://github.com/COS301-SE-2025/CRISP)

## Changelog

### Version 1.0.0
- Initial release
- Core anonymization strategies
- STIX 2.0/2.1 support
- Configuration system
- Comprehensive test suite
- Trust-based sharing capabilities
- Auto-detection functionality