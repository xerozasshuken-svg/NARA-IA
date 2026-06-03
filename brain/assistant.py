"""Orquestacion minima del flujo de voz de NARA IA."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from audio import SilenceConfig
from speech import WakeWordConfig, extract_command, record_and_transcribe, speak
from .intents import generate_response


@dataclass(frozen=True)
class TurnTimings:
    """Tiempos internos de un turno de voz."""

    listen_seconds: float
    think_seconds: float
    speak_seconds: float

    @property
    def total_seconds(self) -> float:
        return self.listen_seconds + self.think_seconds + self.speak_seconds


@dataclass(frozen=True)
class VoiceTurnResult:
    """Resultado de un ciclo corto de escucha, transcripcion y activacion."""

    audio_path: Path
    transcript: str
    wake_word_detected: bool
    command: str
    response: str
    timings: TurnTimings


def run_voice_turn(
    duration_seconds: float = 3.0,
    wake_config: WakeWordConfig | None = None,
    listen_prompt: str = "Te escucho.",
    idle_response: str = "No escuche mi palabra de activacion.",
    processing_prompt: str | None = None,
    use_silence_detection: bool = True,
    silence_config: SilenceConfig | None = None,
) -> VoiceTurnResult:
    """Ejecuta un turno de voz y responde si detecta la palabra de activacion."""
    if listen_prompt:
        speak(listen_prompt)

    listen_start = perf_counter()
    audio_path, transcript = record_and_transcribe(
        duration_seconds,
        use_silence_detection=use_silence_detection,
        silence_config=silence_config,
    )
    listen_seconds = perf_counter() - listen_start
    if processing_prompt:
        speak(processing_prompt)

    think_start = perf_counter()
    command = extract_command(transcript, config=wake_config)
    wake_word_detected = command is not None

    if wake_word_detected:
        response = generate_response(command or "")
    else:
        response = idle_response
    think_seconds = perf_counter() - think_start

    speak_start = perf_counter()
    speak(response)
    speak_seconds = perf_counter() - speak_start

    return VoiceTurnResult(
        audio_path=audio_path,
        transcript=transcript,
        wake_word_detected=wake_word_detected,
        command=command or "",
        response=response,
        timings=TurnTimings(
            listen_seconds=listen_seconds,
            think_seconds=think_seconds,
            speak_seconds=speak_seconds,
        ),
    )
