from typing import Dict, List, Optional, Any, Tuple
from django.db.models import QuerySet
from django.core.exceptions import PermissionDenied
from ..models import CustomUser, Organization
from core.trust.models import TrustRelationship, TrustLevel, TrustGroup
from .access_control_service import AccessControlService
import logging

logger = logging.getLogger(__name__)


class TrustAwareService:
    """
    High-level service that provides trust-aware operations for the CRISP platform.
    Combines user management and trust management functionality.
    """
    
    def __init__(self):
        self.access_control = AccessControlService()
    
    def get_user_dashboard_data(self, user: CustomUser) -> Dict[str, Any]:
        """
        Get dashboard data for a user based on their role and trust relationships.
        
        Args:
            user: User to get dashboard data for
            
        Returns:
            dict: Dashboard data including accessible organizations, permissions, etc.
        """
        if not user.is_active:
            return {'error': 'User account is not active'}
        
        dashboard_data = {
            'user_info': {
                'username': user.username,
                'role': user.role,
                'organization': {
                    'id': str(user.organization.id),
                    'name': user.organization.name,
                    'domain': user.organization.domain
                },
                'permissions': list(self.access_control.get_user_permissions(user)),
                'is_publisher': user.is_publisher,
                'is_verified': user.is_verified,
            },
            'accessible_organizations': [],
            'trust_relationships': [],
            'trust_groups': [],
            'recent_activities': [],
            'pending_actions': []
        }
        
        # Get accessible organizations
        accessible_orgs = self.access_control.get_accessible_organizations(user)
        dashboard_data['accessible_organizations'] = [
            {
                'id': str(org.id),
                'name': org.name,
                'domain': org.domain,
                'is_own': org.id == user.organization.id,
                'access_level': self._get_org_access_level(user, org)
            }
            for org in accessible_orgs
        ]
        
        # Get trust relationships (for publishers and admins)
        if user.can_manage_trust_relationships:
            trust_relationships = self._get_user_trust_relationships(user)
            dashboard_data['trust_relationships'] = trust_relationships
            
            # Get trust groups
            trust_groups = self._get_user_trust_groups(user)
            dashboard_data['trust_groups'] = trust_groups
            
            # Get pending actions
            pending_actions = self._get_pending_trust_actions(user)
            dashboard_data['pending_actions'] = pending_actions
        
        return dashboard_data
    
    def _get_org_access_level(self, user: CustomUser, organization: Organization) -> str:
        """Get the access level for a user to a specific organization"""
        if organization.id == user.organization.id:
            return 'full'
        
        if user.role == 'BlueVisionAdmin':
            return 'administrative'
        
        # Check trust relationship
        try:
            relationship = TrustRelationship.objects.filter(
                source_organization=user.organization,
                target_organization=organization,
                is_active=True,
                status='active'
            ).select_related('trust_level').first()
            
            if relationship:
                return relationship.get_effective_access_level()
        except Exception as e:
            logger.error(f"Error getting org access level: {str(e)}")
        
        return 'none'
    
    def _get_user_trust_relationships(self, user: CustomUser) -> List[Dict]:
        """Get trust relationships for user's organization"""
        relationships = []
        
        try:
            # Outgoing relationships (where user's org is source)
            outgoing = TrustRelationship.objects.filter(
                source_organization=user.organization
            ).select_related('target_organization', 'trust_level')
            
            for rel in outgoing:
                relationships.append({
                    'id': str(rel.id),
                    'type': 'outgoing',
                    'partner_organization': {
                        'id': str(rel.target_organization.id),
                        'name': rel.target_organization.name
                    },
                    'trust_level': rel.trust_level.name,
                    'status': rel.status,
                    'access_level': rel.get_effective_access_level(),
                    'anonymization_level': rel.get_effective_anonymization_level(),
                    'is_bilateral': rel.is_bilateral,
                    'created_at': rel.created_at.isoformat(),
                    'is_effective': rel.is_effective
                })
            
            # Incoming relationships (where user's org is target)
            incoming = TrustRelationship.objects.filter(
                target_organization=user.organization
            ).select_related('source_organization', 'trust_level')
            
            for rel in incoming:
                relationships.append({
                    'id': str(rel.id),
                    'type': 'incoming',
                    'partner_organization': {
                        'id': str(rel.source_organization.id),
                        'name': rel.source_organization.name
                    },
                    'trust_level': rel.trust_level.name,
                    'status': rel.status,
                    'access_level': rel.get_effective_access_level(),
                    'anonymization_level': rel.get_effective_anonymization_level(),
                    'is_bilateral': rel.is_bilateral,
                    'created_at': rel.created_at.isoformat(),
                    'is_effective': rel.is_effective
                })
                
        except Exception as e:
            logger.error(f"Error getting trust relationships: {str(e)}")
        
        return relationships
    
    def _get_user_trust_groups(self, user: CustomUser) -> List[Dict]:
        """Get trust groups for user's organization"""
        groups = []
        
        try:
            from core.trust.models import TrustGroupMembership
            
            memberships = TrustGroupMembership.objects.filter(
                organization=user.organization,
                is_active=True
            ).select_related('trust_group')
            
            for membership in memberships:
                group = membership.trust_group
                groups.append({
                    'id': str(group.id),
                    'name': group.name,
                    'description': group.description,
                    'group_type': group.group_type,
                    'membership_type': membership.membership_type,
                    'member_count': group.get_member_count(),
                    'is_public': group.is_public,
                    'joined_at': membership.joined_at.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error getting trust groups: {str(e)}")
        
        return groups
    
    def _get_pending_trust_actions(self, user: CustomUser) -> List[Dict]:
        """Get pending trust-related actions for the user"""
        pending = []
        
        try:
            # Pending trust relationship approvals
            pending_relationships = TrustRelationship.objects.filter(
                target_organization=user.organization,
                status='pending',
                approved_by_target=False
            ).select_related('source_organization', 'trust_level')
            
            for rel in pending_relationships:
                pending.append({
                    'type': 'trust_approval',
                    'id': str(rel.id),
                    'title': f"Trust relationship request from {rel.source_organization.name}",
                    'description': f"Requesting {rel.trust_level.name} trust level",
                    'created_at': rel.created_at.isoformat(),
                    'priority': 'medium',
                    'action_required': 'approve_or_deny'
                })
            
            # TODO: Add other types of pending actions like:
            # - Trust group invitations
            # - Policy update approvals
            # - Security alerts requiring attention
            
        except Exception as e:
            logger.error(f"Error getting pending actions: {str(e)}")
        
        return pending
    
    def create_trust_relationship(self, requesting_user: CustomUser,
                                target_organization: Organization,
                                trust_level: TrustLevel,
                                relationship_type: str = 'bilateral',
                                notes: str = '') -> TrustRelationship:
        """
        Create a new trust relationship between organizations.
        
        Args:
            requesting_user: User creating the relationship
            target_organization: Target organization for the relationship
            trust_level: Trust level for the relationship
            relationship_type: Type of relationship (bilateral, community, etc.)
            notes: Optional notes about the relationship
            
        Returns:
            TrustRelationship: Created trust relationship
            
        Raises:
            PermissionDenied: If user doesn't have permission to create relationships
        """
        # Check permissions
        self.access_control.require_permission(
            requesting_user, 
            'can_manage_trust_relationships'
        )
        
        # Validate that user can create relationships for their organization
        if requesting_user.organization == target_organization:
            raise ValueError("Cannot create trust relationship with own organization")
        
        # Check if relationship already exists
        existing = TrustRelationship.objects.filter(
            source_organization=requesting_user.organization,
            target_organization=target_organization
        ).first()
        
        if existing:
            raise ValueError("Trust relationship already exists between these organizations")
        
        # Create the relationship
        relationship = TrustRelationship.objects.create(
            source_organization=requesting_user.organization,
            target_organization=target_organization,
            trust_level=trust_level,
            relationship_type=relationship_type,
            status='pending',
            notes=notes,
            created_by=requesting_user,
            last_modified_by=requesting_user,
            anonymization_level=trust_level.default_anonymization_level,
            access_level=trust_level.default_access_level
        )
        
        # Auto-approve from source side
        relationship.approve(requesting_user.organization, requesting_user)
        
        logger.info(
            f"Trust relationship created between {requesting_user.organization.name} "
            f"and {target_organization.name} by {requesting_user.username}"
        )
        
        return relationship
    
    def approve_trust_relationship(self, approving_user: CustomUser,
                                 relationship_id: str, approve: bool = True,
                                 reason: str = '') -> TrustRelationship:
        """
        Approve or deny a trust relationship.
        
        Args:
            approving_user: User approving/denying the relationship
            relationship_id: ID of the relationship to approve/deny
            approve: True to approve, False to deny
            reason: Optional reason for the decision
            
        Returns:
            TrustRelationship: Updated trust relationship
            
        Raises:
            PermissionDenied: If user doesn't have permission
        """
        # Check permissions
        self.access_control.require_permission(
            approving_user,
            'can_manage_trust_relationships'
        )
        
        try:
            relationship = TrustRelationship.objects.get(id=relationship_id)
        except TrustRelationship.DoesNotExist:
            raise ValueError("Trust relationship not found")
        
        # Check if user can approve this relationship
        if (relationship.target_organization != approving_user.organization and
            approving_user.role != 'BlueVisionAdmin'):
            raise PermissionDenied("Cannot approve relationship for other organizations")
        
        if approve:
            relationship.approve(approving_user.organization, approving_user)
            action = "approved"
        else:
            relationship.deny(approving_user.organization, approving_user, reason)
            action = "denied"
        
        logger.info(
            f"Trust relationship {relationship.id} {action} by {approving_user.username}"
        )
        
        return relationship
    
    def get_threat_intelligence_access(self, user: CustomUser,
                                     source_organization: Organization,
                                     threat_data: Dict) -> Dict[str, Any]:
        """
        Get access information for threat intelligence data.
        
        Args:
            user: User requesting access
            source_organization: Organization that published the threat data
            threat_data: Metadata about the threat intelligence
            
        Returns:
            dict: Access information and anonymized data
        """
        access_info = self.access_control.get_trust_aware_data_access(
            user, 'threat_intelligence', source_organization
        )
        
        if not access_info['can_access']:
            return {
                'can_access': False,
                'message': 'Access denied based on trust relationships'
            }
        
        # Apply anonymization based on trust level
        anonymized_data = self._apply_anonymization(
            threat_data, access_info['anonymization_level']
        )
        
        return {
            'can_access': True,
            'data': anonymized_data,
            'access_info': access_info,
            'trust_metadata': {
                'source_organization': source_organization.name,
                'anonymization_applied': access_info['anonymization_level'],
                'access_level': access_info['access_level'],
                'restrictions': access_info.get('restrictions', [])
            }
        }
    
    def _apply_anonymization(self, data: Dict, anonymization_level: str) -> Dict:
        """
        Apply anonymization to data based on trust level.
        
        Args:
            data: Original data
            anonymization_level: Level of anonymization to apply
            
        Returns:
            dict: Anonymized data
        """
        if anonymization_level == 'none':
            return data.copy()
        
        anonymized = data.copy()
        
        if anonymization_level in ['minimal', 'partial', 'full']:
            # Apply IP address anonymization
            if 'ip_addresses' in anonymized:
                anonymized['ip_addresses'] = [
                    self._anonymize_ip(ip) for ip in anonymized['ip_addresses']
                ]
            
            # Apply email anonymization
            if 'email_addresses' in anonymized:
                anonymized['email_addresses'] = [
                    self._anonymize_email(email) for email in anonymized['email_addresses']
                ]
        
        if anonymization_level in ['partial', 'full']:
            # Remove organization-specific identifiers
            anonymized.pop('organization_id', None)
            anonymized.pop('internal_reference', None)
            
            # Generalize timestamps
            if 'timestamp' in anonymized:
                anonymized['timestamp'] = self._generalize_timestamp(anonymized['timestamp'])
        
        if anonymization_level == 'full':
            # Remove all potentially identifying information
            anonymized.pop('user_id', None)
            anonymized.pop('source_system', None)
            anonymized.pop('detailed_context', None)
        
        return anonymized
    
    def _anonymize_ip(self, ip_address: str) -> str:
        """Anonymize an IP address"""
        parts = ip_address.split('.')
        if len(parts) == 4:
            # IPv4: Replace last octet with XXX
            return f"{parts[0]}.{parts[1]}.{parts[2]}.XXX"
        return "XXX.XXX.XXX.XXX"
    
    def _anonymize_email(self, email: str) -> str:
        """Anonymize an email address"""
        if '@' in email:
            local, domain = email.rsplit('@', 1)
            return f"{local[:2]}***@{domain}"
        return "***@***.***"
    
    def _generalize_timestamp(self, timestamp: str) -> str:
        """Generalize a timestamp to reduce precision"""
        # Convert to date only, removing time information
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.date().isoformat()
        except:
            return timestamp
    
    def validate_organization_access(self, user: CustomUser, 
                                   organization_ids: List[str]) -> Dict[str, bool]:
        """
        Validate user access to multiple organizations.
        
        Args:
            user: User to validate access for
            organization_ids: List of organization IDs to check
            
        Returns:
            dict: Mapping of organization_id -> can_access (bool)
        """
        accessible_org_ids = {
            str(org.id) for org in self.access_control.get_accessible_organizations(user)
        }
        
        return {
            org_id: org_id in accessible_org_ids
            for org_id in organization_ids
        }
    
    def get_organization_trust_metrics(self, user: CustomUser) -> Dict[str, Any]:
        """
        Get trust metrics for user's organization.
        
        Args:
            user: User requesting metrics
            
        Returns:
            dict: Trust metrics and statistics
        """
        self.access_control.require_permission(user, 'can_view_organization_analytics')
        
        org = user.organization
        metrics = {
            'organization': {
                'id': str(org.id),
                'name': org.name
            },
            'trust_relationships': {
                'total': 0,
                'active': 0,
                'pending': 0,
                'by_trust_level': {},
                'by_access_level': {}
            },
            'trust_groups': {
                'member_of': 0,
                'administering': 0
            },
            'data_sharing': {
                'threats_shared': 0,
                'threats_received': 0,
                'anonymization_effectiveness': 0.0
            }
        }
        
        try:
            # Get trust relationship metrics
            relationships = TrustRelationship.objects.filter(
                source_organization=org
            ).select_related('trust_level')
            
            metrics['trust_relationships']['total'] = relationships.count()
            metrics['trust_relationships']['active'] = relationships.filter(
                status='active', is_active=True
            ).count()
            metrics['trust_relationships']['pending'] = relationships.filter(
                status='pending'
            ).count()
            
            # Group by trust level
            for rel in relationships:
                level = rel.trust_level.name
                metrics['trust_relationships']['by_trust_level'][level] = \
                    metrics['trust_relationships']['by_trust_level'].get(level, 0) + 1
            
            # Group by access level
            for rel in relationships:
                access = rel.get_effective_access_level()
                metrics['trust_relationships']['by_access_level'][access] = \
                    metrics['trust_relationships']['by_access_level'].get(access, 0) + 1
            
            # Get trust group metrics
            from core.trust.models import TrustGroupMembership
            memberships = TrustGroupMembership.objects.filter(
                organization=org, is_active=True
            )
            metrics['trust_groups']['member_of'] = memberships.count()
            metrics['trust_groups']['administering'] = memberships.filter(
                membership_type='administrator'
            ).count()
            
        except Exception as e:
            logger.error(f"Error getting trust metrics: {str(e)}")
        
        return metrics
    
    def get_accessible_organizations(self, user: CustomUser) -> List[Organization]:
        """
        Get organizations accessible to the user through trust relationships.
        
        Args:
            user: User to get accessible organizations for
            
        Returns:
            List[Organization]: Accessible organizations
        """
        accessible = [user.organization]  # Always include own organization
        
        try:
            # Get organizations through trust relationships
            relationships = TrustRelationship.objects.filter(
                source_organization=user.organization,
                is_active=True,
                status='active'
            ).select_related('target_organization')
            
            for rel in relationships:
                if rel.target_organization not in accessible:
                    accessible.append(rel.target_organization)
            
            # Get organizations through trust groups
            from core.trust.models import TrustGroupMembership
            memberships = TrustGroupMembership.objects.filter(
                organization=user.organization,
                is_active=True
            ).select_related('trust_group')
            
            for membership in memberships:
                other_memberships = TrustGroupMembership.objects.filter(
                    trust_group=membership.trust_group,
                    is_active=True
                ).exclude(organization=user.organization).select_related('organization')
                
                for other_membership in other_memberships:
                    if other_membership.organization not in accessible:
                        accessible.append(other_membership.organization)
        
        except Exception as e:
            logger.error(f"Error getting accessible organizations: {str(e)}")
        
        return accessible
    
    def calculate_trust_score(self, source_org: Organization, target_org: Organization) -> float:
        """
        Calculate trust score between two organizations.
        
        Args:
            source_org: Source organization
            target_org: Target organization
            
        Returns:
            float: Trust score (0-100)
        """
        try:
            # Get direct relationship
            relationship = TrustRelationship.objects.filter(
                source_organization=source_org,
                target_organization=target_org,
                is_active=True,
                status='active'
            ).first()
            
            if relationship:
                return float(relationship.trust_level.numerical_value)
            
            # Check for mutual trust groups
            from core.trust.models import TrustGroupMembership
            common_groups = TrustGroupMembership.objects.filter(
                organization=source_org,
                is_active=True,
                trust_group__in=TrustGroupMembership.objects.filter(
                    organization=target_org,
                    is_active=True
                ).values_list('trust_group', flat=True)
            )
            
            if common_groups.exists():
                # Return average of common group trust levels
                total_score = 0
                count = 0
                for membership in common_groups:
                    if membership.trust_group.default_trust_level:
                        total_score += membership.trust_group.default_trust_level.numerical_value
                        count += 1
                return float(total_score / count) if count > 0 else 0.0
            
            return 0.0  # No relationship
            
        except Exception as e:
            logger.error(f"Error calculating trust score: {str(e)}")
            return 0.0
    
    def get_trust_context(self, user: CustomUser) -> Dict[str, Any]:
        """
        Get trust context for user including relationships and permissions.
        
        Args:
            user: User to get trust context for
            
        Returns:
            Dict[str, Any]: Trust context data
        """
        try:
            context = {
                'user_organization': {
                    'id': str(user.organization.id),
                    'name': user.organization.name,
                    'domain': user.organization.domain
                },
                'trust_relationships': [],
                'trust_groups': [],
                'accessible_organizations': [],
                'trust_permissions': list(self.access_control.get_user_permissions(user))
            }
            
            # Get trust relationships
            relationships = TrustRelationship.objects.filter(
                source_organization=user.organization,
                is_active=True
            ).select_related('target_organization', 'trust_level')
            
            for rel in relationships:
                context['trust_relationships'].append({
                    'id': str(rel.id),
                    'target_organization': rel.target_organization.name,
                    'trust_level': rel.trust_level.name,
                    'status': rel.status,
                    'access_level': rel.access_level
                })
            
            # Get trust groups
            from core.trust.models import TrustGroupMembership
            memberships = TrustGroupMembership.objects.filter(
                organization=user.organization,
                is_active=True
            ).select_related('trust_group')
            
            for membership in memberships:
                context['trust_groups'].append({
                    'id': str(membership.trust_group.id),
                    'name': membership.trust_group.name,
                    'membership_type': membership.membership_type,
                    'member_count': membership.trust_group.member_count
                })
            
            # Get accessible organizations
            accessible = self.get_accessible_organizations(user)
            context['accessible_organizations'] = [
                {
                    'id': str(org.id),
                    'name': org.name,
                    'domain': org.domain
                }
                for org in accessible
            ]
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting trust context: {str(e)}")
            return {
                'error': 'Failed to get trust context',
                'user_organization': {
                    'id': str(user.organization.id),
                    'name': user.organization.name
                },
                'trust_relationships': [],
                'trust_groups': [],
                'accessible_organizations': [],
                'trust_permissions': []
            }