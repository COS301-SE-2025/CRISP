from django.db import models
from django.utils import timezone
from core.patterns.observer.threat_feed import ThreatFeed

class TTPData(models.Model):
    """
    Model representing Tactics, Techniques, and Procedures (TTPs) data.
    """
    MITRE_TACTIC_CHOICES = [
        ('reconnaissance', 'Reconnaissance'),
        ('resource_development', 'Resource Development'),
        ('initial_access', 'Initial Access'),
        ('execution', 'Execution'),
        ('persistence', 'Persistence'),
        ('privilege_escalation', 'Privilege Escalation'),
        ('defense_evasion', 'Defense Evasion'),
        ('credential_access', 'Credential Access'),
        ('discovery', 'Discovery'),
        ('lateral_movement', 'Lateral Movement'),
        ('collection', 'Collection'),
        ('command_and_control', 'Command and Control'),
        ('exfiltration', 'Exfiltration'),
        ('impact', 'Impact'),
        ('other', 'Other'),
    ]
    
    threat_feed = models.ForeignKey(ThreatFeed, on_delete=models.CASCADE, related_name='ttp_data')
    name = models.CharField(max_length=255)
    description = models.TextField()
    mitre_tactic = models.CharField(max_length=50, choices=MITRE_TACTIC_CHOICES, null=True, blank=True)
    mitre_technique_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    stix_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_anonymized = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ttp_data'
        indexes = [
            models.Index(fields=['mitre_technique_id']),
            models.Index(fields=['stix_id']),
        ]
        
    def __str__(self):
        return self.name

    def to_stix(self):
        """Convert to STIX Attack Pattern object"""
        # This will be implemented using the Factory pattern
        pass