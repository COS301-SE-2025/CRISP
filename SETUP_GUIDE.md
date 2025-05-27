# CRISP TAXII Feed Consumer Setup Guide

This guide will help you set up the TAXII Feed Consumption Service for the CRISP (Cyber Risk Information Sharing Platform) project.

## Development Environment Setup

### Prerequisites

Make sure you have the following installed:
- Python 3.9+
- SQLite (included with Python)
- Redis (optional, for production)
- PostgreSQL (optional, for production)

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/CRISP.git
cd CRISP
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root with the following content:

```
# Database settings (SQLite for development)
# For PostgreSQL in production, uncomment and update these:
# DB_NAME=crisp_db
# DB_USER=postgres
# DB_PASSWORD=yourpassword
# DB_HOST=localhost
# DB_PORT=5432

# TAXII client settings
TAXII_VERIFY_SSL=True
TAXII_PAGE_SIZE=100
CRISP_VERSION=1.0.0

# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Step 5: Apply migrations

```bash
python manage.py migrate
```

### Step 6: Create a superuser

```bash
python manage.py createsuperuser
```

### Step 7: Start the development server

```bash
python manage.py runserver
```

### Step 8: Start Celery worker (for background tasks)

```bash
# Terminal 1 - Celery worker
celery -A crisp_project worker --loglevel=info

# Terminal 2 - Celery beat scheduler (for periodic tasks)
celery -A crisp_project beat --loglevel=info
```

## Production Deployment

For production, you'll need to:

1. Set up PostgreSQL database
2. Set up Redis for Celery
3. Configure a web server like Nginx
4. Use Gunicorn or uWSGI as the WSGI server
5. Set up Supervisor to manage Celery processes
6. Set DEBUG=False in .env
7. Update SECRET_KEY with a secure random key

## Using the Application

1. Access the admin interface at http://localhost:8000/admin
2. Go to Feed Sources and add a new TAXII feed source
3. Configure the feed with appropriate authentication details
4. Use the "Discover" feature to find collections
5. Select a collection and set polling interval
6. Feeds will be consumed automatically based on the polling schedule

## API Usage

The application provides a REST API for programmatic usage:

```python
import requests

# Get authentication token (if authentication is enabled)
auth_response = requests.post('http://localhost:8000/api/token/', {
    'username': 'admin',
    'password': 'password'
})
token = auth_response.json()['access']

# Create a new feed source
response = requests.post(
    'http://localhost:8000/api/feed-sources/',
    json={
        'name': 'Example Feed',
        'discovery_url': 'https://example.com/taxii2/',
        'categories': ['malware', 'indicators'],
        'poll_interval': 'daily',
        'auth_type': 'api_key',
        'auth_credentials': {
            'key': 'your-api-key',
            'header_name': 'Authorization'
        },
        'is_active': True
    },
    headers={'Authorization': f'Bearer {token}'}
)
```

## Troubleshooting

- If Celery tasks aren't running, check Redis connection or database backend
- For authentication issues with TAXII feeds, verify credentials in the feed source configuration
- Check feed consumption logs in the admin interface for detailed error messages
- Database migration errors might require manual intervention or resetting migrations
