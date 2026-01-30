##############################################
#   🌦 WETTER-DASHBOARD – APP STARTER 1.0.5  #
##############################################

__version__ = "1.0.5"

"""
WetterApp - Backend Entry Point
--------------------------------
Initialisiert:
- Logging konfiguration
- Environment Variablen laden aus .env Datei
- Weather-Provider aus .env auswählen (CSV oder API/OpenWeather)
- Dashboard Backend starten
"""

# =============== IMPORTS ====================
             
import logging
import os

from dotenv import load_dotenv

from backend.dashboard import WeatherDashboard 
from backend.logging_config import configure_logging

from backend.provider.csv_weather_provider import CSVWeatherProvider
from backend.provider.api_weather_provider import APIWeatherProvider


# ============================================
#  1) HAUPT-FUNKTION - main-Boot-Sequenz
# ============================================
def main():
    """
    Startet das Wetter-Dashboard Backend.
    Erstellt eine Instanz von WeatherDashboard und startet den Server.
    """
    
    # ===== 1) .ENV DATEI LADEN (API-KEYS ETC.) =====
    load_dotenv() 


    # ===== 2) LOGGING STARTEN UND STARTKONTEXT LOGGEN =====
    configure_logging()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Wetter-Dashboard Backend v{__version__} startet...") 

    # Startkontext loggen
    logger.info("WEATHER_PROVIDER =%s ", os.getenv("WEATHER_PROVIDER", "not set"))
    logger.info("LOG_LEVEL = %s", os.getenv("LOG_LEVEL", "INFO"))
    


    # ===== 3) WEATHER PROVIDER INITIALISIEREN =====
    provider_mode = os.getenv("WEATHER_PROVIDER", "csv").lower()
    api_key = os.getenv("OPENWEATHER_API_KEY")

    # Prüfen ob API gewählt UND ein Key vorhanden ist, sonst Fallback auf CSV
    if provider_mode in ("api", "openweather") and api_key:
        provider = APIWeatherProvider(api_key = api_key)
    else:
        provider = CSVWeatherProvider("weather_sample.csv")



    # ===== 4) DASHBOARD BACKEND INITIALISIEREN UND STARTEN =====
    app = WeatherDashboard(provider = provider)             # Initialsieren
    app.run(city="Berlin")                                  # Server starten             
        

# ============================================
#   ===== SCRIPT START (Entry-Point) =====
# ============================================
if __name__ == "__main__":
    main()  # Hauptfunktion ausführen

