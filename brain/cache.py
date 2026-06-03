"""Preparacion de audios frecuentes para acelerar respuestas conocidas."""

from __future__ import annotations

from speech import SpeakResult, warm_up_tts_cache

from .knowledge import load_knowledge_entries


SYSTEM_TTS_PHRASES = (
    "Lista.",
    "Sigo activa.",
    "De acuerdo. Voy a detener el modo escucha.",
    "Deteniendo escucha",
    "Estoy lista. Dime que necesitas.",
    "No tengo una respuesta preparada para eso todavia.",
)


def warm_up_common_tts_cache() -> list[SpeakResult]:
    """Genera audios cacheados para respuestas frecuentes del asistente."""
    response_phrases = [entry.response for entry in load_knowledge_entries()]
    phrases = list(dict.fromkeys([*SYSTEM_TTS_PHRASES, *response_phrases]))
    return warm_up_tts_cache(phrases)
