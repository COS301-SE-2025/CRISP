from abc import ABC, abstractmethod
from typing import Dict, Any


class Subject(ABC):
    """
    Abstract subject interface for Observer pattern
    """
    
    @abstractmethod
    def add_observer(self, observer):
        """Add an observer to this subject"""
        pass
    
    @abstractmethod
    def remove_observer(self, observer):
        """Remove an observer from this subject"""
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: str, data: Dict[str, Any]):
        """Notify all observers of a change"""
        pass


class Observer(ABC):
    """
    Abstract observer interface for Observer pattern
    """
    
    @abstractmethod
    def update(self, subject: Subject, event_type: str, data: Dict[str, Any]):
        """Update observer with new data from subject"""
        pass