"""
Behavior Analytics API Views
REST API endpoints for user behavior analytics and anomaly detection
"""

import logging
import csv
import json
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from core.models.user_behavior_models import (
    UserBehaviorBaseline, UserSession, BehaviorAnomaly, 
    UserActivityLog, BehaviorAlert
)
from core.services.user_behavior_analytics_service import UserBehaviorAnalyticsService

User = get_user_model()
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def behavior_analytics_dashboard(request):
    """
    Get behavior analytics dashboard data
    """
    try:
        # Check if user has admin permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        days = int(request.GET.get('days', 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get organization-specific data
        organization = request.user.organization
        if request.user.is_superuser:
            # Superuser can see all organizations
            user_filter = Q()
        else:
            # Regular admin sees only their organization
            user_filter = Q(user__organization=organization)
        
        # Overall statistics
        total_users = User.objects.filter(user_filter).count()
        active_sessions = UserSession.objects.filter(
            user_filter,
            start_time__gte=start_date,
            end_time__isnull=True
        ).count()
        
        total_anomalies = BehaviorAnomaly.objects.filter(
            user_filter,
            detected_at__gte=start_date
        ).count()
        
        active_alerts = BehaviorAlert.objects.filter(
            user_filter,
            created_at__gte=start_date,
            is_acknowledged=False
        ).count()
        
        # Anomaly breakdown by type
        anomaly_breakdown = list(
            BehaviorAnomaly.objects.filter(
                user_filter,
                detected_at__gte=start_date
            ).values('anomaly_type').annotate(
                count=Count('anomaly_type')
            ).order_by('-count')
        )
        
        # Severity breakdown
        severity_breakdown = list(
            BehaviorAnomaly.objects.filter(
                user_filter,
                detected_at__gte=start_date
            ).values('severity').annotate(
                count=Count('severity')
            )
        )
        
        # Top risky users
        risky_users = list(
            BehaviorAnomaly.objects.filter(
                user_filter,
                detected_at__gte=start_date,
                confidence_score__gte=70
            ).values('user__username', 'user__first_name', 'user__last_name').annotate(
                anomaly_count=Count('id'),
                avg_confidence=Avg('confidence_score')
            ).order_by('-anomaly_count')[:10]
        )
        
        # Recent high-confidence anomalies
        recent_anomalies = []
        anomalies = BehaviorAnomaly.objects.filter(
            user_filter,
            detected_at__gte=start_date,
            confidence_score__gte=70
        ).select_related('user').order_by('-detected_at')[:10]
        
        for anomaly in anomalies:
            recent_anomalies.append({
                'id': str(anomaly.id),
                'user': {
                    'username': anomaly.user.username,
                    'full_name': f"{anomaly.user.first_name} {anomaly.user.last_name}".strip()
                },
                'anomaly_type': anomaly.get_anomaly_type_display(),
                'severity': anomaly.severity,
                'confidence_score': anomaly.confidence_score,
                'title': anomaly.title,
                'description': anomaly.description,
                'detected_at': anomaly.detected_at.isoformat(),
                'is_investigated': anomaly.is_investigated
            })
        
        # Activity timeline (hourly breakdown)
        activity_timeline = []
        for hour in range(24):
            hour_start = start_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            activity_count = UserActivityLog.objects.filter(
                user_filter,
                timestamp__gte=hour_start,
                timestamp__lt=hour_end
            ).count()
            
            anomaly_count = BehaviorAnomaly.objects.filter(
                user_filter,
                detected_at__gte=hour_start,
                detected_at__lt=hour_end
            ).count()
            
            activity_timeline.append({
                'hour': hour,
                'activity_count': activity_count,
                'anomaly_count': anomaly_count
            })
        
        return Response({
            'success': True,
            'data': {
                'period_days': days,
                'statistics': {
                    'total_users': total_users,
                    'active_sessions': active_sessions,
                    'total_anomalies': total_anomalies,
                    'active_alerts': active_alerts
                },
                'anomaly_breakdown': anomaly_breakdown,
                'severity_breakdown': severity_breakdown,
                'risky_users': risky_users,
                'recent_anomalies': recent_anomalies,
                'activity_timeline': activity_timeline
            }
        })
        
    except Exception as e:
        logger.error(f"Error in behavior analytics dashboard: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch behavior analytics data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_behavior_anomalies(request):
    """
    Get behavior anomalies with filtering and pagination
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        user_id = request.GET.get('user_id')
        anomaly_type = request.GET.get('anomaly_type')
        severity = request.GET.get('severity')
        days = int(request.GET.get('days', 30))
        is_investigated = request.GET.get('is_investigated')
        
        # Build queryset
        organization = request.user.organization
        if request.user.is_superuser:
            queryset = BehaviorAnomaly.objects.all()
        else:
            queryset = BehaviorAnomaly.objects.filter(user__organization=organization)
        
        # Apply filters
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        queryset = queryset.filter(detected_at__gte=start_date)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if anomaly_type:
            queryset = queryset.filter(anomaly_type=anomaly_type)
        if severity:
            queryset = queryset.filter(severity=severity)
        if is_investigated is not None:
            queryset = queryset.filter(is_investigated=is_investigated.lower() == 'true')
        
        # Order by detection time (newest first)
        queryset = queryset.select_related('user', 'session').order_by('-detected_at')
        
        # Paginate results
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        # Serialize data
        anomalies_data = []
        for anomaly in page:
            anomalies_data.append({
                'id': str(anomaly.id),
                'user': {
                    'id': str(anomaly.user.id),
                    'username': anomaly.user.username,
                    'full_name': f"{anomaly.user.first_name} {anomaly.user.last_name}".strip(),
                    'email': anomaly.user.email
                },
                'session_id': str(anomaly.session.id) if anomaly.session else None,
                'anomaly_type': anomaly.anomaly_type,
                'anomaly_type_display': anomaly.get_anomaly_type_display(),
                'severity': anomaly.severity,
                'confidence_score': anomaly.confidence_score,
                'title': anomaly.title,
                'description': anomaly.description,
                'detection_method': anomaly.detection_method,
                'baseline_value': anomaly.baseline_value,
                'observed_value': anomaly.observed_value,
                'deviation_percentage': anomaly.deviation_percentage,
                'context_data': anomaly.context_data,
                'is_investigated': anomaly.is_investigated,
                'investigation_notes': anomaly.investigation_notes,
                'investigated_by': anomaly.investigated_by.username if anomaly.investigated_by else None,
                'investigated_at': anomaly.investigated_at.isoformat() if anomaly.investigated_at else None,
                'is_false_positive': anomaly.is_false_positive,
                'is_confirmed_threat': anomaly.is_confirmed_threat,
                'detected_at': anomaly.detected_at.isoformat()
            })
        
        return Response({
            'success': True,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': anomalies_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching behavior anomalies: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch behavior anomalies'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def investigate_anomaly(request, anomaly_id):
    """
    Mark an anomaly as investigated
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the anomaly
        try:
            if request.user.is_superuser:
                anomaly = BehaviorAnomaly.objects.get(id=anomaly_id)
            else:
                anomaly = BehaviorAnomaly.objects.get(
                    id=anomaly_id,
                    user__organization=request.user.organization
                )
        except BehaviorAnomaly.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Anomaly not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update investigation status
        investigation_notes = request.data.get('investigation_notes', '')
        is_false_positive = request.data.get('is_false_positive', False)
        is_confirmed_threat = request.data.get('is_confirmed_threat', False)
        
        anomaly.is_investigated = True
        anomaly.investigation_notes = investigation_notes
        anomaly.investigated_by = request.user
        anomaly.investigated_at = timezone.now()
        anomaly.is_false_positive = is_false_positive
        anomaly.is_confirmed_threat = is_confirmed_threat
        anomaly.save()
        
        # Acknowledge related alerts
        BehaviorAlert.objects.filter(
            anomaly=anomaly,
            is_acknowledged=False
        ).update(
            is_acknowledged=True,
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        
        logger.info(f"Anomaly {anomaly_id} investigated by {request.user.username}")
        
        return Response({
            'success': True,
            'message': 'Anomaly investigation completed'
        })
        
    except Exception as e:
        logger.error(f"Error investigating anomaly: {e}")
        return Response({
            'success': False,
            'message': 'Failed to update investigation status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_behavior_profile(request, user_id):
    """
    Get detailed behavior profile for a specific user
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the user
        try:
            if request.user.is_superuser:
                target_user = User.objects.get(id=user_id)
            else:
                target_user = User.objects.get(
                    id=user_id,
                    organization=request.user.organization
                )
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        days = int(request.GET.get('days', 30))
        
        # Get behavior analytics service
        analytics_service = UserBehaviorAnalyticsService()
        
        # Get user behavior summary
        behavior_summary = analytics_service.get_user_behavior_summary(target_user, days)
        
        # Get baseline information
        try:
            baseline = UserBehaviorBaseline.objects.get(user=target_user)
            baseline_data = {
                'avg_login_frequency_per_day': baseline.avg_login_frequency_per_day,
                'avg_session_duration_minutes': baseline.avg_session_duration_minutes,
                'common_login_hours': baseline.common_login_hours,
                'common_login_days': baseline.common_login_days,
                'avg_api_calls_per_session': baseline.avg_api_calls_per_session,
                'common_accessed_endpoints': baseline.common_accessed_endpoints,
                'baseline_period_start': baseline.baseline_period_start.isoformat(),
                'baseline_period_end': baseline.baseline_period_end.isoformat(),
                'last_updated': baseline.last_updated.isoformat()
            }
        except UserBehaviorBaseline.DoesNotExist:
            baseline_data = None
        
        # Get recent sessions
        recent_sessions = []
        sessions = UserSession.objects.filter(
            user=target_user,
            start_time__gte=timezone.now() - timedelta(days=days)
        ).order_by('-start_time')[:10]
        
        for session in sessions:
            recent_sessions.append({
                'id': str(session.id),
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration_minutes': session.duration_minutes,
                'ip_address': session.ip_address,
                'api_calls_count': session.api_calls_count,
                'is_anomalous': session.is_anomalous,
                'anomaly_score': session.anomaly_score
            })
        
        # Get recent anomalies
        recent_anomalies = []
        anomalies = BehaviorAnomaly.objects.filter(
            user=target_user,
            detected_at__gte=timezone.now() - timedelta(days=days)
        ).order_by('-detected_at')[:10]
        
        for anomaly in anomalies:
            recent_anomalies.append({
                'id': str(anomaly.id),
                'anomaly_type': anomaly.get_anomaly_type_display(),
                'severity': anomaly.severity,
                'confidence_score': anomaly.confidence_score,
                'title': anomaly.title,
                'detected_at': anomaly.detected_at.isoformat(),
                'is_investigated': anomaly.is_investigated
            })
        
        return Response({
            'success': True,
            'data': {
                'user': {
                    'id': str(target_user.id),
                    'username': target_user.username,
                    'full_name': f"{target_user.first_name} {target_user.last_name}".strip(),
                    'email': target_user.email,
                    'role': target_user.role,
                    'is_active': target_user.is_active
                },
                'behavior_summary': behavior_summary,
                'baseline': baseline_data,
                'recent_sessions': recent_sessions,
                'recent_anomalies': recent_anomalies
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching user behavior profile: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch user behavior profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_user_baseline(request, user_id):
    """
    Generate or update behavioral baseline for a user
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the user
        try:
            if request.user.is_superuser:
                target_user = User.objects.get(id=user_id)
            else:
                target_user = User.objects.get(
                    id=user_id,
                    organization=request.user.organization
                )
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate baseline
        analytics_service = UserBehaviorAnalyticsService()
        baseline = analytics_service.create_user_baseline(target_user)
        
        if baseline:
            return Response({
                'success': True,
                'message': f'Baseline generated for {target_user.username}',
                'data': {
                    'baseline_period_start': baseline.baseline_period_start.isoformat(),
                    'baseline_period_end': baseline.baseline_period_end.isoformat(),
                    'sessions_analyzed': baseline.total_sessions_analyzed
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'Insufficient data to generate baseline'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error generating user baseline: {e}")
        return Response({
            'success': False,
            'message': 'Failed to generate user baseline'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def behavior_alerts(request):
    """
    Get active behavior alerts
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Build queryset
        organization = request.user.organization
        if request.user.is_superuser:
            queryset = BehaviorAlert.objects.all()
        else:
            queryset = BehaviorAlert.objects.filter(user__organization=organization)
        
        # Apply filters
        is_acknowledged = request.GET.get('is_acknowledged')
        alert_type = request.GET.get('alert_type')
        priority = request.GET.get('priority')
        
        if is_acknowledged is not None:
            queryset = queryset.filter(is_acknowledged=is_acknowledged.lower() == 'true')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Order by creation time (newest first)
        queryset = queryset.select_related('user', 'anomaly').order_by('-created_at')
        
        # Paginate
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        # Serialize data
        alerts_data = []
        for alert in page:
            alerts_data.append({
                'id': str(alert.id),
                'user': {
                    'username': alert.user.username,
                    'full_name': f"{alert.user.first_name} {alert.user.last_name}".strip()
                },
                'alert_type': alert.alert_type,
                'priority': alert.priority,
                'title': alert.title,
                'message': alert.message,
                'recommended_actions': alert.recommended_actions,
                'is_acknowledged': alert.is_acknowledged,
                'acknowledged_by': alert.acknowledged_by.username if alert.acknowledged_by else None,
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'created_at': alert.created_at.isoformat(),
                'anomaly_id': str(alert.anomaly.id)
            })
        
        return Response({
            'success': True,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': alerts_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching behavior alerts: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch behavior alerts'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_alert(request, alert_id):
    """
    Acknowledge a behavior alert
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the alert
        try:
            if request.user.is_superuser:
                alert = BehaviorAlert.objects.get(id=alert_id)
            else:
                alert = BehaviorAlert.objects.get(
                    id=alert_id,
                    user__organization=request.user.organization
                )
        except BehaviorAlert.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Alert not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Acknowledge the alert
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        logger.info(f"Alert {alert_id} acknowledged by {request.user.username}")
        
        return Response({
            'success': True,
            'message': 'Alert acknowledged successfully'
        })
        
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        return Response({
            'success': False,
            'message': 'Failed to acknowledge alert'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_activity_logs(request):
    """
    Get system activity logs for download
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        days = int(request.GET.get('days', 7))
        log_type = request.GET.get('log_type', 'all')  # all, sessions, anomalies, alerts, activities
        user_id = request.GET.get('user_id')
        export_format = request.GET.get('format', 'json')  # json, csv
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Build organization filter
        organization = request.user.organization
        if request.user.is_superuser:
            user_filter = Q()
        else:
            user_filter = Q(user__organization=organization)
        
        # Apply user filter if specified
        if user_id:
            user_filter &= Q(user_id=user_id)
        
        logs_data = []
        
        # Collect different types of logs based on log_type
        if log_type in ['all', 'activities']:
            # User activity logs
            try:
                activities = UserActivityLog.objects.filter(
                    user_filter,
                    timestamp__gte=start_date
                ).select_related('user').order_by('-timestamp')[:1000]  # Limit to 1000 for performance
                
                for activity in activities:
                    logs_data.append({
                        'timestamp': activity.timestamp.isoformat(),
                        'log_type': 'activity',
                        'user_id': str(activity.user.id),
                        'username': activity.user.username,
                        'action_type': activity.action_type,
                        'endpoint': activity.endpoint or '',
                        'ip_address': activity.ip_address,
                        'user_agent': activity.user_agent or '',
                        'response_status': activity.response_status,
                        'request_data': activity.request_data,
                        'success': activity.success,
                        'duration_ms': activity.duration_ms,
                        'session_id': str(activity.session_id) if activity.session_id else None
                    })
            except Exception as e:
                logger.warning(f"Error fetching activity logs: {e}")
                # Continue with other log types even if activity logs fail
        
        if log_type in ['all', 'sessions']:
            # User session logs
            try:
                sessions = UserSession.objects.filter(
                    user_filter,
                    start_time__gte=start_date
                ).select_related('user').order_by('-start_time')[:500]
                
                for session in sessions:
                    logs_data.append({
                        'timestamp': session.start_time.isoformat(),
                        'log_type': 'session',
                        'user_id': str(session.user.id),
                        'username': session.user.username,
                        'session_id': str(session.id),
                        'ip_address': session.ip_address,
                        'user_agent': session.user_agent or '',
                        'duration_minutes': session.duration_minutes,
                        'end_time': session.end_time.isoformat() if session.end_time else None,
                        'is_anomalous': session.is_anomalous,
                        'anomaly_score': session.anomaly_score,
                        'api_calls_count': session.api_calls_count,
                        'endpoints_accessed': session.endpoints_accessed,
                        'data_records_accessed': session.data_records_accessed
                    })
            except Exception as e:
                logger.warning(f"Error fetching session logs: {e}")
                # Continue with other log types even if session logs fail
        
        if log_type in ['all', 'anomalies']:
            # Behavior anomaly logs
            try:
                anomalies = BehaviorAnomaly.objects.filter(
                    user_filter,
                    detected_at__gte=start_date
                ).select_related('user').order_by('-detected_at')[:500]
                
                for anomaly in anomalies:
                    logs_data.append({
                        'timestamp': anomaly.detected_at.isoformat(),
                        'log_type': 'anomaly',
                        'user_id': str(anomaly.user.id),
                        'username': anomaly.user.username,
                        'anomaly_id': str(anomaly.id),
                        'anomaly_type': anomaly.anomaly_type,
                        'severity': anomaly.severity,
                        'confidence_score': anomaly.confidence_score,
                        'title': anomaly.title,
                        'description': anomaly.description,
                        'detection_method': anomaly.detection_method,
                        'baseline_value': anomaly.baseline_value,
                        'observed_value': anomaly.observed_value,
                        'deviation_percentage': anomaly.deviation_percentage,
                        'is_investigated': anomaly.is_investigated,
                        'is_false_positive': anomaly.is_false_positive,
                        'is_confirmed_threat': anomaly.is_confirmed_threat,
                        'context_data': anomaly.context_data
                    })
            except Exception as e:
                logger.warning(f"Error fetching anomaly logs: {e}")
                # Continue with other log types even if anomaly logs fail
        
        if log_type in ['all', 'alerts']:
            # Behavior alert logs
            try:
                alerts = BehaviorAlert.objects.filter(
                    user_filter,
                    created_at__gte=start_date
                ).select_related('user', 'anomaly').order_by('-created_at')[:500]
                
                for alert in alerts:
                    logs_data.append({
                        'timestamp': alert.created_at.isoformat(),
                        'log_type': 'alert',
                        'user_id': str(alert.user.id),
                        'username': alert.user.username,
                        'alert_id': str(alert.id),
                        'alert_type': alert.alert_type,
                        'priority': alert.priority,
                        'title': alert.title,
                        'message': alert.message,
                        'is_acknowledged': alert.is_acknowledged,
                        'acknowledged_by': alert.acknowledged_by.username if alert.acknowledged_by else None,
                        'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                        'recommended_actions': alert.recommended_actions,
                        'anomaly_id': str(alert.anomaly.id)
                    })
            except Exception as e:
                logger.warning(f"Error fetching alert logs: {e}")
                # Continue even if alert logs fail
        
        # Sort all logs by timestamp (newest first)
        logs_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Return data based on requested format
        if export_format == 'csv':
            return _export_logs_as_csv(logs_data, log_type, days)
        else:
            return Response({
                'success': True,
                'data': {
                    'logs': logs_data,
                    'total_count': len(logs_data),
                    'period_days': days,
                    'log_type': log_type,
                    'generated_at': timezone.now().isoformat()
                }
            })
        
    except Exception as e:
        logger.error(f"Error fetching system activity logs: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch system activity logs'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_system_logs(request):
    """
    Download system logs as a file
    """
    try:
        # Check permissions
        if not (request.user.is_superuser or request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Insufficient permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get parameters
        days = int(request.GET.get('days', 7))
        log_type = request.GET.get('log_type', 'all')
        export_format = request.GET.get('format', 'csv')
        user_id = request.GET.get('user_id')
        
        # Get logs data (reuse the logic from system_activity_logs)
        # This is a simplified version for download
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        organization = request.user.organization
        if request.user.is_superuser:
            user_filter = Q()
        else:
            user_filter = Q(user__organization=organization)
        
        if user_id:
            user_filter &= Q(user_id=user_id)
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"system_logs_{log_type}_{days}days_{timestamp}"
        
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            
            writer = csv.writer(response)
            
            # Write CSV headers
            headers = [
                'Timestamp', 'Log Type', 'User ID', 'Username', 'Action/Event',
                'Details', 'IP Address', 'Severity', 'Status'
            ]
            writer.writerow(headers)
            
            # Write activity logs
            if log_type in ['all', 'activities']:
                activities = UserActivityLog.objects.filter(
                    user_filter,
                    timestamp__gte=start_date
                ).select_related('user').order_by('-timestamp')[:1000]
                
                for activity in activities:
                    writer.writerow([
                        activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'Activity',
                        str(activity.user.id),
                        activity.user.username,
                        activity.action_type,
                        f"{activity.endpoint} - {activity.response_status}",
                        activity.ip_address,
                        'Info',
                        'Normal'
                    ])
            
            # Write session logs
            if log_type in ['all', 'sessions']:
                sessions = UserSession.objects.filter(
                    user_filter,
                    start_time__gte=start_date
                ).select_related('user').order_by('-start_time')[:500]
                
                for session in sessions:
                    status_text = 'Anomalous' if session.is_anomalous else 'Normal'
                    writer.writerow([
                        session.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Session',
                        str(session.user.id),
                        session.user.username,
                        'User Session',
                        f"Duration: {session.duration_minutes}min, API calls: {session.api_calls_count}",
                        session.ip_address,
                        'Warning' if session.is_anomalous else 'Info',
                        status_text
                    ])
            
            # Write anomaly logs
            if log_type in ['all', 'anomalies']:
                anomalies = BehaviorAnomaly.objects.filter(
                    user_filter,
                    detected_at__gte=start_date
                ).select_related('user').order_by('-detected_at')[:500]
                
                for anomaly in anomalies:
                    writer.writerow([
                        anomaly.detected_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'Anomaly',
                        str(anomaly.user.id),
                        anomaly.user.username,
                        anomaly.anomaly_type,
                        anomaly.description,
                        '',  # IP address not directly available
                        anomaly.severity.title(),
                        'Investigated' if anomaly.is_investigated else 'Pending'
                    ])
            
            # Write alert logs
            if log_type in ['all', 'alerts']:
                alerts = BehaviorAlert.objects.filter(
                    user_filter,
                    created_at__gte=start_date
                ).select_related('user').order_by('-created_at')[:500]
                
                for alert in alerts:
                    writer.writerow([
                        alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'Alert',
                        str(alert.user.id),
                        alert.user.username,
                        alert.alert_type,
                        alert.message,
                        '',  # IP address not directly available
                        alert.priority.title(),
                        'Acknowledged' if alert.is_acknowledged else 'Active'
                    ])
            
            return response
        
        else:  # JSON format
            # Collect all logs for JSON export
            logs_data = []
            
            # Add activity logs
            if log_type in ['all', 'activities']:
                activities = UserActivityLog.objects.filter(
                    user_filter,
                    timestamp__gte=start_date
                ).select_related('user').order_by('-timestamp')[:1000]
                
                for activity in activities:
                    logs_data.append({
                        'timestamp': activity.timestamp.isoformat(),
                        'log_type': 'activity',
                        'user_id': str(activity.user.id),
                        'username': activity.user.username,
                        'action_type': activity.action_type,
                        'endpoint': activity.endpoint,
                        'ip_address': activity.ip_address,
                        'response_status': activity.response_status,
                        'duration_ms': activity.duration_ms
                    })
            
            # Add session logs
            if log_type in ['all', 'sessions']:
                sessions = UserSession.objects.filter(
                    user_filter,
                    start_time__gte=start_date
                ).select_related('user').order_by('-start_time')[:500]
                
                for session in sessions:
                    logs_data.append({
                        'timestamp': session.start_time.isoformat(),
                        'log_type': 'session',
                        'user_id': str(session.user.id),
                        'username': session.user.username,
                        'session_id': str(session.id),
                        'ip_address': session.ip_address,
                        'duration_minutes': session.duration_minutes,
                        'is_anomalous': session.is_anomalous,
                        'api_calls_count': session.api_calls_count
                    })
            
            # Add anomaly logs
            if log_type in ['all', 'anomalies']:
                anomalies = BehaviorAnomaly.objects.filter(
                    user_filter,
                    detected_at__gte=start_date
                ).select_related('user').order_by('-detected_at')[:500]
                
                for anomaly in anomalies:
                    logs_data.append({
                        'timestamp': anomaly.detected_at.isoformat(),
                        'log_type': 'anomaly',
                        'user_id': str(anomaly.user.id),
                        'username': anomaly.user.username,
                        'anomaly_type': anomaly.anomaly_type,
                        'severity': anomaly.severity,
                        'confidence_score': anomaly.confidence_score,
                        'title': anomaly.title,
                        'description': anomaly.description
                    })
            
            # Add alert logs
            if log_type in ['all', 'alerts']:
                alerts = BehaviorAlert.objects.filter(
                    user_filter,
                    created_at__gte=start_date
                ).select_related('user').order_by('-created_at')[:500]
                
                for alert in alerts:
                    logs_data.append({
                        'timestamp': alert.created_at.isoformat(),
                        'log_type': 'alert',
                        'user_id': str(alert.user.id),
                        'username': alert.user.username,
                        'alert_type': alert.alert_type,
                        'priority': alert.priority,
                        'title': alert.title,
                        'message': alert.message,
                        'is_acknowledged': alert.is_acknowledged
                    })
            
            # Sort by timestamp
            logs_data.sort(key=lambda x: x['timestamp'], reverse=True)
            
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
            
            json.dump({
                'generated_at': timezone.now().isoformat(),
                'period_days': days,
                'log_type': log_type,
                'total_records': len(logs_data),
                'logs': logs_data
            }, response, indent=2)
            
            return response
        
    except Exception as e:
        logger.error(f"Error downloading system logs: {e}")
        return Response({
            'success': False,
            'message': 'Failed to download system logs'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _export_logs_as_csv(logs_data, log_type, days):
    """
    Helper function to export logs as CSV response
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"system_logs_{log_type}_{days}days_{timestamp}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    if not logs_data:
        writer = csv.writer(response)
        writer.writerow(['No data available for the specified criteria'])
        return response
    
    writer = csv.writer(response)
    
    # Write headers based on first log entry
    if logs_data:
        headers = list(logs_data[0].keys())
        writer.writerow(headers)
        
        # Write data rows
        for log in logs_data:
            row = []
            for header in headers:
                value = log.get(header, '')
                # Convert lists/dicts to strings for CSV
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                row.append(value)
            writer.writerow(row)
    
    return response