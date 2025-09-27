"""
Management command to test asset monitoring functionality without requiring Celery/Redis.
Provides direct testing of asset alert correlation and monitoring.
"""

import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction

from core.models.models import AssetInventory, Organization, Indicator, CustomAlert
from core.services.asset_alert_service import AssetBasedAlertService


class Command(BaseCommand):
    help = 'Test asset monitoring and alerting functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            type=str,
            help='Specific organization ID to test'
        )

        parser.add_argument(
            '--hours-back',
            type=int,
            default=24,
            help='Hours back to check for indicators (default: 24)'
        )

        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for demonstration'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']

        try:
            if options['create_test_data']:
                self.create_test_data()

            self.test_asset_validation()
            self.test_asset_correlation(options)
            self.test_alert_generation(options)

            self.stdout.write(
                self.style.SUCCESS('✅ All asset monitoring tests passed!')
            )

        except Exception as e:
            raise CommandError(f'Asset monitoring test failed: {e}')

    def create_test_data(self):
        """Create test data for asset monitoring demonstration"""
        self.stdout.write('Creating test data...')

        # Get or create test organization
        org, created = Organization.objects.get_or_create(
            name='Test Security Org',
            defaults={
                'description': 'Test organization for asset monitoring',
                'organization_type': 'private',
                'is_active': True,
                'is_verified': True,
            }
        )

        if created:
            self.stdout.write(f'Created test organization: {org.name}')

        # Create test assets
        test_assets = [
            {
                'name': 'Production Web Server',
                'asset_type': 'ip_range',
                'asset_value': '192.168.1.100',
                'criticality': 'critical',
                'environment': 'production',
            },
            {
                'name': 'Company Website',
                'asset_type': 'domain',
                'asset_value': 'example.com',
                'criticality': 'high',
                'environment': 'production',
            },
            {
                'name': 'Email Domain',
                'asset_type': 'email_domain',
                'asset_value': 'company.com',
                'criticality': 'high',
                'environment': 'production',
            },
            {
                'name': 'Apache Web Server',
                'asset_type': 'software',
                'asset_value': 'Apache HTTP Server 2.4',
                'criticality': 'medium',
                'environment': 'production',
            },
        ]

        # Get test user (create if needed)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        test_user, _ = User.objects.get_or_create(
            username='testadmin',
            defaults={
                'email': 'test@example.com',
                'organization': org,
                'role': 'BlueVisionAdmin',
                'is_active': True,
            }
        )

        created_assets = 0
        for asset_data in test_assets:
            asset, created = AssetInventory.objects.get_or_create(
                organization=org,
                asset_value=asset_data['asset_value'],
                asset_type=asset_data['asset_type'],
                defaults={
                    'name': asset_data['name'],
                    'criticality': asset_data['criticality'],
                    'environment': asset_data['environment'],
                    'created_by': test_user,
                    'alert_enabled': True,
                }
            )
            if created:
                created_assets += 1
                asset.generate_fingerprints()

        self.stdout.write(f'Created {created_assets} test assets')

        # Create test indicators
        test_indicators = [
            {
                'type': 'domain',
                'value': 'malicious.example.com',
                'name': 'Malicious Domain Indicator',
            },
            {
                'type': 'ip',
                'value': '192.168.1.100',
                'name': 'Suspicious IP Address',
            },
            {
                'type': 'process',
                'value': 'apache',
                'name': 'Apache Process Indicator',
            },
        ]

        from core.models.models import ThreatFeed
        test_feed, _ = ThreatFeed.objects.get_or_create(
            name='Test Feed',
            defaults={
                'taxii_server_url': 'http://test.feed',
                'description': 'Test feed for asset monitoring',
                'is_active': True,
                'owner': org,
            }
        )

        created_indicators = 0
        for ind_data in test_indicators:
            indicator, created = Indicator.objects.get_or_create(
                value=ind_data['value'],
                type=ind_data['type'],
                defaults={
                    'name': ind_data['name'],
                    'threat_feed': test_feed,
                    'confidence': 85,
                    'stix_id': f"indicator--{uuid.uuid4()}",
                    'first_seen': timezone.now(),
                    'last_seen': timezone.now(),
                }
            )
            if created:
                created_indicators += 1

        self.stdout.write(f'Created {created_indicators} test indicators')

    def test_asset_validation(self):
        """Test asset inventory validation"""
        self.stdout.write('Testing asset validation...')

        # Count assets
        total_assets = AssetInventory.objects.count()
        alert_enabled = AssetInventory.objects.filter(alert_enabled=True).count()
        critical_assets = AssetInventory.objects.filter(criticality='critical').count()

        self.stdout.write(f'  • Total assets: {total_assets}')
        self.stdout.write(f'  • Alert-enabled assets: {alert_enabled}')
        self.stdout.write(f'  • Critical assets: {critical_assets}')

        # Check for assets without fingerprints
        no_fingerprints = AssetInventory.objects.filter(fingerprints__isnull=True).count()
        if no_fingerprints > 0:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  {no_fingerprints} assets missing fingerprints')
            )

        # Update fingerprints for assets that need them
        updated_count = 0
        for asset in AssetInventory.objects.filter(fingerprints__isnull=True)[:10]:
            asset.generate_fingerprints()
            updated_count += 1

        if updated_count > 0:
            self.stdout.write(f'  • Updated fingerprints for {updated_count} assets')

        self.stdout.write('✅ Asset validation completed')

    def test_asset_correlation(self, options):
        """Test asset-indicator correlation"""
        self.stdout.write('Testing asset-indicator correlation...')

        hours_back = options['hours_back']
        organization_id = options.get('organization')

        # Get recent indicators
        cutoff_time = timezone.now() - timedelta(hours=hours_back)
        recent_indicators = Indicator.objects.filter(
            created_at__gte=cutoff_time
        ).order_by('-created_at')[:50]

        if not recent_indicators.exists():
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  No indicators found in last {hours_back} hours')
            )
            return

        self.stdout.write(f'  • Found {recent_indicators.count()} recent indicators')

        # Get organizations to test
        if organization_id:
            organizations = Organization.objects.filter(id=organization_id, is_active=True)
        else:
            organizations = Organization.objects.filter(is_active=True)[:5]  # Limit for testing

        # Test correlation
        alert_service = AssetBasedAlertService()
        total_correlations = 0

        for org in organizations:
            asset_count = AssetInventory.objects.filter(
                organization=org,
                alert_enabled=True
            ).count()

            if asset_count == 0:
                continue

            self.stdout.write(f'  • Testing {org.name} ({asset_count} assets)...')

            # Test each indicator against organization assets
            for indicator in recent_indicators[:10]:  # Limit for testing
                assets = AssetInventory.objects.filter(
                    organization=org,
                    alert_enabled=True
                )

                matched_assets = alert_service._correlate_indicator_with_assets(
                    indicator, list(assets)
                )

                if matched_assets:
                    total_correlations += len(matched_assets)
                    if self.verbose:
                        self.stdout.write(
                            f'    ↳ Indicator {indicator.type}:{indicator.value} '
                            f'matched {len(matched_assets)} assets'
                        )

        self.stdout.write(f'  • Total asset correlations found: {total_correlations}')
        self.stdout.write('✅ Asset correlation testing completed')

    def test_alert_generation(self, options):
        """Test alert generation"""
        self.stdout.write('Testing alert generation...')

        hours_back = options['hours_back']
        organization_id = options.get('organization')

        # Get recent indicators
        cutoff_time = timezone.now() - timedelta(hours=hours_back)
        recent_indicators = list(Indicator.objects.filter(
            created_at__gte=cutoff_time
        ).order_by('-created_at')[:20])

        if not recent_indicators:
            self.stdout.write(
                self.style.WARNING('  ⚠️  No recent indicators for alert testing')
            )
            return

        alert_service = AssetBasedAlertService()

        if organization_id:
            # Test specific organization
            try:
                organization = Organization.objects.get(id=organization_id, is_active=True)
                self.stdout.write(f'  • Testing alerts for {organization.name}...')

                alerts = alert_service.process_indicators_for_organization(
                    recent_indicators, organization
                )

                self.stdout.write(f'  • Generated {len(alerts)} alerts')

                if self.verbose and alerts:
                    for alert in alerts[:3]:  # Show first 3 alerts
                        self.stdout.write(
                            f'    ↳ Alert: {alert.title} (Severity: {alert.severity})'
                        )

            except Organization.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Organization {organization_id} not found')
                )

        else:
            # Test all organizations
            self.stdout.write('  • Testing alerts for all organizations...')

            alerts = alert_service.process_new_indicators(recent_indicators)

            self.stdout.write(f'  • Generated {len(alerts)} total alerts')

            if alerts:
                # Show alert breakdown by organization
                from collections import Counter
                org_counts = Counter(alert.organization.name for alert in alerts)

                for org_name, count in org_counts.most_common(5):
                    self.stdout.write(f'    ↳ {org_name}: {count} alerts')

                # Show severity breakdown
                severity_counts = Counter(alert.severity for alert in alerts)
                self.stdout.write('  • Alert severity breakdown:')
                for severity, count in severity_counts.items():
                    self.stdout.write(f'    ↳ {severity}: {count}')

        self.stdout.write('✅ Alert generation testing completed')

    def show_statistics(self):
        """Show current system statistics"""
        self.stdout.write('\n📊 Current System Statistics:')

        # Asset statistics
        total_assets = AssetInventory.objects.count()
        enabled_assets = AssetInventory.objects.filter(alert_enabled=True).count()
        critical_assets = AssetInventory.objects.filter(criticality='critical').count()

        self.stdout.write(f'Assets: {total_assets} total, {enabled_assets} monitored, {critical_assets} critical')

        # Alert statistics
        total_alerts = CustomAlert.objects.count()
        recent_alerts = CustomAlert.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        self.stdout.write(f'Alerts: {total_alerts} total, {recent_alerts} this week')

        # Organization statistics
        active_orgs = Organization.objects.filter(is_active=True).count()
        self.stdout.write(f'Organizations: {active_orgs} active')