import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def resolve_metadata_output_path(
    output_csv_path: str | Path | None,
    output_metadata_path: str | Path | None,
) -> Path:
    """
    Wyznacza ścieżkę zapisu pliku metadanych eksperymentu.

    Jeśli użytkownik podał output_metadata_path, używana jest ta ścieżka.
    Jeśli podał tylko output_csv_path, tworzona jest ścieżka obok CSV
    z końcówką .metadata.json.

    Args:
        output_csv_path: Opcjonalna ścieżka do CSV.
        output_metadata_path: Opcjonalna jawna ścieżka do JSON z metadanymi.

    Returns:
        Ścieżka do pliku metadanych.

    Raises:
        ValueError: Jeśli nie podano ani CSV, ani ścieżki metadanych.
    """
    if output_metadata_path is not None:
        return Path(output_metadata_path)

    if output_csv_path is not None:
        csv_path = Path(output_csv_path)
        return csv_path.with_suffix(".metadata.json")

    raise ValueError("Either output_csv_path or output_metadata_path must be provided.")


def write_experiment_metadata(
    metadata: Mapping[str, Any],
    output_path: str | Path,
) -> Path:
    """
    Zapisuje metadane eksperymentu do pliku JSON.

    Args:
        metadata: Słownik z konfiguracją eksperymentu.
        output_path: Ścieżka zapisu pliku JSON.

    Returns:
        Ścieżka do zapisanego pliku.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    metadata_to_save = dict(metadata)

    metadata_to_save.setdefault(
        "generated_at_utc",
        datetime.now(timezone.utc).isoformat(),
    )

    output_file.write_text(
        json.dumps(
            metadata_to_save,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return output_file