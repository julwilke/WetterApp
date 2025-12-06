#####################################
# CLI-Version MVP der Wetterabfrage #
#####################################

# weather_cli.py
# Dieses Skript fragt die aktuelle Wetterlage für eine eingegebene Postleitzahl (PLZ) ab
# und gibt Temperatur, Luftfeuchte und eine kurze Wetterbeschreibung aus.
# Jede Zeile ist kommentiert, damit du genau siehst, was passiert und wo du später
# Erweiterungen einfügst.

# Standardbibliothek 'os' wird genutzt, um Umgebungsvariablen (API-Key) zu lesen.
import os  # os: Zugriff auf Umgebungsvariablen, Pfade etc.

# 'sys' wird verwendet, um ggf. das Programm mit einem Fehlercode zu beenden.
import sys  # sys: Beenden mit sys.exit, Zugriff auf argv falls nötig

# 'requests' wird verwendet, um HTTP-Anfragen an die Wetter-API zu senden.
import requests  # requests: einfache HTTP-Anfragen in Python

# 'typing' für optionale Typannotationen (Verbesserung der Lesbarkeit).
from typing import Optional, Dict  # Optional, Dict: Typen für Funktionsergebnisse

# Konstanten definieren: Basis-URL der OpenWeatherMap-API für den aktuellen Wetterabruf.
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"  # Basis-Endpunkt für "current weather"

# Hilfsfunktion: API-Key aus der Umgebungsvariable holen.
def get_api_key() -> Optional[str]:
    # Lies den API-Key aus der Umgebungsvariablen 'OPENWEATHER_API_KEY'.
    api_key = os.getenv("OPENWEATHER_API_KEY")  # os.getenv: gibt None zurück, wenn Variable nicht gesetzt
    # Wenn kein API-Key gesetzt ist, gib None zurück (Aufrufer kann Fehler behandeln).
    return api_key  # Rückgabe des API-Keys oder None

# Hilfsfunktion: Baut die Anfrage-Parameter für OpenWeatherMap zusammen.
def build_query_params(zip_code: str, country_code: str = "DE", units: str = "metric") -> Dict[str, str]:
    # OpenWeatherMap akzeptiert ein 'zip' Parameter der Form "PLZ,COUNTRYCODE" (z.B. "10115,DE").
    zip_param = f"{zip_code},{country_code}"  # Erzeuge das zip-Argument
    # Erzeuge das Dict mit Parametern; apiKey wird später ergänzt.
    params = {"zip": zip_param, "units": units}  # units=metric → Temperatur in Celsius
    return params  # Rückgabe der Basis-Parameter (ohne apiKey)

# Hauptfunktion: Führt die Anfrage aus und gibt strukturierte Daten zurück.
def fetch_current_weather(api_key: str, zip_code: str, country_code: str = "DE") -> Dict:
    # Baue die Basis-Parameter zusammen.
    params = build_query_params(zip_code, country_code)  # Basis-Parameter (zip, units)
    # Füge den API-Key zu den Parametern hinzu.
    params["appid"] = api_key  # 'appid' ist der Parametername für den OpenWeatherMap API-Key
    # Sende die GET-Anfrage an die API.
    response = requests.get(OPENWEATHER_URL, params=params, timeout=10)  # timeout in Sekunden setzen
    # Prüfe, ob der HTTP-Statuscode 200 (OK) ist; wenn nicht, werfe einen Fehler mit Info.
    if response.status_code != 200:
        # Versuche, die Fehlermeldung aus der API-Antwort zu lesen; falls nicht möglich, zeige Statuscode.
        try:
            err = response.json()  # JSON-Fehlerantwort parsen
        except ValueError:
            err = {"message": f"HTTP {response.status_code} ohne JSON-Antwort"}  # Fallback-Fehlerinfo
        # Hebe eine Exception mit hilfreicher Information, damit der Aufrufer es behandeln kann.
        raise RuntimeError(f"API-Anfrage fehlgeschlagen: {response.status_code} - {err}")
    # Wenn die Antwort OK ist, parse das JSON und gib es zurück.
    return response.json()  # Rückgabe des geparsten JSON-Dictionaries

# Hilfsfunktion: Extrahiert die gewünschten Informationen (Temperatur, Luftfeuchte, Beschreibung).
def parse_weather_data(api_response: Dict) -> Dict[str, Optional[str]]:
    # Standardmäßige Rückstruktur mit Default-Werten zur Robustheit.
    result = {
        "location_name": None,  # z.B. "Berlin"
        "temperature_celsius": None,  # z.B. 5.2
        "humidity_percent": None,  # z.B. 87
        "weather_description": None,  # z.B. "light rain"
    }
    # Versuche, den Ortsnamen (name) zu lesen.
    result["location_name"] = api_response.get("name")  # 'name' ist der Ortsname laut API
    # 'main' enthält Temperatur und Luftfeuchte – sichere Zugriffe mit .get.
    main = api_response.get("main", {})  # 'main' ist ein dict, fallback zu leerem dict
    result["temperature_celsius"] = main.get("temp")  # 'temp' ist Temperatur in gewählten Units
    result["humidity_percent"] = main.get("humidity")  # 'humidity' ist in Prozent
    # 'weather' ist üblicherweise eine Liste; wir nehmen das erste Element und dessen 'description'.
    weather_list = api_response.get("weather", [])  # fallback: leere Liste
    if weather_list and isinstance(weather_list, list):
        # Falls vorhanden, nimm die Beschreibung des ersten Eintrags.
        result["weather_description"] = weather_list[0].get("description")
    # Gib das strukturierte Ergebnis zurück.
    return result  # Rückgabe des aufbereiteten Results

# Ausgabe-Funktion: Formatiert und druckt die Daten in der Konsole.
def display_weather(parsed: Dict[str, Optional[str]]) -> None:
    # Lese einzelne Felder aus dem Dictionary mit Fallbacks.
    location = parsed.get("location_name") or "Unbekannter Ort"  # Fallback-Text wenn kein Name vorhanden
    temp = parsed.get("temperature_celsius")  # Temperatur (kann None sein)
    humidity = parsed.get("humidity_percent")  # Luftfeuchte (kann None sein)
    desc = parsed.get("weather_description") or "Keine Beschreibung verfügbar"  # Fallback-Beschreibung
    # Drucke eine klare Kopfzeile mit Ort.
    print(f"Wetter für: {location}")  # z.B. "Wetter für: Berlin"
    # Wenn Temperatur vorhanden, formatiere sie schön (eine Nachkommastelle), ansonsten Hinweis.
    if temp is not None:
        try:
            # Versuche, die Temperatur als Float zu behandeln und formatiere auf 1 Nachkommastelle.
            temp_num = float(temp)  # Umwandlung zu float
            print(f"Temperatur: {temp_num:.1f} °C")  # Ausgabe z. B. "Temperatur: 4.7 °C"
        except (TypeError, ValueError):
            # Falls die Temperatur nicht in ein Float umgewandelt werden kann, gebe Rohwert aus.
            print(f"Temperatur: {temp}")  # Roh-Angabe
    else:
        # Wenn kein Temperaturwert vorhanden ist, Hinweis ausgeben.
        print("Temperatur: Keine Daten verfügbar")  # Hinweis
    # Wenn Luftfeuchte vorhanden, gib sie aus, sonst Hinweis.
    if humidity is not None:
        print(f"Luftfeuchte: {humidity} %")  # Ausgabe z. B. "Luftfeuchte: 72 %"
    else:
        print("Luftfeuchte: Keine Daten verfügbar")  # Hinweis
    # Drucke die Wetterbeschreibung (z. B. "leichter Regen").
    print(f"Wetterbeschreibung: {desc}")  # Ausgabe der Beschreibung

# Funktion zum Einlesen der PLZ vom Benutzer (kann später durch CLI-Argumente ersetzt werden).
def prompt_for_zip() -> str:
    # Fordere den Benutzer zur Eingabe der Postleitzahl auf.
    zip_code = input("Bitte Postleitzahl (z.B. 10115) eingeben: ").strip()  # input() & strip() zum Säubern
    # Wenn der Benutzer nichts eingegeben hat, beende das Programm mit einer freundlichen Meldung.
    if not zip_code:
        print("Keine Postleitzahl eingegeben. Abbruch.")  # Meldung
        sys.exit(1)  # Beenden mit Fehlercode 1
    # Gib die eingelesene PLZ zurück.
    return zip_code  # Rückgabe der PLZ als String

# Hauptprogramm / Entrypoint
def main() -> None:
    # Lies den API-Key.
    api_key = get_api_key()  # Hole API-Key aus Umgebungsvariablen
    # Wenn kein API-Key vorhanden ist, informiere den Benutzer und beende.
    if not api_key:
        print("Fehler: OPENWEATHER_API_KEY ist nicht gesetzt.")  # Fehlermeldung
        print("Setze die Umgebungsvariable OPENWEATHER_API_KEY und versuche es erneut.")  # Hilfestellung
        sys.exit(2)  # Beende mit anderem Fehlercode
    # Frage den Benutzer nach der PLZ.
    zip_code = prompt_for_zip()  # Lese PLZ
    # Optional: Standard-Ländercode 'DE' verwenden; später durch optionalen Parameter erweiterbar.
    country_code = "DE"  # Default-Ländercode
    # Versuche die API zu kontaktieren und Daten zu holen; fange Fehler ab um hilfreiche Meldungen zu geben.
    try:
        api_response = fetch_current_weather(api_key=api_key, zip_code=zip_code, country_code=country_code)  # API-Call
    except Exception as e:
        # Bei einem Fehler während der Anfrage: Fehlermeldung zeigen und beenden.
        print(f"Fehler beim Abrufen der Wetterdaten: {e}")  # Fehlerausgabe
        sys.exit(3)  # Beenden mit Fehlercode 3
    # Wenn Anfrage erfolgreich war, parse die Rückgabe.
    parsed = parse_weather_data(api_response)  # Daten aufbereiten
    # Zeige die Daten in der Konsole an.
    display_weather(parsed)  # Ausgabe

# Standard-Python-Idiom um main() auszuführen, wenn das Skript direkt gestartet wird.
if __name__ == "__main__":
    # Aufruf von main(), Programmstart.
    main()  # Start der Anwendung