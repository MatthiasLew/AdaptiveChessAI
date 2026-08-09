import chess
import pytest

from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot


def test_adaptive_minimax_bot_has_default_name_depth_and_empty_profile():
    bot = AdaptiveMinimaxBot()

    assert bot.name == "AdaptiveMinimaxBot"
    assert bot.depth == 1
    assert bot.opponent_profile.observed_moves == 0


def test_adaptive_minimax_bot_rejects_invalid_depth():
    with pytest.raises(ValueError):
        AdaptiveMinimaxBot(depth=0)


def test_adaptive_minimax_bot_returns_legal_move():
    board = chess.Board()
    bot = AdaptiveMinimaxBot(depth=1)

    move = bot.choose_move(board)

    assert move in board.legal_moves


def test_adaptive_minimax_bot_does_not_modify_board():
    board = chess.Board()
    original_fen = board.fen()

    bot = AdaptiveMinimaxBot(depth=1)

    bot.choose_move(board)

    assert board.fen() == original_fen


def test_adaptive_minimax_bot_ignores_own_move_observation():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")

    bot = AdaptiveMinimaxBot()

    bot.observe_move(
        board_before_move=board,
        move=move,
        played_by=chess.WHITE,
        is_own_move=True,
    )

    assert bot.opponent_profile.observed_moves == 0


def test_adaptive_minimax_bot_observes_opponent_move():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")

    bot = AdaptiveMinimaxBot()

    bot.observe_move(
        board_before_move=board,
        move=move,
        played_by=chess.WHITE,
        is_own_move=False,
    )

    assert bot.opponent_profile.observed_moves == 1
    assert bot.opponent_profile.center_moves == 1