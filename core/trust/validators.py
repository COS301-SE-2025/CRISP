"""
Trust Management Validators

Validation functions and classes for trust management operations.
Provides security validation, trust relationship validation, and access control validation.
"""

import re
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class TrustRelationshipValidator:
    """Validator for trust relationship operations."""
    
    @staticmethod
    def validate_create_relationship(source_org: str, target_org: str, trust_level_name: str, 
                                   created_by: str, **kwargs) -> Dict[str, Any]:
        """Validate trust relationship creation."""
        errors = []
        
        # Basic validation
        if not source_org or not target_org:
            errors.append("Source and target organizations are required")
        
        if source_org == target_org:
            errors.append("Cannot create trust relationship with same organization")
        
        if not trust_level_name:
            errors.append("Trust level is required")
        
        if not created_by:
            errors.append("Created by user is required")
            
        # Validate organization UUIDs
        for org_id in [source_org, target_org]:
            try:
                uuid.UUID(org_id)
            except (ValueError, TypeError):
                errors.append(f"Invalid organization UUID: {org_id}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_approve_relationship(relationship_id: str, approving_org: str, 
                                    approved_by: str) -> Dict[str, Any]:
        """Validate trust relationship approval."""
        errors = []
        
        if not relationship_id:
            errors.append("Relationship ID is required")
        
        if not approving_org:
            errors.append("Approving organization is required")
            
        if not approved_by:
            errors.append("Approved by user is required")
            
        try:
            uuid.UUID(relationship_id)
        except (ValueError, TypeError):
            errors.append("Invalid relationship ID")
            
        try:
            uuid.UUID(approving_org)
        except (ValueError, TypeError):
            errors.append("Invalid approving organization UUID")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_revoke_relationship(relationship_id: str, revoking_org: str, 
                                   revoked_by: str, reason: str = None) -> Dict[str, Any]:
        """Validate trust relationship revocation."""
        errors = []
        
        if not relationship_id:
            errors.append("Relationship ID is required")
        
        if not revoking_org:
            errors.append("Revoking organization is required")
            
        if not revoked_by:
            errors.append("Revoked by user is required")
            
        try:
            uuid.UUID(relationship_id)
        except (ValueError, TypeError):
            errors.append("Invalid relationship ID")
            
        try:
            uuid.UUID(revoking_org)
        except (ValueError, TypeError):
            errors.append("Invalid revoking organization UUID")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class TrustGroupValidator:
    """Validator for trust group operations."""
    
    @staticmethod
    def validate_create_group(name: str, description: str, creator_org: str, 
                            group_type: str = None, **kwargs) -> Dict[str, Any]:
        """Validate trust group creation."""
        errors = []
        
        if not name or len(name.strip()) < 3:
            errors.append("Group name must be at least 3 characters")
        
        if not description or len(description.strip()) < 10:
            errors.append("Group description must be at least 10 characters")
        
        if not creator_org:
            errors.append("Creator organization is required")
            
        try:
            uuid.UUID(creator_org)
        except (ValueError, TypeError):
            errors.append("Invalid creator organization UUID")
        
        # Validate group type
        valid_types = ['sector', 'geography', 'purpose', 'custom', 'community']
        if group_type and group_type not in valid_types:
            errors.append(f"Invalid group type. Must be one of: {', '.join(valid_types)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_join_group(group_id: str, organization: str, membership_type: str = None,
                          joined_by: str = None) -> Dict[str, Any]:
        """Validate trust group joining."""
        errors = []
        
        if not group_id:
            errors.append("Group ID is required")
        
        if not organization:
            errors.append("Organization is required")
            
        try:
            uuid.UUID(group_id)
        except (ValueError, TypeError):
            errors.append("Invalid group ID")
            
        try:
            uuid.UUID(organization)
        except (ValueError, TypeError):
            errors.append("Invalid organization UUID")
        
        # Validate membership type
        valid_types = ['admin', 'member', 'observer']
        if membership_type and membership_type not in valid_types:
            errors.append(f"Invalid membership type. Must be one of: {', '.join(valid_types)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class AccessControlValidator:
    """Validator for access control operations."""
    
    @staticmethod
    def validate_sharing_policy(policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sharing policy configuration."""
        errors = []
        
        required_fields = ['name', 'trust_level_id', 'resource_types']
        for field in required_fields:
            if field not in policy_config:
                errors.append(f"Missing required field: {field}")
        
        # Validate resource types
        if 'resource_types' in policy_config:
            valid_types = ['indicator', 'malware', 'attack-pattern', 'vulnerability', 'report']
            invalid_types = [rt for rt in policy_config['resource_types'] if rt not in valid_types]
            if invalid_types:
                errors.append(f"Invalid resource types: {', '.join(invalid_types)}")
        
        # Validate allowed actions
        if 'allowed_actions' in policy_config:
            valid_actions = ['read', 'download', 'share', 'modify', 'delete']
            invalid_actions = [a for a in policy_config['allowed_actions'] if a not in valid_actions]
            if invalid_actions:
                errors.append(f"Invalid actions: {', '.join(invalid_actions)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class SecurityValidator:
    """Security validator for trust management operations."""
    
    @staticmethod
    def validate_input_sanitization(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize input data."""
        errors = []
        sanitized_data = {}
        
        for key, value in input_data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized_value = re.sub(r'[<>"\';]', '', value)
                # Check for script injection attempts
                if re.search(r'<script|javascript:|data:', value.lower()):
                    errors.append(f"Potentially malicious content detected in {key}")
                sanitized_data[key] = sanitized_value
            else:
                sanitized_data[key] = value
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized_data
        }
    
    @staticmethod
    def validate_rate_limiting(operation: str, user_id: str, organization_id: str,
                             limit: int = 100, window_minutes: int = 60) -> Dict[str, Any]:
        """Validate rate limiting for operations."""
        cache_key = f"rate_limit:{operation}:{user_id}:{organization_id}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return {
                'valid': False,
                'errors': [f"Rate limit exceeded for {operation}. Limit: {limit} per {window_minutes} minutes"],
                'current_count': current_count,
                'limit': limit
            }
        
        # Increment counter
        cache.set(cache_key, current_count + 1, window_minutes * 60)
        
        return {
            'valid': True,
            'errors': [],
            'current_count': current_count + 1,
            'limit': limit
        }
    
    @staticmethod
    def validate_suspicious_patterns(operation_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect suspicious patterns in operations."""
        errors = []
        warnings = []
        
        # Check for unusual timing patterns
        if 'timestamp' in operation_data:
            try:
                op_time = datetime.fromisoformat(operation_data['timestamp'].replace('Z', '+00:00'))
                current_time = timezone.now()
                
                # Check if operation is happening outside business hours
                if op_time.hour < 6 or op_time.hour > 22:
                    warnings.append("Operation occurring outside business hours")
                
                # Check for operations too far in the future or past
                time_diff = abs((current_time - op_time).total_seconds())
                if time_diff > 3600:  # More than 1 hour difference
                    errors.append("Operation timestamp is too far from current time")
                    
            except (ValueError, TypeError):
                errors.append("Invalid timestamp format")
        
        # Check for rapid-fire operations
        user_id = user_context.get('user_id')
        if user_id:
            recent_ops_key = f"recent_ops:{user_id}"
            recent_ops = cache.get(recent_ops_key, [])
            
            # Add current operation
            recent_ops.append(timezone.now().timestamp())
            
            # Keep only operations from the last 5 minutes
            cutoff = timezone.now().timestamp() - 300
            recent_ops = [ts for ts in recent_ops if ts > cutoff]
            
            if len(recent_ops) > 20:  # More than 20 operations in 5 minutes
                warnings.append("Unusually high operation frequency detected")
            
            cache.set(recent_ops_key, recent_ops, 300)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_cryptographic_integrity(data: Dict[str, Any], expected_signature: str = None) -> Dict[str, Any]:
        """Validate cryptographic integrity of data."""
        errors = []
        
        # Check if we have a secret key for HMAC validation
        secret_key = getattr(settings, 'TRUST_MANAGEMENT_SECRET_KEY', None)
        
        if expected_signature and secret_key:
            # Calculate HMAC signature
            data_string = str(sorted(data.items()))
            calculated_signature = hmac.new(
                secret_key.encode(),
                data_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(expected_signature, calculated_signature):
                errors.append("Cryptographic signature validation failed")
        elif expected_signature:
            errors.append("Cannot validate signature: secret key not configured")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_temporal_security(operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate temporal security constraints."""
        errors = []
        warnings = []
        
        # Check for replay attacks (operations with old timestamps)
        if 'timestamp' in operation_data:
            try:
                op_time = datetime.fromisoformat(operation_data['timestamp'].replace('Z', '+00:00'))
                current_time = timezone.now()
                age = (current_time - op_time).total_seconds()
                
                if age > 300:  # Older than 5 minutes
                    errors.append("Operation timestamp too old (potential replay attack)")
                elif age > 60:  # Older than 1 minute
                    warnings.append("Operation timestamp is older than expected")
                    
            except (ValueError, TypeError):
                errors.append("Invalid timestamp format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_trust_escalation(current_trust_level: str, requested_trust_level: str) -> Dict[str, Any]:
        """Validate trust level escalation attempts."""
        errors = []
        warnings = []
        
        # Define trust level hierarchy
        trust_hierarchy = {
            'none': 0,
            'low': 1,
            'medium': 2,
            'high': 3,
            'complete': 4
        }
        
        current_level = trust_hierarchy.get(current_trust_level, 0)
        requested_level = trust_hierarchy.get(requested_trust_level, 0)
        
        # Check for significant trust escalation
        if requested_level > current_level + 1:
            errors.append("Trust escalation too large - requires additional approval")
        elif requested_level > current_level:
            warnings.append("Trust level escalation detected")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_anonymization_downgrade(current_level: str, requested_level: str) -> Dict[str, Any]:
        """Validate anonymization level downgrade attempts."""
        errors = []
        warnings = []
        
        # Define anonymization hierarchy (higher = more anonymous)
        anon_hierarchy = {
            'none': 0,
            'minimal': 1,
            'partial': 2,
            'full': 3,
            'custom': 2  # Treat custom as partial level
        }
        
        current_anon = anon_hierarchy.get(current_level, 2)
        requested_anon = anon_hierarchy.get(requested_level, 2)
        
        if requested_anon < current_anon:
            warnings.append("Anonymization level downgrade detected")
            
            # Significant downgrade requires validation
            if current_anon - requested_anon > 1:
                errors.append("Significant anonymization downgrade requires additional approval")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_api_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate API request data for security compliance.
        
        Args:
            request_data: Dictionary containing request data to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Input sanitization
        sanitization_result = SecurityValidator.validate_input_sanitization(request_data)
        if not sanitization_result['valid']:
            errors.extend(sanitization_result['errors'])
        
        # Check for suspicious patterns in the request
        user_context = {
            'user_id': request_data.get('user_id', 'unknown'),
            'timestamp': timezone.now().isoformat()
        }
        
        pattern_result = SecurityValidator.validate_suspicious_patterns(request_data, user_context)
        if not pattern_result['valid']:
            errors.extend(pattern_result['errors'])
        warnings.extend(pattern_result.get('warnings', []))
        
        # Temporal security validation
        temporal_result = SecurityValidator.validate_temporal_security(request_data)
        if not temporal_result['valid']:
            errors.extend(temporal_result['errors'])
        warnings.extend(temporal_result.get('warnings', []))
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'sanitized_data': sanitization_result.get('sanitized_data', request_data)
        }

    @staticmethod
    def record_security_event(event_type: str, user_id: str, organization_id: str,
                            details: Dict[str, Any]) -> None:
        """Record security events for monitoring."""
        try:
            from .models.trust_models import TrustLog
            
            TrustLog.objects.create(
                organization_id=organization_id,
                action='security_event',
                resource_type='security',
                resource_id=event_type,
                user_id=user_id,
                details={
                    'event_type': event_type,
                    'timestamp': timezone.now().isoformat(),
                    **details
                },
                success=True
            )
        except Exception as e:
            logger.error(f"Failed to record security event: {e}")


def validate_trust_operation(operation: str, data: Dict[str, Any], 
                           user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main validation function for trust operations.
    
    Args:
        operation: Type of operation (create_relationship, approve_relationship, etc.)
        data: Operation data to validate
        user_context: User context information
    
    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []
    
    try:
        user_context = user_context or {}
        
        # Input sanitization
        sanitization_result = SecurityValidator.validate_input_sanitization(data)
        if not sanitization_result['valid']:
            errors.extend(sanitization_result['errors'])
        
        # Rate limiting validation
        if 'user_id' in user_context and 'organization_id' in user_context:
            rate_limit_result = SecurityValidator.validate_rate_limiting(
                operation, 
                user_context['user_id'], 
                user_context['organization_id']
            )
            if not rate_limit_result['valid']:
                errors.extend(rate_limit_result['errors'])
        
        # Suspicious pattern detection
        if user_context:
            pattern_result = SecurityValidator.validate_suspicious_patterns(data, user_context)
            if not pattern_result['valid']:
                errors.extend(pattern_result['errors'])
            warnings.extend(pattern_result.get('warnings', []))
        
        # Operation-specific validation
        if operation == 'create_relationship':
            op_result = TrustRelationshipValidator.validate_create_relationship(**data)
        elif operation == 'approve_relationship':
            op_result = TrustRelationshipValidator.validate_approve_relationship(**data)
        elif operation == 'revoke_relationship':
            op_result = TrustRelationshipValidator.validate_revoke_relationship(**data)
        elif operation == 'create_group':
            op_result = TrustGroupValidator.validate_create_group(**data)
        elif operation == 'join_group':
            op_result = TrustGroupValidator.validate_join_group(**data)
        else:
            op_result = {'valid': True, 'errors': []}
        
        if not op_result['valid']:
            errors.extend(op_result['errors'])
        
        # Record security events if there are warnings or errors
        if (errors or warnings) and user_context.get('user_id') and user_context.get('organization_id'):
            SecurityValidator.record_security_event(
                'validation_issues',
                user_context['user_id'],
                user_context['organization_id'],
                {
                    'operation': operation,
                    'errors': errors,
                    'warnings': warnings,
                    'data_keys': list(data.keys())
                }
            )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
        
    except Exception as e:
        logger.error(f"Validation error for operation {operation}: {e}")
        return {
            'valid': False,
            'errors': [f"Validation error: {str(e)}"],
            'warnings': warnings
        }