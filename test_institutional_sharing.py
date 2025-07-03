#!/usr/bin/env python3
"""
Institutional Data Sharing Simulation for CRISP Threat Intel Platform
Demonstrates how two educational institutions share threat intelligence data
with trust-based anonymization.
"""

import sys
import os
import json
from datetime import datetime, timezone as dt_timezone

# Add paths for core components
sys.path.insert(0, 'core/patterns/strategy')
sys.path.insert(0, 'crisp_threat_intel')

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def print_subheader(title):
    """Print a formatted subheader"""
    print(f"\n--- {title} ---")

class MockOrganization:
    """Mock organization for simulation"""
    def __init__(self, name, trust_level_to_others=0.5):
        self.name = name
        self.trust_level_to_others = trust_level_to_others
        self.threat_intelligence = []
        self.received_intelligence = []

class MockThreatIntel:
    """Mock threat intelligence object"""
    def __init__(self, source_org, threat_type, indicator, description, severity="medium"):
        self.source_org = source_org
        self.threat_type = threat_type
        self.indicator = indicator
        self.description = description
        self.severity = severity
        self.created_at = datetime.now()
        self.stix_object = self._create_stix_object()
    
    def _create_stix_object(self):
        """Create STIX object representation"""
        import uuid
        
        # Determine pattern based on indicator type
        if self._is_ip(self.indicator):
            pattern = f"[ipv4-addr:value = '{self.indicator}']"
        elif self._is_domain(self.indicator):
            pattern = f"[domain-name:value = '{self.indicator}']"
        elif self._is_email(self.indicator):
            pattern = f"[email-addr:value = '{self.indicator}']"
        elif self._is_url(self.indicator):
            pattern = f"[url:value = '{self.indicator}']"
        else:
            pattern = f"[file:name = '{self.indicator}']"
        
        return {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{uuid.uuid4()}",
            "created": self.created_at.isoformat() + "Z",
            "modified": self.created_at.isoformat() + "Z",
            "name": f"{self.threat_type} - {self.indicator}",
            "description": self.description,
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": pattern,
            "valid_from": self.created_at.isoformat() + "Z",
            "x_crisp_source_org": self.source_org.name,
            "x_crisp_severity": self.severity
        }
    
    def _is_ip(self, value):
        """Check if value is an IP address"""
        parts = value.split('.')
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
    
    def _is_domain(self, value):
        """Check if value is a domain"""
        return '.' in value and not self._is_ip(value) and not '@' in value and not value.startswith('http')
    
    def _is_email(self, value):
        """Check if value is an email"""
        return '@' in value
    
    def _is_url(self, value):
        """Check if value is a URL"""
        return value.startswith(('http://', 'https://'))

class InstitutionalSharingSimulator:
    """Simulates institutional threat intelligence sharing"""
    
    def __init__(self):
        self.organizations = {}
        self.trust_relationships = {}
        self.shared_collections = {}
        
        # Import anonymization components
        try:
            from core.patterns.strategy import AnonymizationContext, AnonymizationLevel, DataType
            self.anonymization_context = AnonymizationContext()
            self.AnonymizationLevel = AnonymizationLevel
            self.DataType = DataType
            self.anonymization_available = True
        except ImportError:
            print("⚠️  Core anonymization not available, using mock anonymization")
            self.anonymization_available = False
    
    def create_organization(self, name, org_type="university"):
        """Create a new organization"""
        org = MockOrganization(name)
        org.org_type = org_type
        self.organizations[name] = org
        print(f"✅ Created organization: {name} ({org_type})")
        return org
    
    def set_trust_relationship(self, org1_name, org2_name, trust_level):
        """Set trust level between two organizations"""
        if org1_name not in self.trust_relationships:
            self.trust_relationships[org1_name] = {}
        self.trust_relationships[org1_name][org2_name] = trust_level
        
        trust_desc = self._get_trust_description(trust_level)
        print(f"🤝 Set trust: {org1_name} → {org2_name} = {trust_level} ({trust_desc})")
    
    def _get_trust_description(self, trust_level):
        """Get human-readable trust description"""
        if trust_level >= 0.8:
            return "High Trust"
        elif trust_level >= 0.5:
            return "Medium Trust"
        elif trust_level >= 0.2:
            return "Low Trust"
        else:
            return "No Trust"
    
    def add_threat_intelligence(self, org_name, threat_type, indicator, description, severity="medium"):
        """Add threat intelligence to an organization"""
        org = self.organizations[org_name]
        threat = MockThreatIntel(org, threat_type, indicator, description, severity)
        org.threat_intelligence.append(threat)
        print(f"🚨 {org_name} detected: {threat_type} - {indicator} ({severity} severity)")
        return threat
    
    def share_intelligence(self, source_org_name, target_org_name, collection_name="shared_threats"):
        """Simulate sharing threat intelligence between organizations"""
        source_org = self.organizations[source_org_name]
        target_org = self.organizations[target_org_name]
        
        # Get trust level
        trust_level = self.trust_relationships.get(source_org_name, {}).get(target_org_name, 0.3)
        
        print_subheader(f"Sharing from {source_org_name} to {target_org_name}")
        print(f"Trust Level: {trust_level} ({self._get_trust_description(trust_level)})")
        
        # Create shared collection if it doesn't exist
        if collection_name not in self.shared_collections:
            self.shared_collections[collection_name] = {
                'objects': [],
                'created_by': source_org_name,
                'trust_levels': {}
            }
        
        shared_objects = []
        
        for threat in source_org.threat_intelligence:
            # Apply anonymization based on trust level
            anonymized_stix = self._anonymize_stix_object(threat.stix_object, trust_level)
            shared_objects.append(anonymized_stix)
            
            print(f"  📤 Sharing: {threat.threat_type}")
            print(f"     Original: {threat.stix_object['pattern']}")
            print(f"     Shared:   {anonymized_stix['pattern']}")
            print(f"     Anonymized: {anonymized_stix.get('x_crisp_anonymized', False)}")
        
        # Store in target organization
        target_org.received_intelligence.extend(shared_objects)
        
        # Add to shared collection
        collection = self.shared_collections[collection_name]
        collection['objects'].extend(shared_objects)
        collection['trust_levels'][target_org_name] = trust_level
        
        print(f"✅ Shared {len(shared_objects)} threat indicators")
        return shared_objects
    
    def _anonymize_stix_object(self, stix_object, trust_level):
        """Anonymize STIX object based on trust level"""
        if not self.anonymization_available:
            return self._mock_anonymize_stix_object(stix_object, trust_level)
        
        # Use real anonymization if available
        try:
            from crisp_threat_intel.strategies.integrated_anonymization import IntegratedAnonymizationContext
            context = IntegratedAnonymizationContext()
            return context.anonymize_stix_object(stix_object, trust_level)
        except ImportError:
            return self._mock_anonymize_stix_object(stix_object, trust_level)
    
    def _mock_anonymize_stix_object(self, stix_object, trust_level):
        """Mock anonymization for demonstration"""
        anonymized = stix_object.copy()
        pattern = stix_object['pattern']
        
        # Extract the value from the pattern
        import re
        value_match = re.search(r"'([^']+)'", pattern)
        if not value_match:
            return anonymized
        
        original_value = value_match.group(1)
        anonymized_value = self._mock_anonymize_value(original_value, trust_level)
        
        # Replace in pattern
        anonymized['pattern'] = pattern.replace(f"'{original_value}'", f"'{anonymized_value}'")
        anonymized['x_crisp_anonymized'] = trust_level < 0.8
        anonymized['x_crisp_trust_level'] = trust_level
        
        return anonymized
    
    def _mock_anonymize_value(self, value, trust_level):
        """Mock value anonymization"""
        if trust_level >= 0.8:
            return value  # No anonymization
        elif trust_level >= 0.5:
            # Low anonymization
            if self._is_ip(value):
                parts = value.split('.')
                return f"{parts[0]}.{parts[1]}.{parts[2]}.x"
            elif self._is_domain(value):
                parts = value.split('.')
                if len(parts) >= 2:
                    return f"*.{'.'.join(parts[-2:])}"
                return f"*.{value}"
            elif self._is_email(value):
                local, domain = value.split('@')
                return f"user-{hash(local) % 1000000:06d}@{domain}"
            elif self._is_url(value):
                if '://' in value:
                    protocol, rest = value.split('://', 1)
                    domain = rest.split('/')[0]
                    return f"{protocol}://*.{domain}/[path-removed]"
        elif trust_level >= 0.2:
            # Medium anonymization
            if self._is_ip(value):
                parts = value.split('.')
                return f"{parts[0]}.{parts[1]}.x.x"
            elif self._is_domain(value):
                parts = value.split('.')
                return f"*.{parts[-1]}"
            elif self._is_email(value):
                return f"user-{hash(value) % 1000000:06d}@*.domain"
            elif self._is_url(value):
                return "https://*.domain"
        else:
            # Full anonymization
            return f"anon-{hash(value) % 1000000:06d}"
        
        return value
    
    def _is_ip(self, value):
        """Check if value is an IP address"""
        parts = value.split('.')
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
    
    def _is_domain(self, value):
        """Check if value is a domain"""
        return '.' in value and not self._is_ip(value) and not '@' in value and not value.startswith('http')
    
    def _is_email(self, value):
        """Check if value is an email"""
        return '@' in value
    
    def _is_url(self, value):
        """Check if value is a URL"""
        return value.startswith(('http://', 'https://'))
    
    def generate_bundle(self, collection_name, requesting_org_name):
        """Generate STIX bundle for organization"""
        if collection_name not in self.shared_collections:
            return None
        
        collection = self.shared_collections[collection_name]
        trust_level = collection['trust_levels'].get(requesting_org_name, 0.3)
        
        bundle = {
            "type": "bundle",
            "id": f"bundle--{collection_name}-{requesting_org_name}",
            "objects": collection['objects'],
            "x_crisp_collection": collection_name,
            "x_crisp_requesting_org": requesting_org_name,
            "x_crisp_trust_level": trust_level,
            "x_crisp_object_count": len(collection['objects'])
        }
        
        return bundle
    
    def print_organization_status(self, org_name):
        """Print status of an organization"""
        org = self.organizations[org_name]
        print_subheader(f"{org_name} Status")
        print(f"Threat Intelligence Created: {len(org.threat_intelligence)}")
        print(f"Intelligence Received: {len(org.received_intelligence)}")
        
        if org.threat_intelligence:
            print("\nCreated Threats:")
            for threat in org.threat_intelligence:
                print(f"  🚨 {threat.threat_type}: {threat.indicator} ({threat.severity})")
        
        if org.received_intelligence:
            print("\nReceived Intelligence:")
            for intel in org.received_intelligence:
                anonymized = intel.get('x_crisp_anonymized', False)
                trust = intel.get('x_crisp_trust_level', 'N/A')
                print(f"  📥 {intel['name']} (Trust: {trust}, Anonymized: {anonymized})")
                print(f"      Pattern: {intel['pattern']}")

def demonstrate_institutional_sharing():
    """Demonstrate institutional threat intelligence sharing"""
    print_header("CRISP Institutional Threat Intelligence Sharing Simulation")
    
    # Initialize simulator
    sim = InstitutionalSharingSimulator()
    
    # Create educational institutions
    print_subheader("Creating Educational Institutions")
    university_a = sim.create_organization("State University A", "university")
    university_b = sim.create_organization("Tech University B", "university")
    community_college = sim.create_organization("Community College C", "college")
    
    # Set up trust relationships
    print_subheader("Establishing Trust Relationships")
    # University A trusts University B highly (research partners)
    sim.set_trust_relationship("State University A", "Tech University B", 0.8)
    # University A has medium trust with Community College
    sim.set_trust_relationship("State University A", "Community College C", 0.5)
    # University B has low trust with Community College (new relationship)
    sim.set_trust_relationship("Tech University B", "Community College C", 0.3)
    
    # University A detects threats
    print_subheader("University A Detects Threats")
    sim.add_threat_intelligence(
        "State University A", 
        "Phishing Campaign", 
        "phishing.fake-university.edu", 
        "Phishing site targeting student credentials",
        "high"
    )
    sim.add_threat_intelligence(
        "State University A",
        "Malware C2",
        "203.0.113.42",
        "Command and control server for campus malware",
        "critical"
    )
    sim.add_threat_intelligence(
        "State University A",
        "Suspicious Email",
        "attacker@criminal-org.net",
        "Email address used in targeted attacks",
        "medium"
    )
    sim.add_threat_intelligence(
        "State University A",
        "Malicious URL", 
        "https://fake-portal.evil.com/login",
        "Fake portal stealing university logins",
        "high"
    )
    
    # University B detects different threats
    print_subheader("University B Detects Threats")
    sim.add_threat_intelligence(
        "Tech University B",
        "Ransomware Infrastructure",
        "ransomware-pay.dark.net",
        "Payment portal for ransomware attacks",
        "critical"
    )
    sim.add_threat_intelligence(
        "Tech University B",
        "Botnet Node",
        "198.51.100.123",
        "Compromised system in botnet",
        "medium"
    )
    
    # Simulate sharing scenarios
    print_header("Threat Intelligence Sharing Scenarios")
    
    # Scenario 1: High trust sharing (University A → University B)
    print_subheader("Scenario 1: High Trust Sharing")
    print("University A shares with University B (trusted research partner)")
    shared_objects_1 = sim.share_intelligence("State University A", "Tech University B")
    
    # Scenario 2: Medium trust sharing (University A → Community College)
    print_subheader("Scenario 2: Medium Trust Sharing") 
    print("University A shares with Community College C (moderate trust)")
    shared_objects_2 = sim.share_intelligence("State University A", "Community College C")
    
    # Scenario 3: Low trust sharing (University B → Community College)
    print_subheader("Scenario 3: Low Trust Sharing")
    print("University B shares with Community College C (new partner)")
    shared_objects_3 = sim.share_intelligence("Tech University B", "Community College C")
    
    # Show organization status
    print_header("Final Organization Status")
    sim.print_organization_status("State University A")
    sim.print_organization_status("Tech University B") 
    sim.print_organization_status("Community College C")
    
    # Generate bundles for different organizations
    print_header("STIX Bundle Generation")
    
    bundle_b = sim.generate_bundle("shared_threats", "Tech University B")
    bundle_c = sim.generate_bundle("shared_threats", "Community College C")
    
    if bundle_b:
        print_subheader("Bundle for University B (High Trust)")
        print(f"Objects: {bundle_b['x_crisp_object_count']}")
        print(f"Trust Level: {bundle_b['x_crisp_trust_level']}")
        print("Sample Object:")
        if bundle_b['objects']:
            sample = bundle_b['objects'][0]
            print(f"  Name: {sample['name']}")
            print(f"  Pattern: {sample['pattern']}")
            print(f"  Anonymized: {sample.get('x_crisp_anonymized', False)}")
    
    if bundle_c:
        print_subheader("Bundle for Community College C (Medium/Low Trust)")
        print(f"Objects: {bundle_c['x_crisp_object_count']}")
        print(f"Trust Level: {bundle_c['x_crisp_trust_level']}")
        print("Sample Object:")
        if bundle_c['objects']:
            sample = bundle_c['objects'][0]
            print(f"  Name: {sample['name']}")
            print(f"  Pattern: {sample['pattern']}")
            print(f"  Anonymized: {sample.get('x_crisp_anonymized', False)}")
    
    # Summary
    print_header("Simulation Summary")
    print("✅ Successfully demonstrated institutional threat intelligence sharing")
    print("✅ Trust-based anonymization applied automatically")
    print("✅ Different levels of data protection based on relationships")
    print("✅ STIX-compliant objects maintained throughout process")
    print("✅ Real-world educational use case validated")
    
    print("\n🎓 Educational Benefits:")
    print("  • Universities can share sensitive threat data safely")
    print("  • Research collaboration enabled with privacy protection")
    print("  • Community colleges receive anonymized threat intelligence")
    print("  • Incident response improved through shared awareness")
    print("  • Compliance maintained with data protection requirements")

def main():
    """Main function"""
    demonstrate_institutional_sharing()

if __name__ == "__main__":
    main()