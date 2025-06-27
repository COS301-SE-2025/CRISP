"""
Unit tests for Observer pattern
"""
import unittest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
from django.utils import timezone

from core.models.threat_feed import ThreatFeed
from core.models.auth import Organization
from .test_base import CrispTestCase


# Create Observer implementations for testing
class OrganizationObserver:
    """Observer for organizations to receive feed updates"""
    
    def __init__(self, organization):
        """Initialize with an organization"""
        self.organization = organization
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


class ObserverPatternTestCase(CrispTestCase):
    """Test cases for Observer pattern"""

    def setUp(self):
        """Set up the test environment"""
        super().setUp()

        self.organization1 = self.create_unique_organization("Organization 1")
        self.organization2 = self.create_unique_organization("Organization 2")
        
        # Create a test threat feed with Organization owner
        self.feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Observer Pattern",
            owner=self.organization1,
            is_public=True
        )
        
        # Create observers
        self.organization_observer1 = OrganizationObserver(self.organization1)
        self.organization_observer2 = OrganizationObserver(self.organization2)
        self.alert_observer = AlertSystemObserver()
        
        # Attach observers
        self.feed.attach(self.organization_observer1)
        self.feed.attach(self.organization_observer2)
        self.feed.attach(self.alert_observer)
        
        # Store original _observers to restore after each test
        self.original_observers = self.feed._observers.copy()

    def tearDown(self):
        """Clean up after the test"""
        # Restore original observers
        self.feed._observers = self.original_observers

    def test_attach_observer(self):
        """Test attaching an observer"""
        # Create a new observer
        new_observer = OrganizationObserver(MagicMock())
        
        # Initial state
        observer_count = len(self.feed._observers)
        
        # Attach the observer
        self.feed.attach(new_observer)
        
        # Check that the observer was attached
        self.assertEqual(len(self.feed._observers), observer_count + 1)
        self.assertIn(new_observer, self.feed._observers)
        
        # Attaching the same observer again should not duplicate
        self.feed.attach(new_observer)
        self.assertEqual(len(self.feed._observers), observer_count + 1)

    def test_detach_observer(self):
        """Test detaching an observer"""
        # Initial state
        observer_count = len(self.feed._observers)
        self.assertIn(self.organization_observer1, self.feed._observers)
        
        # Detach an observer
        self.feed.detach(self.organization_observer1)
        
        # Check that the observer was detached
        self.assertEqual(len(self.feed._observers), observer_count - 1)
        self.assertNotIn(self.organization_observer1, self.feed._observers)
        
        # Detaching a non-attached observer
        self.feed.detach(MagicMock())

    def test_notify_observers(self):
        """Test notifying observers"""
        # Initial state
        self.assertEqual(self.organization_observer1.update_count, 0)
        self.assertEqual(self.organization_observer2.update_count, 0)
        self.assertEqual(len(self.alert_observer.alerts), 0)
        
        # Notify observers
        self.feed.notify()
        
        # Check that observers were notified
        self.assertEqual(self.organization_observer1.update_count, 1)
        self.assertEqual(self.organization_observer2.update_count, 1)
        self.assertEqual(len(self.alert_observer.alerts), 1)
        
        # Check that the correct feed was passed to the observers
        self.assertEqual(self.organization_observer1.last_update_feed, self.feed)
        self.assertEqual(self.organization_observer2.last_update_feed, self.feed)
        self.assertEqual(self.alert_observer.alerts[0]['feed_id'], self.feed.id)
        self.assertEqual(self.alert_observer.alerts[0]['feed_name'], self.feed.name)

    def test_save_triggers_notify(self):
        """Test that saving a ThreatFeed triggers notification."""
        # Initial state
        self.assertEqual(self.organization_observer1.update_count, 0)
        
        # Update the feed
        self.feed.name = "Updated Feed Name"
        self.feed.save()
        
        # Check that observers were notified
        self.assertEqual(self.organization_observer1.update_count, 1)
        self.assertEqual(self.organization_observer1.last_update_feed, self.feed)
        
        # New feeds should not trigger notifications during creation
        new_feed = ThreatFeed.objects.create(
            name="New Feed",
            description="New Test Feed",
            owner=self.organization2
        )
        
        # Update count should still be 1 (no new notifications)
        self.assertEqual(self.organization_observer1.update_count, 1)

    def test_is_subscribed_by(self):
        """Test checking if an organization is subscribed to a feed"""
        # Create a mock FeedSubscription model 
        class MockFeedSubscription:
            def __init__(self, feed, organization):
                self.feed = feed
                self.organization = organization
        
        # Mock the subscriptions manager on the ThreatFeed model
        self.feed.subscriptions = MagicMock()
        
        # Test when organization is subscribed
        self.feed.subscriptions.filter.return_value.exists.return_value = True
        self.assertTrue(self.feed.is_subscribed_by(self.organization1))
        self.feed.subscriptions.filter.assert_called_with(institution=self.organization1)
        
        # Test when organization is not subscribed
        self.feed.subscriptions.filter.return_value.exists.return_value = False
        self.assertFalse(self.feed.is_subscribed_by(self.organization2))
        self.feed.subscriptions.filter.assert_called_with(institution=self.organization2)


# This test uses the patched_feed_save decorator to test the notification behavior
# without actually saving to the database
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


class ObserverIntegrationTestCase(CrispTestCase):
    """Integration test cases for Observer pattern"""

    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        # Create test organizations
        self.organization1 = self.create_unique_organization("Organization 1")
        self.organization2 = self.create_unique_organization("Organization 2")
        
        # Create a test threat feed
        self.feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Observer Pattern",
            owner=self.organization1,
            is_public=True
        )

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