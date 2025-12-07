"""
Persistenter Cache für WetterApp.
Kombiniert:
- Memory Cache (schnell)
- SQLite Cache (persistent)
- TTL (Zeit bis Eintrag verfällt)
- optionale Speicherung in der History

Wird später von Provider verwendet, um doppelte API/CSV-Aufrufe zu vermeiden.
"""

import time
from typing import Any, Dict, Optional
from backend.storage.sqlite_handler import SQLiteHandler


class PersistentCache:
    def __init__(self, ttl_seconds: int = 600, enable_history: bool = True) -> None:
        """
        ttl_seconds: Gültigkeitsdauer für Einträge im In-Memory-Cache.
        enable_history: Falls True, werden Werte zusätzlich in weather_history gespeichert.
        """
        self.ttl = ttl_seconds
        self.enable_history = enable_history

        # In-Memory Cache
        self.memory_cache: Dict[str, tuple[Any, float]] = {}

        # Persistente Speicherung via SQLite
        self.db = SQLiteHandler()

    # --------------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------------
    def normalize_key(self, key: str) -> str:
        """Normalisiert die Keys, damit 'BERLIN', 'Berlin' und 'berlin' identisch sind."""
        return key.strip().lower()

    def is_expired(self, expires_at: float) -> bool:
        """Prüft, ob der Cache-Eintrag zu alt ist."""
        return time.time() > expires_at

    # --------------------------------------------------------
    # CACHE LESEN
    # --------------------------------------------------------
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Liest Daten aus Memory-Cache oder SQLite.
        Gibt entweder die Daten oder None zurück.
        """
        norm_key = self.normalize_key(key)

        # 1) Memory Cache prüfen
        if norm_key in self.memory_cache:
            value, expires_at = self.memory_cache[norm_key]

            if not self.is_expired(expires_at):
                return value
            else:
                del self.memory_cache[norm_key]

        # 2) Persistenter Cache (SQLite)
        db_value = self.db.get_cache(norm_key)

        if db_value is not None:
            # Kein TTL auf DB → jetzt frischen Memory-Eintrag legen
            expires_at = time.time() + self.ttl
            self.memory_cache[norm_key] = (db_value, expires_at)
            return db_value

        return None

    # --------------------------------------------------------
    # CACHE SCHREIBEN
    # --------------------------------------------------------
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Speichert Wert im Memory-Cache und im SQLite-Cache."""
        norm_key = self.normalize_key(key)
        expires_at = time.time() + self.ttl

        # Memory aktualisieren
        self.memory_cache[norm_key] = (value, expires_at)

        # Persistenten Cache schreiben
        self.db.set_cache(norm_key, value)

        # Historie optional
        if self.enable_history:
            self.db.add_history(norm_key, value)

    # --------------------------------------------------------
    # OPTIONAL: MEMORY-CACHE LEEREN
    # --------------------------------------------------------
    def clear_memory(self) -> None:
        """Leert nur den In-Memory-Cache (nicht die SQLite-DB)."""
        self.memory_cache.clear()
