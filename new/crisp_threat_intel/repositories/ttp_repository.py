from typing import List, Dict, Any, Optional
from django.db.models import Q
from .base import BaseRepository
from ..domain.models import TTPData, ThreatFeed


class TTPRepository(BaseRepository[TTPData]):
    """
    Repository for managing TTPs (Tactics, Techniques, and Procedures)
    """
    
    def __init__(self):
        super().__init__(TTPData)
    
    def get_by_threat_feed(self, threat_feed: ThreatFeed) -> List[TTPData]:
        """Get all TTPs for a threat feed"""
        return list(self.model_class.objects.filter(threat_feed=threat_feed))
    
    def get_by_stix_id(self, stix_id: str) -> Optional[TTPData]:
        """Get TTP by STIX ID"""
        return self.model_class.objects.filter(stix_id=stix_id).first()
    
    def get_by_mitre_id(self, mitre_id: str) -> List[TTPData]:
        """Get TTPs by MITRE ATT&CK ID"""
        return list(self.model_class.objects.filter(
            external_references__contains=[{
                'source_name': 'mitre-attack',
                'external_id': mitre_id
            }]
        ))
    
    def get_by_tactic(self, tactic: str) -> List[TTPData]:
        """Get TTPs by MITRE tactic"""
        return list(self.model_class.objects.filter(x_mitre_tactics__contains=[tactic]))
    
    def get_by_platform(self, platform: str) -> List[TTPData]:
        """Get TTPs by platform"""
        return list(self.model_class.objects.filter(x_mitre_platforms__contains=[platform]))
    
    def get_by_technique(self, technique: str) -> List[TTPData]:
        """Get TTPs by MITRE technique"""
        return list(self.model_class.objects.filter(x_mitre_techniques__contains=[technique]))
    
    def search(self, query_params: Dict[str, Any]) -> List[TTPData]:
        """Search TTPs based on query parameters"""
        queryset = self.model_class.objects.all()
        
        # Filter by threat feed
        if 'threat_feed' in query_params:
            queryset = queryset.filter(threat_feed=query_params['threat_feed'])
        
        # Filter by name (case-insensitive partial match)
        if 'name' in query_params:
            queryset = queryset.filter(name__icontains=query_params['name'])
        
        # Filter by description
        if 'description' in query_params:
            queryset = queryset.filter(description__icontains=query_params['description'])
        
        # Filter by MITRE tactics
        if 'x_mitre_tactics' in query_params:
            tactics = query_params['x_mitre_tactics']
            if isinstance(tactics, list):
                queryset = queryset.filter(x_mitre_tactics__overlap=tactics)
            else:
                queryset = queryset.filter(x_mitre_tactics__contains=[tactics])
        
        # Filter by MITRE techniques
        if 'x_mitre_techniques' in query_params:
            techniques = query_params['x_mitre_techniques']
            if isinstance(techniques, list):
                queryset = queryset.filter(x_mitre_techniques__overlap=techniques)
            else:
                queryset = queryset.filter(x_mitre_techniques__contains=[techniques])
        
        # Filter by MITRE platforms
        if 'x_mitre_platforms' in query_params:
            platforms = query_params['x_mitre_platforms']
            if isinstance(platforms, list):
                queryset = queryset.filter(x_mitre_platforms__overlap=platforms)
            else:
                queryset = queryset.filter(x_mitre_platforms__contains=[platforms])
        
        # Filter by kill chain phases
        if 'kill_chain_phase' in query_params:
            phase = query_params['kill_chain_phase']
            queryset = queryset.filter(kill_chain_phases__contains=[{'phase_name': phase}])
        
        # Filter by creation date
        if 'created_after' in query_params:
            queryset = queryset.filter(created__gte=query_params['created_after'])
        
        if 'created_before' in query_params:
            queryset = queryset.filter(created__lte=query_params['created_before'])
        
        # Filter by modification date
        if 'modified_after' in query_params:
            queryset = queryset.filter(modified__gte=query_params['modified_after'])
        
        if 'modified_before' in query_params:
            queryset = queryset.filter(modified__lte=query_params['modified_before'])
        
        # Filter by revocation status
        if 'revoked' in query_params:
            queryset = queryset.filter(revoked=query_params['revoked'])
        
        # Filter by anonymization status
        if 'anonymized' in query_params:
            queryset = queryset.filter(anonymized=query_params['anonymized'])
        
        # Filter by creator
        if 'created_by' in query_params:
            queryset = queryset.filter(created_by=query_params['created_by'])
        
        # Filter by STIX creator reference
        if 'created_by_ref' in query_params:
            queryset = queryset.filter(created_by_ref=query_params['created_by_ref'])
        
        # Filter by external reference source
        if 'external_ref_source' in query_params:
            source = query_params['external_ref_source']
            queryset = queryset.filter(external_references__contains=[{'source_name': source}])
        
        # Filter by external reference ID
        if 'external_ref_id' in query_params:
            ext_id = query_params['external_ref_id']
            queryset = queryset.filter(external_references__contains=[{'external_id': ext_id}])
        
        # Text search across multiple fields
        if 'search' in query_params:
            search_term = query_params['search']
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(x_mitre_tactics__contains=[search_term]) |
                Q(x_mitre_techniques__contains=[search_term]) |
                Q(x_mitre_platforms__contains=[search_term])
            )
        
        # Order results
        order_by = query_params.get('order_by', '-created')
        queryset = queryset.order_by(order_by)
        
        # Apply limit
        if 'limit' in query_params:
            queryset = queryset[:query_params['limit']]
        
        return list(queryset)
    
    def get_ttps_by_kill_chain_phase(self, kill_chain_name: str, phase_name: str) -> List[TTPData]:
        """Get TTPs by kill chain phase"""
        return list(self.model_class.objects.filter(
            kill_chain_phases__contains=[{
                'kill_chain_name': kill_chain_name,
                'phase_name': phase_name
            }]
        ))
    
    def get_mitre_attack_ttps(self) -> List[TTPData]:
        """Get TTPs that reference MITRE ATT&CK"""
        return list(self.model_class.objects.filter(
            external_references__contains=[{'source_name': 'mitre-attack'}]
        ))
    
    def get_recently_created_ttps(self, days: int = 7, threat_feed: ThreatFeed = None) -> List[TTPData]:
        """Get TTPs created in the last N days"""
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        queryset = self.model_class.objects.filter(created__gte=cutoff_date)
        
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        return list(queryset.order_by('-created'))
    
    def get_recently_modified_ttps(self, days: int = 7, threat_feed: ThreatFeed = None) -> List[TTPData]:
        """Get TTPs modified in the last N days"""
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        queryset = self.model_class.objects.filter(modified__gte=cutoff_date)
        
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        return list(queryset.order_by('-modified'))
    
    def get_ttps_statistics(self, threat_feed: ThreatFeed = None) -> Dict[str, Any]:
        """Get TTP statistics"""
        from django.db.models import Count
        
        queryset = self.model_class.objects.all()
        if threat_feed:
            queryset = queryset.filter(threat_feed=threat_feed)
        
        stats = queryset.aggregate(
            total_ttps=Count('id'),
            active_ttps=Count('id', filter=Q(revoked=False)),
            revoked_ttps=Count('id', filter=Q(revoked=True)),
            anonymized_ttps=Count('id', filter=Q(anonymized=True)),
            mitre_ttps=Count('id', filter=Q(external_references__contains=[{'source_name': 'mitre-attack'}]))
        )
        
        # Get tactic distribution
        tactic_stats = {}
        platform_stats = {}
        technique_stats = {}
        
        for ttp in queryset:
            # Count tactics
            for tactic in ttp.x_mitre_tactics:
                tactic_stats[tactic] = tactic_stats.get(tactic, 0) + 1
            
            # Count platforms
            for platform in ttp.x_mitre_platforms:
                platform_stats[platform] = platform_stats.get(platform, 0) + 1
            
            # Count techniques
            for technique in ttp.x_mitre_techniques:
                technique_stats[technique] = technique_stats.get(technique, 0) + 1
        
        stats.update({
            'tactic_distribution': tactic_stats,
            'platform_distribution': platform_stats,
            'technique_distribution': technique_stats,
            'mitre_coverage': self._calculate_mitre_coverage(queryset)
        })
        
        return stats
    
    def get_tactic_coverage(self) -> Dict[str, int]:
        """Get coverage of MITRE ATT&CK tactics"""
        tactic_counts = {}
        
        for ttp in self.model_class.objects.all():
            for tactic in ttp.x_mitre_tactics:
                tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1
        
        return tactic_counts
    
    def get_platform_coverage(self) -> Dict[str, int]:
        """Get coverage of platforms"""
        platform_counts = {}
        
        for ttp in self.model_class.objects.all():
            for platform in ttp.x_mitre_platforms:
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        return platform_counts
    
    def bulk_update_tactics(self, ttp_ids: List[str], new_tactics: List[str]) -> int:
        """Bulk update tactics for multiple TTPs"""
        from django.utils import timezone
        
        updated_count = self.model_class.objects.filter(
            id__in=ttp_ids
        ).update(
            x_mitre_tactics=new_tactics,
            modified=timezone.now()
        )
        
        return updated_count
    
    def bulk_revoke_ttps(self, ttp_ids: List[str]) -> int:
        """Bulk revoke multiple TTPs"""
        from django.utils import timezone
        
        updated_count = self.model_class.objects.filter(
            id__in=ttp_ids
        ).update(
            revoked=True,
            modified=timezone.now()
        )
        
        return updated_count
    
    def find_related_ttps(self, ttp: TTPData) -> List[TTPData]:
        """Find TTPs related to the given TTP based on tactics and techniques"""
        related_ttps = []
        
        # Find TTPs with overlapping tactics
        if ttp.x_mitre_tactics:
            tactics_related = self.model_class.objects.filter(
                x_mitre_tactics__overlap=ttp.x_mitre_tactics
            ).exclude(id=ttp.id)
            related_ttps.extend(tactics_related)
        
        # Find TTPs with overlapping techniques
        if ttp.x_mitre_techniques:
            techniques_related = self.model_class.objects.filter(
                x_mitre_techniques__overlap=ttp.x_mitre_techniques
            ).exclude(id=ttp.id)
            related_ttps.extend(techniques_related)
        
        # Remove duplicates and return
        return list(set(related_ttps))
    
    def _calculate_mitre_coverage(self, queryset) -> Dict[str, Any]:
        """Calculate MITRE ATT&CK framework coverage"""
        unique_tactics = set()
        unique_techniques = set()
        unique_platforms = set()
        
        for ttp in queryset:
            unique_tactics.update(ttp.x_mitre_tactics)
            unique_techniques.update(ttp.x_mitre_techniques)
            unique_platforms.update(ttp.x_mitre_platforms)
        
        # Known MITRE tactics (simplified - would be updated with actual framework data)
        known_tactics = {
            'reconnaissance', 'resource-development', 'initial-access',
            'execution', 'persistence', 'privilege-escalation',
            'defense-evasion', 'credential-access', 'discovery',
            'lateral-movement', 'collection', 'command-and-control',
            'exfiltration', 'impact'
        }
        
        coverage = {
            'tactics_covered': len(unique_tactics),
            'techniques_covered': len(unique_techniques),
            'platforms_covered': len(unique_platforms),
            'tactic_coverage_percentage': round((len(unique_tactics) / len(known_tactics)) * 100, 2) if known_tactics else 0,
            'covered_tactics': list(unique_tactics),
            'missing_tactics': list(known_tactics - unique_tactics) if known_tactics else [],
            'covered_techniques': list(unique_techniques),
            'covered_platforms': list(unique_platforms)
        }
        
        return coverage