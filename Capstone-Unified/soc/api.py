"""
SOC (Security Operations Center) API Views
REST API endpoints for SOC incident and case management
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
from django.db import transaction
from django.db.models import Q, Count
from django.core.exceptions import ValidationError
from django.http import HttpResponse

from soc.models import SOCIncident, SOCCase, SOCPlaybook, SOCIncidentActivity, SOCEvidence, SOCMetrics
from core.models.models import Organization, Indicator, AssetInventory
from core.user_management.models import CustomUser

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def incidents_list(request):
    """
    List all incidents or create new incident
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            # Get query parameters
            incident_status = request.GET.get('status')
            priority = request.GET.get('priority')
            category = request.GET.get('category')
            assigned_to = request.GET.get('assigned_to')
            search = request.GET.get('search')
            
            # Build queryset - superusers/BlueVisionAdmin can see all incidents
            if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
                queryset = SOCIncident.objects.all()
            else:
                queryset = SOCIncident.objects.filter(organization=organization)
            
            # Apply filters
            if incident_status:
                queryset = queryset.filter(status=incident_status)
            if priority:
                queryset = queryset.filter(priority=priority)
            if category:
                queryset = queryset.filter(category=category)
            if assigned_to:
                queryset = queryset.filter(assigned_to__username=assigned_to)
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(incident_id__icontains=search)
                )
            
            # Order by created date (newest first)
            queryset = queryset.select_related('organization', 'assigned_to', 'created_by').order_by('-created_at')
            
            # Paginate results
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(queryset, request)
            
            # Serialize data
            incidents_data = []
            for incident in page:
                incidents_data.append({
                    'id': str(incident.id),
                    'incident_id': incident.incident_id,
                    'title': incident.title,
                    'description': incident.description,
                    'category': incident.category,
                    'category_display': incident.get_category_display(),
                    'priority': incident.priority,
                    'priority_display': incident.get_priority_display(),
                    'severity': incident.severity,
                    'severity_display': incident.get_severity_display(),
                    'status': incident.status,
                    'status_display': incident.get_status_display(),
                    'organization': incident.organization.name,
                    'assigned_to': incident.assigned_to.username if incident.assigned_to else None,
                    'created_by': incident.created_by.username,
                    'detected_at': incident.detected_at.isoformat(),
                    'created_at': incident.created_at.isoformat(),
                    'updated_at': incident.updated_at.isoformat(),
                    'is_overdue': incident.is_overdue,
                    'sla_deadline': incident.sla_deadline.isoformat() if incident.sla_deadline else None,
                    'related_indicators_count': incident.related_indicators.count(),
                    'related_assets_count': incident.related_assets.count(),
                    'source': incident.source,
                    'tags': incident.tags,
                })
            
            return paginator.get_paginated_response({
                'success': True,
                'data': incidents_data
            })
        
        elif request.method == 'POST':
            # Create new incident
            incident_data = request.data
            
            # Validate required fields
            required_fields = ['title', 'description', 'category', 'priority', 'severity']
            for field in required_fields:
                if not incident_data.get(field):
                    return Response({
                        'success': False,
                        'message': f'Field {field} is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                with transaction.atomic():
                    # Set SLA deadline based on priority
                    sla_hours = {'low': 24, 'medium': 8, 'high': 4, 'critical': 1}
                    sla_deadline = timezone.now() + timedelta(hours=sla_hours.get(incident_data['priority'], 8))
                    
                    # Create incident
                    incident = SOCIncident.objects.create(
                        title=incident_data['title'],
                        description=incident_data['description'],
                        category=incident_data['category'],
                        priority=incident_data['priority'],
                        severity=incident_data['severity'],
                        organization=organization,
                        created_by=request.user,
                        source=incident_data.get('source', 'manual'),
                        sla_deadline=sla_deadline,
                        tags=incident_data.get('tags', []),
                        metadata=incident_data.get('metadata', {})
                    )
                    
                    # Add related indicators if provided
                    related_indicators = incident_data.get('related_indicators', [])
                    if related_indicators:
                        try:
                            indicators = Indicator.objects.filter(id__in=related_indicators)
                            incident.related_indicators.add(*indicators)
                            logger.info(f"Added {indicators.count()} indicators to incident {incident.incident_id}")
                        except Exception as e:
                            logger.warning(f"Error adding indicators to incident: {str(e)}")
                    
                    # Log activity
                    activity_details = {
                        'priority': incident_data['priority'], 
                        'category': incident_data['category'],
                        'related_indicators_count': len(related_indicators)
                    }
                    SOCIncidentActivity.objects.create(
                        incident=incident,
                        user=request.user,
                        activity_type='created',
                        description=f"Incident created by {request.user.username}" + 
                                   (f" with {len(related_indicators)} related IOCs" if related_indicators else ""),
                        details=activity_details
                    )
                    
                    logger.info(f"Created incident {incident.incident_id} for organization {organization.name}")
                    
                    return Response({
                        'success': True,
                        'message': 'Incident created successfully',
                        'data': {
                            'id': str(incident.id),
                            'incident_id': incident.incident_id,
                            'title': incident.title,
                            'status': incident.status,
                            'priority': incident.priority,
                            'sla_deadline': incident.sla_deadline.isoformat()
                        }
                    }, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                return Response({
                    'success': False,
                    'message': f'Validation error: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in incidents_list: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to process incidents request'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def incident_detail(request, incident_id):
    """
    Get, update, or delete specific incident
    """
    try:
        organization = request.user.organization
        if not organization and request.user.role != 'BlueVisionAdmin':
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get incident
        try:
            if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
                incident = SOCIncident.objects.get(id=incident_id)
            else:
                incident = SOCIncident.objects.get(id=incident_id, organization=organization)
        except SOCIncident.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Incident not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            # Get incident details with related data
            related_indicators = [
                {
                    'id': indicator.id,
                    'type': indicator.type,
                    'value': indicator.value[:100] + '...' if len(indicator.value) > 100 else indicator.value,
                    'stix_id': indicator.stix_id
                }
                for indicator in incident.related_indicators.all()[:10]
            ]
            
            related_assets = [
                {
                    'id': str(asset.id),
                    'name': asset.name,
                    'asset_type': asset.get_asset_type_display(),
                    'criticality': asset.get_criticality_display()
                }
                for asset in incident.related_assets.all()[:10]
            ]
            
            # Get recent activities
            activities = [
                {
                    'id': str(activity.id),
                    'activity_type': activity.get_activity_type_display(),
                    'description': activity.description,
                    'user': activity.user.username,
                    'created_at': activity.created_at.isoformat()
                }
                for activity in incident.activities.all()[:20]
            ]
            
            incident_data = {
                'id': str(incident.id),
                'incident_id': incident.incident_id,
                'title': incident.title,
                'description': incident.description,
                'category': incident.category,
                'category_display': incident.get_category_display(),
                'priority': incident.priority,
                'priority_display': incident.get_priority_display(),
                'severity': incident.severity,
                'severity_display': incident.get_severity_display(),
                'status': incident.status,
                'status_display': incident.get_status_display(),
                'organization': incident.organization.name,
                'assigned_to': incident.assigned_to.username if incident.assigned_to else None,
                'created_by': incident.created_by.username,
                'detected_at': incident.detected_at.isoformat(),
                'assigned_at': incident.assigned_at.isoformat() if incident.assigned_at else None,
                'resolved_at': incident.resolved_at.isoformat() if incident.resolved_at else None,
                'closed_at': incident.closed_at.isoformat() if incident.closed_at else None,
                'created_at': incident.created_at.isoformat(),
                'updated_at': incident.updated_at.isoformat(),
                'is_overdue': incident.is_overdue,
                'sla_deadline': incident.sla_deadline.isoformat() if incident.sla_deadline else None,
                'source': incident.source,
                'external_ticket_id': incident.external_ticket_id,
                'tags': incident.tags,
                'metadata': incident.metadata,
                'related_indicators': related_indicators,
                'related_assets': related_assets,
                'activities': activities
            }

            return Response({
                'success': True,
                'data': incident_data
            })

        elif request.method == 'PUT':
            # Update incident
            incident_data = request.data
            old_status = incident.status
            
            try:
                with transaction.atomic():
                    # Update fields
                    if 'title' in incident_data:
                        incident.title = incident_data['title']
                    if 'description' in incident_data:
                        incident.description = incident_data['description']
                    if 'priority' in incident_data and incident_data['priority'] != incident.priority:
                        old_priority = incident.priority
                        incident.priority = incident_data['priority']
                        # Log priority change
                        SOCIncidentActivity.objects.create(
                            incident=incident,
                            user=request.user,
                            activity_type='priority_change',
                            description=f"Priority changed from {old_priority} to {incident_data['priority']}",
                            details={'old_priority': old_priority, 'new_priority': incident_data['priority']}
                        )
                    if 'status' in incident_data and incident_data['status'] != incident.status:
                        incident.status = incident_data['status']
                        # Update timestamps based on status
                        if incident_data['status'] == 'resolved' and not incident.resolved_at:
                            incident.resolved_at = timezone.now()
                        elif incident_data['status'] == 'closed' and not incident.closed_at:
                            incident.closed_at = timezone.now()
                        # Log status change
                        SOCIncidentActivity.objects.create(
                            incident=incident,
                            user=request.user,
                            activity_type='status_change',
                            description=f"Status changed from {old_status} to {incident_data['status']}",
                            details={'old_status': old_status, 'new_status': incident_data['status']}
                        )
                    if 'assigned_to' in incident_data:
                        if incident_data['assigned_to']:
                            try:
                                user = CustomUser.objects.get(username=incident_data['assigned_to'])
                                incident.assign_to(user)
                            except CustomUser.DoesNotExist:
                                return Response({
                                    'success': False,
                                    'message': 'Assigned user not found'
                                }, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            incident.assigned_to = None
                    if 'tags' in incident_data:
                        incident.tags = incident_data['tags']
                    
                    incident.save()
                    
                    logger.info(f"Updated incident {incident.incident_id} by {request.user.username}")
                    
                    return Response({
                        'success': True,
                        'message': 'Incident updated successfully'
                    })
            
            except ValidationError as e:
                return Response({
                    'success': False,
                    'message': f'Validation error: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            # Hard delete incident (actual deletion)
            incident_id_str = incident.incident_id
            
            # Log activity before deletion
            SOCIncidentActivity.objects.create(
                incident=incident,
                user=request.user,
                activity_type='deleted',
                description=f"Incident permanently deleted by {request.user.username}",
                details={'reason': 'hard_delete', 'deleted_at': timezone.now().isoformat()}
            )
            
            logger.info(f"Hard deleting incident {incident_id_str} by {request.user.username}")
            
            # Actually delete the incident
            incident.delete()
            
            return Response({
                'success': True,
                'message': 'Incident deleted permanently'
            })

    except Exception as e:
        logger.error(f"Error in incident_detail: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to process incident request'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def soc_dashboard(request):
    """
    SOC Dashboard metrics and KPIs
    """
    try:
        organization = request.user.organization
        if not organization and request.user.role != 'BlueVisionAdmin':
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Build queryset based on user role
        if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
            incidents_qs = SOCIncident.objects.all()
        else:
            incidents_qs = SOCIncident.objects.filter(organization=organization)

        # Get time ranges
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Basic metrics
        total_incidents = incidents_qs.count()
        open_incidents = incidents_qs.filter(status__in=['new', 'assigned', 'in_progress']).count()
        critical_incidents = incidents_qs.filter(priority='critical', status__in=['new', 'assigned', 'in_progress']).count()
        overdue_incidents = incidents_qs.filter(sla_deadline__lt=now, status__in=['new', 'assigned', 'in_progress']).count()
        
        # Recent activity
        incidents_today = incidents_qs.filter(created_at__date=today).count()
        incidents_week = incidents_qs.filter(created_at__gte=week_ago).count()
        incidents_month = incidents_qs.filter(created_at__gte=month_ago).count()
        
        resolved_today = incidents_qs.filter(resolved_at__date=today).count()
        resolved_week = incidents_qs.filter(resolved_at__gte=week_ago).count()

        # Status breakdown
        status_breakdown = incidents_qs.values('status').annotate(count=Count('status')).order_by('status')
        status_data = {item['status']: item['count'] for item in status_breakdown}

        # Priority breakdown
        priority_breakdown = incidents_qs.values('priority').annotate(count=Count('priority')).order_by('priority')
        priority_data = {item['priority']: item['count'] for item in priority_breakdown}

        # Category breakdown
        category_breakdown = incidents_qs.values('category').annotate(count=Count('category')).order_by('category')
        category_data = {item['category']: item['count'] for item in category_breakdown}

        # Recent incidents for dashboard
        recent_incidents = []
        for incident in incidents_qs.order_by('-created_at')[:10]:
            recent_incidents.append({
                'id': str(incident.id),
                'incident_id': incident.incident_id,
                'title': incident.title,
                'priority': incident.priority,
                'status': incident.status,
                'created_at': incident.created_at.isoformat(),
                'is_overdue': incident.is_overdue
            })

        dashboard_data = {
            'metrics': {
                'total_incidents': total_incidents,
                'open_incidents': open_incidents,
                'critical_incidents': critical_incidents,
                'overdue_incidents': overdue_incidents,
                'incidents_today': incidents_today,
                'incidents_week': incidents_week,
                'incidents_month': incidents_month,
                'resolved_today': resolved_today,
                'resolved_week': resolved_week,
            },
            'breakdowns': {
                'status': status_data,
                'priority': priority_data,
                'category': category_data,
            },
            'recent_incidents': recent_incidents,
            'organization': organization.name if organization else 'All Organizations',
            'last_updated': now.isoformat()
        }

        return Response({
            'success': True,
            'data': dashboard_data
        })

    except Exception as e:
        logger.error(f"Error in soc_dashboard: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get SOC dashboard data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def incident_assign(request, incident_id):
    """
    Assign incident to a user
    """
    try:
        organization = request.user.organization
        if not organization and request.user.role != 'BlueVisionAdmin':
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get incident
        try:
            if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
                incident = SOCIncident.objects.get(id=incident_id)
            else:
                incident = SOCIncident.objects.get(id=incident_id, organization=organization)
        except SOCIncident.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Incident not found'
            }, status=status.HTTP_404_NOT_FOUND)

        username = request.data.get('username')
        if not username:
            return Response({
                'success': False,
                'message': 'Username is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(username=username)
            incident.assign_to(user)
            
            # Log activity
            SOCIncidentActivity.objects.create(
                incident=incident,
                user=request.user,
                activity_type='assigned',
                description=f"Incident assigned to {user.username} by {request.user.username}",
                details={'assigned_to': user.username}
            )
            
            logger.info(f"Assigned incident {incident.incident_id} to {user.username}")
            
            return Response({
                'success': True,
                'message': f'Incident assigned to {user.username}'
            })
            
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error in incident_assign: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to assign incident'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def incident_add_comment(request, incident_id):
    """
    Add comment/activity to incident
    """
    try:
        organization = request.user.organization
        if not organization and request.user.role != 'BlueVisionAdmin':
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get incident
        try:
            if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
                incident = SOCIncident.objects.get(id=incident_id)
            else:
                incident = SOCIncident.objects.get(id=incident_id, organization=organization)
        except SOCIncident.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Incident not found'
            }, status=status.HTTP_404_NOT_FOUND)

        comment = request.data.get('comment')
        if not comment:
            return Response({
                'success': False,
                'message': 'Comment is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create activity
        activity = SOCIncidentActivity.objects.create(
            incident=incident,
            user=request.user,
            activity_type='comment',
            description=comment,
            details={'comment_type': 'user_comment'}
        )
        
        logger.info(f"Added comment to incident {incident.incident_id} by {request.user.username}")
        
        return Response({
            'success': True,
            'message': 'Comment added successfully',
            'data': {
                'activity_id': str(activity.id),
                'created_at': activity.created_at.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error in incident_add_comment: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to add comment'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incidents_export(request):
    """
    Export incidents to CSV or JSON format
    """
    try:
        organization = request.user.organization
        if not organization and request.user.role != 'BlueVisionAdmin':
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get export parameters
        export_format = request.GET.get('format', 'csv').lower()
        days = int(request.GET.get('days', 30))
        status_filter = request.GET.get('status')
        priority_filter = request.GET.get('priority')
        
        # Build queryset - superusers/BlueVisionAdmin can export all incidents
        if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
            queryset = SOCIncident.objects.all()
        else:
            queryset = SOCIncident.objects.filter(organization=organization)
            
        # Filter by date range
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=start_date)
        
        # Apply additional filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
            
        # Order by created date (newest first)
        queryset = queryset.select_related('organization', 'assigned_to', 'created_by').order_by('-created_at')
        
        # Prepare incident data
        incidents_data = []
        for incident in queryset:
            incidents_data.append({
                'incident_id': incident.incident_id,
                'title': incident.title,
                'description': incident.description,
                'category': incident.get_category_display(),
                'priority': incident.get_priority_display(),
                'severity': incident.get_severity_display(),
                'status': incident.get_status_display(),
                'organization': incident.organization.name,
                'assigned_to': incident.assigned_to.username if incident.assigned_to else 'Unassigned',
                'created_by': incident.created_by.username,
                'detected_at': incident.detected_at.isoformat(),
                'created_at': incident.created_at.isoformat(),
                'updated_at': incident.updated_at.isoformat(),
                'resolved_at': incident.resolved_at.isoformat() if incident.resolved_at else '',
                'closed_at': incident.closed_at.isoformat() if incident.closed_at else '',
                'is_overdue': 'Yes' if incident.is_overdue else 'No',
                'sla_deadline': incident.sla_deadline.isoformat() if incident.sla_deadline else '',
                'source': incident.source,
                'external_ticket_id': incident.external_ticket_id or '',
                'tags': ', '.join(incident.tags) if incident.tags else '',
                'related_indicators_count': incident.related_indicators.count(),
                'related_assets_count': incident.related_assets.count()
            })
        
        # Generate filename
        org_name = organization.name.replace(' ', '_') if organization else 'All_Organizations'
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'soc_incidents_{org_name}_{timestamp}'
        
        if export_format == 'csv':
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            
            if incidents_data:
                writer = csv.DictWriter(response, fieldnames=incidents_data[0].keys())
                writer.writeheader()
                writer.writerows(incidents_data)
            else:
                writer = csv.writer(response)
                writer.writerow(['No incidents found for the specified criteria'])
                
            return response
            
        elif export_format == 'json':
            # Create JSON response
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
            
            export_data = {
                'export_metadata': {
                    'export_date': timezone.now().isoformat(),
                    'organization': organization.name if organization else 'All Organizations',
                    'days_range': days,
                    'total_incidents': len(incidents_data),
                    'filters_applied': {
                        'status': status_filter,
                        'priority': priority_filter
                    }
                },
                'incidents': incidents_data
            }
            
            response.write(json.dumps(export_data, indent=2))
            return response
        
        else:
            return Response({
                'success': False,
                'message': 'Unsupported export format. Use "csv" or "json".'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except ValueError:
        return Response({
            'success': False,
            'message': 'Invalid days parameter. Must be a number.'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in incidents_export: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to export incidents'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def threat_map(request):
    """
    Get threat map data for SOC visualization
    """
    try:
        # Generate sample threat map data
        # In a real implementation, this would pull from threat intelligence feeds
        threat_data = {
            'global_threats': {
                'malware_families': [
                    {'name': 'Emotet', 'severity': 'high', 'active_campaigns': 12, 'regions': ['NA', 'EU']},
                    {'name': 'Ryuk', 'severity': 'critical', 'active_campaigns': 8, 'regions': ['NA', 'AS']},
                    {'name': 'TrickBot', 'severity': 'medium', 'active_campaigns': 15, 'regions': ['EU', 'AS']}
                ],
                'attack_vectors': [
                    {'vector': 'Phishing', 'count': 245, 'trend': 'increasing'},
                    {'vector': 'Malicious Downloads', 'count': 156, 'trend': 'stable'},
                    {'vector': 'Credential Stuffing', 'count': 89, 'trend': 'decreasing'}
                ],
                'targeted_industries': [
                    {'industry': 'Healthcare', 'threat_level': 'high', 'incidents': 34},
                    {'industry': 'Financial', 'threat_level': 'critical', 'incidents': 28},
                    {'industry': 'Education', 'threat_level': 'medium', 'incidents': 19}
                ]
            },
            'last_updated': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'data': threat_data
        })
        
    except Exception as e:
        logger.error(f"Error in threat_map: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get threat map data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_health(request):
    """
    Get system health metrics for SOC monitoring
    """
    try:
        import random
        
        # Get simulated system metrics
        cpu_usage = random.randint(15, 85)
        memory_usage = random.randint(25, 75)
        
        # Count active SOC incidents
        if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
            active_alerts = SOCIncident.objects.filter(
                status__in=['new', 'assigned', 'in_progress'],
                priority__in=['high', 'critical']
            ).count()
            connected_users = CustomUser.objects.filter(last_login__gte=timezone.now() - timedelta(hours=1)).count()
        else:
            org = request.user.organization
            active_alerts = SOCIncident.objects.filter(
                organization=org,
                status__in=['new', 'assigned', 'in_progress'],
                priority__in=['high', 'critical']
            ).count() if org else 0
            connected_users = CustomUser.objects.filter(
                organization=org,
                last_login__gte=timezone.now() - timedelta(hours=1)
            ).count() if org else 1
        
        health_data = {
            'cpu_usage': round(cpu_usage, 1),
            'memory_usage': round(memory_usage, 1),
            'active_alerts': active_alerts,
            'connected_users': connected_users,
            'services_status': {
                'threat_feeds': 'online',
                'incident_management': 'online',
                'user_authentication': 'online',
                'database': 'online'
            },
            'last_updated': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'data': health_data
        })
        
    except Exception as e:
        logger.error(f"Error in system_health: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get system health data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_threats(request):
    """
    Get top threats based on recent incident data
    """
    try:
        organization = request.user.organization
        
        # Build queryset based on user role
        if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
            incidents_qs = SOCIncident.objects.all()
        else:
            incidents_qs = SOCIncident.objects.filter(organization=organization) if organization else SOCIncident.objects.none()
        
        # Get recent incidents (last 30 days)
        recent_incidents = incidents_qs.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        # Aggregate threat data
        threat_categories = {}
        for incident in recent_incidents:
            category = incident.category
            if category not in threat_categories:
                threat_categories[category] = {
                    'name': incident.get_category_display(),
                    'category': category,
                    'incidents': 0,
                    'severity': 'low'
                }
            threat_categories[category]['incidents'] += 1
            
            # Set highest severity seen
            if incident.priority == 'critical':
                threat_categories[category]['severity'] = 'critical'
            elif incident.priority == 'high' and threat_categories[category]['severity'] != 'critical':
                threat_categories[category]['severity'] = 'high'
            elif incident.priority == 'medium' and threat_categories[category]['severity'] not in ['critical', 'high']:
                threat_categories[category]['severity'] = 'medium'
        
        # Sort by incident count and return top 10
        top_threats = sorted(
            threat_categories.values(),
            key=lambda x: x['incidents'],
            reverse=True
        )[:10]
        
        return Response({
            'success': True,
            'threats': top_threats
        })
        
    except Exception as e:
        logger.error(f"Error in top_threats: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get top threats data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mitre_tactics(request):
    """
    Get MITRE ATT&CK tactics data for SOC analysis
    """
    try:
        # Simulated MITRE tactics data
        tactics_data = [
            {
                'name': 'Initial Access',
                'description': 'Techniques used to gain an initial foothold within a network',
                'technique_count': 9,
                'detection_count': 15,
                'mitre_id': 'TA0001'
            },
            {
                'name': 'Execution',
                'description': 'Techniques that result in adversary-controlled code running on a local or remote system',
                'technique_count': 12,
                'detection_count': 8,
                'mitre_id': 'TA0002'
            },
            {
                'name': 'Persistence',
                'description': 'Techniques that adversaries use to keep access to systems across restarts',
                'technique_count': 19,
                'detection_count': 12,
                'mitre_id': 'TA0003'
            },
            {
                'name': 'Privilege Escalation',
                'description': 'Techniques used to gain higher-level permissions on a system or network',
                'technique_count': 13,
                'detection_count': 6,
                'mitre_id': 'TA0004'
            },
            {
                'name': 'Defense Evasion',
                'description': 'Techniques that adversaries use to avoid detection throughout their compromise',
                'technique_count': 40,
                'detection_count': 22,
                'mitre_id': 'TA0005'
            },
            {
                'name': 'Credential Access',
                'description': 'Techniques for stealing credentials like account names and passwords',
                'technique_count': 15,
                'detection_count': 9,
                'mitre_id': 'TA0006'
            }
        ]
        
        return Response({
            'success': True,
            'tactics': tactics_data
        })
        
    except Exception as e:
        logger.error(f"Error in mitre_tactics: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get MITRE tactics data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def threat_intelligence(request):
    """
    Get enhanced threat intelligence summary for SOC dashboard with IOC integration
    """
    try:
        from core.models.models import ThreatFeed, Indicator, TTPData
        from django.db.models import Count, Q
        
        organization = request.user.organization
        
        # Get threat intelligence metrics
        active_feeds = ThreatFeed.objects.filter(is_active=True).count()
        
        # Filter IOCs based on user organization and trust relationships
        if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
            indicators_qs = Indicator.objects.all()
        else:
            # Get indicators accessible to user's organization through trust relationships
            if organization:
                indicators_qs = Indicator.objects.filter(
                    Q(threat_feed__owner=organization) |
                    Q(threat_feed__is_public=True) |
                    Q(threat_feed__isnull=True)  # Public indicators
                ).distinct()
            else:
                indicators_qs = Indicator.objects.none()
        
        total_iocs = indicators_qs.count()
        
        # Recent IOC updates (last 24 hours)
        recent_indicators = indicators_qs.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # High confidence IOCs
        high_confidence_iocs = indicators_qs.filter(confidence__gte=80).count()
        
        # IOC type breakdown
        ioc_types = indicators_qs.values('type').annotate(count=Count('type')).order_by('-count')[:5]
        
        # Recent high-priority IOCs
        recent_critical_iocs = []
        for ioc in indicators_qs.filter(
            confidence__gte=85,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:10]:
            recent_critical_iocs.append({
                'id': str(ioc.id),
                'type': ioc.type,
                'value': ioc.value[:50] + '...' if len(ioc.value) > 50 else ioc.value,
                'confidence': ioc.confidence,
                'source': ioc.threat_feed.name if ioc.threat_feed else 'Manual Entry',
                'created_at': ioc.created_at.isoformat()
            })
        
        # TTP correlation
        try:
            ttps_count = TTPData.objects.count()
            recent_ttps = TTPData.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        except Exception as e:
            logger.error(f"Error fetching TTP data: {str(e)}")
            ttps_count = 0
            recent_ttps = 0
        
        # Feed status summary
        feed_status = []
        try:
            for feed in ThreatFeed.objects.filter(is_active=True)[:5]:
                try:
                    indicator_count = feed.indicators.count()
                except Exception as e:
                    logger.warning(f"Error counting indicators for feed {feed.name}: {str(e)}")
                    indicator_count = 0
                    
                feed_status.append({
                    'name': feed.name,
                    'status': feed.consumption_status,
                    'last_update': feed.last_sync.isoformat() if feed.last_sync else None,
                    'indicator_count': indicator_count
                })
        except Exception as e:
            logger.error(f"Error fetching feed status: {str(e)}")
            feed_status = []
        
        # Threat trends analysis
        week_ago = timezone.now() - timedelta(days=7)
        current_week_iocs = indicators_qs.filter(created_at__gte=week_ago).count()
        previous_week_iocs = indicators_qs.filter(
            created_at__gte=week_ago - timedelta(days=7),
            created_at__lt=week_ago
        ).count()
        
        ioc_trend = 'stable'
        ioc_change = 0
        if previous_week_iocs > 0:
            ioc_change = ((current_week_iocs - previous_week_iocs) / previous_week_iocs) * 100
            if ioc_change > 10:
                ioc_trend = 'increasing'
            elif ioc_change < -10:
                ioc_trend = 'decreasing'
        
        intel_data = {
            'feeds_active': active_feeds,
            'iocs_count': total_iocs,
            'recent_iocs_24h': recent_indicators,
            'high_confidence_iocs': high_confidence_iocs,
            'ttps_count': ttps_count,
            'recent_ttps': recent_ttps,
            'confidence': 'High' if high_confidence_iocs > total_iocs * 0.7 else 'Medium',
            'last_update': timezone.now().isoformat(),
            'threat_level': 'High' if recent_indicators > 50 else 'Medium' if recent_indicators > 20 else 'Low',
            'ioc_trend': {
                'direction': ioc_trend,
                'change_percentage': round(ioc_change, 1),
                'current_week': current_week_iocs,
                'previous_week': previous_week_iocs
            },
            'ioc_types_breakdown': [
                {
                    'type': item['type'],
                    'count': item['count'],
                    'percentage': round((item['count'] / total_iocs) * 100, 1) if total_iocs > 0 else 0
                }
                for item in ioc_types
            ],
            'recent_critical_iocs': recent_critical_iocs,
            'feed_status': feed_status,
            'trending_threats': [
                {
                    'name': 'Malware IOCs',
                    'count': indicators_qs.filter(type='file_hash').count(),
                    'trend': 'increasing' if current_week_iocs > previous_week_iocs else 'stable'
                },
                {
                    'name': 'Network IOCs',
                    'count': indicators_qs.filter(type__in=['ip', 'domain', 'url']).count(),
                    'trend': 'increasing'
                },
                {
                    'name': 'Email Threats',
                    'count': indicators_qs.filter(type='email').count(),
                    'trend': 'stable'
                }
            ]
        }
        
        return Response({
            'success': True,
            'data': intel_data
        })
        
    except Exception as e:
        logger.error(f"Error in threat_intelligence: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get threat intelligence data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_ioc_alerts(request):
    """
    Get live IOC-based alerts for real-time SOC monitoring
    """
    try:
        from core.models.models import Indicator, CustomAlert, AssetInventory
        from django.db.models import Q
        
        organization = request.user.organization
        
        # Filter based on user organization
        if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
            alerts_qs = CustomAlert.objects.all()
        else:
            alerts_qs = CustomAlert.objects.filter(organization=organization) if organization else CustomAlert.objects.none()
        
        # Get recent IOC-based alerts (last 24 hours)
        recent_alerts = alerts_qs.filter(
            created_at__gte=timezone.now() - timedelta(hours=24),
            status__in=['new', 'acknowledged', 'investigating']
        ).order_by('-created_at')[:20]
        
        live_alerts = []
        for alert in recent_alerts:
            # Get related IOCs
            related_iocs = []
            for indicator in alert.source_indicators.all()[:5]:
                related_iocs.append({
                    'type': indicator.type,
                    'value': indicator.value[:30] + '...' if len(indicator.value) > 30 else indicator.value,
                    'confidence': indicator.confidence
                })
            
            # Get matched assets
            matched_assets = []
            for asset in alert.matched_assets.all()[:3]:
                matched_assets.append({
                    'name': asset.name,
                    'type': asset.asset_type,
                    'criticality': asset.criticality
                })
            
            live_alerts.append({
                'id': str(alert.id),
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity,
                'alert_type': alert.alert_type,
                'created_at': alert.created_at.isoformat(),
                'related_iocs': related_iocs,
                'matched_assets': matched_assets,
                'organization': alert.organization.name if alert.organization else 'System',
                'is_acknowledged': alert.status == 'acknowledged',
                'threat_score': getattr(alert, 'confidence_score', 0)
            })
        
        # IOC correlation statistics
        total_active_alerts = alerts_qs.filter(status__in=['new', 'acknowledged', 'investigating']).count()
        high_severity_alerts = alerts_qs.filter(
            severity__in=['high', 'critical'],
            status__in=['new', 'acknowledged', 'investigating']
        ).count()
        
        # Recent IOC matches
        recent_ioc_matches = Indicator.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1),
            confidence__gte=70
        ).count()
        
        response_data = {
            'live_alerts': live_alerts,
            'statistics': {
                'total_active_alerts': total_active_alerts,
                'high_severity_alerts': high_severity_alerts,
                'recent_ioc_matches': recent_ioc_matches,
                'alert_rate_24h': len(live_alerts)
            },
            'last_updated': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"Error in live_ioc_alerts: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get live IOC alerts'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ioc_incident_correlation(request):
    """
    Get IOC-incident correlation data for SOC analysis
    """
    try:
        from core.models.models import Indicator
        
        organization = request.user.organization
        
        # Build queryset based on user role
        if request.user.is_superuser or request.user.role == 'BlueVisionAdmin':
            incidents_qs = SOCIncident.objects.all()
        else:
            incidents_qs = SOCIncident.objects.filter(organization=organization) if organization else SOCIncident.objects.none()
        
        # Get incidents with IOC correlations (last 30 days)
        recent_incidents = incidents_qs.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).prefetch_related('related_indicators')
        
        correlation_data = []
        for incident in recent_incidents:
            if incident.related_indicators.exists():
                ioc_details = []
                for ioc in incident.related_indicators.all()[:10]:
                    ioc_details.append({
                        'type': ioc.type,
                        'value': ioc.value[:40] + '...' if len(ioc.value) > 40 else ioc.value,
                        'confidence': ioc.confidence,
                        'source': ioc.threat_feed.name if ioc.threat_feed else 'Manual'
                    })
                
                correlation_data.append({
                    'incident_id': incident.incident_id,
                    'title': incident.title,
                    'priority': incident.priority,
                    'status': incident.status,
                    'created_at': incident.created_at.isoformat(),
                    'ioc_count': incident.related_indicators.count(),
                    'related_iocs': ioc_details
                })
        
        # IOC effectiveness metrics
        total_incidents_with_iocs = len(correlation_data)
        total_incidents = recent_incidents.count()
        correlation_rate = (total_incidents_with_iocs / total_incidents * 100) if total_incidents > 0 else 0
        
        # Top IOC types in incidents
        ioc_type_stats = {}
        for incident in recent_incidents:
            for ioc in incident.related_indicators.all():
                ioc_type = ioc.type
                if ioc_type not in ioc_type_stats:
                    ioc_type_stats[ioc_type] = {'count': 0, 'incidents': set()}
                ioc_type_stats[ioc_type]['count'] += 1
                ioc_type_stats[ioc_type]['incidents'].add(incident.id)
        
        top_ioc_types = [
            {
                'type': ioc_type,
                'count': stats['count'],
                'incidents_affected': len(stats['incidents'])
            }
            for ioc_type, stats in sorted(ioc_type_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        ]
        
        return Response({
            'success': True,
            'data': {
                'correlations': correlation_data,
                'statistics': {
                    'total_incidents': total_incidents,
                    'incidents_with_iocs': total_incidents_with_iocs,
                    'correlation_rate': round(correlation_rate, 1),
                    'top_ioc_types': top_ioc_types
                },
                'last_updated': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in ioc_incident_correlation: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get IOC-incident correlation data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)