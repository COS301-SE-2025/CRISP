"""
Unit tests for Observer pattern
"""
import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
from django.utils import timezone

from core.models.models import ThreatFeed, Institution, Organization


# Create Observer implementations for testing
class InstitutionObserver:
    """Observer for institutions to receive feed updates"""
    
    def __init__(self, institution):
        """Initialize with an institution"""
        self.institution = institution
        self.update_count = 0
        self.last_update_feed = None
    
    def update(self, subject):
        """Handle notification from subject"""
        self.update_count += 1
        self.last_update_feed = subject


class AlertSystemObserver:
    """Observer for alert systems to receive feed updates"""
    
    def __init__(self):
        """Initialize the alert system observer"""
        self.alerts = []
    
    def update(self, subject):
        """Handle notification from subject"""
        self.alerts.append({
            'feed_id': subject.id,
            'feed_name': subject.name,
            'timestamp': timezone.now()
        })


# Decorator to patch the ThreatFeed.save method for testing
def patched_feed_save(func):
    """Decorator to patch the ThreatFeed.save method for testing"""
    def wrapper(*args, **kwargs):
        original_save = ThreatFeed.save
        
        # Replace save with a version that only calls notify
        def mock_save(self, *args, **kwargs):
            is_new = self.pk is None
            if not is_new:
                self.notify()
        
        # Apply the patch
        ThreatFeed.save = mock_save
        
        try:
            # Run the test
            return func(*args, **kwargs)
        finally:
            # Restore the original method
            ThreatFeed.save = original_save
    
    return wrapper


class ObserverPatternTestCase(TestCase):
    """Test cases for Observer pattern"""

    def setUp(self):
        """Set up the test environment"""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()

        # Create Organizations first
        self.organization1 = Organization.objects.create(
            name=f"Test Organization 1 - {timezone.now().timestamp()}",
            description="Test Organization 1",
            identity_class="organization",
            organization_type="university",
            contact_email="test1@example.com"
        )
        
        self.organization2 = Organization.objects.create(
            name=f"Test Organization 2 - {timezone.now().timestamp()}",
            description="Test Organization 2",
            identity_class="organization",
            organization_type="university",
            contact_email="test2@example.com"
        )

        # Create Institutions linked to Organizations
        self.institution1 = Institution.objects.create(
            name="Institution 1",
            description="Test Institution 1",
            contact_email="test1@example.com",
            contact_name="Test Contact 1",
            organization=self.organization1
        )
        
        self.institution2 = Institution.objects.create(
            name="Institution 2",
            description="Test Institution 2",
            contact_email="test2@example.com",
            contact_name="Test Contact 2",
            organization=self.organization2
        )
        
        # Create a test threat feed
        from core.tests.test_data_fixtures import create_test_threat_feed
        self.feed = create_test_threat_feed(owner=self.organization1)

        # Create observers
        self.institution_observer1 = InstitutionObserver(self.institution1)
        self.institution_observer2 = InstitutionObserver(self.institution2)
        self.alert_observer = AlertSystemObserver()

    def test_observer_attachment_detachment(self):
        """Test attaching and detaching observers"""
        # Initially no observers
        self.assertEqual(len(self.feed._observers), 0)
        
        # Attach observers
        self.feed.attach(self.institution_observer1)
        self.feed.attach(self.alert_observer)
        
        # Check that observers were attached
        self.assertEqual(len(self.feed._observers), 2)
        self.assertIn(self.institution_observer1, self.feed._observers)
        self.assertIn(self.alert_observer, self.feed._observers)
        
        # Detach one observer
        self.feed.detach(self.institution_observer1)
        
        # Check that the observer was removed
        self.assertEqual(len(self.feed._observers), 1)
        self.assertNotIn(self.institution_observer1, self.feed._observers)
        self.assertIn(self.alert_observer, self.feed._observers)

    def test_observer_notification(self):
        """Test that observers are notified when feed is updated"""
        # Attach observers
        self.feed.attach(self.institution_observer1)
        self.feed.attach(self.institution_observer2)
        
        # Initial state
        self.assertEqual(self.institution_observer1.update_count, 0)
        
        # Update the feed
        self.feed.name = "Updated Feed Name"
        self.feed.save()
        
        # Check that observers were notified
        self.assertEqual(self.institution_observer1.update_count, 1)
        self.assertEqual(self.institution_observer1.last_update_feed, self.feed)
        
        # New feeds should not trigger notifications during creation
        from core.tests.test_data_fixtures import create_test_threat_feed
        new_feed = create_test_threat_feed()
        
        # Update count should still be 1
        self.assertEqual(self.institution_observer1.update_count, 1)

    def test_is_subscribed_by(self):
        """Test checking if an institution is subscribed to a feed"""
        # Mock the subscriptions manager on the ThreatFeed model
        self.feed.subscriptions = MagicMock()
        
        # Test when institution is subscribed
        self.feed.subscriptions.filter.return_value.exists.return_value = True
        self.assertTrue(self.feed.is_subscribed_by(self.institution1))
        self.feed.subscriptions.filter.assert_called_with(institution=self.institution1)
        
        # Test when institution is not subscribed
        self.feed.subscriptions.filter.return_value.exists.return_value = False
        self.assertFalse(self.feed.is_subscribed_by(self.institution2))
        self.feed.subscriptions.filter.assert_called_with(institution=self.institution2)


class ObserverIntegrationTestCase(TestCase):
    """Integration test cases for Observer pattern"""

    def setUp(self):
        """Set up the test environment."""
        # Clear any existing data
        ThreatFeed.objects.all().delete()
        Institution.objects.all().delete()
        Organization.objects.all().delete()

        # Create an Organization first
        self.organization = Organization.objects.create(
            name=f"Test Organization - {timezone.now().timestamp()}",
            description="Test Organization for integration",
            identity_class="organization",
            organization_type="university",
            contact_email="test@example.com"
        )

        # Create Institutions linked to Organization
        self.institution1 = Institution.objects.create(
            name="Institution 1",
            description="Test Institution 1",
            contact_email="test1@example.com",
            contact_name="Test Contact 1",
            organization=self.organization
        )
        
        self.institution2 = Institution.objects.create(
            name="Institution 2",
            description="Test Institution 2",
            contact_email="test2@example.com",
            contact_name="Test Contact 2"
        )
        
        # Create a test threat feed
        from core.tests.test_data_fixtures import create_test_threat_feed
        self.feed = create_test_threat_feed(owner=self.organization)

    @patched_feed_save
    def test_notification_flow(self):
        """Test the entire notification flow."""
        # Create observers
        observer1 = MagicMock()
        observer2 = MagicMock()
        
        # Attach observers
        self.feed.attach(observer1)
        self.feed.attach(observer2)
        
        # Update the feed
        self.feed.name = "Updated Feed Name"
        self.feed.save()
        
        # Check that observers were notified
        observer1.update.assert_called_once_with(self.feed)
        observer2.update.assert_called_once_with(self.feed)
        
        # Detach one observer
        self.feed.detach(observer1)
        
        # Update again
        self.feed.description = "Updated description"
        self.feed.save()
        
        # First observer should not be called again
        self.assertEqual(observer1.update.call_count, 1)
        
        # Second observer should be called again
        self.assertEqual(observer2.update.call_count, 2)


if __name__ == '__main__':
    unittest.main()