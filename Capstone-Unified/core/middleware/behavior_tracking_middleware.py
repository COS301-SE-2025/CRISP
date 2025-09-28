"""
Behavior Tracking Middleware
Tracks user activities and sessions for behavioral analysis
"""

import logging
import time
import json
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import resolve
from django.core.cache import cache
from core.models.user_behavior_models import UserSession, UserActivityLog
from core.services.user_behavior_analytics_service import UserBehaviorAnalyticsService

User = get_user_model()
logger = logging.getLogger(__name__)


class BehaviorTrackingMiddleware:
    """
    Middleware to track user behavior for security analytics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.analytics_service = UserBehaviorAnalyticsService()
        
        # Endpoints to track for behavior analysis
        self.tracked_endpoints = [
            'api/soc/',
            'api/indicators/',
            'api/threat-feeds/',
            'api/users/',
            'api/organizations/',
            'api/auth/',
            'api/alerts/',
        ]
        
        # High-value endpoints that require special attention
        self.high_value_endpoints = [
            'export',
            'delete',
            'create',
            'assign',
            'incidents/',
        ]
    
    def __call__(self, request):
        # Pre-processing
        start_time = time.time()
        
        # Track the request
        self.track_request_start(request)
        
        # Process the request
        response = self.get_response(request)
        
        # Post-processing
        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)
        
        # Track the response
        self.track_request_end(request, response, duration_ms)
        
        return response
    
    def track_request_start(self, request):
        """
        Track the start of a request
        """
        if not self.should_track_request(request):
            return
        
        # Store request start time for duration calculation
        request._behavior_start_time = time.time()
        
        # Get or create user session
        if hasattr(request, 'user') and request.user.is_authenticated:
            session = self.get_or_create_user_session(request)
            request._behavior_session = session
    
    def track_request_end(self, request, response, duration_ms):
        """
        Track the end of a request and log activity
        """
        if not self.should_track_request(request) or not hasattr(request, 'user') or not request.user.is_authenticated:
            return
        
        try:
            # Log the activity
            self.log_user_activity(request, response, duration_ms)
            
            # Update session metrics
            if hasattr(request, '_behavior_session'):
                self.update_session_metrics(request, response)
            
            # Check for real-time anomalies on critical endpoints
            if self.is_critical_endpoint(request):
                self.check_real_time_anomalies(request)
                
        except Exception as e:
            logger.error(f"Error in behavior tracking: {e}")
    
    def should_track_request(self, request):
        """
        Determine if this request should be tracked
        """
        # Skip static files and health checks
        if request.path.startswith(('/static/', '/media/', '/health/')):
            return False
        
        # Skip if not an API endpoint we're interested in
        return any(endpoint in request.path for endpoint in self.tracked_endpoints)
    
    def get_or_create_user_session(self, request):
        """
        Get or create a user session for tracking
        """
        user = request.user
        session_key = request.session.session_key
        
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Check for existing active session
        try:
            session = UserSession.objects.get(
                user=user,
                session_key=session_key,
                end_time__isnull=True
            )
        except UserSession.DoesNotExist:
            # Create new session
            session = UserSession.objects.create(
                user=user,
                session_key=session_key,
                start_time=timezone.now(),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                login_method=self.detect_login_method(request)
            )
            
            logger.info(f"New session created for {user.username}: {session.id}")
        
        return session
    
    def log_user_activity(self, request, response, duration_ms):
        """
        Log detailed user activity
        """
        user = request.user
        
        # Determine action type
        action_type = self.determine_action_type(request)
        
        # Get resource information
        resource_info = self.extract_resource_info(request, response)
        
        # Create activity log
        UserActivityLog.objects.create(
            user=user,
            session=getattr(request, '_behavior_session', None),
            action_type=action_type,
            endpoint=request.path,
            method=request.method,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            request_data=self.sanitize_request_data(request),
            response_status=response.status_code,
            resource_accessed=resource_info.get('resource', ''),
            resource_count=resource_info.get('count', 1),
            success=200 <= response.status_code < 400,
            duration_ms=duration_ms
        )
    
    def update_session_metrics(self, request, response):
        """
        Update session-level metrics
        """
        session = request._behavior_session
        
        # Increment API call count
        session.api_calls_count += 1
        
        # Track endpoints accessed
        endpoint = request.path
        if endpoint not in session.endpoints_accessed:
            session.endpoints_accessed.append(endpoint)
        
        # Track data access
        if response.status_code == 200:
            data_count = self.estimate_data_records(request, response)
            session.data_records_accessed += data_count
        
        # Track SOC-specific activities
        self.update_soc_activities(request, response, session)
        
        session.save()
    
    def update_soc_activities(self, request, response, session):
        """
        Update SOC-specific activity counters
        """
        if 'incidents' in request.path:
            if request.method == 'POST' and response.status_code in [200, 201]:
                session.incidents_created += 1
            elif request.method in ['PUT', 'PATCH'] and response.status_code == 200:
                session.incidents_modified += 1
            elif 'assign' in request.path and request.method == 'POST':
                session.incidents_assigned += 1
        
        elif 'threat-feeds' in request.path and response.status_code == 200:
            session.threat_feeds_accessed += 1
        
        elif 'export' in request.path and response.status_code == 200:
            session.exports_performed += 1
    
    def check_real_time_anomalies(self, request):
        """
        Check for real-time anomalies on critical endpoints
        """
        if not hasattr(request, '_behavior_session'):
            return
        
        session = request._behavior_session
        
        # Check for rapid-fire requests (potential automation)
        cache_key = f"request_count_{session.user.id}_{session.session_key}"
        request_count = cache.get(cache_key, 0)
        request_count += 1
        cache.set(cache_key, request_count, 60)  # 1-minute window
        
        if request_count > 50:  # More than 50 requests per minute
            logger.warning(f"Rapid requests detected for {session.user.username}: {request_count}/min")
            # Could trigger immediate anomaly detection here
        
        # Check for bulk data access
        if 'export' in request.path or self.estimate_data_records(request, None) > 1000:
            logger.warning(f"Bulk data access detected for {session.user.username}")
    
    def determine_action_type(self, request):
        """
        Determine the type of action being performed
        """
        path = request.path.lower()
        method = request.method
        
        if 'auth' in path and method == 'POST':
            return 'login'
        elif 'logout' in path:
            return 'logout'
        elif 'incidents' in path:
            if method == 'POST':
                return 'incident_create'
            elif method in ['PUT', 'PATCH']:
                return 'incident_update'
            elif 'assign' in path:
                return 'incident_assign'
            elif method == 'DELETE':
                return 'incident_delete'
        elif 'export' in path:
            return 'export_data'
        elif method == 'DELETE':
            return 'admin_action'
        elif any(admin_path in path for admin_path in ['users', 'organizations', 'settings']):
            return 'admin_action'
        else:
            return 'api_call'
    
    def extract_resource_info(self, request, response):
        """
        Extract information about the resource being accessed
        """
        resource_info = {'resource': '', 'count': 1}
        
        try:
            # Extract resource from URL
            url_name = resolve(request.path).url_name
            resource_info['resource'] = url_name or request.path
            
            # Estimate record count from response
            if hasattr(response, 'content') and response.get('Content-Type', '').startswith('application/json'):
                try:
                    content = json.loads(response.content)
                    if isinstance(content, dict):
                        # Check for pagination info
                        if 'count' in content:
                            resource_info['count'] = content['count']
                        elif 'results' in content and isinstance(content['results'], list):
                            resource_info['count'] = len(content['results'])
                        elif 'data' in content and isinstance(content['data'], list):
                            resource_info['count'] = len(content['data'])
                    elif isinstance(content, list):
                        resource_info['count'] = len(content)
                except (json.JSONDecodeError, AttributeError):
                    pass
                    
        except Exception:
            pass
        
        return resource_info
    
    def estimate_data_records(self, request, response):
        """
        Estimate the number of data records accessed/returned
        """
        try:
            if response and hasattr(response, 'content'):
                content_length = len(response.content)
                # Rough estimate: 1KB per record on average
                return max(1, content_length // 1024)
            else:
                # For requests without response, estimate based on endpoint
                if 'export' in request.path:
                    return 100  # Assume export endpoints return more data
                elif any(bulk_endpoint in request.path for bulk_endpoint in ['list', 'all']):
                    return 10
                else:
                    return 1
        except Exception:
            return 1
    
    def is_critical_endpoint(self, request):
        """
        Check if this is a critical endpoint requiring immediate analysis
        """
        return any(critical in request.path for critical in self.high_value_endpoints)
    
    def detect_login_method(self, request):
        """
        Detect the method used for login
        """
        if 'mfa' in request.path.lower():
            return 'mfa'
        elif 'sso' in request.path.lower():
            return 'sso'
        else:
            return 'password'
    
    def get_client_ip(self, request):
        """
        Get the client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def sanitize_request_data(self, request):
        """
        Sanitize request data for logging (remove sensitive information)
        """
        try:
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
                data = json.loads(request.body.decode('utf-8'))
                
                # Remove sensitive fields
                sensitive_fields = ['password', 'token', 'secret', 'key', 'credential']
                for field in sensitive_fields:
                    if field in data:
                        data[field] = '[REDACTED]'
                
                return data
        except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
            pass
        
        return {}


class SessionCleanupMiddleware:
    """
    Middleware to handle session cleanup and analytics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.analytics_service = UserBehaviorAnalyticsService()
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Check for logout or session end
        if self.is_logout_request(request) or self.is_session_ending(request):
            self.finalize_user_session(request)
        
        return response
    
    def is_logout_request(self, request):
        """Check if this is a logout request"""
        return 'logout' in request.path or request.method == 'POST' and 'auth' in request.path
    
    def is_session_ending(self, request):
        """Check if the session is ending"""
        return hasattr(request, 'session') and request.session.get('_session_ending', False)
    
    def finalize_user_session(self, request):
        """Finalize user session and trigger analytics"""
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return
        
        try:
            # Find active session
            session_key = request.session.session_key
            if session_key:
                sessions = UserSession.objects.filter(
                    user=request.user,
                    session_key=session_key,
                    end_time__isnull=True
                )
                
                for session in sessions:
                    # Set end time and calculate duration
                    session.end_time = timezone.now()
                    session.calculate_duration()
                    session.save()
                    
                    # Trigger behavioral analysis
                    anomalies = self.analytics_service.analyze_session_for_anomalies(session)
                    
                    if anomalies:
                        logger.info(f"Session analysis completed for {request.user.username}: {len(anomalies)} anomalies detected")
                    
        except Exception as e:
            logger.error(f"Error finalizing session: {e}")