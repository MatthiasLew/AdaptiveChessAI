from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ExperimentKind(str, Enum):
    """
    Typy eksperymentów dostępne z poziomu GUI.
    """

    FULL_SUITE = "full_suite"
    RANDOM_VS_MINIMAX = "random_vs_minimax"
    RANDOM_VS_ADAPTIVE = "random_vs_adaptive"
    STATIC_VS_ADAPTIVE = "static_vs_adaptive"


@dataclass(frozen=True)
class ExperimentRunConfig:
    """
    Konfiguracja pojedynczego uruchomienia eksperymentu z GUI.
    """

    matches: int
    max_half_moves: int
    depth: int
    output_dir: str


def get_project_root() -> Path:
    """
    Zwraca katalog główny projektu.
    """
    return Path(__file__).resolve().parents[3]


def validate_experiment_run_config(config: ExperimentRunConfig) -> None:
    """
    Waliduje konfigurację eksperymentu.
    """
    if config.matches < 1:
        raise ValueError("matches must be at least 1.")

    if config.max_half_moves < 1:
        raise ValueError("max_half_moves must be at least 1.")

    if config.depth < 1:
        raise ValueError("depth must be at least 1.")

    if not config.output_dir.strip():
        raise ValueError("output_dir cannot be empty.")


def resolve_output_dir(
    output_dir: str | Path,
    project_root: Path | None = None,
) -> Path:
    """
    Zamienia folder wyników na ścieżkę absolutną.
    """
    root = project_root or get_project_root()
    path = Path(output_dir)

    if path.is_absolute():
        return path

    return root / path


def build_experiment_command(
    experiment_kind: ExperimentKind | str,
    config: ExperimentRunConfig,
    project_root: Path | None = None,
) -> list[str]:
    """
    Buduje argumenty procesu dla wybranego eksperymentu.

    Zwraca listę argumentów dla Pythona, gdzie pierwszy element to ścieżka
    do skryptu, a kolejne elementy to argumenty CLI.
    """
    validate_experiment_run_config(config)

    root = project_root or get_project_root()
    kind = ExperimentKind(experiment_kind)

    if kind == ExperimentKind.FULL_SUITE:
        return [
            str(root / "scripts" / "run_full_experiment_suite.py"),
            "--output-dir",
            config.output_dir,
            "--matches",
            str(config.matches),
            "--max-half-moves",
            str(config.max_half_moves),
            "--depths",
            str(config.depth),
        ]

    if kind == ExperimentKind.RANDOM_VS_MINIMAX:
        return _build_series_command(
            script_path=root / "scripts" / "run_random_vs_minimax_series.py",
            output_csv_name="random_vs_minimax_gui.csv",
            config=config,
        )

    if kind == ExperimentKind.RANDOM_VS_ADAPTIVE:
        return _build_series_command(
            script_path=root / "scripts" / "run_random_vs_adaptive_series.py",
            output_csv_name="random_vs_adaptive_gui.csv",
            config=config,
        )

    if kind == ExperimentKind.STATIC_VS_ADAPTIVE:
        return _build_series_command(
            script_path=root / "scripts" / "run_static_vs_adaptive_series.py",
            output_csv_name="static_vs_adaptive_gui.csv",
            config=config,
        )

    raise ValueError(f"Unsupported experiment kind: {experiment_kind}")


def _build_series_command(
    script_path: Path,
    output_csv_name: str,
    config: ExperimentRunConfig,
) -> list[str]:
    output_csv = Path(config.output_dir) / output_csv_name

    return [
        str(script_path),
        "--matches",
        str(config.matches),
        "--max-half-moves",
        str(config.max_half_moves),
        "--depths",
        str(config.depth),
        "--output-csv",
        str(output_csv),
    ]