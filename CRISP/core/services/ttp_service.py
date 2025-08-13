import logging
from typing import Optional, Dict, Any, List
from core.models.models import TTPData, CustomUser, Organization
from core.repositories.ttp_repository import TTPRepository
from .access_control_service import AccessControlService
from .audit_service import AuditService

logger = logging.getLogger(__name__)

class TTPService:
    """
    Service for handling TTP (Tactics, Techniques, and Procedures) operations with trust-aware access control.
    Acts as an intermediary between the STIX/TAXII service and the repository.
    Integrates with anonymization strategies using the Strategy pattern and trust levels.
    """
    
    def __init__(self, anonymization_context=None):
        """
        Initialize the service with a repository and optional anonymization context.
        
        Args:
            anonymization_context: AnonymizationContext for anonymizing data (optional)
        """
        self.repository = TTPRepository()
        self.anonymization_context = anonymization_context
        self.access_control = AccessControlService()
        self.audit_service = AuditService()
    
    def create_ttp(self, ttp_data, user: CustomUser = None, anonymize=False, 
                   requesting_organization: Organization = None):
        """
        Create a new TTP with trust-aware access control and optional anonymization.
        
        Args:
            ttp_data: Dictionary containing TTP data
            user: User creating the TTP
            anonymize: Boolean indicating whether to anonymize the data
            requesting_organization: Organization requesting the TTP (for trust context)
            
        Returns:
            TTPData: The created TTP
            
        Raises:
            PermissionDenied: If user lacks permission to create TTPs
        """
        # Check permissions
        if user:
            self.access_control.require_permission(user, 'can_publish_threat_intelligence')
        
        # Apply trust-aware anonymization if needed
        if anonymize and requesting_organization:
            source_org = user.organization if user else None
            if source_org:
                access_info = self.access_control.get_trust_aware_data_access(
                    user, 'ttp', source_org
                )
                ttp_data = self._apply_trust_anonymization(ttp_data, access_info)
        elif anonymize:
            ttp_data = self._anonymize_ttp(ttp_data)
        
        # Create the TTP using the repository
        ttp = self.repository.create(ttp_data)
        
        # Log the creation
        if user:
            self.audit_service.log_user_action(
                user=user,
                action='ttp_created',
                success=True,
                additional_data={
                    'ttp_id': str(ttp.id),
                    'mitre_technique_id': ttp_data.get('mitre_technique_id'),
                    'anonymized': anonymize
                }
            )
        
        return ttp
    
    def update_ttp(self, ttp_id, ttp_data, anonymize=False):
        """
        Update an existing TTP with optional anonymization.
        
        Args:
            ttp_id: ID of the TTP to update
            ttp_data: Dictionary containing updated TTP data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            TTPData: The updated TTP
        """
        # Placeholder for anonymization strategy
        if anonymize:
            # This will be implemented later to use the strategy pattern
            ttp_data = self._anonymize_ttp(ttp_data)
        
        # Update the TTP using the repository
        return self.repository.update(ttp_id, ttp_data)
    
    def get_ttp_by_id(self, ttp_id):
        """
        Get a TTP by ID.
        
        Args:
            ttp_id: ID of the TTP to retrieve
            
        Returns:
            TTPData: The retrieved TTP or None if not found
        """
        return self.repository.get_by_id(ttp_id)
    
    def get_ttp_by_stix_id(self, stix_id):
        """
        Get a TTP by STIX ID.
        
        Args:
            stix_id: STIX ID of the TTP to retrieve
            
        Returns:
            TTPData: The retrieved TTP or None if not found
        """
        return self.repository.get_by_stix_id(stix_id)
    
    def get_ttps_by_feed(self, feed_id):
        """
        Get TTPs by feed ID.
        
        Args:
            feed_id: ID of the feed
            
        Returns:
            QuerySet: TTPs belonging to the feed
        """
        return self.repository.get_by_feed(feed_id)
    
    def get_ttps_by_mitre_id(self, mitre_id):
        """
        Get TTPs by MITRE ATT&CK technique ID.
        
        Args:
            mitre_id: MITRE technique ID
            
        Returns:
            QuerySet: TTPs with the specified MITRE technique ID
        """
        return self.repository.get_by_mitre_id(mitre_id)
    
    def delete_ttp(self, ttp_id):
        """
        Delete a TTP by ID.
        
        Args:
            ttp_id: ID of the TTP to delete
        """
        self.repository.delete(ttp_id)
    
    def get_ttps_for_user(self, user: CustomUser, limit: int = 100, 
                         filters: Dict = None) -> List[TTPData]:
        """
        Get TTPs accessible to a user based on trust relationships
        
        Args:
            user: User requesting TTPs
            limit: Maximum number of TTPs to return
            filters: Additional filters to apply
            
        Returns:
            List of accessible TTPs
        """
        if not user:
            return []
        
        # Get accessible organization IDs
        accessible_org_ids = self.access_control.get_accessible_data_sources(user)
        
        # Get TTPs from accessible organizations
        ttps = self.repository.get_by_organizations(accessible_org_ids, limit=limit)
        
        # Apply additional filters if provided
        if filters:
            if 'mitre_technique_id' in filters:
                ttps = ttps.filter(mitre_technique_id=filters['mitre_technique_id'])
            if 'feed_id' in filters:
                ttps = ttps.filter(feed_id=filters['feed_id'])
        
        # Log access attempt
        self.audit_service.log_user_action(
            user=user,
            action='ttps_accessed',
            success=True,
            additional_data={
                'accessible_orgs_count': len(accessible_org_ids),
                'result_count': ttps.count(),
                'filters': filters or {}
            }
        )
        
        return list(ttps)
    
    def get_ttp_with_trust_context(self, ttp_id, requesting_user: CustomUser):
        """
        Get a TTP with trust-aware anonymization applied
        
        Args:
            ttp_id: ID of the TTP to retrieve
            requesting_user: User requesting the TTP
            
        Returns:
            TTP with appropriate anonymization applied or None if not accessible
        """
        ttp = self.repository.get_by_id(ttp_id)
        if not ttp:
            return None
        
        # Check if user can access this TTP's source organization
        source_org = ttp.organization if hasattr(ttp, 'organization') else None
        if source_org and not self.access_control.can_access_organization(requesting_user, source_org):
            # Log access denial
            self.audit_service.log_security_event(
                action='ttp_access_denied',
                user=requesting_user,
                success=False,
                failure_reason='Insufficient trust relationship with source organization',
                additional_data={'ttp_id': str(ttp_id)}
            )
            return None
        
        # Apply trust-aware anonymization if needed
        if source_org and requesting_user.organization != source_org:
            access_info = self.access_control.get_trust_aware_data_access(
                requesting_user, 'ttp', source_org
            )
            if access_info['can_access']:
                # Apply anonymization based on trust level
                ttp = self._apply_trust_based_anonymization(ttp, access_info)
        
        # Log successful access
        self.audit_service.log_user_action(
            user=requesting_user,
            action='ttp_accessed',
            success=True,
            additional_data={
                'ttp_id': str(ttp_id),
                'source_organization': source_org.name if source_org else None
            }
        )
        
        return ttp
    
    def _anonymize_ttp(self, ttp_data):
        """
        Use the anonymization context to anonymize TTP data.
        
        Args:
            ttp_data: Dictionary containing TTP data
            
        Returns:
            dict: Anonymized TTP data
        """
        if self.anonymization_context:
            return self.anonymization_context.anonymize_ttp(ttp_data)
        return ttp_data
    
    def _apply_trust_anonymization(self, ttp_data: Dict, access_info: Dict) -> Dict:
        """
        Apply trust-aware anonymization to TTP data
        
        Args:
            ttp_data: Original TTP data
            access_info: Trust access information from access control service
            
        Returns:
            Anonymized TTP data based on trust level
        """
        if not access_info.get('can_access'):
            return {}
        
        anonymization_level = access_info.get('anonymization_level', 'full')
        
        if anonymization_level == 'none':
            # Full access - no anonymization
            return ttp_data
        elif anonymization_level == 'minimal':
            # Minimal anonymization - remove only highly sensitive data
            anonymized_data = ttp_data.copy()
            sensitive_fields = ['internal_context', 'source_attribution']
            for field in sensitive_fields:
                anonymized_data.pop(field, None)
            return anonymized_data
        elif anonymization_level == 'moderate':
            # Moderate anonymization - remove moderately sensitive data
            anonymized_data = ttp_data.copy()
            moderate_fields = ['internal_context', 'source_attribution', 'specific_targets', 'campaign_details']
            for field in moderate_fields:
                anonymized_data.pop(field, None)
            return anonymized_data
        elif anonymization_level == 'standard':
            # Standard anonymization - remove most sensitive data
            if self.anonymization_context:
                return self.anonymization_context.anonymize_ttp(ttp_data)
            return ttp_data
        else:
            # Full anonymization - heavily anonymize
            essential_fields = ['mitre_technique_id', 'technique_name', 'tactic', 'description']
            return {k: v for k, v in ttp_data.items() if k in essential_fields}
    
    def _apply_trust_based_anonymization(self, ttp, access_info: Dict):
        """
        Apply trust-based anonymization to a TTP model instance
        
        Args:
            ttp: TTP model instance
            access_info: Trust access information
            
        Returns:
            TTP with appropriate fields anonymized
        """
        anonymization_level = access_info.get('anonymization_level', 'full')
        
        if anonymization_level == 'none':
            # No anonymization needed
            return ttp
        elif anonymization_level in ['minimal', 'moderate']:
            # Light anonymization - preserve most data
            return ttp
        else:
            # Heavier anonymization - use anonymization context if available
            if self.anonymization_context:
                # Convert to dict, anonymize, and convert back
                ttp_dict = {
                    'mitre_technique_id': ttp.mitre_technique_id,
                    'technique_name': ttp.technique_name,
                    'tactic': ttp.tactic,
                    'description': ttp.description,
                    'created': ttp.created,
                    'modified': ttp.modified
                }
                anonymized_dict = self._apply_trust_anonymization(ttp_dict, access_info)
                # Update TTP fields with anonymized data
                for key, value in anonymized_dict.items():
                    if hasattr(ttp, key):
                        setattr(ttp, key, value)
            
            return ttp