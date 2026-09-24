from copy import deepcopy

import chess
import pytest

from adaptive_chess.experiments.research import ResearchCampaign


def test_bad_openings_do_not_create_campaign(tmp_path):
    path = tmp_path / "bad.sqlite3"
    with pytest.raises(ValueError):
        ResearchCampaign.create(path, "p", openings=[["e2e5"]])
    assert not path.exists()


def test_different_environment_blocks_further_training(tmp_path, monkeypatch):
    import adaptive_chess.experiments.research as module

    campaign = ResearchCampaign.create(tmp_path / "env.sqlite3", "p")
    monkeypatch.setattr(module, "environment_compatible", lambda saved: False)
    with pytest.raises(ValueError, match="środowisko"):
        campaign.resume()
    assert campaign.data["active"] is None


def test_database_connections_close_without_waiting_for_gc(tmp_path, monkeypatch):
    import sqlite3

    import adaptive_chess.experiments.campaign as module

    original = sqlite3.connect
    connections = []

    def track(*args, **kwargs):
        db = original(*args, **kwargs)
        connections.append(db)
        return db

    monkeypatch.setattr(module.sqlite3, "connect", track)
    path = tmp_path / "closed.sqlite3"
    campaign = ResearchCampaign.create(path, "p")
    campaign.resume().play_human_move_uci("e2e4")
    campaign.finish(resign=True)
    for db in connections:
        with pytest.raises(sqlite3.ProgrammingError, match="closed"):
            db.execute("SELECT 1")
    path.unlink()


@pytest.mark.parametrize(
    "changes",
    [
        {"nodes": 0},
        {"nodes": 100001},
        {"openings": []},
        {"openings": [[], []]},
        {"openings": [["f2f3", "e7e5", "g2g4", "d8h4"]]},
    ],
    ids=["zero-budget", "excess-budget", "no-openings", "duplicate", "terminal"],
)
def test_invalid_protocol_does_not_leave_a_database(tmp_path, changes):
    path = tmp_path / "invalid.sqlite3"
    with pytest.raises(ValueError):
        ResearchCampaign.create(path, "participant", **changes)
    assert not path.exists()


def test_modified_checkpoint_is_rejected_on_load(tmp_path):
    path = tmp_path / "tampered.sqlite3"
    campaign = ResearchCampaign.create(path, "p")
    campaign.data["models"]["imitation"][0]["state"]["weights"][0] = 42
    campaign.save()
    with pytest.raises(ValueError, match="checkpoint"):
        ResearchCampaign(path)


def test_training_balances_agents_and_colors_across_restart(tmp_path):
    path = tmp_path / "balanced.sqlite3"
    campaign = ResearchCampaign.create(path, "p", games=2, nodes=10)
    order = campaign.data["research"]["agents"]
    seen = []
    for index in range(8):
        campaign = ResearchCampaign(path)
        session = campaign.resume()
        seen.append((session.bot_name, session.human_color))
        assert session.human_color == (index < 4)
        campaign.finish(resign=True)
    assert [name for name, _ in seen] == order * 2
    assert campaign.training_complete
    assert all(len(history) == 3 for history in campaign.data["models"].values())


def test_held_out_games_alternate_colors_without_advancing_training(tmp_path):
    campaign = ResearchCampaign.create(tmp_path / "heldout.sqlite3", "p", nodes=10)
    before = deepcopy(campaign.data["models"])
    for color in (chess.WHITE, chess.BLACK):
        session = campaign.resume_evaluation("td", 0)
        assert session.human_color == color
        campaign.finish(resign=True)
    assert campaign.data["models"] == before
    assert campaign.data["completed"] == []
    assert len(campaign.data["human_evaluations"]) == 2


@pytest.mark.parametrize(
    "old_hash",
    [
        "3ec6a4a0990fc51d9d90eb12cfa543a2259b0c679011bf0cb8e3774217dd3d5c",
        "f3f6c0a3a4a6b216e624740e155928b026011105781fcaae7421ff319e4effb9",
        "1e3e891d838ba3bedbada285cbd84df17e31718a24ad79a91541382af2bf71c1",
        "18f8edc01a8f4af82eeb391697daa2522c95d00181f8dfb8888a17c91ebb719b",
    ],
)
def test_known_ui_upgrade_preserves_existing_campaign(tmp_path, old_hash):
    campaign = ResearchCampaign.create(tmp_path / "upgrade.sqlite3", "p")
    campaign.data["environment"]["source_sha256"] = old_hash
    campaign.save()
    campaign.resume()
    assert campaign.data["environment"]["source_sha256"] == old_hash
    assert campaign.data["active"]["runtime_environment"]["source_sha256"] != old_hash


def test_unknown_source_version_still_blocks_resume(tmp_path):
    campaign = ResearchCampaign.create(tmp_path / "unknown.sqlite3", "p")
    campaign.data["environment"]["source_sha256"] = "unknown"
    campaign.save()
    with pytest.raises(ValueError, match="środowisko"):
        campaign.resume()
