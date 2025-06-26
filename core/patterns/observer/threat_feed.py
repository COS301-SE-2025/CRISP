"""
Observer pattern implementation for ThreatFeed updates.
This module provides observer functionality without duplicating the model.
"""

class ThreatFeedSubject:
    """
    Subject class for ThreatFeed Observer pattern implementation.
    This avoids model conflicts by providing observer functionality separately.
    """
    
    def __init__(self):
        self._observers = []
    
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
    
    def notify(self, threat_feed=None):
        """Notify all observers about an event."""
        for observer in self._observers:
            observer.update(threat_feed)


class ThreatFeedObserver:
    """
    Abstract base class for ThreatFeed observers.
    """
    
    def update(self, threat_feed):
        """Called when the ThreatFeed subject notifies observers."""
        raise NotImplementedError("Subclasses must implement update()")


# Global subject instance for ThreatFeed events
threat_feed_subject = ThreatFeedSubject()