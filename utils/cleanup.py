"""Limpieza de archivos generados por NARA IA."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .paths import RECORDINGS_DIR


@dataclass(frozen=True)
class CleanupResult:
    """Resumen de archivos eliminados durante una limpieza."""

    deleted_files: tuple[Path, ...]

    @property
    def deleted_count(self) -> int:
        return len(self.deleted_files)


def cleanup_recordings(
    directory: Path = RECORDINGS_DIR,
    keep_latest: int = 20,
    older_than_days: int | None = None,
) -> CleanupResult:
    """Elimina grabaciones antiguas conservando las mas recientes."""
    if not directory.exists():
        return CleanupResult(deleted_files=())

    recordings = sorted(
        directory.glob("*.wav"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    files_to_delete = set(recordings[keep_latest:])

    if older_than_days is not None:
        cutoff = datetime.now() - timedelta(days=older_than_days)
        for recording in recordings:
            modified_at = datetime.fromtimestamp(recording.stat().st_mtime)
            if modified_at < cutoff:
                files_to_delete.add(recording)

    deleted_files: list[Path] = []
    for recording in sorted(files_to_delete):
        recording.unlink(missing_ok=True)
        deleted_files.append(recording)

    return CleanupResult(deleted_files=tuple(deleted_files))
