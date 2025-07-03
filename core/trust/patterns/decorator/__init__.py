"""
Decorator Pattern Implementation

Implements the Decorator pattern for trust management as specified in the CRISP domain model.
"""

from .trust_decorators import (
    TrustEvaluationComponent,
    BasicTrustEvaluation,
    TrustEvaluationDecorator,
    SecurityEnhancementDecorator,
    ComplianceDecorator,
    AuditDecorator,
    TrustDecoratorChain,
)

__all__ = [
    'TrustEvaluationComponent',
    'BasicTrustEvaluation', 
    'TrustEvaluationDecorator',
    'SecurityEnhancementDecorator',
    'ComplianceDecorator',
    'AuditDecorator',
    'TrustDecoratorChain',
]