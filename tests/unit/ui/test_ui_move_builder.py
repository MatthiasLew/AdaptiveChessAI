import chess

from adaptive_chess.ui.move_builder import (
    build_uci_move_from_clicks,
    get_legal_target_squares,
)


def test_build_uci_move_from_clicks_returns_regular_move():
    board = chess.Board()

    move_uci = build_uci_move_from_clicks(
        board=board,
        from_square=chess.E2,
        to_square=chess.E4,
    )

    assert move_uci == "e2e4"


def test_build_uci_move_from_clicks_returns_queen_promotion_by_default():
    board = chess.Board("8/4P3/8/8/8/8/8/4k2K w - - 0 1")

    move_uci = build_uci_move_from_clicks(
        board=board,
        from_square=chess.E7,
        to_square=chess.E8,
    )

    assert move_uci == "e7e8q"


def test_build_uci_move_from_clicks_returns_base_uci_for_illegal_move():
    board = chess.Board()

    move_uci = build_uci_move_from_clicks(
        board=board,
        from_square=chess.A1,
        to_square=chess.A8,
    )

    assert move_uci == "a1a8"


def test_get_legal_target_squares_returns_targets_for_selected_piece():
    board = chess.Board()

    targets = get_legal_target_squares(
        board=board,
        from_square=chess.E2,
    )

    assert chess.E3 in targets
    assert chess.E4 in targets


def test_get_legal_target_squares_returns_empty_tuple_for_empty_square():
    board = chess.Board()

    targets = get_legal_target_squares(
        board=board,
        from_square=chess.E4,
    )

    assert targets == ()