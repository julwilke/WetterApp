markdown
# weather_cli.py — Erklärung, Anleitung und was sich in dieser Endfassung geändert hat

Dieses Dokument erklärt kurz und ausführlich:
- wie du die weather_cli.py benutzt,
- welche Funktionen darin sind und wofür sie da sind,
- welche Dateien / Tests ergänzt wurden,
- und welche konkreten Änderungen ich vorgenommen habe.

> Speicherort der Datei: Repository-Root als `weather_cli.py`  
> Ergänzende Testdatei: `tests/test_parse_weather.py` (führt Unit-Tests für parse_weather_data aus)

---

## 1) Kurz: Was macht das Skript?
- Holt aktuelles Wetter für eine Postleitzahl (PLZ) von OpenWeatherMap.
- Ausgabe: Ort, Temperatur (°C), Luftfeuchtigkeit (%) und kurze Wetterbeschreibung.
- Zusätzliche Optionen:
  - `--zip` / `-z` : PLZ direkt übergeben (non-interactive).
  - `--country` / `-c` : Ländercode (z. B. DE, US). Default: DE.
  - `--log-csv` : Pfad zu einer CSV-Datei, an die die Abfrage inklusive Rohdaten angehängt wird.
  - `--dotenv` : Pfad zu einer .env-Datei, die vor Ausführung geladen wird (öffnet lokalen Workflow).
  - `--raw` : Ausgabe der kompletten Roh-JSON-Antwort (Debug).

---

## 2) Wie starte ich das (Schritt-für-Schritt, PowerShell)
1. Virtuelle Umgebung anlegen:
   - `python -m venv .venv`
2. venv aktivieren (PowerShell):
   - `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`
   - `& ".\.venv\Scripts\Activate.ps1"`
3. Abhängigkeiten installieren (minimal):
   - `python -m pip install --upgrade pip`
   - `python -m pip install requests python-dotenv pytest`
   - (Alternativ: `python -m pip install -r requirements.txt` falls vorhanden)
4. API-Key setzen (lokal, nicht commiten):
   - PowerShell: `$env:OPENWEATHER_API_KEY="DEIN_KEY"`
   - Oder `.env` anlegen mit Zeile: `OPENWEATHER_API_KEY=DEIN_KEY` und `--dotenv .env` verwenden.
5. CLI testen:
   - Interaktiv: `python weather_cli.py`
   - Direkt: `python weather_cli.py --zip 10115 --country DE`
   - Mit CSV-Logging: `python weather_cli.py --zip 10115 --log-csv logs/logs.csv`
   - Mit Raw-Output: `python weather_cli.py --zip 10115 --raw`

---

## 3) Tests
- Datei: `tests/test_parse_weather.py`
- Testet: die Funktion `parse_weather_data(api_response)` mit:
  - einer vollwertigen Beispiel-Antwort und
  - einer Antwort mit fehlenden Feldern.
- Ausführen: `python -m pytest -q`

Warum Tests?
- `parse_weather_data` ist die logisch wichtigste, rein-funktionale Komponente (leicht zu testen).
- Tests zeigen Robustheit: kein Absturz bei fehlenden Feldern.

---

## 4) Wichtige Funktionen & Zweck (Kurzreferenz)

- `optional_load_dotenv(dotenv_path)`  
  Lädt .env, falls python-dotenv installiert ist. Praktisch für lokale API-Key Verwaltung.

- `get_api_key()`  
  Liest `OPENWEATHER_API_KEY` aus der Umgebung — zentrale Stelle, leicht mockbar/testbar.

- `build_query_params(zip_code, country_code, units)`  
  Erzeugt die Query-Parameter für die API (z.B. `"10115,DE"`).

- `fetch_current_weather(api_key, zip_code, country_code)`  
  Führt HTTP GET mit Timeout aus und handhabt Fehlerfälle (Network / non-200 / ungültiges JSON).
  Wirft bei Fehlern `RuntimeError` mit klarer Nachricht.

- `parse_weather_data(api_response)`  
  Extrahiert `name`, `main.temp`, `main.humidity` und `weather[0].description` sowie `raw` JSON.
  Diese Funktion ist deterministisch und leicht testbar.

- `display_weather(parsed)`  
  Formatiert und gibt die Wetterdaten für Menschen aus; nutzt Fallbacks.

- `log_to_csv(csv_path, zip_code, country_code, result)`  
  Anhängen des Ergebnisses an CSV-Datei; schreibt Header, wenn nötig; behandelt Ordnererstellung.

- `prompt_for_zip_interactive()`  
  Interaktive Eingabe der PLZ + optional Ländercode; bei leerer PLZ wird sauber beendet.

---

## 5) Exit‑Codes (konsequente Bedeutung)
- 0 — Erfolgreich
- 1 — Interaktive Eingabe abgebrochen (keine PLZ eingegeben)
- 2 — Fehlender API-Key (Konfigurationsproblem)
- 3 — Fehler beim Abrufen der Daten (Netzwerk / API)

---

## 6) Konkrete Änderungen, die ich vorgenommen habe
(Das ist die Liste der Dinge, die ich implementiert/festgeschrieben habe, im Vergleich zu dem Stand davor)

1. Korrektes .env-Argument:
   - Fix: `argparse` argument heißt `--dotenv` mit `dest="dotenv_path"` und der Code prüft `args.dotenv_path`.
   - Problem vorher: Prüfung auf `args.dotenv` führte zu AttributeError.

2. Robuste API-Fehlerbehandlung:
   - Timeout gesetzt (`HTTP_TIMEOUT = 10`).
   - requests-Ausnahmen fangen und in `RuntimeError` mit hilfreicher Fehlermeldung umwandeln.
   - Bei non-200 Antworten wird API-Fehlertext/JSON extrahiert und zurückgemeldet.

3. Sauberer JSON-Parsing-Fallback:
   - Fehler beim JSON-Parsing führen kontrolliert zu RuntimeError.

4. CSV-Logging:
   - Implementiert `log_to_csv` mit Header-Logik, Ordnererstellung und Windows-kompatiblem newline handling.
   - Loggingfehler sind nicht-blockierend (nur Warnung).

5. Parsing-Funktion isoliert & testbar:
   - `parse_weather_data` extrahiert Felder und gibt ein sauberes Dict zurück.
   - Diese Funktion ist die Basis der Unit-Tests.

6. Erweiterte Kommentare / Struktur:
   - Datei strukturiert in Konfiguration, Hilfsfunktionen, Hauptlogik.
   - Viele Kommentare pro Funktion und erklärende Strings.

7. Tests:
   - `tests/test_parse_weather.py` hinzugefügt (zwei einfache Tests).
   - Tests prüfen sowohl „vollständige“ als auch „unvollständige“ API-Antworten.

---

## 7) Empfehlung für die Abgabe (was noch tun)
- Datei `weather_cli.py` ins Repo-Root speichern (falls noch nicht geschehen).
- `tests/test_parse_weather.py` in `tests/` speichern und `pytest` laufen lassen.
- `requirements.txt` im Root sicherstellen (z.B. `requests`, `python-dotenv`, `pytest`, `pandas`, `flask` falls Dashboard).
- `.env.example` hinzufügen (mit Kommentar `OPENWEATHER_API_KEY=`) und `.gitignore` prüfen.
- Optional: einen Mock-Modus implementieren (z. B. `--mock-from-csv sample.csv`), damit Prüfer ohne API-Key das CLI sehen können.

---

## 8) Häufige Fragen / Troubleshooting
- "ModuleNotFoundError: requests": `python -m pip install requests`
- "AttributeError: 'Namespace' object has no attribute 'dotenv'": alte Version nutzen? Stelle sicher, dass die aktuelle weather_cli.py gespeichert ist (prüfe `args.dotenv_path`).
- "API key fehlt": setze `$env:OPENWEATHER_API_KEY="DEIN_KEY"` oder erstelle `.env` und benutze `--dotenv .env`.

---

## 9) Weiteres (falls gewünscht)
- Ich kann die weather_cli.py so erweitern, dass sie ohne API-Key mit einer sample-CSV arbeitet (`--use-sample sample.csv`), oder
- ich kann Tests erweitern und fetch_current_weather mit einem HTTP-Mock (z. B. responses oder requests-mock) testen.
- Sag mir, ob ich das ergänzen soll.

--- 
Ende der Erläuterung.
