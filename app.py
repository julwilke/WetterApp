##############################################
#   🌦 WETTER-DASHBOARD – APP STARTER 1.0.1  #
##############################################

__version__ = "1.0.1"

#Docstring mit Minimalbeschreibung
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
# Im Rest des Programms dann nur noch logger = logging.getLogger(__name__) nutzen und dann...
# z.B. logger.info("Nachricht"), logger.warning("Warnung"), logger.error("Fehler")

from backend.dashboard import WeatherDashboard # J: optimiert für die Lesbarkeit 
from backend.logging_config import configure_logging  #J: Logging Konfiguration importieren
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
    
    # ===== 1) LOGGING KONFIGURIEREN =====
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Wetter-Dashboard Backend v{__version__} startet...")    

    # ===== 2) .ENV DATEI LADEN (API-KEYS ETC.) =====
    load_dotenv() 

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
