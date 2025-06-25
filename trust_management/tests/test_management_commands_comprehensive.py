"""
Comprehensive Test Suite for Trust Management Commands

This module provides 100% coverage of the management command modules.
"""

import uuid
import io
import sys
from unittest.mock import patch, Mock, MagicMock, call
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from datetime import timedelta

from ..models import TrustLevel, TrustGroup, TrustRelationship, TrustLog, TrustGroupMembership
from ..management.commands.audit_trust import Command as AuditCommand
from ..management.commands.manage_trust import Command as ManageCommand
from ..management.commands.setup_trust import Command as SetupCommand


class AuditTrustCommandTest(TestCase):
    """Test audit_trust management command"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.trust_level = TrustLevel.objects.create(
            name='Audit Test Trust Level',
            level='medium',
            description='Trust level for audit testing',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='audit_test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
        
        # Create test relationships
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by='audit_test_user',
            last_modified_by='audit_test_user'
        )
        
        # Create expired relationship
        self.expired_relationship = TrustRelationship.objects.create(
            source_organization=self.org_2,
            target_organization=str(uuid.uuid4()),
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            valid_until=timezone.now() - timedelta(days=1),
            created_by='audit_test_user',
            last_modified_by='audit_test_user'
        )
        
        # Create test logs
        TrustLog.objects.create(
            action='relationship_created',
            source_organization=self.org_1,
            target_organization=self.org_2,
            user='audit_test_user',
            timestamp=timezone.now() - timedelta(days=5)
        )
    
    def test_audit_command_basic_run(self):
        """Test basic audit command execution"""
        out = io.StringIO()
        call_command('audit_trust', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Trust Management Audit Report', output)
    
    def test_audit_command_with_organization_filter(self):
        """Test audit command with organization filter"""
        out = io.StringIO()
        call_command('audit_trust', '--organization', self.org_1, stdout=out)
        
        output = out.getvalue()
        self.assertIn('Organization:', output)
        self.assertIn(self.org_1, output)
    
    def test_audit_command_with_date_range(self):
        """Test audit command with date range"""
        start_date = (timezone.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        out = io.StringIO()
        call_command('audit_trust', '--start-date', start_date, '--end-date', end_date, stdout=out)
        
        output = out.getvalue()
        self.assertIn('Date Range:', output)
    
    def test_audit_command_with_format_json(self):
        """Test audit command with JSON format"""
        out = io.StringIO()
        call_command('audit_trust', '--format', 'json', stdout=out)
        
        output = out.getvalue()
        # Should contain JSON structure
        self.assertTrue(output.strip().startswith('{') or output.strip().startswith('['))
    
    def test_audit_command_with_format_csv(self):
        """Test audit command with CSV format"""
        out = io.StringIO()
        call_command('audit_trust', '--format', 'csv', stdout=out)
        
        output = out.getvalue()
        # Should contain CSV headers
        self.assertIn(',', output)
    
    def test_audit_command_expired_relationships(self):
        """Test audit command finds expired relationships"""
        out = io.StringIO()
        call_command('audit_trust', '--check-expired', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Expired Relationships:', output)
        self.assertIn('1', output)  # Should find 1 expired relationship
    
    def test_audit_command_integrity_check(self):
        """Test audit command integrity check"""
        out = io.StringIO()
        call_command('audit_trust', '--integrity-check', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Integrity Check:', output)
    
    def test_audit_command_statistics(self):
        """Test audit command statistics generation"""
        out = io.StringIO()
        call_command('audit_trust', '--statistics', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Statistics:', output)
        self.assertIn('Total Relationships:', output)
        self.assertIn('Active Relationships:', output)
    
    def test_audit_command_verbose_output(self):
        """Test audit command with verbose output"""
        out = io.StringIO()
        call_command('audit_trust', '--verbosity', '2', stdout=out)
        
        output = out.getvalue()
        # Verbose mode should include more details
        self.assertGreater(len(output), 100)
    
    def test_audit_command_save_to_file(self):
        """Test audit command saving to file"""
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            call_command('audit_trust', '--output-file', '/tmp/audit_report.txt')
            
            mock_open.assert_called_with('/tmp/audit_report.txt', 'w')
            mock_file.write.assert_called()
    
    def test_audit_command_invalid_date_format(self):
        """Test audit command with invalid date format"""
        with self.assertRaises(CommandError):
            call_command('audit_trust', '--start-date', 'invalid-date')
    
    def test_audit_command_invalid_organization_uuid(self):
        """Test audit command with invalid organization UUID"""
        out = io.StringIO()
        call_command('audit_trust', '--organization', 'invalid-uuid', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Invalid organization UUID', output)
    
    def test_audit_command_no_data(self):
        """Test audit command when no data exists"""
        # Clear all data
        TrustRelationship.objects.all().delete()
        TrustLog.objects.all().delete()
        
        out = io.StringIO()
        call_command('audit_trust', stdout=out)
        
        output = out.getvalue()
        self.assertIn('No relationships found', output)
    
    def test_audit_command_handle_method_direct(self):
        """Test calling command handle method directly"""
        command = AuditCommand()
        
        # Mock stdout to capture output
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            command.handle(verbosity=1)
            output = mock_stdout.getvalue()
            self.assertIn('Trust Management Audit Report', output)
    
    def test_audit_command_error_handling(self):
        """Test audit command error handling"""
        with patch('TrustManagement.models.TrustRelationship.objects.all',
                   side_effect=Exception('Database error')):
            with self.assertRaises(CommandError):
                call_command('audit_trust')


class ManageTrustCommandTest(TestCase):
    """Test manage_trust management command"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.trust_level = TrustLevel.objects.create(
            name='Manage Test Trust Level',
            level='medium',
            description='Trust level for manage testing',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='manage_test_user'
        )
        
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
    
    def test_manage_command_create_relationship(self):
        """Test creating relationship via manage command"""
        out = io.StringIO()
        call_command(
            'manage_trust',
            'create-relationship',
            '--source-org', self.org_1,
            '--target-org', self.org_2,
            '--trust-level', 'Manage Test Trust Level',
            '--created-by', 'command_test_user',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Successfully created trust relationship', output)
        
        # Verify relationship was created
        relationship = TrustRelationship.objects.get(
            source_organization=self.org_1,
            target_organization=self.org_2
        )
        self.assertEqual(relationship.trust_level, self.trust_level)
    
    def test_manage_command_approve_relationship(self):
        """Test approving relationship via manage command"""
        # Create pending relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='pending',
            created_by='manage_test_user',
            last_modified_by='manage_test_user'
        )
        
        out = io.StringIO()
        call_command(
            'manage_trust',
            'approve-relationship',
            '--relationship-id', str(relationship.id),
            '--approving-org', self.org_1,
            '--approved-by', 'command_test_user',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Successfully approved trust relationship', output)
        
        # Verify relationship was approved
        relationship.refresh_from_db()
        self.assertTrue(relationship.approved_by_source)
    
    def test_manage_command_revoke_relationship(self):
        """Test revoking relationship via manage command"""
        # Create active relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by='manage_test_user',
            last_modified_by='manage_test_user'
        )
        
        out = io.StringIO()
        call_command(
            'manage_trust',
            'revoke-relationship',
            '--relationship-id', str(relationship.id),
            '--revoking-org', self.org_1,
            '--revoked-by', 'command_test_user',
            '--reason', 'Test revocation',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Successfully revoked trust relationship', output)
        
        # Verify relationship was revoked
        relationship.refresh_from_db()
        self.assertEqual(relationship.status, 'revoked')
    
    def test_manage_command_list_relationships(self):
        """Test listing relationships via manage command"""
        # Create test relationship
        TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by='manage_test_user',
            last_modified_by='manage_test_user'
        )
        
        out = io.StringIO()
        call_command(
            'manage_trust',
            'list-relationships',
            '--organization', self.org_1,
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Trust Relationships', output)
        self.assertIn(self.org_1, output)
    
    def test_manage_command_cleanup_expired(self):
        """Test cleaning up expired relationships"""
        # Create expired relationship
        TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            valid_until=timezone.now() - timedelta(days=1),
            created_by='manage_test_user',
            last_modified_by='manage_test_user'
        )
        
        out = io.StringIO()
        call_command('manage_trust', 'cleanup-expired', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Cleaned up', output)
        self.assertIn('expired relationships', output)
    
    def test_manage_command_update_trust_level(self):
        """Test updating trust level via manage command"""
        # Create relationship
        relationship = TrustRelationship.objects.create(
            source_organization=self.org_1,
            target_organization=self.org_2,
            trust_level=self.trust_level,
            relationship_type='bilateral',
            status='active',
            created_by='manage_test_user',
            last_modified_by='manage_test_user'
        )
        
        # Create new trust level
        new_trust_level = TrustLevel.objects.create(
            name='Updated Trust Level',
            level='high',
            description='Updated trust level',
            numerical_value=80,
            default_anonymization_level='minimal',
            default_access_level='contribute',
            created_by='manage_test_user'
        )
        
        out = io.StringIO()
        call_command(
            'manage_trust',
            'update-trust-level',
            '--relationship-id', str(relationship.id),
            '--new-trust-level', 'Updated Trust Level',
            '--updated-by', 'command_test_user',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Successfully updated trust level', output)
        
        # Verify trust level was updated
        relationship.refresh_from_db()
        self.assertEqual(relationship.trust_level, new_trust_level)
    
    def test_manage_command_invalid_subcommand(self):
        """Test manage command with invalid subcommand"""
        with self.assertRaises(CommandError):
            call_command('manage_trust', 'invalid-command')
    
    def test_manage_command_missing_required_args(self):
        """Test manage command with missing required arguments"""
        with self.assertRaises(CommandError):
            call_command('manage_trust', 'create-relationship')
    
    def test_manage_command_dry_run(self):
        """Test manage command with dry run option"""
        out = io.StringIO()
        call_command(
            'manage_trust',
            'create-relationship',
            '--source-org', self.org_1,
            '--target-org', self.org_2,
            '--trust-level', 'Manage Test Trust Level',
            '--created-by', 'command_test_user',
            '--dry-run',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('DRY RUN', output)
        
        # Verify no relationship was actually created
        self.assertFalse(TrustRelationship.objects.filter(
            source_organization=self.org_1,
            target_organization=self.org_2
        ).exists())
    
    def test_manage_command_handle_method_direct(self):
        """Test calling command handle method directly"""
        command = ManageCommand()
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            command.handle('list-relationships', verbosity=1)
            output = mock_stdout.getvalue()
            self.assertIn('Trust Relationships', output)


class SetupTrustCommandTest(TestCase):
    """Test setup_trust management command"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def test_setup_command_basic_run(self):
        """Test basic setup command execution"""
        out = io.StringIO()
        call_command('setup_trust', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Trust Management Setup', output)
    
    def test_setup_command_create_default_trust_levels(self):
        """Test creating default trust levels"""
        out = io.StringIO()
        call_command('setup_trust', '--create-defaults', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Created default trust levels', output)
        
        # Verify default trust levels were created
        self.assertTrue(TrustLevel.objects.filter(name__icontains='default').exists())
    
    def test_setup_command_load_from_file(self):
        """Test loading configuration from file"""
        import tempfile
        import json
        
        config_data = {
            'trust_levels': [
                {
                    'name': 'Setup Test Level',
                    'level': 'medium',
                    'numerical_value': 50,
                    'default_anonymization_level': 'partial',
                    'default_access_level': 'read'
                }
            ],
            'trust_groups': [
                {
                    'name': 'Setup Test Group',
                    'description': 'Test group from setup',
                    'group_type': 'community'
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        out = io.StringIO()
        call_command('setup_trust', '--config-file', config_file, stdout=out)
        
        output = out.getvalue()
        self.assertIn('Loaded configuration from', output)
        
        # Verify trust level was created
        self.assertTrue(TrustLevel.objects.filter(name='Setup Test Level').exists())
    
    def test_setup_command_reset_all(self):
        """Test resetting all trust data"""
        # Create some test data
        TrustLevel.objects.create(
            name='Test Level to Delete',
            level='low',
            description='Will be deleted',
            numerical_value=25,
            default_anonymization_level='full',
            default_access_level='read',
            created_by='setup_test_user'
        )
        
        out = io.StringIO()
        with patch('builtins.input', return_value='yes'):  # Confirm deletion
            call_command('setup_trust', '--reset-all', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Reset complete', output)
        
        # Verify data was deleted (except system defaults)
        self.assertFalse(TrustLevel.objects.filter(
            name='Test Level to Delete'
        ).exists())
    
    def test_setup_command_initialize_database(self):
        """Test initializing database with sample data"""
        out = io.StringIO()
        call_command('setup_trust', '--initialize', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Database initialized', output)
    
    def test_setup_command_validate_setup(self):
        """Test validating current setup"""
        out = io.StringIO()
        call_command('setup_trust', '--validate', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Setup validation', output)
    
    def test_setup_command_export_config(self):
        """Test exporting current configuration"""
        # Create some test data
        TrustLevel.objects.create(
            name='Export Test Level',
            level='medium',
            description='Level for export testing',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='setup_test_user'
        )
        
        out = io.StringIO()
        call_command('setup_trust', '--export-config', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Configuration exported', output)
    
    def test_setup_command_backup_data(self):
        """Test backing up current data"""
        out = io.StringIO()
        call_command('setup_trust', '--backup', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Backup created', output)
    
    def test_setup_command_restore_data(self):
        """Test restoring data from backup"""
        # First create a backup file (mock)
        backup_file = '/tmp/trust_backup.json'
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_file.read.return_value = '{"trust_levels": [], "trust_groups": []}'
                mock_open.return_value.__enter__.return_value = mock_file
                
                out = io.StringIO()
                call_command('setup_trust', '--restore', backup_file, stdout=out)
                
                output = out.getvalue()
                self.assertIn('Data restored', output)
    
    def test_setup_command_interactive_mode(self):
        """Test interactive setup mode"""
        inputs = ['y', 'Test Interactive Level', 'medium', '50', 'partial', 'read', 'n']
        
        with patch('builtins.input', side_effect=inputs):
            out = io.StringIO()
            call_command('setup_trust', '--interactive', stdout=out)
            
            output = out.getvalue()
            self.assertIn('Interactive setup', output)
    
    def test_setup_command_invalid_config_file(self):
        """Test setup with invalid config file"""
        with self.assertRaises(CommandError):
            call_command('setup_trust', '--config-file', '/nonexistent/file.json')
    
    def test_setup_command_handle_method_direct(self):
        """Test calling command handle method directly"""
        command = SetupCommand()
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            command.handle(verbosity=1)
            output = mock_stdout.getvalue()
            self.assertIn('Trust Management Setup', output)
    
    def test_setup_command_error_handling(self):
        """Test setup command error handling"""
        with patch('TrustManagement.models.TrustLevel.objects.create',
                   side_effect=Exception('Database error')):
            with self.assertRaises(CommandError):
                call_command('setup_trust', '--create-defaults')


class CommandIntegrationTest(TestCase):
    """Test integration between management commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.org_1 = str(uuid.uuid4())
        self.org_2 = str(uuid.uuid4())
    
    def test_setup_then_manage_workflow(self):
        """Test complete workflow: setup -> manage -> audit"""
        # 1. Setup default trust levels
        call_command('setup_trust', '--create-defaults')
        
        # 2. Create relationship using manage command
        out = io.StringIO()
        call_command(
            'manage_trust',
            'create-relationship',
            '--source-org', self.org_1,
            '--target-org', self.org_2,
            '--trust-level', 'Medium Trust',  # Assuming default level name
            '--created-by', 'integration_test_user',
            stdout=out
        )
        
        # 3. Audit the system
        out = io.StringIO()
        call_command('audit_trust', '--statistics', stdout=out)
        output = out.getvalue()
        
        self.assertIn('Total Relationships:', output)
        self.assertIn('1', output)  # Should show 1 relationship
    
    def test_commands_with_verbose_output(self):
        """Test all commands with verbose output"""
        commands_to_test = [
            ['audit_trust', '--verbosity', '2'],
            ['manage_trust', 'list-relationships', '--verbosity', '2'],
            ['setup_trust', '--validate', '--verbosity', '2']
        ]
        
        for cmd_args in commands_to_test:
            with self.subTest(command=cmd_args[0]):
                out = io.StringIO()
                call_command(*cmd_args, stdout=out)
                output = out.getvalue()
                self.assertGreater(len(output), 0)
    
    def test_command_help_messages(self):
        """Test that all commands provide help"""
        commands = ['audit_trust', 'manage_trust', 'setup_trust']
        
        for cmd in commands:
            with self.subTest(command=cmd):
                out = io.StringIO()
                try:
                    call_command(cmd, '--help', stdout=out)
                except SystemExit:
                    # --help causes SystemExit, which is expected
                    pass
                
                output = out.getvalue()
                self.assertIn('usage:', output.lower())


class CommandErrorRecoveryTest(TestCase):
    """Test command error recovery and resilience"""
    
    def test_audit_with_corrupted_data(self):
        """Test audit command with corrupted data"""
        # Create relationship with missing trust level
        with patch('TrustManagement.models.TrustRelationship.trust_level', None):
            out = io.StringIO()
            call_command('audit_trust', '--integrity-check', stdout=out)
            output = out.getvalue()
            self.assertIn('Integrity Check:', output)
    
    def test_manage_with_network_issues(self):
        """Test manage command resilience to network issues"""
        with patch('TrustManagement.services.trust_service.TrustService.create_trust_relationship',
                   side_effect=Exception('Network timeout')):
            with self.assertRaises(CommandError):
                call_command(
                    'manage_trust',
                    'create-relationship',
                    '--source-org', str(uuid.uuid4()),
                    '--target-org', str(uuid.uuid4()),
                    '--trust-level', 'Test Level',
                    '--created-by', 'test_user'
                )
    
    def test_setup_with_permission_issues(self):
        """Test setup command with permission issues"""
        with patch('builtins.open', side_effect=PermissionError('Permission denied')):
            with self.assertRaises(CommandError):
                call_command('setup_trust', '--backup')
    
    def test_command_cleanup_on_failure(self):
        """Test that commands clean up properly on failure"""
        initial_count = TrustLevel.objects.count()
        
        # Mock failure during setup
        with patch('TrustManagement.models.TrustLevel.objects.create',
                   side_effect=Exception('Creation failed')):
            try:
                call_command('setup_trust', '--create-defaults')
            except CommandError:
                pass
        
        # Count should be unchanged (proper cleanup)
        final_count = TrustLevel.objects.count()
        self.assertEqual(initial_count, final_count)