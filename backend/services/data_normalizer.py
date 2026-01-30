##############################################
#          DATA NORMALIZER - 1.0.4           #
##############################################

# Normalizer für Wetterdaten. Konvertiert rohe Daten in das vom Dashboard erwartete (immer gleiche) Format. 
# Fehlt ein Wert -> Definierte Default-Werte verwenden.
# Alle Rückgaben sind in nativen Python-Datentypen (keine numpy/pandas Typen) & JSON-serialisierbar.
# Ziel --> Einheitliche Datenstruktur für das Dashboard.
# Bedingung: Eingabedaten sind "flache" dicts, also Einzeiler, keine verschachtelten Strukturen (Daher wird z.B. im API Provider das JSON auch erstmal in ein 'flat_raw'-dict umgebaut)

import numbers

# Hilfsfunktion -> int
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

# Hilfsfunktion -> float
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

# Hilfsfunktion -> String
def _to_str(value, default=""):
    """Konvertiert value in einen str, falls möglich. Andernfalls wird default zurückgegeben."""

    if value is None:
        return default
    return str(value).strip()

# Hilfsfunktion -> Bool
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

# Hauptfunktion zur Normalisierung
def normalize_weather_data(raw: dict) -> dict:
    """
    Nimmt rohe Wetterdaten (z.B. aus CSV oder einer API) und normalisiert:
    - Datentypen (numpy -> Python)
    - fehlende Felder bekommen Defaults
    - Keys werden auf das vom Dashboard erwartete Schema gebracht
    """

    # Stadtname extrahieren
    city = _to_str(raw.get("CITY") or raw.get("city"), default="Unbekannt")

    # Temperatur
    temp = _to_float(
        raw.get("TEMPERATURE") 
        or raw.get("temp") 
        or raw.get("currentTemperature"),
        default=None
    )

    # Min/Max/FeelsLike
    feels_like = _to_float(raw.get("feelsLike"), default=None)
    temp_min = _to_float(raw.get("tempMin"), default=None)
    temp_max = _to_float(raw.get("tempMax"), default=None)

    # Luftfeuchtigkeit, Druck
    humidity = _to_int(raw.get("humidity"), default=None)
    pressure = _to_int(raw.get("pressure"), default=None)

    # Wetterbeschreibung
    weather_desc = _to_str(
        raw.get("weatherDescription") 
        or raw.get("description") 
        or raw.get("weather"),
        default="--"
    )

    # Bewölkungsgrad
    cloud_coverage = _to_int(raw.get("cloudCoverage") or raw.get("clouds"), default=None)

    # Winddaten
    wind_speed = _to_float(raw.get("windSpeed") or raw.get("wind_speed"), default=None)
    wind_gust = _to_float(raw.get("windGust") or raw.get("wind_gust"), default=None)
    wind_dir = _to_int(raw.get("windDirection") or raw.get("wind_deg"), default=None)

    # UV-Index
    uv_index = _to_float(raw.get("uvIndex") or raw.get("uvi"), default=None)

    # Sichtweite
    visibility = _to_int(raw.get("visibility"), default=None)

    # Taupunkt & Luftqualität (Air Quality Index)
    dew_point = _to_float(raw.get("dewPoint"), default=None)
    aqi = _to_int(raw.get("airQualityIndex") or raw.get("aqi"), default=None)

    # Feinstaubwerte
    pm10 = _to_float(raw.get("pm10"), default=None)
    pm2_5 = _to_float(raw.get("pm2_5") or raw.get("pm2.5") or raw.get("pm2_5"), default=None)

    # Gase
    co = _to_float(raw.get("co"), default=None)
    no2 = _to_float(raw.get("no2"), default=None)
    o3 = _to_float(raw.get("o3"), default=None)

    # Sonstige
    pollen = _to_int(raw.get("pollenCount") or raw.get("pollen"), default=None)
    pressure_trend = _to_str(raw.get("pressureTrend"), default="--")
    fog = _to_bool(raw.get("fog"), default=False)

    # Sonnenaufgang/-untergang
    sunrise = _to_str(raw.get("sunrise"), default="08:00")
    sunset = _to_str(raw.get("sunset"), default="18:30")

    # Niederschlag (inkl. Hilfsfunktion pick() siehe unten)
    rain1h = _to_float(pick(raw, "rain1h", "rain_1h"), default=None)
    rain3h = _to_float(pick(raw, "rain3h", "rain_3h"), default=None)
    snow1h = _to_float(pick(raw, "snow1h", "snow_1h"), default=None)
    snow3h = _to_float(pick(raw, "snow3h", "snow_3h"), default=None)

    # Dictionairy final zusammenstellen
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


# Hilfsfunktion um auch 0/0.0 zu akzeptieren
def pick(raw: dict, *keys):
    """
    Hilfsfunktion, da Werte wie 0.0 als "nicht vorhanden" gewertet wurden.
    Hier abgefangen, dass 0 oder 0.0 auch i.O. sind und einfach der erste Vorhandene Wert an der Stelle im dict verwendet wird
    """
    for k in keys:
        if k in raw:
            v = raw[k]

            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue

            return v
        return None
    