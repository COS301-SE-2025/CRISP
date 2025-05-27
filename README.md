# Threat Intelligence Publication Service

A comprehensive service that allows organizations to create, anonymize, and publish threat intelligence in STIX 2.1 format via TAXII 2.1 endpoints. This implementation follows the requirements specified in SRS R2.1, R2.2, and R2.3.

## Features

- **STIX 2.1 Object Creation**
  - Support for core STIX objects (Indicator, Malware, Attack-Pattern, Threat-Actor)
  - Web API for manual threat intelligence entry
  - Bulk upload support for CSV and JSON formats
  - Auto-generation of STIX metadata (timestamps, UUIDs, relationships)

- **TAXII 2.1 Server Implementation**
  - Discovery service endpoint (GET /taxii2/)
  - Collections management (GET /taxii2/collections/)
  - Object publishing (POST /taxii2/collections/{id}/objects/)
  - Support for filtering and pagination
  - Authentication and authorization for API access

- **Trust-Based Sharing**
  - Filter shared intelligence based on trust relationships
  - Apply appropriate anonymization levels per trust level
  - Selective sharing to authorized organizations only
  - Audit logging for all sharing activities

## Technical Implementation

- Uses python-stix2 library for STIX object creation and validation
- Implements Factory Method pattern for STIX object creation (per SRS 7.3.1)
- Implements Strategy Pattern for anonymization algorithms (per SRS 7.3.3)
- Django REST Framework for TAXII API endpoints
- Comprehensive validation for STIX 2.1 compliance

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd threat_intel_service
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure your PostgreSQL database in `threat_intel/settings.py`.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Initialize the database with sample data:
   ```
   python initial_setup.py
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

### API Endpoints

#### TAXII 2.1 Endpoints

- `GET /taxii2/` - TAXII Discovery
- `GET /taxii2/collections/` - List Collections
- `GET /taxii2/collections/{id}/` - Get Collection
- `GET /taxii2/collections/{id}/objects/` - Get Objects
- `POST /taxii2/collections/{id}/objects/` - Add Objects
- `GET /taxii2/collections/{id}/objects/{object_id}/` - Get Object
- `GET /taxii2/collections/{id}/manifest/` - Get Manifest

#### REST API Endpoints

- `/api/organizations/` - Organization management
- `/api/stix/` - STIX object management
- `/api/stix/create-from-form/{stix_type}/` - Create STIX object from form data
- `/api/stix/bulk-upload/` - Bulk upload of STIX objects
- `/api/stix/{id}/anonymize/` - Create anonymized version of STIX object
- `/api/collections/` - Collection management
- `/api/collections/{id}/objects/` - Get objects in collection
- `/api/collections/{id}/add_object/` - Add object to collection
- `/api/collections/{id}/remove_object/` - Remove object from collection
- `/api/feeds/` - Feed management
- `/api/feeds/{id}/publish/` - Publish feed
- `/api/trust/relationships/` - Trust relationship management
- `/api/trust/groups/` - Trust group management
- `/api/trust/memberships/` - Trust group membership management

### Authentication

All API endpoints require authentication. The system uses OAuth2 for API authentication.

### Creating STIX Objects

#### Manual Entry

To create a STIX object via the API:

```python
import requests

# Create an indicator
data = {
    "name": "Suspicious IP",
    "description": "Indicator for a suspicious IP address",
    "pattern": "[ipv4-addr:value = '192.168.1.1']",
    "pattern_type": "stix",
    "indicator_types": ["malicious-activity"],
    "valid_from": "2023-01-01T00:00:00Z"
}

response = requests.post(
    "http://localhost:8000/api/stix/create-from-form/indicator/",
    json=data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

#### Bulk Upload

For CSV upload, you need to provide a mapping configuration:

```python
import requests

files = {
    "data": open("indicators.csv", "rb")
}

data = {
    "format": "csv",
    "mapping": {
        "stix_type": "indicator",
        "properties": {
            "name": "indicator_name",
            "description": "description",
            "labels": "tags",
            "confidence": "confidence_score"
        },
        "pattern_field": "ioc_value",
        "pattern_prefix": "[file:hashes.MD5 = '",
        "pattern_suffix": "']",
        "list_delimiter": "|"
    }
}

response = requests.post(
    "http://localhost:8000/api/stix/bulk-upload/",
    data=data,
    files=files,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Publishing Threat Intelligence

To publish threat intelligence via a feed:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/feeds/YOUR_FEED_ID/publish/",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

## Anonymization

The system supports three levels of anonymization:

- **None**: No anonymization, used for high-trust relationships
- **Partial**: Anonymizes selected sensitive fields based on trust level (default)
- **Full**: Aggressive anonymization of all sensitive fields, used for low-trust relationships

The anonymization strategy preserves the analytical value of the intelligence while protecting the source organization's sensitive information.

## Testing

To test the functionality of the system:

```
python test_functionality.py
```

This will create sample STIX objects, test anonymization, generate STIX bundles, and publish feeds.

## Audit Logging

The system logs all activities related to threat intelligence sharing, including:

- TAXII API access
- STIX object creation, updates, and deletion
- Collection management
- Trust relationship management
- Feed publishing

Logs can be accessed via the Django admin interface or directly in the database.

## Security

- OAuth2 authentication for API access
- HTTPS recommended for production deployment
- Role-based access control
- Trust-based sharing controls
- Comprehensive audit logging

## Performance

The system is designed to handle bulk processing of 100 records per second (P1.6 requirement) and supports scaling through Celery for background tasks.

## License

This project is licensed under the terms of the license included in the repository.