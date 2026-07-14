from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.experiments.match_runner import MatchRunner


def main() -> None:
    """
    Uruchamia przykładową partię RandomBot vs RandomBot
    i wypisuje podstawowe informacje o wyniku.
    """
    white_bot = RandomBot("RandomBot-White")
    black_bot = RandomBot("RandomBot-Black")

    runner = MatchRunner(max_half_moves=100)
    result = runner.play(white_bot, black_bot)

    print("=== RandomBot vs RandomBot ===")
    print(f"Białe: {result.white_bot_name}")
    print(f"Czarne: {result.black_bot_name}")
    print(f"Wynik: {result.result}")
    print(f"Liczba półruchów: {result.half_moves}")
    print(f"Osiągnięto limit ruchów: {result.reached_move_limit}")
    print(f"Ruchy UCI: {' '.join(result.moves_uci)}")
    print(f"Końcowy FEN: {result.final_fen}")


if __name__ == "__main__":
    main()
