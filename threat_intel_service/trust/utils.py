"""
Utility functions for trust-based sharing.
"""
from typing import Dict, List, Any, Union, Optional
from django.conf import settings

from core.models import Organization, STIXObject, Collection
from trust.models import TrustRelationship, TrustGroup, TrustGroupMembership
from anonymization.strategy import AnonymizationStrategyFactory


def get_trust_level(source_org: Organization, target_org: Organization) -> float:
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
        relationship = TrustRelationship.objects.get(
            source_organization=source_org,
            target_organization=target_org
        )
        return relationship.trust_level
    except TrustRelationship.DoesNotExist:
        # No relationship exists
        return 0.0


def get_anonymization_strategy(source_org: Organization, target_org: Organization) -> str:
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
        relationship = TrustRelationship.objects.get(
            source_organization=source_org,
            target_organization=target_org
        )
        return relationship.anonymization_strategy
    except TrustRelationship.DoesNotExist:
        # Default to full anonymization if no relationship exists
        return 'full'


def filter_by_trust_level(stix_objects: List[STIXObject], 
                         requesting_org: Organization,
                         min_trust_level: float = 0.0) -> List[STIXObject]:
    """
    Filter STIX objects based on trust level.
    
    Args:
        stix_objects: List of STIX objects
        requesting_org: Organization requesting the objects
        min_trust_level: Minimum trust level required
        
    Returns:
        Filtered list of STIX objects
    """
    filtered_objects = []
    
    for obj in stix_objects:
        source_org = obj.source_organization
        trust_level = get_trust_level(source_org, requesting_org)
        
        if trust_level >= min_trust_level:
            filtered_objects.append(obj)
    
    return filtered_objects


def apply_anonymization(stix_object: STIXObject, 
                       requesting_org: Organization) -> Dict[str, Any]:
    """
    Apply anonymization to a STIX object based on trust relationship.
    
    Args:
        stix_object: STIX object to anonymize
        requesting_org: Organization requesting the object
        
    Returns:
        Anonymized STIX object as dictionary
    """
    source_org = stix_object.source_organization
    
    # No anonymization needed for own objects
    if source_org == requesting_org:
        return stix_object.to_stix()
    
    # Get trust level and strategy
    trust_level = get_trust_level(source_org, requesting_org)
    strategy_name = get_anonymization_strategy(source_org, requesting_org)
    
    # Get strategy and apply anonymization
    strategy = AnonymizationStrategyFactory.get_strategy(strategy_name)
    anonymized = strategy.anonymize(stix_object.to_stix(), trust_level)
    
    return anonymized


def get_accessible_collections(requesting_org: Organization) -> List[Collection]:
    """
    Get all collections accessible to an organization.
    
    Args:
        requesting_org: Organization requesting access
        
    Returns:
        List of accessible collections
    """
    # Get collections owned by the organization
    owned_collections = Collection.objects.filter(owner=requesting_org)
    
    # Get collections shared with the organization based on trust relationships
    trusted_orgs = TrustRelationship.objects.filter(
        source_organization=requesting_org
    ).values_list('target_organization', flat=True)
    
    shared_collections = Collection.objects.filter(
        owner__in=trusted_orgs,
        can_read=True
    )
    
    # Combine and deduplicate collections
    all_collections = list(owned_collections)
    for collection in shared_collections:
        if collection not in all_collections:
            all_collections.append(collection)
    
    return all_collections


def apply_trust_group(group: TrustGroup, organization: Organization) -> Dict[str, int]:
    """
    Apply trust relationships from a group to an organization.
    
    Args:
        group: The trust group
        organization: The organization to establish trust relationships from
        
    Returns:
        Dictionary with counts of created and updated relationships
    """
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
    
    return {
        'created_count': created_count,
        'updated_count': updated_count
    }


def get_effective_trust_level(source_org: Organization, 
                             target_org: Organization) -> Dict[str, Any]:
    """
    Get the effective trust level and details between two organizations.
    
    Args:
        source_org: Source organization
        target_org: Target organization
        
    Returns:
        Dictionary with trust details
    """
    if source_org == target_org:
        return {
            'trust_level': 1.0,
            'trust_level_name': 'high',
            'anonymization_strategy': 'none',
            'direct_relationship': True,
            'relationship_type': 'self',
            'effectiveness_score': 1.0
        }
    
    try:
        # Check for direct relationship
        relationship = TrustRelationship.objects.get(
            source_organization=source_org,
            target_organization=target_org
        )
        
        # Get anonymization effectiveness
        strategy = AnonymizationStrategyFactory.get_strategy(relationship.anonymization_strategy)
        effectiveness = strategy.get_effectiveness_score()
        
        return {
            'trust_level': relationship.trust_level,
            'trust_level_name': relationship.trust_level_name,
            'anonymization_strategy': relationship.anonymization_strategy,
            'direct_relationship': True,
            'relationship_type': 'direct',
            'effectiveness_score': effectiveness
        }
        
    except TrustRelationship.DoesNotExist:
        # No direct relationship exists
        
        # Check for shared group membership
        source_groups = TrustGroup.objects.filter(
            memberships__organization=source_org
        )
        
        target_groups = TrustGroup.objects.filter(
            memberships__organization=target_org
        )
        
        # Find common groups
        common_groups = set(source_groups) & set(target_groups)
        
        if common_groups:
            # Use highest trust level from common groups
            highest_trust = 0.0
            highest_group = None
            
            for group in common_groups:
                if group.default_trust_level > highest_trust:
                    highest_trust = group.default_trust_level
                    highest_group = group
            
            # Get anonymization effectiveness
            strategy_name = 'partial'
            if highest_trust >= 0.8:
                strategy_name = 'none'
            elif highest_trust < 0.4:
                strategy_name = 'full'
                
            strategy = AnonymizationStrategyFactory.get_strategy(strategy_name)
            effectiveness = strategy.get_effectiveness_score()
            
            return {
                'trust_level': highest_trust,
                'trust_level_name': highest_group.default_trust_level_name,
                'anonymization_strategy': strategy_name,
                'direct_relationship': False,
                'relationship_type': 'group',
                'group_name': highest_group.name,
                'effectiveness_score': effectiveness
            }
        
        # No relationship at all
        return {
            'trust_level': 0.0,
            'trust_level_name': 'none',
            'anonymization_strategy': 'full',
            'direct_relationship': False,
            'relationship_type': 'none',
            'effectiveness_score': 0.8  # Full anonymization preserves ~80% value
        }