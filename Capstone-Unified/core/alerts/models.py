"""
Notification and Alert models for CRISP system
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Notification(models.Model):
    """
    Model to store system notifications for users
    """
    
    NOTIFICATION_TYPES = [
        ('feed_update', 'Feed Update'),
        ('threat_alert', 'Threat Alert'),
        ('user_invitation', 'User Invitation'),
        ('system_alert', 'System Alert'),
        ('trust_relationship', 'Trust Relationship'),
        ('security_alert', 'Security Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Notification content
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Recipients
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    related_object_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Email integration
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'crisp_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['priority', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @classmethod
    def create_feed_update_notification(cls, feed, users, new_indicators_count=0, updated_indicators_count=0):
        """Create feed update notifications for multiple users"""
        notifications = []
        
        title = f"Feed Update: {feed.name}"
        message = f"Feed '{feed.name}' has been updated with {new_indicators_count} new indicators"
        if updated_indicators_count > 0:
            message += f" and {updated_indicators_count} updated indicators"
        message += "."
        
        for user in users:
            notification = cls.objects.create(
                notification_type='feed_update',
                title=title,
                message=message,
                recipient=user,
                organization=user.organization,
                related_object_type='ThreatFeed',
                related_object_id=str(feed.id),
                metadata={
                    'feed_name': feed.name,
                    'feed_id': str(feed.id),
                    'new_indicators': new_indicators_count,
                    'updated_indicators': updated_indicators_count,
                }
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def get_unread_for_user(cls, user):
        """Get unread notifications for a user"""
        return cls.objects.filter(
            recipient=user,
            is_read=False
        ).exclude(
            expires_at__lt=timezone.now()
        )
    
    @classmethod
    def get_recent_for_user(cls, user, days=30):
        """Get recent notifications for a user"""
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        
        return cls.objects.filter(
            recipient=user,
            created_at__gte=start_date
        ).exclude(
            expires_at__lt=timezone.now()
        )


class FeedUpdateSubscription(models.Model):
    """
    Model to track user subscriptions to feed updates
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feed_subscriptions'
    )
    
    # Can be specific feed or organization-wide
    threat_feed = models.ForeignKey(
        'core.ThreatFeed',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscribers'
    )
    
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feed_subscriptions'
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    
    # Frequency control
    FREQUENCY_CHOICES = [
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ]
    notification_frequency = models.CharField(
        max_length=15, 
        choices=FREQUENCY_CHOICES, 
        default='immediate'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'crisp_feed_subscriptions'
        unique_together = ['user', 'threat_feed', 'organization']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['threat_feed', 'is_active']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        if self.threat_feed:
            return f"{self.user.username} -> {self.threat_feed.name}"
        else:
            return f"{self.user.username} -> {self.organization.name} (all feeds)"