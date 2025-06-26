"""
Unit tests for TAXII-related management commands
"""
import unittest
from unittest.mock import patch, MagicMock, call
from io import StringIO
import sys
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from core.models.threat_feed import ThreatFeed
from core.models.institution import Institution
from core.management.commands.taxii_operations import Command as TaxiiOperationsCommand
from core.management.commands.test_taxii import Command as TestTaxiiCommand
from core.tests.test_stix_mock_data import TAXII2_COLLECTIONS


class TaxiiOperationsCommandTestCase(TestCase):
    """Test cases for the 'taxii_operations' management command"""

    def setUp(self):
        """Set up the test environment"""

        super().setUp()
        # Create an Institution to use as the owner for ThreatFeeds
        self.institution = Institution.objects.create(
            name="Test Institution",
            description="Test description"
        )

        # Create a test threat feed
        self.feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test Feed for Command",
            is_external=True,
            taxii_server_url="https://test.example.com/taxii",
            taxii_api_root="api1",
            taxii_collection_id="collection1"
        )
        
        # Create the command instance
        self.command = TaxiiOperationsCommand()
        
        # Capture stdout/stderr
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.command.stdout = self.stdout
        self.command.stderr = self.stderr
        
        # Override the sys.stderr for CommandError testing
        self.old_stderr = sys.stderr
        sys.stderr = self.stderr

    def tearDown(self):
        """Clean up after the test"""
        sys.stderr = self.old_stderr

    @patch('core.services.stix_taxii_service.StixTaxiiService.discover_collections')
    def test_discover_command(self, mock_discover_collections):
        """Test the 'discover' command"""
        mock_discover_collections.return_value = TAXII2_COLLECTIONS
        
        # Create StringIO objects for capturing output
        out = StringIO()
        err = StringIO()
        
        # Call the command with explicit stdout/stderr
        call_command('taxii_operations', 'discover',
                    server='https://test.example.com/taxii',
                    api_root='api1',
                    username='testuser',
                    password='testpass',
                    stdout=out,
                    stderr=err)
        
        # Get the captured output
        output = out.getvalue()
        
        # Check that discover_collections was called correctly
        mock_discover_collections.assert_called_once_with(
            'https://test.example.com/taxii',
            'api1',
            'testuser',
            'testpass'
        )
        
        # Check the output
        self.assertIn(f"Found {len(TAXII2_COLLECTIONS)} collections:", output)

    @patch('core.services.stix_taxii_service.StixTaxiiService.discover_collections')
    def test_discover_command_error(self, mock_discover_collections):
        """Test error handling in the 'discover' command"""
        mock_discover_collections.side_effect = Exception("Test error")
        
        # Capture stderr
        err = StringIO()
        
        # Call the command with stderr capture
        call_command('taxii_operations', 'discover',
                     server='https://test.example.com/taxii',
                     api_root='api1',
                     stderr=err)
        
        # Check the error output
        error_output = err.getvalue()
        self.assertIn("Error discovering collections: Test error", error_output)

    @patch('core.services.stix_taxii_service.StixTaxiiService.consume_feed')
    def test_consume_command(self, mock_consume_feed):
        """Test the 'consume' command"""
        mock_consume_feed.return_value = {
            'indicators_created': 5,
            'indicators_updated': 2,
            'ttp_created': 3,
            'ttp_updated': 1,
            'skipped': 0,
            'errors': 0
        }
        
        # Create StringIO objects
        out = StringIO()
        err = StringIO()
        
        # Call the command with explicit stdout/stderr
        call_command('taxii_operations', 'consume', 
                    feed_id=self.feed.id,
                    stdout=out,
                    stderr=err)
        
        # Check that consume_feed was called correctly
        mock_consume_feed.assert_called_once_with(self.feed.id)
        
        # Check the output
        output = out.getvalue()
        self.assertIn("Feed consumed:", output)
        self.assertIn("Indicators created: 5", output)
        self.assertIn("TTPs created: 3", output)

    @patch('core.services.stix_taxii_service.StixTaxiiService.consume_feed')
    def test_consume_command_nonexistent_feed(self, mock_consume_feed):
        """Test the 'consume' command with a non-existent feed"""
        
        # Capture stderr
        err = StringIO()
        
        # Call the command with non-existent feed ID
        call_command('taxii_operations', 'consume', 
                    feed_id=999,
                    stderr=err)
        
        # Check that error was handled and written to stderr
        error_output = err.getvalue()
        import re
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', error_output)
        self.assertIn("Feed with ID 999 does not exist", clean_output)

    def test_add_command(self):
        """Test the 'add' command."""
        # Create StringIO objects
        out = StringIO()
        err = StringIO()
        
        # Call the command with explicit stdout/stderr
        call_command('taxii_operations', 'add',
                    name='New Feed',
                    description='New Test Feed',
                    server='https://new.example.com/taxii',
                    api_root='api2',
                    collection_id='collection2',
                    owner_id=self.institution.id,
                    stdout=out,
                    stderr=err)
        
        # Check that the feed was created
        feed = ThreatFeed.objects.filter(name='New Feed').first()
        self.assertIsNotNone(feed)
        self.assertEqual(feed.taxii_server_url, 'https://new.example.com/taxii')
        self.assertEqual(feed.taxii_api_root, 'api2')
        self.assertEqual(feed.taxii_collection_id, 'collection2')
        self.assertTrue(feed.is_external)
        
        # Check the output
        output = out.getvalue()
        self.assertIn(f"Feed added with ID: {feed.id}", output)

    def test_invalid_command(self):
        """Test calling an invalid command."""
        # Call an invalid command and expect an error
        with self.assertRaises(CommandError):
            call_command('taxii_operations', 'invalid_command')


class TestTaxiiCommandTestCase(TestCase):
    """Test cases for the 'test_taxii' management command"""

    def setUp(self):
        """Set up the test environment"""
        super().setUp()
        # Create an Institution
        self.institution = Institution.objects.create(
            name="Test Institution",
            description="Test description"
        )

        # Create the command instance
        self.command = TestTaxiiCommand()
        
        # Capture stdout/stderr
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.command.stdout = self.stdout
        self.command.stderr = self.stderr

    @patch('core.services.otx_taxii_service.OTXTaxiiService.get_collections')
    def test_list_collections(self, mock_get_collections):
        """Test the '--list-collections' option"""
        
        mock_get_collections.return_value = [
            {'id': 'collection1', 'title': 'Test Collection 1', 'description': 'Collection 1 description', 'available': True},
            {'id': 'collection2', 'title': 'Test Collection 2', 'description': 'Collection 2 description', 'available': True}
        ]
        
        # Capture stdout
        out = StringIO()
        
        # Call the command
        call_command('test_taxii', list_collections=True, stdout=out)
        
        # Check that get_collections was called
        mock_get_collections.assert_called_once()
        
        # Check the output
        output = out.getvalue()
        self.assertIn("Listing available collections...", output)
        self.assertIn("Found 2 collections:", output)
        self.assertIn("Test Collection 1", output)
        self.assertIn("Test Collection 2", output)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.get_collections')
    def test_list_collections_error(self, mock_get_collections):
        """Test error handling in the '--list-collections' option"""

        mock_get_collections.side_effect = Exception("Test error")
        
        # Capture stderr
        err = StringIO()
        
        # Call the command
        call_command('test_taxii', list_collections=True, stderr=err)
        
        # Check the error output
        error_output = err.getvalue()
        self.assertIn("Error listing collections: Test error", error_output)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_consume_option(self, mock_consume_feed):
        """Test the '--consume' option."""

        mock_consume_feed.return_value = {
            'indicators_created': 5,
            'indicators_updated': 2,
            'ttp_created': 3,
            'ttp_updated': 1,
            'skipped': 0,
            'errors': 0
        }
        
        # Capture stdout
        out = StringIO()
        
        # Call the command with explicit stdout capture
        call_command('test_taxii', 
                    consume=True, 
                    collection='test_collection', 
                    stdout=out)
        
        # Check that consume_feed was called correctly
        mock_consume_feed.assert_called_once_with(collection_name='test_collection')
        
        # Check the output
        output = out.getvalue()
        self.assertIn("Consuming from collection: test_collection", output)
        self.assertIn("Feed consumed:", output)
        self.assertIn("Indicators created: 5", output)
        self.assertIn("TTPs created: 3", output)

    @patch('core.services.otx_taxii_service.OTXTaxiiService.consume_feed')
    def test_consume_option_error(self, mock_consume_feed):
        """Test error handling in the '--consume' option"""

        mock_consume_feed.side_effect = Exception("Test error")
        
        # Capture stderr
        err = StringIO()
        
        # Call the command
        call_command('test_taxii', consume=True, collection='test_collection', stderr=err)
        
        # Check the error output
        error_output = err.getvalue()
        self.assertIn("Error consuming feed: Test error", error_output)


    def test_consume_without_collection(self):
        """Test the '--consume' option without providing a collection name"""
        # Capture stderr
        err = StringIO()
        
        # Call the command without a collection name
        call_command('test_taxii', consume=True, stderr=err)
        
        # Check the error output
        error_output = err.getvalue()
        self.assertIn("Collection name is required for consuming", error_output)


if __name__ == '__main__':
    unittest.main()