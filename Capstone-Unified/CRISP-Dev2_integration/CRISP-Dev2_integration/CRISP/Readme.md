# CRISP - Cyber Risk Information Sharing Platform

## Overview

CRISP (Cyber Risk Information Sharing Platform) is a comprehensive threat intelligence sharing system designed to streamline and enhance collaborative cybersecurity efforts among organizations, particularly those in the educational sector facing increasing ransomware threats. The platform enables institutions to consume external threat intelligence, create and share their own threat feeds, and apply intelligent anonymization based on trust relationships.

## Key Features

### **Threat Intelligence Consumption**
- **TAXII 2.1 Compliance**: Consumes standardized threat intelligence from external sources (AlienVault OTX, etc.)
- **STIX Processing**: Handles STIX 1.x (XML) and STIX 2.x (JSON) formats
- **Batch Processing**: Efficient handling of large volumes of threat data
- **Deduplication**: Automatic prevention of duplicate indicators and TTPs

### **Threat Feed Creation & Sharing**
- **STIX/TAXII Export**: Publish threat feeds in industry-standard formats
- **Observer Pattern**: Real-time notifications when feeds are updated
- **Collection Management**: Organize threat intelligence into collections

### **Trust-Based Anonymization**
- **Multi-Level Anonymization**: HIGH, MEDIUM, LOW, and NONE levels
- **Trust Relationships**: Define trust levels between organizations
- **Strategy Pattern**: Flexible anonymization algorithms for different data types
- **Contextual Sharing**: Share appropriate level of detail based on trust relationships

### **Organization Management**
- **Institution Support**: Educational institutions, government agencies, private organizations
- **Trust Networks**: Group-based trust management for collaborative sharing
- **Role-Based Access**: Different access levels for different organization types

## System Architecture

The CRISP platform follows a modular, service-oriented architecture implementing several design patterns:

### Core Design Patterns

#### **Factory Pattern**
```
StixObjectCreator (abstract)
├── StixIndicatorCreator: Creates STIX indicators
└── StixTTPCreator: Creates STIX attack patterns
```

#### **Decorator Pattern** 
```
StixObjectComponent (interface)
├── StixValidationDecorator: Adds validation capabilities
├── StixTaxiiExportDecorator: Adds TAXII export functionality
└── StixEnrichmentDecorator: Adds data enrichment capabilities
```

#### **Strategy Pattern**
```
AnonymizationStrategy (interface)
├── DomainAnonymizationStrategy: Anonymizes domain names
├── IPAddressAnonymizationStrategy: Anonymizes IP addresses
└── EmailAnonymizationStrategy: Anonymizes email addresses
```

#### **Observer Pattern**
```
ThreatFeed (Subject)
├── InstitutionObserver: Notifies institutions about updates
└── AlertSystemObserver: Triggers security alerts
```

## Project Structure

```
crisp/
├── manage.py                         # Django management script
├── requirements.txt                  # Project dependencies
├── .env                              # Environment variables
├── crisp_unified/                   # Django settings and configuration
│   ├── settings.py                   # Main settings
│   ├── test_settings.py              # Test-specific settings
│   ├── celery.py                     # Celery configuration
│   └── main_test_runner.py           # Orchestrated test runner
├── core/                             # Main application
│   ├── models/
│   │   └── models.py                 # Database models
│   ├── api/
│   │   └── threat_feed_views.py      # REST API endpoints
│   ├── patterns/                     # Design pattern implementations
│   │   ├── factory/                  # Factory pattern (STIX object creation)
│   │   ├── decorator/                # Decorator pattern (STIX enhancement)
│   │   ├── strategy/                 # Strategy pattern (anonymization)
│   │   └── observer/                 # Observer pattern (notifications)
│   ├── services/                     # Business logic layer
│   │   ├── stix_taxii_service.py     # STIX/TAXII operations
│   │   ├── otx_taxii_service.py      # AlienVault OTX integration
│   │   ├── indicator_service.py      # Indicator management
│   │   └── ttp_service.py            # TTP management
│   ├── repositories/                 # Data access layer
│   │   ├── threat_feed_repository.py
│   │   ├── indicator_repository.py
│   │   └── ttp_repository.py
│   ├── tasks/                        # Celery background tasks
│   │   └── taxii_tasks.py
│   ├── management/commands/          # Django management commands
│   │   ├── setup_crisp.py            # Initial setup
│   │   ├── setup_otx.py              # OTX configuration
│   │   ├── run_orchestrated_tests.py # Test runner
│   │   └── taxii_operations.py       # TAXII utilities
│   └── admin.py                      # Django admin configuration
├── crisp-react/                      # React frontend application
│   ├── package.json                  # Node.js dependencies
│   ├── vite.config.js                # Vite build configuration
│   ├── index.html                    # HTML entry point
│   ├── src/
│   │   ├── App.jsx                   # Main React application component
│   │   ├── main.jsx                  # React entry point
│   │   └── style.css                 # Application styles
│   └── public/                       # Static assets
```

## Prerequisites

### Backend Requirements
- **Python 3.9+**
- **PostgreSQL 13+**
- **Redis 6+** (for Celery)
- **RabbitMQ** (for Celery message broker)

### Frontend Requirements  
- **Node.js 18+**
- **npm 9+**

## Installation & Setup

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd CRISP

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_NAME=crisp
DB_USER=myuser
DB_PASSWORD=securepassword
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True

# External API Keys
OTX_API_KEY=your_otx_api_key  # Get from otx.alienvault.com

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 3. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE USER myuser WITH PASSWORD 'your_password';
CREATE DATABASE crisp;
GRANT ALL PRIVILEGES ON DATABASE crisp TO myuser;
\q

# Apply migrations
python manage.py makemigrations core
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Running the Application

### Backend (Django API Server)

1. **Start the Django Server**:
```bash
python manage.py runserver
```

The Django API will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

2. **Start Background Worker (Celery)**:
```bash
# Ensure Redis is running
redis-cli ping  # Should return PONG

# Start Celery worker for asynchronous processing
celery -A crisp_unified worker -l info
```

### Frontend (React UI)

1. **Navigate to the React app directory**:
```bash
cd crisp-react
```

2. **Install Node.js dependencies**:
```bash
npm install
```

3. **Start the React development server**:
```bash
npm run dev
```

The React UI will be available at [http://127.0.0.1:5173/](http://127.0.0.1:5173/) (Vite default port)

### Full System Setup (Both Backend + Frontend)

1. **Terminal 1 - Django Backend**:
```bash
# From project root
python manage.py runserver
```

2. **Terminal 2 - Celery Worker**:
```bash
# From project root  
celery -A crisp_unified worker -l info
```

3. **Terminal 3 - React Frontend**:
```bash
# From project root
cd crisp-react
npm install
npm run dev
```

### Accessing the Application

- **React UI (Main Interface)**: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
- **Django API**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## React Frontend Features

### **Dashboard**
- **Live Statistics**: Real-time display of threat feeds, IoCs, TTPs, and system status
- **Interactive Charts**: D3.js-powered threat activity trends visualization
- **System Monitoring**: Live backend connectivity status with color-coded indicators

### **Threat Feeds Management**
- **Live Feed Data**: Real-time display of all configured threat feeds
- **Feed Consumption**: One-click buttons to consume threat intelligence from external sources
- **Status Monitoring**: Live sync status, last update times, and feed health indicators
- **Feed Classification**: Visual distinction between external and internal feeds

### **IoC Management**
- **Dynamic Table**: Live display of indicators of compromise from backend
- **Real-time Data**: Indicators automatically populated from consumed threat feeds
- **Filtering & Search**: Built-in filtering capabilities for different IoC types
- **Export Controls**: Export and import functionality for IoC data

### **TTP Analysis**
- **MITRE ATT&CK Integration**: Live display of tactics, techniques, and procedures
- **Attack Tree Visualization**: Interactive charts showing TTP relationships
- **Real-time Updates**: TTPs automatically populated from threat intelligence feeds
- **Threat Actor Mapping**: Association of TTPs with specific threat actors

### **Institutions Network**
- **Trust Visualization**: Interactive network map showing trust relationships
- **Real-time Monitoring**: Live status of connected institutions
- **Statistics Dashboard**: IoC exchange statistics and activity monitoring

### **Real-time Features**
- **Auto-refresh**: System status checks every 30 seconds
- **Live Data**: All components connected to Django REST API endpoints
- **Error Handling**: Graceful degradation when backend is unavailable
- **Loading States**: User-friendly loading indicators throughout the interface

## Usage Guide

### 1. Initial Setup via Admin Interface

1. **Access Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

2. **Create Organizations**:
   - Go to "Organizations" → "Add Organization"
   - Fill in organization details (name, type, contact info)

3. **Create Trust Relationships**:
   - Go to "Trust relationships" → "Add Trust relationship" 
   - Define trust levels between organizations (HIGH: 80-100%, MEDIUM: 20-79%, LOW: 0-19%)

4. **Setup Threat Feeds**:
   - Go to "Threat feeds" → "Add Threat feed"
   - Configure external feeds (e.g., AlienVault OTX):
     ```
     Name: AlienVault OTX Feed
     Description: External threat intelligence from AlienVault OTX
     Is External: ✓
     TAXII Server URL: https://otx.alienvault.com/taxii
     TAXII API Root: taxii
     TAXII Collection ID: user_AlienVault
     TAXII Username: [Your OTX API Key]
     ```

### 2. Consuming Threat Intelligence via API

#### Start Feed Consumption

```bash
# Consume last 7 days of data in batches of 100
curl -X POST "http://127.0.0.1:8000/api/threat-feeds/1/consume/?force_days=7&batch_size=100"

# Asynchronous consumption (runs in background)
curl -X POST "http://127.0.0.1:8000/api/threat-feeds/1/consume/?force_days=7&batch_size=100&async=true"

# Limited consumption for testing
curl -X POST "http://127.0.0.1:8000/api/threat-feeds/1/consume/?limit=10"
```

#### Check Feed Status

```bash
curl -X GET "http://127.0.0.1:8000/api/threat-feeds/1/status/"
```

Example response:
```json
{
  "id": 1,
  "name": "AlienVault OTX Feed",
  "indicators_count": 1547,
  "ttps_count": 23,
  "last_sync": "2025-01-15T10:30:00Z",
  "is_external": true
}
```

### 3. Publishing Threat Feeds (TAXII Export)

```bash
# Export threat feed as STIX/TAXII
python manage.py publish_feeds --feed-id 1

# Export with anonymization based on trust relationships
python manage.py publish_feeds --feed-id 1 --anonymize --trust-level MEDIUM
```

### 4. Data Processing Flow

1. **External Consumption**: System connects to TAXII servers and retrieves STIX data
2. **Parsing**: STIX objects are parsed and converted to CRISP entities
3. **Deduplication**: System checks for existing indicators/TTPs by STIX ID
4. **Storage**: New entities are stored in PostgreSQL database
5. **Notification**: Observer pattern triggers notifications to subscribed institutions
6. **Anonymization**: When sharing, data is anonymized based on trust relationships

## Anonymization Features

### Trust Levels and Anonymization

The system applies different anonymization levels based on trust relationships:

- **HIGH Trust (80-100%)**: Minimal anonymization, full context sharing
- **MEDIUM Trust (20-79%)**: Moderate anonymization, some details preserved
- **LOW Trust (0-19%)**: Heavy anonymization, limited context
- **NO Trust**: No sharing or complete anonymization

### Anonymization Examples

#### Domain Anonymization
```python
# Original: "malicious.example.com"
# LOW trust: "*.edu" (category-based)
# MEDIUM trust: "malicious.XXX.com" (partial masking)
# HIGH trust: "malicious.example.com" (full disclosure)
```

#### IP Address Anonymization  
```python
# Original: "192.168.1.100"
# LOW trust: "192.168.1.XXX" (subnet preserved)
# MEDIUM trust: "192.168.XXX.XXX" (network preserved)
# HIGH trust: "192.168.1.100" (full disclosure)
```

## Testing

### Run All Tests

```bash
# Run comprehensive test suite
python manage.py run_orchestrated_tests --settings=crisp_unified.test_settings
```

### Test Categories

The test suite is organized into logical categories:

1. **Foundation Tests**: Core design patterns (Factory, Decorator, Strategy, Observer)
2. **Data Layer Tests**: Repository pattern and database operations
3. **Service Layer Tests**: Business logic and TAXII operations
4. **Integration Tests**: Component interaction testing
5. **API Tests**: REST endpoint testing

### Run Specific Test Categories

```bash
# Test only design patterns
python manage.py test core.tests.test_factory core.tests.test_decorator --settings=crisp_unified.test_settings

# Test TAXII services
python manage.py test core.tests.test_taxii_service --settings=crisp_unified.test_settings

# Test anonymization strategies
python manage.py test core.tests.test_strategy --settings=crisp_unified.test_settings
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py run_orchestrated_tests --settings=crisp_unified.test_settings

# Generate coverage report
coverage report
coverage html  # Generates HTML report in htmlcov/
```

## API Endpoints

### Threat Feed Management

```bash
# List all threat feeds
GET /api/threat-feeds/

# Get specific threat feed details
GET /api/threat-feeds/{id}/

# Start feed consumption
POST /api/threat-feeds/{id}/consume/

# Get feed status and statistics
GET /api/threat-feeds/{id}/status/

# Export feed as STIX/TAXII
POST /api/threat-feeds/{id}/export/
```

### Indicators and TTPs

```bash
# List indicators for a feed
GET /api/threat-feeds/{id}/indicators/

# List TTPs for a feed  
GET /api/threat-feeds/{id}/ttps/

# Get specific indicator
GET /api/indicators/{id}/

# Get specific TTP
GET /api/ttps/{id}/
```

## Architecture Benefits

### Design Pattern Benefits

1. **Factory Pattern**: Standardized STIX object creation with consistent validation
2. **Decorator Pattern**: Flexible enhancement of STIX objects without modifying core classes
3. **Strategy Pattern**: Pluggable anonymization algorithms for different data types
4. **Observer Pattern**: Decoupled notification system for real-time updates

### Technical Advantages

- **Modular Architecture**: Easy to extend and maintain
- **Batch Processing**: Efficient handling of large datasets
- **Asynchronous Processing**: Non-blocking operations with Celery
- **Industry Standards**: Full STIX/TAXII compliance
- **Test Coverage**: Comprehensive test suite (>90% coverage)

## Deployment Considerations

### Production Settings

1. **Database**: Use PostgreSQL with connection pooling
2. **Cache**: Redis for session storage and caching
3. **Queue**: RabbitMQ or Redis for Celery message broker
4. **Web Server**: Gunicorn with Nginx reverse proxy
5. **Security**: HTTPS, secure headers, input validation

### Scaling

- **Horizontal Scaling**: Multiple Celery workers for feed consumption
- **Database Optimization**: Indexes on STIX IDs and timestamps
- **Caching**: Cache frequently accessed threat intelligence data
- **Load Balancing**: Multiple Django instances behind load balancer

---

**CRISP Platform** - Enhancing cybersecurity through collaborative threat intelligence sharing.
