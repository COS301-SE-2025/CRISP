#!/usr/bin/env python3
"""
File Structure Validation Script for CRISP User Management
Checks that all required files exist and are properly structured
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description=""):
    """Check if file exists and return status"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {file_path} ({size} bytes) {description}")
        return True
    else:
        print(f"❌ {file_path} - MISSING {description}")
        return False

def validate_python_syntax(file_path):
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r') as f:
            compile(f.read(), file_path, 'exec')
        return True
    except SyntaxError as e:
        print(f"  ⚠️  Syntax Error in {file_path}: {e}")
        return False
    except Exception:
        return True  # File might not be Python

def main():
    print("🛡️ CRISP User Management - File Structure Validation")
    print("=" * 60)
    
    base_path = Path(".")
    files_checked = 0
    files_missing = 0
    syntax_errors = 0
    
    # Core Django files
    core_files = [
        ("manage.py", "Django management script"),
        ("test_settings.py", "Django test settings"),
        ("test_urls.py", "URL configuration"),
        (".env", "Environment variables (optional)"),
    ]
    
    print("\n📁 Core Django Files:")
    for file_path, desc in core_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif file_path.endswith('.py'):
            if not validate_python_syntax(file_path):
                syntax_errors += 1
    
    # UserManagement app files
    app_files = [
        ("UserManagement/__init__.py", "App initialization"),
        ("UserManagement/admin.py", "Django admin configuration"),
        ("UserManagement/apps.py", "App configuration"),
        ("UserManagement/models.py", "Data models"),
        ("UserManagement/serializers.py", "API serializers"),
        ("UserManagement/urls.py", "URL routing"),
        ("UserManagement/utils.py", "Utility functions"),
        ("UserManagement/validators.py", "Custom validators"),
        ("UserManagement/permissions.py", "Custom permissions"),
        ("UserManagement/middleware.py", "Custom middleware"),
        ("UserManagement/signals.py", "Django signals"),
        ("UserManagement/settings.py", "App-specific settings"),
    ]
    
    print("\n📦 UserManagement App Files:")
    for file_path, desc in app_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Services
    service_files = [
        ("UserManagement/services/__init__.py", "Services package"),
        ("UserManagement/services/auth_service.py", "Authentication service"),
    ]
    
    print("\n🔧 Service Files:")
    for file_path, desc in service_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Factories
    factory_files = [
        ("UserManagement/factories/__init__.py", "Factories package"),
        ("UserManagement/factories/user_factory.py", "User factory"),
    ]
    
    print("\n🏭 Factory Files:")
    for file_path, desc in factory_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Strategies
    strategy_files = [
        ("UserManagement/strategies/__init__.py", "Strategies package"),
        ("UserManagement/strategies/authentication_strategies.py", "Auth strategies"),
    ]
    
    print("\n🎯 Strategy Files:")
    for file_path, desc in strategy_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Observers
    observer_files = [
        ("UserManagement/observers/__init__.py", "Observers package"),
        ("UserManagement/observers/auth_observers.py", "Auth observers"),
    ]
    
    print("\n👁️ Observer Files:")
    for file_path, desc in observer_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Views
    view_files = [
        ("UserManagement/views/__init__.py", "Views package"),
        ("UserManagement/views/auth_views.py", "Authentication views"),
        ("UserManagement/views/user_views.py", "User management views"),
        ("UserManagement/views/admin_views.py", "Admin views"),
    ]
    
    print("\n🌐 View Files:")
    for file_path, desc in view_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Tests
    test_files = [
        ("UserManagement/tests/__init__.py", "Tests package"),
        ("UserManagement/tests/test_authentication.py", "Authentication tests"),
        ("UserManagement/tests/test_user_management.py", "User management tests"),
        ("UserManagement/tests/test_security.py", "Security tests"),
        ("UserManagement/tests/test_integration.py", "Integration tests"),
    ]
    
    print("\n🧪 Test Files:")
    for file_path, desc in test_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Management Commands
    mgmt_files = [
        ("UserManagement/management/__init__.py", "Management package"),
        ("UserManagement/management/commands/__init__.py", "Commands package"),
        ("UserManagement/management/commands/setup_auth.py", "Setup command"),
    ]
    
    print("\n⚙️ Management Command Files:")
    for file_path, desc in mgmt_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
        elif not validate_python_syntax(file_path):
            syntax_errors += 1
    
    # Migrations
    migration_dir = "UserManagement/migrations"
    print(f"\n🗃️ Migration Files:")
    if os.path.exists(migration_dir):
        migration_files = [f for f in os.listdir(migration_dir) if f.endswith('.py')]
        print(f"✅ {migration_dir}/ ({len(migration_files)} migration files)")
        for migration in sorted(migration_files):
            print(f"  📄 {migration}")
    else:
        print(f"❌ {migration_dir}/ - MISSING")
        files_missing += 1
    
    # Documentation and Test Files
    doc_files = [
        ("README.md", "Main documentation"),
        ("QUICK_START.md", "Quick start guide"),
        ("COMPREHENSIVE_TESTING_GUIDE.md", "Testing guide"),
        ("test_system.py", "System test script"),
        ("test_login.py", "Login test script"),
        ("run_all_tests.sh", "Test runner script"),
    ]
    
    print("\n📚 Documentation & Test Scripts:")
    for file_path, desc in doc_files:
        files_checked += 1
        if not check_file_exists(file_path, desc):
            files_missing += 1
    
    # Database files
    db_files = [
        ("test_db.sqlite3", "SQLite database (created after migration)"),
    ]
    
    print("\n🗄️ Database Files:")
    for file_path, desc in db_files:
        if os.path.exists(file_path):
            check_file_exists(file_path, desc)
        else:
            print(f"ℹ️  {file_path} - Not yet created (run migrations)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 File Validation Summary:")
    print(f"✅ Files Checked: {files_checked}")
    print(f"❌ Files Missing: {files_missing}")
    print(f"⚠️  Syntax Errors: {syntax_errors}")
    
    success_rate = ((files_checked - files_missing - syntax_errors) / files_checked) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if files_missing == 0 and syntax_errors == 0:
        print("\n🎉 All files present and valid!")
        return 0
    else:
        print(f"\n⚠️  Issues found: {files_missing} missing files, {syntax_errors} syntax errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())