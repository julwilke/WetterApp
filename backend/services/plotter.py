##################################################
# PLOTTER - 1.0.0
##################################################

# Imports
import matplotlib
matplotlib.use("Agg")  # wichtig: kein Display nötig auf Server
import matplotlib.pyplot as plt

from io import BytesIO

# FUNKTION: Historische Daten / History
def build_single_history_plot_png(df, var, title, y_label):
    """
    Baut EINEN Plot (Linie) und gibt PNG-Bytes zurück.
    """
    
    # ===== 1) FEHLER ABFANGEN =====
    if df is None or df.empty:
        return None

    if var not in df.columns:
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


# FUNKTION: Vorhersage / Forecast
def build_single_forecast_plot_png(df, var, title, y_label):
    """
    Baut EINEN Forecast-Plot (Linie) und gibt PNG-Bytes zurück
    """

    # ===== 1) FEHLER ABFANGEN ======
    if df is None or df.empty:
        return None
    
    if var not in df.columns:
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
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)

    return buf.getvalue()
    


