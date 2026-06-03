"""Transcripcion de voz a texto usando Vosk."""

from __future__ import annotations

import argparse
import json
import os
import wave
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from audio import SilenceConfig, record_to_wav, record_to_wav_until_silence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"


@dataclass(frozen=True)
class VoskConfig:
    """Configuracion del motor STT offline."""

    model_path: Path | None = None


def transcribe_wav(
    audio_path: str | Path,
    config: VoskConfig | None = None,
) -> str:
    """Transcribe un archivo WAV mono PCM usando un modelo local de Vosk."""
    model_path = _resolve_model_path(config)

    # Import tardio: permite importar el modulo aunque Vosk aun no este instalado.
    from vosk import KaldiRecognizer, SetLogLevel

    SetLogLevel(-1)

    with wave.open(str(audio_path), "rb") as wav_file:
        _validate_wav(wav_file)

        model = _load_model(str(model_path))
        recognizer = KaldiRecognizer(model, wav_file.getframerate())
        text_parts: list[str] = []

        while True:
            data = wav_file.readframes(4000)
            if not data:
                break

            if recognizer.AcceptWaveform(data):
                partial_result = json.loads(recognizer.Result())
                text = partial_result.get("text", "").strip()
                if text:
                    text_parts.append(text)

        final_result = json.loads(recognizer.FinalResult())
        final_text = final_result.get("text", "").strip()
        if final_text:
            text_parts.append(final_text)

    return " ".join(text_parts).strip()


@lru_cache(maxsize=2)
def _load_model(model_path: str):
    """Carga y reutiliza modelos Vosk para evitar recargas en cada turno."""
    from vosk import Model, SetLogLevel

    SetLogLevel(-1)
    return Model(model_path)


def record_and_transcribe(
    duration_seconds: float = 3.0,
    config: VoskConfig | None = None,
    use_silence_detection: bool = False,
    silence_config: SilenceConfig | None = None,
) -> tuple[Path, str]:
    """Graba audio del microfono y devuelve la ruta junto a la transcripcion."""
    if use_silence_detection:
        audio_path = record_to_wav_until_silence(
            silence_config=silence_config
            or SilenceConfig(max_duration_seconds=duration_seconds)
        )
    else:
        audio_path = record_to_wav(duration_seconds)
    transcript = transcribe_wav(audio_path, config=config)
    return audio_path, transcript


def warm_up_stt(config: VoskConfig | None = None) -> Path:
    """Carga el modelo Vosk antes de escuchar para evitar demora en el primer turno."""
    model_path = _resolve_model_path(config)
    _load_model(str(model_path))
    return model_path


def _resolve_model_path(config: VoskConfig | None = None) -> Path:
    """Busca el modelo Vosk por configuracion, variable de entorno o carpeta local."""
    configured_path = config.model_path if config else None
    env_path = os.getenv("NARA_VOSK_MODEL")
    model_path = configured_path or (Path(env_path) if env_path else None)

    if model_path:
        resolved_path = Path(model_path)
        if resolved_path.exists():
            return resolved_path
        raise FileNotFoundError(f"No se encontro el modelo Vosk en {resolved_path}.")

    candidates = sorted(
        path for path in MODELS_DIR.iterdir() if path.is_dir() and "vosk" in path.name
    )
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        "No se encontro un modelo Vosk. Descarga un modelo offline en models/ "
        "o define NARA_VOSK_MODEL con la ruta de la carpeta del modelo."
    )


def _validate_wav(wav_file: wave.Wave_read) -> None:
    """Vosk espera audio WAV mono PCM; el recorder del proyecto ya genera ese formato."""
    if wav_file.getnchannels() != 1:
        raise ValueError("Vosk requiere WAV mono de un solo canal.")

    if wav_file.getsampwidth() != 2:
        raise ValueError("Vosk requiere WAV PCM de 16 bits.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcripcion offline con Vosk.")
    parser.add_argument(
        "--audio",
        type=Path,
        default=None,
        help="WAV a transcribir. Si se omite, graba desde el microfono.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=3.0,
        help="Segundos a grabar cuando no se pasa --audio.",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=None,
        help="Ruta a la carpeta del modelo Vosk.",
    )
    parser.add_argument(
        "--silence",
        action="store_true",
        help="Graba hasta detectar silencio en lugar de usar duracion fija.",
    )
    return parser


def main() -> None:
    """Permite probar STT ejecutando: python -m speech.stt."""
    args = _build_parser().parse_args()
    config = VoskConfig(model_path=args.model)

    if args.audio:
        audio_path = args.audio
        transcript = transcribe_wav(audio_path, config=config)
    else:
        audio_path, transcript = record_and_transcribe(
            duration_seconds=args.duration,
            config=config,
            use_silence_detection=args.silence,
        )

    print(f"Audio: {audio_path}")
    print(f"Texto: {transcript}")


if __name__ == "__main__":
    main()
