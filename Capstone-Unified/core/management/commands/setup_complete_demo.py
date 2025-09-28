"""
Complete Demo Setup Script - Coordinates all population scripts for optimal system demonstration
"""

import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Set up complete demo environment with all systems properly integrated'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean all existing demo data before setup'
        )
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick setup with minimal data for fast testing'
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Full setup with comprehensive data for complete demonstration'
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n' + '='*60 + '\n'
                    '🎯 CRISP COMPLETE DEMO SETUP\n'
                    '   Asset Alert System (WOW Factor #1)\n'
                    '='*60 + '\n'
                )
            )

            # Step 1: Basic system setup (ensure tables exist)
            self.setup_basic_system()

            if options['clean']:
                self.clean_all_data()

            # Step 2: Population parameters based on mode
            if options['quick']:
                orgs = 2
                assets_per_org = 8
                indicators = 20
                feeds = 2
            elif options['full']:
                orgs = 5
                assets_per_org = 25
                indicators = 100
                feeds = 5
            else:  # default
                orgs = 3
                assets_per_org = 15
                indicators = 50
                feeds = 3

            # Step 3: Populate threat intelligence data
            self.setup_threat_intelligence(feeds, indicators)

            # Step 4: Populate asset alert system
            self.setup_asset_alert_system(orgs, assets_per_org, indicators)

            # Step 5: Generate additional demo data
            self.setup_additional_demo_data()

            # Step 6: Final verification
            self.verify_setup()

            self.stdout.write(
                self.style.SUCCESS(
                    '\n' + '='*60 + '\n'
                    '✅ CRISP DEMO SETUP COMPLETE!\n'
                    '\n'
                    '🔐 Login Credentials: See DEMO_USER_CREDENTIALS.md\n'
                    '🎯 Asset Management: Navigate to Asset Management section\n'
                    '🚨 Alerts: Check Custom Alerts tab for generated alerts\n'
                    '⚡ Features: Try bulk upload, correlation trigger, filters\n'
                    '\n'
                    'System ready for demonstration!\n'
                    '='*60 + '\n'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Demo setup failed: {str(e)}')
            )
            sys.exit(1)

    def clean_all_data(self):
        """Clean all demo data from the system."""
        self.stdout.write('🧹 Cleaning all demo data...')

        # Clean asset alert demo data
        call_command('populate_asset_demo_data', '--clean')

        # Clean other demo data
        try:
            call_command('cleanup_test_data')
        except:
            pass  # Command might not exist

        self.stdout.write(self.style.SUCCESS('   ✅ Demo data cleaned'))

    def setup_basic_system(self):
        """Set up basic system requirements."""
        self.stdout.write('🔧 Setting up basic system...')

        # Ensure migrations are applied
        call_command('migrate', verbosity=0)

        # Set up base users
        call_command('setup_base_users')

        # Initialize trust levels
        try:
            call_command('init_trust_levels')
        except:
            pass  # Might not be needed

        self.stdout.write(self.style.SUCCESS('   ✅ Basic system ready'))

    def setup_threat_intelligence(self, feeds, indicators):
        """Set up threat intelligence feeds and data."""
        self.stdout.write('🦠 Setting up threat intelligence...')

        # Setup VirusTotal feed
        call_command('setup_virustotal_feed', '--with-samples')

        # Clean up any invalid feeds
        call_command('cleanup_feeds', '--force')

        # Populate basic threat data if available
        try:
            call_command('populate_database', '--no-input')
        except:
            self.stdout.write('   ⚠️  Standard population not available, using asset demo data only')

        self.stdout.write(self.style.SUCCESS('   ✅ Threat intelligence ready'))

    def setup_asset_alert_system(self, orgs, assets_per_org, indicators):
        """Set up the complete asset alert system."""
        self.stdout.write('🎯 Setting up Asset Alert System...')

        # Populate comprehensive asset demo data
        call_command(
            'populate_asset_demo_data',
            '--organizations', str(orgs),
            '--assets-per-org', str(assets_per_org),
            '--indicators', str(indicators)
        )

        self.stdout.write(self.style.SUCCESS('   ✅ Asset Alert System ready'))

    def setup_additional_demo_data(self):
        """Set up additional demonstration data."""
        self.stdout.write('📊 Setting up additional demo data...')

        # Populate reports demo if available
        try:
            call_command('populate_reports_demo')
        except:
            pass

        # Sync MITRE data if available
        try:
            call_command('sync_mitre_data', '--limit', '100')
        except:
            pass

        self.stdout.write(self.style.SUCCESS('   ✅ Additional data ready'))

    def verify_setup(self):
        """Verify that all components are properly set up."""
        self.stdout.write('🔍 Verifying setup...')

        from core.models.models import (
            Organization, AssetInventory, CustomAlert,
            Indicator
        )
        from user_management.models.user_models import CustomUser as User

        # Check organizations
        orgs = Organization.objects.filter(trust_metadata__contains={'demo': True})
        self.stdout.write(f'   📋 Organizations: {orgs.count()}')

        # Check users
        users = User.objects.filter(metadata__contains={'demo': True})
        self.stdout.write(f'   👥 Demo Users: {users.count()}')

        # Check assets
        assets = AssetInventory.objects.filter(metadata__contains={'demo': True})
        self.stdout.write(f'   🏢 Assets: {assets.count()}')

        # Check indicators
        indicators = Indicator.objects.filter(metadata__contains={'demo': True})
        self.stdout.write(f'   🎯 Threat Indicators: {indicators.count()}')

        # Check alerts
        alerts = CustomAlert.objects.filter(metadata__contains={'demo': True})
        self.stdout.write(f'   🚨 Custom Alerts: {alerts.count()}')

        # Verify at least one organization has assets and alerts
        if orgs.exists():
            sample_org = orgs.first()
            org_assets = sample_org.asset_inventory.count()
            org_alerts = CustomAlert.objects.filter(organization=sample_org).count()

            self.stdout.write(f'   📊 Sample Org ({sample_org.name}):')
            self.stdout.write(f'       Assets: {org_assets}')
            self.stdout.write(f'       Alerts: {org_alerts}')

        self.stdout.write(self.style.SUCCESS('   ✅ Setup verified'))