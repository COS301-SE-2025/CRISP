from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q

from .models import ExternalFeedSource, FeedConsumptionLog
from .serializers import (
    ExternalFeedSourceSerializer,
    FeedConsumptionLogSerializer,
    FeedCollectionSerializer
)
from .tasks import manual_feed_refresh
from .taxii_client import TaxiiClient, TaxiiClientError


class ExternalFeedSourceViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing external feed sources.
    
    Allows CRUD operations on feed sources and additional actions
    like refreshing a feed, discovering collections, and viewing stats.
    """
    queryset = ExternalFeedSource.objects.all()
    serializer_class = ExternalFeedSourceSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Override to set the added_by field to the current user."""
        serializer.save(added_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """
        Manually refresh a feed source.
        
        Triggers a Celery task to consume the feed immediately.
        """
        feed_source = self.get_object()
        task = manual_feed_refresh.delay(str(feed_source.id))
        
        return Response({
            'status': 'refresh scheduled',
            'task_id': task.id,
            'feed_id': str(feed_source.id),
            'feed_name': feed_source.name
        })
    
    @action(detail=True, methods=['get'])
    def collections(self, request, pk=None):
        """
        List available collections for a feed source.
        
        Connects to the TAXII server and retrieves collection information.
        """
        feed_source = self.get_object()
        
        try:
            client = TaxiiClient(feed_source)
            collections = client.get_collections()
            
            serializer = FeedCollectionSerializer(collections, many=True)
            return Response(serializer.data)
            
        except TaxiiClientError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_collection(self, request, pk=None):
        """
        Set the collection ID for a feed source.
        
        Updates which collection will be polled for this feed.
        """
        feed_source = self.get_object()
        collection_id = request.data.get('collection_id')
        
        if not collection_id:
            raise ValidationError({'collection_id': 'This field is required.'})
        
        feed_source.collection_id = collection_id
        feed_source.save(update_fields=['collection_id'])
        
        return Response({
            'status': 'collection updated',
            'feed_id': str(feed_source.id),
            'collection_id': collection_id
        })
    
    @action(detail=True, methods=['get'])
    def discover(self, request, pk=None):
        """
        Perform TAXII discovery for a feed source.
        
        Connects to the TAXII server and retrieves discovery information.
        """
        feed_source = self.get_object()
        
        try:
            client = TaxiiClient(feed_source)
            discovery_info = client.discover()
            
            return Response(discovery_info)
            
        except TaxiiClientError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about feed sources.
        
        Returns counts by category, poll interval, and status.
        """
        total = ExternalFeedSource.objects.count()
        active = ExternalFeedSource.objects.filter(is_active=True).count()
        
        # Count by category
        categories = {}
        for choice in ExternalFeedSource.FeedCategory.choices:
            category = choice[0]
            categories[category] = ExternalFeedSource.objects.filter(
                categories__contains=[category]
            ).count()
        
        # Count by poll interval
        intervals = {}
        for choice in ExternalFeedSource.PollInterval.choices:
            interval = choice[0]
            intervals[interval] = ExternalFeedSource.objects.filter(
                poll_interval=interval
            ).count()
        
        # Count by last poll status
        status_counts = {
            'success': 0,
            'partial': 0,
            'failure': 0,
            'never_polled': 0
        }
        
        # Get feeds with their latest log
        feeds_with_logs = ExternalFeedSource.objects.annotate(
            log_count=Count('consumption_logs')
        )
        
        for feed in feeds_with_logs:
            if feed.log_count == 0:
                status_counts['never_polled'] += 1
            else:
                latest_log = feed.consumption_logs.order_by('-start_time').first()
                if latest_log.status == FeedConsumptionLog.ConsumptionStatus.SUCCESS:
                    status_counts['success'] += 1
                elif latest_log.status == FeedConsumptionLog.ConsumptionStatus.PARTIAL:
                    status_counts['partial'] += 1
                else:
                    status_counts['failure'] += 1
        
        return Response({
            'total': total,
            'active': active,
            'by_category': categories,
            'by_interval': intervals,
            'by_status': status_counts
        })


class FeedConsumptionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for viewing feed consumption logs.
    
    Provides read-only access to consumption logs with filtering
    by feed source, status, and date range.
    """
    queryset = FeedConsumptionLog.objects.all().order_by('-start_time')
    serializer_class = FeedConsumptionLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by feed source
        feed_source_id = self.request.query_params.get('feed_source')
        if feed_source_id:
            queryset = queryset.filter(feed_source_id=feed_source_id)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about feed consumption logs.
        
        Returns counts by status, daily success rates, and error trends.
        """
        # Get time range parameters
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=days)
        
        # Base queryset within time range
        queryset = FeedConsumptionLog.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        )
        
        # Count by status
        status_counts = {
            'success': queryset.filter(status=FeedConsumptionLog.ConsumptionStatus.SUCCESS).count(),
            'partial': queryset.filter(status=FeedConsumptionLog.ConsumptionStatus.PARTIAL).count(),
            'failure': queryset.filter(status=FeedConsumptionLog.ConsumptionStatus.FAILURE).count(),
            'total': queryset.count()
        }
        
        # Calculate success rate
        if status_counts['total'] > 0:
            success_rate = (status_counts['success'] + status_counts['partial']) / status_counts['total'] * 100
        else:
            success_rate = 0
        
        # Get daily stats
        daily_stats = []
        for day in range(days):
            day_start = end_date - timezone.timedelta(days=day+1)
            day_end = end_date - timezone.timedelta(days=day)
            
            day_logs = queryset.filter(
                start_time__gte=day_start,
                start_time__lt=day_end
            )
            
            day_success = day_logs.filter(status=FeedConsumptionLog.ConsumptionStatus.SUCCESS).count()
            day_partial = day_logs.filter(status=FeedConsumptionLog.ConsumptionStatus.PARTIAL).count()
            day_failure = day_logs.filter(status=FeedConsumptionLog.ConsumptionStatus.FAILURE).count()
            day_total = day_logs.count()
            
            if day_total > 0:
                day_success_rate = (day_success + day_partial) / day_total * 100
            else:
                day_success_rate = 0
            
            daily_stats.append({
                'date': day_start.date().isoformat(),
                'success': day_success,
                'partial': day_partial,
                'failure': day_failure,
                'total': day_total,
                'success_rate': day_success_rate
            })
        
        # Get object counts
        object_stats = {
            'total_retrieved': queryset.aggregate(sum=models.Sum('objects_retrieved'))['sum'] or 0,
            'total_processed': queryset.aggregate(sum=models.Sum('objects_processed'))['sum'] or 0,
            'total_failed': queryset.aggregate(sum=models.Sum('objects_failed'))['sum'] or 0
        }
        
        # Get most common error patterns
        error_logs = queryset.exclude(error_message='').values('error_message')
        error_patterns = {}
        
        for log in error_logs:
            error_msg = log['error_message']
            # Extract first line or first 100 chars for grouping
            error_key = error_msg.split('\n')[0][:100]
            
            if error_key in error_patterns:
                error_patterns[error_key] += 1
            else:
                error_patterns[error_key] = 1
        
        # Convert to sorted list
        error_trends = [
            {'error': k, 'count': v}
            for k, v in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
        ][:5]  # Top 5 errors
        
        return Response({
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            },
            'status_counts': status_counts,
            'success_rate': success_rate,
            'daily_stats': daily_stats,
            'object_stats': object_stats,
            'error_trends': error_trends
        })