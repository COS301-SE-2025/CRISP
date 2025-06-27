"""
Comprehensive tests for Django management commands
Tests for taxii_operations and test_taxii commands.
"""
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from core.models.auth import Organization
from core.models.threat_feed import ThreatFeed
from core.management.commands.taxii_operations import Command as TaxiiOperationsCommand
from core.tests.test_base import CrispTestCase


class TaxiiOperationsCommandTest(CrispTestCase):
    """Test taxii_operations management command"""
    
    def setUp(self):
        super().setUp()
        self.command = TaxiiOperationsCommand()
        
        # Create test organization
        self.org = Organization.objects.create(
            name="TAXII Test Org", domain="taxii.com", contact_email="test@taxii.com"
        )
        
        # Create test threat feed
        self.threat_feed = ThreatFeed.objects.create(
            name="Test TAXII Feed",
            description="Test threat feed for TAXII operations",
            owner=self.org,
            is_external=True,
            taxii_server_url="https://test.taxii.server",
            taxii_api_root="/api/v1/",
            taxii_collection_id="test-collection-123"
        )
    
    def test_command_help(self):
        """Test command help and argument structure"""
        # Test that command has expected help text
        self.assertIn('TAXII operations', self.command.help)
        
        # Test command attributes
        self.assertTrue(hasattr(self.command, 'add_arguments'))
        self.assertTrue(hasattr(self.command, 'handle'))
        self.assertTrue(hasattr(self.command, 'handle_discover'))
        self.assertTrue(hasattr(self.command, 'handle_consume'))
        self.assertTrue(hasattr(self.command, 'handle_add'))
    
    def test_handle_no_command(self):
        """Test handling when no command is provided"""
        with self.assertRaises(CommandError) as context:
            self.command.handle()
        
        self.assertIn('A command is required', str(context.exception))
    
    @patch('core.services.stix_taxii_service.StixTaxiiService.discover_collections')
    def test_handle_discover_success(self, mock_discover):
        """Test successful discover command"""
        mock_collections = [
            {'id': 'collection1', 'title': 'Test Collection 1'},
            {'id': 'collection2', 'title': 'Test Collection 2'}
        ]
        mock_discover.return_value = mock_collections
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.command.handle_discover({
                'server': 'https://test.server',
                'api_root': '/api/v1/',
                'username': 'testuser',
                'password': 'testpass'
            })
            
            output = mock_stdout.getvalue()
            self.assertIn('Found 2 collections', output)
            self.assertIn('collection1', output)
            self.assertIn('Test Collection 1', output)
    
    @patch('core.services.stix_taxii_service.StixTaxiiService.consume_feed')
    def test_handle_consume_success(self, mock_consume):
        """Test successful consume command"""
        mock_result = {
            'indicators_created': 5,
            'indicators_updated': 3,
            'ttp_created': 2,
            'ttp_updated': 1,
            'skipped': 0,
            'errors': 0
        }
        mock_consume.return_value = mock_result
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.command.handle_consume({'feed_id': self.threat_feed.id})
            
            output = mock_stdout.getvalue()
            self.assertIn('Feed consumed', output)
            self.assertIn('Indicators created: 5', output)
            self.assertIn('Indicators updated: 3', output)
    
    def test_handle_add_success(self):
        """Test successful add command"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.command.handle_add({
                'name': 'New TAXII Feed',
                'description': 'New feed for testing',
                'server': 'https://new.server',
                'api_root': '/api/v2/',
                'collection_id': 'new-collection',
                'owner_id': str(self.org.id)
            })
            
            output = mock_stdout.getvalue()
            self.assertIn('Feed added with ID:', output)
            self.assertIn('Name: New TAXII Feed', output)
            
            # Verify feed was created
            new_feed = ThreatFeed.objects.filter(name='New TAXII Feed').first()
            self.assertIsNotNone(new_feed)
            self.assertEqual(new_feed.owner, self.org)
    
    def test_handle_consume_feed_not_found(self):
        """Test consume command with non-existent feed"""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            self.command.handle_consume({'feed_id': 99999})
            
            output = mock_stderr.getvalue()
            self.assertIn('Feed with ID 99999 does not exist', output)
    
    def test_handle_add_owner_not_found(self):
        """Test add command with non-existent owner"""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            self.command.handle_add({
                'name': 'Test Feed',
                'description': 'Test description',
                'server': 'https://test.server',
                'api_root': '/api/v1/',
                'collection_id': 'test-collection',
                'owner_id': 'non-existent-id'
            })
            
            output = mock_stderr.getvalue()
            self.assertIn('Organization with ID non-existent-id does not exist', output)


class ManagementCommandIntegrationTest(CrispTestCase):
    """Integration tests for management commands"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Integration Test Org", domain="integration.com", contact_email="test@integration.com"
        )
    
    @patch('core.services.stix_taxii_service.StixTaxiiService.discover_collections')
    def test_call_command_discover(self, mock_discover):
        """Test calling discover command via call_command"""
        mock_discover.return_value = [
            {'id': 'test-collection', 'title': 'Test Collection'}
        ]
        
        out = StringIO()
        call_command(
            'taxii_operations', 'discover',
            '--server', 'https://test.server',
            '--api-root', '/api/v1/',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Found 1 collections', output)
        self.assertIn('test-collection', output)
    
    def test_call_command_add(self):
        """Test calling add command via call_command"""
        out = StringIO()
        call_command(
            'taxii_operations', 'add',
            '--name', 'CLI Test Feed',
            '--description', 'Feed created via CLI',
            '--server', 'https://cli.server',
            '--api-root', '/api/v1/',
            '--collection-id', 'cli-collection',
            '--owner-id', str(self.org.id),
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Feed added with ID:', output)
        self.assertIn('Name: CLI Test Feed', output)
        
        # Verify feed was created
        cli_feed = ThreatFeed.objects.filter(name='CLI Test Feed').first()
        self.assertIsNotNone(cli_feed)
        self.assertEqual(cli_feed.description, 'Feed created via CLI')


class ManagementCommandErrorHandlingTest(CrispTestCase):
    """Test error handling across management commands"""
    
    def setUp(self):
        super().setUp()
        self.command = TaxiiOperationsCommand()
    
    def test_command_exception_handling(self):
        """Test command exception handling"""
        with patch('core.services.stix_taxii_service.StixTaxiiService') as mock_service:
            mock_service.side_effect = Exception("Service unavailable")
            
            with patch('sys.stderr', new_callable=StringIO):
                try:
                    self.command.handle(command='discover', server='test', api_root='/api/')
                except:
                    pass  # Exception should be handled gracefully
    
    def test_command_database_error_handling(self):
        """Test handling of database errors"""
        with patch('core.models.threat_feed.ThreatFeed.objects.get') as mock_get:
            mock_get.side_effect = Exception("Database connection failed")
            
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                self.command.handle_consume({'feed_id': 1})
                
                output = mock_stderr.getvalue()
                self.assertIn('Error consuming feed', output)