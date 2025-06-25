import logging
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from core.patterns.observer.threat_feed import ThreatFeed
from core.services.otx_taxii_service import OTXTaxiiService
from core.serializers.threat_feed_serializer import ThreatFeedSerializer
from core.models.indicator import Indicator  
from core.models.ttp_data import TTPData     

logger = logging.getLogger(__name__)

class ThreatFeedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ThreatFeed operations.
    """
    queryset = ThreatFeed.objects.all()
    serializer_class = ThreatFeedSerializer
    
    @action(detail=False, methods=['get'])
    def external(self, request):
        """
        Get all external threat feeds.
        """
        external_feeds = ThreatFeed.objects.filter(is_external=True)
        serializer = self.get_serializer(external_feeds, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_collections(self, request):
        """
        Get available TAXII collections from configured sources.
        """
        try:
            service = OTXTaxiiService()
            collections = service.get_collections()
            return Response(collections)
        except Exception as e:
            logger.error(f"Error retrieving collections: {str(e)}")
            return Response(
                {"error": "Failed to retrieve collections", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """
        Consume indicators from a specific threat feed.
        """
        logger.info(f"CONSUME API CALLED for feed ID: {pk}")
        
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
            logger.info(f"Found feed: {feed.name}, collection: {feed.taxii_collection_id}")
            
            limit_param = request.query_params.get('limit')
            batch_size = request.query_params.get('batch_size', 100)
            
            try:
                batch_size = int(batch_size)
            except ValueError:
                batch_size = 100
                
            limit = None
            if limit_param:
                try:
                    limit = int(limit_param)
                except ValueError:
                    return Response(
                        {"error": "Invalid limit parameter, must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get force_days parameter if provided
            force_days = request.query_params.get('force_days')
            if force_days:
                try:
                    force_days = int(force_days)
                except ValueError:
                    return Response(
                        {"error": "Invalid force_days parameter, must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Use OTXTaxiiService
            service = OTXTaxiiService()
            
            # Check if async processing is requested
            if request.query_params.get('async', '').lower() == 'true':
                from core.tasks.taxii_tasks import consume_feed_task
                task = consume_feed_task.delay(
                    feed_id=int(pk), 
                    limit=limit, 
                    force_days=force_days,
                    batch_size=batch_size
                )
                return Response({
                    "status": "processing",
                    "message": "Processing started in background",
                    "task_id": task.id
                })
            
            # Process synchronously
            stats = service.consume_feed(
                threat_feed_id=int(pk), 
                limit=limit, 
                force_days=force_days,
                batch_size=batch_size
            )
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error consuming feed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            return Response(
                {"error": "Failed to consume feed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get the status of the threat feed."""
        feed = get_object_or_404(ThreatFeed, pk=pk)

        # Get counts
        indicator_count = Indicator.objects.filter(threat_feed_id=pk).count()
        ttp_count = TTPData.objects.filter(threat_feed_id=pk).count()

        # Get the most recent indicator
        latest_indicator = Indicator.objects.filter(threat_feed_id=pk).order_by('-created_at').first()
        latest_date = latest_indicator.created_at if latest_indicator else None

        return Response({
            "name": feed.name,
            "is_external": feed.is_external,
            "last_sync": feed.last_sync,
            "indicator_count": indicator_count,
            "ttp_count": ttp_count,
            "latest_indicator_date": latest_date
        })
    