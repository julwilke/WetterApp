# Erklärung zu tests/test_parse_weather.py

Kurz: Diese Markdown‑Datei erklärt, was `tests/test_parse_weather.py` prüft, wie du die Tests lokal ausführst und welche Voraussetzungen erfüllt sein müssen.

## Zweck der Tests
- Validiert die Kernfunktionen der CLI‑Logik ohne echte Netzwerkanfragen.
- Schwerpunkte:
  - `parse_weather_data` — extrahiert Felder aus einer API‑Antwort.
  - `display_weather` — erzeugt menschenlesbare Ausgabe auf stdout.
  - `log_to_csv` — legt eine CSV-Datei an (inkl. Header) und hängt eine Datenzeile an.

## Wo liegt die Testdatei
- Pfad: `tests/test_parse_weather.py`

## Was genau getestet wird
1. `test_parse_weather_full`
   - Nutzt eine vollständige Beispielantwort.
   - Erwartet: Ort (`name`), Temperatur (`main.temp`), Luftfeuchte (`main.humidity`), Beschreibung (`weather[0].description`) und ein gültiges `raw` JSON‑String.

2. `test_parse_weather_missing_fields`
   - Nutzt eine abgespeckte Beispielantwort (ohne `name`, ohne `temp`, leeres `weather`).
   - Erwartet: keine Exceptions; fehlende Felder → `None`; vorhandene Felder bleiben erhalten.

3. `test_display_weather_outputs_readable_text`
   - Übergibt ein bereits geparstes Dict an `display_weather`.
   - Prüft: formatierte Ausgabe (z. B. Temperatur mit einer Dezimalstelle, Ort, Luftfeuchte, Beschreibung).

4. `test_log_to_csv_creates_file_and_writes_header_and_row`
   - Nutzt `tmp_path` (pytest) für einen temporären Ordner.
   - Prüft: Datei existiert, Header entspricht erwarteter Spaltenliste, mindestens eine Datenzeile vorhanden.

## Voraussetzungen
- `weather_cli.py` muss importierbar sein (Wrapper im Repo‑Root oder direkte Implementierung).
  - Wenn die Implementierung in `cli/` liegt, sorgt der Wrapper `weather_cli.py` im Repo‑Root dafür, dass `from weather_cli import ...` funktioniert.
  - Alternativ: passe die Importzeile in der Testdatei an (`from cli.weather_cli import ...`).
- Python 3.x und `pytest` installiert (z. B. `python -m pip install pytest`).
- Keine API‑Keys nötig — Tests verwenden statische Beispiel‑Daten.

## Tests ausführen (lokal)
1. Virtuelle Umgebung (empfohlen):
   - python -m venv .venv
   - Windows PowerShell: & ".\.venv\Scripts\Activate.ps1"
   - macOS / Linux: source .venv/bin/activate

2. Abhängigkeiten:
   - python -m pip install --upgrade pip
   - python -m pip install pytest

3. Testlauf:
   - Im Repo‑Root: python -m pytest -q
   - Nur diese Datei: python -m pytest -q tests/test_parse_weather.py

## Troubleshooting
- ModuleNotFoundError: No module named 'weather_cli'
  - Stelle sicher, dass `weather_cli.py` im Repo‑Root liegt oder passe die Importpfade.
  - Prüfe, ob du `pytest` aus dem Repo‑Root startest (damit das aktuelle Verzeichnis im PYTHONPATH ist).

- Dateikonflikte beim Verschieben von Tests
  - Falls du eine verschachtelte `tests/tests/` hattest: verschiebe Dateien in `tests/` und entferne den leeren inneren Ordner.
  - Prüfe mit `git status` vor dem Commit.

## Empfehlung für Commit‑Message (kurz)
- "Add/Update tests/test_parse_weather.py — unit tests for parser, display and CSV logging"

## Weiteres
- Du kannst Tests erweitern:
  - Mocking von `fetch_current_weather` (z. B. `responses` oder `requests-mock`), um API‑Fehler zu simulieren.
  - CLI‑argument tests mit `monkeypatch` auf `sys.argv`.
- Wenn du willst, passe ich die Test‑Imports an eure Ordnerstruktur oder erstelle den Wrapper automatisch — sag Bescheid.
