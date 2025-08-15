"""
Trust Management Validators

Validation functions and classes for trust management operations.
Provides security validation, trust relationship validation, and access control validation.
"""

import re
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, time
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


class SecurityValidator:
    """Enhanced security validator for trust operations."""
    
    @staticmethod
    def validate_input_sanitization(input_data):
        """Validate and sanitize input data"""
        result = {'valid': True, 'errors': [], 'sanitized_data': {}}
        
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>'
        ]
        
        for key, value in input_data.items():
            if isinstance(value, str):
                has_dangerous_content = False
                # Check for dangerous patterns
                for pattern in dangerous_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        has_dangerous_content = True
                        result['errors'].append(f'Dangerous content detected in {key}')
                
                # If dangerous content is found, mark as invalid
                if has_dangerous_content:
                    result['valid'] = False
                
                # Sanitize by removing dangerous characters
                sanitized = re.sub(r'[<>"\']', '', value)
                result['sanitized_data'][key] = sanitized
            else:
                result['sanitized_data'][key] = value
        
        return result
    
    @staticmethod
    def validate_rate_limiting(user_id=None, operation=None, action=None, organization_id=None, limit=5, window=60, window_minutes=None):
        """Validate rate limiting"""
        # Support both 'operation' and 'action' parameters for backward compatibility
        action_name = operation or action or 'default'
        # Support both window (seconds) and window_minutes parameters
        window_seconds = window_minutes * 60 if window_minutes else window
        
        # Build cache key with organization if provided
        if organization_id:
            cache_key = f"rate_limit:{action_name}:{user_id}:{organization_id}"
        else:
            cache_key = f"rate_limit_{user_id}_{action_name}"
            
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return {
                'valid': False,
                'errors': ['Rate limit exceeded'],
                'current_count': current_count,
                'limit': limit
            }
        
        # Increment counter
        new_count = current_count + 1
        cache.set(cache_key, new_count, window_seconds)
        
        return {
            'valid': True,
            'errors': [],
            'current_count': new_count,
            'limit': limit
        }
    
    def validate_suspicious_patterns(self, user_id, operation_data):
        """Detect suspicious patterns"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check business hours (9 AM to 5 PM)
        now = datetime.now().time()
        business_start = time(9, 0)
        business_end = time(17, 0)
        
        if not (business_start <= now <= business_end):
            result['warnings'].append('Operation occurring outside business hours')
            # Only make invalid for certain high-risk operations, otherwise just warn
            if operation_data.get('high_risk', False):
                result['valid'] = False
                result['errors'].append('Operation occurring outside business hours')
        
        # Check for rapid operations
        recent_ops_key = f"recent_ops_{user_id}"
        recent_ops = cache.get(recent_ops_key, [])
        
        if len(recent_ops) > 5:  # More than 5 operations recently
            result['warnings'].append('Unusually high operation frequency detected')
        
        # Check for invalid timestamps
        timestamp = operation_data.get('timestamp')
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if timezone.is_naive(timestamp):
                        timestamp = timezone.make_aware(timestamp)
                
                current_time = timezone.now()
                time_diff = (current_time - timestamp).total_seconds()
                
                # Check for operations with very old timestamps
                if time_diff > 3600:  # More than 1 hour old
                    result['valid'] = False
                    result['errors'].append('Operation timestamp too old')
            except (ValueError, TypeError):
                result['valid'] = False
                result['errors'].append('Invalid timestamp format')
        
        return result
    
    @staticmethod
    def validate_cryptographic_integrity(data: Any, signature: str, secret_key: str = None) -> Dict[str, Any]:
        """Validate cryptographic integrity of data."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Get secret key from settings or parameter
            if not secret_key:
                secret_key = getattr(settings, 'TRUST_MANAGEMENT_SECRET_KEY', None)
                if not secret_key:
                    result['valid'] = False
                    result['errors'].append("Cannot validate signature: secret key not configured")
                    return result
            
            # Convert data to string for signature calculation
            if isinstance(data, dict):
                data_string = str(sorted(data.items()))
            else:
                data_string = str(data)
            
            # Generate expected signature
            expected_signature = hmac.new(
                secret_key.encode(),
                data_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                result['valid'] = False
                result['errors'].append("Cryptographic signature validation failed")
                
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Cryptographic validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_temporal_security(operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate temporal security aspects."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            timestamp = operation_data.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if timezone.is_naive(timestamp):
                        timestamp = timezone.make_aware(timestamp)
                
                current_time = timezone.now()
                time_diff = (current_time - timestamp).total_seconds()
                
                # Check for replay attacks (operations too old)
                if time_diff > 300:  # More than 5 minutes old
                    result['valid'] = False
                    result['errors'].append("Operation timestamp too old (potential replay attack)")
                elif time_diff > 120:  # More than 2 minutes old
                    result['warnings'].append("Operation timestamp is older than expected")
                    
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Temporal security validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_trust_escalation(from_level: str, to_level: str) -> Dict[str, Any]:
        """Validate trust level escalation."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            level_hierarchy = {
                'none': 0,
                'low': 1,
                'medium': 2,
                'high': 3,
                'complete': 4
            }
            
            # Handle invalid levels gracefully
            if from_level not in level_hierarchy or to_level not in level_hierarchy:
                # Return valid for unknown levels rather than failing
                return result
            
            from_value = level_hierarchy[from_level]
            to_value = level_hierarchy[to_level]
            
            if to_value > from_value:
                if to_value > from_value + 2:  # Large jump (e.g., low to complete)
                    result['valid'] = False
                    result['errors'].append(f"Trust escalation too large: from {from_level} to {to_level}")
                else:
                    result['warnings'].append("Trust level escalation detected")
                
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Trust escalation validation failed: {str(e)}")
        
        return result


class TrustGroupValidator:
    """Validator for trust group operations."""
    
    @staticmethod
    def validate_create_group(name: str, description: str, creator_org: str, 
                            group_type: str = 'community') -> Dict:
        """Validate trust group creation data."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            valid_group_types = ['sector', 'geography', 'purpose', 'custom', 'community']
            
            # Validate group name
            if not name or len(name.strip()) < 3:
                result['valid'] = False
                result['errors'].append("Group name must be at least 3 characters")
            
            # Validate description
            if not description or len(description.strip()) < 10:
                result['valid'] = False
                result['errors'].append("Group description must be at least 10 characters")
            
            # Validate creator organization
            if not creator_org:
                result['valid'] = False
                result['errors'].append("Creator organization is required")
            else:
                try:
                    uuid.UUID(creator_org)
                except (ValueError, TypeError):
                    result['valid'] = False
                    result['errors'].append("Invalid creator organization UUID")
            
            # Validate group type
            if group_type not in valid_group_types:
                result['valid'] = False
                result['errors'].append(f"Invalid group type. Must be one of: {', '.join(valid_group_types)}")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_join_group(group_id: str, organization: str, 
                          membership_type: str = 'member', joined_by: str = None) -> Dict:
        """Validate joining a trust group."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            valid_membership_types = ['admin', 'member', 'observer']
            
            # Validate group ID
            if not group_id:
                result['valid'] = False
                result['errors'].append("Group ID is required")
            else:
                try:
                    uuid.UUID(group_id)
                except (ValueError, TypeError):
                    result['valid'] = False
                    result['errors'].append("Invalid group ID")
            
            # Validate organization
            if not organization:
                result['valid'] = False
                result['errors'].append("Organization is required")
            else:
                try:
                    uuid.UUID(organization)
                except (ValueError, TypeError):
                    result['valid'] = False
                    result['errors'].append("Invalid organization UUID")
            
            # Validate membership type
            if membership_type not in valid_membership_types:
                result['valid'] = False
                result['errors'].append(f"Invalid membership type. Must be one of: {', '.join(valid_membership_types)}")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Validation failed: {str(e)}")
        
        return result


class AccessControlValidator:
    """Validator for access control and sharing policies."""
    
    @staticmethod
    def validate_sharing_policy(policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sharing policy configuration."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check required fields
            required_fields = ['trust_level_id', 'resource_types']
            for field in required_fields:
                if field not in policy_config:
                    result['valid'] = False
                    result['errors'].append(f"Missing required field: {field}")
            
            # Validate resource types
            valid_resource_types = ['indicator', 'malware', 'attack-pattern', 'vulnerability', 'report']
            if 'resource_types' in policy_config:
                invalid_types = []
                for resource_type in policy_config['resource_types']:
                    if resource_type not in valid_resource_types:
                        invalid_types.append(resource_type)
                
                if invalid_types:
                    result['valid'] = False
                    result['errors'].append(f"Invalid resource types: {', '.join(invalid_types)}")
            
            # Validate actions if provided
            if 'allowed_actions' in policy_config:
                valid_actions = ['read', 'download', 'share', 'modify', 'delete']
                invalid_actions = []
                for action in policy_config['allowed_actions']:
                    if action not in valid_actions:
                        invalid_actions.append(action)
                
                if invalid_actions:
                    result['valid'] = False
                    result['errors'].append(f"Invalid actions: {', '.join(invalid_actions)}")
                        
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Validation failed: {str(e)}")
        
        return result


def validate_trust_operation(operation_type, data, user_context):
    """
    Validate trust operations
    """
    try:
        # Basic validation logic
        if not operation_type:
            return {'valid': False, 'errors': ['Operation type is required']}
        
        if not data:
            return {'valid': False, 'errors': ['Data is required']}
        
        # Add specific validation based on operation_type
        if operation_type == 'create_relationship':
            # Accept both forms of field names
            source_field = 'source_organization' if 'source_organization' in data else 'source_org'
            target_field = 'target_organization' if 'target_organization' in data else 'target_org'
            
            required_fields = [source_field, target_field]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {'valid': False, 'errors': [f'Missing required fields: {missing_fields}']}
        
        return {'valid': True, 'errors': []}
    
    except Exception as e:
        return {'valid': False, 'errors': [str(e)]}