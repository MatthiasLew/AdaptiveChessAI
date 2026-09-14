import json
import sqlite3

import chess
import chess.pgn
import pytest

from adaptive_chess.adaptation.adaptive_scoring import (
    calculate_adaptive_move_adjustment,
)
from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile
from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot
from adaptive_chess.evaluation.position import evaluate_position
from adaptive_chess.experiments.campaign import Campaign, state_hash
from adaptive_chess.experiments.campaign_tournament import (
    export_campaign,
    prepare_tournament,
    run_tournament,
    standings,
)


def test_training_survives_restart_and_replay_does_not_double_count(tmp_path):
    path = tmp_path / "campaign.sqlite3"
    campaign = Campaign.create(path, "player", games=2)
    campaign.resume().play_human_move_uci("e2e4")
    before = campaign.bot.opponent_profile.to_dict()
    fen = campaign.session.get_fen()
    resumed = Campaign(path)
    assert resumed.resume().get_fen() == fen
    assert resumed.bot.opponent_profile.to_dict() == before
    resumed.finish(resign=True)
    resumed.finish(resign=True)
    assert len(resumed.data["completed"]) == 1
    assert resumed.data["checkpoints"][-1]["profile"] == before
    # Static reference gets the same game quota; round two flips human colors.
    resumed.resume()
    resumed.finish(resign=True)
    resumed = Campaign(path)
    assert resumed.resume().human_color == chess.BLACK
    assert resumed.bot.opponent_profile.to_dict() == before
    assert len(resumed.session.get_move_history()) == 1


def test_restart_after_human_move_before_bot_response(tmp_path, monkeypatch):
    path = tmp_path / "game.sqlite3"
    campaign = Campaign.create(path, "p", 1)
    session = campaign.resume()

    def crash(board):
        raise RuntimeError("Interrupted inference")

    monkeypatch.setattr(campaign.bot, "choose_move", crash)
    with pytest.raises(RuntimeError, match="Interrupted"):
        session.play_human_move_uci("e2e4")
    assert Campaign(path).data["active"]["moves"] == ["e2e4"]
    restored = Campaign(path)
    session = restored.resume()
    assert len(session.get_move_history()) == 2
    assert restored.bot.opponent_profile.observed_moves == 1
    assert Campaign(path).data["active"]["moves"] == [
        m.move_uci for m in session.get_move_history()
    ]


def test_frozen_bot_does_not_learn_but_training_bot_does():
    frozen = AdaptiveMinimaxBot(training=False)
    train = AdaptiveMinimaxBot()
    for bot in (frozen, train):
        bot.observe_move(chess.Board(), chess.Move.from_uci("e2e4"), True, False)
    assert frozen.opponent_profile.observed_moves == 0
    assert train.opponent_profile.observed_moves == 1


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"observed_moves": True, "captures": 0, "checks": 0, "center_moves": 0},
        {"observed_moves": 1, "captures": 2, "checks": 0, "center_moves": 0},
        {"observed_moves": -1, "captures": 0, "checks": 0, "center_moves": 0},
    ],
)
def test_rejects_invalid_profile(data):
    with pytest.raises(ValueError):
        OpponentMoveProfile.from_dict(data)


def test_automatic_draw_evaluation_including_repetition():
    board = chess.Board("7k/8/8/8/8/8/R7/K7 w - - 150 76")
    assert board.is_valid() and board.is_game_over()
    assert evaluate_position(board) == 0
    assert (
        calculate_adaptive_move_adjustment(
            board,
            chess.Move.from_uci("a3a2"),
            chess.WHITE,
            OpponentMoveProfile(10, 8, 8, 8),
        )
        == 0
    )
    board = chess.Board("7k/8/8/8/8/8/R7/K7 w - - 0 1")
    for _ in range(4):
        for move in ("a2b2", "h8g8", "b2a2", "g8h8"):
            board.push_uci(move)
    assert board.is_fivefold_repetition()
    assert evaluate_position(board) == 0


def test_campaign_does_not_overwrite_or_silently_lose_concurrent_updates(tmp_path):
    path = tmp_path / "campaign.sqlite3"
    first = Campaign.create(path, "p", 1)
    second = Campaign(path)
    with pytest.raises(FileExistsError):
        Campaign.create(path, "other", 1)
    first.resume()
    with pytest.raises(RuntimeError, match="innym oknie"):
        second.save()
    assert Campaign(path).data["active"] is not None


def test_checkpoint_corruption_rejected(tmp_path):
    path = tmp_path / "campaign.sqlite3"
    campaign = Campaign.create(path, "p", 1)
    campaign.data["checkpoints"][0]["profile"]["observed_moves"] = 3
    with sqlite3.connect(path) as db:
        db.execute("UPDATE campaign SET document=?", (json.dumps(campaign.data),))
    with pytest.raises(ValueError, match="checksum"):
        Campaign(path)


def test_complete_campaign_frozen_tournament_resume_and_export(tmp_path, monkeypatch):
    path = tmp_path / "campaign.sqlite3"
    campaign = Campaign.create(path, "p", 1)
    with pytest.raises(ValueError, match="trening"):
        prepare_tournament(campaign)
    campaign.resume().play_human_move_uci("e2e4")
    campaign.finish(resign=True)
    campaign.resume()
    campaign.finish(resign=True)
    before = state_hash(campaign.data["checkpoints"])
    prepare_tournament(campaign, max_half_moves=2)
    from adaptive_chess.experiments.match_runner import MatchRunner

    original = MatchRunner.play
    calls = []

    def interrupt(self, white, black):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError("stop")
        return original(self, white, black)

    monkeypatch.setattr(MatchRunner, "play", interrupt)
    with pytest.raises(RuntimeError, match="stop"):
        run_tournament(path)
    assert len(Campaign(path).data["tournament"]["results"]) == 1
    monkeypatch.setattr(MatchRunner, "play", original)
    run_tournament(path)
    result = Campaign(path)
    assert state_hash(result.data["checkpoints"]) == before
    games = result.data["tournament"]["results"]
    assert len(games) == 18
    assert {g["index"] for g in games} == set(range(18))
    assert all(g["result"] == "*" for g in games)
    assert all(row["draws"] == 0 for row in standings(result))
    run_tournament(path)
    assert len(Campaign(path).data["tournament"]["results"]) == 18
    output = export_campaign(result)
    with (output / "games.pgn").open(encoding="utf-8") as stream:
        parsed = []
        while (game := chess.pgn.read_game(stream)) is not None:
            assert not game.errors
            parsed.append(game)
    assert len(parsed) == 20
    assert (output / "report.md").is_file()


def test_export_without_tournament(tmp_path):
    campaign = Campaign.create(tmp_path / "campaign.sqlite3", "p", 1)
    output = export_campaign(campaign)
    assert (output / "games.pgn").read_text(encoding="utf-8") == ""
