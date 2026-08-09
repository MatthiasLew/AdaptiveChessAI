import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SuiteCommand:
    """
    Pojedyncza komenda uruchamiana w ramach pełnego zestawu eksperymentów.
    """

    name: str
    command: list[str]


def parse_args() -> argparse.Namespace:
    """
    Parsuje argumenty przekazane z terminala.

    Returns:
        Konfiguracja pełnego zestawu eksperymentów.
    """
    parser = argparse.ArgumentParser(
        description="Run full adaptive chess experiment suite."
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/full_suite",
        help="Directory for CSV files, metadata, reports and charts.",
    )

    parser.add_argument(
        "--matches",
        type=int,
        default=5,
        help="Number of matches per experiment/color configuration.",
    )

    parser.add_argument(
        "--max-half-moves",
        type=int,
        default=80,
        help="Maximum number of half-moves per match.",
    )

    parser.add_argument(
        "--depths",
        type=int,
        nargs="+",
        default=[1],
        help="Depths to test, for example: --depths 1 2",
    )

    parser.add_argument(
        "--adjudication-material-threshold",
        type=int,
        default=3,
        help="Material threshold for adjudicating move-limit matches.",
    )

    parser.add_argument(
        "--skip-random-series",
        action="store_true",
        help="Skip RandomBot vs RandomBot baseline.",
    )

    parser.add_argument(
        "--skip-reports",
        action="store_true",
        help="Skip text report generation.",
    )

    parser.add_argument(
        "--skip-charts",
        action="store_true",
        help="Skip chart generation.",
    )

    return parser.parse_args()


def validate_suite_config(
    matches_count: int,
    max_half_moves: int,
    depths: list[int],
    adjudication_material_threshold: int,
) -> None:
    """
    Sprawdza poprawność konfiguracji pełnego zestawu eksperymentów.

    Args:
        matches_count: Liczba partii.
        max_half_moves: Limit półruchów.
        depths: Lista głębokości.
        adjudication_material_threshold: Próg materiałowy adjudykacji.

    Raises:
        ValueError: Jeśli konfiguracja jest niepoprawna.
    """
    if matches_count < 1:
        raise ValueError("--matches must be at least 1.")

    if max_half_moves < 1:
        raise ValueError("--max-half-moves must be at least 1.")

    if not depths:
        raise ValueError("--depths must contain at least one value.")

    if any(depth < 1 for depth in depths):
        raise ValueError("Every depth must be at least 1.")

    if adjudication_material_threshold < 1:
        raise ValueError("--adjudication-material-threshold must be at least 1.")


def build_experiment_commands(args: argparse.Namespace) -> list[SuiteCommand]:
    """
    Buduje listę komend uruchamiających eksperymenty.

    Args:
        args: Argumenty CLI.

    Returns:
        Lista komend eksperymentalnych.
    """
    output_dir = Path(args.output_dir)
    python_executable = sys.executable

    common_args = [
        "--matches",
        str(args.matches),
        "--max-half-moves",
        str(args.max_half_moves),
        "--adjudication-material-threshold",
        str(args.adjudication_material_threshold),
    ]

    depth_args = ["--depths", *[str(depth) for depth in args.depths]]

    commands: list[SuiteCommand] = []

    if not args.skip_random_series:
        commands.append(
            SuiteCommand(
                name="random_series",
                command=[
                    python_executable,
                    str(PROJECT_ROOT / "scripts" / "run_random_series.py"),
                    *common_args,
                    "--output-csv",
                    str(output_dir / "random_series.csv"),
                ],
            )
        )

    commands.extend(
        [
            SuiteCommand(
                name="random_vs_minimax",
                command=[
                    python_executable,
                    str(PROJECT_ROOT / "scripts" / "run_random_vs_minimax_series.py"),
                    *common_args,
                    *depth_args,
                    "--output-csv",
                    str(output_dir / "random_vs_minimax.csv"),
                ],
            ),
            SuiteCommand(
                name="random_vs_adaptive",
                command=[
                    python_executable,
                    str(PROJECT_ROOT / "scripts" / "run_random_vs_adaptive_series.py"),
                    *common_args,
                    *depth_args,
                    "--output-csv",
                    str(output_dir / "random_vs_adaptive.csv"),
                ],
            ),
            SuiteCommand(
                name="static_vs_adaptive",
                command=[
                    python_executable,
                    str(PROJECT_ROOT / "scripts" / "run_static_vs_adaptive_series.py"),
                    *common_args,
                    *depth_args,
                    "--output-csv",
                    str(output_dir / "static_vs_adaptive.csv"),
                ],
            ),
        ]
    )

    return commands


def build_analysis_commands(args: argparse.Namespace) -> list[SuiteCommand]:
    """
    Buduje listę komend generujących raporty i wykresy dla zapisanych CSV.

    Args:
        args: Argumenty CLI.

    Returns:
        Lista komend analitycznych.
    """
    output_dir = Path(args.output_dir)
    python_executable = sys.executable

    csv_names = [
        "random_vs_minimax",
        "random_vs_adaptive",
        "static_vs_adaptive",
    ]

    if not args.skip_random_series:
        csv_names.insert(0, "random_series")

    commands: list[SuiteCommand] = []

    for csv_name in csv_names:
        csv_path = output_dir / f"{csv_name}.csv"

        if not args.skip_reports:
            commands.append(
                SuiteCommand(
                    name=f"report_{csv_name}",
                    command=[
                        python_executable,
                        str(PROJECT_ROOT / "scripts" / "analyze_results_csv.py"),
                        "--input-csv",
                        str(csv_path),
                        "--output-report",
                        str(output_dir / f"{csv_name}_report.txt"),
                    ],
                )
            )

        if not args.skip_charts:
            commands.append(
                SuiteCommand(
                    name=f"charts_{csv_name}",
                    command=[
                        python_executable,
                        str(PROJECT_ROOT / "scripts" / "generate_charts.py"),
                        "--input-csv",
                        str(csv_path),
                        "--output-dir",
                        str(output_dir / "charts" / csv_name),
                    ],
                )
            )

    return commands


def run_command(command: SuiteCommand) -> None:
    """
    Uruchamia pojedynczą komendę.

    Args:
        command: Komenda do uruchomienia.

    Raises:
        subprocess.CalledProcessError: Jeśli komenda zakończy się błędem.
    """
    print()
    print(f"=== RUN: {command.name} ===")
    print(" ".join(command.command))
    print()

    subprocess.run(
        command.command,
        cwd=PROJECT_ROOT,
        check=True,
    )


def run_suite(args: argparse.Namespace) -> None:
    """
    Uruchamia pełny zestaw eksperymentów oraz opcjonalną analizę.

    Args:
        args: Argumenty CLI.
    """
    validate_suite_config(
        matches_count=args.matches,
        max_half_moves=args.max_half_moves,
        depths=args.depths,
        adjudication_material_threshold=args.adjudication_material_threshold,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    experiment_commands = build_experiment_commands(args)
    analysis_commands = build_analysis_commands(args)

    print("Pełny zestaw eksperymentów AdaptiveChessAI")
    print(f"Folder wyników: {output_dir}")
    print(f"Liczba partii: {args.matches}")
    print(f"Limit półruchów: {args.max_half_moves}")
    print(f"Głębokości: {args.depths}")
    print(f"Próg adjudykacji materiałowej: {args.adjudication_material_threshold}")
    print(f"Liczba komend eksperymentalnych: {len(experiment_commands)}")
    print(f"Liczba komend analitycznych: {len(analysis_commands)}")

    for command in experiment_commands:
        run_command(command)

    for command in analysis_commands:
        run_command(command)

    print()
    print("Zakończono pełny zestaw eksperymentów.")
    print(f"Wyniki zapisano w: {output_dir}")


def main() -> None:
    args = parse_args()
    run_suite(args)


if __name__ == "__main__":
    main()