import pytest
import chess

from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot


def test_static_minimax_bot_has_default_name_and_depth():
    bot = StaticMinimaxBot()

    assert bot.name == "StaticMinimaxBot"
    assert bot.depth == 1


def test_static_minimax_bot_rejects_invalid_depth():
    with pytest.raises(ValueError):
        StaticMinimaxBot(depth=0)


def test_static_minimax_bot_returns_legal_move():
    board = chess.Board()
    bot = StaticMinimaxBot(depth=1)

    move = bot.choose_move(board)

    assert move in board.legal_moves


def test_static_minimax_bot_does_not_modify_board():
    board = chess.Board()
    original_fen = board.fen()

    bot = StaticMinimaxBot(depth=1)

    bot.choose_move(board)

    assert board.fen() == original_fen


def test_static_minimax_bot_can_capture_free_queen():
    board = chess.Board("4k3/8/8/8/8/8/4q3/4K3 w - - 0 1")
    bot = StaticMinimaxBot(depth=1)

    move = bot.choose_move(board)

    assert move == chess.Move.from_uci("e1e2")


def test_static_minimax_bot_works_for_black_to_move():
    board = chess.Board("4k3/4Q3/8/8/8/8/8/4K3 b - - 0 1")
    bot = StaticMinimaxBot(depth=1)

    move = bot.choose_move(board)

    assert move in board.legal_moves


def test_static_minimax_bot_raises_error_when_no_legal_moves():
    board = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")
    bot = StaticMinimaxBot(depth=1)

    assert len(list(board.legal_moves)) == 0

    with pytest.raises(ValueError):
        bot.choose_move(board)