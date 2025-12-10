##############################################
#   🌦 WETTER-DASHBOARD – MAP GENERATOR 1.1 #
##############################################

# =============== IMPORTS ====================
import os
import folium

# ============================================
#   KONSTANTEN / ORDNER (J: Nach unten verschoben und mit "dynamischen" Pfaden angepasst)
# ============================================
# ...


# ============================================
#   MAP GENERIEREN
# ============================================
def generate_map(lat=52.5200, lon=13.4050, temp="--", zoom=12):
    """
    Erstellt eine Folium-Karte für gegebene Koordinaten.
    Fügt einen Temperatur-Pin hinzu und speichert die Karte als map.html.
    
    Parameter:
        lat (float): Breitengrad
        lon (float): Längengrad
        temp (str/int): Temperatur für Marker
        zoom (int): Zoom-Level der Karte
    """
    print(f"🗺️  Erstelle Karte für Koordinaten: {lat}, {lon}")

    # Neue Folium-Karte
    m = folium.Map(location=[lat, lon], zoom_start=zoom)

    # Temperatur-Pin als DivIcon
    html = f"""
    <div style="position: relative; display: inline-block; text-align:center; white-space: nowrap;">
        <div style="
            background-color: #ff5722;
            color: white;
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            white-space: nowrap;
        ">
            {temp} °C
        </div>
        <div style="
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 10px solid #ff5722;
            margin: 0 auto;
        "></div>
    </div>
    """

    # Marker auf der Karte setzen
    folium.Marker(
        [lat, lon],
        icon=folium.DivIcon(
            html=html,
            icon_size=(30, 30),
            icon_anchor=(24, 45)
        ),
        tooltip=f"{temp}°C"
    ).add_to(m)

    # Zielordner für die Map-Datei
    # backend/
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # WetterApp/
    project_root = os.path.abspath(os.path.join(base_dir, ".."))

    # WetterApp/weather_dashboard/static/map
    map_dir = os.path.join(project_root, "weather_dashboard", "static", "map")

    # Ordner sicher erstellen
    os.makedirs(map_dir, exist_ok=True)

    # Zieldatei
    output_path = os.path.join(map_dir, "map.html")

    # Karte speichern
    m.save(output_path)

    #Ausgabe Konsole
    print(f"✅ Karte gespeichert unter: {output_path}")