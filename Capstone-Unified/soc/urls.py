"""
SOC URL Configuration
URL patterns for SOC API endpoints
"""

from django.urls import path
from soc import api

urlpatterns = [
    # Incident management
    path('incidents/', api.incidents_list, name='incidents_list'),
    path('incidents/export/', api.incidents_export, name='incidents_export'),
    path('incidents/<uuid:incident_id>/', api.incident_detail, name='incident_detail'),
    path('incidents/<uuid:incident_id>/assign/', api.incident_assign, name='incident_assign'),
    path('incidents/<uuid:incident_id>/comment/', api.incident_add_comment, name='incident_add_comment'),
    
    # Enhanced SOC Dashboard
    path('dashboard/', api.soc_dashboard, name='soc_dashboard'),
    path('threat-map/', api.threat_map, name='threat_map'),
    path('system-health/', api.system_health, name='system_health'),
    path('top-threats/', api.top_threats, name='top_threats'),
    path('mitre-tactics/', api.mitre_tactics, name='mitre_tactics'),
    path('threat-intelligence/', api.threat_intelligence, name='threat_intelligence'),
    
    # IOC Integration
    path('live-ioc-alerts/', api.live_ioc_alerts, name='live_ioc_alerts'),
    path('ioc-incident-correlation/', api.ioc_incident_correlation, name='ioc_incident_correlation'),
]