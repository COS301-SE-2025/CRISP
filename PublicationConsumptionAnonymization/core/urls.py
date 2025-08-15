"""
Core app URL configuration
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from core.models.models import ThreatFeed, Indicator, TTPData

@api_view(['GET'])
def status_view(request):
    """Simple status endpoint"""
    return Response({
        'status': 'active',
        'app': 'CRISP Core',
        'threat_feeds': ThreatFeed.objects.count(),
        'indicators': Indicator.objects.count(),
        'ttps': TTPData.objects.count()
    })

urlpatterns = [
    path('', status_view, name='core-status'),
]