"""
Trust Strategy Pattern Implementation

Implements the Strategy pattern for trust evaluation algorithms.
Provides different trust evaluation strategies for various scenarios.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)


class TrustEvaluationStrategy(ABC):
    """
    Abstract base class for trust evaluation strategies.
    Implements the Strategy pattern for trust evaluation algorithms.
    """
    
    @abstractmethod
    def evaluate_trust(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate trust based on the strategy's algorithm.
        
        Args:
            context: Trust evaluation context containing user, resource, and other data
            
        Returns:
            Dictionary containing trust evaluation results
        """
        pass


class BasicTrustStrategy(TrustEvaluationStrategy):
    """
    Basic trust evaluation strategy.
    Uses simple trust level-based evaluation.
    """
    
    def evaluate_trust(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate trust using basic trust level approach.
        
        Args:
            context: Trust evaluation context
            
        Returns:
            Basic trust evaluation results
        """
        trust_level = context.get('trust_level')
        user = context.get('user')
        resource = context.get('resource')
        
        if not trust_level:
            return {
                'trust_score': 0,
                'access_granted': False,
                'reason': 'No trust level specified',
                'strategy': 'basic'
            }
        
        # Simple trust score based on trust level
        trust_score = min(trust_level.level * 10, 100)
        
        # Grant access if trust level is 3 or higher
        access_granted = trust_level.level >= 3
        
        return {
            'trust_score': trust_score,
            'access_granted': access_granted,
            'reason': f'Trust level {trust_level.level} evaluation',
            'strategy': 'basic',
            'trust_level_name': trust_level.name,
            'evaluation_timestamp': timezone.now().isoformat()
        }


class AdvancedTrustStrategy(TrustEvaluationStrategy):
    """
    Advanced trust evaluation strategy.
    Considers multiple factors including user history, context, and risk assessment.
    """
    
    def evaluate_trust(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate trust using advanced multi-factor approach.
        
        Args:
            context: Trust evaluation context
            
        Returns:
            Advanced trust evaluation results
        """
        trust_level = context.get('trust_level')
        user = context.get('user')
        resource = context.get('resource')
        user_history = context.get('user_history', {})
        time_context = context.get('time_context', {})
        resource_sensitivity = context.get('resource_sensitivity', 'standard')
        
        if not trust_level:
            return {
                'trust_score': 0,
                'access_granted': False,
                'reason': 'No trust level specified',
                'strategy': 'advanced'
            }
        
        # Base trust score from trust level
        base_score = trust_level.level * 10
        
        # Factor in user history
        history_modifier = self._calculate_history_modifier(user_history)
        
        # Factor in time context
        time_modifier = self._calculate_time_modifier(time_context)
        
        # Factor in resource sensitivity
        sensitivity_modifier = self._calculate_sensitivity_modifier(resource_sensitivity)
        
        # Calculate final trust score
        trust_score = min(
            base_score + history_modifier + time_modifier + sensitivity_modifier,
            100
        )
        
        # Access decision based on multiple factors
        access_granted = self._determine_access(
            trust_score, resource_sensitivity, time_context, user_history
        )
        
        factors_considered = {
            'base_score': base_score,
            'history_modifier': history_modifier,
            'time_modifier': time_modifier,
            'sensitivity_modifier': sensitivity_modifier,
            'resource_sensitivity': resource_sensitivity
        }
        
        return {
            'trust_score': max(0, trust_score),
            'access_granted': access_granted,
            'reason': self._generate_reason(trust_score, access_granted, factors_considered),
            'strategy': 'advanced',
            'factors_considered': factors_considered,
            'trust_level_name': trust_level.name,
            'evaluation_timestamp': timezone.now().isoformat()
        }
    
    def _calculate_history_modifier(self, user_history: Dict[str, Any]) -> int:
        """Calculate trust modifier based on user history."""
        successful_accesses = user_history.get('successful_accesses', 0)
        failed_accesses = user_history.get('failed_accesses', 0)
        
        if successful_accesses + failed_accesses == 0:
            return 0
        
        success_rate = successful_accesses / (successful_accesses + failed_accesses)
        
        if success_rate >= 0.95:
            return 10
        elif success_rate >= 0.8:
            return 5
        elif success_rate >= 0.6:
            return 0
        else:
            return -10
    
    def _calculate_time_modifier(self, time_context: Dict[str, Any]) -> int:
        """Calculate trust modifier based on time context."""
        hour = time_context.get('hour')
        day_of_week = time_context.get('day_of_week')
        
        modifier = 0
        
        # Business hours bonus
        if hour and 8 <= hour <= 18:
            modifier += 5
        elif hour and (hour < 6 or hour > 22):
            modifier -= 5
        
        # Weekday bonus
        if day_of_week and 1 <= day_of_week <= 5:
            modifier += 2
        
        return modifier
    
    def _calculate_sensitivity_modifier(self, resource_sensitivity: str) -> int:
        """Calculate trust modifier based on resource sensitivity."""
        sensitivity_modifiers = {
            'low': 5,
            'standard': 0,
            'high': -10,
            'critical': -20
        }
        
        return sensitivity_modifiers.get(resource_sensitivity, 0)
    
    def _determine_access(self, trust_score: int, resource_sensitivity: str, 
                         time_context: Dict[str, Any], user_history: Dict[str, Any]) -> bool:
        """Determine access based on multiple factors."""
        # Base threshold varies by resource sensitivity
        thresholds = {
            'low': 30,
            'standard': 50,
            'high': 70,
            'critical': 85
        }
        
        threshold = thresholds.get(resource_sensitivity, 50)
        
        # Additional checks for sensitive resources
        if resource_sensitivity in ['high', 'critical']:
            # Require good history for sensitive resources
            failed_accesses = user_history.get('failed_accesses', 0)
            if failed_accesses > 5:
                return False
            
            # Check time restrictions for critical resources
            if resource_sensitivity == 'critical':
                hour = time_context.get('hour')
                if hour and (hour < 8 or hour > 18):
                    return False
        
        return trust_score >= threshold
    
    def _generate_reason(self, trust_score: int, access_granted: bool, 
                        factors: Dict[str, Any]) -> str:
        """Generate human-readable reason for the trust decision."""
        if access_granted:
            return f"Access granted with trust score {trust_score}"
        else:
            return f"Access denied with trust score {trust_score}"


class RiskBasedTrustStrategy(TrustEvaluationStrategy):
    """
    Risk-based trust evaluation strategy.
    Focuses on risk assessment and mitigation.
    """
    
    def evaluate_trust(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate trust using risk-based approach.
        
        Args:
            context: Trust evaluation context
            
        Returns:
            Risk-based trust evaluation results
        """
        trust_level = context.get('trust_level')
        user = context.get('user')
        resource = context.get('resource')
        risk_factors = context.get('risk_factors', {})
        
        if not trust_level:
            return {
                'trust_score': 0,
                'access_granted': False,
                'reason': 'No trust level specified',
                'strategy': 'risk_based'
            }
        
        # Base trust score
        base_score = trust_level.level * 10
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(risk_factors)
        
        # Adjust trust score based on risk
        adjusted_score = max(0, base_score - risk_score)
        
        # Access decision
        access_granted = adjusted_score >= 40 and risk_score < 50
        
        return {
            'trust_score': adjusted_score,
            'access_granted': access_granted,
            'reason': f'Risk-adjusted trust score {adjusted_score} (risk: {risk_score})',
            'strategy': 'risk_based',
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'trust_level_name': trust_level.name,
            'evaluation_timestamp': timezone.now().isoformat()
        }
    
    def _calculate_risk_score(self, risk_factors: Dict[str, Any]) -> int:
        """Calculate risk score based on various risk factors."""
        risk_score = 0
        
        # IP-based risk
        if risk_factors.get('unknown_ip'):
            risk_score += 20
        
        # Device-based risk
        if risk_factors.get('unknown_device'):
            risk_score += 15
        
        # Time-based risk
        if risk_factors.get('unusual_time'):
            risk_score += 10
        
        # Behavioral risk
        if risk_factors.get('unusual_behavior'):
            risk_score += 25
        
        # Geographic risk
        if risk_factors.get('unusual_location'):
            risk_score += 20
        
        return min(risk_score, 100)


class TrustEvaluationContext:
    """
    Context class for trust evaluation strategies.
    Allows dynamic strategy switching.
    """
    
    def __init__(self, strategy: TrustEvaluationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: TrustEvaluationStrategy):
        """Set the trust evaluation strategy."""
        self._strategy = strategy
    
    def execute_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the current trust evaluation strategy."""
        return self._strategy.evaluate_trust(context)


class TrustContext:
    """
    Utility class for creating and managing trust evaluation contexts.
    """
    
    @staticmethod
    def create_context(user, resource: str, organization=None, 
                      additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a standardized trust evaluation context.
        
        Args:
            user: User requesting access
            resource: Resource being accessed
            organization: Organization context
            additional_data: Additional context data
            
        Returns:
            Standardized trust context dictionary
        """
        context = {
            'user': user,
            'resource': resource,
            'organization': organization,
            'timestamp': timezone.now(),
            'request_id': str(uuid.uuid4()),
            'additional_data': additional_data or {}
        }
        
        return context
    
    @staticmethod
    def validate_context(context: Dict[str, Any]) -> bool:
        """
        Validate that a trust context contains required fields.
        
        Args:
            context: Trust context to validate
            
        Returns:
            True if context is valid, False otherwise
        """
        required_fields = ['user', 'resource']
        
        for field in required_fields:
            if field not in context or context[field] is None:
                return False
        
        return True
    
    @staticmethod
    def enrich_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich trust context with additional metadata.
        
        Args:
            context: Base trust context
            
        Returns:
            Enriched trust context
        """
        enriched = context.copy()
        
        # Add request metadata
        if 'request_id' not in enriched:
            enriched['request_id'] = str(uuid.uuid4())
        
        # Add session information
        enriched['session_info'] = {
            'session_id': str(uuid.uuid4()),
            'created_at': timezone.now().isoformat()
        }
        
        # Add security context
        enriched['security_context'] = {
            'requires_mfa': False,
            'ip_whitelist_checked': False,
            'device_fingerprint': None
        }
        
        return enriched


# Strategy registry for easy access
TRUST_STRATEGIES = {
    'basic': BasicTrustStrategy,
    'advanced': AdvancedTrustStrategy,
    'risk_based': RiskBasedTrustStrategy
}


def get_trust_strategy(strategy_name: str) -> TrustEvaluationStrategy:
    """
    Get a trust evaluation strategy by name.
    
    Args:
        strategy_name: Name of the strategy to get
        
    Returns:
        Trust evaluation strategy instance
        
    Raises:
        ValueError: If strategy name is not recognized
    """
    if strategy_name not in TRUST_STRATEGIES:
        raise ValueError(f"Unknown trust strategy: {strategy_name}")
    
    return TRUST_STRATEGIES[strategy_name]()
