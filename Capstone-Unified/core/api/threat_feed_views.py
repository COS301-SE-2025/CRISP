import logging
import csv
import json
import uuid
from datetime import timedelta, datetime
from collections import defaultdict, OrderedDict
from io import StringIO
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, renderer_classes
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.permissions import AllowAny
from rest_framework.views import exception_handler
from django.core.cache import cache
from celery.result import AsyncResult

from core.models.models import ThreatFeed, SystemActivity
from core.services.otx_taxii_service import OTXTaxiiService
from core.serializers.threat_feed_serializer import ThreatFeedSerializer
from core.models.models import Indicator  
from core.models.models import TTPData     

logger = logging.getLogger(__name__)

class ThreatFeedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ThreatFeed operations
    """
    # Default queryset - will be filtered in get_queryset method
    queryset = ThreatFeed.objects.all()
    serializer_class = ThreatFeedSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter threat feeds based on user's organization and feed type, excluding inactive feeds."""
        from django.db.models import Q

        user_org = getattr(self.request.user, 'organization', None)

        # Base filter to exclude inactive feeds from main threat feeds list
        base_filter = Q(is_active=True)

        if user_org is None:
            # User has no organization, only show active external feeds
            return ThreatFeed.objects.filter(base_filter & Q(is_external=True))
        elif self.request.user.role == 'BlueVisionAdmin':
            # BlueVision admins can see all active threat feeds (hidden feeds like internal manual indicators are excluded)
            return ThreatFeed.objects.filter(base_filter)
        else:
            # Regular users can see:
            # 1. All active external/public threat feeds
            # 2. Their organization's active internal threat feeds
            return ThreatFeed.objects.filter(
                base_filter & (
                    Q(is_external=True) |  # All external feeds
                    Q(owner=user_org, is_external=False)  # Own organization's internal feeds
                )
            )

    def perform_create(self, serializer):
        """Log activity when a new feed is created"""
        feed = serializer.save()
        
        # Log activity
        activity_title = f"New threat feed added: {feed.name}"
        activity_description = f"{'External' if feed.is_external else 'Internal'} threat feed '{feed.name}' has been configured"
        SystemActivity.log_activity(
            activity_type='feed_added',
            title=activity_title,
            description=activity_description,
            threat_feed=feed,
            metadata={
                'feed_type': 'external' if feed.is_external else 'internal',
                'is_active': feed.is_active,
                'taxii_url': feed.taxii_server_url if feed.is_external else None
            }
        )
    
    def destroy(self, request, *args, **kwargs):
        """Custom destroy method with logging"""
        feed = self.get_object()
        feed_name = feed.name
        
        # Log activity before deletion
        activity_title = f"Threat feed deleted: {feed_name}"
        activity_description = f"{'External' if feed.is_external else 'Internal'} threat feed '{feed_name}' has been removed from the system"
        SystemActivity.log_activity(
            activity_type='feed_deleted',
            title=activity_title,
            description=activity_description,
            threat_feed=feed,
            metadata={
                'feed_type': 'external' if feed.is_external else 'internal',
                'had_indicators': feed.indicators.count() > 0,
                'had_ttps': feed.ttps.count() > 0
            }
        )
        
        # Perform the actual deletion
        response = super().destroy(request, *args, **kwargs)
        
        logger.info(f"Threat feed '{feed_name}' successfully deleted")
        return response
    
    @action(detail=False, methods=['get'])
    def external(self, request):
        """
        Get all external threat feeds
        """
        external_feeds = ThreatFeed.objects.filter(is_external=True)
        serializer = self.get_serializer(external_feeds, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_collections(self, request):
        """
        Get available TAXII collections from configured sources
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
    
    @action(detail=True, methods=['get'])
    def consumption_progress(self, request, pk=None):
        """
        Get real-time consumption progress for a threat feed
        """
        try:
            feed = self.get_object()
            progress_key = f"consumption_progress_{feed.id}"
            progress_data = cache.get(progress_key)
            
            if progress_data:
                return Response({
                    'success': True,
                    'progress': progress_data
                })
            else:
                return Response({
                    'success': True,
                    'progress': None,
                    'message': 'No active consumption in progress'
                })
                
        except Exception as e:
            logger.error(f"Error getting consumption progress: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def cancel_consumption(self, request, pk=None):
        """Cancel ongoing feed consumption."""
        try:
            feed = self.get_object()
            mode = request.data.get('mode', 'stop_now')  # 'stop_now' or 'cancel_job'
            task_id = request.data.get('task_id')  # Optional task ID to cancel

            # Set cancellation flag in cache
            from django.core.cache import cache
            cancel_key = f"cancel_consumption_{feed.id}"
            cache.set(cancel_key, {'mode': mode, 'timestamp': timezone.now().isoformat()}, timeout=3600)

            # Try to revoke Celery task if task_id provided
            if task_id:
                try:
                    from settings.celery import app as celery_app
                    celery_app.control.revoke(task_id, terminate=True)
                    logger.info(f"Revoked Celery task {task_id} for feed {feed.name}")
                except Exception as e:
                    logger.warning(f"Could not revoke Celery task {task_id}: {str(e)}")

            if mode == 'cancel_job':
                # Remove indicators added in the last consumption session
                # Use a time-based approach - indicators added in the last hour
                from datetime import timedelta
                one_hour_ago = timezone.now() - timedelta(hours=1)
                
                # Find recent indicators that might belong to current session
                recent_indicators = feed.indicators.filter(created_at__gte=one_hour_ago)
                deleted_count = recent_indicators.count()
                
                if deleted_count > 0:
                    # Delete recent indicators and their related TTPs
                    from core.models.models import TTPData
                    # Delete TTPs that were created from these indicators
                    TTPData.objects.filter(
                        threat_feed=feed,
                        created_at__gte=one_hour_ago
                    ).delete()
                    
                    # Delete the indicators
                    recent_indicators.delete()
                    
                logger.info(f"Cancel job mode for feed {feed.name} - deleted {deleted_count} recent indicators")

                return Response({
                    'success': True,
                    'message': 'Consumption cancelled and recent data removed',
                    'indicators_kept': feed.indicators.count(),
                    'indicators_removed': deleted_count,
                    'total_expected': deleted_count
                })
            else:
                # Stop now mode - keep existing indicators
                current_count = feed.indicators.count()
                logger.info(f"Stop now mode for feed {feed.name} - keeping {current_count} indicators")

                return Response({
                    'success': True,
                    'message': 'Consumption stopped, indicators kept',
                    'indicators_kept': current_count,
                    'indicators_removed': 0,
                    'total_expected': current_count
                })

        except Exception as e:
            logger.error(f"Error cancelling consumption for feed {pk}: {str(e)}")
            return Response(
                {"error": "Failed to cancel consumption", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """
        Consume indicators from a specific threat feed
        """
        logger.info(f"CONSUME API CALLED for feed ID: {pk}")
        
        try:
            try:
                feed = get_object_or_404(ThreatFeed, pk=pk)
            except Http404 as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
            logger.info(f"Found feed: {feed.name}, collection: {feed.taxii_collection_id}")
            
            # Parse parameters
            limit_param = request.query_params.get('limit')
            batch_size = request.query_params.get('batch_size', 100)
            force_days = request.query_params.get('force_days')
            
            # Validate parameters with reasonable defaults
            limit = 10  # Default to 10 blocks for faster processing
            if limit_param:
                try:
                    limit = int(limit_param)
                    # Validate range (1-100 blocks)
                    if limit < 1 or limit > 100:
                        return Response(
                            {"error": "limit parameter must be between 1 and 100"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except ValueError:
                    return Response(
                        {"error": "Invalid limit parameter, must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if force_days:
                try:
                    force_days = int(force_days)
                    # Validate range (1-365 days)
                    if force_days < 1 or force_days > 365:
                        return Response(
                            {"error": "force_days parameter must be between 1 and 365"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except ValueError:
                    return Response(
                        {"error": "Invalid force_days parameter, must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            try:
                batch_size = int(batch_size)
            except ValueError:
                batch_size = 100
            
            # Log parameters for debugging
            logger.info(f"Parameters: limit={limit}, force_days={force_days}, batch_size={batch_size}")

            # Check if this is a VirusTotal feed and handle differently
            if 'virustotal' in feed.name.lower():
                logger.info("Detected VirusTotal feed - using VirusTotal API service")
                from core.services.virustotal_service import VirusTotalService

                # For VirusTotal, always use async due to rate limiting
                if request.query_params.get('async', '').lower() != 'true':
                    logger.info("VirusTotal feed consumption forced to async due to rate limiting")

                # Quick API connection test first
                vt_service = VirusTotalService()
                connection_test = vt_service.test_api_connection()
                if not connection_test['success']:
                    return Response({
                        'success': False,
                        'error': f"VirusTotal API connection failed: {connection_test['error']}",
                        'quota_info': connection_test.get('quota', 'Unknown')
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                # Check if we have indicators to process
                from core.models.models import Indicator
                vt_indicators_count = Indicator.objects.filter(
                    threat_feed=feed,
                    type__in=['md5', 'sha1', 'sha256', 'url']
                ).count()

                if vt_indicators_count == 0:
                    return Response({
                        'success': True,
                        'indicators': 0,
                        'ttps': 0,
                        'status': 'completed',
                        'feed_name': feed.name,
                        'service_type': 'virustotal_api',
                        'message': 'No indicators available for VirusTotal analysis',
                        'quota_info': connection_test.get('quota', 'Unknown')
                    })

                # Start async processing
                try:
                    # Create a simple background task simulation
                    import threading
                    import time

                    def vt_sync_task():
                        """Background VirusTotal sync task"""
                        try:
                            logger.info(f"Starting VirusTotal background sync for {feed.name}")
                            
                            # Check for cancellation before starting
                            from django.core.cache import cache
                            cancel_key = f"cancel_consumption_{feed.id}"
                            
                            if cache.get(cancel_key):
                                logger.info(f"VirusTotal sync cancelled before start for {feed.name}")
                                return
                            
                            result = vt_service.sync_virustotal_feed(
                                feed, 
                                limit=min(limit, 10),  # Limit to 10 indicators
                                cancel_check=lambda: cache.get(cancel_key) is not None
                            )

                            # Check cancellation after completion
                            cancellation_signal = cache.get(cancel_key)
                            if cancellation_signal:
                                cache.delete(cancel_key)  # Clean up
                                
                                if cancellation_signal.get('mode') == 'cancel_job':
                                    # Remove recently added indicators/TTPs
                                    from datetime import timedelta
                                    one_hour_ago = timezone.now() - timedelta(hours=1)
                                    
                                    recent_indicators = feed.indicators.filter(created_at__gte=one_hour_ago)
                                    deleted_count = recent_indicators.count()
                                    
                                    if deleted_count > 0:
                                        from core.models.models import TTPData
                                        TTPData.objects.filter(
                                            threat_feed=feed,
                                            created_at__gte=one_hour_ago
                                        ).delete()
                                        recent_indicators.delete()
                                    
                                    logger.info(f"VirusTotal sync cancelled with cleanup: {deleted_count} items removed")
                                else:
                                    logger.info(f"VirusTotal sync cancelled but data kept")
                                return

                            if result['success'] and result.get('ttps_created', 0) > 0:
                                activity_title = f"VirusTotal sync: {result['ttps_created']} TTPs extracted from {result['indicators_processed']} indicators"
                                SystemActivity.log_activity(
                                    activity_type='virustotal_sync',
                                    title=activity_title,
                                    description=f"Successfully analyzed {result['indicators_processed']} indicators and extracted {result['ttps_created']} TTPs from VirusTotal",
                                    threat_feed=feed,
                                    metadata=result
                                )

                            logger.info(f"VirusTotal background sync completed: {result}")
                        except Exception as e:
                            logger.error(f"VirusTotal background sync failed: {str(e)}")

                    # Start background thread
                    thread = threading.Thread(target=vt_sync_task)
                    thread.daemon = True
                    thread.start()

                    # Return immediate response
                    return Response({
                        'status': 'processing',
                        'message': f'VirusTotal analysis started for {vt_indicators_count} indicators. This may take several minutes due to API rate limits.',
                        'feed_name': feed.name,
                        'service_type': 'virustotal_api',
                        'estimated_time_minutes': vt_indicators_count * 0.25,  # ~15 seconds per indicator
                        'indicators_to_analyze': vt_indicators_count,
                        'quota_info': connection_test.get('quota', 'Unknown'),
                        'note': 'VirusTotal processing is asynchronous due to API rate limits. Check system activities for completion status.'
                    })

                except Exception as e:
                    logger.error(f"Failed to start VirusTotal sync: {str(e)}")
                    return Response({
                        'success': False,
                        'error': 'Failed to start VirusTotal analysis',
                        'details': str(e),
                        'feed_name': feed.name
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                # Route to appropriate service based on feed type
                if 'crisp' in feed.name.lower() and feed.taxii_server_url and 'crisp-threat-intel' in feed.taxii_server_url:
                    # CRISP custom feeds should populate their data when consumed
                    logger.info("CRISP custom feed detected - populating custom data")

                    try:
                        from django.core.management import call_command
                        from io import StringIO
                        import sys

                        # Capture output from the population command
                        old_stdout = sys.stdout
                        mystdout = StringIO()
                        sys.stdout = mystdout

                        # Run population command for this specific feed
                        call_command('populate_comprehensive_threat_intel', feed_name=feed.name, verbosity=0)

                        # Restore stdout and get output
                        sys.stdout = old_stdout
                        command_output = mystdout.getvalue()

                        # Get updated counts
                        indicators_count = feed.indicators.count()
                        ttps_count = feed.ttps.count()

                        logger.info(f"CRISP feed {feed.name} populated: {indicators_count} indicators, {ttps_count} TTPs")

                        return Response({
                            'success': True,
                            'message': f'CRISP custom feed "{feed.name}" populated successfully.',
                            'feed_name': feed.name,
                            'service_type': 'crisp_custom',
                            'indicators_count': indicators_count,
                            'ttps_count': ttps_count,
                            'indicators_created': indicators_count,
                            'ttps_created': ttps_count,
                            'note': 'CRISP custom feeds populate data from internal configurations.'
                        })

                    except Exception as e:
                        logger.error(f"Error populating CRISP feed {feed.name}: {str(e)}")
                        return Response({
                            'success': False,
                            'message': f'Failed to populate CRISP feed "{feed.name}": {str(e)}',
                            'feed_name': feed.name,
                            'service_type': 'crisp_custom'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                elif 'mitre' in feed.name.lower() or 'cti-taxii.mitre.org' in (feed.taxii_server_url or ''):
                    # MITRE feeds should use StixTaxiiService
                    logger.info("MITRE feed detected - using StixTaxiiService")
                    from core.services.stix_taxii_service import StixTaxiiService
                    service = StixTaxiiService()

                elif ('alienvault' in feed.name.lower() or 'otx' in feed.name.lower() or
                      'otx.alienvault.com' in (feed.taxii_server_url or '')):
                    # AlienVault OTX feeds should use OTXTaxiiService
                    logger.info("AlienVault OTX feed detected - using OTXTaxiiService")
                    from core.services.otx_taxii_service import OTXTaxiiService
                    service = OTXTaxiiService()

                else:
                    # Default to StixTaxiiService for unknown feeds
                    logger.info(f"Unknown feed type for {feed.name} - defaulting to StixTaxiiService")
                    from core.services.stix_taxii_service import StixTaxiiService
                    service = StixTaxiiService()

                # Check if async processing is requested
                if request.query_params.get('async', '').lower() == 'true':
                    # Check Redis availability first
                    redis_available = False
                    try:
                        from django.core.cache import cache
                        cache.get('redis_test')  # Test Redis connection
                        redis_available = True
                    except Exception as redis_error:
                        logger.warning(f"Redis not available for async consumption: {redis_error}")
                        redis_available = False

                    if redis_available:
                        from core.tasks.taxii_tasks import consume_feed_task

                        # Check if feed is actively running (allow starting fresh consumption even if previously paused)
                        # Use atomic update to prevent race conditions
                        from django.db import transaction
                        with transaction.atomic():
                            # Refresh feed status from database
                            feed.refresh_from_db()
                            if feed.consumption_status in ['running', 'starting']:
                                return Response({
                                    "error": f"Feed consumption is already running or starting. Use pause endpoint to control it.",
                                    "current_status": feed.consumption_status,
                                    "can_be_paused": feed.can_be_paused(),
                                    "can_be_resumed": feed.can_be_resumed()
                                }, status=status.HTTP_400_BAD_REQUEST)

                            # Immediately mark as starting to prevent other requests
                            feed.consumption_status = 'starting'
                            feed.save(update_fields=['consumption_status'])

                        # Reset paused state for fresh consumption
                        if feed.consumption_status == 'paused':
                            logger.info(f"Resetting paused feed {feed.name} for fresh consumption")
                            feed.consumption_status = 'idle'
                            feed.current_task_id = None
                            feed.paused_at = None
                            feed.pause_metadata = {}
                            feed.save(update_fields=['consumption_status', 'current_task_id', 'paused_at', 'pause_metadata'])

                        try:
                            task = consume_feed_task.delay(
                                feed_id=int(pk),
                                limit=limit,
                                force_days=force_days,
                                batch_size=batch_size
                            )

                            # Update feed status to running
                            feed.start_consumption(task.id)

                            return Response({
                                "status": "processing",
                                "message": "Processing started in background",
                                "task_id": task.id,
                                "feed_status": feed.consumption_status
                            })
                        except Exception as celery_error:
                            logger.warning(f"Celery task creation failed: {celery_error}, falling back to sync consumption")
                            # Fall through to sync consumption
                    else:
                        logger.info(f"Redis unavailable, falling back to synchronous consumption for feed {feed.name}")
                        # Fall through to sync consumption

                # Set feed status to processing for sync consumption
                feed.consumption_status = 'processing'
                feed.save(update_fields=['consumption_status'])

                try:
                    stats = service.consume_feed(feed, limit=limit, force_days=force_days, batch_size=batch_size)

                    # Update feed status on successful completion
                    from django.utils import timezone
                    feed.consumption_status = 'idle'
                    feed.last_sync = timezone.now()
                    feed.sync_count = (feed.sync_count or 0) + 1
                    feed.last_error = None
                    feed.save(update_fields=['consumption_status', 'last_sync', 'sync_count', 'last_error'])

                except Exception as consumption_error:
                    # Update feed status on error
                    feed.consumption_status = 'idle'
                    feed.last_error = str(consumption_error)[:500]  # Truncate long errors
                    feed.save(update_fields=['consumption_status', 'last_error'])
                    raise  # Re-raise the exception to be handled by outer try-except
            
            # Format response properly for API consumers
            if isinstance(stats, tuple):
                indicator_count, ttp_count = stats
                formatted_stats = {
                    "indicators": indicator_count,
                    "ttps": ttp_count,
                    "status": "completed",
                    "feed_name": feed.name,
                    "parameters_used": {
                        "limit": limit,
                        "force_days": force_days,
                        "batch_size": batch_size
                    }
                }
                
                # Log activity
                if indicator_count > 0 or ttp_count > 0:
                    activity_title = f"Consumed {indicator_count} indicators from {feed.name}"
                    activity_description = f"Feed consumption completed successfully. Added {indicator_count} indicators and {ttp_count} TTPs."
                    SystemActivity.log_activity(
                        activity_type='feed_consumed',
                        title=activity_title,
                        description=activity_description,
                        threat_feed=feed,
                        metadata={
                            'indicator_count': indicator_count,
                            'ttp_count': ttp_count,
                            'parameters': {
                                'limit': limit,
                                'force_days': force_days,
                                'batch_size': batch_size
                            }
                        }
                    )
                    
                    # Add to batch notification service to trigger user notifications
                    try:
                        from core.services.batch_notification_service import batch_notification_service
                        batch_notification_service.add_feed_change(
                            threat_feed=feed,
                            new_indicators=indicator_count,
                            updated_indicators=0  # Feed consumption typically adds new indicators
                        )
                        logger.info(f"Added feed consumption to batch notification service: {feed.name} (+{indicator_count} indicators)")

                        # Trigger frontend auto-refresh for feed consumption
                        from django.core.cache import cache
                        from django.utils import timezone
                        cache.set('indicators_updated', timezone.now().isoformat(), timeout=300)
                        cache.set('feeds_updated', timezone.now().isoformat(), timeout=300)
                        logger.info(f"🔄 Triggered frontend refresh after feed consumption: {feed.name} (+{indicator_count} indicators)")
                    except Exception as e:
                        logger.error(f"Error adding feed consumption to batch notification service: {e}")
                        # Don't fail the request if notification fails
            else:
                formatted_stats = stats

            return Response(formatted_stats)
            
        except ValueError as ve:
            logger.warning(f"Invalid request data or feed config: {ve}")
            return Response(
                {"error": "Invalid request data", "details": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get counts
        indicator_count = Indicator.objects.filter(threat_feed_id=pk).count()
        ttp_count = TTPData.objects.filter(threat_feed_id=pk).count()

        # Get the most recent indicator
        latest_indicator = Indicator.objects.filter(threat_feed_id=pk).order_by('-created_at').first()
        latest_date = latest_indicator.created_at if latest_indicator else None

        return Response({
            "name": feed.name,
            "is_external": feed.is_external,
            "is_active": feed.is_active,
            "last_sync": feed.last_sync,
            "indicator_count": indicator_count,
            "ttp_count": ttp_count,
            "latest_indicator_date": latest_date
        })

    @action(detail=False, methods=['get'], url_path='task-status/(?P<task_id>[^/.]+)')
    def task_status(self, request, task_id=None):
        """Check the status of a Celery task."""
        try:
            result = AsyncResult(task_id)

            if result.state == 'PENDING':
                response = {
                    'state': result.state,
                    'status': 'Pending...'
                }
            elif result.state == 'SUCCESS':
                response = {
                    'state': result.state,
                    'result': result.result
                }
            elif result.state == 'FAILURE':
                response = {
                    'state': result.state,
                    'error': str(result.info)
                }
            else:
                response = {
                    'state': result.state,
                    'info': result.info
                }

            return Response(response)
        except Exception as e:
            return Response({
                'error': f'Error checking task status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='task-status/(?P<task_id>[^/.]+)')
    def task_status(self, request, task_id=None):
        """Get the status of a specific Celery task."""
        try:
            from django.core.cache import cache
            
            # Check cache for task status
            cache_key = f"task_status_{task_id}"
            task_status_data = cache.get(cache_key)
            
            if task_status_data:
                return Response({
                    'success': True,
                    'task_id': task_id,
                    'status': task_status_data.get('status', 'unknown'),
                    'stage': task_status_data.get('stage', ''),
                    'message': task_status_data.get('message', ''),
                    'progress': task_status_data.get('progress', {}),
                    'last_update': task_status_data.get('last_update'),
                    'feed_id': task_status_data.get('feed_id')
                })
            
            # Fallback to Celery status
            from celery.result import AsyncResult
            task_result = AsyncResult(task_id)
            
            return Response({
                'success': True,
                'task_id': task_id,
                'status': task_result.status.lower() if task_result.status else 'unknown',
                'result': task_result.result if task_result.ready() else None,
                'info': task_result.info if hasattr(task_result, 'info') else None
            })
            
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {str(e)}")
            return Response({
                'success': False,
                'error': str(e),
                'task_id': task_id,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='cancel-task/(?P<task_id>[^/.]+)')
    def cancel_task(self, request, task_id=None):
        """Cancel a specific Celery task by ID."""
        try:
            from django.core.cache import cache
            from settings.celery import app as celery_app
            from celery.result import AsyncResult

            mode = request.data.get('mode', 'stop_now')  # 'stop_now' or 'cancel_job'

            # Get task details from cache
            task_key = f"task_status_{task_id}"
            cached_status = cache.get(task_key)

            if not cached_status:
                # Task not in cache - check if it's a Celery task that's still running
                try:
                    task_result = AsyncResult(task_id, app=celery_app)

                    # If task is already completed/failed/revoked, reset any stuck feeds and return success
                    if task_result.state in ['SUCCESS', 'FAILURE', 'REVOKED', 'RETRY']:
                        # Reset any feeds stuck with this task_id
                        try:
                            from core.models.models import ThreatFeed
                            stuck_feeds = ThreatFeed.objects.filter(current_task_id=task_id, consumption_status='running')
                            for feed in stuck_feeds:
                                logger.info(f"Resetting stuck feed {feed.name} (ID: {feed.id}) with completed task {task_id}")
                                feed.stop_consumption()
                        except Exception as e:
                            logger.warning(f"Could not reset stuck feeds with task_id {task_id}: {str(e)}")

                        return Response({
                            'success': True,
                            'message': f'Task {task_id} was already {task_result.state.lower()}',
                            'task_status': task_result.state.lower()
                        })

                    # If task is pending or running, try to revoke it and reset any stuck feeds
                    if task_result.state in ['PENDING', 'STARTED']:
                        try:
                            celery_app.control.revoke(task_id, terminate=True)
                            logger.info(f"Revoked orphaned Celery task {task_id}")
                        except Exception as e:
                            logger.warning(f"Could not revoke orphaned Celery task {task_id}: {str(e)}")

                        # Reset any feeds stuck with this task_id
                        try:
                            from core.models.models import ThreatFeed
                            stuck_feeds = ThreatFeed.objects.filter(current_task_id=task_id, consumption_status='running')
                            logger.info(f"DEBUG: Found {stuck_feeds.count()} stuck feeds for task {task_id}")
                            for feed in stuck_feeds:
                                logger.info(f"Resetting stuck feed {feed.name} (ID: {feed.id}) with pending/started task {task_id}")
                                feed.stop_consumption()
                                logger.info(f"Feed {feed.name} reset - new status: {feed.consumption_status}, task_id: {feed.current_task_id}")
                        except Exception as e:
                            logger.warning(f"Could not reset stuck feeds with task_id {task_id}: {str(e)}")
                            import traceback
                            logger.warning(f"Traceback: {traceback.format_exc()}")

                        return Response({
                            'success': True,
                            'message': f'Task {task_id} cancellation requested (task was not in progress tracking)',
                            'task_status': 'cancelled'
                        })

                except Exception as e:
                    logger.warning(f"Could not check Celery task status for {task_id}: {str(e)}")

                # Task not found anywhere - likely completed and expired from cache
                # Try to find and reset any feeds that might be stuck with this task_id
                try:
                    from core.models.models import ThreatFeed
                    stuck_feeds = ThreatFeed.objects.filter(current_task_id=task_id, consumption_status='running')
                    for feed in stuck_feeds:
                        logger.info(f"Resetting stuck feed {feed.name} (ID: {feed.id}) with orphaned task {task_id}")
                        feed.stop_consumption()  # This will reset the status and clear current_task_id
                except Exception as e:
                    logger.warning(f"Could not reset stuck feeds with task_id {task_id}: {str(e)}")

                return Response({
                    'success': True,
                    'message': 'Task not found or already completed',
                    'task_status': 'completed_or_expired'
                })
            
            feed_id = cached_status.get('feed_id')
            if not feed_id:
                return Response({
                    'success': False,
                    'error': 'Cannot determine feed ID for this task'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set cancellation flag
            cancel_key = f"cancel_consumption_{feed_id}"
            cache.set(cancel_key, {
                'mode': mode, 
                'timestamp': timezone.now().isoformat(),
                'task_id': task_id
            }, timeout=3600)
            
            # Revoke the Celery task
            try:
                celery_app.control.revoke(task_id, terminate=True)
                logger.info(f"Revoked Celery task {task_id}")
            except Exception as e:
                logger.warning(f"Could not revoke Celery task {task_id}: {str(e)}")
            
            # Update task status in cache
            cache.set(task_key, {
                'status': 'cancelling',
                'feed_id': feed_id,
                'message': f'Task cancellation requested ({mode})',
                'cancellation_mode': mode
            }, timeout=3600)
            
            return Response({
                'success': True,
                'message': f'Task {task_id} cancellation requested',
                'mode': mode,
                'task_id': task_id
            })
            
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reset_feed_status(self, request, pk=None):
        """Reset a stuck feed to idle status."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)

            # Reset the feed status
            old_status = feed.consumption_status
            old_task_id = feed.current_task_id

            feed.stop_consumption()

            logger.info(f"Reset feed {feed.name} (ID: {feed.id}) from status '{old_status}' with task_id '{old_task_id}' to 'idle'")

            return Response({
                'success': True,
                'message': f'Feed {feed.name} has been reset to idle status',
                'old_status': old_status,
                'old_task_id': old_task_id,
                'new_status': feed.consumption_status
            })

        except Exception as e:
            logger.error(f"Error resetting feed {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def pause_consumption(self, request, pk=None):
        """Pause consumption of a specific threat feed."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)

            from django.core.cache import cache
            from django.utils import timezone

            # Check if feed is actually capable of being paused
            if not feed.can_be_paused():
                # If feed says it's running but has no task_id, it's probably stuck
                if feed.consumption_status == 'running' and not feed.current_task_id:
                    logger.warning(f"Feed {feed.id} appears stuck in 'running' status with no task_id. Resetting to idle.")
                    feed.stop_consumption()
                    return Response({
                        'success': False,
                        'error': 'Feed was stuck in running status and has been reset to idle. Please try consuming again.',
                        'reset_performed': True
                    }, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    'success': False,
                    'error': f'Feed cannot be paused. Current status: {feed.consumption_status}',
                    'current_status': feed.consumption_status,
                    'current_task_id': feed.current_task_id,
                    'can_be_paused': feed.can_be_paused()
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if there's already a pause signal for this feed
            pause_key = f"pause_consumption_{feed.id}"
            existing_pause_signal = cache.get(pause_key)

            if existing_pause_signal:
                # There's already a pause request pending
                logger.info(f"Pause already requested for feed {feed.id}")
                return Response({
                    'success': True,
                    'message': f'Pause already requested for feed "{feed.name}". The task will pause at the next checkpoint.',
                    'feed_id': str(feed.id),
                    'current_status': feed.consumption_status,
                    'already_requested': True
                })

            # Set pause flag in cache for the running task to check
            pause_key = f"pause_consumption_{feed.id}"
            cache.set(pause_key, {
                'paused': True,
                'requested_at': timezone.now().isoformat(),
                'user_id': request.user.id if hasattr(request, 'user') else None
            }, timeout=3600)  # 1 hour timeout

            logger.info(f"Pause requested for feed {feed.name} (ID: {feed.id})")

            return Response({
                'success': True,
                'message': f'Pause requested for feed "{feed.name}". The task will pause at the next checkpoint.',
                'feed_id': str(feed.id),
                'current_status': feed.consumption_status
            })
            
        except Exception as e:
            logger.error(f"Error pausing feed consumption: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def resume_consumption(self, request, pk=None):
        """Resume consumption of a paused threat feed."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
            
            if not feed.can_be_resumed():
                # Provide more detailed error information
                error_details = {
                    'success': False,
                    'error': f'Feed consumption cannot be resumed. Current status: {feed.consumption_status}',
                    'current_status': feed.consumption_status,
                    'can_be_resumed': feed.can_be_resumed(),
                    'has_pause_metadata': bool(feed.pause_metadata),
                    'current_task_id': feed.current_task_id
                }
                
                # Provide user-friendly explanation
                if feed.consumption_status == 'idle':
                    error_details['explanation'] = 'Feed is not paused. It may have completed successfully or was never paused.'
                elif feed.consumption_status == 'running':
                    error_details['explanation'] = 'Feed is currently running and does not need to be resumed.'
                else:
                    error_details['explanation'] = f'Feed status "{feed.consumption_status}" does not support resumption.'
                
                logger.info(f"Resume request failed for feed {feed.id}: {error_details['explanation']}")
                return Response(error_details, status=status.HTTP_400_BAD_REQUEST)
            
            from core.tasks.taxii_tasks import consume_feed_task
            from django.core.cache import cache
            
            # Clear any pause flags
            pause_key = f"pause_consumption_{feed.id}"
            cache.delete(pause_key)
            
            # Start a new task to resume consumption using the saved metadata
            task = consume_feed_task.delay(
                feed_id=str(feed.id),
                resume_metadata=feed.pause_metadata,
                is_resume=True
            )
            
            # Update feed status
            feed.resume_consumption(task.id)
            
            logger.info(f"Resuming consumption for feed {feed.name} (ID: {feed.id}) with task {task.id}")
            
            return Response({
                'success': True,
                'message': f'Resuming consumption for feed "{feed.name}"',
                'feed_id': str(feed.id),
                'task_id': task.id,
                'resumed_from': feed.pause_metadata.get('last_processed_item', 'beginning')
            })
            
        except Exception as e:
            logger.error(f"Error resuming feed consumption: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def consumption_status(self, request, pk=None):
        """Get detailed consumption status for a threat feed."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
            
            from django.core.cache import cache
            
            # Check for pause flags
            pause_key = f"pause_consumption_{feed.id}"
            pause_info = cache.get(pause_key)
            
            # Get task status if available
            task_status = None
            if feed.current_task_id:
                from settings.celery import app as celery_app
                try:
                    task = celery_app.AsyncResult(feed.current_task_id)
                    task_status = task.status
                except:
                    task_status = 'UNKNOWN'
            
            return Response({
                'success': True,
                'feed_id': str(feed.id),
                'feed_name': feed.name,
                'consumption_status': feed.consumption_status,
                'current_task_id': feed.current_task_id,
                'task_status': task_status,
                'paused_at': feed.paused_at.isoformat() if feed.paused_at else None,
                'can_be_paused': feed.can_be_paused(),
                'can_be_resumed': feed.can_be_resumed(),
                'is_consuming': feed.is_consuming(),
                'pause_requested': pause_info is not None,
                'pause_metadata': feed.pause_metadata,
                'last_error': feed.last_error
            })
            
        except Exception as e:
            logger.error(f"Error getting consumption status: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def test_connection(self, request, pk=None):
        """Test TAXII connection without consuming."""
        try:
            try:
                feed = get_object_or_404(ThreatFeed, pk=pk)
            except Http404 as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
            service = OTXTaxiiService()
            
            # Test getting collections
            collections = service.get_collections()
            
            return Response({
                "status": "success",
                "feed_name": feed.name,
                "collections_found": len(collections),
                "collections": collections[:3]
            })
        except Exception as e:
            return Response({
                "status": "error", 
                "error": str(e)
            }, status=500)
    
    @action(detail=True, methods=['get'])
    def indicators(self, request, pk=None):
        """Get indicators for a specific threat feed."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get indicators for this feed
        indicators = Indicator.objects.filter(threat_feed_id=pk).order_by('-created_at')
        
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Calculate pagination
        start = (page - 1) * page_size
        end = start + page_size
        total_count = indicators.count()
        
        indicators_page = indicators[start:end]
        
        # Format the response
        results = []
        for indicator in indicators_page:
            results.append({
                'id': indicator.id,
                'type': indicator.type,
                'value': indicator.value,
                'stix_id': indicator.stix_id,
                'name': indicator.name,
                'description': indicator.description,
                'confidence': indicator.confidence,
                'first_seen': indicator.first_seen,
                'last_seen': indicator.last_seen,
                'created_at': indicator.created_at,
                'is_anonymized': indicator.is_anonymized,
                'source': feed.name
            })
        
        return Response({
            'count': total_count,
            'next': f'/api/threat-feeds/{pk}/indicators/?page={page + 1}&page_size={page_size}' if end < total_count else None,
            'previous': f'/api/threat-feeds/{pk}/indicators/?page={page - 1}&page_size={page_size}' if page > 1 else None,
            'results': results
        })
    
    @action(detail=True, methods=['get'])
    def ttps(self, request, pk=None):
        """Get TTPs for a specific threat feed."""
        try:
            feed = get_object_or_404(ThreatFeed, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get TTPs for this feed
        ttps = TTPData.objects.filter(threat_feed_id=pk).order_by('-created_at')
        
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Calculate pagination
        start = (page - 1) * page_size
        end = start + page_size
        total_count = ttps.count()
        
        ttps_page = ttps[start:end]
        
        # Format the response
        results = []
        for ttp in ttps_page:
            results.append({
                'id': ttp.id,
                'stix_id': ttp.stix_id,
                'title': ttp.name,
                'description': ttp.description,
                'technique_id': ttp.mitre_technique_id,
                'tactic': ttp.mitre_tactic,
                'technique': ttp.mitre_technique_id,  # Use technique_id for technique field
                'sub_technique': ttp.mitre_subtechnique,
                'confidence': None,  # Field doesn't exist in model
                'created_at': ttp.created_at,
                'source': feed.name
            })
        
        return Response({
            'count': total_count,
            'next': f'/api/threat-feeds/{pk}/ttps/?page={page + 1}&page_size={page_size}' if end < total_count else None,
            'previous': f'/api/threat-feeds/{pk}/ttps/?page={page - 1}&page_size={page_size}' if page > 1 else None,
            'results': results
        })
        
    def handle_exception(self, exc):
        # Let DRF handle known exceptions
        response = exception_handler(exc, self.get_exception_handler_context())

        # If response is None, it's likely an unhandled exception
        if response is None:
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return response

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def indicators_list(request):
    """Get all indicators across all feeds for dashboard summary or create new indicator."""
    if request.method == 'GET':
        try:
            # Get pagination parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))

            # Get filtering parameters
            type_filter = request.GET.get('type', '')
            source_filter = request.GET.get('source', '')
            search_filter = request.GET.get('search', '')
            severity_filter = request.GET.get('severity', '')
            status_filter = request.GET.get('status', '')
            date_range_filter = request.GET.get('dateRange', '')
            ordering = request.GET.get('ordering', '-created_at')

            # Build the queryset with organization filtering
            from django.db.models import Q

            # Get user's organization
            user_org = getattr(request.user, 'organization', None)
            
            # Check if user is superuser or BlueVisionAdmin
            is_admin = (getattr(request.user, 'is_superuser', False) or
                       getattr(request.user, 'role', '') == 'BlueVisionAdmin')

            logger.info(f"User {request.user.username} role: {request.user.role}, org: {user_org}, is_admin: {is_admin}")

            if user_org is None and not is_admin:
                # User has no organization and is not admin, return empty queryset
                logger.info(f"User has no organization and is not admin, returning empty queryset")
                indicators = Indicator.objects.none()
            elif is_admin:
                # Admins (superuser or BlueVisionAdmin) can see all indicators
                logger.info(f"Admin user, returning all indicators")
                indicators = Indicator.objects.all()
            else:
                # Regular users can see:
                # 1. Indicators from threat feeds owned by their organization (both external and internal)
                # 2. Indicators that have been shared with their organization
                indicators = Indicator.objects.filter(
                    Q(threat_feed__owner=user_org) |  # Feeds consumed by their organization (external or internal)
                    Q(sharing_relationships__target_organization=user_org)  # Shared indicators
                ).distinct()

            if type_filter:
                indicators = indicators.filter(type__icontains=type_filter)

            if source_filter:
                indicators = indicators.filter(threat_feed__name__icontains=source_filter)

            if search_filter:
                from django.db.models import Q
                indicators = indicators.filter(
                    Q(value__icontains=search_filter) |
                    Q(description__icontains=search_filter) |
                    Q(name__icontains=search_filter)
                )

            if severity_filter:
                indicators = indicators.filter(severity__icontains=severity_filter)

            if status_filter:
                # Map frontend status to backend fields
                if status_filter.lower() == 'anonymized':
                    indicators = indicators.filter(is_anonymized=True)
                elif status_filter.lower() == 'active':
                    indicators = indicators.filter(is_anonymized=False)

            if date_range_filter:
                from datetime import datetime, timedelta
                from django.utils import timezone
                now = timezone.now()

                if date_range_filter == 'last7days':
                    start_date = now - timedelta(days=7)
                    indicators = indicators.filter(created_at__gte=start_date)
                elif date_range_filter == 'last30days':
                    start_date = now - timedelta(days=30)
                    indicators = indicators.filter(created_at__gte=start_date)
                elif date_range_filter == 'last90days':
                    start_date = now - timedelta(days=90)
                    indicators = indicators.filter(created_at__gte=start_date)

            # Apply ordering
            indicators = indicators.order_by(ordering)
            
            # Calculate pagination
            start = (page - 1) * page_size
            end = start + page_size
            total_count = indicators.count()
            
            logger.info(f"After filtering, total indicators: {total_count}, page: {page}, page_size: {page_size}")
            
            indicators_page = indicators[start:end]
            
            # Format the response
            results = []
            for indicator in indicators_page:
                # Get the feed name
                feed_name = 'Unknown'
                if hasattr(indicator, 'threat_feed') and indicator.threat_feed:
                    feed_name = indicator.threat_feed.name
                elif hasattr(indicator, 'threat_feed_id') and indicator.threat_feed_id:
                    try:
                        feed = ThreatFeed.objects.get(id=indicator.threat_feed_id)
                        feed_name = feed.name
                    except ThreatFeed.DoesNotExist:
                        pass

                # Check if this indicator was shared with the current user's organization
                sharing_info = None
                if user_org:
                    try:
                        from core.models.models import IndicatorSharingRelationship
                        sharing_relationship = IndicatorSharingRelationship.objects.filter(
                            indicator=indicator,
                            target_organization=user_org
                        ).select_related('shared_by_user', 'indicator__threat_feed__owner').first()

                        if sharing_relationship:
                            # Get source organization from the sharing user's organization
                            source_org_name = sharing_relationship.shared_by_user.organization.name if sharing_relationship.shared_by_user and sharing_relationship.shared_by_user.organization else 'Unknown'
                            shared_by_name = sharing_relationship.shared_by_user.username if sharing_relationship.shared_by_user else 'System'

                            sharing_info = {
                                'is_shared': True,
                                'shared_from': source_org_name,
                                'shared_by': shared_by_name,
                                'shared_at': sharing_relationship.shared_at,
                                'anonymization_level': sharing_relationship.anonymization_level,
                                'share_method': sharing_relationship.share_method
                            }
                    except Exception as e:
                        # If there's an error checking sharing, don't break the response
                        pass

                # If not shared, mark as original
                if not sharing_info:
                    sharing_info = {
                        'is_shared': False,
                        'shared_from': None,
                        'shared_by': None,
                        'shared_at': None,
                        'anonymization_level': None,
                        'share_method': None
                    }

                results.append({
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value,
                    'stix_id': indicator.stix_id,
                    'name': indicator.name,
                    'description': indicator.description,
                    'confidence': indicator.confidence,
                    'first_seen': indicator.first_seen,
                    'last_seen': indicator.last_seen,
                    'created_at': indicator.created_at,
                    'is_anonymized': indicator.is_anonymized,
                    'source': feed_name,
                    'sharing': sharing_info
                })
            
            return Response({
                'count': total_count,
                'next': f'/api/indicators/?page={page + 1}&page_size={page_size}' if end < total_count else None,
                'previous': f'/api/indicators/?page={page - 1}&page_size={page_size}' if page > 1 else None,
                'results': results
            })
        except Exception as e:
            logger.error(f"Error fetching indicators: {str(e)}")
            return Response(
                {"error": "Failed to fetch indicators", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            from core.repositories.indicator_repository import IndicatorRepository
            from core.services.indicator_service import IndicatorService
            from core.models.models import Organization
            import uuid
            
            data = request.data
            
            # Validate required fields
            required_fields = ['type', 'value']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {"error": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get or create internal feed for manual entries (hidden from main feed list)
            default_org, created = Organization.objects.get_or_create(
                name="Internal System",
                defaults={'description': 'Internal system organization for manually created indicators'}
            )
            
            # Create hidden internal feed that won't appear in main threat feeds list
            default_feed, created = ThreatFeed.objects.get_or_create(
                name="Internal Manual Indicators",
                defaults={
                    'description': 'Internal storage for manually created indicators',
                    'is_external': False,
                    'is_active': False,  # Make inactive so it doesn't appear in main feeds list
                    'owner': default_org
                }
            )
            
            # Prepare indicator data with correct fields
            from django.utils import timezone
            now = timezone.now()
            
            indicator_data = {
                'value': data['value'].strip(),
                'type': data['type'],
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'confidence': int(data.get('confidence', 50)),
                'stix_id': f'indicator--{uuid.uuid4()}',
                'threat_feed': data.get('threat_feed_id') and ThreatFeed.objects.get(id=data['threat_feed_id']) or default_feed,
                'first_seen': now,
                'last_seen': now,
            }
            
            # Create the indicator directly using the repository
            from core.repositories.indicator_repository import IndicatorRepository
            indicator = IndicatorRepository.create(indicator_data)
            
            # Log activity
            activity_title = f"New {indicator.type} indicator added"
            activity_description = f"Indicator '{indicator.value}' added manually"
            SystemActivity.log_activity(
                activity_type='indicator_added',
                title=activity_title,
                description=activity_description,
                indicator=indicator,
                threat_feed=indicator.threat_feed,
                metadata={
                    'indicator_type': indicator.type,
                    'confidence': indicator.confidence,
                    'source': 'Manual Entry'
                }
            )

            # Trigger frontend auto-refresh for new indicator
            from django.core.cache import cache
            cache.set('indicators_updated', timezone.now().isoformat(), timeout=300)
            logger.info("🔄 Triggered frontend indicator refresh after manual indicator creation")
            
            # Format response
            feed_name = 'Manual Entry'
            if indicator.threat_feed:
                feed_name = indicator.threat_feed.name
            
            result = {
                'id': indicator.id,
                'type': indicator.type,
                'value': indicator.value,
                'stix_id': indicator.stix_id,
                'name': indicator.name,
                'description': indicator.description,
                'confidence': indicator.confidence,
                'first_seen': indicator.first_seen,
                'last_seen': indicator.last_seen,
                'created_at': indicator.created_at,
                'is_anonymized': indicator.is_anonymized,
                'source': feed_name
            }
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating indicator: {str(e)}")
            return Response(
                {"error": "Failed to create indicator", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def indicators_export(request):
    """Export indicators with chunked processing for large datasets"""
    try:
        data = request.data
        export_format = data.get('format', 'csv')
        export_scope = data.get('scope', 'filtered')
        custom_count = data.get('custom_count', 1000)

        # Get filter parameters from request
        filters = data.get('filters', {})

        # Start with organization-scoped indicators
        from django.db.models import Q

        # Get user's organization
        user_org = getattr(request.user, 'organization', None)

        if user_org is None:
            # User has no organization, return empty queryset
            indicators = Indicator.objects.none()
        elif request.user.role == 'BlueVisionAdmin':
            # BlueVision admins can see all indicators
            indicators = Indicator.objects.select_related('threat_feed').all()
        else:
            # Regular users can see:
            # 1. Indicators from threat feeds owned by their organization (both external and internal)
            # 2. Indicators that have been shared with their organization
            indicators = Indicator.objects.select_related('threat_feed').filter(
                Q(threat_feed__owner=user_org) |  # Feeds consumed by their organization (external or internal)
                Q(sharing_relationships__target_organization=user_org)  # Shared indicators
            ).distinct()

        # Apply filters (same logic as indicators_list)
        if filters.get('type'):
            indicators = indicators.filter(type__icontains=filters['type'])
        if filters.get('source'):
            indicators = indicators.filter(threat_feed__name__icontains=filters['source'])
        if filters.get('searchTerm'):
            from django.db.models import Q
            search = filters['searchTerm']
            indicators = indicators.filter(
                Q(value__icontains=search) |
                Q(description__icontains=search) |
                Q(name__icontains=search)
            )
        if filters.get('severity'):
            indicators = indicators.filter(severity__icontains=filters['severity'])
        if filters.get('status'):
            if filters['status'].lower() == 'anonymized':
                indicators = indicators.filter(is_anonymized=True)
            elif filters['status'].lower() == 'active':
                indicators = indicators.filter(is_anonymized=False)
        if filters.get('dateRange'):
            from datetime import datetime, timedelta
            from django.utils import timezone
            now = timezone.now()
            if filters['dateRange'] == 'last7days':
                start_date = now - timedelta(days=7)
                indicators = indicators.filter(created_at__gte=start_date)
            elif filters['dateRange'] == 'last30days':
                start_date = now - timedelta(days=30)
                indicators = indicators.filter(created_at__gte=start_date)
            elif filters['dateRange'] == 'last90days':
                start_date = now - timedelta(days=90)
                indicators = indicators.filter(created_at__gte=start_date)

        # Apply scope limits
        if export_scope == 'custom':
            indicators = indicators[:custom_count]

        # Order by creation date
        indicators = indicators.order_by('-created_at')

        # Get total count before limiting
        total_count = indicators.count()

        if total_count == 0:
            return Response(
                {"error": "No indicators match the specified criteria"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Use chunked export for better performance
        return _create_chunked_export(indicators, export_format, total_count)

    except Exception as e:
        logger.error(f"Error in indicators export: {str(e)}")
        return Response(
            {"error": "Export failed", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _create_chunked_export(indicators_queryset, export_format, total_count):
    """Create a chunked export response for large datasets"""
    import csv
    import json
    from django.http import StreamingHttpResponse
    from io import StringIO

    def generate_csv():
        """Generate CSV data in chunks to avoid memory issues"""
        # CSV headers
        yield 'Type,Value,Severity,Source,Date Added,Status,Description\n'

        # Process in chunks of 500 to avoid memory issues
        chunk_size = 500
        for offset in range(0, total_count, chunk_size):
            # Get this chunk of indicators
            chunk = indicators_queryset[offset:offset + chunk_size]

            for indicator in chunk:
                # Format data safely, handling None values and escaping quotes
                value = (indicator.value or '').replace('"', '""')  # Escape quotes for CSV
                description = (indicator.description or '').replace('"', '""')[:100]  # Limit length and escape
                source = indicator.threat_feed.name if indicator.threat_feed else 'Unknown'
                status_val = 'Anonymized' if getattr(indicator, 'is_anonymized', False) else 'Active'
                severity = indicator.severity or 'Unknown'
                indicator_type = indicator.type or 'Unknown'

                # Create CSV row with proper quoting
                row = f'"{indicator_type}","{value}","{severity}","{source}","{indicator.created_at.strftime("%Y-%m-%d %H:%M")}","{status_val}","{description}"\n'
                yield row

    def generate_json():
        """Generate JSON data in chunks"""
        yield '{"indicators": [\n'

        chunk_size = 500
        first_item = True

        for offset in range(0, total_count, chunk_size):
            chunk = indicators_queryset[offset:offset + chunk_size]

            for indicator in chunk:
                if not first_item:
                    yield ','
                first_item = False

                indicator_data = {
                    'id': indicator.id,
                    'type': indicator.type or 'Unknown',
                    'value': indicator.value or '',
                    'severity': indicator.severity or 'Unknown',
                    'source': indicator.threat_feed.name if indicator.threat_feed else 'Unknown',
                    'created_at': indicator.created_at.isoformat(),
                    'status': 'Anonymized' if getattr(indicator, 'is_anonymized', False) else 'Active',
                    'description': (indicator.description or '')[:200]  # Limit description length
                }
                yield '\n  ' + json.dumps(indicator_data, ensure_ascii=False)

        yield '\n], "total_count": ' + str(total_count) + ', "export_timestamp": "' + timezone.now().isoformat() + '"}'

    # Create appropriate response based on format
    if export_format == 'csv':
        response = StreamingHttpResponse(
            generate_csv(),
            content_type='text/csv'
        )
        filename = f'indicators_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    else:  # JSON format
        response = StreamingHttpResponse(
            generate_json(),
            content_type='application/json'
        )
        filename = f'indicators_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'

    # Set download headers
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['X-Total-Count'] = str(total_count)
    response['Access-Control-Expose-Headers'] = 'Content-Disposition, X-Total-Count'

    logger.info(f"Starting chunked export of {total_count} indicators in {export_format} format")
    return response

@api_view(['POST'])
@permission_classes([AllowAny])
def indicators_bulk_import(request):
    """Bulk import indicators from a list with security validation."""
    try:
        from core.services.indicator_service import IndicatorService
        from core.models.models import Organization
        import uuid
        import re
        import hashlib
        import time
        
        data = request.data
        
        # Security validation: Check request size and rate limiting
        max_indicators = 10000  # Maximum indicators per request
        # Note: Request size validation removed to avoid "body after reading" error
        # DRF handles request size limits through DATA_UPLOAD_MAX_MEMORY_SIZE setting
        
        # Validate that indicators list is provided
        if 'indicators' not in data or not isinstance(data['indicators'], list):
            return Response(
                {"error": "Missing or invalid 'indicators' field. Expected a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        indicators_data = data['indicators']
        
        if not indicators_data:
            return Response(
                {"error": "Empty indicators list provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if len(indicators_data) > max_indicators:
            return Response(
                {"error": f"Too many indicators. Maximum allowed: {max_indicators}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create internal feed for manual entries (hidden from main feed list)
        default_org, created = Organization.objects.get_or_create(
            name="Internal System",
            defaults={'description': 'Internal system organization for manually created indicators'}
        )
        
        # Create hidden internal feed that won't appear in main threat feeds list
        default_feed, created = ThreatFeed.objects.get_or_create(
            name="Internal Manual Indicators",
            defaults={
                'description': 'Internal storage for manually created indicators',
                'is_external': False,
                'is_active': False,  # Make inactive so it doesn't appear in main feeds list
                'owner': default_org
            }
        )
        
        from core.repositories.indicator_repository import IndicatorRepository
        from django.utils import timezone
        created_indicators = []
        errors = []
        
        # Security validation function for indicator data
        def validate_and_sanitize_indicator(indicator_data, idx):
            """Validate and sanitize individual indicator data"""
            errors = []
            
            # Validate required fields
            required_fields = ['type', 'value']
            for field in required_fields:
                if field not in indicator_data:
                    errors.append(f"Indicator {idx + 1}: Missing required field '{field}'")
                    return None, errors
            
            # Sanitize and validate indicator value
            value = str(indicator_data['value']).strip()
            if not value:
                errors.append(f"Indicator {idx + 1}: Empty value")
                return None, errors
            
            # Length validation
            if len(value) > 2048:  # Max 2KB per value
                errors.append(f"Indicator {idx + 1}: Value too long (max 2048 characters)")
                return None, errors
            
            # Pattern validation based on type
            indicator_type = str(indicator_data['type']).lower().strip()
            validation_patterns = {
                'ip': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                'domain': r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.?$',
                'url': r'^https?://[^\s/$.?#].[^\s]*$',
                'file_hash': r'^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$|^[a-fA-F0-9]{128}$',  # MD5, SHA1, SHA256, SHA512
                'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            }
            
            if indicator_type in validation_patterns:
                if not re.match(validation_patterns[indicator_type], value):
                    errors.append(f"Indicator {idx + 1}: Invalid {indicator_type} format")
                    return None, errors
            
            # Check for malicious patterns
            malicious_patterns = [
                r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
                r'javascript:',
                r'vbscript:',
                r'on\w+\s*=',
                r'<iframe\b[^>]*>',
                r'eval\s*\(',
                r'document\.cookie',
                r'window\.location',
            ]
            
            for pattern in malicious_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    errors.append(f"Indicator {idx + 1}: Potentially malicious content detected")
                    return None, errors
            
            # Sanitize name
            name = str(indicator_data.get('name', '')).strip()
            if len(name) > 500:  # Max 500 chars for name
                name = name[:500]
            
            # Sanitize description
            description = str(indicator_data.get('description', '')).strip()
            if len(description) > 1000:  # Max 1KB description
                description = description[:1000]
            
            # Validate confidence
            try:
                confidence = int(indicator_data.get('confidence', 50))
                if confidence < 0 or confidence > 100:
                    confidence = 50  # Default to medium confidence
            except (ValueError, TypeError):
                confidence = 50
            
            return {
                'type': indicator_type,
                'value': value,
                'name': name,
                'description': description,
                'confidence': confidence
            }, errors

        # Process each indicator
        for idx, indicator_data in enumerate(indicators_data):
            try:
                # Validate and sanitize indicator
                sanitized_data, validation_errors = validate_and_sanitize_indicator(indicator_data, idx)
                
                if validation_errors:
                    errors.extend(validation_errors)
                    continue
                
                if not sanitized_data:
                    continue
                
                # Check for duplicates using sanitized data
                existing = Indicator.objects.filter(
                    value=sanitized_data['value'],
                    type=sanitized_data['type']
                ).first()
                
                if existing:
                    # Skip duplicate
                    continue
                
                # Prepare indicator data with correct fields using sanitized data
                now = timezone.now()
                indicator_create_data = {
                    'value': sanitized_data['value'],
                    'type': sanitized_data['type'],
                    'name': sanitized_data.get('name', ''),
                    'description': sanitized_data['description'],
                    'confidence': sanitized_data['confidence'],
                    'stix_id': f'indicator--{uuid.uuid4()}',
                    'threat_feed': indicator_data.get('threat_feed_id') and ThreatFeed.objects.get(id=indicator_data['threat_feed_id']) or default_feed,
                    'first_seen': now,
                    'last_seen': now,
                }
                
                # Create the indicator
                indicator = IndicatorRepository.create(indicator_create_data)
                
                # Format for response
                feed_name = 'Manual Entry'
                if indicator.threat_feed:
                    feed_name = indicator.threat_feed.name
                
                created_indicators.append({
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value,
                    'stix_id': indicator.stix_id,
                    'name': indicator.name,
                    'description': indicator.description,
                    'confidence': indicator.confidence,
                    'first_seen': indicator.first_seen,
                    'last_seen': indicator.last_seen,
                    'created_at': indicator.created_at,
                    'is_anonymized': indicator.is_anonymized,
                    'source': feed_name
                })
                
            except Exception as e:
                errors.append(f"Indicator {idx + 1}: {str(e)}")
                continue
        
        # Log bulk import activity
        if len(created_indicators) > 0:
            activity_title = f"Bulk imported {len(created_indicators)} indicators"
            activity_description = f"Successfully imported {len(created_indicators)} indicators with {len(errors)} errors"
            SystemActivity.log_activity(
                activity_type='indicators_bulk_added',
                title=activity_title,
                description=activity_description,
                metadata={
                    'imported_count': len(created_indicators),
                    'error_count': len(errors),
                    'total_attempted': len(indicators_data)
                }
            )

            # Trigger frontend auto-refresh for bulk imported indicators
            from django.core.cache import cache
            from django.utils import timezone
            cache.set('indicators_updated', timezone.now().isoformat(), timeout=300)
            logger.info(f"🔄 Triggered frontend indicator refresh after bulk import of {len(created_indicators)} indicators")
        
        return Response({
            'success': True,
            'created_count': len(created_indicators),
            'error_count': len(errors),
            'created_indicators': created_indicators,
            'errors': errors
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in bulk import: {str(e)}")
        return Response(
            {"error": "Failed to bulk import indicators", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([AllowAny])
def indicator_update(request, indicator_id):
    """Update a specific indicator."""
    try:
        from core.repositories.indicator_repository import IndicatorRepository
        
        # Get the indicator
        indicator = IndicatorRepository.get_by_id(indicator_id)
        if not indicator:
            return Response(
                {"error": "Indicator not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        
        # Prepare update data (only allow certain fields to be updated)
        update_data = {}
        updatable_fields = ['value', 'type', 'name', 'description', 'confidence']
        
        for field in updatable_fields:
            if field in data:
                if field == 'confidence':
                    update_data[field] = int(data[field])
                else:
                    update_data[field] = data[field]
        
        # Update the indicator
        updated_indicator = IndicatorRepository.update(indicator_id, update_data)
        
        if not updated_indicator:
            return Response(
                {"error": "Failed to update indicator"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Format response
        feed_name = 'Manual Entry'
        if updated_indicator.threat_feed:
            feed_name = updated_indicator.threat_feed.name
        
        result = {
            'id': updated_indicator.id,
            'type': updated_indicator.type,
            'value': updated_indicator.value,
            'stix_id': updated_indicator.stix_id,
            'name': updated_indicator.name,
            'description': updated_indicator.description,
            'confidence': updated_indicator.confidence,
            'first_seen': updated_indicator.first_seen,
            'last_seen': updated_indicator.last_seen,
            'created_at': updated_indicator.created_at,
            'is_anonymized': updated_indicator.is_anonymized,
            'source': feed_name
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating indicator: {str(e)}")
        return Response(
            {"error": "Failed to update indicator", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def indicator_delete(request, indicator_id):
    """Delete a specific indicator."""
    try:
        from core.repositories.indicator_repository import IndicatorRepository
        from core.services.audit_service import AuditService

        # Get the indicator first to check if it exists
        indicator = IndicatorRepository.get_by_id(indicator_id)
        if not indicator:
            return Response(
                {"error": "Indicator not found", "indicator_id": indicator_id},
                status=status.HTTP_404_NOT_FOUND
            )

        # Store indicator info for audit logging
        indicator_info = {
            'id': indicator.id,
            'type': indicator.type,
            'value': indicator.value[:50] + '...' if len(indicator.value) > 50 else indicator.value
        }

        # Delete the indicator
        deleted = IndicatorRepository.delete(indicator_id)

        if deleted:
            # Log the deletion for audit purposes
            audit_service = AuditService()
            audit_service.log_user_action(
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                action='indicator_deleted',
                success=True,
                additional_data={
                    'description': f'Indicator {indicator_info["type"]}: {indicator_info["value"]} deleted',
                    'indicator_id': indicator_id,
                    'indicator_info': indicator_info
                }
            )

            return Response(
                {
                    "success": True,
                    "message": "Indicator deleted successfully",
                    "indicator_id": indicator_id
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Failed to delete indicator"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Error deleting indicator {indicator_id}: {str(e)}")
        return Response(
            {"error": "Failed to delete indicator", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def indicators_bulk_delete(request):
    """Bulk delete indicators or clear all indicators."""
    try:
        from core.repositories.indicator_repository import IndicatorRepository
        from core.services.audit_service import AuditService
        from core.models.models import Indicator
        
        # Get request data
        data = request.data if hasattr(request, 'data') and request.data else {}
        
        # Check if this is a "clear all" request
        clear_all = data.get('clear_all', False)
        indicator_ids = data.get('indicator_ids', [])
        
        if clear_all:
            # Check if user is authenticated and is a superuser
            is_superuser = (hasattr(request, 'user') and
                          request.user.is_authenticated and
                          getattr(request.user, 'is_superuser', False))

            # Get user's organization
            user_org = getattr(request.user, 'organization', None) if hasattr(request, 'user') and request.user.is_authenticated else None

            if is_superuser:
                # Superusers can delete ALL indicators regardless of organization
                indicators = Indicator.objects.all()
            elif user_org:
                # Regular users only delete indicators from their organization's feeds
                # Use the correct relationship: threat_feed__owner (not organization)
                indicators = Indicator.objects.filter(threat_feed__owner=user_org)
            else:
                # Unauthenticated requests - no deletion allowed
                return Response(
                    {"error": "Authentication required to delete indicators"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            total_count = indicators.count()
            
            if total_count == 0:
                return Response(
                    {"success": True, "message": "No indicators to delete", "deleted_count": 0},
                    status=status.HTTP_200_OK
                )
            
            # Delete all indicators in batches to avoid memory issues
            batch_size = 1000
            deleted_count = 0
            
            while indicators.exists():
                batch_ids = list(indicators.values_list('id', flat=True)[:batch_size])
                batch_deleted, _ = Indicator.objects.filter(id__in=batch_ids).delete()
                deleted_count += batch_deleted
                
                # Log progress for large deletions
                if deleted_count % 5000 == 0:
                    logger.info(f"Bulk delete progress: {deleted_count}/{total_count} indicators deleted")
            
            # Log the bulk deletion for audit purposes
            audit_service = AuditService()
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            audit_service.log_user_action(
                user=user,
                action='indicators_bulk_deleted',
                success=True,
                additional_data={
                    'description': f'Bulk deleted all indicators (total: {deleted_count})',
                    'deleted_count': deleted_count,
                    'clear_all': True,
                    'user_role': getattr(user, 'role', 'Unknown') if user else 'Unauthenticated'
                }
            )
            
            return Response(
                {
                    "success": True,
                    "message": f"Successfully deleted all {deleted_count} indicators",
                    "deleted_count": deleted_count,
                    "operation": "clear_all"
                },
                status=status.HTTP_200_OK
            )
            
        elif indicator_ids:
            # Bulk delete specific indicators
            if not isinstance(indicator_ids, list):
                return Response(
                    {"error": "indicator_ids must be a list"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Limit the number of indicators that can be deleted at once
            if len(indicator_ids) > 10000:
                return Response(
                    {"error": "Cannot delete more than 10,000 indicators at once"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get indicators that exist
            existing_indicators = Indicator.objects.filter(id__in=indicator_ids)
            existing_count = existing_indicators.count()
            
            if existing_count == 0:
                return Response(
                    {"success": True, "message": "No valid indicators found to delete", "deleted_count": 0},
                    status=status.HTTP_200_OK
                )
            
            # Delete the indicators
            deleted_count, _ = existing_indicators.delete()
            
            # Log the bulk deletion for audit purposes
            audit_service = AuditService()
            audit_service.log_user_action(
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                action='indicators_bulk_deleted',
                success=True,
                additional_data={
                    'description': f'Bulk deleted {deleted_count} indicators',
                    'deleted_count': deleted_count,
                    'requested_ids': len(indicator_ids),
                    'indicator_ids': indicator_ids[:100]  # Log first 100 IDs only
                }
            )
            
            return Response(
                {
                    "success": True,
                    "message": f"Successfully deleted {deleted_count} out of {len(indicator_ids)} requested indicators",
                    "deleted_count": deleted_count,
                    "requested_count": len(indicator_ids),
                    "operation": "bulk_delete"
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Must provide either 'clear_all': true or 'indicator_ids': [...]"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error in bulk delete indicators: {str(e)}")
        return Response(
            {"error": "Failed to delete indicators", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def indicator_share(request, indicator_id):
    """Share an indicator with specified organizations using comprehensive sharing service."""
    try:
        from core.services.ioc_sharing_service import IOCSharingService
        from core.repositories.indicator_repository import IndicatorRepository

        # Get the indicator
        indicator = IndicatorRepository.get_by_id(indicator_id)
        if not indicator:
            return Response(
                {"error": "Indicator not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data

        # Validate required fields
        if 'organizations' not in data or not isinstance(data['organizations'], list):
            return Response(
                {"error": "Missing or invalid 'organizations' field. Expected a list of organization IDs."},
                status=status.HTTP_400_BAD_REQUEST
            )

        organizations = data['organizations']
        anonymization_level = data.get('anonymization_level', 'partial')
        share_method = data.get('share_method', 'taxii')

        # Use the IOC sharing service
        sharing_service = IOCSharingService()

        # Share with organizations
        result = sharing_service.share_indicators_with_organizations(
            indicator_ids=[indicator_id],
            target_organizations=organizations,
            sharing_user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
            anonymization_level=anonymization_level,
            share_method=share_method
        )

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error sharing indicator: {str(e)}")
        return Response(
            {"error": "Failed to share indicator", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def indicator_generate_share_url(request, indicator_id):
    """Generate a secure share URL for an indicator."""
    try:
        from core.services.ioc_sharing_service import IOCSharingService

        data = request.data
        expiry_hours = data.get('expiry_hours', 24)
        access_type = data.get('access_type', 'view')

        # Use the IOC sharing service
        sharing_service = IOCSharingService()

        # Generate share URL
        result = sharing_service.generate_share_url(
            indicator_id=indicator_id,
            sharing_user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
            expiry_hours=expiry_hours,
            access_type=access_type
        )

        return Response(result, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except PermissionError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        logger.error(f"Error generating share URL: {str(e)}")
        return Response(
            {"error": "Failed to generate share URL", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def indicator_shared_access(request, share_token):
    """Access a shared indicator using a share token."""
    try:
        from core.services.ioc_sharing_service import IOCSharingService

        # Use the IOC sharing service
        sharing_service = IOCSharingService()

        # Access shared indicator
        result = sharing_service.access_shared_indicator(
            share_token=share_token,
            accessing_user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        )

        return Response(result, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error accessing shared indicator: {str(e)}")
        return Response(
            {"error": "Failed to access shared indicator", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def sharing_permissions(request):
    """Get sharing permissions for the current user."""
    try:
        from core.services.ioc_sharing_service import IOCSharingService

        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Use the IOC sharing service
        sharing_service = IOCSharingService()

        # Get permissions
        permissions = sharing_service.get_sharing_permissions(request.user)

        return Response(permissions, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting sharing permissions: {str(e)}")
        return Response(
            {"error": "Failed to get sharing permissions", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def shared_indicators(request):
    """Get indicators shared with the current user's organization."""
    try:
        from core.services.ioc_sharing_service import IOCSharingService

        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get user's organization
        user_org = getattr(request.user, 'organization', None)
        if not user_org:
            return Response(
                {"error": "User not associated with an organization"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use the IOC sharing service
        sharing_service = IOCSharingService()

        # Get shared indicators
        shared_indicators = sharing_service.get_shared_indicators_for_organization(user_org)

        return Response({
            'success': True,
            'shared_indicators': shared_indicators,
            'count': len(shared_indicators),
            'organization': {
                'id': str(user_org.id),
                'name': user_org.name
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting shared indicators: {str(e)}")
        return Response(
            {"error": "Failed to get shared indicators", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def system_health(request):
    """Get system health status including database, Redis, and system resources."""
    try:
        import psutil
        from django.db import connection
        from django.core.cache import cache
        from django.utils import timezone
        import redis
        
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': {},
            'services': {'redis': {}},
            'system': {},
            'feeds': {}
        }
        
        overall_status = 'healthy'
        
        # Database health check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    health_data['database'] = {
                        'status': 'healthy',
                        'connection': 'active',
                        'connection_count': 1,
                        'details': 'Database connection successful'
                    }
                else:
                    health_data['database'] = {
                        'status': 'unhealthy',
                        'connection': 'failed',
                        'connection_count': 0,
                        'details': 'Database query returned unexpected result'
                    }
                    overall_status = 'unhealthy'
        except Exception as e:
            health_data['database'] = {
                'status': 'unhealthy',
                'connection': 'failed',
                'connection_count': 0,
                'details': f'Database error: {str(e)}'
            }
            overall_status = 'unhealthy'
        
        # Redis health check
        try:
            # Try to connect to Redis using cache framework
            cache.set('health_check', 'test', 10)
            test_value = cache.get('health_check')
            if test_value == 'test':
                health_data['services']['redis'] = {
                    'status': 'healthy',
                    'connection': 'active',
                    'info': '6.0+',
                    'details': 'Redis connection and operations successful'
                }
            else:
                health_data['services']['redis'] = {
                    'status': 'unhealthy',
                    'connection': 'failed',
                    'info': 'unknown',
                    'details': 'Redis cache test failed'
                }
                overall_status = 'degraded'
        except Exception as e:
            health_data['services']['redis'] = {
                'status': 'unhealthy',
                'connection': 'failed',
                'info': 'unknown',
                'details': f'Redis error: {str(e)}'
            }
            overall_status = 'degraded'
        
        # System resources check
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine resource status
            resource_status = 'healthy'
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                resource_status = 'warning'
                if overall_status == 'healthy':
                    overall_status = 'degraded'
            
            health_data['system'] = {
                'status': resource_status,
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'disk_percent': round(disk.percent, 1),
                'last_check': timezone.now().isoformat(),
                'details': f'CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%, Disk: {disk.percent:.1f}%'
            }
        except Exception as e:
            health_data['system'] = {
                'status': 'unknown',
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_percent': 0.0,
                'last_check': timezone.now().isoformat(),
                'details': f'Resource monitoring error: {str(e)}'
            }
        
        # Feed status summary
        try:
            total_feeds = ThreatFeed.objects.count()
            active_feeds = ThreatFeed.objects.filter(is_active=True).count()
            external_feeds = ThreatFeed.objects.filter(is_external=True, is_active=True).count()
            
            # Get individual feed details
            feeds_list = []
            # Get user's organization for filtering
            user_org = getattr(request.user, 'organization', None)

            if user_org is None:
                # User has no organization, only show external feeds
                feeds_queryset = ThreatFeed.objects.filter(is_external=True)
            elif request.user.role == 'BlueVisionAdmin':
                feeds_queryset = ThreatFeed.objects.all()
            else:
                # Regular users can see external feeds + their organization's internal feeds
                from django.db.models import Q
                feeds_queryset = ThreatFeed.objects.filter(
                    Q(is_external=True) |  # All external feeds
                    Q(owner=user_org, is_external=False)  # Own organization's internal feeds
                )

            for feed in feeds_queryset:
                # Get feed sync status
                sync_status = 'healthy' if feed.is_active else 'inactive'
                if feed.last_sync:
                    # Check if last sync was recent (within 24 hours)
                    time_since_sync = timezone.now() - feed.last_sync
                    if time_since_sync.total_seconds() > 86400:  # 24 hours
                        sync_status = 'warning'
                
                feeds_list.append({
                    'id': feed.id,
                    'name': feed.name,
                    'is_active': feed.is_active,
                    'is_external': feed.is_external,
                    'sync_status': sync_status,
                    'last_sync': feed.last_sync.isoformat() if feed.last_sync else None,
                    'description': feed.description or '',
                    'last_error': None  # Add error tracking if needed
                })
            
            health_data['feeds'] = {
                'status': 'healthy' if active_feeds > 0 else 'warning',
                'total': total_feeds,
                'active': active_feeds,
                'external': external_feeds,
                'feeds': feeds_list,
                'details': f'{active_feeds}/{total_feeds} feeds active, {external_feeds} external'
            }
        except Exception as e:
            health_data['feeds'] = {
                'status': 'unknown',
                'total': 0,
                'active': 0,
                'external': 0,
                'feeds': [],
                'details': f'Feed status error: {str(e)}'
            }
        
        health_data['status'] = overall_status
        
        return Response(health_data)
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return Response({
            'status': 'error',
            'timestamp': timezone.now().isoformat(),
            'error': 'Failed to get system health',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def recent_activities(request):
    """Get recent system activities for dashboard."""
    try:
        # Get limit parameter (default to 20)
        limit = int(request.GET.get('limit', 20))
        if limit > 100:  # Cap the limit
            limit = 100
        
        # Fetch recent activities - remove user relation to avoid DB errors
        activities = SystemActivity.objects.select_related(
            'threat_feed', 'indicator', 'organization'
        ).order_by('-created_at')[:limit]
        
        # Format activities for frontend
        activities_data = []
        for activity in activities:
            # Calculate time ago
            time_diff = timezone.now() - activity.created_at
            if time_diff.total_seconds() < 60:
                time_ago = "Just now"
            elif time_diff.total_seconds() < 3600:
                minutes = int(time_diff.total_seconds() / 60)
                time_ago = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif time_diff.total_seconds() < 86400:
                hours = int(time_diff.total_seconds() / 3600)
                time_ago = f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(time_diff.total_seconds() / 86400)
                time_ago = f"{days} day{'s' if days != 1 else ''} ago"
            
            activities_data.append({
                'id': activity.id,
                'type': activity.activity_type,
                'category': activity.category,
                'title': activity.title,
                'description': activity.description or '',
                'badge_text': activity.get_activity_type_display(),
                'time_ago': time_ago,
                'timestamp': activity.created_at.isoformat(),
                'metadata': activity.metadata or {},
                'related_objects': {
                    'threat_feed': {
                        'id': str(activity.threat_feed.id),
                        'name': activity.threat_feed.name
                    } if activity.threat_feed else None,
                    'indicator': {
                        'id': str(activity.indicator.id),
                        'value': activity.indicator.value,
                        'type': activity.indicator.type
                    } if activity.indicator else None,
                    'organization': {
                        'id': str(activity.organization.id),
                        'name': activity.organization.name
                    } if activity.organization else None,
                }
            })
        
        return Response({
            'success': True,
            'count': len(activities_data),
            'activities': activities_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching recent activities: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch recent activities',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def threat_activity_chart_data(request):
    """Get historical IoC data aggregated by date for the threat activity chart."""
    try:
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        import json
        
        # Get date range parameters
        days = int(request.GET.get('days', 30))  # Default to 30 days
        indicator_type = request.GET.get('type', None)  # Optional filter by indicator type
        feed_id = request.GET.get('feed_id', None)  # Optional filter by feed
        
        # Validate days parameter
        if days < 1 or days > 365:
            days = 30
            
        # Calculate date range
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Build base query
        query = Indicator.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Apply filters
        if indicator_type:
            query = query.filter(type=indicator_type)
        if feed_id:
            query = query.filter(threat_feed_id=feed_id)
        
        # Aggregate by date and type
        daily_data = query.extra(
            select={'date': 'DATE(created_at)'}
        ).values('date', 'type').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Also get overall daily totals
        daily_totals = query.extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            total=Count('id')
        ).order_by('date')
        
        # Process data for chart
        chart_data = {}
        type_data = {}
        
        # Initialize all dates in range with zero counts
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            chart_data[date_str] = 0
            current_date += timedelta(days=1)
        
        # Fill in actual totals
        for item in daily_totals:
            date_str = item['date'].strftime('%Y-%m-%d')
            chart_data[date_str] = item['total']
        
        # Process type breakdown
        for item in daily_data:
            date_str = item['date'].strftime('%Y-%m-%d')
            ioc_type = item['type']
            count = item['count']
            
            if date_str not in type_data:
                type_data[date_str] = {}
            type_data[date_str][ioc_type] = count
        
        # Convert to list format for D3
        result_data = []
        for date_str in sorted(chart_data.keys()):
            result_data.append({
                'date': date_str,
                'count': chart_data[date_str],
                'types': type_data.get(date_str, {})
            })
        
        # Get summary statistics
        total_indicators = sum(chart_data.values())
        avg_daily = total_indicators / days if days > 0 else 0
        
        # Get type distribution for the period
        type_summary = Indicator.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        if indicator_type:
            type_summary = type_summary.filter(type=indicator_type)
        if feed_id:
            type_summary = type_summary.filter(threat_feed_id=feed_id)
            
        type_counts = type_summary.values('type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'success': True,
            'data': result_data,
            'summary': {
                'total_indicators': total_indicators,
                'avg_daily': round(avg_daily, 2),
                'days': days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'type_distribution': list(type_counts)
            },
            'filters': {
                'type': indicator_type,
                'feed_id': feed_id,
                'days': days
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting threat activity chart data: {str(e)}")
        return Response(
            {"error": "Failed to get chart data", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def ttps_list(request):
    """
    GET: Get list of TTPs with advanced filtering and pagination using TTPFilterService.
    POST: Create a new TTP with validation.
    
    GET Query Parameters:
    - Basic pagination:
      * page: Page number (default: 1)
      * page_size: Items per page (default: 20, max: 100)
    
    - Filter parameters:
      * tactics: Comma-separated list of MITRE tactics
      * techniques: Comma-separated list of technique IDs
      * technique_search: Partial technique ID search
      * severity_levels: Comma-separated severity levels (critical,high,medium,low,info)
      * date_from: Start date (ISO format)
      * date_to: End date (ISO format) 
      * created_after: Created after date (ISO format)
      * created_before: Created before date (ISO format)
      * threat_feed_ids: Comma-separated threat feed IDs
      * external_feeds_only: true/false - filter by external feeds only
      * active_feeds_only: true/false - filter by active feeds only
      * search: Search query across multiple fields
      * search_fields: Comma-separated fields to search (name,description,mitre_technique_id,mitre_subtechnique)
      * has_subtechniques: true/false - filter by presence of subtechniques
      * anonymized_only: true/false - filter by anonymization status
    
    - Sorting parameters:
      * sort_by: Field to sort by (name,mitre_technique_id,mitre_tactic,created_at,updated_at,severity_score)
      * sort_order: asc/desc (default: desc)
    
    - Legacy parameters (backward compatibility):
      * tactic: Single MITRE tactic filter
      * technique_id: Single technique ID filter
      * feed_id: Single threat feed ID filter
      * ordering: Sort field with direction prefix
    
    POST Body Parameters:
    - name: TTP name (required)
    - description: TTP description (required)
    - mitre_technique_id: MITRE ATT&CK technique ID (required, e.g., T1566.001)
    - mitre_tactic: MITRE tactic (required, from MITRE_TACTIC_CHOICES)
    - mitre_subtechnique: MITRE subtechnique name (optional)
    - threat_feed_id: ID of associated threat feed (optional, defaults to manual entry feed)
    - stix_id: Custom STIX ID (optional, auto-generated if not provided)
    """
    
    if request.method == 'POST':
        return _create_ttp(request)
    
    # Handle GET request with new filter service
    try:
        from core.services.ttp_filter_service import TTPFilterService
        
        # Initialize filter service
        filter_service = TTPFilterService()
        
        # Check if using legacy parameters for backward compatibility
        legacy_params = ['tactic', 'technique_id', 'feed_id', 'ordering']
        is_legacy_request = any(param in request.GET for param in legacy_params)
        
        if is_legacy_request:
            # Handle legacy request format
            return _handle_legacy_ttp_request(request, filter_service)
        
        # Build filter criteria from request
        criteria = filter_service.build_criteria_from_request(request)
        
        # Apply filters and get results
        result = filter_service.filter_ttps(criteria)
        
        # Build response in expected format
        response_data = {
            'success': True,
            'count': result.total_count,
            'filtered_count': result.filtered_count,
            'num_pages': result.total_pages,
            'current_page': result.page,
            'page_size': result.page_size,
            'has_next': result.has_next,
            'has_previous': result.has_previous,
            'next_page': result.page + 1 if result.has_next else None,
            'previous_page': result.page - 1 if result.has_previous else None,
            'results': result.ttps,
            'filters_applied': result.filters_applied,
            'statistics': result.statistics
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting TTPs list with filters: {str(e)}")
        return Response(
            {"error": "Failed to get TTPs list", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _handle_legacy_ttp_request(request, filter_service):
    """Handle legacy TTP request format for backward compatibility"""
    try:
        # Convert legacy parameters to new format
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        tactic = request.GET.get('tactic', '').strip()
        technique_id = request.GET.get('technique_id', '').strip()
        search = request.GET.get('search', '').strip()
        feed_id = request.GET.get('feed_id', '').strip()
        ordering = request.GET.get('ordering', '-created_at')
        
        # Build criteria using legacy parameters
        from core.services.ttp_filter_service import FilterCriteria, SortOrder
        
        # Parse ordering
        sort_by = ordering.lstrip('-')
        sort_order = SortOrder.DESC if ordering.startswith('-') else SortOrder.ASC
        
        criteria = FilterCriteria(
            tactics=[tactic] if tactic else None,
            technique_search=technique_id if technique_id else None,
            search_query=search if search else None,
            threat_feed_ids=[int(feed_id)] if feed_id and feed_id.isdigit() else None,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Apply filters
        result = filter_service.filter_ttps(criteria)
        
        # Return in legacy format
        response_data = {
            'success': True,
            'count': result.filtered_count,
            'num_pages': result.total_pages,
            'current_page': result.page,
            'page_size': result.page_size,
            'has_next': result.has_next,
            'has_previous': result.has_previous,
            'next_page': result.page + 1 if result.has_next else None,
            'previous_page': result.page - 1 if result.has_previous else None,
            'results': result.ttps,
            'filters': {
                'tactic': tactic,
                'technique_id': technique_id,
                'search': search,
                'feed_id': feed_id,
                'ordering': ordering
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error handling legacy TTP request: {str(e)}")
        return Response(
            {"error": "Failed to process legacy TTP request", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _create_ttp(request):
    """
    Create a new TTP with comprehensive validation.
    """
    try:
        from core.repositories.ttp_repository import TTPRepository
        from core.services.ttp_service import TTPService
        import uuid
        import re
        
        data = request.data
        errors = []
        
        # Validate required fields
        required_fields = ['name', 'description', 'mitre_technique_id', 'mitre_tactic']
        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                errors.append(f"Field '{field}' is required and cannot be empty")
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract and validate data
        name = str(data['name']).strip()
        description = str(data['description']).strip()
        mitre_technique_id = str(data['mitre_technique_id']).strip().upper()
        mitre_tactic = str(data['mitre_tactic']).strip().lower()
        mitre_subtechnique = str(data.get('mitre_subtechnique', '')).strip() or None
        threat_feed_id = data.get('threat_feed_id')
        stix_id = str(data.get('stix_id', '')).strip() or None
        
        # Validate name length
        if len(name) < 3:
            errors.append("TTP name must be at least 3 characters long")
        if len(name) > 255:
            errors.append("TTP name cannot exceed 255 characters")
            
        # Validate description length
        if len(description) < 10:
            errors.append("TTP description must be at least 10 characters long")
        if len(description) > 5000:
            errors.append("TTP description cannot exceed 5000 characters")
        
        # Validate MITRE technique ID format
        mitre_pattern = r'^T\d{4}(\.\d{3})?$'
        if not re.match(mitre_pattern, mitre_technique_id):
            errors.append("MITRE technique ID must follow format T1234 or T1234.001 (e.g., T1566.001)")
        
        # Validate MITRE tactic
        valid_tactics = [choice[0] for choice in TTPData.MITRE_TACTIC_CHOICES]
        if mitre_tactic not in valid_tactics:
            errors.append(f"Invalid MITRE tactic. Must be one of: {', '.join(valid_tactics)}")
        
        # Validate subtechnique length if provided
        if mitre_subtechnique and len(mitre_subtechnique) > 255:
            errors.append("MITRE subtechnique name cannot exceed 255 characters")
        
        # Get or create default threat feed if not provided
        if threat_feed_id:
            try:
                threat_feed_id = int(threat_feed_id)
                threat_feed = ThreatFeed.objects.get(id=threat_feed_id)
            except (ValueError, ThreatFeed.DoesNotExist):
                errors.append(f"Invalid threat feed ID: {threat_feed_id}")
                threat_feed = None
        else:
            # Get or create default manual entry feed
            from core.models.models import Organization
            default_org, created = Organization.objects.get_or_create(
                name="Manual Entry",
                defaults={'description': 'Default organization for manually created TTPs'}
            )
            
            threat_feed, created = ThreatFeed.objects.get_or_create(
                name="Manual TTP Feed",
                defaults={
                    'description': 'Default feed for manually created TTPs',
                    'is_external': False,
                    'is_active': True,
                    'owner': default_org
                }
            )
        
        # Generate STIX ID if not provided
        if not stix_id:
            stix_id = f"attack-pattern--{str(uuid.uuid4())}"
        else:
            # Validate STIX ID format
            stix_pattern = r'^attack-pattern--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if not re.match(stix_pattern, stix_id):
                errors.append("STIX ID must follow format: attack-pattern--xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        
        # Check for duplicate MITRE technique ID within the same feed
        existing_ttp = TTPData.objects.filter(
            mitre_technique_id=mitre_technique_id,
            threat_feed=threat_feed
        ).first()
        
        if existing_ttp:
            errors.append(f"TTP with MITRE technique ID '{mitre_technique_id}' already exists in this threat feed")
        
        # Check for duplicate STIX ID
        if TTPData.objects.filter(stix_id=stix_id).exists():
            errors.append(f"TTP with STIX ID '{stix_id}' already exists")
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the TTP
        ttp_data = {
            'name': name,
            'description': description,
            'mitre_technique_id': mitre_technique_id,
            'mitre_tactic': mitre_tactic,
            'mitre_subtechnique': mitre_subtechnique,
            'threat_feed': threat_feed,
            'stix_id': stix_id,
            'is_anonymized': False
        }
        
        # Use TTPService for creation if available, otherwise use repository
        try:
            ttp_service = TTPService()
            ttp = ttp_service.create_ttp(ttp_data)
        except:
            # Fallback to repository method
            ttp = TTPRepository.create(ttp_data)
        
        # Log the creation activity
        try:
            SystemActivity.objects.create(
                activity_type='ttp_created',
                description=f'New TTP created: {ttp.name} ({ttp.mitre_technique_id})',
                details={
                    'ttp_id': ttp.id,
                    'mitre_technique_id': ttp.mitre_technique_id,
                    'mitre_tactic': ttp.mitre_tactic,
                    'threat_feed_id': ttp.threat_feed.id if ttp.threat_feed else None,
                    'source': 'manual_creation'
                }
            )
        except Exception as e:
            logger.warning(f"Could not log TTP creation activity: {str(e)}")
        
        # Format response data
        tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic)
        
        response_data = {
            'success': True,
            'message': 'TTP created successfully',
            'data': {
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': ttp.mitre_tactic,
                'mitre_tactic_display': tactic_display,
                'mitre_subtechnique': ttp.mitre_subtechnique,
                'stix_id': ttp.stix_id,
                'threat_feed': {
                    'id': ttp.threat_feed.id,
                    'name': ttp.threat_feed.name,
                    'is_external': ttp.threat_feed.is_external
                } if ttp.threat_feed else None,
                'is_anonymized': ttp.is_anonymized,
                'created_at': ttp.created_at.isoformat(),
                'updated_at': ttp.updated_at.isoformat(),
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating TTP: {str(e)}")
        return Response(
            {"error": "Failed to create TTP", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _update_ttp(request, ttp_id):
    """
    Update an existing TTP with validation and conflict detection.

    Supports both PUT (complete update) and PATCH (partial update) methods.
    """
    try:
        from core.repositories.ttp_repository import TTPRepository
        from core.services.ttp_service import TTPService
        import re

        # Check permissions - only publishers and BlueVision admins can edit TTPs
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Authentication required to edit TTPs"
            }, status=status.HTTP_401_UNAUTHORIZED)

        user_role = getattr(request.user, 'role', 'viewer')
        user_org = getattr(request.user, 'organization', None)

        if user_role not in ['publisher', 'BlueVisionAdmin'] and not request.user.is_superuser:
            org_name = user_org.name if user_org else "your organization"
            return Response({
                "success": False,
                "message": f"Access denied. Only publishers can edit TTPs. Please contact the administrator of {org_name} to request publisher access.",
                "user_role": user_role,
                "required_roles": ["publisher", "BlueVisionAdmin"]
            }, status=status.HTTP_403_FORBIDDEN)

        # Get the existing TTP
        ttp = TTPRepository.get_by_id(ttp_id)
        if not ttp:
            return Response(
                {"error": "TTP not found", "ttp_id": ttp_id},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        errors = []
        is_put = request.method == 'PUT'
        
        # For PUT requests, validate that all required fields are present
        if is_put:
            required_fields = ['name', 'description', 'mitre_technique_id', 'mitre_tactic']
            for field in required_fields:
                if not data.get(field) or not str(data.get(field)).strip():
                    errors.append(f"Field '{field}' is required for PUT requests and cannot be empty")
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare update data with existing values as fallback
        update_data = {}
        
        # Handle name field
        if 'name' in data:
            name = str(data['name']).strip()
            if len(name) < 3:
                errors.append("TTP name must be at least 3 characters long")
            elif len(name) > 255:
                errors.append("TTP name cannot exceed 255 characters")
            else:
                update_data['name'] = name
        elif is_put:
            update_data['name'] = ttp.name  # Keep existing for PUT
        
        # Handle description field
        if 'description' in data:
            description = str(data['description']).strip()
            if len(description) < 10:
                errors.append("TTP description must be at least 10 characters long")
            elif len(description) > 5000:
                errors.append("TTP description cannot exceed 5000 characters")
            else:
                update_data['description'] = description
        elif is_put:
            update_data['description'] = ttp.description  # Keep existing for PUT
        
        # Handle MITRE technique ID
        if 'mitre_technique_id' in data:
            mitre_technique_id = str(data['mitre_technique_id']).strip().upper()
            mitre_pattern = r'^T\d{4}(\.\d{3})?$'
            if not re.match(mitre_pattern, mitre_technique_id):
                errors.append("MITRE technique ID must follow format T1234 or T1234.001 (e.g., T1566.001)")
            else:
                # Check for duplicates (excluding current TTP)
                existing_ttp = TTPData.objects.filter(
                    mitre_technique_id=mitre_technique_id,
                    threat_feed=ttp.threat_feed
                ).exclude(id=ttp.id).first()
                
                if existing_ttp:
                    errors.append(f"TTP with MITRE technique ID '{mitre_technique_id}' already exists in this threat feed")
                else:
                    update_data['mitre_technique_id'] = mitre_technique_id
        elif is_put:
            update_data['mitre_technique_id'] = ttp.mitre_technique_id  # Keep existing for PUT
        
        # Handle MITRE tactic
        if 'mitre_tactic' in data:
            mitre_tactic = str(data['mitre_tactic']).strip().lower()
            valid_tactics = [choice[0] for choice in TTPData.MITRE_TACTIC_CHOICES]
            if mitre_tactic not in valid_tactics:
                errors.append(f"Invalid MITRE tactic. Must be one of: {', '.join(valid_tactics)}")
            else:
                update_data['mitre_tactic'] = mitre_tactic
        elif is_put:
            update_data['mitre_tactic'] = ttp.mitre_tactic  # Keep existing for PUT
        
        # Handle MITRE subtechnique (optional)
        if 'mitre_subtechnique' in data:
            mitre_subtechnique = str(data['mitre_subtechnique']).strip() if data['mitre_subtechnique'] else None
            if mitre_subtechnique and len(mitre_subtechnique) > 255:
                errors.append("MITRE subtechnique name cannot exceed 255 characters")
            else:
                update_data['mitre_subtechnique'] = mitre_subtechnique
        elif is_put:
            update_data['mitre_subtechnique'] = ttp.mitre_subtechnique  # Keep existing for PUT
        
        # Handle threat feed ID (optional)
        if 'threat_feed_id' in data:
            threat_feed_id = data['threat_feed_id']
            if threat_feed_id:
                try:
                    threat_feed_id = int(threat_feed_id)
                    threat_feed = ThreatFeed.objects.get(id=threat_feed_id)
                    update_data['threat_feed'] = threat_feed
                except (ValueError, ThreatFeed.DoesNotExist):
                    errors.append(f"Invalid threat feed ID: {threat_feed_id}")
            else:
                update_data['threat_feed'] = ttp.threat_feed  # Keep existing if null provided
        elif is_put:
            update_data['threat_feed'] = ttp.threat_feed  # Keep existing for PUT
        
        # Handle STIX ID (optional, but cannot be changed if already set)
        if 'stix_id' in data:
            stix_id = str(data['stix_id']).strip() if data['stix_id'] else None
            if stix_id:
                # Validate STIX ID format
                stix_pattern = r'^attack-pattern--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                if not re.match(stix_pattern, stix_id):
                    errors.append("STIX ID must follow format: attack-pattern--xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
                elif stix_id != ttp.stix_id:
                    # Check if the new STIX ID already exists
                    if TTPData.objects.filter(stix_id=stix_id).exclude(id=ttp.id).exists():
                        errors.append(f"TTP with STIX ID '{stix_id}' already exists")
                    else:
                        update_data['stix_id'] = stix_id
                # If stix_id matches existing, no change needed
            # If empty stix_id provided, keep existing
        elif is_put:
            update_data['stix_id'] = ttp.stix_id  # Keep existing for PUT
        
        if errors:
            return Response(
                {"error": "Validation failed", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if any changes were actually made
        changes_made = False
        for field, new_value in update_data.items():
            current_value = getattr(ttp, field)
            if current_value != new_value:
                changes_made = True
                break
        
        if not changes_made:
            return Response(
                {"message": "No changes detected", "data": _format_ttp_response(ttp)},
                status=status.HTTP_200_OK
            )
        
        # Store original values for logging
        original_values = {
            'name': ttp.name,
            'mitre_technique_id': ttp.mitre_technique_id,
            'mitre_tactic': ttp.mitre_tactic
        }
        
        # Update the TTP
        try:
            ttp_service = TTPService()
            updated_ttp = ttp_service.update_ttp(ttp.id, update_data)
        except:
            # Fallback to repository method
            updated_ttp = TTPRepository.update(ttp.id, update_data)
        
        if not updated_ttp:
            return Response(
                {"error": "Failed to update TTP", "ttp_id": ttp_id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Log the update activity
        try:
            changed_fields = [field for field, new_value in update_data.items() 
                            if getattr(ttp, field) != new_value]
            
            SystemActivity.objects.create(
                activity_type='ttp_updated',
                description=f'TTP updated: {updated_ttp.name} ({updated_ttp.mitre_technique_id})',
                details={
                    'ttp_id': updated_ttp.id,
                    'method': request.method,
                    'changed_fields': changed_fields,
                    'original_values': original_values,
                    'mitre_technique_id': updated_ttp.mitre_technique_id,
                    'mitre_tactic': updated_ttp.mitre_tactic,
                    'source': 'api_update'
                }
            )
        except Exception as e:
            logger.warning(f"Could not log TTP update activity: {str(e)}")
        
        # Format and return response
        response_data = {
            'success': True,
            'message': f'TTP updated successfully using {request.method} method',
            'data': _format_ttp_response(updated_ttp)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response(
            {"error": "Invalid TTP ID format", "ttp_id": ttp_id},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error updating TTP {ttp_id}: {str(e)}")
        return Response(
            {"error": "Failed to update TTP", "details": str(e), "ttp_id": ttp_id},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _format_ttp_response(ttp):
    """Helper function to format TTP data for API responses."""
    tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic)
    
    return {
        'id': ttp.id,
        'name': ttp.name,
        'description': ttp.description,
        'mitre_technique_id': ttp.mitre_technique_id,
        'mitre_tactic': ttp.mitre_tactic,
        'mitre_tactic_display': tactic_display,
        'mitre_subtechnique': ttp.mitre_subtechnique,
        'stix_id': ttp.stix_id,
        'threat_feed': {
            'id': ttp.threat_feed.id,
            'name': ttp.threat_feed.name,
            'is_external': ttp.threat_feed.is_external
        } if ttp.threat_feed else None,
        'is_anonymized': ttp.is_anonymized,
        'created_at': ttp.created_at.isoformat(),
        'updated_at': ttp.updated_at.isoformat(),
    }


def _delete_ttp(request, ttp_id):
    """
    Delete a TTP with safety checks and comprehensive logging.

    Performs the following operations:
    1. Validates TTP exists
    2. Checks for related data and dependencies
    3. Creates backup of TTP data for audit trail
    4. Performs deletion
    5. Logs deletion activity
    """
    try:
        from core.repositories.ttp_repository import TTPRepository
        from core.services.ttp_service import TTPService
        from django.db.models import Q

        # Check permissions - only publishers and BlueVision admins can delete TTPs
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Authentication required to delete TTPs"
            }, status=status.HTTP_401_UNAUTHORIZED)

        user_role = getattr(request.user, 'role', 'viewer')
        user_org = getattr(request.user, 'organization', None)

        if user_role not in ['publisher', 'BlueVisionAdmin'] and not request.user.is_superuser:
            org_name = user_org.name if user_org else "your organization"
            return Response({
                "success": False,
                "message": f"Access denied. Only publishers can delete TTPs. Please contact the administrator of {org_name} to request publisher access.",
                "user_role": user_role,
                "required_roles": ["publisher", "BlueVisionAdmin"]
            }, status=status.HTTP_403_FORBIDDEN)

        # Get the existing TTP
        ttp = TTPRepository.get_by_id(ttp_id)
        if not ttp:
            return Response(
                {"error": "TTP not found", "ttp_id": ttp_id},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store TTP data for logging before deletion
        ttp_backup = {
            'id': ttp.id,
            'name': ttp.name,
            'description': ttp.description,
            'mitre_technique_id': ttp.mitre_technique_id,
            'mitre_tactic': ttp.mitre_tactic,
            'mitre_subtechnique': ttp.mitre_subtechnique,
            'stix_id': ttp.stix_id,
            'threat_feed_id': ttp.threat_feed.id if ttp.threat_feed else None,
            'threat_feed_name': ttp.threat_feed.name if ttp.threat_feed else None,
            'is_anonymized': ttp.is_anonymized,
            'created_at': ttp.created_at.isoformat(),
            'updated_at': ttp.updated_at.isoformat()
        }
        
        # Safety checks - look for related data
        warnings = []
        related_data = {}
        
        # Check for related indicators that might reference this TTP
        try:
            related_indicators_count = Indicator.objects.filter(
                Q(description__icontains=ttp.mitre_technique_id) |
                Q(value__icontains=ttp.mitre_technique_id) |
                Q(threat_feed=ttp.threat_feed)
            ).count()
            
            if related_indicators_count > 0:
                warnings.append(f"Found {related_indicators_count} indicators that may reference this TTP")
                related_data['related_indicators_count'] = related_indicators_count
        except Exception as e:
            logger.warning(f"Could not check related indicators for TTP {ttp_id}: {str(e)}")
        
        # Check if this is the only TTP in the threat feed
        try:
            if ttp.threat_feed:
                feed_ttp_count = TTPData.objects.filter(threat_feed=ttp.threat_feed).count()
                if feed_ttp_count == 1:
                    warnings.append(f"This is the only TTP in threat feed '{ttp.threat_feed.name}'")
                    related_data['is_last_ttp_in_feed'] = True
                else:
                    related_data['remaining_ttps_in_feed'] = feed_ttp_count - 1
        except Exception as e:
            logger.warning(f"Could not check feed TTP count for TTP {ttp_id}: {str(e)}")
        
        # Check if this TTP is referenced in system activities
        try:
            activity_references = SystemActivity.objects.filter(
                Q(description__icontains=ttp.mitre_technique_id) |
                Q(details__contains=str(ttp.id))
            ).count()
            
            if activity_references > 0:
                related_data['activity_references'] = activity_references
        except Exception as e:
            logger.warning(f"Could not check activity references for TTP {ttp_id}: {str(e)}")
        
        # Perform the deletion
        try:
            # Use TTPService for deletion if available, otherwise use repository
            try:
                ttp_service = TTPService()
                ttp_service.delete_ttp(ttp.id)
                deletion_success = True  # Service doesn't return value, assume success if no exception
            except:
                # Fallback to repository method
                deletion_success = TTPRepository.delete(ttp.id)
            
            if not deletion_success:
                return Response(
                    {"error": "Failed to delete TTP", "ttp_id": ttp_id},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error during TTP deletion for ID {ttp_id}: {str(e)}")
            return Response(
                {"error": "Failed to delete TTP", "details": str(e), "ttp_id": ttp_id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Log the deletion activity with comprehensive details
        try:
            SystemActivity.objects.create(
                activity_type='ttp_deleted',
                description=f'TTP deleted: {ttp_backup["name"]} ({ttp_backup["mitre_technique_id"]})',
                details={
                    'deleted_ttp': ttp_backup,
                    'warnings': warnings,
                    'related_data': related_data,
                    'deletion_timestamp': timezone.now().isoformat(),
                    'source': 'api_delete'
                }
            )
        except Exception as e:
            logger.warning(f"Could not log TTP deletion activity: {str(e)}")
        
        # Build success response
        response_data = {
            'success': True,
            'message': f'TTP "{ttp_backup["name"]}" ({ttp_backup["mitre_technique_id"]}) deleted successfully',
            'deleted_ttp': {
                'id': ttp_backup['id'],
                'name': ttp_backup['name'],
                'mitre_technique_id': ttp_backup['mitre_technique_id'],
                'mitre_tactic': ttp_backup['mitre_tactic'],
                'threat_feed_name': ttp_backup['threat_feed_name']
            },
            'deletion_timestamp': timezone.now().isoformat()
        }
        
        # Include warnings if any
        if warnings:
            response_data['warnings'] = warnings
            response_data['notice'] = 'TTP deleted successfully, but please review the warnings for potential impacts'
        
        # Include related data summary if any
        if related_data:
            response_data['impact_summary'] = related_data
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response(
            {"error": "Invalid TTP ID format", "ttp_id": ttp_id},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error deleting TTP {ttp_id}: {str(e)}")
        return Response(
            {"error": "Failed to delete TTP", "details": str(e), "ttp_id": ttp_id},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])  # Keep AllowAny for GET, but add role checks in _update_ttp
def ttp_detail(request, ttp_id):
    """
    GET: Get detailed information about a specific TTP.
    PUT: Completely update a TTP (all fields required).
    PATCH: Partially update a TTP (only provided fields updated).
    DELETE: Remove a TTP from the system.
    
    Path Parameters:
    - ttp_id: The ID of the TTP to retrieve/update/delete
    
    GET Returns detailed TTP information including:
    - All TTP fields and metadata
    - Related threat feed information
    - STIX mapping details
    - Creation and modification history
    - Related indicators (if any)
    
    PUT/PATCH Body Parameters:
    - name: TTP name (PUT: required, PATCH: optional)
    - description: TTP description (PUT: required, PATCH: optional)
    - mitre_technique_id: MITRE ATT&CK technique ID (PUT: required, PATCH: optional)
    - mitre_tactic: MITRE tactic (PUT: required, PATCH: optional)
    - mitre_subtechnique: MITRE subtechnique name (optional)
    - threat_feed_id: ID of associated threat feed (optional)
    - stix_id: STIX ID (optional, cannot be changed if already set)
    
    DELETE removes the TTP with:
    - Safety checks for related data
    - Activity logging for audit trail
    - Confirmation of successful deletion
    """
    
    if request.method in ['PUT', 'PATCH']:
        return _update_ttp(request, ttp_id)
    elif request.method == 'DELETE':
        return _delete_ttp(request, ttp_id)
    
    # Handle GET request (existing detail functionality)
    try:
        from core.repositories.ttp_repository import TTPRepository
        
        # Get the TTP by ID
        ttp = TTPRepository.get_by_id(ttp_id)
        if not ttp:
            return Response(
                {"error": "TTP not found", "ttp_id": ttp_id},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get tactic display name
        tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic)
        
        # Get related indicators that reference this TTP (if any)
        related_indicators = []
        try:
            # Look for indicators that might reference this TTP in their descriptions or metadata
            from django.db.models import Q
            indicators = Indicator.objects.filter(
                Q(description__icontains=ttp.mitre_technique_id) |
                Q(value__icontains=ttp.mitre_technique_id) |
                Q(threat_feed=ttp.threat_feed)
            ).select_related('threat_feed')[:5]  # Limit to 5 related indicators
            
            for indicator in indicators:
                related_indicators.append({
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value[:100] + '...' if len(indicator.value) > 100 else indicator.value,
                    'confidence': getattr(indicator, 'confidence', None),
                    'created_at': indicator.created_at.isoformat(),
                    'threat_feed': {
                        'id': indicator.threat_feed.id,
                        'name': indicator.threat_feed.name
                    } if indicator.threat_feed else None
                })
        except Exception as e:
            logger.warning(f"Could not fetch related indicators for TTP {ttp_id}: {str(e)}")
        
        # Get MITRE ATT&CK framework context
        mitre_context = {
            'tactic': ttp.mitre_tactic,
            'tactic_display': tactic_display,
            'technique_id': ttp.mitre_technique_id,
            'subtechnique': ttp.mitre_subtechnique,
            'framework_url': f"https://attack.mitre.org/techniques/{ttp.mitre_technique_id.replace('.', '/')}/" if ttp.mitre_technique_id else None
        }
        
        # Build detailed response
        ttp_detail_data = {
            'id': ttp.id,
            'name': ttp.name,
            'description': ttp.description,
            'stix_id': ttp.stix_id,
            
            # MITRE ATT&CK Information
            'mitre': mitre_context,
            
            # Threat Feed Information
            'threat_feed': {
                'id': ttp.threat_feed.id,
                'name': ttp.threat_feed.name,
                'description': ttp.threat_feed.description,
                'is_external': ttp.threat_feed.is_external,
                'is_active': ttp.threat_feed.is_active,
                'source_type': getattr(ttp.threat_feed, 'source_type', 'unknown'),
                'created_at': ttp.threat_feed.created_at.isoformat(),
            } if ttp.threat_feed else None,
            
            # Anonymization Information
            'anonymization': {
                'is_anonymized': ttp.is_anonymized,
                'has_original_data': bool(ttp.original_data),
                'original_data_keys': list(ttp.original_data.keys()) if ttp.original_data else []
            },
            
            # Timestamps
            'created_at': ttp.created_at.isoformat(),
            'updated_at': ttp.updated_at.isoformat(),
            
            # Related Data
            'related_indicators': related_indicators,
            'related_indicators_count': len(related_indicators),
            
            # Metadata
            'metadata': {
                'has_subtechnique': bool(ttp.mitre_subtechnique),
                'tactic_category': ttp.mitre_tactic,
                'data_source': 'threat_feed',
                'stix_version': '2.1' if ttp.stix_id and 'attack-pattern' in ttp.stix_id else 'unknown'
            }
        }
        
        return Response({
            'success': True,
            'data': ttp_detail_data
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response(
            {"error": "Invalid TTP ID format", "ttp_id": ttp_id},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting TTP detail for ID {ttp_id}: {str(e)}")
        return Response(
            {"error": "Failed to get TTP details", "details": str(e), "ttp_id": ttp_id},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def mitre_matrix(request):
    """
    GET: Get MITRE ATT&CK Matrix data with technique counts organized by tactic.
    
    Query Parameters:
    - feed_id: Filter by specific threat feed ID (optional)
    - include_zero: Include tactics with zero techniques (default: false)
    - format: Response format - 'matrix' or 'list' (default: 'matrix')
    
    Returns MITRE ATT&CK matrix data structured by tactics with technique counts,
    technique details, and overall statistics.
    """
    try:
        logger.info(f"MITRE Matrix called with parameters: {request.GET}")
        # Get query parameters
        feed_id = request.GET.get('feed_id', '').strip()
        include_zero = request.GET.get('include_zero', 'false').lower() == 'true'
        response_format = request.GET.get('response_format', request.GET.get('format', 'matrix')).lower()
        
        # Start with all TTPs
        queryset = TTPData.objects.select_related('threat_feed').all()
        
        # Apply feed filter if provided
        if feed_id:
            try:
                feed_id_int = int(feed_id)
                queryset = queryset.filter(threat_feed_id=feed_id_int)
            except ValueError:
                return Response(
                    {"error": "Invalid feed_id parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get technique counts by tactic
        tactic_counts = queryset.values('mitre_tactic').annotate(
            count=Count('id')
        ).order_by('mitre_tactic')
        
        # Create a mapping of tactic codes to counts
        tactic_count_map = {item['mitre_tactic']: item['count'] for item in tactic_counts if item['mitre_tactic']}
        
        # Get detailed technique data grouped by tactic
        tactic_techniques = defaultdict(list)
        all_techniques = queryset.order_by('mitre_tactic', 'mitre_technique_id')
        
        for ttp in all_techniques:
            if ttp.mitre_tactic:  # Only include TTPs with valid tactics
                technique_data = {
                    'id': ttp.id,
                    'name': ttp.name,
                    'technique_id': ttp.mitre_technique_id,
                    'subtechnique': ttp.mitre_subtechnique,
                    'description': ttp.description[:200] + '...' if len(ttp.description) > 200 else ttp.description,
                    'threat_feed': {
                        'id': ttp.threat_feed.id,
                        'name': ttp.threat_feed.name,
                        'is_external': ttp.threat_feed.is_external
                    } if ttp.threat_feed else None,
                    'is_anonymized': ttp.is_anonymized,
                    'created_at': ttp.created_at.isoformat(),
                    'stix_id': ttp.stix_id
                }
                tactic_techniques[ttp.mitre_tactic].append(technique_data)
        
        # Build the complete matrix structure
        matrix_data = OrderedDict()
        total_techniques = 0
        
        # Process all MITRE tactics from the model choices
        for tactic_code, tactic_display in TTPData.MITRE_TACTIC_CHOICES:
            technique_count = tactic_count_map.get(tactic_code, 0)
            techniques = tactic_techniques.get(tactic_code, [])
            
            # Skip tactics with zero techniques if include_zero is False
            if not include_zero and technique_count == 0:
                continue
            
            matrix_data[tactic_code] = {
                'tactic_code': tactic_code,
                'tactic_name': tactic_display,
                'technique_count': technique_count,
                'techniques': techniques,
                'has_techniques': technique_count > 0,
                'percentage': 0  # Will be calculated after we have the total
            }
            
            total_techniques += technique_count
        
        # Calculate percentages
        for tactic_data in matrix_data.values():
            if total_techniques > 0:
                tactic_data['percentage'] = round((tactic_data['technique_count'] / total_techniques) * 100, 2)
        
        # Get feed information if filtering by specific feed
        feed_info = None
        if feed_id:
            try:
                from core.models.models import ThreatFeed
                feed = ThreatFeed.objects.get(id=feed_id_int)
                feed_info = {
                    'id': feed.id,
                    'name': feed.name,
                    'description': feed.description,
                    'is_external': feed.is_external,
                    'is_active': feed.is_active
                }
            except ThreatFeed.DoesNotExist:
                feed_info = {'error': 'Feed not found'}
        
        # Build response based on format
        if response_format == 'list':
            # Simple list format
            tactics_list = []
            for tactic_data in matrix_data.values():
                tactics_list.append({
                    'tactic': tactic_data['tactic_code'],
                    'name': tactic_data['tactic_name'],
                    'count': tactic_data['technique_count'],
                    'percentage': tactic_data['percentage']
                })
            
            response_data = {
                'success': True,
                'format': 'list',
                'total_techniques': total_techniques,
                'total_tactics': len(matrix_data),
                'tactics': tactics_list,
                'feed_filter': feed_info,
                'generated_at': timezone.now().isoformat()
            }
        else:
            # Full matrix format (default)
            response_data = {
                'success': True,
                'format': 'matrix',
                'total_techniques': total_techniques,
                'total_tactics': len(matrix_data),
                'matrix': dict(matrix_data),
                'feed_filter': feed_info,
                'statistics': {
                    'most_common_tactic': max(matrix_data.items(), key=lambda x: x[1]['technique_count'])[0] if matrix_data else None,
                    'least_common_tactic': min(matrix_data.items(), key=lambda x: x[1]['technique_count'])[0] if matrix_data else None,
                    'tactics_with_techniques': sum(1 for tactic_data in matrix_data.values() if tactic_data['technique_count'] > 0),
                    'tactics_without_techniques': sum(1 for tactic_data in matrix_data.values() if tactic_data['technique_count'] == 0),
                    'average_techniques_per_tactic': round(total_techniques / len(matrix_data), 2) if matrix_data else 0
                },
                'filters': {
                    'feed_id': feed_id,
                    'include_zero': include_zero,
                    'format': response_format
                },
                'generated_at': timezone.now().isoformat()
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting MITRE matrix data: {str(e)}")
        return Response(
            {"error": "Failed to get MITRE matrix data", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_trends(request):
    """
    GET: Get TTP trends data for time-series analysis and visualization.
    
    Query Parameters:
    - days: Number of days to look back (default: 30, max: 365)
    - tactic: Filter by specific MITRE tactic (optional)
    - technique_id: Filter by specific MITRE technique ID (optional)
    - feed_id: Filter by specific threat feed ID (optional)
    - granularity: Time granularity - 'day', 'week', 'month' (default: 'day')
    - group_by: Group data by - 'tactic', 'technique', 'feed' (default: 'tactic')
    - include_zero: Include dates with zero observations (default: true)
    
    Returns time-series data showing TTP observation trends over time,
    organized by the specified grouping with comprehensive statistics.
    """
    try:
        from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
        
        # Get and validate query parameters
        days = int(request.GET.get('days', 30))
        if days < 1 or days > 365:
            days = 30
            
        tactic = request.GET.get('tactic', '').strip()
        technique_id = request.GET.get('technique_id', '').strip()
        feed_id = request.GET.get('feed_id', '').strip()
        granularity = request.GET.get('granularity', 'day').lower()
        group_by = request.GET.get('group_by', 'tactic').lower()
        include_zero = request.GET.get('include_zero', 'true').lower() == 'true'
        
        # Validate parameters
        valid_granularities = ['day', 'week', 'month']
        if granularity not in valid_granularities:
            return Response(
                {"error": f"Invalid granularity. Must be one of: {', '.join(valid_granularities)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_group_by = ['tactic', 'technique', 'feed']
        if group_by not in valid_group_by:
            return Response(
                {"error": f"Invalid group_by. Must be one of: {', '.join(valid_group_by)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Start with all TTPs in the date range
        queryset = TTPData.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).select_related('threat_feed')
        
        # Apply filters
        if tactic:
            queryset = queryset.filter(mitre_tactic=tactic)
        
        if technique_id:
            queryset = queryset.filter(mitre_technique_id__icontains=technique_id)
        
        if feed_id:
            try:
                feed_id_int = int(feed_id)
                queryset = queryset.filter(threat_feed_id=feed_id_int)
            except ValueError:
                return Response(
                    {"error": "Invalid feed_id parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Choose truncation function based on granularity
        truncate_func = {
            'day': TruncDate,
            'week': TruncWeek,
            'month': TruncMonth
        }[granularity]
        
        # Group data by date and specified grouping
        if group_by == 'tactic':
            # Group by tactic
            trends_data = queryset.annotate(
                date_group=truncate_func('created_at')
            ).values('date_group', 'mitre_tactic').annotate(
                count=Count('id')
            ).order_by('date_group', 'mitre_tactic')
            
            group_field = 'mitre_tactic'
            group_display_map = dict(TTPData.MITRE_TACTIC_CHOICES)
            
        elif group_by == 'technique':
            # Group by technique
            trends_data = queryset.annotate(
                date_group=truncate_func('created_at')
            ).values('date_group', 'mitre_technique_id', 'name').annotate(
                count=Count('id')
            ).order_by('date_group', 'mitre_technique_id')
            
            group_field = 'mitre_technique_id'
            group_display_map = {}
            
        else:  # group_by == 'feed'
            # Group by threat feed
            trends_data = queryset.annotate(
                date_group=truncate_func('created_at')
            ).values('date_group', 'threat_feed__id', 'threat_feed__name').annotate(
                count=Count('id')
            ).order_by('date_group', 'threat_feed__id')
            
            group_field = 'threat_feed__id'
            group_display_map = {}
        
        # Organize data for time series
        time_series = defaultdict(lambda: defaultdict(int))
        groups_found = set()
        dates_found = set()
        
        for item in trends_data:
            date_key = item['date_group'].strftime('%Y-%m-%d')
            
            if group_by == 'tactic':
                group_key = item[group_field] or 'unknown'
                group_display = group_display_map.get(group_key, group_key.replace('_', ' ').title())
            elif group_by == 'technique':
                group_key = item[group_field]
                group_display = f"{group_key}: {item['name'][:50]}{'...' if len(item['name']) > 50 else ''}"
            else:  # feed
                group_key = item[group_field]
                group_display = item['threat_feed__name']
            
            time_series[group_key][date_key] = item['count']
            groups_found.add((group_key, group_display))
            dates_found.add(date_key)
        
        # Generate complete date range if include_zero is True
        if include_zero:
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                date_key = current_date.strftime('%Y-%m-%d')
                dates_found.add(date_key)
                
                # Move to next period
                if granularity == 'day':
                    current_date += timedelta(days=1)
                elif granularity == 'week':
                    current_date += timedelta(weeks=1)
                else:  # month
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
        
        # Build the response data structure
        sorted_dates = sorted(dates_found)
        series_data = []
        
        for group_key, group_display in sorted(groups_found, key=lambda x: x[1]):
            data_points = []
            total_count = 0
            max_count = 0
            
            for date_key in sorted_dates:
                count = time_series[group_key].get(date_key, 0)
                data_points.append({
                    'date': date_key,
                    'count': count
                })
                total_count += count
                max_count = max(max_count, count)
            
            series_data.append({
                'group_key': group_key,
                'group_name': group_display,
                'group_type': group_by,
                'data_points': data_points,
                'total_count': total_count,
                'max_count': max_count,
                'average_count': round(total_count / len(sorted_dates), 2) if sorted_dates else 0
            })
        
        # Calculate overall statistics
        total_observations = sum(series['total_count'] for series in series_data)
        
        # Get top performers
        top_groups = sorted(series_data, key=lambda x: x['total_count'], reverse=True)[:5]
        
        # Calculate trend direction for each series (simple linear trend)
        for series in series_data:
            if len(series['data_points']) >= 2:
                # Simple trend calculation: compare first half to second half
                mid_point = len(series['data_points']) // 2
                first_half_avg = sum(p['count'] for p in series['data_points'][:mid_point]) / mid_point if mid_point > 0 else 0
                second_half_avg = sum(p['count'] for p in series['data_points'][mid_point:]) / (len(series['data_points']) - mid_point)
                
                if second_half_avg > first_half_avg * 1.1:
                    series['trend'] = 'increasing'
                elif second_half_avg < first_half_avg * 0.9:
                    series['trend'] = 'decreasing'
                else:
                    series['trend'] = 'stable'
                
                series['trend_percentage'] = round(((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0, 2)
            else:
                series['trend'] = 'insufficient_data'
                series['trend_percentage'] = 0
        
        # Get feed information if filtering by specific feed
        feed_info = None
        if feed_id:
            try:
                from core.models.models import ThreatFeed
                feed = ThreatFeed.objects.get(id=feed_id_int)
                feed_info = {
                    'id': feed.id,
                    'name': feed.name,
                    'description': feed.description,
                    'is_external': feed.is_external,
                    'is_active': feed.is_active
                }
            except ThreatFeed.DoesNotExist:
                feed_info = {'error': 'Feed not found'}
        
        # Build final response
        response_data = {
            'success': True,
            'total_observations': total_observations,
            'total_groups': len(series_data),
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': days,
                'granularity': granularity
            },
            'series': series_data,
            'top_performers': [
                {
                    'group_key': series['group_key'],
                    'group_name': series['group_name'],
                    'total_count': series['total_count'],
                    'trend': series['trend']
                }
                for series in top_groups
            ],
            'statistics': {
                'peak_observation_date': None,  # Will be calculated
                'average_daily_observations': round(total_observations / len(sorted_dates), 2) if sorted_dates else 0,
                'most_active_period': granularity,
                'groups_with_increasing_trend': sum(1 for s in series_data if s['trend'] == 'increasing'),
                'groups_with_decreasing_trend': sum(1 for s in series_data if s['trend'] == 'decreasing'),
                'groups_with_stable_trend': sum(1 for s in series_data if s['trend'] == 'stable')
            },
            'filters': {
                'days': days,
                'tactic': tactic,
                'technique_id': technique_id,
                'feed_id': feed_id,
                'granularity': granularity,
                'group_by': group_by,
                'include_zero': include_zero
            },
            'feed_filter': feed_info,
            'generated_at': timezone.now().isoformat()
        }
        
        # Find peak observation date
        daily_totals = defaultdict(int)
        for series in series_data:
            for point in series['data_points']:
                daily_totals[point['date']] += point['count']
        
        if daily_totals:
            peak_date = max(daily_totals.items(), key=lambda x: x[1])
            response_data['statistics']['peak_observation_date'] = {
                'date': peak_date[0],
                'count': peak_date[1]
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting TTP trends data: {str(e)}")
        return Response(
            {"error": "Failed to get TTP trends data", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_export(request):
    """
    GET: Export TTP data in multiple formats (CSV, JSON, STIX).

    Query Parameters:
    - format: Export format - 'csv', 'json', 'stix' (default: 'json')
    - tactic: Filter by specific MITRE tactic (optional)
    - technique_id: Filter by specific MITRE technique ID (optional)
    - feed_id: Filter by specific threat feed ID (optional)
    - include_anonymized: Include anonymized TTPs (default: true)
    - include_original: Include original data for anonymized TTPs (default: false)
    - fields: Comma-separated list of fields to include (optional)
    - limit: Maximum number of records to export (default: 1000, max: 10000)
    - created_after: Filter TTPs created after this date (YYYY-MM-DD format)
    - created_before: Filter TTPs created before this date (YYYY-MM-DD format)

    Returns TTP data in the specified format with proper content headers for download.
    """
    try:
        logger.info(f"TTP Export request: format={request.GET.get('format', 'json')}, method={request.method}, path={request.path}")
        # Get and validate query parameters
        export_format = request.GET.get('export_format', request.GET.get('format', 'json')).lower()
        tactic = request.GET.get('tactic', '').strip()
        technique_id = request.GET.get('technique_id', '').strip()
        feed_id = request.GET.get('feed_id', '').strip()
        include_anonymized = request.GET.get('include_anonymized', 'true').lower() == 'true'
        include_original = request.GET.get('include_original', 'false').lower() == 'true'
        fields_param = request.GET.get('fields', '').strip()
        limit = int(request.GET.get('limit', 1000))
        created_after = request.GET.get('created_after', '').strip()
        created_before = request.GET.get('created_before', '').strip()
        
        # Validate format
        valid_formats = ['csv', 'json', 'stix']
        if export_format not in valid_formats:
            return Response(
                {"error": f"Invalid format. Must be one of: {', '.join(valid_formats)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate limit
        if limit < 1 or limit > 10000:
            limit = 1000
        
        # Start with all TTPs
        queryset = TTPData.objects.select_related('threat_feed').all()
        
        # Apply filters
        if not include_anonymized:
            queryset = queryset.filter(is_anonymized=False)
        
        if tactic:
            queryset = queryset.filter(mitre_tactic=tactic)
        
        if technique_id:
            queryset = queryset.filter(mitre_technique_id__icontains=technique_id)
        
        if feed_id:
            try:
                feed_id_int = int(feed_id)
                queryset = queryset.filter(threat_feed_id=feed_id_int)
            except ValueError:
                return Response(
                    {"error": "Invalid feed_id parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Apply date filters
        if created_after:
            try:
                after_date = datetime.strptime(created_after, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=after_date)
            except ValueError:
                return Response(
                    {"error": "Invalid created_after date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if created_before:
            try:
                before_date = datetime.strptime(created_before, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=before_date)
            except ValueError:
                return Response(
                    {"error": "Invalid created_before date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Apply limit and order
        queryset = queryset.order_by('-created_at')[:limit]
        ttps = list(queryset)
        
        # Define available fields
        all_fields = [
            'id', 'name', 'description', 'mitre_technique_id', 'mitre_tactic', 
            'mitre_tactic_display', 'mitre_subtechnique', 'stix_id', 
            'threat_feed_id', 'threat_feed_name', 'threat_feed_is_external',
            'is_anonymized', 'created_at', 'updated_at'
        ]
        
        # Parse fields parameter
        if fields_param:
            requested_fields = [f.strip() for f in fields_param.split(',')]
            selected_fields = [f for f in requested_fields if f in all_fields]
            if not selected_fields:
                selected_fields = all_fields
        else:
            selected_fields = all_fields
        
        # Helper function to extract TTP data
        def extract_ttp_data(ttp):
            # Get tactic display name
            tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic) if ttp.mitre_tactic else ''
            
            data = {
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': ttp.mitre_tactic or '',
                'mitre_tactic_display': tactic_display,
                'mitre_subtechnique': ttp.mitre_subtechnique or '',
                'stix_id': ttp.stix_id,
                'threat_feed_id': ttp.threat_feed.id if ttp.threat_feed else None,
                'threat_feed_name': ttp.threat_feed.name if ttp.threat_feed else '',
                'threat_feed_is_external': ttp.threat_feed.is_external if ttp.threat_feed else False,
                'is_anonymized': ttp.is_anonymized,
                'created_at': ttp.created_at.isoformat(),
                'updated_at': ttp.updated_at.isoformat()
            }
            
            # Add original data if requested and available
            if include_original and ttp.is_anonymized and ttp.original_data:
                data['original_data'] = ttp.original_data
            
            # Filter to selected fields
            return {field: data[field] for field in selected_fields if field in data}
        
        # Generate timestamp for filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        # CSV Export
        if export_format == 'csv':
            try:
                logger.info(f"Processing CSV export with {len(ttps)} TTPs and {len(selected_fields)} fields")
                output = StringIO()
                writer = csv.DictWriter(output, fieldnames=selected_fields, extrasaction='ignore')
                writer.writeheader()

                for ttp in ttps:
                    row_data = extract_ttp_data(ttp)
                    # Convert complex data to strings for CSV
                    for key, value in row_data.items():
                        if isinstance(value, (dict, list)):
                            row_data[key] = json.dumps(value)
                        elif value is None:
                            row_data[key] = ''
                    writer.writerow(row_data)

                response = HttpResponse(output.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="ttps_export_{timestamp}.csv"'
                logger.info("CSV export completed successfully")
                return response
            except Exception as csv_error:
                logger.error(f"CSV export error: {str(csv_error)}")
                return Response(
                    {"error": f"CSV export failed: {str(csv_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # JSON Export
        elif export_format == 'json':
            export_data = {
                'export_info': {
                    'format': 'json',
                    'generated_at': timezone.now().isoformat(),
                    'total_records': len(ttps),
                    'filters_applied': {
                        'tactic': tactic,
                        'technique_id': technique_id,
                        'feed_id': feed_id,
                        'include_anonymized': include_anonymized,
                        'include_original': include_original,
                        'created_after': created_after,
                        'created_before': created_before,
                        'limit': limit
                    },
                    'selected_fields': selected_fields
                },
                'ttps': [extract_ttp_data(ttp) for ttp in ttps]
            }
            
            response = HttpResponse(
                json.dumps(export_data, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="ttps_export_{timestamp}.json"'
            return response
        
        # STIX Export
        elif export_format == 'stix':
            # Create STIX bundle
            stix_objects = []
            bundle_id = f"bundle--{str(uuid.uuid4())}"
            
            # Add identity object for the organization
            identity_obj = {
                "type": "identity",
                "spec_version": "2.1",
                "id": f"identity--{str(uuid.uuid4())}",
                "created": timezone.now().isoformat(),
                "modified": timezone.now().isoformat(),
                "name": "CRISP Threat Intelligence Platform",
                "identity_class": "system",
                "description": "Collaborative Research Infrastructure for Sharing Practices"
            }
            stix_objects.append(identity_obj)
            
            # Convert TTPs to STIX Attack Pattern objects
            for ttp in ttps:
                # Create basic STIX attack pattern
                attack_pattern = {
                    "type": "attack-pattern",
                    "spec_version": "2.1",
                    "id": ttp.stix_id,
                    "created": ttp.created_at.isoformat(),
                    "modified": ttp.updated_at.isoformat(),
                    "name": ttp.name,
                    "description": ttp.description,
                    "created_by_ref": identity_obj["id"]
                }
                
                # Add MITRE ATT&CK external references
                external_refs = []
                if ttp.mitre_technique_id:
                    mitre_url = f"https://attack.mitre.org/techniques/{ttp.mitre_technique_id.replace('.', '/')}/"
                    external_refs.append({
                        "source_name": "mitre-attack",
                        "external_id": ttp.mitre_technique_id,
                        "url": mitre_url
                    })
                
                if external_refs:
                    attack_pattern["external_references"] = external_refs
                
                # Add kill chain phases
                if ttp.mitre_tactic:
                    tactic_mapping = {
                        'reconnaissance': 'reconnaissance',
                        'resource_development': 'resource-development',
                        'initial_access': 'initial-access',
                        'execution': 'execution',
                        'persistence': 'persistence',
                        'privilege_escalation': 'privilege-escalation',
                        'defense_evasion': 'defense-evasion',
                        'credential_access': 'credential-access',
                        'discovery': 'discovery',
                        'lateral_movement': 'lateral-movement',
                        'collection': 'collection',
                        'command_and_control': 'command-and-control',
                        'exfiltration': 'exfiltration',
                        'impact': 'impact'
                    }
                    
                    kill_chain_phase = tactic_mapping.get(ttp.mitre_tactic, ttp.mitre_tactic)
                    attack_pattern["kill_chain_phases"] = [{
                        "kill_chain_name": "mitre-attack",
                        "phase_name": kill_chain_phase
                    }]
                
                # Add custom properties
                if ttp.threat_feed:
                    attack_pattern["x_crisp_threat_feed"] = ttp.threat_feed.name
                    attack_pattern["x_crisp_threat_feed_external"] = ttp.threat_feed.is_external
                
                if ttp.mitre_subtechnique:
                    attack_pattern["x_crisp_subtechnique"] = ttp.mitre_subtechnique
                
                if ttp.is_anonymized:
                    attack_pattern["x_crisp_anonymized"] = True
                    if include_original and ttp.original_data:
                        attack_pattern["x_crisp_original_data"] = ttp.original_data
                
                stix_objects.append(attack_pattern)
            
            # Create STIX bundle
            bundle = {
                "type": "bundle",
                "id": bundle_id,
                "spec_version": "2.1",
                "objects": stix_objects
            }
            
            response = HttpResponse(
                json.dumps(bundle, indent=2, ensure_ascii=False),
                content_type='application/stix+json'
            )
            response['Content-Disposition'] = f'attachment; filename="ttps_stix_export_{timestamp}.json"'
            return response
        
    except Exception as e:
        logger.error(f"Error exporting TTP data: {str(e)}")
        return Response(
            {"error": "Failed to export TTP data", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def ttp_mitre_mapping(request):
    """
    POST: Map a TTP to MITRE ATT&CK framework
    
    Request Body:
    {
        "name": "TTP name",
        "description": "TTP description"
    }
    
    Returns mapping suggestions with confidence scores.
    """
    try:
        from core.services.mitre_mapping_service import TTPMappingService
        
        # Validate request data
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        
        if not name:
            return Response(
                {"error": "TTP name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize mapping service and perform mapping
        mapping_service = TTPMappingService()
        mapping_result = mapping_service.map_ttp_to_mitre(name, description)
        
        return Response(mapping_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error mapping TTP to MITRE: {str(e)}")
        return Response(
            {"error": "Failed to map TTP to MITRE", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def ttp_bulk_mapping(request):
    """
    POST: Map multiple TTPs to MITRE ATT&CK framework in bulk
    
    Request Body:
    {
        "ttps": [
            {
                "id": "optional_id",
                "name": "TTP name",
                "description": "TTP description"
            }
        ]
    }
    
    Returns bulk mapping results.
    """
    try:
        from core.services.mitre_mapping_service import TTPMappingService
        
        # Validate request data
        ttps = request.data.get('ttps', [])
        
        if not ttps or not isinstance(ttps, list):
            return Response(
                {"error": "TTPs array is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(ttps) > 100:  # Limit bulk operations
            return Response(
                {"error": "Maximum 100 TTPs allowed per bulk request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate each TTP
        for i, ttp in enumerate(ttps):
            if not isinstance(ttp, dict) or not ttp.get('name'):
                return Response(
                    {"error": f"TTP at index {i} must have a 'name' field"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Initialize mapping service and perform bulk mapping
        mapping_service = TTPMappingService()
        bulk_result = mapping_service.bulk_map_ttps(ttps)
        
        return Response(bulk_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in bulk TTP mapping: {str(e)}")
        return Response(
            {"error": "Failed to perform bulk TTP mapping", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def ttp_mapping_validation(request):
    """
    POST: Validate a MITRE technique-tactic mapping
    
    Request Body:
    {
        "technique_id": "T1566",
        "tactic_id": "initial-access"
    }
    
    Returns validation result.
    """
    try:
        from core.services.mitre_mapping_service import TTPMappingService
        
        # Validate request data
        technique_id = request.data.get('technique_id', '').strip()
        tactic_id = request.data.get('tactic_id', '').strip()
        
        if not technique_id:
            return Response(
                {"error": "technique_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not tactic_id:
            return Response(
                {"error": "tactic_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize mapping service and validate mapping
        mapping_service = TTPMappingService()
        validation_result = mapping_service.validate_mapping(technique_id, tactic_id)
        
        return Response(validation_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error validating TTP mapping: {str(e)}")
        return Response(
            {"error": "Failed to validate TTP mapping", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def ttp_auto_map_existing(request):
    """
    POST: Automatically map existing TTPs that don't have MITRE mappings
    
    Query Parameters:
    - limit: Maximum number of TTPs to process (default: 50, max: 200)
    - force: Whether to re-map TTPs that already have mappings (default: false)
    - confidence_threshold: Minimum confidence score to apply mappings (default: 80)
    
    Returns auto-mapping results and statistics.
    """
    try:
        from core.services.mitre_mapping_service import TTPMappingService
        from core.models.models import TTPData
        
        # Get query parameters
        limit = min(int(request.GET.get('limit', 50)), 200)
        force_remap = request.GET.get('force', 'false').lower() == 'true'
        confidence_threshold = float(request.GET.get('confidence_threshold', 80))
        
        # Build queryset
        queryset = TTPData.objects.all()
        
        if not force_remap:
            # Only process TTPs without existing mappings
            from django.db import models as django_models
            queryset = queryset.filter(
                django_models.Q(mitre_technique_id__isnull=True) | 
                django_models.Q(mitre_technique_id__exact='') |
                django_models.Q(mitre_tactic__isnull=True) |
                django_models.Q(mitre_tactic__exact='')
            )
        
        ttps_to_process = queryset[:limit]
        
        if not ttps_to_process:
            return Response({
                "success": True,
                "message": "No TTPs found that need mapping",
                "total_processed": 0,
                "successfully_mapped": 0,
                "high_confidence_mappings": 0,
                "mappings": []
            })
        
        # Prepare TTP data for bulk mapping
        ttp_data = []
        for ttp in ttps_to_process:
            ttp_data.append({
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description
            })
        
        # Perform bulk mapping
        mapping_service = TTPMappingService()
        bulk_result = mapping_service.bulk_map_ttps(ttp_data)
        
        # Apply mappings that meet confidence threshold
        applied_mappings = 0
        high_confidence_mappings = 0
        updated_ttps = []
        
        for mapping_data in bulk_result.get('mappings', []):
            mapping = mapping_data.get('mapping', {})
            best_match = mapping.get('best_match')
            confidence = mapping.get('confidence', 0)
            
            if best_match and confidence >= confidence_threshold:
                try:
                    ttp_id = mapping_data.get('ttp_id')
                    ttp = TTPData.objects.get(id=ttp_id)
                    
                    # Update TTP with MITRE mapping
                    ttp.mitre_technique_id = best_match.get('technique_id', '')
                    ttp.mitre_tactic = best_match.get('tactic_id', '')
                    ttp.save()
                    
                    applied_mappings += 1
                    if confidence >= 90:
                        high_confidence_mappings += 1
                    
                    updated_ttps.append({
                        'ttp_id': ttp.id,
                        'ttp_name': ttp.name,
                        'technique_id': best_match.get('technique_id'),
                        'technique_name': best_match.get('technique_name'),
                        'tactic_id': best_match.get('tactic_id'),
                        'tactic_name': best_match.get('tactic_name'),
                        'confidence': confidence
                    })
                    
                except Exception as e:
                    logger.error(f"Error updating TTP {ttp_id}: {e}")
        
        return Response({
            "success": True,
            "total_processed": len(ttps_to_process),
            "total_mappings_found": bulk_result.get('mapped_count', 0),
            "successfully_applied": applied_mappings,
            "high_confidence_mappings": high_confidence_mappings,
            "confidence_threshold": confidence_threshold,
            "updated_ttps": updated_ttps,
            "bulk_mapping_stats": {
                "mapped_count": bulk_result.get('mapped_count', 0),
                "high_confidence_count": bulk_result.get('high_confidence_count', 0),
                "errors": bulk_result.get('errors', [])
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in auto-mapping existing TTPs: {str(e)}")
        return Response(
            {"error": "Failed to auto-map existing TTPs", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_technique_frequencies(request):
    """
    GET: Get technique frequency statistics
    
    Query Parameters:
    - days: Number of days to analyze (default: 30, max: 365)
    - threat_feed_id: Filter by specific threat feed ID (optional)
    - include_subtechniques: Include sub-techniques in counts (default: true)
    - min_occurrences: Minimum occurrences to include (default: 1)
    
    Returns frequency statistics for MITRE techniques.
    """
    try:
        from core.services.ttp_aggregation_service import TTPAggregationService
        
        # Get and validate query parameters
        days = min(int(request.GET.get('days', 30)), 365)
        threat_feed_id = request.GET.get('threat_feed_id')
        include_subtechniques = request.GET.get('include_subtechniques', 'true').lower() == 'true'
        min_occurrences = max(int(request.GET.get('min_occurrences', 1)), 1)
        
        if threat_feed_id:
            try:
                threat_feed_id = int(threat_feed_id)
            except ValueError:
                return Response(
                    {"error": "Invalid threat_feed_id parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get frequency statistics
        aggregation_service = TTPAggregationService()
        frequencies = aggregation_service.get_technique_frequencies(
            days=days,
            threat_feed_id=threat_feed_id,
            include_subtechniques=include_subtechniques,
            min_occurrences=min_occurrences
        )
        
        # Format response
        response_data = {
            'success': True,
            'analysis_period': {
                'days': days,
                'threat_feed_id': threat_feed_id,
                'include_subtechniques': include_subtechniques,
                'min_occurrences': min_occurrences
            },
            'total_techniques': len(frequencies),
            'techniques': {
                technique_id: {
                    'count': stats.count,
                    'percentage': stats.percentage,
                    'rank': stats.rank,
                    'first_seen': stats.first_seen.isoformat() if stats.first_seen else None,
                    'last_seen': stats.last_seen.isoformat() if stats.last_seen else None
                }
                for technique_id, stats in frequencies.items()
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting technique frequencies: {str(e)}")
        return Response(
            {"error": "Failed to get technique frequencies", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_tactic_frequencies(request):
    """
    GET: Get tactic frequency statistics
    
    Query Parameters:
    - days: Number of days to analyze (default: 30, max: 365)
    - threat_feed_id: Filter by specific threat feed ID (optional)
    - min_occurrences: Minimum occurrences to include (default: 1)
    
    Returns frequency statistics for MITRE tactics.
    """
    try:
        from core.services.ttp_aggregation_service import TTPAggregationService
        
        # Get and validate query parameters
        days = min(int(request.GET.get('days', 30)), 365)
        threat_feed_id = request.GET.get('threat_feed_id')
        min_occurrences = max(int(request.GET.get('min_occurrences', 1)), 1)
        
        if threat_feed_id:
            try:
                threat_feed_id = int(threat_feed_id)
            except ValueError:
                return Response(
                    {"error": "Invalid threat_feed_id parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get frequency statistics
        aggregation_service = TTPAggregationService()
        frequencies = aggregation_service.get_tactic_frequencies(
            days=days,
            threat_feed_id=threat_feed_id,
            min_occurrences=min_occurrences
        )
        
        # Format response
        response_data = {
            'success': True,
            'analysis_period': {
                'days': days,
                'threat_feed_id': threat_feed_id,
                'min_occurrences': min_occurrences
            },
            'total_tactics': len(frequencies),
            'tactics': {
                tactic_id: {
                    'count': stats.count,
                    'percentage': stats.percentage,
                    'rank': stats.rank,
                    'first_seen': stats.first_seen.isoformat() if stats.first_seen else None,
                    'last_seen': stats.last_seen.isoformat() if stats.last_seen else None
                }
                for tactic_id, stats in frequencies.items()
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting tactic frequencies: {str(e)}")
        return Response(
            {"error": "Failed to get tactic frequencies", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_technique_trends(request):
    """
    GET: Get time-based trends for a specific technique
    
    Query Parameters:
    - technique_id: MITRE technique ID (required)
    - days: Number of days to analyze (default: 90, max: 365)
    - granularity: Time granularity - 'day', 'week', 'month' (default: 'day')
    - threat_feed_id: Filter by specific threat feed ID (optional)
    - moving_average_window: Window size for moving average (default: 7)
    - include_analysis: Include trend analysis (default: true)
    
    Returns time-based trend data for the specified technique.
    """
    try:
        from core.services.ttp_aggregation_service import TTPAggregationService
        
        # Get and validate query parameters
        technique_id = request.GET.get('technique_id', '').strip()
        if not technique_id:
            return Response(
                {"error": "technique_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        days = min(int(request.GET.get('days', 90)), 365)
        granularity = request.GET.get('granularity', 'day').lower()
        threat_feed_id = request.GET.get('threat_feed_id')
        moving_average_window = max(int(request.GET.get('moving_average_window', 7)), 1)
        include_analysis = request.GET.get('include_analysis', 'true').lower() == 'true'
        
        if granularity not in ['day', 'week', 'month']:
            return Response(
                {"error": "Invalid granularity. Must be 'day', 'week', or 'month'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if threat_feed_id:
            try:
                threat_feed_id = int(threat_feed_id)
            except ValueError:
                return Response(
                    {"error": "Invalid threat_feed_id parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get trend data
        aggregation_service = TTPAggregationService()
        trend_points = aggregation_service.get_technique_trends(
            technique_id=technique_id,
            days=days,
            granularity=granularity,
            threat_feed_id=threat_feed_id,
            moving_average_window=moving_average_window
        )
        
        # Format trend points for response
        formatted_trends = [
            {
                'date': point.date,
                'value': point.value,
                'percentage_change': point.percentage_change,
                'moving_average': point.moving_average
            }
            for point in trend_points
        ]
        
        # Prepare response
        response_data = {
            'success': True,
            'technique_id': technique_id,
            'analysis_period': {
                'days': days,
                'granularity': granularity,
                'threat_feed_id': threat_feed_id,
                'moving_average_window': moving_average_window
            },
            'trend_points': formatted_trends,
            'total_data_points': len(formatted_trends),
            'summary': {
                'total_occurrences': sum(point.value for point in trend_points),
                'peak_value': max((point.value for point in trend_points), default=0),
                'average_value': round(sum(point.value for point in trend_points) / len(trend_points), 2) if trend_points else 0
            }
        }
        
        # Add trend analysis if requested
        if include_analysis and trend_points:
            trend_analysis = aggregation_service.analyze_trend_direction(trend_points)
            response_data['trend_analysis'] = {
                'direction': trend_analysis.direction,
                'strength': trend_analysis.strength,
                'confidence': trend_analysis.confidence,
                'slope': trend_analysis.slope,
                'r_squared': trend_analysis.r_squared,
                'volatility': trend_analysis.volatility
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting technique trends: {str(e)}")
        return Response(
            {"error": "Failed to get technique trends", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_feed_comparison(request):
    """
    GET: Compare TTP statistics across different threat feeds
    
    Query Parameters:
    - days: Number of days to analyze (default: 30, max: 365)
    - top_n: Number of top feeds to include (default: 10, max: 50)
    
    Returns comparative statistics across threat feeds.
    """
    try:
        from core.services.ttp_aggregation_service import TTPAggregationService
        
        # Get and validate query parameters
        days = min(int(request.GET.get('days', 30)), 365)
        top_n = min(int(request.GET.get('top_n', 10)), 50)
        
        # Get comparison statistics
        aggregation_service = TTPAggregationService()
        comparison_stats = aggregation_service.get_feed_comparison_stats(
            days=days,
            top_n=top_n
        )
        
        if not comparison_stats:
            return Response(
                {"error": "No data available for feed comparison"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(comparison_stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feed comparison stats: {str(e)}")
        return Response(
            {"error": "Failed to get feed comparison statistics", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_seasonal_patterns(request):
    """
    GET: Analyze seasonal patterns in TTP occurrence
    
    Query Parameters:
    - technique_id: Optional specific technique to analyze
    - days: Number of days to analyze (default: 365, minimum: 90)
    - granularity: Time granularity - 'week', 'month' (default: 'week')
    
    Returns seasonal pattern analysis.
    """
    try:
        from core.services.ttp_aggregation_service import TTPAggregationService
        
        # Get and validate query parameters
        technique_id = request.GET.get('technique_id', '').strip() or None
        days = max(int(request.GET.get('days', 365)), 90)  # Minimum 90 days for seasonal analysis
        granularity = request.GET.get('granularity', 'week').lower()
        
        if granularity not in ['week', 'month']:
            return Response(
                {"error": "Invalid granularity. Must be 'week' or 'month'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get seasonal pattern analysis
        aggregation_service = TTPAggregationService()
        seasonal_analysis = aggregation_service.get_seasonal_patterns(
            technique_id=technique_id,
            days=days,
            granularity=granularity
        )
        
        if 'error' in seasonal_analysis:
            return Response(seasonal_analysis, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(seasonal_analysis, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting seasonal patterns: {str(e)}")
        return Response(
            {"error": "Failed to get seasonal patterns", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def ttp_clear_aggregation_cache(request):
    """
    POST: Clear TTP aggregation cache
    
    Request Body (optional):
    {
        "pattern": "technique_freq"  // Optional pattern to match specific cache keys
    }
    
    Returns cache clearing confirmation.
    """
    try:
        from core.services.ttp_aggregation_service import TTPAggregationService
        
        # Get optional pattern from request
        pattern = request.data.get('pattern', '').strip() or None
        
        # Clear cache
        aggregation_service = TTPAggregationService()
        aggregation_service.clear_cache(pattern)
        
        return Response({
            "success": True,
            "message": f"Cache cleared successfully{f' with pattern: {pattern}' if pattern else ''}",
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error clearing aggregation cache: {str(e)}")
        return Response(
            {"error": "Failed to clear aggregation cache", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_filter_options(request):
    """
    GET: Get available filter options for TTP search and filtering
    
    Returns all available filter options including:
    - Available tactics with counts
    - Top techniques with usage counts
    - Available threat feeds with TTP counts
    - Severity levels
    - Valid sort fields
    - Searchable fields
    """
    try:
        from core.services.ttp_filter_service import TTPFilterService
        
        # Initialize filter service
        filter_service = TTPFilterService()
        
        # Get filter options
        options = filter_service.get_filter_options()
        
        return Response({
            "success": True,
            "filter_options": options,
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting filter options: {str(e)}")
        return Response(
            {"error": "Failed to get filter options", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def ttp_advanced_search(request):
    """
    POST: Perform advanced TTP search with complex filtering criteria
    
    Request Body:
    {
        "filters": {
            "tactics": ["initial_access", "execution"],
            "techniques": ["T1566", "T1059"],
            "technique_search": "T15",
            "severity_levels": ["critical", "high"],
            "date_from": "2024-01-01T00:00:00Z",
            "date_to": "2024-12-31T23:59:59Z",
            "threat_feed_ids": [1, 2, 3],
            "external_feeds_only": true,
            "active_feeds_only": true,
            "search_query": "malware phishing",
            "search_fields": ["name", "description"],
            "has_subtechniques": true,
            "anonymized_only": false
        },
        "sorting": {
            "sort_by": "severity_score",
            "sort_order": "desc"
        },
        "pagination": {
            "page": 1,
            "page_size": 50
        }
    }
    
    Returns filtered and paginated TTP results with statistics.
    """
    try:
        from core.services.ttp_filter_service import TTPFilterService, FilterCriteria, SeverityLevel, SortOrder
        from datetime import datetime
        
        # Parse request body
        data = request.data if request.data else {}
        filters = data.get('filters', {})
        sorting = data.get('sorting', {})
        pagination = data.get('pagination', {})
        
        # Parse severity levels
        severity_levels = None
        if filters.get('severity_levels'):
            try:
                severity_levels = [
                    SeverityLevel(level) for level in filters['severity_levels']
                    if level in [s.value for s in SeverityLevel]
                ]
            except ValueError:
                pass
        
        # Parse date parameters
        date_from = None
        date_to = None
        if filters.get('date_from'):
            try:
                date_from = datetime.fromisoformat(filters['date_from'].replace('Z', '+00:00'))
            except:
                pass
        if filters.get('date_to'):
            try:
                date_to = datetime.fromisoformat(filters['date_to'].replace('Z', '+00:00'))
            except:
                pass
        
        # Parse sort order
        sort_order = SortOrder.DESC
        if sorting.get('sort_order', '').lower() == 'asc':
            sort_order = SortOrder.ASC
        
        # Build filter criteria
        criteria = FilterCriteria(
            tactics=filters.get('tactics'),
            techniques=filters.get('techniques'),
            technique_search=filters.get('technique_search'),
            severity_levels=severity_levels,
            date_from=date_from,
            date_to=date_to,
            created_after=datetime.fromisoformat(filters['created_after'].replace('Z', '+00:00')) if filters.get('created_after') else None,
            created_before=datetime.fromisoformat(filters['created_before'].replace('Z', '+00:00')) if filters.get('created_before') else None,
            updated_after=datetime.fromisoformat(filters['updated_after'].replace('Z', '+00:00')) if filters.get('updated_after') else None,
            updated_before=datetime.fromisoformat(filters['updated_before'].replace('Z', '+00:00')) if filters.get('updated_before') else None,
            threat_feed_ids=filters.get('threat_feed_ids'),
            external_feeds_only=filters.get('external_feeds_only'),
            active_feeds_only=filters.get('active_feeds_only'),
            search_query=filters.get('search_query'),
            search_fields=filters.get('search_fields'),
            has_subtechniques=filters.get('has_subtechniques'),
            anonymized_only=filters.get('anonymized_only'),
            page=pagination.get('page', 1),
            page_size=min(pagination.get('page_size', 20), 100),
            sort_by=sorting.get('sort_by', 'created_at'),
            sort_order=sort_order
        )
        
        # Initialize filter service and apply filters
        filter_service = TTPFilterService()
        result = filter_service.filter_ttps(criteria)
        
        # Build response
        response_data = {
            "success": True,
            "query": {
                "filters": filters,
                "sorting": sorting,
                "pagination": pagination
            },
            "results": {
                "ttps": result.ttps,
                "total_count": result.total_count,
                "filtered_count": result.filtered_count,
                "page": result.page,
                "page_size": result.page_size,
                "total_pages": result.total_pages,
                "has_next": result.has_next,
                "has_previous": result.has_previous
            },
            "filters_applied": result.filters_applied,
            "statistics": result.statistics,
            "timestamp": timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error performing advanced TTP search: {str(e)}")
        return Response(
            {"error": "Failed to perform advanced search", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_search_suggestions(request):
    """
    GET: Get search suggestions for TTP search autocomplete
    
    Query Parameters:
    - q: Search query (minimum 2 characters)
    - type: Suggestion type (technique, tactic, name, description) - default: all
    - limit: Maximum suggestions to return (default: 10, max: 50)
    
    Returns search suggestions based on existing TTP data.
    """
    try:
        from django.db.models import Q
        from core.models.models import TTPData
        
        # Get query parameters
        query = request.GET.get('q', '').strip()
        suggestion_type = request.GET.get('type', 'all')
        limit = min(int(request.GET.get('limit', 10)), 50)
        
        if len(query) < 2:
            return Response({
                "success": True,
                "suggestions": [],
                "message": "Query must be at least 2 characters long"
            }, status=status.HTTP_200_OK)
        
        suggestions = []
        
        # Technique ID suggestions
        if suggestion_type in ['all', 'technique']:
            technique_suggestions = TTPData.objects.filter(
                mitre_technique_id__icontains=query
            ).values('mitre_technique_id').distinct()[:limit]
            
            for item in technique_suggestions:
                suggestions.append({
                    'type': 'technique',
                    'value': item['mitre_technique_id'],
                    'label': f"Technique: {item['mitre_technique_id']}",
                    'category': 'MITRE Technique'
                })
        
        # Tactic suggestions
        if suggestion_type in ['all', 'tactic']:
            tactic_suggestions = TTPData.objects.filter(
                mitre_tactic__icontains=query
            ).values('mitre_tactic').distinct()[:limit]
            
            for item in tactic_suggestions:
                tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(
                    item['mitre_tactic'], item['mitre_tactic']
                )
                suggestions.append({
                    'type': 'tactic',
                    'value': item['mitre_tactic'],
                    'label': f"Tactic: {tactic_display}",
                    'category': 'MITRE Tactic'
                })
        
        # Name suggestions
        if suggestion_type in ['all', 'name']:
            name_suggestions = TTPData.objects.filter(
                name__icontains=query
            ).values('name').distinct()[:limit]
            
            for item in name_suggestions:
                suggestions.append({
                    'type': 'name',
                    'value': item['name'],
                    'label': f"Name: {item['name'][:50]}{'...' if len(item['name']) > 50 else ''}",
                    'category': 'TTP Name'
                })
        
        # Subtechnique suggestions
        if suggestion_type in ['all', 'subtechnique']:
            subtechnique_suggestions = TTPData.objects.filter(
                mitre_subtechnique__icontains=query
            ).exclude(
                mitre_subtechnique__isnull=True
            ).exclude(
                mitre_subtechnique=''
            ).values('mitre_subtechnique').distinct()[:limit]
            
            for item in subtechnique_suggestions:
                suggestions.append({
                    'type': 'subtechnique',
                    'value': item['mitre_subtechnique'],
                    'label': f"Subtechnique: {item['mitre_subtechnique']}",
                    'category': 'MITRE Subtechnique'
                })
        
        # Sort suggestions by relevance (exact matches first, then partial)
        def suggestion_score(suggestion):
            value = suggestion['value'].lower()
            query_lower = query.lower()
            if value.startswith(query_lower):
                return 0  # Exact prefix match
            elif query_lower in value:
                return 1  # Contains match
            else:
                return 2  # Other match
        
        suggestions.sort(key=suggestion_score)
        
        # Limit total suggestions
        suggestions = suggestions[:limit]
        
        return Response({
            "success": True,
            "suggestions": suggestions,
            "query": query,
            "total_suggestions": len(suggestions),
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {str(e)}")
        return Response(
            {"error": "Failed to get search suggestions", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_matrix_cell_details(request):
    """
    GET: Get detailed TTP data for a specific matrix cell (tactic/technique combination)
    
    Query Parameters:
    - tactic: MITRE tactic code (required for tactic-based queries)
    - technique_id: MITRE technique ID (optional for technique-based queries)
    - feed_id: Filter by specific threat feed ID (optional)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - include_related: Include related techniques in same tactic (default: false)
    
    Returns detailed information about TTPs in the specified matrix cell,
    including technique details, threat feed information, and statistics.
    """
    try:
        from core.services.ttp_filter_service import TTPFilterService, FilterCriteria, SortOrder
        from django.db.models import Count, Q
        
        # Get query parameters
        tactic = request.GET.get('tactic', '').strip()
        technique_id = request.GET.get('technique_id', '').strip()
        feed_id = request.GET.get('feed_id', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        
        if not tactic:
            return Response({
                "error": "Missing required parameter: 'tactic' is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate tactic
        valid_tactics = [choice[0] for choice in TTPData.MITRE_TACTIC_CHOICES]
        if tactic not in valid_tactics:
            return Response({
                "error": f"Invalid tactic '{tactic}'. Valid tactics: {', '.join(valid_tactics)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build filter criteria
        criteria = FilterCriteria(
            tactics=[tactic],
            techniques=[technique_id] if technique_id else None,
            threat_feed_ids=[int(feed_id)] if feed_id and feed_id.isdigit() else None,
            page=page,
            page_size=page_size,
            sort_by='created_at',
            sort_order=SortOrder.DESC
        )
        
        # Use the filter service to get TTPs
        filter_service = TTPFilterService()
        result = filter_service.filter_ttps(criteria)
        
        # Get tactic display name
        tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(tactic, tactic)
        
        # Get related techniques if requested
        related_techniques = []
        if include_related:
            related_query = TTPData.objects.filter(mitre_tactic=tactic)
            if feed_id and feed_id.isdigit():
                related_query = related_query.filter(threat_feed_id=int(feed_id))
            
            # Get unique techniques in this tactic
            unique_techniques = related_query.values('mitre_technique_id').annotate(
                count=Count('id')
            ).order_by('-count')[:10]  # Top 10 most common techniques
            
            related_techniques = list(unique_techniques)
        
        # Calculate additional statistics for the matrix cell
        cell_stats = {
            'tactic': tactic,
            'tactic_display': tactic_display,
            'technique_filter': technique_id if technique_id else None,
            'total_ttps_in_cell': result.filtered_count,
            'unique_techniques': TTPData.objects.filter(
                mitre_tactic=tactic
            ).values('mitre_technique_id').distinct().count(),
            'threat_feeds_count': TTPData.objects.filter(
                mitre_tactic=tactic
            ).values('threat_feed_id').distinct().count(),
            'recent_activity': TTPData.objects.filter(
                mitre_tactic=tactic,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'has_subtechniques': TTPData.objects.filter(
                mitre_tactic=tactic
            ).exclude(
                Q(mitre_subtechnique__isnull=True) | Q(mitre_subtechnique='')
            ).count()
        }
        
        # Build comprehensive response
        response_data = {
            "success": True,
            "cell_info": cell_stats,
            "ttps": {
                "results": result.ttps,
                "total_count": result.total_count,
                "filtered_count": result.filtered_count,
                "page": result.page,
                "page_size": result.page_size,
                "total_pages": result.total_pages,
                "has_next": result.has_next,
                "has_previous": result.has_previous
            },
            "related_techniques": related_techniques,
            "filters_applied": result.filters_applied,
            "statistics": result.statistics,
            "query_parameters": {
                "tactic": tactic,
                "technique_id": technique_id,
                "feed_id": feed_id,
                "page": page,
                "page_size": page_size,
                "include_related": include_related
            },
            "timestamp": timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            "error": "Invalid parameter value",
            "details": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error getting matrix cell details: {str(e)}")
        return Response(
            {"error": "Failed to get matrix cell details", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def ttp_technique_details(request, technique_id):
    """
    GET: Get detailed information about a specific MITRE technique
    
    Path Parameters:
    - technique_id: MITRE technique ID (e.g., T1566.001)
    
    Query Parameters:
    - feed_id: Filter by specific threat feed ID (optional)
    - include_variants: Include all variants/subtechniques (default: true)
    - include_tactics: Include all tactics this technique appears in (default: true)
    
    Returns comprehensive information about the specified technique including
    all TTPs using this technique, associated tactics, and usage statistics.
    """
    try:
        from core.services.ttp_filter_service import TTPFilterService, FilterCriteria, SortOrder
        from django.db.models import Count, Q
        from datetime import timedelta
        
        # Get query parameters
        feed_id = request.GET.get('feed_id', '').strip()
        include_variants = request.GET.get('include_variants', 'true').lower() == 'true'
        include_tactics = request.GET.get('include_tactics', 'true').lower() == 'true'
        
        # Validate technique ID format
        import re
        if not re.match(r'^T\d{4}(\.\d{3})?$', technique_id):
            return Response({
                "error": f"Invalid technique ID format: '{technique_id}'. Expected format: T1234 or T1234.001"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build base query
        base_query = TTPData.objects.filter(mitre_technique_id=technique_id)
        if feed_id and feed_id.isdigit():
            base_query = base_query.filter(threat_feed_id=int(feed_id))
        
        # Check if technique exists
        if not base_query.exists():
            return Response({
                "error": f"No TTPs found for technique '{technique_id}'"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all TTPs for this technique
        technique_ttps = list(base_query.select_related('threat_feed').order_by('-created_at'))
        
        # Serialize TTP data
        ttps_data = []
        for ttp in technique_ttps:
            ttps_data.append({
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': ttp.mitre_tactic,
                'mitre_tactic_display': dict(TTPData.MITRE_TACTIC_CHOICES).get(
                    ttp.mitre_tactic, ttp.mitre_tactic
                ) if ttp.mitre_tactic else None,
                'mitre_subtechnique': ttp.mitre_subtechnique,
                'stix_id': ttp.stix_id,
                'is_anonymized': ttp.is_anonymized,
                'created_at': ttp.created_at.isoformat(),
                'updated_at': ttp.updated_at.isoformat(),
                'threat_feed': {
                    'id': ttp.threat_feed.id,
                    'name': ttp.threat_feed.name,
                    'is_external': ttp.threat_feed.is_external,
                    'is_active': ttp.threat_feed.is_active
                } if ttp.threat_feed else None
            })
        
        # Get technique variants/subtechniques if requested
        variants = []
        if include_variants:
            # Get base technique ID (without subtechnique)
            base_technique = technique_id.split('.')[0]
            
            variant_query = TTPData.objects.filter(
                mitre_technique_id__startswith=f"{base_technique}."
            ).exclude(mitre_technique_id=technique_id)
            
            if feed_id and feed_id.isdigit():
                variant_query = variant_query.filter(threat_feed_id=int(feed_id))
            
            variant_data = variant_query.values('mitre_technique_id').annotate(
                count=Count('id'),
                subtechnique_name=Count('mitre_subtechnique')
            ).order_by('-count')
            
            variants = list(variant_data)
        
        # Get associated tactics if requested
        associated_tactics = []
        if include_tactics:
            tactic_data = base_query.values('mitre_tactic').annotate(
                count=Count('id')
            ).exclude(mitre_tactic__isnull=True).order_by('-count')
            
            for item in tactic_data:
                tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(
                    item['mitre_tactic'], item['mitre_tactic']
                )
                associated_tactics.append({
                    'tactic': item['mitre_tactic'],
                    'tactic_display': tactic_display,
                    'count': item['count']
                })
        
        # Calculate statistics
        now = timezone.now()
        statistics = {
            'total_ttps': len(technique_ttps),
            'unique_threat_feeds': base_query.values('threat_feed_id').distinct().count(),
            'first_seen': technique_ttps[-1].created_at.isoformat() if technique_ttps else None,
            'last_seen': technique_ttps[0].created_at.isoformat() if technique_ttps else None,
            'recent_activity': {
                'last_24h': base_query.filter(created_at__gte=now - timedelta(hours=24)).count(),
                'last_7d': base_query.filter(created_at__gte=now - timedelta(days=7)).count(),
                'last_30d': base_query.filter(created_at__gte=now - timedelta(days=30)).count()
            },
            'anonymized_count': base_query.filter(is_anonymized=True).count(),
            'with_subtechniques': base_query.exclude(
                Q(mitre_subtechnique__isnull=True) | Q(mitre_subtechnique='')
            ).count()
        }
        
        # Determine technique severity using our severity mapping
        from core.services.ttp_filter_service import TTPFilterService
        filter_service = TTPFilterService()
        severity = filter_service._get_technique_severity(technique_id)
        
        response_data = {
            "success": True,
            "technique_info": {
                "technique_id": technique_id,
                "base_technique": technique_id.split('.')[0],
                "is_subtechnique": '.' in technique_id,
                "severity": severity.value,
                "name": technique_ttps[0].name if technique_ttps else None
            },
            "ttps": ttps_data,
            "variants": variants if include_variants else None,
            "associated_tactics": associated_tactics if include_tactics else None,
            "statistics": statistics,
            "query_parameters": {
                "technique_id": technique_id,
                "feed_id": feed_id,
                "include_variants": include_variants,
                "include_tactics": include_tactics
            },
            "timestamp": timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting technique details: {str(e)}")
        return Response(
            {"error": "Failed to get technique details", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_http_methods(["GET"])
def ttp_export_csv(request):
    """
    Plain Django view for CSV export to bypass DRF content negotiation issues
    """
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 1000))
        tactic = request.GET.get('tactic', '').strip()
        technique_id = request.GET.get('technique_id', '').strip()
        feed_id = request.GET.get('feed_id', '').strip()

        # Get TTPs with filters
        queryset = TTPData.objects.select_related('threat_feed').all()

        if tactic:
            queryset = queryset.filter(mitre_tactic=tactic)
        if technique_id:
            queryset = queryset.filter(mitre_technique_id__icontains=technique_id)
        if feed_id:
            try:
                feed_id_int = int(feed_id)
                queryset = queryset.filter(threat_feed_id=feed_id_int)
            except ValueError:
                pass

        # Apply limit and order
        queryset = queryset.order_by('-created_at')[:limit]
        ttps = list(queryset)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="ttps_export_{timestamp}.csv"'

        # Define CSV fields
        fieldnames = [
            'id', 'name', 'description', 'mitre_technique_id', 'mitre_tactic',
            'mitre_subtechnique', 'threat_feed_name', 'created_at', 'updated_at'
        ]

        writer = csv.DictWriter(response, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for ttp in ttps:
            # Get tactic display name
            tactic_display = dict(TTPData.MITRE_TACTIC_CHOICES).get(ttp.mitre_tactic, ttp.mitre_tactic) if ttp.mitre_tactic else ''

            row_data = {
                'id': ttp.id,
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': tactic_display,
                'mitre_subtechnique': ttp.mitre_subtechnique or '',
                'threat_feed_name': ttp.threat_feed.name if ttp.threat_feed else '',
                'created_at': ttp.created_at.isoformat(),
                'updated_at': ttp.updated_at.isoformat()
            }

            writer.writerow(row_data)

        return response

    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500, content_type='text/plain')


@csrf_exempt
@require_http_methods(["GET"])
def ttp_export_stix(request):
    """
    Plain Django view for STIX export to bypass DRF content negotiation issues
    """
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 1000))
        tactic = request.GET.get('tactic', '').strip()
        technique_id = request.GET.get('technique_id', '').strip()
        feed_id = request.GET.get('feed_id', '').strip()

        # Get TTPs with filters
        queryset = TTPData.objects.select_related('threat_feed').all()

        if tactic:
            queryset = queryset.filter(mitre_tactic=tactic)
        if technique_id:
            queryset = queryset.filter(mitre_technique_id__icontains=technique_id)
        if feed_id:
            try:
                feed_id_int = int(feed_id)
                queryset = queryset.filter(threat_feed_id=feed_id_int)
            except ValueError:
                pass

        # Apply limit and order
        queryset = queryset.order_by('-created_at')[:limit]
        ttps = list(queryset)

        # Create STIX bundle
        stix_objects = []
        bundle_id = f"bundle--{str(uuid.uuid4())}"

        # Add identity object
        identity_obj = {
            "type": "identity",
            "spec_version": "2.1",
            "id": f"identity--{str(uuid.uuid4())}",
            "created": timezone.now().isoformat(),
            "modified": timezone.now().isoformat(),
            "name": "CRISP Threat Intelligence Platform",
            "identity_class": "system"
        }
        stix_objects.append(identity_obj)

        # Convert TTPs to STIX Attack Pattern objects
        for ttp in ttps:
            attack_pattern = {
                "type": "attack-pattern",
                "spec_version": "2.1",
                "id": ttp.stix_id,
                "created": ttp.created_at.isoformat(),
                "modified": ttp.updated_at.isoformat(),
                "name": ttp.name,
                "description": ttp.description,
                "created_by_ref": identity_obj["id"]
            }

            # Add MITRE external references
            if ttp.mitre_technique_id:
                attack_pattern["external_references"] = [{
                    "source_name": "mitre-attack",
                    "external_id": ttp.mitre_technique_id,
                    "url": f"https://attack.mitre.org/techniques/{ttp.mitre_technique_id.replace('.', '/')}/"
                }]

            # Add kill chain phases
            if ttp.mitre_tactic:
                attack_pattern["kill_chain_phases"] = [{
                    "kill_chain_name": "mitre-attack",
                    "phase_name": ttp.mitre_tactic.replace('_', '-')
                }]

            stix_objects.append(attack_pattern)

        bundle = {
            "type": "bundle",
            "spec_version": "2.1",
            "id": bundle_id,
            "objects": stix_objects
        }

        # Create JSON response
        response = HttpResponse(content_type='application/json')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="ttps_export_{timestamp}.stix"'
        response.write(json.dumps(bundle, indent=2, ensure_ascii=False))
        return response

    except Exception as e:
        logger.error(f"STIX export error: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500, content_type='text/plain')


@api_view(['POST'])
@permission_classes([AllowAny])
def virustotal_sync(request):
    """
    POST: Manually trigger VirusTotal TTP synchronization

    Body Parameters:
    - feed_id: Specific VirusTotal feed ID to sync (optional)
    - limit: Number of indicators to process (default: 50, max: 200)
    - force_sync: Force sync even if recently synced (default: false)

    Triggers the VirusTotal service to analyze existing indicators
    and extract TTP data from malware analysis results.
    """
    try:
        from core.services.virustotal_service import VirusTotalService
        from django.db import transaction

        # Get parameters
        feed_id = request.data.get('feed_id')
        limit = min(int(request.data.get('limit', 50)), 200)  # Cap at 200 for rate limits
        force_sync = request.data.get('force_sync', False)

        # Initialize VirusTotal service
        vt_service = VirusTotalService()

        # Test API connection
        connection_test = vt_service.test_api_connection()
        if not connection_test['success']:
            return Response({
                'success': False,
                'error': f"VirusTotal API connection failed: {connection_test['error']}",
                'quota_info': connection_test.get('quota', 'Unknown')
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Get VirusTotal feeds to sync
        if feed_id:
            try:
                feeds = [ThreatFeed.objects.get(id=int(feed_id), is_active=True)]
                if 'virustotal' not in feeds[0].name.lower():
                    return Response({
                        'success': False,
                        'error': f"Feed '{feeds[0].name}' doesn't appear to be a VirusTotal feed"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ThreatFeed.DoesNotExist, ValueError):
                return Response({
                    'success': False,
                    'error': f"VirusTotal feed with ID {feed_id} not found or inactive"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get all active VirusTotal feeds
            feeds = ThreatFeed.objects.filter(
                name__icontains='virustotal',
                is_active=True
            )

        if not feeds:
            return Response({
                'success': False,
                'error': 'No active VirusTotal feeds found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if we should skip due to recent sync (unless forced)
        if not force_sync:
            for feed in feeds:
                if feed.last_sync and (timezone.now() - feed.last_sync).total_seconds() < 3600:  # 1 hour
                    return Response({
                        'success': False,
                        'error': f'Feed {feed.name} was synced recently. Use force_sync=true to override.',
                        'last_sync': feed.last_sync.isoformat() if feed.last_sync else None
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        results = []
        total_ttps_created = 0
        total_indicators_processed = 0

        # Process each feed
        for feed in feeds:
            try:
                with transaction.atomic():
                    result = vt_service.sync_virustotal_feed(feed, limit=limit)
                    results.append({
                        'feed_id': feed.id,
                        'feed_name': feed.name,
                        'success': result['success'],
                        'ttps_created': result.get('ttps_created', 0),
                        'indicators_processed': result.get('indicators_processed', 0),
                        'errors': result.get('errors', [])
                    })

                    if result['success']:
                        total_ttps_created += result.get('ttps_created', 0)
                        total_indicators_processed += result.get('indicators_processed', 0)

            except Exception as e:
                logger.error(f"VirusTotal sync error for feed {feed.name}: {str(e)}")
                results.append({
                    'feed_id': feed.id,
                    'feed_name': feed.name,
                    'success': False,
                    'error': str(e)
                })

        # Overall success if at least one feed succeeded
        overall_success = any(result['success'] for result in results)

        response_data = {
            'success': overall_success,
            'message': f'VirusTotal sync completed for {len(feeds)} feed(s)',
            'summary': {
                'total_feeds_processed': len(feeds),
                'successful_syncs': sum(1 for result in results if result['success']),
                'total_ttps_created': total_ttps_created,
                'total_indicators_processed': total_indicators_processed,
                'rate_limit_info': 'VirusTotal free tier: 4 requests/minute'
            },
            'feed_results': results,
            'quota_info': connection_test.get('quota', 'Unknown'),
            'timestamp': timezone.now().isoformat()
        }

        return Response(response_data, status=status.HTTP_200_OK if overall_success else status.HTTP_207_MULTI_STATUS)

    except Exception as e:
        logger.error(f"VirusTotal sync endpoint error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to sync VirusTotal feeds',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)