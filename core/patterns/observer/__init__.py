"""
Core Observer Pattern Implementation for CRISP
Provides base classes and interfaces for the observer pattern.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Observer(ABC):
    """
    Abstract base class for all observers in the CRISP system.
    Defines the interface that all observers must implement.
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
    Abstract base class for all subjects in the CRISP observer pattern.
    Manages observer registration and notification.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to this subject.
        
        Args:
            observer: The observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from this subject.
        
        Args:
            observer: The observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_data: Dict[str, Any]) -> None:
        """
        Notify all attached observers of an event.
        
        Args:
            event_data: Dictionary containing event information
        """
        for observer in self._observers:
            try:
                observer.update(self, event_data)
            except Exception as e:
                # Log error but continue notifying other observers
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error notifying observer {observer}: {e}")
    
    def get_observer_count(self) -> int:
        """Get the number of attached observers."""
        return len(self._observers)
    
    def get_observers(self) -> List[Observer]:
        """Get a copy of the observers list."""
        return self._observers.copy()


# Export main classes
__all__ = ['Observer', 'Subject']