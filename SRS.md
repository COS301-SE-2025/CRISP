# Software Requirements Specification (SRS)
## CRISP - Cyber Risk Information Sharing Platform

**Version:** 1.0  
**Date:** May 26, 2025  
**Prepared by:** Data Defenders  
**Client:** BlueVision ITM

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [System Architecture](#5-system-architecture)
6. [User Interface Requirements](#6-user-interface-requirements)
7. [Security Requirements](#7-security-requirements)
8. [Appendices](#8-appendices)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document describes the functional and non-functional requirements for the Cyber Risk Information Sharing Platform (CRISP). CRISP is designed to facilitate secure threat intelligence sharing among organizations, particularly targeting educational institutions vulnerable to cyber attacks.

### 1.2 Scope
CRISP will provide a web-based platform for:
- Secure threat intelligence sharing using industry standards (STIX/TAXII)
- Anonymization of sensitive organizational data
- Integration with external threat intelligence sources
- Real-time threat alerting and notification systems
- Trust-based access control and data sharing

### 1.3 Definitions and Abbreviations
- **CRISP**: Cyber Risk Information Sharing Platform
- **STIX**: Structured Threat Information eXpression
- **TAXII**: Trusted Automated eXchange of Intelligence Information
- **IoC**: Indicators of Compromise
- **TTP**: Tactics, Techniques, and Procedures
- **CTI**: Cyber Threat Intelligence
- **MISP**: Malware Information Sharing Platform

### 1.4 Team Members
- **Armand van der Colf** - u22574982 (Team Lead & Security Specialist)
- **Jadyn Stoltz** - u22609653 (AI/ML Systems Engineer)
- **Diaan Botes** - u22598538 (Full Stack Developer & Data Scientist)
- **Liam van Kasterop** - u22539761 (Backend Developer)
- **Dreas Vermaak** - u22497618 (Backend Developer)

---

## 2. Overall Description

### 2.1 Product Perspective
CRISP is a standalone web application that integrates with external threat intelligence sources and provides standardized threat sharing capabilities. The system will support both manual threat intelligence entry and automated feed consumption.

### 2.2 Product Functions
- User authentication and authorization
- Threat intelligence publication and consumption
- Data anonymization and privacy protection
- Trust relationship management
- Real-time alerting and notifications
- System administration and monitoring

### 2.3 User Classes
- **System Administrators**: Manage users, organizations, and system configuration
- **Security Analysts**: Publish and consume threat intelligence
- **Organization Administrators**: Manage organization-specific settings and users
- **API Users**: External systems consuming threat intelligence via API

---

## 3. Functional Requirements

### R1. Authentication and User Management

#### R1.1 User Authentication
- **R1.1.1** CRISP shall provide secure username and password authentication
- **R1.1.2** CRISP shall enforce password policies (minimum 8 characters, mixed case, numbers)
- **R1.1.3** CRISP shall provide password reset functionality via email
- **R1.1.4** CRISP shall implement account lockout after 5 failed login attempts
- **R1.1.5** CRISP shall log all authentication activities for audit purposes

#### R1.2 User Management
- **R1.2.1** CRISP shall allow administrators to create new user accounts
- **R1.2.2** CRISP shall allow administrators to deactivate user accounts
- **R1.2.3** CRISP shall support role-based access control (Admin, Analyst, Viewer)
- **R1.2.4** CRISP shall verify user credentials and enforce authorization

#### R1.3 Organization Management
- **R1.3.1** CRISP shall allow system administrators to register new organizations
- **R1.3.2** CRISP shall allow administrators to manage organization details
- **R1.3.3** CRISP shall associate users with their respective organizations

### R2. Threat Intelligence Publication

#### R2.1 Data Publication
- **R2.1.1** CRISP shall support manual entry of threat intelligence through web forms
- **R2.1.2** CRISP shall support bulk import via CSV and JSON file uploads
- **R2.1.3** CRISP shall validate threat intelligence data for completeness and format
- **R2.1.4** CRISP shall automatically tag threat intelligence with metadata (timestamp, source, type)

#### R2.2 Data Anonymization
- **R2.2.1** CRISP shall mask IP addresses (e.g., 192.168.1.x becomes 192.168.1.XXX)
- **R2.2.2** CRISP shall mask email addresses (e.g., user@domain.com becomes user@XXX.com)
- **R2.2.3** CRISP shall remove or redact organization-specific identifiers
- **R2.2.4** CRISP shall apply configurable anonymization levels based on sharing policies
- **R2.2.5** CRISP shall preserve the analytical value of threat intelligence after anonymization

#### R2.3 Intelligence Distribution
- **R2.3.1** CRISP shall export threat intelligence in STIX 2.1 format
- **R2.3.2** CRISP shall provide TAXII 2.1 compliant API endpoints
- **R2.3.3** CRISP shall support selective sharing based on trust relationships
- **R2.3.4** CRISP shall send notifications when new intelligence is published

### R3. Threat Feed Consumption

#### R3.1 External Feed Integration
- **R3.1.1** CRISP shall consume STIX/TAXII feeds from external sources
- **R3.1.2** CRISP shall support integration with MISP instances via PyMISP
- **R3.1.3** CRISP shall validate incoming threat data for format compliance
- **R3.1.4** CRISP shall normalize external data to internal schema

#### R3.2 Data Processing
- **R3.2.1** CRISP shall categorize threat data by type (Malware, IP, Domain, Hash, etc.)
- **R3.2.2** CRISP shall tag threat data with industry sectors and attack vectors
- **R3.2.3** CRISP shall detect and handle duplicate threat intelligence entries
- **R3.2.4** CRISP shall maintain version history of threat intelligence updates

#### R3.3 Alerting System
- **R3.3.1** CRISP shall generate alerts for high-priority threat intelligence
- **R3.3.2** CRISP shall support customizable alert thresholds and criteria
- **R3.3.3** CRISP shall deliver alerts via email and web interface notifications
- **R3.3.4** CRISP shall allow users to subscribe to specific threat categories or sources

### R4. Trust Relationship Management

#### R4.1 Trust Configuration
- **R4.1.1** CRISP shall support three trust levels: Public, Trusted, Restricted
- **R4.1.2** CRISP shall allow administrators to configure organization trust relationships
- **R4.1.3** CRISP shall support community groups for multi-organization trust relationships
- **R4.1.4** CRISP shall enable mutual trust agreements between organizations

#### R4.2 Access Control
- **R4.2.1** CRISP shall filter shared intelligence based on trust relationships
- **R4.2.2** CRISP shall apply appropriate anonymization based on trust level
- **R4.2.3** CRISP shall log all access to shared intelligence for audit
- **R4.2.4** CRISP shall support immediate trust relationship revocation

### R5. System Administration

#### R5.1 Monitoring and Statistics
- **R5.1.1** CRISP shall provide system health monitoring dashboard
- **R5.1.2** CRISP shall generate usage reports (users, data volume, API calls)
- **R5.1.3** CRISP shall implement API rate limiting (100 requests/minute per user)
- **R5.1.4** CRISP shall maintain comprehensive audit logs

#### R5.2 System Management
- **R5.2.1** CRISP shall support Docker containerized deployment
- **R5.2.2** CRISP shall provide database backup and restore functionality
- **R5.2.3** CRISP shall support configuration via environment variables
- **R5.2.4** CRISP shall include system health check endpoints

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### 4.1.1 Response Time
- **P1.1** API endpoints shall respond within 2 seconds for 95% of requests
- **P1.2** Web pages shall load within 3 seconds for standard broadband connections
- **P1.3** Threat feed processing shall handle up to 1,000 IoCs per minute
- **P1.4** Real-time alerts shall be generated within 60 seconds of triggering conditions

#### 4.1.2 Throughput
- **P1.5** System shall support 20 concurrent users without performance degradation
- **P1.6** System shall handle 200 API requests per minute during peak usage
- **P1.7** Data processing shall anonymize 100 threat records per second

### 4.2 Reliability Requirements

#### 4.2.1 Availability
- **R1.1** System uptime target of 99% (approximately 7 hours downtime per month)
- **R1.2** Planned maintenance windows not to exceed 4 hours per month
- **R1.3** System recovery time objective (RTO) of 30 minutes
- **R1.4** Data recovery point objective (RPO) of 4 hours

#### 4.2.2 Error Handling
- **R1.5** System shall gracefully handle invalid input data
- **R1.6** System shall provide meaningful error messages to users
- **R1.7** System shall automatically retry failed external API calls (3 attempts)

### 4.3 Scalability Requirements
- **S1.1** Architecture shall support scaling from 5 to 50 organizations
- **S1.2** Database shall handle growth from 100MB to 10GB of threat data
- **S1.3** System shall support horizontal scaling with load balancer

### 4.4 Security Requirements

#### 4.4.1 Authentication & Authorization
- **SEC1.1** All user sessions shall timeout after 60 minutes of inactivity
- **SEC1.2** Administrative accounts should implement two-factor authentication
- **SEC1.3** API authentication via JWT tokens with 24-hour expiration
- **SEC1.4** Role-based access control with principle of least privilege

#### 4.4.2 Data Protection
- **SEC1.5** All data in transit encrypted using TLS 1.2 or higher
- **SEC1.6** Sensitive data at rest encrypted using AES-256
- **SEC1.7** Data anonymization effectiveness target of 95%
- **SEC1.8** Audit logs retained for 12 months

### 4.5 Usability Requirements
- **U1.1** Web interface compatible with Chrome, Firefox, Safari, Edge (latest versions)
- **U1.2** Mobile-responsive design for tablets and smartphones
- **U1.3** New user onboarding completable within 2 hours
- **U1.4** Common tasks achievable within 5 clicks
- **U1.5** Context-sensitive help available throughout interface

### 4.6 Compliance Requirements
- **C1.1** STIX 2.1 specification compliance for threat intelligence format
- **C1.2** TAXII 2.1 specification compliance for threat intelligence sharing
- **C1.3** RESTful API design following OpenAPI 3.0 specification
- **C1.4** Support for data export in JSON and CSV formats

---

## 5. System Architecture

### 5.1 High-Level Architecture
CRISP follows a three-tier architecture:
- **Presentation Layer**: React.js web interface
- **Application Layer**: Django REST API backend
- **Data Layer**: PostgreSQL database with Redis caching

### 5.2 Key Components
- **Authentication Service**: User login, session management
- **Threat Intelligence Engine**: Data processing, anonymization
- **STIX/TAXII Service**: Standards-compliant threat sharing
- **Alert Manager**: Notification and alerting system
- **Trust Manager**: Access control and sharing policies
- **External Integrations**: MISP, OpenCTI, and other CTI sources

### 5.3 Deployment Architecture
- **Containerization**: Docker containers for all services
- **Orchestration**: Docker Compose for local development
- **Web Server**: Nginx reverse proxy
- **Database**: PostgreSQL with automated backups

---

## 6. User Interface Requirements

### 6.1 Web Interface
- **Dashboard**: Overview of system status, recent threats, and alerts
- **Threat Intelligence Management**: Create, edit, view threat data
- **Feed Management**: Configure and monitor external threat feeds
- **User Management**: Administrative interface for user and organization management
- **Reports**: Generate usage and threat intelligence reports

### 6.2 API Interface
- **RESTful API**: JSON-based API for programmatic access
- **TAXII Endpoints**: Standards-compliant threat intelligence sharing
- **Authentication**: JWT-based API authentication
- **Documentation**: OpenAPI/Swagger documentation

---

## 7. Security Requirements

### 7.1 Authentication Security
- Secure password storage using bcrypt hashing
- Protection against brute force attacks
- Session management with secure cookies
- CSRF protection for all forms

### 7.2 Data Security
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Secure configuration management

### 7.3 Infrastructure Security
- HTTPS enforcement for all connections
- Security headers implementation
- Regular security updates and patches
- Vulnerability scanning integration

---

## 8. Appendices

### 8.1 Glossary
Detailed definitions of technical terms and acronyms used throughout the document.

### 8.2 References
- STIX 2.1 Specification: https://docs.oasis-open.org/cti/stix/v2.1/
- TAXII 2.1 Specification: https://docs.oasis-open.org/cti/taxii/v2.1/
- NIST Cybersecurity Framework
- MISP Documentation

### 8.3 Revision History
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | May 26, 2025 | Initial version | Armand van der Colf |

---