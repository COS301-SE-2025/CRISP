# Software Requirements Specification (SRS)
## CRISP - Cyber Risk Information Sharing Platform

**Version:** 1.1  
**Date:** May 26, 2025  
**Prepared by:** Data Defenders  
**Client:** BlueVision ITM

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [User Stories / User Characteristics](#2-user-stories--user-characteristics)
3. [Domain Model](#3-domain-model)
4. [Use Cases](#4-use-cases)
5. [Functional Requirements](#5-functional-requirements)
6. [Service Contracts](#6-service-contracts)
7. [Architectural Requirements](#7-architectural-requirements)
8. [Technology Requirements](#8-technology-requirements)
9. [Deployment Model](#9-deployment-model)
10. [Architecture Diagram](#10-architecture-model)
11. [Appendices](#11-appendices)

---

## 1. Introduction

### 1.1 Business Need
Educational institutions face increasing cyber threats with limited resources for threat intelligence sharing. Recent months have shown a disturbing trend where once an educational Institution is attacked, similar institutions often become subsequent targets. CRISP addresses the critical need for timely and effective information sharing regarding cyber security incidents among educational institutions, enabling proactive defense against emerging threats.

### 1.2 Project Scope
CRISP will provide a web-based platform for BlueVision ITM to serve their clients with:
- Secure threat intelligence sharing using industry standards (STIX/TAXII)
- Anonymization of sensitive Institutional data while preserving analytical value
- Integration with external threat intelligence sources
- Real-time threat alerting and notification systems
- Trust-based access control and data sharing between Institutions
- Autonomous sharing between distributed CRISP instances

The platform will facilitate both consumption of external threat feeds and publication of anonymized threat data, ensuring confidentiality while maximizing the benefit of shared intelligence.

### 1.3 Definitions and Abbreviations
- **CRISP**: Cyber Risk Information Sharing Platform
- **STIX**: Structured Threat Information eXpression
- **TAXII**: Trusted Automated eXchange of Intelligence Information
- **IoC**: Indicators of Compromise
- **TTP**: Tactics, Techniques, and Procedures
- **CTI**: Cyber Threat Intelligence

### 1.4 Team Members
- **Armand van der Colf** - u22574982 (Full Stack Developer & Security)
- **Jadyn Stoltz** - u22609653 (Team Lead & AI/ML Systems Engineer)
- **Diaan Botes** - u22598538 (Full Stack Developer & Data Scientist)
- **Liam van Kasterop** - u22539761 (Full Stack Developer)
- **Dreas Vermaak** - u22497618 (Backend Developer)

---

## 2. User Stories / User Characteristics

### 2.1 User Hierarchy and Roles

#### BlueVision ITM System Administrator
- **Role**: Platform administrator with full system access
- **Purpose**: Manage the entire CRISP platform, onboard new client Institutions, and maintain system health

#### Institution Publisher (Client Institutions)
- **Role**: BlueVision ITM clients who have publishing rights
- **Purpose**: Represent educational institutions that can both publish and consume threat intelligence

#### Institution Users (Viewers)
- **Role**: Users within client Institutions with viewing rights only
- **Purpose**: Security analysts and IT staff who need access to threat intelligence but cannot publish

### 2.2 User Stories

#### BlueVision ITM System Administrator Stories
- As a System Administrator, I want to register new client Institutions so that they can join the threat sharing community
- As a System Administrator, I want to manage Institution accounts and their settings so that I can control platform access and configurations
- As a System Administrator, I want to monitor system health and usage statistics so that I can ensure platform reliability and optimize performance
- As a System Administrator, I want to configure global anonymization policies so that sensitive data is properly protected across all Institutions
- As a System Administrator, I want to manage trust relationships between Institutions so that I can control data sharing permissions
- As a System Administrator, I want to access comprehensive audit logs so that I can track system usage and investigate security incidents

#### Institution Publisher (Client) Stories
- As an Institution Publisher, I want to publish threat intelligence about attacks on my institution so that I can help protect other educational Institutions
- As an Institution Publisher, I want to add users from my Institution so that my team can access relevant threat intelligence
- As an Institution Publisher, I want to configure what types of threats my Institution shares so that I can control our data sharing policies
- As an Institution Publisher, I want to set anonymization levels for different types of data so that I can protect sensitive institutional information
- As an Institution Publisher, I want to consume threat feeds from other Institutions so that I can stay informed about relevant threats
- As an Institution Publisher, I want to receive alerts about threats targeting educational institutions so that I can proactively defend my Institution
- As an Institution Publisher, I want to manage my Institution's users and their permissions so that I can control who has access to what information
- As an Institution Publisher, I want to upload threat intelligence in bulk via CSV/JSON so that I can efficiently share large datasets

#### Institution User (Viewer) Stories
- As an Institution User, I want to view threat intelligence relevant to my institution so that I can understand current threat landscape
- As an Institution User, I want to receive real-time alerts about high-priority threats so that I can respond quickly to emerging risks
- As an Institution User, I want to search and filter threat intelligence by type, date, and severity so that I can find relevant information quickly
- As an Institution User, I want to export threat data for integration with our security tools so that I can enhance our defensive capabilities
- As an Institution User, I want to view threat trends and analytics so that I can understand attack patterns targeting educational institutions
- As an Institution User, I want to access threat intelligence via API so that I can integrate with existing security systems

#### External API User Stories
- As an External System, I want to consume threat intelligence via TAXII-compliant endpoints so that I can integrate with existing security tools
- As an External System, I want to authenticate securely via JWT tokens so that I can access authorized threat data programmatically
- As an External System, I want to receive standardized STIX-formatted data so that I can easily process threat intelligence

---

## 3. Domain Model

### 3.1 UML Class Diagram
![Domain Model](Domain%20Model%20Diagram/COS%20301%20CRISP%20Domain%20Model_2.png)

### 3.2 Core Domain Entities Description
- **User**: System users with different roles (Admin, Publisher, Viewer) and authentication details
- **Institution**: Client institutions with publishing capabilities and user management
- **ThreatIntelligence**: Core threat data including IoCs, TTPs, with anonymization metadata
- **Feed**: External and internal threat intelligence sources and subscriptions
- **Alert**: Notifications for high-priority threats with customizable criteria
- **TrustRelationship**: Defines sharing permissions and anonymization levels between Institutions
- **AnonymizationPolicy**: Rules for protecting sensitive data while preserving analytical value

---

## 4. Use Cases

### 4.1 Use Case Diagrams
The following five essential use case diagrams illustrate the core functionality and interactions within the CRISP system:

1. **System Overview** - High-level view of all major actors and primary use cases

![System Overview Use Case Diagram](Domain Model Diagram/COS 301 CRISP Domain Model.png)

2. **Threat Intelligence Publication and Sharing** - Core value creation through threat data sharing

![Threat Intelligence Publication and Sharing Use Case Diagram](Use%20Case%20Diagrams/U2%20-%20Threat%20Intelligence%20Publication%20and%20Sharing.png)

3. **Threat Intelligence Consumption and Alerts** - Core value consumption and notification system

![Threat Intelligence Consumption and Alerts Use Case Diagram](Use%20Case%20Diagrams/U3%20-%20Threat%20Intelligence%20Consumption%20and%20Alerts.png)

4. **User and Institution Management** - Foundation user and Institution administration

![User and Institution Management Use Case Diagram](Use%20Case%20Diagrams/U4%20-%20User%20and%20Institution%20Management.png)

5. **Data Validation and Quality Assurance** - Ensuring data integrity and STIX compliance

![Data Validation and Quality Assurance Use Case Diagram](Use%20Case%20Diagrams/U5%20-%20Data%20Validation%20and%20Quality%20Assurance.png)

6. **Anonymization and Trust Management Use Case Diagram** - how CRISP handles sensitive data protection

![Anonymization and Trust Management Use Case Diagram](Use%20Case%20Diagrams/Anon.png)

### 4.2 Use Case Relationships

#### 4.2.1 Actor Relationships
- **System Administrator** has administrative access to all system functions
- **Institution Publisher** inherits Institution User capabilities plus publishing rights
- **Institution User** has read-only access to authorized threat intelligence

### 4.3 Use Case Priorities

#### 4.3.1 Critical Use Cases (Must Have)
1. **User Authentication and Authorization** - Foundation for all system access
2. **Threat Intelligence Publication** - Core value creation functionality
3. **Threat Intelligence Consumption** - Core value consumption functionality
4. **Institution Management** - Essential for multi-tenant architecture
5. **Data Validation and STIX Compliance** - Required for standards compliance

#### 4.3.2 Important Use Cases (Should Have)
1. **Real-time Alert System** - Enhances threat response capabilities
2. **Trust Relationship Management** - Enables controlled data sharing
3. **Bulk Data Upload** - Improves operational efficiency
4. **External Feed Integration** - Enriches threat intelligence sources
5. **Data Anonymization** - Protects sensitive Institutional information

#### 4.3.3 Enhancement Use Cases (Could Have)
1. **Advanced Analytics and Reporting** - Provides deeper threat insights
2. **API Rate Limiting and Throttling** - Protects system resources
3. **Audit Trail Management** - Enhances security and compliance
4. **System Health Monitoring** - Improves operational visibility
5. **Data Export Capabilities** - Supports integration requirements

### 4.4 Cross-Functional Use Cases

#### 4.4.1 Security Use Cases
- **Secure Authentication** - Multi-factor authentication for administrative accounts
- **Data Encryption** - End-to-end encryption for sensitive threat intelligence
- **Access Control** - Role-based permissions with principle of least privilege
- **Audit Logging** - Comprehensive logging for security monitoring

#### 4.4.2 Integration Use Cases
- **STIX/TAXII Compliance** - Standards-based threat intelligence exchange
- **External API Integration** - RESTful API for third-party tool integration
- **Feed Syndication** - Automated consumption of external threat feeds
- **Data Format Conversion** - Support for multiple import/export formats

#### 4.4.3 Operational Use Cases
- **System Monitoring** - Real-time system health and performance monitoring
- **Backup and Recovery** - Automated data protection and disaster recovery
- **Configuration Management** - Centralized system configuration and deployment
- **Performance Optimization** - Query optimization and caching strategies
---

## 5. Functional Requirements

### R1. Authentication and User Management

#### R1.1 User Authentication
- **R1.1.1** CRISP shall provide secure username and password authentication for all user types
- **R1.1.2** CRISP shall enforce password policies (minimum 8 characters, mixed case, numbers, special characters)
- **R1.1.3** CRISP shall provide password reset functionality via email verification
- **R1.1.4** CRISP shall implement account lockout after 5 failed login attempts within 15 minutes
- **R1.1.5** CRISP shall log all authentication activities for audit purposes
- **R1.1.6** CRISP shall implement session timeout after 60 minutes of inactivity
- **R1.1.7** CRISP shall provide automatic token refresh capability and token revocation on logout or security events
- **R1.1.8** CRISP shall protect against username enumeration attacks
- **R1.1.9** CRISP shall create tracked user sessions for every authentication with device information, IP address, and activity timestamps

#### R1.2 User Management
- **R1.2.1** CRISP shall allow System Administrators to create and manage Institution accounts
- **R1.2.2** CRISP shall allow Institution Publishers to invite users via email to their Institution
- **R1.2.3** CRISP shall support three user roles: System Admin, Institution Publisher, Institution Viewer
- **R1.2.4** CRISP shall allow Institution Publishers to manage their Institution's user permissions
- **R1.2.5** CRISP shall allow System Administrators to deactivate user accounts across all Institutions
- **R1.2.6** CRISP shall support bulk operations for user management tasks
- **R1.2.7** CRISP shall allow trusted device management including marking devices as trusted, revoking device trust, and automatic device trust expiration
- **R1.2.8** CRISP shall provide comprehensive audit logging for all authentication events, user management actions, and security events

#### R1.3 Institution Management
- **R1.3.1** CRISP shall allow System Administrators to register new client Institutions
- **R1.3.2** CRISP shall associate each Institution with a primary Institution Publisher account
- **R1.3.3** CRISP shall allow Institutions to manage their profile information and settings
- **R1.3.4** CRISP shall provide organization-specific user management and permissions with hierarchical access control
- **R1.3.5** CRISP shall restrict users to see and interact only with users from their organization (except BlueVisionAdmins)
- **R1.3.6** CRISP shall prevent Viewers from accessing or managing users from any organization
- **R1.3.7** CRISP shall scope data and permissions to organization boundaries

### R2. Threat Intelligence Publication

#### R2.1 Data Publication
- **R2.1.1** CRISP shall support manual entry of threat intelligence through web forms by Institution Publishers
- **R2.1.2** CRISP shall support bulk import via CSV and JSON file uploads for Institution Publishers
- **R2.1.3** CRISP shall validate threat intelligence data for completeness, format, and STIX compliance
- **R2.1.4** CRISP shall automatically tag threat intelligence with metadata (timestamp, source Institution, threat type)
- **R2.1.5** CRISP shall require Institution Publishers to categorize threats by type (Malware, IP, Domain, Hash, Email, etc.)

#### R2.2 Data Anonymization
- **R2.2.1** CRISP shall mask IP addresses (e.g., 192.168.1.x becomes 192.168.1.XXX) in shared data
- **R2.2.2** CRISP shall mask email addresses (e.g., user@domain.com becomes user@XXX.com) in shared data
- **R2.2.3** CRISP shall remove or redact Institution-specific identifiers before sharing
- **R2.2.4** CRISP shall apply configurable anonymization levels based on trust relationships
- **R2.2.5** CRISP shall preserve the analytical value of threat intelligence after anonymization (95% effectiveness target)
- **R2.2.6** CRISP shall allow Institution Publishers to preview anonymized data before publication

#### R2.3 Intelligence Distribution
- **R2.3.1** CRISP shall export threat intelligence in STIX 2.1 format for standards compliance
- **R2.3.2** CRISP shall provide TAXII 2.1 compliant API endpoints for threat sharing
- **R2.3.3** CRISP shall support selective sharing based on trust relationships between Institutions
- **R2.3.4** CRISP shall notify subscribed Institutions when new relevant intelligence is published

### R3. Threat Feed Consumption

#### R3.1 External Feed Integration
- **R3.1.1** CRISP shall consume STIX/TAXII feeds from external threat intelligence sources
- **R3.1.2** CRISP shall validate incoming threat data for format compliance and authenticity
- **R3.1.3** CRISP shall normalize external data to internal schema for consistent processing
- **R3.1.4** CRISP shall support automated polling of external feeds at configurable intervals

#### R3.2 Data Processing
- **R3.2.1** CRISP shall categorize threat data by type (Malware, IP, Domain, Hash, Email, etc.)
- **R3.2.2** CRISP shall tag threat data with education sector relevance indicators
- **R3.2.3** CRISP shall detect and handle duplicate threat intelligence entries across sources
- **R3.2.4** CRISP shall maintain version history of threat intelligence updates

#### R3.3 Alerting System
- **R3.3.1** CRISP shall generate alerts for high-priority threat intelligence based on configurable criteria
- **R3.3.2** CRISP shall support customizable alert thresholds per Institution and threat type
- **R3.3.3** CRISP shall deliver alerts via email and web interface notifications
- **R3.3.4** CRISP shall allow users to subscribe to specific threat categories, sources, or severity levels
- **R3.3.5** CRISP shall generate alerts within 60 seconds of triggering conditions

### R4. Trust Relationship Management

#### R4.1 Trust Configuration
- **R4.1.1** CRISP shall support three trust levels: Public, Trusted, Restricted
- **R4.1.2** CRISP shall allow System Administrators to configure Institution trust relationships
- **R4.1.3** CRISP shall support community groups for multi-Institution trust relationships
- **R4.1.4** CRISP shall enable bilateral trust agreements between Institutions

#### R4.2 Access Control
- **R4.2.1** CRISP shall filter shared intelligence based on established trust relationships
- **R4.2.2** CRISP shall apply appropriate anonymization levels based on trust level
- **R4.2.3** CRISP shall log all access to shared intelligence for audit purposes
- **R4.2.4** CRISP shall support immediate trust relationship revocation with effect on data sharing

### R5. System Administration

#### R5.1 Monitoring and Statistics
- **R5.1.1** CRISP shall provide system health monitoring dashboard for administrators
- **R5.1.2** CRISP shall generate usage reports (users, Institutions, data volume, API calls)
- **R5.1.3** CRISP shall implement API rate limiting (100 requests/minute per user)
- **R5.1.4** CRISP shall maintain comprehensive audit logs for 12 months
- **R5.1.5** CRISP shall provide real-time system performance metrics

#### R5.2 System Management
- **R5.2.1** CRISP shall support Docker containerized deployment for easy installation
- **R5.2.2** CRISP shall provide automated database backup and restore functionality
- **R5.2.3** CRISP shall support configuration via environment variables
- **R5.2.4** CRISP shall include system health check endpoints for monitoring

---


## 6 Service Contracts

The CRISP platform implements REST APIs over HTTPS with JWT authentication, TAXII 2.1 compliance, and trust-based data anonymization. Services enforce loose coupling through standardized contracts with versioned APIs, comprehensive error handling, and retry policies.

## 6.1 Core API Contracts

### 6.1.1 Authentication Service (v1.0)
| Endpoint | Method | Auth | Rate Limit |
|----------|---------|------|-----------|
| `/api/auth/login` | POST | None | 5/min |
| `/api/auth/refresh` | POST | JWT | 20/min |

```bash
POST /api/auth/login
Content-Type: application/json
{
  "username": "user@example.com", 
  "password": "SecurePassword123"
}

Response 200:
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "username": "user@example.com",
    "role": "publisher",
    "institution_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "expires_in": 900
}

Error 401: {"success": false, "error": "INVALID_CREDENTIALS", "message": "Invalid username or password"}
```

### 6.1.2 Institution Management
| Endpoint | Method | Auth | Description |
|----------|---------|------|-------------|
| `/api/institutions/` | POST | None | Create institution |
| `/api/institutions/{id}/users/` | GET | JWT | Get users |


```bash
POST /api/institutions/
{"name": "TechCorp", "contact_email": "admin@techcorp.com", "institution_type": "private_sector", 
 "publisher_user": {"username": "admin", "email": "admin@techcorp.com", "password": "SecurePassword123"}}
Response 201: {"id": "550e8400-e29b-41d4-a716-446655440000", "status": "created"}

GET /api/institutions/{id}/users/
Response: {"users": [{"id": "uuid", "username": "admin", "role": "publisher"}]}
}}
```

### 6.1.3 Threat Intelligence
| Endpoint | Method | Parameters | Description |
|----------|---------|------------|-------------|
| `/api/threats/` | GET | type, severity, date_from, limit, offset | List threats |
| `/api/threats/` | POST | - | Create threat |


```bash
GET /api/threats/?type=malware&severity=high&limit=10
Response: {"threats": [{"id": "threat_123", "indicators": ["hash:md5:d41d8cd98f00b204e9800998ecf8427e"], 
"severity": "high", "ttps": ["T1055", "T1083"], "trust_score": 0.95}], "pagination": {"total": 150}}

POST /api/threats/
{"type": "malware", "indicators": ["hash:md5:d41d8cd98f00b204e9800998ecf8427e"], 
 "severity": "critical", "ttps": ["T1055", "T1083"], "anonymization_level": "medium"}
Response 201: {"id": "threat_789012", "status": "created"}

```

### 6.1.4 TAXII 2.1 Services
| Endpoint | Method | Content-Type | Description |
|----------|---------|--------------|-------------|
| `/taxii2/` | GET | application/taxii+json;version=2.1 | Discovery |
| `/taxii2/collections/` | GET | application/taxii+json;version=2.1 | List collections |
| `/taxii2/collections/{id}/objects/` | GET/POST | application/stix+json;version=2.1 | STIX objects |

```bash
GET /taxii2/
Accept: application/taxii+json;version=2.1
Response: {
  "title": "CRISP TAXII 2.1 Server",
  "description": "Cyber Risk Information Sharing Platform",
  "contact": "admin@crisp.example.com",
  "api_roots": ["/taxii2/"]
}

GET /taxii2/collections/
Authorization: Bearer {access_token}
Response: {
  "collections": [{
    "id": "col_malware_indicators",
    "title": "Malware Indicators",
    "can_read": true,
    "can_write": true,
    "media_types": ["application/stix+json;version=2.1"]
  }]
}

GET /taxii2/collections/col_malware_indicators/objects/?added_after=2025-01-15T00:00:00Z&limit=20
Response: {
  "objects": [{
    "type": "indicator",
    "spec_version": "2.1",
    "id": "indicator--f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "labels": ["malicious-activity"],
    "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
    "valid_from": "2025-01-15T10:00:00.000Z"
  }]
}
```

### 6.1.5 Alert Services
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/alerts/` | GET | Get user alerts |
| `/api/alerts/subscribe/` | POST | Create subscription |
| `/api/alerts/{id}/read/` | PUT | Mark as read |

```bash
POST /api/alerts/subscribe/
{
  "threat_types": ["malware", "phishing"],
  "severity_levels": ["high", "critical"],
  "notification_methods": ["email", "in_app"],
  "frequency": "immediate"
}
Response 201: {"subscription_id": "sub_456789", "status": "created", "active": true}

GET /api/alerts/?unread_only=true&limit=20
Response: {
  "alerts": [{
    "id": "alert_123456",
    "threat_id": "threat_789012",
    "severity": "critical",
    "message": "New high-severity threat detected",
    "read": false
  }],
  "unread_count": 5
}

PUT /api/alerts/alert_123456/read/
Response: {"status": "marked_as_read", "read_at": "2025-01-15T10:35:00Z"}
```

## 6.2 Internal Service Interfaces

```python
interface AlertService {
  generateAlert(threat: ThreatIntelligence, criteria: AlertCriteria): Alert
  notifySubscribers(alert: Alert): void
  manageSubscription(user_id: string, subscription: AlertSubscription): boolean
}
```

## 6.3 Error Handling & Timeouts

**Standard Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable description",
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

**Error Classifications:**
- Client Errors (400-499): No retry - `VALIDATION_ERROR`, `UNAUTHORIZED`


**Timeout Matrix:**
- API requests: 30s
- Database queries: 10s  
- File uploads: 300s
- Bulk operations: 600s

**Circuit Breaker:** 5 failure threshold, 60s recovery timeout

## 6.4 Communication Protocols

**External Communication:**
- HTTPS/TLS 1.3 for all API communication (30s timeout)
- TAXII 2.1 for STIX object exchange (60s timeout)
- WebSockets (WSS) for real-time notifications (300s timeout)

**Internal Communication:**
- Direct function calls (synchronous service-to-service)
- Django signals (asynchronous event notifications)
- Celery tasks (background processing with retry)

**Data Formats:** JSON, STIX 2.1 objects, CSV for bulk uploads, multipart/form-data

## 6.5 Versioning & Security

**API Versioning:**
- URL path versioning (`/api/v1/`, `/api/v2/`)
- 12-month deprecation policy
- Backward compatibility for additive changes
- Content negotiation: `Accept: application/json;version=1.0`

**Authentication & Authorization:**
- JWT Bearer tokens (15-minute lifetime)
- API keys for service-to-service  
- OAuth 2.0 for third-party integration

**Data Protection:**
- AES-256-GCM encryption at rest
- Trust-based data anonymization
- Audit logging with correlation IDs

## 6.6 Testing & Monitoring

**Contract Testing:**
- JSON schema validation for all payloads
- Integration tests with pytest


## 7. Architectural Requirements

### 7.1 Quality Requirements

#### 7.1.1 Performance Requirements
- **P1.1** API endpoints shall respond within 2 seconds for 95% of requests under normal load
- **P1.2** Web pages shall load within 3 seconds for standard broadband connections
- **P1.3** Threat feed processing shall handle up to 1,000 IoCs per minute
- **P1.4** Real-time alerts shall be generated and delivered within 60 seconds of triggering conditions
- **P1.5** System shall support 20 concurrent users without performance degradation
- **P1.6** Bulk threat intelligence uploads shall process 100 records per second
- **P1.7** Data anonymization shall process 100 threat records per second

#### 7.1.2 Reliability Requirements
- **R1.1** System uptime target of 99% (approximately 7 hours downtime per month)
- **R1.2** Planned maintenance windows not to exceed 4 hours per month
- **R1.3** System recovery time objective (RTO) of 30 minutes for critical failures
- **R1.4** Data recovery point objective (RPO) of 4 hours for database recovery
- **R1.5** System shall gracefully handle invalid input data without crashing
- **R1.6** System shall provide meaningful error messages to users for all failure scenarios
- **R1.7** System shall automatically retry failed external API calls (maximum 3 attempts with exponential backoff)

#### 7.1.3 Scalability Requirements
- **S1.1** Architecture shall support scaling from 5 to 50 client Institutions
- **S1.2** Database shall handle growth from 100MB to 10GB of threat intelligence data
- **S1.3** System shall support horizontal scaling with load balancer for increased user load
- **S1.4** API shall support rate limiting and throttling to prevent abuse
- **S1.5** System shall support distributed deployment across multiple CRISP instances

#### 7.1.4 Security Requirements
- **SEC1.1** All user sessions shall timeout after 60 minutes of inactivity
- **SEC1.2** Administrative accounts should implement two-factor authentication capability
- **SEC1.3** API authentication via JWT tokens with 24-hour expiration and refresh capability
- **SEC1.4** Role-based access control with principle of least privilege enforcement
- **SEC1.5** All data in transit encrypted using TLS 1.2 or higher
- **SEC1.6** Sensitive data at rest encrypted using AES-256 encryption
- **SEC1.7** Data anonymization effectiveness target of 95% (analytical value preserved)
- **SEC1.8** Comprehensive audit logs retained for 12 months with tamper-proof storage
- **SEC1.9** Input validation and sanitization for all user inputs to prevent injection attacks
- **SEC1.10** CSRF protection implemented for all state-changing operations

#### 7.1.5 Usability Requirements
- **U1.1** Web interface compatible with Chrome, Firefox, Safari, Edge (latest 2 versions)
- **U1.2** Mobile-responsive design supporting tablets and smartphones (viewport ≥ 768px)
- **U1.3** New Institution Publisher onboarding completable within 2 hours including user setup
- **U1.4** Common threat intelligence tasks achievable within 5 clicks from dashboard
- **U1.5** Context-sensitive help and documentation available throughout interface
- **U1.6** System shall provide clear feedback for all user actions within 1 second

#### 7.1.6 Compliance Requirements
- **C1.1** Full STIX 2.1 specification compliance for threat intelligence format and structure
- **C1.2** Complete TAXII 2.1 specification compliance for threat intelligence sharing protocols
- **C1.3** RESTful API design following OpenAPI 3.0 specification with comprehensive documentation
- **C1.4** Support for data export in JSON, CSV, and STIX formats for interoperability

### 7.2 Architectural Patterns

#### 7.2.1 N-Layered Architecture Pattern

We adopted a 4-layered architecture approach, promoting strict sepration of concerns and undirectional dependencies across the layers
 
- **Presentation Layer**: Responsible for handling HTTP requests/responses, authentication checks, and API endpoint exposure, implemented using Django REST Framework views and serializers. 
- **Service Layer**: Encapsulates domain-specific business logic, workflows, and validations through dedicated service classes (AuthenticationService, ThreatIntelligenceService, InstitutionService, AlertService, STIXTaxiiService, AnonymizationService, TrustService, FeedService) that remain independent of HTTP and database concerns.
- **Data Access Layer**: Manages data persistence operations to abstract database interactions from higher layers (ThreatFeedRepository, IndicatorRepository, InstitutionRepository, TTPRepository).
- **Data Layer**: PostgreSQL database with Django ORM models (Object relational mapping) representing core domain entities (User, Institution, ThreatFeed, Indicator, TTPData, TrustRelationship).
- **Strict Layering and Dependency Flow**: Higher layers depend only on the immediate lower layer, with no reverse or cross-layer coupling, ensuring maintainability and testability.

#### 7.2.2 Service-Oriented Architecture (SOA) Pattern

The service layer implements SOA principles to achieve modularity, reusability, and loose coupling.

- **Service Encapsulation**: Each service encapsulates a specific domain concern with well-defined interfaces and responsibilities.
- **Service Autonomy**: Services operate independently with their own data access and business logic, reducing interdependencies.
- **Service Composability**: Complex operations are achieved by composing multiple services (e.g., threat publication involves ThreatIntelligenceService, AnonymizationService, and STIXTaxiiService).
- **Service Contracts**: Clear interfaces define service capabilities, inputs, and outputs, enabling contract-based development.
- **Service Discovery**: Services are loosely coupled through dependency injection and interface-based communication.

#### 7.2.3 Model-View-Controller (MVC) Pattern

Our frontend implements the MVC pattern using React to separate presentation concerns.

- **Model**: Context API and state management handle application data, API responses, and client-side data models representing threat intelligence, users, and institutions.
- **View**: React components with Material-UI provide the user interface, including dashboards, forms, data visualizations using D3.js.
- **Controller**:  Event handlers, API calls, navigation logic, and user interaction management bridge the Model and View components.
- **Separation of Concerns**: Clear boundaries between data management, presentation, and user interaction logic enable independent development and testing.
- **Component Reusability**: Modular React components can be reused across different views and contexts within the application.

### 7.3 Design Patterns

#### 7.3.1 Factory Method Pattern
- **Implementation**: StixObjectCreator with concrete creators for different STIX object types
- **Purpose**: Encapsulates creation logic for converting CRISP entities to standardized STIX objects
- **Benefits**: Ensures consistency, enables extensibility, maintains standardization

#### 7.3.2 Observer Pattern
- **Implementation**: ThreatFeed as subject with InstitutionObserver and AlertSystemObserver
- **Purpose**: Real-time notifications when threat intelligence is updated
- **Benefits**: Loose coupling, broadcast updates, dynamic subscription management

#### 7.3.3 Strategy Pattern
- **Implementation**: AnonymizationStrategy with concrete strategies for different data types
- **Purpose**: Flexible anonymization approaches based on data type and trust level
- **Benefits**: Runtime algorithm selection, encapsulated algorithms, easy extensibility

#### 7.3.4 Adapter Pattern
- **Implementation**: ThreatIntelligenceSource interface with adapters for external sources
- **Purpose**: Unified interface for various external threat intelligence sources
- **Benefits**: Isolation from external changes, simplified integration, format conversion

#### 7.3.5 Decorator Pattern
- **Implementation**: StixObjectDecorator with validation, export, and enrichment decorators
- **Purpose**: Dynamic enhancement of STIX objects with additional capabilities
- **Benefits**: Composable functionality, single responsibility, open/closed principle

#### 7.3.6 Facade Pattern
- **Implementation**: CRISPFacade providing simplified interface to complex subsystems
- **Purpose**: Hide complexity of interactions between different services
- **Benefits**: Simplified client interface, reduced dependencies, clear system boundaries

### 7.4 Constraints

#### 7.4.1 Technology Constraints
- **TC1.1** Must use open-source technologies to minimize licensing costs
- **TC1.2** Backend must be implemented in Python using Django framework
- **TC1.3** Frontend must use React.js for consistency with team expertise
- **TC1.4** Database must be PostgreSQL for production reliability and security features
- **TC1.5** Containerization must use Docker for consistent deployment environments

#### 7.4.2 Standards Compliance Constraints
- **SC1.1** Must fully comply with STIX 2.1 specification for threat intelligence format
- **SC1.2** Must fully comply with TAXII 2.1 specification for threat sharing protocols
- **SC1.3** API must follow RESTful design principles and OpenAPI 3.0 specification
- **SC1.4** Must support JSON-based data exchange for interoperability

#### 7.4.3 Security Constraints
- **SEC1.1** No storage of unencrypted sensitive data anywhere in the system
- **SEC1.2** All external communications must use HTTPS/TLS encryption
- **SEC1.3** User passwords must be hashed using bcrypt with minimum 12 rounds
- **SEC1.4** API keys and secrets must be stored in secure configuration management
- **SEC1.5** Audit logging must be immutable and tamper-resistant

#### 7.4.4 Business Constraints
- **BC1.1** Development must be completed within academic project timeline (semester duration)
- **BC1.2** Solution must be deployable on standard Linux server infrastructure
- **BC1.3** System must support BlueVision ITM's client base of educational institutions
- **BC1.4** Platform must be cost-effective for small to medium educational institutions

#### 7.4.5 Operational Constraints
- **OC1.1** System must be operable by IT staff with standard cybersecurity knowledge
- **OC1.2** Backup and recovery procedures must be automated and reliable
- **OC1.3** System monitoring and alerting must be built-in for operational visibility
- **OC1.4** Documentation must be comprehensive for both users and administrators

---

## 8. Technology Requirements

### 8.1 Backend Technologies

#### 8.1.1 Core Framework
- **Python 3.9+**: Primary development language with robust cybersecurity libraries
- **Django 4.2+ with Django REST Framework**: Secure web framework with batteries-included approach
- **PostgreSQL 13+**: Primary database with advanced security and querying capabilities
- **Redis 6+**: Caching layer and session storage for improved performance

#### 8.1.2 Message Queue and Processing
- **RabbitMQ**: Message broker for distributed communication between CRISP instances
- **Celery**: Asynchronous task processing for threat feed consumption and alert generation

### 8.2 Threat Intelligence and Security

#### 8.2.1 Standards Implementation
- **python-stix2**: Python library for STIX 2.1 object creation and manipulation
- **taxii2-client**: Client library for TAXII 2.1 protocol implementation
- **OpenCTI Integration**: Integration capabilities with open source threat intelligence platform

#### 8.2.2 Security Libraries
- **PyJWT**: JSON Web Token implementation for API authentication
- **bcrypt**: Secure password hashing
- **cryptography**: Encryption libraries for data protection

### 8.3 Frontend Technologies

#### 8.3.1 Core Framework
- **React.js 18+**: Modern frontend library with component-based architecture
- **Material-UI**: UI component library for consistent design
- **D3.js**: Advanced data visualization for threat intelligence dashboards

#### 8.3.2 State Management and Routing
- **React Router**: Client-side routing for single-page application
- **Context API**: State management for user authentication and global state

### 8.4 DevOps and Infrastructure

#### 8.4.1 Containerization
- **Docker**: Application containerization for consistent environments
- **Docker Compose**: Multi-container orchestration for development and deployment
- **Nginx**: Web server and reverse proxy for production deployment

#### 8.4.2 Development Tools
- **Git**: Version control with GitHub for collaboration
- **GitHub Actions**: Continuous integration and automated testing
- **pytest**: Python testing framework for comprehensive test coverage

### 8.5 Security and Monitoring Tools

#### 8.5.1 Security Testing
- **OWASP ZAP**: Automated security vulnerability scanning
- **Bandit**: Python security linter for identifying common security issues
- **Safety**: Python dependency vulnerability checking

#### 8.5.2 Monitoring and Logging
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Metrics visualization and dashboards
- **Structured Logging**: JSON-based logging for better analysis and monitoring

## 9. Deployment Model

### 9.1 Target Environment Strategy

CRISP deploys primarily **on-premises** to meet educational institutions' stringent security and compliance requirements for sensitive threat intelligence data. The architecture supports **hybrid cloud integration** for non-sensitive operations including backup storage, disaster recovery, and external threat intelligence feed consumption. This approach ensures critical data remains within institutional security perimeters while leveraging cloud capabilities for enhanced resilience and external integrations.

### 9.2 Deployment Topology

The system implements a **containerized microservices architecture** using Docker, organized into two execution environments as illustrated in the deployment diagram:

#### 9.2.1 Frontend Environment
Single Docker container hosting the React client application with five core components:
- **LandingPage**: Platform entry and orientation
- **ThreatDashboard**: Primary threat intelligence interface
- **UserManagement**: User account administration
- **TrustManagement**: Inter-institutional relationship management
- **AlertSystem**: Real-time threat notifications

#### 9.2.2 Backend Environment
Four specialized Docker containers providing distributed services:

**Django Container**: Core application server with REST APIs, business logic, STIX processing, and authentication services.

**PostgreSQL Container**: Persistent data storage for user data, threat intelligence (STIX-formatted), trust relationships, and organizational information with row-level security and audit logging.

**Redis Container**: High-performance caching for frequently accessed data, secure session management, and API rate limiting.

**Celery Container**: Asynchronous background processing including general tasks, TAXII polling for external feeds, and email processing.

### 9.3 Tools and Platforms

**Containerization**: Docker provides consistent packaging and deployment across environments. Docker Compose orchestrates multi-container applications for development and smaller deployments.

**Development Pipeline**: GitHub Actions implements CI/CD with automated testing, security scanning, and deployment procedures. Infrastructure as Code principles ensure reproducible, version-controlled deployments.

### 9.4 Quality Requirements Support

**Scalability**: Horizontal scaling through independent container scaling based on demand patterns. Database read replicas and intelligent caching reduce bottlenecks. Multi-server distribution enables load balancing across dedicated nodes optimized for specific service types.

**Reliability**: Container health checks ensure service availability. Automated failover mechanisms and rolling updates prevent service interruptions. Comprehensive backup procedures with geographic distribution protect against data loss and enable rapid disaster recovery.

**Maintainability**: Automated deployment eliminates manual configuration errors. Version-controlled Infrastructure as Code simplifies environment provisioning and change tracking. Comprehensive monitoring provides proactive issue identification and rapid troubleshooting capabilities.

The architecture scales from single-server proof-of-concept deployments to distributed multi-server production environments serving multiple educational institutions, supporting growth without requiring fundamental architectural changes while maintaining security, performance, and operational requirements throughout the platform lifecycle.

![Deployment Diagram](Deployment%20Diagram/DeploymentDiagram_v1.png)

## 10. Architecture Diagram

### 10. System Architecture Overview

The threat intelligence platform employs a **hybrid architectural approach** combining **N-tier layered architecture** with **Service-Oriented Architecture (SOA)** principles and **Model-View-Controller (MVC)** patterns.

#### 10.1 Architectural Layers

The system is structured across four distinct layers:

**Presentation Layer** implements the MVC pattern with View components for user interface rendering and Controller components handling authentication, authorization, threat detection, and user management. This separation ensures clean presentation logic and robust security controls.

**Business Logic Layer** adopts SOA principles through specialized microservices including STIX/TAXII Service for threat data standardization, Alert Service for real-time notifications, Threat Intelligence Service for data analysis, and supporting services for organization management, anonymization, authentication, and trust relationships.

**Data Access Layer** implements the Repository pattern with dedicated repositories for each domain entity (Indicators, ThreatFeeds, TTPs, Organizations, Users, Audit logs). This abstraction provides consistent data access interfaces and enables easier testing and maintenance.

**Data Layer** centralizes persistent storage using institution, threat feed, indicator, TTP, and trust group models, ensuring data integrity and consistency.

#### 10.2 Architectural Justification

The **N-tier architecture** provides clear separation of concerns, enabling independent scaling and maintenance of each layer. **SOA implementation** allows individual services to be developed, deployed, and scaled independently, crucial for a threat intelligence platform requiring high availability and performance.

**External Systems Integration** through dedicated interfaces (Celery for background processing, Redis for caching, SMTP for notifications, and external threat feeds) ensures loose coupling and system reliability.

This hybrid approach delivers scalability, maintainability, security, and performance required for enterprise threat intelligence operations.

![View Architecture Diagram](Architecture%20Diagram/ArchitectureDiagram_v1.png)

---

## 11. Appendices

### 11.1 Glossary
- **Anonymization**: Process of removing or masking identifying information while preserving analytical value
- **CRISP Instance**: Individual deployment of the CRISP platform serving specific Institutions
- **Educational Institution**: Universities, colleges, schools, and other learning Institutions
- **Institution Publisher**: Primary user account for client Institutions with publishing rights
- **Threat Actor**: Individual or group responsible for cyber attacks and malicious activities
- **Trust Relationship**: Defined level of data sharing permission between Institutions

### 11.2 References
- STIX 2.1 Specification: https://docs.oasis-open.org/cti/stix/v2.1/
- TAXII 2.1 Specification: https://docs.oasis-open.org/cti/taxii/v2.1/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- Django Documentation: https://docs.djangoproject.com/
- React Documentation: https://react.dev/

### 11.3 Revision History
| Version | Date | Changes | Author/s |
|---------|------|---------|--------|
| 1.0 | May 24, 2025 | Initial version | Dreas Vermaak |
| 1.1 | May 26, 2025 | Restructured to match specification requirements | Armand van der Colf|
| 1.2 | August 13, 2025 | Service Contracts Updated | Dreas Vermaak |
| 1.3 | August 18, 2025 | Added Updated diagrams with descriptions | Dreas Vermaak & Liam van Kasterop |
---
