"""
Trust Management Utility Functions

Utility functions for trust management operations including anonymization,
trust score calculation, relationship summaries, and configuration management.
"""

import uuid
import hashlib
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Avg, Count, Q
import logging

logger = logging.getLogger(__name__)


def validate_organization_uuid(org_uuid: str) -> bool:
    """
    Validate organization UUID format.
    
    Args:
        org_uuid: Organization UUID string to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid_obj = uuid.UUID(org_uuid)
        return str(uuid_obj) == org_uuid
    except (ValueError, TypeError):
        return False


def anonymize_organization_id(org_id: str, salt: str = None) -> str:
    """
    Anonymize organization ID using SHA-256 hashing.
    
    Args:
        org_id: Organization ID to anonymize
        salt: Optional salt for hashing
        
    Returns:
        Anonymized organization ID
    """
    if salt is None:
        salt = "trust_management_default_salt"
    
    # Combine org_id with salt and hash
    combined = f"{org_id}:{salt}"
    hash_obj = hashlib.sha256(combined.encode())
    return f"anon_{hash_obj.hexdigest()[:16]}"


def generate_trust_relationship_id(source_org: str = None, target_org: str = None) -> str:
    """
    Generate a trust relationship ID.
    
    If source_org and target_org are provided, generates a deterministic ID.
    If not provided, generates a random UUID.
    
    Args:
        source_org: Source organization ID (optional)
        target_org: Target organization ID (optional)
        
    Returns:
        Generated relationship ID
    """
    if source_org and target_org:
        # Create deterministic ID based on organizations (sorted for consistency)
        orgs = sorted([source_org, target_org])
        combined = f"{orgs[0]}:{orgs[1]}"
        hash_obj = hashlib.md5(combined.encode())
        return f"trust_{hash_obj.hexdigest()[:16]}"
    else:
        # Generate random UUID when no organizations provided
        return str(uuid.uuid4())


def calculate_trust_score(base_score, relationship_age_days: int = 0, 
                         activity_factor: float = 0.0, max_score: int = 100) -> float:
    """
    Calculate dynamic trust score based on various factors.
    
    Args:
        base_score: Base trust score (can be int or TrustLevel object)
        relationship_age_days: Age of relationship in days
        activity_factor: Activity factor (0.0 to 1.0)
        max_score: Maximum possible score
        
    Returns:
        Calculated trust score
    """
    # Extract numerical value if base_score is a TrustLevel object
    if hasattr(base_score, 'numerical_value'):
        base_value = base_score.numerical_value
    else:
        base_value = base_score
    
    # Age factor calculation (0 to 0.1 max bonus)
    age_factor = min(0.1, relationship_age_days / 365.0 * 0.1)
    
    # Activity factor (provided as parameter, max 0.05)
    activity_factor = min(0.05, activity_factor * 0.05)
    
    # Calculate score with multiplicative factors
    score = base_value * (1 + age_factor + activity_factor)
    
    # Cap at maximum score
    return min(score, max_score)


def get_trust_relationship_summary(relationship) -> Dict[str, Any]:
    """
    Get a comprehensive summary of a trust relationship.
    
    Args:
        relationship: TrustRelationship instance
        
    Returns:
        Dictionary containing relationship summary
    """
    try:
        summary = {
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
            'is_bilateral': relationship.is_bilateral,
            'anonymization_level': relationship.anonymization_level,
            'access_level': relationship.access_level,
            'created_at': relationship.created_at.isoformat(),
            'created_by': relationship.created_by,
            'is_active': relationship.is_active
        }
        
        # Add structured access control information
        summary['access_control'] = {
            'access_level': getattr(relationship, 'access_level', 'read'),
            'anonymization_level': getattr(relationship, 'anonymization_level', 'partial')
        }
        
        # Add validity information
        valid_from = getattr(relationship, 'valid_from', relationship.created_at)
        valid_until = getattr(relationship, 'valid_until', None)
        current_time = timezone.now()
        
        summary['validity'] = {
            'valid_from': valid_from.isoformat() if valid_from else None,
            'valid_until': valid_until.isoformat() if valid_until else None,
            'is_expired': valid_until and current_time > valid_until,
            'days_remaining': (valid_until - current_time).days if valid_until else None
        }
        
        # Add timestamps
        summary['timestamps'] = {
            'created_at': relationship.created_at.isoformat(),
            'activated_at': getattr(relationship, 'activated_at', None)
        }
        if summary['timestamps']['activated_at']:
            summary['timestamps']['activated_at'] = summary['timestamps']['activated_at'].isoformat()
        
        # Add metadata
        summary['metadata'] = {
            'created_by': relationship.created_by,
            'notes': getattr(relationship, 'notes', '')
        }
        
        # Add approval info if available
        if hasattr(relationship, 'approved_by_source'):
            summary['approved_by_source'] = relationship.approved_by_source
            summary['approved_by_target'] = relationship.approved_by_target
            
            # Add structured approval status
            summary['approval_status'] = {
                'source_approved': getattr(relationship, 'approved_by_source', False),
                'target_approved': getattr(relationship, 'approved_by_target', False),
                'fully_approved': (getattr(relationship, 'approved_by_source', False) and 
                                 getattr(relationship, 'approved_by_target', False))
            }
        
        # Legacy fields for backward compatibility
        if hasattr(relationship, 'valid_until') and relationship.valid_until:
            summary['expires_at'] = relationship.valid_until.isoformat()
            summary['days_until_expiration'] = (relationship.valid_until - timezone.now()).days
        else:
            summary['expires_at'] = None
            summary['days_until_expiration'] = None
        
        return summary
        
    except Exception as e:
        logger.error(f"Error creating relationship summary: {e}")
        return {'error': str(e)}


def get_trust_group_summary(group) -> Dict[str, Any]:
    """
    Get a comprehensive summary of a trust group.
    
    Args:
        group: TrustGroup instance
        
    Returns:
        Dictionary containing group summary
    """
    try:
        summary = {
            'id': str(group.id),
            'name': group.name,
            'description': group.description,
            'group_type': group.group_type,
            'is_public': group.is_public,
            'requires_approval': getattr(group, 'requires_approval', False),
            'created_at': group.created_at.isoformat(),
            'created_by': group.created_by,
            'is_active': group.is_active
        }
        
        # Add member count
        member_count = 0
        if hasattr(group, 'get_member_count'):
            member_count = group.get_member_count()
        elif hasattr(group, 'member_count'):
            member_count = group.member_count
        else:
            try:
                from .models.trust_models import TrustGroupMembership
                member_count = TrustGroupMembership.objects.filter(
                    trust_group=group, 
                    is_active=True
                ).count()
            except:
                member_count = 0
        
        # Add structured membership information
        summary['membership'] = {
            'member_count': member_count,
            'administrators': getattr(group, 'administrators', [])
        }
        
        # Add default trust level info
        if group.default_trust_level:
            summary['default_trust_level'] = {
                'name': group.default_trust_level.name,
                'level': group.default_trust_level.level,
                'numerical_value': group.default_trust_level.numerical_value
            }
        
        # Add policies
        summary['policies'] = getattr(group, 'group_policies', {})
        
        # Add status information
        summary['status'] = {
            'is_active': getattr(group, 'is_active', True)
        }
        
        # Add timestamps
        summary['timestamps'] = {
            'created_at': group.created_at.isoformat(),
            'updated_at': getattr(group, 'updated_at', group.created_at).isoformat()
        }
        
        # Add metadata
        summary['metadata'] = {
            'created_by': group.created_by
        }
        
        # Legacy fields for backward compatibility
        summary['member_count'] = member_count
        if hasattr(group, 'administrators') and group.administrators:
            summary['administrators'] = group.administrators
        
        return summary
        
    except Exception as e:
        logger.error(f"Error creating group summary: {e}")
        return {'error': str(e)}


def calculate_sharing_statistics(organization_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Calculate sharing statistics for an organization.
    
    Args:
        organization_id: Organization ID
        days: Number of days to look back
        
    Returns:
        Dictionary containing sharing statistics
    """
    try:
        from .models.trust_models import TrustLog
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get all sharing-related logs using source_organization field
        sharing_logs = TrustLog.objects.filter(
            source_organization=organization_id,
            timestamp__gte=cutoff_date
        )
        
        # Calculate statistics based on action types
        intelligence_shared = sharing_logs.filter(action='intelligence_shared').count()
        access_granted = sharing_logs.filter(action='access_granted').count()
        intelligence_accessed = sharing_logs.filter(action='intelligence_accessed').count()
        
        # Total sharing activities (shared + granted, not accessed)
        total_sharing_activities = intelligence_shared + access_granted
        
        # Get unique partner organizations
        partner_orgs = sharing_logs.values_list('target_organization', flat=True).distinct()
        
        statistics = {
            'organization_id': organization_id,
            'period_days': days,
            'intelligence_shared': intelligence_shared,
            'access_granted': access_granted,
            'intelligence_accessed': intelligence_accessed,
            'total_sharing_activities': total_sharing_activities,
            'unique_partners': len([org for org in partner_orgs if org]),
            'calculated_at': timezone.now().isoformat()
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error calculating sharing statistics: {e}")
        return {
            'organization_id': organization_id,
            'period_days': days,
            'error': str(e),
            'calculated_at': timezone.now().isoformat()
        }


def get_trust_network_analysis(organization_id: str) -> Dict[str, Any]:
    """
    Analyze trust network for an organization.
    
    Args:
        organization_id: Organization ID to analyze
        
    Returns:
        Dictionary containing network analysis
    """
    try:
        from .models.trust_models import TrustRelationship, TrustGroup, TrustGroupMembership
        
        # Get all active relationships for this organization
        relationships = TrustRelationship.objects.filter(
            Q(source_organization=organization_id) | Q(target_organization=organization_id),
            status='active'  # Use status instead of is_active
        )
        
        # Calculate basic metrics
        total_relationships = relationships.count()
        
        # Calculate effective relationships (only active ones)
        effective_relationships = total_relationships  # All filtered relationships are active
        
        # Calculate effectiveness ratio
        effectiveness_ratio = 1.0 if total_relationships > 0 else 0
        
        # Calculate trust level distribution
        trust_levels = relationships.values_list('trust_level__level', flat=True)
        trust_distribution = {}
        for level in trust_levels:
            trust_distribution[level] = trust_distribution.get(level, 0) + 1
        
        # Get connected organizations (network reach)
        connected_orgs = set()
        for rel in relationships:
            if rel.source_organization == organization_id:
                connected_orgs.add(rel.target_organization)
            else:
                connected_orgs.add(rel.source_organization)
        
        network_reach = len(connected_orgs)
        
        analysis = {
            'organization': organization_id,
            'total_relationships': total_relationships,
            'effective_relationships': effective_relationships,
            'effectiveness_ratio': effectiveness_ratio,
            'trust_level_distribution': trust_distribution,
            'network_reach': network_reach,
            'analysis_timestamp': timezone.now().isoformat()
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing trust network: {e}")
        return {
            'organization': organization_id,
            'error': str(e),
            'analysis_timestamp': timezone.now().isoformat()
        }


def export_trust_configuration(format_type: str = 'json') -> Union[str, Dict[str, Any]]:
    """
    Export trust configuration in specified format.
    
    Args:
        format_type: Export format ('json', 'csv')
        
    Returns:
        Configuration data in specified format
    """
    try:
        from .models.trust_models import TrustLevel, TrustGroup
        
        # Gather configuration data
        trust_levels = []
        for level in TrustLevel.objects.filter(is_active=True):
            level_data = {
                'name': level.name,
                'level': level.level,
                'numerical_value': level.numerical_value,
                'description': level.description,
                'default_anonymization_level': level.default_anonymization_level,
                'default_access_level': level.default_access_level,
                'is_system_default': getattr(level, 'is_system_default', False),
                'created_at': level.created_at.isoformat()
            }
            # Add sharing_policies if it exists
            if hasattr(level, 'sharing_policies'):
                level_data['sharing_policies'] = level.sharing_policies
            trust_levels.append(level_data)
        
        trust_groups = []
        for group in TrustGroup.objects.filter(is_active=True):
            group_data = {
                'name': group.name,
                'description': group.description,
                'group_type': group.group_type,
                'is_public': group.is_public,
                'default_trust_level': group.default_trust_level.name if group.default_trust_level else None,
                'created_at': group.created_at.isoformat()
            }
            # Add group_policies if it exists
            if hasattr(group, 'group_policies'):
                group_data['group_policies'] = group.group_policies
            trust_groups.append(group_data)
        
        config_data = {
            'export_timestamp': timezone.now().isoformat(),
            'trust_levels': trust_levels,
            'trust_groups': trust_groups,
            'version': '1.0'  # Use 'version' instead of 'configuration_version'
        }
        
        if format_type.lower() == 'json':
            return json.dumps(config_data, indent=2)
        elif format_type.lower() == 'csv':
            # For CSV format, currently returns JSON for simplicity
            # Can be enhanced later to provide proper CSV format
            return json.dumps(config_data, indent=2)
        else:
            raise ValueError("Format must be 'json' or 'csv'")
        
    except ValueError as ve:
        # Re-raise ValueError so tests can catch it
        raise ve
    except Exception as e:
        logger.error(f"Error exporting trust configuration: {e}")
        if format_type.lower() == 'json':
            return json.dumps({'error': str(e)})
        else:
            return f"Error: {str(e)}"


def validate_trust_configuration(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate trust configuration data.
    
    Args:
        config_data: Configuration data to validate
        
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Check required sections
    required_sections = ['trust_levels', 'trust_groups']
    for section in required_sections:
        if section not in config_data:
            errors.append(f"Missing required field: {section}")
    
    # Validate trust levels
    if 'trust_levels' in config_data:
        for i, level in enumerate(config_data['trust_levels']):
            level_errors = []
            
            # Check required fields
            required_fields = ['name', 'level', 'numerical_value']
            for field in required_fields:
                if field not in level:
                    level_errors.append(f"Missing {field}")
            
            # Validate numerical value
            if 'numerical_value' in level:
                try:
                    value = int(level['numerical_value'])
                    if value < 0 or value > 100:
                        level_errors.append("numerical_value must be 0-100")
                except (ValueError, TypeError):
                    level_errors.append("numerical_value must be an integer")
            
            if level_errors:
                errors.append(f"Trust level {i}: {'; '.join(level_errors)}")
    
    # Validate trust groups
    if 'trust_groups' in config_data:
        for i, group in enumerate(config_data['trust_groups']):
            # Check each required field individually to match test expectations
            required_fields = ['name', 'default_trust_level']
            for field in required_fields:
                if field not in group:
                    errors.append(f"Trust group {i}: Missing {field}")
    
    return len(errors) == 0, errors


def format_trust_relationship_for_display(relationship, include_details: bool = True) -> str:
    """
    Format trust relationship for human-readable display.
    
    Args:
        relationship: TrustRelationship instance
        include_details: Whether to include detailed information
        
    Returns:
        Formatted string representation
    """
    try:
        # Get status emoji
        status_emojis = {
            'active': '✅',
            'pending': '⏳',
            'suspended': '⏸️',
            'revoked': '❌',
            'expired': '🔒'
        }
        
        # Get trust level emoji
        trust_emojis = {
            'none': '🚫',
            'low': '🟡',
            'medium': '🟠',
            'high': '🟢',
            'complete': '💎'
        }
        
        # Truncate organization IDs for display (first 8 characters)
        source_short = relationship.source_organization[:8]
        target_short = relationship.target_organization[:8]
        
        # Get appropriate emojis
        status_emoji = status_emojis.get(relationship.status, '❓')
        trust_emoji = trust_emojis.get(relationship.trust_level.level, '❓')
        
        # Basic format with emojis
        basic_format = f"{source_short} -> {target_short} "
        basic_format += f"{trust_emoji} {relationship.trust_level.name} "
        basic_format += f"{status_emoji} {relationship.relationship_type}"
        
        return basic_format
        
    except Exception as e:
        logger.error(f"Error formatting relationship for display: {e}")
        return f"Trust Relationship (error: {str(e)})"