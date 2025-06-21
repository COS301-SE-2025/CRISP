"""
Main application views for CRISP Threat Intelligence Platform
"""
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_status(request):
    """API status endpoint"""
    return Response({
        'status': 'active',
        'platform': 'CRISP Threat Intelligence',
        'version': '1.0.0',
        'user': request.user.username,
        'taxii_endpoint': '/taxii2/',
    })


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': '2025-01-21T10:00:00Z'
    })