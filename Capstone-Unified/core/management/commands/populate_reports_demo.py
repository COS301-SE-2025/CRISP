import random
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.models import Organization, ThreatFeed, Indicator, TTPData
from core.trust_management.models.trust_models import TrustRelationship, TrustLevel

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with realistic threat intelligence data for reports demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo data before populating'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing demo data...')
            self.clear_demo_data()

        self.stdout.write('Creating demo threat intelligence data...')
        
        # Create organizations
        edu_orgs = self.create_educational_organizations()
        financial_orgs = self.create_financial_organizations()
        gov_orgs = self.create_government_organizations()
        
        # Create trust relationships
        self.create_trust_relationships(edu_orgs + financial_orgs + gov_orgs)
        
        # Create threat feeds and indicators
        self.create_education_threat_campaign(edu_orgs)
        self.create_financial_threat_campaign(financial_orgs)
        self.create_government_threat_campaign(gov_orgs)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated reports demo data!')
        )

    def clear_demo_data(self):
        """Clear existing demo data"""
        demo_orgs = Organization.objects.filter(name__contains='Demo')
        for org in demo_orgs:
            # Delete related threat feeds and indicators
            ThreatFeed.objects.filter(owner=org).delete()
            TrustRelationship.objects.filter(source_organization=org).delete()
            TrustRelationship.objects.filter(target_organization=org).delete()
        demo_orgs.delete()
        
        # Clear demo TTPs
        TTPData.objects.filter(mitre_technique_id__startswith='T1').delete()

    def create_educational_organizations(self):
        """Create educational institutions"""
        edu_names = [
            'University of Cape Town Demo',
            'Stellenbosch University Demo', 
            'University of Witwatersrand Demo',
            'Rhodes University Demo',
            'University of Pretoria Demo',
            'Cape Peninsula University Demo'
        ]
        
        organizations = []
        for name in edu_names:
            org, created = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'organization_type': 'educational',
                    'is_active': True,
                    'contact_email': f"security@{name.lower().replace(' ', '').replace('demo', '')}.ac.za",
                    'created_at': datetime.now()
                }
            )
            organizations.append(org)
            if created:
                self.stdout.write(f'Created educational org: {name}')
                
        return organizations

    def create_financial_organizations(self):
        """Create financial institutions"""
        financial_names = [
            'Standard Bank Demo',
            'First National Bank Demo',
            'ABSA Bank Demo',
            'Nedbank Demo',
            'Capitec Bank Demo'
        ]
        
        organizations = []
        for name in financial_names:
            org, created = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'organization_type': 'private',
                    'is_active': True,
                    'contact_email': f"security@{name.lower().replace(' ', '').replace('demo', '')}.co.za",
                    'created_at': datetime.now()
                }
            )
            organizations.append(org)
            if created:
                self.stdout.write(f'Created financial org: {name}')
                
        return organizations

    def create_government_organizations(self):
        """Create government institutions"""
        gov_names = [
            'Department of Home Affairs Demo',
            'South African Revenue Service Demo',
            'Department of Health Demo',
            'Department of Education Demo'
        ]
        
        organizations = []
        for name in gov_names:
            org, created = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'organization_type': 'government',
                    'is_active': True,
                    'contact_email': f"security@{name.lower().replace(' ', '').replace('demo', '')}.gov.za",
                    'created_at': datetime.now()
                }
            )
            organizations.append(org)
            if created:
                self.stdout.write(f'Created government org: {name}')
                
        return organizations

    def create_trust_relationships(self, organizations):
        """Create trust relationships between organizations"""
        edu_orgs = [org for org in organizations if org.organization_type == 'educational']
        financial_orgs = [org for org in organizations if org.organization_type == 'private']
        gov_orgs = [org for org in organizations if org.organization_type == 'government']
        
        # High trust within same sectors
        self.create_sector_trust_relationships(edu_orgs, 0.8, 0.9)
        self.create_sector_trust_relationships(financial_orgs, 0.7, 0.85)
        self.create_sector_trust_relationships(gov_orgs, 0.9, 0.95)
        
        # Medium trust between sectors
        self.create_cross_sector_trust(edu_orgs, gov_orgs, 0.6, 0.75)
        self.create_cross_sector_trust(financial_orgs, gov_orgs, 0.5, 0.7)
        self.create_cross_sector_trust(edu_orgs, financial_orgs, 0.4, 0.6)

    def create_sector_trust_relationships(self, organizations, min_trust, max_trust):
        """Create trust relationships within a sector"""
        # Get available trust levels
        trust_levels = list(TrustLevel.objects.filter(is_active=True).order_by('numerical_value'))

        if not trust_levels:
            self.stdout.write(self.style.WARNING('No trust levels found. Skipping trust relationships.'))
            return

        for i, source_org in enumerate(organizations):
            for target_org in organizations[i+1:]:
                if random.random() < 0.8:  # 80% chance of relationship
                    # Select appropriate trust level based on min/max range
                    suitable_levels = [
                        tl for tl in trust_levels
                        if min_trust * 100 <= tl.numerical_value <= max_trust * 100
                    ]
                    if not suitable_levels:
                        suitable_levels = trust_levels

                    trust_level = random.choice(suitable_levels)
                    TrustRelationship.objects.get_or_create(
                        source_organization=source_org,
                        target_organization=target_org,
                        defaults={
                            'trust_level': trust_level,
                            'is_bilateral': True,
                            'status': 'active',
                            'approved_by_source': True,
                            'approved_by_target': True,
                            'anonymization_level': 'partial'
                        }
                    )

    def create_cross_sector_trust(self, org_list1, org_list2, min_trust, max_trust):
        """Create trust relationships between different sectors"""
        # Get available trust levels
        trust_levels = list(TrustLevel.objects.filter(is_active=True).order_by('numerical_value'))

        if not trust_levels:
            self.stdout.write(self.style.WARNING('No trust levels found. Skipping cross-sector trust relationships.'))
            return

        for source_org in org_list1:
            for target_org in org_list2:
                if random.random() < 0.4:  # 40% chance of cross-sector relationship
                    # Select appropriate trust level based on min/max range
                    suitable_levels = [
                        tl for tl in trust_levels
                        if min_trust * 100 <= tl.numerical_value <= max_trust * 100
                    ]
                    if not suitable_levels:
                        suitable_levels = trust_levels

                    trust_level = random.choice(suitable_levels)
                    TrustRelationship.objects.get_or_create(
                        source_organization=source_org,
                        target_organization=target_org,
                        defaults={
                            'trust_level': trust_level,
                            'is_bilateral': False,
                            'status': 'active',
                            'approved_by_source': True,
                            'approved_by_target': True,
                            'anonymization_level': 'partial'
                        }
                    )

    def create_education_threat_campaign(self, edu_orgs):
        """Create education sector ransomware campaign"""
        campaign_name = "Education Ransomware Campaign 2025"
        
        # Create dummy threat feed for TTPs
        dummy_feed, _ = ThreatFeed.objects.get_or_create(
            name="Demo TTP Feed",
            defaults={
                'owner': edu_orgs[0],  # Use first education org as owner
                'description': 'Demo threat feed for TTP data',
                'is_active': True
            }
        )
        
        # Create TTPs for education campaign
        education_ttps = [
            {
                'mitre_technique_id': 'T1566.001',
                'name': 'Spearphishing Attachment',
                'mitre_tactic': 'initial_access',
                'description': 'Phishing emails with malicious attachments targeting education staff'
            },
            {
                'mitre_technique_id': 'T1059.003',
                'name': 'Windows Command Shell',
                'mitre_tactic': 'execution',
                'description': 'Command line execution for initial malware deployment'
            },
            {
                'mitre_technique_id': 'T1486',
                'name': 'Data Encrypted for Impact',
                'mitre_tactic': 'impact',
                'description': 'Ransomware encryption of education system files'
            },
            {
                'mitre_technique_id': 'T1021.001',
                'name': 'Remote Desktop Protocol',
                'mitre_tactic': 'lateral_movement',
                'description': 'RDP abuse for lateral movement within education networks'
            }
        ]
        
        for ttp_data in education_ttps:
            TTPData.objects.get_or_create(
                mitre_technique_id=ttp_data['mitre_technique_id'],
                threat_feed=dummy_feed,
                defaults={
                    'name': ttp_data['name'],
                    'description': ttp_data['description'],
                    'mitre_tactic': ttp_data['mitre_tactic'],
                    'stix_id': f"attack-pattern--{uuid.uuid4()}",
                }
            )
        
        # Create indicators for each education organization
        malicious_ips = [
            '185.220.101.42', '198.96.155.3', '89.248.172.16',
            '194.147.142.12', '213.232.87.19', '176.123.26.89',
            '91.219.236.225', '185.234.218.65', '77.91.124.155'
        ]
        
        malicious_domains = [
            'edu-portal-update.com', 'university-login.net', 'student-system.org',
            'academic-notice.info', 'education-alert.biz', 'campus-security.co'
        ]
        
        malicious_hashes = [
            'a1b2c3d4e5f6789012345678901234567890abcd',
            'f1e2d3c4b5a69870123456789012345678901abc',
            '9876543210abcdef1234567890123456789012ab'
        ]
        
        self.create_indicators_for_organizations(
            edu_orgs, 
            campaign_name,
            malicious_ips,
            malicious_domains, 
            malicious_hashes,
            ['T1566.001', 'T1059.003', 'T1486', 'T1021.001']
        )

    def create_financial_threat_campaign(self, financial_orgs):
        """Create financial sector banking trojan campaign"""
        campaign_name = "Banking Trojan Campaign 2025"
        
        # Create dummy threat feed for TTPs
        dummy_feed, _ = ThreatFeed.objects.get_or_create(
            name="Demo TTP Feed",
            defaults={
                'owner': financial_orgs[0],  # Use first financial org as owner
                'description': 'Demo threat feed for TTP data',
                'is_active': True
            }
        )
        
        # Create TTPs for financial campaign
        financial_ttps = [
            {
                'mitre_technique_id': 'T1566.002',
                'name': 'Spearphishing Link',
                'mitre_tactic': 'initial_access',
                'description': 'Banking phishing emails with malicious links'
            },
            {
                'mitre_technique_id': 'T1555',
                'name': 'Credentials from Password Stores',
                'mitre_tactic': 'credential_access',
                'description': 'Banking credential theft from browsers'
            },
            {
                'mitre_technique_id': 'T1056.001',
                'name': 'Keylogging',
                'mitre_tactic': 'credential_access',
                'description': 'Keylogger for banking credential capture'
            }
        ]
        
        for ttp_data in financial_ttps:
            TTPData.objects.get_or_create(
                mitre_technique_id=ttp_data['mitre_technique_id'],
                threat_feed=dummy_feed,
                defaults={
                    'name': ttp_data['name'],
                    'description': ttp_data['description'],
                    'mitre_tactic': ttp_data['mitre_tactic'],
                    'stix_id': f"attack-pattern--{uuid.uuid4()}",
                }
            )
        
        # Financial threat indicators
        malicious_ips = [
            '162.244.92.15', '185.159.158.77', '194.87.45.23',
            '212.102.63.194', '94.177.123.88'
        ]
        
        malicious_domains = [
            'secure-banking.co.za', 'bank-verification.org.za',
            'online-banking-sa.com', 'financial-alert.co.za'
        ]
        
        malicious_hashes = [
            'b2c3d4e5f6a789012345678901234567890abcde',
            'e3f4a5b6c7d89012345678901234567890abcdef'
        ]
        
        self.create_indicators_for_organizations(
            financial_orgs,
            campaign_name,
            malicious_ips,
            malicious_domains,
            malicious_hashes,
            ['T1566.002', 'T1555', 'T1056.001']
        )

    def create_government_threat_campaign(self, gov_orgs):
        """Create government sector APT campaign"""
        campaign_name = "Government APT Campaign 2025"
        
        # Create dummy threat feed for TTPs
        dummy_feed, _ = ThreatFeed.objects.get_or_create(
            name="Demo TTP Feed",
            defaults={
                'owner': gov_orgs[0],  # Use first government org as owner
                'description': 'Demo threat feed for TTP data',
                'is_active': True
            }
        )
        
        # Create TTPs for government campaign
        govt_ttps = [
            {
                'mitre_technique_id': 'T1190',
                'name': 'Exploit Public-Facing Application',
                'mitre_tactic': 'initial_access',
                'description': 'Web application exploits targeting government portals'
            },
            {
                'mitre_technique_id': 'T1078',
                'name': 'Valid Accounts',
                'mitre_tactic': 'persistence',
                'description': 'Compromised government employee accounts'
            },
            {
                'mitre_technique_id': 'T1041',
                'name': 'Exfiltration Over C2 Channel',
                'mitre_tactic': 'exfiltration',
                'description': 'Government data exfiltration through command and control'
            }
        ]
        
        for ttp_data in govt_ttps:
            TTPData.objects.get_or_create(
                mitre_technique_id=ttp_data['mitre_technique_id'],
                threat_feed=dummy_feed,
                defaults={
                    'name': ttp_data['name'],
                    'description': ttp_data['description'],
                    'mitre_tactic': ttp_data['mitre_tactic'],
                    'stix_id': f"attack-pattern--{uuid.uuid4()}",
                }
            )
        
        # Government threat indicators
        malicious_ips = [
            '103.87.95.12', '156.245.12.88', '198.12.74.156',
            '45.76.189.123', '172.93.201.44'
        ]
        
        malicious_domains = [
            'gov-update.co.za', 'sars-notification.org.za',
            'home-affairs.net.za'
        ]
        
        malicious_hashes = [
            'c4d5e6f7a8b901234567890123456789012abcdef',
            'd5e6f7a8b9c012345678901234567890123abcdef'
        ]
        
        self.create_indicators_for_organizations(
            gov_orgs,
            campaign_name,
            malicious_ips,
            malicious_domains,
            malicious_hashes,
            ['T1190', 'T1078', 'T1041']
        )

    def create_indicators_for_organizations(self, organizations, campaign_name, ips, domains, hashes, ttp_ids):
        """Create indicators distributed across organizations over the past 30 days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for org in organizations:
            # Create threat feed for organization
            feed, created = ThreatFeed.objects.get_or_create(
                name=f"{campaign_name} - {org.name}",
                owner=org,
                defaults={
                    'description': f'Threat indicators for {campaign_name} affecting {org.name}',
                    'is_active': True,
                    'created_at': datetime.now()
                }
            )
            
            # Randomly distribute indicators over 30 days
            num_indicators = random.randint(8, 15)
            all_indicators = ips + domains + hashes
            
            for i in range(num_indicators):
                # Random date within last 30 days
                days_ago = random.randint(0, 30)
                indicator_date = end_date - timedelta(days=days_ago)
                
                # Pick random indicator
                indicator_value = random.choice(all_indicators)
                
                # Determine indicator type
                if indicator_value in ips:
                    indicator_type = 'ip'
                elif indicator_value in domains:
                    indicator_type = 'domain'
                else:
                    indicator_type = 'file_hash'  # Use 'file_hash' instead of 'hash'
                
                # Generate unique STIX ID
                stix_id = f"indicator--{uuid.uuid4()}"
                
                Indicator.objects.get_or_create(
                    value=indicator_value,
                    threat_feed=feed,
                    defaults={
                        'type': indicator_type,  # Use 'type' instead of 'indicator_type'
                        'confidence': int(random.uniform(60, 95)),  # Integer instead of float
                        'description': f'{campaign_name} indicator - {indicator_type}',
                        'first_seen': indicator_date,
                        'last_seen': indicator_date + timedelta(hours=random.randint(1, 48)),
                        'stix_id': stix_id,  # Required field
                        'name': f'{campaign_name} - {indicator_type.upper()}'  # Optional name
                    }
                )
            
            self.stdout.write(f'Created {num_indicators} indicators for {org.name}')