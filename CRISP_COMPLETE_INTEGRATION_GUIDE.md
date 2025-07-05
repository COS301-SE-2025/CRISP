# CRISP Integration System - Complete Documentation

## Overview

**CRISP (Cyber Risk Information Sharing Platform)** is a comprehensive, integrated system that combines UserManagement and TrustManagement capabilities to provide secure, role-based access control for threat intelligence sharing between organizations.

## System Architecture

### Core Components

1. **UserManagement System** (`apps/user_management/`)
   - User authentication and authorization
   - Organization management
   - Role-based access control
   - User invitation and onboarding
   - Security audit logging

2. **TrustManagement System** (`apps/trust_management/`)
   - Trust level definitions and management
   - Trust relationship establishment
   - Trust group management
   - Comprehensive audit logging
   - Access control based on trust levels

3. **Core Integration Services** (`apps/core/`)
   - Unified business logic
   - Cross-system workflows
   - Integration APIs
   - Dashboard and reporting services

## How the Systems Work Together

### 1. Organization Registration and Setup

When a new organization joins CRISP:

```python
# Complete organization setup with trust integration
organization = CRISPIntegrationService.create_organization_with_trust_setup(
    name="State University",
    domain="state-univ.edu",
    contact_email="admin@state-univ.edu",
    admin_user_data={
        'username': 'admin',
        'email': 'admin@state-univ.edu',
        'password': 'SecurePass123!',
        'first_name': 'Admin',
        'last_name': 'User'
    },
    institution_type='university',
    default_trust_level='public'
)
```

**What happens:**
- Organization record is created in the database
- Administrative user is created with publisher role
- Default trust level is assigned to the organization
- Organization becomes available for trust relationships
- Audit logs are created for the registration

### 2. User Management and Roles

Users are managed within their organizations with specific roles:

- **Viewer**: Can view shared intelligence based on trust relationships
- **Publisher**: Can publish intelligence and view shared content
- **Admin**: Can manage users within their organization and approve trust relationships
- **System Admin**: Can manage the entire system (BlueVision staff)

```python
# User invitation workflow
invitation = CRISPIntegrationService.invite_user_to_organization(
    organization=organization,
    inviting_user=admin_user,
    email='newuser@state-univ.edu',
    role='publisher'
)
```

### 3. Trust Relationship Management

Organizations establish trust relationships to share intelligence:

```python
# Create bilateral trust relationship
relationship = CRISPIntegrationService.create_trust_relationship(
    source_org=university_org,
    target_org=government_org,
    trust_level_name='Trusted Partners',
    relationship_type='bilateral'
)
```

**Trust Levels:**
- **Public Access** (25): General threat intelligence, fully anonymized
- **Trusted Partners** (50): Detailed intelligence, partially anonymized
- **Restricted Access** (75): Sensitive intelligence, minimal anonymization

### 4. Intelligence Access Control

Access to shared intelligence is controlled based on:
- User's role within their organization
- Trust relationships between organizations
- Trust levels assigned to intelligence
- Anonymization requirements

```python
# Check what intelligence sources a user can access
accessible_sources = CRISPIntegrationService.get_user_accessible_intelligence_sources(
    user=user,
    intelligence_type='threat_indicator'
)
```

### 5. Trust Dashboard and Monitoring

Organizations can monitor their trust relationships:

```python
# Get dashboard data
dashboard_data = CRISPIntegrationService.get_organization_trust_dashboard_data(organization)
```

**Dashboard includes:**
- Active trust relationships
- Pending approval requests
- Active users in organization
- Available intelligence sources
- Recent audit activities

## Integration Features

### Unified Authentication
- Single sign-on across all system components
- JWT-based authentication with refresh tokens
- Session management with device tracking
- Progressive account lockout for security

### Role-Based Access Control
- Organization-based user isolation
- Role inheritance and permissions
- Dynamic permission evaluation
- API endpoint protection

### Trust-Based Intelligence Filtering
- Automatic filtering based on trust relationships
- Anonymization level enforcement
- Access logging and audit trails
- Real-time permission evaluation

### Comprehensive Audit Logging
- All user authentication events
- Trust relationship changes
- Intelligence access events
- Administrative actions
- Security incidents

## Database Schema

### User Management Tables
- `user_management_organization` - Organization information
- `user_management_customuser` - Extended user model
- `user_management_invitationtoken` - User invitation tokens
- `user_management_authenticationslog` - Authentication audit logs

### Trust Management Tables
- `trust_management_trustlevel` - Trust level definitions
- `trust_management_trustrelationship` - Trust relationships between organizations
- `trust_management_trustgroup` - Trust groups for community relationships
- `trust_management_trustlog` - Trust operation audit logs

## API Integration

### Authentication Endpoints
- `POST /api/auth/login/` - User authentication
- `POST /api/auth/refresh/` - Token refresh
- `GET /api/auth/profile/` - User profile information
- `POST /api/auth/logout/` - User logout

### Organization Management
- `GET /api/organizations/` - List organizations
- `POST /api/organizations/` - Create organization
- `GET /api/organizations/{id}/dashboard/` - Organization dashboard

### Trust Management
- `GET /api/trust/relationships/` - List trust relationships
- `POST /api/trust/relationships/` - Create trust relationship
- `PUT /api/trust/relationships/{id}/approve/` - Approve relationship
- `GET /api/trust/levels/` - List trust levels

## Security Features

### Multi-Layer Security
1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based permissions
3. **Trust Evaluation**: Dynamic trust-based access control
4. **Audit Logging**: Comprehensive activity tracking
5. **Data Protection**: Anonymization based on trust levels

### Threat Protection
- Rate limiting on authentication endpoints
- Account lockout after failed attempts
- IP-based access controls
- Device fingerprinting for trusted devices
- Suspicious activity detection

## Testing and Coverage

### Test Suite Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-system workflow testing
- **End-to-End Tests**: Complete user workflow testing
- **Security Tests**: Authentication and authorization testing

### Coverage Metrics
- **Overall Coverage**: Targeting 80%+ code coverage
- **Critical Path Coverage**: 100% for security components
- **Integration Coverage**: Complete workflow testing
- **Performance Testing**: Load and stress testing

## Deployment and Operations

### Environment Requirements
- Python 3.8+
- Django 4.2+
- SQLite (development) / PostgreSQL (production)
- Redis (for caching and sessions)
- NGINX (for production deployment)

### Configuration Management
- Environment-specific settings
- Secret key management
- Database connection pooling
- Caching configuration
- Logging configuration

### Monitoring and Alerting
- Application performance monitoring
- Security event alerting
- Database performance monitoring
- User activity analytics
- System health checks

## How to Run the System

### Development Environment

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd CRISP
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage_unified.py migrate
   python manage_unified.py createsuperuser
   ```

3. **Run Development Server**
   ```bash
   python manage_unified.py runserver
   ```

### Testing

1. **Run Integration Tests**
   ```bash
   python comprehensive_test_suite.py
   ```

2. **Run Main Integration Demo**
   ```bash
   python main_integration_runner.py
   ```

3. **Generate Coverage Report**
   ```bash
   python -m coverage run --source=apps manage_unified.py test apps
   python -m coverage report
   python -m coverage html
   ```

## System Benefits

### For Organizations
- **Secure Intelligence Sharing**: Trust-based access control
- **Role-Based Management**: Proper user access control
- **Audit Compliance**: Comprehensive logging and reporting
- **Flexible Trust Levels**: Configurable sharing permissions

### For Users
- **Single Sign-On**: Unified authentication across services
- **Role-Based Access**: Appropriate permissions for user roles
- **Self-Service**: User invitation and profile management
- **Transparency**: Clear audit trail of all activities

### For Administrators
- **Centralized Management**: Single system for user and trust management
- **Real-Time Monitoring**: Live dashboards and reporting
- **Security Controls**: Comprehensive security features
- **Scalability**: Designed for multi-organization deployment

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic user management
- ✅ Trust relationship management
- ✅ Integration services
- ✅ Basic API endpoints

### Phase 2 (Planned)
- Advanced intelligence filtering
- Real-time threat intelligence feeds
- Machine learning for threat analysis
- Advanced analytics and reporting

### Phase 3 (Future)
- Mobile applications
- API ecosystem for third-party integrations
- Advanced AI/ML features
- Global threat intelligence network

## Conclusion

CRISP represents a complete, integrated solution for secure threat intelligence sharing between organizations. By combining robust user management with sophisticated trust management, the system provides the foundation for secure, scalable, and compliant information sharing in the cybersecurity domain.

The system is designed with security, scalability, and usability in mind, providing organizations with the tools they need to collaborate effectively while maintaining appropriate security controls and audit requirements.

## Support and Contact

For technical support, feature requests, or questions about the CRISP system, please contact:

- **Development Team**: [development@crisp.platform]
- **Security Team**: [security@crisp.platform]
- **Support**: [support@crisp.platform]

---

*This documentation reflects the current state of the CRISP integration system as of July 2025. For the most up-to-date information, please refer to the project repository and release notes.*
