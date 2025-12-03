#verwaltet den cache für die API-Respionses, speichert sie in data/cache mit timestamp und stadtname im dateinamen

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class CacheManager:
    """Verwaltet Cache für API-Responses"""
    
    def __init__(self, cache_dir='data/cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(minutes=10)  # 10 Minuten Cache - danach Aktuallisierung nötig
    
    def _get_cache_filename(self, city):
        """Erstellt Dateinamen wie 2025-11-26-14-07_paris.json"""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')
        safe_city = city.lower().replace(' ', '_')
        return f"{timestamp}_{safe_city}.json"
    
    def save(self, city, data):
        """Speichert API-Response im Cache"""
        filename = self._get_cache_filename(city)
        filepath = self.cache_dir / filename
        
        cache_entry = {
            'timestamp': datetime.now().isoformat(),
            'city': city,
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cache_entry, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Cache gespeichert: {filepath}")
        return filepath
    
    def get_latest(self, city):
        """Holt neuesten Cache für eine Stadt"""
        safe_city = city.lower().replace(' ', '_')
        cache_files = sorted(
            [f for f in self.cache_dir.glob(f"*_{safe_city}. json")],
            reverse=True
        )
        
        if not cache_files:
            return None
        
        latest_file = cache_files[0]
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            cache_entry = json.load(f)
        
        # Prüfe ob Cache noch gültig
        cached_time = datetime.fromisoformat(cache_entry['timestamp'])
        if datetime.now() - cached_time > self.cache_duration:
            print(f"⚠️ Cache veraltet für {city}")
            return None
        
        print(f"✅ Cache getroffen: {latest_file}")
        return cache_entry['data']
    
    def is_valid(self, city):
        """Prüft ob gültiger Cache existiert"""
        return self.get_latest(city) is not None
    
