"""
Populate comprehensive demo data for the Asset Alert System (WOW Factor #1)
Creates realistic assets, threat indicators, and alerts for demonstration purposes.
"""

import random
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from core.models.models import (
    Organization, AssetInventory, Indicator, CustomAlert, ThreatFeed
)
from core.services.asset_alert_service import AssetBasedAlertService

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate comprehensive demo data for Asset Alert System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organizations',
            type=int,
            default=3,
            help='Number of organizations to create'
        )
        parser.add_argument(
            '--assets-per-org',
            type=int,
            default=15,
            help='Number of assets per organization'
        )
        parser.add_argument(
            '--indicators',
            type=int,
            default=50,
            help='Number of threat indicators to create'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing demo data before creating new'
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.clean_demo_data()

        with transaction.atomic():
            organizations = self.create_organizations(options['organizations'])
            self.create_users(organizations)
            self.create_assets(organizations, options['assets_per_org'])
            indicators = self.create_threat_indicators(options['indicators'])
            self.generate_alerts(organizations, indicators)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated demo data:\n'
                f'- {len(organizations)} organizations\n'
                f'- {sum(org.asset_inventory.count() for org in organizations)} assets\n'
                f'- {len(indicators)} threat indicators\n'
                f'- {CustomAlert.objects.count()} custom alerts'
            )
        )

    def clean_demo_data(self):
        """Clean existing demo data."""
        self.stdout.write('Cleaning existing demo data...')
        CustomAlert.objects.filter(alert_id__startswith='DEMO-').delete()
        AssetInventory.objects.filter(metadata__contains={'demo': True}).delete()
        
        # Clean indicators by demo feed
        demo_feed = ThreatFeed.objects.filter(name='Demo Threat Feed').first()
        if demo_feed:
            Indicator.objects.filter(threat_feed=demo_feed).delete()
            demo_feed.delete()
            
        User.objects.filter(metadata__contains={'demo': True}).delete()
        Organization.objects.filter(trust_metadata__contains={'demo': True}).delete()

    def create_organizations(self, count):
        """Create demo organizations."""
        organizations = []
        org_templates = [
            {
                'name': 'TechCorp University',
                'description': 'Leading technology university with cutting-edge research facilities',
                'organization_type': 'educational',
                'domain': 'techcorp.edu',
                'contact_email': 'security@techcorp.edu',
                'website': 'https://www.techcorp.edu',
                'sectors': ['education', 'research', 'technology']
            },
            {
                'name': 'StateGov Department',
                'description': 'State government cybersecurity department',
                'organization_type': 'government',
                'domain': 'stategov.gov',
                'contact_email': 'cyber@stategov.gov',
                'website': 'https://cyber.stategov.gov',
                'sectors': ['government', 'public-safety', 'infrastructure']
            },
            {
                'name': 'SecureFinance Corp',
                'description': 'Financial services company specializing in digital banking',
                'organization_type': 'private',
                'domain': 'securefinance.com',
                'contact_email': 'security@securefinance.com',
                'website': 'https://www.securefinance.com',
                'sectors': ['finance', 'banking', 'fintech']
            },
            {
                'name': 'HealthSystem Regional',
                'description': 'Regional healthcare system with multiple hospitals',
                'organization_type': 'private',
                'domain': 'healthsystem.org',
                'contact_email': 'it-security@healthsystem.org',
                'website': 'https://www.healthsystem.org',
                'sectors': ['healthcare', 'medical', 'patient-care']
            },
            {
                'name': 'CityGov Municipality',
                'description': 'City government IT and infrastructure services',
                'organization_type': 'government',
                'domain': 'citygov.gov',
                'contact_email': 'cybersec@citygov.gov',
                'website': 'https://www.citygov.gov',
                'sectors': ['government', 'municipal', 'public-services']
            }
        ]

        for i in range(min(count, len(org_templates))):
            template = org_templates[i]
            org = Organization.objects.create(
                name=template['name'],
                description=template['description'],
                organization_type=template['organization_type'],
                domain=template['domain'],
                contact_email=template['contact_email'],
                website=template['website'],
                sectors=template['sectors'],
                is_publisher=True,
                is_verified=True,
                is_active=True,
                trust_metadata={'demo': True, 'created_by': 'populate_asset_demo_data'}
            )
            organizations.append(org)
            self.stdout.write(f'Created organization: {org.name}')

        return organizations

    def create_users(self, organizations):
        """Create demo users for each organization."""
        roles = ['viewer', 'publisher', 'BlueVisionAdmin']

        for org in organizations:
            org_name_short = org.name.split()[0].lower()

            # Create admin user
            admin_user = User.objects.create_user(
                username=f'{org_name_short}_admin',
                email=f'admin@{org.domain}',
                password='demo123!',
                organization=org,
                role='BlueVisionAdmin',
                first_name='Admin',
                last_name='User',
                is_active=True,
                metadata={'demo': True}
            )

            # Create regular users
            for i, role in enumerate(['publisher', 'viewer']):
                user = User.objects.create_user(
                    username=f'{org_name_short}_{role}',
                    email=f'{role}@{org.domain}',
                    password='demo123!',
                    organization=org,
                    role=role,
                    first_name=role.capitalize(),
                    last_name='User',
                    is_active=True,
                    metadata={'demo': True}
                )

            self.stdout.write(f'Created users for {org.name}')

    def create_assets(self, organizations, assets_per_org):
        """Create diverse assets for each organization."""
        asset_templates = {
            'educational': [
                {'name': 'Student Portal', 'type': 'domain', 'value': 'portal.{domain}', 'criticality': 'high'},
                {'name': 'Research Database', 'type': 'domain', 'value': 'research.{domain}', 'criticality': 'critical'},
                {'name': 'Campus Network', 'type': 'ip_range', 'value': '10.{subnet}.0.0/16', 'criticality': 'high'},
                {'name': 'Library System', 'type': 'domain', 'value': 'library.{domain}', 'criticality': 'medium'},
                {'name': 'Faculty Email', 'type': 'domain', 'value': 'mail.{domain}', 'criticality': 'high'},
                {'name': 'Learning Management', 'type': 'domain', 'value': 'lms.{domain}', 'criticality': 'high'},
                {'name': 'WiFi Infrastructure', 'type': 'ip_range', 'value': '172.16.{subnet}.0/24', 'criticality': 'medium'},
                {'name': 'Lab Computers', 'type': 'ip_range', 'value': '192.168.{subnet}.0/24', 'criticality': 'medium'},
                {'name': 'Administrative System', 'type': 'domain', 'value': 'admin.{domain}', 'criticality': 'critical'},
                {'name': 'Video Conferencing', 'type': 'domain', 'value': 'meet.{domain}', 'criticality': 'medium'},
            ],
            'government': [
                {'name': 'Citizen Portal', 'type': 'domain', 'value': 'portal.{domain}', 'criticality': 'critical'},
                {'name': 'Internal Network', 'type': 'ip_range', 'value': '10.{subnet}.0.0/16', 'criticality': 'critical'},
                {'name': 'Public Website', 'type': 'domain', 'value': 'www.{domain}', 'criticality': 'high'},
                {'name': 'Emergency Services', 'type': 'domain', 'value': 'emergency.{domain}', 'criticality': 'critical'},
                {'name': 'DMZ Network', 'type': 'ip_range', 'value': '203.{subnet}.1.0/24', 'criticality': 'high'},
                {'name': 'Records System', 'type': 'domain', 'value': 'records.{domain}', 'criticality': 'critical'},
                {'name': 'Payment Gateway', 'type': 'domain', 'value': 'payments.{domain}', 'criticality': 'critical'},
                {'name': 'Public WiFi', 'type': 'ip_range', 'value': '172.20.{subnet}.0/24', 'criticality': 'low'},
                {'name': 'Staff Email', 'type': 'domain', 'value': 'mail.{domain}', 'criticality': 'high'},
                {'name': 'Document Management', 'type': 'domain', 'value': 'docs.{domain}', 'criticality': 'high'},
            ],
            'private': [
                {'name': 'Corporate Website', 'type': 'domain', 'value': 'www.{domain}', 'criticality': 'high'},
                {'name': 'Customer Portal', 'type': 'domain', 'value': 'portal.{domain}', 'criticality': 'critical'},
                {'name': 'Internal Network', 'type': 'ip_range', 'value': '10.{subnet}.0.0/16', 'criticality': 'critical'},
                {'name': 'API Gateway', 'type': 'domain', 'value': 'api.{domain}', 'criticality': 'critical'},
                {'name': 'Database Cluster', 'type': 'ip_range', 'value': '172.16.{subnet}.0/24', 'criticality': 'critical'},
                {'name': 'Mobile App Backend', 'type': 'domain', 'value': 'mobile-api.{domain}', 'criticality': 'high'},
                {'name': 'CDN Endpoints', 'type': 'domain', 'value': 'cdn.{domain}', 'criticality': 'medium'},
                {'name': 'Analytics Platform', 'type': 'domain', 'value': 'analytics.{domain}', 'criticality': 'medium'},
                {'name': 'Backup Systems', 'type': 'ip_range', 'value': '192.168.{subnet}.0/24', 'criticality': 'high'},
                {'name': 'VPN Gateway', 'type': 'ip_range', 'value': '198.51.100.{subnet}/28', 'criticality': 'high'},
            ]
        }

        software_assets = [
            {'name': 'Windows Active Directory', 'type': 'software', 'value': 'Microsoft Active Directory', 'criticality': 'critical'},
            {'name': 'Apache Web Server', 'type': 'software', 'value': 'Apache HTTP Server 2.4', 'criticality': 'high'},
            {'name': 'MySQL Database', 'type': 'software', 'value': 'MySQL 8.0', 'criticality': 'critical'},
            {'name': 'Nginx Load Balancer', 'type': 'software', 'value': 'Nginx 1.20', 'criticality': 'high'},
            {'name': 'Docker Containers', 'type': 'software', 'value': 'Docker Engine 20.10', 'criticality': 'medium'},
            {'name': 'Kubernetes Cluster', 'type': 'software', 'value': 'Kubernetes 1.21', 'criticality': 'high'},
            {'name': 'Cisco Firewall', 'type': 'software', 'value': 'Cisco ASA 9.x', 'criticality': 'critical'},
            {'name': 'VMware vSphere', 'type': 'software', 'value': 'VMware vSphere 7.0', 'criticality': 'high'},
        ]

        for org in organizations:
            org_type = org.organization_type
            templates = asset_templates.get(org_type, asset_templates['private'])

            # Create infrastructure assets
            assets_created = 0
            subnet_counter = 1

            for template in templates[:assets_per_org-5]:  # Leave room for software assets
                asset_value = template['value'].format(
                    domain=org.domain,
                    subnet=subnet_counter
                )

                asset = AssetInventory.objects.create(
                    name=template['name'],
                    asset_type=template['type'],
                    asset_value=asset_value,
                    description=f"Demo {template['name']} for {org.name}",
                    criticality=template['criticality'],
                    environment='production',
                    organization=org,
                    created_by=User.objects.filter(organization=org, role='BlueVisionAdmin').first(),
                    alert_enabled=True,
                    alert_channels=['email', 'slack'],
                    metadata={
                        'demo': True,
                        'category': 'infrastructure',
                        'owner': 'IT Security Team',
                        'last_scan': (timezone.now() - timedelta(days=random.randint(1, 7))).isoformat()
                    }
                )
                assets_created += 1
                subnet_counter += 1

            # Add some software assets
            for software in random.sample(software_assets, min(5, assets_per_org - assets_created)):
                asset = AssetInventory.objects.create(
                    name=software['name'],
                    asset_type=software['type'],
                    asset_value=software['value'],
                    description=f"Critical software component: {software['value']}",
                    criticality=software['criticality'],
                    environment='production',
                    organization=org,
                    created_by=User.objects.filter(organization=org, role='BlueVisionAdmin').first(),
                    alert_enabled=True,
                    alert_channels=['email', 'sms'],
                    metadata={
                        'demo': True,
                        'category': 'software',
                        'version': f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
                        'vendor': software['value'].split()[0],
                        'last_update': (timezone.now() - timedelta(days=random.randint(1, 30))).isoformat()
                    }
                )
                assets_created += 1

            self.stdout.write(f'Created {assets_created} assets for {org.name}')

    def create_threat_indicators(self, count):
        """Create realistic threat indicators."""
        indicators = []

        # Malicious domains
        malicious_domains = [
            'malware-command.xyz',
            'phishing-bank.com',
            'fake-update.net',
            'suspicious-download.org',
            'crypto-miner.club',
            'data-exfil.info',
            'botnet-control.biz',
            'trojan-dropper.site',
            'ransomware-payment.onion',
            'credential-harvest.dev'
        ]

        # Malicious IPs
        malicious_ips = [
            '192.0.2.100',    # TEST-NET-1
            '198.51.100.50',  # TEST-NET-2
            '203.0.113.25',   # TEST-NET-3
            '192.0.2.200',
            '198.51.100.150',
            '203.0.113.75',
            '192.0.2.250',
            '198.51.100.200',
            '203.0.113.100',
            '192.0.2.50'
        ]

        # File hashes
        malicious_hashes = [
            'da39a3ee5e6b4b0d3255bfef95601890afd80709',
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            '356a192b7913b04c54574d18c28d46e6395428ab',
            '2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881',
            '2cf24dba4f21d4288094c4b97bdc06b7e6c2f3c4a9d0a8adfc3b93b5d1a38a4e',
            '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
            '6b1a6a4c7e5f2a9b8d3c4e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b',
            '7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e',
            '8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a',
            '9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c'
        ]

        # Get or create demo threat feed
        demo_feed, created = ThreatFeed.objects.get_or_create(
            name='Demo Threat Feed',
            defaults={
                'description': 'Demo threat intelligence feed for asset alert testing',
                'taxii_server_url': 'https://demo.threats.local/feed',
                'taxii_collection_id': 'demo-feed-collection',
                'is_active': True,
                'owner': Organization.objects.first()
            }
        )

        # Create domain indicators
        for i, domain in enumerate(malicious_domains[:count//3]):
            first_seen_date = timezone.now() - timedelta(days=random.randint(1, 60))
            indicator = Indicator.objects.create(
                type='domain',
                value=domain,
                name=f'Malicious Domain: {domain}',
                description=f'Malicious domain {domain} identified in demo threat feed',
                confidence=random.randint(70, 95),
                threat_feed=demo_feed,
                stix_id=f'indicator--{uuid.uuid4()}',
                first_seen=first_seen_date,
                last_seen=first_seen_date + timedelta(hours=random.randint(1, 48))
            )
            indicators.append(indicator)

        # Create IP indicators
        for i, ip in enumerate(malicious_ips[:count//3]):
            first_seen_date = timezone.now() - timedelta(days=random.randint(1, 60))
            indicator = Indicator.objects.create(
                type='ip',
                value=ip,
                name=f'Malicious IP: {ip}',
                description=f'Malicious IP {ip} reported in multiple campaigns',
                confidence=random.randint(60, 90),
                threat_feed=demo_feed,
                stix_id=f'indicator--{uuid.uuid4()}',
                first_seen=first_seen_date,
                last_seen=first_seen_date + timedelta(hours=random.randint(1, 48))
            )
            indicators.append(indicator)

        # Create file hash indicators
        for i, hash_val in enumerate(malicious_hashes[:count//3]):
            first_seen_date = timezone.now() - timedelta(days=random.randint(1, 60))
            indicator = Indicator.objects.create(
                type='file_hash',
                value=hash_val,
                hash_type='sha1',
                name=f'Malicious File Hash: {hash_val[:16]}...',
                description=f'Malware sample {hash_val} analyzed by demo security team',
                confidence=random.randint(80, 98),
                threat_feed=demo_feed,
                stix_id=f'indicator--{uuid.uuid4()}',
                first_seen=first_seen_date,
                last_seen=first_seen_date + timedelta(hours=random.randint(1, 48))
            )
            indicators.append(indicator)

        self.stdout.write(f'Created {len(indicators)} threat indicators')
        return indicators

    def generate_alerts(self, organizations, indicators):
        """Generate realistic alerts using the AssetBasedAlertService."""
        alert_service = AssetBasedAlertService()

        # Create some alerts for each organization
        total_alerts = 0
        for org in organizations:
            # Process indicators for this organization
            org_indicators = random.sample(indicators, min(20, len(indicators)))
            alerts = alert_service._process_indicators_for_organization(org_indicators, org)

            # Create some additional manual alerts for demo
            self.create_manual_demo_alerts(org)

            total_alerts += len(alerts)
            self.stdout.write(f'Generated {len(alerts)} alerts for {org.name}')

        self.stdout.write(f'Total alerts generated: {total_alerts}')

    def create_manual_demo_alerts(self, organization):
        """Create additional manual demo alerts with various statuses."""
        assets = list(organization.asset_inventory.all()[:5])
        if not assets:
            return

        alert_scenarios = [
            {
                'title': 'Critical Infrastructure Targeted by APT Group',
                'description': 'Advanced persistent threat group has been detected targeting critical infrastructure assets. Multiple indicators suggest a coordinated campaign focusing on gaining persistent access to network resources.',
                'severity': 'critical',
                'status': 'investigating',
                'assets': assets[:2]
            },
            {
                'title': 'Phishing Campaign Targeting Domain Assets',
                'description': 'Large-scale phishing campaign detected using typosquatted domains similar to organizational assets. Campaign appears to be harvesting credentials for unauthorized access.',
                'severity': 'high',
                'status': 'new',
                'assets': assets[2:4]
            },
            {
                'title': 'Malware Communication to C2 Server',
                'description': 'Network monitoring has detected communication patterns consistent with malware beaconing to command and control infrastructure. Immediate investigation recommended.',
                'severity': 'high',
                'status': 'resolved',
                'assets': assets[4:5]
            },
            {
                'title': 'Suspicious Network Scanning Activity',
                'description': 'Automated scanning detected targeting network ranges associated with organizational infrastructure. Pattern suggests reconnaissance for potential exploitation.',
                'severity': 'medium',
                'status': 'dismissed',
                'assets': assets[1:3]
            }
        ]

        for scenario in alert_scenarios:
            alert_id = f"DEMO-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            alert = CustomAlert.objects.create(
                alert_id=alert_id,
                title=scenario['title'],
                description=scenario['description'],
                alert_type='infrastructure_targeted',
                severity=scenario['severity'],
                status=scenario['status'],
                organization=organization,
                confidence_score=random.uniform(0.7, 0.95),
                relevance_score=random.uniform(0.6, 0.9),
                detected_at=timezone.now() - timedelta(hours=random.randint(1, 72)),
                response_actions=[
                    {
                        'priority': 'high',
                        'action': 'investigate_assets',
                        'title': 'Investigate Affected Assets',
                        'description': 'Conduct thorough investigation of all affected assets'
                    },
                    {
                        'priority': 'medium',
                        'action': 'enhance_monitoring',
                        'title': 'Enhance Monitoring',
                        'description': 'Increase monitoring sensitivity for affected infrastructure'
                    }
                ],
                metadata={
                    'demo': True,
                    'scenario': scenario['title'],
                    'generation_method': 'manual_demo'
                }
            )

            # Associate with assets
            alert.matched_assets.set(scenario['assets'])

            # Associate with affected users
            affected_users = User.objects.filter(
                organization=organization,
                role__in=['BlueVisionAdmin', 'publisher']
            )
            alert.affected_users.set(affected_users)