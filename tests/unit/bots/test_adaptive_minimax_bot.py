import chess
import pytest

from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot
from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile

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

def test_adaptive_minimax_bot_uses_adaptive_adjustment(monkeypatch):
    board = chess.Board()
    bot = AdaptiveMinimaxBot(depth=1)

    preferred_move = chess.Move.from_uci("b1c3")

    def fake_alpha_beta_score(
        board: chess.Board,
        depth: int,
        perspective: chess.Color,
    ) -> float:
        return 0.0

    def fake_adaptive_adjustment(
        board_after_move: chess.Board,
        move: chess.Move,
        perspective: chess.Color,
        opponent_profile,
    ) -> float:
        if move == preferred_move:
            return 1.0

        return 0.0

    monkeypatch.setattr(
        "adaptive_chess.bots.adaptive_minimax_bot.alpha_beta_score",
        fake_alpha_beta_score,
    )
    monkeypatch.setattr(
        "adaptive_chess.bots.adaptive_minimax_bot.calculate_adaptive_move_adjustment",
        fake_adaptive_adjustment,
    )

    move = bot.choose_move(board)

    assert move == preferred_move

def test_adaptive_minimax_bot_can_use_shared_opponent_profile():
    shared_profile = OpponentMoveProfile()

    first_bot = AdaptiveMinimaxBot(
        name="FirstAdaptiveBot",
        opponent_profile=shared_profile,
    )
    second_bot = AdaptiveMinimaxBot(
        name="SecondAdaptiveBot",
        opponent_profile=shared_profile,
    )

    board = chess.Board()
    move = chess.Move.from_uci("e2e4")

    first_bot.observe_move(
        board_before_move=board,
        move=move,
        played_by=chess.WHITE,
        is_own_move=False,
    )

    assert first_bot.opponent_profile.observed_moves == 1
    assert second_bot.opponent_profile.observed_moves == 1
    assert shared_profile.observed_moves == 1