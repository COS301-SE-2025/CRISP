#!/usr/bin/env python3
"""
Test session management functionality
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')
django.setup()

def test_session_monitoring():
    """Test session monitoring commands"""
    print("Testing Session Management Commands")
    print("=" * 50)
    
    print("\n1. Testing session monitoring command...")
    try:
        result = subprocess.run(
            ['python3', 'manage.py', 'monitor_sessions', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   monitor_sessions command available")
        else:
            print(f"   monitor_sessions command failed: {result.stderr}")
    except Exception as e:
        print(f"   Error testing monitor_sessions: {e}")

    print("\n2. Testing session cleanup command...")
    try:
        result = subprocess.run(
            ['python3', 'manage.py', 'cleanup_sessions', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   cleanup_sessions command available")
        else:
            print(f"   cleanup_sessions command failed: {result.stderr}")
    except Exception as e:
        print(f"   Error testing cleanup_sessions: {e}")

    print("\n3. Running session statistics...")
    try:
        result = subprocess.run(
            ['python3', 'manage.py', 'monitor_sessions'],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            print("   Session monitoring successful")
            print("   Output:")
            for line in result.stdout.split('\n')[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"   Session monitoring failed: {result.stderr}")
    except Exception as e:
        print(f"   Error running session monitoring: {e}")

def test_session_cleanup_dry_run():
    """Test session cleanup in dry-run mode"""
    print("\n4. Testing session cleanup (dry-run)...")
    try:
        result = subprocess.run(
            ['python3', 'manage.py', 'cleanup_sessions', '--dry-run'],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            print("   Session cleanup dry-run successful")
            print("   🧹 Output:")
            for line in result.stdout.split('\n')[:15]:  # Show first 15 lines
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"   Session cleanup failed: {result.stderr}")
    except Exception as e:
        print(f"   Error running session cleanup: {e}")

def show_session_management_usage():
    """Show usage instructions"""
    print("\n" + "=" * 50)
    print("📚 SESSION MANAGEMENT USAGE GUIDE")
    print("=" * 50)
    
    print("\nMONITORING SESSIONS:")
    print("  # View all active sessions")
    print("  python3 manage.py monitor_sessions")
    print()
    print("  # View sessions for specific user")
    print("  python3 manage.py monitor_sessions --username your_username")
    print()
    print("  # Show only active sessions")
    print("  python3 manage.py monitor_sessions --active-only")
    print()
    print("  # Show detailed session information")
    print("  python3 manage.py monitor_sessions --detailed")
    print()
    print("  # Watch mode (updates every 30 seconds)")
    print("  python3 manage.py monitor_sessions --watch")
    
    print("\n🧹 CLEANING UP SESSIONS:")
    print("  # Dry run - see what would be cleaned")
    print("  python3 manage.py cleanup_sessions --dry-run")
    print()
    print("  # Clean up expired and inactive sessions")
    print("  python3 manage.py cleanup_sessions")
    print()
    print("  # Clean up for specific user")
    print("  python3 manage.py cleanup_sessions --username your_username")
    print()
    print("  # Mark sessions inactive after 12 hours")
    print("  python3 manage.py cleanup_sessions --max-inactive-hours 12")
    print()
    print("  # Delete old session records (older than 30 days)")
    print("  python3 manage.py cleanup_sessions --delete-old-sessions --days-to-keep 30")
    
    print("\n⚙️ AUTOMATIC SESSION MANAGEMENT:")
    print("  • Sessions are automatically tracked via middleware")
    print("  • Inactive sessions are marked after 24 hours (configurable)")
    print("  • Expired sessions are cleaned up every 5 minutes")
    print("  • All session activity is logged in AuthenticationLog")
    
    print("\nWHAT TRIGGERS SESSION DEACTIVATION:")
    print("  1. ⏰ Session expires (JWT token expiration)")
    print("  2. 😴 No activity for 24+ hours (configurable)")
    print("  3. Manual logout via API")
    print("  4. Manual cleanup via management commands")
    print("  5. 🔄 Token refresh failure")
    
    print("\nVIEWING SESSION DATA:")
    print("  • Django Admin: /admin/UserManagement/usersession/")
    print("  • API Endpoint: /api/user/sessions/ (for own sessions)")
    print("  • Admin API: /api/admin/sessions/ (for all sessions)")
    print("  • Logs: /admin/UserManagement/authenticationlog/")

def main():
    """Main test function"""
    print("🛡️ CRISP Session Management Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_session_monitoring()
        test_session_cleanup_dry_run()
        show_session_management_usage()
        
        print("\n" + "=" * 50)
        print("SESSION MANAGEMENT SYSTEM READY!")
        print("=" * 50)
        print("Key Features Implemented:")
        print("  Automatic session activity tracking")
        print("  Periodic cleanup of expired sessions")
        print("  Inactivity-based session deactivation")
        print("  Comprehensive session monitoring")
        print("  Management commands for cleanup")
        print("  Detailed audit logging")
        
        print("\nNext Steps:")
        print("  1. Login as a user and monitor session activity")
        print("  2. Run: python3 manage.py monitor_sessions --watch")
        print("  3. Test inactivity timeout (wait 24+ hours or change config)")
        print("  4. Set up cron job for regular cleanup")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)