from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ValidationError
import uuid

from ...models import TrustRelationship, TrustGroup, TrustLevel
from ...services.trust_service import TrustService
from ...services.trust_group_service import TrustGroupService


class Command(BaseCommand):
    """
    Management command for managing trust relationships and groups.
    Provides CLI interface for common trust management operations.
    """
    
    help = 'Manage trust relationships and groups via command line'
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Available actions')
        
        # Create relationship
        create_rel_parser = subparsers.add_parser('create-relationship', help='Create trust relationship')
        create_rel_parser.add_argument('--source-org', required=True, help='Source organization UUID')
        create_rel_parser.add_argument('--target-org', required=True, help='Target organization UUID')
        create_rel_parser.add_argument('--trust-level', required=True, help='Trust level name')
        create_rel_parser.add_argument('--type', default='bilateral', help='Relationship type')
        create_rel_parser.add_argument('--notes', help='Additional notes')
        create_rel_parser.add_argument('--created-by', default='system', help='User creating relationship')
        
        # Approve relationship
        approve_parser = subparsers.add_parser('approve-relationship', help='Approve trust relationship')
        approve_parser.add_argument('--relationship-id', required=True, help='Relationship UUID')
        approve_parser.add_argument('--approving-org', required=True, help='Approving organization UUID')
        approve_parser.add_argument('--approved-by', default='system', help='User approving')
        
        # Revoke relationship
        revoke_parser = subparsers.add_parser('revoke-relationship', help='Revoke trust relationship')
        revoke_parser.add_argument('--relationship-id', required=True, help='Relationship UUID')
        revoke_parser.add_argument('--revoking-org', required=True, help='Revoking organization UUID')
        revoke_parser.add_argument('--revoked-by', default='system', help='User revoking')
        revoke_parser.add_argument('--reason', help='Reason for revocation')
        
        # List relationships
        list_rel_parser = subparsers.add_parser('list-relationships', help='List trust relationships')
        list_rel_parser.add_argument('--organization', help='Filter by organization UUID')
        list_rel_parser.add_argument('--status', help='Filter by status')
        list_rel_parser.add_argument('--type', help='Filter by relationship type')
        list_rel_parser.add_argument('--include-inactive', action='store_true', help='Include inactive relationships')
        
        # Create group
        create_group_parser = subparsers.add_parser('create-group', help='Create trust group')
        create_group_parser.add_argument('--name', required=True, help='Group name')
        create_group_parser.add_argument('--description', required=True, help='Group description')
        create_group_parser.add_argument('--creator-org', required=True, help='Creator organization UUID')
        create_group_parser.add_argument('--type', default='community', help='Group type')
        create_group_parser.add_argument('--public', action='store_true', help='Make group public')
        create_group_parser.add_argument('--no-approval', action='store_true', help='No approval required')
        create_group_parser.add_argument('--trust-level', default='Standard Trust', help='Default trust level')
        
        # Join group
        join_group_parser = subparsers.add_parser('join-group', help='Join trust group')
        join_group_parser.add_argument('--group-id', required=True, help='Group UUID')
        join_group_parser.add_argument('--organization', required=True, help='Organization UUID')
        join_group_parser.add_argument('--membership-type', default='member', help='Membership type')
        join_group_parser.add_argument('--invited-by', help='Inviting organization UUID')
        
        # Leave group
        leave_group_parser = subparsers.add_parser('leave-group', help='Leave trust group')
        leave_group_parser.add_argument('--group-id', required=True, help='Group UUID')
        leave_group_parser.add_argument('--organization', required=True, help='Organization UUID')
        leave_group_parser.add_argument('--reason', help='Reason for leaving')
        
        # List groups
        list_groups_parser = subparsers.add_parser('list-groups', help='List trust groups')
        list_groups_parser.add_argument('--organization', help='Filter by member organization UUID')
        list_groups_parser.add_argument('--public-only', action='store_true', help='Show only public groups')
        list_groups_parser.add_argument('--include-inactive', action='store_true', help='Include inactive groups')
        
        # Check trust
        check_trust_parser = subparsers.add_parser('check-trust', help='Check trust level between organizations')
        check_trust_parser.add_argument('--source-org', required=True, help='Source organization UUID')
        check_trust_parser.add_argument('--target-org', required=True, help='Target organization UUID')
        
        # Test access
        test_access_parser = subparsers.add_parser('test-access', help='Test intelligence access')
        test_access_parser.add_argument('--requesting-org', required=True, help='Requesting organization UUID')
        test_access_parser.add_argument('--intelligence-owner', required=True, help='Intelligence owner UUID')
        test_access_parser.add_argument('--access-level', default='read', help='Required access level')
        test_access_parser.add_argument('--resource-type', help='Type of resource being accessed')
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        action = options.get('action')
        
        if not action:
            self.print_help('manage', '')
            return
        
        try:
            if action == 'create-relationship':
                self.create_relationship(options)
            elif action == 'approve-relationship':
                self.approve_relationship(options)
            elif action == 'revoke-relationship':
                self.revoke_relationship(options)
            elif action == 'list-relationships':
                self.list_relationships(options)
            elif action == 'create-group':
                self.create_group(options)
            elif action == 'join-group':
                self.join_group(options)
            elif action == 'leave-group':
                self.leave_group(options)
            elif action == 'list-groups':
                self.list_groups(options)
            elif action == 'check-trust':
                self.check_trust(options)
            elif action == 'test-access':
                self.test_access(options)
            else:
                raise CommandError(f"Unknown action: {action}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Command failed: {str(e)}'))
            raise CommandError(str(e))
    
    def create_relationship(self, options):
        """Create a trust relationship."""
        try:
            relationship = TrustService.create_trust_relationship(
                source_org=options['source_org'],
                target_org=options['target_org'],
                trust_level_name=options['trust_level'],
                relationship_type=options['type'],
                created_by=options['created_by'],
                notes=options.get('notes', '')
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Trust relationship created successfully:\n'
                    f'  ID: {relationship.id}\n'
                    f'  Source: {relationship.source_organization}\n'
                    f'  Target: {relationship.target_organization}\n'
                    f'  Trust Level: {relationship.trust_level.name}\n'
                    f'  Status: {relationship.status}'
                )
            )
            
        except ValidationError as e:
            raise CommandError(f"Validation error: {str(e)}")
        except Exception as e:
            raise CommandError(f"Failed to create relationship: {str(e)}")
    
    def approve_relationship(self, options):
        """Approve a trust relationship."""
        try:
            activated = TrustService.approve_trust_relationship(
                relationship_id=options['relationship_id'],
                approving_org=options['approving_org'],
                approved_by_user=options['approved_by']
            )
            
            status_msg = 'activated' if activated else 'approved (waiting for other party)'
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Trust relationship {status_msg} successfully:\n'
                    f'  Relationship ID: {options["relationship_id"]}\n'
                    f'  Approved by: {options["approving_org"]}'
                )
            )
            
        except ValidationError as e:
            raise CommandError(f"Validation error: {str(e)}")
        except Exception as e:
            raise CommandError(f"Failed to approve relationship: {str(e)}")
    
    def revoke_relationship(self, options):
        """Revoke a trust relationship."""
        try:
            success = TrustService.revoke_trust_relationship(
                relationship_id=options['relationship_id'],
                revoking_org=options['revoking_org'],
                revoked_by_user=options['revoked_by'],
                reason=options.get('reason')
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Trust relationship revoked successfully:\n'
                        f'  Relationship ID: {options["relationship_id"]}\n'
                        f'  Revoked by: {options["revoking_org"]}\n'
                        f'  Reason: {options.get("reason", "No reason provided")}'
                    )
                )
            else:
                raise CommandError("Failed to revoke relationship")
                
        except ValidationError as e:
            raise CommandError(f"Validation error: {str(e)}")
        except Exception as e:
            raise CommandError(f"Failed to revoke relationship: {str(e)}")
    
    def list_relationships(self, options):
        """List trust relationships."""
        try:
            if options.get('organization'):
                relationships = TrustService.get_trust_relationships_for_organization(
                    organization=options['organization'],
                    include_inactive=options.get('include_inactive', False),
                    relationship_type=options.get('type')
                )
            else:
                # Get all relationships
                relationships = TrustRelationship.objects.select_related('trust_level')
                
                if not options.get('include_inactive'):
                    relationships = relationships.filter(is_active=True)
                
                if options.get('status'):
                    relationships = relationships.filter(status=options['status'])
                
                if options.get('type'):
                    relationships = relationships.filter(relationship_type=options['type'])
                
                relationships = relationships.all()
            
            if not relationships:
                self.stdout.write('No trust relationships found matching criteria.')
                return
            
            self.stdout.write(f'Found {len(relationships)} trust relationship(s):\n')
            
            for rel in relationships:
                effective_marker = ' (EFFECTIVE)' if rel.is_effective else ''
                self.stdout.write(
                    f'ID: {rel.id}\n'
                    f'  Source: {rel.source_organization}\n'
                    f'  Target: {rel.target_organization}\n'
                    f'  Type: {rel.relationship_type}\n'
                    f'  Trust Level: {rel.trust_level.name}\n'
                    f'  Status: {rel.status}{effective_marker}\n'
                    f'  Created: {rel.created_at}\n'
                    f'  Source Approved: {rel.approved_by_source}\n'
                    f'  Target Approved: {rel.approved_by_target}\n'
                )
                
                if rel.valid_until:
                    self.stdout.write(f'  Expires: {rel.valid_until}')
                
                if rel.notes:
                    self.stdout.write(f'  Notes: {rel.notes}')
                
                self.stdout.write('')
                
        except Exception as e:
            raise CommandError(f"Failed to list relationships: {str(e)}")
    
    def create_group(self, options):
        """Create a trust group."""
        try:
            group = TrustGroupService.create_trust_group(
                name=options['name'],
                description=options['description'],
                creator_org=options['creator_org'],
                group_type=options['type'],
                is_public=options.get('public', False),
                requires_approval=not options.get('no_approval', False),
                default_trust_level_name=options['trust_level']
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Trust group created successfully:\n'
                    f'  ID: {group.id}\n'
                    f'  Name: {group.name}\n'
                    f'  Type: {group.group_type}\n'
                    f'  Public: {group.is_public}\n'
                    f'  Requires Approval: {group.requires_approval}\n'
                    f'  Default Trust Level: {group.default_trust_level.name}'
                )
            )
            
        except ValidationError as e:
            raise CommandError(f"Validation error: {str(e)}")
        except Exception as e:
            raise CommandError(f"Failed to create group: {str(e)}")
    
    def join_group(self, options):
        """Join a trust group."""
        try:
            membership = TrustGroupService.join_trust_group(
                group_id=options['group_id'],
                organization=options['organization'],
                membership_type=options['membership_type'],
                invited_by=options.get('invited_by'),
                user='system'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully joined trust group:\n'
                    f'  Group ID: {options["group_id"]}\n'
                    f'  Organization: {options["organization"]}\n'
                    f'  Membership Type: {membership.membership_type}\n'
                    f'  Joined: {membership.joined_at}'
                )
            )
            
        except ValidationError as e:
            raise CommandError(f"Validation error: {str(e)}")
        except Exception as e:
            raise CommandError(f"Failed to join group: {str(e)}")
    
    def leave_group(self, options):
        """Leave a trust group."""
        try:
            success = TrustGroupService.leave_trust_group(
                group_id=options['group_id'],
                organization=options['organization'],
                user='system',
                reason=options.get('reason')
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully left trust group:\n'
                        f'  Group ID: {options["group_id"]}\n'
                        f'  Organization: {options["organization"]}\n'
                        f'  Reason: {options.get("reason", "No reason provided")}'
                    )
                )
            else:
                raise CommandError("Failed to leave group")
                
        except ValidationError as e:
            raise CommandError(f"Validation error: {str(e)}")
        except Exception as e:
            raise CommandError(f"Failed to leave group: {str(e)}")
    
    def list_groups(self, options):
        """List trust groups."""
        try:
            if options.get('organization'):
                groups = TrustGroupService.get_trust_groups_for_organization(
                    organization=options['organization'],
                    include_inactive=options.get('include_inactive', False)
                )
            elif options.get('public_only'):
                groups = TrustGroupService.get_public_trust_groups()
            else:
                groups = TrustGroup.objects.all()
                if not options.get('include_inactive'):
                    groups = groups.filter(is_active=True)
            
            if not groups:
                self.stdout.write('No trust groups found matching criteria.')
                return
            
            self.stdout.write(f'Found {len(groups)} trust group(s):\n')
            
            for group in groups:
                member_count = group.get_member_count()
                public_marker = ' (PUBLIC)' if group.is_public else ' (PRIVATE)'
                
                self.stdout.write(
                    f'ID: {group.id}\n'
                    f'  Name: {group.name}{public_marker}\n'
                    f'  Type: {group.group_type}\n'
                    f'  Description: {group.description}\n'
                    f'  Default Trust Level: {group.default_trust_level.name}\n'
                    f'  Members: {member_count}\n'
                    f'  Requires Approval: {group.requires_approval}\n'
                    f'  Created: {group.created_at}\n'
                    f'  Created by: {group.created_by}\n'
                )
                
                if group.administrators:
                    self.stdout.write(f'  Administrators: {", ".join(group.administrators)}')
                
                self.stdout.write('')
                
        except Exception as e:
            raise CommandError(f"Failed to list groups: {str(e)}")
    
    def check_trust(self, options):
        """Check trust level between organizations."""
        try:
            trust_info = TrustService.check_trust_level(
                source_org=options['source_org'],
                target_org=options['target_org']
            )
            
            if trust_info:
                trust_level, relationship = trust_info
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Trust relationship found:\n'
                        f'  Source: {options["source_org"]}\n'
                        f'  Target: {options["target_org"]}\n'
                        f'  Trust Level: {trust_level.name} ({trust_level.level})\n'
                        f'  Numerical Value: {trust_level.numerical_value}\n'
                        f'  Relationship Type: {relationship.relationship_type}\n'
                        f'  Effective: {relationship.is_effective}\n'
                        f'  Access Level: {relationship.get_effective_access_level()}\n'
                        f'  Anonymization Level: {relationship.get_effective_anonymization_level()}'
                    )
                )
                
                if relationship.trust_group:
                    self.stdout.write(f'  Trust Group: {relationship.trust_group.name}')
                    
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'No trust relationship found between:\n'
                        f'  Source: {options["source_org"]}\n'
                        f'  Target: {options["target_org"]}'
                    )
                )
                
        except Exception as e:
            raise CommandError(f"Failed to check trust: {str(e)}")
    
    def test_access(self, options):
        """Test intelligence access."""
        try:
            can_access, reason, relationship = TrustService.can_access_intelligence(
                requesting_org=options['requesting_org'],
                intelligence_owner=options['intelligence_owner'],
                intelligence_type=options.get('resource_type'),
                required_access_level=options['access_level']
            )
            
            access_result = 'GRANTED' if can_access else 'DENIED'
            style = self.style.SUCCESS if can_access else self.style.ERROR
            
            self.stdout.write(
                style(
                    f'Intelligence access {access_result}:\n'
                    f'  Requesting Org: {options["requesting_org"]}\n'
                    f'  Intelligence Owner: {options["intelligence_owner"]}\n'
                    f'  Required Access Level: {options["access_level"]}\n'
                    f'  Resource Type: {options.get("resource_type", "Not specified")}\n'
                    f'  Reason: {reason}'
                )
            )
            
            if relationship:
                self.stdout.write(
                    f'  Trust Level: {relationship.trust_level.name}\n'
                    f'  Effective Access Level: {relationship.get_effective_access_level()}\n'
                    f'  Relationship Type: {relationship.relationship_type}'
                )
                
        except Exception as e:
            raise CommandError(f"Failed to test access: {str(e)}")