import pytest

from adaptive_chess.analysis.research_report import (
    human_rows,
    learning_rows,
)
from adaptive_chess.experiments.research import ResearchCampaign


def test_human_threshold_requires_evidence_and_preserves_uncertainty(tmp_path):
    campaign = ResearchCampaign.create(tmp_path / "human.sqlite3", "p")
    point = campaign.data["models"]["td"][0]
    for i in range(10):
        campaign.data["human_evaluations"].append(
            {
                "agent": "td",
                "model_checkpoint": point,
                "human_white": i % 2 == 0,
                "result": "0-1" if i % 2 == 0 else "1-0",
            }
        )
    row = human_rows(campaign)[0]
    assert row["score"] == 1.0
    assert 0 < row["ci_low"] < 0.5
    assert not row["operational_threshold_met"]
    campaign.data["human_evaluations"] *= 2
    assert human_rows(campaign)[0]["operational_threshold_met"]


@pytest.mark.parametrize(
    "result,white,expected",
    [
        ("1-0", True, 1.0),
        ("1-0", False, 0.0),
        ("0-1", True, 0.0),
        ("0-1", False, 1.0),
        ("1/2-1/2", True, 0.5),
        ("*", False, None),
    ],
)
def test_scores_use_agent_color_and_do_not_turn_cutoffs_into_draws(
    result, white, expected
):
    from adaptive_chess.analysis.research_report import score

    assert score(result, white) == expected


def test_learning_curve_excludes_an_incomplete_color_pair(tmp_path):
    campaign = ResearchCampaign.create(tmp_path / "pairs.sqlite3", "p")
    campaign.data["evaluations"] = {
        "results": [
            {
                "agent": "td",
                "games": 0,
                "opening": 0,
                "agent_white": True,
                "result": "1-0",
            },
            {
                "agent": "td",
                "games": 0,
                "opening": 0,
                "agent_white": False,
                "result": "0-1",
            },
            {
                "agent": "td",
                "games": 0,
                "opening": 1,
                "agent_white": True,
                "result": "0-1",
            },
            {
                "agent": "td",
                "games": 0,
                "opening": 1,
                "agent_white": False,
                "result": "*",
            },
        ]
    }
    row = next(r for r in learning_rows(campaign) if r["agent"] == "td")
    assert row["evaluated_games"] == 4
    assert row["complete_pairs"] == 1
    assert row["unfinished"] == 1
    assert row["score"] == 1.0
    assert row["ci_low"] is None
