# weather_cli.py
#
# Ziele:
# - Klarer und stabiler Ablauf (Argumente → dotenv → API-Aufruf → Parsing → Ausgabe → optionales Logging)
# - Saubere Fehlerbehandlung mit verständlichen Meldungen und Exit-Codes
# - Leicht testbar (parse_weather_data ist rein funktional)
#
# Kurz: Diese Datei ist die empfohlene "Endfassung" eurer weather CLI.
import os                      # für Umgebungsvariablen & Dateisystemfunktionen
import sys                     # für sys.exit mit Exit-Codes
import csv                     # CSV-Logging
import json                    # JSON Serialisierung
import time                    # UTC Zeitstempel
from typing import Optional, Dict, Tuple  # Typinformationen zur Lesbarkeit
import argparse                # Kommandozeilenargumente parsen
import requests                # HTTP-Client für API-Aufrufe

# python-dotenv ist optional; falls installiert, kann .env automatisch geladen werden
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except Exception:
    load_dotenv = None
    DOTENV_AVAILABLE = False

# ---------------------
# Konfiguration / Defaults
# ---------------------
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"  # OpenWeatherMap Current Weather API
HTTP_TIMEOUT = 10            # Sekunden; verhindert, dass requests ewig blockiert
DEFAULT_COUNTRY = "DE"       # Default-Ländercode, wenn nichts eingegeben wird
DEFAULT_UNITS = "metric"     # metric => Temperatur in °C

# ---------------------
# Hilfsfunktionen
# ---------------------

def optional_load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """
    Versucht, eine .env-Datei zu laden (falls python-dotenv installiert ist).
    - dotenv_path: optionaler Pfad zur .env; wenn None => load_dotenv() versucht Standard-Datei.
    - Keine Ausnahme wenn python-dotenv fehlt; Funktion ist eine no-op dann.
    """
    if DOTENV_AVAILABLE:
        if dotenv_path:
            load_dotenv(dotenv_path)
        else:
            load_dotenv()
    else:
        # dotenv nicht installiert: nichts tun — Nutzer kann Umgebungsvariablen manuell setzen
        return

def get_api_key() -> Optional[str]:
    """
    Liest OPENWEATHER_API_KEY aus der Umgebung und gibt ihn zurück.
    - Rückgabe: API-Key string oder None wenn nicht gesetzt.
    """
    return os.getenv("OPENWEATHER_API_KEY")

def build_query_params(zip_code: str, country_code: str = DEFAULT_COUNTRY, units: str = DEFAULT_UNITS) -> Dict[str, str]:
    """
    Baut das Query-Parameter-Dict für OpenWeatherMap.
    - OpenWeatherMap erwartet 'zip' im Format 'PLZ,COUNTRY' (z.B. '10115,DE').
    - 'units' erlaubt 'metric' (°C).
    """
    zip_param = f"{zip_code},{country_code}"
    return {"zip": zip_param, "units": units}

def fetch_current_weather(api_key: str, zip_code: str, country_code: str = DEFAULT_COUNTRY) -> Dict:
    """
    Ruft die OpenWeatherMap Current Weather API ab und gibt das geparste JSON zurück.
    - Bei Netzwerk- oder API-Fehlern wird eine RuntimeError mit klarer Nachricht geworfen.
    """
    params = build_query_params(zip_code, country_code)
    params["appid"] = api_key  # OpenWeatherMap erwartet 'appid' als Key-Parameter

    try:
        # Timeout verwenden, um Hänger zu vermeiden
        response = requests.get(OPENWEATHER_URL, params=params, timeout=HTTP_TIMEOUT)
    except requests.exceptions.RequestException as e:
        # Netwerkfehler (Timeout, DNS, Verbindung) => erklärbare RuntimeError
        raise RuntimeError(f"Netzwerkfehler beim Aufruf der Wetter-API: {e}") from e

    # Prüfe HTTP-Status
    if response.status_code != 200:
        # Versuche eine API-Fehlermeldung aus JSON zu lesen, sonst nimm Text/Status
        try:
            err = response.json()
        except ValueError:
            err = {"message": response.text or f"HTTP {response.status_code}"}
        raise RuntimeError(f"API-Anfrage fehlgeschlagen: {response.status_code} - {err}")

    # Parse JSON und gib es zurück
    try:
        return response.json()
    except ValueError as e:
        # Unwahrscheinlicher Fehler: ungültiges JSON
        raise RuntimeError(f"API-Antwort konnte nicht als JSON geparst werden: {e}") from e

def parse_weather_data(api_response: Dict) -> Dict[str, Optional[str]]:
    """
    Extrahiert die wichtigsten Felder aus der API-Antwort.
    - Gibt ein Dict mit keys: location_name, temperature_celsius, humidity_percent, weather_description, raw
    - Werte können None sein, falls Daten fehlen; Funktion ist deterministisch und ohne Seiteneffekte —
      daher leicht zu testen.
    """
    result = {
        "location_name": None,
        "temperature_celsius": None,
        "humidity_percent": None,
        "weather_description": None,
        "raw": None,
    }

    # Ortsname (falls vorhanden)
    result["location_name"] = api_response.get("name")

    # Hauptdaten (temp, humidity)
    main = api_response.get("main", {})
    result["temperature_celsius"] = main.get("temp")
    result["humidity_percent"] = main.get("humidity")

    # Wetterbeschreibung: 'weather' ist typischerweise eine Liste mit mindestens einem Eintrag
    weather_list = api_response.get("weather", [])
    if weather_list and isinstance(weather_list, list):
        result["weather_description"] = weather_list[0].get("description")

    # Raw JSON als kompakter String für Logging/Debug
    try:
        result["raw"] = json.dumps(api_response, ensure_ascii=False)
    except Exception:
        result["raw"] = None

    return result

def display_weather(parsed: Dict[str, Optional[str]]) -> None:
    """
    Formatiert und gibt die Wetterinfos auf der Konsole aus.
    - Nutzt verständliche Fallbacks falls Werte fehlen.
    """
    # Defensives Lesen der Felder
    location = parsed.get("location_name") or "Unbekannter Ort"
    temp = parsed.get("temperature_celsius")
    humidity = parsed.get("humidity_percent")
    desc = parsed.get("weather_description") or "Keine Beschreibung verfügbar"

    # Ausgabe: Ort
    print(f"Wetter für: {location}")

    # Ausgabe: Temperatur (falls vorhanden) mit 1 Dezimalstelle, sonst Rohwert oder Hinweis
    if temp is not None:
        try:
            temp_num = float(temp)
            print(f"Temperatur: {temp_num:.1f} °C")
        except (TypeError, ValueError):
            print(f"Temperatur (Roh): {temp}")
    else:
        print("Temperatur: Keine Daten verfügbar")

    # Ausgabe: Luftfeuchte
    if humidity is not None:
        print(f"Luftfeuchte: {humidity} %")
    else:
        print("Luftfeuchte: Keine Daten verfügbar")

    # Ausgabe: Beschreibung
    print(f"Wetterbeschreibung: {desc}")

def log_to_csv(csv_path: str, zip_code: str, country_code: str, result: Dict) -> None:
    """
    Hängt eine Zeile mit Abfrageergebnis an die CSV an.
    - Schreibt Header, falls Datei neu ist.
    - Verwaltet Verzeichniserstellung und Windows-newline Verhalten.
    - Fehler beim Loggen führen nur zu einer Warnung (keine Exception).
    """
    try:
        # Verzeichnis sicherstellen (z.B. logs/)
        dirpath = os.path.dirname(csv_path)
        if dirpath:
            try:
                os.makedirs(dirpath, exist_ok=True)
            except Exception:
                # Wenn Ordner nicht erstellt werden kann, fahren wir fort (Open kann später fehlschlagen)
                pass

        # Öffne Datei im Append-Modus; newline="" vermeidet CRLF-Doppelzeilen in Windows
        with open(csv_path, mode="a", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "timestamp_iso",
                "zip",
                "country",
                "location",
                "temperature_celsius",
                "humidity_percent",
                "weather_description",
                "raw_json"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Prüfe, ob Datei neu ist (Header schreiben)
            try:
                is_new = os.path.getsize(csv_path) == 0
            except OSError:
                # Datei existiert nicht oder ist nicht zugreifbar -> behandeln als neu
                is_new = True

            if is_new:
                writer.writeheader()

            # Schreibe Zeile mit UTC-Zeitstempel
            writer.writerow({
                "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "zip": zip_code,
                "country": country_code,
                "location": result.get("location_name") or "",
                "temperature_celsius": result.get("temperature_celsius") or "",
                "humidity_percent": result.get("humidity_percent") or "",
                "weather_description": result.get("weather_description") or "",
                "raw_json": result.get("raw") or ""
            })
    except Exception as e:
        # Logging-Fehler: nur Warnung ausgeben (keine Programmbeendigung)
        print(f"Warnung: Konnte nicht in CSV loggen ({csv_path}): {e}")

def prompt_for_zip_interactive() -> Tuple[str, str]:
    """
    Fragt den Nutzer interaktiv nach PLZ und optionalem Ländercode.
    - Beendet das Programm mit Exit-Code 1, wenn keine PLZ eingegeben wird.
    """
    zip_code = input("Bitte Postleitzahl (z.B. 10115) eingeben: ").strip()
    if not zip_code:
        print("Keine Postleitzahl eingegeben. Abbruch.")
        sys.exit(1)
    country_code = input(f"Optionaler Ländercode (zwei Buchstaben, Default: {DEFAULT_COUNTRY}): ").strip() or DEFAULT_COUNTRY
    return zip_code, country_code

# ---------------------
# Hauptprogramm / Entrypoint
# ---------------------
def main() -> None:
    """
    Programm-Flow:
    1) Argumente parsen
    2) optional .env laden
    3) API-Key prüfen (OPENWEATHER_API_KEY)
    4) PLZ/Land ermitteln (Arg oder interaktiv)
    5) API aufrufen
    6) Antwort parsen und anzeigen
    7) optional in CSV loggen
    """
    # Argparse Setup
    parser = argparse.ArgumentParser(description="Wetter CLI: PLZ -> aktuelles Wetter (OpenWeatherMap).")

    # --zip / -z: Postleitzahl (optional)
    parser.add_argument("--zip", "-z", dest="zip_code", help="Postleitzahl (z.B. 10115). Wenn nicht gesetzt, wird interaktiv gefragt.")
    # --country / -c: Ländercode (Default DEFAULT_COUNTRY)
    parser.add_argument("--country", "-c", dest="country_code", default=DEFAULT_COUNTRY, help=f"Ländercode (2 Buchstaben). Default: {DEFAULT_COUNTRY}")
    # --log-csv: Pfad, an den Logs angehängt werden sollen
    parser.add_argument("--log-csv", dest="log_csv", help="CSV-Dateipfad zum Anfügen der Abfrage-Logs (z.B. logs/logs.csv).")
    # --dotenv: optionaler Pfad zu einer .env Datei
    parser.add_argument("--dotenv", dest="dotenv_path", help="Optional: Pfad zu einer .env-Datei, die geladen werden soll (z.B. .env).")
    # --raw: zeigt die rohe API-Antwort (JSON)
    parser.add_argument("--raw", dest="raw", action="store_true", help="Gibt die rohe API-Antwort aus (Debug).")

    # Parse die Kommandozeilenargumente
    args = parser.parse_args()

    # Lade .env falls vorhanden oder angefragt
    if args.dotenv_path:
        optional_load_dotenv(args.dotenv_path)
    else:
        optional_load_dotenv()

    # Lese API-Key (möglicherweise durch .env gesetzt)
    api_key = get_api_key()
    if not api_key:
        # Kein Key -> verständliche Nachricht und saubere Beendigung
        print("Fehler: OPENWEATHER_API_KEY ist nicht gesetzt. Setze die Umgebungsvariable oder nutze --dotenv.")
        print("Beispiel (PowerShell): $env:OPENWEATHER_API_KEY='DEIN_KEY'")
        sys.exit(2)  # Exit-Code 2: fehlende Konfiguration / API-Key

    # PLZ & Ländercode bestimmen: CLI-Argumente haben Vorrang
    if args.zip_code:
        zip_code = args.zip_code.strip()
        country_code = args.country_code.strip()
    else:
        zip_code, country_code = prompt_for_zip_interactive()

    # API-Aufruf und Fehlerbehandlung
    try:
        api_response = fetch_current_weather(api_key=api_key, zip_code=zip_code, country_code=country_code)
    except Exception as e:
        print(f"Fehler beim Abrufen der Wetterdaten: {e}")
        sys.exit(3)  # Exit-Code 3: Fehler bei API/Netzwerk

    # Parse die Antwort in die relevanten Felder
    parsed = parse_weather_data(api_response)

    # Optional: rohe JSON-Antwort ausgeben (für Debug)
    if args.raw:
        print("=== ROHE API-ANTWORT ===")
        try:
            print(json.dumps(api_response, indent=2, ensure_ascii=False))
        except Exception:
            print(repr(api_response))
        print("========================")

    # Anzeige der aufbereiteten Informationen
    display_weather(parsed)

    # Optionales Logging in CSV
    if args.log_csv:
        csv_path = args.log_csv
        log_to_csv(csv_path, zip_code, country_code, parsed)

# Standard-Eintrittspunkt: nur ausführen, wenn Datei direkt gestartet wird
if __name__ == "__main__":
    main()
