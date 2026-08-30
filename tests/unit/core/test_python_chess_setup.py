import chess


def test_starting_position_has_20_legal_moves():
    board = chess.Board()

    legal_moves = list(board.legal_moves)

    assert len(legal_moves) == 20
    assert board.turn == chess.WHITE
    assert not board.is_game_over()
