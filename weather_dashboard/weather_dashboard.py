from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import os
from datetime import datetime
from geopy.geocoders import Nominatim
import generate_map

class WeatherDashboard:
    """
    WeatherDashboard: Flask + SocketIO wrapper that serves the dashboard
    """

    def __init__(self, template_folder='templates', static_folder='static'):
        self.app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.weather_data = self._create_test_data()
        self.city = 'Iserlohn'
        self.last_polled = datetime.utcnow()

        # Geolocator für City→Koordinaten
        self.geolocator = Nominatim(user_agent="weather_dashboard")

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/weather')
        def weather():
            self.last_polled = datetime.utcnow()
            payload = {**self.weather_data, 'city': self.city}
            return jsonify(payload)

        @self.app.route('/status')
        def status():
            iso = self.last_polled.isoformat() + 'Z'
            return jsonify({
                'status': 'ok',
                'lastPolled': iso,
                'apis': {
                    'openweather': {'status':'ok','lastPolled':iso},
                    'meteor': {'status':'ok','lastPolled':iso}
                }
            })

        # -----------------------------------------------
        #  FRONTEND → Backend: Stadt erhalten
        # -----------------------------------------------
        @self.socketio.on('cityInput')
        def handle_city_input(data):
            city = data.get('city', '')
            if city:
                print(f"City empfangen: {city}")
                self.city = city

                # *** TEST-FUNKTION: Koordinaten holen ***
                self.fetch_city_coordinates(city)

                # An alle Clients senden
                self.socketio.emit('update', {'city': self.city})
                self.socketio.emit('update', {**self.weather_data, 'city': self.city})


    # ---------------------------------------------------
    #  TEST-FUNKTION: City → Koordinaten
    # ---------------------------------------------------
    def fetch_city_coordinates(self, city):
        query = city

        try:
            location = self.geolocator.geocode(query)
            if location:
                self.weather_data["lat"] = location.latitude
                self.weather_data["lon"] = location.longitude
                print(f"Koordinaten für {city}: {location.latitude}, {location.longitude}")
                print(location.latitude, location.longitude)
                generate_map.generate_map(location.latitude, location.longitude, temp=self.weather_data.get("currentTemperature", "--"))
            else:
                print(f"Keine Koordinaten gefunden für: {city}")
                # Fallback: Berlin als Default
                self.weather_data["lat"] = 52.5200
                self.weather_data["lon"] = 13.4050
        except Exception as e:
            print(f"Fehler beim Geocoding: {e}")
            # Default-Koordinaten
            self.weather_data["lat"] = 52.5200
            self.weather_data["lon"] = 13.4050
        
    def _create_test_data(self):
        return {
            "city": "Berlin",
            "currentTemperature": 21.2,
            "currentTemperature_history": [
                {"hr": -4, "value": 18.3},
                {"hr": -3, "value": 17.7},
                {"hr": -2, "value": 19.5},
                {"hr": -1, "value": 21.6},
            ],
            "feelsLike": 21.0,
            "feelsLike_history": [
                {"hr": -4, "value": 17.0},
                {"hr": -3, "value": 18.5},
                {"hr": -2, "value": 16.2},
                {"hr": -1, "value": 20.3},
            ],
            "tempMin": 15.4,
            "tempMin_history": [
                {"hr": -4, "value": 14.8},
                {"hr": -3, "value": 12.0},
                {"hr": -2, "value": 15.1},
                {"hr": -1, "value": 17.3},
            ],
            "tempMax": 25.6,
            "tempMax_history": [
                {"hr": -4, "value": 25.1},
                {"hr": -3, "value": 21.0},
                {"hr": -2, "value": 23.2},
                {"hr": -1, "value": 25.0},
            ],
            "humidity": 52,
            "humidity_history": [
                {"hr": -4, "value": 55},
                {"hr": -3, "value": 63},
                {"hr": -2, "value": 51},
                {"hr": -1, "value": 30},
            ],
            "lat": 52.5200,
            "lon": 13.4050,
            "pressure": 1015,
            "pressure_history": [
                {"hr": -4, "value": 1012},
                {"hr": -3, "value": 1011},
                {"hr": -2, "value": 1013},
                {"hr": -1, "value": 1012},
            ],
            "weatherDescription": "leicht bewölkt",
            "cloudCoverage": 20,
            "rain1h": 0,
            "rain3h": 0,
            "snow1h": 0,
            "snow3h": 0,
            "windSpeed": 6,
            "windSpeed_history": [
                {"hr": -4, "value": 5.4},
                {"hr": -3, "value": 2.3},
                {"hr": -2, "value": 5.5},
                {"hr": -1, "value": 7.1},
            ],
            "windDirection": 110,
            "uvIndex": 4,
            "sunrise": "06:32",
            "sunset": "18:45",
            "visibility": 10000,
            "dewPoint": 11,
            "airQualityIndex": 45,
            "pm10": 18,
            "pm2_5": 12,
            "co": 0.4,
            "no2": 20,
            "o3": 35,
            "pollenCount": 5,
            "pressureTrend": "leicht steigend",
            "fog": False
        }

    def update_variable(self, var, val):
        if var in self.weather_data:
            if isinstance(self.weather_data[var], bool):
                self.weather_data[var] = val.lower() in ["true", "1", "yes"]
            else:
                self.weather_data[var] = type(self.weather_data[var])(val)
            print(f"{var} aktualisiert: {self.weather_data[var]}")

            # Komplette Wetterdaten an alle Clients senden
            self.socketio.emit('update', {**self.weather_data, 'city': self.city})
        else:
            print(f"Variable '{var}' existiert nicht.")

    def start_console(self):
        print("Konsole gestartet. 'exit' zum Beenden")
        while True:
            var = input("Variablenname: ")
            if var.lower() == "exit":
                break
            val = input(f"Wert für '{var}': ")
            self.update_variable(var, val)

    def run(self, host='0.0.0.0', port=5000):
        threading.Thread(target=lambda: self.socketio.run(self.app, host=host, port=port), daemon=True).start()
        if os.environ.get('NO_CONSOLE') in [None, '', '0']:
            self.start_console()
