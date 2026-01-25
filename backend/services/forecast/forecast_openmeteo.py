##################################################
# FORECAST-PROVIDER – OpenMeteo - 1.0.0
##################################################
import requests
import pandas as pd
import logging

# Logger konfigurieren
logger = logging.getLogger(__name__)

# Funktion
def fetch_openmeteo_forecast_dataframe(lat, lon, days=7):
    """
    Holt Forecast-Daten aus der Open-Meteo Forecast API
    und gibt sie als pandas-DataFrame zurück.

    DataFrame-Spalten:
        time, temperature_2m, relative_humidity_2m, wind_speed_10m
    """

    # ===== 1) FEHLER ABFANGEN =====

    # Sind keine Koordinaten für die Anfrage vorhanden?
    if lat is None or lon is None:
        logger.info("Keine Koordinaten für Vorhersage vorhanden!")
        return None
    
    # Begrenzen auf 1-14 Tage
    if days < 1:
        days = 1

    elif days > 14:
        days = 14

    # ===== 2) ANFRAGE VORBEREITEN =====
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "forecast_days": days,
        "timezone": "UTC"
    } 

    # ===== 3) ANFRAGE SENDEN =====
    try:
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code != 200: # 200 == OK
            logger.info(f"Forecast-Request fehlgeschlagen: status={resp.status_code}")
            return None
        
        raw = resp.json()
        logger.debug(f"Forecast-Daten raw={raw}")

    except Exception:
        logger.info("Anfrage für Forecast-Daten fehlgeschlagen!")
        return None

    # Stundenbasis bilden, bei Fehler return 'None'
    hourly = raw.get("hourly", None)

    if hourly is None:
        return None
    
    # Zeitstempel bilden, bei Fehler return 'None'
    times = hourly.get("time", [])

    if not times:
        return None
    
    # ===== 4) DATAFRAME BILDEN ======
    df = pd.DataFrame({
        "time": pd.to_datetime(times, utc=True),
        "temperature_2m": hourly.get("temperature_2m", []),
        "relative_humidity_2m": hourly.get("relative_humidity_2m", []),
        "wind_speed_10m": hourly.get("wind_speed_10m", []),
    })

    return df