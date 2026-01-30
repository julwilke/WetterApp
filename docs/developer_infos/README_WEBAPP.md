# README zum Dashboard / Frontend

## Stadeingabe

| Anzeigename              | Variablenname        |
| ------------------------ | -------------------- |
| Stadt                    | `city`               |

## Wetterdaten (vom Backend an das Frontend übergeben)

Die folgenden Variablen werden aktuell vom Backend an das Frontend übergeben und im Dashboard angezeigt. Die Spalte JSON-Feldname gibt an, aus welchem OpenWeatherMap-Feld (oder vergleichbaren Quellen) der Wert üblicherweise kommt.

| Anzeigename              | Variablenname        | JSON-Feldname / API      | Einheit / Beschreibung                              | Quelle                           |
| ------------------------ | -------------------- | ------------------------ | --------------------------------------------------- | -------------------------------- |
| Stadt                    | `city`               | –                        | Anzeigename / Query-String                           | Backend                           |
| Aktuelle Temperatur      | `currentTemperature` | `main.temp`              | °C                                                  | OpenWeatherMap / Backend         |
| Gefühlt wie              | `feelsLike`          | `main.feels_like`        | °C                                                  | OpenWeatherMap / Backend         |
| Minimum Temperatur       | `tempMin`            | `main.temp_min`          | °C                                                  | OpenWeatherMap / Backend         |
| Maximum Temperatur       | `tempMax`            | `main.temp_max`          | °C                                                  | OpenWeatherMap / Backend         |
| Luftfeuchtigkeit         | `humidity`           | `main.humidity`          | %                                                   | OpenWeatherMap / Backend         |
| Luftdruck                | `pressure`           | `main.pressure`          | hPa                                                 | OpenWeatherMap / Backend         |
| Wetterbeschreibung       | `weatherDescription` | `weather[0].description` | Text                                                | OpenWeatherMap / Backend         |
| Wolkenbedeckung          | `cloudCoverage`      | `clouds.all`             | %                                                   | OpenWeatherMap / Backend         |
| Niederschlag (1h)        | `rain1h`             | `rain.1h`                | mm                                                  | OpenWeatherMap / Backend         |
| Niederschlag (3h)        | `rain3h`             | `rain.3h`                | mm                                                  | OpenWeatherMap / Backend         |
| Schnee (1h)              | `snow1h`             | `snow.1h`                | mm                                                  | OpenWeatherMap / Backend         |
| Schnee (3h)              | `snow3h`             | `snow.3h`                | mm                                                  | OpenWeatherMap / Backend         |
| Windgeschwindigkeit      | `windSpeed`          | `wind.speed`             | km/h (oder m/s, je nach Umrechnung)                 | OpenWeatherMap / Backend         |
| Windböen                 | `windGust`           | `wind.gust`              | km/h (oder m/s, je nach Umrechnung)                 | OpenWeatherMap / Backend         |
| Windrichtung             | `windDirection`      | `wind.deg`               | °                                                   | OpenWeatherMap / Backend         |
| UV-Index                 | `uvIndex`            | `uvi`                    | Index                                               | OpenWeatherMap / Backend         |
| Sonnenaufgang            | `sunrise`            | `sys.sunrise`            | Uhrzeit oder Timestamp (je nach Implementierung)    | OpenWeatherMap / Backend         |
| Sonnenuntergang          | `sunset`             | `sys.sunset`             | Uhrzeit oder Timestamp (je nach Implementierung)    | OpenWeatherMap / Backend         |
| Sichtweite               | `visibility`         | `visibility`             | m                                                   | OpenWeatherMap / Backend         |
| Taupunkt                 | `dewPoint`           | `main.dew_point`*        | °C (optional, ggf. aus Temp+Feuchtigkeit berechnen) | OpenWeatherMap / Backend         |
| Luftqualitätsindex       | `airQualityIndex`    | `aqi`                    | Index                                               | Air-Pollution API / Backend      |
| PM10                     | `pm10`               | `components.pm10`        | µg/m³                                               | Air-Pollution API / Backend      |
| PM2.5                    | `pm2_5`              | `components.pm2_5`       | µg/m³                                               | Air-Pollution API / Backend      |
| CO                       | `co`                 | `components.co`          | µg/m³ or ppm (API abhängig)                         | Air-Pollution API / Backend      |
| NO2                      | `no2`                | `components.no2`         | µg/m³                                               | Air-Pollution API / Backend      |
| O3                       | `o3`                 | `components.o3`          | µg/m³                                               | Air-Pollution API / Backend      |
| Pollen (optional)        | `pollenCount`        | `pollen`                 | Anzahl pro m³ (API abhängig)                        | Pollen API / Backend             |
| Luftdrucktrend           | `pressureTrend`      | berechnet / custom       | steigend/fallend                                    | Backend (berechnet)              |
| Nebel / Sichtbehinderung | `fog` / `mist`       | `weather[0].id`          | anhand ID interpretieren                            | OpenWeatherMap / Backend         |

## Status API

| Endpoint | Rückgabe-Felder | Beschreibung |
| -------- | --------------- | ------------ |
| `/status` | `status` (z. B. `ok`), `lastPolled` (ISO 8601 UTC Zeitstempel) | Liefert einen kleinen Status-Block, der vom Frontend verwendet wird, um Online/Offline-Zustand und die letzte Abfragezeit darzustellen. |

Zusätzlich liefert `/status` nun auch ein Objekt `apis`, in dem pro konfigurierter API der Status und `lastPolled` enthalten sind.

Beispiel:

```json
{
  "status": "ok",
  "lastPolled": "2025-11-28T10:41:40.808938Z",
  "apis": {
    "openweather": { "status": "ok", "lastPolled": "2025-11-28T10:41:40.808938Z" },
    "meteor": { "status": "error", "lastPolled": "2025-11-28T08:12:32.000000Z" }
 }
}
```

Hinweis: `lastPolled` wird in der UI als relative Zeit dargestellt (z. B. `45s`, `4m`, `2std`, `3d`).

## Beispiel JSON für `/weather`

Das Backend liefert typischerweise ein JSON mit allen sichtbaren Feldern für das Dashboard. Hier ein Beispiel (vereinfachte Ausgabe mit Testwerten):

```json
{
  "city": "Berlin",
  "currentTemperature": 20.0,
  "currentTemperature_history": [
    { "hr": -4, "value": 18 },
        { "hr": -3, "value": 18.5 },
        { "hr": -2, "value": 19 },
        { "hr": -1, "value": 19.5 },
  ],                                            // Neu
  "feelsLike": 20.0,
  "feelsLike_history": [
    { "hr": -4, "value": 18 },
        { "hr": -3, "value": 18.5 },
        { "hr": -2, "value": 19 },
        { "hr": -1, "value": 19.5 },
  ],                                            // Neu
  "tempMin": 15.0,
  "tempMin_history":  [
    { "hr": -4, "value": 18 },
        { "hr": -3, "value": 18.5 },
        { "hr": -2, "value": 19 },
        { "hr": -1, "value": 19.5 },
  ],                                            // Neu
  "tempMax": 25.0,
  "tempMax_history":  [
    { "hr": -4, "value": 18 },
        { "hr": -3, "value": 18.5 },
        { "hr": -2, "value": 19 },
        { "hr": -1, "value": 19.5 },
  ],                                            // Neu
  "humidity": 50,
  "humidity_history":  [
    { "hr": -4, "value": 18 },
        { "hr": -3, "value": 18.5 },
        { "hr": -2, "value": 19 },
        { "hr": -1, "value": 19.5 },
  ],                                            // Neu
  "lat": 51.43779,                              // aus der fetch_city_coordinates
  "lon": 7.7953822,                             // aus der fetch_city_coordinates
  "pressure": 1013,
  "pressure_history":  [
    { "hr": -4, "value": 18 },
        { "hr": -3, "value": 18.5 },
        { "hr": -2, "value": 19 },
        { "hr": -1, "value": 19.5 },
  ],                                            // Neu
  "weatherDescription": "klar",
  "cloudCoverage": 0,
  "rain1h": 0,
  "rain3h": 0,
  "snow1h": 0,
  "snow3h": 0,
  "windSpeed": 5,
  "windSpeed_history":  [
    { "hr": -4, "value": 18 },
        { "hr": -3, "value": 18.5 },
        { "hr": -2, "value": 19 },
        { "hr": -1, "value": 19.5 },
  ],                                            // Neu
  "windGust": 7,
  "windDirection": 90,
  "uvIndex": 3,
  "sunrise": "06:30",
  "sunset": "18:30",
  "visibility": 10000,
  "dewPoint": 10,
  "airQualityIndex": 50,
  "pm10": 20,
  "pm2_5": 10,
  "co": 0.3,
  "no2": 15,
  "o3": 40,
  "pollenCount": 0,
  "pressureTrend": "stabil",
  "fog": false
}

```

Hinweis: Die Felder `sunrise` und `sunset` können je nach Backend-Implementierung als Uhrzeit-Strings (z. B. `"06:30"`) oder Unix-Timestamps übergeben werden. Das Frontend unterstützt derzeit einfache `HH:MM`-Strings sowie Dezimalstunden. Bei anderen Formaten (z. B. rohe UTC-Timestamps) müsste das Backend konvertiert oder das Frontend entsprechend angepasst werden.
