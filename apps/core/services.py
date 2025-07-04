"""
Integration service that connects UserManagement and TrustManagement
Implements the business logic for the integrated CRISP system
"""
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.user_management.models import CustomUser, Organization, InvitationToken
from apps.trust_management.models import TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership, TrustLog


class CRISPIntegrationService:
    """
    Service that handles integration between User Management and Trust Management
    Implements SRS functional requirements for integrated system
    """
    
    @staticmethod
    def create_organization_with_trust_setup(
        name: str,
        domain: str,
        contact_email: str,
        admin_user_data: Dict,
        institution_type: str = 'university',
        default_trust_level: str = 'public'
    ) -> Organization:
        """
        Create an organization with integrated trust management setup
        Implements R1.3.1 - System Administrators register new client Institutions
        """
        try:
            with transaction.atomic():
                # Create organization
                organization = Organization.objects.create(
                    name=name,
                    domain=domain,
                    contact_email=contact_email,
                    institution_type=institution_type,
                    trust_level_default=default_trust_level,
                    is_bluevision_client=True
                )
                
                # Create admin user
                admin_user = CustomUser.objects.create_user(
                    username=admin_user_data['username'],
                    email=admin_user_data['email'],
                    password=admin_user_data['password'],
                    organization=organization,
                    role='publisher',
                    is_organization_admin=True,
                    first_name=admin_user_data.get('first_name', ''),
                    last_name=admin_user_data.get('last_name', ''),
                    terms_accepted=True,
                    terms_accepted_date=timezone.now()
                )
                
                # Log organization creation
                TrustLog.objects.create(
                    action='organization_created',
                    source_organization=organization.id,
                    user=admin_user.username,
                    details={
                        'organization_name': name,
                        'institution_type': institution_type,
                        'admin_user': admin_user.email
                    }
                )
                
                return organization
                
        except Exception as e:
            raise ValidationError(f"Failed to create organization: {str(e)}")
    
    @staticmethod
    def invite_user_to_organization(
        organization: Organization,
        inviting_user: CustomUser,
        email: str,
        role: str = 'viewer'
    ) -> InvitationToken:
        """
        Invite a user to join an organization
        Implements R1.2.2 - Institution Publishers invite users via email
        """
        if not inviting_user.can_manage_organization():
            raise ValidationError("User does not have permission to invite users")
        
        if inviting_user.organization != organization:
            raise ValidationError("User can only invite to their own organization")
        
        # Create invitation token
        invitation = InvitationToken.objects.create(
            organization=organization,
            invited_by=inviting_user,
            email=email,
            role=role,
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Log invitation
        TrustLog.objects.create(
            action='user_invited',
            source_organization=organization.id,
            user=inviting_user.username,
            details={
                'invited_email': email,
                'role': role,
                'invitation_token': str(invitation.token)
            }
        )
        
        return invitation
    
    @staticmethod
    def create_trust_relationship(
        source_org: Organization,
        target_org: Organization,
        trust_level_name: str,
        relationship_type: str = 'bilateral',
        created_by_user: CustomUser = None
    ) -> TrustRelationship:
        """
        Create a trust relationship between organizations
        Implements R4.1.4 - Enable bilateral trust agreements
        """
        if source_org == target_org:
            raise ValidationError("Cannot create trust relationship with same organization")
        
        try:
            trust_level = TrustLevel.objects.get(name=trust_level_name, is_active=True)
        except TrustLevel.DoesNotExist:
            raise ValidationError(f"Trust level '{trust_level_name}' not found")
        
        # Check if relationship already exists
        existing = TrustRelationship.objects.filter(
            source_organization=source_org.id,
            target_organization=target_org.id,
            status__in=['pending', 'active']
        ).first()
        
        if existing:
            raise ValidationError("Trust relationship already exists between these organizations")
        
        created_by = created_by_user.username if created_by_user else 'system'
        
        with transaction.atomic():
            relationship = TrustRelationship.objects.create(
                source_organization=source_org.id,
                target_organization=target_org.id,
                trust_level=trust_level,
                relationship_type=relationship_type,
                created_by=created_by,
                last_modified_by=created_by,
                approved_by_source=True if relationship_type == 'community' else False
            )
            
            # Log relationship creation
            TrustLog.objects.create(
                action='relationship_created',
                source_organization=source_org.id,
                target_organization=target_org.id,
                trust_relationship=relationship,
                user=created_by,
                details={
                    'trust_level': trust_level_name,
                    'relationship_type': relationship_type
                }
            )
            
            return relationship
    
    @staticmethod
    def get_user_accessible_intelligence_sources(
        user: CustomUser,
        intelligence_type: str = None
    ) -> List[Dict]:
        """
        Get threat intelligence sources accessible to a user based on trust relationships
        Implements R4.2.1 - Filter shared intelligence based on trust relationships
        """
        if not user.organization:
            return []
        
        # Get all active trust relationships for user's organization
        relationships = TrustRelationship.objects.filter(
            models.Q(source_organization=user.organization.id) |
            models.Q(target_organization=user.organization.id),
            status='active'
        ).select_related('trust_level')
        
        accessible_sources = []
        
        for relationship in relationships:
            # Determine if user's org is source or target
            if str(relationship.source_organization) == str(user.organization.id):
                partner_org_id = relationship.target_organization
            else:
                partner_org_id = relationship.source_organization
            
            try:
                partner_org = Organization.objects.get(id=partner_org_id)
                accessible_sources.append({
                    'organization': partner_org,
                    'trust_level': relationship.trust_level.level,
                    'anonymization_level': relationship.trust_level.default_anonymization_level,
                    'access_level': relationship.trust_level.default_access_level,
                    'relationship_type': relationship.relationship_type
                })
            except Organization.DoesNotExist:
                continue
        
        return accessible_sources
    
    @staticmethod
    def can_user_access_intelligence(
        user: CustomUser,
        intelligence_owner_org_id: str,
        intelligence_type: str = None,
        required_access_level: str = 'read'
    ) -> Tuple[bool, str, Optional[TrustRelationship]]:
        """
        Check if a user can access specific intelligence based on trust relationships
        Implements R4.2.1 - Filter shared intelligence based on trust relationships
        """
        if not user.organization:
            return False, "User has no organization", None
        
        if str(user.organization.id) == intelligence_owner_org_id:
            return True, "User's own organization", None
        
        # Check for active trust relationship
        relationship = TrustRelationship.objects.filter(
            models.Q(
                source_organization=user.organization.id,
                target_organization=intelligence_owner_org_id
            ) |
            models.Q(
                source_organization=intelligence_owner_org_id,
                target_organization=user.organization.id
            ),
            status='active'
        ).select_related('trust_level').first()
        
        if not relationship:
            return False, "No trust relationship exists", None
        
        # Check access level
        access_level_hierarchy = {
            'read': 1,
            'contribute': 2,
            'admin': 3
        }
        
        effective_access = relationship.trust_level.default_access_level
        required_level = access_level_hierarchy.get(required_access_level, 1)
        effective_level = access_level_hierarchy.get(effective_access, 1)
        
        if effective_level >= required_level:
            return True, f"Access granted via {relationship.trust_level.name}", relationship
        else:
            return False, f"Insufficient access level: {effective_access} < {required_access_level}", relationship
    
    @staticmethod
    def get_organization_trust_dashboard_data(organization: Organization) -> Dict:
        """
        Get comprehensive trust dashboard data for an organization
        Implements dashboard requirements for trust relationship management
        """
        # Get trust relationships
        relationships = TrustRelationship.objects.filter(
            models.Q(source_organization=organization.id) |
            models.Q(target_organization=organization.id)
        ).select_related('trust_level')
        
        # Get trust groups
        group_memberships = TrustGroupMembership.objects.filter(
            organization=organization.id,
            is_active=True
        ).select_related('trust_group')
        
        # Calculate statistics
        active_relationships = relationships.filter(status='active')
        pending_relationships = relationships.filter(status='pending')
        
        # Get partner organizations
        partner_org_ids = set()
        for rel in active_relationships:
            if str(rel.source_organization) == str(organization.id):
                partner_org_ids.add(rel.target_organization)
            else:
                partner_org_ids.add(rel.source_organization)
        
        partner_orgs = Organization.objects.filter(id__in=partner_org_ids)
        
        return {
            'organization': organization,
            'relationships': {
                'total': relationships.count(),
                'active': active_relationships.count(),
                'pending': pending_relationships.count(),
                'by_trust_level': {
                    level: active_relationships.filter(trust_level__level=level).count()
                    for level in ['public', 'trusted', 'restricted']
                }
            },
            'trust_groups': {
                'total': group_memberships.count(),
                'groups': [membership.trust_group for membership in group_memberships]
            },
            'partners': list(partner_orgs),
            'sharing_stats': {
                'can_share_with': partner_orgs.count(),
                'trust_groups': group_memberships.count()
            }
        }
    
    @staticmethod
    def approve_trust_relationship(
        relationship: TrustRelationship,
        approving_org: Organization,
        approving_user: CustomUser
    ) -> bool:
        """
        Approve a trust relationship on behalf of an organization
        Implements bilateral approval process
        """
        if not approving_user.can_manage_organization():
            raise ValidationError("User does not have permission to approve trust relationships")
        
        if approving_user.organization != approving_org:
            raise ValidationError("User can only approve for their own organization")
        
        # Check if organization is part of this relationship
        if str(approving_org.id) not in [str(relationship.source_organization), str(relationship.target_organization)]:
            raise ValidationError("Organization is not part of this trust relationship")
        
        with transaction.atomic():
            relationship.approve(approving_org.id, approving_user.username)
            
            # Log approval
            TrustLog.objects.create(
                action='relationship_approved',
                source_organization=relationship.source_organization,
                target_organization=relationship.target_organization,
                trust_relationship=relationship,
                user=approving_user.username,
                details={
                    'approving_organization': str(approving_org.id),
                    'is_fully_approved': relationship.is_fully_approved()
                }
            )
            
            return relationship.is_fully_approved()


# Import Q for use in the service
from django.db import models
