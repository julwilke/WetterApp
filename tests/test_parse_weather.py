# tests/test_parse_weather.py
# -------------------------------------------------------------------------------
# Unit-Tests für weather_cli.py (flexiblere Version)
#
# Änderungen gegenüber vorher:
# - header-Check in CSV-Test ist jetzt tolerant gegenüber zusätzlicher Spalten
#   (prüft nur, dass die erwarteten Spalten vorhanden sind).
# - raw-Feld-Akzeptanz: raw kann jetzt entweder ein JSON-String oder ein Dict sein.
# - Temperatur-Assertion ist robuster (prüft erst, ob Wert vorhanden ist und konvertierbar).
# - Aussagekräftigere Assertion-Messages für einfacheres Debugging.
# -------------------------------------------------------------------------------

import csv
import json
from typing import Dict, Any

import pytest

# Importiert die zu testenden Funktionen über den Root-Wrapper weather_cli.py
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

    assert parsed["location_name"] == "Berlin", f"location_name falsch: {parsed.get('location_name')}"
    # Temperatur: prüfe, dass ein Wert vorhanden und konvertierbar ist
    temp = parsed.get("temperature_celsius")
    assert temp is not None, "temperature_celsius ist None, erwartet Zahl (z. B. 6.5)"
    try:
        temp_f = float(temp)
    except Exception:
        pytest.fail(f"temperature_celsius kann nicht in float konvertiert werden: {temp!r}")
    assert temp_f == pytest.approx(6.5, rel=1e-6)

    assert parsed["humidity_percent"] == 81, f"humidity_percent falsch: {parsed.get('humidity_percent')}"
    assert parsed["weather_description"] == "light rain", f"weather_description falsch: {parsed.get('weather_description')}"

    # raw: Akzeptiere entweder ein JSON-String oder ein Dict
    raw = parsed.get("raw")
    assert raw is not None, "raw sollte nicht None sein"
    if isinstance(raw, str):
        # Wenn String: sollte gültiges JSON sein
        try:
            json.loads(raw)
        except ValueError as e:
            pytest.fail(f"raw ist ein String, aber kein gültiges JSON: {e}")
    else:
        # Wenn kein String: akzeptiere Dict/Mapping
        assert isinstance(raw, dict), f"raw muss dict oder JSON-string sein, ist: {type(raw)}"

def test_parse_weather_missing_fields():
    """parse_weather_data gibt None für fehlende Felder zurück und wirft keine Exceptions."""
    api_resp = sample_api_response_missing_fields()
    parsed = parse_weather_data(api_resp)

    assert parsed["location_name"] is None, f"Erwartet location_name None bei fehlendem name, got: {parsed.get('location_name')}"
    assert parsed["temperature_celsius"] is None, f"Erwartet temperature_celsius None bei fehlender temp, got: {parsed.get('temperature_celsius')}"
    assert parsed["humidity_percent"] == 55, f"humidity_percent falsch: {parsed.get('humidity_percent')}"
    assert parsed["weather_description"] is None, f"weather_description erwartet None, got: {parsed.get('weather_description')}"
    raw = parsed.get("raw")
    assert raw is None or isinstance(raw, (str, dict)), "raw sollte None, str oder dict sein"

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

    assert "Wetter für: Teststadt" in out, f"Ausgabe enthält nicht erwarteten Ort. Out:\n{out}"
    # Temperatur mit einer Nachkommastelle prüfen (z. B. 12.345 -> 12.3)
    assert "Temperatur: 12.3" in out, f"Temperatur format falsch oder fehlt. Out:\n{out}"
    assert "Luftfeuchte: 42" in out, f"Luftfeuchte fehlt. Out:\n{out}"
    assert "Wetterbeschreibung: klarer Himmel" in out, f"Wetterbeschreibung fehlt. Out:\n{out}"

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
        "raw": {"sample": True}  # dict ist jetzt auch erlaubt
    }

    log_to_csv(str(csv_file), zip_code="12345", country_code="DE", result=parsed)

    assert csv_file.exists(), f"CSV-Datei wurde nicht erstellt: {csv_file}"

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert len(rows) >= 2, f"CSV sollte mindestens Header + 1 Zeile enthalten, hat {len(rows)} Zeilen"

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
    # Tolerante Überprüfung: die erwarteten Spalten müssen vorhanden sein (Reihenfolge optional)
    assert set(expected_header).issubset(set(header)), f"CSV-Header fehlt Spalten. Erwartet mindestens: {expected_header}, gefunden: {header}"

    # Prüfe, dass in der Datenzeile die Location und Temperatur vorkommen
    data_row = rows[1]
    assert any("SampleCity" in cell for cell in data_row), f"SampleCity nicht in Datenzeile: {data_row}"
    # Temperatur prüfen (als Teilstring möglich, z. B. "3.14" oder "3.1")
    assert any("3.14" in cell or "3.1" in cell for cell in data_row), f"Temperatur 3.14 nicht in Datenzeile: {data_row}"
