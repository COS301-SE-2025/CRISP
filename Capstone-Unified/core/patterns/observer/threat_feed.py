from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Observer(ABC):
    """
    Abstract base class for observers in the CRISP system.
    """
    
    @abstractmethod
    def update(self, subject: 'Subject', event_data: Dict[str, Any]) -> None:
        """
        Update method called when the subject notifies observers.
        
        Args:
            subject: The subject object that triggered the notification
            event_data: Dictionary containing event information and context
        """
        pass


class Subject(ABC):
    """
    Abstract base class for subjects in the observer pattern.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer to this subject."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer from this subject."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_data: Dict[str, Any]) -> None:
        """Notify all attached observers of an event."""
        for observer in self._observers:
            try:
                observer.update(self, event_data)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error notifying observer {observer}: {e}")


class ThreatFeedObserver(Observer):
    """
    Base observer for threat feed events.
    Concrete implementations should inherit from this.
    """
    
    def __init__(self, observer_id: str):
        self.observer_id = observer_id
    
    def update(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """
        Handle threat feed updates.
        Override in concrete implementations.
        """
        pass
    
    def get_observer_id(self) -> str:
        """Get unique identifier for this observer."""
        return self.observer_id