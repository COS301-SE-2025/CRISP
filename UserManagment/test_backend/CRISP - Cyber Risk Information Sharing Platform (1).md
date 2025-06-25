
## Overview

CRISP (Cyber Risk Information Sharing Platform) is a system designed to streamline and enhance threat intelligence sharing among organizations, particularly those in the educational sector facing increasing ransomware threats. The platform enables institutions to share Indicators of Compromise (IoCs), Tactics, Techniques, and Procedures (TTPs) in a secure, standardized way while maintaining appropriate levels of confidentiality through anonymization.

## System Architecture

The CRISP system follows a modular, service-oriented architecture implementing several design patterns to ensure flexibility, extensibility, and maintainability.

### Core Components

#### 1. Domain Model

The domain model consists of the following key entities:

- **Institution**: Organizations that share/consume threat intelligence
- **User**: Employees of institutions who interact with the system
- **ThreatFeed**: Collections of threat data owned by institutions
- **Indicator/IoC**: Indicators of compromise that might signal a threat
- **TTPData**: Tactics, Techniques, and Procedures used by threat actors

#### 2. Service Layer

The service layer manages business logic and operations:

- **ThreatFeedService**: Manages threat feeds
- **IndicatorService**: Handles IoC operations
- **TTPService**: Manages TTP data
- **StixTaxiiService**: Handles STIX/TAXII operations for standardized sharing

#### 3. Repository Layer

Repositories handle data persistence:

- **ThreatFeedRepository**: Manages storage and retrieval of threat feeds
- **IndicatorRepository**: Manages storage and retrieval of indicators
- **TTPRepository**: Manages storage and retrieval of TTP data

### Design Patterns Implementation

#### Factory Pattern

The Factory Method pattern standardizes the creation of STIX objects from CRISP entities:

- **StixObjectCreator** (abstract): Defines interface for creating STIX objects
- **StixIndicatorCreator**: Creates STIX indicators from CRISP Indicators
- **StixTTPCreator**: Creates STIX attack patterns from CRISP TTPs
- **StixObject** (product): The STIX objects created by the factories

#### Decorator Pattern

The Decorator pattern dynamically adds capabilities to STIX objects:

- **StixObjectComponent** (interface): Defines the component interface
- **StixDecorator** (abstract): Base decorator class
- **StixValidationDecorator**: Adds validation capabilities
- **StixTaxiiExportDecorator**: Adds TAXII export functionality
- **StixEnrichmentDecorator**: Adds data enrichment capabilities

#### Strategy Pattern

The Strategy pattern provides flexible anonymization algorithms:

- **AnonymizationStrategy** (interface): Defines anonymization interface
- **AnonymizationContext**: Context class that uses strategies
- **DomainAnonymizationStrategy**: Strategy for anonymizing domains
- **IPAddressAnonymizationStrategy**: Strategy for anonymizing IP addresses
- **EmailAnonymizationStrategy**: Strategy for anonymizing email addresses

#### Observer Pattern

The Observer pattern notifies subscribers when threat feeds are updated:

- **Subject** (interface): Defines subject interface
- **ThreatFeed** (concrete subject): Maintains list of observers
- **Observer** (interface): Defines observer interface
- **InstitutionObserver**: Notifies institutions about feed updates
- **AlertSystemObserver**: Triggers alerts based on feed updates

## Data Flow

### Threat Feed Creation and Sharing

1. A **User** (part of an **Institution**) creates a threat feed through the **ThreatFeedService**
2. The **ThreatFeedService** creates a new **ThreatFeed** and saves it to the **ThreatFeedRepository**
3. The User adds Indicators or TTPs to the feed through the **IndicatorService** or **TTPService**
4. These are saved to the repository and associated with the ThreatFeed
5. When ready to publish, the **ThreatFeedService** calls the **StixTaxiiService**

### STIX/TAXII Conversion and Export

1. The **StixTaxiiService** takes the CRISP entities (Indicators/TTPs)
2. It uses the **Factory Pattern** (StixObjectCreator hierarchy) to convert them to STIX objects
3. These base STIX objects are then enhanced using the **Decorator Pattern**:
    - **StixValidationDecorator** ensures objects conform to STIX specifications
    - **StixTaxiiExportDecorator** adds export capabilities
    - **StixEnrichmentDecorator** adds additional context if needed
4. The decorated STIX objects are exported to external TAXII servers

### Consuming External Threat Intelligence

1. The **StixTaxiiService** imports STIX objects from external TAXII servers
2. These are converted to CRISP entities (Indicators, TTPs)
3. Imported entities are stored in the repositories
4. They can be added to existing feeds or create new feeds

### Anonymization Process

When sharing threat intelligence:

1. The **AnonymizationContext** determines the appropriate level of anonymization based on trust relationships
2. It selects the appropriate **AnonymizationStrategy** for each data type
3. Sensitive data is anonymized while preserving usefulness
4. The anonymized data is then ready for sharing

## Class Relationships

### ThreatFeedService Relationships

- **ThreatFeedService** → **ThreatFeed**: Service creates and manages Feed objects
- **ThreatFeedService** → **ThreatFeedRepository**: Service uses Repository for persistence
- **ThreatFeedService** → **StixTaxiiService**: Service uses StixTaxiiService for STIX/TAXII operations

### StixTaxiiService Relationships

- **StixTaxiiService** → **StixObjectCreator**: Service uses Factory to create STIX objects
- **StixTaxiiService** → **Decorators**: Service applies decorators to enhance STIX objects

### Factory Pattern Relationships

- **StixObjectCreator** ← **StixIndicatorCreator**: Inheritance relationship
- **StixObjectCreator** ← **StixTTPCreator**: Inheritance relationship
- **StixObject** ← created by **StixObjectCreator** hierarchy

### Decorator Pattern Relationships

- **StixObject** → implements **StixObjectComponent**: Implementation relationship
- **StixDecorator** → implements **StixObjectComponent**: Implementation relationship
- **StixDecorator** → has-a **StixObjectComponent**: Composition relationship
- **StixValidationDecorator** → extends **StixDecorator**: Inheritance relationship
- **StixTaxiiExportDecorator** → extends **StixDecorator**: Inheritance relationship
- **StixEnrichmentDecorator** → extends **StixDecorator**: Inheritance relationship

### Observer Pattern Relationships

- **ThreatFeed** → implements **Subject**: Implementation relationship
- **InstitutionObserver** → implements **Observer**: Implementation relationship
- **AlertSystemObserver** → implements **Observer**: Implementation relationship
- **Subject** → observers **Observer**: Association relationship

### FeedSubscription Relationships

- **Institution** → has-many **FeedSubscription**: Composition relationship
- **ThreatFeed** → has-many **FeedSubscription**: Association relationship
- **FeedSubscription** → has-a **FeedFilter**: Composition relationship

### Strategy Pattern Relationships

- **AnonymizationContext** → uses **AnonymizationStrategy**: Association relationship
- **AnonymizationStrategy** ← implemented by concrete strategies: Implementation relationship

## Current Implementation Status

The current implementation includes:

1. **Domain Model Classes**:
    - Institution
    - User
    - ThreatFeed
    - Indicator
    - TTPData
    - TrustRelationship
2. **Factory Pattern**:
    - StixObjectCreator (abstract)
    - StixIndicatorCreator
    - StixTTPCreator
    - StixObject hierarchy
3. **Decorator Pattern**:
    - StixObjectComponent (interface)
    - StixDecorator (abstract)
    - StixValidationDecorator
    - StixTaxiiExportDecorator
    - StixEnrichmentDecorator
4. **Strategy Pattern**:
    - AnonymizationStrategy (interface)
    - AnonymizationContext
    - Concrete strategies (Domain, IP, Email)
5. **Service Classes**:
    - ThreatFeedService
    - IndicatorService
    - TTPService
    - StixTaxiiService
6. **Observer Pattern**:
    - Subject interface
    - Observer interface
    - ThreatFeed (as Subject)
    - Institution/Alert observers

## Next Steps for Implementation

The following components should be implemented next:

1. **Repository Layer**:
    - Complete the ThreatFeedRepository with all CRUD operations
    - Implement IndicatorRepository and TTPRepository
    - Add transaction management and error handling
2. **Authentication & Authorization**:
    - Implement user authentication system
    - Add role-based access control
    - Integrate with institution trust relationships
3. **TAXII Server Integration**:
    - Complete the TAXII server/client implementation
    - Implement collection management
    - Add subscription handling
    - Configure authentication for TAXII communications
4. **Alert System**:
    - Implement the Smart Alerting System (wow factor)
    - Create AlertRule class and related components
    - Develop infrastructure asset matching algorithms
5. **User Interface**:
    - Develop web interface for threat feed management
    - Create dashboards for threat intelligence visualization
    - Implement user and institution management screens
6. **Testing Framework**:
    - Unit tests for all components
    - Integration tests for service interactions
    - System tests for end-to-end flows
7. **Deployment Configuration**:
    - Dockerize the application
    - Create deployment scripts
    - Configure monitoring and logging
8. **Documentation**:
    - API documentation
    - User manual
    - Administrator guide

## Conclusion

The CRISP system architecture provides a robust foundation for threat intelligence sharing while maintaining appropriate confidentiality through anonymization. The implementation of various design patterns ensures the system is flexible, extensible, and maintainable.

By completing the next implementation steps, the system will fulfill all the requirements specified in the project proposal, including core requirements, optional features, and wow factors.