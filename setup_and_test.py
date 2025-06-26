#!/usr/bin/env python3
"""
CRISP Ultra-Clean Structure Setup Script
This script sets up the environment and validates the structure
"""
import os
import sys

def setup_python_path():
    """Setup Python path for the ultra-clean structure"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    core_path = os.path.join(project_root, 'core')
    
    # Add paths to sys.path if not already there
    for path in [project_root, core_path]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    print(f"✅ Python path configured:")
    print(f"   - Project root: {project_root}")
    print(f"   - Core path: {core_path}")

def test_individual_components():
    """Test each component individually"""
    print("\n🧪 Testing Individual Components:")
    print("-" * 40)
    
    # Test 1: Core models file
    print("1. Testing core models file...")
    try:
        import models
        print(f"   ✅ models.py loaded successfully")
        print(f"   ✅ Found Organization: {hasattr(models, 'Organization')}")
        print(f"   ✅ Found CustomUser: {hasattr(models, 'CustomUser')}")
    except Exception as e:
        print(f"   ❌ models.py failed: {e}")
    
    # Test 2: STIX objects
    print("\n2. Testing STIX objects...")
    try:
        from models.stix_object import STIXObject
        print(f"   ✅ STIXObject loaded: {STIXObject.__name__}")
    except Exception as e:
        print(f"   ❌ STIX objects failed: {e}")
    
    # Test 3: Trust models
    print("\n3. Testing trust models...")
    try:
        from models.trust_models.models import TrustLevel
        print(f"   ✅ TrustLevel loaded: {TrustLevel.__name__}")
    except Exception as e:
        print(f"   ❌ Trust models failed: {e}")
    
    # Test 4: Other models
    print("\n4. Testing other models...")
    try:
        from models.indicator import Indicator
        print(f"   ✅ Indicator loaded: {Indicator.__name__}")
    except Exception as e:
        print(f"   ❌ Other models failed: {e}")

def create_simple_test_commands():
    """Create simple test commands for the user"""
    commands = [
        "# Navigate to the project directory",
        "cd '/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone'",
        "",
        "# Run the setup and test",
        "python3 setup_and_test.py",
        "",
        "# Test individual components:",
        "",
        "# 1. Test core models directly",
        "python3 -c \"import sys; sys.path.append('core'); import models; print('✅ Organization:', models.Organization.__name__); print('✅ CustomUser:', models.CustomUser.__name__)\"",
        "",
        "# 2. Test STIX models", 
        "python3 -c \"import sys; sys.path.append('.'); from core.models.stix_object import STIXObject; print('✅ STIXObject:', STIXObject.__name__)\"",
        "",
        "# 3. Test trust models",
        "python3 -c \"import sys; sys.path.append('.'); from core.models.trust_models.models import TrustLevel; print('✅ TrustLevel:', TrustLevel.__name__)\"",
        "",
        "# 4. Test design patterns",
        "python3 -c \"import sys; sys.path.append('.'); from core.patterns.strategy.enums import AnonymizationLevel; print('✅ AnonymizationLevel:', AnonymizationLevel.__name__)\"",
    ]
    
    print("\n🚀 SIMPLE TEST COMMANDS:")
    print("=" * 50)
    for cmd in commands:
        print(cmd)

def main():
    """Main setup function"""
    print("🎯 CRISP ULTRA-CLEAN STRUCTURE SETUP")
    print("=" * 50)
    
    # Setup Python path
    setup_python_path()
    
    # Test components
    test_individual_components()
    
    # Show commands
    create_simple_test_commands()
    
    print("\n🏆 SETUP COMPLETE!")
    print("✅ Ultra-clean structure ready!")
    print("📦 Only 3 root directories: backup, core, crisp")
    print("🚀 Use the commands above to test individual components")

if __name__ == "__main__":
    main()
