from copy import deepcopy

import chess
import chess.pgn
import pytest

from adaptive_chess.analysis.research_report import (
    export_research,
    human_rows,
    learning_rows,
)
from adaptive_chess.experiments.campaign import state_hash
from adaptive_chess.experiments.research import ResearchCampaign, load_campaign
from adaptive_chess.experiments.research_evaluation import run_research


def test_four_methods_restart_control_games_curves_and_tournament(tmp_path):
    path = tmp_path / "research.sqlite3"
    campaign = ResearchCampaign.create(
        path, "test", games=1, nodes=30, openings=[["e2e4", "e7e5"]]
    )
    assert isinstance(load_campaign(path), ResearchCampaign)
    for _ in range(4):
        session = campaign.resume()
        session.play_human_move_uci("e2e4")
        snapshot = campaign.bot.snapshot()
        fen = session.get_fen()
        campaign = ResearchCampaign(path)
        assert campaign.resume().get_fen() == fen
        assert campaign.bot.snapshot() == snapshot
        campaign.finish(resign=True)
        campaign.finish(resign=True)
    assert campaign.training_complete
    assert {len(h) for h in campaign.data["models"].values()} == {2}
    assert campaign.data["models"]["td"][-1]["state"]["weights"] != [0.0] * 7
    before = state_hash(campaign.data["models"])
    campaign.resume_evaluation("imitation", 0).play_human_move_uci("e2e4")
    campaign = ResearchCampaign(path)
    campaign.resume()
    campaign.finish(resign=True)
    assert state_hash(campaign.data["models"]) == before
    assert len(campaign.data["completed"]) == 4
    assert len(human_rows(campaign)) == 1
    assert not human_rows(campaign)[0]["operational_threshold_met"]
    run_research(path, max_half_moves=2)
    campaign = ResearchCampaign(path)
    assert len(campaign.data["evaluations"]["results"]) == 16
    assert len(campaign.data["tournament"]["results"]) == 12
    assert state_hash(campaign.data["models"]) == before
    run_research(path, max_half_moves=100)
    assert len(ResearchCampaign(path).data["evaluations"]["results"]) == 16
    rows = learning_rows(campaign)
    assert all(row["score"] is None for row in rows)
    assert all(row["unfinished"] == 2 for row in rows)
    output = export_research(campaign)
    assert (output / "learning.png").stat().st_size > 1000
    records = (
        campaign.data["completed"]
        + campaign.data["human_evaluations"]
        + campaign.data["evaluations"]["results"]
        + campaign.data["tournament"]["results"]
    )
    with (output / "games.pgn").open(encoding="utf-8") as stream:
        for record in records:
            game = chess.pgn.read_game(stream)
            assert game is not None and not game.errors
            assert game.headers["Result"] == record["result"]
            board = game.board()
            for move in game.mainline_moves():
                assert move in board.legal_moves
                board.push(move)
            assert board.fen() == record["final_fen"]
            assert [m.uci() for m in game.mainline_moves()] == record["moves"]
        assert chess.pgn.read_game(stream) is None


def test_evaluation_can_run_before_training_and_remains_isolated(tmp_path):
    path = tmp_path / "initial.sqlite3"
    campaign = ResearchCampaign.create(path, "p", games=1, nodes=10, openings=[[]])
    original = deepcopy(campaign.data["models"])
    run_research(path, 1)
    restored = ResearchCampaign(path)
    assert restored.data["models"] == original
    assert restored.data["tournament"] is None


def test_checkpoint_evaluation_resumes_after_interruption(tmp_path, monkeypatch):
    import adaptive_chess.experiments.research_evaluation as module

    path = tmp_path / "resume.sqlite3"
    ResearchCampaign.create(path, "p", games=1, nodes=10, openings=[[]])
    original = module.play
    calls = 0

    def interrupted(*args):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated interruption")
        return original(*args)

    monkeypatch.setattr(module, "play", interrupted)
    with pytest.raises(RuntimeError, match="simulated"):
        module.run_research(path, 1)
    first = deepcopy(ResearchCampaign(path).data["evaluations"]["results"])
    assert len(first) == 1
    monkeypatch.setattr(module, "play", original)
    module.run_research(path, 1)
    results = ResearchCampaign(path).data["evaluations"]["results"]
    assert len(results) == 8
    assert results[0] == first[0]
