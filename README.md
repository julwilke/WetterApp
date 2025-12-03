# WetterApp 123🌦️

Ein Gruppenprojekt im Rahmen des Masterstudiums "Angewandte KI".

## 📋 Projektbeschreibung

Die WetterApp ist eine Python-basierte Anwendung zur Abfrage und Analyse von Wetterdaten. Das Projekt startet mit einem einfachen Skript zum Abrufen aktueller Wetterdaten per API für eine gegebene Postleitzahl und wird schrittweise um weitere Features erweitert.

## ✅ To-Dos bis zum nächsten Meeting

### 📅 Bis Samstag/Sonntag, 29/30.11.2025
- ✅ privaten Branch erstellen und lokale Entwicklungsumgebung einrichten (Python lokal installieren, wenn man möchte VisualStudioCode, PyCharm, ...)
- ✅ Erstes funktionierendes Skript: Eingabe PLZ → Ausgabe Wetterdaten in der Konsole
- [ ] Wetter-APIs recherchieren (z.B. OpenWeatherMap, MeteoStat, OpenMeteo)
- [ ] Python-Version festlegen (empfohlen: 3.10+, bislang haben wir alle 3.13)
- [ ] Einlesen in Python Installation, Virtuelle Umgebungen (.venv) und ggf. lokale Programmierumgebungen (VSC, PyCharm, ...)
- [ ] Daten speichern oder nur live abrufen (CSV/SQLite) Problem bei Live: begrenzte API-Calls, mindestens einen Ordner mit Mock-Daten/historischen Daten
- [ ] API-Schnittstelle weiter bauen
- [ ] Projekt-Struktur festlegen (Ordner, Module)
- [ ] README mit Installationsanleitung ergänzen
- [ ] WebApp Grund-Framework beginnen / recherchieren

## 🎯 Projektziele

- **Phase 1**: 
    - Einfaches Python-Skript zur Wetterabfrage per API (Postleitzahl → aktuelle Wetterdaten) in der Konsole --> MVP (Minimum Viable Product)
    - Grundlegende WebApp entwickeln
    - Abgabefertig und bewertbare Lösung fertigstellen
- **Phase 2**: 
    - Erweiterte Wetteranalysen und Datenvisualisierung, weitere Funktionen bestimmen und einbinden
- **Phase 3**: 
    - Integration von KI-Modellen/-Funktionen (eigene Vorhersagen, Mustererkennung, Anomalien (z.B. "ungewöhnlich warmer Dezember")
- **Phase 4**: Finalisierung
    - configs anpassen
    - requirements.txt fertigstellen und fremd-prüfen lassen
    - README.MD sauber machen
    - .venv Beispiel anfertigen für den Notfall

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

- Bis hier sollte ein abgabefähiges, robustes, ordentliches und gut bewertbares Projekt bereits vorliegen! Rest ist nur noch erweitern und verbessern.

### 3: Erweiterte Funktionen
- [ ] Historische Wetterdaten abrufen
- [ ] Datenvisualisierung (matplotlib/plotly)
- [ ] Mehrere Standorte vergleichen

### 4: Benutzeroberfläche
- [ ] Weboberfläche (Flask/Streamlit) oder Desktopumgebung? (Tkinter / PyQt / PySide) - Minimum: Eingabe PLZ, Ausgabe bestimmter Wetterdaten

### 5: KI-Integration
- [ ] Datensatz für Training vorbereiten
- [ ] Einfaches ML-Modell trainieren (z.B. Temperaturvorhersage)
- [ ] Modell evaluieren und optimieren
- [ ] Ideen: Clustering von Temperaturmustern, Korrelationen zwischen Feuchte, Wind, Temperatur, kleine Wettervorhersage selbst erstellen

### 6: Finalisierung
- [ ] Code-Refactoring
- [ ] Präsentation vorbereiten
- [ ] READNE.md / requirements.txt / docs finalisieren

## 📚 Aufgabenstellung der FH

**Thema: Analyse und Visualisierung von Wetterdaten**

- **Kernidee**: Abruf, Analyse und Darstellung von Wetterdaten für einen bestimmten Ort.
- **Datenquelle**: Kostenlose Wetter-APIs wie OpenWeatherMap oder Meteostat.

### Mögliche Umsetzungen:
- **Grundversion**: Ein Skript, das für eine feste Stadt die aktuelle Temperatur, Luftfeuchtigkeit und Wetterbeschreibung ausgibt.
- **Grafische Version**: Eine Desktop-Anwendung (mit Tkinter/PyQt) oder eine kleine Webseite, auf der ein Benutzer einen Ort eingeben kann und die aktuellen Wetterdaten sowie eine Vorhersage für die nächsten Tage erhält.

### Optionale Erweiterungen & Vertiefungen:
- **Historischer Vergleich**: Visualisierung von Temperatur- oder Niederschlagsverläufen für den aktuellen Monat im Vergleich zum gleichen Monat der Vorjahre.
- **Interaktive Karte**: Nutzung von Folium, um Wetterdaten (z.B. Temperaturen oder Windgeschwindigkeiten) für mehrere Orte gleichzeitig auf einer Weltkarte darzustellen.
- **Agrar-Dashboard**: Spezialisierte Ansicht, die für Landwirte relevante Daten wie die Niederschlagsmenge der letzten 30 Tage oder die Anzahl der Sonnenstunden anzeigt.
- **KI-Anwendung (Mustererkennung)**: Analyse historischer Daten, um Korrelationen zu finden (z.B. "Wie hängt die Windgeschwindigkeit mit schnellen Temperaturänderungen zusammen?"). Anwendung von Clustering, um typische "Wetterprofile" für eine Jahreszeit zu identifizieren.

### Hilfreiche Python-Bibliotheken:
- **Datenbeschaffung**: `requests` (für die Kommunikation mit der Wetter-API)
- **Datenverarbeitung**: `pandas` (zur Handhabung der Zeitreihendaten)
- **UI**: `Tkinter` (in Python enthalten), `PyQt` (umfangreicher), `Flask` (für eine Weboberfläche)
- **Visualisierung**: `Matplotlib`, `Seaborn` (für ansprechendere Graphen), `Folium` (für interaktive Karten)
- **KI & Statistik**: `Scikit-learn` (für Clustering und Korrelationsanalysen)


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

- Adham
- Tugba 
- Nick-Andre
- Julian

## 📝 Notizen

- Meeting-Protokolle im `/docs` Ordner
- Branch-Strategie: Private-Branches → Main

---

## 📄 License

AGPLv3 — see LICENSE file for full terms.
© 2025 <PKI Gruppe B1-3>

---

**Letzte Aktualisierung**: 26.11.2025
