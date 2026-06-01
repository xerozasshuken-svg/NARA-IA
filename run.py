from __future__ import annotations

import importlib.util
import sys


REQUIRED_MODULES = ("numpy", "sounddevice", "vosk")


def main():
    """Entry point for the NARA IA assistant."""
    if not _check_runtime_dependencies():
        sys.exit(1)

    from brain import run_listening_loop

    run_listening_loop(duration_seconds=3)


def _check_runtime_dependencies() -> bool:
    """Muestra una ayuda clara si el entorno local aun no esta preparado."""
    missing_modules = [
        module for module in REQUIRED_MODULES if importlib.util.find_spec(module) is None
    ]

    if not missing_modules:
        return True

    print("Faltan dependencias de Python para ejecutar NARA IA:")
    for module in missing_modules:
        print(f"- {module}")

    print()
    print("Crea un entorno virtual local e instala dependencias:")
    print("Windows PowerShell: .\\setup.ps1")
    print("Linux/Raspberry Pi: bash setup.sh")
    print()
    print("No copies la carpeta venv entre computadoras; cada equipo debe crear la suya.")
    return False


if __name__ == "__main__":
    main()
