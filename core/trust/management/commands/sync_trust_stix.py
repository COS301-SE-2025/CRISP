from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from ...integrations.stix_taxii_integration import stix_taxii_trust_integration
from ...patterns.repository.trust_repository import trust_repository_manager
from ...patterns.factory.stix_trust_factory import stix_trust_factory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronize trust management data with STIX/TAXII servers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--export',
            action='store_true',
            help='Export trust data to STIX/TAXII',
        )
        parser.add_argument(
            '--import',
            action='store_true',
            dest='import_data',
            help='Import trust data from STIX/TAXII',
        )
        parser.add_argument(
            '--organization',
            type=str,
            help='Specific organization to sync',
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='Number of days to look back for updates',
        )
        parser.add_argument(
            '--collection-id',
            type=str,
            help='TAXII collection ID to use',
        )

    def handle(self, *args, **options):
        if options['export']:
            self.export_trust_data(options)
        
        if options['import_data']:
            self.import_trust_data(options)
        
        if not options['export'] and not options['import_data']:
            self.stdout.write(
                self.style.WARNING('No action specified. Use --export or --import')
            )

    def export_trust_data(self, options):
        """Export trust data to STIX/TAXII."""
        self.stdout.write('Starting trust data export to STIX/TAXII...')
        
        organization = options.get('organization')
        collection_id = options.get('collection_id')
        
        try:
            if organization:
                # Export for specific organization
                self.export_organization_data(organization, collection_id)
            else:
                # Export all active trust relationships
                self.export_all_data(collection_id)
            
            self.stdout.write(
                self.style.SUCCESS('Trust data export completed successfully')
            )
            
        except Exception as e:
            logger.error(f"Trust data export failed: {str(e)}")
            raise CommandError(f"Export failed: {str(e)}")

    def export_organization_data(self, organization, collection_id):
        """Export trust data for specific organization."""
        # Get trust relationships
        relationships = trust_repository_manager.relationships.get_for_organization(
            organization, include_inactive=False
        )
        
        # Get trust groups
        groups = trust_repository_manager.groups.get_groups_for_organization(
            organization, include_inactive=False
        )
        
        exported_count = 0
        
        # Export relationships
        for relationship in relationships:
            try:
                stix_object = stix_taxii_trust_integration.export_trust_relationship_to_stix(
                    relationship,
                    export_config={
                        'validate': True,
                        'enrich': True,
                        'prepare_for_taxii': True
                    }
                )
                
                if stix_taxii_trust_integration.publish_to_taxii_server(
                    stix_object, collection_id
                ):
                    exported_count += 1
                    self.stdout.write(f"Exported relationship: {relationship.id}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Failed to export relationship {relationship.id}: {str(e)}")
                )
        
        # Export groups
        for group in groups:
            try:
                stix_object = stix_taxii_trust_integration.export_trust_group_to_stix(
                    group,
                    export_config={
                        'validate': True,
                        'enrich': True,
                        'prepare_for_taxii': True,
                        'include_members': True
                    }
                )
                
                if stix_taxii_trust_integration.publish_to_taxii_server(
                    stix_object, collection_id
                ):
                    exported_count += 1
                    self.stdout.write(f"Exported group: {group.id}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Failed to export group {group.id}: {str(e)}")
                )
        
        self.stdout.write(f"Exported {exported_count} trust objects for organization {organization}")

    def export_all_data(self, collection_id):
        """Export all trust data."""
        # Get all active relationships
        relationships = trust_repository_manager.relationships.get_all(include_inactive=False)
        
        # Get all active groups
        groups = trust_repository_manager.groups.get_all(include_inactive=False)
        
        # Get all active trust levels
        levels = trust_repository_manager.levels.get_all(include_inactive=False)
        
        # Create bundle with all entities
        all_entities = list(relationships) + list(groups) + list(levels)
        
        if all_entities:
            try:
                bundle = stix_trust_factory.create_bundle(
                    all_entities,
                    created_by="CRISP Trust Management System",
                    bundle_type="trust-intelligence-export"
                )
                
                if stix_taxii_trust_integration.publish_to_taxii_server(
                    bundle, collection_id
                ):
                    self.stdout.write(f"Exported bundle with {len(all_entities)} trust objects")
                else:
                    self.stdout.write(
                        self.style.WARNING("Failed to publish trust bundle to TAXII server")
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Failed to create/export trust bundle: {str(e)}")
                )

    def import_trust_data(self, options):
        """Import trust data from STIX/TAXII."""
        self.stdout.write('Starting trust data import from STIX/TAXII...')
        
        collection_id = options.get('collection_id')
        days_back = options.get('days_back', 7)
        organization = options.get('organization', 'import-system')
        
        try:
            # Calculate added_after timestamp
            added_after = timezone.now() - timedelta(days=days_back)
            
            # Fetch trust objects from TAXII server
            trust_objects = stix_taxii_trust_integration.fetch_trust_intelligence_from_taxii(
                collection_id, added_after
            )
            
            imported_count = 0
            
            for stix_object in trust_objects:
                try:
                    # Import trust relationship
                    if self._is_trust_relationship(stix_object):
                        relationship = stix_taxii_trust_integration.import_trust_relationship_from_stix(
                            stix_object, organization
                        )
                        if relationship:
                            imported_count += 1
                            self.stdout.write(f"Imported relationship: {relationship.id}")
                    
                    # Additional import logic for groups and levels would go here
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to import STIX object {stix_object.get('id')}: {str(e)}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Import completed. Imported {imported_count} trust objects')
            )
            
        except Exception as e:
            logger.error(f"Trust data import failed: {str(e)}")
            raise CommandError(f"Import failed: {str(e)}")

    def _is_trust_relationship(self, stix_object):
        """Check if STIX object is a trust relationship."""
        return (
            stix_object.get('type') == 'x-crisp-trust-relationship' or
            'x_crisp_trust_relationship' in stix_object
        )