"""
Trust Management Validators

Comprehensive validation logic for trust relationships, groups, and operations.
"""

import re
import sys
import uuid
import hashlib
import hmac
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from datetime import timedelta
from collections import defaultdict

from ..models.models import TrustRelationship, TrustGroup, TrustLevel, SharingPolicy

logger = logging.getLogger(__name__)


class TrustRelationshipValidator:
    """
    Validator for trust relationship operations.
    """
    
    @staticmethod
    def validate_create_relationship(
        source_org: str,
        target_org: str,
        trust_level_name: str,
        relationship_type: str = 'bilateral',
        valid_until: timezone.datetime = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate trust relationship creation parameters.
        
        Returns:
            Dict with validation results and any errors
        """
        errors = []
        warnings = []
        
        # Validate organization UUIDs
        try:
            uuid.UUID(source_org)
        except (ValueError, TypeError):
            errors.append(f"Invalid source organization UUID: {source_org}")
        
        try:
            uuid.UUID(target_org)
        except (ValueError, TypeError):
            errors.append(f"Invalid target organization UUID: {target_org}")
        
        # Check if organizations are different
        if source_org == target_org:
            errors.append("Source and target organizations cannot be the same")
        
        # Validate trust level exists
        try:
            trust_level = TrustLevel.objects.get(name=trust_level_name, is_active=True)
        except TrustLevel.DoesNotExist:
            errors.append(f"Trust level '{trust_level_name}' not found or inactive")
            trust_level = None
        
        # Validate relationship type
        valid_types = ['bilateral', 'community', 'hierarchical', 'federation']
        if relationship_type not in valid_types:
            errors.append(f"Invalid relationship type. Must be one of: {valid_types}")
        
        # Validate expiration date
        if valid_until:
            if valid_until <= timezone.now():
                errors.append("Expiration date must be in the future")
            elif valid_until < timezone.now() + timedelta(days=1):
                warnings.append("Relationship expires within 24 hours")
        
        # Check for existing relationship
        existing = TrustRelationship.objects.filter(
            source_organization=source_org,
            target_organization=target_org,
            is_active=True
        ).first()
        
        if existing:
            errors.append("Active trust relationship already exists between these organizations")
        
        # Validate trust level constraints
        if trust_level:
            validation_result = TrustRelationshipValidator.validate_trust_level_constraints(
                trust_level, relationship_type
            )
            errors.extend(validation_result.get('errors', []))
            warnings.extend(validation_result.get('warnings', []))
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'trust_level': trust_level
        }
    
    @staticmethod
    def validate_trust_level_constraints(
        trust_level: TrustLevel,
        relationship_type: str
    ) -> Dict[str, Any]:
        """
        Validate trust level constraints for relationship type.
        """
        errors = []
        warnings = []
        
        # Community relationships should use medium or lower trust
        if relationship_type == 'community' and trust_level.numerical_value > 75:
            warnings.append(
                "High trust levels are unusual for community relationships. "
                "Consider using a lower trust level."
            )
        
        # Hierarchical relationships should use high trust
        if relationship_type == 'hierarchical' and trust_level.numerical_value < 50:
            warnings.append(
                "Low trust levels may be insufficient for hierarchical relationships. "
                "Consider using a higher trust level."
            )
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_approval_request(
        relationship_id: str,
        approving_org: str,
        approved_by_user: str
    ) -> Dict[str, Any]:
        """
        Validate trust relationship approval request.
        """
        errors = []
        warnings = []
        
        # Validate relationship ID
        try:
            relationship = TrustRelationship.objects.get(id=relationship_id, is_active=True)
        except TrustRelationship.DoesNotExist:
            errors.append("Trust relationship not found or inactive")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate approving organization
        if (relationship.source_organization != approving_org and 
            relationship.target_organization != approving_org):
            errors.append("Organization is not part of this trust relationship")
        
        # Check if already approved
        if relationship.source_organization == approving_org and relationship.approved_by_source:
            errors.append("Source organization has already approved this relationship")
        
        if relationship.target_organization == approving_org and relationship.approved_by_target:
            errors.append("Target organization has already approved this relationship")
        
        # Check relationship status
        if relationship.status not in ['pending', 'active']:
            errors.append(f"Cannot approve relationship with status: {relationship.status}")
        
        # Validate user identifier
        if not approved_by_user or not approved_by_user.strip():
            warnings.append("No user specified for approval")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'relationship': relationship
        }
    
    @staticmethod
    def validate_revocation_request(
        relationship_id: str,
        revoking_org: str,
        revoked_by_user: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        Validate trust relationship revocation request.
        """
        errors = []
        warnings = []
        
        # Validate relationship ID
        try:
            relationship = TrustRelationship.objects.get(id=relationship_id, is_active=True)
        except TrustRelationship.DoesNotExist:
            errors.append("Trust relationship not found or inactive")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate revoking organization
        if (relationship.source_organization != revoking_org and 
            relationship.target_organization != revoking_org):
            errors.append("Organization is not part of this trust relationship")
        
        # Check relationship status
        if relationship.status in ['revoked', 'expired']:
            errors.append(f"Cannot revoke relationship with status: {relationship.status}")
        
        # Validate reason
        if not reason or not reason.strip():
            warnings.append("No reason provided for revocation")
        elif len(reason) > 1000:
            warnings.append("Revocation reason is very long")
        
        # Check if this will affect active intelligence sharing
        if relationship.status == 'active':
            warnings.append(
                "Revoking an active relationship will immediately stop intelligence sharing"
            )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'relationship': relationship
        }


class TrustGroupValidator:
    """
    Validator for trust group operations.
    """
    
    @staticmethod
    def validate_create_group(
        name: str,
        description: str,
        creator_org: str,
        group_type: str = 'community',
        default_trust_level_name: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate trust group creation parameters.
        """
        errors = []
        warnings = []
        
        # Validate name
        if not name or not name.strip():
            errors.append("Group name is required")
        elif len(name) > 255:
            errors.append("Group name is too long (max 255 characters)")
        elif TrustGroup.objects.filter(name=name.strip()).exists():
            errors.append(f"Trust group with name '{name}' already exists")
        
        # Validate name format
        if name and not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
            warnings.append(
                "Group name contains special characters that may cause issues"
            )
        
        # Validate description
        if not description or not description.strip():
            errors.append("Group description is required")
        elif len(description) > 2000:
            errors.append("Group description is too long (max 2000 characters)")
        
        # Validate creator organization
        try:
            uuid.UUID(creator_org)
        except (ValueError, TypeError):
            errors.append(f"Invalid creator organization UUID: {creator_org}")
        
        # Validate group type
        valid_types = ['community', 'sector', 'geography', 'purpose', 'federation']
        if group_type not in valid_types:
            errors.append(f"Invalid group type. Must be one of: {valid_types}")
        
        # Validate default trust level
        if default_trust_level_name:
            try:
                trust_level = TrustLevel.objects.get(
                    name=default_trust_level_name, 
                    is_active=True
                )
            except TrustLevel.DoesNotExist:
                errors.append(f"Default trust level '{default_trust_level_name}' not found or inactive")
                trust_level = None
        else:
            trust_level = TrustLevel.get_default_trust_level()
            if not trust_level:
                errors.append("No default trust level found and none specified")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'trust_level': trust_level
        }
    
    @staticmethod
    def validate_join_group(
        group_id: str,
        organization: str,
        membership_type: str = 'member',
        invited_by: str = None
    ) -> Dict[str, Any]:
        """
        Validate trust group join request.
        """
        errors = []
        warnings = []
        
        # Validate group ID
        try:
            group = TrustGroup.objects.get(id=group_id, is_active=True)
        except TrustGroup.DoesNotExist:
            errors.append("Trust group not found or inactive")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate organization
        try:
            uuid.UUID(organization)
        except (ValueError, TypeError):
            errors.append(f"Invalid organization UUID: {organization}")
        
        # Check if already a member
        from ..models.models import TrustGroupMembership
        existing_membership = TrustGroupMembership.objects.filter(
            trust_group=group,
            organization=organization,
            is_active=True
        ).first()
        
        if existing_membership:
            errors.append("Organization is already a member of this group")
        
        # Validate membership type
        valid_types = ['member', 'administrator', 'moderator']
        if membership_type not in valid_types:
            errors.append(f"Invalid membership type. Must be one of: {valid_types}")
        
        # Check if requesting admin/moderator role
        if membership_type in ['administrator', 'moderator'] and not invited_by:
            warnings.append(
                "Requesting elevated membership without invitation may require approval"
            )
        
        # Check group approval requirements
        if group.requires_approval and not invited_by:
            warnings.append("Group requires approval for membership")
        
        # Validate inviting organization
        if invited_by:
            try:
                uuid.UUID(invited_by)
            except (ValueError, TypeError):
                errors.append(f"Invalid inviting organization UUID: {invited_by}")
            
            # Check if inviting org can invite
            if not group.can_administer(invited_by):
                inviting_membership = TrustGroupMembership.objects.filter(
                    trust_group=group,
                    organization=invited_by,
                    is_active=True
                ).first()
                
                if not inviting_membership:
                    warnings.append("Inviting organization is not a member of this group")
                elif inviting_membership.membership_type == 'member':
                    warnings.append("Regular members cannot invite others to elevated roles")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'group': group
        }
    
    @staticmethod
    def validate_leave_group(
        group_id: str,
        organization: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        Validate trust group leave request.
        """
        errors = []
        warnings = []
        
        # Validate group and membership
        try:
            group = TrustGroup.objects.get(id=group_id, is_active=True)
        except TrustGroup.DoesNotExist:
            errors.append("Trust group not found or inactive")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        from ..models.models import TrustGroupMembership
        try:
            membership = TrustGroupMembership.objects.get(
                trust_group=group,
                organization=organization,
                is_active=True
            )
        except TrustGroupMembership.DoesNotExist:
            errors.append("Organization is not an active member of this group")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check if last administrator
        if membership.membership_type == 'administrator':
            admin_count = TrustGroupMembership.objects.filter(
                trust_group=group,
                membership_type='administrator',
                is_active=True
            ).count()
            
            if admin_count <= 1:
                errors.append(
                    "Cannot leave group - you are the last administrator. "
                    "Please promote another member to administrator first."
                )
        
        # Validate reason
        if reason and len(reason) > 1000:
            warnings.append("Leave reason is very long")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'group': group,
            'membership': membership
        }


class AccessControlValidator:
    """
    Validator for access control operations.
    """
    
    @staticmethod
    def validate_intelligence_access(
        requesting_org: str,
        intelligence_owner: str,
        resource_type: str = None,
        required_access_level: str = 'read'
    ) -> Dict[str, Any]:
        """
        Validate intelligence access request.
        """
        errors = []
        warnings = []
        
        # Validate organization UUIDs
        try:
            uuid.UUID(requesting_org)
        except (ValueError, TypeError):
            errors.append(f"Invalid requesting organization UUID: {requesting_org}")
        
        try:
            uuid.UUID(intelligence_owner)
        except (ValueError, TypeError):
            errors.append(f"Invalid intelligence owner UUID: {intelligence_owner}")
        
        # Validate access level
        valid_levels = ['none', 'read', 'subscribe', 'contribute', 'full']
        if required_access_level not in valid_levels:
            errors.append(f"Invalid access level. Must be one of: {valid_levels}")
        
        # Validate resource type
        if resource_type:
            valid_types = [
                'indicator', 'malware', 'attack-pattern', 'threat-actor',
                'identity', 'relationship', 'tool', 'vulnerability',
                'observed-data', 'report', 'course-of-action', 'campaign',
                'intrusion-set', 'infrastructure', 'location', 'note',
                'opinion', 'marking-definition'
            ]
            if resource_type not in valid_types:
                warnings.append(f"Unusual resource type: {resource_type}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_sharing_policy(policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate sharing policy configuration.
        """
        errors = []
        warnings = []
        
        # Validate required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if not policy_data.get(field):
                errors.append(f"Field '{field}' is required")
        
        # Validate policy name
        name = policy_data.get('name', '')
        if name and SharingPolicy.objects.filter(name=name).exists():
            errors.append(f"Sharing policy with name '{name}' already exists")
        
        # Validate STIX types
        allowed_types = policy_data.get('allowed_stix_types', [])
        blocked_types = policy_data.get('blocked_stix_types', [])
        
        valid_stix_types = [
            'indicator', 'malware', 'attack-pattern', 'threat-actor',
            'identity', 'relationship', 'tool', 'vulnerability',
            'observed-data', 'report', 'course-of-action', 'campaign',
            'intrusion-set', 'infrastructure', 'location', 'note',
            'opinion', 'marking-definition'
        ]
        
        for stix_type in allowed_types:
            if stix_type not in valid_stix_types:
                warnings.append(f"Unknown STIX type in allowed list: {stix_type}")
        
        for stix_type in blocked_types:
            if stix_type not in valid_stix_types:
                warnings.append(f"Unknown STIX type in blocked list: {stix_type}")
        
        # Check for conflicts
        overlapping_types = set(allowed_types) & set(blocked_types)
        if overlapping_types:
            errors.append(f"STIX types cannot be both allowed and blocked: {overlapping_types}")
        
        # Validate TLP level
        tlp_level = policy_data.get('max_tlp_level')
        if tlp_level:
            valid_tlp = ['white', 'green', 'amber', 'red']
            if tlp_level not in valid_tlp:
                errors.append(f"Invalid TLP level. Must be one of: {valid_tlp}")
        
        # Validate age constraints
        max_age_days = policy_data.get('max_age_days')
        if max_age_days is not None:
            if not isinstance(max_age_days, int) or max_age_days < 0:
                errors.append("max_age_days must be a non-negative integer")
            elif max_age_days > 3650:  # 10 years
                warnings.append("Very long retention period specified")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


class SecurityValidator:
    """
    Security-focused validators for trust operations.
    """
    
    # Rate limiting storage (in production, use Redis or proper cache)
    _operation_history = defaultdict(list)
    _suspicious_patterns = defaultdict(int)
    
    @staticmethod
    def validate_bulk_operations(operation_count: int, user: str) -> Dict[str, Any]:
        """
        Validate bulk operation requests for security.
        """
        errors = []
        warnings = []
        
        # Check operation count limits
        if operation_count > 100:
            errors.append("Bulk operations limited to 100 items per request")
        elif operation_count > 50:
            warnings.append("Large bulk operation - consider breaking into smaller batches")
        
        # Validate user for audit trail
        if not user or not user.strip():
            warnings.append("No user specified for bulk operation")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_trust_escalation(
        current_trust_level: TrustLevel,
        new_trust_level: TrustLevel,
        justification: str = None
    ) -> Dict[str, Any]:
        """
        Validate trust level escalation for security review.
        """
        errors = []
        warnings = []
        
        trust_increase = new_trust_level.numerical_value - current_trust_level.numerical_value
        
        # Significant trust increase requires justification
        if trust_increase > 25:
            if not justification or len(justification.strip()) < 10:
                errors.append(
                    "Significant trust level increase requires detailed justification"
                )
            else:
                # Check for suspicious or inadequate justifications
                suspicious_keywords = ['hack', 'attack', 'test', 'pentest', 'exploit', 'breach']
                if any(keyword in justification.lower() for keyword in suspicious_keywords):
                    errors.append(
                        "Trust escalation with suspicious justification requires detailed justification"
                    )
                elif len(justification.strip()) < 50:  # Require substantial justification
                    errors.append(
                        "Significant trust level increase requires detailed justification (minimum 50 characters)"
                    )
                else:
                    warnings.append("Trust level increase may require security review")
        
        # Complete trust requires special validation
        if new_trust_level.level == 'complete':
            if not justification or 'security review' not in justification.lower():
                warnings.append(
                    "Complete trust level should include security review confirmation"
                )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'trust_increase': trust_increase
        }
    
    @staticmethod
    def validate_anonymization_downgrade(
        current_level: str,
        new_level: str,
        trust_level: TrustLevel
    ) -> Dict[str, Any]:
        """
        Validate anonymization level downgrade.
        """
        errors = []
        warnings = []
        
        anonymization_levels = ['full', 'partial', 'minimal', 'none']
        current_index = anonymization_levels.index(current_level) if current_level in anonymization_levels else 0
        new_index = anonymization_levels.index(new_level) if new_level in anonymization_levels else 0
        
        # Check for downgrade
        if new_index > current_index:
            anonymization_reduction = new_index - current_index
            
            if anonymization_reduction > 1:
                warnings.append(
                    "Significant anonymization reduction - ensure this is intentional"
                )
            
            # No anonymization requires high trust
            if new_level == 'none' and trust_level.numerical_value < 75:
                errors.append(
                    "No anonymization requires high trust level (75+)"
                )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_rate_limiting(operation_type: str, user: str, organization: str = None, 
                             time_window_minutes: int = 60, max_operations: int = 10) -> Dict[str, Any]:
        """
        Validate operation against rate limiting rules.
        """
        errors = []
        warnings = []
        
        try:
            # Use cache-based rate limiting for better concurrency
            cache_key = f"rate_limit:{operation_type}:{user}"
            org_cache_key = f"rate_limit_org:{operation_type}:{organization}" if organization else None
            
            # Get current count from cache
            current_count = cache.get(cache_key, 0)
            
            # Handle potential cache corruption (negative values)
            if current_count < 0:
                current_count = 0
                cache.set(cache_key, 0, timeout=time_window_minutes * 60)
            
            # Check user rate limiting
            if current_count >= max_operations:
                errors.append(f"Rate limit exceeded for user")
                return {
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings,
                    'current_count': current_count,
                    'max_operations': max_operations
                }
            elif current_count >= max_operations * 0.8:
                warnings.append(f"Approaching rate limit: {current_count}/{max_operations} operations")
            
            # Check organization level rate limiting (50 operations per hour)
            if organization and org_cache_key:
                org_count = cache.get(org_cache_key, 0)
                if org_count < 0:
                    org_count = 0
                    cache.set(org_cache_key, 0, timeout=time_window_minutes * 60)
                
                org_limit = max_operations * 5  # Organization limit is 5x user limit
                if org_count >= org_limit:
                    errors.append(f"Organization rate limit exceeded")
                    return {
                        'valid': False,
                        'errors': errors,
                        'warnings': warnings,
                        'current_count': current_count,
                        'max_operations': max_operations
                    }
                elif org_count >= org_limit * 0.8:
                    warnings.append(f"Approaching organization rate limit: {org_count}/{org_limit} operations")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'current_count': current_count,
                'max_operations': max_operations
            }
        except Exception as e:
            logger.error(f"Rate limiting validation error: {str(e)}")
            return {
                'valid': True,  # Allow operation if rate limiting fails
                'errors': [],
                'warnings': [f"Rate limiting check failed: {str(e)}"],
                'current_count': 0,
                'max_operations': max_operations
            }
    
    @staticmethod
    def record_operation(operation_type: str, user: str, organization: str = None):
        """
        Record an operation for rate limiting and pattern analysis.
        """
        try:
            # Use cache-based tracking for better concurrency
            cache_key = f"rate_limit:{operation_type}:{user}"
            current_count = cache.get(cache_key, 0)
            
            # Increment count with 1 hour timeout
            cache.set(cache_key, current_count + 1, timeout=3600)
            
            # Also track organization level
            if organization:
                org_cache_key = f"rate_limit_org:{operation_type}:{organization}"
                org_count = cache.get(org_cache_key, 0)
                cache.set(org_cache_key, org_count + 1, timeout=3600)
            
            # Log for audit trail
            logger.info(f"Operation recorded: {operation_type} by {user} for org {organization}")
        except Exception as e:
            logger.error(f"Failed to record operation: {str(e)}")
    
    @staticmethod
    def validate_input_sanitization(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data for injection attacks and malicious content.
        """
        errors = []
        warnings = []
        
        # SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|;|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\'\s*(OR|AND)\s+\'\w+\'\s*=\s*\'\w+)",
        ]
        
        # XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
        ]
        
        # Command injection patterns
        cmd_patterns = [
            r"[;&|`]",
            r"\$\([^)]*\)",
            r"`[^`]*`",
            r"__import__",
            r"\.system\(",
            r"rm\s+-rf",
        ]
        
        # Template injection patterns
        template_patterns = [
            r"\{\{.*\}\}",
            r"\$\{.*\}",
            r"\#{.*\}",
        ]
        
        # LDAP injection patterns  
        ldap_patterns = [
            r"jndi:",
            r"ldap://",
        ]
        
        def check_patterns(value: str, patterns: List[str], attack_type: str):
            if not isinstance(value, str):
                return False
                
            found_pattern = False
            for pattern in patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    if not found_pattern:  # Only add error once per attack type
                        errors.append(f"Potential {attack_type} attack detected in input")
                    warnings.append(f"Detected {attack_type} pattern in input: {pattern}")
                    logger.warning(f"Security: {attack_type} pattern detected: {pattern}")
                    found_pattern = True
            return found_pattern
        
        # Check all string values recursively
        def validate_recursive(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    validate_recursive(value, current_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    validate_recursive(item, f"{path}[{i}]")
            elif isinstance(data, str):
                # Check for malicious patterns
                check_patterns(data, sql_patterns, "SQL injection")
                check_patterns(data, xss_patterns, "XSS")
                check_patterns(data, cmd_patterns, "Command injection")
                check_patterns(data, template_patterns, "Template injection")
                check_patterns(data, ldap_patterns, "LDAP injection")
                
                # Check for null bytes
                if '\x00' in data:
                    errors.append("Null byte detected in input")
                
                # Check for extremely long strings (possible buffer overflow)
                if len(data) > 10000:
                    warnings.append(f"Very long input detected: {len(data)} characters")
                    errors.append(f"Input exceeds maximum length: {len(data)} characters")
                elif len(data) > 5000:
                    warnings.append(f"Long input detected: {len(data)} characters")
        
        validate_recursive(input_data)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_cryptographic_integrity(data: Dict[str, Any], signature: str = None, 
                                       expected_hash: str = None, key: str = None) -> Dict[str, Any]:
        """
        Validate cryptographic integrity of data.
        """
        errors = []
        warnings = []
        
        if not key:
            key = getattr(settings, 'TRUST_MANAGEMENT_SECRET_KEY', 'default-key')
        
        try:
            if signature:
                # HMAC signature validation
                message = str(sorted(data.items())).encode('utf-8')
                expected_signature = hmac.new(
                    key.encode('utf-8'),
                    message,
                    hashlib.sha256
                ).hexdigest()
                
                # Compare signatures
                if not hmac.compare_digest(signature, expected_signature):
                    errors.append("HMAC signature verification failed")
                    logger.warning("Security: HMAC signature verification failed for data")
            
            elif expected_hash:
                # Hash validation
                data_str = str(sorted(data.items()))
                actual_hash = hashlib.sha256(data_str.encode()).hexdigest()
                
                if actual_hash != expected_hash:
                    errors.append("Cryptographic hash mismatch detected")
                    logger.warning("Security: Hash mismatch detected")
            
        except Exception as e:
            errors.append(f"Error validating cryptographic integrity: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_temporal_security(timestamp, max_age_minutes: int = 5) -> Dict[str, Any]:
        """
        Validate temporal security (replay attack prevention).
        """
        errors = []
        warnings = []
        
        try:
            # Handle both Unix timestamp (float) and datetime objects
            if isinstance(timestamp, (int, float)):
                request_time = timestamp
                current_time = time.time()
            else:
                # Assume datetime object
                request_time = timestamp.timestamp()
                current_time = time.time()
            
            age_seconds = current_time - request_time
            age_minutes = age_seconds / 60
            
            # Check if request is too old (replay attack)
            if age_seconds > max_age_minutes * 60:
                errors.append(f"Request too old: {age_minutes:.1f} minutes")
            elif age_seconds > max_age_minutes * 60 * 0.8:
                warnings.append(f"Request approaching age limit: {age_minutes:.1f} minutes")
            
            # Check for future timestamps (clock skew or tampering)
            if request_time > current_time + 60:  # 1 minute in the future
                errors.append("Request timestamp is in the future - possible clock skew or tampering")
            elif request_time > current_time + 30:  # 30 seconds in the future
                warnings.append("Request timestamp is slightly in the future - check clock synchronization")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'age_minutes': age_minutes
            }
        except Exception as e:
            logger.error(f"Temporal security validation error: {str(e)}")
            return {
                'valid': False,
                'errors': [f"Invalid timestamp format: {str(e)}"],
                'warnings': warnings,
                'age_minutes': 0
            }
    
    @staticmethod
    def validate_suspicious_patterns(user: str, organization: str = None, 
                                   operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect suspicious patterns in operations.
        """
        errors = []
        warnings = []
        
        try:
            # Track operation frequency for the user
            freq_key = f"suspicious_patterns:{user}"
            current_count = cache.get(freq_key, 0)
            
            # Increment and cache the count
            cache.set(freq_key, current_count + 1, timeout=3600)  # 1 hour window
            
            # Check for high operation frequency
            if current_count > 10:  # More than 10 operations in an hour
                warnings.append(f"Detected high operation frequency for user: {current_count + 1} operations")
            
            # Check for mutual trust relationships
            if operation_data:
                source_org = operation_data.get('source_organization')
                target_org = operation_data.get('target_organization')
                
                if source_org and target_org:
                    # Check if reverse relationship exists
                    reverse_exists = TrustRelationship.objects.filter(
                        source_organization=target_org,
                        target_organization=source_org,
                        is_active=True
                    ).exists()
                    
                    if reverse_exists:
                        warnings.append("Potential mutual trust relationship detected")
                
                # Check for high trust level requests
                trust_level_name = operation_data.get('trust_level_name', '')
                if any(level in trust_level_name.lower() for level in ['high', 'complete']):
                    warnings.append("High trust level selected - ensure proper authorization")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'operation_count': current_count + 1
            }
        except Exception as e:
            logger.error(f"Suspicious pattern validation error: {str(e)}")
            return {
                'valid': True,  # Don't block operations if pattern detection fails
                'errors': [],
                'warnings': [f"Pattern detection failed: {str(e)}"],
                'operation_count': 0
            }


def validate_trust_operation(operation_type: str, **kwargs) -> Dict[str, Any]:
    """
    Main validation function for trust operations with comprehensive security checks.
    
    Args:
        operation_type: Type of operation to validate
        **kwargs: Operation-specific parameters
        
    Returns:
        Validation result dictionary
    """
    all_errors = []
    all_warnings = []
    
    # Extract common parameters for security validation
    user = kwargs.get('created_by') or kwargs.get('user') or kwargs.get('approved_by_user')
    organization = kwargs.get('source_org') or kwargs.get('organization') or kwargs.get('creator_org')
    
    try:
        # Perform security validations first
        if user and operation_type:
            # Rate limiting check
            rate_result = SecurityValidator.validate_rate_limiting(
                operation_type, user, organization
            )
            all_errors.extend(rate_result.get('errors', []))
            all_warnings.extend(rate_result.get('warnings', []))
            
            # If rate limited, return immediately
            if not rate_result['valid']:
                import sys
                if not ('test' in sys.argv or getattr(settings, 'TESTING', False)):
                    logger.warning(f"Trust operation validation failed for {user}: Rate limit exceeded")
                return {
                    'valid': False,
                    'errors': all_errors,
                    'warnings': all_warnings
                }
            
            # Input sanitization check
            sanitization_result = SecurityValidator.validate_input_sanitization(kwargs)
            all_errors.extend(sanitization_result.get('errors', []))
            all_warnings.extend(sanitization_result.get('warnings', []))
            
            # If input is malicious, return immediately
            if not sanitization_result['valid']:
                import sys
                if not ('test' in sys.argv or getattr(settings, 'TESTING', False)):
                    logger.warning(f"Trust operation validation failed for {user}: Malicious input detected")
                return {
                    'valid': False,
                    'errors': all_errors,
                    'warnings': all_warnings
                }
            
            # Suspicious pattern detection
            pattern_result = SecurityValidator.validate_suspicious_patterns(
                user, organization, kwargs
            )
            all_warnings.extend(pattern_result.get('warnings', []))
        
        # Standard validation
        validators = {
            'create_relationship': TrustRelationshipValidator.validate_create_relationship,
            'approve_relationship': TrustRelationshipValidator.validate_approval_request,
            'revoke_relationship': TrustRelationshipValidator.validate_revocation_request,
            'create_group': TrustGroupValidator.validate_create_group,
            'join_group': TrustGroupValidator.validate_join_group,
            'leave_group': TrustGroupValidator.validate_leave_group,
            'intelligence_access': AccessControlValidator.validate_intelligence_access,
            'sharing_policy': AccessControlValidator.validate_sharing_policy,
            'bulk_operation': SecurityValidator.validate_bulk_operations,
            'trust_escalation': SecurityValidator.validate_trust_escalation,
            'anonymization_downgrade': SecurityValidator.validate_anonymization_downgrade,
        }
        
        validator = validators.get(operation_type)
        if not validator:
            return {
                'valid': False,
                'errors': [f"Unknown operation type: {operation_type}"],
                'warnings': all_warnings
            }
        
        # Run the specific validator
        result = validator(**kwargs)
        
        # Combine results
        all_errors.extend(result.get('errors', []))
        all_warnings.extend(result.get('warnings', []))
        
        final_result = {
            'valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': all_warnings
        }
        
        # Add any additional data from the specific validator
        for key, value in result.items():
            if key not in ['valid', 'errors', 'warnings']:
                final_result[key] = value
        
        # Log security warnings if there are any (reduced verbosity for tests)
        import sys
        is_testing = 'test' in sys.argv or getattr(settings, 'TESTING', False)
        
        if all_warnings and not is_testing:
            logger.warning(f"Trust operation validation warnings for {user}: {', '.join(all_warnings)}")
        
        # Log security errors if validation failed
        if all_errors and not is_testing:
            logger.warning(f"Trust operation validation failed for {user}: {', '.join(all_errors)}")
        
        # Record the operation if it's valid and we have the necessary info
        if final_result['valid'] and user and operation_type:
            SecurityValidator.record_operation(operation_type, user, organization)
        
        return final_result
        
    except Exception as e:
        logger.error(f"Trust operation validation error: {str(e)}")
        return {
            'valid': False,
            'errors': [f"Validation error: {str(e)}"],
            'warnings': all_warnings
        }