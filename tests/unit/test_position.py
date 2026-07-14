import pytest
import chess

from adaptive_chess.evaluation.position import (
    CHECKMATE_SCORE,
    evaluate_position,
)


def test_starting_position_is_equal():
    board = chess.Board()

    assert evaluate_position(board, chess.WHITE) == 0.0
    assert evaluate_position(board, chess.BLACK) == 0.0


def test_position_evaluation_after_white_captures_pawn():
    board = chess.Board()

    board.push_san("e4")
    board.push_san("d5")
    board.push_san("exd5")

    assert evaluate_position(board, chess.WHITE) == 1.0
    assert evaluate_position(board, chess.BLACK) == -1.0


def test_position_evaluation_after_black_queen_is_removed():
    board = chess.Board()

    board.remove_piece_at(chess.D8)

    assert evaluate_position(board, chess.WHITE) == 9.0
    assert evaluate_position(board, chess.BLACK) == -9.0


def test_checkmate_is_best_for_winning_side():
    board = chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1")

    assert board.is_checkmate()
    assert evaluate_position(board, chess.WHITE) == CHECKMATE_SCORE
    assert evaluate_position(board, chess.BLACK) == -CHECKMATE_SCORE


def test_stalemate_is_evaluated_as_draw():
    board = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")

    assert board.is_stalemate()
    assert evaluate_position(board, chess.WHITE) == 0.0
    assert evaluate_position(board, chess.BLACK) == 0.0


def test_position_evaluation_rejects_invalid_perspective():
    board = chess.Board()

    with pytest.raises(ValueError):
        evaluate_position(board, "white")
