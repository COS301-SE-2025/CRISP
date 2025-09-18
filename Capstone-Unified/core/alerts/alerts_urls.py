"""
URL configuration for CRISP Alerts System
"""

from django.urls import path
from . import alerts_views

urlpatterns = [
    # Alert endpoints
    path('list/', alerts_views.get_alerts_list, name='alerts-list'),
    path('<uuid:notification_id>/mark-read/', alerts_views.mark_notification_read, name='alerts-mark-read'),
    path('<uuid:notification_id>/delete/', alerts_views.delete_notification, name='alerts-delete'),
    path('mark-all-read/', alerts_views.mark_all_notifications_read, name='alerts-mark-all-read'),
    
    # Email alert endpoints
    path('threat/', alerts_views.send_threat_alert, name='alerts-send-threat'),
    path('feed/', alerts_views.send_feed_notification, name='alerts-send-feed'),
    path('test-connection/', alerts_views.test_gmail_connection, name='alerts-test-connection'),
    path('statistics/', alerts_views.get_email_statistics, name='alerts-statistics'),
    path('test-email/', alerts_views.send_test_email, name='alerts-test-email'),
    
    # Notification management endpoints  
    path('preferences/', alerts_views.get_notification_preferences, name='alerts-get-preferences'),
    path('preferences/update/', alerts_views.update_notification_preferences, name='alerts-update-preferences'),
]