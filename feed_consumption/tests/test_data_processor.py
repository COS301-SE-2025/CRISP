import uuid
import json
from unittest import mock
from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError

from stix2.exceptions import STIXError

from feed_consumption.models import ExternalFeedSource, FeedConsumptionLog
from feed_consumption.data_processor import (
    DataProcessor, DataProcessingError, StixValidationError
)


# Mock the ThreatIntelligence, StixObject, and DuplicateTracker models
@mock.patch('feed_consumption.data_processor.ThreatIntelligence')
@mock.patch('feed_consumption.data_processor.StixObject')
@mock.patch('feed_consumption.data_processor.DuplicateTracker')
class DataProcessorTests(TestCase):
    """Test the data processor implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='password123'
        )
        
        self.feed_source = ExternalFeedSource.objects.create(
            name='Test Feed',
            discovery_url='https://example.com/taxii2/',
            categories=['malware', 'indicators'],
            poll_interval=ExternalFeedSource.PollInterval.DAILY,
            added_by=self.user
        )
        
        self.log_entry = FeedConsumptionLog.objects.create(
            feed_source=self.feed_source
        )
        
        # Create sample STIX objects for testing
        self.indicator_object = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f",
            "created_by_ref": "identity--f431f809-377b-45e0-aa1c-6a4751cae5ff",
            "created": "2016-04-06T20:03:48.000Z",
            "modified": "2016-04-06T20:03:48.000Z",
            "indicator_types": ["malicious-activity"],
            "name": "Poison Ivy Malware",
            "description": "This indicator contains a pattern for Poison Ivy malware.",
            "pattern": "file:hashes.MD5 = '3773a88f65a5e780c8c11b55a12c0a89'",
            "pattern_type": "stix",
            "valid_from": "2016-01-01T00:00:00Z"
        }
        
        self.malware_object = {
            "type": "malware",
            "spec_version": "2.1",
            "id": "malware--fdd60b30-b67c-11e3-b0b9-f01faf20d111",
            "created": "2014-02-20T09:16:08.989Z",
            "modified": "2014-02-20T09:16:08.989Z",
            "name": "Poison Ivy",
            "description": "A remote access trojan (RAT).",
            "malware_types": ["remote-access-trojan"],
            "is_family": True
        }
        
        self.attack_pattern_object = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": "attack-pattern--0c7b5b88-8ff7-4a4d-aa9d-feb398cd0061",
            "created": "2016-05-12T08:17:27.000Z",
            "modified": "2016-05-12T08:17:27.000Z",
            "name": "Spear Phishing",
            "description": "Spear phishing is a targeted form of phishing...",
            "external_references": [
                {
                    "source_name": "CAPEC",
                    "external_id": "CAPEC-163"
                }
            ]
        }
        
        self.education_related_object = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--5e579975-2d61-4318-a61e-6471b916e3a3",
            "created": "2018-01-17T20:15:31.000Z",
            "modified": "2018-01-17T20:15:31.000Z",
            "name": "University Phishing Campaign",
            "description": "Targets educational institutions with spear phishing emails.",
            "pattern": "[url:value = 'https://university-update.com/login']",
            "pattern_type": "stix",
            "valid_from": "2018-01-01T00:00:00Z"
        }
        
        # Create the processor
        self.processor = DataProcessor(self.feed_source, self.log_entry)
    
    @mock.patch('feed_consumption.data_processor.stix2.parse')
    @mock.patch('feed_consumption.data_processor.validate_instance')
    def test_validate_stix_object_success(self, mock_validate, mock_parse, *mocks):
        """Test successful STIX object validation."""
        # Configure mocks
        mock_parse.return_value = mock.MagicMock()
        
        validation_results = mock.MagicMock()
        validation_results.is_valid = True
        mock_validate.return_value = validation_results
        
        # Validate the indicator object
        result = self.processor.validate_stix_object(self.indicator_object)
        
        # Check results
        self.assertTrue(result)
        mock_parse.assert_called_once_with(self.indicator_object, allow_custom=True)
        mock_validate.assert_called_once_with(self.indicator_object)
    
    @mock.patch('feed_consumption.data_processor.stix2.parse')
    @mock.patch('feed_consumption.data_processor.validate_instance')
    def test_validate_stix_object_invalid(self, mock_validate, mock_parse, *mocks):
        """Test validation of an invalid STIX object."""
        # Configure mocks
        mock_parse.return_value = mock.MagicMock()
        
        validation_results = mock.MagicMock()
        validation_results.is_valid = False
        validation_results.errors = ["Invalid pattern syntax", "Missing required field"]
        mock_validate.return_value = validation_results
        
        # Validate the object and check exception
        with self.assertRaises(StixValidationError) as context:
            self.processor.validate_stix_object(self.indicator_object)
        
        # Check error message
        self.assertIn("Invalid pattern syntax", str(context.exception))
        self.assertIn("Missing required field", str(context.exception))
        
        # Check log entry was updated
        self.assertIn("Invalid pattern syntax", self.log_entry.error_message)
    
    @mock.patch('feed_consumption.data_processor.stix2.parse')
    def test_validate_stix_object_parse_error(self, mock_parse, *mocks):
        """Test STIX object that fails to parse."""
        # Configure mock to raise exception
        mock_parse.side_effect = STIXError("Invalid STIX format")
        
        # Validate the object and check exception
        with self.assertRaises(StixValidationError) as context:
            self.processor.validate_stix_object(self.indicator_object)
        
        # Check error message
        self.assertIn("Invalid STIX format", str(context.exception))
        
        # Check log entry was updated
        self.assertIn("Invalid STIX format", self.log_entry.error_message)
    
    def test_generate_object_hash_indicator(self, *mocks):
        """Test hash generation for indicator objects."""
        hash1 = self.processor.generate_object_hash(self.indicator_object)
        
        # Same pattern but different ID should have same hash
        modified_object = self.indicator_object.copy()
        modified_object['id'] = "indicator--different-uuid"
        hash2 = self.processor.generate_object_hash(modified_object)
        
        self.assertEqual(hash1, hash2)
        
        # Different pattern should have different hash
        modified_object = self.indicator_object.copy()
        modified_object['pattern'] = "file:hashes.MD5 = 'different-hash-value'"
        hash3 = self.processor.generate_object_hash(modified_object)
        
        self.assertNotEqual(hash1, hash3)
    
    def test_generate_object_hash_malware(self, *mocks):
        """Test hash generation for malware objects."""
        hash1 = self.processor.generate_object_hash(self.malware_object)
        
        # Same name but different ID should have same hash
        modified_object = self.malware_object.copy()
        modified_object['id'] = "malware--different-uuid"
        hash2 = self.processor.generate_object_hash(modified_object)
        
        self.assertEqual(hash1, hash2)
        
        # Different name should have different hash
        modified_object = self.malware_object.copy()
        modified_object['name'] = "Different Malware"
        hash3 = self.processor.generate_object_hash(modified_object)
        
        self.assertNotEqual(hash1, hash3)
    
    def test_generate_object_hash_attack_pattern(self, *mocks):
        """Test hash generation for attack pattern objects."""
        hash1 = self.processor.generate_object_hash(self.attack_pattern_object)
        
        # Same name and external references but different ID should have same hash
        modified_object = self.attack_pattern_object.copy()
        modified_object['id'] = "attack-pattern--different-uuid"
        hash2 = self.processor.generate_object_hash(modified_object)
        
        self.assertEqual(hash1, hash2)
        
        # Different external references should have different hash
        modified_object = self.attack_pattern_object.copy()
        modified_object['external_references'] = [
            {
                "source_name": "CAPEC",
                "external_id": "CAPEC-164"  # Different ID
            }
        ]
        hash3 = self.processor.generate_object_hash(modified_object)
        
        self.assertNotEqual(hash1, hash3)
    
    def test_is_duplicate(self, *mocks):
        """Test duplicate detection."""
        # Mock DuplicateTracker.objects.filter
        mock_duplicate_tracker = mocks[0]
        mock_filter = mock.MagicMock()
        mock_duplicate_tracker.objects.filter.return_value = mock_filter
        
        # Test with existing duplicate
        mock_filter.exists.return_value = True
        self.assertTrue(self.processor.is_duplicate("test-hash"))
        mock_duplicate_tracker.objects.filter.assert_called_with(object_hash="test-hash")
        
        # Test with no duplicate
        mock_filter.exists.return_value = False
        self.assertFalse(self.processor.is_duplicate("test-hash"))
    
    def test_is_education_relevant_true(self, *mocks):
        """Test education relevance detection for relevant objects."""
        # Test object with education keywords in description
        self.assertTrue(self.processor.is_education_relevant(self.education_related_object))
        
        # Test object with education keywords in name
        obj = self.indicator_object.copy()
        obj['name'] = "University Credential Harvester"
        self.assertTrue(self.processor.is_education_relevant(obj))
        
        # Test object with education keywords in pattern
        obj = self.indicator_object.copy()
        obj['pattern'] = "[domain-name:value = 'university-login.com']"
        self.assertTrue(self.processor.is_education_relevant(obj))
        
        # Test identity object with education sector
        obj = {
            "type": "identity",
            "id": "identity--test",
            "name": "Test University",
            "sectors": ["education", "research"]
        }
        self.assertTrue(self.processor.is_education_relevant(obj))
        
        # Test object with education victim references
        obj = {
            "type": "campaign",
            "id": "campaign--test",
            "name": "Test Campaign",
            "victim_refs": ["identity--university-victim"]
        }
        self.assertTrue(self.processor.is_education_relevant(obj))
    
    def test_is_education_relevant_false(self, *mocks):
        """Test education relevance detection for non-relevant objects."""
        # Basic indicator with no education references
        self.assertFalse(self.processor.is_education_relevant(self.indicator_object))
        
        # Malware with no education references
        self.assertFalse(self.processor.is_education_relevant(self.malware_object))
        
        # Attack pattern with no education references
        self.assertFalse(self.processor.is_education_relevant(self.attack_pattern_object))
    
    def test_normalize_to_internal_indicator(self, *mocks):
        """Test normalization of indicator objects."""
        normalized = self.processor.normalize_to_internal(self.indicator_object)
        
        # Check common fields
        self.assertEqual(normalized['stix_id'], self.indicator_object['id'])
        self.assertEqual(normalized['stix_type'], 'indicator')
        self.assertEqual(normalized['created'], self.indicator_object['created'])
        self.assertEqual(normalized['modified'], self.indicator_object['modified'])
        self.assertEqual(normalized['feed_source'], self.feed_source)
        self.assertEqual(normalized['raw_data'], self.indicator_object)
        self.assertFalse(normalized['is_education_relevant'])
        
        # Check indicator-specific fields
        self.assertEqual(normalized['name'], self.indicator_object['name'])
        self.assertEqual(normalized['description'], self.indicator_object['description'])
        self.assertEqual(normalized['pattern'], self.indicator_object['pattern'])
        self.assertEqual(normalized['pattern_type'], self.indicator_object['pattern_type'])
        self.assertEqual(normalized['indicator_types'], self.indicator_object['indicator_types'])
        self.assertEqual(normalized['valid_from'], self.indicator_object['valid_from'])
    
    def test_normalize_to_internal_malware(self, *mocks):
        """Test normalization of malware objects."""
        normalized = self.processor.normalize_to_internal(self.malware_object)
        
        # Check common fields
        self.assertEqual(normalized['stix_id'], self.malware_object['id'])
        self.assertEqual(normalized['stix_type'], 'malware')
        
        # Check malware-specific fields
        self.assertEqual(normalized['name'], self.malware_object['name'])
        self.assertEqual(normalized['description'], self.malware_object['description'])
        self.assertEqual(normalized['malware_types'], self.malware_object['malware_types'])
        self.assertEqual(normalized['is_family'], self.malware_object['is_family'])
    
    def test_normalize_to_internal_attack_pattern(self, *mocks):
        """Test normalization of attack pattern objects."""
        normalized = self.processor.normalize_to_internal(self.attack_pattern_object)
        
        # Check common fields
        self.assertEqual(normalized['stix_id'], self.attack_pattern_object['id'])
        self.assertEqual(normalized['stix_type'], 'attack-pattern')
        
        # Check attack pattern-specific fields
        self.assertEqual(normalized['name'], self.attack_pattern_object['name'])
        self.assertEqual(normalized['description'], self.attack_pattern_object['description'])
        self.assertEqual(normalized['external_references'], self.attack_pattern_object['external_references'])
    
    def test_save_to_database_new_object(self, *mocks):
        """Test saving a new object to the database."""
        # Mock objects
        mock_duplicate_tracker = mocks[0]
        mock_stix_object = mocks[1]
        mock_threat_intel = mocks[2]
        
        # Mock duplicate check
        mock_filter = mock.MagicMock()
        mock_filter.exists.return_value = False
        mock_duplicate_tracker.objects.filter.return_value = mock_filter
        
        # Mock StixObject creation
        mock_stix_obj = mock.MagicMock()
        mock_stix_object.objects.create.return_value = mock_stix_obj
        
        # Normalize an indicator
        normalized = self.processor.normalize_to_internal(self.indicator_object)
        
        # Save to database
        result, created = self.processor.save_to_database(normalized)
        
        # Check result
        self.assertEqual(result, mock_stix_obj)
        self.assertTrue(created)
        
        # Verify StixObject.objects.create was called
        mock_stix_object.objects.create.assert_called_once()
        args = mock_stix_object.objects.create.call_args[1]
        self.assertEqual(args['stix_id'], self.indicator_object['id'])
        self.assertEqual(args['stix_type'], 'indicator')
        self.assertEqual(args['feed_source'], self.feed_source)
        
        # Verify DuplicateTracker.objects.create was called
        mock_duplicate_tracker.objects.create.assert_called_once()
        args = mock_duplicate_tracker.objects.create.call_args[1]
        self.assertEqual(args['stix_object'], mock_stix_obj)
        
        # Verify ThreatIntelligence.objects.create was called
        mock_threat_intel.objects.create.assert_called_once()
        args = mock_threat_intel.objects.create.call_args[1]
        self.assertEqual(args['stix_object'], mock_stix_obj)
        self.assertEqual(args['name'], self.indicator_object['name'])
        self.assertEqual(args['description'], self.indicator_object['description'])
    
    def test_save_to_database_duplicate(self, *mocks):
        """Test handling a duplicate object."""
        # Mock objects
        mock_duplicate_tracker = mocks[0]
        mock_stix_object = mocks[1]
        mock_threat_intel = mocks[2]
        
        # Mock duplicate check to return True
        mock_filter = mock.MagicMock()
        mock_filter.exists.return_value = True
        mock_duplicate_tracker.objects.filter.return_value = mock_filter
        
        # Mock StixObject.objects.get
        mock_stix_obj = mock.MagicMock()
        mock_stix_object.objects.get.return_value = mock_stix_obj
        
        # Normalize an indicator
        normalized = self.processor.normalize_to_internal(self.indicator_object)
        
        # Generate hash
        object_hash = self.processor.generate_object_hash(self.indicator_object)
        
        # Save to database
        result, created = self.processor.save_to_database(normalized)
        
        # Check result
        self.assertEqual(result, mock_stix_obj)
        self.assertFalse(created)
        self.assertEqual(self.processor.duplicate_count, 1)
        
        # Verify StixObject.objects.get was called
        mock_stix_object.objects.get.assert_called_once_with(object_hash=object_hash)
        
        # Verify StixObject.objects.create was NOT called
        mock_stix_object.objects.create.assert_not_called()
        
        # Verify ThreatIntelligence.objects.create was NOT called
        mock_threat_intel.objects.create.assert_not_called()
    
    def test_save_to_database_education_relevant(self, *mocks):
        """Test saving an education-relevant object."""
        # Mock objects
        mock_duplicate_tracker = mocks[0]
        mock_stix_object = mocks[1]
        mock_threat_intel = mocks[2]
        
        # Mock duplicate check
        mock_filter = mock.MagicMock()
        mock_filter.exists.return_value = False
        mock_duplicate_tracker.objects.filter.return_value = mock_filter
        
        # Mock StixObject creation
        mock_stix_obj = mock.MagicMock()
        mock_stix_object.objects.create.return_value = mock_stix_obj
        
        # Normalize an education-related indicator
        normalized = self.processor.normalize_to_internal(self.education_related_object)
        
        # Save to database
        result, created = self.processor.save_to_database(normalized)
        
        # Check result
        self.assertEqual(result, mock_stix_obj)
        self.assertTrue(created)
        self.assertEqual(self.processor.edu_relevant_count, 1)
        
        # Verify StixObject.objects.create was called with is_education_relevant=True
        mock_stix_object.objects.create.assert_called_once()
        args = mock_stix_object.objects.create.call_args[1]
        self.assertTrue(args['is_education_relevant'])
    
    @mock.patch('feed_consumption.data_processor.DataProcessor.validate_stix_object')
    @mock.patch('feed_consumption.data_processor.DataProcessor.normalize_to_internal')
    @mock.patch('feed_consumption.data_processor.DataProcessor.save_to_database')
    def test_process_object_success(self, mock_save, mock_normalize, mock_validate, *mocks):
        """Test successful processing of a single object."""
        # Configure mocks
        mock_validate.return_value = True
        mock_normalize.return_value = {'normalized': 'data'}
        mock_save.return_value = (mock.MagicMock(), True)
        
        # Process an indicator
        result = self.processor.process_object(self.indicator_object)
        
        # Check result
        self.assertEqual(result, {'normalized': 'data'})
        self.assertEqual(self.processor.processed_count, 1)
        self.assertEqual(self.processor.failed_count, 0)
        
        # Verify methods were called
        mock_validate.assert_called_once_with(self.indicator_object)
        mock_normalize.assert_called_once_with(self.indicator_object)
        mock_save.assert_called_once_with({'normalized': 'data'})
    
    @mock.patch('feed_consumption.data_processor.DataProcessor.validate_stix_object')
    def test_process_object_validation_error(self, mock_validate, *mocks):
        """Test processing an object that fails validation."""
        # Configure mock to raise exception
        mock_validate.side_effect = StixValidationError("Validation failed")
        
        # Process an indicator
        result = self.processor.process_object(self.indicator_object)
        
        # Check result
        self.assertIsNone(result)
        self.assertEqual(self.processor.processed_count, 0)
        self.assertEqual(self.processor.failed_count, 1)
    
    @mock.patch('feed_consumption.data_processor.DataProcessor.validate_stix_object')
    @mock.patch('feed_consumption.data_processor.DataProcessor.normalize_to_internal')
    @mock.patch('feed_consumption.data_processor.DataProcessor.save_to_database')
    def test_process_object_database_error(self, mock_save, mock_normalize, mock_validate, *mocks):
        """Test processing an object that fails to save to the database."""
        # Configure mocks
        mock_validate.return_value = True
        mock_normalize.return_value = {'normalized': 'data'}
        mock_save.side_effect = IntegrityError("Database error")
        
        # Process an indicator
        result = self.processor.process_object(self.indicator_object)
        
        # Check result
        self.assertIsNone(result)
        self.assertEqual(self.processor.processed_count, 0)
        self.assertEqual(self.processor.failed_count, 1)
        
        # Check log entry was updated with error
        self.assertIn("Database error", self.log_entry.error_message)
    
    @mock.patch('feed_consumption.data_processor.DataProcessor.process_object')
    def test_process_objects(self, mock_process_object, *mocks):
        """Test processing a batch of objects."""
        # Configure mock
        def side_effect(obj):
            if obj['id'] == self.indicator_object['id']:
                self.processor.processed_count += 1
                return {'processed': 'indicator'}
            elif obj['id'] == self.malware_object['id']:
                self.processor.processed_count += 1
                return {'processed': 'malware'}
            else:
                self.processor.failed_count += 1
                return None
                
        mock_process_object.side_effect = side_effect
        
        # Process a batch of objects
        objects = [
            self.indicator_object,
            self.malware_object,
            {'id': 'invalid-object', 'type': 'unknown'}
        ]
        
        result = self.processor.process_objects(objects)
        
        # Check result
        self.assertEqual(result['processed'], 2)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['duplicates'], 0)
        self.assertEqual(result['edu_relevant'], 0)
        
        # Verify log entry was updated
        self.log_entry.refresh_from_db()
        self.assertEqual(self.log_entry.objects_processed, 2)
        self.assertEqual(self.log_entry.objects_failed, 1)
        self.assertEqual(self.log_entry.status, FeedConsumptionLog.ConsumptionStatus.PARTIAL)
        self.assertIsNotNone(self.log_entry.end_time)
    
    @mock.patch('feed_consumption.data_processor.DataProcessor.process_object')
    def test_process_objects_all_success(self, mock_process_object, *mocks):
        """Test processing a batch where all objects succeed."""
        # Configure mock
        def side_effect(obj):
            self.processor.processed_count += 1
            if obj['type'] == 'indicator':
                return {'processed': 'indicator'}
            else:
                return {'processed': 'malware'}
                
        mock_process_object.side_effect = side_effect
        
        # Process a batch of objects
        objects = [self.indicator_object, self.malware_object]
        
        result = self.processor.process_objects(objects)
        
        # Check result
        self.assertEqual(result['processed'], 2)
        self.assertEqual(result['failed'], 0)
        
        # Verify log entry was updated
        self.log_entry.refresh_from_db()
        self.assertEqual(self.log_entry.status, FeedConsumptionLog.ConsumptionStatus.SUCCESS)
    
    @mock.patch('feed_consumption.data_processor.DataProcessor.process_object')
    def test_process_objects_all_fail(self, mock_process_object, *mocks):
        """Test processing a batch where all objects fail."""
        # Configure mock
        def side_effect(obj):
            self.processor.failed_count += 1
            return None
                
        mock_process_object.side_effect = side_effect
        
        # Process a batch of objects
        objects = [self.indicator_object, self.malware_object]
        
        result = self.processor.process_objects(objects)
        
        # Check result
        self.assertEqual(result['processed'], 0)
        self.assertEqual(result['failed'], 2)
        
        # Verify log entry was updated
        self.log_entry.refresh_from_db()
        self.assertEqual(self.log_entry.status, FeedConsumptionLog.ConsumptionStatus.FAILURE)
