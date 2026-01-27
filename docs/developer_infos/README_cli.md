# WetterApp CLI – Dokumentation (cli/cli.py)

Diese README beschreibt mein **CLI-Tool** aus `cli/cli.py`.  
Damit kann ich Wetterdaten im Terminal anzeigen – entweder aus einer **CSV-Datei** oder live über die **OpenWeather API**.

Außerdem können die Daten optional in eine **Log-Datei (CSV)** geschrieben werden.

---

## ✅ Überblick / Ziel des Programms

Das Ziel des Programms ist ein kleines Command-Line-Tool, das Wetterdaten:

- **einliest**
- **normalisiert**
- **formatiert ausgibt**
- und optional **speichert/loggt**

Das Tool ist so gebaut, dass es mit verschiedenen CSV-Formaten möglichst robust funktioniert.

---

## ✨ Features

✅ CSV-Dateien lesen (`--file`) oder Daten über `stdin` verarbeiten  
✅ OpenWeather API Abruf (`--ow-city`) für aktuelle Werte  
✅ Ausgabe als Text oder JSON (`--format`)  
✅ Feldauswahl für die Ausgabe (`--fields`)  
✅ Logging in eine CSV-Datei (`--log`)  
✅ Unterstützung für typische Zusatzfelder:

- `date`
- `city`
- `temp`
- `description`
- `precipitation`
- `wind`
- `humidity`
- `pressure`
- `clouds`

---

## 📁 Projektstruktur (relevant)

```text
WetterApp/
│
├── cli/
│   ├── __init__.py
│   ├── cli.py
│   └── test_parse_weather.py
```

---

## ⚙️ Voraussetzungen

- Python **3.10+**
- Optional: OpenWeather API-Key (nur für API-Modus)

---

## ▶️ Programm ausführen (Beispiele)

### ✅ 1) CSV-Datei einlesen und Ausgabe im Terminal

```bash
python -m cli.cli --file cli/sample.csv
```

Beispiel-Ausgabe:

```text
09.12.2025 Berlin: 5°C — Leicht bewölkt
```

---

### ✅ 2) Nur bestimmte Felder ausgeben

```bash
python -m cli.cli --file cli/sample.csv --fields date,city,temp,description
```

---

### ✅ 3) Ausgabe als JSON

```bash
python -m cli.cli --file cli/sample.csv --format json
```

Hier wird ein JSON-Array ausgegeben (Liste von Zeilen-Objekten).

---

## 📝 Logging / Log-Datei (CSV)

### ✅ 4) Daten in eine Logdatei schreiben

```bash
python -m cli.cli --file cli/sample.csv --log cli/logged.csv    # Für Sample -> CSV
python -m cli.cli --ow-city Berlin --log cli/logged.csv         # Für API -> CSV
```

Wichtig:

- Falls `logged.csv` nicht existiert → Datei wird erstellt
- Header wird automatisch geschrieben
- Bei erneutem Start werden Daten **angehängt** (append)

---

### ✅ 5) Nur loggen (keine Terminalausgabe)

```bash
python -m cli.cli --file cli/sample.csv --log cli/logged.csv --only-log
```

---

## 🌍 OpenWeather API Modus

### ✅ 6) Live-Wetter abrufen

```bash
python -m cli.cli --ow-city Berlin --ow-key "DEIN_API_KEY"
```

---

### ✅ 7) API Abruf + Logging

```bash
python -m cli.cli --ow-city Berlin --ow-key "DEIN_API_KEY" --log cli/logged.csv
```

---

## 🔑 API-Key als Environment Variable setzen (PowerShell)

Damit man den API-Key nicht jedes Mal eintippen muss:

```powershell
$env:OPENWEATHER_API_KEY="DEIN_API_KEY"
python -m cli.cli --ow-city Berlin
```

---

## 🧪 Tests ausführen

Die Tests liegen unter:

```
tests/test_parse_weather.py
```

Alle Tests starten (im Projekt-Root):

```bash
pytest -q
```

Oder nur die CLI-Tests:

```bash
pytest tests/test_parse_weather.py -q
```

---

## 🛠 Typische Fehler & Lösungen

### ❌ PowerShell Fehler: `Unerwartetes Token 'python'`

Das passiert oft, wenn man eine Zeile so schreibt:

```powershell
5. python cli.py ...
```

PowerShell interpretiert `5.` als Ausdruck und bekommt dann Probleme.

✅ Lösung: Nummerierung entfernen:

```powershell
python cli.py --ow-city Berlin --ow-key "DEIN_API_KEY"
```

---

### ❌ OpenWeather: HTTP Error 401 (Unauthorized)

Bedeutet: OpenWeather akzeptiert den API-Key nicht.

✅ Mögliche Gründe:

- Key ist falsch kopiert
- Key ist noch nicht aktiviert (manchmal dauert es ein paar Minuten)
- falsche Anführungszeichen beim Copy/Paste

✅ Lösung:

```powershell
python cli.py --ow-city Berlin --ow-key 'DEIN_API_KEY'
```

---

## 📌 Umsetzungsidee / technische Hinweise

Ich habe versucht, das Tool robust zu machen, weil CSV-Dateien in der Praxis oft leicht unterschiedlich aufgebaut sind.

Daher werden:

- Header-Namen normalisiert (`lowercase`, `trim`)
- BOM (UTF-8) entfernt
- Werte vereinheitlicht (immer als String)
- alternative Feldnamen erkannt (z.B. `wind_speed`, `wind_kmh`, `rain`, `snow` usw.)

Dadurch bricht das Tool nicht sofort ab, wenn die CSV aus einer anderen Quelle kommt.

---

## ✅ Fazit

Mit `cli/cli.py` kann ich Wetterdaten:

- lokal aus CSV lesen
- online über OpenWeather abrufen
- schön formatieren
- oder als JSON zurückgeben
- und zusätzlich in eine Log-Datei speichern

Das Tool ist bewusst klein gehalten, aber flexibel genug, um später erweitert zu werden.

---
