###############################################
#   🌦 CSV-WEATHER-PROVIDER – 1.0.2           #
###############################################

# =============== IMPORTS ====================
import pandas as pd
import os               
import logging

from backend.services import data_normalizer

# Logger für dieses Modul
logger = logging.getLogger(__name__)



# ===== KLASSE ERSTELLEN =====
class CSVWeatherProvider:
    """ Liest Wetterdaten aus einer CSV-Datei, normalisiert sie und stellt sie bereit. """

    def __init__(self, filename="weather_sample.csv"): #J: Hier nicht den Pfad, sondern den Dateinamen nehmen 'filename'
        """Initialisiert den CSVWeatherProvider mit dem Pfad zur CSV-Datei"""
        
        # J: Neu hinzugefügt um die Probleme beim verschieben der app.py oder .csv (Pfadprobleme) zu lösen:

        # Ordner, in dem dieses Skript liegt /WetterApp/backend
        base_dir = os.path.dirname(os.path.abspath(__file__))   

        # Project-Root-Pfad ("Überordner") bestimmen -> von "hier" 2 Ordner hoch
        project_root = os.path.abspath(os.path.join(base_dir, "..", "..")) 

        # /data/samples
        samples_dir = os.path.join(project_root, "data", "samples")

        # FINALER absoluter Pfad zu der CSV-Datei
        self.csv_path = os.path.join(samples_dir, filename)
        self.csv_path = os.path.abspath(self.csv_path)                           

        #Fehler throwen falls nicht gefunden
        if not os.path.exists(self.csv_path):   
            logger.error(f"CSV-Datei nicht gefunden unter: {self.csv_path}")
        else:
            logger.info(f"CSV-Daten geladen aus {self.csv_path}")


    def get_weather_for_city(self, city: str):
        """Liest CSV, filtert nach Stadt und gibt Wetterdaten als Dictionary zurück."""

        #1) CSV laden (J: Try Except hinzugefügt falls Pfad nicht gefunden wurde)
        try:
            df = pd.read_csv(self.csv_path) # wird bei jedem Request geladen, aufgrund kleiner CSV/kleiner Last aber erstmal so gelassen
            
        except Exception as e:
            logger.error(f"CSV konnte nicht geladen werden: {e}")
            return None

        # 2) Filtern auf Stadt
        df_city = df[df["CITY"].str.lower() == city.lower()]

        if df_city.empty:
            logger.info(f"Keine Wetterdaten für Stadt '{city}' in der CSV-Datei gefunden.") 
            return None

        # 3) Zeile des Datensatz extrahieren in dict Form
        row = df_city.iloc[0].to_dict()

        # 4) Normalisieren der Daten (immernoch dict Form)
        normalized_data = data_normalizer.normalize_weather_data(row)

        logger.info(f"Wetterdaten für Stadt '{city}' erfolgreich aus CSV geladen.")

        # 5) Daten zurückgeben (inkl. aller nötigen Felder und Normalisierung und Default-Werte)       
        return (normalized_data)
           