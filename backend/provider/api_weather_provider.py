###############################################
# 🌦 API-WEATHER-PROVIDER – OpenWeatherMap
###############################################

"""
Dieser Provider lädt LIVE-Wetterdaten über eine externe API (OpenWeatherMap).

Ziel:
- gleiche Schnittstelle wie CSVWeatherProvider
- austauschbar im WeatherDashboard
- später leicht erweiterbar (Forecast, Air Quality, etc.)
"""

# =============== IMPORTS ====================

import os
import logging
import requests
from datetime import datetime

from backend.services import data_normalizer

# Logger für dieses Modul
logger = logging.getLogger(__name__)

# ============================================
#   API WEATHER PROVIDER
# ============================================

class APIWeatherProvider:
    """
    Ruft Wetterdaten LIVE von OpenWeatherMap ab
    und gibt sie im gleichen Format zurück wie der CSV-Provider.
    """

    def __init__(self, api_key: str = None):
        """
        Initialisiert den APIWeatherProvider.

        Args:
            api_key (str): OpenWeatherMap API-Key
                           Falls None → wird aus ENV gelesen
        """

        # ------------------------------------------------
        # 1️⃣ API-Key laden
        # ------------------------------------------------

        # Falls kein Key übergeben wurde → aus Umgebungsvariable lesen
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")

        if not self.api_key:
            logger.error(
                "❌ Kein OpenWeather API-Key gefunden! "
                "Bitte OPENWEATHER_API_KEY als Umgebungsvariable setzen."
            )

        # ------------------------------------------------
        # 2️⃣ Basis-URL für OpenWeather
        # ------------------------------------------------

        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

        logger.info("🌐 APIWeatherProvider initialisiert")

    # ============================================
    #   HAUPTMETHODE – gleiche Signatur wie CSV
    # ============================================

    def get_weather_for_city(self, city: str):
        """
        Holt aktuelle Wetterdaten für eine Stadt von OpenWeatherMap.

        Args:
            city (str): Stadtname (z.B. 'Berlin')

        Returns:
            dict | None:
                - normalisierte Wetterdaten
                - None, falls Fehler oder Stadt nicht gefunden
        """

        # ---------------------------------------------
        # 1️⃣ Eingabe prüfen
        # ---------------------------------------------

        if city is None or str(city).strip() == "":
            logger.warning("APIWeatherProvider: Leerer Stadtname übergeben.")
            return None

        city_clean = str(city).strip()

        logger.info(f"🌍 API-Abfrage für Stadt: {city_clean}")

        # ---------------------------------------------
        # 2️⃣ Request-Parameter bauen
        # ---------------------------------------------

        params = {
            "q": city_clean,
            "appid": self.api_key,
            "units": "metric",      # Celsius
            "lang": "de"             # Deutsche Wetterbeschreibungen
        }

        # ---------------------------------------------
        # 3️⃣ API-Request ausführen
        # ---------------------------------------------

        try:
            response = requests.get(self.base_url, params=params, timeout=10)

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API-Request fehlgeschlagen: {e}")
            return None

        # ---------------------------------------------
        # 4️⃣ HTTP-Status prüfen
        # ---------------------------------------------

        if response.status_code != 200:
            logger.warning(
                f"⚠️ API lieferte Fehlercode {response.status_code} "
                f"für Stadt '{city_clean}'"
            )
            return None

        # ---------------------------------------------
        # 5️⃣ JSON parsen
        # ---------------------------------------------

        try:
            raw_data = response.json()

            # raw_data (JSON Antwort) "flach" machen in ein-Zeilen-dict, damit data_normalizer es versteht
            flat_raw = {
                "city": raw_data.get("name"),
                "temp": raw_data.get("main", {}).get("temp"),
                "feelsLike": raw_data.get("main", {}).get("feels_like"),
                "tempMin": raw_data.get("main", {}).get("temp_min"),
                "tempMax": raw_data.get("main", {}).get("temp_max"),
                "humidity": raw_data.get("main", {}).get("humidity"),
                "pressure": raw_data.get("main", {}).get("pressure"),
                "weatherDescription": (
                    raw_data.get("weather", [{}])[0].get("description")
                ),
                "wind_speed": raw_data.get("wind", {}).get("speed"),
                "wind_deg": raw_data.get("wind", {}).get("deg"),
                "clouds": raw_data.get("clouds", {}).get("all"),
            }

        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der API-Antwort: {e}")
            return None

        logger.debug(f"RAW API DATA: {raw_data}") # JULIAN TEST

        # ---------------------------------------------
        # 6️⃣ Rohdaten normalisieren
        # ---------------------------------------------
        """
        raw_data ist das originale OpenWeather JSON.
        flat_data ist "abgeflacht"/"einzeilig gemacht" damit es aussieht wie das CSV Sample.
        Wir normalisieren es (genau wie im CSV provider), damit:
        - Frontend IMMER das gleiche Datenformat bekommt
        - CSV & API identisch nutzbar sind
        """ 

        normalized_data = data_normalizer.normalize_weather_data(flat_raw)

        logger.debug(f"NORMALIZED DATA: {normalized_data}") # JULIAN TEST
        # ---------------------------------------------
        # 7️⃣ Metadaten ergänzen
        # ---------------------------------------------

        normalized_data["source"] = "openweather"
        normalized_data["lastUpdated"] = datetime.utcnow().isoformat() + "Z"

        logger.debug(f"NORMALIZED DATA: {normalized_data}") # JULIAN TEST

        logger.info(
            f"✅ Wetterdaten für '{city_clean}' erfolgreich von API geladen."
        )

        # ---------------------------------------------
        # 8️⃣ Rückgabe
        # ---------------------------------------------

        return normalized_data

