import chess
import pytest

from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.experiments.match_runner import MatchRunner
from adaptive_chess.evaluation.position import CHECKMATE_SCORE


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
    assert isinstance(result.final_material_balance, int)
    assert len(result.material_balances) == result.half_moves
    assert len(result.position_scores) == result.half_moves
    assert all(isinstance(balance, int) for balance in result.material_balances)
    assert all(isinstance(score, float) for score in result.position_scores)


def test_match_runner_marks_move_limit_as_reached():
    runner = MatchRunner(max_half_moves=1)

    result = runner.play(RandomBot("RandomWhite"), RandomBot("RandomBlack"))

    assert result.half_moves == 1
    assert len(result.moves_uci) == 1
    assert result.reached_move_limit is True
    assert result.result == "1/2-1/2"
    assert isinstance(result.final_material_balance, int)
    assert len(result.material_balances) == 1
    assert len(result.position_scores) == 1


def test_match_runner_can_finish_checkmate_game():
    white_bot = ScriptedBot("WhiteScriptedBot", ["f2f3", "g2g4"])
    black_bot = ScriptedBot("BlackScriptedBot", ["e7e5", "d8h4"])

    runner = MatchRunner(max_half_moves=10)

    result = runner.play(white_bot, black_bot)

    assert result.result == "0-1"
    assert result.half_moves == 4
    assert result.moves_uci == ("f2f3", "e7e5", "g2g4", "d8h4")
    assert result.reached_move_limit is False
    assert result.final_material_balance == 0
    assert result.material_balances == (0, 0, 0, 0)
    assert result.position_scores[-1] == -CHECKMATE_SCORE


def test_match_runner_tracks_material_balance_after_each_move():
    white_bot = ScriptedBot("WhiteScriptedBot", ["e2e4", "e4d5"])
    black_bot = ScriptedBot("BlackScriptedBot", ["d7d5"])

    runner = MatchRunner(max_half_moves=3)

    result = runner.play(white_bot, black_bot)

    assert result.moves_uci == ("e2e4", "d7d5", "e4d5")
    assert result.material_balances == (0, 0, 1)
    assert result.position_scores == (0.0, 0.0, 1.0)
    assert result.final_material_balance == 1


def test_match_runner_rejects_invalid_move_limit():
    with pytest.raises(ValueError):
        MatchRunner(max_half_moves=0)


def test_match_runner_reports_final_material_balance_from_white_perspective():
    initial_fen = "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    runner = MatchRunner(max_half_moves=1, initial_fen=initial_fen)

    result = runner.play(RandomBot("RandomWhite"), RandomBot("RandomBlack"))

    assert result.final_material_balance == 9
