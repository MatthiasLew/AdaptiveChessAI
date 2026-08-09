import chess
import pytest

from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot
from scripts.play_human_vs_bot_terminal import (
    create_bot,
    parse_color,
    render_board,
)


def test_create_bot_creates_random_bot():
    bot = create_bot(
        bot_type="random",
        depth=1,
    )

    assert isinstance(bot, RandomBot)


def test_create_bot_creates_static_minimax_bot():
    bot = create_bot(
        bot_type="static",
        depth=1,
    )

    assert isinstance(bot, StaticMinimaxBot)
    assert bot.depth == 1


def test_create_bot_creates_adaptive_minimax_bot():
    bot = create_bot(
        bot_type="adaptive",
        depth=1,
    )

    assert isinstance(bot, AdaptiveMinimaxBot)
    assert bot.depth == 1


def test_create_bot_rejects_invalid_depth():
    with pytest.raises(ValueError):
        create_bot(
            bot_type="static",
            depth=0,
        )


def test_create_bot_rejects_unknown_bot_type():
    with pytest.raises(ValueError):
        create_bot(
            bot_type="unknown",
            depth=1,
        )


def test_parse_color_accepts_white():
    assert parse_color("white") == chess.WHITE


def test_parse_color_accepts_black():
    assert parse_color("black") == chess.BLACK


def test_parse_color_rejects_unknown_color():
    with pytest.raises(ValueError):
        parse_color("red")


def test_render_board_contains_coordinates():
    board = chess.Board()

    rendered = render_board(board)

    assert "8" in rendered
    assert "1" in rendered
    assert "a b c d e f g h" in rendered