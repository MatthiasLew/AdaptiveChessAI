import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from adaptive_chess.analysis.statistics import summarize_matches
from adaptive_chess.bots.adaptive_minimax_bot import (
    ADAPTIVE_BOT_VERSION,
    AdaptiveMinimaxBot,
)
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.data.csv_exporter import export_match_series_collection_to_csv
from adaptive_chess.evaluation.position import POSITION_EVALUATION_VERSION
from adaptive_chess.experiments.match_runner import MatchResult
from adaptive_chess.experiments.metadata import (
    resolve_metadata_output_path,
    write_experiment_metadata,
)
from adaptive_chess.experiments.series_runner import SeriesRunner


def parse_args() -> argparse.Namespace:
    """
    Parsuje argumenty przekazane z terminala.

    Returns:
        Obiekt z konfiguracją eksperymentu.
    """
    parser = argparse.ArgumentParser(
        description="Run RandomBot vs AdaptiveMinimaxBot comparison series."
    )

    parser.add_argument(
        "--matches",
        type=int,
        default=20,
        help="Number of matches per color configuration.",
    )

    parser.add_argument(
        "--max-half-moves",
        type=int,
        default=100,
        help="Maximum number of half-moves per match.",
    )

    parser.add_argument(
        "--depths",
        type=int,
        nargs="+",
        default=[1],
        help="Adaptive minimax depths to test, for example: --depths 1 2",
    )

    parser.add_argument(
        "--adjudication-material-threshold",
        type=int,
        default=3,
        help="Material threshold for adjudicating move-limit matches.",
    )

    parser.add_argument(
        "--output-csv",
        type=str,
        default=None,
        help="Optional path for exporting match results to CSV.",
    )

    parser.add_argument(
        "--output-metadata",
        type=str,
        default=None,
        help="Optional path for exporting experiment metadata to JSON.",
    )

    return parser.parse_args()


def validate_experiment_config(
        matches_count: int,
        max_half_moves: int,
        depths: list[int],
        adjudication_material_threshold: int = 3,
) -> None:
    """
    Sprawdza poprawność konfiguracji eksperymentu.

    Args:
        matches_count: Liczba partii na konfigurację.
        max_half_moves: Limit półruchów.
        depths: Lista głębokości minimaxa.
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
        raise ValueError("Every adaptive minimax depth must be at least 1.")

    if adjudication_material_threshold < 1:
        raise ValueError("--adjudication-material-threshold must be at least 1.")


def print_series_summary(title: str, results: tuple[MatchResult, ...]) -> None:
    """
    Wypisuje podsumowanie serii partii.

    Args:
        title: Tytuł eksperymentu.
        results: Wyniki partii z SeriesRunner.
    """
    summary = summarize_matches(results)

    print(f"=== {title} ===")
    print(f"Liczba partii: {summary.total_matches}")
    print()

    print("Wyniki formalne:")
    print(f"Wygrane białych: {summary.white_wins}")
    print(f"Wygrane czarnych: {summary.black_wins}")
    print(f"Remisy: {summary.draws}")
    print()

    print("Wyniki techniczne:")
    print(f"Wygrane białych: {summary.adjudicated_white_wins}")
    print(f"Wygrane czarnych: {summary.adjudicated_black_wins}")
    print(f"Remisy: {summary.adjudicated_draws}")
    print()

    print("Statystyki:")
    print(f"Średnia liczba półruchów: {summary.average_half_moves:.2f}")
    print(
        "Średnia końcowa przewaga materialna białych: "
        f"{summary.average_final_material_balance:.2f}"
    )
    print(f"Partie zakończone limitem: {summary.move_limit_reached_count}")
    print()

    print("Szczegóły partii:")
    for index, result in enumerate(results, start=1):
        print(
            f"{index:02d}. wynik={result.result}, "
            f"wynik_tech={result.adjudicated_result}, "
            f"półruchy={result.half_moves}, "
            f"materiał={result.final_material_balance}, "
            f"zakończenie={result.termination_reason.value}"
        )

    print()


def run_comparison_for_depth(
        matches_count: int,
        max_half_moves: int,
        adaptive_depth: int,
        adjudication_material_threshold: int,
) -> list[tuple[str, tuple[MatchResult, ...]]]:
    """
    Uruchamia porównanie RandomBot vs AdaptiveMinimaxBot dla jednej głębokości.

    Args:
        matches_count: Liczba partii w każdej konfiguracji kolorów.
        max_half_moves: Limit półruchów na partię.
        adaptive_depth: Głębokość minimaxa używana przez bota adaptacyjnego.
        adjudication_material_threshold: Próg materiałowy adjudykacji.

    Returns:
        Lista serii wyników gotowa do opcjonalnego eksportu CSV.
    """
    random_vs_adaptive_name = (
        f"RandomBot-White vs AdaptiveMinimaxBot-Black-depth-{adaptive_depth}"
    )
    adaptive_vs_random_name = (
        f"AdaptiveMinimaxBot-White-depth-{adaptive_depth} vs RandomBot-Black"
    )

    random_white_vs_adaptive_black = SeriesRunner(
        matches_count=matches_count,
        max_half_moves=max_half_moves,
        adjudication_material_threshold=adjudication_material_threshold,
    ).play_series(
        white_bot_factory=lambda: RandomBot("RandomBot-White"),
        black_bot_factory=lambda: AdaptiveMinimaxBot(
            name=f"AdaptiveMinimaxBot-Black-depth-{adaptive_depth}",
            depth=adaptive_depth,
        ),
    )

    adaptive_white_vs_random_black = SeriesRunner(
        matches_count=matches_count,
        max_half_moves=max_half_moves,
        adjudication_material_threshold=adjudication_material_threshold,
    ).play_series(
        white_bot_factory=lambda: AdaptiveMinimaxBot(
            name=f"AdaptiveMinimaxBot-White-depth-{adaptive_depth}",
            depth=adaptive_depth,
        ),
        black_bot_factory=lambda: RandomBot("RandomBot-Black"),
    )

    print(f"######## Depth={adaptive_depth} ########")
    print()

    print_series_summary(
        random_vs_adaptive_name,
        random_white_vs_adaptive_black,
    )

    print_series_summary(
        adaptive_vs_random_name,
        adaptive_white_vs_random_black,
    )

    return [
        (random_vs_adaptive_name, random_white_vs_adaptive_black),
        (adaptive_vs_random_name, adaptive_white_vs_random_black),
    ]


def build_experiment_metadata(args: argparse.Namespace) -> dict[str, object]:
    """
    Buduje słownik metadanych opisujących konfigurację eksperymentu.
    """
    series = []

    for depth in args.depths:
        series.append(
            {
                "experiment_name": (
                    f"RandomBot-White vs AdaptiveMinimaxBot-Black-depth-{depth}"
                ),
                "white_bot": "RandomBot",
                "black_bot": "AdaptiveMinimaxBot",
                "adaptive_minimax_depth": depth,
            }
        )
        series.append(
            {
                "experiment_name": (
                    f"AdaptiveMinimaxBot-White-depth-{depth} vs RandomBot-Black"
                ),
                "white_bot": "AdaptiveMinimaxBot",
                "black_bot": "RandomBot",
                "adaptive_minimax_depth": depth,
            }
        )

    return {
        "experiment_type": "random_vs_adaptive_minimax",
        "matches_count_per_color_configuration": args.matches,
        "max_half_moves": args.max_half_moves,
        "adaptive_minimax_depths": args.depths,
        "adjudication_material_threshold": args.adjudication_material_threshold,
        "position_evaluation_version": POSITION_EVALUATION_VERSION,
        "adaptive_bot_version": ADAPTIVE_BOT_VERSION,
        "series": series,
        "output_csv": args.output_csv,
    }


def maybe_write_metadata(args: argparse.Namespace) -> None:
    """
    Zapisuje metadane, jeśli użytkownik podał output CSV albo output metadata.
    """
    if args.output_csv is None and args.output_metadata is None:
        return

    metadata_path = resolve_metadata_output_path(
        output_csv_path=args.output_csv,
        output_metadata_path=args.output_metadata,
    )

    saved_path = write_experiment_metadata(
        metadata=build_experiment_metadata(args),
        output_path=metadata_path,
    )

    print(f"Zapisano metadane: {saved_path}")


def main() -> None:
    """
    Uruchamia eksperyment porównawczy dla jednej lub wielu głębokości bota adaptacyjnego.
    """
    args = parse_args()

    validate_experiment_config(
        matches_count=args.matches,
        max_half_moves=args.max_half_moves,
        depths=args.depths,
        adjudication_material_threshold=args.adjudication_material_threshold,
    )

    print("Eksperyment: RandomBot vs AdaptiveMinimaxBot")
    print(f"Liczba partii na konfigurację kolorów: {args.matches}")
    print(f"Limit półruchów na partię: {args.max_half_moves}")
    print(f"Testowane głębokości bota adaptacyjnego: {args.depths}")
    print(f"Próg adjudykacji materiałowej: {args.adjudication_material_threshold}")
    print(f"Wersja oceny pozycji: {POSITION_EVALUATION_VERSION}")
    print(f"Wersja adaptacji: {ADAPTIVE_BOT_VERSION}")
    print()

    all_series: list[tuple[str, tuple[MatchResult, ...]]] = []

    for depth in args.depths:
        depth_series = run_comparison_for_depth(
            matches_count=args.matches,
            max_half_moves=args.max_half_moves,
            adaptive_depth=depth,
            adjudication_material_threshold=args.adjudication_material_threshold,
        )
        all_series.extend(depth_series)

    if args.output_csv is not None:
        saved_path = export_match_series_collection_to_csv(
            series_collection=all_series,
            output_path=args.output_csv,
        )
        print(f"Zapisano CSV: {saved_path}")

    maybe_write_metadata(args)


if __name__ == "__main__":
    main()
