"""Rutas compartidas para archivos generados por NARA IA."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RECORDINGS_DIR = DATA_DIR / "recordings"


def ensure_data_dirs() -> None:
    """Crea las carpetas de datos locales que el asistente necesita."""
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
