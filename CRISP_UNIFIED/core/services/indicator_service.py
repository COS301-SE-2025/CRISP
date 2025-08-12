import logging
from typing import Optional, Dict, Any, List
from core.models.models import Indicator, CustomUser, Organization
from core.repositories.indicator_repository import IndicatorRepository
from .access_control_service import AccessControlService
from .audit_service import AuditService

logger = logging.getLogger(__name__)

class IndicatorService:
    """
    Service for handling Indicator operations with trust-aware access control.
    Acts as an intermediary between the STIX/TAXII service and the repository.
    Integrates with anonymization strategies using the Strategy pattern and trust levels.
    """
    
    def __init__(self, anonymization_context=None):
        """
        Initialize the service with a repository and optional anonymization context.
        
        Args:
            anonymization_context: AnonymizationContext for anonymizing data (optional)
        """
        self.repository = IndicatorRepository()
        self.anonymization_context = anonymization_context
        self.access_control = AccessControlService()
        self.audit_service = AuditService()
    
    def create_indicator(self, indicator_data, user: CustomUser = None, anonymize=False, 
                        requesting_organization: Organization = None):
        """
        Create a new indicator with trust-aware access control and optional anonymization.
        
        Args:
            indicator_data: Dictionary containing indicator data
            user: User creating the indicator
            anonymize: Boolean indicating whether to anonymize the data
            requesting_organization: Organization requesting the indicator (for trust context)
            
        Returns:
            Indicator: The created indicator
            
        Raises:
            PermissionDenied: If user lacks permission to create indicators
        """
        # Check permissions
        if user:
            self.access_control.require_permission(user, 'can_publish_threat_intelligence')
        
        # Apply trust-aware anonymization if needed
        if anonymize and requesting_organization:
            source_org = user.organization if user else None
            if source_org:
                access_info = self.access_control.get_trust_aware_data_access(
                    user, 'indicator', source_org
                )
                indicator_data = self._apply_trust_anonymization(indicator_data, access_info)
        elif anonymize:
            indicator_data = self._anonymize_indicator(indicator_data)
        
        # Create the indicator using the repository
        indicator = self.repository.create(indicator_data)
        
        # Log the creation
        if user:
            self.audit_service.log_user_action(
                user=user,
                action='indicator_created',
                success=True,
                additional_data={
                    'indicator_id': str(indicator.id),
                    'indicator_type': indicator_data.get('type'),
                    'anonymized': anonymize
                }
            )
        
        return indicator
    
    def update_indicator(self, indicator_id, indicator_data, anonymize=False):
        """
        Update an existing indicator with optional anonymization
        """
        # Placeholder for anonymization strategy
        if anonymize:
            indicator_data = self._anonymize_indicator(indicator_data)
        
        # Update the indicator using the repository
        return self.repository.update(indicator_id, indicator_data)
    
    def get_indicator_by_id(self, indicator_id):
        """
        Get an indicator by ID.
        
        Args:
            indicator_id: ID of the indicator to retrieve
            
        Returns:
            Indicator: The retrieved indicator or None if not found
        """
        return self.repository.get_by_id(indicator_id)
    
    def get_indicator_by_stix_id(self, stix_id):
        """
        Get an indicator by STIX ID.
        
        Args:
            stix_id: STIX ID of the indicator to retrieve
            
        Returns:
            Indicator: The retrieved indicator or None if not found
        """
        return self.repository.get_by_stix_id(stix_id)
    
    def get_indicators_by_feed(self, feed_id):
        """
        Get indicators by feed ID.
        
        Args:
            feed_id: ID of the feed
            
        Returns:
            QuerySet: Indicators belonging to the feed
        """
        return self.repository.get_by_feed(feed_id)
    
    def get_indicators_by_type(self, indicator_type):
        """
        Get indicators by type.
        
        Args:
            indicator_type: Type of indicators to retrieve
            
        Returns:
            QuerySet: Indicators of the specified type
        """
        return self.repository.get_by_type(indicator_type)
    
    def delete_indicator(self, indicator_id):
        """
        Delete an indicator by ID.
        
        Args:
            indicator_id: ID of the indicator to delete
        """
        self.repository.delete(indicator_id)
    
    def get_indicators_for_user(self, user: CustomUser, limit: int = 100, 
                               filters: Dict = None) -> List[Indicator]:
        """
        Get indicators accessible to a user based on trust relationships
        
        Args:
            user: User requesting indicators
            limit: Maximum number of indicators to return
            filters: Additional filters to apply
            
        Returns:
            List of accessible indicators
        """
        if not user:
            return []
        
        # Get accessible organization IDs
        accessible_org_ids = self.access_control.get_accessible_data_sources(user)
        
        # Get indicators from accessible organizations
        indicators = self.repository.get_by_organizations(accessible_org_ids, limit=limit)
        
        # Apply additional filters if provided
        if filters:
            if 'type' in filters:
                indicators = indicators.filter(type=filters['type'])
            if 'feed_id' in filters:
                indicators = indicators.filter(feed_id=filters['feed_id'])
        
        # Log access attempt
        self.audit_service.log_user_action(
            user=user,
            action='indicators_accessed',
            success=True,
            additional_data={
                'accessible_orgs_count': len(accessible_org_ids),
                'result_count': indicators.count(),
                'filters': filters or {}
            }
        )
        
        return list(indicators)
    
    def get_indicator_with_trust_context(self, indicator_id, requesting_user: CustomUser):
        """
        Get an indicator with trust-aware anonymization applied
        
        Args:
            indicator_id: ID of the indicator to retrieve
            requesting_user: User requesting the indicator
            
        Returns:
            Indicator with appropriate anonymization applied or None if not accessible
        """
        indicator = self.repository.get_by_id(indicator_id)
        if not indicator:
            return None
        
        # Check if user can access this indicator's source organization
        source_org = indicator.organization if hasattr(indicator, 'organization') else None
        if source_org and not self.access_control.can_access_organization(requesting_user, source_org):
            # Log access denial
            self.audit_service.log_security_event(
                action='indicator_access_denied',
                user=requesting_user,
                success=False,
                failure_reason='Insufficient trust relationship with source organization',
                additional_data={'indicator_id': str(indicator_id)}
            )
            return None
        
        # Apply trust-aware anonymization if needed
        if source_org and requesting_user.organization != source_org:
            access_info = self.access_control.get_trust_aware_data_access(
                requesting_user, 'indicator', source_org
            )
            if access_info['can_access']:
                # Apply anonymization based on trust level
                indicator = self._apply_trust_based_anonymization(indicator, access_info)
        
        # Log successful access
        self.audit_service.log_user_action(
            user=requesting_user,
            action='indicator_accessed',
            success=True,
            additional_data={
                'indicator_id': str(indicator_id),
                'source_organization': source_org.name if source_org else None
            }
        )
        
        return indicator
    
    def _anonymize_indicator(self, indicator_data):
        """
        Use the anonymization context to anonymize indicator data.
        
        Args:
            indicator_data: Dictionary containing indicator data
            
        Returns:
            dict: Anonymized indicator data
        """
        if self.anonymization_context:
            return self.anonymization_context.anonymize_indicator(indicator_data)
        return indicator_data
    
    def _apply_trust_anonymization(self, indicator_data: Dict, access_info: Dict) -> Dict:
        """
        Apply trust-aware anonymization to indicator data
        
        Args:
            indicator_data: Original indicator data
            access_info: Trust access information from access control service
            
        Returns:
            Anonymized indicator data based on trust level
        """
        if not access_info.get('can_access'):
            return {}
        
        anonymization_level = access_info.get('anonymization_level', 'full')
        
        if anonymization_level == 'none':
            # Full access - no anonymization
            return indicator_data
        elif anonymization_level == 'minimal':
            # Minimal anonymization - remove only highly sensitive data
            anonymized_data = indicator_data.copy()
            # Remove specific sensitive fields while keeping most data
            sensitive_fields = ['source_ip_internal', 'internal_references']
            for field in sensitive_fields:
                anonymized_data.pop(field, None)
            return anonymized_data
        elif anonymization_level == 'moderate':
            # Moderate anonymization - remove moderately sensitive data
            anonymized_data = indicator_data.copy()
            moderate_fields = ['source_ip_internal', 'internal_references', 'attribution', 'context']
            for field in moderate_fields:
                anonymized_data.pop(field, None)
            return anonymized_data
        elif anonymization_level == 'standard':
            # Standard anonymization - remove most sensitive data
            if self.anonymization_context:
                return self.anonymization_context.anonymize_indicator(indicator_data)
            return indicator_data
        else:
            # Full anonymization - heavily anonymize
            essential_fields = ['type', 'pattern', 'labels']
            return {k: v for k, v in indicator_data.items() if k in essential_fields}
    
    def _apply_trust_based_anonymization(self, indicator, access_info: Dict):
        """
        Apply trust-based anonymization to an indicator model instance
        
        Args:
            indicator: Indicator model instance
            access_info: Trust access information
            
        Returns:
            Indicator with appropriate fields anonymized
        """
        anonymization_level = access_info.get('anonymization_level', 'full')
        
        if anonymization_level == 'none':
            # No anonymization needed
            return indicator
        elif anonymization_level in ['minimal', 'moderate']:
            # Light anonymization - preserve most data
            return indicator
        else:
            # Heavier anonymization - use anonymization context if available
            if self.anonymization_context:
                # Convert to dict, anonymize, and convert back
                indicator_dict = {
                    'type': indicator.type,
                    'pattern': indicator.pattern,
                    'labels': indicator.labels,
                    'created': indicator.created,
                    'modified': indicator.modified
                }
                anonymized_dict = self._apply_trust_anonymization(indicator_dict, access_info)
                # Update indicator fields with anonymized data
                for key, value in anonymized_dict.items():
                    if hasattr(indicator, key):
                        setattr(indicator, key, value)
            
            return indicator