"""
Decorator Pattern Implementation

Implements the Decorator pattern for enhancing STIX trust objects with
validation, anonymization, enrichment, and TAXII export capabilities
as specified in the CRISP domain model.
"""

from .stix_trust_decorators import (
    StixTrustObjectComponent,
    ConcreteStixTrustComponent,
    StixTrustDecorator,
    StixTrustValidationDecorator,
    StixTrustAnonymizationDecorator,
    StixTrustEnrichmentDecorator,
    StixTrustTaxiiExportDecorator,
    StixTrustDecoratorChain,
)

__all__ = [
    'StixTrustObjectComponent',
    'ConcreteStixTrustComponent',
    'StixTrustDecorator',
    'StixTrustValidationDecorator',
    'StixTrustAnonymizationDecorator',
    'StixTrustEnrichmentDecorator',
    'StixTrustTaxiiExportDecorator',
    'StixTrustDecoratorChain',
]