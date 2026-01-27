# README – WetterApp CLI + Tests

## Überblick
In diesem Teilprojekt habe ich ein CLI-Tool entwickelt, das Wetterdaten entweder aus einer CSV-Datei oder direkt über die OpenWeather API auslesen kann.  
Die Ausgabe kann als Text oder JSON erfolgen und die Ergebnisse können optional in eine Log-CSV-Datei geschrieben werden.

Zusätzlich habe ich Unit-Tests geschrieben, die sicherstellen, dass Parsing, Ausgabeformatierung und Logging stabil funktionieren.

---

## Features der CLI (`cli/cli.py`)

### ✅ Unterstützte Datenquellen

#### 1) CSV-Modus
- Wetterdaten werden aus einer CSV gelesen  
- entweder über `--file <datei.csv>` oder per stdin (Pipe)

#### 2) API-Modus (OpenWeather)
- Abruf aktueller Wetterdaten über Stadtname (`--ow-city`)  
- API-Key kann per `--ow-key` oder Umgebungsvariable `OPENWEATHER_API_KEY` gesetzt werden

---

### ✅ Unterstützte Felder
Die CLI kann u.a. folgende Felder anzeigen und loggen:

- `date`
- `city`
- `temp`
- `description`
- `precipitation`
- `wind`
- `humidity`
- `pressure`
- `clouds`

Standardmäßig werden alle ausgegeben, aber man kann sie mit `--fields` einschränken.

---

### ✅ Ausgabeformate
- `--format text` *(Standard)*
- `--format json`

---

### ✅ Logging
Mit `--log <datei.csv>` können die Daten in eine CSV-Datei geschrieben werden.  
Die Datei bekommt automatisch einen Header, falls sie noch nicht existiert.

Optional kann man mit `--only-log` festlegen, dass nichts auf stdout ausgegeben wird.

---

## Beispiel-Aufrufe

### CSV-Datei lesen
```bash
python cli/cli.py --file sample.csv
