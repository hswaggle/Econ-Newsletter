import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class DataCache:
    def __init__(self, cache_dir='cache', cache_duration_hours=24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(hours=cache_duration_hours)
    
    def _get_cache_path(self, key):
        """Get the file path for a cache key"""
        return self.cache_dir / f"{key}.json"
    
    def get(self, key):
        """Get cached data if it exists and is fresh"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is still fresh
            cached_time = datetime.fromisoformat(cached['cached_at'])
            if datetime.now() - cached_time < self.cache_duration:
                print(f"✓ Using cached data for {key} (cached {cached_time.strftime('%Y-%m-%d %H:%M')})")
                return cached['data']
            else:
                print(f"⚠ Cache expired for {key}")
                return None
                
        except Exception as e:
            print(f"✗ Error reading cache for {key}: {e}")
            return None
    
    def set(self, key, data):
        """Cache data with timestamp"""
        cache_path = self._get_cache_path(key)
        
        try:
            cached = {
                'cached_at': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cached, f, indent=2)
            
            print(f"✓ Cached data for {key}")
        except Exception as e:
            print(f"✗ Error writing cache for {key}: {e}")
    
    def clear(self, key=None):
        """Clear cache for a specific key or all cache"""
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                print(f"✓ Cleared cache for {key}")
        else:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
            print("✓ Cleared all cache")