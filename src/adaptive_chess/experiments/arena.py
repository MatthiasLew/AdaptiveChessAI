"""Spectator matches of frozen checkpoints, separate from research evaluation."""

from collections.abc import Callable
from threading import Event

import chess

from adaptive_chess.evaluation.material import calculate_material_balance
from adaptive_chess.experiments.research import ResearchCampaign
from adaptive_chess.experiments.research_evaluation import agent


def spectator_match(
    campaign: ResearchCampaign,
    white: dict,
    black: dict,
    limit: int,
    delay: float,
    cancel: Event,
    publish: Callable[[dict], None],
) -> dict:
    if not 1 <= limit <= 1000 or not 0 <= delay <= 5:
        raise ValueError("Nieprawidłowy limit lub tempo podglądu.")
    bots = [agent(campaign, p) for p in (white, black)]
    snapshots = [bot.snapshot() for bot in bots]
    board = chess.Board()
    moves: list[str] = []
    metrics = []
    publish(
        {
            "kind": "start",
            "white": white["kind"],
            "black": black["kind"],
            "fen": board.fen(),
            "limit": limit,
        }
    )
    while not board.is_game_over() and len(moves) < limit:
        if cancel.wait(delay):
            break
        bot = bots[0 if board.turn else 1]
        move = bot.choose_move(board.copy())
        if cancel.is_set():
            break
        san, side = board.san(move), "white" if board.turn else "black"
        board.push(move)
        moves.append(move.uci())
        metrics.append({"side": side, "nodes": bot.nodes, "seconds": bot.last_seconds})
        publish(
            {
                "kind": "move",
                "fen": board.fen(),
                "ply": len(moves),
                "san": san,
                "uci": move.uci(),
                "side": side,
                "material": calculate_material_balance(board),
                "nodes": bot.nodes,
                "seconds": bot.last_seconds,
            }
        )
    if snapshots != [bot.snapshot() for bot in bots]:
        raise RuntimeError("Podgląd zmienił zamrożony model.")
    outcome = board.outcome()
    result = outcome.result() if outcome else "*"
    reason = "rules" if outcome else "cancelled" if cancel.is_set() else "move_limit"
    publish({"kind": "end", "result": result, "reason": reason})
    return {
        "white": white["kind"],
        "black": black["kind"],
        "result": result,
        "termination": reason,
        "moves": moves,
        "move_metrics": metrics,
        "initial_fen": chess.STARTING_FEN,
        "final_fen": board.fen(),
        "white_hash": white["hash"],
        "black_hash": black["hash"],
    }
