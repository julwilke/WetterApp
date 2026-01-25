##################################################
# HISTORY-PROVIDER – OpenMeteo - 1.0.1
##################################################
import requests
import pandas as pd
import logging

# Logger konfigurieren 
logger = logging.getLogger(__name__)

# Funktion
def fetch_openmeteo_history_dataframe(lat, lon, start_date, end_date):
    """
    Holt stündliche History-Daten aus der Open-Meteo Archive API
    und gibt sie als pandas-DataFrame zurück.

    DataFrame-Spalten:
      time, temperature_2m, relative_humidity_2m, wind_speed_10m
    """

    # ===== 1) FEHLER ABFANGEN =====

    # Sind keine Koordinaten für die Anfrage vorhanden?
    if lat is None or lon is None:
        logger.info("Keine Koordinaten für historische Daten vorhanden!")
        return None

    # ===== 2) ANFRAGE VORBEREITEN =====
    url = "https://archive-api.open-meteo.com/v1/archive"

    # Abgeholt werden ["temperature_2m,relative_humidity_2m,wind_speed_10m"]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "UTC"
    }

    # ===== 3) ANFRAGE SENDEN =====
    try:
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code != 200: # 200 == OK
            logger.info(f"History-Request fehlgeschlagen: status={resp.status_code}")
            return None
        
        raw = resp.json()
        logger.debug(f"Histroy-Daten raw={raw}")

    except Exception:
        logger.info("Anfrage für historische Daten fehlgeschlagen!")
        return None

    # Stundenbasis bilden, bei Fehler return 'None'
    hourly = raw.get("hourly", None)
    
    if hourly is None:
        return None

    # Zeitstempel bilden, bei Fehler return 'None'
    times = hourly.get("time", [])

    if not times:
        return None


    # ===== 4) DATAFRAME BILDEN =====
    df = pd.DataFrame({
        "time": pd.to_datetime(times, utc=True),
        "temperature_2m": hourly.get("temperature_2m", []),
        "relative_humidity_2m": hourly.get("relative_humidity_2m", []),
        "wind_speed_10m": hourly.get("wind_speed_10m", []),
    })

    return df