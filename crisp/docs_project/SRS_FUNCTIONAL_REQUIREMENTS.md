# Software Requirements Specification (SRS)
## CRISP - Cyber Risk Information Sharing Platform

**Version:** 1.1  
**Date:** May 26, 2025  
**Prepared by:** Data Defenders  
**Client:** BlueVision ITM

---

## R4. Trust Relationship Management

### R4.1 Trust Configuration
- **R4.1.1** CRISP shall support three trust levels: Public, Trusted, Restricted
- **R4.1.2** CRISP shall allow System Administrators to configure Institution trust relationships
- **R4.1.3** CRISP shall support community groups for multi-Institution trust relationships
- **R4.1.4** CRISP shall enable bilateral trust agreements between Institutions

### R4.2 Access Control
- **R4.2.1** CRISP shall filter shared intelligence based on established trust relationships
- **R4.2.2** CRISP shall apply appropriate anonymization levels based on trust level
- **R4.2.3** CRISP shall log all access to shared intelligence for audit purposes
- **R4.2.4** CRISP shall support immediate trust relationship revocation with effect on data sharing

## Trust Levels Definition

### Public Trust Level
- **Access:** Basic threat intelligence indicators
- **Anonymization:** Full anonymization of source details
- **Sharing:** Public indicators, general threat patterns
- **Use Case:** Broad community sharing of basic threat data

### Trusted Trust Level  
- **Access:** Detailed threat intelligence with context
- **Anonymization:** Partial anonymization preserving analytical value
- **Sharing:** Detailed IoCs, TTPs, attack patterns with context
- **Use Case:** Established partners with proven reliability

### Restricted Trust Level
- **Access:** Sensitive threat intelligence and attribution
- **Anonymization:** Minimal anonymization, source attribution preserved
- **Sharing:** Full threat intelligence including sensitive details
- **Use Case:** Close partners, incident response cooperation

## Key Trust Management Entities

- **TrustLevel**: Defines the three trust levels (Public, Trusted, Restricted)
- **TrustRelationship**: Bilateral trust agreements between institutions
- **TrustGroup**: Community groups for multi-institution trust relationships  
- **TrustLog**: Audit trail for all trust-related access and actions
- **AccessControlContext**: Context for making trust-based access decisions