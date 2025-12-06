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

#from logging import dieLoggingFunktion     #J: Für logging "der Dinge die passieren"
#from dotenv import load_dotenv             #J: Für das einbinden der eigenen, persönlichen .venvs inkl. API-Keys
#import argparse                            #J: Für Konsolenausgabe

from backend import dashboard




# ============================================
#   HAUPT-FUNKTION
# ============================================
def main():
    """
    Startet das Wetter-Dashboard Backend.
    Erstellt eine Instanz von WeatherDashboard und startet den Server.
    """
    
    print("Wetter-Dashboard Backend v{__version__} startet...")

    #try: #Grundsätzliche "Fatal Errors" abfangen, folgt noch
    app = dashboard.WeatherDashboard()   # Backend initialisieren
    app.run()                            # Server + Socket starten

    #except Exception as e:
        #logging.exception("Fataler Fehler im Backend!: ")

# ============================================
#   SCRIPT START
# ============================================
if __name__ == "__main__":
    main()  # Hauptfunktion ausführen
