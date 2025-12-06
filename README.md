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

Die WetterApp ist eine Python-basierte Anwendung zur Abfrage und Analyse von Wetterdaten. Das Projekt startet mit einem einfachen Skript zum Abrufen aktueller Wetterdaten per API für eine gegebene Postleitzahl und wird schrittweise um weitere Features erweitert.

Das Ziel ist eine benutzerfreundliche und erweiterbare WebApp mit vielen üblichen Funktionen der Darstellung von Wetter Daten.

## Version

-aktuelle Version: 1.0.0

## 🎯 Projektziele

- **Phase 1**:
    -✅ Einfaches Python-Skript zur Wetterabfrage per API (Postleitzahl → aktuelle Wetterdaten) in der Konsole --> MVP (Minimum Viable Product)
    -✅ Grundlegende WebApp entwickeln
    -[ ] Abgabefertige und bewertbare Lösung fertigstellen
- **Phase 2**:
    -[ ] Erweiterte Wetteranalysen und Datenvisualisierung, weitere Funktionen bestimmen und einbinden
    -[ ] Persistenz ausgewählter Daten
    -[ ] Logging, Debugging, Test-Funktionen einbauen
- **Phase 3**:
    -[ ] Integration von KI-Funktionen (eigene Vorhersagen, Mustererkennung, Anomalien (z.B. "ungewöhnlich warmer Dezember")
- **Phase 4**: Finalisierung
    -[ ] Code-Refactoring / Hardening
    -[ ] docs / configs / README.MD finalisieren

## 🛠️ Installation & Verwendung

```bash
# Repository klonen
git clone https://github.com/julwilke/WetterApp.git
cd WetterApp

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Skript ausführen
python app.py
```

## 📦 Technology-Stack

- **Sprache**: Python 3.10+ (prüfen!)
- **API**: OpenWeatherMap
- **Libraries**: folgen
- **Zukünftig**: folgen

## 👥 Team

- Adham
- Tugba
- Nick-Andre
- Julian

## 📝 Notizen

- Meeting-Protokolle im `/docs` Ordner
- Branch-Strategie: Private-Branches → Main

---

## 📄 License

AGPLv3 — see LICENSE file for full terms.
© 2025 (PKI Gruppe B1-3)

---

**Letzte Aktualisierung**: 30.11.2025
