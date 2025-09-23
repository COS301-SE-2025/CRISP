"""
Demo Asset-Based Alerts Management Command for CRISP WOW Factor #1
Creates sample data and demonstrates the asset-based alert system functionality.
"""

import logging
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from core.models.models import (
    Organization, AssetInventory, CustomAlert, Indicator, ThreatFeed
)
from core.services.asset_alert_service import AssetBasedAlertService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Demo Asset-Based Alert System - Creates sample data and demonstrates functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['setup', 'demo', 'cleanup', 'full'],
            default='full',
            help='Mode: setup (create data), demo (generate alerts), cleanup (remove data), full (all)'
        )
        parser.add_argument(
            '--organization',
            type=str,
            help='Organization name to use for demo (default: creates "Demo University")'
        )
        parser.add_argument(
            '--skip-setup',
            action='store_true',
            help='Skip data setup and use existing data'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        mode = options['mode']

        if self.verbose:
            logging.basicConfig(level=logging.INFO)

        self.stdout.write(
            self.style.SUCCESS('🎯 CRISP Asset-Based Alert System Demo')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 50)
        )

        try:
            if mode in ['setup', 'full']:
                if not options['skip_setup']:
                    self.setup_demo_data(options.get('organization'))

            if mode in ['demo', 'full']:
                self.run_demo()

            if mode in ['cleanup', 'full'] and mode != 'full':
                # Only cleanup if explicitly requested, not in full mode
                self.cleanup_demo_data()

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Demo failed: {str(e)}')
            )
            raise

    def setup_demo_data(self, org_name=None):
        """Set up demo data including organization, users, and assets."""
        self.stdout.write('\n📋 Setting up demo data...')

        try:
            with transaction.atomic():
                # Create or get demo organization
                org_name = org_name or "Demo University"
                organization, created = Organization.objects.get_or_create(
                    name=org_name,
                    defaults={
                        'description': 'Demo organization for asset-based alert testing',
                        'organization_type': 'educational',
                        'contact_email': 'security@demouniversity.edu',
                        'website': 'https://demo.university.edu',
                        'domain': 'demo.university.edu',
                        'is_active': True,
                        'is_verified': True,
                        'trust_metadata': {
                            'notification_preferences': {
                                'email_enabled': True,
                                'sms_enabled': True,
                                'slack_enabled': True,
                                'webhook_enabled': True,
                                'servicenow_enabled': False,
                                'jira_enabled': False
                            }
                        }
                    }
                )

                if created:
                    self.stdout.write(f'✅ Created organization: {organization.name}')
                else:
                    self.stdout.write(f'📍 Using existing organization: {organization.name}')

                # Create demo user if needed
                demo_user, user_created = User.objects.get_or_create(
                    username='demo_security_admin',
                    defaults={
                        'email': 'security@demouniversity.edu',
                        'first_name': 'Demo',
                        'last_name': 'Admin',
                        'organization': organization,
                        'role': 'publisher',
                        'is_active': True
                    }
                )

                if user_created:
                    demo_user.set_password('demo123')
                    demo_user.save()
                    self.stdout.write(f'✅ Created demo user: {demo_user.username}')
                else:
                    self.stdout.write(f'📍 Using existing user: {demo_user.username}')

                # Create sample assets
                demo_assets = [
                    {
                        'name': 'Main Web Server',
                        'asset_type': 'ip_range',
                        'asset_value': '192.168.1.10/32',
                        'criticality': 'critical',
                        'description': 'Primary web server hosting university portal'
                    },
                    {
                        'name': 'Student Database Server',
                        'asset_type': 'ip_range',
                        'asset_value': '10.0.100.50/32',
                        'criticality': 'critical',
                        'description': 'Database server containing student information'
                    },
                    {
                        'name': 'University Domain',
                        'asset_type': 'domain',
                        'asset_value': 'demo.university.edu',
                        'criticality': 'high',
                        'description': 'Main university domain'
                    },
                    {
                        'name': 'Student Portal',
                        'asset_type': 'subdomain',
                        'asset_value': 'portal.demo.university.edu',
                        'criticality': 'high',
                        'description': 'Student information system portal'
                    },
                    {
                        'name': 'Email System',
                        'asset_type': 'service',
                        'asset_value': 'mail.demo.university.edu',
                        'criticality': 'high',
                        'description': 'University email system'
                    },
                    {
                        'name': 'Research Network',
                        'asset_type': 'ip_range',
                        'asset_value': '172.16.0.0/24',
                        'criticality': 'medium',
                        'description': 'Research department network segment'
                    },
                    {
                        'name': 'WordPress CMS',
                        'asset_type': 'software',
                        'asset_value': 'WordPress 6.3',
                        'criticality': 'medium',
                        'description': 'Content management system for university website'
                    },
                    {
                        'name': 'Development Environment',
                        'asset_type': 'ip_range',
                        'asset_value': '192.168.10.0/24',
                        'criticality': 'low',
                        'environment': 'development',
                        'description': 'Development and testing environment'
                    }
                ]

                created_assets = 0
                for asset_data in demo_assets:
                    asset, asset_created = AssetInventory.objects.get_or_create(
                        organization=organization,
                        name=asset_data['name'],
                        asset_type=asset_data['asset_type'],
                        defaults={
                            'asset_value': asset_data['asset_value'],
                            'criticality': asset_data['criticality'],
                            'description': asset_data['description'],
                            'environment': asset_data.get('environment', 'production'),
                            'created_by': demo_user,
                            'alert_enabled': True,
                            'alert_channels': ['email', 'slack']
                        }
                    )

                    if asset_created:
                        asset.generate_fingerprints()
                        created_assets += 1

                self.stdout.write(f'✅ Created {created_assets} new assets')

                # Create sample threat indicators
                sample_indicators = [
                    {
                        'type': 'ipv4-addr',
                        'pattern': '[ipv4-addr:value = \'192.168.1.10\']',
                        'value': '192.168.1.10',
                        'labels': ['malicious-activity', 'web-server-attack']
                    },
                    {
                        'type': 'domain-name',
                        'pattern': '[domain-name:value = \'demo.university.edu\']',
                        'value': 'demo.university.edu',
                        'labels': ['phishing', 'education-sector']
                    },
                    {
                        'type': 'domain-name',
                        'pattern': '[domain-name:value = \'portal.demo.university.edu\']',
                        'value': 'portal.demo.university.edu',
                        'labels': ['credential-theft', 'student-portal']
                    },
                    {
                        'type': 'software',
                        'pattern': '[software:name = \'WordPress\' AND software:version = \'6.3\']',
                        'value': 'WordPress 6.3',
                        'labels': ['vulnerability', 'cms-exploit']
                    },
                    {
                        'type': 'ipv4-addr',
                        'pattern': '[ipv4-addr:value = \'172.16.0.100\']',
                        'value': '172.16.0.100',
                        'labels': ['lateral-movement', 'research-network']
                    }
                ]

                # Get or create a demo threat feed
                demo_feed, feed_created = ThreatFeed.objects.get_or_create(
                    name='Demo Threat Feed',
                    defaults={
                        'description': 'Demo threat feed for asset-based alert testing',
                        'owner': organization,
                        'is_external': False,
                        'is_public': True
                    }
                )

                created_indicators = 0
                for indicator_data in sample_indicators:
                    indicator, indicator_created = Indicator.objects.get_or_create(
                        type=indicator_data['type'],
                        value=indicator_data['value'],
                        threat_feed=demo_feed,
                        defaults={
                            'name': f"Demo {indicator_data['type']} indicator",
                            'description': f"Demo indicator for {indicator_data['value']}",
                            'confidence': 85,
                            'stix_id': f"indicator--{uuid.uuid4()}",
                            'first_seen': timezone.now(),
                            'last_seen': timezone.now()
                        }
                    )

                    if indicator_created:
                        created_indicators += 1

                self.stdout.write(f'✅ Created {created_indicators} new threat indicators')

                self.stdout.write(
                    self.style.SUCCESS(f'\n🎉 Demo data setup complete!')
                )
                self.stdout.write(f'   Organization: {organization.name}')
                self.stdout.write(f'   Assets: {AssetInventory.objects.filter(organization=organization).count()}')
                self.stdout.write(f'   Indicators: {Indicator.objects.filter(threat_feed=demo_feed).count()}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up demo data: {str(e)}')
            )
            raise

    def run_demo(self):
        """Run the asset-based alert correlation demo."""
        self.stdout.write('\n🔍 Running asset-based alert correlation demo...')

        try:
            # Get demo organization
            demo_org = Organization.objects.filter(
                name__icontains='demo'
            ).first()

            if not demo_org:
                self.stdout.write(
                    self.style.ERROR('No demo organization found. Run setup first.')
                )
                return

            # Get recent indicators
            recent_indicators = Indicator.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-created_at')

            if not recent_indicators.exists():
                self.stdout.write(
                    self.style.WARNING('No recent indicators found. Creating some now...')
                )
                # Create some indicators on the fly for demo
                self._create_demo_indicators(demo_org)
                recent_indicators = Indicator.objects.filter(
                    created_at__gte=timezone.now() - timedelta(minutes=5)
                )

            self.stdout.write(f'📊 Processing {recent_indicators.count()} indicators...')

            # Initialize asset alert service
            alert_service = AssetBasedAlertService()

            # Process indicators for the demo organization
            generated_alerts = alert_service.process_indicators_for_organization(
                list(recent_indicators), demo_org
            )

            self.stdout.write(
                self.style.SUCCESS(f'🚨 Generated {len(generated_alerts)} custom alerts!')
            )

            # Display alert details
            for alert in generated_alerts:
                self._display_alert_details(alert)

            # Show statistics
            self._display_statistics(demo_org, alert_service)

            # Demonstrate alert management
            if generated_alerts:
                self._demonstrate_alert_management(generated_alerts[0])

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running demo: {str(e)}')
            )
            raise

    def _create_demo_indicators(self, organization):
        """Create some demo indicators for immediate testing."""
        demo_feed = ThreatFeed.objects.filter(
            name='Demo Threat Feed'
        ).first()

        if not demo_feed:
            demo_feed = ThreatFeed.objects.create(
                name='Demo Threat Feed',
                description='Demo threat feed',
                owner=organization,
                is_external=False,
                is_active=True
            )

        # Create indicators that will match demo assets
        demo_indicators = [
            {
                'type': 'ipv4-addr',
                'pattern': '[ipv4-addr:value = \'192.168.1.10\']',
                'value': '192.168.1.10',
                'labels': ['targeted-attack', 'web-server']
            },
            {
                'type': 'domain-name',
                'pattern': '[domain-name:value = \'demo.university.edu\']',
                'value': 'demo.university.edu',
                'labels': ['phishing', 'domain-spoofing']
            }
        ]

        for indicator_data in demo_indicators:
            Indicator.objects.create(
                type=indicator_data['type'],
                value=indicator_data['value'],
                name=f"Demo {indicator_data['type']} indicator",
                description=f"Demo indicator for {indicator_data['value']}",
                confidence=90,
                threat_feed=demo_feed,
                stix_id=f"indicator--{uuid.uuid4()}",
                first_seen=timezone.now(),
                last_seen=timezone.now()
            )

    def _display_alert_details(self, alert):
        """Display detailed information about a generated alert."""
        self.stdout.write(f'\n📋 Alert Details:')
        self.stdout.write(f'   ID: {alert.alert_id}')
        self.stdout.write(f'   Title: {alert.title}')
        self.stdout.write(f'   Severity: {alert.severity.upper()}')
        self.stdout.write(f'   Status: {alert.status}')
        self.stdout.write(f'   Confidence: {round(alert.confidence_score * 100)}%')
        self.stdout.write(f'   Relevance: {round(alert.relevance_score * 100)}%')

        # Show matched assets
        matched_assets = alert.matched_assets.all()
        self.stdout.write(f'   Matched Assets ({matched_assets.count()}):')
        for asset in matched_assets:
            self.stdout.write(f'     • {asset.name} ({asset.get_criticality_display()})')

        # Show delivery channels
        if alert.delivery_channels:
            self.stdout.write(f'   Delivery Channels: {", ".join(alert.delivery_channels)}')

        # Show response actions
        if alert.response_actions:
            self.stdout.write(f'   Response Actions: {len(alert.response_actions)} recommended')

    def _display_statistics(self, organization, alert_service):
        """Display statistics about the alert system."""
        self.stdout.write(f'\n📈 Statistics:')

        try:
            stats = alert_service.get_alert_statistics(organization)

            self.stdout.write(f'   Total Assets: {AssetInventory.objects.filter(organization=organization).count()}')
            self.stdout.write(f'   Alert-Enabled Assets: {AssetInventory.objects.filter(organization=organization, alert_enabled=True).count()}')
            self.stdout.write(f'   Total Alerts Generated: {stats.get("total_alerts", 0)}')
            self.stdout.write(f'   Recent Alerts (30d): {stats.get("recent_alerts", 0)}')
            self.stdout.write(f'   Average Confidence: {stats.get("avg_confidence", 0)}%')
            self.stdout.write(f'   Average Relevance: {stats.get("avg_relevance", 0)}%')

            # Show alerts by severity
            by_severity = stats.get('by_severity', {})
            if by_severity:
                self.stdout.write(f'   Alerts by Severity:')
                for severity, count in by_severity.items():
                    if count > 0:
                        self.stdout.write(f'     • {severity.title()}: {count}')

        except Exception as e:
            self.stdout.write(f'   Error getting statistics: {str(e)}')

    def _demonstrate_alert_management(self, alert):
        """Demonstrate alert management operations."""
        self.stdout.write(f'\n🔧 Demonstrating alert management...')

        try:
            # Acknowledge the alert
            self.stdout.write(f'   Acknowledging alert {alert.alert_id}...')
            alert.acknowledge()
            self.stdout.write(f'   ✅ Alert acknowledged at {alert.acknowledged_at}')

            # Show asset summary
            asset_summary = alert.get_asset_summary()
            self.stdout.write(f'   Asset Summary:')
            self.stdout.write(f'     Total: {asset_summary["total_count"]}')

            for criticality, count in asset_summary.get('by_criticality', {}).items():
                self.stdout.write(f'     {criticality.title()}: {count}')

        except Exception as e:
            self.stdout.write(f'   Error in alert management demo: {str(e)}')

    def cleanup_demo_data(self):
        """Clean up demo data."""
        self.stdout.write(f'\n🧹 Cleaning up demo data...')

        try:
            with transaction.atomic():
                # Delete demo alerts
                demo_alerts = CustomAlert.objects.filter(
                    organization__name__icontains='demo'
                )
                alert_count = demo_alerts.count()
                demo_alerts.delete()
                self.stdout.write(f'   Deleted {alert_count} demo alerts')

                # Delete demo assets
                demo_assets = AssetInventory.objects.filter(
                    organization__name__icontains='demo'
                )
                asset_count = demo_assets.count()
                demo_assets.delete()
                self.stdout.write(f'   Deleted {asset_count} demo assets')

                # Delete demo indicators
                demo_indicators = Indicator.objects.filter(
                    feed__name__icontains='demo'
                )
                indicator_count = demo_indicators.count()
                demo_indicators.delete()
                self.stdout.write(f'   Deleted {indicator_count} demo indicators')

                # Delete demo feeds
                demo_feeds = ThreatFeed.objects.filter(
                    name__icontains='demo'
                )
                feed_count = demo_feeds.count()
                demo_feeds.delete()
                self.stdout.write(f'   Deleted {feed_count} demo feeds')

                # Optionally delete demo organization and user
                demo_orgs = Organization.objects.filter(
                    name__icontains='demo'
                )
                for org in demo_orgs:
                    # Delete associated users
                    user_count = User.objects.filter(organization=org).count()
                    User.objects.filter(organization=org).delete()
                    self.stdout.write(f'   Deleted {user_count} demo users')

                org_count = demo_orgs.count()
                demo_orgs.delete()
                self.stdout.write(f'   Deleted {org_count} demo organizations')

                self.stdout.write(
                    self.style.SUCCESS(f'🎉 Demo cleanup complete!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error cleaning up demo data: {str(e)}')
            )
            raise