from django.utils import timezone
from typing import Dict, List, Optional, Any
from django.db.models import Q
from django.core.exceptions import ValidationError
import logging
import json

logger = logging.getLogger(__name__)


class AuditService:
    """
    Comprehensive audit logging service for both user management and trust systems.
    Provides unified logging, querying, and reporting capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_user_event(self, user, action: str, ip_address: str = None, 
                      user_agent: str = None, success: bool = True, 
                      failure_reason: str = None, additional_data: Dict = None, 
                      target_user=None, target_organization=None):
        """
        Log user management events.
        
        Args:
            user: User performing the action
            action: Action type (must be in ACTION_CHOICES)
            ip_address: IP address of the request
            user_agent: User agent string
            success: Whether the action was successful
            failure_reason: Reason for failure (if applicable)
            additional_data: Additional context data
            target_user: Target user for the action (if applicable)
            target_organization: Target organization for the action (if applicable)
        """
        try:
            from ..user_management.models import AuthenticationLog
            
            # Ensure additional_data is serializable
            if additional_data:
                additional_data = self._sanitize_data(additional_data)
            
            log_entry = AuthenticationLog.objects.create(
                user=user,
                action=action,
                ip_address=ip_address or '127.0.0.1',
                user_agent=user_agent or 'Unknown',
                success=success,
                failure_reason=failure_reason,
                additional_data=additional_data or {},
                target_user=target_user,
                target_organization=target_organization
            )
            
            self.logger.info(
                f"User event logged: {action} by {user.username if user else 'System'} "
                f"- Success: {success}"
            )
            
            return log_entry
            
        except Exception as e:
            self.logger.error(f"Failed to log user event: {str(e)}")
            raise
    
    def log_trust_event(self, user, action: str, success: bool = True, 
                       details: str = None, trust_relationship=None, 
                       trust_group=None, additional_data: Dict = None):
        """
        Log trust management events.
        
        Args:
            user: User performing the action
            action: Action type (must be in ACTION_CHOICES)
            success: Whether the action was successful
            details: Additional details about the action
            trust_relationship: Related trust relationship (if applicable)
            trust_group: Related trust group (if applicable)
            additional_data: Additional context data
        """
        try:
            from ..trust.models import TrustLog
            
            # Ensure additional_data is serializable
            if additional_data:
                additional_data = self._sanitize_data(additional_data)
            
            log_entry = TrustLog.objects.create(
                user=user,
                action=action,
                success=success,
                details=details or '',
                trust_relationship=trust_relationship,
                trust_group=trust_group,
                additional_data=additional_data or {}
            )
            
            self.logger.info(
                f"Trust event logged: {action} by {user.username if user else 'System'} "
                f"- Success: {success}"
            )
            
            return log_entry
            
        except Exception as e:
            self.logger.error(f"Failed to log trust event: {str(e)}")
            raise
    
    def log_combined_event(self, user, user_action: str, trust_action: str, 
                          success: bool = True, ip_address: str = None, 
                          user_agent: str = None, trust_relationship=None, 
                          trust_group=None, additional_data: Dict = None):
        """
        Log events that span both user management and trust systems.
        
        Args:
            user: User performing the action
            user_action: User management action type
            trust_action: Trust management action type
            success: Whether the action was successful
            ip_address: IP address of the request
            user_agent: User agent string
            trust_relationship: Related trust relationship (if applicable)
            trust_group: Related trust group (if applicable)
            additional_data: Additional context data
        """
        try:
            # Log to both systems
            user_log = self.log_user_event(
                user=user,
                action=user_action,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                additional_data=additional_data
            )
            
            trust_log = self.log_trust_event(
                user=user,
                action=trust_action,
                success=success,
                trust_relationship=trust_relationship,
                trust_group=trust_group,
                additional_data=additional_data
            )
            
            return {
                'user_log': user_log,
                'trust_log': trust_log
            }
            
        except Exception as e:
            self.logger.error(f"Failed to log combined event: {str(e)}")
            raise
    
    def get_audit_logs(self, filters: Dict = None, limit: int = 100, 
                      offset: int = 0, include_trust_logs: bool = True, 
                      include_user_logs: bool = True) -> Dict:
        """
        Get audit logs with filtering and pagination.
        
        Args:
            filters: Dictionary of filter criteria
            limit: Maximum number of results
            offset: Number of results to skip
            include_trust_logs: Whether to include trust logs
            include_user_logs: Whether to include user logs
        
        Returns:
            Dictionary with logs and metadata
        """
        try:
            logs = []
            
            if include_user_logs:
                user_logs = self._get_user_logs(filters, limit, offset)
                logs.extend(user_logs)
            
            if include_trust_logs:
                trust_logs = self._get_trust_logs(filters, limit, offset)
                logs.extend(trust_logs)
            
            # Sort by timestamp (most recent first)
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Apply limit after sorting
            logs = logs[:limit]
            
            return {
                'logs': logs,
                'total_count': len(logs),
                'filters_applied': filters or {},
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'has_more': len(logs) == limit
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get audit logs: {str(e)}")
            raise
    
    def get_user_activity_summary(self, user, days: int = 30) -> Dict:
        """
        Get activity summary for a specific user.
        
        Args:
            user: User to get summary for
            days: Number of days to look back
        
        Returns:
            Dictionary with activity summary
        """
        try:
            from datetime import timedelta
            from ..user_management.models import AuthenticationLog
            from ..trust.models import TrustLog
            
            start_date = timezone.now() - timedelta(days=days)
            
            # Get user management activities
            user_activities = AuthenticationLog.objects.filter(
                user=user,
                timestamp__gte=start_date
            ).values('action').annotate(
                count=models.Count('id')
            )
            
            # Get trust activities
            trust_activities = TrustLog.objects.filter(
                user=user,
                timestamp__gte=start_date
            ).values('action').annotate(
                count=models.Count('id')
            )
            
            # Recent activities
            recent_user_logs = AuthenticationLog.objects.filter(
                user=user,
                timestamp__gte=start_date
            ).order_by('-timestamp')[:10]
            
            recent_trust_logs = TrustLog.objects.filter(
                user=user,
                timestamp__gte=start_date
            ).order_by('-timestamp')[:10]
            
            return {
                'user_id': str(user.id),
                'username': user.username,
                'summary_period_days': days,
                'user_activities': list(user_activities),
                'trust_activities': list(trust_activities),
                'recent_user_logs': [self._format_user_log(log) for log in recent_user_logs],
                'recent_trust_logs': [self._format_trust_log(log) for log in recent_trust_logs],
                'total_activities': len(user_activities) + len(trust_activities)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user activity summary: {str(e)}")
            raise
    
    def get_security_events(self, severity: str = 'all', days: int = 7) -> List[Dict]:
        """
        Get security-related events for monitoring.
        
        Args:
            severity: Security severity level ('high', 'medium', 'low', 'all')
            days: Number of days to look back
        
        Returns:
            List of security events
        """
        try:
            from datetime import timedelta
            from ..user_management.models import AuthenticationLog
            from ..trust.models import TrustLog
            
            start_date = timezone.now() - timedelta(days=days)
            
            # Define security-relevant actions
            high_severity_actions = [
                'login_failure', 'account_locked', 'account_unlocked',
                'relationship_revoked', 'access_denied', 'user_deactivated'
            ]
            
            medium_severity_actions = [
                'password_change', 'password_reset', 'trusted_device_added',
                'relationship_suspended', 'group_left'
            ]
            
            low_severity_actions = [
                'login_success', 'logout', 'token_refresh',
                'relationship_created', 'group_joined'
            ]
            
            # Build query based on severity
            if severity == 'high':
                relevant_actions = high_severity_actions
            elif severity == 'medium':
                relevant_actions = medium_severity_actions
            elif severity == 'low':
                relevant_actions = low_severity_actions
            else:
                relevant_actions = high_severity_actions + medium_severity_actions + low_severity_actions
            
            # Get user security events
            user_events = AuthenticationLog.objects.filter(
                action__in=relevant_actions,
                timestamp__gte=start_date
            ).order_by('-timestamp')
            
            # Get trust security events
            trust_events = TrustLog.objects.filter(
                action__in=relevant_actions,
                timestamp__gte=start_date
            ).order_by('-timestamp')
            
            # Format events
            events = []
            
            for event in user_events:
                events.append({
                    'type': 'user',
                    'severity': self._get_event_severity(event.action),
                    'timestamp': event.timestamp.isoformat(),
                    'action': event.action,
                    'user': event.user.username if event.user else 'System',
                    'ip_address': event.ip_address,
                    'success': event.success,
                    'details': event.failure_reason or 'Success'
                })
            
            for event in trust_events:
                events.append({
                    'type': 'trust',
                    'severity': self._get_event_severity(event.action),
                    'timestamp': event.timestamp.isoformat(),
                    'action': event.action,
                    'user': event.user.username if event.user else 'System',
                    'success': event.success,
                    'details': event.details or 'Success'
                })
            
            # Sort by timestamp
            events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get security events: {str(e)}")
            raise
    
    def _get_user_logs(self, filters: Dict = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get user management logs with filtering."""
        try:
            from ..user_management.models import AuthenticationLog
            
            query = AuthenticationLog.objects.select_related('user', 'target_user')
            
            if filters:
                if 'action' in filters:
                    query = query.filter(action=filters['action'])
                if 'user_id' in filters:
                    query = query.filter(user_id=filters['user_id'])
                if 'success' in filters:
                    query = query.filter(success=filters['success'])
                if 'start_date' in filters:
                    query = query.filter(timestamp__gte=filters['start_date'])
                if 'end_date' in filters:
                    query = query.filter(timestamp__lte=filters['end_date'])
            
            logs = query.order_by('-timestamp')[offset:offset+limit]
            
            return [self._format_user_log(log) for log in logs]
            
        except Exception as e:
            self.logger.error(f"Failed to get user logs: {str(e)}")
            return []
    
    def _get_trust_logs(self, filters: Dict = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get trust management logs with filtering."""
        try:
            from ..trust.models import TrustLog
            
            query = TrustLog.objects.select_related('user', 'trust_relationship', 'trust_group')
            
            if filters:
                if 'action' in filters:
                    query = query.filter(action=filters['action'])
                if 'user_id' in filters:
                    query = query.filter(user_id=filters['user_id'])
                if 'success' in filters:
                    query = query.filter(success=filters['success'])
                if 'start_date' in filters:
                    query = query.filter(timestamp__gte=filters['start_date'])
                if 'end_date' in filters:
                    query = query.filter(timestamp__lte=filters['end_date'])
            
            logs = query.order_by('-timestamp')[offset:offset+limit]
            
            return [self._format_trust_log(log) for log in logs]
            
        except Exception as e:
            self.logger.error(f"Failed to get trust logs: {str(e)}")
            return []
    
    def _format_user_log(self, log) -> Dict:
        """Format user log for API response."""
        return {
            'id': str(log.id),
            'type': 'user',
            'action': log.action,
            'user': log.user.username if log.user else 'System',
            'user_id': str(log.user.id) if log.user else None,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'success': log.success,
            'failure_reason': log.failure_reason,
            'timestamp': log.timestamp.isoformat(),
            'additional_data': log.additional_data,
            'target_user': log.target_user.username if log.target_user else None,
            'target_organization': log.target_organization.name if log.target_organization else None
        }
    
    def _format_trust_log(self, log) -> Dict:
        """Format trust log for API response."""
        return {
            'id': str(log.id),
            'type': 'trust',
            'action': log.action,
            'user': log.user.username if log.user else 'System',
            'user_id': str(log.user.id) if log.user else None,
            'success': log.success,
            'details': log.details,
            'timestamp': log.timestamp.isoformat(),
            'additional_data': log.additional_data,
            'trust_relationship': {
                'id': str(log.trust_relationship.id),
                'source': log.trust_relationship.source_organization.name,
                'target': log.trust_relationship.target_organization.name
            } if log.trust_relationship else None,
            'trust_group': {
                'id': str(log.trust_group.id),
                'name': log.trust_group.name
            } if log.trust_group else None
        }
    
    def _get_event_severity(self, action: str) -> str:
        """Determine severity level for an action."""
        high_severity = [
            'login_failure', 'account_locked', 'account_unlocked',
            'relationship_revoked', 'access_denied', 'user_deactivated'
        ]
        
        medium_severity = [
            'password_change', 'password_reset', 'trusted_device_added',
            'relationship_suspended', 'group_left'
        ]
        
        if action in high_severity:
            return 'high'
        elif action in medium_severity:
            return 'medium'
        else:
            return 'low'
    
    def _sanitize_data(self, data: Any) -> Dict:
        """Sanitize data for JSON serialization."""
        if isinstance(data, dict):
            return {k: self._sanitize_value(v) for k, v in data.items()}
        else:
            return {'data': self._sanitize_value(data)}
    
    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize individual values for JSON serialization."""
        if hasattr(value, '__dict__'):
            return str(value)
        elif isinstance(value, (list, tuple)):
            return [self._sanitize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._sanitize_value(v) for k, v in value.items()}
        else:
            return value