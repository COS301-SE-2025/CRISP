
from .enums import AnonymizationLevel, DataType
from .context import AnonymizationContext


def demonstrate_anonymization():
    """Demonstrate the anonymization system"""
    print("=== CRISP Anonymization System Demo ===\n")
    
    # Create anonymization context
    context = AnonymizationContext()
    
    # Test data
    test_data = [
        ("192.168.1.100", DataType.IP_ADDRESS),
        ("2001:db8::1", DataType.IP_ADDRESS),
        ("malicious.example.com", DataType.DOMAIN),
        ("admin@company.edu", DataType.EMAIL),
        ("https://evil.example.org/malware.exe", DataType.URL),
    ]
    
    levels = [AnonymizationLevel.LOW, AnonymizationLevel.MEDIUM, 
              AnonymizationLevel.HIGH, AnonymizationLevel.FULL]
    
    for data, data_type in test_data:
        print(f"Original: {data} ({data_type.value})")
        for level in levels:
            anonymized = context.execute_anonymization(data, data_type, level)
            print(f"  {level.value.upper():6}: {anonymized}")
        print()
    
    # Test auto-detection
    print("=== Auto-Detection Demo ===")
    auto_test_data = [
        "10.0.0.1",
        "badguy@evil.com", 
        "suspicious.domain.net",
        "http://malware-site.com/payload"
    ]
    
    for data in auto_test_data:
        print(f"Auto-detecting: {data}")
        for level in [AnonymizationLevel.LOW, AnonymizationLevel.HIGH]:
            anonymized = context.auto_detect_and_anonymize(data, level)
            print(f"  {level.value.upper():4}: {anonymized}")
        print()


def test_bulk_anonymization():
    """Test bulk anonymization functionality"""
    print("=== Bulk Anonymization Demo ===\n")
    
    context = AnonymizationContext()
    
    # Bulk test data
    bulk_data = [
        ("192.168.1.1", DataType.IP_ADDRESS),
        ("192.168.1.2", DataType.IP_ADDRESS),
        ("evil1.com", DataType.DOMAIN),
        ("evil2.com", DataType.DOMAIN),
        ("attacker@malicious.org", DataType.EMAIL),
    ]
    
    print("Original data:")
    for data, data_type in bulk_data:
        print(f"  {data} ({data_type.value})")
    
    print(f"\nBulk anonymization at MEDIUM level:")
    results = context.bulk_anonymize(bulk_data, AnonymizationLevel.MEDIUM)
    for i, result in enumerate(results):
        print(f"  {bulk_data[i][0]} -> {result}")


if __name__ == "__main__":
    demonstrate_anonymization()
    print("\n" + "="*50 + "\n")
    test_bulk_anonymization()
