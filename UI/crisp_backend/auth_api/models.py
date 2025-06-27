from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Custom User Model
class CrispUser(AbstractUser):
    # Basic role field
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('analyst', 'Security Analyst'),
        ('user', 'Standard User'),
        ('guest', 'Guest'),
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='analyst')
    
    # Additional fields
    organization = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    # Security fields
    last_password_change = models.DateTimeField(null=True, blank=True)
    require_password_change = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    
    # Optional: Additional fields you might want
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Add the is_admin field that's missing
    is_admin = models.BooleanField(default=False)
    
    # You can use this to determine if a user is an admin
    def is_admin_user(self):
        return self.is_admin or self.is_staff or self.role.lower() in ['admin', 'administrator']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'CRISP User'
        verbose_name_plural = 'CRISP Users'

# Indicator of Compromise (IoC) model
class IndicatorOfCompromise(models.Model):
    TYPE_CHOICES = (
        ('ip', 'IP Address'),
        ('domain', 'Domain'),
        ('url', 'URL'),
        ('hash', 'File Hash'),
        ('email', 'Email'),
        ('other', 'Other'),
    )
    SEVERITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('review', 'Under Review'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    source = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(CrispUser, on_delete=models.SET_NULL, null=True, related_name='created_iocs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.value} ({self.get_severity_display()})"
    
    class Meta:
        verbose_name = 'Indicator of Compromise'
        verbose_name_plural = 'Indicators of Compromise'
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['value']),
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
        ]
        unique_together = ['type', 'value']

# Organization model
class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    trust_level = models.PositiveSmallIntegerField(default=50)  # 0-100
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

# ThreatFeed model
class ThreatFeed(models.Model):
    TYPE_CHOICES = (
        ('stix_taxii', 'STIX/TAXII'),
        ('misp', 'MISP'),
        ('custom', 'Custom'),
        ('internal', 'Internal'),
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    feed_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    url = models.URLField(blank=True)
    api_key = models.CharField(max_length=512, blank=True)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_feed_type_display()})"