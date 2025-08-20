"""
TTP API Views - Export and MITRE matrix endpoints for TTPs
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from core.models.models import TTPData
import csv
import json
import io
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class TTPExportView(APIView):
    """API endpoint for exporting TTP data in various formats"""
    
    def get(self, request):
        try:
            # Get query parameters
            format_type = request.GET.get('format', 'json')
            limit = request.GET.get('limit')
            feed_filter = request.GET.get('feed')
            tactic_filter = request.GET.get('tactic')
            technique_filter = request.GET.get('technique')
            include_anonymized = request.GET.get('include_anonymized', 'true').lower() == 'true'
            fields = request.GET.get('fields', '').split(',') if request.GET.get('fields') else None
            
            # Base queryset
            queryset = TTPData.objects.all()
            
            # Apply filters
            if feed_filter:
                queryset = queryset.filter(threat_feed__id=feed_filter)
            if tactic_filter:
                queryset = queryset.filter(mitre_tactic=tactic_filter)
            if technique_filter:
                queryset = queryset.filter(mitre_technique_id=technique_filter)
            
            # Apply limit
            if limit:
                try:
                    queryset = queryset[:int(limit)]
                except ValueError:
                    return Response({'error': 'Invalid limit parameter'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
            
            # Export based on format
            if format_type == 'csv':
                return self._export_csv(queryset, fields)
            elif format_type == 'stix':
                return self._export_stix(queryset)
            else:  # json
                return self._export_json(queryset, fields, include_anonymized)
                
        except Exception as e:
            logger.error(f"TTP export error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _export_csv(self, queryset, fields):
        """Export as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Default fields if none specified
        if not fields:
            fields = ['name', 'mitre_technique_id', 'mitre_tactic', 'created_at']
        
        # Write header
        writer.writerow(fields)
        
        # Write data
        for ttp in queryset:
            row = []
            for field in fields:
                value = getattr(ttp, field, '')
                if hasattr(value, 'strftime'):  # datetime field
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row.append(str(value))
            writer.writerow(row)
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ttps.csv"'
        return response
    
    def _export_stix(self, queryset):
        """Export as STIX bundle"""
        objects = []
        
        for ttp in queryset:
            stix_obj = {
                'type': 'attack-pattern',
                'id': ttp.stix_id or f'attack-pattern--{ttp.id}',
                'name': ttp.name,
                'description': ttp.description or '',
                'created': ttp.created_at.isoformat(),
                'modified': ttp.updated_at.isoformat() if ttp.updated_at else ttp.created_at.isoformat()
            }
            
            # Add MITRE fields
            if ttp.mitre_technique_id:
                stix_obj['external_references'] = [{
                    'source_name': 'mitre-attack',
                    'external_id': ttp.mitre_technique_id,
                    'url': f'https://attack.mitre.org/techniques/{ttp.mitre_technique_id}'
                }]
            
            if ttp.mitre_tactic:
                stix_obj['kill_chain_phases'] = [{
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': ttp.mitre_tactic
                }]
            
            objects.append(stix_obj)
        
        bundle = {
            'type': 'bundle',
            'id': f'bundle--{queryset.count()}-ttps',
            'objects': objects
        }
        
        return Response(bundle)
    
    def _export_json(self, queryset, fields, include_anonymized):
        """Export as JSON"""
        data = []
        
        for ttp in queryset:
            item = {
                'id': str(ttp.id),
                'name': ttp.name,
                'description': ttp.description,
                'mitre_technique_id': ttp.mitre_technique_id,
                'mitre_tactic': ttp.mitre_tactic,
                'created_at': ttp.created_at.isoformat(),
                'threat_feed': ttp.threat_feed.name if ttp.threat_feed else None
            }
            
            if include_anonymized:
                item['is_anonymized'] = getattr(ttp, 'is_anonymized', False)
            
            # Filter fields if specified
            if fields:
                item = {k: v for k, v in item.items() if k in fields}
            
            data.append(item)
        
        return Response({'ttps': data, 'count': len(data)})


@method_decorator(login_required, name='dispatch')
class MITREMatrixView(APIView):
    """API endpoint for MITRE ATT&CK Matrix visualization"""
    
    def get(self, request):
        try:
            # Get query parameters
            feed_filter = request.GET.get('feed')
            include_zero = request.GET.get('include_zero', 'false').lower() == 'true'
            format_type = request.GET.get('format', 'matrix')
            
            # Get TTPs
            queryset = TTPData.objects.all()
            if feed_filter:
                queryset = queryset.filter(threat_feed__id=feed_filter)
            
            # Basic MITRE tactics
            tactics = ['initial-access', 'execution', 'persistence', 'privilege-escalation', 
                      'defense-evasion', 'credential-access', 'discovery', 'lateral-movement',
                      'collection', 'command-and-control', 'exfiltration', 'impact']
            
            if format_type == 'list':
                return self._get_list_format(queryset, tactics, include_zero)
            else:
                return self._get_matrix_format(queryset, tactics, include_zero)
                
        except Exception as e:
            logger.error(f"MITRE matrix error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_matrix_format(self, queryset, tactics, include_zero):
        """Get matrix format data"""
        # Count TTPs by tactic and technique
        ttp_counts = {}
        for ttp in queryset:
            tactic = ttp.mitre_tactic or 'unknown'
            technique = ttp.mitre_technique_id or 'unknown'
            key = f"{tactic}:{technique}"
            ttp_counts[key] = ttp_counts.get(key, 0) + 1
        
        # Build matrix structure
        matrix = {}
        for tactic in tactics:
            matrix[tactic] = {}
            
        # Add TTP counts to matrix
        for key, count in ttp_counts.items():
            tactic, technique = key.split(':', 1)
            if tactic in matrix:
                matrix[tactic][technique] = count
        
        # Calculate statistics
        total_ttps = queryset.count()
        tactic_stats = {}
        for tactic in tactics:
            tactic_count = queryset.filter(mitre_tactic=tactic).count()
            tactic_stats[tactic] = tactic_count
        
        return Response({
            'matrix': matrix,
            'tactics': tactics,
            'statistics': {
                'total_ttps': total_ttps,
                'tactic_counts': tactic_stats,
                'unique_techniques': len(set(ttp.mitre_technique_id for ttp in queryset if ttp.mitre_technique_id))
            }
        })
    
    def _get_list_format(self, queryset, tactics, include_zero):
        """Get list format data"""
        tactic_counts = {}
        for tactic in tactics:
            count = queryset.filter(mitre_tactic=tactic).count()
            if include_zero or count > 0:
                tactic_counts[tactic] = count
        
        return Response({
            'tactics': tactic_counts,
            'total': queryset.count()
        })