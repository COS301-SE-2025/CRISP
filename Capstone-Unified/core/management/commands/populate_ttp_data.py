"""
Django management command to populate TTP Analysis with realistic test data.
Usage: python manage.py populate_ttp_data [--count 100] [--clear-existing]
"""

import random
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from core.models.models import TTPData, ThreatFeed, Organization
from core.services.mitre_mapping_service import MITREFrameworkData


class Command(BaseCommand):
    help = 'Populate TTP Analysis with realistic test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of TTP records to create (default: 100)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Delete existing TTP data before populating'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=90,
            help='Spread creation dates over this many days (default: 90)'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear_existing']
        days_back = options['days_back']

        self.stdout.write(self.style.SUCCESS(f'Starting TTP data population...'))
        
        # Clear existing data if requested
        if clear_existing:
            deleted_count = TTPData.objects.count()
            TTPData.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing TTP records')
            )

        # Get or create threat feeds
        threat_feeds = self.get_or_create_threat_feeds()
        
        # Generate realistic TTP data
        ttp_data_list = self.generate_ttp_data(count, threat_feeds, days_back)
        
        # Bulk create TTPs
        with transaction.atomic():
            created_ttps = TTPData.objects.bulk_create(ttp_data_list, batch_size=50)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_ttps)} TTP records')
        )
        
        # Display statistics
        self.display_statistics()

    def get_or_create_threat_feeds(self):
        """Get or create sample threat feeds for TTP data"""
        # First, get or create default organization
        default_org, _ = Organization.objects.get_or_create(
            name='Default Organization',
            defaults={
                'description': 'Default organization for threat feeds',
                'organization_type': 'educational'
            }
        )
        
        feeds_data = [
            {
                'name': 'APT Intelligence Feed',
                'description': 'Advanced Persistent Threat intelligence from multiple sources (JSON format)',
                'taxii_server_url': 'https://api.example.com/apt-intel',
                'is_active': True,
                'owner': default_org
            },
            {
                'name': 'MITRE ATT&CK Techniques',
                'description': 'Official MITRE ATT&CK framework techniques (STIX format)',
                'taxii_server_url': 'https://github.com/mitre/cti',
                'is_active': True,
                'owner': default_org
            },
            {
                'name': 'Cybercrime TTP Feed',
                'description': 'Cybercriminal tactics, techniques, and procedures (XML format)',
                'taxii_server_url': 'https://feed.cybercrime-tracker.net/ttps',
                'is_active': True,
                'owner': default_org
            },
            {
                'name': 'Nation State Indicators',
                'description': 'Nation-state sponsored attack techniques (JSON format)',
                'taxii_server_url': 'https://intel.gov.example/nation-state',
                'is_active': True,
                'owner': default_org
            },
            {
                'name': 'Ransomware Tactics Feed',
                'description': 'Ransomware group techniques and procedures (STIX format)',
                'taxii_server_url': 'https://ransomware-tracker.org/ttps',
                'is_active': True,
                'owner': default_org
            }
        ]
        
        feeds = []
        for feed_data in feeds_data:
            feed, created = ThreatFeed.objects.get_or_create(
                name=feed_data['name'],
                defaults=feed_data
            )
            feeds.append(feed)
            if created:
                self.stdout.write(f'Created threat feed: {feed.name}')
        
        return feeds

    def generate_ttp_data(self, count, threat_feeds, days_back):
        """Generate realistic TTP data based on MITRE ATT&CK framework"""
        
        # Real MITRE ATT&CK techniques with their tactics and descriptions
        mitre_techniques = [
            {
                'id': 'T1566.001',
                'name': 'Spearphishing Attachment',
                'tactic': 'initial_access',
                'subtechnique': 'Spearphishing Attachment',
                'description': 'Adversaries may send spearphishing emails with a malicious attachment in an attempt to gain access to victim systems. Spearphishing attachment is a specific variant of spearphishing that uses an attachment as the lure.'
            },
            {
                'id': 'T1059.001',
                'name': 'PowerShell',
                'tactic': 'execution',
                'subtechnique': 'PowerShell',
                'description': 'Adversaries may abuse PowerShell commands and scripts for execution. PowerShell is a powerful interactive command-line interface and scripting environment included in the Windows operating system.'
            },
            {
                'id': 'T1055',
                'name': 'Process Injection',
                'tactic': 'privilege_escalation',
                'subtechnique': '',
                'description': 'Adversaries may inject code into processes in order to evade process-based defenses as well as possibly elevate privileges.'
            },
            {
                'id': 'T1047',
                'name': 'Windows Management Instrumentation',
                'tactic': 'execution',
                'subtechnique': '',
                'description': 'Adversaries may abuse Windows Management Instrumentation (WMI) to achieve execution.'
            },
            {
                'id': 'T1070.004',
                'name': 'File Deletion',
                'tactic': 'defense_evasion',
                'subtechnique': 'File Deletion',
                'description': 'Adversaries may delete files left behind by the actions of their intrusion activity.'
            },
            {
                'id': 'T1083',
                'name': 'File and Directory Discovery',
                'tactic': 'discovery',
                'subtechnique': '',
                'description': 'Adversaries may enumerate files and directories or may search in specific locations of a host or network share for certain information within a file system.'
            },
            {
                'id': 'T1003.001',
                'name': 'LSASS Memory',
                'tactic': 'credential_access',
                'subtechnique': 'LSASS Memory',
                'description': 'Adversaries may attempt to access credential material stored in the process memory of the Local Security Authority Subsystem Service (LSASS).'
            },
            {
                'id': 'T1021.001',
                'name': 'Remote Desktop Protocol',
                'tactic': 'lateral_movement',
                'subtechnique': 'Remote Desktop Protocol',
                'description': 'Adversaries may use Valid Accounts to log into a computer using the Remote Desktop Protocol (RDP).'
            },
            {
                'id': 'T1071.001',
                'name': 'Web Protocols',
                'tactic': 'command_and_control',
                'subtechnique': 'Web Protocols',
                'description': 'Adversaries may communicate using application layer protocols associated with web traffic to avoid detection/network filtering.'
            },
            {
                'id': 'T1041',
                'name': 'Exfiltration Over C2 Channel',
                'tactic': 'exfiltration',
                'subtechnique': '',
                'description': 'Adversaries may steal data by exfiltrating it over an existing command and control channel.'
            },
            {
                'id': 'T1486',
                'name': 'Data Encrypted for Impact',
                'tactic': 'impact',
                'subtechnique': '',
                'description': 'Adversaries may encrypt data on target systems or on large numbers of systems in a network to interrupt availability to system and network resources.'
            },
            {
                'id': 'T1057',
                'name': 'Process Discovery',
                'tactic': 'discovery',
                'subtechnique': '',
                'description': 'Adversaries may attempt to get information about running processes on a system.'
            },
            {
                'id': 'T1027',
                'name': 'Obfuscated Files or Information',
                'tactic': 'defense_evasion',
                'subtechnique': '',
                'description': 'Adversaries may attempt to make an executable or file difficult to discover or analyze by encrypting, encoding, or otherwise obfuscating its contents.'
            },
            {
                'id': 'T1053.005',
                'name': 'Scheduled Task',
                'tactic': 'persistence',
                'subtechnique': 'Scheduled Task',
                'description': 'Adversaries may abuse the Windows Task Scheduler to perform task scheduling for initial or recurring execution of malicious code.'
            },
            {
                'id': 'T1078.004',
                'name': 'Cloud Accounts',
                'tactic': 'initial_access',
                'subtechnique': 'Cloud Accounts',
                'description': 'Adversaries may obtain and abuse credentials of a cloud account as a means of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion.'
            },
            {
                'id': 'T1105',
                'name': 'Ingress Tool Transfer',
                'tactic': 'command_and_control',
                'subtechnique': '',
                'description': 'Adversaries may transfer tools or other files from an external system into a compromised environment.'
            },
            {
                'id': 'T1518.001',
                'name': 'Security Software Discovery',
                'tactic': 'discovery',
                'subtechnique': 'Security Software Discovery',
                'description': 'Adversaries may attempt to get a listing of security software, configurations, defensive tools, and sensors that are installed on a system or in a cloud environment.'
            },
            {
                'id': 'T1112',
                'name': 'Modify Registry',
                'tactic': 'defense_evasion',
                'subtechnique': '',
                'description': 'Adversaries may interact with the Windows Registry to hide configuration information within Registry keys, remove information as part of cleaning up, or as part of other techniques to aid in persistence and execution.'
            },
            {
                'id': 'T1140',
                'name': 'Deobfuscate/Decode Files or Information',
                'tactic': 'defense_evasion',
                'subtechnique': '',
                'description': 'Adversaries may use Obfuscated Files or Information to hide artifacts of an intrusion from analysis.'
            },
            {
                'id': 'T1562.001',
                'name': 'Disable or Modify Tools',
                'tactic': 'defense_evasion',
                'subtechnique': 'Disable or Modify Tools',
                'description': 'Adversaries may modify and/or disable security tools to avoid possible detection of their malware/tools and activities.'
            }
        ]

        # Additional techniques to reach 100+ datapoints
        additional_techniques = [
            {'id': 'T1204.002', 'name': 'Malicious File', 'tactic': 'execution', 'subtechnique': 'Malicious File'},
            {'id': 'T1036', 'name': 'Masquerading', 'tactic': 'defense_evasion', 'subtechnique': ''},
            {'id': 'T1543.003', 'name': 'Windows Service', 'tactic': 'persistence', 'subtechnique': 'Windows Service'},
            {'id': 'T1082', 'name': 'System Information Discovery', 'tactic': 'discovery', 'subtechnique': ''},
            {'id': 'T1016', 'name': 'System Network Configuration Discovery', 'tactic': 'discovery', 'subtechnique': ''},
            {'id': 'T1049', 'name': 'System Network Connections Discovery', 'tactic': 'discovery', 'subtechnique': ''},
            {'id': 'T1033', 'name': 'System Owner/User Discovery', 'tactic': 'discovery', 'subtechnique': ''},
            {'id': 'T1007', 'name': 'System Service Discovery', 'tactic': 'discovery', 'subtechnique': ''},
            {'id': 'T1124', 'name': 'System Time Discovery', 'tactic': 'discovery', 'subtechnique': ''},
            {'id': 'T1497', 'name': 'Virtualization/Sandbox Evasion', 'tactic': 'defense_evasion', 'subtechnique': ''},
        ]

        all_techniques = mitre_techniques + additional_techniques
        
        ttp_data_list = []
        start_date = timezone.now() - timedelta(days=days_back)
        
        # Track used combinations to avoid duplicates
        used_combinations = set()
        
        # Check existing combinations in database
        existing_combinations = set(
            TTPData.objects.values_list('mitre_technique_id', 'threat_feed_id')
        )
        used_combinations.update(existing_combinations)
        
        for i in range(count):
            max_attempts = 10
            attempt = 0
            
            while attempt < max_attempts:
                # Select technique (with some repetition for realistic distribution)
                technique = random.choice(all_techniques)
                
                # Select random threat feed
                threat_feed = random.choice(threat_feeds)
                
                # Check if this combination already exists
                combination_key = (technique['id'], threat_feed.id)
                
                if combination_key not in used_combinations:
                    used_combinations.add(combination_key)
                    break
                
                attempt += 1
            
            if attempt >= max_attempts:
                # If we can't find a unique combination, skip this record
                self.stdout.write(f"⚠️  Skipping record {i+1} - no unique combination available")
                continue
            
            # Generate random creation time within the specified range
            random_days = random.randint(0, days_back)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            created_at = start_date + timedelta(
                days=random_days, 
                hours=random_hours, 
                minutes=random_minutes
            )
            
            # Generate unique STIX ID
            stix_id = f"attack-pattern--{uuid.uuid4()}"
            
            # Determine anonymization (20% chance)
            is_anonymized = random.choice([True] * 2 + [False] * 8)  # 20% chance
            
            # Create description variations
            base_description = technique.get('description', f'Technique involving {technique["name"]}')
            description_variations = [
                base_description,
                f"Advanced variant of {technique['name']} observed in recent campaigns. {base_description[:200]}...",
                f"Modified {technique['name']} technique with enhanced evasion capabilities. {base_description[:150]}...",
                f"Automated {technique['name']} implementation detected across multiple targets. {base_description[:180]}...",
            ]
            
            # Create TTP record
            ttp = TTPData(
                name=technique['name'],
                description=random.choice(description_variations),
                mitre_technique_id=technique['id'],
                mitre_tactic=technique['tactic'],
                mitre_subtechnique=technique.get('subtechnique', ''),
                threat_feed=threat_feed,
                stix_id=stix_id,
                is_anonymized=is_anonymized,
                original_data={
                    'source': f'Simulated data from {threat_feed.name}',
                    'confidence': random.choice(['high', 'medium', 'low']),
                    'severity': random.choice(['critical', 'high', 'medium', 'low']),
                    'tags': random.sample(['apt', 'malware', 'ransomware', 'phishing', 'lateral-movement', 'persistence', 'evasion'], k=random.randint(1, 3))
                },
                created_at=created_at,
                updated_at=created_at + timedelta(minutes=random.randint(0, 60))
            )
            
            ttp_data_list.append(ttp)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                self.stdout.write(f'Generated {i + 1}/{count} TTP records...')
        
        return ttp_data_list

    def display_statistics(self):
        """Display statistics about the created TTP data"""
        total_ttps = TTPData.objects.count()
        
        # Count by tactic
        from django.db.models import Count
        tactic_stats = TTPData.objects.values('mitre_tactic').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Count by feed
        feed_stats = TTPData.objects.select_related('threat_feed').values(
            'threat_feed__name'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Anonymization stats
        anonymized_count = TTPData.objects.filter(is_anonymized=True).count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('TTP DATA STATISTICS'))
        self.stdout.write('='*50)
        self.stdout.write(f'Total TTP Records: {total_ttps}')
        self.stdout.write(f'Anonymized Records: {anonymized_count} ({anonymized_count/total_ttps*100:.1f}%)')
        
        self.stdout.write('\nTTPs by MITRE Tactic:')
        for tactic in tactic_stats[:10]:  # Top 10
            self.stdout.write(f'  {tactic["mitre_tactic"]}: {tactic["count"]}')
        
        self.stdout.write('\nTTPs by Threat Feed:')
        for feed in feed_stats:
            self.stdout.write(f'  {feed["threat_feed__name"]}: {feed["count"]}')
        
        # Date range
        from django.db.models import Min, Max
        date_range = TTPData.objects.aggregate(
            earliest=Min('created_at'),
            latest=Max('created_at')
        )
        
        if date_range['earliest'] and date_range['latest']:
            self.stdout.write(f'\nDate Range:')
            self.stdout.write(f'  Earliest: {date_range["earliest"].strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'  Latest: {date_range["latest"].strftime("%Y-%m-%d %H:%M")}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('TTP data population completed successfully!'))
        self.stdout.write('='*50)