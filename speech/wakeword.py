"""Configuracion inicial de palabra de activacion."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class WakeWordConfig:
    """Define como se invoca al asistente antes de procesar comandos."""

    phrase: str = os.getenv("NARA_WAKE_WORD", "nara")


def contains_wake_word(text: str, config: WakeWordConfig | None = None) -> bool:
    """Evalua texto ya transcrito para saber si contiene la palabra de activacion."""
    return extract_command(text, config=config) is not None


def extract_command(text: str, config: WakeWordConfig | None = None) -> str | None:
    """Devuelve el texto posterior a la palabra de activacion, si aparece."""
    wake_config = config or WakeWordConfig()
    normalized_text = text.casefold().strip()
    normalized_phrase = wake_config.phrase.casefold().strip()

    if not normalized_phrase:
        return None

    wake_index = normalized_text.find(normalized_phrase)
    if wake_index == -1:
        return None

    command_start = wake_index + len(normalized_phrase)
    return text[command_start:].strip(" ,.:;")
