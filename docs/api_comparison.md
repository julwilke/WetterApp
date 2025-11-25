# Vergleich: Wetter-APIs fuer die WetterApp 

## Auswahlkriterien aus den Projektzielen
- Niedrige Einstiegshürde: idealerweise keyless oder Free-Tier ohne Kreditkarte; kein Leaken von Secrets im Frontend.
- Einfache Integration: klare HTTP-Endpoints, JSON-Ausgabe, solide Doku; lauffaehig mit fetch im Client oder kleinem Proxy.
- Stabil fuer DACH/Europa: Forecast-Daten, Zeitzonen, Einheiten; vernuenftige Rate-Limits.
- Lizenz/Risiken: Attribution-Pflichten, Fair-Use-Grenzen, Kosten beim Ueberschreiten des Free-Tiers.

## Kurzueberblick (auf einen Blick)

| API | Key noetig | Free/Trial | Daten & Staerken | Rate-Limit/SLA (Stand 2024, gerundet) | Fit fuer PKI-WetterApp |
|---|---|---|---|---|---|
| Open-Meteo | Nein (non-commercial) | Frei, Fair-Use | Forecast global, viele Parameter, Open-Source-Stack | kein offizielles SLA, Fair-Use ~10k Requests/Tag praktikabel | MVP, Demos ohne Key-Handling |
| OpenWeatherMap (OWM) | Ja | Free-Plan, aber registrierungspflichtig | Aktuell + Forecast + Alerts + Air-Quality, Map-Tiles | One Call 3.0 ~1000 Calls/Tag (Free), 60/min Throttle | Produktnahe App, wenn spaeter mehr Features gebraucht |
| Meteostat | Ja (direkt oder RapidAPI) | RapidAPI Free ~500 Calls/Monat | Historische stationaere Messdaten, Bulk-Exporte | Fair-Use; Schnell ueber Limit -> Kosten | Klimadaten, Zeitreihen, Rueckblick-Features |
| Visual Crossing | Ja | Trial (meist 1000 Calls/Tag) | Forecast + Historie in einem Endpoint, CSV/Excel-Export | Minuten-Limits, Credits verbrauchen sich schnell | Reports, kombinierte Historie/Forecast in UI |

## Detail-Profile

### Open-Meteo
**Staerken**
- Kein Key: sofort nutzbar in Frontend-Demos; keine Secret-Verwaltung.
- Viele Modelle/Parameter (Temp, Niederschlag, Wind, Sonnenstand, Solar), einfache Query-Strings.
- Open-Source-Orientierung, transparente Quellen; gute Zeitzonen-Unterstuetzung.

**Schwaechen**
- Kein formales SLA; Ausfallrisiko muss abgefangen werden (Fallback/Retry).
- Wenig oder keine echten historischen Daten; keine Map-Tiles.

**Risiken**
- Fair-Use kann bei sehr vielen Requests greifen (429 moeglich); IP-Rate-Limits nicht exakt dokumentiert.
- Fuer kommerzielle Nutzung ist ggf. ein Vertrag oder ein anderes Angebot noetig.

**Integrationstipps**
- Endpunkt: `https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m,precipitation_probability&timezone=Europe%2FBerlin`
- Caching auf Stundenbasis spart Requests; Fallback auf statische Demo-Daten fuer Praesentationen.

### OpenWeatherMap (OWM)
**Staerken**
- Breiter Funktionsumfang: Current, Forecast, Alerts, Air Quality, Maps, Geocoding.
- Gute globale Abdeckung, viele Tutorials und SDKs.

**Schwaechen**
- API-Key Pflicht und in Free-Plan streng limitiert; Key darf nicht im Frontend liegen.
- Historische Daten kostenpflichtig; One Call 3.0 hat andere Limits als aeltere Versionen.

**Risiken**
- Ueberschreitung der 1000 Calls/Tag fuehrt zu Sperren oder Kosten; Request-Burst >60/min wird gedrosselt.
- Kommerzielle Nutzung erfordert planbare Kosten; AGB verlangen teilweise Attribution.

**Integrationstipps**
- Nutzung ueber kleinen Backend-Proxy, der den Key aus `.env` liest.
- Beispiel: `https://api.openweathermap.org/data/3.0/onecall?lat=52.52&lon=13.41&exclude=minutely&appid=$OWM_API_KEY&units=metric&lang=de`
- Bei Karten: Tile-Caching vermeiden; auf offizielle Limits achten.

### Meteostat
**Staerken**
- Starke historische Daten (Stationsdaten, Zeitreihen, Bulk CSV).
- Ideal fuer Klimatrends, Rueckblicke ("Wetter vor einer Woche/letztes Jahr").

**Schwaechen**
- Forecast/Current weniger umfangreich als OWM; Fokus klar auf Historie.
- Freikontingent bei RapidAPI gering; direkte API erfordert Registrierung.

**Risiken**
- Nach Free-Limit steigen Kosten pro Request; ungecachete UI kann Limit schnell ueberschreiten.
- Stationen variieren in Qualitaet/Verfuegbarkeit; Datenluecken moeglich.

**Integrationstipps**
- Beispiel: `https://meteostat.p.rapidapi.com/point/daily?lat=52.52&lon=13.41&start=2024-01-01&end=2024-01-31`
- Immer mit Caching/Local Storage arbeiten; Datumsspannen begrenzen.

### Visual Crossing
**Staerken**
- Kombiniert Forecast und Historie, liefert auch CSV/Excel fuer Reports.
- Flexible Parameter (Agrar, Solar, Marine) und solide Geocoding-Optionen.

**Schwaechen**
- Nur mit Key, Trial schnell verbraucht; Pricing basiert auf Credits.
- Dokumentation weniger schlank als Open-Meteo/OWM.

**Risiken**
- Credit-Verbrauch durch breite Parameterlisten; Vorsicht bei breiten Zeitraeumen.
- SLA und Kartenfeatures an Plan gebunden; ohne Plan keine Garantien.

**Integrationstipps**
- Beispiel: `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/berlin?key=$VC_KEY&unitGroup=metric&include=hours`
- Queries so schmal wie moeglich halten, um Credits zu sparen.

## Empfehlungen nach Einsatzziel
- MVP/Studierenden-Demo ohne Key-Handling: Open-Meteo.
- Historische Vergleiche oder Klimadiagramme: Meteostat (mit Caching).
- Alerts/Maps oder spaeterer produktnaher Ausbau: OpenWeatherMap.
- Reporting mit kombinierter Historie+Forecast (Export): Visual Crossing.

## Risiko-Checkliste (kurz)
- **Rate-Limits**: Monitoring und Retry-Backoff einbauen; UI-Cache nutzen.
- **Keys/Secrets** (OWM, Meteostat, Visual Crossing): nie im Frontend bundlen, nur per Backend/Proxy.
- **Kosten**: Free-Limits dokumentieren, bei Ueberschreitung harte Abbrueche oder Fallback-Daten.
- **Attribution/Lizenzen**: Open-Meteo meist CC-BY; OWM verlangt ggf. Quellenangabe; Visual Crossing Terms pruefen.
- **Verfuegbarkeit**: Kein SLA bei Open-Meteo; fuer Praesentationen Offline-Demo parat halten.

## To-dos fuer die Repo-Integration
- API-Wahl und Limits in `docs/api_comparison.md` aktuell halten; gewaehlte API im README kurz nennen.
- `.env.example` mit benoetigten Keys (OWM/Meteostat/VC) bereitstellen; Keys nur serverseitig nutzen.
- Caching-Strategie im Code hinterlegen (z.B. stundenweise Forecast-Cache, Datumslimits fuer Historie).
- Fallback-Daten fuer Demos anlegen, damit Praesentationen ohne Netz/Limit funktionieren.
