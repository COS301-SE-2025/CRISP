"""
SOC URL Configuration
URL patterns for SOC API endpoints
"""

from django.urls import path
from soc import api

app_name = 'soc'

urlpatterns = [
    # Incident management
    path('incidents/', api.incidents_list, name='incidents_list'),
    path('incidents/export/', api.incidents_export, name='incidents_export'),
    path('incidents/<uuid:incident_id>/', api.incident_detail, name='incident_detail'),
    path('incidents/<uuid:incident_id>/assign/', api.incident_assign, name='incident_assign'),
    path('incidents/<uuid:incident_id>/comment/', api.incident_add_comment, name='incident_add_comment'),
    
    # Dashboard
    path('dashboard/', api.soc_dashboard, name='soc_dashboard'),
]