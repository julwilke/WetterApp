##############################################
#   🌦 WETTER-DASHBOARD – APP STARTER 1.0.0  #
##############################################

__version__ = "1.0.0"

#Docstring mit Minimalbeschreibung
"""
WetterApp - Backend Entry Point
--------------------------------
Initialisiert:
- Logging
- Environment Variablen
- Dashboard Backend
- Optionale CLI Argumente
"""

# =============== IMPORTS ====================

# TODO: Uncomment and use these imports when implementing:
#   - Logging system events
#   - Loading .env files with API keys
#   - Command-line argument parsing
#from logging import dieLoggingFunktion     #J: Für logging "der Dinge die passieren"
#from dotenv import load_dotenv             #J: Für das einbinden der eigenen, persönlichen .venvs inkl. API-Keys
#import argparse                            #J: Für Konsolenausgabe
from backend import dashboard

# ============================================
#  1) Konsolen Argumente lesen
# ============================================

#def parse_args(): ...

# ============================================
#  2) HAUPT-FUNKTION - main-Boot-Sequenz
# ============================================
def main():
    """
    Startet das Wetter-Dashboard Backend.
    Erstellt eine Instanz von WeatherDashboard und startet den Server.
    """
    
    print(f"Wetter-Dashboard Backend v{__version__} startet...")

    #try: #Grundsätzliche "Fatal Errors" abfangen, folgt noch
    app = dashboard.WeatherDashboard()   # Backend initialisieren
    app.run(city="Berlin")               # Server + Socket starten

    

    #except Exception as e:
        #logging.exception("Fataler Fehler im Backend!: ")

# ============================================
#  3) SCRIPT START (Entry-Point)
# ============================================
if __name__ == "__main__":
    main()  # Hauptfunktion ausführen
