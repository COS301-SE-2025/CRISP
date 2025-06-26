"""
Observer Pattern Package Initialization
File: core/patterns/observer/__init__.py

This package implements the Observer pattern for CRISP threat intelligence sharing.
"""

from .subject import Subject
from .observer import Observer
from .threat_feed import ThreatFeedSubject
from .institution_observer import InstitutionObserver
from .alert_system_observer import AlertSystemObserver
from .email_notification_observer import EmailNotificationObserver

__all__ = [
    'Subject',
    'Observer',
    'ThreatFeedSubject',
    'InstitutionObserver',
    'AlertSystemObserver',
    'EmailNotificationObserver'
]