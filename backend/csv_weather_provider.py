import pandas as pd

class CSVWeatherProvider:
    def __init__(self, csv_path="weather_sample.csv"):
        self.csv_path = csv_path

    def get_weather_for_city(self, city: str):
        """Liest CSV, filtert nach Stadt und gibt Wetterdaten als Dictionary zurück."""
        df = pd.read_csv(self.csv_path)

        df_city = df[df["CITY"].str.lower() == city.lower()]

        if df_city.empty:
            return None

        row = df_city.iloc[0].to_dict()

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