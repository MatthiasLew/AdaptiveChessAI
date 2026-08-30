import chess
import pytest

from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot
from adaptive_chess.ui.bot_factory import (
    BotKind,
    create_bot_for_gui,
    parse_human_color,
)


def test_create_bot_for_gui_creates_random_bot():
    bot = create_bot_for_gui(
        bot_kind=BotKind.RANDOM,
        depth=1,
    )

    assert isinstance(bot, RandomBot)
    assert bot.name == "RandomBot"


def test_create_bot_for_gui_creates_static_minimax_bot():
    bot = create_bot_for_gui(
        bot_kind=BotKind.STATIC_MINIMAX,
        depth=2,
    )

    assert isinstance(bot, StaticMinimaxBot)
    assert bot.depth == 2


def test_create_bot_for_gui_creates_adaptive_minimax_bot():
    bot = create_bot_for_gui(
        bot_kind=BotKind.ADAPTIVE_MINIMAX,
        depth=2,
    )

    assert isinstance(bot, AdaptiveMinimaxBot)
    assert bot.depth == 2


def test_create_bot_for_gui_rejects_invalid_depth():
    with pytest.raises(ValueError):
        create_bot_for_gui(
            bot_kind=BotKind.RANDOM,
            depth=0,
        )


def test_create_bot_for_gui_rejects_unknown_bot_kind():
    with pytest.raises(ValueError):
        create_bot_for_gui(
            bot_kind="unknown",
            depth=1,
        )


def test_parse_human_color_accepts_white():
    assert parse_human_color("white") == chess.WHITE


def test_parse_human_color_accepts_black():
    assert parse_human_color("black") == chess.BLACK


def test_parse_human_color_rejects_unknown_color():
    with pytest.raises(ValueError):
        parse_human_color("red")