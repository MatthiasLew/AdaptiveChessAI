from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from adaptive_chess.analysis.statistics import summarize_matches
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.experiments.series_runner import SeriesRunner


def main() -> None:
    """
    Uruchamia serię partii RandomBot vs RandomBot
    i wypisuje podstawowe statystyki.
    """
    matches_count = 20
    max_half_moves = 100

    runner = SeriesRunner(
        matches_count=matches_count,
        max_half_moves=max_half_moves,
    )

    results = runner.play_series(
        white_bot_factory=lambda: RandomBot("RandomBot-White"),
        black_bot_factory=lambda: RandomBot("RandomBot-Black"),
    )

    summary = summarize_matches(results)

    print("=== RandomBot vs RandomBot — seria partii ===")
    print(f"Liczba partii: {summary.total_matches}")
    print(f"Limit półruchów na partię: {max_half_moves}")
    print()
    print("Wyniki:")
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
            f"limit={result.reached_move_limit}"
        )


if __name__ == "__main__":
    main()