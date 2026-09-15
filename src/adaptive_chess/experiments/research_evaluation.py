"""Resumable evaluation of every saved checkpoint and final round robin."""

from itertools import combinations
from pathlib import Path
from time import perf_counter

import chess

from adaptive_chess.experiments.campaign import (
    environment_compatible,
    environment_metadata,
    state_hash,
)
from adaptive_chess.experiments.match_runner import MatchRunner
from adaptive_chess.experiments.research import ResearchCampaign, validate_model
from adaptive_chess.learning.agents import KINDS, ResearchAgent


def agent(campaign: ResearchCampaign, point: dict) -> ResearchAgent:
    validate_model(point)
    return ResearchAgent(
        point["state"],
        campaign.data["depth"],
        campaign.data["research"]["nodes"],
        False,
        campaign.data["research"]["seed"],
    )


def play(
    campaign: ResearchCampaign, white: dict, black: dict, opening: list, limit: int
) -> dict:
    board = chess.Board()
    for move in opening:
        board.push_uci(move)
    bots = [agent(campaign, point) for point in (white, black)]
    before = [b.snapshot() for b in bots]
    start = perf_counter()
    result = MatchRunner(limit, board.fen()).play(*bots)
    if before != [b.snapshot() for b in bots]:
        raise RuntimeError("Evaluation mutated a model.")
    return {
        "white": white["kind"],
        "black": black["kind"],
        "result": "*" if result.reached_move_limit else result.result,
        "termination": result.termination_reason.value,
        "moves": list(result.moves_uci),
        "half_moves": result.half_moves,
        "initial_fen": board.fen(),
        "final_fen": result.final_fen,
        "seconds": perf_counter() - start,
        "white_hash": white["hash"],
        "black_hash": black["hash"],
    }


def run_research(
    path: str | Path, max_half_moves: int = 200, tournament: bool = True
) -> None:
    campaign = ResearchCampaign(path)
    if not 1 <= max_half_moves <= 1000:
        raise ValueError("Invalid move limit.")
    if campaign.data["active"] is not None:
        raise ValueError("Najpierw zakończ lub wznów aktywną partię.")
    if campaign.data["evaluations"] is None:
        campaign.data["evaluations"] = {
            "environment": environment_metadata(),
            "limit": max_half_moves,
            "results": [],
            "protocol": "paired_static_reference_v1",
        }
        campaign.save()
    evaluation = campaign.data["evaluations"]
    if not environment_compatible(evaluation["environment"]):
        raise ValueError(
            "Evaluation environment changed; preserve the original environment."
        )
    done = {r["key"] for r in evaluation["results"]}
    static = campaign.data["models"]["static"][0]
    for kind in KINDS:
        for point in campaign.data["models"][kind]:
            for i, opening in enumerate(campaign.data["research"]["openings"]):
                for white_side in (True, False):
                    key = f"{point['hash']}:{i}:{white_side}"
                    if key in done:
                        continue
                    white, black = (point, static) if white_side else (static, point)
                    result = play(campaign, white, black, opening, evaluation["limit"])
                    evaluation["results"].append(
                        {
                            **result,
                            "key": key,
                            "agent": kind,
                            "games": point["games"],
                            "opening": i,
                            "agent_white": white_side,
                        }
                    )
                    campaign.save()
                    print(
                        f"Checkpoint {kind}/{point['games']}: otwarcie {i + 1}, "
                        f"{'białe' if white_side else 'czarne'}",
                        flush=True,
                    )
    if tournament and campaign.training_complete:
        _final_tournament(campaign, evaluation["limit"])
    from adaptive_chess.analysis.research_report import export_research

    export_research(campaign)


def _final_tournament(campaign: ResearchCampaign, limit: int) -> None:
    if campaign.data["tournament"] is None:
        schedule = []
        for first, second in combinations(KINDS, 2):
            for opening in campaign.data["research"]["openings"]:
                for white, black in ((first, second), (second, first)):
                    schedule.append(
                        {"white": white, "black": black, "opening": opening}
                    )
        campaign.data["tournament"] = {
            "schedule": schedule,
            "results": [],
            "max_half_moves": limit,
            "models_hash": state_hash(campaign.data["models"]),
        }
        campaign.save()
    tournament = campaign.data["tournament"]
    if tournament["models_hash"] != state_hash(campaign.data["models"]):
        raise ValueError("Tournament models changed.")
    for index in range(len(tournament["results"]), len(tournament["schedule"])):
        item = tournament["schedule"][index]
        result = play(
            campaign,
            campaign.data["models"][item["white"]][-1],
            campaign.data["models"][item["black"]][-1],
            item["opening"],
            tournament["max_half_moves"],
        )
        tournament["results"].append({**item, **result, "index": index})
        campaign.save()
        print(f"Turniej {index + 1}/{len(tournament['schedule'])}", flush=True)
