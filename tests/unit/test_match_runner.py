import chess
import pytest

from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.experiments.match_runner import MatchRunner


class ScriptedBot(BaseBot):
    """
    Bot testowy wykonujący z góry ustaloną sekwencję ruchów.

    Nie jest częścią aplikacji produkcyjnej.
    Służy tylko do deterministycznych testów MatchRunnera.
    """

    def __init__(self, name: str, moves: list[str]) -> None:
        super().__init__(name)
        self._moves = moves

    def choose_move(self, board: chess.Board) -> chess.Move:
        if not self._moves:
            raise ValueError("No scripted moves left.")

        move = chess.Move.from_uci(self._moves.pop(0))

        if move not in board.legal_moves:
            raise ValueError(f"Scripted move is illegal: {move}")

        return move


def test_match_runner_can_play_random_bots_until_move_limit():
    runner = MatchRunner(max_half_moves=10)

    result = runner.play(RandomBot("RandomWhite"), RandomBot("RandomBlack"))

    assert result.white_bot_name == "RandomWhite"
    assert result.black_bot_name == "RandomBlack"
    assert result.result in {"1-0", "0-1", "1/2-1/2"}
    assert result.half_moves <= 10
    assert len(result.moves_uci) == result.half_moves
    assert all(isinstance(move, str) for move in result.moves_uci)
    assert isinstance(result.final_fen, str)


def test_match_runner_marks_move_limit_as_reached():
    runner = MatchRunner(max_half_moves=1)

    result = runner.play(RandomBot("RandomWhite"), RandomBot("RandomBlack"))

    assert result.half_moves == 1
    assert len(result.moves_uci) == 1
    assert result.reached_move_limit is True
    assert result.result == "1/2-1/2"


def test_match_runner_can_finish_checkmate_game():
    white_bot = ScriptedBot("WhiteScriptedBot", ["f2f3", "g2g4"])
    black_bot = ScriptedBot("BlackScriptedBot", ["e7e5", "d8h4"])

    runner = MatchRunner(max_half_moves=10)

    result = runner.play(white_bot, black_bot)

    assert result.result == "0-1"
    assert result.half_moves == 4
    assert result.moves_uci == ("f2f3", "e7e5", "g2g4", "d8h4")
    assert result.reached_move_limit is False


def test_match_runner_rejects_invalid_move_limit():
    with pytest.raises(ValueError):
        MatchRunner(max_half_moves=0)