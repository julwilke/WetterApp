###############################################
#   🌦 API-WEATHER-PROVIDER – 1.0.0           #
###############################################

# IMPORTS
import logging
import os

from dotenv import load_dotenv

from backend.services import data_normalizer

# Logger-Konfiguration
logger = logging.getLogger(__name__)

# .env Datei laden
load_dotenv()

# Klasse zur Bereitstellung von Wetterdaten über eine API
class APIWeatherProvider:
    """
    Platzhalter für einen API-basierten Wetter-Provider.

    TODO:
    - In __init__ API-Key und Basis-URL setzen
    - In get_weather_for_city einen echten HTTP-Request an die Wetter-API senden
    - API-JSON auf ein "raw"-Dict mappen, das normalize_weather_data versteht
    """
    # Initialisierer / Konstruktor
    def __init__(self, api_key) -> None:
        """
        Initialisiert den API-Provider.

        Args:
            api_key: API-Key für den genutzten Wetterdienst.
                     Kann später auch aus der .env / Umgebungsvariable gelesen werden.
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")     # Entweder beim Aufruf übergebener Key oder aus .env
        # TODO: Hier später z.B. Basis-URL und weitere Einstellungen setzen.
        # z.B.:   # self.base_url = "url der wetter api"

    def get_weather_for_city(self, city: str) -> dict:      # Gleicher Rückgabetyp wie CSVWeatherProvider!!!
        """
        Holt die Wetterdaten für eine gegebene Stadt über die API.

        Args:
            city: Name der Stadt, für die die Wetterdaten abgerufen werden sollen.

        Returns:
            Ein normalisiertes Dict mit den Wetterdaten der Stadt.
        """

        return None