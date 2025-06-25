"""
Trust Management Utility Functions

Common utility functions and helpers for trust management operations.
"""

import uuid
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from django.utils import timezone
from datetime import timedelta, datetime

from .models import TrustRelationship, TrustGroup, TrustLevel


def generate_trust_relationship_id() -> str:
    """
    Generate a unique ID for trust relationships.
    
    Returns:
        String UUID for the relationship
    """
    return str(uuid.uuid4())


def validate_organization_uuid(org_id: str) -> bool:
    """
    Validate that a string is a valid UUID for an organization.
    
    Args:
        org_id: Organization ID string to validate
        
    Returns:
        Boolean indicating if the UUID is valid
    """
    try:
        uuid.UUID(org_id)
        return True
    except (ValueError, TypeError):
        return False


def calculate_trust_score(
    trust_level: TrustLevel,
    relationship_age_days: int,
    activity_score: float = 1.0
) -> float:
    """
    Calculate a composite trust score based on multiple factors.
    
    Args:
        trust_level: TrustLevel object
        relationship_age_days: Age of the relationship in days
        activity_score: Activity score (0.0 to 1.0) based on sharing history
        
    Returns:
        Composite trust score (0.0 to 100.0)
    """
    base_score = trust_level.numerical_value
    
    # Age factor (relationships gain trust over time, up to 10% boost)
    age_factor = min(relationship_age_days / 365.0, 1.0) * 0.1
    
    # Activity factor (active sharing increases trust, up to 5% boost)
    activity_factor = activity_score * 0.05
    
    # Calculate final score
    final_score = base_score * (1 + age_factor + activity_factor)
    
    return min(final_score, 100.0)


def get_trust_relationship_summary(relationship: TrustRelationship) -> Dict[str, Any]:
    """
    Get a comprehensive summary of a trust relationship.
    
    Args:
        relationship: TrustRelationship object
        
    Returns:
        Dictionary with relationship summary information
    """
    now = timezone.now()
    
    return {
        'id': str(relationship.id),
        'source_organization': relationship.source_organization,
        'target_organization': relationship.target_organization,
        'trust_level': {
            'name': relationship.trust_level.name,
            'level': relationship.trust_level.level,
            'numerical_value': relationship.trust_level.numerical_value
        },
        'relationship_type': relationship.relationship_type,
        'status': relationship.status,
        'is_effective': relationship.is_effective,
        'is_bilateral': relationship.is_bilateral,
        'approval_status': {
            'source_approved': relationship.approved_by_source,
            'target_approved': relationship.approved_by_target,
            'fully_approved': relationship.is_fully_approved
        },
        'access_control': {
            'access_level': relationship.get_effective_access_level(),
            'anonymization_level': relationship.get_effective_anonymization_level()
        },
        'validity': {
            'valid_from': relationship.valid_from,
            'valid_until': relationship.valid_until,
            'is_expired': relationship.is_expired,
            'days_remaining': (relationship.valid_until - now).days if relationship.valid_until else None
        },
        'timestamps': {
            'created_at': relationship.created_at,
            'activated_at': relationship.activated_at,
            'revoked_at': relationship.revoked_at
        },
        'metadata': {
            'created_by': relationship.created_by,
            'last_modified_by': relationship.last_modified_by,
            'notes': relationship.notes
        }
    }


def get_trust_group_summary(group: TrustGroup) -> Dict[str, Any]:
    """
    Get a comprehensive summary of a trust group.
    
    Args:
        group: TrustGroup object
        
    Returns:
        Dictionary with group summary information
    """
    member_count = group.get_member_count()
    
    return {
        'id': str(group.id),
        'name': group.name,
        'description': group.description,
        'group_type': group.group_type,
        'is_public': group.is_public,
        'requires_approval': group.requires_approval,
        'default_trust_level': {
            'name': group.default_trust_level.name,
            'level': group.default_trust_level.level,
            'numerical_value': group.default_trust_level.numerical_value
        },
        'membership': {
            'member_count': member_count,
            'administrators': group.administrators
        },
        'policies': group.group_policies,
        'status': {
            'is_active': group.is_active
        },
        'timestamps': {
            'created_at': group.created_at,
            'updated_at': group.updated_at
        },
        'metadata': {
            'created_by': group.created_by
        }
    }


def anonymize_organization_id(org_id: str, salt: str = None) -> str:
    """
    Create an anonymized version of an organization ID.
    
    Args:
        org_id: Organization UUID to anonymize
        salt: Optional salt for hashing
        
    Returns:
        Anonymized organization identifier
    """
    if salt is None:
        salt = "crisp_trust_anonymization"
    
    # Create a hash of the org ID with salt
    hash_input = f"{org_id}{salt}".encode('utf-8')
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    
    # Return first 16 characters as anonymized ID
    return f"anon_{hash_digest[:16]}"


def calculate_sharing_statistics(organization: str, days: int = 30) -> Dict[str, int]:
    """
    Calculate sharing statistics for an organization.
    
    Args:
        organization: Organization UUID
        days: Number of days to look back
        
    Returns:
        Dictionary with sharing statistics
    """
    from .models import TrustLog
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Get sharing-related log entries
    sharing_logs = TrustLog.objects.filter(
        source_organization=organization,
        timestamp__gte=cutoff_date,
        action__in=['intelligence_shared', 'access_granted']
    )
    
    access_logs = TrustLog.objects.filter(
        source_organization=organization,
        timestamp__gte=cutoff_date,
        action='intelligence_accessed'
    )
    
    return {
        'intelligence_shared': sharing_logs.filter(action='intelligence_shared').count(),
        'access_granted': sharing_logs.filter(action='access_granted').count(),
        'intelligence_accessed': access_logs.count(),
        'total_sharing_activities': sharing_logs.count(),
        'period_days': days
    }


def get_trust_network_analysis(organization: str) -> Dict[str, Any]:
    """
    Analyze the trust network for an organization.
    
    Args:
        organization: Organization UUID
        
    Returns:
        Dictionary with network analysis results
    """
    from django.db.models import Q
    
    # Get all relationships involving this organization
    relationships = TrustRelationship.objects.filter(
        Q(source_organization=organization) | Q(target_organization=organization),
        is_active=True,
        status='active'
    ).select_related('trust_level')
    
    # Analyze trust levels
    trust_levels = {}
    total_relationships = len(relationships)
    effective_relationships = 0
    
    for rel in relationships:
        level = rel.trust_level.level
        trust_levels[level] = trust_levels.get(level, 0) + 1
        
        if rel.is_effective:
            effective_relationships += 1
    
    # Calculate network metrics
    return {
        'organization': organization,
        'total_relationships': total_relationships,
        'effective_relationships': effective_relationships,
        'effectiveness_ratio': effective_relationships / max(total_relationships, 1),
        'trust_level_distribution': trust_levels,
        'network_reach': len(set(
            rel.target_organization if rel.source_organization == organization 
            else rel.source_organization
            for rel in relationships if rel.is_effective
        )),
        'analysis_timestamp': timezone.now()
    }


def export_trust_configuration(format: str = 'json') -> str:
    """
    Export the current trust configuration.
    
    Args:
        format: Export format ('json' or 'csv')
        
    Returns:
        Serialized trust configuration
    """
    if format not in ['json', 'csv']:
        raise ValueError("Format must be 'json' or 'csv'")
    
    # Get all trust levels
    trust_levels = []
    for level in TrustLevel.objects.filter(is_active=True):
        trust_levels.append({
            'name': level.name,
            'level': level.level,
            'numerical_value': level.numerical_value,
            'default_anonymization_level': level.default_anonymization_level,
            'default_access_level': level.default_access_level,
            'sharing_policies': level.sharing_policies,
            'is_system_default': level.is_system_default
        })
    
    # Get all trust groups
    trust_groups = []
    for group in TrustGroup.objects.filter(is_active=True):
        trust_groups.append({
            'name': group.name,
            'description': group.description,
            'group_type': group.group_type,
            'is_public': group.is_public,
            'requires_approval': group.requires_approval,
            'default_trust_level': group.default_trust_level.name,
            'group_policies': group.group_policies,
            'administrators': group.administrators
        })
    
    config = {
        'export_timestamp': timezone.now().isoformat(),
        'trust_levels': trust_levels,
        'trust_groups': trust_groups,
        'version': '1.0'
    }
    
    if format == 'json':
        return json.dumps(config, indent=2, default=str)
    else:
        # CSV format would require more complex serialization
        # For now, return JSON
        return json.dumps(config, indent=2, default=str)


def validate_trust_configuration(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a trust configuration before import.
    
    Args:
        config_data: Configuration data to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    required_fields = ['trust_levels', 'trust_groups']
    for field in required_fields:
        if field not in config_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate trust levels
    if 'trust_levels' in config_data:
        for i, level in enumerate(config_data['trust_levels']):
            if 'name' not in level:
                errors.append(f"Trust level {i}: Missing name")
            if 'numerical_value' not in level:
                errors.append(f"Trust level {i}: Missing numerical_value")
            elif not (0 <= level['numerical_value'] <= 100):
                errors.append(f"Trust level {i}: numerical_value must be 0-100")
    
    # Validate trust groups
    if 'trust_groups' in config_data:
        for i, group in enumerate(config_data['trust_groups']):
            if 'name' not in group:
                errors.append(f"Trust group {i}: Missing name")
            if 'default_trust_level' not in group:
                errors.append(f"Trust group {i}: Missing default_trust_level")
    
    return len(errors) == 0, errors


def format_trust_relationship_for_display(relationship: TrustRelationship) -> str:
    """
    Format a trust relationship for human-readable display.
    
    Args:
        relationship: TrustRelationship object
        
    Returns:
        Formatted string representation
    """
    source_short = relationship.source_organization[:8]
    target_short = relationship.target_organization[:8]
    
    status_emoji = {
        'pending': '⏳',
        'active': '✅',
        'suspended': '⏸️',
        'revoked': '❌',
        'expired': '🔒'
    }.get(relationship.status, '❓')
    
    trust_emoji = {
        'none': '🚫',
        'low': '🟡',
        'medium': '🟠',
        'high': '🟢',
        'complete': '💎'
    }.get(relationship.trust_level.level, '❓')
    
    return (
        f"{status_emoji} {source_short}...→{target_short}... "
        f"{trust_emoji} {relationship.trust_level.name} "
        f"({relationship.relationship_type})"
    )