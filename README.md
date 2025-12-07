<h1 align="center">🌦️ WetterApp</h1>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/python-3.11%2B-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/status-stable-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-AGPL--3.0-red?style=for-the-badge" />
</p>

---

### Ein Gruppenprojekt im Rahmen des Masterstudiums "Angewandte KI"

---

# 📌 Projektübersicht

Das WetterApp-Backend stellt eine modulare und erweiterbare Architektur bereit,  
mit der Wetterdaten über mehrere Provider (CSV, API) verarbeitet und an eine Web- oder CLI-Oberfläche übergeben werden können.

Version `v1.0.0` bildet den **ersten stabilen Release**, der eine konsistente Projektstruktur, sauberes Boot-Verhalten und robuste Datenpfade bereitstellt.

---

## 🛠️ Installation & Verwendung

```bash
# Repository klonen
git clone https://github.com/julwilke/WetterApp.git

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# API-Key setzen in .env (neu erstellen oder Umbennenung von .env.example)
OPENWEATHER_API_KEY = dein_key

# Dashboard starten
python app.py

(läuft dann unter: http://127.0.0.1:5000)

# CLI-Version starten
python cli/cli.py

```

# 🏗 Architekturüberblick

```text
WetterApp/
├── app.py                       # Entry Point (Boot-Sequenz)
│
├── backend/                     # Backend-Logik (Provider, Routing, Map)
│   ├── dashboard.py             # Haupt-Backend: Routing, Socket, Initialisierung
│   ├── csv_weather_provider.py  # CSV-Provider (Test-/Fallback-Daten)
│   ├── generate_map.py          # Dynamische Folium-Map-Erzeugung
│   └── __init__.py
│
├── cli/                         # CLI-Version der App (Alternative zum Web-Dashboard)
│   ├── cli.py                   # Wetterabfrage per Konsole (API/PLZ)
│   └── __init__.py
│
├── weather_dashboard/           # Frontend (HTML, CSS, JS)
│   ├── static/
│   │   └── map/                 # Dynamisch generierte HTML-Karten
│   └── templates/               # index.html & UI-Struktur
│
├── data/
│   └── samples/                 # Beispiel-/Fallback-Daten wie weather_sample.csv
│
├── docs/                        # Allgemeine Dokumentation & Projektunterlagen
│
├── logging/                     # Reserviert für Logging-Konfigurationen
│
├── requirements.txt             # Python-Abhängigkeiten
├── .env.example                 # Beispielkonfiguration (API-Keys, Flags)
└── LICENSE
```

## 📋 Projektbeschreibung

📌 Projektübersicht

Die WetterApp ist ein modular aufgebautes System zur Abfrage, Aufbereitung und Darstellung von Wetterdaten.
Sie besteht aus:

- einer CLI-Version zur Wetterabfrage über die Konsole
- einem Backend auf Basis von Flask & Socket.IO
- einem CSV-Provider als Fallback-/Beispiel-Datenquelle
- einem Map-Generator, der dynamisch Folium-Karten erzeugt
- einem Web-Dashboard, das Nutzerinteraktionen live verarbeitet

Die Architektur ist noch erweiterbar und geplant ist zukünftig:

- zusätzliche Wetter-APIs
- Persistenzschichten
- Logging
- KI-gestützte Wetteranalysen

## Version

- aktuelle Version: `1.0.0`

## 🎯 Projektziele

- **Phase 1**:
  - ✅ CLI-Version zur Wetterabfrage per API (Postleitzahl → aktuelle Wetterdaten) in der Konsole 
    - --> MVP (Minimum Viable Product)
  - ✅ Grundlegende WebApp entwickeln
  - ✅ Wetterdaten aus CSV (Als Test/Fallback)
  - ✅ Live-Updates im Dashboard
  - ✅ Kartenerstellung passend zur Wetterabfrage
  - ❌ CSV-Daten durch API-Live-Abfrage erweitern
  - ❌ Abgabefertige und bewertbare Lösung fertigstellen

- **Phase 2**:
  - ❌ Erweiterte Wetteranalysen und Datenvisualisierung, weitere Funktionen bestimmen und einbinden
  - ❌ Persistenz ausgewählter Daten (CSV Cache, SQLite Datenbank)
  - ❌ Logging, Debugging, Test-Funktionen einbauen

- **Phase 3**: (Optional)
  - ❌ Integration von KI-Funktionen 
    - eigene Vorhersagen, Mustererkennung, Anomalien (z.B. "ungewöhnlich warmer Dezember")
  - ❌ Trendanalyse
  - ❌ Mustererkennung
  - ❌ Umsetzung eigener Vorhersagemodelle

- **Phase 4**: Finalisierung
  - ❌ Code-Refactoring / Hardening
  - ❌ Finalisieren der Konfiguration und Dokumentation
    - /docs
    - env.example
    - config.py's
    - README.MD
    - requirements.txt

## ⚙️ Technologie-Stack

- Python 3.11+
- Flask – Webserver & Routing
- Flask-SocketIO – Live-Datenübertragung
- Folium – Generierung interaktiver Karten
- Pandas – CSV-Verarbeitung
- geopy (Nominatim) – Geocoding für Städte
- Requests – API-Abfragen
- dotenv – Laden von API-Keys aus .env

## 👥 Team

- Adham
- Tugba
- Nick-Andre
- Julian

## 📝 Notizen

## 📄 License

AGPLv3 — see LICENSE file for full terms.
© 2025 (PKI Gruppe B1-3)

---

**Letzte Aktualisierung**: 07.12.2025 by Julian
