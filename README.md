<h1 align="center">🌦️ WetterApp</h1>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.5-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/status-stable-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PKI-B_3_1-orange?style=for-the-badge" />
</p>


<h2 align="center">Ein Gruppenprojekt im Rahmen des Masterstudiums "Angewandte KI"</h1>

<p align="center">
  <img src="docs/WetterApp_Screenshot-v1_0_1.png" alt="WetterApp Demo" width="700"/>
</p>

# 📋 Überblick

Die **WetterApp** ist eine Web-Anwendung, die Wetterdaten abruft und visualisiert:

- **API-Calls** sorgen für die Datengrundlage (Aktual: OpenWeatherMap, Historisch & Vorhersage: OpenMeteo)
- **Interaktive Karte** zeigt die aktuelle Stadt mit Temperatur-Pin (`Folium`)
- **Echtzeit-Updates** über WebSockets (``Socket.IO``)
- **Historische Verlaufsansicht** mit serverseitig gerenderten Plots
- **Wettervorhersage** mit serverseitig gerenderten Plots
- **Flexible Datenquellen**: CSV-Dateien oder externe APIs (z. B. OpenWeather)
- **Responsives Design** über ``Bootstrap``
- **Modulare Backend-Architektur** für einfache Erweiterungen bei gleichbleibenden Schnittstellen


# ✨ Features

### Frontend

- 🗺️ **Live-Karte**:  Zeigt gewählte Stadt mit Temperatur-Marker
- 📊 **Wetter-Widgets**: Temperatur, Luftfeuchtigkeit, Windgeschwindigkeit, Sonnenauf-/-untergang
- 📈 **Verlaufsansicht (History)**: Anzeige historischer Wetterdaten als Diagramm in einem Overlay
- 🔄 **WebSocket-Updates**:  Kein Seiten-Neuladen nötig
- 🎨 **Modernes UI**: Bootstrap, responsives Design

### Backend

- 🔌 **Provider-Architektur**: Einfacher Wechsel zwischen CSV und API
- 📝 **Data Normalizer**: Vereinheitlicht Daten aus verschiedenen Quellen -> stets gleiches Format ans Frontend
- 📊 **Serverseitige Plot-Erzeugung**: Historische Zeitreihen werden im Backend mit Matplotlib gerendert
- 🛡️ **Robuste Fehlerbehandlung**: Validierung, Logging, Fallbacks
- 🗂️ **Saubere Struktur**: Getrennte Layer (Provider, Services, Dashboard)


# 📡 API-Schnittstellen

| Daten                 | Server         | API                  | URL                                                    |
|-----------------------|----------------|----------------------|--------------------------------------------------------|
| **Aktualwerte**       | OpenWeatherMap | Current weather data | https://openweathermap.org/current                     |
| **Historische Werte** | OpenMeteo      | Historical Weather   | https://open-meteo.com/en/docs/historical-weather-api  |
| **Vorhersage**        | OpenMeteo         | Historical Forecast  | https://open-meteo.com/en/docs/historical-forecast-api |


# 🛠️ Installation & Verwendung

### Voraussetzungen

- Python 3.9+
- pip


```bash
# Repository klonen
git clone https://github.com/julwilke/WetterApp.git
```

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

```bash
# Dependencies installieren
pip install -r requirements.txt
```

### Konfiguration

```bash
# Umgebungsvariablen konfigurieren
# Erstelle eine .env (oder bennene .env.example um) mit folgendem Inhalt:

# Welcher Provider? ('api' oder 'csv')
WEATHER_PROVIDER = api
OPENWEATHER_API_KEY = dein_key_hier

# Auf welchem Niveau soll der Logger Meldungen ausgeben? (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

### Starten
```bash
# Dashboard starten
python app.py

(läuft dann unter: http://127.0.0.1:5000)
```

### CLI-Starten

```bash
# Für API-Tests und Development

# Starten mit sample Daten aus "sample.csv"
python -m cli.cli --file cli/sample.csv

# Für API-Abfrage
$env:OPENWEATHER_API_KEY="DEIN_KEY_HIER"   
python -m cli.cli --ow-city Berlin

# API-Abfrage inklusive Datenexport -> .csv
python -m cli.cli --ow-city Berlin --log cli/LOG_NAME.csv
```

### Automatisierte PyTests für CLI-Version
```bash
# PyTest ausführen
pytest cli/test_parse_weather.py
```


# 🏗 Architektur (Kern)

```text
WetterApp/
├── app.py                              # Einstiegspunkt der Anwendung
├── .env                                # Konfiguration (nicht im Repo)
├── requirements.txt                    # Python-Abhängigkeiten
│
├── backend/
│   ├── dashboard.py                    # Flask + Socket.IO Backend
│   ├── logging_config.py               # Zentrale Logging-Konfiguration
│   │
│   ├── provider/
│   │   ├── csv_weather_provider.py     # CSV-Datenquelle
│   │   └── api_weather_provider. py    # API-Gerüst (OpenWeather)
│   │
│   └── services/
│       ├── data_normalizer.py          # Daten-Normalisierung
|       |── history_openmeteo.py        # Zugriff auf Open-Meteo Archive API (History)
|       |── plotter.py                  # Matplotlib-Plot-Erzeugung (PNG)
│       └── generate_map. py             # Folium-Karten-Generator
│
├── weather_dashboard/
│   ├── templates/
│   │   └── index.html                  # Frontend HTML
│   │
│   └── static/
│       ├── styles.css                  # Styling
│       ├── script.js                   # Frontend-Logik (WebSocket, UI-Updates)
│       └── map/                        # Generierte Karten (dynamisch)
│
└── data/
    └── samples/
        └── weather_sample.csv          # Beispiel-Wetterdaten
```


# 🛠️ Technology Stack

## Backend (Python)

| Package | Verwendung |
|---------|------------|
| **python-dotenv** | Laden von Umgebungsvariablen aus `.env` |
| **Flask** | Web-Framework für HTTP-Routen und Template-Rendering |
| **Flask-SocketIO** | WebSocket-Unterstützung für Echtzeit-Updates |
| **requests** |  HTTP-Client für API-Calls (API-Provider vorbereitet) |
| **Geopy** |  Geocoding (Stadtname → GPS-Koordinaten) |
| **Folium** |  Generierung interaktiver Leaflet-Karten |
| **Pandas** |  CSV-Datenverarbeitung und Filterung |
| **Matplotlib**  | Serverseitige Erzeugung von Verlaufsdiagrammen |
| **pytest**   | Für automatisierte Tests der CLI-Version |
| **numpy** | NP-Datentypen

## Frontend

| Technologie | Verwendung |
|-------------|------------|
| **HTML5** | Markup und Struktur |
| **CSS3** | Styling und Layout |
| **JavaScript (ES6+)** | Client-seitige Logik und DOM-Manipulation |
| **Bootstrap** | Responsive UI-Framework (Grid, Components) |
| **Socket.IO Client** | WebSocket-Kommunikation mit Backend |
| **Leaflet** | Interaktive Kartenvisualisierung (über Folium) |

## Entwicklung & Tools

- **Python** 3.10+
- **pip** 
- **Virtual Environment** (venv) 


## 👥 Team

### PKI- Projektgruppe B1-3

Alle Projektmitglieder haben gemeinsam an Konzeption, Abstimmung und Integration der Anwendung gearbeitet.
Für die Präsentation und zur besseren fachlichen Zuordnung wurden dennoch folgende Themenschwerpunkte festgelegt:

- Adham - Weather Provider & API-Anbindung
- Tugba - CLI-Tooling & automatisierte Tests
- Nick-Andre - Frontend & Benutzeroberfläche
- Julian - Backend-Architektur & Datenverarbeitung

## 📄 License

AGPLv3 — see LICENSE file for full terms.
© 2026 (PKI Gruppe B1-3)

---

**Letzte Aktualisierung**: 26.01.2026
