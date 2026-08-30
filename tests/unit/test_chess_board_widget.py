import chess

from adaptive_chess.ui.widgets.chess_board_widget import (
    is_light_square,
    piece_to_unicode,
    square_to_grid_position,
)


def test_piece_to_unicode_returns_empty_string_for_empty_square():
    assert piece_to_unicode(None) == ""


def test_piece_to_unicode_returns_white_piece_symbol():
    piece = chess.Piece.from_symbol("K")

    assert piece_to_unicode(piece) == "♔"


def test_piece_to_unicode_returns_black_piece_symbol():
    piece = chess.Piece.from_symbol("q")

    assert piece_to_unicode(piece) == "♛"


def test_square_to_grid_position_for_white_orientation():
    assert square_to_grid_position(chess.A1, flipped=False) == (7, 0)
    assert square_to_grid_position(chess.H8, flipped=False) == (0, 7)


def test_square_to_grid_position_for_black_orientation():
    assert square_to_grid_position(chess.A1, flipped=True) == (0, 7)
    assert square_to_grid_position(chess.H8, flipped=True) == (7, 0)


def test_is_light_square_uses_chessboard_colors():
    assert is_light_square(chess.A1) is False
    assert is_light_square(chess.B1) is True
    assert is_light_square(chess.A2) is True