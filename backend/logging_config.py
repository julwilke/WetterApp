"""
Zentrale Logging-Konfiguration für das gesamte Projekt.
Diese Datei wird einmal in app.py aufgerufen.
Alle anderen Module holen sich nur noch einen Logger über: 
    logger = logging.getLogger(__name__)
"""

import logging

def configure_logging(level: int = logging.INFO) -> None:
    """
    Richtet die grundlegende Logging-Konfiguration ein.

    Args:
        level: Minimale Log-Level-Schwelle (z.B. logging.INFO, logging.DEBUG)
    """
    # Grundlegende Konfiguration des Loggings, sollte nur EINMAL aufgerufen werden
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )