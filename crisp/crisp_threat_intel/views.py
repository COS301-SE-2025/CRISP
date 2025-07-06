"""
Main application views for CRISP Threat Intelligence Platform
"""
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import STIXObject, Collection, Organization
from core.patterns.strategy.context import AnonymizationContext
from core.patterns.strategy.enums import AnonymizationLevel
import json
import copy


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_status(request):
    """API status endpoint"""
    return Response({
        'status': 'active',
        'platform': 'CRISP Threat Intelligence',
        'version': '1.0.0',
        'user': request.user.username,
        'taxii_endpoint': '/taxii2/',
    })


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': '2025-01-21T10:00:00Z'
    })


@api_view(['POST'])
def anonymize_objects(request):
    """Anonymize multiple STIX objects"""
    trust_level = request.data.get('trust_level', 0.5)
    object_ids = request.data.get('object_ids', [])
    
    if not object_ids:
        # Anonymize all objects if none specified
        objects = STIXObject.objects.all()
    else:
        objects = STIXObject.objects.filter(stix_id__in=object_ids)
    
    anonymized_count = 0
    results = []
    
    for obj in objects:
        try:
            # Parse STIX data
            stix_data = obj.raw_data
            
            # Get appropriate strategy
            strategy = AnonymizationStrategyFactory.create_composite_strategy(stix_data, trust_level)
            
            # Apply anonymization
            anonymized_data = strategy.anonymize(stix_data, trust_level)
            
            # Store original data if not already stored
            if not obj.original_data:
                obj.original_data = copy.deepcopy(stix_data)
            
            # Update object with anonymized data
            obj.raw_data = anonymized_data
            obj.anonymized = True
            obj.anonymization_strategy = strategy.__class__.__name__
            obj.anonymization_trust_level = trust_level
            obj.save()
            
            anonymized_count += 1
            results.append({
                'stix_id': obj.stix_id,
                'anonymized': True,
                'trust_level': trust_level
            })
            
        except Exception as e:
            results.append({
                'stix_id': obj.stix_id,
                'error': str(e),
                'anonymized': False
            })
    
    return Response({
        'anonymized_count': anonymized_count,
        'total_objects': len(objects),
        'results': results
    })


@api_view(['POST'])
def anonymize_single_object(request, object_id):
    """Anonymize a single STIX object"""
    trust_level = request.data.get('trust_level', 0.5)
    
    try:
        obj = get_object_or_404(STIXObject, stix_id=object_id)
        
        # Parse STIX data
        stix_data = obj.raw_data
        
        # Get appropriate strategy
        strategy = AnonymizationStrategyFactory.create_composite_strategy(stix_data, trust_level)
        
        # Apply anonymization
        anonymized_data = strategy.anonymize(stix_data, trust_level)
        
        # Store original data if not already stored
        if not obj.original_data:
            obj.original_data = copy.deepcopy(stix_data)
        
        # Update object with anonymized data
        obj.raw_data = anonymized_data
        obj.anonymized = True
        obj.anonymization_strategy = strategy.__class__.__name__
        obj.anonymization_trust_level = trust_level
        obj.save()
        
        return Response({
            'stix_id': obj.stix_id,
            'anonymized': True,
            'trust_level': trust_level,
            'anonymized_data': anonymized_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'stix_id': object_id
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def anonymize_collection(request, collection_id):
    """Anonymize all objects in a collection"""
    trust_level = request.data.get('trust_level', 0.5)
    
    try:
        collection = get_object_or_404(Collection, id=collection_id)
        objects = STIXObject.objects.filter(collectionobject__collection=collection)
        
        anonymized_count = 0
        results = []
        
        for obj in objects:
            try:
                # Parse STIX data
                stix_data = obj.raw_data
                
                # Get appropriate strategy
                strategy = AnonymizationStrategyFactory.create_composite_strategy(stix_data, trust_level)
                
                # Apply anonymization
                anonymized_data = strategy.anonymize(stix_data, trust_level)
                
                # Store original data if not already stored
                if not obj.original_data:
                    obj.original_data = copy.deepcopy(stix_data)
                
                # Update object with anonymized data
                obj.raw_data = anonymized_data
                obj.anonymized = True
                obj.anonymization_strategy = strategy.__class__.__name__
                obj.anonymization_trust_level = trust_level
                obj.save()
                
                anonymized_count += 1
                results.append({
                    'stix_id': obj.stix_id,
                    'anonymized': True,
                    'trust_level': trust_level
                })
                
            except Exception as e:
                results.append({
                    'stix_id': obj.stix_id,
                    'error': str(e),
                    'anonymized': False
                })
        
        return Response({
            'collection_id': collection_id,
            'collection_name': collection.name,
            'anonymized_count': anonymized_count,
            'total_objects': len(objects),
            'results': results
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'collection_id': collection_id
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_objects(request):
    """List all STIX objects with anonymization status"""
    objects = STIXObject.objects.all().order_by('-created_at')
    
    # Filter parameters
    anonymized = request.GET.get('anonymized')
    object_type = request.GET.get('type')
    
    if anonymized is not None:
        objects = objects.filter(anonymized=anonymized.lower() == 'true')
    
    if object_type:
        objects = objects.filter(stix_type=object_type)
    
    results = []
    for obj in objects:
        # Extract key patterns for display
        pattern_preview = ""
        if obj.raw_data.get('pattern'):
            pattern_preview = obj.raw_data['pattern'][:100] + "..." if len(obj.raw_data['pattern']) > 100 else obj.raw_data['pattern']
        
        results.append({
            'stix_id': obj.stix_id,
            'stix_type': obj.stix_type,
            'name': obj.raw_data.get('name', 'Unnamed'),
            'anonymized': obj.anonymized,
            'created': obj.created_at,
            'source_org': obj.source_organization.name if obj.source_organization else 'Unknown',
            'pattern_preview': pattern_preview,
            'has_anonymization_markers': 'x_crisp_anonymized' in obj.raw_data,
            'trust_level': obj.raw_data.get('x_crisp_trust_level', 'N/A')
        })
    
    return Response({
        'total': len(results),
        'objects': results
    })


@api_view(['GET'])
def get_object_details(request, object_id):
    """Get detailed view of a STIX object"""
    try:
        obj = get_object_or_404(STIXObject, stix_id=object_id)
        
        return Response({
            'stix_id': obj.stix_id,
            'stix_type': obj.stix_type,
            'anonymized': obj.anonymized,
            'source_organization': obj.source_organization.name if obj.source_organization else 'Unknown',
            'created_at': obj.created_at,
            'raw_data': obj.raw_data,
            'anonymization_info': {
                'is_anonymized': 'x_crisp_anonymized' in obj.raw_data,
                'trust_level': obj.raw_data.get('x_crisp_trust_level'),
                'anonymization_markers': [key for key in obj.raw_data.keys() if key.startswith('x_crisp_')]
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


def anonymization_demo(request):
    """Demo page showing anonymization effects"""
    
    # Get some sample indicators to demonstrate
    indicators = STIXObject.objects.filter(stix_type='indicator')[:10]
    
    demo_data = []
    trust_levels = [0.9, 0.5, 0.2]  # High, Medium, Low trust
    
    for indicator in indicators:
        if 'pattern' in indicator.raw_data:
            original_data = copy.deepcopy(indicator.raw_data)
            
            # Show what anonymization would look like at different trust levels
            anonymization_examples = []
            
            for trust_level in trust_levels:
                try:
                    strategy = AnonymizationStrategyFactory.create_composite_strategy(original_data, trust_level)
                    anonymized = strategy.anonymize(original_data, trust_level)
                    
                    trust_label = "High" if trust_level >= 0.8 else "Medium" if trust_level >= 0.4 else "Low"
                    
                    anonymization_examples.append({
                        'trust_level': trust_level,
                        'trust_label': trust_label,
                        'strategy': strategy.__class__.__name__,
                        'original_pattern': original_data.get('pattern', ''),
                        'anonymized_pattern': anonymized.get('pattern', ''),
                        'anonymized_data': anonymized
                    })
                except Exception as e:
                    anonymization_examples.append({
                        'trust_level': trust_level,
                        'error': str(e)
                    })
            
            demo_data.append({
                'indicator': indicator,
                'original_data': original_data,
                'anonymization_examples': anonymization_examples
            })
    
    # Create HTML response
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CRISP Anonymization Demo</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .indicator {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; }}
            .trust-level {{ margin: 10px 0; padding: 10px; border-left: 3px solid #007cba; }}
            .high-trust {{ border-left-color: #28a745; }}
            .medium-trust {{ border-left-color: #ffc107; }}
            .low-trust {{ border-left-color: #dc3545; }}
            .pattern {{ font-family: monospace; background: #f8f9fa; padding: 5px; }}
            .original {{ background: #e8f5e8; }}
            .anonymized {{ background: #fff3cd; }}
            pre {{ white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <h1>CRISP Threat Intelligence - Anonymization Demo</h1>
        <p>This demo shows how STIX indicators are anonymized based on trust levels between organizations.</p>
        
        <h2>Trust Levels:</h2>
        <ul>
            <li><strong>High Trust (0.8+):</strong> No anonymization - full data sharing</li>
            <li><strong>Medium Trust (0.4-0.8):</strong> Partial anonymization - preserve some context</li>
            <li><strong>Low Trust (0.0-0.4):</strong> Full anonymization - maximum privacy protection</li>
        </ul>
    """
    
    for item in demo_data:
        indicator = item['indicator']
        original = item['original_data']
        
        html_content += f"""
        <div class="indicator">
            <h3>Indicator: {original.get('name', 'Unnamed')} ({indicator.stix_id})</h3>
            <p><strong>Type:</strong> {indicator.stix_type}</p>
            <p><strong>Source Organization:</strong> {indicator.source_organization.name if indicator.source_organization else 'Unknown'}</p>
            
            <div class="pattern original">
                <strong>Original Pattern:</strong><br>
                {original.get('pattern', 'No pattern')}
            </div>
        """
        
        for example in item['anonymization_examples']:
            if 'error' not in example:
                trust_class = f"{example['trust_label'].lower()}-trust"
                html_content += f"""
                <div class="trust-level {trust_class}">
                    <h4>{example['trust_label']} Trust (Level: {example['trust_level']})</h4>
                    <p><strong>Strategy:</strong> {example['strategy']}</p>
                    <div class="pattern anonymized">
                        <strong>Anonymized Pattern:</strong><br>
                        {example['anonymized_pattern']}
                    </div>
                </div>
                """
        
        html_content += "</div>"
    
    html_content += """
        <h2>API Endpoints:</h2>
        <ul>
            <li><code>GET /api/objects/</code> - List all objects with anonymization status</li>
            <li><code>GET /api/objects/&lt;stix_id&gt;/</code> - Get detailed object information</li>
            <li><code>POST /api/anonymize/</code> - Anonymize objects with specified trust level</li>
        </ul>
        
        <h2>Management Commands:</h2>
        <pre>
# Anonymize all objects with low trust (0.3)
python manage.py anonymize_objects --trust-level=0.3

# Dry run to see what would be anonymized
python manage.py anonymize_objects --dry-run --trust-level=0.5

# Anonymize specific object
python manage.py anonymize_objects --object-id=indicator--example-id
        </pre>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')