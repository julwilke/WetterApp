#Hier ist die Schnittstelle zwischen dem API-Call und dem Frontend

from fastapi import APIRouter, HTTPException
from api.fetch_weather import fetch_weather                #API-Call von Adham
from services.data_normalizer import normalize_weather_data     #Datennormalisierung von Julian


#Im Frontend wollen wir "city" eingeben, und für diese city dann den API-Call machen
router = APIRouter()

@router.get("/{city}")
def weather(city: str):
    try:
        raw = fetch_weather(city)                          #Die Funktion in fetch_weather.py von Adham
        normalized = normalize_weather_data(raw, city)      #Die raw-Daten normalisieren mit der Funktion von Julian

        return normalized                                   #Normalisierte Daten (dict) zurückgeben
    
    except Exception as error:                                      #Falls es nicht klappt, HTTP Error mit 400 throwen
        raise HTTPException(status_code=400, detail=str(error))