import pytest
import chess

from src.adaptive_chess.bots.random_bot import RandomBot


def test_random_bot_has_default_name():
    bot = RandomBot()

    assert bot.name == "RandomBot"


def test_random_bot_returns_legal_move():
    board = chess.Board()
    bot = RandomBot()

    move = bot.choose_move(board)

    assert move in board.legal_moves


def test_random_bot_does_not_modify_board():
    board = chess.Board()
    original_fen = board.fen()
    bot = RandomBot()

    bot.choose_move(board)

    assert board.fen() == original_fen


def test_random_bot_raises_error_when_no_legal_moves():
    board = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")
    bot = RandomBot()

    assert len(list(board.legal_moves)) == 0

    with pytest.raises(ValueError):
        bot.choose_move(board)