# TAXII Feed Consumption Service

A Django application for consuming external TAXII 2.1 compliant threat intelligence feeds, part of the CRISP (Cyber Risk Information Sharing Platform) project.

## Overview

This service provides a complete implementation for consuming STIX/TAXII 2.1 threat intelligence feeds, including:

- TAXII 2.1 client implementation for discovery and data retrieval
- Feed configuration management with Django admin interface
- Asynchronous data processing with Celery
- Duplicate detection and education sector relevance tagging
- Comprehensive error handling and monitoring

## Features

- **TAXII 2.1 Client**:
  - Discovery service client (GET /taxii2/)
  - Collections enumeration (GET /taxii2/collections/)
  - Object retrieval with filtering (GET /taxii2/collections/{id}/objects/)
  - Support for API key, JWT, and basic authentication

- **Feed Configuration**:
  - Django models for external feed sources
  - Admin interface for configuration
  - Support for feed categorization (malware, indicators, TTPs)
  - Configurable polling intervals (hourly, daily, weekly)

- **Data Processing**:
  - STIX 2.1 format validation
  - Normalization to internal schema
  - Duplicate detection across feed sources
  - Education sector relevance tagging

- **Error Handling**:
  - Comprehensive logging for all activities
  - Graceful handling of network and authentication failures
  - Retry mechanism with exponential backoff
  - Health check endpoints for monitoring

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- RabbitMQ (for Celery)

### Setup

1. Add the application to your Django project:

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'feed_consumption',
]

# TAXII client settings
TAXII_VERIFY_SSL = True  # Set to False for development/testing with self-signed certs
TAXII_PAGE_SIZE = 100    # Number of objects to retrieve per page
CRISP_VERSION = '1.0.0'  # Used in User-Agent header
```

2. Set up Celery for asynchronous tasks:

```python
# celery.py
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Add periodic tasks
app.conf.beat_schedule = {
    'schedule-feed-consumption': {
        'task': 'feed_consumption.tasks.schedule_feed_consumption',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'retry-failed-feeds': {
        'task': 'feed_consumption.tasks.retry_failed_feeds',
        'schedule': 3600.0,  # Run every hour
    },
}
```

3. Apply migrations:

```bash
python manage.py makemigrations feed_consumption
python manage.py migrate
```

4. Start the Celery worker and beat scheduler:

```bash
celery -A your_project worker -l info
celery -A your_project beat -l info
```

## Usage

### Adding a Feed Source

1. Via the Django Admin interface:
   - Navigate to Feed Sources section
   - Click "Add Feed Source"
   - Enter the feed details (name, discovery URL, authentication)
   - Set categories and polling interval
   - Save to activate the feed

2. Via the API:

```python
from feed_consumption.models import ExternalFeedSource

feed = ExternalFeedSource.objects.create(
    name='MISP Community Feed',
    discovery_url='https://example.com/taxii2/',
    categories=['malware', 'indicators'],
    poll_interval=ExternalFeedSource.PollInterval.DAILY,
    auth_type=ExternalFeedSource.AuthType.API_KEY,
    auth_credentials={'key': 'your-api-key', 'header_name': 'Authorization'},
    is_active=True,
    added_by=request.user
)
```

### Manually Triggering Feed Consumption

1. Via the Django Admin interface:
   - Go to the Feed Source detail page
   - Click "Refresh Now" button

2. Via the API:

```python
from feed_consumption.tasks import manual_feed_refresh

# Trigger immediate refresh
result = manual_feed_refresh.delay(str(feed_id))
```

3. Via management command:

```bash
python manage.py refresh_feed <feed_id>
```

### Monitoring Feed Status

1. Check the Feed Consumption Logs in the admin interface
2. Use the health check endpoint:

```
GET /feed-consumption/health/
```

3. Check the dashboard for analytics:

```
GET /feed-consumption/dashboard/
```

## API Endpoints

The service provides a REST API for managing feed sources and monitoring consumption:

- `GET /api/feed-sources/` - List all feed sources
- `POST /api/feed-sources/` - Create a new feed source
- `GET /api/feed-sources/{id}/` - Get feed source details
- `POST /api/feed-sources/{id}/refresh/` - Trigger immediate refresh
- `GET /api/feed-sources/{id}/collections/` - List available TAXII collections
- `POST /api/feed-sources/{id}/set_collection/` - Set active collection
- `GET /api/feed-sources/{id}/discover/` - Perform TAXII discovery
- `GET /api/feed-sources/stats/` - Get feed source statistics
- `GET /api/consumption-logs/` - List consumption logs
- `GET /api/consumption-logs/{id}/` - Get consumption log details
- `GET /api/consumption-logs/stats/` - Get consumption statistics

## Architecture

The feed consumption service follows a modular architecture:

1. **Models Layer**:
   - `ExternalFeedSource` - Configuration for feed sources
   - `FeedConsumptionLog` - Logging for consumption activities

2. **Service Layer**:
   - `TaxiiClient` - Handles TAXII protocol communication
   - `DataProcessor` - Validates, normalizes, and stores threat data

3. **Task Layer**:
   - Celery tasks for asynchronous processing
   - Scheduled polling based on intervals
   - Retry mechanism for failed feeds

4. **API Layer**:
   - REST API for feed management
   - Health check and monitoring endpoints

## Testing

Run the comprehensive test suite with:

```bash
python manage.py test feed_consumption
```

The tests cover:
- Model validation and methods
- TAXII client functionality
- Data processing pipeline
- Celery tasks
- API endpoints

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
