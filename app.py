##############################################
#   🌦 WETTER-DASHBOARD – APP STARTER 1.0.1  #
##############################################

__version__ = "1.0.1"

#Docstring mit Minimalbeschreibung
"""
WetterApp - Backend Entry Point
--------------------------------
Initialisiert:
- Logging
- TODO: Environment Variablen
- Dashboard Backend
- Optionale CLI Argumente
"""

# =============== IMPORTS ====================

#TODO: from dotenv import load_dotenv             #J: Für das einbinden der eigenen, persönlichen .venvs inkl. API-Keys
#TODO: falls nötig: import argparse                 

import logging
# Im Rest des Programms dann nur noch logger = logging.getLogger(__name__) nutzen und dann...
# z.B. logger.info("Nachricht"), logger.warning("Warnung"), logger.error("Fehler")

from backend import dashboard 
from backend.logging_config import configure_logging  #J: Logging Konfiguration importieren

# ============================================
#  1) Konsolen Argumente lesen (OPTIONAL)
# ============================================

#def parse_args(): 

# ============================================
#  2) HAUPT-FUNKTION - main-Boot-Sequenz
# ============================================
def main():
    """
    Startet das Wetter-Dashboard Backend.
    Erstellt eine Instanz von WeatherDashboard und startet den Server.
    """
    
    # 1) Logging konfigurieren
    configure_logging()

    logger = logging.getLogger(__name__)
    logger.info(f"Wetter-Dashboard Backend v{__version__} startet...")    

    # 2) TODO: .env Datei laden (API-Keys etc.)
    #load_dotenv()  #J: Lädt die .env Datei im Projektverzeichnis

    # 3) Dashboard Backend initialisieren und starten
    app = dashboard.WeatherDashboard() 

    # 4) Server starten (Standard-Stadt kann hier übergeben werden)
    app.run(city="Berlin")               


# ============================================
#  3) SCRIPT START (Entry-Point)
# ============================================
if __name__ == "__main__":
    main()  # Hauptfunktion ausführen
