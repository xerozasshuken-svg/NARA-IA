"""Base local de preguntas y respuestas preformuladas."""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path


RESPONSES_PATH = Path(__file__).with_name("responses.json")


@dataclass(frozen=True)
class KnowledgeEntry:
    """Entrada editable de conocimiento local."""

    id: str
    patterns: tuple[str, ...]
    response: str


def find_predefined_response(command: str) -> str | None:
    """Busca una respuesta local por coincidencia simple de patrones."""
    normalized_command = normalize_text(command)

    for entry in load_knowledge_entries():
        for pattern in entry.patterns:
            if normalize_text(pattern) in normalized_command:
                return entry.response

    return None


def load_knowledge_entries(path: Path = RESPONSES_PATH) -> list[KnowledgeEntry]:
    """Carga preguntas y respuestas desde JSON para mantenerlas editables."""
    with path.open("r", encoding="utf-8") as file:
        raw_entries = json.load(file)

    return [
        KnowledgeEntry(
            id=str(entry["id"]),
            patterns=tuple(entry["patterns"]),
            response=str(entry["response"]),
        )
        for entry in raw_entries
    ]


def normalize_text(text: str) -> str:
    """Normaliza texto para comparar comandos sin depender de acentos o mayusculas."""
    without_accents = unicodedata.normalize("NFD", text.casefold())
    return "".join(
        character
        for character in without_accents
        if unicodedata.category(character) != "Mn"
    ).strip()
