import pytest
import chess

from src.adaptive_chess.core.game import Game


def test_game_starts_from_initial_position():
    game = Game()

    assert game.get_turn() == chess.WHITE
    assert len(game.get_legal_moves()) == 20
    assert not game.is_game_over()
    assert game.get_result() is None


def test_game_can_be_created_from_fen():
    fen = "8/8/8/8/8/8/8/K6k w - - 0 1"

    game = Game(fen)

    assert game.get_fen() == fen


def test_game_can_make_legal_move():
    game = Game()

    game.make_move_uci("e2e4")

    board = game.get_board_copy()

    assert game.get_turn() == chess.BLACK
    assert board.piece_at(chess.E4) == chess.Piece(chess.PAWN, chess.WHITE)
    assert board.piece_at(chess.E2) is None


def test_game_rejects_illegal_move():
    game = Game()

    with pytest.raises(ValueError):
        game.make_move_uci("e2e5")


def test_game_rejects_invalid_uci_move():
    game = Game()

    with pytest.raises(ValueError):
        game.make_move_uci("not-a-move")


def test_get_board_copy_does_not_modify_original_game():
    game = Game()
    original_fen = game.get_fen()

    board_copy = game.get_board_copy()
    board_copy.push(chess.Move.from_uci("e2e4"))

    assert game.get_fen() == original_fen


def test_game_detects_checkmate_result():
    game = Game()

    game.make_move_uci("f2f3")
    game.make_move_uci("e7e5")
    game.make_move_uci("g2g4")
    game.make_move_uci("d8h4")

    assert game.is_game_over()
    assert game.get_result() == "0-1"
