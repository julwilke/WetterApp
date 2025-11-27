# Stadeingabe

| Anzeigename              | Variablenname        |
| ------------------------ | -------------------- |
| Stadt                    | `City`               |

# Wetterdaten für Weboberfläche mit JSON-Feldern und Quellen (ChatGPT)

| Anzeigename              | Variablenname        | JSON-Feldname / API      | Einheit / Beschreibung                              | Quelle                           |
| ------------------------ | -------------------- | ------------------------ | --------------------------------------------------- | -------------------------------- |
| Aktuelle Temperatur      | `currentTemperature` | `main.temp`              | °C                                                  | OpenWeatherMap                   |
| Gefühlt wie              | `feelsLike`          | `main.feels_like`        | °C                                                  | OpenWeatherMap                   |
| Minimum Temperatur       | `tempMin`            | `main.temp_min`          | °C                                                  | OpenWeatherMap                   |
| Maximum Temperatur       | `tempMax`            | `main.temp_max`          | °C                                                  | OpenWeatherMap                   |
| Luftfeuchtigkeit         | `humidity`           | `main.humidity`          | %                                                   | OpenWeatherMap                   |
| Luftdruck                | `pressure`           | `main.pressure`          | hPa                                                 | OpenWeatherMap                   |
| Wetterbeschreibung       | `weatherDescription` | `weather[0].description` | Text                                                | OpenWeatherMap                   |
| Wolkenbedeckung          | `cloudCoverage`      | `clouds.all`             | %                                                   | OpenWeatherMap                   |
| Niederschlag (1h)        | `rain1h`             | `rain.1h`                | mm                                                  | OpenWeatherMap                   |
| Niederschlag (3h)        | `rain3h`             | `rain.3h`                | mm                                                  | OpenWeatherMap                   |
| Schnee (1h)              | `snow1h`             | `snow.1h`                | mm                                                  | OpenWeatherMap                   |
| Schnee (3h)              | `snow3h`             | `snow.3h`                | mm                                                  | OpenWeatherMap                   |
| Windgeschwindigkeit      | `windSpeed`          | `wind.speed`             | m/s                                                 | OpenWeatherMap                   |
| Windböen                 | `windGust`           | `wind.gust`              | m/s                                                 | OpenWeatherMap                   |
| Windrichtung             | `windDirection`      | `wind.deg`               | °                                                   | OpenWeatherMap                   |
| UV-Index                 | `uvIndex`            | `uvi`                    | Index                                               | OpenWeatherMap                   |
| Sonnenaufgang            | `sunrise`            | `sys.sunrise`            | Timestamp                                           | OpenWeatherMap                   |
| Sonnenuntergang          | `sunset`             | `sys.sunset`             | Timestamp                                           | OpenWeatherMap                   |
| Sichtweite               | `visibility`         | `visibility`             | m                                                   | OpenWeatherMap                   |
| Taupunkt                 | `dewPoint`           | `main.dew_point`*        | °C (optional, ggf. aus Temp+Feuchtigkeit berechnen) | Meteo / berechnet                |
| Luftqualitätsindex       | `airQualityIndex`    | `aqi`                    | Index                                               | OpenWeatherMap Air Pollution API |
| PM10                     | `pm10`               | `components.pm10`        | µg/m³                                               | OpenWeatherMap Air Pollution API |
| PM2.5                    | `pm2_5`              | `components.pm2_5`       | µg/m³                                               | OpenWeatherMap Air Pollution API |
| CO                       | `co`                 | `components.co`          | µg/m³                                               | OpenWeatherMap Air Pollution API |
| NO2                      | `no2`                | `components.no2`         | µg/m³                                               | OpenWeatherMap Air Pollution API |
| O3                       | `o3`                 | `components.o3`          | µg/m³                                               | OpenWeatherMap Air Pollution API |
| Pollen (optional)        | `pollenCount`        | `pollen`                 | Anzahl pro m³ (API abhängig)                        | Meteo / spez. API                |
| Luftdrucktrend           | `pressureTrend`      | berechnet / custom       | steigend/fallend                                    | Meteo / berechnet                |
| Nebel / Sichtbehinderung | `fog` / `mist`       | `weather[0].id`          | anhand ID interpretieren                            | OpenWeatherMap                   |

# Status API
| Name                     | Status (online/offline) | letzte Abfrage           |
| ------------------------ | ----------------------- | ------------------------ |
| OpenWeather              | `statusOpenWeather`     | `lastupdateOpenWeather`  |
| Meteor                   | `statusMeteor`          | `lastupdateMeteor`       |
