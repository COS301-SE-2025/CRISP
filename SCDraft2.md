# Service Contracts Documentation

## 3.4.4 Service Contracts

The CRISP platform implements REST APIs over HTTPS with JWT authentication, TAXII 2.1 compliance, and trust-based data anonymization. Services enforce loose coupling through standardized contracts with versioned APIs, comprehensive error handling, and retry policies.

## Core API Contracts

### Authentication Service (v1.0)
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

### Institution Management
| Endpoint | Method | Auth | Description |
|----------|---------|------|-------------|
| `/api/institutions/` | POST | None | Create institution |
| `/api/institutions/{id}/users/` | GET | JWT | Get users |
| `/api/institutions/{id}/users/invite/` | POST | JWT | Invite user |

```bash
POST /api/institutions/
{"name": "TechCorp", "contact_email": "admin@techcorp.com", "institution_type": "private_sector", 
 "publisher_user": {"username": "admin", "email": "admin@techcorp.com", "password": "SecurePassword123"}}
Response 201: {"id": "550e8400-e29b-41d4-a716-446655440000", "status": "created"}

GET /api/institutions/{id}/users/
Response: {"users": [{"id": "uuid", "username": "admin", "role": "publisher"}]}

POST /api/institutions/{id}/users/invite/
{"email": "user@techcorp.com", "role": "viewer"}
Response: {"status": "invitation_sent", "invitation_id": "inv_123456789"}
```

### Threat Intelligence
| Endpoint | Method | Parameters | Description |
|----------|---------|------------|-------------|
| `/api/threats/` | GET | type, severity, date_from, limit, offset | List threats |
| `/api/threats/` | POST | - | Create threat |
| `/api/threats/bulk-upload/` | POST | - | Bulk upload |

```bash
GET /api/threats/?type=malware&severity=high&limit=10
Response: {"threats": [{"id": "threat_123", "indicators": ["hash:md5:d41d8cd98f00b204e9800998ecf8427e"], 
"severity": "high", "ttps": ["T1055", "T1083"], "trust_score": 0.95}], "pagination": {"total": 150}}

POST /api/threats/
{"type": "malware", "indicators": ["hash:md5:d41d8cd98f00b204e9800998ecf8427e"], 
 "severity": "critical", "ttps": ["T1055", "T1083"], "anonymization_level": "medium"}
Response 201: {"id": "threat_789012", "status": "created"}

POST /api/threats/bulk-upload/
Content-Type: multipart/form-data, file: threats.csv
Response: {"processed": 100, "created": 95, "errors": ["Row 5: Invalid format"]}
```

### TAXII 2.1 Services
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

### Alert Services
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

## Internal Service Interfaces

```python
class AnonymizationService:
    def anonymize(data: ThreatData, level: AnonymizationLevel) -> AnonymizedThreatData
    def preview(data: ThreatData, level: AnonymizationLevel) -> AnonymizedThreatData
    def validate_effectiveness(original: ThreatData, anonymized: AnonymizedThreatData) -> float
    
class TrustService:
    def evaluate_access(requesting_org: str, target_org: str, data_type: str) -> AccessLevel
    def get_anonymization_level(trust_relationship: TrustLevel) -> AnonymizationLevel
    def update_trust_relationship(org1: str, org2: str, level: TrustLevel) -> bool
    
class FeedService:
    def consume_feed(feed_url: str, format: str) -> List[ThreatIntelligence]
    def normalize_feed_data(external_data: Any, source_format: str) -> ThreatIntelligence
    def validate_feed_data(data: ThreatIntelligence) -> ValidationResult
```

## Error Handling & Timeouts

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
- Server Errors (500-599): Exponential backoff - `INTERNAL_ERROR`, `SERVICE_UNAVAILABLE`  
- Rate Limits (429): Linear backoff - `RATE_LIMITED`

**Timeout Matrix:**
- API requests: 30s
- Database queries: 10s  
- File uploads: 300s
- Bulk operations: 600s

**Circuit Breaker:** 5 failure threshold, 60s recovery timeout

## Communication Protocols

**External Communication:**
- HTTPS/TLS 1.3 for all API communication (30s timeout)
- TAXII 2.1 for STIX object exchange (60s timeout)
- WebSockets (WSS) for real-time notifications (300s timeout)

**Internal Communication:**
- Direct function calls (synchronous service-to-service)
- Django signals (asynchronous event notifications)
- Celery tasks (background processing with retry)

**Data Formats:** JSON, STIX 2.1 objects, CSV for bulk uploads, multipart/form-data

## Versioning & Security

**API Versioning:**
- URL path versioning (`/api/v1/`, `/api/v2/`)
- 12-month deprecation policy
- Backward compatibility for additive changes
- Content negotiation: `Accept: application/json;version=1.0`

**Authentication & Authorization:**
- JWT Bearer tokens (15-minute lifetime)
- API keys for service-to-service (1-year lifetime)  
- OAuth 2.0 for third-party integration

**Data Protection:**
- TLS 1.3 encryption in transit
- AES-256-GCM encryption at rest
- Trust-based data anonymization
- Audit logging with correlation IDs

## Testing & Monitoring

**Contract Testing:**
- Pact framework for consumer-driven contracts
- JSON schema validation for all payloads
- Integration tests with pytest
- Load testing with Locust

**Health Checks:**
```bash
GET /health
Response: {"status": "healthy", "services": {"database": "healthy", "redis": "healthy"}}
```

**Service Level Objectives:**
- Authentication: <200ms (p95), 99.9% availability
- Threat Intelligence: <500ms (p95), 99.5% availability  
- TAXII Services: <1000ms (p95), 99.0% availability

**Monitoring:** Prometheus metrics, distributed tracing with correlation IDs, error rate alerting (>1%)