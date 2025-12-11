###############################################
#   🌦 WETTER-DASHBOARD – BACKEND 1.0.0       #
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
import logging
from datetime import datetime

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

from geopy.geocoders import Nominatim

from backend.provider.csv_weather_provider import CSVWeatherProvider
from backend.services import generate_map

#from services import data_normalizer   # J: aktuell noch nicht hier verwendet
#from venv import logger                # J: Woher kam das?

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

        #Hier passiert...
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Provider auswählen: Entwerder eine der APIs oder Default CSV-Provider nutzen
        if provider is not None:
            self.provider = provider
        else:
            self.provider = CSVWeatherProvider("weather_sample.csv")    

        #Leer initialisieren, setzen in run() bzw. initialize()
        self.city = None                    # Aktuelle Stadt
        self.weather_data = None            # Wetterdaten für die Stadt als dict
        self.last_polled = None             # Zeitpunkt der letzten erfolgreichen Abfrage
        
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
        """Definiert die Routen. Routen werden erst registriert, wenn WeatherDashboard() erstellt wird."""
       
       # Route für den API-Status (Dummy) später evtl. erweitern
        @self.app.route('/status')
        def status():
            """
            Einfache Status-Route für das API-Status-Menü im Frontend.
            Aktuell Dummy: keine echten API-Checks.
            """
            return jsonify({
                "apis": {},
                "lastPolled": datetime.utcnow().isoformat() + "Z"
            })

        # Route für die Hauptseite     
        @self.app.route('/')
        def index():
            return render_template('index.html')

        # Route für Wetterdaten als JSON wenn Frontend diese anfragt
        @self.app.route('/weather')
        def weather():
            """Liefert die aktuellen Wetterdaten für self.city als JSON.
            Nutzt self.weather_data, lädt aber bei jedem Aufruf neu vom Provider.

            Returns:
                _type_: _description_
            """

            # ===== 1) FEHLER ABFANGEN =====

            # Prüfen ob überhaupt eine Stadt gesetzt ist
            if not self.city:
                logger.warning("Request auf /weather ohne definierte Stadt")

                response = {
                    "city": None
                }

                return jsonify(response), 400 # 400 = Bad Request                  
                
            
            # Falls noch keine Daten im Speicher sind, neu laden
            if self.weather_data is None:
                logger.info(f"/weather: Keine Daten im Speicher, lade neu für '{self.city}'.'") 

                # Neu laden          
                data = self.provider.get_weather_for_city(self.city)

                if data is None:
                    logger.warning(f"/weather: Keine Daten für Stadt '{self.city}' gefunden.")

                    response = {
                        "city": self.city
                    }
                    
                    return jsonify(response), 404   # 404 = Not Found
                           
                # Erfolgreich Daten geladen
                self.weather_data = data
                self.last_polled = datetime.utcnow()

            # Koordinaten zur aktuellen Stadt holen - Karte noch nicht generieren hier
            lat, lon = self.fetch_coordinates(self.city)

            response = {                
                "lat": lat,
                "lon": lon,
                "lastPolled": datetime.utcnow().isoformat() + "Z",
            }
            
            # Wetterdaten hinzufügen ins JSON dict
            for key, value in self.weather_data.items():
                response[key] = value

            return jsonify(response)
        



        
    # ========================================
    # SOCKET → erhält (neue) Stadt vom Frontend
    # ========================================

    def define_socket_events(self):
        """Registriert alle Socket.IO - Events."""
        
        @self.socketio.on("cityInput")
        def socket_city_input(data):
            """Empfängt eine neue Stadt vom Frontend via Websocket."""

            # ===== 1) FEHLER ABFANGEN =====

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
                    logger.info(f"cityInput: Stadt '{new_city_str}' ist bereits gesetzt, ignoriere Anfrage.")
                    return
                
            # ===== 2) NEUE STADT ÜBERNEHMEN =====

            logger.info(f"🌍 Neue Stadt gewählt → '{new_city_str}' (vorher: '{self.city}')")
            self.city = new_city_str



            # ===== 3) WETTERDATEN LADEN =====

            # Sofort Wetter aktualisieren
            updated_data = self.provider.get_weather_for_city(self.city)

            if updated_data is None:
                logger.warning(f"cityInput: Keine Wetterdaten für Stadt '{self.city}' gefunden.")

                # Frontend benachrichtigen, dass Stadt nicht gefunden wurde #ggf. erweitern, falls Frontend in Zukunft mehr "versteht"
                error_payload = {
                    "city": self.city                    
                }                    

                self.socketio.emit("update", error_payload)
                return

            # Wenn Daten gefunden wurden, internen Zustand aktualisieren
            self.weather_data = updated_data
            self.last_polled = datetime.utcnow()



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


    #NEU JULIAN 1.0.0 - für das leere initialisieren am Anfang im Konstruktor, jetzt hier die Parameter beschreiben
    #...erst hier wird mit Werten initialisiert


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

        #Falls keine Daten gefunden wurden, auf Default zurückfallen
        if data is None:
            logger.warning(f"Initialisierung: Keine Daten für Stadt '{city_clean}' gefunden. Fallback auf Default 'Berlin'.")
            city_clean = "Berlin"
            data = self.provider.get_weather_for_city(city_clean)

        # Dann setzen der internen Variablen
        self.city = city_clean
        self.weather_data = data
        self.last_polled = datetime.utcnow()

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
        """ Holt die Koordinaten (lat, lon) für eine Stadt über Geopy Nominatim."""

        # Stadt ist None oder leer, Fallback auf Berlin
        if city is None:
            logger.warning("fetch_coordinates: Stadt ist None, Fallback auf Berlin.")
            return 52.5200, 13.4050

        # Stadt-String trimmen und prüfen ob leer ist 
        city_str = str(city).strip()
        if city_str == "":
            logger.warning("fetch_coordinates: Stadt ist leer, Fallback auf Berlin.")
            return 52.5200, 13.4050

        # Geocoding versuchen
        try:
            location = self.geolocator.geocode(city_str)

            if location is not None:
                return location.latitude, location.longitude
            else:
                logger.warning(
                    f"Geocoding: Keine Koordinaten für Stadt '{city_str}' gefunden. "
                    "Fallback auf Berlin."
                )

        except Exception as e:
            logger.error(f"Error geocoding '{city_str}': {e}")

        # Fallback: Koordinaten von Berlin
        return 52.5200, 13.4050
    


    # ========================================
    # SERVER STARTEN
    # ========================================

    def run(self, host="0.0.0.0", port=5000, city="Berlin"): # run() braucht jetzt city als argument (Berlin als DEFAULT) J: warum? warum reicht nicht run()?
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
