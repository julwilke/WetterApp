from flask import Flask, render_template
from flask_socketio import SocketIO
import threading

class WeatherDashboard:
    def __init__(self, template_folder='templates', static_folder='static'):
        self.app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.weather_data = self._create_test_data()

        @self.app.route('/')
        def index():
            return render_template('index.html')

    def _create_test_data(self):
        return {
            "currentTemperature": 20,
            "feelsLike": 20,
            "tempMin": 15,
            "tempMax": 25,
            "humidity": 50,
            "pressure": 1013,
            "weatherDescription": "klar",
            "cloudCoverage": 0,
            "rain1h": 0,
            "rain3h": 0,
            "snow1h": 0,
            "snow3h": 0,
            "windSpeed": 5,
            "windGust": 7,
            "windDirection": 90,
            "uvIndex": 3,
            "sunrise": "06:30",
            "sunset": "18:30",
            "visibility": 10000,
            "dewPoint": 10,
            "airQualityIndex": 50,
            "pm10": 20,
            "pm2_5": 10,
            "co": 0.3,
            "no2": 15,
            "o3": 40,
            "pollenCount": 0,
            "pressureTrend": "stabil",
            "fog": False
        }

    def update_variable(self, var, val):
        if var in self.weather_data:
            if isinstance(self.weather_data[var], bool):
                self.weather_data[var] = val.lower() in ["true", "1", "yes"]
            else:
                self.weather_data[var] = type(self.weather_data[var])(val)
            print(f"{var} aktualisiert: {self.weather_data[var]}")
            # Push an Frontend
            self.socketio.emit('update', {var: self.weather_data[var]})
        else:
            print(f"Variable '{var}' existiert nicht.")

    def start_console(self):
        print("Konsole für Wetterdaten-Änderungen gestartet. 'exit' zum Beenden")
        while True:
            var = input("Variablenname eingeben: ")
            if var.lower() == "exit":
                break
            val = input(f"Wert für '{var}' eingeben: ")
            self.update_variable(var, val)

    def run(self, host='0.0.0.0', port=5000):
        threading.Thread(target=lambda: self.socketio.run(self.app, host=host, port=port), daemon=True).start()
        self.start_console()
