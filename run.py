from __future__ import annotations

import importlib.util
import argparse
import sys


REQUIRED_MODULES = ("numpy", "sounddevice", "vosk")


def main():
    """Entry point for the NARA IA assistant."""
    if not _check_runtime_dependencies():
        sys.exit(1)

    from brain import run_listening_loop, warm_up_common_tts_cache
    from audio import SilenceConfig

    args = _build_parser().parse_args()
    if args.warm_tts_cache:
        results = warm_up_common_tts_cache()
        for result in results:
            status = "HIT" if result.cache_hit else "MISS"
            print(f"{status}: {result.text} -> {result.audio_path}")
        return

    silence_config = SilenceConfig(
        threshold=args.silence_threshold,
        silence_seconds=args.silence_seconds,
        max_duration_seconds=args.duration,
    )
    run_listening_loop(
        duration_seconds=args.duration,
        use_silence_detection=not args.fixed_duration,
        silence_config=silence_config,
        verbose_prompts=args.verbose_prompts,
        quiet_start=args.quiet_start,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NARA IA asistente de voz local.")
    parser.add_argument(
        "--duration",
        type=float,
        default=8.0,
        help="Duracion maxima de escucha por turno.",
    )
    parser.add_argument(
        "--fixed-duration",
        action="store_true",
        help="Usa duracion fija en lugar de deteccion de silencio.",
    )
    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=0.015,
        help="Sensibilidad de silencio. Menor valor escucha sonidos mas bajos.",
    )
    parser.add_argument(
        "--silence-seconds",
        type=float,
        default=0.8,
        help="Segundos de silencio necesarios para terminar de grabar.",
    )
    parser.add_argument(
        "--verbose-prompts",
        action="store_true",
        help="Activa avisos hablados extra como Te escucho y Procesando.",
    )
    parser.add_argument(
        "--quiet-start",
        action="store_true",
        help="No dice Lista al iniciar; empieza a escuchar apenas carga modelos.",
    )
    parser.add_argument(
        "--warm-tts-cache",
        action="store_true",
        help="Genera audios cacheados para respuestas frecuentes y termina.",
    )
    return parser


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
