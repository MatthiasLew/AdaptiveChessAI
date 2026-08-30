import pytest
import chess

from adaptive_chess.evaluation.position import (
    CHECKMATE_SCORE,
    calculate_center_control_balance,
    calculate_mobility_balance,
    evaluate_position,
)


def test_starting_position_is_equal():
    board = chess.Board()

    assert evaluate_position(board, chess.WHITE) == 0.0
    assert evaluate_position(board, chess.BLACK) == 0.0


def test_position_evaluation_after_white_captures_pawn_is_better_for_white():
    board = chess.Board()

    board.push_san("e4")
    board.push_san("d5")
    board.push_san("exd5")

    white_score = evaluate_position(board, chess.WHITE)
    black_score = evaluate_position(board, chess.BLACK)

    assert white_score > 0.0
    assert black_score == pytest.approx(-white_score)


def test_position_evaluation_after_black_queen_is_removed_is_better_for_white():
    board = chess.Board()

    board.remove_piece_at(chess.D8)

    white_score = evaluate_position(board, chess.WHITE)
    black_score = evaluate_position(board, chess.BLACK)

    assert white_score > 8.0
    assert black_score == pytest.approx(-white_score)


def test_center_control_after_e4_is_better_for_white():
    board = chess.Board()

    board.push_san("e4")

    white_center_control = calculate_center_control_balance(board, chess.WHITE)
    black_center_control = calculate_center_control_balance(board, chess.BLACK)

    assert white_center_control > black_center_control
    assert black_center_control == -white_center_control


def test_starting_position_has_equal_mobility():
    board = chess.Board()

    assert calculate_mobility_balance(board, chess.WHITE) == 0
    assert calculate_mobility_balance(board, chess.BLACK) == 0


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


def test_mobility_balance_rejects_invalid_perspective():
    board = chess.Board()

    with pytest.raises(ValueError):
        calculate_mobility_balance(board, "white")


def test_center_control_balance_rejects_invalid_perspective():
    board = chess.Board()

    with pytest.raises(ValueError):
        calculate_center_control_balance(board, "white")