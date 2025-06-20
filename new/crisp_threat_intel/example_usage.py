"""
Example usage of the CRISP threat intelligence platform

This module demonstrates how to use the various components of the platform.
"""

from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
from datetime import timedelta

from .domain.models import Institution, User, ThreatFeed, Indicator, TTPData, TrustRelationship
from .services.threat_feed_service import ThreatFeedService
from .services.indicator_service import IndicatorService
from .services.ttp_service import TTPService
from .services.stix_taxii_service import StixTaxiiService
from .strategies.anonymization_strategy import AnonymizationContext, AnonymizationStrategyFactory
from .factories.stix_object_creator import StixObjectFactory
from .decorators.stix_decorators import StixObject, StixValidationDecorator, StixEnrichmentDecorator
from .observers.feed_observers import InstitutionObserver, AlertSystemObserver


def demo_basic_setup():
    """Demonstrate basic platform setup"""
    print("=== CRISP Platform Demo: Basic Setup ===")
    
    # Create Django users
    django_user1 = DjangoUser.objects.create_user(
        username='analyst1',
        email='analyst1@university-a.edu',
        password='secure_password'
    )
    
    django_user2 = DjangoUser.objects.create_user(
        username='analyst2',
        email='analyst2@university-b.edu',
        password='secure_password'
    )
    
    # Create institutions
    university_a = Institution.objects.create(
        name='University A',
        description='A leading research university',
        sectors=['education'],
        contact_email='security@university-a.edu',
        created_by=django_user1
    )
    
    university_b = Institution.objects.create(
        name='University B',
        description='Another research university',
        sectors=['education'],
        contact_email='security@university-b.edu',
        created_by=django_user2
    )
    
    # Create CRISP users
    user1 = User.objects.create(
        django_user=django_user1,
        institution=university_a,
        role='analyst'
    )
    
    user2 = User.objects.create(
        django_user=django_user2,
        institution=university_b,
        role='analyst'
    )
    
    print(f"Created institutions: {university_a.name}, {university_b.name}")
    print(f"Created users: {user1}, {user2}")
    
    return university_a, university_b, user1, user2


def demo_threat_feed_management(university_a, user1):
    """Demonstrate threat feed management"""
    print("\n=== CRISP Platform Demo: Threat Feed Management ===")
    
    # Create threat feed service
    feed_service = ThreatFeedService()
    
    # Create a threat feed
    feed_data = {
        'name': 'University A Malware Feed',
        'description': 'Feed containing malware indicators detected on campus',
        'update_interval': 3600,  # 1 hour
        'query_parameters': {
            'confidence_threshold': 70,
            'labels': ['malware', 'malicious-activity']
        }
    }
    
    threat_feed = feed_service.create_threat_feed(university_a, user1, feed_data)
    print(f"Created threat feed: {threat_feed.name}")
    
    # Get feed statistics
    stats = feed_service.get_feed_statistics(str(threat_feed.id))
    print(f"Feed statistics: {stats}")
    
    return threat_feed


def demo_indicator_management(threat_feed, user1):
    """Demonstrate indicator management"""
    print("\n=== CRISP Platform Demo: Indicator Management ===")
    
    # Create indicator service
    indicator_service = IndicatorService()
    
    # Create indicators
    indicators_data = [
        {
            'name': 'Malicious IP Address',
            'description': 'IP address used in phishing campaign',
            'pattern': "[ipv4-addr:value = '192.0.2.1']",
            'labels': ['malicious-activity', 'phishing'],
            'confidence': 85,
            'valid_from': timezone.now()
        },
        {
            'name': 'Suspicious Domain',
            'description': 'Domain hosting malware',
            'pattern': "[domain-name:value = 'evil.example.com']",
            'labels': ['malicious-activity', 'malware'],
            'confidence': 90,
            'valid_from': timezone.now()
        },
        {
            'name': 'Malware Hash',
            'description': 'SHA256 hash of known malware',
            'pattern': "[file:hashes.'SHA-256' = 'abc123def456789...']",
            'labels': ['malicious-activity', 'malware'],
            'confidence': 95,
            'valid_from': timezone.now()
        }
    ]
    
    indicators = []
    for indicator_data in indicators_data:
        indicator = indicator_service.create_indicator(threat_feed, user1, indicator_data)
        indicators.append(indicator)
        print(f"Created indicator: {indicator.name}")
    
    # Validate a pattern
    validation_result = indicator_service.validate_indicator_pattern(
        "[ipv4-addr:value = '10.0.0.1']", 'stix'
    )
    print(f"Pattern validation result: {validation_result}")
    
    return indicators


def demo_ttp_management(threat_feed, user1):
    """Demonstrate TTP management"""
    print("\n=== CRISP Platform Demo: TTP Management ===")
    
    # Create TTP service
    ttp_service = TTPService()
    
    # Create TTPs
    ttps_data = [
        {
            'name': 'Spearphishing Link',
            'description': 'Adversaries may send spearphishing emails with malicious links',
            'kill_chain_phases': [
                {'kill_chain_name': 'mitre-attack', 'phase_name': 'initial-access'}
            ],
            'x_mitre_platforms': ['Linux', 'macOS', 'Windows'],
            'x_mitre_tactics': ['initial-access'],
            'x_mitre_techniques': ['T1566.002'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1566.002',
                    'url': 'https://attack.mitre.org/techniques/T1566/002/'
                }
            ]
        },
        {
            'name': 'Command and Scripting Interpreter',
            'description': 'Adversaries may abuse command and script interpreters',
            'kill_chain_phases': [
                {'kill_chain_name': 'mitre-attack', 'phase_name': 'execution'}
            ],
            'x_mitre_platforms': ['Linux', 'macOS', 'Windows'],
            'x_mitre_tactics': ['execution'],
            'x_mitre_techniques': ['T1059'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1059',
                    'url': 'https://attack.mitre.org/techniques/T1059/'
                }
            ]
        }
    ]
    
    ttps = []
    for ttp_data in ttps_data:
        ttp = ttp_service.create_ttp(threat_feed, user1, ttp_data)
        ttps.append(ttp)
        print(f"Created TTP: {ttp.name}")
    
    # Get TTP statistics
    stats = ttp_service.get_ttp_statistics(threat_feed)
    print(f"TTP statistics: {stats}")
    
    return ttps


def demo_trust_relationships(university_a, university_b, user1):
    """Demonstrate trust relationship management"""
    print("\n=== CRISP Platform Demo: Trust Relationships ===")
    
    # Create trust relationship
    trust_relationship = TrustRelationship.objects.create(
        source_institution=university_a,
        target_institution=university_b,
        trust_level=0.8,  # High trust
        established_by=user1
    )
    
    print(f"Created trust relationship: {trust_relationship}")
    print(f"Trust level: {trust_relationship.trust_level}")
    
    return trust_relationship


def demo_anonymization(indicators, ttps, university_a, university_b):
    """Demonstrate anonymization strategies"""
    print("\n=== CRISP Platform Demo: Anonymization ===")
    
    # Create STIX objects from domain models
    stix_objects = []
    for indicator in indicators:
        stix_data = indicator.to_stix()
        stix_objects.append(stix_data)
    
    for ttp in ttps:
        stix_data = ttp.to_stix()
        stix_objects.append(stix_data)
    
    # Demonstrate different anonymization strategies
    strategies = ['none', 'partial', 'full']
    trust_levels = [0.9, 0.6, 0.2]
    
    for strategy_name, trust_level in zip(strategies, trust_levels):
        print(f"\n--- {strategy_name.title()} Anonymization (Trust Level: {trust_level}) ---")
        
        strategy = AnonymizationStrategyFactory.get_strategy(strategy_name)
        context = AnonymizationContext(strategy)
        
        for i, stix_obj in enumerate(stix_objects[:2]):  # Just show first 2 objects
            anonymized = context.anonymize_data(stix_obj, trust_level)
            
            print(f"Original {stix_obj['type']}: {stix_obj.get('name', 'N/A')}")
            print(f"Anonymized {anonymized['type']}: {anonymized.get('name', 'N/A')}")
            
            if stix_obj['type'] == 'indicator':
                print(f"  Original pattern: {stix_obj.get('pattern', 'N/A')}")
                print(f"  Anonymized pattern: {anonymized.get('pattern', 'N/A')}")


def demo_stix_creation_and_decoration():
    """Demonstrate STIX object creation and decoration"""
    print("\n=== CRISP Platform Demo: STIX Creation and Decoration ===")
    
    # Create STIX object using factory
    indicator_data = {
        'type': 'indicator',
        'name': 'Demo Indicator',
        'pattern': "[file:name = 'malware.exe']",
        'labels': ['malicious-activity'],
        'valid_from': timezone.now().isoformat()
    }
    
    stix_obj = StixObjectFactory.create_stix_object(indicator_data)
    print(f"Created STIX object: {stix_obj.get_type()}")
    
    # Add validation decorator
    validator = StixValidationDecorator(stix_obj)
    is_valid = validator.validate()
    validation_results = validator.get_validation_results()
    
    print(f"Validation result: {is_valid}")
    if validation_results['warnings']:
        print(f"Warnings: {validation_results['warnings']}")
    
    # Add enrichment decorator
    enrichment_decorator = StixEnrichmentDecorator(stix_obj)
    
    # Add confidence score
    enrichment_decorator.add_confidence_score(85, 'automated-analysis')
    
    # Add external reference
    enrichment_decorator.add_external_reference(
        source_name='internal-analysis',
        description='Detected in internal security scan'
    )
    
    # Add context information
    enrichment_decorator.add_context_information(
        'detection_method',
        {'scanner': 'antivirus', 'detection_time': timezone.now().isoformat()}
    )
    
    enriched_data = enrichment_decorator.to_dict()
    print(f"Enriched STIX object confidence: {enriched_data.get('confidence')}")
    print(f"External references count: {len(enriched_data.get('external_references', []))}")


def demo_observer_pattern(threat_feed):
    """Demonstrate observer pattern"""
    print("\n=== CRISP Platform Demo: Observer Pattern ===")
    
    # Create observers
    institution_observer = InstitutionObserver(threat_feed.institution)
    alert_observer = AlertSystemObserver({
        'high_volume_threshold': 5,
        'error_threshold': 3
    })
    
    # Add observers to threat feed
    threat_feed.add_observer(institution_observer)
    threat_feed.add_observer(alert_observer)
    
    # Trigger notifications
    threat_feed.notify_observers('test_event', {
        'message': 'This is a test notification',
        'object_count': 10
    })
    
    print("Observers notified successfully")


def demo_stix_taxii_service(threat_feed, indicators, ttps, university_b):
    """Demonstrate STIX/TAXII service operations"""
    print("\n=== CRISP Platform Demo: STIX/TAXII Service ===")
    
    # Create STIX/TAXII service
    stix_taxii_service = StixTaxiiService()
    
    # Create STIX bundle
    objects = indicators + ttps
    bundle = stix_taxii_service.create_stix_bundle(objects)
    
    print(f"Created STIX bundle with {len(bundle['objects'])} objects")
    print(f"Bundle ID: {bundle['id']}")
    
    # Create anonymized bundle for sharing with University B
    anonymized_bundle = stix_taxii_service.create_anonymized_bundle(
        objects, university_b, threat_feed.institution
    )
    
    print(f"Created anonymized bundle with {len(anonymized_bundle['objects'])} objects")
    
    # Validate STIX objects
    for i, obj in enumerate(bundle['objects'][:2]):  # Validate first 2 objects
        validation_result = stix_taxii_service.validate_stix_object(obj)
        print(f"Object {i+1} validation: {validation_result['is_valid']}")
        if validation_result['warnings']:
            print(f"  Warnings: {validation_result['warnings']}")


def run_complete_demo():
    """Run complete demonstration of CRISP platform features"""
    print("🚀 Starting CRISP Threat Intelligence Platform Demo")
    print("=" * 60)
    
    try:
        # Basic setup
        university_a, university_b, user1, user2 = demo_basic_setup()
        
        # Threat feed management
        threat_feed = demo_threat_feed_management(university_a, user1)
        
        # Indicator management
        indicators = demo_indicator_management(threat_feed, user1)
        
        # TTP management
        ttps = demo_ttp_management(threat_feed, user1)
        
        # Trust relationships
        trust_relationship = demo_trust_relationships(university_a, university_b, user1)
        
        # Anonymization
        demo_anonymization(indicators, ttps, university_a, university_b)
        
        # STIX creation and decoration
        demo_stix_creation_and_decoration()
        
        # Observer pattern
        demo_observer_pattern(threat_feed)
        
        # STIX/TAXII service
        demo_stix_taxii_service(threat_feed, indicators, ttps, university_b)
        
        print("\n" + "=" * 60)
        print("✅ CRISP Platform Demo completed successfully!")
        print("All major components demonstrated:")
        print("  - Domain models and relationships")
        print("  - Factory pattern for STIX object creation")
        print("  - Strategy pattern for anonymization")
        print("  - Decorator pattern for STIX enhancement")
        print("  - Observer pattern for notifications")
        print("  - Service layer for business logic")
        print("  - Repository layer for data access")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


if __name__ == '__main__':
    # This would be run in a Django management command or shell
    run_complete_demo()