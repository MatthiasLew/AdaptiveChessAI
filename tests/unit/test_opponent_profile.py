import pytest
import chess

from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile


def test_opponent_profile_starts_empty():
    profile = OpponentMoveProfile()

    assert profile.observed_moves == 0
    assert profile.captures == 0
    assert profile.checks == 0
    assert profile.center_moves == 0
    assert profile.capture_ratio == 0.0
    assert profile.check_ratio == 0.0
    assert profile.center_move_ratio == 0.0


def test_opponent_profile_observes_center_move():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")

    profile = OpponentMoveProfile()
    profile.observe_move(board, move)

    assert profile.observed_moves == 1
    assert profile.center_moves == 1
    assert profile.center_move_ratio == 1.0


def test_opponent_profile_observes_capture():
    board = chess.Board()

    board.push_san("e4")
    board.push_san("d5")

    move = chess.Move.from_uci("e4d5")

    profile = OpponentMoveProfile()
    profile.observe_move(board, move)

    assert profile.observed_moves == 1
    assert profile.captures == 1
    assert profile.capture_ratio == 1.0


def test_opponent_profile_observes_check():
    board = chess.Board()

    board.push_san("f3")
    board.push_san("e5")
    board.push_san("g4")

    move = chess.Move.from_uci("d8h4")

    profile = OpponentMoveProfile()
    profile.observe_move(board, move)

    assert profile.observed_moves == 1
    assert profile.checks == 1
    assert profile.check_ratio == 1.0


def test_opponent_profile_rejects_illegal_move():
    board = chess.Board()
    move = chess.Move.from_uci("a1a8")

    profile = OpponentMoveProfile()

    with pytest.raises(ValueError):
        profile.observe_move(board, move)