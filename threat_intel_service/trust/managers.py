"""
Custom managers for trust-related models.
"""
from django.db import models
from django.conf import settings


class TrustRelationshipManager(models.Manager):
    """
    Custom manager for TrustRelationship model.
    """
    
    def get_trust_level(self, source_org, target_org):
        """
        Get the trust level between two organizations.
        
        Args:
            source_org: Source organization
            target_org: Target organization
            
        Returns:
            Trust level as a float (0.0 to 1.0)
        """
        if source_org == target_org:
            # Organizations fully trust themselves
            return 1.0
            
        try:
            relationship = self.get(
                source_organization=source_org,
                target_organization=target_org
            )
            return relationship.trust_level
        except self.model.DoesNotExist:
            # No relationship exists
            return 0.0
    
    def get_anonymization_strategy(self, source_org, target_org):
        """
        Get the anonymization strategy to use for sharing between two organizations.
        
        Args:
            source_org: Source organization
            target_org: Target organization
            
        Returns:
            Anonymization strategy name
        """
        if source_org == target_org:
            # No anonymization needed for own data
            return 'none'
            
        try:
            relationship = self.get(
                source_organization=source_org,
                target_organization=target_org
            )
            return relationship.anonymization_strategy
        except self.model.DoesNotExist:
            # Default to full anonymization if no relationship exists
            return 'full'
    
    def get_trusted_organizations(self, organization, min_trust_level=0.0):
        """
        Get all organizations trusted by the given organization.
        
        Args:
            organization: The organization
            min_trust_level: Minimum trust level (0.0 to 1.0)
            
        Returns:
            QuerySet of trusted organizations
        """
        relationships = self.filter(
            source_organization=organization,
            trust_level__gte=min_trust_level
        )
        
        # Get target organizations
        from core.models import Organization
        org_ids = relationships.values_list('target_organization', flat=True)
        
        return Organization.objects.filter(id__in=org_ids)
    
    def get_trusting_organizations(self, organization, min_trust_level=0.0):
        """
        Get all organizations that trust the given organization.
        
        Args:
            organization: The organization
            min_trust_level: Minimum trust level (0.0 to 1.0)
            
        Returns:
            QuerySet of trusting organizations
        """
        relationships = self.filter(
            target_organization=organization,
            trust_level__gte=min_trust_level
        )
        
        # Get source organizations
        from core.models import Organization
        org_ids = relationships.values_list('source_organization', flat=True)
        
        return Organization.objects.filter(id__in=org_ids)


class TrustGroupManager(models.Manager):
    """
    Custom manager for TrustGroup model.
    """
    
    def get_groups_for_organization(self, organization):
        """
        Get all groups that an organization is a member of.
        
        Args:
            organization: The organization
            
        Returns:
            QuerySet of groups
        """
        from trust.models import TrustGroupMembership
        
        # Get group IDs from memberships
        memberships = TrustGroupMembership.objects.filter(organization=organization)
        group_ids = memberships.values_list('trust_group', flat=True)
        
        return self.filter(id__in=group_ids)
    
    def apply_group_trust(self, group, organization):
        """
        Apply trust relationships from a group to an organization.
        
        Args:
            group: The trust group
            organization: The organization to establish trust relationships from
            
        Returns:
            Tuple of (created_count, updated_count)
        """
        from trust.models import TrustRelationship, TrustGroupMembership
        
        # Get all members of the group
        memberships = TrustGroupMembership.objects.filter(trust_group=group)
        
        created_count = 0
        updated_count = 0
        
        for membership in memberships:
            target_org = membership.organization
            
            # Skip if this is the same organization
            if target_org == organization:
                continue
                
            # Check if relationship already exists
            existing = TrustRelationship.objects.filter(
                source_organization=organization,
                target_organization=target_org
            ).first()
            
            if existing:
                # Update existing relationship
                existing.trust_level_name = group.default_trust_level_name
                existing.trust_level = group.default_trust_level
                existing.save()
                updated_count += 1
            else:
                # Create new relationship
                TrustRelationship.objects.create(
                    source_organization=organization,
                    target_organization=target_org,
                    trust_level_name=group.default_trust_level_name,
                    trust_level=group.default_trust_level
                )
                created_count += 1
        
        return (created_count, updated_count)


class TrustGroupMembershipManager(models.Manager):
    """
    Custom manager for TrustGroupMembership model.
    """
    
    def get_members(self, group):
        """
        Get all members of a trust group.
        
        Args:
            group: The trust group
            
        Returns:
            QuerySet of organizations
        """
        from core.models import Organization
        
        # Get organization IDs from memberships
        memberships = self.filter(trust_group=group)
        org_ids = memberships.values_list('organization', flat=True)
        
        return Organization.objects.filter(id__in=org_ids)
    
    def get_groups(self, organization):
        """
        Get all groups that an organization is a member of.
        
        Args:
            organization: The organization
            
        Returns:
            QuerySet of groups
        """
        from trust.models import TrustGroup
        
        # Get group IDs from memberships
        memberships = self.filter(organization=organization)
        group_ids = memberships.values_list('trust_group', flat=True)
        
        return TrustGroup.objects.filter(id__in=group_ids)