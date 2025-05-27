import json
from datetime import timedelta

from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Sum, Q, F, Value, CharField
from django.db.models.functions import TruncDay

from .models import ExternalFeedSource, FeedConsumptionLog
from .tasks import manual_feed_refresh


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin users."""
    
    def test_func(self):
        return self.request.user.is_staff


class HealthCheckView(View):
    """
    Health check endpoint for monitoring systems.
    
    Returns status information about the feed consumption service.
    """
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        # Check if we can connect to the database
        try:
            feed_count = ExternalFeedSource.objects.count()
            
            # Check recent activity
            last_day = timezone.now() - timedelta(days=1)
            recent_logs = FeedConsumptionLog.objects.filter(start_time__gte=last_day).count()
            recent_successful = FeedConsumptionLog.objects.filter(
                start_time__gte=last_day,
                status=FeedConsumptionLog.ConsumptionStatus.SUCCESS
            ).count()
            
            # Calculate success rate
            if recent_logs > 0:
                success_rate = (recent_successful / recent_logs) * 100
            else:
                success_rate = 0
            
            # Check for feeds that haven't been polled recently
            active_feeds = ExternalFeedSource.objects.filter(is_active=True)
            outdated_feeds = 0
            
            for feed in active_feeds:
                if feed.poll_interval == ExternalFeedSource.PollInterval.HOURLY:
                    threshold = timezone.now() - timedelta(hours=2)
                elif feed.poll_interval == ExternalFeedSource.PollInterval.DAILY:
                    threshold = timezone.now() - timedelta(days=2)
                elif feed.poll_interval == ExternalFeedSource.PollInterval.WEEKLY:
                    threshold = timezone.now() - timedelta(days=8)
                else:  # Monthly
                    threshold = timezone.now() - timedelta(days=32)
                
                if not feed.last_poll_time or feed.last_poll_time < threshold:
                    outdated_feeds += 1
            
            status = "healthy"
            if outdated_feeds > 0 or success_rate < 80:
                status = "degraded"
            
            # Return health status
            return JsonResponse({
                'status': status,
                'feed_count': feed_count,
                'active_feeds': active_feeds.count(),
                'recent_polls': recent_logs,
                'success_rate': success_rate,
                'outdated_feeds': outdated_feeds,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e)
            }, status=500)


class FeedSourceListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """View to list all feed sources."""
    
    model = ExternalFeedSource
    template_name = 'feed_consumption/feed_source_list.html'
    context_object_name = 'feed_sources'
    
    def get_queryset(self):
        """Get feed sources with their latest consumption log."""
        return ExternalFeedSource.objects.all().order_by('name')
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        
        # Add category and status filters
        context['categories'] = ExternalFeedSource.FeedCategory.choices
        context['poll_intervals'] = ExternalFeedSource.PollInterval.choices
        
        # Get filter parameters
        category = self.request.GET.get('category')
        interval = self.request.GET.get('interval')
        status = self.request.GET.get('status')
        
        # Apply filters
        queryset = context['feed_sources']
        
        if category:
            queryset = queryset.filter(categories__contains=[category])
            context['selected_category'] = category
        
        if interval:
            queryset = queryset.filter(poll_interval=interval)
            context['selected_interval'] = interval
        
        if status:
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
            context['selected_status'] = status
        
        # Replace original queryset with filtered one
        context['feed_sources'] = queryset
        
        return context


class FeedSourceDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View to show details of a specific feed source."""
    
    model = ExternalFeedSource
    template_name = 'feed_consumption/feed_source_detail.html'
    context_object_name = 'feed_source'
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        
        # Get recent logs
        context['logs'] = self.object.consumption_logs.order_by('-start_time')[:10]
        
        # Calculate success rate
        logs = self.object.consumption_logs.all()
        total_logs = logs.count()
        
        if total_logs > 0:
            successful = logs.filter(
                status=FeedConsumptionLog.ConsumptionStatus.SUCCESS
            ).count()
            partial = logs.filter(
                status=FeedConsumptionLog.ConsumptionStatus.PARTIAL
            ).count()
            success_rate = ((successful + partial) / total_logs) * 100
        else:
            success_rate = 0
        
        context['success_rate'] = success_rate
        
        # Get stats for retrieved/processed objects
        stats = logs.aggregate(
            total_retrieved=Sum('objects_retrieved'),
            total_processed=Sum('objects_processed'),
            total_failed=Sum('objects_failed')
        )
        
        context['stats'] = stats
        
        return context


class RefreshFeedView(LoginRequiredMixin, AdminRequiredMixin, View):
    """View to trigger manual refresh of a feed source."""
    
    def post(self, request, pk):
        """Handle POST requests."""
        feed_source = get_object_or_404(ExternalFeedSource, pk=pk)
        
        # Schedule Celery task
        task = manual_feed_refresh.delay(str(feed_source.id))
        
        messages.success(
            request,
            f"Refresh task scheduled for {feed_source.name}. Check logs for results."
        )
        
        return redirect('feed_consumption:feed_source_detail', pk=pk)


class ConsumptionLogListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """View to list all consumption logs."""
    
    model = FeedConsumptionLog
    template_name = 'feed_consumption/log_list.html'
    context_object_name = 'logs'
    paginate_by = 20
    
    def get_queryset(self):
        """Get consumption logs with filters."""
        queryset = FeedConsumptionLog.objects.all().order_by('-start_time')
        
        # Apply filters
        feed_id = self.request.GET.get('feed_id')
        status = self.request.GET.get('status')
        days = self.request.GET.get('days')
        
        if feed_id:
            queryset = queryset.filter(feed_source_id=feed_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if days:
            try:
                days = int(days)
                cutoff = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(start_time__gte=cutoff)
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['feed_sources'] = ExternalFeedSource.objects.all().order_by('name')
        context['statuses'] = FeedConsumptionLog.ConsumptionStatus.choices
        
        # Add selected filters
        context['selected_feed'] = self.request.GET.get('feed_id')
        context['selected_status'] = self.request.GET.get('status')
        context['selected_days'] = self.request.GET.get('days')
        
        return context


class ConsumptionLogDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View to show details of a specific consumption log."""
    
    model = FeedConsumptionLog
    template_name = 'feed_consumption/log_detail.html'
    context_object_name = 'log'


class DashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Dashboard view with charts and stats."""
    
    template_name = 'feed_consumption/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add dashboard data to context."""
        context = super().get_context_data(**kwargs)
        
        # Get time range (default: last 7 days)
        days = int(self.request.GET.get('days', 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        context['days'] = days
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        # Get feed stats
        feed_stats = {
            'total': ExternalFeedSource.objects.count(),
            'active': ExternalFeedSource.objects.filter(is_active=True).count(),
            'inactive': ExternalFeedSource.objects.filter(is_active=False).count()
        }
        
        # Get category distribution
        categories = {}
        for choice in ExternalFeedSource.FeedCategory.choices:
            category = choice[0]
            categories[category] = ExternalFeedSource.objects.filter(
                categories__contains=[category]
            ).count()
        
        feed_stats['categories'] = categories
        
        # Get consumption stats
        logs = FeedConsumptionLog.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        )
        
        consumption_stats = {
            'total_polls': logs.count(),
            'success': logs.filter(status=FeedConsumptionLog.ConsumptionStatus.SUCCESS).count(),
            'partial': logs.filter(status=FeedConsumptionLog.ConsumptionStatus.PARTIAL).count(),
            'failure': logs.filter(status=FeedConsumptionLog.ConsumptionStatus.FAILURE).count(),
            'objects_retrieved': logs.aggregate(Sum('objects_retrieved'))['objects_retrieved__sum'] or 0,
            'objects_processed': logs.aggregate(Sum('objects_processed'))['objects_processed__sum'] or 0,
            'objects_failed': logs.aggregate(Sum('objects_failed'))['objects_failed__sum'] or 0
        }
        
        # Calculate success rate
        if consumption_stats['total_polls'] > 0:
            consumption_stats['success_rate'] = (
                (consumption_stats['success'] + consumption_stats['partial']) / 
                consumption_stats['total_polls'] * 100
            )
        else:
            consumption_stats['success_rate'] = 0
        
        # Get daily stats for charts
        daily_stats = []
        daily_data = logs.annotate(
            date=TruncDay('start_time')
        ).values('date').annotate(
            success=Count('id', filter=Q(status=FeedConsumptionLog.ConsumptionStatus.SUCCESS)),
            partial=Count('id', filter=Q(status=FeedConsumptionLog.ConsumptionStatus.PARTIAL)),
            failure=Count('id', filter=Q(status=FeedConsumptionLog.ConsumptionStatus.FAILURE)),
            total=Count('id'),
            objects=Sum('objects_processed')
        ).order_by('date')
        
        for day in daily_data:
            if day['total'] > 0:
                success_rate = (day['success'] + day['partial']) / day['total'] * 100
            else:
                success_rate = 0
                
            daily_stats.append({
                'date': day['date'].strftime('%Y-%m-%d'),
                'success': day['success'],
                'partial': day['partial'],
                'failure': day['failure'],
                'total': day['total'],
                'objects': day['objects'] or 0,
                'success_rate': success_rate
            })
        
        # Get top performing feeds
        top_feeds = ExternalFeedSource.objects.annotate(
            log_count=Count('consumption_logs', filter=Q(
                consumption_logs__start_time__gte=start_date,
                consumption_logs__start_time__lte=end_date
            )),
            success_count=Count('consumption_logs', filter=Q(
                consumption_logs__start_time__gte=start_date,
                consumption_logs__start_time__lte=end_date,
                consumption_logs__status=FeedConsumptionLog.ConsumptionStatus.SUCCESS
            )),
            objects_count=Sum('consumption_logs__objects_processed', filter=Q(
                consumption_logs__start_time__gte=start_date,
                consumption_logs__start_time__lte=end_date
            ))
        ).filter(log_count__gt=0).order_by('-objects_count')[:5]
        
        top_feed_data = []
        for feed in top_feeds:
            if feed.log_count > 0:
                success_rate = feed.success_count / feed.log_count * 100
            else:
                success_rate = 0
                
            top_feed_data.append({
                'id': feed.id,
                'name': feed.name,
                'log_count': feed.log_count,
                'success_rate': success_rate,
                'objects_count': feed.objects_count or 0
            })
        
        # Add to context
        context['feed_stats'] = feed_stats
        context['consumption_stats'] = consumption_stats
        context['daily_stats'] = json.dumps(daily_stats)
        context['top_feeds'] = top_feed_data
        
        return context
