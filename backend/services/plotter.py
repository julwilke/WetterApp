##################################################
# PLOTTER - 1.0.1
##################################################

# Imports
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

from io import BytesIO

# FUNKTION: Historische Daten / History oder Forecast
def build_single_line_plot_png(df, var, title, y_label):
    """
    Interne Funktion für beide Plots.
    Baut EINEN Plot (Linie) für history ODER Forecast und gibt PNG zurück.
    - "Agg" Argument verwenden, damit kein GUI-Backend von MPL verwendet wird
        sondern nur das Bild gerendert wird.
    - Input Parameter
        - df:       Pandas Data-Frame mit den anzuzeigenden Daten
        - var:      Name der Messgröße
        - title:    Plot-Titel
        - y_label:  Y-Achsen Beschriftung
    """
    
    # ===== 1) FEHLER ABFANGEN =====
    if df is None or df.empty:  #DataFrame leer
        return None

    if var not in df.columns:   #var fehlt
        return None

    # ===== 2) PLOT-STRUKTUR AUFBAUEN =====
    x = df["time"]
    y = df[var]

        # Subplots bilden
    fig, ax = plt.subplots(figsize=(12, 4))

    # ===== 3) PLOTTEN =====
    ax.plot(x, y, linewidth=1.8)    
    ax.set_title(title)
    ax.set_xlabel("Zeitpunkt")
    ax.set_ylabel(y_label)

    # ===== 4) LAYOUT =====
    fig.autofmt_xdate()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    # ===== 5) SPEICHERN =====
    buf = BytesIO()     #In-Memory speichern
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)

    return buf.getvalue()


# FUNKTION: Öffentliche Funktionen für History und Forecast

def build_single_history_plot_png(df, var, title, y_label):
    """
    Baut EINEN History-Plot (Linie) und gibt PNG zurück.
    Anwendung von _build_single_line_plot_png.
    """
    return build_single_line_plot_png(df, var, title, y_label)


def build_single_forecast_plot_png(df, var, title, y_label):
    """
    Baut EINEN Forecast-Plot (Linie) und gibt PNG zurück.
    Anwendung von _build_single_line_plot_png.
    """
    return build_single_line_plot_png(df, var, title, y_label)
    


