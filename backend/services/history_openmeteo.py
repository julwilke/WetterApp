##################################################
# HISTORY-PROVIDER – OpenMeteo - 1.0.0
##################################################
import requests
import pandas as pd


def fetch_openmeteo_history_dataframe(lat, lon, start_date, end_date):
    """
    Holt stündliche History-Daten aus der Open-Meteo Archive API
    und gibt sie als pandas DataFrame zurück.

    DataFrame-Spalten:
      time, temperature_2m, relative_humidity_2m, wind_speed_10m
      (plus optional weitere, aber wir starten bewusst klein)
    """

    if lat is None or lon is None:
        return None

    url = "https://archive-api.open-meteo.com/v1/archive"

    # Wir holen erstmal genau die 3 wichtigsten Werte
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "UTC"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return None
        raw = resp.json()

    except Exception:
        return None

    hourly = raw.get("hourly", None)
    
    if hourly is None:
        return None


    times = hourly.get("time", [])

    if not times:
        return None

    # ====================
    # X) DATAFRAME BILDEN
    # ====================
    df = pd.DataFrame({
        "time": pd.to_datetime(times, utc=True),
        "temperature_2m": hourly.get("temperature_2m", []),
        "relative_humidity_2m": hourly.get("relative_humidity_2m", []),
        "wind_speed_10m": hourly.get("wind_speed_10m", []),
    })

    return df