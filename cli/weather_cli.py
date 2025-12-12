"""
# cli/weather_cli.py
# Thin compatibility wrapper that re-exports the implementation from cli.cli
"""
from .cli import parse_weather_data, display_weather, log_to_csv, main  # type: ignore

__all__ = ["parse_weather_data", "display_weather", "log_to_csv", "main"]
