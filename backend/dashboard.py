###############################################
#   🌦 WETTER-DASHBOARD – BACKEND 1.0.0       #
###############################################

# =============== IMPORTS ====================
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from datetime import datetime
from backend.csv_weather_provider import CSVWeatherProvider
from geopy.geocoders import Nominatim
from backend import generate_map
import os

# ============================================
#   BACKEND-CORE 
# ============================================
class WeatherDashboard:

    def __init__(self):

        # Frontend-Ordner korrekt setzen
        self.app = Flask(
            __name__,
            template_folder='../weather_dashboard/templates',
            static_folder='../weather_dashboard/static'
        )

        #Hier passiert...
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # CSV Provider #J: Initialisieren, aber noch nicht laden!
        self.provider = CSVWeatherProvider("weather_sample.csv") 

        # Standard-Stadt beim Start noch nicht belegen, das folgt später
        #self.city = "Berlin"
        #self.weather_data = self.provider.get_weather_for_city(self.city)
        #self.last_polled = datetime.utcnow()

        #Leer initialisieren, später belegen
        self.city = None
        self.weather_data = None
        self.last_polled = None
        
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

        @self.app.route('/')
        def index():

            return render_template('index.html')


        @self.app.route('/weather')
        def weather():

            data = self.provider.get_weather_for_city(self.city)
            if not data:
                return jsonify({"❌": "City not found in CSV", "city": self.city})

            # Karte **nicht** hier generieren
            lat, lon = self.fetch_coordinates(self.city)

            return jsonify({
                **data,
                "city": self.city,
                "lat": lat,
                "lon": lon,
                "lastPolled": datetime.utcnow().isoformat() + "Z"
            })

    # ========================================
    # SOCKET → erhält Stadt vom Frontend
    # ========================================
    def define_socket_events(self):

        @self.socketio.on("cityInput")
        def socket_city_input(data):

            new_city = data.get("city")
            
            if not new_city: #Leerer Return falls es dieselbe Stadt ist
                return
            
            #Neue Stad übernehmen
            print(f"🌍 Neue Stadt gewählt → {self.city}")  
            self.city = new_city                            


            # Sofort Wetter aktualisieren
            updated = self.provider.get_weather_for_city(self.city)
            if updated:
                self.weather_data = updated

            # Karte NEU GENERIEREN (wichtig!) / Koordinaten holen
            lat, lon = self.fetch_coordinates(self.city)
            
            generate_map.generate_map(
                lat, lon,
                temp=self.weather_data.get("currentTemperature", "--")
            )

            # Live Update an Frontend für Aktualisierung
            self.socketio.emit("update", {
                "city": self.city,
                "lat": lat,
                "lon": lon,
                **self.weather_data
            })


    #NEU JULIAN 1.0.0 - für das leere initialisieren am Anfang im Konstruktor, jetzt hier die Parameter beschreiben
    #...erst hier wird mit Werten initialisiert
    # ========================================
    # INITIALISIERUNG NACH PARAMETERN
    # ========================================

    def initialize(self, city):

        self.city = city
        self.weather_data = self.provider.get_weather_for_city(city)

        #DEFAULT laden falls Stadt nicht gefunden wurde
        if not self.weather_data:
            print(f"Stadt '{city}' nicht gefunden. Fallback auf Default: Berlin.")
            self.city = 'Berlin'
            self.weather_data = self.provider.get_weather_for_city('Berlin')

        self.last_polled = datetime.utcnow()

    # ========================================
    # HELPER → Koordinaten holen + Map Update
    # ========================================
    def fetch_coordinates(self, city):
        try:
            loc = self.geolocator.geocode(city)
            if loc:
                return loc.latitude, loc.longitude
        except: #J: Hier noch was einfügen?
            pass
        return 52.5200, 13.4050  # Default Berlin

    # ========================================
    # SERVER STARTEN
    # ========================================
    def run(self, host="0.0.0.0", port=5000, city="Berlin"): # run() braucht jertzt city als argument (Berlin als DEFAULT)
        """
        - Hier initialisieren, da nun Parameter bekannt sind
        - Jetzt dürfen Daten geladen werden
        - Vereinfachung für Tests und Debugging
        """

        #HIER WIRD DANN ENDLICH INITIALISIERT!
        self.initialize(city)

        print("🚀 Dashboard läuft → http://127.0.0.1:5000")
        print("📡 Websocket aktiv – UI lädt Live-Daten")
        self.socketio.run(self.app, host=host, port=port)
