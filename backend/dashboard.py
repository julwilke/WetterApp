##############################################
#   🌦 WETTER-DASHBOARD – FINAL BACKEND 1.1  #
##############################################

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

        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # CSV Provider 
        self.provider = CSVWeatherProvider("weather_sample.csv")

        # Standard-Stadt beim Start
        self.city = "Berlin"
        self.weather_data = self.provider.get_weather_for_city(self.city)

        self.last_polled = datetime.utcnow()

        self.geolocator = Nominatim(user_agent="weather_dashboard")

        # ========================================
        # ROUTES → Frontend API
        # ========================================

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/weather')
        def weather():
            data = self.provider.get_weather_for_city(self.city)
            if not data:
                return jsonify({"error": "City not found in CSV", "city": self.city})

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
        @self.socketio.on("cityInput")
        def socket_city_input(data):
            new_city = data.get("city")
            if new_city:
                self.city = new_city
                print(f"🌍 Neue Stadt gewählt → {self.city}")

                # Sofort Wetter aktualisieren
                updated = self.provider.get_weather_for_city(self.city)
                if updated:
                    self.weather_data = updated

                # 🌍 Karte NEU GENERIEREN (wichtig!)
                lat, lon = self.fetch_coordinates(self.city)
                generate_map.generate_map(
                    lat, lon,
                    temp=self.weather_data.get("currentTemperature", "--")
                )

                # Live Update an Frontend
                self.socketio.emit("update", {
                    "city": self.city,
                    "lat": lat,
                    "lon": lon,
                    **self.weather_data
                })

    # ========================================
    # HELPER → Koordinaten holen + Map Update
    # ========================================
    def fetch_coordinates(self, city):
        try:
            loc = self.geolocator.geocode(city)
            if loc:
                return loc.latitude, loc.longitude
        except:
            pass
        return 52.5200, 13.4050  # Default Berlin

    # ========================================
    # SERVER STARTEN
    # ========================================
    def run(self, host="0.0.0.0", port=5000):
        print("🚀 Dashboard läuft → http://127.0.0.1:5000")
        print("📡 Websocket aktiv – UI lädt Live-Daten")
        self.socketio.run(self.app, host=host, port=port)
