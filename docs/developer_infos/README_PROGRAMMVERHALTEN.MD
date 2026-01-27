# Programmverhalten 

## 1) Start und Konfiguration: `app.py`

- startet das Backend. Mehr nicht
- lädt `.env` und Logging
- entscheidet, woher die Daten kommen (API/CSV)
- `app = dashboard.WeatherDashboard()` erzeugt ein Dashboard aus der Klasse `WeatherDashboard`

*-> Backend ist konfiguriert, aber noch nicht gestartet*

## 2) Backend-Kern: `WeatherDashboard` (`dashboard.py`)

- setzt **Flask** und **Socket-IO** auf
- registriert HTTP-Routen (``/``, ``/weather``, ``/status``, ...)
- WebSocket-Events (Stadtwechsel ohne Seitenreload)
- hält den aktuellen Zustand
  - aktuelle Stadt
  - Wetterdaten
  - letzter Aktualisierungszeitpunkt

*-> Backend ist bereit, Frontend kann zugreifen*

## 3) Initialisierung & Serverstart: `run()`

- initialisiert die Start-Stadt
- holt Wetterdaten über den gewählten Provider (CSV/API)
- ermittelt Koordinaten (Geopy)
- erzeugt die Karte (Folium)
- startet HTTP-Server + WebSocket

*-> Dashboard ist vollständig lauffähig*

## 4) Datenbeschaffung: Provider-Prinzip

- `CSVWeatherProvider`: lädt CSV
- `APIWeatherProvider`: ruft Live-Daten ab
- alle Daten werden einheitlich normalisiert, egal aus welcher Quelle

*-> Frontend erhält immer das gleiche Format*

## 5) Benutzerinteraktion (Live-Update)

- Nutzer gibt neue Stadt ein -> Frontend sendet WebSocket-Event
- Backend:
  - prüft Stadt
  - lädt neue Daten
  - aktualisiert Karte & Zeitreihen
  - sendet Update zurück
- kein Seitenreload nötig

*-> Reaktive Oberfläche mit Echtzeit-Feedback*

## 6) Visualisierung
- Wetterdaten als Kacheln
- Karte: Folium-Map mit Temperatur Marker
- Verlauf & Prognose: Matplotlibs als PNG
- Frontend lädt aktualisierung automatisch dynamisch nach
