"""
Reports API - Threat intelligence reports and analytics endpoints
Handles report generation, export, and analytics for different sectors
"""

import logging
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.services.reports_service import ReportsService
from core.services.access_control_service import AccessControlService

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def education_sector_analysis(request):
    """
    Generate education sector threat analysis report.
    
    GET /api/reports/education-sector-analysis/
    Query Parameters:
        - start_date: YYYY-MM-DD (default: 30 days ago)
        - end_date: YYYY-MM-DD (default: today)  
        - organization_ids: comma-separated UUIDs (optional)
        - format: json|summary (default: json)
    
    Returns:
        Complete education sector analysis report
    """
    try:
        access_control = AccessControlService()
        reports_service = ReportsService()
        
        # Check permissions
        if not access_control.can_view_reports(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view reports'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Parse query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        organization_ids_str = request.GET.get('organization_ids')
        report_format = request.GET.get('format', 'json')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = parse_datetime(start_date_str + 'T00:00:00Z')
                if not start_date:
                    # Try parsing as date only
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    start_date = start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date_str:
            try:
                end_date = parse_datetime(end_date_str + 'T23:59:59Z')
                if not end_date:
                    # Try parsing as date only
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                    end_date = end_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse organization IDs
        organization_ids = None
        if organization_ids_str:
            try:
                organization_ids = [id.strip() for id in organization_ids_str.split(',') if id.strip()]
            except Exception:
                return Response({
                    'success': False,
                    'message': 'Invalid organization_ids format. Use comma-separated UUIDs.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate report
        logger.info(f"Generating education sector analysis for user {request.user.username}")
        
        report_data = reports_service.generate_education_sector_analysis(
            start_date=start_date,
            end_date=end_date,
            organization_ids=organization_ids
        )
        
        # Format response based on requested format
        if report_format == 'summary':
            # Return only essential data for quick loading
            summary_data = {
                'id': report_data['id'],
                'title': report_data['title'],
                'type': report_data['type'],
                'date': report_data['date'],
                'views': report_data['views'],
                'statistics': report_data['statistics'],
                'description': report_data['description']
            }
            return Response({
                'success': True,
                'report': summary_data
            }, status=status.HTTP_200_OK)
        
        # Return full report data
        return Response({
            'success': True,
            'report': report_data,
            'meta': {
                'generated_at': datetime.now().isoformat(),
                'generated_by': request.user.username,
                'report_type': 'education_sector_analysis',
                'data_sources': ['organizations', 'indicators', 'ttps', 'trust_relationships']
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating education sector analysis: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to generate education sector analysis'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_sector_analysis(request):
    """
    Generate financial sector threat analysis report.
    
    GET /api/reports/financial-sector-analysis/
    Query Parameters: (same as education sector)
    """
    try:
        access_control = AccessControlService()
        reports_service = ReportsService()
        
        # Check permissions
        if not access_control.can_view_reports(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view reports'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Parse query parameters (same logic as education sector)
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        organization_ids_str = request.GET.get('organization_ids')
        report_format = request.GET.get('format', 'json')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = parse_datetime(start_date_str + 'T00:00:00Z')
                if not start_date:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    start_date = start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date_str:
            try:
                end_date = parse_datetime(end_date_str + 'T23:59:59Z')
                if not end_date:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                    end_date = end_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse organization IDs
        organization_ids = None
        if organization_ids_str:
            try:
                organization_ids = [id.strip() for id in organization_ids_str.split(',') if id.strip()]
            except Exception:
                return Response({
                    'success': False,
                    'message': 'Invalid organization_ids format. Use comma-separated UUIDs.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate report
        logger.info(f"Generating financial sector analysis for user {request.user.username}")
        
        report_data = reports_service.generate_financial_sector_analysis(
            start_date=start_date,
            end_date=end_date,
            organization_ids=organization_ids
        )
        
        # Format response based on requested format
        if report_format == 'summary':
            summary_data = {
                'id': report_data['id'],
                'title': report_data['title'],
                'type': report_data['type'],
                'date': report_data['date'],
                'views': report_data['views'],
                'statistics': report_data['statistics'],
                'description': report_data['description']
            }
            return Response({
                'success': True,
                'report': summary_data
            }, status=status.HTTP_200_OK)
        
        # Return full report data
        return Response({
            'success': True,
            'report': report_data,
            'meta': {
                'generated_at': datetime.now().isoformat(),
                'generated_by': request.user.username,
                'report_type': 'financial_sector_analysis',
                'data_sources': ['organizations', 'indicators', 'ttps', 'trust_relationships']
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating financial sector analysis: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to generate financial sector analysis'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def government_sector_analysis(request):
    """
    Generate government sector threat analysis report.
    
    GET /api/reports/government-sector-analysis/
    Query Parameters: (same as education sector)
    """
    try:
        access_control = AccessControlService()
        reports_service = ReportsService()
        
        # Check permissions
        if not access_control.can_view_reports(request.user):
            return Response({
                'success': False,
                'message': 'Insufficient permissions to view reports'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Parse query parameters (same logic as other sectors)
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        organization_ids_str = request.GET.get('organization_ids')
        report_format = request.GET.get('format', 'json')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = parse_datetime(start_date_str + 'T00:00:00Z')
                if not start_date:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    start_date = start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date_str:
            try:
                end_date = parse_datetime(end_date_str + 'T23:59:59Z')
                if not end_date:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                    end_date = end_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse organization IDs
        organization_ids = None
        if organization_ids_str:
            try:
                organization_ids = [id.strip() for id in organization_ids_str.split(',') if id.strip()]
            except Exception:
                return Response({
                    'success': False,
                    'message': 'Invalid organization_ids format. Use comma-separated UUIDs.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate report
        logger.info(f"Generating government sector analysis for user {request.user.username}")
        
        report_data = reports_service.generate_government_sector_analysis(
            start_date=start_date,
            end_date=end_date,
            organization_ids=organization_ids
        )
        
        # Format response based on requested format
        if report_format == 'summary':
            summary_data = {
                'id': report_data['id'],
                'title': report_data['title'],
                'type': report_data['type'],
                'date': report_data['date'],
                'views': report_data['views'],
                'statistics': report_data['statistics'],
                'description': report_data['description']
            }
            return Response({
                'success': True,
                'report': summary_data
            }, status=status.HTTP_200_OK)
        
        # Return full report data
        return Response({
            'success': True,
            'report': report_data,
            'meta': {
                'generated_at': datetime.now().isoformat(),
                'generated_by': request.user.username,
                'report_type': 'government_sector_analysis',
                'data_sources': ['organizations', 'indicators', 'ttps', 'trust_relationships']
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating government sector analysis: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to generate government sector analysis'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trend_analysis(request):
    """
    Generate cross-sector trend analysis report.
    
    GET /api/reports/trend-analysis/
    Query Parameters:
        - start_date: YYYY-MM-DD (default: 90 days ago)
        - end_date: YYYY-MM-DD (default: today)
        - sectors: comma-separated list (educational,government,private)
        - trend_type: ioc_evolution|ttp_emergence|cross_sector (default: all)
    """
    # Placeholder for trend analysis
    return Response({
        'success': False,
        'message': 'Trend analysis not yet implemented'
    }, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trust_network_analysis(request):
    """
    Generate trust network analysis report.
    
    GET /api/reports/trust-network-analysis/
    Query Parameters:
        - organization_id: UUID (optional, defaults to user's organization)
        - include_sectors: comma-separated list (optional)
        - network_depth: 1-3 (default: 2)
    """
    # Placeholder for trust network analysis
    return Response({
        'success': False,
        'message': 'Trust network analysis not yet implemented'
    }, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_available_reports(request):
    """
    Get list of available report types and their status.
    
    GET /api/reports/available/
    """
    try:
        reports_service = ReportsService()
        
        available_reports = reports_service.get_available_report_types()
        
        # Add implementation status
        for report in available_reports:
            if report['id'] == 'education-sector-analysis':
                report['status'] = 'implemented'
                report['endpoint'] = '/api/reports/education-sector-analysis/'
            else:
                report['status'] = 'planned'
                report['endpoint'] = f"/api/reports/{report['id']}/"
        
        return Response({
            'success': True,
            'reports': available_reports,
            'total_count': len(available_reports)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing available reports: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to list available reports'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_report(request, report_id):
    """
    Export a report in specified format.
    
    POST /api/reports/export/{report_id}/
    Body:
        {
            "format": "pdf|csv|json",
            "include_charts": true|false,
            "include_raw_data": true|false
        }
    """
    # Placeholder for report export functionality
    return Response({
        'success': False,
        'message': 'Report export functionality not yet implemented'
    }, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_status(request):
    """
    Get status information about the reports system.
    
    GET /api/reports/status/
    """
    try:
        from core.models.models import Organization, Indicator, TTPData, TrustRelationship
        
        status_info = {
            'system_status': 'operational',
            'data_sources': {
                'organizations': {
                    'total': Organization.objects.count(),
                    'educational': Organization.objects.filter(organization_type='educational').count(),
                    'government': Organization.objects.filter(organization_type='government').count(),
                    'private': Organization.objects.filter(organization_type='private').count()
                },
                'indicators': {
                    'total': Indicator.objects.count(),
                    'last_24h': Indicator.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=1)
                    ).count()
                },
                'ttps': {
                    'total': TTPData.objects.count(),
                    'last_24h': TTPData.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=1)
                    ).count()
                },
                'trust_relationships': {
                    'total': TrustRelationship.objects.count(),
                    'active': TrustRelationship.objects.filter(status='active').count()
                }
            },
            'available_reports': ['education-sector-analysis'],
            'planned_reports': ['financial-sector-analysis', 'government-sector-analysis', 'trend-analysis'],
            'last_updated': datetime.now().isoformat()
        }
        
        return Response({
            'success': True,
            'status': status_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting report status: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get report status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)