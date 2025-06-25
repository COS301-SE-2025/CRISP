from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from ...models import TrustLevel, TrustGroup, SharingPolicy


class Command(BaseCommand):
    """
    Management command to set up initial trust management configuration.
    Creates default trust levels, policies, and system configurations.
    """
    
    help = 'Set up initial trust management configuration for CRISP'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing trust configuration (WARNING: destructive)',
        )
        parser.add_argument(
            '--create-defaults',
            action='store_true',
            help='Create default trust levels and policies',
        )
        parser.add_argument(
            '--create-sample-groups',
            action='store_true',
            help='Create sample trust groups for testing',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_trust_configuration()
                
                if options['create_defaults'] or not options['reset']:
                    self.create_default_trust_levels()
                    self.create_default_sharing_policies()
                
                if options['create_sample_groups']:
                    self.create_sample_trust_groups()
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully set up trust management configuration')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to set up trust configuration: {str(e)}')
            )
            raise CommandError(f'Setup failed: {str(e)}')
    
    def reset_trust_configuration(self):
        """Reset all trust configuration (WARNING: destructive)."""
        self.stdout.write('Resetting trust configuration...')
        
        # Delete in order to avoid foreign key constraints
        from ...models import TrustRelationship, TrustGroupMembership, TrustLog
        
        TrustLog.objects.all().delete()
        TrustGroupMembership.objects.all().delete()
        TrustRelationship.objects.all().delete()
        TrustGroup.objects.all().delete()
        SharingPolicy.objects.all().delete()
        TrustLevel.objects.all().delete()
        
        self.stdout.write('Trust configuration reset complete.')
    
    def create_default_trust_levels(self):
        """Create default trust levels."""
        self.stdout.write('Creating default trust levels...')
        
        default_levels = [
            {
                'name': 'No Trust',
                'level': 'none',
                'description': 'No trust relationship - no intelligence sharing',
                'numerical_value': 0,
                'default_anonymization_level': 'full',
                'default_access_level': 'none',
                'sharing_policies': {
                    'max_tlp': 'white',
                    'require_attribution': False,
                    'max_age_days': 0
                }
            },
            {
                'name': 'Basic Trust',
                'level': 'low',
                'description': 'Basic trust level for initial partnerships',
                'numerical_value': 25,
                'default_anonymization_level': 'full',
                'default_access_level': 'read',
                'sharing_policies': {
                    'max_tlp': 'green',
                    'require_attribution': False,
                    'max_age_days': 7
                },
                'is_system_default': True
            },
            {
                'name': 'Standard Trust',
                'level': 'medium',
                'description': 'Standard trust level for established partnerships',
                'numerical_value': 50,
                'default_anonymization_level': 'partial',
                'default_access_level': 'read',
                'sharing_policies': {
                    'max_tlp': 'amber',
                    'require_attribution': False,
                    'max_age_days': 30
                }
            },
            {
                'name': 'High Trust',
                'level': 'high',
                'description': 'High trust level for close partnerships',
                'numerical_value': 75,
                'default_anonymization_level': 'minimal',
                'default_access_level': 'contribute',
                'sharing_policies': {
                    'max_tlp': 'amber',
                    'require_attribution': True,
                    'max_age_days': 90
                }
            },
            {
                'name': 'Complete Trust',
                'level': 'complete',
                'description': 'Complete trust level for strategic partnerships',
                'numerical_value': 100,
                'default_anonymization_level': 'none',
                'default_access_level': 'full',
                'sharing_policies': {
                    'max_tlp': 'red',
                    'require_attribution': True,
                    'max_age_days': 365
                }
            }
        ]
        
        for level_data in default_levels:
            trust_level, created = TrustLevel.objects.get_or_create(
                name=level_data['name'],
                defaults={
                    'level': level_data['level'],
                    'description': level_data['description'],
                    'numerical_value': level_data['numerical_value'],
                    'default_anonymization_level': level_data['default_anonymization_level'],
                    'default_access_level': level_data['default_access_level'],
                    'sharing_policies': level_data['sharing_policies'],
                    'is_system_default': level_data.get('is_system_default', False),
                    'created_by': 'system'
                }
            )
            
            if created:
                self.stdout.write(f'  Created trust level: {trust_level.name}')
            else:
                self.stdout.write(f'  Trust level already exists: {trust_level.name}')
    
    def create_default_sharing_policies(self):
        """Create default sharing policies."""
        self.stdout.write('Creating default sharing policies...')
        
        default_policies = [
            {
                'name': 'Public Intelligence Policy',
                'description': 'Policy for sharing publicly available threat intelligence',
                'allowed_stix_types': ['indicator', 'attack-pattern', 'malware'],
                'blocked_stix_types': ['vulnerability', 'identity'],
                'max_tlp_level': 'white',
                'max_age_days': 30,
                'require_anonymization': True,
                'allow_attribution': False,
                'additional_constraints': {
                    'exclude_internal_refs': True,
                    'exclude_personal_data': True
                }
            },
            {
                'name': 'Educational Sector Policy',
                'description': 'Policy for sharing within educational institutions',
                'allowed_stix_types': ['indicator', 'attack-pattern', 'malware', 'campaign'],
                'blocked_stix_types': ['vulnerability'],
                'max_tlp_level': 'green',
                'max_age_days': 60,
                'require_anonymization': True,
                'allow_attribution': False,
                'additional_constraints': {
                    'sector_specific': 'education',
                    'geographic_scope': 'national'
                }
            },
            {
                'name': 'Government Partnership Policy',
                'description': 'Policy for sharing with government entities',
                'allowed_stix_types': ['indicator', 'attack-pattern', 'malware', 'threat-actor', 'campaign'],
                'blocked_stix_types': [],
                'max_tlp_level': 'amber',
                'max_age_days': 180,
                'require_anonymization': False,
                'allow_attribution': True,
                'additional_constraints': {
                    'clearance_required': True,
                    'audit_trail': True
                }
            },
            {
                'name': 'Research Collaboration Policy',
                'description': 'Policy for academic research collaboration',
                'allowed_stix_types': ['attack-pattern', 'malware', 'campaign'],
                'blocked_stix_types': ['indicator', 'vulnerability'],
                'max_tlp_level': 'green',
                'max_age_days': 365,
                'require_anonymization': True,
                'allow_attribution': True,
                'additional_constraints': {
                    'research_use_only': True,
                    'publication_allowed': True
                }
            }
        ]
        
        for policy_data in default_policies:
            policy, created = SharingPolicy.objects.get_or_create(
                name=policy_data['name'],
                defaults={
                    'description': policy_data['description'],
                    'allowed_stix_types': policy_data['allowed_stix_types'],
                    'blocked_stix_types': policy_data['blocked_stix_types'],
                    'max_tlp_level': policy_data['max_tlp_level'],
                    'max_age_days': policy_data['max_age_days'],
                    'require_anonymization': policy_data['require_anonymization'],
                    'allow_attribution': policy_data['allow_attribution'],
                    'additional_constraints': policy_data['additional_constraints'],
                    'created_by': 'system'
                }
            )
            
            if created:
                self.stdout.write(f'  Created sharing policy: {policy.name}')
            else:
                self.stdout.write(f'  Sharing policy already exists: {policy.name}')
    
    def create_sample_trust_groups(self):
        """Create sample trust groups for testing."""
        self.stdout.write('Creating sample trust groups...')
        
        # Get default trust level
        try:
            default_trust_level = TrustLevel.objects.get(is_system_default=True)
        except TrustLevel.DoesNotExist:
            default_trust_level = TrustLevel.objects.first()
            if not default_trust_level:
                self.stdout.write(
                    self.style.ERROR('No trust levels found. Create trust levels first.')
                )
                return
        
        sample_groups = [
            {
                'name': 'Educational Institutions Sharing Network',
                'description': 'Network for sharing threat intelligence among educational institutions',
                'group_type': 'sector',
                'is_public': True,
                'requires_approval': True,
                'group_policies': {
                    'sector': 'education',
                    'sharing_scope': 'national',
                    'data_retention_days': 90
                }
            },
            {
                'name': 'Regional Cybersecurity Consortium',
                'description': 'Regional consortium for cybersecurity information sharing',
                'group_type': 'geography',
                'is_public': True,
                'requires_approval': True,
                'group_policies': {
                    'geographic_scope': 'regional',
                    'membership_fee': False,
                    'meeting_frequency': 'quarterly'
                }
            },
            {
                'name': 'Critical Infrastructure Protection Group',
                'description': 'Private group for critical infrastructure operators',
                'group_type': 'purpose',
                'is_public': False,
                'requires_approval': True,
                'group_policies': {
                    'clearance_required': True,
                    'industry_specific': 'critical_infrastructure',
                    'incident_response': True
                }
            },
            {
                'name': 'Open Source Intelligence Network',
                'description': 'Public network for open source threat intelligence',
                'group_type': 'community',
                'is_public': True,
                'requires_approval': False,
                'group_policies': {
                    'open_source_only': True,
                    'public_attribution': True,
                    'no_restrictions': True
                }
            }
        ]
        
        for group_data in sample_groups:
            group, created = TrustGroup.objects.get_or_create(
                name=group_data['name'],
                defaults={
                    'description': group_data['description'],
                    'group_type': group_data['group_type'],
                    'is_public': group_data['is_public'],
                    'requires_approval': group_data['requires_approval'],
                    'default_trust_level': default_trust_level,
                    'group_policies': group_data['group_policies'],
                    'created_by': 'system',
                    'administrators': ['system']
                }
            )
            
            if created:
                self.stdout.write(f'  Created trust group: {group.name}')
            else:
                self.stdout.write(f'  Trust group already exists: {group.name}')
    
    def get_summary_info(self):
        """Get summary information about current trust configuration."""
        trust_levels_count = TrustLevel.objects.count()
        trust_groups_count = TrustGroup.objects.count()
        sharing_policies_count = SharingPolicy.objects.count()
        
        self.stdout.write('\nCurrent trust configuration summary:')
        self.stdout.write(f'  Trust levels: {trust_levels_count}')
        self.stdout.write(f'  Trust groups: {trust_groups_count}')
        self.stdout.write(f'  Sharing policies: {sharing_policies_count}')
        
        if trust_levels_count > 0:
            self.stdout.write('\nTrust levels:')
            for level in TrustLevel.objects.all():
                default_marker = ' (DEFAULT)' if level.is_system_default else ''
                self.stdout.write(f'  - {level.name} ({level.level}, {level.numerical_value}){default_marker}')
        
        if trust_groups_count > 0:
            self.stdout.write('\nTrust groups:')
            for group in TrustGroup.objects.all():
                public_marker = ' (PUBLIC)' if group.is_public else ' (PRIVATE)'
                self.stdout.write(f'  - {group.name}{public_marker}')
        
        if sharing_policies_count > 0:
            self.stdout.write('\nSharing policies:')
            for policy in SharingPolicy.objects.all():
                active_marker = ' (ACTIVE)' if policy.is_active else ' (INACTIVE)'
                self.stdout.write(f'  - {policy.name}{active_marker}')