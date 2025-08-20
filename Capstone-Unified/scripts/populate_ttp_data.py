#!/usr/bin/env python3
"""
Standalone script to populate TTP Analysis with realistic test data.
This script can be run independently or integrated into Django management commands.

Usage: python scripts/populate_ttp_data.py [--count 100] [--clear]
"""

import os
import sys
import django
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_unified.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from core.models.models import TTPData, ThreatFeed, Organization


def create_sample_threat_feeds():
    """Create sample threat feeds if they don't exist"""
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
            print(f'✓ Created threat feed: {feed.name}')
        else:
            print(f'- Using existing feed: {feed.name}')
    
    return feeds


def get_mitre_techniques():
    """Return a comprehensive list of MITRE ATT&CK techniques"""
    return [
        # Initial Access
        {'id': 'T1566.001', 'name': 'Spearphishing Attachment', 'tactic': 'initial_access', 'subtechnique': 'Spearphishing Attachment'},
        {'id': 'T1566.002', 'name': 'Spearphishing Link', 'tactic': 'initial_access', 'subtechnique': 'Spearphishing Link'},
        {'id': 'T1078.004', 'name': 'Cloud Accounts', 'tactic': 'initial_access', 'subtechnique': 'Cloud Accounts'},
        {'id': 'T1190', 'name': 'Exploit Public-Facing Application', 'tactic': 'initial_access', 'subtechnique': ''},
        {'id': 'T1133', 'name': 'External Remote Services', 'tactic': 'initial_access', 'subtechnique': ''},
        
        # Execution
        {'id': 'T1059.001', 'name': 'PowerShell', 'tactic': 'execution', 'subtechnique': 'PowerShell'},
        {'id': 'T1059.003', 'name': 'Windows Command Shell', 'tactic': 'execution', 'subtechnique': 'Windows Command Shell'},
        {'id': 'T1047', 'name': 'Windows Management Instrumentation', 'tactic': 'execution', 'subtechnique': ''},
        {'id': 'T1204.002', 'name': 'Malicious File', 'tactic': 'execution', 'subtechnique': 'Malicious File'},
        {'id': 'T1053.005', 'name': 'Scheduled Task', 'tactic': 'execution', 'subtechnique': 'Scheduled Task'},
        
        # Persistence
        {'id': 'T1543.003', 'name': 'Windows Service', 'tactic': 'persistence', 'subtechnique': 'Windows Service'},
        {'id': 'T1547.001', 'name': 'Registry Run Keys / Startup Folder', 'tactic': 'persistence', 'subtechnique': 'Registry Run Keys / Startup Folder'},
        {'id': 'T1574.002', 'name': 'DLL Side-Loading', 'tactic': 'persistence', 'subtechnique': 'DLL Side-Loading'},
        {'id': 'T1136.001', 'name': 'Local Account', 'tactic': 'persistence', 'subtechnique': 'Local Account'},
        
        # Privilege Escalation
        {'id': 'T1055', 'name': 'Process Injection', 'tactic': 'privilege_escalation', 'subtechnique': ''},
        {'id': 'T1134', 'name': 'Access Token Manipulation', 'tactic': 'privilege_escalation', 'subtechnique': ''},
        {'id': 'T1068', 'name': 'Exploitation for Privilege Escalation', 'tactic': 'privilege_escalation', 'subtechnique': ''},
        
        # Defense Evasion
        {'id': 'T1027', 'name': 'Obfuscated Files or Information', 'tactic': 'defense_evasion', 'subtechnique': ''},
        {'id': 'T1070.004', 'name': 'File Deletion', 'tactic': 'defense_evasion', 'subtechnique': 'File Deletion'},
        {'id': 'T1036', 'name': 'Masquerading', 'tactic': 'defense_evasion', 'subtechnique': ''},
        {'id': 'T1112', 'name': 'Modify Registry', 'tactic': 'defense_evasion', 'subtechnique': ''},
        {'id': 'T1562.001', 'name': 'Disable or Modify Tools', 'tactic': 'defense_evasion', 'subtechnique': 'Disable or Modify Tools'},
        {'id': 'T1140', 'name': 'Deobfuscate/Decode Files or Information', 'tactic': 'defense_evasion', 'subtechnique': ''},
        {'id': 'T1497', 'name': 'Virtualization/Sandbox Evasion', 'tactic': 'defense_evasion', 'subtechnique': ''},
        
        # Credential Access
        {'id': 'T1003.001', 'name': 'LSASS Memory', 'tactic': 'credential_access', 'subtechnique': 'LSASS Memory'},
        {'id': 'T1552.001', 'name': 'Credentials In Files', 'tactic': 'credential_access', 'subtechnique': 'Credentials In Files'},
        {'id': 'T1110', 'name': 'Brute Force', 'tactic': 'credential_access', 'subtechnique': ''},
        
        # Discovery
        {'id': 'T1083', 'name': 'File and Directory Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1057', 'name': 'Process Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1082', 'name': 'System Information Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1016', 'name': 'System Network Configuration Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1049', 'name': 'System Network Connections Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1033', 'name': 'System Owner/User Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1007', 'name': 'System Service Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1124', 'name': 'System Time Discovery', 'tactic': 'discovery', 'subtechnique': ''},
        {'id': 'T1518.001', 'name': 'Security Software Discovery', 'tactic': 'discovery', 'subtechnique': 'Security Software Discovery'},
        
        # Lateral Movement
        {'id': 'T1021.001', 'name': 'Remote Desktop Protocol', 'tactic': 'lateral_movement', 'subtechnique': 'Remote Desktop Protocol'},
        {'id': 'T1021.002', 'name': 'SMB/Windows Admin Shares', 'tactic': 'lateral_movement', 'subtechnique': 'SMB/Windows Admin Shares'},
        {'id': 'T1550.002', 'name': 'Pass the Hash', 'tactic': 'lateral_movement', 'subtechnique': 'Pass the Hash'},
        
        # Collection
        {'id': 'T1005', 'name': 'Data from Local System', 'tactic': 'collection', 'subtechnique': ''},
        {'id': 'T1039', 'name': 'Data from Network Shared Drive', 'tactic': 'collection', 'subtechnique': ''},
        {'id': 'T1113', 'name': 'Screen Capture', 'tactic': 'collection', 'subtechnique': ''},
        
        # Command and Control
        {'id': 'T1071.001', 'name': 'Web Protocols', 'tactic': 'command_and_control', 'subtechnique': 'Web Protocols'},
        {'id': 'T1105', 'name': 'Ingress Tool Transfer', 'tactic': 'command_and_control', 'subtechnique': ''},
        {'id': 'T1095', 'name': 'Non-Application Layer Protocol', 'tactic': 'command_and_control', 'subtechnique': ''},
        
        # Exfiltration
        {'id': 'T1041', 'name': 'Exfiltration Over C2 Channel', 'tactic': 'exfiltration', 'subtechnique': ''},
        {'id': 'T1567.002', 'name': 'Exfiltration to Cloud Storage', 'tactic': 'exfiltration', 'subtechnique': 'Exfiltration to Cloud Storage'},
        
        # Impact
        {'id': 'T1486', 'name': 'Data Encrypted for Impact', 'tactic': 'impact', 'subtechnique': ''},
        {'id': 'T1490', 'name': 'Inhibit System Recovery', 'tactic': 'impact', 'subtechnique': ''},
        {'id': 'T1489', 'name': 'Service Stop', 'tactic': 'impact', 'subtechnique': ''},
    ]


def generate_realistic_descriptions():
    """Generate realistic TTP descriptions"""
    description_templates = [
        "Adversaries utilize {technique} to {purpose}. This technique has been observed in {context} and provides {benefit}.",
        "The {technique} technique allows attackers to {action}. Recent campaigns have shown {trend}.",
        "{technique} is commonly used by threat actors to {objective}. This approach offers {advantage}.",
        "Malicious actors employ {technique} as a method to {goal}. Security researchers have documented {observation}.",
        "Implementation of {technique} enables adversaries to {capability}. Analysis shows {finding}."
    ]
    
    purposes = ["establish persistence", "evade detection", "escalate privileges", "gather intelligence", "maintain access"]
    contexts = ["APT campaigns", "ransomware attacks", "nation-state operations", "cybercrime activities", "targeted attacks"]
    benefits = ["stealth capabilities", "persistence mechanisms", "evasion techniques", "lateral movement options", "data access"]
    actions = ["bypass security controls", "execute malicious code", "steal credentials", "move laterally", "exfiltrate data"]
    trends = ["increased sophistication", "automated deployment", "multi-stage execution", "living-off-the-land techniques", "fileless approaches"]
    advantages = ["reduced detection rates", "improved persistence", "enhanced stealth", "simplified deployment", "increased success rates"]
    objectives = ["compromise systems", "steal sensitive data", "disrupt operations", "maintain long-term access", "deploy additional payloads"]
    capabilities = ["execute arbitrary code", "access sensitive information", "modify system configurations", "establish communication channels", "deploy additional tools"]
    observations = ["evolution in techniques", "increased prevalence", "sophisticated implementations", "novel evasion methods", "improved automation"]
    findings = ["consistent attack patterns", "correlation with known groups", "technical innovations", "defensive gaps", "emerging trends"]
    
    return {
        'templates': description_templates,
        'purposes': purposes,
        'contexts': contexts,
        'benefits': benefits,
        'actions': actions,
        'trends': trends,
        'advantages': advantages,
        'objectives': objectives,
        'capabilities': capabilities,
        'observations': observations,
        'findings': findings
    }


def create_ttp_records(count=100, days_back=90, clear_existing=False):
    """Create TTP records with realistic data"""
    
    print(f"\n🔧 Starting TTP data population...")
    print(f"📊 Target: {count} records over {days_back} days")
    
    # Clear existing data if requested
    if clear_existing:
        deleted_count = TTPData.objects.count()
        TTPData.objects.all().delete()
        print(f"🗑️  Deleted {deleted_count} existing TTP records")
    
    # Get or create threat feeds
    print("\n📡 Setting up threat feeds...")
    threat_feeds = create_sample_threat_feeds()
    
    # Get MITRE techniques
    techniques = get_mitre_techniques()
    description_data = generate_realistic_descriptions()
    
    print(f"\n⚡ Generating {count} TTP records...")
    
    ttp_records = []
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
            # Select technique with weighted distribution (some techniques more common)
            technique = random.choice(techniques)
            
            # Select threat feed with realistic distribution
            threat_feed = random.choice(threat_feeds)
            
            # Check if this combination already exists
            combination_key = (technique['id'], threat_feed.id)
            
            if combination_key not in used_combinations:
                used_combinations.add(combination_key)
                break
            
            attempt += 1
        
        if attempt >= max_attempts:
            # If we can't find a unique combination, skip this record
            print(f"⚠️  Skipping record {i+1} - no unique combination available")
            continue
        
        # Generate random creation time
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
        
        # Determine anonymization (15% chance)
        is_anonymized = random.choice([True] * 15 + [False] * 85)
        
        # Generate realistic description
        template = random.choice(description_data['templates'])
        description = template.format(
            technique=technique['name'].lower(),
            purpose=random.choice(description_data['purposes']),
            context=random.choice(description_data['contexts']),
            benefit=random.choice(description_data['benefits']),
            action=random.choice(description_data['actions']),
            trend=random.choice(description_data['trends']),
            advantage=random.choice(description_data['advantages']),
            objective=random.choice(description_data['objectives']),
            goal=random.choice(description_data['objectives']),
            capability=random.choice(description_data['capabilities']),
            observation=random.choice(description_data['observations']),
            finding=random.choice(description_data['findings'])
        )
        
        # Create original data with realistic metadata
        original_data = {
            'source': f'Intelligence feed: {threat_feed.name}',
            'confidence': random.choices(
                ['high', 'medium', 'low'], 
                weights=[30, 50, 20]
            )[0],
            'severity': random.choices(
                ['critical', 'high', 'medium', 'low'], 
                weights=[10, 25, 45, 20]
            )[0],
            'tlp': random.choices(
                ['red', 'amber', 'green', 'white'], 
                weights=[5, 20, 35, 40]
            )[0],
            'tags': random.sample([
                'apt', 'malware', 'ransomware', 'phishing', 'lateral-movement', 
                'persistence', 'evasion', 'discovery', 'collection', 'exfiltration',
                'backdoor', 'trojan', 'spyware', 'rootkit', 'keylogger'
            ], k=random.randint(2, 5)),
            'mitre_version': '14.1',
            'last_modified': created_at.isoformat(),
            'kill_chain_phases': [
                {
                    'kill_chain_name': 'mitre-attack',
                    'phase_name': technique['tactic']
                }
            ]
        }
        
        # Create TTP record
        ttp = TTPData(
            name=technique['name'],
            description=description,
            mitre_technique_id=technique['id'],
            mitre_tactic=technique['tactic'],
            mitre_subtechnique=technique.get('subtechnique', ''),
            threat_feed=threat_feed,
            stix_id=stix_id,
            is_anonymized=is_anonymized,
            original_data=original_data,
            created_at=created_at,
            updated_at=created_at + timedelta(minutes=random.randint(0, 60))
        )
        
        ttp_records.append(ttp)
        
        # Progress indicator
        if (i + 1) % 20 == 0:
            print(f"📝 Generated {i + 1}/{count} records...")
    
    # Bulk create records
    print(f"\n💾 Saving {len(ttp_records)} records to database...")
    with transaction.atomic():
        created_records = TTPData.objects.bulk_create(ttp_records, batch_size=50)
    
    print(f"✅ Successfully created {len(created_records)} TTP records!")
    
    return created_records


def display_statistics():
    """Display comprehensive statistics about the TTP data"""
    from django.db.models import Count, Min, Max
    
    total_ttps = TTPData.objects.count()
    
    print("\n" + "="*60)
    print("📊 TTP DATA STATISTICS")
    print("="*60)
    print(f"Total TTP Records: {total_ttps}")
    
    # Anonymization stats
    anonymized_count = TTPData.objects.filter(is_anonymized=True).count()
    print(f"Anonymized Records: {anonymized_count} ({anonymized_count/total_ttps*100:.1f}%)")
    
    # Tactic distribution
    print("\n🎯 Distribution by MITRE Tactic:")
    tactic_stats = TTPData.objects.values('mitre_tactic').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for tactic in tactic_stats:
        percentage = (tactic['count'] / total_ttps) * 100
        tactic_name = tactic['mitre_tactic'].replace('_', ' ').title()
        print(f"  {tactic_name:<25} {tactic['count']:>3} ({percentage:>4.1f}%)")
    
    # Feed distribution
    print("\n📡 Distribution by Threat Feed:")
    feed_stats = TTPData.objects.select_related('threat_feed').values(
        'threat_feed__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    for feed in feed_stats:
        percentage = (feed['count'] / total_ttps) * 100
        print(f"  {feed['threat_feed__name']:<30} {feed['count']:>3} ({percentage:>4.1f}%)")
    
    # Time range
    date_range = TTPData.objects.aggregate(
        earliest=Min('created_at'),
        latest=Max('created_at')
    )
    
    if date_range['earliest'] and date_range['latest']:
        print(f"\n📅 Date Range:")
        print(f"  Earliest: {date_range['earliest'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  Latest:   {date_range['latest'].strftime('%Y-%m-%d %H:%M')}")
        
        duration = date_range['latest'] - date_range['earliest']
        print(f"  Duration: {duration.days} days")
    
    # Top techniques
    print("\n🔝 Top 10 Most Common Techniques:")
    technique_stats = TTPData.objects.values('mitre_technique_id', 'name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for i, technique in enumerate(technique_stats, 1):
        print(f"  {i:>2}. {technique['mitre_technique_id']:<10} {technique['name']:<35} ({technique['count']} occurrences)")
    
    print("\n" + "="*60)
    print("✅ TTP data population completed successfully!")
    print("="*60)


def main():
    """Main function to run the TTP data population"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate TTP Analysis with realistic test data')
    parser.add_argument('--count', type=int, default=100, help='Number of TTP records to create')
    parser.add_argument('--days-back', type=int, default=90, help='Spread creation dates over this many days')
    parser.add_argument('--clear', action='store_true', help='Clear existing TTP data before populating')
    
    args = parser.parse_args()
    
    try:
        # Create TTP records
        records = create_ttp_records(
            count=args.count, 
            days_back=args.days_back, 
            clear_existing=args.clear
        )
        
        # Display statistics
        display_statistics()
        
        print(f"\n🎉 Successfully populated TTP Analysis with {len(records)} datapoints!")
        print("You can now access the TTP Analysis page to see the data visualization.")
        
    except Exception as e:
        print(f"\n❌ Error during TTP data population: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())