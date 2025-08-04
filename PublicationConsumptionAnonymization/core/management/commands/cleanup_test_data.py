from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from core.models.models import (
    Collection, Organization, STIXObject, ThreatFeed, 
    Indicator, TTPData, Institution, CollectionObject
)


class Command(BaseCommand):
    help = 'Clean up test data from database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Only delete objects with test patterns',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Custom pattern to match for deletion (e.g., "test-", "temp-")',
            default='test'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        if options['test_only']:
            self.cleanup_test_objects(
                dry_run=options['dry_run'],
                force=options['force'],
                pattern=options['pattern']
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Use --test-only flag to clean test data. '
                    'This prevents accidental deletion of production data.'
                )
            )

    def cleanup_test_objects(self, dry_run=False, force=False, pattern='test'):
        """Clean up test objects based on naming patterns"""
        self.stdout.write(f'Searching for test objects with pattern: "{pattern}"')
        
        cleanup_operations = [
            ('CollectionObject', CollectionObject, None),
            ('Collection (test aliases)', Collection, {'alias__icontains': pattern}),
            ('STIXObject (test IDs)', STIXObject, {'stix_id__icontains': pattern}),
            ('Indicator (test feeds)', Indicator, {'threat_feed__name__icontains': pattern}),
            ('TTPData (test feeds)', TTPData, {'threat_feed__name__icontains': pattern}),
            ('ThreatFeed (test names)', ThreatFeed, {'name__icontains': pattern}),
            ('Institution (test names)', Institution, {'name__icontains': pattern}),
            ('Organization (test names)', Organization, {'name__icontains': pattern}),
            ('User (test usernames)', User, {'username__icontains': pattern}),
        ]
        
        # Count objects to be deleted
        total_count = 0
        operation_counts = {}
        
        for name, model, filters in cleanup_operations:
            if filters:
                count = model.objects.filter(**filters).count()
            else:
                count = model.objects.count()
            
            operation_counts[name] = count
            total_count += count
            
            if count > 0:
                self.stdout.write(f'  {name}: {count} objects')
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No test objects found to clean up.'))
            return
        
        self.stdout.write(f'\nTotal objects to be deleted: {total_count}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN - No objects were actually deleted.')
            )
            return
        
        # Confirm deletion
        if not force:
            confirm = input(f'\nDelete {total_count} test objects? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Deletion cancelled.')
                return
        
        try:
            with transaction.atomic():
                deleted_counts = {}
                
                for name, model, filters in cleanup_operations:
                    if operation_counts[name] > 0:
                        if filters:
                            count, _ = model.objects.filter(**filters).delete()
                        else:
                            count, _ = model.objects.all().delete()
                        
                        deleted_counts[name] = count
                        self.stdout.write(f'  Deleted {count} {name} objects')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted {sum(deleted_counts.values())} test objects.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cleanup: {str(e)}')
            )
            raise CommandError(f'Cleanup failed: {str(e)}')

    def cleanup_specific_test_run(self, test_id):
        """Clean up objects from a specific test run."""
        self.stdout.write(f'Cleaning up test run: {test_id}')
        
        patterns = [
            f'_{test_id}',
            f'-{test_id}',
            f'{test_id}_',
            f'{test_id}-'
        ]
        
        total_deleted = 0
        
        for pattern in patterns:
            # Collections
            collections = Collection.objects.filter(alias__icontains=pattern)
            count = collections.count()
            if count > 0:
                collections.delete()
                total_deleted += count
                self.stdout.write(f'  Deleted {count} collections with pattern "{pattern}"')
            
            # Organizations
            orgs = Organization.objects.filter(name__icontains=pattern)
            count = orgs.count()
            if count > 0:
                orgs.delete()
                total_deleted += count
                self.stdout.write(f'  Deleted {count} organizations with pattern "{pattern}"')
            
            # Users
            users = User.objects.filter(username__icontains=pattern)
            count = users.count()
            if count > 0:
                users.delete()
                total_deleted += count
                self.stdout.write(f'  Deleted {count} users with pattern "{pattern}"')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cleaned up {total_deleted} objects from test run {test_id}'
            )
        )

    def cleanup_orphaned_objects(self):
        """Clean up orphaned test objects."""
        self.stdout.write('Cleaning up orphaned objects...')
        
        orphaned_count = 0
        
        # STIXObjects without source organization
        orphaned_stix = STIXObject.objects.filter(source_organization__isnull=True)
        count = orphaned_stix.count()
        if count > 0:
            orphaned_stix.delete()
            orphaned_count += count
            self.stdout.write(f'  Deleted {count} orphaned STIX objects')
        
        # Collections without owner
        orphaned_collections = Collection.objects.filter(owner__isnull=True)
        count = orphaned_collections.count()
        if count > 0:
            orphaned_collections.delete()
            orphaned_count += count
            self.stdout.write(f'  Deleted {count} orphaned collections')
        
        # ThreatFeeds without owner
        orphaned_feeds = ThreatFeed.objects.filter(owner__isnull=True)
        count = orphaned_feeds.count()
        if count > 0:
            orphaned_feeds.delete()
            orphaned_count += count
            self.stdout.write(f'  Deleted {count} orphaned threat feeds')
        
        # Indicators without threat feed
        orphaned_indicators = Indicator.objects.filter(threat_feed__isnull=True)
        count = orphaned_indicators.count()
        if count > 0:
            orphaned_indicators.delete()
            orphaned_count += count
            self.stdout.write(f'  Deleted {count} orphaned indicators')
        
        # TTPs without threat feed
        orphaned_ttps = TTPData.objects.filter(threat_feed__isnull=True)
        count = orphaned_ttps.count()
        if count > 0:
            orphaned_ttps.delete()
            orphaned_count += count
            self.stdout.write(f'  Deleted {count} orphaned TTPs')
        
        if orphaned_count == 0:
            self.stdout.write('No orphaned objects found.')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Cleaned up {orphaned_count} orphaned objects.')
            )

    def reset_test_database(self):
        """Reset the entire test database (dangerous!)."""
        self.stdout.write(
            self.style.WARNING(
                'This will delete ALL data from the database!'
            )
        )
        
        confirm = input('Are you absolutely sure? Type "RESET" to confirm: ')
        if confirm != 'RESET':
            self.stdout.write('Reset cancelled.')
            return
        
        try:
            with transaction.atomic():
                # Delete all data in reverse dependency order
                CollectionObject.objects.all().delete()
                Collection.objects.all().delete()
                STIXObject.objects.all().delete()
                Indicator.objects.all().delete()
                TTPData.objects.all().delete()
                ThreatFeed.objects.all().delete()
                Institution.objects.all().delete()
                Organization.objects.all().delete()
                
                # Keep superuser accounts
                User.objects.filter(is_superuser=False).delete()
                
                self.stdout.write(
                    self.style.SUCCESS('Database reset completed.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Reset failed: {str(e)}')
            )

    def get_test_data_statistics(self):
        """Get statistics about test data in the database"""
        self.stdout.write('Test Data Statistics:')
        self.stdout.write('=' * 50)
        
        # Count test objects
        test_patterns = ['test', 'temp', 'mock', 'fake']
        
        for pattern in test_patterns:
            self.stdout.write(f'\nObjects containing "{pattern}":')
            
            collections = Collection.objects.filter(alias__icontains=pattern).count()
            organizations = Organization.objects.filter(name__icontains=pattern).count()
            users = User.objects.filter(username__icontains=pattern).count()
            stix_objects = STIXObject.objects.filter(stix_id__icontains=pattern).count()
            threat_feeds = ThreatFeed.objects.filter(name__icontains=pattern).count()
            
            self.stdout.write(f'  Collections: {collections}')
            self.stdout.write(f'  Organizations: {organizations}')
            self.stdout.write(f'  Users: {users}')
            self.stdout.write(f'  STIX Objects: {stix_objects}')
            self.stdout.write(f'  Threat Feeds: {threat_feeds}')
        
        # Total counts
        self.stdout.write('\nTotal Database Counts:')
        self.stdout.write(f'  Collections: {Collection.objects.count()}')
        self.stdout.write(f'  Organizations: {Organization.objects.count()}')
        self.stdout.write(f'  Users: {User.objects.count()}')
        self.stdout.write(f'  STIX Objects: {STIXObject.objects.count()}')
        self.stdout.write(f'  Threat Feeds: {ThreatFeed.objects.count()}')
        self.stdout.write(f'  Indicators: {Indicator.objects.count()}')
        self.stdout.write(f'  TTPs: {TTPData.objects.count()}')