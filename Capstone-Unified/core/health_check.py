"""
Health check endpoint for production monitoring
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import time


def health_check(request):
    """
    Health check endpoint that verifies:
    - Database connectivity
    - Cache (Redis) connectivity
    - Basic application functionality
    """
    status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }

    overall_healthy = True

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status['checks']['database'] = 'healthy'
    except Exception as e:
        status['checks']['database'] = f'unhealthy: {str(e)}'
        overall_healthy = False

    # Cache check
    try:
        cache.set('health_check', 'test', 10)
        value = cache.get('health_check')
        if value == 'test':
            status['checks']['cache'] = 'healthy'
        else:
            status['checks']['cache'] = 'unhealthy: cache get/set failed'
            overall_healthy = False
    except Exception as e:
        status['checks']['cache'] = f'unhealthy: {str(e)}'
        overall_healthy = False

    if not overall_healthy:
        status['status'] = 'unhealthy'
        return JsonResponse(status, status=503)

    return JsonResponse(status)