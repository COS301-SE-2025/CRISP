"""
Asset Inventory API for CRISP WOW Factor #1
Provides REST API endpoints for managing asset inventories and custom alerts.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models.models import AssetInventory, CustomAlert, Organization, Indicator
from core.services.asset_alert_service import AssetBasedAlertService
from core.serializers.threat_feed_serializer import ThreatFeedSerializer

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def asset_inventory_list(request):
    """
    List organization's asset inventory or create new asset.
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
            asset_type = request.GET.get('asset_type')
            criticality = request.GET.get('criticality')
            alert_enabled = request.GET.get('alert_enabled')

            # Build queryset
            queryset = AssetInventory.objects.filter(
                organization=organization
            ).select_related('organization', 'created_by').order_by('-created_at')

            # Apply filters
            if asset_type:
                queryset = queryset.filter(asset_type=asset_type)
            if criticality:
                queryset = queryset.filter(criticality=criticality)
            if alert_enabled is not None:
                queryset = queryset.filter(alert_enabled=alert_enabled.lower() == 'true')

            # Paginate results
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(queryset, request)

            # Serialize data
            assets_data = []
            for asset in page:
                assets_data.append({
                    'id': str(asset.id),
                    'name': asset.name,
                    'asset_type': asset.asset_type,
                    'asset_type_display': asset.get_asset_type_display(),
                    'asset_value': asset.asset_value,
                    'description': asset.description,
                    'criticality': asset.criticality,
                    'criticality_display': asset.get_criticality_display(),
                    'environment': asset.environment,
                    'alert_enabled': asset.alert_enabled,
                    'alert_channels': asset.alert_channels,
                    'created_by': asset.created_by.username,
                    'created_at': asset.created_at.isoformat(),
                    'updated_at': asset.updated_at.isoformat(),
                    'last_seen': asset.last_seen.isoformat() if asset.last_seen else None,
                    'fingerprints': asset.fingerprints,
                    'metadata': asset.metadata,
                    'alert_count': asset.alerts.count()
                })

            return paginator.get_paginated_response({
                'success': True,
                'data': assets_data
            })

        elif request.method == 'POST':
            # Create new asset
            asset_data = request.data

            # Validate required fields
            required_fields = ['name', 'asset_type', 'asset_value']
            for field in required_fields:
                if not asset_data.get(field):
                    return Response({
                        'success': False,
                        'message': f'Field {field} is required'
                    }, status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    # Create asset
                    asset = AssetInventory.objects.create(
                        name=asset_data['name'],
                        asset_type=asset_data['asset_type'],
                        asset_value=asset_data['asset_value'],
                        description=asset_data.get('description', ''),
                        criticality=asset_data.get('criticality', 'medium'),
                        environment=asset_data.get('environment', 'production'),
                        organization=organization,
                        created_by=request.user,
                        alert_enabled=asset_data.get('alert_enabled', True),
                        alert_channels=asset_data.get('alert_channels', []),
                        metadata=asset_data.get('metadata', {})
                    )

                    # Generate fingerprints for threat correlation
                    asset.generate_fingerprints()

                    logger.info(f"Created asset {asset.name} for organization {organization.name}")

                    return Response({
                        'success': True,
                        'message': 'Asset created successfully',
                        'data': {
                            'id': str(asset.id),
                            'name': asset.name,
                            'asset_type': asset.asset_type,
                            'asset_value': asset.asset_value,
                            'criticality': asset.criticality,
                            'alert_enabled': asset.alert_enabled
                        }
                    }, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response({
                    'success': False,
                    'message': f'Validation error: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error in asset_inventory_list: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to process asset inventory request'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def asset_inventory_detail(request, asset_id):
    """
    Get, update, or delete specific asset.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get asset
        try:
            asset = AssetInventory.objects.get(
                id=asset_id,
                organization=organization
            )
        except AssetInventory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Asset not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            # Get asset details with related alerts
            recent_alerts = asset.alerts.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).order_by('-detected_at')[:10]

            asset_data = {
                'id': str(asset.id),
                'name': asset.name,
                'asset_type': asset.asset_type,
                'asset_type_display': asset.get_asset_type_display(),
                'asset_value': asset.asset_value,
                'description': asset.description,
                'criticality': asset.criticality,
                'criticality_display': asset.get_criticality_display(),
                'environment': asset.environment,
                'alert_enabled': asset.alert_enabled,
                'alert_channels': asset.alert_channels,
                'created_by': asset.created_by.username,
                'created_at': asset.created_at.isoformat(),
                'updated_at': asset.updated_at.isoformat(),
                'last_seen': asset.last_seen.isoformat() if asset.last_seen else None,
                'fingerprints': asset.fingerprints,
                'metadata': asset.metadata,
                'recent_alerts': [
                    {
                        'id': str(alert.id),
                        'alert_id': alert.alert_id,
                        'title': alert.title,
                        'severity': alert.severity,
                        'status': alert.status,
                        'detected_at': alert.detected_at.isoformat()
                    }
                    for alert in recent_alerts
                ]
            }

            return Response({
                'success': True,
                'data': asset_data
            })

        elif request.method == 'PUT':
            # Update asset
            asset_data = request.data

            try:
                with transaction.atomic():
                    # Update fields
                    if 'name' in asset_data:
                        asset.name = asset_data['name']
                    if 'description' in asset_data:
                        asset.description = asset_data['description']
                    if 'criticality' in asset_data:
                        asset.criticality = asset_data['criticality']
                    if 'environment' in asset_data:
                        asset.environment = asset_data['environment']
                    if 'alert_enabled' in asset_data:
                        asset.alert_enabled = asset_data['alert_enabled']
                    if 'alert_channels' in asset_data:
                        asset.alert_channels = asset_data['alert_channels']
                    if 'metadata' in asset_data:
                        asset.metadata = asset_data['metadata']

                    asset.save()

                    # Regenerate fingerprints if asset value changed
                    if 'asset_value' in asset_data and asset_data['asset_value'] != asset.asset_value:
                        asset.asset_value = asset_data['asset_value']
                        asset.generate_fingerprints()

                    logger.info(f"Updated asset {asset.name} for organization {organization.name}")

                    return Response({
                        'success': True,
                        'message': 'Asset updated successfully'
                    })

            except ValidationError as e:
                return Response({
                    'success': False,
                    'message': f'Validation error: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            # Delete asset
            asset_name = asset.name
            asset.delete()

            logger.info(f"Deleted asset {asset_name} for organization {organization.name}")

            return Response({
                'success': True,
                'message': 'Asset deleted successfully'
            })

    except Exception as e:
        logger.error(f"Error in asset_inventory_detail: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to process asset request'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_alerts_list(request):
    """
    List custom alerts for the organization.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get query parameters
        alert_status = request.GET.get('status')
        severity = request.GET.get('severity')
        days = int(request.GET.get('days', 30))

        # Build queryset
        queryset = CustomAlert.objects.filter(
            organization=organization,
            created_at__gte=timezone.now() - timezone.timedelta(days=days)
        ).select_related('organization', 'assigned_to').prefetch_related(
            'matched_assets', 'source_indicators', 'affected_users'
        ).order_by('-detected_at')

        # Apply filters
        if alert_status:
            queryset = queryset.filter(status=alert_status)
        if severity:
            queryset = queryset.filter(severity=severity)

        # Paginate results
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        # Serialize data
        alerts_data = []
        for alert in page:
            alerts_data.append({
                'id': str(alert.id),
                'alert_id': alert.alert_id,
                'title': alert.title,
                'description': alert.description,
                'alert_type': alert.alert_type,
                'alert_type_display': alert.get_alert_type_display(),
                'severity': alert.severity,
                'severity_display': alert.get_severity_display(),
                'status': alert.status,
                'status_display': alert.get_status_display(),
                'confidence_score': alert.confidence_score,
                'relevance_score': alert.relevance_score,
                'assigned_to': alert.assigned_to.username if alert.assigned_to else None,
                'detected_at': alert.detected_at.isoformat(),
                'created_at': alert.created_at.isoformat(),
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                'matched_assets_count': alert.matched_assets.count(),
                'source_indicators_count': alert.source_indicators.count(),
                'affected_users_count': alert.affected_users.count(),
                'delivery_channels': alert.delivery_channels,
                'response_actions': alert.response_actions,
                'asset_summary': alert.get_asset_summary(),
                'is_active': alert.is_active
            })

        return paginator.get_paginated_response({
            'success': True,
            'data': alerts_data
        })

    except Exception as e:
        logger.error(f"Error in custom_alerts_list: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get custom alerts'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def custom_alert_detail(request, alert_id):
    """
    Get alert details or update alert status.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get alert
        try:
            alert = CustomAlert.objects.get(
                id=alert_id,
                organization=organization
            )
        except CustomAlert.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Alert not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            # Get detailed alert information
            matched_assets = []
            for asset in alert.matched_assets.all():
                matched_assets.append({
                    'id': str(asset.id),
                    'name': asset.name,
                    'asset_type': asset.get_asset_type_display(),
                    'asset_value': asset.asset_value,
                    'criticality': asset.get_criticality_display(),
                    'environment': asset.environment
                })

            source_indicators = []
            for indicator in alert.source_indicators.all():
                source_indicators.append({
                    'id': str(indicator.id),
                    'type': indicator.type,
                    'pattern': getattr(indicator, 'pattern', ''),
                    'value': getattr(indicator, 'value', ''),
                    'created': indicator.created.isoformat() if hasattr(indicator, 'created') else None
                })

            alert_data = {
                'id': str(alert.id),
                'alert_id': alert.alert_id,
                'title': alert.title,
                'description': alert.description,
                'alert_type': alert.alert_type,
                'alert_type_display': alert.get_alert_type_display(),
                'severity': alert.severity,
                'severity_display': alert.get_severity_display(),
                'status': alert.status,
                'status_display': alert.get_status_display(),
                'confidence_score': alert.confidence_score,
                'relevance_score': alert.relevance_score,
                'assigned_to': alert.assigned_to.username if alert.assigned_to else None,
                'detected_at': alert.detected_at.isoformat(),
                'created_at': alert.created_at.isoformat(),
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                'matched_assets': matched_assets,
                'source_indicators': source_indicators,
                'affected_users': [user.username for user in alert.affected_users.all()],
                'delivery_channels': alert.delivery_channels,
                'delivery_status': alert.delivery_status,
                'response_actions': alert.response_actions,
                'metadata': alert.metadata,
                'response_time': str(alert.response_time) if alert.response_time else None,
                'resolution_time': str(alert.resolution_time) if alert.resolution_time else None,
                'is_active': alert.is_active
            }

            return Response({
                'success': True,
                'data': alert_data
            })

        elif request.method == 'POST':
            # Update alert status
            action = request.data.get('action')

            if action == 'acknowledge':
                alert.acknowledge(request.user)
                message = 'Alert acknowledged successfully'
            elif action == 'resolve':
                alert.resolve(request.user)
                message = 'Alert resolved successfully'
            elif action == 'false_positive':
                alert.mark_false_positive(request.user)
                message = 'Alert marked as false positive'
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid action. Use: acknowledge, resolve, or false_positive'
                }, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Alert {alert.alert_id} {action} by {request.user.username}")

            return Response({
                'success': True,
                'message': message
            })

    except Exception as e:
        logger.error(f"Error in custom_alert_detail: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to process alert request'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_asset_correlation(request):
    """
    Manually trigger asset correlation for new indicators.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get recent indicators to process
        days = int(request.data.get('days', 7))  # Increased to 7 days default
        recent_indicators = Indicator.objects.filter(
            created__gte=timezone.now() - timezone.timedelta(days=days)
        ).order_by('-created')[:100]  # Limit to 100 recent indicators

        # If no recent indicators, use all indicators for demo purposes
        if not recent_indicators:
            recent_indicators = Indicator.objects.all().order_by('-created')[:50]
            
        if not recent_indicators:
            # Create some demo indicators for testing
            from datetime import datetime
            demo_indicators = []
            
            # Create demo IoCs that might match assets
            demo_iocs = [
                {'type': 'ip', 'value': '192.168.1.100', 'pattern': '192.168.1.100'},
                {'type': 'domain', 'value': 'malicious.example.com', 'pattern': 'malicious.example.com'},
                {'type': 'url', 'value': 'http://evil.com/malware.exe', 'pattern': 'evil.com'},
                {'type': 'file_hash', 'value': 'a1b2c3d4e5f6', 'pattern': 'a1b2c3d4e5f6'},
            ]
            
            for ioc in demo_iocs:
                try:
                    indicator = Indicator.objects.create(
                        type=ioc['type'],
                        value=ioc['value'],
                        pattern=ioc['pattern'],
                        created=timezone.now(),
                        modified=timezone.now(),
                        labels=['malicious'],
                        spec_version='2.1',
                        stix_id=f"indicator--demo-{ioc['type']}-{timezone.now().timestamp()}"
                    )
                    demo_indicators.append(indicator)
                except Exception as e:
                    logger.warning(f"Could not create demo indicator: {e}")
                    
            recent_indicators = demo_indicators

        # Initialize alert service and process indicators
        alert_service = AssetBasedAlertService()
        generated_alerts = alert_service.process_indicators_for_organization(
            list(recent_indicators), organization
        )

        logger.info(f"Manually triggered asset correlation for {organization.name}: "
                   f"{len(generated_alerts)} alerts generated from {len(recent_indicators)} indicators")

        return Response({
            'success': True,
            'message': f'Asset correlation completed. Generated {len(generated_alerts)} alerts from {len(recent_indicators)} indicators.',
            'data': {
                'indicators_processed': len(recent_indicators),
                'alerts_generated': len(generated_alerts),
                'alert_ids': [alert.alert_id for alert in generated_alerts]
            }
        })

    except Exception as e:
        logger.error(f"Error in trigger_asset_correlation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'message': f'Failed to trigger asset correlation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asset_alert_statistics(request):
    """
    Get asset-based alert statistics for the organization.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Initialize alert service
        alert_service = AssetBasedAlertService()

        # Get statistics
        alert_stats = alert_service.get_alert_statistics(organization)

        # Get asset statistics
        total_assets = AssetInventory.objects.filter(organization=organization).count()
        alert_enabled_assets = AssetInventory.objects.filter(
            organization=organization,
            alert_enabled=True
        ).count()

        # Asset breakdown by type and criticality
        asset_types = {}
        asset_criticalities = {}

        for asset in AssetInventory.objects.filter(organization=organization):
            asset_type = asset.get_asset_type_display()
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1

            criticality = asset.get_criticality_display()
            asset_criticalities[criticality] = asset_criticalities.get(criticality, 0) + 1

        statistics = {
            'alert_statistics': alert_stats,
            'asset_statistics': {
                'total_assets': total_assets,
                'alert_enabled_assets': alert_enabled_assets,
                'alert_coverage_percentage': round(
                    (alert_enabled_assets / total_assets * 100) if total_assets > 0 else 0, 1
                ),
                'by_type': asset_types,
                'by_criticality': asset_criticalities
            },
            'organization': {
                'name': organization.name,
                'type': organization.get_organization_type_display() if hasattr(organization, 'get_organization_type_display') else organization.organization_type
            }
        }

        return Response({
            'success': True,
            'data': statistics
        })

    except Exception as e:
        logger.error(f"Error in asset_alert_statistics: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_asset_upload(request):
    """
    Bulk upload assets from CSV or JSON data.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        assets_data = request.data.get('assets', [])
        if not assets_data:
            return Response({
                'success': False,
                'message': 'No asset data provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        created_assets = []
        errors = []

        with transaction.atomic():
            for i, asset_data in enumerate(assets_data):
                try:
                    # Validate required fields
                    if not all(field in asset_data for field in ['name', 'asset_type', 'asset_value']):
                        errors.append(f"Row {i+1}: Missing required fields")
                        continue

                    # Create asset
                    asset = AssetInventory.objects.create(
                        name=asset_data['name'],
                        asset_type=asset_data['asset_type'],
                        asset_value=asset_data['asset_value'],
                        description=asset_data.get('description', ''),
                        criticality=asset_data.get('criticality', 'medium'),
                        environment=asset_data.get('environment', 'production'),
                        organization=organization,
                        created_by=request.user,
                        alert_enabled=asset_data.get('alert_enabled', True),
                        alert_channels=asset_data.get('alert_channels', []),
                        metadata=asset_data.get('metadata', {})
                    )

                    # Generate fingerprints
                    asset.generate_fingerprints()
                    created_assets.append(asset)

                except Exception as e:
                    errors.append(f"Row {i+1}: {str(e)}")

        logger.info(f"Bulk uploaded {len(created_assets)} assets for organization {organization.name}")

        return Response({
            'success': True,
            'message': f'Successfully created {len(created_assets)} assets',
            'data': {
                'created_count': len(created_assets),
                'error_count': len(errors),
                'errors': errors[:10]  # Limit errors shown
            }
        })

    except Exception as e:
        logger.error(f"Error in bulk_asset_upload: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to upload assets'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_alert_detail(request, alert_id):
    """
    Get detailed information about a specific custom alert.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        alert_service = AssetBasedAlertService()
        alert_details = alert_service.get_alert_details(alert_id, organization)

        if not alert_details:
            return Response({
                'success': False,
                'message': 'Alert not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'data': alert_details
        })

    except Exception as e:
        logger.error(f"Error in custom_alert_detail: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get alert details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def custom_alert_action(request, alert_id):
    """
    Perform actions on custom alerts (acknowledge, resolve, dismiss, escalate).
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action')
        if not action:
            return Response({
                'success': False,
                'message': 'Action is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        alert_service = AssetBasedAlertService()
        result = alert_service.update_alert_status(alert_id, action, organization, request.user)

        if result['success']:
            return Response({
                'success': True,
                'message': result['message'],
                'data': {
                    'old_status': result['old_status'],
                    'new_status': result['new_status']
                }
            })
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error in custom_alert_action: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to update alert'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_asset_correlation(request):
    """
    Manually trigger asset correlation for the organization.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        days = request.data.get('days', 1)
        if not isinstance(days, int) or days < 1 or days > 30:
            days = 1

        alert_service = AssetBasedAlertService()
        result = alert_service.trigger_correlation_for_organization(organization, days)

        if result['success']:
            return Response({
                'success': True,
                'message': result['message'],
                'data': {
                    'alerts_generated': result['alerts_generated'],
                    'indicators_processed': result['indicators_processed'],
                    'organization': result['organization'],
                    'time_range_days': result['time_range_days']
                }
            })
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error in trigger_asset_correlation: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to trigger correlation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asset_alert_feed(request):
    """
    Real-time feed of asset alerts for the organization.
    """
    try:
        organization = request.user.organization
        if not organization:
            return Response({
                'success': False,
                'message': 'User must belong to an organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get parameters
        limit = min(int(request.GET.get('limit', 50)), 100)
        since = request.GET.get('since')  # ISO timestamp
        severity = request.GET.get('severity')
        status_filter = request.GET.get('status')

        # Build queryset
        queryset = CustomAlert.objects.filter(organization=organization)

        if since:
            try:
                from datetime import datetime
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__gt=since_dt)
            except:
                pass

        if severity:
            queryset = queryset.filter(severity=severity)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Get alerts with related data
        alerts = queryset.select_related('organization').prefetch_related(
            'matched_assets', 'source_indicators'
        ).order_by('-created_at')[:limit]

        # Serialize alerts
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': str(alert.id),
                'alert_id': alert.alert_id,
                'title': alert.title,
                'description': alert.description[:200] + '...' if len(alert.description) > 200 else alert.description,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'severity_display': alert.get_severity_display(),
                'status': alert.status,
                'status_display': alert.get_status_display(),
                'confidence_score': alert.confidence_score,
                'relevance_score': alert.relevance_score,
                'detected_at': alert.detected_at.isoformat(),
                'created_at': alert.created_at.isoformat(),
                'matched_assets': [
                    {
                        'id': str(asset.id),
                        'name': asset.name,
                        'asset_type': asset.asset_type,
                        'criticality': asset.criticality
                    }
                    for asset in alert.matched_assets.all()[:3]  # Limit for performance
                ],
                'matched_asset_count': alert.matched_assets.count(),
                'source_indicator_count': alert.source_indicators.count()
            })

        return Response({
            'success': True,
            'data': {
                'alerts': alerts_data,
                'count': len(alerts_data),
                'has_more': len(alerts_data) == limit,
                'last_updated': timezone.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error in asset_alert_feed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get alert feed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)