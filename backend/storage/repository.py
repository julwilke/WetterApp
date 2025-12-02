#Persistente Datenhaltungsschicht
 
def save_entry(city, provider, payload):
    """
    Speichert einen Eintrag für eine Stadt, einen Provider und die zugehörigen Daten.
    
    Args:
        city: Name der Stadt
        provider: Name des Wetter-Providers
        payload: Die zu speichernden Daten
    """
    pass

def get_history(city=None, limit=20):
    """
    Ruft die Historie der gespeicherten Wettereinträge ab.
    
    Args:
        city: Name der Stadt (optional, wenn None werden alle Städte abgerufen)
        limit: Maximale Anzahl der zurückzugebenden Einträge (Standard: 20)
        
    Returns:
        Liste der Einträge, gefiltert nach Stadt falls angegeben
    """
    pass