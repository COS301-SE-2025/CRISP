from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
import json

from .models import ExternalFeedSource, FeedConsumptionLog

def health_check(request):
    """
    Health check endpoint for monitoring
    """
    # Check if we have any active feed sources
    active_feeds = ExternalFeedSource.objects.filter(is_active=True).count()
    
    # Check recent log entries for failures
    one_day_ago = timezone.now() - timezone.timedelta(days=1)
    recent_failures = FeedConsumptionLog.objects.filter(
        status=FeedConsumptionLog.Status.FAILED,
        created_at__gte=one_day_ago
    ).count()
    
    # Get last successful poll
    last_success = FeedConsumptionLog.objects.filter(
        status=FeedConsumptionLog.Status.COMPLETED
    ).order_by('-end_time').first()
    
    status = "healthy" if recent_failures < active_feeds else "degraded"
    if active_feeds == 0:
        status = "no active feeds"
    
    response = {
        "status": status,
        "active_feeds": active_feeds,
        "recent_failures": recent_failures,
        "last_successful_poll": last_success.end_time.isoformat() if last_success else None,
        "timestamp": timezone.now().isoformat()
    }
    
    return JsonResponse(response)

@login_required
def dashboard(request):
    """
    Dashboard view showing feed consumption statistics
    """
    # Get high level stats
    total_feeds = ExternalFeedSource.objects.count()
    active_feeds = ExternalFeedSource.objects.filter(is_active=True).count()
    
    # Get feed consumption statistics
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    consumption_stats = {
        "total_logs": FeedConsumptionLog.objects.filter(created_at__gte=thirty_days_ago).count(),
        "completed": FeedConsumptionLog.objects.filter(status=FeedConsumptionLog.Status.COMPLETED, created_at__gte=thirty_days_ago).count(),
        "failed": FeedConsumptionLog.objects.filter(status=FeedConsumptionLog.Status.FAILED, created_at__gte=thirty_days_ago).count(),
        "objects_processed": FeedConsumptionLog.objects.filter(created_at__gte=thirty_days_ago).aggregate(total=Sum('objects_processed'))['total'] or 0,
        "objects_added": FeedConsumptionLog.objects.filter(created_at__gte=thirty_days_ago).aggregate(total=Sum('objects_added'))['total'] or 0,
    }
    
    # Get feed sources with most objects added
    top_feeds = FeedConsumptionLog.objects.filter(
        status=FeedConsumptionLog.Status.COMPLETED,
        created_at__gte=thirty_days_ago
    ).values('feed_source__name').annotate(
        total_objects=Sum('objects_added')
    ).order_by('-total_objects')[:5]
    
    # Get recent failures for notification
    recent_failures = FeedConsumptionLog.objects.filter(
        status=FeedConsumptionLog.Status.FAILED,
        created_at__gte=timezone.now() - timezone.timedelta(days=1)
    ).select_related('feed_source')[:10]
    
    # Pass data to template
    context = {
        'total_feeds': total_feeds,
        'active_feeds': active_feeds,
        'consumption_stats': consumption_stats,
        'top_feeds': top_feeds,
        'recent_failures': recent_failures,
    }
    
    return render(request, 'feed_consumption/dashboard.html', context)
