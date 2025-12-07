# tests/test_parse_weather.py
# -------------------------------------------------------------------------------
# Unit-Tests für weather_cli.py
#
# Zweck:
# - Diese Tests prüfen die Kernfunktionalität der CLI-Logik, ohne Netzwerkanfragen zu machen.
# - Getestet werden:
#   1) parse_weather_data: Extraktion der relevanten Felder aus einer API-Antwort.
#   2) display_weather: Formatierte Ausgabe auf stdout (mittels pytest capfd).
#   3) log_to_csv: CSV-Logging schreibt Header und Zeile (mittels pytest tmp_path).
#
# Hinweise:
# - Lege diese Datei im Repo-Root unter tests/test_parse_weather.py ab.
# - Ausführen: In aktivierter venv -> python -m pytest -q
# - Die Tests importieren Funktionen direkt aus weather_cli.py:
#     from weather_cli import parse_weather_data, display_weather, log_to_csv
# -------------------------------------------------------------------------------

import csv
import json
from typing import Dict, Any

import pytest

# Importiere die zu testenden Funktionen aus weather_cli.py.
# Achte darauf, dass weather_cli.py im Repo-Root liegt (dort, wo du pytest ausführst).
from weather_cli import parse_weather_data, display_weather, log_to_csv

# ---------------------------
# Helper: Beispiel-Antworten
# ---------------------------

def sample_api_response_full() -> Dict[str, Any]:
    """
    Repräsentative OpenWeatherMap-ähnliche Antwort mit allen relevanten Feldern.
    Diese Daten werden in test_parse_weather_full() verwendet.
    """
    return {
        "coord": {"lon": 13.3889, "lat": 52.5172},
        "weather": [
            {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
        ],
        "base": "stations",
        "main": {
            "temp": 6.5,
            "feels_like": 5.1,
            "temp_min": 5.0,
            "temp_max": 8.0,
            "pressure": 1012,
            "humidity": 81
        },
        "visibility": 10000,
        "wind": {"speed": 4.12, "deg": 240},
        "clouds": {"all": 75},
        "dt": 1605182400,
        "sys": {"type": 1, "id": 1275, "country": "DE", "sunrise": 1605153245, "sunset": 1605189245},
        "timezone": 3600,
        "id": 2950159,
        "name": "Berlin",
        "cod": 200
    }

def sample_api_response_missing_fields() -> Dict[str, Any]:
    """
    Beispiel-Antwort mit fehlenden Feldern:
    - kein 'name', kein 'temp' in 'main' und leeres 'weather' Array.
    Dient zur Prüfung der Robustheit von parse_weather_data.
    """
    return {
        "main": {
            # 'temp' fehlt absichtlich
            "humidity": 55
        },
        "weather": []  # leer, d. h. keine description
    }

# ---------------------------
# Tests für parse_weather_data
# ---------------------------

def test_parse_weather_full():
    """
    Testet, dass parse_weather_data aus einer vollständigen API-Antwort
    die erwarteten Felder extrahiert und raw JSON enthält.
    """
    # Erzeuge Beispiel-Antwort
    api_resp = sample_api_response_full()

    # Parse die Antwort
    parsed = parse_weather_data(api_resp)

    # Assertions: die extrahierten Werte müssen mit den Eingabedaten übereinstimmen
    assert parsed["location_name"] == "Berlin", "Ort sollte 'Berlin' sein"
    # Temperatur wird als Zahl erwartet; wir vergleichen mit Approx für Fließkomma-Sicherheit
    assert float(parsed["temperature_celsius"]) == pytest.approx(6.5, rel=1e-6)
    assert parsed["humidity_percent"] == 81, "Luftfeuchte sollte 81 sein"
    assert parsed["weather_description"] == "light rain", "Beschreibung sollte 'light rain' sein"
    # raw sollte ein nicht-leerer JSON-String sein; Validität prüfen
    assert parsed["raw"] is not None
    # Versuche, raw zu parsen -> sollte gültiges JSON sein
    json.loads(parsed["raw"])


def test_parse_weather_missing_fields():
    """
    Testet, dass parse_weather_data robust ist:
    - keine Exceptions bei fehlenden Feldern
    - fehlende Werte sind None
    """
    api_resp = sample_api_response_missing_fields()
    parsed = parse_weather_data(api_resp)

    # 'name' fehlt -> None
    assert parsed["location_name"] is None
    # 'temp' fehlt -> None
    assert parsed["temperature_celsius"] is None
    # humidity ist vorhanden -> übernommen
    assert parsed["humidity_percent"] == 55
    # weather list leer -> description None
    assert parsed["weather_description"] is None
    # raw kann String oder None sein (je nach Serialisierung); Hauptsache: keine Exception
    assert (parsed["raw"] is None) or isinstance(parsed["raw"], str)

# ---------------------------
# Test für display_weather (Ausgabe prüfen)
# ---------------------------

def test_display_weather_outputs_readable_text(capfd):
    """
    Testet, dass display_weather menschenlesbare Strings ausgibt.
    Wir fangen stdout mit pytest's capfd (capture file descriptors) ab und prüfen Inhalt.
    """
    # Erzeuge ein parsed-Dictionary wie es parse_weather_data liefert
    parsed = {
        "location_name": "Teststadt",
        "temperature_celsius": 12.345,  # float-Wert
        "humidity_percent": 42,
        "weather_description": "klarer Himmel",
        "raw": '{"dummy":true}'
    }

    # Rufe display_weather auf (diese Funktion gibt direkt auf stdout aus)
    display_weather(parsed)

    # capfd.readouterr() liefert captured stdout/stderr
    captured = capfd.readouterr()
    out = captured.out

    # Prüfe, dass die wichtigsten Teile in der Ausgabe vorkommen
    assert "Wetter für: Teststadt" in out
    # Temperaturformattierung: 12.345 -> 12.3 °C (eine Nachkommastelle)
    assert "Temperatur: 12.3 °C" in out
    assert "Luftfeuchte: 42" in out
    assert "Wetterbeschreibung: klarer Himmel" in out

# ---------------------------
# Test für log_to_csv (schreibt echte Datei in temporären Ordner)
# ---------------------------

def test_log_to_csv_creates_file_and_writes_header_and_row(tmp_path):
    """
    Testet, dass log_to_csv eine Datei erstellt (inkl. Header) und eine Zeile anhängt.
    Wir verwenden pytest tmp_path für einen temporären, isolierten Pfad.
    """
    # Pfad zur temporären CSV-Datei
    csv_file = tmp_path / "logs" / "test_logs.csv"
    # parsed-Daten, die log_to_csv erwartet (wie aus parse_weather_data)
    parsed = {
        "location_name": "SampleCity",
        "temperature_celsius": 3.14,
        "humidity_percent": 77,
        "weather_description": "nebel",
        "raw": '{"sample":true}'
    }

    # Aufruf der Funktion (soll Verzeichnisse anlegen und Datei schreiben)
    log_to_csv(str(csv_file), zip_code="12345", country_code="DE", result=parsed)

    # Prüfe, dass Datei existiert
    assert csv_file.exists(), "CSV-Datei sollte erstellt worden sein"

    # Öffne die Datei und prüfe Header + Anzahl der Zeilen (Header + 1 Datenzeile)
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Minimal: zwei Zeilen (Header + 1 Eintrag)
    assert len(rows) >= 2, "CSV sollte mindestens Header und eine Datenzeile enthalten"

    # Prüfe, dass Header die erwarteten Spaltennamen enthält
    header = rows[0]
    expected_header = [
        "timestamp_iso",
        "zip",
        "country",
        "location",
        "temperature_celsius",
        "humidity_percent",
        "weather_description",
        "raw_json"
    ]
    assert header == expected_header, f"Header stimmt nicht: {header}"

    # Prüfe, dass in der Datenzeile die Location und Temperatur vorkommen
    data_row = rows[1]
    assert "SampleCity" in data_row
    # Temperatur als String vorhanden (3.14) - einfache In-Check genügt
    assert any("3.14" in cell or "3.1" in cell for cell in data_row)

# End of tests
