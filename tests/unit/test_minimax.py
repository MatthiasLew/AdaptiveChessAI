import pytest
import chess

from adaptive_chess.evaluation.position import CHECKMATE_SCORE
from adaptive_chess.search.minimax import (
    alpha_beta_score,
    find_best_move,
    find_best_move_alpha_beta,
    minimax_score,
)

def test_minimax_score_at_depth_zero_uses_position_evaluation():
    board = chess.Board()

    board.push_san("e4")
    board.push_san("d5")
    board.push_san("exd5")

    white_score = minimax_score(board, depth=0, perspective=chess.WHITE)
    black_score = minimax_score(board, depth=0, perspective=chess.BLACK)

    assert white_score > 0.0
    assert black_score == pytest.approx(-white_score)
def test_find_best_move_can_capture_free_queen():
    board = chess.Board("4k3/8/8/8/8/8/4q3/4K3 w - - 0 1")

    move = find_best_move(board, depth=1, perspective=chess.WHITE)

    assert move == chess.Move.from_uci("e1e2")


def test_find_best_move_does_not_modify_board():
    board = chess.Board()
    original_fen = board.fen()

    find_best_move(board, depth=1, perspective=chess.WHITE)

    assert board.fen() == original_fen


def test_find_best_move_finds_mate_in_one():
    board = chess.Board("7k/6Q1/6K1/8/8/8/8/8 w - - 0 1")

    move = find_best_move(board, depth=1, perspective=chess.WHITE)

    board.push(move)

    assert board.is_checkmate()
    assert minimax_score(board, depth=0, perspective=chess.WHITE) == CHECKMATE_SCORE


def test_find_best_move_rejects_depth_zero():
    board = chess.Board()

    with pytest.raises(ValueError):
        find_best_move(board, depth=0, perspective=chess.WHITE)


def test_minimax_score_rejects_negative_depth():
    board = chess.Board()

    with pytest.raises(ValueError):
        minimax_score(board, depth=-1, perspective=chess.WHITE)


def test_find_best_move_rejects_wrong_perspective_for_turn():
    board = chess.Board()

    with pytest.raises(ValueError):
        find_best_move(board, depth=1, perspective=chess.BLACK)


def test_find_best_move_rejects_position_with_no_legal_moves():
    board = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")

    assert len(list(board.legal_moves)) == 0

    with pytest.raises(ValueError):
        find_best_move(board, depth=1, perspective=chess.BLACK)

def test_alpha_beta_score_matches_minimax_score_at_depth_zero():
    board = chess.Board()

    assert alpha_beta_score(board, depth=0, perspective=chess.WHITE) == minimax_score(
        board,
        depth=0,
        perspective=chess.WHITE,
    )


def test_alpha_beta_score_matches_minimax_score_after_capture():
    board = chess.Board()

    board.push_san("e4")
    board.push_san("d5")
    board.push_san("exd5")

    assert alpha_beta_score(board, depth=1, perspective=chess.WHITE) == minimax_score(
        board,
        depth=1,
        perspective=chess.WHITE,
    )


def test_find_best_move_alpha_beta_can_capture_free_queen():
    board = chess.Board("4k3/8/8/8/8/8/4q3/4K3 w - - 0 1")

    move = find_best_move_alpha_beta(board, depth=1, perspective=chess.WHITE)

    assert move == chess.Move.from_uci("e1e2")


def test_find_best_move_alpha_beta_does_not_modify_board():
    board = chess.Board()
    original_fen = board.fen()

    find_best_move_alpha_beta(board, depth=1, perspective=chess.WHITE)

    assert board.fen() == original_fen


def test_find_best_move_alpha_beta_rejects_depth_zero():
    board = chess.Board()

    with pytest.raises(ValueError):
        find_best_move_alpha_beta(board, depth=0, perspective=chess.WHITE)


def test_alpha_beta_score_rejects_negative_depth():
    board = chess.Board()

    with pytest.raises(ValueError):
        alpha_beta_score(board, depth=-1, perspective=chess.WHITE)


def test_find_best_move_alpha_beta_rejects_wrong_perspective_for_turn():
    board = chess.Board()

    with pytest.raises(ValueError):
        find_best_move_alpha_beta(board, depth=1, perspective=chess.BLACK)


def test_find_best_move_alpha_beta_rejects_position_with_no_legal_moves():
    board = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")

    assert len(list(board.legal_moves)) == 0

    with pytest.raises(ValueError):
        find_best_move_alpha_beta(board, depth=1, perspective=chess.BLACK)