#!/usr/bin/env python
"""
Script to test the functionality of the Threat Intelligence Publication Service.
This creates sample STIX objects, publishes them, and tests the anonymization.
"""
import os
import sys
import json
import uuid
import django
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Q 
import stix2


from datetime import datetime, timedelta
from copy import deepcopy
import time
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import stix2.utils # For formatting timestamps


# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threat_intel.settings')
django.setup()

from django.contrib.auth.models import User, Group # This import is likely causing the issue if it's before django.setup() or if setup isn't effective
from core.models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity

# Import models
from django.contrib.auth.models import User, Group
from core.models import Organization, STIXObject, Collection, CollectionObject, Feed, Identity
from trust.models import TrustRelationship, TrustGroup, TrustGroupMembership
from stix_factory.factory import STIXObjectFactoryRegistry
from stix_factory.validators import STIXValidator
from anonymization.strategy import AnonymizationStrategyFactory
from core.utils import (
    get_or_create_identity,
    generate_bundle_from_collection,
    publish_feed,
    process_csv_to_stix
)
from core.security import SecurityValidator, DataIntegrityValidator

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Test Statistics ---
class TestStats:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.timings = {}
        self.errors = []

    def record_pass(self, test_name):
        self.passed += 1
        logger.info(f"PASS: {test_name}")

    def record_fail(self, test_name, error_message):
        self.failed += 1
        self.errors.append(f"FAIL: {test_name} - {error_message}")
        logger.error(f"FAIL: {test_name} - {error_message}")

    def record_skip(self, test_name, reason):
        self.skipped += 1
        logger.warning(f"SKIP: {test_name} - {reason}")

    def record_timing(self, test_name, duration):
        self.timings[test_name] = duration
        logger.info(f"TIME: {test_name} - {duration:.4f}s")

    def print_summary(self):
        total_tests = self.passed + self.failed + self.skipped
        logger.info("\n" + "="*30 + " TEST SUMMARY " + "="*30)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Skipped: {self.skipped}")
        if self.failed > 0:
            logger.error("\n--- Detailed Failures ---")
            for error in self.errors:
                logger.error(error)
        logger.info("\n--- Test Timings (seconds) ---")
        for name, duration in sorted(self.timings.items(), key=lambda item: item[1], reverse=True):
            logger.info(f"{name}: {duration:.4f}")
        logger.info("="*74 + "\n")

stats = TestStats()

# --- Enhanced Test Helper Functions ---

def timed_test(func):
    def wrapper(*args, **kwargs):
        test_name = func.__name__
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            stats.record_pass(test_name)
            return result
        except AssertionError as e:
            stats.record_fail(test_name, str(e))
        except Exception as e:
            stats.record_fail(test_name, f"Unexpected error: {type(e).__name__} - {str(e)}")
        finally:
            duration = time.time() - start_time
            stats.record_timing(test_name, duration)
    return wrapper

def get_admin_user():
    """Get or create admin user."""
    user, created = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True, 'email': 'test_admin@example.com'}
    )
    if created:
        user.set_password('admin_password')
        user.save()
        logger.info("Created test_admin user.")
    return user

@timed_test
def setup_organizations():
    """Create or get multiple organizations for testing."""
    logger.info("\n--- Setting up Organizations ---")
    org_names = [
        "Org Alpha Publisher", "Org Beta Subscriber HighTrust", "Org Gamma Subscriber MediumTrust",
        "Org Delta Subscriber LowTrust", "Org Epsilon Subscriber NoTrust", "Org Zeta Isolated"
    ]
    orgs = {}
    admin_user = get_admin_user()
    for name in org_names:
        org, created = Organization.objects.get_or_create(
            name=name,
            defaults={
                'description': f"Test organization {name}",
                'created_by': admin_user,
                'identity_class': 'organization',
                'sectors': ['education', 'research' if 'Research' in name else 'general'],
                # Ensure stix_id is unique and set if not auto-generated by a signal
                'stix_id': f"identity--{str(uuid.uuid4())}"
            }
        )
        # Ensure identity object is created/linked
        get_or_create_identity(org)
        orgs[name] = org
        logger.info(f"Ensured organization: {name} (ID: {org.id}, STIX ID: {org.stix_identity.stix_id if hasattr(org, 'stix_identity') and org.stix_identity else 'N/A'})")
    assert len(orgs) == len(org_names), "Not all organizations were created/retrieved."
    return orgs

@timed_test
def setup_trust_relationships(organizations, admin_user):
    """Sets up diverse trust relationships between organizations."""
    logger.info("\n--- Setting up Trust Relationships ---")
    org_alpha = organizations["Org Alpha Publisher"]
    org_beta = organizations["Org Beta Subscriber HighTrust"]
    org_gamma = organizations["Org Gamma Subscriber MediumTrust"]
    org_delta = organizations["Org Delta Subscriber LowTrust"]

    relationships_config = [
        (org_alpha, org_beta, 0.9, 'none', "Alpha to Beta High Trust"),
        (org_alpha, org_gamma, 0.6, 'partial', "Alpha to Gamma Medium Trust"),
        (org_alpha, org_delta, 0.3, 'full', "Alpha to Delta Low Trust"),
        (org_beta, org_alpha, 0.8, 'none', "Beta to Alpha (mutual high)"),
    ]
    created_rels = []
    for src, tgt, level, anon_type, notes in relationships_config:
        # The TrustRelationship model does not have a 'created_by' field.
        # Audit logs would capture user actions if these were created via views.
        # For direct model creation in tests, 'created_by' is not applicable here.
        rel, created = TrustRelationship.objects.update_or_create(
            source_organization=src,
            target_organization=tgt,
            defaults={
                'trust_level': Decimal(str(level)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP),
                'anonymization_strategy': anon_type,
                'notes': notes
                # Removed 'created_by': admin_user
            }
        )
        rel.refresh_from_db()
        logger.info(f"Ensured trust: {src.name} -> {tgt.name} (Level: {rel.trust_level}, Anon: {rel.anonymization_strategy}) {'Created' if created else 'Exists'}")
        created_rels.append(rel)

    assert len(created_rels) == len(relationships_config), "Not all trust relationships were set up."
    beta_rel = TrustRelationship.objects.get(source_organization=org_alpha, target_organization=org_beta)
    # The model's save method might adjust anonymization_strategy based on trust_level.
    # For a 0.9 trust level, 'none' strategy is expected.
    expected_anon_strat_for_beta = 'none' # Based on TrustRelationship.save() logic
    assert beta_rel.anonymization_strategy == expected_anon_strat_for_beta, \
        f"Expected '{expected_anon_strat_for_beta}' anon for high trust {org_alpha.name}->{org_beta.name}, got {beta_rel.anonymization_strategy}"


@timed_test
def setup_collections(orgs, admin_user):
    """Create various collections for different organizations and purposes."""
    logger.info("\n--- Setting up Collections ---")
    collections = {}
    # Using slugs for aliases for URL-friendliness
    collection_configs = [
        (orgs["Org Alpha Publisher"], "Alpha Main Indicators", "Primary indicator feed from Alpha", "alpha-main-indicators", True, True, ['application/stix+json;version=2.1'], 'partial'),
        (orgs["Org Alpha Publisher"], "Alpha Malware Research", "Internal malware research data", "alpha-malware-research", True, True, ['application/stix+json;version=2.1'], 'none'),
        (orgs["Org Beta Subscriber HighTrust"], "Beta Shared TTPs", "TTPs shared by Beta community", "beta-shared-ttps", True, False, ['application/stix+json;version=2.1'], 'partial'),
        (orgs["Org Alpha Publisher"], "Alpha Empty Collection", "An empty collection from Alpha", "alpha-empty", True, True, [], 'full'),
        (orgs["Org Alpha Publisher"], "Alpha Bulk Test Collection", "For testing bulk uploads", "alpha-bulk-test", True, True, ['application/stix+json;version=2.1'], 'partial'),
    ]

    for owner, title, desc, alias, can_read, can_write, media_types, default_anon in collection_configs:
        coll, created = Collection.objects.update_or_create(
            alias=alias, # Alias should be unique
            owner=owner,
            defaults={
                'title': title,
                'description': desc,
                'can_read': can_read,
                'can_write': can_write,
                'media_types': media_types,
                'default_anonymization': default_anon,
            }
        )
        collections[title] = coll
        logger.info(f"Ensured collection: {title} (ID: {coll.id}, Alias: {coll.alias}) {'Created' if created else 'Exists'}")
    assert len(collections) == len(collection_configs), "Not all collections were created/retrieved."
    return collections


def create_stix_object_via_factory(organization: Organization, stix_data: dict, collection: Optional[Collection] = None, created_by_user=None) -> STIXObject:
    """Helper to create and save STIX object and link to collection."""
    identity_sdo = get_or_create_identity(organization) # Returns STIX SDO dict
    stix_data['created_by_ref'] = identity_sdo['id']

    if 'created' not in stix_data:
        stix_data['created'] = stix2.utils.format_datetime(timezone.now())
    if 'modified' not in stix_data:
        stix_data['modified'] = stix_data['created']
    if 'id' not in stix_data:
         stix_data['id'] = f"{stix_data['type']}--{str(uuid.uuid4())}"
    if 'spec_version' not in stix_data: # <<< FIX for spec_version error
        stix_data['spec_version'] = '2.1'

    validator = STIXValidator()
    validation_result = validator.validate(stix_data)
    assert validation_result['valid'], f"STIX data validation failed for {stix_data.get('id')}: {validation_result['errors']}"

    stix_db_obj, created = STIXObject.objects.update_or_create(
        stix_id=stix_data['id'],
        # source_organization=organization, # This might cause issues if stix_id is not globally unique yet.
                                          # Let's assume stix_id is the primary lookup. If it's an update, source_org should match.
        defaults={
            'stix_type': stix_data['type'],
            'spec_version': stix_data.get('spec_version', '2.1'),
            'created': parse_datetime(stix_data['created']),
            'modified': parse_datetime(stix_data['modified']),
            'created_by_ref': stix_data.get('created_by_ref'),
            'raw_data': stix_data,
            'created_by': created_by_user or get_admin_user(),
            'source_organization': organization, # Set source_organization here
            # 'name': stix_data.get('name', f"Unnamed {stix_data['type']}") # Removed if STIXObject model does not have 'name'
        }
    )
    logger.info(f"Ensured STIX Object in DB: {stix_db_obj.stix_id} ({'Created' if created else 'Exists'})")

    if collection:
        _, co_created = CollectionObject.objects.get_or_create(
            collection=collection,
            stix_object=stix_db_obj
        )
        logger.info(f"Linked {stix_db_obj.stix_id} to collection '{collection.title}' ({'New Link' if co_created else 'Link Exists'})")

    DataIntegrityValidator.validate_stix_object_integrity(stix_db_obj.id) # Pass Django model ID
    logger.info(f"Data integrity validated for STIX Object: {stix_db_obj.stix_id}")

    return stix_db_obj


@timed_test
def test_identity_creation_and_retrieval(organizations):
    logger.info("\n=== Testing Identity Creation and Retrieval ===")
    org_alpha = organizations["Org Alpha Publisher"]
    admin_user = get_admin_user()

    identity_sdo1 = get_or_create_identity(org_alpha)
    assert identity_sdo1 is not None, "Failed to create/retrieve identity SDO for Org Alpha"
    assert identity_sdo1["identity_class"] == "organization", "Identity SDO class mismatch"
    logger.info(f"Identity SDO for {org_alpha.name}: {identity_sdo1['id']}")

    # Validate that a core.models.Identity instance exists with this STIX ID
    db_identity_model = Identity.objects.get(stix_id=identity_sdo1['id'])
    assert db_identity_model.name == org_alpha.name, "core.models.Identity name mismatch"
    assert db_identity_model.organization == org_alpha, "core.models.Identity organization link mismatch"

    # Validate that a STIXObject of type 'identity' exists
    db_stix_object_identity = STIXObject.objects.get(stix_id=identity_sdo1['id'], stix_type='identity')
    assert db_stix_object_identity.source_organization == org_alpha, "STIXObject identity source org mismatch"

    identity_sdo2 = get_or_create_identity(org_alpha)
    assert identity_sdo2["id"] == identity_sdo1["id"], "get_or_create_identity did not retrieve existing identity SDO"
    logger.info(f"Retrieved existing identity SDO for {org_alpha.name}: {identity_sdo2['id']}")

    org_temp, _ = Organization.objects.get_or_create(
        name="Org Temp Identity Test 2",
        defaults={'created_by': admin_user, 'description': 'Temporary org for identity test'}
    )
    identity_sdo3 = get_or_create_identity(org_temp)
    assert identity_sdo3 is not None, "Failed to create identity SDO for new Org Temp"
    assert org_temp.stix_id == identity_sdo3['id'], "Org stix_id not updated by get_or_create_identity"
    
    # Check the Identity model again for the temp org
    db_temp_identity_model = Identity.objects.get(stix_id=identity_sdo3['id'])
    assert db_temp_identity_model.organization == org_temp

    logger.info(f"Created identity SDO for {org_temp.name}: {identity_sdo3['id']}")
    org_temp.delete() # Clean up (will cascade delete Identity model and STIXObject via source_organization if configured)
    logger.info("Identity creation and retrieval tests passed.")


@timed_test
def test_stix_object_creation_variations(org_publisher, collections, admin_user):
    logger.info("\n=== Testing STIX Object Creation Variations ===")
    coll_indicators = collections["Alpha Main Indicators"]
    coll_malware = collections["Alpha Malware Research"]
    created_stix_db_objects = {"indicator": [], "malware": [], "attack-pattern": [], "threat-actor": [], "relationship": []}

    # Indicator
    ind_data = {
        "type": "indicator", "name": "Test IP Indicator v3", "pattern_type": "stix",
        "pattern": "[ipv4-addr:value = '192.0.2.3']",
        "valid_from": stix2.utils.format_datetime(timezone.now()), # Use stix2.utils for formatting
        "description": "A test indicator for a suspicious IP.",
        "spec_version": "2.1" # Explicitly add spec_version
    }
    try:
        db_obj = create_stix_object_via_factory(org_publisher, ind_data, coll_indicators, admin_user)
        created_stix_db_objects["indicator"].append(db_obj)
        assert db_obj.stix_type == "indicator", "Indicator type mismatch"
    except Exception as e:
        logger.error(f"Failed to create indicator: {e}", exc_info=True)
        stats.record_fail("test_stix_object_creation_variations_indicator", str(e))


    # Malware
    mal_data = {
        "type": "malware", "name": "Test Ransomware v3", "is_family": False,
        "malware_types": ["ransomware"], "description": "A test ransomware sample.",
        "spec_version": "2.1"
    }
    try:
        db_obj = create_stix_object_via_factory(org_publisher, mal_data, coll_malware, admin_user)
        created_stix_db_objects["malware"].append(db_obj)
        assert db_obj.stix_type == "malware", "Malware type mismatch"
    except Exception as e:
        logger.error(f"Failed to create malware: {e}", exc_info=True)
        stats.record_fail("test_stix_object_creation_variations_malware", str(e))


    # Attack Pattern
    ap_data = {
        "type": "attack-pattern", "name": "Test Phishing AP v3",
        "description": "A test attack pattern for phishing.",
        "external_references": [{"source_name": "mitre-attack", "external_id": "T1566"}],
        "spec_version": "2.1"
    }
    try:
        db_obj = create_stix_object_via_factory(org_publisher, ap_data, coll_indicators, admin_user)
        created_stix_db_objects["attack-pattern"].append(db_obj)
        assert db_obj.stix_type == "attack-pattern", "Attack Pattern type mismatch"
    except Exception as e:
        logger.error(f"Failed to create attack-pattern: {e}", exc_info=True)
        stats.record_fail("test_stix_object_creation_variations_ap", str(e))

    # Threat Actor
    ta_data = {
        "type": "threat-actor", "name": "Test Actor Group v3",
        "description": "A test threat actor group.", "threat_actor_types": ["crime-syndicate"],
        "spec_version": "2.1"
    }
    try:
        db_obj = create_stix_object_via_factory(org_publisher, ta_data, coll_malware, admin_user)
        created_stix_db_objects["threat-actor"].append(db_obj)
        assert db_obj.stix_type == "threat-actor", "Threat Actor type mismatch"
    except Exception as e:
        logger.error(f"Failed to create threat-actor: {e}", exc_info=True)
        stats.record_fail("test_stix_object_creation_variations_ta", str(e))


    if created_stix_db_objects["indicator"] and created_stix_db_objects["malware"]:
        rel_data = {
            "type": "relationship",
            "source_ref": created_stix_db_objects["indicator"][0].stix_id,
            "target_ref": created_stix_db_objects["malware"][0].stix_id,
            "relationship_type": "indicates", "description": "Test IP v3 indicates Test Ransomware v3.",
            "spec_version": "2.1"
        }
        try:
            db_obj = create_stix_object_via_factory(org_publisher, rel_data, coll_indicators, admin_user)
            created_stix_db_objects["relationship"].append(db_obj)
            assert db_obj.stix_type == "relationship", "Relationship type mismatch"
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}", exc_info=True)
            stats.record_fail("test_stix_object_creation_variations_rel", str(e))
    else:
        logger.warning("Skipping relationship creation as prerequisite indicator or malware failed to create.")
        stats.record_skip("test_stix_object_creation_variations_relationship", "Prerequisite objects missing.")

    logger.info("STIX object creation variations tests completed.")
    if not all(created_stix_db_objects.get(obj_type) for obj_type in ["indicator", "malware", "attack-pattern", "threat-actor"]):
         logger.warning("Not all core STIX object types were successfully created. Subsequent tests might be affected.")
    return created_stix_db_objects

@timed_test
def test_collection_management(org_publisher, collections, created_stix_objects_map, admin_user):
    logger.info("\n=== Testing Collection Management ===")
    coll_target = collections["Alpha Main Indicators"]
    initial_count = coll_target.stix_objects.count()
    logger.info(f"Initial objects in '{coll_target.title}': {initial_count}")

    # Add a new object to the collection (if not already added by creation helper)
    new_ip_data = {
        "type": "indicator", "name": "Collection Test IP", "pattern_type": "stix",
        "pattern": "[ipv4-addr:value = '198.51.100.5']", "valid_from": timezone.now().isoformat()
    }
    new_stix_obj = create_stix_object_via_factory(org_publisher, new_ip_data, created_by_user=admin_user) # Not added to collection yet

    # Explicitly add
    CollectionObject.objects.get_or_create(collection=coll_target, stix_object=new_stix_obj)
    coll_target.refresh_from_db() # Refresh related manager
    count_after_add = coll_target.stix_objects.count()
    logger.info(f"Objects after adding '{new_stix_obj.name}': {count_after_add}")
    assert count_after_add > initial_count, "Object count did not increase after adding."

    # Remove the object
    CollectionObject.objects.filter(collection=coll_target, stix_object=new_stix_obj).delete()
    coll_target.refresh_from_db()
    count_after_remove = coll_target.stix_objects.count()
    logger.info(f"Objects after removing '{new_stix_obj.name}': {count_after_remove}")
    assert count_after_remove == initial_count, "Object count did not revert after removal."

    # Test integrity of a collection
    DataIntegrityValidator.validate_collection_integrity(coll_target)
    logger.info(f"Data integrity validated for collection '{coll_target.title}'")

    empty_coll = collections["Alpha Empty Collection"]
    assert empty_coll.stix_objects.count() == 0, "Empty collection is not empty."
    logger.info("Collection management tests passed.")


@timed_test
def test_anonymization_variations(created_stix_objects_map, organizations):
    logger.info("\n=== Testing Anonymization Variations ===")
    org_alpha = organizations["Org Alpha Publisher"] # Owner
    org_beta_ht = organizations["Org Beta Subscriber HighTrust"]
    org_gamma_mt = organizations["Org Gamma Subscriber MediumTrust"]
    org_delta_lt = organizations["Org Delta Subscriber LowTrust"]
    org_epsilon_nt = organizations["Org Epsilon Subscriber NoTrust"] # No direct trust relationship expected

    indicator_to_test = created_stix_objects_map["indicator"][0]
    original_stix_data = indicator_to_test.to_stix() # This is already a dict
    assert isinstance(original_stix_data, dict), "STIXObject.to_stix() did not return a dict"

    logger.info(f"Original Indicator ({indicator_to_test.stix_id}) for anonymization: {json.dumps(original_stix_data, indent=2)}")

    scenarios = [
        ("None (High Trust)", org_beta_ht, 'none', 0.9), # Trust level for strategy eval
        ("Partial (Medium Trust)", org_gamma_mt, 'partial', 0.6),
        ("Full (Low Trust)", org_delta_lt, 'full', 0.3),
        ("Full (No Trust - Default)", org_epsilon_nt, 'full', 0.0) # Simulate no relationship for default
    ]

    for desc, requesting_org, strategy_name, effective_trust_level in scenarios:
        logger.info(f"\n--- Anonymizing for: {desc} (Requesting Org: {requesting_org.name}) ---")
        anonymization_strategy_instance = AnonymizationStrategyFactory.get_strategy(strategy_name)

        # The anonymize method expects a dict
        anonymized_data = anonymization_strategy_instance.anonymize(deepcopy(original_stix_data), effective_trust_level)
        assert anonymized_data is not None, f"Anonymization returned None for {desc}"
        assert anonymized_data.get("id") == original_stix_data.get("id"), f"Anonymized ID mismatch for {desc}"
        logger.info(f"Anonymized Data ({desc}): {json.dumps(anonymized_data, indent=2)}")

        if strategy_name == "none":
            assert anonymized_data.get("description") == original_stix_data.get("description"), f"'none' strategy changed description for {desc}"
            assert anonymized_data.get("name") == original_stix_data.get("name"), f"'none' strategy changed name for {desc}"
            assert anonymized_data.get("pattern") == original_stix_data.get("pattern"), f"'none' strategy changed pattern for {desc}"
        elif strategy_name == "partial":
            # Name might be anonymized, description should be redacted but exist, pattern transformed
            assert "Anonymized" in anonymized_data.get("name", ""), f"Partial strategy did not anonymize name sufficiently for {desc}"
            assert original_stix_data.get("description") != anonymized_data.get("description"), f"Partial strategy did not alter description for {desc}"
            assert "REDACTED" in anonymized_data.get("description", ""), f"Partial strategy did not redact description for {desc}"
            assert original_stix_data.get("pattern") != anonymized_data.get("pattern"), f"Partial strategy did not alter pattern for {desc}"
            assert "192.0.x.x" in anonymized_data.get("pattern", ""), f"Partial strategy did not anonymize IP in pattern for {desc}" # Based on current IP anon logic
        elif strategy_name == "full":
            assert "Anonymized" in anonymized_data.get("name", ""), f"Full strategy did not anonymize name for {desc}"
            assert "Anonymized indicator description" in anonymized_data.get("description", "") or "Anonymized description" in anonymized_data.get("description",""), f"Full strategy description unexpected for {desc}"
            assert "10.0.0.x" in anonymized_data.get("pattern", "") or "anonymized.domain.tld" in anonymized_data.get("pattern",""), f"Full strategy did not fully anonymize pattern for {desc}"

    logger.info("Anonymization variations tests completed.")

@timed_test
def test_bundle_generation_with_trust(organizations, collections, created_stix_objects_map, admin_user):
    logger.info("\n=== Testing Bundle Generation with Trust Relationships ===")
    org_alpha = organizations["Org Alpha Publisher"]
    coll_alpha_main = collections["Alpha Main Indicators"]

    # Ensure collection has objects
    if not coll_alpha_main.stix_objects.exists():
        logger.info(f"Populating '{coll_alpha_main.title}' for bundle test...")
        # Add one of each type of created object to this collection for diversity
        for stix_type, db_obj_list in created_stix_objects_map.items():
            if db_obj_list: # If any objects of this type were created
                obj_to_add = db_obj_list[0] # Take the first one
                if not CollectionObject.objects.filter(collection=coll_alpha_main, stix_object=obj_to_add).exists():
                    CollectionObject.objects.create(collection=coll_alpha_main, stix_object=obj_to_add)
                    logger.info(f"Added {obj_to_add.stix_id} to {coll_alpha_main.title}")
    coll_alpha_main.refresh_from_db()
    object_count_in_coll = coll_alpha_main.stix_objects.count()
    assert object_count_in_coll > 0, f"Collection {coll_alpha_main.title} is empty, cannot test bundle generation effectively."
    logger.info(f"Collection '{coll_alpha_main.title}' has {object_count_in_coll} STIX objects for bundle generation.")


    test_scenarios = [
        ("Internal View (Org Alpha)", org_alpha, "none"),
        ("High Trust (Org Beta)", organizations["Org Beta Subscriber HighTrust"], "none"),
        ("Medium Trust (Org Gamma)", organizations["Org Gamma Subscriber MediumTrust"], "partial"),
        ("Low Trust (Org Delta)", organizations["Org Delta Subscriber LowTrust"], "full"),
        ("No Trust (Org Epsilon)", organizations["Org Epsilon Subscriber NoTrust"], "full"), # Default should be full
    ]

    for desc, requesting_org, expected_anon_level_for_some_fields in test_scenarios:
        logger.info(f"\n--- Generating Bundle for: {desc} (Requesting: {requesting_org.name}) ---")
        # `generate_bundle_from_collection` uses the trust relationship between collection.owner and requesting_organization
        bundle = generate_bundle_from_collection(coll_alpha_main, requesting_organization=requesting_org)
        assert bundle is not None, f"Bundle generation failed for {desc}"
        assert bundle["type"] == "bundle", f"Bundle type mismatch for {desc}"
        bundle_stix_objects = [obj for obj in bundle.get("objects", []) if obj.get("type") != "identity"]
        logger.info(f"Bundle for {desc} contains {len(bundle_stix_objects)} STIX objects (excluding identities).")

        # Check object count (should match collection count as filtering by trust is about content, not exclusion from bundle)
        assert len(bundle_stix_objects) == object_count_in_coll, \
            f"Object count mismatch for {desc}. Expected {object_count_in_coll}, Got {len(bundle_stix_objects)}"

        # Spot check anonymization on one indicator object's description and pattern
        indicator_in_bundle = next((obj for obj in bundle_stix_objects if obj.get("type") == "indicator"), None)
        original_indicator_db = STIXObject.objects.get(stix_id=indicator_in_bundle["id"]) if indicator_in_bundle else None
        original_indicator_dict = original_indicator_db.to_stix() if original_indicator_db else {}


        if indicator_in_bundle and original_indicator_dict:
            logger.info(f"Checking anonymization for indicator {indicator_in_bundle['id']} in bundle for {desc}")
            logger.info(f"Original Description: {original_indicator_dict.get('description')}")
            logger.info(f"Bundle Description:   {indicator_in_bundle.get('description')}")
            logger.info(f"Original Pattern:     {original_indicator_dict.get('pattern')}")
            logger.info(f"Bundle Pattern:       {indicator_in_bundle.get('pattern')}")

            if expected_anon_level_for_some_fields == "none":
                assert indicator_in_bundle.get("description") == original_indicator_dict.get("description"), f"Description altered for 'none' anon ({desc})"
                assert indicator_in_bundle.get("pattern") == original_indicator_dict.get("pattern"), f"Pattern altered for 'none' anon ({desc})"
            elif expected_anon_level_for_some_fields == "partial":
                assert indicator_in_bundle.get("description") != original_indicator_dict.get("description"), f"Description not altered for 'partial' anon ({desc})"
                assert "REDACTED" in indicator_in_bundle.get("description", ""), f"Description not redacted for 'partial' anon ({desc})"
                assert indicator_in_bundle.get("pattern") != original_indicator_dict.get("pattern"), f"Pattern not altered for 'partial' anon ({desc})"
                # Add more specific checks for partial pattern anonymization if logic is stable
            elif expected_anon_level_for_some_fields == "full":
                assert indicator_in_bundle.get("description") != original_indicator_dict.get("description"), f"Description not altered for 'full' anon ({desc})"
                if original_indicator_dict.get("description"): # Only assert if original had one
                     assert "Anonymized" in indicator_in_bundle.get("description", ""), f"Description not fully anonymized for 'full' anon ({desc})"
                assert indicator_in_bundle.get("pattern") != original_indicator_dict.get("pattern"), f"Pattern not altered for 'full' anon ({desc})"
                # Add more specific checks for full pattern anonymization
        else:
            logger.warning(f"Could not find an indicator object in the bundle for {desc} to check anonymization.")

    logger.info("Bundle generation tests with trust passed.")

@timed_test
def test_feed_management_and_publishing(org_publisher, collections, created_stix_objects_map, admin_user):
    logger.info("\n=== Testing Feed Management and Publishing ===")
    coll_main_indicators = collections["Alpha Main Indicators"]
    coll_empty = collections["Alpha Empty Collection"]

    # Ensure main collection has objects for the feed
    if not coll_main_indicators.stix_objects.exists():
        indicator_obj = created_stix_objects_map["indicator"][0]
        CollectionObject.objects.create(collection=coll_main_indicators, stix_object=indicator_obj)
        logger.info(f"Added {indicator_obj.stix_id} to {coll_main_indicators.title} for feed test.")
    coll_main_indicators.refresh_from_db()
    assert coll_main_indicators.stix_objects.count() > 0, "Feed source collection is empty."


    feed_active, _ = Feed.objects.update_or_create(
        name="Active Indicators Feed",
        collection=coll_main_indicators,
        defaults={
            'description': "Test feed for active indicators", 'update_interval': 3600,
            'status': 'active', 'created_by': admin_user
        }
    )
    feed_empty, _ = Feed.objects.update_or_create(
        name="Empty Collection Feed",
        collection=coll_empty,
        defaults={'description': "Test feed for an empty collection", 'status': 'active', 'created_by': admin_user}
    )
    feed_paused, _ = Feed.objects.update_or_create(
        name="Paused Malware Feed",
        collection=collections["Alpha Malware Research"],
        defaults={'description': "Test feed for paused malware", 'status': 'paused', 'created_by': admin_user}
    )

    # Test publishing active feed
    logger.info(f"--- Publishing Feed: {feed_active.name} ---")
    publish_result = publish_feed(feed_active) # core.utils.publish_feed
    assert publish_result is not None, f"Publishing failed for feed {feed_active.name}"
    assert "published_at" in publish_result, f"Publish result for {feed_active.name} missing 'published_at'"
    # Expected objects = collection objects + 1 (owner identity)
    expected_count_active = coll_main_indicators.stix_objects.count() + 1
    assert publish_result["object_count"] == expected_count_active, \
        f"Published object count mismatch for {feed_active.name}. Expected {expected_count_active}, Got {publish_result['object_count']}"
    feed_active.refresh_from_db()
    assert feed_active.last_published_time is not None, "last_published_time not updated."
    assert feed_active.last_bundle_id == publish_result["bundle_id"], "last_bundle_id mismatch."
    logger.info(f"Feed '{feed_active.name}' published. Bundle ID: {feed_active.last_bundle_id}, Objects: {publish_result['object_count']}")

    # Test publishing empty feed
    logger.info(f"--- Publishing Feed: {feed_empty.name} ---")
    publish_result_empty = publish_feed(feed_empty)
    expected_count_empty = coll_empty.stix_objects.count() + 1 # Should be 1 (just owner identity)
    assert publish_result_empty["object_count"] == expected_count_empty, \
        f"Published object count mismatch for {feed_empty.name}. Expected {expected_count_empty}, Got {publish_result_empty['object_count']}"
    logger.info(f"Feed '{feed_empty.name}' published. Bundle ID: {publish_result_empty['bundle_id']}, Objects: {publish_result_empty['object_count']}")


    # Test publishing paused feed (should not publish or error differently)
    logger.info(f"--- Attempting to Publish Paused Feed: {feed_paused.name} ---")
    try:
        # This depends on how `publish_feed` handles non-active feeds.
        # Assuming it might raise an error or return a specific status.
        # For now, let's assume it might not publish and last_published_time remains None or unchanged.
        initial_paused_pub_time = feed_paused.last_published_time
        publish_feed(feed_paused) # Attempt to publish
        feed_paused.refresh_from_db()
        assert feed_paused.last_published_time == initial_paused_pub_time, "Paused feed was published or its timestamp changed."
        logger.info(f"Paused feed '{feed_paused.name}' correctly not published.")
    except ValueError as e: # Or whatever exception your publish_feed might raise for non-active
        logger.info(f"Correctly handled attempt to publish paused feed: {e}")


    logger.info("Feed management and publishing tests passed.")

@timed_test
def test_simulated_bulk_stix_creation(organization, collection_target, admin_user):
    logger.info(f"\n=== Testing Simulated Bulk STIX Object Creation via CSV processing utility ===")
    logger.info(f"Target collection for bulk upload: '{collection_target.title}'")

    csv_content = """indicator_name,description,tags,confidence_score,ioc_value,pattern_type
Bulk IP Indicator 1,From bulk upload test 1,bulk;internal,80,10.0.0.1,ipv4-addr
Bulk Domain Indicator 2,From bulk upload test 2,bulk;external,70,evil-bulk.com,domain-name
Bulk File Hash Indicator 3,From bulk upload test 3,bulk;malware,90,d41d8cd98f00b204e9800998ecf8427e,file-md5
Invalid Pattern Type,Test,test,50,test.url,url-pattern-invalid
Missing IOC Value,Test,test,50,,ipv4-addr""" # Added invalid row

    # Note: process_csv_to_stix mapping needs to handle different pattern_types based on a CSV column
    # For simplicity, let's assume a flexible mapping or enhance process_csv_to_stix later.
    # Current process_csv_to_stix uses a single pattern_prefix/suffix.
    # This test will highlight the need for more dynamic pattern generation in process_csv_to_stix.
    mapping = {
        "stix_type": "indicator",
        "properties": {
            "name": "indicator_name",
            "description": "description",
            "labels": "tags", # Assuming ';' is the delimiter
            "confidence": "confidence_score",
            # 'pattern' will be constructed
        },
        "pattern_field": "ioc_value", # Field containing the core observable value
        "pattern_type_field": "pattern_type", # Field specifying STIX pattern type (e.g., 'ipv4-addr', 'domain-name')
        "list_delimiter": ";"
    }

    initial_coll_count = collection_target.stix_objects.count()
    processed_stix_dicts = process_csv_to_stix(csv_content, mapping, organization)
    logger.info(f"process_csv_to_stix generated {len(processed_stix_dicts)} STIX dictionaries.")

    created_count_in_db = 0
    for stix_dict in processed_stix_dicts:
        # The create_stix_object_via_factory will handle DB creation and linking
        try:
            create_stix_object_via_factory(organization, stix_dict, collection_target, admin_user)
            created_count_in_db +=1
        except AssertionError as e: # Catch validation errors from create_stix_object_via_factory
            logger.warning(f"Skipping STIX object due to validation error: {stix_dict.get('id', 'N/A')} - {e}")
        except Exception as e:
            logger.error(f"Error processing STIX dict in bulk test: {stix_dict.get('id', 'N/A')} - {e}")


    collection_target.refresh_from_db()
    final_coll_count = collection_target.stix_objects.count()
    logger.info(f"Collection '{collection_target.title}' object count: Before={initial_coll_count}, After={final_coll_count}")

    # Expected successful creations from CSV: 3 valid rows.
    # The `process_csv_to_stix` might filter out the "Missing IOC" one if pattern construction fails.
    # The "Invalid Pattern Type" might also fail in `create_stix_object_via_factory`'s STIX validation step.
    # So, `created_count_in_db` should reflect actually valid and created objects.
    # We expect at least 3 successful.
    assert created_count_in_db >= 3, f"Expected at least 3 STIX objects to be created from valid CSV rows, got {created_count_in_db}"
    assert final_coll_count >= initial_coll_count + 3, f"Collection count did not increase by at least 3 after bulk processing. Got {final_coll_count - initial_coll_count}"
    logger.info(f"Successfully processed and potentially created {created_count_in_db} STIX objects from CSV.")
    logger.info("Simulated bulk STIX object creation test passed (focus on utility function).")


@timed_test
def test_error_handling_scenarios(org_publisher, collections, admin_user, organizations, created_stix_db_objects):
    logger.info("\n=== Testing Error Handling Scenarios ===")
    coll_mixed = collections["Alpha Main Indicators"]
    org_zeta_isolated = organizations.get("Org Zeta Isolated") # Used to create a unique trust relationship

    # Test 1: Invalid STIX object data for factory
    invalid_indicator_data = {"type": "indicator", "name": "Missing Pattern", "spec_version": "2.1"}
    try:
        create_stix_object_via_factory(org_publisher, invalid_indicator_data, coll_mixed, admin_user)
        stats.record_fail("test_error_handling_scenarios_invalid_stix", "Should have raised validation error for invalid indicator data.")
    except AssertionError as e:
        logger.info(f"Successfully caught STIX validation error for invalid indicator: {e}")
    except Exception as e:
        stats.record_fail("test_error_handling_scenarios_invalid_stix", f"Unexpected error for invalid indicator: {type(e).__name__} - {e}")

    # Test 3: Invalid trust level in TrustRelationship
    if org_zeta_isolated and org_publisher != org_zeta_isolated :
        # Attempt to create a new relationship with an org that should not have one with org_publisher yet
        # First, ensure no pre-existing relationship to avoid IntegrityError
        TrustRelationship.objects.filter(source_organization=org_publisher, target_organization=org_zeta_isolated).delete()
        try:
            TrustRelationship.objects.create(
                source_organization=org_publisher,
                target_organization=org_zeta_isolated,
                trust_level=Decimal("2.0"), # Invalid value > 1.0
                anonymization_strategy='none' # This will be overridden by model's save method based on trust_level if validation passed
            )
            # If it gets here, Django's field validation (MaxValueValidator) didn't run or was bypassed.
            stats.record_fail("test_error_handling_scenarios_invalid_trust_level", "Creation with invalid trust_level (2.0) did not raise ValidationError.")
        except django.core.exceptions.ValidationError as e:
            logger.info(f"Successfully caught Django ValidationError for invalid trust level (2.0): {e}")
            # This is the expected outcome for field validation.
        except IntegrityError as e:
            # This case should be less likely now with the delete, but good to log if it happens.
            logger.error(f"IntegrityError during invalid trust level test (unexpected duplicate): {e}")
            stats.record_fail("test_error_handling_scenarios_invalid_trust_level", f"IntegrityError hit for supposedly unique pair: {e}")
        except Exception as e:
            stats.record_fail("test_error_handling_scenarios_invalid_trust_level", f"Unexpected error for invalid trust level: {type(e).__name__} - {e}")
    else:
        stats.record_skip("test_error_handling_scenarios_invalid_trust_level", "Org Zeta Isolated not available or same as publisher, skipping specific trust level validation test.")


    # Test 4: Anonymization strategy not found
    non_existent_strategy = "non_existent_strategy_foo_bar_baz_qux" # Make it very unique
    indicator_list = created_stix_db_objects.get("indicator", []) if created_stix_db_objects else []

    if indicator_list: # Only proceed if an indicator was successfully created earlier
        sample_stix_obj_db = indicator_list[0]
        sample_stix_data = sample_stix_obj_db.to_stix()
        try:
            returned_strategy_instance = AnonymizationStrategyFactory.get_strategy(non_existent_strategy)
            default_strategy_instance = AnonymizationStrategyFactory.get_default_strategy()
            
            # Check if the factory correctly fell back to the default strategy
            if type(returned_strategy_instance) == type(default_strategy_instance) and \
               non_existent_strategy.lower() != getattr(settings, 'ANONYMIZATION_SETTINGS', {}).get('DEFAULT_STRATEGY', 'partial').lower():
                logger.info(f"Non-existent anonymization strategy '{non_existent_strategy}' correctly fell back to default strategy '{type(default_strategy_instance).__name__}'.")
                # This is a pass for the current factory behavior (logs warning, returns default)
            else:
                # This case means either the non-existent strategy was somehow found (unexpected),
                # or it coincidentally matched the default strategy's name while we expected a fallback from a unique name.
                stats.record_fail(
                    "test_error_handling_scenarios_invalid_anon_strategy",
                    f"Expected fallback for non-existent strategy '{non_existent_strategy}'. "
                    f"Got: {type(returned_strategy_instance).__name__}. Default is: {type(default_strategy_instance).__name__}."
                )
        except Exception as e:
            stats.record_fail("test_error_handling_scenarios_invalid_anon_strategy", f"Unexpected error when getting non-existent anonymization strategy: {type(e).__name__} - {e}")
    else:
        stats.record_skip("test_error_handling_scenarios_invalid_anon_strategy", "No indicator STIX object available to test anonymization strategy fallback.")

    logger.info("Error handling scenarios test section completed.")


def check_utility_functions_availability():
    logger.info("\n=== Checking Utility Function Availability ===")
    try:
        # These are already imported at the top, this is more of a conceptual check
        assert callable(get_or_create_identity)
        assert callable(generate_bundle_from_collection)
        assert callable(publish_feed)
        assert callable(process_csv_to_stix)
        logger.info("✓ All required utility functions appear to be available.")
        return True
    except AssertionError:
        logger.error("✗ One or more utility functions are not callable/available.")
        return False
    except NameError as e:
        logger.error(f"✗ Missing utility functions: {e}")
        return False


def cleanup_test_data():
    logger.info("\n--- Cleaning up Test Data ---")
    # Order of deletion matters due to foreign key constraints
    CollectionObject.objects.all().delete()
    logger.info("Deleted CollectionObjects.")
    Feed.objects.filter(name__icontains="Test Feed").delete() # More specific
    Feed.objects.filter(name__icontains="Active Indicators Feed").delete()
    Feed.objects.filter(name__icontains="Empty Collection Feed").delete()
    Feed.objects.filter(name__icontains="Paused Malware Feed").delete()
    logger.info("Deleted Feeds.")
    STIXObject.objects.filter(
        Q(raw_data__name__icontains="Test ") | # Check 'name' within the JSONB field
        Q(stix_id__startswith="indicator--") |
        Q(stix_id__startswith="malware--") |
        Q(stix_id__startswith="relationship--") |
        Q(stix_id__startswith="attack-pattern--") |
        Q(stix_id__startswith="threat-actor--")
    ).delete()
    logger.info("Deleted STIXObjects.")
    Collection.objects.filter(Q(title__icontains="Alpha ") | Q(title__icontains="Beta ")).delete() # More specific
    logger.info("Deleted Collections.")
    TrustRelationship.objects.all().delete()
    logger.info("Deleted TrustRelationships.")
    Identity.objects.filter(Q(name__icontains="Org ") | Q(name__icontains="Test ")).delete()
    logger.info("Deleted Identities.")
    Organization.objects.filter(name__icontains="Org ").delete() # More specific
    logger.info("Deleted Organizations.")
    User.objects.filter(username='test_admin').delete()
    logger.info("Deleted test_admin user.")
    logger.info("Test data cleanup complete.")


def main():
    """Main function to orchestrate the comprehensive testing."""
    logger.info("=== Starting Comprehensive Threat Intelligence Service Functionality Tests ===")
    global stats
    stats = TestStats() # Reset stats for a fresh run

    # Initialize created_stix_objects with the expected structure at the beginning of main
    # This ensures it's always a dictionary with expected keys, even if creation tests fail partially or entirely.
    created_stix_db_objects = {
        "indicator": [],
        "malware": [],
        "attack-pattern": [],
        "threat-actor": [],
        "relationship": []
    }

    try:
        # Perform cleanup before tests
        cleanup_test_data()

        utils_available = check_utility_functions_availability()
        if not utils_available:
            stats.record_skip("main_execution_setup", "Skipping most tests due to missing utility functions.")
            # No early return here, let it fall through to finally for summary

        if utils_available: # Only proceed with main tests if utils are okay
            admin_user = get_admin_user()

            organizations = setup_organizations()
            # Ensure organizations setup was successful before proceeding
            if stats.failed > 0 and any("setup_organizations" in err for err in stats.errors):
                stats.record_skip("main_execution_setup", "Skipping tests due to organization setup failure.")
            else:
                org_alpha_publisher = organizations["Org Alpha Publisher"]

                setup_trust_relationships(organizations, admin_user)
                collections = setup_collections(organizations, admin_user)

                test_identity_creation_and_retrieval(organizations)

                # test_stix_object_creation_variations populates the created_stix_db_objects dictionary
                created_stix_db_objects = test_stix_object_creation_variations(org_alpha_publisher, collections, admin_user)

                # Check if created_stix_db_objects is valid and if any actual objects were created
                # The 'all(created_stix_objects.values())' check was problematic because an empty list is falsy.
                # A better check is if the dict itself is not None and then if specific critical object types were made.
                essential_types_created = True
                if created_stix_db_objects:
                    for essential_type in ["indicator", "malware"]: # Example essential types for further tests
                        if not created_stix_db_objects.get(essential_type):
                            essential_types_created = False
                            logger.warning(f"Essential STIX type '{essential_type}' was not created. Dependent tests may be affected.")
                            break
                else: # If the function somehow returned None or was not assigned
                    logger.error("created_stix_db_objects is None after test_stix_object_creation_variations. Critical failure.")
                    essential_types_created = False
                    # Ensure created_stix_db_objects is at least an empty dict for later .get calls
                    created_stix_db_objects = {key: [] for key in ["indicator", "malware", "attack-pattern", "threat-actor", "relationship"]}


                if essential_types_created:
                    test_collection_management(org_alpha_publisher, collections, created_stix_db_objects, admin_user)
                    test_anonymization_variations(created_stix_db_objects, organizations)
                    test_bundle_generation_with_trust(organizations, collections, created_stix_db_objects, admin_user)
                    test_feed_management_and_publishing(org_alpha_publisher, collections, created_stix_db_objects, admin_user)
                else:
                    stats.record_skip("dependent_tests_after_stix_creation", "Skipping some tests due to critical failures or no objects in STIX object creation.")

                bulk_collection_target = collections.get("Alpha Bulk Test Collection")
                if bulk_collection_target:
                    test_simulated_bulk_stix_creation(org_alpha_publisher, bulk_collection_target, admin_user)
                else:
                    stats.record_skip("test_simulated_bulk_stix_creation", "Target collection for bulk upload not found.")

                # Pass the populated created_stix_db_objects to test_error_handling_scenarios
                test_error_handling_scenarios(org_alpha_publisher, collections, admin_user, organizations, created_stix_db_objects)

    except Exception as e:
        logger.critical(f"CRITICAL ERROR during test execution: {type(e).__name__} - {str(e)}", exc_info=True)
        stats.record_fail("main_execution_critical_error", f"A critical error occurred: {e}")
    finally:
        # Perform cleanup after tests
        # cleanup_test_data() # Optional: comment out if you want to inspect DB state after tests
        stats.print_summary()
        logger.info("=== Comprehensive Threat Intelligence Service Functionality Tests Completed ===")
        if stats.failed > 0:
            sys.exit(1) # Exit with error code if tests failed


if __name__ == "__main__":
    main()