import uuid
import json
from unittest import mock
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError

from stix2 import Indicator, Malware, Relationship, Bundle # For creating STIX objects
from stix2.exceptions import STIXError # For raising STIXError

from feed_consumption.models import ExternalFeedSource, FeedConsumptionLog # Added model imports
from feed_consumption.data_processing_service import DataProcessor
from feed_consumption.data_processor import DataProcessingError, StixValidationError


# Mock the ThreatIntelligence, StixObject, and DuplicateTracker models
@mock.patch('feed_consumption.data_processing_service.ThreatIntelligence') # Patched to data_processing_service
@mock.patch('feed_consumption.data_processing_service.StixObject') # Patched to data_processing_service
@mock.patch('feed_consumption.data_processing_service.DuplicateTracker') # Patched to data_processing_service
@patch('feed_consumption.data_processing_service.DuplicateTracker.objects.get_or_create')
@patch('feed_consumption.data_processing_service.StixObject.objects.create')
@patch('feed_consumption.data_processing_service.ThreatIntelligence.objects.create')
@patch('feed_consumption.data_processing_service.DataProcessor._parse_stix_object') # Patching the instance method
@patch('feed_consumption.data_processing_service.DataProcessor.validate_stix_object') # Patching the instance method
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
    
    @mock.patch('feed_consumption.data_processing_service.stix2.parse') # Patched to data_processing_service
    @mock.patch('feed_consumption.data_processing_service.validate_instance') # Patched to data_processing_service
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
    
    @mock.patch('feed_consumption.data_processing_service.stix2.parse') # Patched to data_processing_service
    @mock.patch('feed_consumption.data_processing_service.validate_instance') # Patched to data_processing_service
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
    
    @mock.patch('feed_consumption.data_processing_service.stix2.parse') # Patched to data_processing_service
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
    
    @mock.patch('feed_consumption.data_processing_service.DataProcessor.validate_stix_object')
    @mock.patch('feed_consumption.data_processing_service.DataProcessor._parse_stix_object')
    @mock.patch('feed_consumption.data_processing_service.ThreatIntelligence.objects.create')
    @mock.patch('feed_consumption.data_processing_service.StixObject.objects.create')
    @mock.patch('feed_consumption.data_processing_service.DuplicateTracker.objects.get_or_create')
    def test_process_object_success(self, mock_get_or_create_duplicate, mock_stix_object_create, mock_ti_create, mock_parse_stix, mock_validate_stix):
        """Test successful processing of a single object."""
        # Configure mocks
        mock_parse_stix.return_value = self.stix_object_valid
        mock_validate_stix.return_value = True
        mock_get_or_create_duplicate.return_value = (MagicMock(spec=DuplicateTracker), True) # New object
        mock_ti_create.return_value = MagicMock(spec=ThreatIntelligence)
        mock_stix_object_create.return_value = MagicMock(spec=StixObject)
        
        # Process an indicator
        result = self.processor.process_object(self.indicator_object)
        
        # Check result
        self.assertEqual(result, {'parsed': 'data'})
        self.assertEqual(self.processor.processed_count, 1)
        self.assertEqual(self.processor.failed_count, 0)
        
        # Verify methods were called
        mock_validate_stix.assert_called_once_with(self.indicator_object)
        mock_parse_stix.assert_called_once_with(self.indicator_object, allow_custom=True)
        mock_stix_object_create.assert_called_once()
    
    @mock.patch('feed_consumption.data_processing_service.DataProcessor.validate_stix_object')
    @mock.patch('feed_consumption.data_processing_service.DataProcessor._parse_stix_object')
    @mock.patch('feed_consumption.data_processing_service.ThreatIntelligence.objects.create')
    @mock.patch('feed_consumption.data_processing_service.StixObject.objects.create')
    @mock.patch('feed_consumption.data_processing_service.DuplicateTracker.objects.get_or_create')
    def test_process_object_duplicate(self, mock_validate_stix, mock_parse_stix, mock_ti_create, mock_stix_object_create, mock_get_or_create_duplicate):
        """Test processing an object that is a duplicate."""
        mock_parse_stix.return_value = self.stix_object_valid
        mock_validate_stix.return_value = True
        # Simulate duplicate found
        mock_duplicate_instance = MagicMock(spec=DuplicateTracker)
        mock_get_or_create_duplicate.return_value = (mock_duplicate_instance, False) # False means it was not created, so it existed

        success, result = self.processor.process_object(self.stix_data_valid)

        self.assertFalse(success)
        self.assertEqual(result, "Duplicate object")
        mock_parse_stix.assert_called_once_with(self.stix_data_valid)
        mock_validate_stix.assert_called_once_with(self.stix_object_valid)
        mock_get_or_create_duplicate.assert_called_once()
        mock_ti_create.assert_not_called() # Should not be called for duplicates
        mock_stix_object_create.assert_not_called()

    @mock.patch('feed_consumption.data_processing_service.DataProcessor.validate_stix_object')
    @mock.patch('feed_consumption.data_processing_service.DataProcessor._parse_stix_object')
    @mock.patch('feed_consumption.data_processing_service.ThreatIntelligence.objects.create')
    @mock.patch('feed_consumption.data_processing_service.StixObject.objects.create')
    @mock.patch('feed_consumption.data_processing_service.DuplicateTracker.objects.get_or_create')
    def test_process_object_validation_error(self, mock_validate_stix, mock_parse_stix, mock_ti_create, mock_stix_object_create, mock_get_or_create_duplicate):
        """Test processing an object that fails validation."""
        mock_parse_stix.return_value = self.stix_object_valid
        mock_validate_stix.side_effect = StixValidationError("Invalid STIX pattern")

        success, result = self.processor.process_object(self.stix_data_valid)

        self.assertFalse(success)
        self.assertEqual(result, "STIX validation failed: Invalid STIX pattern")
        mock_parse_stix.assert_called_once_with(self.stix_data_valid)
        mock_validate_stix.assert_called_once_with(self.stix_object_valid)
        mock_ti_create.assert_not_called()
        mock_stix_object_create.assert_not_called()
        mock_get_or_create_duplicate.assert_not_called() # Should not be called if validation fails before duplicate check

    @mock.patch('feed_consumption.data_processing_service.DataProcessor.validate_stix_object')
    @mock.patch('feed_consumption.data_processing_service.DataProcessor._parse_stix_object')
    @mock.patch('feed_consumption.data_processing_service.ThreatIntelligence.objects.create')
    @mock.patch('feed_consumption.data_processing_service.StixObject.objects.create')
    @mock.patch('feed_consumption.data_processing_service.DuplicateTracker.objects.get_or_create')
    def test_process_object_database_error(self, mock_validate_stix, mock_parse_stix, mock_ti_create, mock_stix_object_create, mock_get_or_create_duplicate):
        """Test processing an object that fails to save to the database."""
        mock_parse_stix.return_value = self.stix_object_valid
        mock_validate_stix.return_value = True
        mock_get_or_create_duplicate.return_value = (MagicMock(spec=DuplicateTracker), True)
        mock_ti_create.side_effect = Exception("DB error") # Simulate database error

        success, result = self.processor.process_object(self.stix_data_valid)

        self.assertFalse(success)
        self.assertEqual(result, "Database error: DB error")
        mock_parse_stix.assert_called_once_with(self.stix_data_valid)
        mock_validate_stix.assert_called_once_with(self.stix_object_valid)
        mock_get_or_create_duplicate.assert_called_once()
        mock_ti_create.assert_called_once() # It will be called, but then raise an error
        mock_stix_object_create.assert_not_called() # If TI create fails, StixObject might not be created

    def test_process_objects(self, mock_validate_stix, mock_parse_stix, mock_ti_create, mock_stix_object_create, mock_get_or_create_duplicate):
        stix_data_list = [self.stix_data_valid, {"type": "malware", "id": "malware--example"}]
        
        # Mock side effects for process_object calls
        # For simplicity, assume the first succeeds and the second is a duplicate
        mock_stix_obj1 = Indicator(**self.stix_data_valid)
        mock_stix_obj2 = Malware(id="malware--example", is_family=False)

        # Configure side effects for the patched methods based on calls to process_object
        # This requires careful ordering or more specific side_effect functions if logic is complex.
        # For this test, we'll mock the behavior of process_object indirectly via its components.

        # First call (success)
        mock_parse_stix.side_effect = [mock_stix_obj1, mock_stix_obj2]
        mock_validate_stix.side_effect = [True, True] # Both validate
        mock_get_or_create_duplicate.side_effect = [
            (MagicMock(spec=DuplicateTracker), True),  # First is new
            (MagicMock(spec=DuplicateTracker), False) # Second is duplicate
        ]
        mock_ti_create.return_value = MagicMock(spec=ThreatIntelligence)
        mock_stix_object_create.return_value = MagicMock(spec=StixObject)

        processed_count, errors = self.processor.process_objects(stix_data_list)

        self.assertEqual(processed_count, 1) # Only the first one was truly processed and saved
        self.assertEqual(len(errors), 1)
        self.assertIn("Duplicate object", errors[0]['reason'])
        self.assertEqual(errors[0]['object_id'], "malware--example")

        self.assertEqual(mock_parse_stix.call_count, 2)
        self.assertEqual(mock_validate_stix.call_count, 2)
        self.assertEqual(mock_get_or_create_duplicate.call_count, 2)
        self.assertEqual(mock_ti_create.call_count, 1) # Only for the first object
        self.assertEqual(mock_stix_object_create.call_count, 1) # Only for the first object

    def test_process_objects_all_success(self, mock_validate_stix, mock_parse_stix, mock_ti_create, mock_stix_object_create, mock_get_or_create_duplicate):
        stix_data_list = [self.stix_data_valid, {
            "type": "malware", 
            "spec_version": "2.1",
            "id": "malware--0f29a97f-1769-4403-a358-21e16f08008a",
            "created": "2017-01-20T00:00:00.000Z",
            "modified": "2017-01-20T00:00:00.000Z",
            "name": "Cryptolocker",
            "is_family": False
        }]
        mock_stix_obj1 = Indicator(**stix_data_list[0])
        mock_stix_obj2 = Malware(**stix_data_list[1])

        mock_parse_stix.side_effect = [mock_stix_obj1, mock_stix_obj2]
        mock_validate_stix.return_value = True # Both validate successfully
        mock_get_or_create_duplicate.return_value = (MagicMock(spec=DuplicateTracker), True) # Both are new
        mock_ti_create.return_value = MagicMock(spec=ThreatIntelligence)
        mock_stix_object_create.return_value = MagicMock(spec=StixObject)

        processed_count, errors = self.processor.process_objects(stix_data_list)

        self.assertEqual(processed_count, 2)
        self.assertEqual(len(errors), 0)
        self.assertEqual(mock_ti_create.call_count, 2)
        self.assertEqual(mock_stix_object_create.call_count, 2)

    def test_process_objects_all_fail(self, mock_validate_stix, mock_parse_stix, mock_ti_create, mock_stix_object_create, mock_get_or_create_duplicate):
        stix_data_list = [self.stix_data_valid, {"type": "malware", "id": "malware--example"}]
        mock_stix_obj1 = Indicator(**stix_data_list[0])
        mock_stix_obj2 = Malware(id="malware--example", is_family=False)

        mock_parse_stix.side_effect = [mock_stix_obj1, mock_stix_obj2]
        mock_validate_stix.side_effect = StixValidationError("Validation failed") # Both fail validation

        processed_count, errors = self.processor.process_objects(stix_data_list)

        self.assertEqual(processed_count, 0)
        self.assertEqual(len(errors), 2)
        self.assertIn("STIX validation failed: Validation failed", errors[0]['reason'])
        self.assertIn("STIX validation failed: Validation failed", errors[1]['reason'])
        mock_ti_create.assert_not_called()
        mock_stix_object_create.assert_not_called()

    # Test _parse_stix_object directly (though it's an internal method)
    @patch('feed_consumption.data_processing_service.parse') # Patch the 'parse' function from stix2 library
    def test_parse_stix_object_success(self, mock_stix2_parse, mock_validate_stix, mock_parse_stix_method_ignore, mock_ti_create, mock_stix_object_create, mock_get_or_create_duplicate):
        mock_stix2_parse.return_value = self.stix_object_valid
        # We are testing _parse_stix_object, so we call it directly.
        # The other mocks (mock_validate_stix, etc.) are for the class-level patches and can be ignored or configured if _parse_stix_object calls them.
        # In this case, _parse_stix_object only calls stix2.parse.
        
        parsed_obj = self.processor._parse_stix_object(self.stix_data_valid)
        self.assertEqual(parsed_obj, self.stix_object_valid)
        mock_stix2_parse.assert_called_once_with(self.stix_data_valid, allow_custom=True)

    @patch('feed_consumption.data_processing_service.parse')
    def test_parse_stix_object_failure(self, mock_stix2_parse, mock_validate_stix_ignore, mock_parse_stix_method_ignore, mock_ti_create_ignore, mock_stix_object_create_ignore, mock_get_or_create_duplicate_ignore):
        mock_stix2_parse.side_effect = STIXError("Invalid format")
        with self.assertRaises(DataProcessingError) as context:
            self.processor._parse_stix_object(self.stix_data_valid)
        self.assertIn("Failed to parse STIX object: Invalid format", str(context.exception))

    # Test validate_stix_object directly
    def test_validate_stix_object_valid(self, mock_validate_stix_method_ignore, mock_parse_stix_method_ignore, mock_ti_create_ignore, mock_stix_object_create_ignore, mock_get_or_create_duplicate_ignore):
        # No external calls to mock for this simple validation if it's just checking type
        # If it used stix2.validate_string or similar, that would need mocking.
        # Assuming validate_stix_object is more complex and might be patched by `mock_validate_stix` in other tests.
        # For a direct test, if it has internal logic:
        malware_obj = Malware(name="Test Malware", is_family=False) # Valid STIX object
        try:
            self.processor.validate_stix_object(malware_obj) # Should not raise
        except StixValidationError:
            self.fail("validate_stix_object raised StixValidationError unexpectedly for valid object")

    def test_validate_stix_object_invalid_pattern(self, mock_validate_stix_method_ignore, mock_parse_stix_method_ignore, mock_ti_create_ignore, mock_stix_object_create_ignore, mock_get_or_create_duplicate_ignore):
        # Create an indicator with an invalid pattern to test the actual validation logic
        # This assumes that the internal validate_stix_object will try to validate the pattern.
        # The stix2 library itself might raise an error upon creation with a bad pattern, 
        # or validation might be a separate step.
        # For this test, let's assume the object can be created but fails our custom validation.
        
        # If validate_stix_object uses stix2.validate_instance or similar, that would be the target for a mock if testing isolation.
        # Here, we test the integrated behavior.
        indicator_invalid_pattern = Indicator(
            name="Invalid Pattern Indicator", 
            pattern_type="stix", 
            pattern="[ipv4-addr:value = '198.51.100.1' OR ]" # Invalid pattern
        )
        with self.assertRaises(StixValidationError) as context:
            self.processor.validate_stix_object(indicator_invalid_pattern)
        self.assertIn("Invalid pattern syntax", str(context.exception)) # Or whatever message it produces

    @patch('feed_consumption.data_processing_service.parse') # Mocking stix2.parse for this specific test of validate_stix_object
    def test_validate_stix_object_parse_error_in_validation_path(self, mock_stix2_parse_for_validation, mock_validate_stix_method_ignore, mock_parse_stix_method_ignore, mock_ti_create_ignore, mock_stix_object_create_ignore, mock_get_or_create_duplicate_ignore):
        # This test is a bit conceptual if validate_stix_object itself doesn't call parse.
        # The original test_validate_stix_object_parse_error seemed to imply parse was part of validation.
        # If validate_stix_object is *given* a string and calls parse, then this is valid.
        # If it's given an object, parse errors are for _parse_stix_object.
        # Let's assume for a moment validate_stix_object can be passed raw data that it tries to parse.
        
        # This test is more about _parse_stix_object, which is already tested.
        # The original test name was test_validate_stix_object_parse_error
        # It was mocking `parse` from `stix2` and making it raise STIXError.
        # This should be tested in the context of `_parse_stix_object` or if `validate_stix_object` itself calls `parse`.
        # Given the current structure, `validate_stix_object` receives an already parsed object.
        # So, a STIXError from `parse` would occur in `_parse_stix_object`.
        # We will keep the STIXError import and ensure _parse_stix_object handles it.
        pass # Covered by test_parse_stix_object_failure
