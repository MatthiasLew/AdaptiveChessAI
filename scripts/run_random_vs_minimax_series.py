import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from adaptive_chess.analysis.statistics import summarize_matches
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot
from adaptive_chess.experiments.match_runner import MatchResult
from adaptive_chess.experiments.series_runner import SeriesRunner


def parse_args() -> argparse.Namespace:
    """
    Parsuje argumenty przekazane z terminala.

    Returns:
        Obiekt z konfiguracją eksperymentu.
    """
    parser = argparse.ArgumentParser(
        description="Run RandomBot vs StaticMinimaxBot comparison series."
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
        help="Minimax depths to test, for example: --depths 1 2",
    )

    return parser.parse_args()


def validate_experiment_config(
    matches_count: int,
    max_half_moves: int,
    depths: list[int],
) -> None:
    """
    Sprawdza poprawność konfiguracji eksperymentu.

    Args:
        matches_count: Liczba partii na konfigurację.
        max_half_moves: Limit półruchów.
        depths: Lista głębokości minimaxa.

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
        raise ValueError("Every minimax depth must be at least 1.")


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
    minimax_depth: int,
) -> None:
    """
    Uruchamia porównanie RandomBot vs StaticMinimaxBot dla jednej głębokości minimaxa.

    Args:
        matches_count: Liczba partii w każdej konfiguracji kolorów.
        max_half_moves: Limit półruchów na partię.
        minimax_depth: Głębokość minimaxa.
    """
    random_white_vs_minimax_black = SeriesRunner(
        matches_count=matches_count,
        max_half_moves=max_half_moves,
    ).play_series(
        white_bot_factory=lambda: RandomBot("RandomBot-White"),
        black_bot_factory=lambda: StaticMinimaxBot(
            name=f"StaticMinimaxBot-Black-depth-{minimax_depth}",
            depth=minimax_depth,
        ),
    )

    minimax_white_vs_random_black = SeriesRunner(
        matches_count=matches_count,
        max_half_moves=max_half_moves,
    ).play_series(
        white_bot_factory=lambda: StaticMinimaxBot(
            name=f"StaticMinimaxBot-White-depth-{minimax_depth}",
            depth=minimax_depth,
        ),
        black_bot_factory=lambda: RandomBot("RandomBot-Black"),
    )

    print(f"######## Depth={minimax_depth} ########")
    print()

    print_series_summary(
        f"RandomBot-White vs StaticMinimaxBot-Black-depth-{minimax_depth}",
        random_white_vs_minimax_black,
    )

    print_series_summary(
        f"StaticMinimaxBot-White-depth-{minimax_depth} vs RandomBot-Black",
        minimax_white_vs_random_black,
    )


def main() -> None:
    """
    Uruchamia eksperyment porównawczy dla jednej lub wielu głębokości minimaxa.
    """
    args = parse_args()

    validate_experiment_config(
        matches_count=args.matches,
        max_half_moves=args.max_half_moves,
        depths=args.depths,
    )

    print("Eksperyment: RandomBot vs StaticMinimaxBot")
    print(f"Liczba partii na konfigurację kolorów: {args.matches}")
    print(f"Limit półruchów na partię: {args.max_half_moves}")
    print(f"Testowane głębokości minimaxa: {args.depths}")
    print()

    for depth in args.depths:
        run_comparison_for_depth(
            matches_count=args.matches,
            max_half_moves=args.max_half_moves,
            minimax_depth=depth,
        )


if __name__ == "__main__":
    main()