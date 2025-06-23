

CRISP is a system designed to streamline and enhance threat intelligence sharing among organizations, particularly those in the educational sector facing increasing ransomware threats. The platform enables institutions to share Indicators of Compromise (IoCs), Tactics, Techniques, and Procedures (TTPs) in a secure, standardized way while maintaining appropriate levels of confidentiality through anonymization.

## Overview

CRISP addresses the critical need for timely and effective information sharing regarding cybersecurity incidents. When an organization is attacked, similar organizations often become subsequent targets. By providing a platform for sharing threat intelligence, CRISP enables institutions to proactively defend against emerging threats.

Inspired by the Malware Information Sharing Platform (MISP) and the CIRCL information sharing community, CRISP facilitates both consumption of external threat feeds and publication of anonymized threat data.

## System Architecture

The CRISP system follows a modular, service-oriented architecture implementing several design patterns to ensure flexibility, extensibility, and maintainability.

### Core Components

#### Domain Model

- **Institution**: Organizations that share/consume threat intelligence
- **User**: Employees of institutions who interact with the system
- **ThreatFeed**: Collections of threat data owned by institutions
- **Indicator/IoC**: Indicators of compromise that might signal a threat
- **TTPData**: Tactics, Techniques, and Procedures used by threat actors

#### Service Layer

- **ThreatFeedService**: Manages threat feeds
- **IndicatorService**: Handles IoC operations
- **TTPService**: Manages TTP data
- **StixTaxiiService**: Handles STIX/TAXII operations for standardized sharing
- **OTXTaxiiService**: Specialized service for AlienVault OTX TAXII feeds

#### Repository Layer

- **ThreatFeedRepository**: Manages storage and retrieval of threat feeds
- **IndicatorRepository**: Manages storage and retrieval of indicators
- **TTPRepository**: Manages storage and retrieval of TTP data

### Design Patterns Implementation

#### Factory Pattern

The Factory Method pattern standardizes the creation of STIX objects from CRISP entities:

- **StixObjectCreator** (abstract): Defines interface for creating STIX objects
- **StixIndicatorCreator**: Creates STIX indicators from CRISP Indicators
- **StixTTPCreator**: Creates STIX attack patterns from CRISP TTPs

This pattern allows for consistent creation of STIX objects while hiding the complexity of the creation process from client code. Each creator knows how to convert between CRISP entities and STIX objects.

#### Decorator Pattern

The Decorator pattern dynamically adds capabilities to STIX objects:

- **StixObjectComponent** (interface): Defines the component interface
- **StixDecorator** (abstract): Base decorator class
- **StixValidationDecorator**: Adds validation capabilities
- **StixTaxiiExportDecorator**: Adds TAXII export functionality
- **StixEnrichmentDecorator**: Adds data enrichment capabilities

This pattern allows for flexible enhancement of STIX objects without modifying their core functionality, adhering to the Open-Closed Principle.

#### Strategy Pattern

The Strategy pattern provides flexible anonymization algorithms:

- **AnonymizationStrategy** (interface): Defines anonymization interface
- **AnonymizationContext**: Context class that uses strategies
- **DomainAnonymizationStrategy**: Strategy for anonymizing domains
- **IPAddressAnonymizationStrategy**: Strategy for anonymizing IP addresses
- **EmailAnonymizationStrategy**: Strategy for anonymizing email addresses

This pattern allows for swappable anonymization algorithms depending on the type of data and the required level of privacy.

#### Observer Pattern

The Observer pattern notifies subscribers when threat feeds are updated:

- **Subject** (interface): Defines subject interface
- **ThreatFeed** (concrete subject): Maintains list of observers
- **Observer** (interface): Defines observer interface
- **InstitutionObserver**: Notifies institutions about feed updates
- **AlertSystemObserver**: Triggers alerts based on feed updates

This pattern enables automatic notifications when threat feeds are updated, allowing for real-time dissemination of threat intelligence.

## Data Flow

### Threat Intelligence Consumption

1. The system connects to external TAXII feeds (such as AlienVault OTX)
2. It retrieves STIX-formatted threat intelligence data (indicators and TTPs)
3. The data is processed in batches to manage memory usage
4. Each item is parsed, converted to CRISP entities, and stored in the database
5. The system avoids duplicates by checking STIX IDs
6. Processing statistics are tracked and reported

### STIX/TAXII Conversion and Export

1. The **StixTaxiiService** takes the CRISP entities (Indicators/TTPs)
2. It uses the **Factory Pattern** (StixObjectCreator hierarchy) to convert them to STIX objects
3. These base STIX objects are then enhanced using the **Decorator Pattern**
4. The decorated STIX objects are exported to external TAXII servers

### Anonymization Process

When sharing threat intelligence:

1. The **AnonymizationContext** determines the appropriate level of anonymization based on trust relationships
2. It selects the appropriate **AnonymizationStrategy** for each data type
3. Sensitive data is anonymized while preserving usefulness
4. The anonymized data is then ready for sharing

## Project Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- RabbitMQ (for Celery)

### Environment Setup

1. **Clone the repository**

bash

```bash
git clone <repository-url>
cd CRISP
```

2. **Create and activate a virtual environment**

bash

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

bash

```bash
pip install -r requirements.txt
```

4. **Create a .env file**

Create a `.env` file in the project root with the following variables:

```
# Database settings
DB_NAME=crisp
DB_USER=myuser  # Replace with your PostgreSQL user
DB_PASSWORD=your_password  # Replace with your PostgreSQL password
DB_HOST=localhost
DB_PORT=5432

# Django settings
DJANGO_SECRET_KEY=your_django_secret_key  # Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=True

# OTX API Key (for AlienVault OTX integration)
OTX_API_KEY=your_otx_api_key  # Get from otx.alienvault.com

# Redis settings
REDIS_URL=redis://localhost:6379/0
```

5. **Set up the PostgreSQL database**

Create a PostgreSQL user and database:

bash

```bash
sudo -u postgres psql
CREATE USER myuser WITH PASSWORD 'your_password';
CREATE DATABASE crisp;
GRANT ALL PRIVILEGES ON DATABASE crisp TO myuser;
\q
```

6. **Apply migrations**

bash

```bash
python manage.py makemigrations core
python manage.py migrate
```

7. **Create a superuser**

bash

```bash
python manage.py createsuperuser
```

## Running the Application

### Start the Django Development Server

bash

```bash
python manage.py runserver
```

The server will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Start the Celery Worker (in a separate terminal)

bash

```bash
# Make sure Redis is running
redis-cli ping  # Should return PONG

# Start Celery worker
celery -A crisp worker -l info
```

## Using the Application

### Admin Interface

Access the admin interface at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to manage:

- Institutions
- Threat feeds
- Indicators
- TTP data

### API Endpoints

- List threat feeds: `http://127.0.0.1:8000/api/threat-feeds/`
- List external feeds: `http://127.0.0.1:8000/api/threat-feeds/external/`
- Available collections: `http://127.0.0.1:8000/api/threat-feeds/available_collections/`
- Get threat feed status: `http://127.0.0.1:8000/api/threat-feeds/{id}/status/`
- Consume threat intelligence: `http://127.0.0.1:8000/api/threat-feeds/{id}/consume/`

### Setting Up Threat Intelligence Consumption

1. **Create an Institution**
    - Navigate to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
    - Go to "Institutions" and click "Add Institution"
    - Fill in the details and save
2. **Create a Threat Feed**
    - Go to "Threat feeds" and click "Add Threat feed"
    - Fill in the details:
        - Name: "AlienVault OTX Feed"
        - Description: "External threat feed from AlienVault OTX"
        - Owner: Select your institution
        - Is External: Check this box
        - TAXII Server URL: "[https://otx.alienvault.com/taxii](https://otx.alienvault.com/taxii)"
        - TAXII API Root: "taxii"
        - TAXII Collection ID: "user_AlienVault"
        - TAXII Username: Your OTX API key
        - Is Public: Check if you want to share this feed
    - Save the threat feed
3. **Consume Threat Intelligence**
    - Use the API endpoint:
        
        bash
        
        ```bash
        curl -X POST "http://127.0.0.1:8000/api/threat-feeds/1/consume/?force_days=7&batch_size=100"
        ```
        
    - Or with specific parameters:
        
        bash
        
        ```bash
        # Process in batches of 100 with data from the last 30 days
        curl -X POST "http://127.0.0.1:8000/api/threat-feeds/1/consume/?force_days=30&batch_size=100"
        
        # Process in the background (async mode)
        curl -X POST "http://127.0.0.1:8000/api/threat-feeds/1/consume/?force_days=7&batch_size=100&async=true"
        
        # Limit the number of blocks to process (for testing)
        curl -X POST "http://127.0.0.1:8000/api/threat-feeds/1/consume/?limit=10"
        ```
        
4. **Check Feed Status**
    - Use the status API endpoint:
        
        bash
        
        ```bash
        curl -X GET "http://127.0.0.1:8000/api/threat-feeds/1/status/"
        ```
        
    - This will show the number of indicators and TTPs, along with the last sync time
5. **Verify Imported Data**
    - Check the admin interface for imported indicators and TTPs
    - Or use the Django shell:
        
        bash
        
        ```bash
        python manage.py shell
        ```
        
        python
        
        ```python
        from core.models.indicator import Indicator
        print(f"Total indicators: {Indicator.objects.count()}")
        ```
        

## Testing the TAXII Connection

You can test the TAXII connection directly with the provided test scripts:

bash

```bash
# Test direct API connection to OTX
python test_otx.py

# Test TAXII connection
python test_taxii_connection.py

# Test TAXII polling with a 7-day window
python test_taxii_polling.py
```

## Project Structure

```
crisp/
├── manage.py                         # Django management script
├── requirements.txt                  # Project dependencies
├── .env                              # Environment variables
├── crisp/                           
│   ├── __init__.py                  
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # URL configuration
│   ├── celery.py                     # Celery configuration
│   └── wsgi.py                      
├── core/                            
│   ├── __init__.py                  
│   ├── admin.py                      # Admin panel configuration
│   ├── apps.py                      
│   ├── models/                       # Domain models
│   │   ├── __init__.py              
│   │   ├── indicator.py              # Indicator model
│   │   ├── institution.py            # Institution model
│   │   └── ttp_data.py               # TTP data model
│   ├── patterns/                     # Design pattern implementations
│   │   ├── observer/                 # Observer pattern
│   │   │   ├── __init__.py          
│   │   │   └── threat_feed.py        # ThreatFeed as Subject
│   │   ├── factory/                  # Factory pattern
│   │   │   ├── __init__.py          
│   │   │   ├── stix_object_creator.py
│   │   │   ├── stix_indicator_creator.py
│   │   │   └── stix_ttp_creator.py  
│   │   └── decorator/                # Decorator pattern
│   │       ├── __init__.py          
│   │       ├── stix_object_component.py
│   │       └── stix_decorator.py    
│   ├── repositories/                 # Repositories layer
│   │   ├── __init__.py              
│   │   ├── threat_feed_repository.py
│   │   ├── indicator_repository.py  
│   │   └── ttp_repository.py        
│   ├── services/                     # Services layer
│   │   ├── __init__.py              
│   │   ├── otx_taxii_service.py      # OTX TAXII service
│   │   ├── stix_taxii_service.py     # Generic STIX/TAXII service
│   │   └── threat_feed_service.py   
│   ├── parsers/                      # Data parsers
│   │   ├── __init__.py              
│   │   └── stix1_parser.py           # STIX 1.x parser
│   ├── tasks/                        # Celery tasks
│   │   ├── __init__.py              
│   │   └── taxii_tasks.py            # TAXII-related tasks
│   └── views/                        # Django views
│       ├── __init__.py              
│       ├── home.py                   # Homepage view
│       └── api/                      # API views
│           ├── __init__.py          
│           └── threat_feed_views.py   # ThreatFeed API
```

## Conclusion

CRISP provides a robust platform for sharing threat intelligence using industry-standard protocols (STIX/TAXII). The implementation of design patterns ensures the system is flexible, extensible, and maintainable. The batched processing approach allows for efficient handling of large volumes of threat data, making it suitable for real-world threat intelligence sharing.

By following the instructions in this README, you can set up and use CRISP to consume threat feeds and share threat intelligence securely among trusted partners.