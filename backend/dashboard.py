###############################################
#   🌦 WETTER-DASHBOARD – BACKEND 1.0.4       #
###############################################

""" 
Backend-Klasse für das Wetter-Dashboard.
    
Aufgaben: 
    - Initialisierung des Flask-Servers und SocketIO
    - Routen und Websocket-Ereignisse definieren
    - Wetterdaten von einem Weather-Provider abrufen
    - Karten mit Wetterinformationen generieren
    - Reagieren auf Frontend-Ereignisse via Websockets
"""

# =============== IMPORTS ====================
import os
import logging

# Brauche ich die hier überhaupt? 
import matplotlib
matplotlib.use("Agg") # Server ohne Display
import matplotlib.pyplot as plt

from datetime import datetime, timedelta, timezone

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO

from geopy.geocoders import Nominatim

from io import BytesIO

from backend.provider.csv_weather_provider import CSVWeatherProvider
from backend.services import generate_map

from backend.services.history.history_openmeteo import fetch_openmeteo_history_dataframe
from backend.services.forecast.forecast_openmeteo import fetch_openmeteo_forecast_dataframe

from backend.services.plotter import build_single_history_plot_png, build_single_forecast_plot_png

# ============================================
#    1) Logging -Konfiguration 
# ============================================

logger = logging.getLogger(__name__)

# ============================================
#    2)  BACKEND-CORE 
# ============================================
class WeatherDashboard:
    """Klasse für das WeatherDashboard"""
    def __init__(self, provider = None):
        """KONSTRUKTOR: Initialisiert das WeatherDashboard mit Flask und SocketIO.
        Args:
            provider: Instanz eines Weather-Providers mit Methode get_weather_for_city(city) -> dict | None für Default CSV-Provider
        """
        # Frontend-Ordner korrekt setzen
        self.app = Flask(
            __name__,
            template_folder='../weather_dashboard/templates',
            static_folder='../weather_dashboard/static'
        )

        self.socketio = SocketIO(self.app, cors_allowed_origins="*") # Hier alle Origins erlaubt, ich denke aber für das Studentenprojekt ist das in Ordnung 

        # Provider auswählen: Entwerder eine der APIs oder Default CSV-Provider nutzen
        if provider is not None:
            self.provider = provider
        else:
            self.provider = CSVWeatherProvider("weather_sample.csv")    

        #Leer initialisieren, setzen in run() bzw. initialize()
        self.city = None                    # Aktuelle Stadt
        self.weather_data = None            # Wetterdaten für die Stadt als dict
        self.last_polled = None             # Zeitpunkt der letzten erfolgreichen Abfrage
             
        
        #Geodaten für Karte cachen, damit Nominatim nicht unnötig oft die Koordinaten wandelt und die Stadt abholt für die Karte
        self.geo_cache = {}

        #Geolocator Client bauen, später über Nominatim Städte zu Koordinaten auflösen
        self.geolocator = Nominatim(user_agent="weather_dashboard")

        #J: Neu hinzugefügt für bessere Modularisierung
        self.define_routes()
        self.define_socket_events()

    # ========================================
    # ROUTES → Frontend API
    # ========================================

    #J: Routen und Sockets als Funktionen (siehe oben im __init__) statt alles in den Konstruktor zu laden

    def define_routes(self):
        """
        Definiert die Routen. Routen werden erst registriert, wenn WeatherDashboard() erstellt wird.
        """
       
        # Route für die Hauptseite     
        @self.app.route('/')
        def index():
            return render_template('index.html')

        # Route für den API-Status / sichtbar im Dashboard oben rechts. unterscheidet zwischen API und CSV und zeigt Letztten Abruf (last_polled an)
        @self.app.route('/status')
        def status():
            
            # 1) Quelle bestimmen (API/CSV)            
            
            provider_klasse = self.provider.__class__.__name__

            # Nimmt den Namen "openweather" oder "csv" so wie es das Frontend erwartet
            if provider_klasse == "APIWeatherProvider":
                provider_key = "openweather"          
            elif provider_klasse == "CSVWeatherProvider":
                provider_key = "csv"
            else:
                provider_key = "unknown" 

            # 2) Rückgabe
            return jsonify({
                "apis": {
                    provider_key: {
                        "status": "ok" if self.last_polled is not None else "unbekannt",
                        "lastPolled": (
                            self.last_polled.isoformat() + "Z"
                            if self.last_polled else None
                        )
                    }
                }
            })

       

        # Route für Wetterdaten als JSON wenn Frontend diese anfragt
        @self.app.route('/weather')
        def weather():
            """
            Liefert die aktuellen Wetterdaten für self.city als JSON.
            
            - HTTP Statuscode bei Fehlern
            - Daten werden refreshed beim Provider, wenn sie 
                - fehlen
                - noch nicht abgerufen wurden
            """

            # ===== 1) FEHLER ABFANGEN / DATEN VALIDIEREN =====

            # Prüfen ob überhaupt eine Stadt gesetzt ist
            if not self.city:
                logger.warning("Anfrage (Request) auf /weather ohne definierte Stadt")

                return jsonify({
                    "city": None, 
                    "error": "Keine Stadt gesetzt"
                    }), 400  # 400 = Bad Request                  
                
            #now = datetime.utcnow()            # Aktuelle Zeit für den Ablauf der Gültigkeit der Werte setzen
            now = datetime.now(timezone.utc)    # Test Julian s.o.

            # ===== 2) REFRESH DER DATEN - ENTSCHEIDUNG =====
         
            # Refresh-Variable TRUE setzen, wenn 
            # - noch keine Daten vorhanden (Erststart der App)
            # - noch nie erfolgreich abgefragt wurde
    
            
            refresh_noetig = (
                self.weather_data is None
                or self.last_polled is None
            )
            
           # ===== 3) REFRESH DER DATEN - DATEN ABHOLEN =====

           #  Wenn Refresh nötig ist, dann das Wetter abrufen
            if refresh_noetig:
                logger.info(
                    f"/weather: Refresh nötig für (city='{self.city}', "
                    f"last_polled={self.last_polled}"
                )

                # --- Versuchen die Daten zu Refreshen ---
                try:
                    daten_fresh = self.provider.get_weather_for_city(self.city)

                    # === FALL A: Provider liefert nichts (None) ===
                    if daten_fresh is None:
                        logger.warning(f"/weather: Provider liefert keine Daten für '{self.city}'")

                        # Fallback 1: Cache existiert und wir können Cache-Daten zurückgeben (HTTP 200: OK)
                        if self.weather_data is not None:
                            logger.info("/weather: Cache vorhanden - verwende Cache-Daten als Fallback")
                                                      
                        # Fallback 2: Kein Cache und wir können nichts zurückliefern (HTTP 503: Service unavailable )
                        else:
                            logger.error("/weather: Kein Cache verfügbar, kann keine Daten liefern")
                            
                            return jsonify({
                                "city": self.city,
                                "error": "Provider zur Zeit nicht verfügbar (Keine Daten und kein Cache vorhanden)"
                            }), 503 # 503: Service unavailable


                    # === FALL B: Provider liefert gute Daten (dict) ===
                    else:
                        # Cache kann aktualisiert werden
                        self.weather_data = daten_fresh
                        self.last_polled = now
                                    
                # --- Fangen der harten Fehler die nicht im try-Block behandelt werden (Exception) ---
                except Exception as e:                    
                    logger.error(f"/weather: Fehler beim Abrufen für '{self.city}': {e}")
                    
                    # Fallback 1: Cache existiert und wir können Cache-Daten zurückgeben (HTTP 200: OK) 
                    if self.weather_data is not None:
                        logger.info("/weather: Fehler - Fallback auf Cache Daten")

                    # Fallback 2: Kein Cache vorhanden - Fehler!
                    else:
                        logger.error("/weather: Fehler - Kein Cache für Fallback verfügbar")

                        return jsonify({
                            "city": self.city,
                            "error": "Wetterdaten-Abruf ist fehlgeschlagen"
                        }), 503 #503 = Service unavailable



            # ===== 4) KOORDINATEN HOLEN FÜR MAP (noch keine Generierung) =====
            logger.info(f"Koordinaten für '{self.city}' werden geholt")
            lat, lon = self.fetch_coordinates(self.city)
            


            # ===== 5) RESPONSE BAUEN =====
            response = {        
                "city": self.city,        
                "lat": lat,
                "lon": lon,
                                    #"lastPolled": (self.last_polled.isoformat() + "Z") if self.last_polled else None, # Zeitstempel der letzten ERFOLGREICHEN Abfrage
                "lastPolled": self.last_polled.isoformat().replace("+00:00", "Z") if self.last_polled else None #Test Julian s.o.
            }

            # Damit History im Frontend nicht crasht, aber zumindest leer übergeben wird. Kann erweitert werden
            # Frontend erwartet '_history' - Werte im response
            response.update({
                "currentTemperature_history": [],
                "humidity_history": [],
                "pressure_history": [],
            })
            
            # Wetterdaten hinzufügen ins JSON dict
            if isinstance(self.weather_data, dict):
                response.update(self.weather_data)

            else:
                # Sollte eigentlich abgefangen sein, nur zur Sicherheit ^^
                logger.error("/weather: weather_data ist nicht verfügbar/kein dict")
                return jsonify({
                    "city": self.city,
                    "error": "Keine Wetterdaten verfügbar"
                }), 503 # 503 = Service unavailable

            return jsonify(response), 200 # 200 = OK        




        # Route für die Vergangenheitsdaten / History
              
        @self.app.route('/history_plot.png')
        def history_plot_png():
            """
            Liefert ein Matplotlib-PNG für eine Variable (var).
            Standard: letzte 2 Tage, UTC.
            """

            # Welche Variable wollen wir plotten?
            var = request.args.get("var", "temperature_2m")

            # Zeitraum in Tagen
            days = request.args.get("days", "2")
            
            try:
                days = int(days)
            except Exception:
                days = 2

            # Stadt: Aus der Anfrage oder ansonsten self.city nehmen
            city = request.args.get("city")
            
            if city is None or str(city).strip() == "":
                city = self.city

            if city is None or str(city).strip() == "":
                return jsonify({"error": "Keine Stadt gesetzt"}), 400

            # Datum berechnen
            end_date = datetime.now(timezone.utc).date() # Julian Test veraltet: datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)

            # Koordinaten holen
            lat, lon = self.fetch_coordinates(city)

            # DataFrame holen
            df = fetch_openmeteo_history_dataframe(
                lat=lat,
                lon=lon,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )

            # Plot-Beschriftung je nach 'var' (genau wie im Forecast)
            if var == "temperature_2m":
                title = f"Temperatur Vergangenheit: {city}"
                y_label = "°C"
            elif var == "relative_humidity_2m":
                title = f"Luftfeuchte Vergangenheit: {city}"
                y_label = "%"
            elif var == "wind_speed_10m":
                title = f"Windgeschwindigkeit Vergangenheit: {city}"
                y_label = "km/h"
            else:
                title = f"History: {city} ({var})"
                y_label = var

            # Erstellen des Plots
            png = build_single_history_plot_png(df, var, title, y_label)

            if png is None:
                return jsonify({"error": "Keine Plot-Daten für History verfügbar"}), 503

            return send_file(
                BytesIO(png),
                mimetype="image/png",
                as_attachment=False,
                download_name="history.png"
            )

        # Route für die Zukunftsdaten / Forecast
        @self.app.route('/forecast_plot.png')
        def forecast_plot_png():
            """
            Liefert ein Matplotlib-PNG für eine Variable (var).
            Standard: nächste 7 Tage, UTC.
            """

            # Welche Variable wollen wir plotten?
            var = request.args.get("var", "temperature_2m")

            # Zeitraum in Tagen
            days = request.args.get("days", "7")

            try:
                days = int(days)
            except Exception:
                days = 7

            # Begrenzen auf 1...14 Tage
            if days < 1:
                days = 1
            if days > 14:
                days = 14

            # Stadt: Aus der Anfrage oder ansonsten self.city nehmen
            city = request.args.get("city")

            if city is None or str(city).strip() == "":
                city = self.city

            if city is None or str(city).strip() == "":
                return jsonify({"error": "Keine Stadt gesetzt"}), 400

            # Koordinaten holen
            lat, lon = self.fetch_coordinates(city)

            df = fetch_openmeteo_forecast_dataframe(
                lat=lat,
                lon=lon,
                days=days
            )

            # Plot-Beschriftung je nach 'var' (genau wie bei history)
            if var == "temperature_2m":
                title = f"Temperatur Vorhersage: {city}"
                y_label = "°C"
            elif var == "relative_humidity_2m":
                title = f"Luftfeuchte Vorhersage: {city}"
                y_label = "%"
            elif var == "wind_speed_10m":
                title = f"Windgeschwindigkeit Vorhersage: {city}"
                y_label = "km/h"
            else:
                title = f"Forecast: {city} ({var})"
                y_label = var

            # Erstellen des Plots
            png = build_single_forecast_plot_png(df, var, title, y_label)

            if png is None:
                return jsonify({"error": "Keine Plot-Daten für Forecast verfügbar"}), 503
            
            return send_file(
                BytesIO(png),
                mimetype="image/png",
                as_attachment=False,
                download_name="forecast.png"
            )


    # ========================================
    # SOCKET → erhält (neue) Stadt vom Frontend
    # ========================================

    def define_socket_events(self):
        """Registriert alle Socket.IO - Events."""
        
        @self.socketio.on("cityInput")
        def socket_city_input(data):
            """Empfängt eine neue Stadt vom Frontend via Websocket."""

            # ===== 1) EINGABEN ABFANGEN UND PRÜFEN OB O.K. =====

            # Prüfen ob Daten da sind, wenn nicht, leeren Dict nutzen
            if data is None:
                data = {}

            elif not isinstance(data, dict):
                logger.warning(f"cityInput: Unerwarteter Datentyp: {type(data)}")
                data = {}

            # Stadtname aus dem Dict lesen 
            if "city" in data:
                new_city = data["city"]
            else:
                logger.warning("cityInput: Kein 'city' Feld im empfangenen Datenobjekt.")
                new_city = ""
           
            # Wenn Leer oder None new_city, ignorieren...
            if new_city is None: 
                logger.info("cityInput: Leerer Stadtname empfangen, ignoriere Anfrage.")
                return
            
            # ... wenn String, trimmen und prüfen ob leer
            new_city_str = str(new_city).strip() #String erzwingen und trimmen
            if new_city_str == "":
                logger.info("cityInput: Leerer Stadtname empfangen, ignoriere Anfrage.")
                return
            
            # Prüfen, ob die neue Stadt == der aktuellen Stadt ist
            if self.city is not None:
                old_city_str = str(self.city).strip()

                if new_city_str.lower() == old_city_str.lower():
                    logger.debug(f"cityInput: Stadt unverändert: '{new_city_str}'")
                    return
                

            # ===== 2) NEUE STADT versuchen =====

            logger.info(f"🌍 Versuche Stadtwechsel → '{new_city_str}' (vorher: '{self.city}')")
            # VERALTET -> 'self.city = new_city_str' -> J: Nach unten in 3) verschoben weil: Wenn ich die Stadt önder steht oben IMMER ne neue Stadt im Dashboard, die karten und werte werden nur aktualisiert, wenn auch vorhadnen und geprüft.
            # jetzt wird auch oben der Name erst aktualisiert, wenn wirklich eine neue Stadt übernommen wurde

            # Sofort Wetter versuchen abzuholen
            updated_data = self.provider.get_weather_for_city(new_city_str) # hier jetzt new_city_str

            if updated_data is None:
                logger.warning(f"cityInput: Keine Wetterdaten für Stadt '{new_city_str}' gefunden.") # Hier jetzt New City

                # Frontend benachrichtigen, dass Stadt nicht gefunden wurde #ggf. erweitern, falls Frontend in Zukunft mehr "versteht"
                error_payload = {
                    "city": self.city               # Wenn keine neue Stadt (new_city_str) gefunden wieder auf alte zurückfallen                    
                }                    

                self.socketio.emit("update", error_payload)
                return

            # ===== 3) ERFOLG -> STADT ÜBERNEHMEN =====

            logger.info(f"✅ Stadtwechsel erfolgreich: '{self.city}' → '{new_city_str}'") # Erst hier die Stadt wirklich übernommen, wenn sie auch gefunden wurde

            self.city = new_city_str
            self.weather_data = updated_data
            self.last_polled = datetime.now(timezone.utc)   #Vorher Julian: datetime.utcnow()


            # ===== 4) KARTE GENERIEREN =====

            # Neue Koordinaten holen
            lat, lon = self.fetch_coordinates(self.city)

            # Karte generieren mit evtl. aktuellem Temperaturwert
            try:
                current_temp = self.weather_data.get("currentTemperature", "--")
                generate_map.generate_map(lat, lon, temp=current_temp)

            except Exception as e:
                logger.error(f"Fehler beim Generieren der Karte für Stadt '{self.city}': {e}")
                
            

            # ===== 5) FRONTEND BENACHRICHTIGEN =====           
            
            #payload zusammenbauen - ggf. erweitern für Frontend wenn es mehr "versteht"
            payload = {
                "city": self.city,
                "lat": lat,
                "lon": lon
            }

            # Wetterdaten hinzufügen
            for key, value in self.weather_data.items():
                payload[key] = value

            # Live Update an Frontend für Aktualisierung
            self.socketio.emit("update", payload) # J: payload ist das dict mit den Daten


    # ========================================
    # INITIALISIERUNG NACH PARAMETERN
    # ========================================

    def initialize(self, city):
        """
        Initialisiert das Dashboard mit einer Startstadt.

        - setzt self.city
        - lädt initiale Wetterdaten für die Stadt
        - Fällt auf Default zurück, falls Stadt nicht gefunden wurde
        - setzt self.last_polled
        """

        #Stadt-String sauber machen
        if city is None:
            city_clean = ""
        else:
            city_clean = str(city).strip()

        # Wenn kein sinnvoller Stadtname, auf Default setzen
        if city_clean == "":
            logger.info("Initialisierung: Kein Stadtname übergeben, setze auf Default 'Berlin'.")
            city_clean = "Berlin"

        logger.info(f"Initialisiere Dashboard mit Stadt '{city_clean}'.")

        data = self.provider.get_weather_for_city(city_clean)

        # Wenn keine Daten abgerufen wurden und nicht Berlin (Default) verwendet wurde
        if data is None and city_clean.lower() != "berlin":
            logger.warning(f"Initialisierung: Keine Daten für '{city_clean}'. Fallback auf Berlin.")
            city_clean = "Berlin"
            data = self.provider.get_weather_for_city(city_clean)

        # Wenn keine Daten abgerufen wurden und selbst "berlin" nicht funktioniert
        if data is None:
            logger.error(f"Initialisierung fehlgeschlagen: Provider {type(self.provider).__name__} liefert keine Daten.")
            return

        # Dann setzen der internen Variablen
        self.city = city_clean
        self.weather_data = data
        self.last_polled = datetime.now(timezone.utc)   # Test Julian veraltet: datetime.utcnow()

        # Karte erstellen
        lat, lon = self.fetch_coordinates(self.city)
        try:
            current_temp = self.weather_data.get("currentTemperature", "--")
            generate_map.generate_map(lat, lon, temp=current_temp)
        except Exception as e:
            logger.error(f"Fehler beim Generieren der Karte für Stadt '{self.city}': {e}")



    # ========================================
    # HELPER → Koordinaten holen + Map Update
    # ========================================
    def fetch_coordinates(self, city):
        """ 
        Holt die Koordinaten (lat, lon) für eine Stadt über Geopy (Nominatim).
        - ungültige Eingaben wie 'None' oder ein leerer String fallen auf Berlin zurück
        - Bekannte Städte (zuvor aufgerufen) werden aus Cache abgeholt für Laufzeit Optimierung
        - Unbekannte Städte werden über Geopy/Nominatim abgeholt
        - Fehler oder kein Treffer fallen auf Berlin zurück
        """

        # ===== 1) FEHLER ABFANGEN / VALIDATION =====

        # Stadt ist None oder leer, Fallback auf Berlin
        if city is None:
            logger.warning("fetch_coordinates: Stadt ist None, Fallback auf Berlin.")
            return 52.5200, 13.4050

        # Stadt-String trimmen und prüfen ob leer ist 
        city_str = str(city).strip()
        if city_str == "":
            logger.warning("fetch_coordinates: Stadt ist leer, Fallback auf Berlin.")
            return 52.5200, 13.4050 # Berlin

        # ===== 2) CACHE PRÜFEN =====

        cached_geo = city_str.lower()

        if cached_geo in self.geo_cache:
            return self.geo_cache[cached_geo]

        # ===== 3) GEOCODING VERSUCHEN =====
        
        try:
            logger.info(f"fetch_coordinates: Geocoding für Stadt '{city_str}'")
            
            location = self.geolocator.geocode(city_str)

            if location is not None:
                koordinaten = (location.latitude, location.longitude)
                self.geo_cache[cached_geo] = koordinaten   # Aktualisieren des Geo-Caches
                
                return koordinaten
            
            else:
                logger.warning(f"fetch_coordinates: Keine Koordinaten für Stadt '{city_str}' gefunden - Fallback auf Berlin.")

        except Exception as e:
            logger.error(f"fetch_coordinates: Error beim Geocoding von: '{city_str}': {e}")

        # ===== 4) FALLBACK AUF BERLIN =====
        return 52.5200, 13.4050
    


    # ========================================
    # SERVER STARTEN
    # ========================================

    def run(self, host="0.0.0.0", port=5000, city="Berlin"):
        """
        - Hier initialisieren, da nun Parameter bekannt sind
        - Jetzt dürfen Daten geladen werden
        - Vereinfachung für Tests und Debugging
        """

        # Initialisierung mit Startstadt
        self.initialize(city)

        # Loggen der Start-Informationen
        logger.info("🚀 Dashboard läuft → http://127.0.0.1:5000")
        logger.info("📡 Websocket aktiv – UI lädt Live-Daten")

        # Server starten (blockiert, bis Programm beendet wird)
        self.socketio.run(self.app, host=host, port=port)
