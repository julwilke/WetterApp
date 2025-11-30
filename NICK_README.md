# WetterApp 🌦️

Ein Gruppenprojekt im Rahmen des Masterstudiums "Angewandte KI".

## 📋 Projektbeschreibung

Die WetterApp ist eine Python-basierte Anwendung zur Abfrage und Analyse von Wetterdaten. Das Projekt startet mit einem einfachen Skript zum Abrufen aktueller Wetterdaten per API für eine gegebene Postleitzahl und wird schrittweise um weitere Features erweitert.

Das Ziel ist eine benutzerfreundliche und erweiterbare WebApp mit vielen üblichen Funktionen der Darstellung von Wetter Daten.

## 🎯 Projektziele

- **Phase 1**: 
    - ✅ Einfaches Python-Skript zur Wetterabfrage per API (Postleitzahl → aktuelle Wetterdaten) in der Konsole --> MVP (Minimum Viable Product)
    - ✅ Grundlegende WebApp entwickeln
    - [ ] Abgabefertig und bewertbare Lösung fertigstellen
- **Phase 2**: 
    - [ ] Erweiterte Wetteranalysen und Datenvisualisierung, weitere Funktionen bestimmen und einbinden
    - [ ] Persistenz ausgewählter Daten
    - [ ] Logging, Debugging, Test-Funktionen einbauen
- **Phase 3**: 
    - [ ] Integration von KI-Funktionen (eigene Vorhersagen, Mustererkennung, Anomalien (z.B. "ungewöhnlich warmer Dezember")
- **Phase 4**: Finalisierung
    - [ ] Code-Refactoring / Hardening
    - [ ] docs / configs / README.MD finalisieren

## 🛠️ Installation & Verwendung 

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
python app.py
```

## 📦 Technology-Stack

- **Sprache**: Python 3.10+ (prüfen!)
- **API**: OpenWeatherMap, 
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
© 2025 (PKI Gruppe B1-3)

---

**Letzte Aktualisierung**: 30.11.2025
