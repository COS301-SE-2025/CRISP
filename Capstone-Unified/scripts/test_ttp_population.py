#!/usr/bin/env python3
"""
Test script to validate TTP data population
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_unified.settings')
django.setup()

from django.db.models import Count
from core.models.models import TTPData, ThreatFeed


def test_ttp_data_structure():
    """Test that TTP data has the expected structure"""
    print("🧪 Testing TTP Data Structure...")
    
    # Get a sample TTP
    sample_ttp = TTPData.objects.first()
    if not sample_ttp:
        print("❌ No TTP data found. Run population script first.")
        return False
    
    # Test required fields
    required_fields = [
        'name', 'description', 'mitre_technique_id', 'mitre_tactic',
        'threat_feed', 'stix_id', 'created_at', 'updated_at'
    ]
    
    for field in required_fields:
        value = getattr(sample_ttp, field)
        if value is None or (isinstance(value, str) and not value.strip()):
            print(f"❌ Missing or empty field: {field}")
            return False
        print(f"✅ {field}: {str(value)[:50]}...")
    
    # Test MITRE technique ID format
    if not sample_ttp.mitre_technique_id.startswith('T'):
        print(f"❌ Invalid MITRE technique ID format: {sample_ttp.mitre_technique_id}")
        return False
    print(f"✅ MITRE technique ID format: {sample_ttp.mitre_technique_id}")
    
    # Test original_data JSON structure
    if sample_ttp.original_data:
        expected_keys = ['source', 'confidence', 'severity', 'tlp', 'tags']
        for key in expected_keys:
            if key in sample_ttp.original_data:
                print(f"✅ original_data.{key}: {sample_ttp.original_data[key]}")
            else:
                print(f"⚠️  Missing original_data.{key}")
    
    print("✅ TTP data structure test passed")
    return True


def test_data_distribution():
    """Test that data has realistic distribution"""
    print("\n📊 Testing Data Distribution...")
    
    total_ttps = TTPData.objects.count()
    if total_ttps == 0:
        print("❌ No TTP data found")
        return False
    
    print(f"✅ Total TTPs: {total_ttps}")
    
    # Test tactic distribution
    tactics = TTPData.objects.values('mitre_tactic').annotate(
        count=Count('id')
    ).order_by('-count')
    
    if len(tactics) < 5:
        print("⚠️  Low tactic diversity - consider running with more data")
    else:
        print(f"✅ Tactic diversity: {len(tactics)} different tactics")
    
    # Test feed distribution
    feeds = TTPData.objects.values('threat_feed__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    if len(feeds) < 3:
        print("⚠️  Low feed diversity")
    else:
        print(f"✅ Feed diversity: {len(feeds)} different feeds")
    
    # Test anonymization
    anonymized_count = TTPData.objects.filter(is_anonymized=True).count()
    anonymized_percent = (anonymized_count / total_ttps) * 100
    print(f"✅ Anonymized records: {anonymized_count} ({anonymized_percent:.1f}%)")
    
    print("✅ Data distribution test passed")
    return True


def test_mitre_coverage():
    """Test MITRE ATT&CK framework coverage"""
    print("\n🎯 Testing MITRE ATT&CK Coverage...")
    
    # Expected MITRE tactics
    expected_tactics = [
        'reconnaissance', 'resource_development', 'initial_access', 'execution',
        'persistence', 'privilege_escalation', 'defense_evasion', 'credential_access',
        'discovery', 'lateral_movement', 'collection', 'command_and_control',
        'exfiltration', 'impact'
    ]
    
    actual_tactics = set(TTPData.objects.values_list('mitre_tactic', flat=True).distinct())
    
    coverage = len(actual_tactics.intersection(expected_tactics))
    total_expected = len(expected_tactics)
    coverage_percent = (coverage / total_expected) * 100
    
    print(f"✅ Tactic coverage: {coverage}/{total_expected} ({coverage_percent:.1f}%)")
    
    # Show covered tactics
    covered_tactics = actual_tactics.intersection(expected_tactics)
    for tactic in sorted(covered_tactics):
        count = TTPData.objects.filter(mitre_tactic=tactic).count()
        print(f"  - {tactic.replace('_', ' ').title()}: {count} TTPs")
    
    # Show missing tactics
    missing_tactics = set(expected_tactics) - actual_tactics
    if missing_tactics:
        print("⚠️  Missing tactics:")
        for tactic in sorted(missing_tactics):
            print(f"  - {tactic.replace('_', ' ').title()}")
    
    print("✅ MITRE coverage test passed")
    return True


def test_temporal_distribution():
    """Test that data is distributed over time"""
    print("\n📅 Testing Temporal Distribution...")
    
    from django.db.models import Min, Max
    date_range = TTPData.objects.aggregate(
        earliest=Min('created_at'),
        latest=Max('created_at')
    )
    
    if not date_range['earliest'] or not date_range['latest']:
        print("❌ No temporal data found")
        return False
    
    duration = date_range['latest'] - date_range['earliest']
    print(f"✅ Time range: {duration.days} days")
    print(f"✅ Earliest: {date_range['earliest'].strftime('%Y-%m-%d %H:%M')}")
    print(f"✅ Latest: {date_range['latest'].strftime('%Y-%m-%d %H:%M')}")
    
    # Test that data is not all created at the same time
    unique_dates = TTPData.objects.dates('created_at', 'day').count()
    print(f"✅ Spread across {unique_dates} different days")
    
    print("✅ Temporal distribution test passed")
    return True


def run_all_tests():
    """Run all validation tests"""
    print("🚀 Starting TTP Data Validation Tests")
    print("=" * 50)
    
    tests = [
        test_ttp_data_structure,
        test_data_distribution,
        test_mitre_coverage,
        test_temporal_distribution
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📈 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! TTP data is ready for analysis.")
        return True
    else:
        print("⚠️  Some tests failed. Consider reviewing the data or running population again.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)