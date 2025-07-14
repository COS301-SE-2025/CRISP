"""
URL configuration for CRISP Alerts System
"""

from django.urls import path
from . import alerts_views

urlpatterns = [
    # Alert endpoints
    path('threat/', alerts_views.send_threat_alert, name='alerts-send-threat'),
    path('feed/', alerts_views.send_feed_notification, name='alerts-send-feed'),
    path('test-connection/', alerts_views.test_gmail_connection, name='alerts-test-connection'),
    path('statistics/', alerts_views.get_email_statistics, name='alerts-statistics'),
    path('test-email/', alerts_views.send_test_email, name='alerts-test-email'),
]