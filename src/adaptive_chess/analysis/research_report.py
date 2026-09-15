"""Learning curves, paired uncertainty, human assessment and portable raw exports."""

import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import chess
import chess.pgn

from adaptive_chess.experiments.research import ResearchCampaign
from adaptive_chess.learning.agents import KINDS


def score(result: str, white: bool) -> float | None:
    if result == "*":
        return None
    if result == "1/2-1/2":
        return 0.5
    return float(result == ("1-0" if white else "0-1"))


def interval(blocks: list[float], seed: int) -> tuple[float | None, float | None]:
    if len(blocks) < 2:
        return None, None
    rng = random.Random(seed)
    samples = sorted(
        sum(rng.choices(blocks, k=len(blocks))) / len(blocks) for _ in range(2000)
    )
    return samples[49], samples[1949]


def learning_rows(campaign: ResearchCampaign) -> list[dict]:
    evaluation = campaign.data["evaluations"]
    records = evaluation["results"] if evaluation else []
    output = []
    for kind in KINDS:
        baseline = None
        for point in campaign.data["models"][kind]:
            games = [
                r
                for r in records
                if r["agent"] == kind and r["games"] == point["games"]
            ]
            by_opening = defaultdict(list)
            for game in games:
                value = score(game["result"], game["agent_white"])
                if value is not None:
                    by_opening[game["opening"]].append(value)
            pairs = [
                sum(values) / 2 for values in by_opening.values() if len(values) == 2
            ]
            mean = sum(pairs) / len(pairs) if pairs else None
            if point["games"] == 0:
                baseline = mean
            low, high = interval(pairs, campaign.data["research"]["seed"])
            training = [g for g in campaign.data["completed"] if g["agent"] == kind][
                : point["games"]
            ]
            output.append(
                {
                    "agent": kind,
                    "training_games": point["games"],
                    "training_moves": sum(len(g["moves"]) for g in training),
                    "updates": point["state"]["updates"],
                    "evaluated_games": len(games),
                    "unfinished": sum(g["result"] == "*" for g in games),
                    "complete_pairs": len(pairs),
                    "score": mean,
                    "ci_low": low,
                    "ci_high": high,
                    "gain": mean - baseline
                    if mean is not None and baseline is not None
                    else None,
                    "decision_seconds": sum(
                        m["seconds"] for g in training for m in g["move_metrics"]
                    ),
                    "learning_seconds": sum(
                        m.get("learning_seconds", 0)
                        for g in training
                        for m in g["move_metrics"]
                    )
                    + sum(g.get("final_update_seconds", 0) for g in training),
                    "search_nodes": sum(
                        m["nodes"] for g in training for m in g["move_metrics"]
                    ),
                }
            )
    return output


def human_rows(campaign: ResearchCampaign) -> list[dict]:
    groups = defaultdict(list)
    for game in campaign.data["human_evaluations"]:
        groups[(game["agent"], game["model_checkpoint"]["games"])].append(game)
    rows = []
    for (kind, checkpoint), games in sorted(groups.items()):
        values = [score(g["result"], not g["human_white"]) for g in games]
        points = [v for v in values if v is not None]
        pairs = [(points[i] + points[i + 1]) / 2 for i in range(0, len(points) - 1, 2)]
        mean = sum(pairs) / len(pairs) if pairs else None
        # Hoeffding bound on independent bounded color-pair scores, including
        # nonzero uncertainty when every observed pair has the same result.
        radius = math.sqrt(math.log(40) / (2 * len(pairs))) if pairs else None
        low = max(0.0, mean - radius) if mean is not None and radius else None
        high = min(1.0, mean + radius) if mean is not None and radius else None
        config = campaign.data["research"]
        met = (
            2 * len(pairs) >= config["human_min_games"]
            and mean is not None
            and mean >= config["human_threshold"]
            and low is not None
            and low > 0.5
        )
        rows.append(
            {
                "agent": kind,
                "checkpoint": checkpoint,
                "games": len(games),
                "complete_pairs": len(pairs),
                "score": mean,
                "ci_low": low,
                "ci_high": high,
                "operational_threshold_met": met,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        if rows:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def export_research(campaign: ResearchCampaign) -> Path:
    from adaptive_chess.experiments.campaign_tournament import standings

    output = campaign.path.parent / f"{campaign.path.stem}_report"
    output.mkdir(exist_ok=True)
    (output / "campaign.json").write_text(
        json.dumps(campaign.data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rows, human = learning_rows(campaign), human_rows(campaign)
    write_csv(output / "learning.csv", rows)
    write_csv(output / "human_evaluation.csv", human)
    write_csv(output / "standings.csv", standings(campaign))
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure(figsize=(10, 5), layout="constrained")
    FigureCanvasAgg(figure)
    axis = figure.subplots()
    for kind in KINDS:
        measured = [r for r in rows if r["agent"] == kind and r["score"] is not None]
        if measured:
            axis.plot(
                [r["training_games"] for r in measured],
                [r["score"] for r in measured],
                marker="o",
                label=kind,
            )
            uncertain = [r for r in measured if r["ci_low"] is not None]
            axis.fill_between(
                [r["training_games"] for r in uncertain],
                [r["ci_low"] for r in uncertain],
                [r["ci_high"] for r in uncertain],
                alpha=0.12,
            )
    axis.set(
        xlabel="Training games",
        ylabel="Score vs static (complete color pairs)",
        ylim=(-0.05, 1.05),
    )
    axis.grid(alpha=0.25)
    if any(r["score"] is not None for r in rows):
        axis.legend()
    else:
        axis.text(
            0.5,
            0.5,
            "No complete evaluation pairs yet",
            ha="center",
            transform=axis.transAxes,
        )
    figure.savefig(output / "learning.png", dpi=150)
    lines = [
        "# Badanie AdaptiveChessAI",
        "",
        campaign.progress(),
        "",
        "| Agent | Trening | Pary oceny | Wynik | Przyrost | Przerwane |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['agent']} | {row['training_games']} | {row['complete_pairs']} | "
            f"{row['score']} | {row['gain']} | {row['unfinished']} |"
        )
    lines.extend(
        [
            "",
            "![Krzywe uczenia](learning.png)",
            "",
            "Przedziały 95%: bootstrap parami kolorów w obrębie otwarcia (2000 prób). "
            "Mały zbiór otwarć: przedział nie dotyczy populacji graczy.",
            "Krzywa obejmuje pełne pary. Przerwania nie są remisami; "
            "liczba przerwań jest raportowana i ogranicza porównanie.",
            "",
            "## Ocena przeciw człowiekowi",
            "",
        ]
    )
    if not human:
        lines.append("Brak kontrolnych partii człowieka. Nie ustalono progu przewagi.")
    for row in human:
        lines.append(
            f"- {row['agent']}, checkpoint {row['checkpoint']}: "
            f"{row['games']} partii, wynik {row['score']}, "
            f"próg operacyjny: {row['operational_threshold_met']}."
        )
    lines.append(
        "\nPróg operacyjny: minimum 10 gier, wynik >= 60%, dolna granica > 50%. "
        "Ocena człowieka: granica Hoeffdinga 95% na pełnych parach kolorów. "
        "Wymaga niezależnego bloku potwierdzającego; nie stanowi automatycznego "
        "dowodu naukowego przy wielokrotnym sprawdzaniu checkpointów."
    )
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    records = [
        (g, campaign.data["initial_fen"], True)
        for g in campaign.data["completed"] + campaign.data["human_evaluations"]
    ]
    evaluation = campaign.data["evaluations"]
    if evaluation:
        records.extend((g, g["initial_fen"], False) for g in evaluation["results"])
    tournament = campaign.data["tournament"]
    if tournament:
        records.extend((g, g["initial_fen"], False) for g in tournament["results"])
    with (output / "games.pgn").open("w", encoding="utf-8") as stream:
        for record, fen, human_game in records:
            game = chess.pgn.Game()
            game.setup(chess.Board(fen))
            game.headers["Event"] = campaign.data["id"]
            game.headers["Result"] = record["result"]
            if human_game:
                players = (campaign.data["participant"], record["agent"])
                if not record["human_white"]:
                    players = players[::-1]
            else:
                players = record["white"], record["black"]
            game.headers["White"], game.headers["Black"] = players
            game.headers["Termination"] = record["termination"]
            node = game
            for move in record["moves"]:
                node = node.add_variation(chess.Move.from_uci(move))
            print(game, file=stream, end="\n\n")
    return output
