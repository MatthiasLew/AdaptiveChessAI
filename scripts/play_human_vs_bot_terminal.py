import argparse
from pathlib import Path
import sys

import chess


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot
from adaptive_chess.play.human_vs_bot_session import HumanVsBotSession


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Play a terminal chess game against a bot."
    )

    parser.add_argument(
        "--bot",
        choices=("random", "static", "adaptive"),
        default="random",
        help="Bot type.",
    )

    parser.add_argument(
        "--human-color",
        choices=("white", "black"),
        default="white",
        help="Human player color.",
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Minimax depth for static/adaptive bots.",
    )

    return parser.parse_args()


def create_bot(
    bot_type: str,
    depth: int,
) -> BaseBot:
    if depth < 1:
        raise ValueError("--depth must be at least 1.")

    if bot_type == "random":
        return RandomBot("RandomBot")

    if bot_type == "static":
        return StaticMinimaxBot(
            name=f"StaticMinimaxBot-depth-{depth}",
            depth=depth,
        )

    if bot_type == "adaptive":
        return AdaptiveMinimaxBot(
            name=f"AdaptiveMinimaxBot-depth-{depth}",
            depth=depth,
        )

    raise ValueError(f"Unsupported bot type: {bot_type}")


def parse_color(color_name: str) -> chess.Color:
    if color_name == "white":
        return chess.WHITE

    if color_name == "black":
        return chess.BLACK

    raise ValueError(f"Unsupported color: {color_name}")


def render_board(board: chess.Board) -> str:
    """
    Renderuje planszę tekstowo z koordynatami.

    To jest tylko pomocniczy widok terminalowy.
    GUI później będzie miało własny widget planszy.
    """
    lines = []
    board_text_lines = str(board).splitlines()

    for index, line in enumerate(board_text_lines):
        rank = 8 - index
        lines.append(f"{rank}  {line}")

    lines.append("")
    lines.append("   a b c d e f g h")

    return "\n".join(lines)


def print_session_state(session: HumanVsBotSession) -> None:
    print()
    print(render_board(session.get_board_copy()))
    print()
    print(f"FEN: {session.get_fen()}")
    print(f"Status: {session.get_status_message()}")

    history = session.get_move_history()

    if history:
        print()
        print("Historia ruchów:")

        for index, move in enumerate(history, start=1):
            color = "White" if move.color == chess.WHITE else "Black"
            print(
                f"{index:02d}. {color} {move.player_type.value}: "
                f"{move.san} ({move.move_uci})"
            )

    print()


def run_terminal_game(args: argparse.Namespace) -> None:
    bot = create_bot(
        bot_type=args.bot,
        depth=args.depth,
    )
    human_color = parse_color(args.human_color)

    session = HumanVsBotSession(
        bot=bot,
        human_color=human_color,
    )

    opening_bot_move = session.start()

    print("AdaptiveChessAI — terminal human vs bot")
    print(f"Bot: {session.bot_name}")
    print(f"Human color: {args.human_color}")

    if opening_bot_move is not None:
        print(f"Bot starts: {opening_bot_move.san} ({opening_bot_move.move_uci})")

    while not session.is_game_over():
        print_session_state(session)

        move_uci = input("Your move in UCI notation, or 'quit': ").strip()

        if move_uci.lower() in {"quit", "exit", "q"}:
            print("Game interrupted by user.")
            return

        try:
            result = session.play_human_move_uci(move_uci)
        except (RuntimeError, ValueError) as error:
            print(f"Error: {error}")
            continue

        print()
        print(f"Human move: {result.human_move.san} ({result.human_move.move_uci})")

        if result.bot_move is not None:
            print(f"Bot move: {result.bot_move.san} ({result.bot_move.move_uci})")

        print(f"Status: {result.status_message}")

    print_session_state(session)
    print(f"Final result: {session.get_result()}")


def main() -> None:
    args = parse_args()
    run_terminal_game(args)


if __name__ == "__main__":
    main()