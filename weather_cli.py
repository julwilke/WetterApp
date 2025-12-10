"""
# weather_cli.py (Repo-Root)
# Dünner Kompatibilitäts-Wrapper — importiert die Implementierung aus cli.cli
"""

try:
    from cli.cli import parse_weather_data, display_weather, log_to_csv  # type: ignore
    try:
        from cli.cli import main as _main  # type: ignore
    except Exception:
        _main = None
except Exception as e:
    raise ImportError(
        "Konnte die CLI-Implementierung nicht importieren. Erwartet cli/cli.py."
    ) from e

__all__ = ["parse_weather_data", "display_weather", "log_to_csv"]

if "_main" in globals() and _main:
    def main() -> None:
        return _main()
else:
    def main() -> None:
        raise RuntimeError("Kein main() in der CLI-Implementierung gefunden.")

if __name__ == "__main__":
    main()
