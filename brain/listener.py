"""Loop continuo de escucha por turnos para NARA IA."""

from __future__ import annotations

import time

from speech import WakeWordConfig, speak
from utils import cleanup_recordings

from .assistant import VoiceTurnResult, run_voice_turn
from .knowledge import normalize_text


DEFAULT_IDLE_RESPONSE = "Sigo activa. Di Nara para llamarme."
STOP_COMMANDS = ("salir", "termina", "detente", "apagate", "finaliza")


def run_listening_loop(
    duration_seconds: float = 3.0,
    pause_seconds: float = 0.5,
    wake_config: WakeWordConfig | None = None,
    max_turns: int | None = None,
    cleanup_every_turns: int = 10,
    keep_latest_recordings: int = 20,
) -> None:
    """Escucha en ciclos cortos hasta recibir un comando de salida."""
    speak("NARA esta activa.")

    turn_count = 0
    while max_turns is None or turn_count < max_turns:
        turn_count += 1
        result = run_voice_turn(
            duration_seconds=duration_seconds,
            wake_config=wake_config,
            idle_response=DEFAULT_IDLE_RESPONSE,
        )
        _print_turn_summary(result)

        if cleanup_every_turns > 0 and turn_count % cleanup_every_turns == 0:
            cleanup_result = cleanup_recordings(keep_latest=keep_latest_recordings)
            if cleanup_result.deleted_count:
                print(f"Limpieza: {cleanup_result.deleted_count} grabaciones borradas.")

        if result.wake_word_detected and _is_stop_command(result.command):
            speak("Deteniendo escucha")
            break

        time.sleep(pause_seconds)


def _is_stop_command(command: str) -> bool:
    """Detecta comandos hablados para salir del loop continuo."""
    normalized_command = normalize_text(command)
    return any(stop_command in normalized_command for stop_command in STOP_COMMANDS)


def _print_turn_summary(result: VoiceTurnResult) -> None:
    """Muestra informacion util para depurar lo que NARA entendio."""
    print("--- Turno de escucha ---")
    print(f"Audio: {result.audio_path}")
    print(f"Texto: {result.transcript}")
    print(f"Activacion: {result.wake_word_detected}")
    print(f"Comando: {result.command}")
    print(f"Respuesta: {result.response}")
    print(
        "Tiempos: "
        f"escucha={result.timings.listen_seconds:.2f}s, "
        f"brain={result.timings.think_seconds:.2f}s, "
        f"voz={result.timings.speak_seconds:.2f}s, "
        f"total={result.timings.total_seconds:.2f}s"
    )
