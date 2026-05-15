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
    wake_config = config or WakeWordConfig()
    normalized_text = text.casefold().strip()
    normalized_phrase = wake_config.phrase.casefold().strip()
    return bool(normalized_phrase and normalized_phrase in normalized_text)
