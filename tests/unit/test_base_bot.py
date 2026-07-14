import pytest
import chess

from adaptive_chess.bots.base_bot import BaseBot


class IncompleteBot(BaseBot):
    pass


class DummyBot(BaseBot):
    def choose_move(self, board: chess.Board) -> chess.Move:
        return next(iter(board.legal_moves))


def test_incomplete_bot_cannot_be_created():
    with pytest.raises(TypeError):
        IncompleteBot("IncompleteBot")


def test_dummy_bot_can_choose_legal_move():
    board = chess.Board()
    bot = DummyBot("DummyBot")

    move = bot.choose_move(board)

    assert move in board.legal_moves
    assert bot.name == "DummyBot"