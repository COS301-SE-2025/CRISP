# CRISP Anonymization System

A flexible system for anonymizing cybersecurity threat intelligence data at different levels of sensitivity for secure information sharing.

## Overview

The CRISP Anonymization System is a core component of the Cyber Risk Information Sharing Platform (CRISP), designed to facilitate secure sharing of threat intelligence between organizations. It provides configurable anonymization strategies for various types of sensitive data found in threat intelligence feeds, including:

- IP addresses (IPv4 and IPv6)
- Domain names
- Email addresses
- URLs
- STIX 2.1 objects and bundles

## Key Features

- **Multiple Anonymization Levels**: Control the degree of information loss through five anonymization levels:
  - `NONE`: No anonymization, original data preserved
  - `LOW`: Minimal anonymization, most information preserved
  - `MEDIUM`: Moderate anonymization, partial information preserved
  - `HIGH`: High anonymization, minimal information preserved
  - `FULL`: Complete anonymization with consistent hashing

- **Strategy Pattern Implementation**: Extensible architecture using the Strategy design pattern allows easy addition of new anonymization strategies for different data types.

- **Auto-Detection**: Automatically detect data types based on patterns and apply appropriate anonymization strategies.

- **Consistent Anonymization**: Same input values are consistently anonymized to the same output values within a session.

- **STIX 2.1 Support**: Full support for anonymizing STIX 2.1 objects and bundles while preserving their structure and referential integrity.

- **Trust-Based Sharing**: Anonymize data based on trust relationships between organizations.

## Installation

```bash
pip install crisp-anonymization
```

## Basic Usage

```python
from crisp_anonymization import AnonymizationContext, AnonymizationLevel, DataType

# Create anonymization context
context = AnonymizationContext()

# Anonymize an IP address
ip = "192.168.1.100"
anonymized_ip = context.execute_anonymization(ip, DataType.IP_ADDRESS, AnonymizationLevel.MEDIUM)
print(f"Original: {ip}, Anonymized: {anonymized_ip}")  # Output: Original: 192.168.1.100, Anonymized: 192.168.x.x

# Anonymize a domain
domain = "malicious.example.com"
anonymized_domain = context.execute_anonymization(domain, DataType.DOMAIN, AnonymizationLevel.LOW)
print(f"Original: {domain}, Anonymized: {anonymized_domain}")  # Output: Original: malicious.example.com, Anonymized: *.example.com

# Auto-detect and anonymize
mixed_data = "attacker@evil.com"
anonymized_mixed = context.auto_detect_and_anonymize(mixed_data, AnonymizationLevel.HIGH)
print(f"Original: {mixed_data}, Anonymized: {anonymized_mixed}")  # Output: Original: attacker@evil.com, Anonymized: user@*.commercial
```

## STIX 2.1 Anonymization

```python
import json
from crisp_anonymization import AnonymizationContext, AnonymizationLevel

# Create anonymization context
context = AnonymizationContext()

# Sample STIX Indicator
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

# Anonymize STIX object
anonymized_stix = context.anonymize_stix_object(stix_indicator, AnonymizationLevel.MEDIUM)
print(anonymized_stix)
```

## Command Line Usage

```bash
# Run demo mode
python -m crisp_anonymization.main --mode demo

# Run interactive mode
python -m crisp_anonymization.main --mode interactive

# Process STIX file
python -m crisp_anonymization.main --mode stix --file input.json --trust medium --output anonymized.json
```

## Extending the System

To add a new anonymization strategy:

1. Create a new class that inherits from `AnonymizationStrategy`
2. Implement the required methods: `anonymize()`, `can_handle()`, and `validate()`
3. Register the strategy with the `AnonymizationContext`:

```python
from crisp_anonymization import AnonymizationContext, AnonymizationStrategy, AnonymizationLevel, DataType

class HashAnonymizationStrategy(AnonymizationStrategy):
    def anonymize(self, data: str, level: AnonymizationLevel) -> str:
        # Implementation here
        
    def can_handle(self, data_type: DataType) -> bool