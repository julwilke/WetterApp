#Hier werden die Daten aus dem API-Call normalisiert, immer im gleichen Schema, damit die WebApp alles richtig anzeigt
#...alle sinnvollen Werte werden rausgezogen, fehlende mit "0" oder "NONE" belegt
#.....Zusätzlich werden fehlende Werte genullt, damit das Frontend keinen Error schmeißt
#........Leere dicts ( {} ) als Ersatzwerte damit das Frontend nihct crasht


# Vielleicht allgemeiner fassen, gibt es einen Weg, dass alle API-Clients funktionieren?

import datetime


def normalize_weather_data(raw: dict, city: str) -> dict:       #Rohdaten als dictionary im .JSON Format (aus OWM) / city-String für Angabe der stadt im OWM-API-Call, spuckt am Ende wieder ein dict im return aus
    """Normalisiert Rohdaten von OpenWeatherMap API in ein einheitliches Format für die WebApp
    """
    main = raw.get("main", {})               #temp, feels_like, temp_min, temp_max, humidity, pressure
    wind = raw.get("wind", {})               #speed, deg, gust
    sys = raw.get("sys", {})                 #sunrise, sunset
    weather = raw.get("weather", [{}])[0]    #Liste(!) weather abrufen, falls sie exisiter, 0'tes Element auswählen
    clouds = raw.get("clouds", {})           #prozentualer Wolkendecken-Wert
    rain = raw.get("rain", {})               #Regen
    snow = raw.get("snow", {})               #Schnee

    #Check ob das Wetter zur Kategorie Nebel enthält
    #IDs für Nebel, Dunst, Nebel
    fog_ids = {701, 721, 741,}              #erstmal rausgenommen: 711=Rauch, 731=Sand/Staubwirbel, 751 = Sand, 761=Staub, 762=Vulkanasche       Wettercodes siehe https://openweathermap.org/weather-conditions (7xx -> Atmosphere)
    fog = weather.get("id") in fog_ids      #Frontend will fog als BOOL, daher wird geprüft, ob die Wetter-ID eine aus der "Fog-Liste" ist und somit fog vorhanden ist

    #Alle Wetterdaten normalisiert return'en als dictionairy / die oberen params kommen aus der main, weil
    return {
        "city": city,

        "currentTemperature": main.get("temp"),
        "feelsLike": main.get("feels_like"),
        "tempMin": main.get("temp_min"),
        "tempMax": main.get("temp_max"),

        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),

        "weatherDescription": weather.get("description"),
        "cloudCoverage": clouds.get("all", 0),              #0 als DEFAULT, falls keine Wolken vorhanden, dann 0% Wolken

        "rain1h": rain.get("1h", 0),                        #0 als DEFAULT, da OWM Regen nur sendet, wenn auch welcher vorhanden war
        "rain3h": rain.get("3h", 0),                        #...

        "snow1h": snow.get("1h", 0),                        #0 als DEFAULT, da OWM Schnee nur sendet, wenn auch welcher vorhanden war
        "snow3h": snow.get("3h", 0),                        #...

        "windSpeed": wind.get("speed"),
        "windGust": wind.get("gust"),
        "windDirection": wind.get("deg"),

        "sunrise": sys.get("sunrise"),
        "sunset": sys.get("sunset"),

        "visibility": raw.get("visibility"),

        # Diese Werte hat Nick bereits im Frontend angelegt, aber unsere API scheint sie nicht zu liefern, daher lieber NONE belegen, als einen Error o.ä. zu schmeißen
        # wenn wir gute APIs finden, dann die Werte hier stattdessen füllen
        "dewPoint": None,
        "uvIndex": None,

        #Diese Werte stammen wahrscheinlich aus der Air_Pollution API von OWM, das ist aber nicht die die Adham abgerufen hat
        #...daher erstmal alle auf None setzen, bis wir ne "Füllung" haben
        "airQualityIndex": None,
        "pm10": None,
        "pm2_5": None,
        "co": None,
        "no2": None,
        "o3": None,

        "pollenCount": None,
        "pressureTrend": "stabil", # --> später ggf. eigenen Trend berechnen
        "fog": fog,
    }


#Ideen: 

@staticmethod
def air_quality_normalizer():
   if not raw or 'list' not in raw:
            return {}
        components = raw['list'][0]. get('components', {})
        aqi = raw['list'][0].get('main', {}).get('aqi', 0)
        
        return {
            'airQualityIndex': aqi,
            'pm10': components.get('pm10', 0),
            'pm2_5': components.get('pm2_5', 0),
            'co': components.get('co', 0),
            'no2': components.get('no2', 0),
            'o3': components.get('o3', 0),
        }


@staticmethod
def timestamp_to_iso(timestamp):
    """Konvertiert Unix-Timestamp in ISO 8601 Format"""
    if timestamp is None:
        return None
    return datetime.utcfromtimestamp(timestamp).isoformat()