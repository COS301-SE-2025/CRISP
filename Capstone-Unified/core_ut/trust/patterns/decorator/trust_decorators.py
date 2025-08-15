"""
Trust Decorator Pattern Implementation

Implements the Decorator pattern for trust management as specified in the CRISP domain model.
Provides core trust enhancement capabilities without external integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class TrustEvaluationComponent(ABC):
    """
    Abstract component interface for trust evaluations.
    Defines the interface that decorators can enhance.
    """
    
    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate trust access request."""
        pass
    
    @abstractmethod
    def get_access_level(self) -> str:
        """Get access level for this evaluation."""
        pass


class BasicTrustEvaluation(TrustEvaluationComponent):
    """
    Concrete component implementing basic trust evaluation.
    """
    
    def __init__(self, trust_relationship=None):
        self.trust_relationship = trust_relationship
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Basic trust evaluation based on relationship."""
        if not self.trust_relationship:
            return {
                'allowed': False,
                'reason': 'No trust relationship exists',
                'access_level': 'none',
                'anonymization_level': 'full'
            }
        
        if not self.trust_relationship.is_effective:
            return {
                'allowed': False,
                'reason': f'Trust relationship not effective (status: {self.trust_relationship.status})',
                'access_level': 'none',
                'anonymization_level': 'full'
            }
        
        return {
            'allowed': True,
            'reason': f'Access granted via trust level {self.trust_relationship.trust_level.name}',
            'access_level': self.trust_relationship.access_level,
            'anonymization_level': self.trust_relationship.anonymization_level,
            'trust_level': self.trust_relationship.trust_level.level
        }
    
    def get_access_level(self) -> str:
        """Get access level from trust relationship."""
        if self.trust_relationship:
            return self.trust_relationship.get_effective_access_level()
        return 'none'


class TrustEvaluationDecorator(TrustEvaluationComponent):
    """
    Abstract base decorator for trust evaluations.
    """
    
    def __init__(self, component: TrustEvaluationComponent):
        self._component = component
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to wrapped component."""
        return self._component.evaluate(context)
    
    def get_access_level(self) -> str:
        """Delegate to wrapped component."""
        return self._component.get_access_level()


class SecurityEnhancementDecorator(TrustEvaluationDecorator):
    """
    Decorator that adds additional security checks to trust evaluations.
    """
    
    def __init__(self, component: TrustEvaluationComponent, security_level: str = 'standard'):
        super().__init__(component)
        self.security_level = security_level
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced evaluation with additional security checks."""
        result = super().evaluate(context)
        
        if not result['allowed']:
            return result
        
        # Add security enhancements
        enhanced_result = result.copy()
        enhanced_result['security_enhanced'] = True
        enhanced_result['security_level'] = self.security_level
        enhanced_result['enhanced_timestamp'] = timezone.now().isoformat()
        
        # Additional security checks based on context
        user = context.get('user')
        if user and hasattr(user, 'failed_login_attempts'):
            if getattr(user, 'failed_login_attempts', 0) > 3:
                enhanced_result['allowed'] = False
                enhanced_result['reason'] = 'User has excessive failed login attempts'
                enhanced_result['security_violation'] = True
        
        # Check for suspicious timing
        request_time = context.get('request_time')
        if request_time:
            hour = request_time.hour
            if hour < 6 or hour > 22:  # Outside business hours
                enhanced_result['security_warning'] = 'Request outside business hours'
        
        # Enhanced anonymization for high security
        if self.security_level == 'high':
            if enhanced_result.get('anonymization_level') == 'none':
                enhanced_result['anonymization_level'] = 'minimal'
        
        return enhanced_result


class ComplianceDecorator(TrustEvaluationDecorator):
    """
    Decorator that adds regulatory compliance validation to trust evaluations.
    """
    
    def __init__(self, component: TrustEvaluationComponent, 
                 compliance_framework: str = 'default'):
        super().__init__(component)
        self.compliance_framework = compliance_framework
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced evaluation with compliance validation."""
        result = super().evaluate(context)
        
        if not result['allowed']:
            return result
        
        # Add compliance validation
        compliance_result = result.copy()
        compliance_result['compliance_validated'] = True
        compliance_result['compliance_framework'] = self.compliance_framework
        compliance_result['compliance_timestamp'] = timezone.now().isoformat()
        
        # Check data retention requirements
        retention_days = context.get('data_retention_days', 365)
        if retention_days > 2555:  # More than 7 years
            compliance_result['compliance_warning'] = 'Data retention exceeds standard policy'
        
        # Validate anonymization requirements
        resource_type = context.get('resource_type', '')
        if resource_type in ['pii', 'sensitive'] and result.get('anonymization_level') == 'none':
            compliance_result['allowed'] = False
            compliance_result['reason'] = 'Compliance requires anonymization for sensitive data'
            compliance_result['compliance_violation'] = True
        
        return compliance_result


class AuditDecorator(TrustEvaluationDecorator):
    """
    Decorator that adds comprehensive audit logging to trust decisions.
    """
    
    def __init__(self, component: TrustEvaluationComponent, audit_level: str = 'standard'):
        super().__init__(component)
        self.audit_level = audit_level
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced evaluation with audit logging."""
        start_time = timezone.now()
        result = super().evaluate(context)
        end_time = timezone.now()
        
        # Add audit information
        audit_result = result.copy()
        audit_result['audit_logged'] = True
        audit_result['audit_level'] = self.audit_level
        audit_result['evaluation_duration'] = (end_time - start_time).total_seconds()
        audit_result['audit_timestamp'] = start_time.isoformat()
        
        # Create audit trail
        audit_entry = {
            'timestamp': start_time.isoformat(),
            'context': self._sanitize_context(context),
            'result': result,
            'evaluation_duration': audit_result['evaluation_duration'],
            'audit_level': self.audit_level
        }
        
        # Log the audit entry
        if self.audit_level == 'detailed':
            logger.info(f"Trust evaluation audit: {audit_entry}")
        else:
            logger.info(f"Trust evaluation: allowed={result['allowed']}, "
                       f"reason={result.get('reason', 'N/A')}")
        
        # Store audit reference
        audit_result['audit_reference'] = f"audit_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        return audit_result
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from audit context."""
        sanitized = context.copy()
        sensitive_keys = ['password', 'token', 'secret', 'key']
        
        for key in list(sanitized.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '[REDACTED]'
        
        return sanitized


class TrustDecoratorChain:
    """
    Builder class for creating decorator chains for trust evaluations.
    Provides a fluent interface for applying multiple decorators.
    """
    
    def __init__(self, trust_relationship=None):
        self._component = BasicTrustEvaluation(trust_relationship)
    
    def add_security_enhancement(self, security_level: str = 'standard') -> 'TrustDecoratorChain':
        """Add security enhancement decorator to the chain."""
        self._component = SecurityEnhancementDecorator(self._component, security_level)
        return self
    
    def add_compliance_validation(self, compliance_framework: str = 'default') -> 'TrustDecoratorChain':
        """Add compliance validation decorator to the chain."""
        self._component = ComplianceDecorator(self._component, compliance_framework)
        return self
    
    def add_audit_logging(self, audit_level: str = 'standard') -> 'TrustDecoratorChain':
        """Add audit logging decorator to the chain."""
        self._component = AuditDecorator(self._component, audit_level)
        return self
    
    def build(self) -> TrustEvaluationComponent:
        """Build and return the final decorated component."""
        return self._component
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method to evaluate with current chain."""
        return self._component.evaluate(context)