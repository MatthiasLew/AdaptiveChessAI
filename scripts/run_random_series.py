import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from adaptive_chess.analysis.statistics import summarize_matches
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.data.csv_exporter import export_match_results_to_csv
from adaptive_chess.evaluation.position import POSITION_EVALUATION_VERSION
from adaptive_chess.experiments.metadata import (
    resolve_metadata_output_path,
    write_experiment_metadata,
)
from adaptive_chess.experiments.series_runner import SeriesRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a RandomBot vs RandomBot match series."
    )

    parser.add_argument(
        "--matches",
        type=int,
        default=20,
        help="Number of matches to run.",
    )

    parser.add_argument(
        "--max-half-moves",
        type=int,
        default=100,
        help="Maximum number of half-moves per match.",
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
    adjudication_material_threshold: int,
) -> None:
    if matches_count < 1:
        raise ValueError("--matches must be at least 1.")

    if max_half_moves < 1:
        raise ValueError("--max-half-moves must be at least 1.")

    if adjudication_material_threshold < 1:
        raise ValueError("--adjudication-material-threshold must be at least 1.")


def build_experiment_metadata(args: argparse.Namespace) -> dict[str, object]:
    return {
        "experiment_type": "random_vs_random",
        "matches_count": args.matches,
        "max_half_moves": args.max_half_moves,
        "adjudication_material_threshold": args.adjudication_material_threshold,
        "position_evaluation_version": POSITION_EVALUATION_VERSION,
        "series": [
            {
                "experiment_name": "RandomBot-White vs RandomBot-Black",
                "white_bot": "RandomBot",
                "black_bot": "RandomBot",
            }
        ],
        "output_csv": args.output_csv,
    }


def maybe_write_metadata(args: argparse.Namespace) -> None:
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
    Uruchamia serię partii RandomBot vs RandomBot
    i wypisuje podstawowe statystyki.
    """
    args = parse_args()

    validate_experiment_config(
        matches_count=args.matches,
        max_half_moves=args.max_half_moves,
        adjudication_material_threshold=args.adjudication_material_threshold,
    )

    runner = SeriesRunner(
        matches_count=args.matches,
        max_half_moves=args.max_half_moves,
        adjudication_material_threshold=args.adjudication_material_threshold,
    )

    results = runner.play_series(
        white_bot_factory=lambda: RandomBot("RandomBot-White"),
        black_bot_factory=lambda: RandomBot("RandomBot-Black"),
    )

    summary = summarize_matches(results)

    print("=== RandomBot vs RandomBot — seria partii ===")
    print(f"Liczba partii: {summary.total_matches}")
    print(f"Limit półruchów na partię: {args.max_half_moves}")
    print(f"Próg adjudykacji materiałowej: {args.adjudication_material_threshold}")
    print(f"Wersja oceny pozycji: {POSITION_EVALUATION_VERSION}")
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
            f"limit={result.reached_move_limit}, "
            f"zakończenie={result.termination_reason.value}"
        )

    if args.output_csv is not None:
        saved_path = export_match_results_to_csv(
            matches=results,
            output_path=args.output_csv,
            experiment_name="RandomBot-White vs RandomBot-Black",
        )
        print()
        print(f"Zapisano CSV: {saved_path}")

    maybe_write_metadata(args)


if __name__ == "__main__":
    main()