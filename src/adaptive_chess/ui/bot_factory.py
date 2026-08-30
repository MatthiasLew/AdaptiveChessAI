from enum import Enum

import chess

from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot


class BotKind(str, Enum):
    """
    Typy botów dostępne w GUI.
    """

    RANDOM = "random"
    STATIC_MINIMAX = "static_minimax"
    ADAPTIVE_MINIMAX = "adaptive_minimax"


def create_bot_for_gui(
    bot_kind: BotKind | str,
    depth: int,
) -> BaseBot:
    """
    Tworzy bota na podstawie konfiguracji wybranej w GUI.

    Args:
        bot_kind: Typ bota.
        depth: Głębokość minimaxa dla botów minimaxowych.

    Returns:
        Instancja bota.

    Raises:
        ValueError: Jeśli typ bota albo depth są niepoprawne.
    """
    if depth < 1:
        raise ValueError("depth must be at least 1.")

    parsed_bot_kind = BotKind(bot_kind)

    if parsed_bot_kind == BotKind.RANDOM:
        return RandomBot("RandomBot")

    if parsed_bot_kind == BotKind.STATIC_MINIMAX:
        return StaticMinimaxBot(
            name=f"StaticMinimaxBot-depth-{depth}",
            depth=depth,
        )

    if parsed_bot_kind == BotKind.ADAPTIVE_MINIMAX:
        return AdaptiveMinimaxBot(
            name=f"AdaptiveMinimaxBot-depth-{depth}",
            depth=depth,
        )

    raise ValueError(f"Unsupported bot kind: {bot_kind}")


def parse_human_color(color_name: str) -> chess.Color:
    """
    Zamienia tekstową nazwę koloru z GUI na kolor python-chess.
    """
    if color_name == "white":
        return chess.WHITE

    if color_name == "black":
        return chess.BLACK

    raise ValueError(f"Unsupported human color: {color_name}")
