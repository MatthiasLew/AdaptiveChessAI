"""Replay-based facts, without pretending material is an engine accuracy score."""

import chess

from adaptive_chess.evaluation.material import calculate_material_balance


def review_game(moves: list[str], initial_fen: str = chess.STARTING_FEN) -> dict:
    board = chess.Board(initial_fen)
    events = []
    missed = []
    captures = []
    for ply, uci in enumerate(moves, 1):
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            raise ValueError(f"Nielegalny ruch w zapisie: {ply}. {uci}")
        side = "white" if board.turn else "black"
        san = board.san(move)
        before = calculate_material_balance(board)
        mate = None
        for candidate in list(board.legal_moves):
            board.push(candidate)
            is_mate = board.is_checkmate()
            board.pop()
            if is_mate:
                mate = candidate
                break
        alternative = board.san(mate) if mate else None
        board.push(move)
        material = calculate_material_balance(board)
        if mate and not board.is_checkmate():
            missed.append(
                {"ply": ply, "side": side, "played": san, "mate": alternative}
            )
        if abs(material - before) >= 3:
            captures.append({"ply": ply, "san": san, "change": material - before})
        events.append(
            {
                "kind": "move",
                "fen": board.fen(),
                "ply": ply,
                "san": san,
                "uci": uci,
                "side": side,
                "material": material,
            }
        )
    return {
        "events": events,
        "missed_mates": missed,
        "captures": captures,
        "final_fen": board.fen(),
    }
