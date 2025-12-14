"""
# weather_cli.py (Repo-Root)
# Dünner Kompatibilitäts-Wrapper — importiert die Implementierung aus cli.cli
# Aufruf über 'python -m cli.cli' ebenfalls möglich
"""

# Import
from cli.cli import main as cli_main


def main() -> None:
    raise SystemExit(cli_main())


if __name__ == "__main__":
    main()


