
---

## Target Environment Strategy

CRISP deploys primarily **on-premises** to meet educational institutions' stringent security and compliance requirements for sensitive threat intelligence data. The architecture supports **hybrid cloud integration** for non-sensitive operations including backup storage, disaster recovery, and external threat intelligence feed consumption. This approach ensures critical data remains within institutional security perimeters while leveraging cloud capabilities for enhanced resilience and external integrations.

## Deployment Topology

The system implements a **containerized microservices architecture** using Docker, organized into two execution environments as illustrated in the deployment diagram:

### Frontend Environment
Single Docker container hosting the React client application with five core components:
- **LandingPage**: Platform entry and orientation
- **ThreatDashboard**: Primary threat intelligence interface
- **UserManagement**: User account administration
- **TrustManagement**: Inter-institutional relationship management
- **AlertSystem**: Real-time threat notifications

### Backend Environment
Four specialized Docker containers providing distributed services:

**Django Container**: Core application server with REST APIs, business logic, STIX processing, and authentication services.

**PostgreSQL Container**: Persistent data storage for user data, threat intelligence (STIX-formatted), trust relationships, and organizational information with row-level security and audit logging.

**Redis Container**: High-performance caching for frequently accessed data, secure session management, and API rate limiting.

**Celery Container**: Asynchronous background processing including general tasks, TAXII polling for external feeds, and email processing.

## Tools and Platforms

**Containerization**: Docker provides consistent packaging and deployment across environments. Docker Compose orchestrates multi-container applications for development and smaller deployments.

**Development Pipeline**: GitHub Actions implements CI/CD with automated testing, security scanning, and deployment procedures. Infrastructure as Code principles ensure reproducible, version-controlled deployments.

## Quality Requirements Support

**Scalability**: Horizontal scaling through independent container scaling based on demand patterns. Database read replicas and intelligent caching reduce bottlenecks. Multi-server distribution enables load balancing across dedicated nodes optimized for specific service types.

**Reliability**: Container health checks ensure service availability. Automated failover mechanisms and rolling updates prevent service interruptions. Comprehensive backup procedures with geographic distribution protect against data loss and enable rapid disaster recovery.

**Maintainability**: Automated deployment eliminates manual configuration errors. Version-controlled Infrastructure as Code simplifies environment provisioning and change tracking. Comprehensive monitoring provides proactive issue identification and rapid troubleshooting capabilities.

The architecture scales from single-server proof-of-concept deployments to distributed multi-server production environments serving multiple educational institutions, supporting growth without requiring fundamental architectural changes while maintaining security, performance, and operational requirements throughout the platform lifecycle.

---
