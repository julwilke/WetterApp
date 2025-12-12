# Vollständig und sehr detailliert kommentierte Version von cli/cli.py
# Dieses CLI-Tool zeigt Wetterdaten an (aus CSV oder via OpenWeather API),
# loggt optional in eine CSV-Datei und unterstützt erweiterte Felder wie
# city, precipitation, wind, humidity, pressure und clouds.
#
# Hinweise:
# - Speichere diese Datei als cli/cli.py in deinem Projektverzeichnis.
# - Falls du die Datei ersetzt, lösche ggf. das Verzeichnis __pycache__.
# - Testaufrufe siehe weiter unten in den Instruktionen.

from __future__ import annotations  # Ermöglicht modernere Typannotationen (z.B. Optional[List[str]]) in älteren Python-Versionen

# Standardbibliotheken, die wir benötigen:
import argparse            # zum Parsen der Kommandozeilen-Argumente
import csv                 # zum Lesen/Schreiben von CSV-Dateien
import io                  # StringIO wird verwendet, um CSV-Text zu lesen wie eine Datei
import sys                 # für sys.argv und Exit-Codes
import os                  # für Umgebungsvariablen (z. B. OPENWEATHER_API_KEY)
import json                # für JSON-Dumps bei --format json
import urllib.request      # für einfache HTTP-Anfragen zur OpenWeather API
import urllib.parse        # um Query-Parameter URL-encodiert anzuhängen
from datetime import datetime, timezone  # für Zeitstempel (UTC)
from typing import List, Dict, Optional, Any, Sequence  # Typ-Hinweise für bessere Lesbarkeit

# ---------------------------------------------------------------------------
# Hilfsfunktionen zur Normalisierung und Parsing
# ---------------------------------------------------------------------------

def _normalize_value(v: Any) -> str:
    """
    Normiert einen einzelnen CSV-Zellwert zu einem sauberen String.
    - Wenn csv.DictReader mehrere Spalten mit demselben Header liefert, kann v eine Liste sein.
      In diesem Fall verbinden wir die Listenelemente per Komma.
    - None wird zu einem leeren String.
    - Abschließend entfernen wir führende und trailing Whitespaces.
    """
    if isinstance(v, list):
        # Falls Mehrfach-Spalten mit gleichem Header: kombiniere zu einem String
        v = ",".join(str(x) for x in v)
    if v is None:
        # Keine None-Werte zurückgeben, sondern leeren String
        return ""
    # Str-Konvertierung und Trim
    return str(v).strip()


def parse_weather_data(raw: str) -> List[Dict[str, str]]:
    """
    Parst Roh-CSV-Text (ganze Datei als String) und gibt eine Liste von Dicts zurück.
    - Header-Namen werden bereinigt (BOM entfernt, getrimmt, lowercased).
    - Werte werden mittels _normalize_value normalisiert.
    - Rückgabe: List[Dict[str, str]]; jede Dict repräsentiert eine Zeile.
    """
    # Entferne einen möglichen UTF-8 BOM (Byte Order Mark) am Anfang der Datei.
    # BOM macht den Header "\ufeffdate" statt "date" - das führt zu fehlenden Spalten.
    if raw and raw.startswith("\ufeff"):
        raw = raw.lstrip("\ufeff")

    # Vereinheitliche Zeilenenden (Windows CRLF -> LF), so ist das Parsing plattformunabhängig.
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")

    # Verwende csv.DictReader über einen String-Stream (io.StringIO)
    reader = csv.DictReader(io.StringIO(raw))
    rows: List[Dict[str, str]] = []

    # Iteriere über alle Zeilen, bereinige Header-Keys und Werte, füge zur Ergebnisliste hinzu.
    for row in reader:
        normalized: Dict[str, str] = {}
        for k, v in row.items():
            # Key-Bereinigung:
            # - Falls k None ist, ersetze durch leeren String
            # - entferne Whitespaces
            # - entferne evtl. führendes BOM (falls noch vorhanden)
            # - mache lowercase, damit Header-Fallunterschiede egal sind
            key = (k or "").strip().lstrip("\ufeff").lower()
            # Value-Normalisierung (z. B. Lists -> String, None -> "")
            val = _normalize_value(v)
            normalized[key] = val
        rows.append(normalized)

    return rows


def _pick_first(row: Dict[str, str], candidates: Sequence[str]) -> Optional[str]:
    """
    Hilfsfunktion: gib den ersten nicht-leeren Wert für eine Liste möglicher Schlüssel zurück.
    Nützlich, um verschiedene Varianten eines Feldnamens in CSVs zu unterstützen.
    """
    for c in candidates:
        if c in row and row[c] != "":
            return row[c]
    return None


def _extract_precipitation_from_row(row: Dict[str, str]) -> Optional[str]:
    """
    Suche in CSV-Reihen nach üblichen Niederschlags-Feldern:
    precipitation, rain_1h, rain, snow_1h, snow
    """
    val = _pick_first(row, ("precipitation", "rain_1h", "rain", "snow_1h", "snow"))
    return val


def _extract_wind_from_row(row: Dict[str, str]) -> Dict[str, str]:
    """
    Extrahiere Windgeschwindigkeit und -richtung aus CSV-Reihen.
    Unterstützte Header-Beispiele:
    - speed: wind_speed, wind, wind_s, wind_kmh, wind_kph
    - direction: wind_deg, wind_dir, wind_direction
    Gibt ein Dict mit keys 'wind_speed' und 'wind_deg' zurück (leer falls nicht vorhanden).
    """
    speed = _pick_first(row, ("wind_speed", "wind", "wind_s", "wind_kmh", "wind_kph"))
    deg = _pick_first(row, ("wind_deg", "wind_dir", "wind_direction"))
    return {"wind_speed": speed or "", "wind_deg": deg or ""}


def _extract_common_from_api(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extrahiere gängige Felder aus der OpenWeather-API-Antwort.
    Wir geben alle Werte als Strings zurück (leeren String, wenn nicht vorhanden).
    Erwartete Felder: temp, description, precipitation, wind_speed, wind_deg, humidity, pressure, clouds
    """
    out: Dict[str, str] = {}

    # Temperatur aus data['main']['temp'] entnehmen, falls vorhanden
    try:
        out["temp"] = str(data.get("main", {}).get("temp", ""))
    except Exception:
        out["temp"] = ""

    # Beschreibung aus data['weather'][0]['description']
    try:
        weather_list = data.get("weather", [])
        out["description"] = weather_list[0].get("description", "") if weather_list else ""
    except Exception:
        out["description"] = ""

    # Niederschlag (regen/schnee) — prüfe 'rain' zuerst, dann 'snow'
    pr = ""
    if "rain" in data:
        r = data["rain"]
        if isinstance(r, dict):
            # OpenWeather nutzt keys "1h" und "3h" für stündliche/summierte Werte
            pr = str(r.get("1h") or r.get("3h") or "")
        else:
            pr = str(r)
    if not pr and "snow" in data:
        s = data["snow"]
        if isinstance(s, dict):
            pr = str(s.get("1h") or s.get("3h") or "")
        else:
            pr = str(s)
    out["precipitation"] = pr

    # Wind-Info
    w = data.get("wind", {})
    out["wind_speed"] = str(w.get("speed", "")) if w else ""
    out["wind_deg"] = str(w.get("deg", "")) if w else ""

    # Feuchte und Druck
    out["humidity"] = str(data.get("main", {}).get("humidity", ""))
    out["pressure"] = str(data.get("main", {}).get("pressure", ""))

    # Bewölkung (Prozent)
    out["clouds"] = str(data.get("clouds", {}).get("all", "")) if data.get("clouds") else ""

    return out


# ---------------------------------------------------------------------------
# Formatierungsfunktionen — machen Ausgabe hübscher / lesbarer
# ---------------------------------------------------------------------------

def _format_date_for_display(s: str) -> str:
    """
    Formatiert Datum/Zeitstrings lesbar:
    - '2025-12-09' -> '09.12.2025'
    - '2025-12-09T22:01:37Z' -> '09.12.2025 22:01 UTC'
    Falls Parsen fehlschlägt, wird der Originalstring zurückgegeben.
    """
    if not s:
        return "-"
    s0 = s.strip()
    try:
        # OpenWeather gibt oft ISO mit trailing 'Z' -> ersetze durch +00:00 für fromisoformat()
        if s0.endswith("Z"):
            s2 = s0.replace("Z", "+00:00")
        else:
            s2 = s0
        dt = datetime.fromisoformat(s2)
        # Zeige Zeitanteil nur, wenn dieser vorhanden oder ungleich Mitternacht ist.
        if dt.hour != 0 or dt.minute != 0 or "T" in s0 or ":" in s0:
            return dt.strftime("%d.%m.%Y %H:%M UTC")
        else:
            return dt.strftime("%d.%m.%Y")
    except Exception:
        # Fallback: versuche YYYY-MM-DD
        try:
            dt = datetime.strptime(s0, "%Y-%m-%d")
            return dt.strftime("%d.%m.%Y")
        except Exception:
            # Wenn alles scheitert, gib den Originalstring zurück.
            return s0


def _format_temp_for_display(t: str) -> str:
    """
    Temperaturformatierung:
    - Wenn nahe an einer Ganzzahl -> ganze Zahl + °C
    - Sonst eine Nachkommastelle
    - Leerer Wert -> '-'
    """
    if not t:
        return "-"
    try:
        f = float(t)
        if abs(f - round(f)) < 0.05:
            return f"{int(round(f))}°C"
        else:
            return f"{round(f,1):.1f}°C"
    except Exception:
        return t


def _format_precip_for_display(p: str) -> str:
    """
    Niederschlagsformatierung (in mm):
    - <1 mm: evtl. eine Dezimalstelle
    - ganze mm: ganze Zahl
    - sonst 1 Dezimalstelle
    """
    if not p:
        return "-"
    try:
        f = float(p)
        if f < 1 and abs(f - round(f,1)) > 0.01:
            return f"{round(f,1):.1f} mm"
        if abs(f - round(f)) < 0.05:
            return f"{int(round(f))} mm"
        return f"{round(f,1):.1f} mm"
    except Exception:
        return p


def _format_wind_for_display(speed: str, deg: str) -> str:
    """
    Wind-Ausgabe:
    - Geschwindigkeit in m/s (ganze Zahl, oder 1 Dezimalstelle wenn nötig)
    - Richtung als (deg°) angehängt, falls vorhanden
    """
    if not speed and not deg:
        return "-"
    parts = []
    try:
        if speed:
            f = float(speed)
            parts.append(f"{round(f,1):.1f} m/s" if abs(f - round(f)) >= 0.05 else f"{int(round(f))} m/s")
    except Exception:
        parts.append(speed)
    if deg:
        parts.append(f"({deg}°)")
    return " ".join(parts) if parts else "-"


def _format_humidity(h: str) -> str:
    """Luftfeuchte als Prozent (z.B. '81%') oder '-' wenn leer."""
    return f"{h}%" if h else "-"


def _format_pressure(p: str) -> str:
    """Luftdruck in hPa oder '-' wenn leer."""
    return f"{p} hPa" if p else "-"


def _format_clouds(c: str) -> str:
    """Bewölkung in Prozent oder '-' wenn leer."""
    return f"{c}%" if c else "-"


def _format_description(desc: str) -> str:
    """Beschreibungsstring: erstes Zeichen groß, Rest unverändert."""
    if not desc:
        return "-"
    txt = str(desc).strip()
    return txt[0].upper() + txt[1:] if len(txt) > 0 else txt


# ---------------------------------------------------------------------------
# Anzeige-Logik: komponiert Ausgabezeilen basierend auf den angeforderten Feldern
# ---------------------------------------------------------------------------

def display_weather(data: List[Dict[str, str]], fields: Sequence[str]) -> None:
    """
    Drucke Wetterdaten in menschenlesbarer Form:
    - 'fields' bestimmt die Reihenfolge und Auswahl der angezeigten Felder.
    - Standard-Ausgabeformat, wenn 'date' enthalten ist:
      "DATE [CITY]: rest-of-fields-joined-with —"
    - Wenn kein 'date' aber 'city' vorhanden: "CITY: rest"
    """
    if not data:
        print("Keine Wetterdaten zum Anzeigen.")
        return

    for r in data:
        out_parts: List[str] = []

        # Für jedes gewünschte Feld erzeugen wir einen formatierten String-Teil
        for f in fields:
            if f == "date":
                out_parts.append(_format_date_for_display(r.get("date", "-")))
            elif f == "city":
                # city übernehmen oder '-' bei Fehlen
                out_parts.append(r.get("city", "-"))
            elif f == "temp":
                out_parts.append(_format_temp_for_display(r.get("temp", "")))
            elif f == "description":
                out_parts.append(_format_description(r.get("description", r.get("desc", ""))))
            elif f == "precipitation":
                # mehrere mögliche Keys in CSV/API
                p = r.get("precipitation", "") or r.get("rain", "") or r.get("snow", "")
                out_parts.append(_format_precip_for_display(p))
            elif f == "wind":
                ws = r.get("wind_speed", "") or r.get("wind", "")
                wd = r.get("wind_deg", "") or r.get("wind_dir", "")
                out_parts.append(_format_wind_for_display(ws, wd))
            elif f == "humidity":
                out_parts.append(_format_humidity(r.get("humidity", "")))
            elif f == "pressure":
                out_parts.append(_format_pressure(r.get("pressure", "")))
            elif f == "clouds":
                out_parts.append(_format_clouds(r.get("clouds", "")))
            else:
                # Unbekannte Felder: gib Rohwert zurück oder '-' falls nicht vorhanden
                out_parts.append(r.get(f, "-"))

        # Spezialfall: wenn 'date' in den angeforderten Feldern ist,
        # setzen wir Datum (+ optional City) als Präfix und hängen den Rest an.
        if "date" in fields:
            date_idx = fields.index("date")
            date_str = out_parts[date_idx]
            # Falls auch 'city' angefordert wurde, hole dessen Darstellung
            city_str = None
            if "city" in fields:
                city_idx = fields.index("city")
                city_str = out_parts[city_idx]
            # Baue Restteile (ohne date und ggf. city) zusammen
            rest_parts = []
            for i, part in enumerate(out_parts):
                if i == date_idx or (city_str is not None and i == (fields.index("city") if "city" in fields else -1)):
                    continue
                if part and part != "-":
                    rest_parts.append(part)
            rest_str = " — ".join(rest_parts)
            # Formatierung je nachdem, ob City vorhanden ist
            if city_str:
                if rest_str:
                    print(f"{date_str} {city_str}: {rest_str}")
                else:
                    print(f"{date_str} {city_str}")
            else:
                if rest_str:
                    print(f"{date_str}: {rest_str}")
                else:
                    print(f"{date_str}")
        else:
            # Kein Datum in Feldern: bringe ggf. City an den Anfang oder gib alles joined aus
            if "city" in fields:
                city_idx = fields.index("city")
                city_str = out_parts[city_idx]
                rest = [p for i, p in enumerate(out_parts) if i != city_idx and p and p != "-"]
                if rest:
                    print(f"{city_str}: " + " — ".join(rest))
                else:
                    print(f"{city_str}")
            else:
                # Keine Date/City: gebe alle non-empty Teile verbunden aus
                print(" — ".join([p for p in out_parts if p and p != "-"]))


# ---------------------------------------------------------------------------
# Logging in CSV — erweitert um 'city' Spalte
# ---------------------------------------------------------------------------

def log_to_csv(data: List[Dict[str, str]], path: str) -> None:
    """
    Hängt die gegebenen Daten an eine CSV an.
    - Feldreihenfolge ist: date, city, temp, description, precipitation, wind_speed, wind_deg, humidity, pressure, clouds
    - Wenn Datei nicht existiert, wird Header geschrieben.
    - Werte werden als Strings geschrieben.
    """
    fieldnames = ["date", "city", "temp", "description", "precipitation", "wind_speed", "wind_deg", "humidity", "pressure", "clouds"]
    rows = []
    for r in data:
        rows.append({
            "date": r.get("date", ""),
            "city": r.get("city", ""),
            "temp": r.get("temp", ""),
            "description": r.get("description", r.get("desc", "")),
            "precipitation": r.get("precipitation", "") or r.get("rain", "") or r.get("snow", ""),
            "wind_speed": r.get("wind_speed", "") or r.get("wind", ""),
            "wind_deg": r.get("wind_deg", "") or r.get("wind_dir", ""),
            "humidity": r.get("humidity", ""),
            "pressure": r.get("pressure", ""),
            "clouds": r.get("clouds", ""),
        })

    # Prüfe, ob die Datei bereits existiert (damit wir Header nur einmal schreiben)
    try:
        with open(path, "r", newline="", encoding="utf-8") as fh:
            has_header = True
    except FileNotFoundError:
        has_header = False

    # Schreibe die Zeilen in Append-Modus; schreibe Header falls nötig.
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if not has_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


# ---------------------------------------------------------------------------
# OpenWeather-API Integration (aktuelles Wetter)
# ---------------------------------------------------------------------------

def fetch_openweather_for_city(city: str, api_key: str, units: str = "metric", lang: str = "de") -> List[Dict[str, str]]:
    """
    Ruft die OpenWeather Current Weather API für 'city' ab und normalisiert die Antwort.
    - api_key: gültiger OpenWeather API Key
    - units: "metric" oder "imperial"
    - lang: Sprache für die Beschreibung (z.B. "de")
    Rückgabe: Liste mit genau einem Dict (Konsistenz mit CSV-Modus).
    """
    if not api_key:
        raise ValueError("OpenWeather API key missing")

    # Basis-URL
    base = "https://api.openweathermap.org/data/2.5/weather"
    # Query-Parameter (q=city, appid=key, units, lang)
    params = {"q": city, "appid": api_key, "units": units, "lang": lang}
    # Vollständige URL
    url = base + "?" + urllib.parse.urlencode(params)
    # Erstelle Request mit User-Agent, damit manche Server weniger restriktiv antworten
    req = urllib.request.Request(url, headers={"User-Agent": "WetterApp-CLI/1.0"})

    # HTTP-Request (GET) mit Timeout; decode als UTF-8
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        data = json.loads(body)

    # Falls API einen Fehlercode zurückliefert (cod != 200), werfe RuntimeError mit Message
    if isinstance(data, dict) and data.get("cod") and int(data.get("cod")) != 200:
        msg = data.get("message", "Unbekannter Fehler von OpenWeather")
        raise RuntimeError(f"OpenWeather API Fehler: {msg}")

    # Baue die normalisierte Zeile:
    base_row = {}
    # Wenn die API einen kanonischen Stadtnamen zurückgibt (data['name']), verwende ihn
    api_name = data.get("name")
    base_row["city"] = api_name or city
    # Datum: ISO-Z Zeitstempel in UTC ohne Mikrosekunden
    base_row["date"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    # Extrahiere weitere Felder (temp, description, precipitation, wind, humidity, pressure, clouds)
    common = _extract_common_from_api(data)
    base_row.update(common)

    # Gib die Zeile in einer Liste zurück, damit die weitere Verarbeitung (wie beim CSV-Modus)
    # unverändert bleibt (z.B. logging/log_to_csv erwartet List[Dict[str,str]]).
    return [base_row]


# ---------------------------------------------------------------------------
# Feld-Validierung und CLI-Einstiegspunkt
# ---------------------------------------------------------------------------

def _validate_and_split_fields(s: Optional[str]) -> List[str]:
    """
    Parst den Wert von --fields (falls gesetzt). Erwartet eine kommaseparierte Liste.
    Falls nicht gesetzt, geben wir die Default-Felder zurück.
    WICHTIG: Default enthält nun standardmäßig 'city' (neben 'date').
    """
    default = ["date", "city", "temp", "description", "precipitation", "wind", "humidity", "pressure", "clouds"]
    if not s:
        return default
    parts = [p.strip().lower() for p in s.split(",") if p.strip()]
    return parts or default


def main(argv: Optional[List[str]] = None) -> int:
    """
    Hauptfunktion:
    - Argumente parsen
    - Datenquelle bestimmen (CSV oder OpenWeather API)
    - Daten parsen / abrufen
    - Optional loggen
    - Ausgabe entsprechend --format / --quiet / --only-log
    Rückgabewerte:
      0  = Erfolg
      2  = fehlender API-Key
      3  = API-Fehler
      4  = Datei-Lese-Fehler
      5  = Parsing-Fehler
      6  = Log-Schreibfehler
      7  = ungültige Kombination (--only-log ohne --log)
      130= Abbruch (KeyboardInterrupt)
    """
    # Wenn main ohne argv aufgerufen wird, verwende die tatsächlichen Kommandozeilenargumente
    argv = argv if argv is not None else sys.argv[1:]

    # CLI-Argumente definieren
    parser = argparse.ArgumentParser(description="WetterApp CLI with extended weather parameters")
    parser.add_argument("--file", "-f", help="Input CSV file. If omitted read from stdin.")
    parser.add_argument("--log", "-l", help="Append parsed data to a CSV file")
    parser.add_argument("--ow-city", help="Fetch current weather from OpenWeather for CITY")
    parser.add_argument("--ow-key", help="OpenWeather API key (or set OPENWEATHER_API_KEY env var)")
    parser.add_argument("--ow-units", default="metric", choices=["metric", "imperial"], help="Units for OpenWeather (default: metric)")
    parser.add_argument("--ow-lang", default="de", help="Language for OpenWeather description (default: de)")

    # Ausgabe-Steuerung
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress console output (errors still go to stderr).")
    parser.add_argument("--only-log", action="store_true", help="Do not print to stdout; only write to log (--log required).")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format: 'text' or 'json'.")
    parser.add_argument("--fields", help="Comma-separated list of fields to display (order matters). Available: date,city,temp,description,precipitation,wind,humidity,pressure,clouds")

    # Argumente parsen
    args = parser.parse_args(argv)

    try:
        # Felder bestimmen (vom Nutzer gesetzt oder default)
        fields = _validate_and_split_fields(args.fields)

        # Datenbeschaffung: OpenWeather API, Datei oder stdin
        if args.ow_city:
            # API-Key: bevorzugt --ow-key, sonst Umgebungsvariable OPENWEATHER_API_KEY
            key = args.ow_key or os.environ.get("OPENWEATHER_API_KEY")
            if not key:
                # Key fehlt -> Fehler
                print("Kein OpenWeather API-Key angegeben (--ow-key oder OPENWEATHER_API_KEY).", file=sys.stderr)
                return 2
            try:
                # API-Aufruf, liefert Liste mit einer Zeile
                data = fetch_openweather_for_city(args.ow_city, key, units=args.ow_units, lang=args.ow_lang)
            except Exception as e:
                # Fehler bei API-Aufruf -> Ausgabe nach stderr und Fehlercode
                print(f"Fehler beim Abrufen von OpenWeather: {e}", file=sys.stderr)
                return 3
        else:
            # CSV-Modus (Datei lesen oder stdin)
            if args.file:
                try:
                    # Datei im UTF-8 Modus öffnen; falls Datei andere Kodierung hat, kann das Anpassung brauchen
                    with open(args.file, "r", encoding="utf-8") as fh:
                        raw = fh.read()
                except Exception as e:
                    print(f"Fehler beim Lesen der Datei: {e}", file=sys.stderr)
                    return 4
                # CSV parsen (gibt Liste von dicts)
                parsed = parse_weather_data(raw)

                # Normalisiere Felder (z. B. precipitation aus diversen Header-Varianten)
                normalized_rows: List[Dict[str, str]] = []
                for row in parsed:
                    nr = dict(row)  # mache eine Kopie (vermeide Änderung des Originals)
                    # Precipitation Normalisierung
                    p = _extract_precipitation_from_row(row)
                    if p:
                        nr["precipitation"] = p
                    # Wind Normalisierung
                    w = _extract_wind_from_row(row)
                    if w.get("wind_speed"):
                        nr["wind_speed"] = w["wind_speed"]
                    if w.get("wind_deg"):
                        nr["wind_deg"] = w["wind_deg"]
                    # 'city' Spalte wird, falls vorhanden, beibehalten (keine automatische Ergänzung)
                    normalized_rows.append(nr)

                data = normalized_rows
            else:
                # Keine Datei: lese von stdin (z. B. via pipe)
                raw = sys.stdin.read()
                try:
                    data = parse_weather_data(raw)
                except Exception as e:
                    print(f"Fehler beim Parsen der Eingabedaten: {e}", file=sys.stderr)
                    return 5

        # Validierung: only-log ohne log macht keinen Sinn -> Fehler
        if args.only_log and not args.log:
            print("Fehler: --only-log verlangt eine Logdatei (--log <path>).", file=sys.stderr)
            return 7

        # Falls Log gewünscht ist: schreibe immer (auch wenn quiet gesetzt ist)
        if args.log:
            try:
                log_to_csv(data, args.log)
            except Exception as e:
                print(f"Fehler beim Schreiben in die Logdatei: {e}", file=sys.stderr)
                return 6

        # Ausgabe auf stdout: abhängig von quiet / only-log / format
        if not args.quiet and not args.only_log:
            if args.format == "json":
                # JSON-Ausgabe, ensure_ascii=False damit Umlaute korrekt bleiben
                try:
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                except Exception:
                    print(json.dumps(data, ensure_ascii=False))
            else:
                # Text-Ausgabe: benutze display_weather mit den gewählten Feldern
                display_weather(data, fields)

        # Erfolgreich beenden
        return 0

    except KeyboardInterrupt:
        # Bei Strg+C: sauberes Beenden mit Code 130 (conventional)
        print("Abgebrochen.", file=sys.stderr)
        return 130


# Falls dieses Modul direkt ausgeführt wird, rufe main() auf und exit mit dessen Rückgabewert.
if __name__ == "__main__":
    raise SystemExit(main())