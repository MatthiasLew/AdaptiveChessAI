import chess
import pytest

from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.play.human_vs_bot_session import (
    HumanVsBotSession,
    PlayerType,
)


class FirstLegalMoveBot(BaseBot):
    """
    Bot testowy wybierający pierwszy legalny ruch.
    """

    def __init__(self, name: str = "FirstLegalMoveBot") -> None:
        super().__init__(name)

    def choose_move(self, board: chess.Board) -> chess.Move:
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            raise ValueError("No legal moves available.")

        return legal_moves[0]


class IllegalMoveBot(BaseBot):
    """
    Bot testowy zwracający nielegalny ruch.
    """

    def __init__(self) -> None:
        super().__init__("IllegalMoveBot")

    def choose_move(self, board: chess.Board) -> chess.Move:
        return chess.Move.from_uci("a1a8")


def test_session_starts_without_bot_move_when_human_is_white():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    first_move = session.start()

    assert first_move is None
    assert session.get_turn() == chess.WHITE
    assert session.get_move_history() == ()


def test_session_starts_with_bot_move_when_human_is_black():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.BLACK,
    )

    first_move = session.start()

    assert first_move is not None
    assert first_move.player_type == PlayerType.BOT
    assert first_move.color == chess.WHITE
    assert session.get_turn() == chess.BLACK
    assert len(session.get_move_history()) == 1


def test_session_rejects_invalid_human_color():
    with pytest.raises(ValueError):
        HumanVsBotSession(
            bot=FirstLegalMoveBot(),
            human_color="white",
        )


def test_session_rejects_move_before_start():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    with pytest.raises(RuntimeError):
        session.play_human_move_uci("e2e4")


def test_session_rejects_second_start():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    session.start()

    with pytest.raises(RuntimeError):
        session.start()


def test_human_move_is_followed_by_bot_move():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    session.start()

    result = session.play_human_move_uci("e2e4")

    assert result.human_move.player_type == PlayerType.HUMAN
    assert result.human_move.color == chess.WHITE
    assert result.human_move.move_uci == "e2e4"

    assert result.bot_move is not None
    assert result.bot_move.player_type == PlayerType.BOT
    assert result.bot_move.color == chess.BLACK

    assert len(session.get_move_history()) == 2
    assert session.get_turn() == chess.WHITE


def test_session_rejects_invalid_uci_move():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    session.start()

    with pytest.raises(ValueError):
        session.play_human_move_uci("not-a-move")


def test_session_rejects_illegal_human_move():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    session.start()

    with pytest.raises(ValueError):
        session.play_human_move_uci("a1a8")


def test_session_rejects_illegal_bot_move():
    session = HumanVsBotSession(
        bot=IllegalMoveBot(),
        human_color=chess.WHITE,
    )

    session.start()

    with pytest.raises(ValueError):
        session.play_human_move_uci("e2e4")


def test_session_exposes_legal_moves_as_uci():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    session.start()

    legal_moves = session.get_legal_moves_uci()

    assert "e2e4" in legal_moves
    assert "g1f3" in legal_moves


def test_session_exposes_status_message():
    session = HumanVsBotSession(
        bot=FirstLegalMoveBot(),
        human_color=chess.WHITE,
    )

    session.start()

    assert session.get_status_message() == "White to move."


def test_session_with_random_bot_can_play_one_turn():
    session = HumanVsBotSession(
        bot=RandomBot(),
        human_color=chess.WHITE,
    )

    session.start()

    result = session.play_human_move_uci("e2e4")

    assert result.human_move.move_uci == "e2e4"
    assert result.bot_move is not None
    assert len(session.get_move_history()) == 2
