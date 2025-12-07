# tests/test_parse_weather.py
# Unit-Tests für die CLI-Parser-, Ausgabe- und Logging-Funktionen.
# Diese Datei soll unter <repo-root>/tests/test_parse_weather.py liegen.
#
# Wichtig:
# - Die Tests importieren aus weather_cli (Wrapper im Repo-Root).
# - Stelle sicher, dass weather_cli.py (Wrapper) vorhanden ist, damit die Tests laufen.
#
# Ausführen:
# - In einer aktivierten venv: python -m pytest -q

import csv
import json
from typing import Dict, Any

import pytest

# Importiere die zu testenden Funktionen über den Root-Wrapper weather_cli.py
from weather_cli import parse_weather_data, display_weather, log_to_csv

# ---------------------------
# Helper: Beispiel-Antworten
# ---------------------------

def sample_api_response_full() -> Dict[str, Any]:
    """Repräsentative OpenWeatherMap-ähnliche Antwort mit allen relevanten Feldern."""
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
    """Beispiel-Antwort mit fehlenden Feldern (Robustheitstest)."""
    return {
        "main": {
            # 'temp' fehlt absichtlich
            "humidity": 55
        },
        "weather": []  # leer -> keine description
    }

# ---------------------------
# Tests für parse_weather_data
# ---------------------------

def test_parse_weather_full():
    """parse_weather_data extrahiert die erwarteten Felder aus einer vollständigen Antwort."""
    api_resp = sample_api_response_full()
    parsed = parse_weather_data(api_resp)

    assert parsed["location_name"] == "Berlin"
    assert float(parsed["temperature_celsius"]) == pytest.approx(6.5, rel=1e-6)
    assert parsed["humidity_percent"] == 81
    assert parsed["weather_description"] == "light rain"
    assert parsed["raw"] is not None
    json.loads(parsed["raw"])  # raw muss gültiges JSON sein

def test_parse_weather_missing_fields():
    """parse_weather_data gibt None für fehlende Felder zurück und wirft keine Exceptions."""
    api_resp = sample_api_response_missing_fields()
    parsed = parse_weather_data(api_resp)

    assert parsed["location_name"] is None
    assert parsed["temperature_celsius"] is None
    assert parsed["humidity_percent"] == 55
    assert parsed["weather_description"] is None
    assert (parsed["raw"] is None) or isinstance(parsed["raw"], str)

# ---------------------------
# Test für display_weather (stdout output)
# ---------------------------

def test_display_weather_outputs_readable_text(capfd):
    """display_weather gibt formatierte, menschenlesbare Strings auf stdout aus."""
    parsed = {
        "location_name": "Teststadt",
        "temperature_celsius": 12.345,
        "humidity_percent": 42,
        "weather_description": "klarer Himmel",
        "raw": '{"dummy":true}'
    }

    display_weather(parsed)

    captured = capfd.readouterr()
    out = captured.out

    assert "Wetter für: Teststadt" in out
    assert "Temperatur: 12.3 °C" in out
    assert "Luftfeuchte: 42" in out
    assert "Wetterbeschreibung: klarer Himmel" in out

# ---------------------------
# Test für log_to_csv (schreibt Datei in tmp_path)
# ---------------------------

def test_log_to_csv_creates_file_and_writes_header_and_row(tmp_path):
    """log_to_csv legt eine CSV an (inkl. Header) und hängt eine Datenzeile an."""
    csv_file = tmp_path / "logs" / "test_logs.csv"
    parsed = {
        "location_name": "SampleCity",
        "temperature_celsius": 3.14,
        "humidity_percent": 77,
        "weather_description": "nebel",
        "raw": '{"sample":true}'
    }

    log_to_csv(str(csv_file), zip_code="12345", country_code="DE", result=parsed)

    assert csv_file.exists()

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert len(rows) >= 2

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
    assert header == expected_header

    data_row = rows[1]
    assert "SampleCity" in data_row
    assert any("3.14" in cell or "3.1" in cell for cell in data_row)
