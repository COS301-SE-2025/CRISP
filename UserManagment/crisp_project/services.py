"""
CRISP Platform Integration Services
Provides unified services that integrate User Management, Trust Management, and Threat Intelligence
"""

from typing import Optional, List, Dict, Any, Tuple
from django.conf import settings
from django.contrib.auth import get_user_model

from UserManagement.models import Organization
from trust_management_app.core.services.trust_service import TrustService
from trust_management_app.strategies.access_control_strategies import AnonymizationContext
from crisp_threat_intel.models import STIXObject, Collection

User = get_user_model()


class CRISPIntegrationService:
    """
    Main integration service that coordinates between all CRISP components
    """
    
    @staticmethod
    def get_user_organization(user) -> Optional[Organization]:
        """Get the organization for a user"""
        if hasattr(user, 'organization'):
            return user.organization
        return None
    
    @staticmethod
    def check_access_permission(requesting_user, target_organization: Organization, 
                              access_type: str = 'read') -> Tuple[bool, str, Dict]:
        """
        Check if a user has permission to access data from a target organization
        based on trust relationships
        
        Returns: (allowed, access_level, trust_info)
        """
        user_org = CRISPIntegrationService.get_user_organization(requesting_user)
        if not user_org:
            return False, 'none', {'error': 'User not associated with organization'}
        
        if user_org.id == target_organization.id:
            # Same organization - full access
            return True, 'full', {'trust_level': 'complete', 'same_org': True}
        
        # Check trust relationship
        trust_info = TrustService.check_trust_level(user_org, target_organization)
        
        if not trust_info or len(trust_info) == 0:
            return False, 'none', {'error': 'No trust relationship found'}
        
        trust_relationship, trust_level = trust_info[0], trust_info[1] if len(trust_info) > 1 else None
        
        if not trust_level or not trust_level.is_active:
            return False, 'none', {'error': 'Trust relationship not active'}
        
        # Check if access type is allowed for this trust level
        allowed_access = trust_level.default_access_level
        access_levels = ['none', 'read', 'subscribe', 'contribute', 'full']
        
        required_level = access_levels.index(access_type) if access_type in access_levels else 1
        allowed_level = access_levels.index(allowed_access) if allowed_access in access_levels else 0
        
        if allowed_level >= required_level:
            return True, allowed_access, {
                'trust_level': trust_level.level,
                'numerical_value': trust_level.numerical_value,
                'trust_relationship': trust_relationship
            }
        
        return False, allowed_access, {
            'error': f'Insufficient trust level. Required: {access_type}, Available: {allowed_access}'
        }
    
    @staticmethod
    def get_anonymized_stix_objects(requesting_user, source_organization: Organization, 
                                  collection_id: Optional[str] = None) -> List[Dict]:
        """
        Get STIX objects with appropriate anonymization based on trust relationships
        """
        allowed, access_level, trust_info = CRISPIntegrationService.check_access_permission(
            requesting_user, source_organization, 'read'
        )
        
        if not allowed:
            return []
        
        # Get STIX objects
        queryset = STIXObject.objects.filter(source_organization=source_organization)
        
        if collection_id:
            queryset = queryset.filter(collections__id=collection_id)
        
        stix_objects = list(queryset)
        
        # Apply anonymization based on trust level
        if 'trust_relationship' in trust_info:
            trust_relationship = trust_info['trust_relationship']
            anonymization_context = AnonymizationContext(trust_relationship=trust_relationship)
            
            anonymized_objects = []
            for stix_obj in stix_objects:
                try:
                    anonymized_data = anonymization_context.anonymize_data(stix_obj.raw_data)
                    anonymized_objects.append({
                        'stix_id': stix_obj.stix_id,
                        'stix_type': stix_obj.stix_type,
                        'anonymized': True,
                        'anonymization_level': trust_relationship.anonymization_level,
                        'data': anonymized_data
                    })
                except Exception as e:
                    # Fallback to original data if anonymization fails
                    anonymized_objects.append({
                        'stix_id': stix_obj.stix_id,
                        'stix_type': stix_obj.stix_type,
                        'anonymized': False,
                        'error': str(e),
                        'data': stix_obj.raw_data
                    })
            
            return anonymized_objects
        else:
            # Same organization or complete trust - return original data
            return [
                {
                    'stix_id': stix_obj.stix_id,
                    'stix_type': stix_obj.stix_type,
                    'anonymized': False,
                    'data': stix_obj.raw_data
                }
                for stix_obj in stix_objects
            ]
    
    @staticmethod
    def get_accessible_collections(requesting_user) -> List[Dict]:
        """
        Get all collections that the user has access to based on trust relationships
        """
        user_org = CRISPIntegrationService.get_user_organization(requesting_user)
        if not user_org:
            return []
        
        accessible_collections = []
        
        # Get all collections
        for collection in Collection.objects.all():
            # Check access to this collection's owner organization
            allowed, access_level, trust_info = CRISPIntegrationService.check_access_permission(
                requesting_user, collection.owner, 'read'
            )
            
            if allowed:
                accessible_collections.append({
                    'id': str(collection.id),
                    'title': collection.title,
                    'description': collection.description,
                    'alias': collection.alias,
                    'owner': collection.owner.name,
                    'owner_id': str(collection.owner.id),
                    'can_read': collection.can_read,
                    'can_write': collection.can_write and access_level in ['contribute', 'full'],
                    'access_level': access_level,
                    'trust_info': trust_info,
                    'object_count': collection.stix_objects.count()
                })
        
        return accessible_collections
    
    @staticmethod
    def create_stix_object(user, organization: Organization, stix_data: Dict) -> STIXObject:
        """
        Create a new STIX object with proper user and organization attribution
        """
        stix_object = STIXObject.objects.create(
            stix_id=stix_data.get('id'),
            stix_type=stix_data.get('type'),
            spec_version=stix_data.get('spec_version', '2.1'),
            created=stix_data.get('created'),
            modified=stix_data.get('modified'),
            created_by_ref=stix_data.get('created_by_ref'),
            labels=stix_data.get('labels', []),
            confidence=stix_data.get('confidence', 0),
            external_references=stix_data.get('external_references', []),
            object_marking_refs=stix_data.get('object_marking_refs', []),
            granular_markings=stix_data.get('granular_markings', []),
            raw_data=stix_data,
            created_by=user,
            source_organization=organization
        )
        
        return stix_object
    
    @staticmethod
    def get_trust_statistics(organization: Organization) -> Dict:
        """
        Get trust relationship statistics for an organization
        """
        trust_stats = TrustService.get_organization_trust_summary(organization)
        
        return {
            'organization_id': str(organization.id),
            'organization_name': organization.name,
            'initiated_relationships': trust_stats.get('initiated_count', 0),
            'received_relationships': trust_stats.get('received_count', 0),
            'active_relationships': trust_stats.get('active_count', 0),
            'trust_groups': organization.trust_group_memberships.filter(is_active=True).count(),
            'accessible_organizations': len([
                rel for rel in organization.initiated_trust_relationships.filter(status='active')
            ] + [
                rel for rel in organization.received_trust_relationships.filter(status='active')
            ])
        }


class TAXIIIntegrationService:
    """
    Service for integrating TAXII endpoints with trust-based access control
    """
    
    @staticmethod
    def authenticate_taxii_request(request) -> Tuple[Optional[User], Optional[Organization]]:
        """
        Authenticate a TAXII request and return user and organization
        """
        # This would integrate with UserManagement JWT authentication
        # For now, return None to indicate authentication needed
        return None, None
    
    @staticmethod
    def get_collection_objects_with_trust(collection_id: str, requesting_user, 
                                        limit: int = 100, 
                                        added_after: Optional[str] = None) -> Dict:
        """
        Get collection objects with trust-based filtering and anonymization
        """
        try:
            collection = Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            return {'error': 'Collection not found', 'objects': []}
        
        # Check access permission
        allowed, access_level, trust_info = CRISPIntegrationService.check_access_permission(
            requesting_user, collection.owner, 'read'
        )
        
        if not allowed:
            return {'error': 'Access denied', 'objects': []}
        
        # Get anonymized objects
        anonymized_objects = CRISPIntegrationService.get_anonymized_stix_objects(
            requesting_user, collection.owner, collection_id
        )
        
        # Apply TAXII-specific formatting
        taxii_objects = []
        for obj in anonymized_objects[:limit]:
            taxii_objects.append({
                'id': obj['stix_id'],
                'date_added': obj['data'].get('created', ''),
                'version': obj['data'].get('modified', ''),
                'media_type': 'application/stix+json;version=2.1'
            })
        
        return {
            'objects': taxii_objects,
            'more': len(anonymized_objects) > limit,
            'next': str(limit) if len(anonymized_objects) > limit else None
        }