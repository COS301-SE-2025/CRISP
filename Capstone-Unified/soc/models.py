"""
SOC (Security Operations Center) Models
Basic SOC system for incident and case management
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models.models import Organization, Indicator, AssetInventory, TTPData

User = get_user_model()


class SOCPlaybook(models.Model):
    """
    SOC Playbooks for standardized incident response procedures
    """
    PLAYBOOK_TYPES = [
        ('malware', 'Malware Response'),
        ('phishing', 'Phishing Response'),
        ('data_breach', 'Data Breach Response'),
        ('ddos', 'DDoS Response'),
        ('insider_threat', 'Insider Threat Response'),
        ('ransomware', 'Ransomware Response'),
        ('apt', 'APT Response'),
        ('custom', 'Custom Playbook'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    playbook_type = models.CharField(max_length=50, choices=PLAYBOOK_TYPES)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='soc_playbooks')
    
    # Playbook content as JSON
    steps = models.JSONField(default=list, help_text="List of playbook steps")
    automation_rules = models.JSONField(default=dict, help_text="Automation configuration")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_playbooks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default='1.0')

    class Meta:
        db_table = 'soc_playbook'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_playbook_type_display()})"


class SOCIncident(models.Model):
    """
    SOC Incident Management
    """
    INCIDENT_STATUS = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('false_positive', 'False Positive'),
    ]

    INCIDENT_PRIORITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    INCIDENT_SEVERITY = [
        ('informational', 'Informational'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    INCIDENT_CATEGORIES = [
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('data_breach', 'Data Breach'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('ddos', 'DDoS Attack'),
        ('insider_threat', 'Insider Threat'),
        ('ransomware', 'Ransomware'),
        ('apt', 'Advanced Persistent Threat'),
        ('vulnerability', 'Vulnerability'),
        ('policy_violation', 'Policy Violation'),
        ('other', 'Other'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Classification
    category = models.CharField(max_length=50, choices=INCIDENT_CATEGORIES)
    priority = models.CharField(max_length=20, choices=INCIDENT_PRIORITY)
    severity = models.CharField(max_length=20, choices=INCIDENT_SEVERITY)
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS, default='new')
    
    # Organization and assignment
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='soc_incidents')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    
    # Relationships
    related_indicators = models.ManyToManyField(Indicator, blank=True, related_name='soc_incidents')
    related_assets = models.ManyToManyField(AssetInventory, blank=True, related_name='soc_incidents')
    related_ttps = models.ManyToManyField(TTPData, blank=True, related_name='soc_incidents')
    playbook = models.ForeignKey(SOCPlaybook, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timeline
    detected_at = models.DateTimeField(default=timezone.now)
    assigned_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # SLA tracking
    sla_deadline = models.DateTimeField(null=True, blank=True)
    is_sla_breached = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_incidents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional data
    source = models.CharField(max_length=100, blank=True, help_text="Source of incident (manual, alert, etc.)")
    external_ticket_id = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'soc_incident'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['incident_id']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.incident_id}: {self.title}"

    def save(self, *args, **kwargs):
        # Auto-generate incident ID if not provided
        if not self.incident_id:
            year = timezone.now().year
            # Get the count of incidents this year for this organization
            count = SOCIncident.objects.filter(
                organization=self.organization,
                created_at__year=year
            ).count() + 1
            self.incident_id = f"INC-{year}-{self.organization.name[:3].upper()}-{count:04d}"
        
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if incident is past SLA deadline"""
        if self.sla_deadline and self.status not in ['resolved', 'closed']:
            return timezone.now() > self.sla_deadline
        return False

    def assign_to(self, user):
        """Assign incident to a user"""
        self.assigned_to = user
        self.assigned_at = timezone.now()
        if self.status == 'new':
            self.status = 'assigned'
        self.save()

    def resolve(self, user, resolution_notes=""):
        """Mark incident as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
        
        # Create activity log
        SOCIncidentActivity.objects.create(
            incident=self,
            user=user,
            activity_type='status_change',
            description=f"Incident resolved by {user.username}",
            details={'notes': resolution_notes, 'previous_status': 'in_progress'}
        )

    def close(self, user, closure_notes=""):
        """Close incident"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()
        
        # Create activity log
        SOCIncidentActivity.objects.create(
            incident=self,
            user=user,
            activity_type='status_change',
            description=f"Incident closed by {user.username}",
            details={'notes': closure_notes, 'previous_status': 'resolved'}
        )


class SOCCase(models.Model):
    """
    SOC Case Management - Groups related incidents for investigation
    """
    CASE_STATUS = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    CASE_PRIORITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Classification
    priority = models.CharField(max_length=20, choices=CASE_PRIORITY)
    status = models.CharField(max_length=20, choices=CASE_STATUS, default='open')
    
    # Organization and assignment
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='soc_cases')
    lead_investigator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leading_cases')
    investigators = models.ManyToManyField(User, blank=True, related_name='investigating_cases')
    
    # Relationships
    incidents = models.ManyToManyField(SOCIncident, blank=True, related_name='cases')
    
    # Timeline
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'soc_case'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.case_id}: {self.title}"

    def save(self, *args, **kwargs):
        # Auto-generate case ID if not provided
        if not self.case_id:
            year = timezone.now().year
            count = SOCCase.objects.filter(
                organization=self.organization,
                created_at__year=year
            ).count() + 1
            self.case_id = f"CASE-{year}-{self.organization.name[:3].upper()}-{count:04d}"
        
        super().save(*args, **kwargs)


class SOCIncidentActivity(models.Model):
    """
    Activity log for SOC incidents
    """
    ACTIVITY_TYPES = [
        ('created', 'Incident Created'),
        ('assigned', 'Assignment Changed'),
        ('status_change', 'Status Changed'),
        ('priority_change', 'Priority Changed'),
        ('comment', 'Comment Added'),
        ('evidence', 'Evidence Added'),
        ('playbook_executed', 'Playbook Executed'),
        ('closed', 'Incident Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(SOCIncident, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    details = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'soc_incident_activity'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.incident.incident_id} - {self.get_activity_type_display()}"


class SOCEvidence(models.Model):
    """
    Evidence collection for incidents and cases
    """
    EVIDENCE_TYPES = [
        ('file', 'File'),
        ('log', 'Log Entry'),
        ('screenshot', 'Screenshot'),
        ('network_capture', 'Network Capture'),
        ('memory_dump', 'Memory Dump'),
        ('artifact', 'Digital Artifact'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    evidence_type = models.CharField(max_length=50, choices=EVIDENCE_TYPES)
    description = models.TextField(blank=True)
    
    # Relationships
    incident = models.ForeignKey(SOCIncident, on_delete=models.CASCADE, related_name='evidence', null=True, blank=True)
    case = models.ForeignKey(SOCCase, on_delete=models.CASCADE, related_name='evidence', null=True, blank=True)
    
    # Chain of custody
    collected_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collected_evidence')
    collected_at = models.DateTimeField(auto_now_add=True)
    
    # File storage (if applicable)
    file_path = models.CharField(max_length=500, blank=True)
    file_hash = models.CharField(max_length=128, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'soc_evidence'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_evidence_type_display()})"


class SOCMetrics(models.Model):
    """
    SOC performance metrics and KPIs
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='soc_metrics')
    
    # Time period
    date = models.DateField()
    period_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    
    # Metrics
    incidents_created = models.IntegerField(default=0)
    incidents_resolved = models.IntegerField(default=0)
    incidents_closed = models.IntegerField(default=0)
    mean_time_to_response = models.FloatField(null=True, blank=True)  # in minutes
    mean_time_to_resolution = models.FloatField(null=True, blank=True)  # in minutes
    sla_breaches = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    
    # Additional metrics as JSON
    additional_metrics = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'soc_metrics'
        unique_together = [['organization', 'date', 'period_type']]
        ordering = ['-date']

    def __str__(self):
        return f"{self.organization.name} - {self.date} ({self.period_type})"
