"""Small reproducible learners: supervised move ranking and white-value TD(0)."""

import math
import random
from copy import deepcopy
from time import perf_counter

import chess

from adaptive_chess.adaptation.adaptive_scoring import (
    calculate_adaptive_move_adjustment,
)
from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.evaluation.position import evaluate_position

KINDS = ("adaptive", "imitation", "td", "static")
VERSION = "linear_research_v1"


def position_features(board: chess.Board) -> list[float]:
    """White perspective throughout, including when Black is on move."""
    counts = [
        (len(board.pieces(p, chess.WHITE)) - len(board.pieces(p, chess.BLACK))) / 8.0
        for p in range(chess.PAWN, chess.QUEEN + 1)
    ]
    center = (
        sum(
            len(board.attackers(chess.WHITE, s)) - len(board.attackers(chess.BLACK, s))
            for s in (chess.D4, chess.E4, chess.D5, chess.E5)
        )
        / 16.0
    )
    return [*counts, center, 1.0 if board.turn else -1.0]


def move_features(board: chess.Board, move: chess.Move) -> list[float]:
    piece = board.piece_at(move.from_square)
    return [
        float(board.is_capture(move)),
        float(board.gives_check(move)),
        float(move.to_square in (chess.D4, chess.E4, chess.D5, chess.E5)),
        float(board.is_castling(move)),
        float(move.promotion is not None),
        *[
            float(piece is not None and piece.piece_type == kind)
            for kind in range(chess.PAWN, chess.KING + 1)
        ],
    ]


def dot(weights: list[float], features: list[float]) -> float:
    return sum(w * x for w, x in zip(weights, features, strict=True))


def initial_state(kind: str) -> dict:
    if kind not in KINDS:
        raise ValueError("Unknown learning method.")
    return {
        "version": VERSION,
        "kind": kind,
        "weights": [0.0] * (11 if kind == "imitation" else 7),
        "profile": OpponentMoveProfile().to_dict(),
        "updates": 0,
        "learning_rate": 0.05,
        "gamma": 0.99,
    }


class ResearchAgent(BaseBot):
    """All methods share bounded search and a fixed material/positional prior.

    Imitation optimizes a softmax over legal human moves; TD learns an additive
    value residual using transitions from BOTH colors. Neither uses engine labels.
    """

    def __init__(
        self,
        state: dict,
        depth: int = 1,
        nodes: int = 500,
        training: bool = False,
        seed: int = 0,
    ) -> None:
        super().__init__(state.get("kind", "unknown"))
        expected = initial_state(self.name)
        if (
            state.get("version") != VERSION
            or depth < 1
            or nodes < 1
            or len(state.get("weights", [])) != len(expected["weights"])
            or any(
                not isinstance(x, (int, float)) or not math.isfinite(x)
                for x in state["weights"]
            )
        ):
            raise ValueError("Invalid model state or search budget.")
        self.state = deepcopy(state)
        self.profile = OpponentMoveProfile.from_dict(state["profile"])
        self.depth, self.node_limit = depth, nodes
        self.training, self.seed = training, seed
        self.nodes = 0
        self.last_seconds = 0.0
        self.last_learning_seconds = 0.0

    def snapshot(self) -> dict:
        state = deepcopy(self.state)
        state["profile"] = self.profile.to_dict()
        return state

    def _value(self, board: chess.Board) -> float:
        base = evaluate_position(board, chess.WHITE)
        if board.is_game_over():
            return base
        if self.name == "td":
            return base + 3 * math.tanh(
                dot(self.state["weights"], position_features(board))
            )
        return base

    def _search(
        self, board: chess.Board, depth: int, alpha: float, beta: float
    ) -> float:
        self.nodes += 1
        if depth == 0 or board.is_game_over() or self.nodes >= self.node_limit:
            return self._value(board)
        maximizing = board.turn == chess.WHITE
        best = -math.inf if maximizing else math.inf
        for move in board.legal_moves:
            board.push(move)
            score = self._search(board, depth - 1, alpha, beta)
            board.pop()
            best = max(best, score) if maximizing else min(best, score)
            if maximizing:
                alpha = max(alpha, best)
            else:
                beta = min(beta, best)
            if beta <= alpha or self.nodes >= self.node_limit:
                break
        return best

    def choose_move(self, board: chess.Board) -> chess.Move:
        start = perf_counter()
        moves = sorted(board.legal_moves, key=lambda move: move.uci())
        if not moves:
            raise ValueError("No legal move.")
        # Stable per-position tie order: evaluation never advances learned RNG state.
        random.Random(f"{self.seed}:{board.fen()}").shuffle(moves)
        best, best_score = moves[0], -math.inf
        perspective = board.turn
        self.nodes = 0
        for move in moves:
            features = move_features(board, move) if self.name == "imitation" else []
            after = board.copy()
            after.push(move)
            score = self._search(after, self.depth - 1, -math.inf, math.inf)
            score *= 1 if perspective else -1
            if not after.is_game_over():
                if self.name == "imitation":
                    score += dot(self.state["weights"], features)
                elif self.name == "adaptive":
                    score += calculate_adaptive_move_adjustment(
                        after, move, perspective, self.profile
                    )
            if score > best_score:
                best, best_score = move, score
            if self.nodes >= self.node_limit:
                break
        self.last_seconds = perf_counter() - start
        return best

    def observe_move(
        self,
        board_before_move: chess.Board,
        move: chess.Move,
        played_by: chess.Color,
        is_own_move: bool,
    ) -> None:
        start = perf_counter()
        self._learn(board_before_move, move, played_by, is_own_move)
        self.last_learning_seconds = perf_counter() - start if self.training else 0.0

    def _learn(
        self,
        board_before_move: chess.Board,
        move: chess.Move,
        played_by: chess.Color,
        is_own_move: bool,
    ) -> None:
        if not self.training:
            return
        if self.name == "adaptive" and not is_own_move:
            self.profile.observe_move(board_before_move, move)
            self.state["updates"] += 1
        elif self.name == "imitation" and not is_own_move:
            features = [
                move_features(board_before_move, m)
                for m in board_before_move.legal_moves
            ]
            target_features = move_features(board_before_move, move)
            weights = self.state["weights"]
            logits = [dot(weights, f) for f in features]
            probabilities = [math.exp(x - max(logits)) for x in logits]
            total = sum(probabilities)
            for j in range(len(weights)):
                expected = (
                    sum(p * f[j] for p, f in zip(probabilities, features, strict=True))
                    / total
                )
                weights[j] += self.state["learning_rate"] * (
                    target_features[j] - expected
                )
            self.state["updates"] += 1
        elif self.name == "td":
            after = board_before_move.copy()
            after.push(move)
            outcome = after.outcome()
            target = (
                (0.0 if outcome.winner is None else (1.0 if outcome.winner else -1.0))
                if outcome
                else (
                    self.state["gamma"]
                    * math.tanh(dot(self.state["weights"], position_features(after)))
                )
            )
            self._update_td(board_before_move, target)

    def _update_td(self, board: chess.Board, target: float) -> None:
        features = position_features(board)
        weights = self.state["weights"]
        prediction = math.tanh(dot(weights, features))
        delta = (
            self.state["learning_rate"] * (target - prediction) * (1 - prediction**2)
        )
        self.state["weights"] = [
            w + delta * x for w, x in zip(weights, features, strict=True)
        ]
        self.state["updates"] += 1

    def end_game(self, board: chess.Board, result: str) -> None:
        # Rule endings were already learned by observe_move; resignation has no move.
        if self.training and self.name == "td" and not board.is_game_over():
            self._update_td(board, {"1-0": 1.0, "0-1": -1.0, "1/2-1/2": 0.0}[result])
