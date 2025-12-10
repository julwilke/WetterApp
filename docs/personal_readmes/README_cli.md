# WetterApp CLI — Detaillierte Anleitung

Ein kleines, plattformunabhängiges CLI‑Tool zum Anzeigen und Loggen von Wetterdaten.  
Es unterstützt zwei Betriebsarten:

- CSV‑Modus: Lies lokale CSV‑Dateien mit Wetterdaten und zeige sie an.
- API‑Modus: Hole aktuelles Wetter per OpenWeather Current Weather API für eine Stadt.

Die Ausgabe kann formatiert (Text / JSON), gefiltert (--fields) und optional in eine Log‑CSV geschrieben werden. Die CLI erkennt und normalisiert verschiedene Header‑Varianten (z. B. `rain_1h`, `wind_speed`, `wind_deg`) und behandelt UTF‑8/BOM‑Probleme robust.

---

Inhalt
- Kurzübersicht
- Voraussetzungen
- Installation / Vorbereitung
- Schnellstart (Beispiele)
- CSV‑Eingabeformat & Encoding
- API‑Modus (OpenWeather)
- CLI‑Optionen im Detail
- Felder / Ausgabeformatierung
- Logging (logged.csv)
- Troubleshooting (häufige Probleme)
- Entwickeln / Tests / PR
- Lizenzhinweis

---

Kurzübersicht
- Programm: cli/cli.py
- Sprache: Python 3.8+
- Zweck: Wetterdaten anzeigen & optional loggen (CSV / OpenWeather)
- Erweiterte Felder: date, city, temp, description, precipitation, wind, humidity, pressure, clouds

---

Voraussetzungen
- Python 3.8 oder neuer
- Internetzugang für OpenWeather‑Aufrufe
- Optional: OpenWeather API‑Key (kostenlos bei https://openweathermap.org/)

---

Installation / Vorbereitung
1. Klone / öffne dein Projektverzeichnis, in dem `cli/cli.py` liegt.
2. (Optional) Virtuelle Umgebung erstellen und aktivieren:
   - Windows PowerShell:
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
   - macOS / Linux:
     python -m venv .venv
     source .venv/bin/activate
3. Stelle sicher, Python ist erreichbar:
   python -V

---

Schnellstart (PowerShell & Bash Beispiele)

CSV lesen und anzeigen:
- PowerShell:
  $env:OPENWEATHER_API_KEY = "..."  # nur falls du später API brauchst
  python -m cli.cli --file .\sample.csv

- Bash:
  python -m cli.cli --file sample.csv

CSV per stdin (pipe):
- PowerShell:
  Get-Content .\sample.csv -Raw | python -m cli.cli
- Bash:
  cat sample.csv | python -m cli.cli

OpenWeather (API‑Modus):
- Setze Key als Umgebungsvariable (empfohlen):
  $env:OPENWEATHER_API_KEY = "DEIN_ECHTER_KEY"
  python -m cli.cli --ow-city "Berlin"
- Oder Key direkt:
  python -m cli.cli --ow-city "Berlin" --ow-key DEIN_KEY

Loggen in CSV:
- python -m cli.cli --file .\sample.csv --log .\logged.csv
- python -m cli.cli --ow-city "Berlin" --ow-key DEIN_KEY --log .\logged.csv

JSON‑Ausgabe (z. B. für Pipes):
- python -m cli.cli --file .\sample.csv --format json

Nur in Log schreiben (keine Konsole):
- python -m cli.cli --file .\sample.csv --log .\logged.csv --only-log

Keine Konsolenausgabe (nur Fehler auf stderr):
- python -m cli.cli --file .\sample.csv --quiet

Eigenes Feldset anzeigen (Reihenfolge wichtig):
- python -m cli.cli --file .\sample.csv --fields "date,city,temp,wind,precipitation"

---

CSV‑Eingabeformat
- Erwarteter Header (nicht zwingend in dieser Reihenfolge):
  date,city,temp,description,precipitation,wind_speed,wind_deg,humidity,pressure,clouds
- Minimaler, empfohlenes Beispiel (UTF‑8 ohne BOM):
  date,temp,description
  2025-12-09,5,leicht bewölkt
  2025-12-10,6,sonnig

Hinweise:
- Der Parser normalisiert Header: trimmt Whitespaces und wandelt in lowercase.
- Unterstützte alternative Header‑Namen (CSV):
  - precipitation: `precipitation`, `rain`, `rain_1h`, `snow`, `snow_1h`
  - wind speed: `wind_speed`, `wind`, `wind_s`, `wind_kmh`, `wind_kph`
  - wind dir: `wind_deg`, `wind_dir`, `wind_direction`
  - humidity: `humidity`
  - pressure: `pressure`
  - clouds: `clouds`
- Wenn Felder fehlen, bleibt deren Anzeige/Log leer.

Encoding / BOM
- Dateien sollten UTF‑8 ohne BOM speichern.
- Wenn dein CSV ein BOM (bytes 239,187,191) enthält, erzeugt das Probleme mit dem Header (z. B. "\ufeffdate").
- Prüfen (PowerShell):
  Get-Content .\sample.csv -Encoding Byte | Select-Object -First 3
  -> 239 187 191 → BOM vorhanden
- Neu speichern ohne BOM (PowerShell Core):
  Set-Content -Path .\sample.csv -Value "date,temp,description`n2025-12-09,5,leicht bewölkt" -Encoding utf8NoBOM
- Terminal-Encoding in PowerShell bei Umlauten:
  chcp 65001  # temporär UTF‑8

---

API‑Modus (OpenWeather)
- Die CLI nutzt die OpenWeather Current Weather API (endpoint: /data/2.5/weather).
- Benötigt einen API‑Key (AppID). Setze als Umgebungsvariable oder übergib mit --ow-key.
- Standard‑Units: metric (°C, m/s). Für imperial (°F, mph) setze --ow-units imperial.
- Sprache für die Beschreibung steuerbar mit --ow-lang (z. B. de, en).
- Die CLI extrahiert u. a. temp, description, rain/snow, wind.speed, wind.deg, main.humidity, main.pressure, clouds.all.
- Bei API‑Aufruf wird zusätzlich das Feld `city` gesetzt (API‑kanonischer Name oder angefragte Stadt).

401 Unauthorized Fehler
- Ursache: falscher / leerer API‑Key.
- Lösung: Stelle sicher, dass du den richtigen Key verwendest:
  $env:OPENWEATHER_API_KEY = "DEIN_ECHTER_KEY"

Rate Limits
- Beachte die Rate Limits deines OpenWeather-Plans.

---

CLI‑Optionen (kompakt)
- --file, -f <path> : Eingabe‑CSV (wenn weggelassen → stdin)
- --log, -l <path> : Hänge Ergebnisse an Log‑CSV
- --ow-city <city> : Hol aktuelles Wetter für CITY (statt CSV)
- --ow-key <key> : API Key (alternativ OPENWEATHER_API_KEY Umgebungsvariable)
- --ow-units <metric|imperial> : Einheit für API (default: metric)
- --ow-lang <lang> : Sprache (default: de)
- --quiet, -q : Unterdrücke normale stdout‑Ausgabe (Fehler bleiben)
- --only-log : Schreibe nur in Logdatei; keine Ausgabe (erfordert --log)
- --format <text|json> : Ausgabeformat (default: text)
- --fields "<f1,f2,...>" : Komma‑getrennte Liste der anzuzeigenden Felder (Reihenfolge wichtig)
  - Verfügbare Felder: date,city,temp,description,precipitation,wind,humidity,pressure,clouds
  - Default: ["date","city","temp","description","precipitation","wind","humidity","pressure","clouds"]

Exit‑Codes (aus main)
- 0: Erfolg
- 2: OpenWeather API‑Key fehlt
- 3: Fehler beim Abrufen von OpenWeather
- 4: Fehler beim Lesen der Datei
- 5: Fehler beim Parsen der Eingabedaten
- 6: Fehler beim Schreiben in die Logdatei
- 7: Ungültige Kombination (z. B. --only-log ohne --log)
- 130: Abbruch (KeyboardInterrupt)

---

Felder / Ausgabeformatierung (kurz)
- date: ISO‑Z oder CSV Datum → angezeigt als TT.MM.JJJJ oder TT.MM.JJJJ HH:MM UTC
- city: API‑kanonischer Name (bei API) oder CSV‑Spalte `city`
- temp: gerundet (ganze Zahl wenn passend, sonst 1 Dezimalstelle) + °C
- description: erstes Zeichen groß
- precipitation: in mm (1h/3h) formatiert
- wind: m/s (gerundet) + Richtung (deg)
- humidity: Prozent
- pressure: hPa
- clouds: Prozent

---

Logging (logged.csv)
- Header/Reihenfolge:
  date,city,temp,description,precipitation,wind_speed,wind_deg,humidity,pressure,clouds
- Jede CLI‑Ausführung hängt Zeilen an (append). Möchtest du keine Duplikate, lösche die Logdatei vor dem Lauf:
  Remove-Item .\logged.csv -Force
- Wenn CSV‑Modus eingelesen wird und die CSV keine city‑Spalte hat, bleibt city leer; bei API‑Aufruf wird city ausgefüllt.

---

Troubleshooting — häufige Probleme & Lösungen

1) Merkwürdige Zeichen (z. B. "bewÃ¶lkt")
- Ursache: Encoding / Terminal‑Codepage.
- Lösung:
  - Stelle sicher, CSV ist UTF‑8 (ohne BOM) oder öffne mit -Encoding UTF8 beim Get-Content:
    Get-Content .\logged.csv -Raw -Encoding UTF8
  - Setze PowerShell Codepage:
    chcp 65001

2) Datum wird als "-" oder leer angezeigt
- Prüfe CSV Header: kann ein BOM im Header stehen? (erste Bytes 239 187 191)
  Get-Content .\sample.csv -Encoding Byte | Select-Object -First 3
- Neu schreiben ohne BOM (PowerShell Core):
  Set-Content -Path .\sample.csv -Value "date,temp,description`n2025-12-09,5,leicht bewölkt" -Encoding utf8NoBOM

3) Felder wie wind/humidity leer
- Wenn CSV‑Modus: musst die Spalten in der CSV haben (oder alternative Header‑Namen, die der Parser unterstützt).
- Wenn API‑Modus: OpenWeather liefert manche Felder nur bei Bedarf (z. B. rain/snow nur wenn vorhanden).

4) OpenWeather 401 Unauthorized
- Dein API‑Key ist ungültig oder falsch. Setze den korrekten Key:
  $env:OPENWEATHER_API_KEY = "DEIN_ECHTER_KEY"

5) Doppelte Logzeilen (bei wiederholtem Testen)
- logged.csv wird angehängt. Lösche die Datei, wenn du einen sauberen Test willst:
  Remove-Item .\logged.csv -Force

6) --only-log ohne --log
- Das ist ein Fehler (Exit‑Code 7). Gib --log an, wenn du only-log benutzt.

---

Entwicklung / Tests / PR
- Der Code ist in `cli/cli.py`. Funktionen sind separiert:
  - parse_weather_data(raw)
  - fetch_openweather_for_city(city, api_key, ...)
  - display_weather(data, fields)
  - log_to_csv(data, path)
- Vorschlag: Unit‑Tests mit pytest schreiben für:
  - parse_weather_data (BOM, verschiedene Headernamen)
  - _extract_common_from_api (mit Beispiel-API‑JSONs)
  - display_weather (Formatierung)
- Wenn du möchtest, kann ich die Änderungen als Branch + Pull Request erstellen (z. B. "tugba01"). Sag: "Mach PR tugba01".

---

Beispiele — integrierte Cheatsheet

1) API, direkt anzeigen:
$env:OPENWEATHER_API_KEY = "DEIN_ECHTER_KEY"
python -m cli.cli --ow-city "Berlin"

2) API, loggen, keine Ausgabe:
python -m cli.cli --ow-city "Berlin" --ow-key DEIN_KEY --log logged.csv --only-log

3) CSV, nur bestimmte Felder anzeigen:
python -m cli.cli --file sample.csv --fields "date,city,temp,wind,precipitation"

4) CSV per stdin:
Get-Content .\sample.csv -Raw | python -m cli.cli

---

Weiteres / Ideen für Erweiterungen
- Einheit für Wind auf km/h umstellen (--wind-units kmh)
- Mehrere Städte aus Datei (--ow-cities-file)
- Parallelisierte API‑Abfragen (async)
- Pretty table / farbige Terminalausgabe
- Deduplication im Log (Option --unique)

---

Lizenz (Vorschlag)
- Standardmäßig keine Lizenz gesetzt. Falls gewünscht, benutze MIT- oder Apache‑2.0‑Lizenz. Sag Bescheid, welche du bevorzugst und ich füge LICENSE + README‑Abschnitt hinzu.

---

Kontakt / Support
Wenn du konkrete Anpassungen willst (anderes Datumsformat, km/h statt m/s, zusätzliche Felder wie visibility oder UV), sag kurz welche Änderung — ich liefere aktualisierten Code + Testbeispiele.

Vielen Dank — sag „Erstelle README in Repo“ wenn ich das README.md direkt als Commit/Branch/PR für dich anlegen soll (z. B. Branchname: tugba01).  
