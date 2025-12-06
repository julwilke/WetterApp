##############################################
#   🌦 WETTER-DASHBOARD – APP STARTER 1.0  #
##############################################

# =============== IMPORTS ====================
from backend import dashboard

# ============================================
#   HAUPT-FUNKTION
# ============================================
def main():
    """
    Startet das Wetter-Dashboard Backend.
    Erstellt eine Instanz von WeatherDashboard und startet den Server.
    """
    app = dashboard.WeatherDashboard()   # Backend initialisieren
    app.run()                            # Server + Socket starten

# ============================================
#   SCRIPT START
# ============================================
if __name__ == "__main__":
    main()  # Hauptfunktion ausführen
