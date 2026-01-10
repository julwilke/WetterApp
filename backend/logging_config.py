"""
Zentrale Logging-Konfiguration für das gesamte Projekt.
Diese Datei wird einmal in app.py aufgerufen.
Alle anderen Module holen sich nur noch einen Logger über: 
    logger = logging.getLogger(__name__)
"""
import os
import logging

def configure_logging(level: int = logging.INFO) -> None:
    """
    Richtet die grundlegende Logging-Konfiguration ein.

    Args:
        level: Minimale Log-Level-Schwelle (z.B. logging.INFO, logging.DEBUG,... einstellbar im .env)
    """
    
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper() # CAPS falsch im .env falsch eingetragen, und Default auf 'INFO'
    
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Grundlegende Konfiguration des Loggings, sollte nur EINMAL aufgerufen werden
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

