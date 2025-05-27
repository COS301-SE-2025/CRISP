import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Organization

class TrustRelationship(models.Model):
    """
    Model representing trust relationships between organizations.
    Trust level influences the level of anonymization applied to shared data.
    """
    TRUST_LEVEL_CHOICES = (
        ('none', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='trusts'
    )
    target_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='trusted_by'
    )
    trust_level_name = models.CharField(
        max_length=20, 
        choices=TRUST_LEVEL_CHOICES, 
        default='medium'
    )
    trust_level = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5
    )
    anonymization_strategy = models.CharField(
        max_length=50, 
        default='partial'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('source_organization', 'target_organization')
        indexes = [
            models.Index(fields=['source_organization', 'target_organization']),
            models.Index(fields=['trust_level']),
        ]
    
    def __str__(self):
        return f"{self.source_organization} trusts {self.target_organization} ({self.trust_level_name})"
    
    def save(self, *args, **kwargs):
        # Set trust level based on trust level name if not provided
        if not self.trust_level:
            trust_levels = settings.TRUST_SETTINGS.get('TRUST_LEVELS', {})
            self.trust_level = trust_levels.get(self.trust_level_name, 0.5)
        
        # Set anonymization strategy based on trust level
        if self.trust_level >= 0.8:
            self.anonymization_strategy = 'none'
        elif self.trust_level >= 0.4:
            self.anonymization_strategy = 'partial'
        else:
            self.anonymization_strategy = 'full'
            
        super().save(*args, **kwargs)


class TrustGroup(models.Model):
    """
    Model representing a group of organizations with similar trust levels.
    Useful for applying trust settings to multiple organizations at once.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    default_trust_level_name = models.CharField(
        max_length=20, 
        choices=TrustRelationship.TRUST_LEVEL_CHOICES, 
        default='medium'
    )
    default_trust_level = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class TrustGroupMembership(models.Model):
    """
    Model representing membership of an organization in a trust group.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trust_group = models.ForeignKey(
        TrustGroup, 
        on_delete=models.CASCADE, 
        related_name='memberships'
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='trust_group_memberships'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('trust_group', 'organization')
        
    def __str__(self):
        return f"{self.organization} in {self.trust_group}"