from django.db import models
from django.utils import timezone
from .institution import Institution

class ThreatFeed(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='owned_feeds', null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    taxii_collection_id = models.CharField(max_length=255, blank=True, null=True)
    taxii_server_url = models.URLField(blank=True, null=True)
    taxii_api_root = models.CharField(max_length=255, blank=True, null=True)
    taxii_username = models.CharField(max_length=255, blank=True, null=True)
    taxii_password = models.CharField(max_length=255, blank=True, null=True)
    last_sync = models.DateTimeField(blank=True, null=True)
    is_external = models.BooleanField(default=False)

    # For Observer pattern implementation
    _observers = []

    class Meta:
        db_table = 'threat_feeds'

    def __str__(self):
        return self.name

    def attach(self, observer):
        """Attach an observer to the subject."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """Detach an observer from the subject."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self):
        """Notify all observers about an event."""
        for observer in self._observers:
            observer.update(self)

    def is_subscribed_by(self, institution):
        """Check if an institution is subscribed to this feed."""
        if hasattr(self, 'subscriptions'):
            return self.subscriptions.filter(institution=institution).exists()
        return False

    def save(self, *args, **kwargs):
        """Override save to notify observers on update."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not is_new:
            self.notify()