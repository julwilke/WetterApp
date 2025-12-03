import os
import folium
import shutil

# Zielordner
IMAGE_DIR = "/workspaces/WetterApp/weather_dashboard/static/map"

def clear_image_folder():
    """
    Löscht alle Dateien im image-Ordner.
    """
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    for filename in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Fehler beim Löschen von {file_path}: {e}")

    print("Ordner geleert.")

# temp hier übergeben

def generate_map(lat, lon, temp="--", zoom=12):
    """
    Erstellt eine Folium-Karte und speichert sie als map.html.
    """
    print(f"Erstelle Karte für Koordinaten: {lat}, {lon}")

    m = folium.Map(location=[lat, lon], zoom_start=zoom)

    # Grauer Tile-Layer (TopPlus Open Grau)
    #folium.TileLayer(
    #    tiles='http://sgx.geodatenzentrum.de/wmts_topplus_open/tile/1.0.0/web_grau/default/WEBMERCATOR/{z}/{y}/{x}.png',
    #    attr='Map data: &copy; <a href="http://www.govdata.de/dl-de/by-2-0">dl-de/by-2-0</a>',
    #    name='TopPlus Open Grau',
    #    max_zoom=18
    #).add_to(m)

    # Temperatur-Pin (DivIcon mit Kasten + Pfeil)
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

    folium.Marker(
        [lat, lon],
        icon=folium.DivIcon(
            html=html,
            icon_size=(30, 30),
            icon_anchor=(24, 45)
        ),
        tooltip=f"{temp}°C"
    ).add_to(m)


    output_path = os.path.join(IMAGE_DIR, "map.html")
    m.save(output_path)

    print(f"Karte gespeichert unter: {output_path}")


if __name__ == "__main__":
    clear_image_folder()
    generate_map()
