"""Frozen, color-paired evaluation; one transaction per completed match."""

import csv
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import chess
import chess.pgn

from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile
from adaptive_chess.bots.adaptive_minimax_bot import AdaptiveMinimaxBot
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot
from adaptive_chess.experiments.campaign import (
    Campaign,
    environment_metadata,
    state_hash,
    validate_checkpoint,
)
from adaptive_chess.experiments.match_runner import MatchRunner

OPENINGS = ((), ("e2e4", "e7e5"), ("d2d4", "d7d5"))
ENTRANTS = ("Static", "Adaptive-0", "Adaptive-final")


def prepare_tournament(campaign: Campaign, max_half_moves: int = 200) -> dict:
    if not campaign.training_complete:
        raise ValueError("Najpierw ukończ trening wszystkich agentów.")
    if not 1 <= max_half_moves <= 1000:
        raise ValueError("Limit półruchów musi wynosić 1-1000.")
    if campaign.data["tournament"] is None:
        schedule = []
        for first, second in combinations(ENTRANTS, 2):
            for opening in OPENINGS:
                board = chess.Board()
                for move in opening:
                    board.push_uci(move)
                for white, black in ((first, second), (second, first)):
                    schedule.append(
                        {
                            "white": white,
                            "black": black,
                            "opening": opening,
                            "initial_fen": board.fen(),
                        }
                    )
        campaign.data["tournament"] = {
            "schedule": schedule,
            "results": [],
            "max_half_moves": max_half_moves,
            "checkpoints_hash": state_hash(campaign.data["checkpoints"]),
            "protocol": "frozen_three_openings_color_pairs_v1",
            "environment": environment_metadata(),
        }
        campaign.save()
    return campaign.data["tournament"]


def make_entrant(campaign: Campaign, name: str) -> BaseBot:
    if name == "Static":
        return StaticMinimaxBot(name=name, depth=campaign.data["depth"])
    point = campaign.data["checkpoints"][0 if name == "Adaptive-0" else -1]
    validate_checkpoint(point)
    return AdaptiveMinimaxBot(
        name=name,
        depth=campaign.data["depth"],
        training=False,
        opponent_profile=OpponentMoveProfile.from_dict(point["profile"]),
    )


def run_tournament(path: str | Path, max_half_moves: int = 200) -> None:
    campaign = Campaign(path)
    tournament = prepare_tournament(campaign, max_half_moves)
    if tournament["environment"] != environment_metadata():
        raise ValueError("Kod lub środowisko zmieniły się od rozpoczęcia turnieju.")
    if state_hash(campaign.data["checkpoints"]) != tournament["checkpoints_hash"]:
        raise ValueError("Stan agentów zmienił się po utworzeniu turnieju.")
    for index in range(len(tournament["results"]), len(tournament["schedule"])):
        match = tournament["schedule"][index]
        white, black = (
            make_entrant(campaign, match[color]) for color in ("white", "black")
        )
        profiles = [
            bot.opponent_profile.to_dict()
            for bot in (white, black)
            if isinstance(bot, AdaptiveMinimaxBot)
        ]
        result = MatchRunner(
            max_half_moves=tournament["max_half_moves"],
            initial_fen=match["initial_fen"],
        ).play(white, black)
        after = [
            bot.opponent_profile.to_dict()
            for bot in (white, black)
            if isinstance(bot, AdaptiveMinimaxBot)
        ]
        if profiles != after:
            raise RuntimeError("Agent zmienił stan w trybie oceny.")
        # Legacy runner encodes technical cutoffs as draws; campaign exports do not.
        tournament["results"].append(
            {
                "index": index,
                **match,
                "result": "*" if result.reached_move_limit else result.result,
                "termination": result.termination_reason.value,
                "moves": list(result.moves_uci),
                "half_moves": result.half_moves,
                "final_fen": result.final_fen,
            }
        )
        campaign.save()
        print(
            f"Zapisano partię {index + 1}/{len(tournament['schedule'])}: "
            f"{white.name} - {black.name}",
            flush=True,
        )
    export_campaign(campaign)


def standings(campaign: Campaign) -> list[dict]:
    rows: dict[str, dict[str, Any]] = {
        name: {
            "agent": name,
            "games": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "unfinished": 0,
            "points": 0.0,
        }
        for name in ENTRANTS
    }
    tournament = campaign.data["tournament"]
    for game in tournament["results"] if tournament else []:
        for color, win in (("white", "1-0"), ("black", "0-1")):
            row = rows[game[color]]
            row["games"] += 1
            if game["result"] == "*":
                row["unfinished"] += 1
            elif game["result"] == win:
                row["wins"] += 1
                row["points"] += 1
            elif game["result"] == "1/2-1/2":
                row["draws"] += 1
                row["points"] += 0.5
            else:
                row["losses"] += 1
    return sorted(rows.values(), key=lambda row: -row["points"])


def export_campaign(campaign: Campaign) -> Path:
    output = campaign.path.parent / f"{campaign.path.stem}_report"
    output.mkdir(exist_ok=True)
    (output / "campaign.json").write_text(
        json.dumps(campaign.data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    table = standings(campaign)
    with (output / "standings.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    lines = [
        "# Wyniki kampanii",
        "",
        campaign.progress(),
        "",
        "| Agent | Partie | W | D | L | Przerwane | Punkty |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in table:
        lines.append(
            "| "
            + " | ".join(
                str(row[k])
                for k in (
                    "agent",
                    "games",
                    "wins",
                    "draws",
                    "losses",
                    "unfinished",
                    "points",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Punkty dotyczą wyłącznie partii zakończonych według zasad.",
            "Przerwane limitem są oznaczone *, nie są remisami ani porażkami.",
            "Przy różnej liczbie przerwanych partii suma punktów nie ustala "
            "wiarygodnego zwycięzcy. To mały turniej pilotażowy, nie dowód "
            "przewagi nad człowiekiem.",
        ]
    )
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (output / "games.pgn").open("w", encoding="utf-8") as stream:
        records = [
            (game, campaign.data["initial_fen"], True)
            for game in campaign.data["completed"]
        ]
        tournament = campaign.data["tournament"]
        if tournament:
            records.extend(
                (game, game["initial_fen"], False) for game in tournament["results"]
            )
        for record, fen, human in records:
            game = chess.pgn.Game()
            game.setup(chess.Board(fen))
            game.headers["Event"] = campaign.data["id"]
            game.headers["Result"] = record["result"]
            if human:
                white = (
                    campaign.data["participant"]
                    if record["human_white"]
                    else record["agent"]
                )
                black = (
                    record["agent"]
                    if record["human_white"]
                    else campaign.data["participant"]
                )
            else:
                white, black = record["white"], record["black"]
            game.headers["White"], game.headers["Black"] = white, black
            game.headers["Termination"] = record["termination"]
            node = game
            for move in record["moves"]:
                node = node.add_variation(chess.Move.from_uci(move))
            print(game, file=stream, end="\n\n")
    return output
