##############################################
#          DATA NORMALIZER - 1.0.2           #
##############################################

# Normalizer für Wetterdaten. Konvertiert rohe Daten in das vom Dashboard erwartete (immer gleiche) Format. 
# Fehlt ein Wert -> Definierte Default-Werte verwenden.
# Alle Rückgaben sind in nativen Python-Datentypen (keine numpy/pandas Typen) & JSON-serialisierbar.
# Ziel --> Einheitliche Datenstruktur für das Dashboard.
# Bedingung: Eingabedaten sind "flache" dicts, also Einzeiler, keine verschachtelten Strukturen (Daher wird z.B. im API Provider das JSON auch erstmal in ein 'flat_raw'-dict umgebaut)

import numbers

def _to_int(value, default=None):
    """Konvertiert value in einen int, falls möglich. Andernfalls wird default zurückgegeben."""

    if value is None:
        return default
    
    # Numeric-Typen (int, float, numpy, pandas,...)
    if isinstance(value, numbers.Number):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
        
    # String -> int
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return default
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default
    return default


def _to_float(value, default=None):
    """Konvertiert value in einen float, falls möglich. Andernfalls wird default zurückgegeben."""

    if value is None:
        return default
    
    if isinstance(value, numbers.Number):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
        
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    return default


def _to_str(value, default=""):
    """Konvertiert value in einen str, falls möglich. Andernfalls wird default zurückgegeben."""

    if value is None:
        return default
    return str(value).strip()


def _to_bool(value, default=False):
    """Konvertiert value in einen bool, falls möglich. Andernfalls wird default zurückgegeben."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "1", "yes", "y"):
            return True
        if v in ("false", "0", "no", "n"):
            return False
    if isinstance(value, numbers.Number):
        return bool(value)
    return default


def normalize_weather_data(raw: dict) -> dict:
    """
    Nimmt rohe Wetterdaten (z.B. aus CSV oder einer API) und normalisiert:
    - Datentypen (numpy -> Python)
    - fehlende Felder bekommen Defaults
    - Keys werden auf das vom Dashboard erwartete Schema gebracht
    """

    # Stadtname extrahieren
    city = _to_str(raw.get("CITY") or raw.get("city"), default="Unbekannt")

    # Temperaturen
    temp = _to_float(
        raw.get("TEMPERATURE") 
        or raw.get("temp") 
        or raw.get("currentTemperature"),
        default=None
    )

    # Min/Max/FeelsLike , default basierend auf temp
    feels_like = _to_float(raw.get("feelsLike"), default=temp)
    temp_min = _to_float(raw.get("tempMin"), default=(temp - 2 if temp is not None else None))
    temp_max = _to_float(raw.get("tempMax"), default=(temp + 2 if temp is not None else None))

    # Luftfeuchtigkeit, Druck
    humidity = _to_int(raw.get("humidity"), default=50)
    pressure = _to_int(raw.get("pressure"), default=1013)

    # Wetterbeschreibung
    weather_desc = _to_str(
        raw.get("weatherDescription") 
        or raw.get("description") 
        or raw.get("weather"),
        default="klar"
    )

    # Bewölkungsgrad
    cloud_coverage = _to_int(raw.get("cloudCoverage") or raw.get("clouds"), default=0)

    # Winddaten
    wind_speed = _to_float(raw.get("windSpeed") or raw.get("wind_speed"), default=5.0)
    wind_gust = _to_float(raw.get("windGust") or raw.get("wind_gust"), default=7.0)
    wind_dir = _to_int(raw.get("windDirection") or raw.get("wind_deg"), default=90)

    # UV-Index
    uv_index = _to_float(raw.get("uvIndex") or raw.get("uvi"), default=3.0)

    # Sichtweite
    visibility = _to_int(raw.get("visibility"), default=10000)

    # Taupunkt & Luftqualität (Air Quality Index)
    dew_point = _to_float(raw.get("dewPoint"), default=10.0)
    aqi = _to_int(raw.get("airQualityIndex") or raw.get("aqi"), default=50)

    # Feinstaubwerte
    pm10 = _to_float(raw.get("pm10"), default=20.0)
    pm2_5 = _to_float(raw.get("pm2_5") or raw.get("pm2.5") or raw.get("pm2_5"), default=10.0)

    # Gase
    co = _to_float(raw.get("co"), default=0.3)
    no2 = _to_float(raw.get("no2"), default=15.0)
    o3 = _to_float(raw.get("o3"), default=40.0)

    # Sonstige
    pollen = _to_int(raw.get("pollenCount") or raw.get("pollen"), default=0)
    pressure_trend = _to_str(raw.get("pressureTrend"), default="stabil")
    fog = _to_bool(raw.get("fog"), default=False)

    # Sonnenaufgang/-untergang
    sunrise = _to_str(raw.get("sunrise"), default="06:30")
    sunset = _to_str(raw.get("sunset"), default="18:30")

    # Niederschlag
    rain1h = _to_float(raw.get("rain1h") or raw.get("rain_1h"), default=0.0)
    rain3h = _to_float(raw.get("rain3h") or raw.get("rain_3h"), default=0.0)
    snow1h = _to_float(raw.get("snow1h") or raw.get("snow_1h"), default=0.0)
    snow3h = _to_float(raw.get("snow3h") or raw.get("snow_3h"), default=0.0)

    # Dictionairy Final zusammenstellen
    normalized_data = {
        "city": city,
        "currentTemperature": temp,
        "feelsLike": feels_like,
        "tempMin": temp_min,
        "tempMax": temp_max,
        "humidity": humidity,
        "pressure": pressure,
        "weatherDescription": weather_desc,
        "cloudCoverage": cloud_coverage,
        "rain1h": rain1h,
        "rain3h": rain3h,
        "snow1h": snow1h,
        "snow3h": snow3h,
        "windSpeed": wind_speed,
        "windGust": wind_gust,
        "windDirection": wind_dir,
        "uvIndex": uv_index,
        "sunrise": sunrise,
        "sunset": sunset,
        "visibility": visibility,
        "dewPoint": dew_point,
        "airQualityIndex": aqi,
        "pm10": pm10,
        "pm2_5": pm2_5,
        "co": co,
        "no2": no2,
        "o3": o3,
        "pollenCount": pollen,
        "pressureTrend": pressure_trend,
        "fog": fog,
    }

    # Rückgabe des normalisierten Datensatzes für das Dashboard
    return normalized_data        
    