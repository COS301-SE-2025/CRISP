"""
Email tracking models for CRISP alerts system
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid


class EmailLog(models.Model):
    """
    Model to track all emails sent through the CRISP system
    """
    
    EMAIL_TYPES = [
        ('threat_alert', 'Threat Alert'),
        ('feed_notification', 'Feed Notification'),
        ('test_email', 'Test Email'),
        ('system_notification', 'System Notification'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES)
    recipient_emails = models.JSONField(help_text="List of recipient email addresses")
    sender_email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(default=timezone.now)
    
    # Email content metadata
    alert_id = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20, blank=True, null=True)
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    # User context
    sent_by = models.ForeignKey(
        'settings.AUTH_USER_MODEL', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sent_emails'
    )
    organization = models.ForeignKey(
        'ut_user_management.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_emails'
    )
    
    class Meta:
        db_table = 'crisp_email_logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['email_type', 'sent_at']),
            models.Index(fields=['status', 'sent_at']),
            models.Index(fields=['organization', 'sent_at']),
        ]
    
    def __str__(self):
        recipient_count = len(self.recipient_emails) if self.recipient_emails else 0
        return f"{self.get_email_type_display()} to {recipient_count} recipients - {self.status}"
    
    @property
    def recipient_count(self):
        """Get number of recipients"""
        return len(self.recipient_emails) if self.recipient_emails else 0
    
    @classmethod
    def get_statistics(cls, organization=None, days=30):
        """Get email statistics for organization or system-wide"""
        from datetime import timedelta
        
        queryset = cls.objects.all()
        if organization:
            queryset = queryset.filter(organization=organization)
        
        # Filter by date range
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(sent_at__gte=start_date)
        
        # Calculate statistics
        total_sent = queryset.filter(status='sent').count()
        threat_alerts = queryset.filter(email_type='threat_alert', status='sent').count()
        feed_notifications = queryset.filter(email_type='feed_notification', status='sent').count()
        test_emails = queryset.filter(email_type='test_email', status='sent').count()
        
        # Get last email sent
        last_email = queryset.filter(status='sent').first()
        
        return {
            'total_emails_sent': total_sent,
            'threat_alerts_sent': threat_alerts,
            'feed_notifications_sent': feed_notifications,
            'test_emails_sent': test_emails,
            'last_email_sent': last_email.sent_at if last_email else None,
            'failed_emails': queryset.filter(status='failed').count(),
        }