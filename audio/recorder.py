"""Captura minima de microfono para NARA IA."""

from __future__ import annotations

import argparse
import wave
from datetime import datetime
from dataclasses import dataclass
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


def _float_to_pcm16(samples: np.ndarray) -> np.ndarray:
    """Convierte muestras float32 normalizadas a PCM int16."""
    clipped = np.clip(samples, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)


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
    return parser


def main() -> None:
    """Permite probar la captura ejecutando: python -m audio.recorder."""
    args = _build_parser().parse_args()
    output_path = record_to_wav(
        duration_seconds=args.duration,
        output_path=args.output,
        device=args.device,
    )
    print(f"Audio grabado en: {output_path}")


if __name__ == "__main__":
    main()
