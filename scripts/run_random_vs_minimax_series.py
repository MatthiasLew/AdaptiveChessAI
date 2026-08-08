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
            f"półruchy={result.half_moves}, "
            f"materiał={result.final_material_balance}, "
            f"zakończenie={result.termination_reason.value}"
        )

    print()


def main() -> None:
    """
    Uruchamia dwie serie porównawcze:

    1. RandomBot jako białe vs StaticMinimaxBot jako czarne.
    2. StaticMinimaxBot jako białe vs RandomBot jako czarne.
    """
    matches_count = 20
    max_half_moves = 100
    minimax_depth = 1

    random_white_vs_minimax_black = SeriesRunner(
        matches_count=matches_count,
        max_half_moves=max_half_moves,
    ).play_series(
        white_bot_factory=lambda: RandomBot("RandomBot-White"),
        black_bot_factory=lambda: StaticMinimaxBot(
            name="StaticMinimaxBot-Black",
            depth=minimax_depth,
        ),
    )

    minimax_white_vs_random_black = SeriesRunner(
        matches_count=matches_count,
        max_half_moves=max_half_moves,
    ).play_series(
        white_bot_factory=lambda: StaticMinimaxBot(
            name="StaticMinimaxBot-White",
            depth=minimax_depth,
        ),
        black_bot_factory=lambda: RandomBot("RandomBot-Black"),
    )

    print("Eksperyment: RandomBot vs StaticMinimaxBot")
    print(f"Liczba partii na serię: {matches_count}")
    print(f"Limit półruchów na partię: {max_half_moves}")
    print(f"Głębokość minimaxa: {minimax_depth}")
    print()

    print_series_summary(
        "RandomBot-White vs StaticMinimaxBot-Black",
        random_white_vs_minimax_black,
    )

    print_series_summary(
        "StaticMinimaxBot-White vs RandomBot-Black",
        minimax_white_vs_random_black,
    )


if __name__ == "__main__":
    main()