"""
User Behavior Analytics Models
Models for tracking and analyzing user behavior patterns to detect anomalies
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()


class UserBehaviorBaseline(models.Model):
    """
    Stores baseline behavior patterns for each user
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='behavior_baseline')
    
    # Login patterns
    avg_login_frequency_per_day = models.FloatField(default=0.0)
    avg_session_duration_minutes = models.FloatField(default=0.0)
    common_login_hours = models.JSONField(default=list)  # List of common hours [8, 9, 10, ...]
    common_login_days = models.JSONField(default=list)  # List of common weekdays [1, 2, 3, ...]
    
    # Activity patterns
    avg_api_calls_per_session = models.FloatField(default=0.0)
    common_accessed_endpoints = models.JSONField(default=list)  # Most frequently accessed endpoints
    avg_data_access_volume = models.FloatField(default=0.0)  # Average records accessed per session
    
    # Geographical patterns
    common_ip_ranges = models.JSONField(default=list)  # Common IP address patterns
    common_user_agents = models.JSONField(default=list)  # Common browser/device patterns
    
    # SOC-specific patterns
    avg_incidents_created_per_week = models.FloatField(default=0.0)
    avg_incidents_assigned_per_week = models.FloatField(default=0.0)
    common_incident_categories = models.JSONField(default=list)
    
    # Baseline calculation metadata
    baseline_period_start = models.DateTimeField()
    baseline_period_end = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)
    total_sessions_analyzed = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_behavior_baseline'
        verbose_name = 'User Behavior Baseline'
        verbose_name_plural = 'User Behavior Baselines'

    def __str__(self):
        return f"Baseline for {self.user.username}"


class UserSession(models.Model):
    """
    Tracks detailed user session information for behavior analysis
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_sessions')
    session_key = models.CharField(max_length=40, db_index=True)
    
    # Session details
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.FloatField(null=True, blank=True)
    
    # Authentication details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_method = models.CharField(max_length=50, default='password')  # password, mfa, sso
    
    # Activity metrics
    api_calls_count = models.IntegerField(default=0)
    endpoints_accessed = models.JSONField(default=list)
    data_records_accessed = models.IntegerField(default=0)
    
    # SOC-specific activities
    incidents_created = models.IntegerField(default=0)
    incidents_modified = models.IntegerField(default=0)
    incidents_assigned = models.IntegerField(default=0)
    threat_feeds_accessed = models.IntegerField(default=0)
    exports_performed = models.IntegerField(default=0)
    
    # Behavioral flags
    is_anomalous = models.BooleanField(default=False)
    anomaly_score = models.FloatField(default=0.0)  # 0-100 scale
    anomaly_reasons = models.JSONField(default=list)  # List of detected anomalies
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_session'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['ip_address', 'start_time']),
            models.Index(fields=['is_anomalous', 'anomaly_score']),
        ]

    def __str__(self):
        return f"Session {self.session_key[:8]}... for {self.user.username}"

    def calculate_duration(self):
        """Calculate and update session duration"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = delta.total_seconds() / 60
            return self.duration_minutes
        return None


class BehaviorAnomaly(models.Model):
    """
    Records detected behavioral anomalies
    """
    ANOMALY_TYPES = [
        ('login_frequency', 'Unusual Login Frequency'),
        ('login_time', 'Unusual Login Time'),
        ('login_location', 'Unusual Login Location'),
        ('session_duration', 'Unusual Session Duration'),
        ('api_usage', 'Unusual API Usage'),
        ('data_access', 'Unusual Data Access Volume'),
        ('privilege_escalation', 'Potential Privilege Escalation'),
        ('bulk_export', 'Bulk Data Export'),
        ('failed_authentication', 'Multiple Failed Authentications'),
        ('concurrent_sessions', 'Unusual Concurrent Sessions'),
        ('incident_manipulation', 'Unusual Incident Activity'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_anomalies')
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, null=True, blank=True)
    
    # Anomaly details
    anomaly_type = models.CharField(max_length=30, choices=ANOMALY_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    confidence_score = models.FloatField()  # 0-100 scale
    
    # Description and context
    title = models.CharField(max_length=200)
    description = models.TextField()
    detection_method = models.CharField(max_length=100)  # Algorithm used to detect
    
    # Baseline comparison
    baseline_value = models.FloatField(null=True, blank=True)
    observed_value = models.FloatField(null=True, blank=True)
    deviation_percentage = models.FloatField(null=True, blank=True)
    
    # Additional context
    context_data = models.JSONField(default=dict)  # Additional contextual information
    related_events = models.JSONField(default=list)  # Related security events
    
    # Investigation status
    is_investigated = models.BooleanField(default=False)
    investigation_notes = models.TextField(blank=True)
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigated_anomalies')
    investigated_at = models.DateTimeField(null=True, blank=True)
    
    # Resolution
    is_false_positive = models.BooleanField(default=False)
    is_confirmed_threat = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'behavior_anomaly'
        verbose_name = 'Behavior Anomaly'
        verbose_name_plural = 'Behavior Anomalies'
        indexes = [
            models.Index(fields=['user', 'detected_at']),
            models.Index(fields=['anomaly_type', 'severity']),
            models.Index(fields=['is_investigated', 'confidence_score']),
        ]

    def __str__(self):
        return f"{self.get_anomaly_type_display()} - {self.user.username} ({self.severity})"


class UserActivityLog(models.Model):
    """
    Detailed activity logging for behavior analysis
    """
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('api_call', 'API Call'),
        ('data_access', 'Data Access'),
        ('incident_create', 'Incident Created'),
        ('incident_update', 'Incident Updated'),
        ('incident_assign', 'Incident Assigned'),
        ('incident_delete', 'Incident Deleted'),
        ('export_data', 'Data Export'),
        ('admin_action', 'Admin Action'),
        ('config_change', 'Configuration Change'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, null=True, blank=True)
    
    # Activity details
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    endpoint = models.CharField(max_length=200, blank=True)
    method = models.CharField(max_length=10, blank=True)  # GET, POST, PUT, DELETE
    
    # Request details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    response_status = models.IntegerField(null=True, blank=True)
    
    # Contextual information
    resource_accessed = models.CharField(max_length=200, blank=True)  # What was accessed
    resource_count = models.IntegerField(default=1)  # How many records
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Timing
    duration_ms = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_activity_log'
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} at {self.timestamp}"


class BehaviorAlert(models.Model):
    """
    Real-time alerts for immediate attention behavioral anomalies
    """
    ALERT_TYPES = [
        ('immediate', 'Immediate Threat'),
        ('suspicious', 'Suspicious Activity'),
        ('policy_violation', 'Policy Violation'),
        ('data_exfiltration', 'Potential Data Exfiltration'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_alerts')
    anomaly = models.ForeignKey(BehaviorAnomaly, on_delete=models.CASCADE)
    
    # Alert details
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=10, choices=BehaviorAnomaly.SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Alert status
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_behavior_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Recommended actions
    recommended_actions = models.JSONField(default=list)
    auto_actions_taken = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'behavior_alert'
        verbose_name = 'Behavior Alert'
        verbose_name_plural = 'Behavior Alerts'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['alert_type', 'priority']),
            models.Index(fields=['is_acknowledged', 'created_at']),
        ]

    def __str__(self):
        return f"Alert: {self.title} - {self.user.username}"