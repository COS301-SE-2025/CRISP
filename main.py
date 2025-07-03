"""
Main application for CRISP Anonymization System
Demonstrates practical usage scenarios for threat intelligence sharing
"""

import sys
import json
import argparse
from typing import List, Dict, Any
from datetime import datetime

from core.patterns.strategy.context import AnonymizationContext
from core.patterns.strategy.enums import AnonymizationLevel, DataType


class ThreatIntelligenceProcessor:
    """
    Simulates a threat intelligence processor that anonymizes data
    based on trust relationships between institutions
    """
    
    def __init__(self):
        self.anonymization_context = AnonymizationContext()
        self.trust_levels = {
            "high": AnonymizationLevel.LOW,
            "medium": AnonymizationLevel.MEDIUM,
            "low": AnonymizationLevel.HIGH,
            "untrusted": AnonymizationLevel.FULL
        }
    
    def process_threat_feed(self, threat_data: List[Dict], recipient_trust: str) -> List[Dict]:
        """
        Process a threat feed and anonymize data based on recipient trust level
        
        Args:
            threat_data: List of threat indicators
            recipient_trust: Trust level ("high", "medium", "low", "untrusted")
            
        Returns:
            Processed threat feed with appropriate anonymization
        """
        anonymization_level = self.trust_levels.get(recipient_trust, AnonymizationLevel.FULL)
        processed_feed = []
        
        for threat in threat_data:
            processed_threat = threat.copy()
            
            # Anonymize indicators based on their types
            if 'ip_address' in threat:
                processed_threat['ip_address'] = self.anonymization_context.execute_anonymization(
                    threat['ip_address'], DataType.IP_ADDRESS, anonymization_level
                )
            
            if 'domain' in threat:
                processed_threat['domain'] = self.anonymization_context.execute_anonymization(
                    threat['domain'], DataType.DOMAIN, anonymization_level
                )
            
            if 'email' in threat:
                processed_threat['email'] = self.anonymization_context.execute_anonymization(
                    threat['email'], DataType.EMAIL, anonymization_level
                )
            
            if 'url' in threat:
                processed_threat['url'] = self.anonymization_context.execute_anonymization(
                    threat['url'], DataType.URL, anonymization_level
                )
            
            # Add metadata about anonymization
            processed_threat['anonymization_level'] = anonymization_level.value
            processed_threat['processed_at'] = datetime.now().isoformat()
            
            processed_feed.append(processed_threat)
        
        return processed_feed
    
    def process_stix_feed(self, stix_data: Dict, recipient_trust: str) -> Dict:
        """
        Process a STIX feed and anonymize based on recipient trust level
        
        Args:
            stix_data: STIX bundle or object
            recipient_trust: Trust level ("high", "medium", "low", "untrusted")
            
        Returns:
            Processed STIX data with appropriate anonymization
        """
        anonymization_level = self.trust_levels.get(recipient_trust, AnonymizationLevel.FULL)
        
        # Detect STIX version
        stix_version = self.anonymization_context._detect_stix_version(stix_data)
        print(f"Detected STIX version: {stix_version}")
        
        # Process the STIX data
        processed_stix = self.anonymization_context.anonymize_stix_object(
            stix_data,
            anonymization_level
        )
        
        return json.loads(processed_stix)
    
    def auto_process_mixed_indicators(self, indicators: List[str], trust_level: str) -> Dict[str, Any]:
        """
        Auto-detect and process mixed indicators
        
        Args:
            indicators: List of mixed threat indicators
            trust_level: Trust level for anonymization
            
        Returns:
            Dictionary with processed indicators and metadata
        """
        anonymization_level = self.trust_levels.get(trust_level, AnonymizationLevel.FULL)
        results = {
            'processed_indicators': [],
            'anonymization_level': anonymization_level.value,
            'trust_level': trust_level,
            'processed_at': datetime.now().isoformat(),
            'total_count': len(indicators)
        }
        
        for indicator in indicators:
            try:
                anonymized = self.anonymization_context.auto_detect_and_anonymize(
                    indicator, anonymization_level
                )
                results['processed_indicators'].append({
                    'original': indicator,
                    'anonymized': anonymized,
                    'detected_type': self.anonymization_context._detect_data_type(indicator).value
                })
            except Exception as e:
                results['processed_indicators'].append({
                    'original': indicator,
                    'anonymized': f"[ERROR: {str(e)}]",
                    'detected_type': 'unknown'
                })
        
        return results


def demonstrate_basic_usage():
    """Demonstrate basic anonymization functionality"""
    print("=== CRISP Anonymization System - Basic Usage ===\n")
    
    context = AnonymizationContext()
    
    # Sample threat indicators
    indicators = [
        ("192.168.100.50", DataType.IP_ADDRESS),
        ("malicious-c2.evil-corp.net", DataType.DOMAIN),
        ("phishing@fake-bank.com", DataType.EMAIL),
        ("https://exploit-kit.badsite.org/payload.exe", DataType.URL),
    ]
    
    print("Original Indicators:")
    for indicator, data_type in indicators:
        print(f"  {indicator} ({data_type.value})")
    
    print("\nAnonymization at different levels:")
    
    for level in [AnonymizationLevel.LOW, AnonymizationLevel.MEDIUM, 
                  AnonymizationLevel.HIGH, AnonymizationLevel.FULL]:
        print(f"\n--- {level.value.upper()} Level Anonymization ---")
        for indicator, data_type in indicators:
            anonymized = context.execute_anonymization(indicator, data_type, level)
            print(f"  {indicator} → {anonymized}")


def demonstrate_threat_intelligence_sharing():
    """Demonstrate threat intelligence sharing with different trust levels"""
    print("\n\n=== Threat Intelligence Sharing Scenario ===\n")
    
    processor = ThreatIntelligenceProcessor()
    
    # Sample threat intelligence feed
    threat_feed = [
        {
            "threat_id": "TI-001",
            "type": "malware_c2",
            "ip_address": "203.0.113.42",
            "domain": "malware-c2.evil-corp.net",
            "severity": "high",
            "confidence": 0.95,
            "first_seen": "2024-01-15T10:30:00Z"
        },
        {
            "threat_id": "TI-002", 
            "type": "phishing",
            "email": "ceo@fake-company.com",
            "url": "https://phishing-site.badactor.org/login",
            "severity": "medium",
            "confidence": 0.87,
            "first_seen": "2024-01-16T14:22:00Z"
        },
        {
            "threat_id": "TI-003",
            "type": "botnet",
            "ip_address": "198.51.100.123",
            "domain": "botnet-controller.criminal.net",
            "severity": "critical",
            "confidence": 0.98,
            "first_seen": "2024-01-17T09:15:00Z"
        }
    ]
    
    print("Original Threat Feed:")
    for threat in threat_feed:
        print(f"  ID: {threat['threat_id']}")
        if 'ip_address' in threat:
            print(f"    IP: {threat['ip_address']}")
        if 'domain' in threat:
            print(f"    Domain: {threat['domain']}")
        if 'email' in threat:
            print(f"    Email: {threat['email']}")
        if 'url' in threat:
            print(f"    URL: {threat['url']}")
        print(f"    Severity: {threat['severity']}")
        print()
    
    # Process for different trust levels
    trust_levels = ["high", "medium", "low", "untrusted"]
    
    for trust in trust_levels:
        print(f"--- Sharing with {trust.upper()} trust institution ---")
        processed_feed = processor.process_threat_feed(threat_feed, trust)
        
        for threat in processed_feed:
            print(f"  ID: {threat['threat_id']}")
            if 'ip_address' in threat:
                print(f"    IP: {threat['ip_address']}")
            if 'domain' in threat:
                print(f"    Domain: {threat['domain']}")
            if 'email' in threat:
                print(f"    Email: {threat['email']}")
            if 'url' in threat:
                print(f"    URL: {threat['url']}")
            print(f"    Anonymization: {threat['anonymization_level']}")
            print()


def demonstrate_stix_sharing():
    """Demonstrate STIX data sharing"""
    print("\n\n=== STIX Intelligence Sharing Demo ===\n")
    
    processor = ThreatIntelligenceProcessor()
    
    # Sample STIX Indicator
    stix_indicator = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": "indicator--d81f86b8-975b-4c0b-875e-810c5ad40ac2",
        "created": "2021-03-01T15:30:00.000Z",
        "modified": "2021-03-01T15:30:00.000Z",
        "name": "Malicious IP Address",
        "description": "This IP address 192.168.1.100 was observed in malicious activity",
        "indicator_types": ["malicious-activity"],
        "pattern_type": "stix",
        "pattern": "[ipv4-addr:value = '192.168.1.100']",
        "valid_from": "2021-03-01T15:30:00.000Z",
    }
    
    print("Original STIX Indicator:")
    print(json.dumps(stix_indicator, indent=2))
    
    # Process STIX data for different trust levels
    trust_levels = ["high", "medium", "low"]
    
    for trust in trust_levels:
        print(f"\n--- Sharing with {trust.upper()} trust institution ---")
        processed_stix = processor.process_stix_feed(stix_indicator, trust)
        print(json.dumps(processed_stix, indent=2))


def demonstrate_auto_detection():
    """Demonstrate automatic data type detection"""
    print("\n\n=== Auto-Detection Demonstration ===\n")
    
    processor = ThreatIntelligenceProcessor()
    
    # Mixed indicators without explicit type information
    mixed_indicators = [
        "10.0.0.1",
        "2001:db8::1", 
        "suspicious.domain.com",
        "attacker@criminal.org",
        "https://malware-drop.badsite.net/trojan.exe",
        "ftp://files.evil-corp.net/data",
        "mail-server.phishing-campaign.org"
    ]
    
    print("Auto-detecting and processing mixed indicators:")
    print("Original indicators:", mixed_indicators)
    print()
    
    # Process with different trust levels
    for trust in ["high", "low"]:
        print(f"--- Processing with {trust.upper()} trust level ---")
        results = processor.auto_process_mixed_indicators(mixed_indicators, trust)
        
        for item in results['processed_indicators']:
            print(f"  {item['original']}")
            print(f"    Detected as: {item['detected_type']}")
            print(f"    Anonymized:  {item['anonymized']}")
            print()
        
        print(f"Summary: {results['total_count']} indicators processed")
        print(f"Trust level: {results['trust_level']}")
        print(f"Anonymization level: {results['anonymization_level']}")
        print()


def interactive_mode():
    """Interactive mode for testing anonymization"""
    print("\n\n=== Interactive Anonymization Mode ===")
    print("Enter threat indicators to see them anonymized.")
    print("Format: <indicator> [trust_level]")
    print("Trust levels: high, medium, low, untrusted (default: medium)")
    print("Type 'quit' to exit.")
    print()
    
    processor = ThreatIntelligenceProcessor()
    
    while True:
        try:
            user_input = input("Enter indicator: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            # Parse input
            parts = user_input.split()
            indicator = parts[0]
            trust_level = parts[1] if len(parts) > 1 else "medium"
            
            if trust_level not in ["high", "medium", "low", "untrusted"]:
                print(f"Invalid trust level: {trust_level}. Using 'medium'.")
                trust_level = "medium"
            
            # Process the indicator
            results = processor.auto_process_mixed_indicators([indicator], trust_level)
            
            if results['processed_indicators']:
                item = results['processed_indicators'][0]
                print(f"  Original:    {item['original']}")
                print(f"  Detected:    {item['detected_type']}")
                print(f"  Anonymized:  {item['anonymized']}")
                print(f"  Trust level: {trust_level}")
                print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("Goodbye!")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='CRISP Anonymization System')
    parser.add_argument('--mode', choices=['demo', 'interactive', 'test', 'stix'], 
                        default='demo', help='Operation mode')
    parser.add_argument('--file', help='Input file for STIX anonymization')
    parser.add_argument('--trust', choices=['high', 'medium', 'low', 'untrusted'],
                        default='medium', help='Trust level for anonymization')
    parser.add_argument('--output', help='Output file for anonymized data')
    
    return parser.parse_args()


def main():
    """Main application entry point"""
    print("CRISP Anonymization System")
    print("=" * 50)
    
    args = parse_arguments()
    
    if args.mode == "demo":
        demonstrate_basic_usage()
        demonstrate_threat_intelligence_sharing() 
        demonstrate_auto_detection()
        demonstrate_stix_sharing()
    elif args.mode == "interactive":
        interactive_mode()
    elif args.mode == "test":
        # Run a quick test
        context = AnonymizationContext()
        result = context.auto_detect_and_anonymize("192.168.1.1", AnonymizationLevel.MEDIUM)
        print(f"Quick test: 192.168.1.1 → {result}")
    elif args.mode == "stix":
        # Process STIX data
        if not args.file:
            print("Error: --file parameter is required for STIX mode")
            return
        
        try:
            with open(args.file, 'r') as f:
                stix_data = json.load(f)
            
            processor = ThreatIntelligenceProcessor()
            anonymized = processor.process_stix_feed(stix_data, args.trust)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(anonymized, f, indent=2)
                print(f"Anonymized STIX data written to {args.output}")
            else:
                print(json.dumps(anonymized, indent=2))
        except Exception as e:
            print(f"Error processing STIX data: {e}")
    else:
        print(f"Unknown mode: {args.mode}")
        print("Available modes: demo, interactive, test, stix")


if __name__ == "__main__":
    main()