#!/usr/bin/env python3
"""
Comprehensive rate limit cleaner
"""

import os
import sys
import time

def clear_all_rate_limits():
    """Clear all rate limits comprehensively"""
    print("🧹 Comprehensive rate limit clearing...")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    import django
    django.setup()
    
    from django.core.cache import cache
    from django.conf import settings
    
    # Clear entire cache
    cache.clear()
    print("   Cleared all cache")
    
    # Get current time and calculate multiple windows
    current_time = int(time.time())
    
    # Clear rate limits for multiple time windows (5 minute windows)
    for window_size in [60, 300, 3600]:  # 1 min, 5 min, 1 hour windows
        time_window = current_time // window_size
        
        # Clear current and surrounding windows
        for i in range(-10, 11):  # Clear 10 windows before and after
            window = time_window + i
            
            # Different possible key patterns
            key_patterns = [
                f'ratelimit:login:127.0.0.1:{window}',
                f'ratelimit:api:127.0.0.1:{window}',
                f'ratelimit:password_reset:127.0.0.1:{window}',
                f'rl:login:127.0.0.1:{window}',
                f'rl:api:127.0.0.1:{window}',
                f'rl:password_reset:127.0.0.1:{window}',
                f'rate_limit:login:127.0.0.1:{window}',
                f'rate_limit:api:127.0.0.1:{window}',
                f'login:127.0.0.1:{window}',
                f'api:127.0.0.1:{window}',
            ]
            
            for key in key_patterns:
                cache.delete(key)
    
    print("   Cleared all rate limit patterns")
    
    # Also try to clear any keys that might exist in the cache
    try:
        if hasattr(cache, '_cache'):
            all_keys = list(cache._cache.keys())
            for key in all_keys:
                if any(pattern in str(key) for pattern in ['ratelimit', 'rate_limit', 'login', 'api']):
                    cache.delete(key)
                    print(f"   Deleted key: {key}")
    except:
        pass
    
    print("✅ Comprehensive rate limit clearing completed")
    
    # Wait for any pending rate limit windows to expire
    print("⏳ Waiting for rate limit windows to expire...")
    time.sleep(10)
    
    return True

if __name__ == "__main__":
    try:
        clear_all_rate_limits()
        print("✅ Rate limits cleared successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to clear rate limits: {e}")
        sys.exit(1)
