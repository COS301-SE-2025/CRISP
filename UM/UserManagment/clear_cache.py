#!/usr/bin/env python3
"""
Cache management utility for tests
"""

import os
import sys
import time

def clear_all_caches():
    """Clear all Django caches and wait for time window reset"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    import django
    django.setup()
    from django.core.cache import cache
    
    print("🧹 Clearing Django cache...")
    cache.clear()
    
    # Also manually clear any potential rate limit keys for current and recent time windows
    current_time = int(time.time())
    time_window = current_time // 300  # 5 minute windows
    
    # Clear current and previous time windows
    for i in range(-2, 3):  # Clear 2 windows before and after current
        window = time_window + i
        keys_to_clear = [
            f'ratelimit:login:127.0.0.1:{window}',
            f'ratelimit:api:127.0.0.1:{window}',
            f'ratelimit:password_reset:127.0.0.1:{window}',
        ]
        for key in keys_to_clear:
            cache.delete(key)
            print(f"🗑️  Cleared {key}")
    
    print("✅ All caches cleared")
    
    # Verify cache is empty
    try:
        if hasattr(cache, '_cache'):
            remaining = list(cache._cache.keys())
            if remaining:
                print(f"⚠️  Remaining keys: {remaining}")
            else:
                print("✅ Cache is completely empty")
        else:
            print("✅ Cache cleared successfully")
    except:
        print("✅ Cache operations completed")

if __name__ == "__main__":
    clear_all_caches()
