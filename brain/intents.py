"""Resolucion basica de intenciones para comandos de voz."""

from __future__ import annotations

from datetime import datetime

from .knowledge import find_predefined_response, normalize_text


def generate_response(command: str) -> str:
    """Genera una respuesta local para un comando ya activado por wake word."""
    clean_command = command.strip()
    if not clean_command:
        return "Estoy lista. Dime que necesitas."

    dynamic_response = _resolve_dynamic_intent(clean_command)
    if dynamic_response:
        return dynamic_response

    predefined_response = find_predefined_response(clean_command)
    if predefined_response:
        return predefined_response

    return "No tengo una respuesta preparada para eso todavia."


def _resolve_dynamic_intent(command: str) -> str | None:
    """Resuelve intenciones que no conviene guardar como texto fijo."""
    normalized_command = normalize_text(command)
    now = datetime.now()

    if "hora" in normalized_command:
        return f"Son las {now:%H:%M}."

    if "fecha" in normalized_command or "dia es hoy" in normalized_command:
        return f"Hoy es {now:%d/%m/%Y}."

    if any(
        stop_command in normalized_command
        for stop_command in ("salir", "termina", "detente", "apagate", "finaliza")
    ):
        return "De acuerdo."

    return None
