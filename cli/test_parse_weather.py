"""
tests/test_parse_weather.py
-------------------------------------------------------------------------------
Diese Tests sind für die cli/cli.py geschrieben.

Überblick
    parse_weather_data(raw_csv_text) -> List[Dict[str, str]]
    display_weather(data_list, fields_list) -> print auf stdout
    log_to_csv(data_list, path) -> schreibt CSV-Datei (append, Header einmal)

Diese Tests prüfen:
1) CSV Parsing (inkl. BOM und Header-Normalisierung)
2) Ausgabeformat von display_weather
3) log_to_csv: Header wird geschrieben + Zeilen werden angehängt
4) main(): Fehlercode bei falscher Kombination (--only-log ohne --log)
5) API-Modus: OpenWeather wird “gemockt” (kein echtes Internet nötig)

-------------------------------------------------------------------------------
So startet man den Tests:
- Im Projekt-Root (WetterApp):
    pytest
oder:
    pytest -q
oder nur diese Datei:
    pytest tests/test_parse_weather.py -q
-------------------------------------------------------------------------------
"""

from __future__ import annotations

# FIX: Damit "from cli.cli import ..." sicher funktioniert (Windows/VSCode/pytest),
# wird Projekt-Root in sys.path eingefügt.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import io
import json
from typing import Any

import pytest

# Import aus der cli.py Projekt:
# cli ist ein Paket (weil cli/__init__.py existiert)
from cli.cli import (
    parse_weather_data,
    display_weather,
    log_to_csv,
    main,
)

# -----------------------------------------------------------------------------
# 1) Tests für parse_weather_data (CSV Parser)
# -----------------------------------------------------------------------------

def test_parse_weather_data_basic_csv():
    """
    Test 1: Standard-CSV wird korrekt geparst.

    Erwartung:
    - Ergebnis ist eine Liste von Dicts (eine Dict pro Zeile)
    - Header werden klein geschrieben (lowercase)
    """
    raw = "date,city,temp,description\n2025-12-09,Berlin,5,leicht bewölkt\n"
    data = parse_weather_data(raw)

    assert isinstance(data, list), "parse_weather_data sollte eine Liste zurückgeben"
    assert len(data) == 1, "Es sollte genau 1 Datenzeile geben"

    row = data[0]
    assert row["date"] == "2025-12-09"
    assert row["city"] == "Berlin"
    assert row["temp"] == "5"
    assert row["description"] == "leicht bewölkt"


def test_parse_weather_data_removes_bom():
    """
    Test 2: Falls ein UTF-8 BOM am Anfang steht, soll er entfernt werden.

    BOM bedeutet: Der erste Header kann sonst '\ufeffdate' heißen
    -> der Code entfernt das korrekt.
    """
    raw = "\ufeffdate,temp,description\n2025-12-09,5,sonnig\n"
    data = parse_weather_data(raw)

    assert len(data) == 1
    row = data[0]

    # Wichtig: es darf KEIN '\ufeffdate' key übrig bleiben
    assert "date" in row, "BOM wurde nicht entfernt: 'date' fehlt als Key"
    assert "\ufeffdate" not in row, "BOM-Key existiert noch im Dict"
    assert row["date"] == "2025-12-09"
    assert row["temp"] == "5"
    assert row["description"] == "sonnig"


def test_parse_weather_data_header_normalization():
    """
    Test 3: Header werden normalisiert:
    - trimmed
    - lowercased

    Beispiel: ' Temp ' wird zu 'temp'
    """
    raw = " Date , Temp , Description \n2025-12-09,5,leicht bewölkt\n"
    data = parse_weather_data(raw)
    row = data[0]

    assert "date" in row
    assert "temp" in row
    assert "description" in row
    assert row["temp"] == "5"


# -----------------------------------------------------------------------------
# 2) Tests für display_weather (Ausgabe auf stdout)
# -----------------------------------------------------------------------------

def test_display_weather_prints_readable_output(capfd):
    """
    Test 4: display_weather soll eine menschenlesbare Ausgabe erzeugen.

    Es werden absichtlich minimal sinnvolle Daten reingegeben.
    Das Format ist typischerweise:
      '09.12.2025 Berlin: 5°C — Leicht bewölkt'
    """
    data = [
        {
            "date": "2025-12-09",
            "city": "Berlin",
            "temp": "5",
            "description": "leicht bewölkt",
            "precipitation": "",
            "wind_speed": "",
            "wind_deg": "",
            "humidity": "",
            "pressure": "",
            "clouds": "",
        }
    ]

    # Default-Feldliste aus deiner CLI: date, city, temp, description, precipitation, wind, humidity, pressure, clouds
    fields = ["date", "city", "temp", "description"]

    display_weather(data, fields)

    out = capfd.readouterr().out
    assert "Berlin" in out, f"Stadt sollte in Ausgabe vorkommen. Ausgabe:\n{out}"
    assert "09.12.2025" in out, f"Datum sollte formatiert sein. Ausgabe:\n{out}"
    assert "5°C" in out, f"Temperatur sollte als °C erscheinen. Ausgabe:\n{out}"
    # Beschreibung wird in dem Code groß geschrieben
    assert "Leicht bewölkt" in out, f"Beschreibung sollte groß anfangen. Ausgabe:\n{out}"


def test_display_weather_no_data_message(capfd):
    """
    Test 5: Wenn data leer ist, soll ein Hinweis kommen:
        'Keine Wetterdaten zum Anzeigen.'
    """
    display_weather([], ["date", "temp"])
    out = capfd.readouterr().out
    assert "Keine Wetterdaten" in out


# -----------------------------------------------------------------------------
# 3) Tests für log_to_csv (Schreiben / Append)
# -----------------------------------------------------------------------------

def test_log_to_csv_creates_and_appends(tmp_path: Path):
    """
    Test 6: log_to_csv soll:
    - Datei erstellen, wenn sie nicht existiert
    - Header schreiben
    - Datenzeile(n) anhängen
    - Beim 2. Aufruf NICHT noch mal den Header schreiben (weil Datei existiert)
    """
    log_file = tmp_path / "logged.csv"

    # 1. Datensatz
    data1 = [
        {
            "date": "2025-12-09",
            "city": "Berlin",
            "temp": "5",
            "description": "leicht bewölkt",
            "precipitation": "0",
            "wind_speed": "3.0",
            "wind_deg": "240",
            "humidity": "80",
            "pressure": "1012",
            "clouds": "75",
        }
    ]

    # 2. Datensatz
    data2 = [
        {
            "date": "2025-12-10",
            "city": "Hamburg",
            "temp": "6",
            "description": "sonnig",
            "precipitation": "",
            "wind_speed": "",
            "wind_deg": "",
            "humidity": "",
            "pressure": "",
            "clouds": "",
        }
    ]

    # 1) Schreiben
    log_to_csv(data1, str(log_file))
    assert log_file.exists(), "Logdatei wurde nicht erstellt"

    # 2) Append
    log_to_csv(data2, str(log_file))

    # Datei lesen und prüfen
    text = log_file.read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if l.strip()]

    # Erwartung: 1 Header + 2 Datenzeilen = 3 Zeilen
    assert len(lines) == 3, f"Erwartet 3 Zeilen (Header + 2 Rows), bekommen: {len(lines)}\n{text}"

    # Header prüfen
    assert lines[0].startswith("date,city,temp,description,precipitation"), "Header stimmt nicht oder fehlt"

    # Prüfe, dass beide Städte drin stehen
    assert "Berlin" in lines[1]
    assert "Hamburg" in lines[2]


# -----------------------------------------------------------------------------
# 4) Tests für main() (Argument-Handling)
# -----------------------------------------------------------------------------

def test_main_only_log_without_log_is_error(tmp_path, capfd):
    """
    Test 7: --only-log ohne --log soll Exit-Code 7 geben.

    Wichtig:
    - Die Datei muss existieren, sonst endet main() vorher mit Exit-Code 4
      (Fehler beim Lesen der Datei).
    """
    #  echte Dummy-Datei erzeugen
    csv_file = tmp_path / "dummy.csv"
    csv_file.write_text(
        "date,city,temp,description\n2025-12-09,Berlin,5,leicht bewölkt\n",
        encoding="utf-8",
    )

    rc = main(["--file", str(csv_file), "--only-log"])
    err = capfd.readouterr().err

    assert rc == 7
    assert "--only-log verlangt" in err



def test_main_reads_file_and_outputs_text(tmp_path: Path, capfd):
    """
    Test 8: main() soll eine CSV-Datei lesen und etwas ausgeben (Exit-Code 0).
    """
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "date,city,temp,description\n2025-12-09,Berlin,5,leicht bewölkt\n",
        encoding="utf-8",
    )

    rc = main(["--file", str(csv_file)])
    out = capfd.readouterr().out

    assert rc == 0
    assert "Berlin" in out
    assert "5°C" in out


def test_main_outputs_json_format(tmp_path: Path, capfd):
    """
    Test 9: Wenn --format json gesetzt ist, soll JSON ausgegeben werden.
    """
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "date,city,temp,description\n2025-12-09,Berlin,5,leicht bewölkt\n",
        encoding="utf-8",
    )

    rc = main(["--file", str(csv_file), "--format", "json"])
    out = capfd.readouterr().out.strip()

    assert rc == 0
    # Ausgeben soll ein JSON-Array sein (Liste von Zeilen)
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert parsed[0]["city"] == "Berlin"


# -----------------------------------------------------------------------------
# 5) API-Modus testen OHNE Internet (Mock von urllib.request.urlopen)
# -----------------------------------------------------------------------------

class _DummyHTTPResponse:
    """
    Mini-Helferklasse zum Mocken von urllib.request.urlopen(...)
    Damit der Code denkt, er bekommt eine echte HTTP-Antwort.
    """

    def __init__(self, payload: str):
        self._payload = payload.encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_main_api_mode_with_mock(monkeypatch, capfd):
    """
    Test 10: API-Modus soll funktionieren, ohne echtes Internet.

    "patchen" urllib.request.urlopen so,
    dass immer eine Fake-OpenWeather-Antwort zurückkommt.
    """
    import urllib.request

    fake_api_json = {
        "cod": 200,
        "name": "Berlin",
        "main": {"temp": 6.5, "humidity": 81, "pressure": 1012},
        "weather": [{"description": "light rain"}],
        "wind": {"speed": 4.12, "deg": 240},
        "clouds": {"all": 75},
        # optional rain/snow (hier bewusst nicht gesetzt)
    }

    def fake_urlopen(req, timeout=10):
        return _DummyHTTPResponse(json.dumps(fake_api_json))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    # API-Key muss existieren, sonst rc=2 → es wird ein Dummy-Key gegeben
    rc = main(["--ow-city", "Berlin", "--ow-key", "DUMMY_KEY"])
    out = capfd.readouterr().out

    assert rc == 0
    assert "Berlin" in out
    assert "6" in out or "6.5" in out  # je nach Rundung/Formatierung
