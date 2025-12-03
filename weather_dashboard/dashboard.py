from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import os
from datetime import datetime
from backend.csv_weather_provider import CSVWeatherProvider

class WeatherDashboard:

    def __init__(self, template_folder='templates', static_folder='static'):
        self.app = Flask(__name__,
                         template_folder=template_folder,
                         static_folder=static_folder)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # CSV provider
        self.provider = CSVWeatherProvider(csv_path="weather_sample.csv")

        # Default city
        self.city = "Berlin"
        self.weather_data = self.provider.get_weather_for_city(self.city)

        self.last_polled = datetime.utcnow()

        # -------------------------------------------------------
        # ROUTES
        # -------------------------------------------------------

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/weather')
        def weather():
            """Return current weather as JSON"""

            data = self.provider.get_weather_for_city(self.city)
            print("CSV-Daten:", data)
            if data is None:
                return jsonify({"error": "City not found in CSV", "city": self.city})

            # zeitstempel ergänzen
            response = {

                **data,
                "city": self.city,
                "lastPolled": datetime.utcnow().isoformat() + "Z"
            } 
            return jsonify(response)

        @self.app.route('/status')
        def status():
            iso = self.last_polled.isoformat() + "Z"
            return jsonify({
                "status": "ok",
                "lastPolled": iso,
                "apis": {
                    "csv": {"status": "ok", "lastPolled": iso}
                }
            })

        # -------------------------------------------------------
        # SOCKET.IO EVENTS
        # -------------------------------------------------------

        @self.socketio.on("cityInput")
        def socket_city_input(data):
            city = data.get("city", "")
            if city:
                self.city = city
                print(f"Neue Stadt empfangen: {self.city}")
                self.socketio.emit("update", {"city": self.city})

    # -------------------------------------------------------
    # SERVER START
    # -------------------------------------------------------

    def run(self, host='0.0.0.0', port=5000):
        print("Server gestartet")
        self.socketio.run(self.app, host=host, port=port)


# Starten, wenn Datei direkt ausgeführt wird
if __name__ == "__main__":
    WeatherDashboard().run()