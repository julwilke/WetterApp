# Programmablauf

## 1. Boot-Sequenz: `app.py`

- startet das Backend. Mehr nicht. Kein Routing, keine Logik.
- `app = dashboard.WeatherDashboard()` erzeugt ein Dashboard aus der Klasse `WeatherDashboard`
- `app.run()` führt die `run()` Funktion des Dashboards aus. Ab hier übernimmt komplett die Backend-Architektur
- damit ist die Boot-Sequenz abgeschlossen und der Rest passiert in der `WeatherDashboard`-Klasse

## 2. Backend-Kern: `WeatherDashboard` (`dashboard.py`)

- Datei: `dashboard.py`

### 2.1 Erstellen der Instanz ( `__init__()` )

- **A) Flask-App aufsetzen**
  - `self.app = Flask(...templates..., ...static...)`
  - das Backend weiß jetzt, wo das `html`-Template liegt, wo die `.csv` liegt, wo die `css` und `javascript` Dateien liegen und wo die `map.html` gespeichert werden soll

- **B) SocketIO aktivieren**
  - `self.socketio = SocketIO(self.app, cors_allowed_origins="*")`
  - damit ermöglichen wir Live-Updates der Webseite, sobald eine neue Stadt eingegeben wird
  - andernfalls müsste jedes mal ein `HTTP`-Reload gemacht werden

- **C) CSV-Provider vorbereiten**
  - `self.provider = CSVWeatherProvider("weather_sample.csv")`
  - hier wird der Provider noch nicht mit Daten geläden, nur vorbereitet (*Lazy Loading*)

- **D) Initialwerte setzen** (Delayed Initialization)
  - `self.city = None`
  - `self.weather_data = None`
  - `self.last_polled = None`
  - ab hier wird das Dashboard erst wirklich mit (noch leeren) Daten belegt

- **E) Geolocater: Stadt -> Koordinaten**
  - `self.geolocator = Nominatim(user_agent="weather_dashboard")`
  
- **F) Routen registrieren
  - `self.define_routes()

- **G) Websocket-Events registrieren
  - `self.define_socket_events()`
  
=> *Ab hier steht das Backend bereit!*

### 2.2 Der eigentliche Startpunkt: `run(city='Berlin')`

- `app.py` ruft `run()`auf, nicht der Konstruktor des Dashboards!
- hier passiert die echte Initialisierung: `self.initialize(city)`
  - setzt `self.city = city`
  - holt Wetterdaten aus dem .csv
  - Fallback auf 'Berlin', falls Stadt nicht existiert
  - setzt den Timestamp für `last_polled`

 =>  *Ab hier ist das Backend voll eingerichtet!*

- dann startet der Server: `self.socketio.run(self.app)`
  - Websocket läuft
  - HTTP-Routing läuft
  - Frontend kann zugreifen

## 3) CSV-Wetterdaten: `CSVWeatherProvider`

- Datei: `csv_weather_provider`
- löst dynamische Pfadprobleme
  - Bestimmt Ordner des Providers
  - Geht einen Ordner nach oben (von `/backend` in `/root`)
  - navigiert nach `/data/samples`
  - baut dort absoluten Pfad zur `.csv`
  - Lädt die Dater erst beim Aufruf von `get_weather_for_city()`
- Beim Abfragen:
  - `df = pd.read_csv(self.csv_path)`
  - `df_city = df[df["CITY"].str.lower() == city.lower()]`
  - wenn Stadt vorhanden:
    - extrahiere Zeile
    - baue ein Dictionairy mit
      - Temperatur
      - Luftfeuchte
      - Wind
      - ...

## 4) Map-Generator: `generate_map.py`

- erzeugt `folium` Map
- setzt Temperatur-Pin als Icon in die Karte zur gewählten Stadt
- bestimmt Zielpfad zum abspeichern
  - `WetterApp/weather_dashboard/static/map/map.html`
- jeder neue Aufruf einer Stadt generiert eine neue Map
- Frontend merkt das Socket-Event und lädt die neue Map

## 5) Routen des Backends - HTTP-API (`define_routes(self)`)

- `@self.app.route('/')`
  - rendert die `index.html`
- `@self.app.route('/weather')`
  - Gibt `JSON` zurück
    - Wetterdaten aus `csv`
    - Koordinaten aus GeoPy
    - Timestamp
    - *Diese Route nutzt das Frontend, um initiale Daten anzuzeigen*

## 6) Socket-Events - Live-Updater

- Wenn das Dashboard über das WebSocket sendet:
  - `socket.emit("cityInput", { city: "Dortmund" })`
  - dann passiert im Backend:
    - Stadt übernehmen: `self.city = new_city`
    - CSV ansehen für die neue Stadt
    - Koordinaten aus GeoPy holen
    - Neue Folium-Karte rendern
    - Alle Daten via SocketIO wieder zurück ans Frontend senden
      - `self.socketio.emit("update", {...})`

- *Frontend aktualisiert somit ohne die Seite bewusst neuzuladen/aktualisieren zu müssen*
