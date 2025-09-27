"""
Sync API for real-time updates
Provides endpoints for checking if data needs to be refreshed
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_updates(request):
    """
    Check if various data types need to be refreshed
    Returns timestamps of last updates for different data types
    """
    try:
        updates = {
            'indicators_updated': cache.get('indicators_updated'),
            'alerts_updated': cache.get('alerts_updated'),
            'assets_updated': cache.get('assets_updated'),
            'feeds_updated': cache.get('feeds_updated'),
            'current_time': timezone.now().isoformat()
        }

        # Remove None values
        updates = {k: v for k, v in updates.items() if v is not None}

        return Response({
            'success': True,
            'updates': updates
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error checking updates: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_update_seen(request):
    """
    Mark an update as seen by the client
    """
    try:
        update_type = request.data.get('update_type')
        timestamp = request.data.get('timestamp')

        if not update_type or not timestamp:
            return Response({
                'success': False,
                'error': 'update_type and timestamp are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Store the last seen timestamp for this user/update type
        cache_key = f"update_seen_{request.user.id}_{update_type}"
        cache.set(cache_key, timestamp, timeout=3600)

        return Response({
            'success': True,
            'message': f'Marked {update_type} as seen at {timestamp}'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error marking update as seen: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_last_seen(request):
    """
    Get the last seen timestamps for this user
    """
    try:
        update_types = ['indicators_updated', 'alerts_updated', 'assets_updated', 'feeds_updated']
        last_seen = {}

        for update_type in update_types:
            cache_key = f"update_seen_{request.user.id}_{update_type}"
            last_seen[update_type] = cache.get(cache_key)

        return Response({
            'success': True,
            'last_seen': last_seen
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting last seen: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)