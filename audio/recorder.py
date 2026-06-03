"""Captura minima de microfono para NARA IA."""

from __future__ import annotations

import argparse
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd

from utils import RECORDINGS_DIR, ensure_data_dirs


@dataclass(frozen=True)
class AudioConfig:
    """Configuracion base para audio compatible con modelos STT offline."""

    sample_rate: int = 16_000
    channels: int = 1
    dtype: str = "float32"


@dataclass(frozen=True)
class SilenceConfig:
    """Configuracion para cortar la grabacion cuando el usuario deja de hablar."""

    threshold: float = 0.015
    silence_seconds: float = 1.0
    max_duration_seconds: float = 8.0
    min_recording_seconds: float = 0.5
    block_duration_seconds: float = 0.1


def record_audio(
    duration_seconds: float,
    config: AudioConfig | None = None,
    device: int | str | None = None,
) -> np.ndarray:
    """Graba audio desde el microfono y devuelve muestras normalizadas."""
    if duration_seconds <= 0:
        raise ValueError("La duracion de grabacion debe ser mayor que cero.")

    audio_config = config or AudioConfig()
    frame_count = int(duration_seconds * audio_config.sample_rate)

    # sounddevice entrega float32 entre -1.0 y 1.0, ideal para procesar antes de STT.
    recording = sd.rec(
        frames=frame_count,
        samplerate=audio_config.sample_rate,
        channels=audio_config.channels,
        dtype=audio_config.dtype,
        device=device,
    )
    sd.wait()

    return recording


def record_audio_until_silence(
    config: AudioConfig | None = None,
    silence_config: SilenceConfig | None = None,
    device: int | str | None = None,
) -> np.ndarray:
    """Graba hasta detectar silencio o alcanzar una duracion maxima."""
    audio_config = config or AudioConfig()
    silence = silence_config or SilenceConfig()
    block_size = int(audio_config.sample_rate * silence.block_duration_seconds)
    max_blocks = int(silence.max_duration_seconds / silence.block_duration_seconds)
    silence_blocks_needed = int(silence.silence_seconds / silence.block_duration_seconds)
    min_blocks = int(silence.min_recording_seconds / silence.block_duration_seconds)

    recorded_blocks: list[np.ndarray] = []
    silent_blocks = 0
    speech_started = False

    with sd.InputStream(
        samplerate=audio_config.sample_rate,
        channels=audio_config.channels,
        dtype=audio_config.dtype,
        device=device,
        blocksize=block_size,
    ) as stream:
        for block_index in range(max_blocks):
            block, _ = stream.read(block_size)
            recorded_blocks.append(block.copy())

            volume = _rms(block)
            if volume >= silence.threshold:
                speech_started = True
                silent_blocks = 0
            elif speech_started:
                silent_blocks += 1

            enough_audio = block_index + 1 >= min_blocks
            enough_silence = silent_blocks >= silence_blocks_needed
            if speech_started and enough_audio and enough_silence:
                break

    if not recorded_blocks:
        return np.empty((0, audio_config.channels), dtype=audio_config.dtype)

    return np.concatenate(recorded_blocks, axis=0)


def save_wav(
    samples: np.ndarray,
    output_path: str | Path,
    config: AudioConfig | None = None,
) -> Path:
    """Guarda muestras de audio como WAV PCM de 16 bits."""
    audio_config = config or AudioConfig()
    wav_path = Path(output_path)
    wav_path.parent.mkdir(parents=True, exist_ok=True)

    pcm_samples = _float_to_pcm16(samples)

    with wave.open(str(wav_path), "wb") as wav_file:
        wav_file.setnchannels(audio_config.channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(audio_config.sample_rate)
        wav_file.writeframes(pcm_samples.tobytes())

    return wav_path


def record_to_wav(
    duration_seconds: float,
    output_path: str | Path | None = None,
    config: AudioConfig | None = None,
    device: int | str | None = None,
) -> Path:
    """Graba audio del microfono y lo guarda en un archivo WAV."""
    audio_config = config or AudioConfig()
    wav_path = Path(output_path) if output_path else _default_recording_path()
    samples = record_audio(duration_seconds, config=audio_config, device=device)
    return save_wav(samples, wav_path, config=audio_config)


def record_to_wav_until_silence(
    output_path: str | Path | None = None,
    config: AudioConfig | None = None,
    silence_config: SilenceConfig | None = None,
    device: int | str | None = None,
) -> Path:
    """Graba audio y corta automaticamente cuando detecta silencio."""
    audio_config = config or AudioConfig()
    wav_path = Path(output_path) if output_path else _default_recording_path()
    samples = record_audio_until_silence(
        config=audio_config,
        silence_config=silence_config,
        device=device,
    )
    return save_wav(samples, wav_path, config=audio_config)


def _float_to_pcm16(samples: np.ndarray) -> np.ndarray:
    """Convierte muestras float32 normalizadas a PCM int16."""
    clipped = np.clip(samples, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)


def _rms(samples: np.ndarray) -> float:
    """Calcula volumen RMS para detectar voz de forma simple."""
    return float(np.sqrt(np.mean(np.square(samples))))


def _default_recording_path() -> Path:
    """Crea una ruta ordenada para grabaciones de prueba y comandos."""
    ensure_data_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return RECORDINGS_DIR / f"recording_{timestamp}.wav"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prueba de captura de microfono.")
    parser.add_argument(
        "--duration",
        type=float,
        default=3.0,
        help="Segundos a grabar.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Archivo WAV de salida. Por defecto usa data/recordings/.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="ID o nombre del dispositivo de entrada.",
    )
    parser.add_argument(
        "--silence",
        action="store_true",
        help="Graba hasta detectar silencio en lugar de usar duracion fija.",
    )
    return parser


def main() -> None:
    """Permite probar la captura ejecutando: python -m audio.recorder."""
    args = _build_parser().parse_args()
    if args.silence:
        output_path = record_to_wav_until_silence(
            output_path=args.output,
            silence_config=SilenceConfig(max_duration_seconds=args.duration),
            device=args.device,
        )
    else:
        output_path = record_to_wav(
            duration_seconds=args.duration,
            output_path=args.output,
            device=args.device,
        )
    print(f"Audio grabado en: {output_path}")


if __name__ == "__main__":
    main()
