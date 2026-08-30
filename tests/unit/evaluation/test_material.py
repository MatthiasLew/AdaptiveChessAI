import pytest
import chess

from adaptive_chess.evaluation.material import (
    calculate_material,
    calculate_material_balance,
)


def test_starting_position_has_equal_material():
    board = chess.Board()

    white_material = calculate_material(board, chess.WHITE)
    black_material = calculate_material(board, chess.BLACK)

    assert white_material == 39
    assert black_material == 39


def test_starting_position_has_zero_material_balance():
    board = chess.Board()

    balance = calculate_material_balance(board, chess.WHITE)

    assert balance == 0


def test_material_balance_after_white_captures_pawn():
    board = chess.Board()

    board.push_san("e4")
    board.push_san("d5")
    board.push_san("exd5")

    white_balance = calculate_material_balance(board, chess.WHITE)
    black_balance = calculate_material_balance(board, chess.BLACK)

    assert white_balance == 1
    assert black_balance == -1


def test_material_after_removing_black_queen():
    board = chess.Board()

    board.remove_piece_at(chess.D8)

    white_material = calculate_material(board, chess.WHITE)
    black_material = calculate_material(board, chess.BLACK)

    assert white_material == 39
    assert black_material == 30
    assert calculate_material_balance(board, chess.WHITE) == 9


def test_calculate_material_rejects_invalid_color():
    board = chess.Board()

    with pytest.raises(ValueError):
        calculate_material(board, "white")


def test_calculate_material_balance_rejects_invalid_perspective():
    board = chess.Board()

    with pytest.raises(ValueError):
        calculate_material_balance(board, "black")