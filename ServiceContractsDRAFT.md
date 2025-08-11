# Service Contracts Documentation

## 3.4.4 Service Contracts

This document describes the service contracts between the major components and services in the CRISP (Collaborative Threat Intelligence Sharing Platform) system. These contracts define API specifications, data formats, communication protocols, and error-handling mechanisms to ensure reliable integration between components.

---

## Core Service Architecture

The CRISP system is built with a layered service architecture consisting of:

1. **Authentication & Authorization Services**
2. **User & Organization Management Services**
3. **Trust Management Services** 
4. **Threat Intelligence Services**
5. **TAXII Integration Services**
6. **Notification & Alert Services**

---

## 1. Authentication & Authorization Services

### 1.1 Authentication Service Contract

**Service**: `AuthenticationViewSet` (`core.views.auth_views`)
**Version**: 1.0

#### API Endpoints

| Endpoint | Method | Description | Authentication | Response Format |
|----------|---------|-------------|----------------|-----------------|
| `/api/auth/login/` | POST | User authentication | None | JSON |
| `/api/auth/logout/` | POST | User logout | JWT Required | JSON |
| `/api/auth/refresh/` | POST | Token refresh | JWT Required | JSON |
| `/api/auth/register/` | POST | User registration | None | JSON |
| `/api/auth/verify/` | GET | Verify token | JWT Required | JSON |
| `/api/auth/sessions/` | GET | Get active sessions | JWT Required | JSON |
| `/api/auth/revoke_session/` | POST | Revoke session | JWT Required | JSON |
| `/api/auth/change_password/` | POST | Change password | JWT Required | JSON |
| `/api/auth/dashboard/` | GET | Get dashboard data | JWT Required | JSON |
| `/api/auth/forgot_password/` | POST | Request password reset | None | JSON |
| `/api/auth/validate_reset_token/` | POST | Validate reset token | None | JSON |
| `/api/auth/reset_password/` | POST | Reset password | None | JSON |

#### Complete API Call Examples

**1. User Login**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe@example.com",
    "password": "SecurePassword123",
    "remember_device": false,
    "totp_code": null
  }'
```

**Response**:
```json
{
  "success": true,
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "username": "john.doe",
    "email": "john.doe@example.com",
    "role": "publisher",
    "first_name": "John",
    "last_name": "Doe",
    "organization": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "TechCorp Industries",
      "domain": "techcorp.com"
    }
  }
}
```

**2. Token Refresh**
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**3. User Registration**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane.smith",
    "password": "SecurePassword456",
    "password_confirm": "SecurePassword456",
    "email": "jane.smith@healthcare.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "organization": "Healthcare Alliance",
    "role": "viewer"
  }'
```

**4. Change Password**
```bash
curl -X POST http://localhost:8000/api/auth/change_password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -d '{
    "current_password": "OldPassword123",
    "new_password": "NewSecurePassword456",
    "new_password_confirm": "NewSecurePassword456"
  }'
```

**5. Password Reset Request**
```bash
curl -X POST http://localhost:8000/api/auth/forgot_password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com"
  }'
```

#### Error Responses

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_CREDENTIALS` | Invalid username or password |
| 401 | `AUTHENTICATION_FAILED` | Authentication failed |
| 403 | `ACCOUNT_DISABLED` | User account is disabled |
| 429 | `RATE_LIMITED` | Too many authentication attempts |

**Error Response Format**:
```json
{
  "success": false,
  "message": "Authentication failed",
  "timestamp": "2025-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

#### Timeout Configuration
- Request timeout: 30 seconds
- Token expiry: 15 minutes (access), 7 days (refresh)

---

## 2. Trust Management Services

### 2.1 Trust Service Contract

**Service**: `TrustService` (`core.services.trust_service`)
**Version**: 1.0

#### API Endpoints

| Endpoint | Method | Description | Request Format | Response Format |
|----------|---------|-------------|----------------|-----------------|
| `/api/trust/relationships/` | GET, POST | Trust relationships | JSON | JSON |
| `/api/trust/groups/` | GET, POST | Trust groups | JSON | JSON |
| `/api/trust/metrics/` | GET | Trust metrics | JSON | JSON |
| `/api/trust/levels/` | GET | Trust levels | JSON | JSON |

#### Data Formats

**Trust Relationship Request**:
```json
{
  "trustor_id": "uuid",
  "trustee_id": "uuid",
  "trust_level": "string",
  "relationship_type": "string",
  "metadata": "object (optional)"
}
```

**Trust Metrics Response**:
```json
{
  "entity_id": "uuid",
  "trust_score": "float",
  "confidence_level": "float",
  "last_updated": "datetime",
  "metrics": {
    "reliability": "float",
    "reputation": "float",
    "historical_performance": "float"
  }
}
```

#### Error Responses

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_TRUST_LEVEL` | Invalid trust level specified |
| 404 | `ENTITY_NOT_FOUND` | Trust entity not found |
| 409 | `RELATIONSHIP_EXISTS` | Trust relationship already exists |

---

## 3. Threat Intelligence Services

### 3.1 Indicator Service Contract

**Service**: `IndicatorService` (`core.services.indicator_service`)
**Version**: 1.0

#### API Endpoints

| Endpoint | Method | Description | Request Format | Response Format |
|----------|---------|-------------|----------------|-----------------|
| `/api/indicators/` | GET, POST | Threat indicators | JSON | JSON |
| `/api/indicators/{id}/` | GET, PUT, DELETE | Specific indicator | JSON | JSON |
| `/api/indicators/search/` | POST | Search indicators | JSON | JSON |

#### Data Formats

**Indicator Request**:
```json
{
  "type": "string",
  "value": "string",
  "confidence": "integer",
  "labels": ["string"],
  "pattern": "string",
  "valid_from": "datetime",
  "valid_until": "datetime (optional)",
  "trust_level": "string"
}
```

**Indicator Response**:
```json
{
  "id": "uuid",
  "type": "string",
  "value": "string",
  "confidence": "integer",
  "labels": ["string"],
  "pattern": "string",
  "valid_from": "datetime",
  "valid_until": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime",
  "trust_metadata": {
    "level": "string",
    "score": "float",
    "source": "string"
  }
}
```

---

## 4. TAXII Integration Services

### 4.1 TAXII Service Contract

**Service**: `StixTaxiiService` (`core.services.stix_taxii_service`)
**Version**: 2.1 (TAXII 2.1 Compliant)

#### API Endpoints

| Endpoint | Method | Description | Request Format | Response Format |
|----------|---------|-------------|----------------|-----------------|
| `/taxii/` | GET | Discovery endpoint | N/A | JSON |
| `/taxii/collections/` | GET | Collections list | N/A | JSON |
| `/taxii/collections/{id}/objects/` | GET, POST | Collection objects | JSON/STIX | JSON/STIX |
| `/taxii/collections/{id}/manifest/` | GET | Object manifest | N/A | JSON |

#### Data Formats

**TAXII Discovery Response**:
```json
{
  "title": "CRISP TAXII Server",
  "description": "Collaborative threat intelligence sharing",
  "contact": "admin@crisp.example.com",
  "default": "/taxii/",
  "api_roots": ["/taxii/"]
}
```

**STIX Object Format**:
```json
{
  "type": "indicator",
  "spec_version": "2.1",
  "id": "indicator--{uuid}",
  "created": "datetime",
  "modified": "datetime",
  "labels": ["malicious-activity"],
  "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
  "valid_from": "datetime"
}
```

#### Communication Protocols
- **Protocol**: HTTPS/TLS 1.2+
- **Content-Type**: `application/taxii+json;version=2.1`
- **Authentication**: Bearer token or Basic Auth
- **Compression**: gzip supported

#### Error Responses

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_STIX_OBJECT` | Malformed STIX object |
| 401 | `UNAUTHORIZED` | Authentication required |
| 404 | `COLLECTION_NOT_FOUND` | Collection does not exist |
| 406 | `UNSUPPORTED_MEDIA_TYPE` | Unsupported content type |

---

## 5. Notification & Alert Services

### 5.1 Alert Service Contract

**Service**: `AlertService` (`core.views.alert_views`)
**Version**: 1.0

#### API Endpoints

| Endpoint | Method | Description | Request Format | Response Format |
|----------|---------|-------------|----------------|-----------------|
| `/alerts/list/` | GET | Get alerts | N/A | JSON |
| `/alerts/threat/` | POST | Send threat alert | JSON | JSON |
| `/alerts/feed/` | POST | Send feed notification | JSON | JSON |
| `/alerts/test-email/` | POST | Test email service | JSON | JSON |

#### Data Formats

**Alert Request**:
```json
{
  "type": "threat|feed|system",
  "priority": "low|medium|high|critical",
  "title": "string",
  "message": "string",
  "recipients": ["string"],
  "metadata": "object (optional)"
}
```

**Alert Response**:
```json
{
  "alert_id": "uuid",
  "status": "sent|queued|failed",
  "timestamp": "datetime",
  "delivery_status": {
    "email": "boolean",
    "sms": "boolean"
  }
}
```

---

## 6. User & Organization Management Services

### 6.1 Organization Service Contract

**Service**: `OrganizationService` (`core.services.organization_service`)
**Version**: 1.0

#### API Endpoints

| Endpoint | Method | Description | Request Format | Response Format |
|----------|---------|-------------|----------------|-----------------|
| `/api/organizations/` | GET, POST | Organizations | JSON | JSON |
| `/api/organizations/{id}/` | GET, PUT, DELETE | Specific organization | JSON | JSON |
| `/api/organizations/{id}/users/` | GET | Organization users | N/A | JSON |

#### Data Formats

**Organization Request**:
```json
{
  "name": "string",
  "description": "string",
  "domain": "string",
  "organization_type": "string",
  "contact_email": "string",
  "website": "string (optional)"
}
```

**Organization Response**:
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "domain": "string",
  "organization_type": "string",
  "is_publisher": "boolean",
  "is_verified": "boolean",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "users": ["object"]
}
```

---

## Cross-Service Communication Protocols

### Internal Service Communication

**Protocol**: Direct Python method calls within Django application
**Error Handling**: Exception propagation with custom exception classes
**Transaction Management**: Django ORM transactions
**Logging**: Centralized logging via Python logging module

### External Service Communication

**Protocol**: HTTPS REST APIs
**Authentication**: JWT tokens or API keys
**Rate Limiting**: Implemented per service
**Circuit Breaker**: Automatic failover on service unavailability

---

## Error Handling Standards

### Common Error Response Format

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)",
    "timestamp": "datetime",
    "request_id": "uuid"
  }
}
```

### Global Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `AUTHENTICATION_REQUIRED` | Authentication required | 401 |
| `PERMISSION_DENIED` | Insufficient permissions | 403 |
| `RESOURCE_NOT_FOUND` | Requested resource not found | 404 |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | 429 |
| `INTERNAL_ERROR` | Internal server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

---

## Timeout & Retry Policies

### Default Timeouts

- **API Requests**: 30 seconds
- **Database Operations**: 10 seconds
- **External Service Calls**: 60 seconds
- **File Operations**: 120 seconds

### Retry Configuration

- **Maximum Retries**: 3
- **Backoff Strategy**: Exponential (2^n seconds)
- **Retry Conditions**: Network errors, timeout errors, 5xx responses
- **Non-Retry Conditions**: 4xx client errors, authentication failures

---

## Versioning Strategy

### API Versioning

- **Scheme**: URL path versioning (`/api/v1/`, `/api/v2/`)
- **Backward Compatibility**: Maintained for 2 major versions
- **Deprecation Notice**: 6 months advance notice
- **Version Header**: `Accept: application/json;version=1.0`

### Service Contract Versioning

- **Schema Evolution**: Additive changes only
- **Breaking Changes**: New version required
- **Version Negotiation**: Content negotiation headers
- **Documentation**: Version-specific documentation

---

## Testing & Validation

### Contract Testing

- **Consumer-Driven Contracts**: Pact testing framework
- **API Schema Validation**: OpenAPI 3.0 specifications  
- **Integration Testing**: Automated test suites
- **Performance Testing**: Load testing for each service

### Monitoring & Observability

- **Health Checks**: `/health` endpoint for each service
- **Metrics Collection**: Prometheus-compatible metrics
- **Distributed Tracing**: Request correlation IDs
- **Log Aggregation**: Structured JSON logging

---

## Security Considerations

### Data Protection

- **Encryption**: TLS 1.2+ for all communications
- **Sensitive Data**: PII encryption at rest
- **API Keys**: Secure generation and rotation
- **Input Validation**: Comprehensive input sanitization

### Access Control

- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control (RBAC)
- **Trust Levels**: Trust-aware access permissions
- **Audit Logging**: Complete audit trail for all operations

---

*Last Updated: August 2025*
*Version: 1.0*
*Document Owner: CRISP Development Team*