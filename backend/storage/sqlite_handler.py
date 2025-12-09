"""
SQLite Handler
Diese Minimalversion bietet:
- persistente Speicherung (Cache Layer)
- optionale Historie
- automatische Tabellenerstellung

Erweiterbar auf:
- Trend-Analysen
- cron-basierte Updates
- komplette Wetterhistorie
"""

import sqlite3
import json
import os
from datetime import datetime

# ------------------------------------------
# 1) Speicherpfad korrekt ermitteln
# ------------------------------------------

#Pfad in dem diese sqlite_handler.py liegt
STORAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# Pfad zur SQLite DB 'weather.db' im /storage
DB_PATH = os.path.join(os.path.dirname(__file__), "weather.db")

# ------------------------------------------
# 2) Klasse: SQLite Handler
# ------------------------------------------
class SQLiteHandler:
    """Stellt Verbindung zur SQLite DB her und unterstützt Cache + History."""

    def __init__(self):
        # Ordner sicherstellen
        os.makedirs(STORAGE_DIR, exist_ok=True)

        # DB-Verbindung
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

        # Tabellen erzeugen, falls nicht vorhanden
        self.create_tables()

    # --------------------------------------
    # Tabellen generieren
    # --------------------------------------
    def create_tables(self):
        cursor = self.conn.cursor()

        # Persistenter Cache
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            last_updated INTEGER
        )
        """)

        # Historische Werte
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            data TEXT,
            timestamp INTEGER
        )
        """)

        self.conn.commit()

    # --------------------------------------
    # CACHE HOLEN
    # --------------------------------------
    def get_cache(self, key: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM cache WHERE key = ?", (key,))
        row = cursor.fetchone()

        if row:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return None

        return None

    # --------------------------------------
    # CACHE SCHREIBEN
    # --------------------------------------
    def set_cache(self, key: str, value: dict):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO cache (key, value, last_updated)
            VALUES (?, ?, ?)
        """, (
            key,
            json.dumps(value),
            int(datetime.utcnow().timestamp())
        ))
        self.conn.commit()

    # --------------------------------------
    # HISTORIE SCHREIBEN
    # --------------------------------------
    def add_history(self, city: str, data: dict):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO weather_history (city, data, timestamp)
            VALUES (?, ?, ?)
        """, (
            city.lower(),
            json.dumps(data),
            int(datetime.utcnow().timestamp())
        ))
        self.conn.commit()

    # --------------------------------------
    # HISTORIE LESEN
    # --------------------------------------
    def get_history(self, city: str, limit: int = 50):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT data, timestamp
            FROM weather_history
            WHERE city = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (city.lower(), limit))

        rows = cursor.fetchall()

        return [
            {
                "data": json.loads(r[0]),
                "timestamp": r[1]
            }
            for r in rows
        ]
    

