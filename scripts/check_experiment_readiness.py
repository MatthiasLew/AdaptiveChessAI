import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_DIRS = (
    "docs",
    "scripts",
    "src/adaptive_chess",
    "src/adaptive_chess/adaptation",
    "src/adaptive_chess/analysis",
    "src/adaptive_chess/bots",
    "src/adaptive_chess/core",
    "src/adaptive_chess/data",
    "src/adaptive_chess/evaluation",
    "src/adaptive_chess/experiments",
    "src/adaptive_chess/search",
    "tests",
    "tests/unit",
)


REQUIRED_FILES = (
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "docs/experiments.md",
    "docs/mvp_status.md",
    "scripts/analyze_results_csv.py",
    "scripts/check_experiment_readiness.py",
    "scripts/generate_charts.py",
    "scripts/run_full_experiment_suite.py",
    "scripts/run_random_series.py",
    "scripts/run_random_vs_adaptive_series.py",
    "scripts/run_random_vs_minimax_series.py",
    "scripts/run_static_vs_adaptive_series.py",
    "src/adaptive_chess/adaptation/adaptive_scoring.py",
    "src/adaptive_chess/adaptation/opponent_profile.py",
    "src/adaptive_chess/analysis/charts.py",
    "src/adaptive_chess/analysis/csv_report.py",
    "src/adaptive_chess/analysis/statistics.py",
    "src/adaptive_chess/bots/adaptive_minimax_bot.py",
    "src/adaptive_chess/bots/base_bot.py",
    "src/adaptive_chess/bots/random_bot.py",
    "src/adaptive_chess/bots/static_minimax_bot.py",
    "src/adaptive_chess/core/game.py",
    "src/adaptive_chess/data/csv_exporter.py",
    "src/adaptive_chess/evaluation/material.py",
    "src/adaptive_chess/evaluation/position.py",
    "src/adaptive_chess/experiments/adjudication.py",
    "src/adaptive_chess/experiments/match_runner.py",
    "src/adaptive_chess/experiments/metadata.py",
    "src/adaptive_chess/experiments/series_runner.py",
    "src/adaptive_chess/search/minimax.py",
)


@dataclass(frozen=True)
class ReadinessCheck:
    """
    Wynik pojedynczego sprawdzenia gotowości projektu.
    """

    kind: str
    relative_path: str
    exists: bool

    @property
    def status(self) -> str:
        """
        Zwraca tekstowy status sprawdzenia.
        """
        return "OK" if self.exists else "MISSING"


def parse_args() -> argparse.Namespace:
    """
    Parsuje argumenty przekazane z terminala.

    Returns:
        Konfiguracja sprawdzania gotowości.
    """
    parser = argparse.ArgumentParser(
        description="Check AdaptiveChessAI experiment readiness."
    )

    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run full pytest suite after checking required files.",
    )

    parser.add_argument(
        "--run-smoke-suite",
        action="store_true",
        help="Run a small full experiment suite smoke test.",
    )

    parser.add_argument(
        "--smoke-output-dir",
        type=str,
        default="results/readiness_smoke",
        help="Output directory for smoke experiment results.",
    )

    parser.add_argument(
        "--smoke-with-charts",
        action="store_true",
        help="Generate charts during smoke suite. By default charts are skipped.",
    )

    return parser.parse_args()


def collect_readiness_checks(project_root: Path) -> tuple[ReadinessCheck, ...]:
    """
    Zbiera wyniki sprawdzeń wymaganych katalogów i plików.

    Args:
        project_root: Główny katalog projektu.

    Returns:
        Lista wyników sprawdzeń.
    """
    checks: list[ReadinessCheck] = []

    for relative_dir in REQUIRED_DIRS:
        checks.append(
            ReadinessCheck(
                kind="dir",
                relative_path=relative_dir,
                exists=(project_root / relative_dir).is_dir(),
            )
        )

    for relative_file in REQUIRED_FILES:
        checks.append(
            ReadinessCheck(
                kind="file",
                relative_path=relative_file,
                exists=(project_root / relative_file).is_file(),
            )
        )

    return tuple(checks)


def has_failures(checks: tuple[ReadinessCheck, ...]) -> bool:
    """
    Sprawdza, czy lista wyników zawiera braki.

    Args:
        checks: Wyniki sprawdzeń.

    Returns:
        True, jeśli istnieje brakujący plik albo katalog.
    """
    return any(not check.exists for check in checks)


def print_readiness_report(checks: tuple[ReadinessCheck, ...]) -> None:
    """
    Wypisuje raport gotowości projektu.

    Args:
        checks: Wyniki sprawdzeń.
    """
    print("=== AdaptiveChessAI readiness check ===")
    print()

    for check in checks:
        print(f"[{check.status}] {check.kind}: {check.relative_path}")

    print()

    if has_failures(checks):
        print("Status: FAILED")
        print("Projekt ma brakujące pliki albo katalogi.")
        return

    print("Status: OK")
    print("Wymagane pliki i katalogi są obecne.")


def build_test_command() -> list[str]:
    """
    Buduje komendę uruchamiającą testy.

    Returns:
        Komenda dla subprocess.
    """
    return [
        sys.executable,
        "-m",
        "pytest",
    ]


def build_smoke_suite_command(
    project_root: Path,
    output_dir: str,
    include_charts: bool,
) -> list[str]:
    """
    Buduje komendę uruchamiającą mały pełny zestaw eksperymentów.

    Args:
        project_root: Główny katalog projektu.
        output_dir: Folder wyników smoke testu.
        include_charts: Czy generować wykresy.

    Returns:
        Komenda dla subprocess.
    """
    command = [
        sys.executable,
        str(project_root / "scripts" / "run_full_experiment_suite.py"),
        "--output-dir",
        output_dir,
        "--matches",
        "1",
        "--max-half-moves",
        "10",
        "--depths",
        "1",
    ]

    if not include_charts:
        command.append("--skip-charts")

    return command


def run_command(
    name: str,
    command: list[str],
    project_root: Path,
) -> None:
    """
    Uruchamia komendę pomocniczą.

    Args:
        name: Nazwa kroku.
        command: Komenda do uruchomienia.
        project_root: Główny katalog projektu.

    Raises:
        subprocess.CalledProcessError: Jeśli komenda zakończy się błędem.
    """
    print()
    print(f"=== RUN: {name} ===")
    print(" ".join(command))
    print()

    subprocess.run(
        command,
        cwd=project_root,
        check=True,
    )


def main() -> None:
    """
    Uruchamia sprawdzenie gotowości projektu.
    """
    args = parse_args()

    checks = collect_readiness_checks(PROJECT_ROOT)
    print_readiness_report(checks)

    if has_failures(checks):
        raise SystemExit(1)

    if args.run_tests:
        run_command(
            name="pytest",
            command=build_test_command(),
            project_root=PROJECT_ROOT,
        )

    if args.run_smoke_suite:
        run_command(
            name="experiment_smoke_suite",
            command=build_smoke_suite_command(
                project_root=PROJECT_ROOT,
                output_dir=args.smoke_output_dir,
                include_charts=args.smoke_with_charts,
            ),
            project_root=PROJECT_ROOT,
        )

    print()
    print("Readiness check completed successfully.")


if __name__ == "__main__":
    main()