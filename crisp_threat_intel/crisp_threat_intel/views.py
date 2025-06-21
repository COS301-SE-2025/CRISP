"""
Main application views for CRISP Threat Intelligence Platform
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from crisp_threat_intel.models import Organization, Collection, Feed, STIXObject


def home(request):
    """Home page view"""
    context = {
        'title': 'CRISP Threat Intelligence Platform',
        'description': 'Educational threat intelligence sharing platform'
    }
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    # Get user's organization
    try:
        org = Organization.objects.filter(created_by=request.user).first()
        if not org:
            org = Organization.objects.first()  # Fallback
    except:
        org = None
    
    # Get statistics
    stats = {
        'organizations': Organization.objects.count(),
        'collections': Collection.objects.count(),
        'feeds': Feed.objects.count(),
        'stix_objects': STIXObject.objects.count(),
    }
    
    # Get recent objects
    recent_objects = STIXObject.objects.order_by('-created_at')[:10]
    recent_feeds = Feed.objects.order_by('-last_published_time')[:5]
    
    context = {
        'organization': org,
        'stats': stats,
        'recent_objects': recent_objects,
        'recent_feeds': recent_feeds,
    }
    return render(request, 'dashboard.html', context)


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