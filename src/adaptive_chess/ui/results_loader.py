from dataclasses import dataclass
from pathlib import Path

from adaptive_chess.ui.experiment_config import resolve_output_dir

SUPPORTED_RESULT_EXTENSIONS = {
    ".csv": "CSV",
    ".json": "JSON",
    ".md": "Markdown",
    ".txt": "Text",
    ".png": "Image",
}


TEXT_PREVIEW_EXTENSIONS = {
    ".md",
    ".txt",
    ".csv",
    ".json",
}


@dataclass(frozen=True)
class ResultFileInfo:
    """
    Informacja o pojedynczym pliku wynikowym.
    """

    name: str
    path: Path
    category: str
    size_bytes: int


@dataclass(frozen=True)
class ResultsFolderSummary:
    """
    Podsumowanie zawartości folderu wyników.
    """

    folder: Path
    exists: bool
    files: tuple[ResultFileInfo, ...]
    preferred_preview_file: ResultFileInfo | None


def summarize_results_folder(
    folder: str | Path,
    project_root: Path | None = None,
) -> ResultsFolderSummary:
    """
    Wczytuje podstawowe informacje o folderze wyników.
    """
    resolved_folder = resolve_output_dir(
        output_dir=folder,
        project_root=project_root,
    )

    if not resolved_folder.exists():
        return ResultsFolderSummary(
            folder=resolved_folder,
            exists=False,
            files=(),
            preferred_preview_file=None,
        )

    if not resolved_folder.is_dir():
        raise ValueError(f"Results path is not a directory: {resolved_folder}")

    files = discover_result_files(resolved_folder)
    preferred_preview_file = find_preferred_preview_file(files)

    return ResultsFolderSummary(
        folder=resolved_folder,
        exists=True,
        files=files,
        preferred_preview_file=preferred_preview_file,
    )


def discover_result_files(folder: Path) -> tuple[ResultFileInfo, ...]:
    """
    Znajduje obsługiwane pliki wyników w folderze i podfolderach.
    """
    result_files: list[ResultFileInfo] = []

    for path in folder.rglob("*"):
        if not path.is_file():
            continue

        extension = path.suffix.lower()

        if extension not in SUPPORTED_RESULT_EXTENSIONS:
            continue

        result_files.append(
            ResultFileInfo(
                name=path.name,
                path=path,
                category=SUPPORTED_RESULT_EXTENSIONS[extension],
                size_bytes=path.stat().st_size,
            )
        )

    return tuple(
        sorted(
            result_files,
            key=lambda file_info: (
                file_info.category,
                str(file_info.path).lower(),
            ),
        )
    )


def find_preferred_preview_file(
    files: tuple[ResultFileInfo, ...],
) -> ResultFileInfo | None:
    """
    Wybiera najlepszy plik do automatycznego podglądu.

    Priorytet:
    1. suite_summary.md,
    2. pliki .md,
    3. pliki .txt,
    4. pliki .csv,
    5. pliki .json.
    """
    if not files:
        return None

    for file_info in files:
        if file_info.name == "suite_summary.md":
            return file_info

    for extension in (".md", ".txt", ".csv", ".json"):
        for file_info in files:
            if file_info.path.suffix.lower() == extension:
                return file_info

    return None


def read_text_preview(
    path: str | Path,
    max_characters: int = 12_000,
) -> str:
    """
    Czyta tekstowy podgląd pliku wynikowego.
    """
    file_path = Path(path)

    if file_path.suffix.lower() not in TEXT_PREVIEW_EXTENSIONS:
        return "Podgląd tego typu pliku nie jest dostępny. Otwórz plik zewnętrznie."

    text = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    if len(text) <= max_characters:
        return text

    return text[:max_characters] + "\n\n...[podgląd skrócony]"


def format_file_size(size_bytes: int) -> str:
    """
    Formatuje rozmiar pliku do czytelnej postaci.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"

    size_kb = size_bytes / 1024

    if size_kb < 1024:
        return f"{size_kb:.1f} KB"

    size_mb = size_kb / 1024
    return f"{size_mb:.1f} MB"
