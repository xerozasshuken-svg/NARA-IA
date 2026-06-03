"""Modulo de texto a voz usando Piper TTS con cache local de audio."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from utils import TTS_CACHE_DIR, ensure_data_dirs


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "voice.onnx"
MANIFEST_PATH = TTS_CACHE_DIR / "manifest.json"


@dataclass(frozen=True)
class SpeakResult:
    """Resultado util para comprobar si TTS uso cache o genero audio nuevo."""

    audio_path: Path
    cache_hit: bool
    text: str


def speak(text: str, use_cache: bool = True) -> SpeakResult:
    """Convierte texto en voz, reproduce el audio y devuelve datos de cache."""
    result = synthesize(text, use_cache=use_cache)
    _play_audio(result.audio_path)
    return result


def synthesize(text: str, use_cache: bool = True) -> SpeakResult:
    """Genera o recupera audio para un texto sin reproducirlo."""
    clean_text = _clean_text(text)
    audio_path = _cache_path_for_text(clean_text)

    if use_cache and audio_path.exists():
        _update_manifest(clean_text, audio_path, cache_hit=True)
        return SpeakResult(audio_path=audio_path, cache_hit=True, text=clean_text)

    ensure_data_dirs()
    piper_command = _resolve_piper_command()
    model_path = _resolve_model_path()
    _generate_audio(
        piper_command=piper_command,
        model_path=model_path,
        audio_path=audio_path,
        text=clean_text,
    )
    _update_manifest(clean_text, audio_path, cache_hit=False)
    return SpeakResult(audio_path=audio_path, cache_hit=False, text=clean_text)


def warm_up_tts_cache(texts: list[str]) -> list[SpeakResult]:
    """Prepara audios frecuentes para que las respuestas sean mas rapidas."""
    return [synthesize(text, use_cache=True) for text in texts]


def _clean_text(text: str) -> str:
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("El texto para sintetizar no puede estar vacio.")
    return clean_text


def _cache_path_for_text(text: str) -> Path:
    """Crea un nombre estable para cada frase cacheada."""
    ensure_data_dirs()
    text_hash = hashlib.sha256(text.casefold().encode("utf-8")).hexdigest()[:16]
    return TTS_CACHE_DIR / f"{text_hash}.wav"


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}

    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_manifest(manifest: dict) -> None:
    ensure_data_dirs()
    with MANIFEST_PATH.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, ensure_ascii=True, indent=2)


def _update_manifest(text: str, audio_path: Path, cache_hit: bool) -> None:
    manifest = _load_manifest()
    key = audio_path.name
    entry = manifest.get(key, {})
    now = datetime.now().isoformat(timespec="seconds")

    manifest[key] = {
        "text": text,
        "path": str(audio_path),
        "created_at": entry.get("created_at", now),
        "last_used_at": now,
        "uses": int(entry.get("uses", 0)) + 1,
        "last_cache_hit": cache_hit,
    }
    _save_manifest(manifest)


def _resolve_piper_command() -> str:
    """Localiza Piper desde variable de entorno, PATH o el entorno virtual local."""
    configured_command = os.getenv("NARA_PIPER_COMMAND")
    if configured_command:
        return configured_command

    path_command = shutil.which("piper")
    if path_command:
        return path_command

    local_commands = (
        PROJECT_ROOT / "venv" / "Scripts" / "piper.exe",
        PROJECT_ROOT / "venv" / "bin" / "piper",
        PROJECT_ROOT / ".venv" / "Scripts" / "piper.exe",
        PROJECT_ROOT / ".venv" / "bin" / "piper",
    )
    for local_command in local_commands:
        if local_command.exists():
            return str(local_command)

    raise FileNotFoundError(
        "No se encontro Piper. Instala piper-tts o define NARA_PIPER_COMMAND."
    )


def _resolve_model_path() -> Path:
    """Obtiene el modelo de voz local que Piper usara para sintetizar audio."""
    model_path = Path(os.getenv("NARA_PIPER_MODEL", DEFAULT_MODEL_PATH))
    if not model_path.exists():
        raise FileNotFoundError(
            f"No se encontro el modelo de Piper en {model_path}. "
            "Define NARA_PIPER_MODEL con la ruta a un archivo .onnx."
        )
    return model_path


def _generate_audio(
    *,
    piper_command: str,
    model_path: Path,
    audio_path: Path,
    text: str,
) -> None:
    """Genera un WAV cacheable invocando Piper por stdin."""
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            piper_command,
            "--model",
            str(model_path),
            "--output_file",
            str(audio_path),
        ],
        input=text,
        text=True,
        check=True,
    )


def _play_audio(audio_path: Path) -> None:
    """Reproduce el WAV con el reproductor disponible en el sistema."""
    configured_player = os.getenv("NARA_AUDIO_PLAYER")
    if configured_player:
        subprocess.run([configured_player, str(audio_path)], check=True)
        return

    system_name = platform.system()
    if system_name == "Linux":
        subprocess.run(["aplay", str(audio_path)], check=True)
        return

    if system_name == "Darwin":
        subprocess.run(["afplay", str(audio_path)], check=True)
        return

    if system_name == "Windows":
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "$player = New-Object System.Media.SoundPlayer "
                    f"'{audio_path}'; $player.PlaySync()"
                ),
            ],
            check=True,
        )
        return

    raise RuntimeError(
        "No hay reproductor de audio configurado. Define NARA_AUDIO_PLAYER."
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prueba y preparacion de TTS cache.")
    parser.add_argument("text", nargs="?", default="Hola. Estoy lista para ayudarte.")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Fuerza regenerar el audio aunque exista cache.",
    )
    parser.add_argument(
        "--synthesize-only",
        action="store_true",
        help="Genera o recupera el audio sin reproducirlo.",
    )
    return parser


def main() -> None:
    """Permite probar la cache ejecutando: python -m speech.tts."""
    args = _build_parser().parse_args()
    use_cache = not args.no_cache
    result = synthesize(args.text, use_cache=use_cache)

    if not args.synthesize_only:
        _play_audio(result.audio_path)

    status = "HIT" if result.cache_hit else "MISS"
    print(f"Cache: {status}")
    print(f"Audio: {result.audio_path}")


if __name__ == "__main__":
    main()
