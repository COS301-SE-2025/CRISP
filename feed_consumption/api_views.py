"""API views for feed consumption service"""
from django.db.models import Count, Avg, Sum, F
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound

from .models import ExternalFeedSource, FeedConsumptionLog
from .serializers import (
    ExternalFeedSourceSerializer, FeedConsumptionLogSerializer,
    CollectionSerializer, ApiRootSerializer, DiscoverySerializer
)
from .tasks import manual_feed_refresh
from .taxii_client_service import TaxiiClient

class ExternalFeedSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for external feed sources"""
    queryset = ExternalFeedSource.objects.all().order_by('-created_at')
    serializer_class = ExternalFeedSourceSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Add current user as the creator"""
        serializer.save(added_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Trigger an immediate refresh of the feed"""
        feed = self.get_object()
        
        if not feed.collection_id:
            return Response(
                {"detail": "Feed has no collection set. Set a collection first."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Start the Celery task
        task = manual_feed_refresh.delay(str(feed.id))
        
        return Response({
            "message": "Feed refresh has been started.",
            "task_id": task.id
        })
    
    @action(detail=True, methods=['get'])
    def discover(self, request, pk=None):
        """Perform TAXII discovery on the feed"""
        feed = self.get_object()
        
        try:
            client = TaxiiClient(feed)
            
            discovery_data = client.discover()
            serializer = DiscoverySerializer(discovery_data)
            
            # Update API root URL if available
            if discovery_data.get('api_roots'):
                feed.api_root = discovery_data['api_roots'][0]
                feed.save(update_fields=['api_root'])
            
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def collections(self, request, pk=None):
        """Get available collections from the feed's API root"""
        feed = self.get_object()
        
        if not feed.api_root:
            return Response(
                {"detail": "API root URL not set. Run discovery first."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            client = TaxiiClient(feed)
            
            collections = client.get_collections()
            serializer = CollectionSerializer(collections, many=True)
            
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def set_collection(self, request, pk=None):
        """Set the active collection for this feed"""
        feed = self.get_object()
        
        collection_id = request.data.get('collection_id')
        collection_name = request.data.get('collection_name')
        
        if not collection_id:
            return Response(
                {"detail": "collection_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        feed.set_collection(collection_id, collection_name)
        
        return Response({
            "message": f"Collection set to: {collection_id}",
            "feed": ExternalFeedSourceSerializer(feed).data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for feed sources"""
        total_feeds = self.queryset.count()
        active_feeds = self.queryset.filter(is_active=True).count()
        
        # Group by poll interval
        interval_counts = self.queryset.values('poll_interval').annotate(
            count=Count('id')
        )
        
        # Group by auth type
        auth_counts = self.queryset.values('auth_type').annotate(
            count=Count('id')
        )
        
        return Response({
            "total_feeds": total_feeds,
            "active_feeds": active_feeds,
            "by_poll_interval": {item['poll_interval']: item['count'] for item in interval_counts},
            "by_auth_type": {item['auth_type']: item['count'] for item in auth_counts}
        })

class FeedConsumptionLogViewSet(mixins.RetrieveModelMixin, 
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """ViewSet for feed consumption logs"""
    queryset = FeedConsumptionLog.objects.all().order_by('-created_at')
    serializer_class = FeedConsumptionLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by feed source if provided
        feed_id = self.request.query_params.get('feed_id')
        if feed_id:
            queryset = queryset.filter(feed_source_id=feed_id)
            
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for consumption logs"""
        # Base queryset for last 30 days
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        logs = self.queryset.filter(created_at__gte=thirty_days_ago)
        
        # Get counts by status
        status_counts = logs.values('status').annotate(count=Count('id'))
        
        # Get total numbers
        total_processed = logs.aggregate(total=Sum('objects_processed'))['total'] or 0
        total_added = logs.aggregate(total=Sum('objects_added'))['total'] or 0
        total_updated = logs.aggregate(total=Sum('objects_updated'))['total'] or 0
        total_failed = logs.aggregate(total=Sum('objects_failed'))['total'] or 0
        
        # Get average execution time (only for completed tasks)
        avg_execution_time = logs.filter(
            status=FeedConsumptionLog.Status.COMPLETED
        ).aggregate(avg=Avg('execution_time_seconds'))['avg']
        
        return Response({
            "total_logs": logs.count(),
            "by_status": {item['status']: item['count'] for item in status_counts},
            "total_objects": {
                "processed": total_processed,
                "added": total_added,
                "updated": total_updated,
                "failed": total_failed
            },
            "avg_execution_time": avg_execution_time
        })
