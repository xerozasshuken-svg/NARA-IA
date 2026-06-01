"""Modulo minimo de texto a voz usando Piper TTS."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "voice.onnx"


def speak(text: str) -> None:
    """Convierte texto en voz con Piper y reproduce el audio generado."""
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("El texto para sintetizar no puede estar vacio.")

    piper_command = _resolve_piper_command()
    model_path = _resolve_model_path()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        audio_path = Path(temp_audio.name)

    try:
        _generate_audio(
            piper_command=piper_command,
            model_path=model_path,
            audio_path=audio_path,
            text=clean_text,
        )
        _play_audio(audio_path)
    finally:
        # El archivo existe solo mientras se sintetiza y reproduce la respuesta.
        audio_path.unlink(missing_ok=True)


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
    """Genera un WAV temporal invocando Piper por stdin."""
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
