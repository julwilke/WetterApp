# weather_cli.py (Wrapper)
# Diese Datei liegt im Repo-Root und sorgt dafür, dass bestehende Tests und Werkzeuge,
# die "from weather_cli import ..." erwarten, weiterhin funktionieren, auch wenn die
# eigentliche Implementierung im Unterordner cli/ liegt.
#
# Verhalten:
# - Versucht zuerst, die Implementierung aus cli.cli (cli/cli.py) zu importieren.
# - Falls das fehlschlägt, versucht sie cli.weather_cli (cli/weather_cli.py).
# - Exportiert parse_weather_data, display_weather, log_to_csv und main (falls vorhanden).
# - Führt main() aus, wenn diese Datei als Skript direkt gestartet wird.
#
# Hinweis: Diese Datei enthält keine Logik, nur Weiterleitungen / Kompatibilität.

try:
    # Versuch: Implementierung liegt in cli/cli.py (Modul cli.cli)
    from cli.cli import parse_weather_data, display_weather, log_to_csv  # type: ignore
    try:
        from cli.cli import main as _main  # type: ignore
    except Exception:
        _main = None
except Exception:
    try:
        # Fallback: Implementierung liegt in cli/weather_cli.py (Modul cli.weather_cli)
        from cli.weather_cli import parse_weather_data, display_weather, log_to_csv  # type: ignore
        try:
            from cli.weather_cli import main as _main  # type: ignore
        except Exception:
            _main = None
    except Exception:
        # Wenn alles fehlschlägt, geben wir eine aussagekräftige ImportError-Meldung,
        # damit CI / Entwickler sofort sehen, woran es liegt.
        raise ImportError(
            "Konnte die CLI-Implementierung nicht importieren. "
            "Erwarte entweder cli/cli.py oder cli/weather_cli.py mit den Funktionen "
            "parse_weather_data, display_weather, log_to_csv (und optional main)."
        )

# Exportiere Symbole auf Modulebene, damit "from weather_cli import ..." weiterhin funktioniert.
__all__ = ["parse_weather_data", "display_weather", "log_to_csv"]

# Stelle main als Funktion zur Verfügung, falls vorhanden
if "_main" in globals() and _main:
    def main() -> None:
        return _main()
else:
    # main existiert nicht in der Implementierung — define a no-op that raises if used
    def main() -> None:
        raise RuntimeError("Kein main() in der CLI-Implementierung gefunden.")

# Wenn diese Datei direkt ausgeführt wird, rufe main() auf (sofern vorhanden).
if __name__ == "__main__":
    main()
