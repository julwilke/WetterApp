# Erklärung: tests/test_parse_weather.py

Dieses Dokument beschreibt kurz und präzise, was die Testdatei `tests/test_parse_weather.py` genau macht, warum die Tests wichtig sind und wie du sie lokal ausführst.

## Zweck der Tests (Kurz)
- Validiert die Kernlogik eurer CLI (Datei `weather_cli.py`), ohne echte Netzwerkaufrufe.
- Stellt sicher, dass:
  - die Parser-Funktion `parse_weather_data` korrekt Daten extrahiert,
  - die Anzeige-Funktion `display_weather` menschenlesbare Ausgabe erzeugt,
  - das CSV-Logging `log_to_csv` eine Datei mit Header und Datenzeile erzeugt.
- Tests erhöhen Zuverlässigkeit und sind hilfreich für die Bewertung/Abgabe.

## Voraussetzungen
- `weather_cli.py` muss im Repository‑Root liegen (derselbe Ordner, aus dem du `pytest` ausführst).
- Python (empfohlen 3.10+).
- In einer virtuellen Umgebung installierte Abhängigkeiten:
  - pytest
  - requests (falls du andere Tests ausführst)
  - python-dotenv (optional)
- Minimal installieren:
  ```bash
  python -m pip install pytest
  ```

## Wo liegt die Datei
- Pfad: `<repo-root>/tests/test_parse_weather.py`

## Tests im Überblick (was jeder Test macht)

1. `test_parse_weather_full()`
   - Zweck: Prüft, dass `parse_weather_data` aus einer vollständigen, realistisch aussehenden API-Antwort die erwarteten Felder extrahiert:
     - `location_name` → sollte `"Berlin"` sein
     - `temperature_celsius` → z. B. `6.5`
     - `humidity_percent` → z. B. `81`
     - `weather_description` → z. B. `"light rain"`
     - `raw` → enthält gültiges JSON (String)
   - Warum wichtig: Sicherstellt, dass der Parser unter Normalbedingungen korrekt arbeitet.

2. `test_parse_weather_missing_fields()`
   - Zweck: Prüft Robustheit des Parsers bei fehlenden Feldern (z. B. kein `name`, kein `temp` und leeres `weather`-Array).
   - Erwartung:
     - fehlende Werte → `None`
     - vorhandene Werte (z. B. `humidity`) bleiben erhalten
   - Warum wichtig: Verhindert Abstürze bei unvollständigen API-Antworten.

3. `test_display_weather_outputs_readable_text(capfd)`
   - Zweck: Prüft, dass `display_weather` menschenlesbare und formatiere Strings auf stdout ausgibt.
   - Was wird geprüft:
     - Ort wird ausgegeben (`Wetter für: ...`)
     - Temperatur ist mit einer Nachkommastelle formatiert (z. B. `12.3 °C`)
     - Luftfeuchte und Beschreibung sind enthalten
   - Technik: `pytest`'s `capfd` fängt stdout ein und der Test prüft den Inhalt.

4. `test_log_to_csv_creates_file_and_writes_header_and_row(tmp_path)`
   - Zweck: Prüft, dass `log_to_csv`:
     - eine Datei (inkl. Verzeichnis) anlegt,
     - Headerzeile schreibt,
     - mindestens eine Datenzeile anhängt.
   - Technik: `pytest`'s `tmp_path` erzeugt einen temporären Ordner für die Datei, sodass der Test isoliert läuft.

## Wie du die Tests ausführst

1. Im Repo‑Root (dort, wo `weather_cli.py` liegt) in die virtuelle Umgebung:
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     & ".\.venv\Scripts\Activate.ps1"
     python -m pip install --upgrade pip
     python -m pip install pytest
     ```
   - macOS / Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     python -m pip install --upgrade pip
     python -m pip install pytest
     ```

2. Tests ausführen:
   - Alle Tests:
     ```bash
     python -m pytest -q
     ```
   - Nur diese Testdatei:
     ```bash
     python -m pytest -q tests/test_parse_weather.py
     ```
   - Einzelnen Test laufen lassen:
     ```bash
     python -m pytest -q tests/test_parse_weather.py::test_parse_weather_full
     ```

## Mögliche Fehler & Lösungen

- `ModuleNotFoundError: No module named 'weather_cli'`
  - Ursache: `weather_cli.py` nicht im aktuellen Verzeichnis.
  - Lösung: Stelle sicher, dass du `pytest` aus dem Repo‑Root ausführst, wo `weather_cli.py` liegt, oder passe die Importzeile in der Testdatei an (z. B. `from cli import parse_weather_data`, falls du die Datei `cli.py` nennst).

- `ImportError` / fehlende Abhängigkeiten
  - Lösung: `python -m pip install pytest requests python-dotenv`

- Test schreibt keine CSV / Pfadprobleme
  - Lösung: Der CSV-Test verwendet `tmp_path`, sodass er keine Schreibrechte im Repo benötigt. Wenn ein eigener Test mit echtem Pfad fehlschlägt, prüfe Dateirechte und Pfad.

## Hinweise zur Erweiterung
- Du kannst weitere Tests hinzufügen, z. B.:
  - Mocking von `fetch_current_weather` (mittels `requests-mock` oder `responses`), um API‑Fehler zu simulieren.
  - Tests für CLI-Argumenthandling (z. B. `pytest`'s `monkeypatch` auf `sys.argv`).
- Wenn du `requirements.txt` hast, füge `pytest` dort hinzu, damit CI/Reviewer die Abhängigkeiten installieren können.

## Zusammenfassung (in 1 Satz)
Die Datei `tests/test_parse_weather.py` stellt sicher, dass der Kernparser, die Konsolenanzeige und das CSV‑Logging eurer CLI zuverlässig funktionieren — ohne echte Netzwerkanfragen — und hilft so, die Hauptfunktionen priorisiert abzusichern.
