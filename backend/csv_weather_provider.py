###############################################
#   🌦 CSV-WEATHER-PROVIDER – 1.0.0           #
###############################################

# =============== IMPORTS ====================
import pandas as pd
import os               #J: Für Fehlerbehandlung falls die Datei/Pfad nicht gefunden wurde

class CSVWeatherProvider:

    def __init__(self, filename="weather_sample.csv"): #J: Hier nicht den Pfad, sondern den Dateinamen nehmen 'filename'
        
        # Neu hinzugefügt um die Probleme beim verschieben der app.py oder .csv (Pfadprobleme) zu lösen:

        # Ordner, in dem dieses Skript leigt /WetterApp/backend
        base_dir = os.path.dirname(os.path.abspath(__file__))   

        # Project-Root-Pfad ("Überordner") bestimmen
        project_root = os.path.abspath(os.path.join(base_dir, "..")) 

        # /data/samples
        samples_dir = os.path.join(project_root, "data", "samples")

        # FINALER absoluter Pfad zu der CSV-Datei
        self.csv_path = os.path.join(samples_dir, filename)
        self.csv_path = os.path.abspath(self.csv_path)                           

        #Fehler throwen falls nicht gefunden
        if not os.path.exists(self.csv_path):   
            print(f"CSV nicht gefunden!: {self.csv_path}")
        else:
            print(f"CSV geladen aus: {self.csv_path}")


    def get_weather_for_city(self, city: str):
        """Liest CSV, filtert nach Stadt und gibt Wetterdaten als Dictionary zurück."""

        #J: Try Except hinzugefügt falls Pfad nicht gefunden wurde
        try:
            df = pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"CSV konnte nicht geladen werden: {e}")

        # Filtern auf Stadt
        df_city = df[df["CITY"].str.lower() == city.lower()]

        if df_city.empty:
            return None

        row = df_city.iloc[0].to_dict()

        # RETURN inkl. DUMMY Werte für Frontend übergeben bei Bedarf
        return {
            "city": row["CITY"],
            "currentTemperature": row["TEMPERATURE"],
            "feelsLike": row["TEMPERATURE"],      
            "tempMin": row["TEMPERATURE"] - 2,
            "tempMax": row["TEMPERATURE"] + 2,
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
            "fog": False,
        }