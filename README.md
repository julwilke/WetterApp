# WetterApp 🌦️

Ein Gruppenprojekt im Rahmen des Masterstudiums "Angewandte KI".

## 📋 Projektbeschreibung

Die WetterApp ist eine Python-basierte Anwendung zur Abfrage und Analyse von Wetterdaten. Das Projekt startet mit einem einfachen Skript zum Abrufen aktueller Wetterdaten per API für eine gegebene Postleitzahl und wird schrittweise um weitere Features erweitert.

## ✅ To-Dos bis zum nächsten Meeting

### 📅 Bis Mittwoch, 26.11.2025
- [ ] Jeder einen privaten Branch erstellen und lokale Entwicklungsumgebung einrichten (Python lokal installieren, wenn man möchte VisualStudioCode, PyCharm, ...)
- [ ] Wetter-APIs recherchieren (z.B. OpenWeatherMap, MeteoStat, OpenMeteo)
- [ ] Python-Version festlegen (empfohlen: 3.10+, bislang haben wir alle 3.13)
- [ ] Einlesen in Python Installation, Virtuelle Umgebungen (.venv) und ggf. lokale Programmierumgebungen (VSC, PyCharm, ...)

### 📅 Bis Samstag, 29.11.2025
- [ ] API-Key beantragen
- [ ] Erstes funktionierendes Skript: Eingabe PLZ → Ausgabe Wetterdaten in der Konsole
- [ ] Requirements.txt mit benötigten Packages erstellen
- [ ] Projekt-Struktur festlegen (Ordner, Module)
- [ ] README mit Installationsanleitung ergänzen

## 🎯 Projektziele

- **Phase 1**: Einfaches Python-Skript zur Wetterabfrage per API (Postleitzahl → aktuelle Wetterdaten) in der Konsole
- **Phase 2**: Erweiterte Wetteranalysen und Datenvisualisierung, weitere Funktionen bestimmen und einbinden
- **Phase 3**: Übergang zur Weboberfläche zur Benutzerinteraktion, ggf. in Phase 2 schon in diese Richtung hinarbeiten
- **Phase 4**: Integration von KI-Modellen (z.B. Wettervorhersagen, Mustererkennung)

---
## 🗓️ Zeitplan

- **Meetings**: Mittwochs und Sonntags abends
- **Abgabe**: ca. Ende Januar 2026

---
## 🚀 Roadmap

### 1: Grundlagen & Setup
- [ ] Repository-Struktur aufsetzen
- [ ] API-Auswahl und API-Key beantragen (z.B. OpenWeatherMap, WeatherAPI)
- [ ] Erstes Python-Skript: Wetterabfrage per Postleitzahl
- [ ] Requirements.txt erstellen

### 2: Datenverarbeitung & Speicherung
- [ ] Fehlerbehandlung implementieren
- [ ] Daten strukturiert speichern (JSON/CSV)
- [ ] Logging hinzufügen
- [ ] Unit-Tests schreiben

### 3: Erweiterte Funktionen
- [ ] Historische Wetterdaten abrufen
- [ ] Datenvisualisierung (matplotlib/plotly)
- [ ] Mehrere Standorte vergleichen

### 4: KI-Integration
- [ ] Datensatz für Training vorbereiten
- [ ] Einfaches ML-Modell trainieren (z.B. Temperaturvorhersage)
- [ ] Modell evaluieren und optimieren

### 5: Finalisierung
- [ ] Weboberfläche (Flask/Streamlit) - optional
- [ ] Dokumentation vervollständigen
- [ ] Code-Refactoring
- [ ] Präsentation vorbereiten



## 🛠️ Installation & Verwendung (für Personen außerhalb des Developer-Teams)

```bash
# Repository klonen
git clone https://github.com/julwilke/WetterApp.git
cd WetterApp

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Skript ausführen
python wetterapp.py
```

## 📦 Technologie-Stack

- **Sprache**: Python 3.10+
- **API**: Noch offen (z.B. OpenWeatherMap, MeteoStat, OpenMeteo)
- **Libraries**: folgen
- **Zukünftig**: folgen

## 👥 Team

- Adam
- Tugba 
- Nick-Andre
- Julian

## 📝 Notizen

- Meeting-Protokolle im `/docs` Ordner
- Branch-Strategie: Private-Branches → Main

---

## 📄 Lizenz

[MIT-License]

---

**Letzte Aktualisierung**: 23.11.2025