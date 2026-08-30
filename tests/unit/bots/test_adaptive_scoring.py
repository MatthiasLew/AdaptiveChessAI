import chess
import pytest

from adaptive_chess.adaptation.adaptive_scoring import (
    calculate_adaptive_move_adjustment,
)
from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile


def test_adaptive_move_adjustment_is_zero_for_empty_profile():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    board.push(move)

    profile = OpponentMoveProfile()

    adjustment = calculate_adaptive_move_adjustment(
        board_after_move=board,
        move=move,
        perspective=chess.WHITE,
        opponent_profile=profile,
    )

    assert adjustment == 0.0


def test_adaptive_move_adjustment_rewards_center_control_against_center_player():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    board.push(move)

    profile = OpponentMoveProfile(
        observed_moves=4,
        center_moves=4,
    )

    adjustment = calculate_adaptive_move_adjustment(
        board_after_move=board,
        move=move,
        perspective=chess.WHITE,
        opponent_profile=profile,
    )

    assert adjustment > 0.0


def test_adaptive_move_adjustment_rewards_protected_piece_against_capturing_player():
    board = chess.Board()
    move = chess.Move.from_uci("b1c3")
    board.push(move)

    profile = OpponentMoveProfile(
        observed_moves=4,
        captures=4,
    )

    adjustment = calculate_adaptive_move_adjustment(
        board_after_move=board,
        move=move,
        perspective=chess.WHITE,
        opponent_profile=profile,
    )

    assert adjustment > 0.0


def test_adaptive_move_adjustment_rejects_invalid_perspective():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    board.push(move)

    profile = OpponentMoveProfile()

    with pytest.raises(ValueError):
        calculate_adaptive_move_adjustment(
            board_after_move=board,
            move=move,
            perspective="white",
            opponent_profile=profile,
        )