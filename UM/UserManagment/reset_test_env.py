#!/usr/bin/env python3
"""
Test Reset Utility - Clears all rate limiting and prepares for clean testing
"""

import os
import sys
import time

def reset_test_environment():
    """Reset the test environment for clean testing"""
    print("🔄 Resetting test environment...")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    import django
    django.setup()
    from django.core.cache import cache
    
    # Clear all cache
    print("🧹 Clearing Django cache...")
    cache.clear()
    
    # Clear specific rate limiting keys for multiple time windows
    current_time = int(time.time())
    
    # Clear rate limit keys for past, current, and future time windows
    for window_size in [60, 300, 3600]:  # 1 min, 5 min, 1 hour
        for offset in range(-10, 11):  # 10 windows before and after
            time_window = (current_time // window_size) + offset
            
            keys_to_clear = [
                f'ratelimit:login:127.0.0.1:{time_window}',
                f'ratelimit:api:127.0.0.1:{time_window}',
                f'ratelimit:password_reset:127.0.0.1:{time_window}',
                # Also try with different IP patterns
                f'ratelimit:login:localhost:{time_window}',
                f'ratelimit:api:localhost:{time_window}',
            ]
            
            for key in keys_to_clear:
                try:
                    cache.delete(key)
                except:
                    pass
    
    print("✅ Cache cleared comprehensively")
    
    # Wait a moment to ensure any ongoing requests complete
    print("⏳ Waiting for any ongoing requests to complete...")
    time.sleep(2)
    
    print("✅ Test environment reset complete")

if __name__ == "__main__":
    reset_test_environment()
