"""Loop continuo de escucha por turnos para NARA IA."""

from __future__ import annotations

import time

from audio import SilenceConfig
from speech import WakeWordConfig, speak, warm_up_stt
from utils import cleanup_recordings

from .assistant import VoiceTurnResult, run_voice_turn
from .knowledge import normalize_text


DEFAULT_IDLE_RESPONSE = "Sigo activa."
STOP_COMMANDS = ("salir", "termina", "detente", "apagate", "finaliza")


def run_listening_loop(
    duration_seconds: float = 8.0,
    pause_seconds: float = 0.15,
    wake_config: WakeWordConfig | None = None,
    max_turns: int | None = None,
    cleanup_every_turns: int = 10,
    keep_latest_recordings: int = 20,
    use_silence_detection: bool = True,
    silence_config: SilenceConfig | None = None,
    verbose_prompts: bool = False,
    quiet_start: bool = False,
) -> None:
    """Escucha en ciclos cortos hasta recibir un comando de salida."""
    print("[NARA] Inicializando modelos...")
    model_path = warm_up_stt()
    print(f"[NARA] Modelo Vosk listo: {model_path}")
    if not quiet_start:
        speak("Lista.")

    turn_count = 0
    while max_turns is None or turn_count < max_turns:
        turn_count += 1
        print("[NARA] Escuchando...")
        result = run_voice_turn(
            duration_seconds=duration_seconds,
            wake_config=wake_config,
            idle_response=DEFAULT_IDLE_RESPONSE,
            listen_prompt="Te escucho." if verbose_prompts else "",
            processing_prompt="Procesando." if verbose_prompts else None,
            use_silence_detection=use_silence_detection,
            silence_config=silence_config,
        )
        print("[NARA] Turno terminado.")
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
