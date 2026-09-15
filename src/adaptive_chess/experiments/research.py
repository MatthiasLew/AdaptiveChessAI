"""Multi-method campaigns with isolated held-out human evaluation."""

import random
from copy import deepcopy
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

import chess

from adaptive_chess.experiments.campaign import (
    Campaign,
    environment_compatible,
    environment_metadata,
    state_hash,
)
from adaptive_chess.learning.agents import KINDS, ResearchAgent, initial_state
from adaptive_chess.play.human_vs_bot_session import HumanVsBotSession


def model_checkpoint(kind: str, games: int, state: dict) -> dict:
    payload = {"kind": kind, "games": games, "state": deepcopy(state)}
    return {**payload, "hash": state_hash(payload)}


def validate_model(point: dict) -> None:
    if point["hash"] != state_hash({k: point[k] for k in ("kind", "games", "state")}):
        raise ValueError("Uszkodzony checkpoint modelu.")
    if point["kind"] != point["state"]["kind"]:
        raise ValueError("Niezgodna metoda uczenia.")
    ResearchAgent(point["state"])


class ResearchCampaign(Campaign):
    def __init__(self, path) -> None:
        super().__init__(path)
        try:
            config = self.data["research"]
            if (
                set(config["agents"]) != set(KINDS)
                or len(config["agents"]) != len(KINDS)
                or not 1 <= config["nodes"] <= 100000
                or not self.data["models"]
            ):
                raise ValueError("Nieprawidłowy protokół badania.")
            for history in self.data["models"].values():
                for point in history:
                    validate_model(point)
        except (KeyError, TypeError) as error:
            raise ValueError("Nieprawidłowy format badania.") from error

    @classmethod
    def create(
        cls,
        path,
        participant: str,
        games: int = 10,
        depth: int = 1,
        nodes: int = 500,
        seed: int = 42,
        openings: list | None = None,
    ):
        if not 1 <= nodes <= 100000:
            raise ValueError("Budżet węzłów musi wynosić 1-100000.")
        openings = (
            openings
            if openings is not None
            else [[], ["e2e4", "e7e5"], ["d2d4", "d7d5"]]
        )
        if not openings or len(openings) > 100:
            raise ValueError("Wybierz 1-100 otwarć.")
        if len({tuple(o) for o in openings}) != len(openings):
            raise ValueError("Otwarcia muszą być różne.")
        for opening in openings:
            board = chess.Board()
            for move in opening:
                if board.is_game_over():
                    raise ValueError("Otwarcie kończy partię.")
                board.push_uci(move)
            if board.is_game_over():
                raise ValueError("Otwarcie kończy partię.")
        legacy = Campaign.create(path, participant, games, depth)
        order = list(KINDS)
        random.Random(seed).shuffle(order)
        legacy.data.update(
            {
                "research": {
                    "agents": order,
                    "nodes": nodes,
                    "seed": seed,
                    "openings": openings,
                    "human_threshold": 0.60,
                    "human_min_games": 10,
                    "checkpoint_interval": 1,
                },
                "models": {
                    k: [model_checkpoint(k, 0, initial_state(k))] for k in KINDS
                },
                "human_evaluations": [],
                "evaluations": None,
                "protocol": "four_methods_shared_node_budget_v2",
            }
        )
        legacy.save()
        return cls(path)

    @property
    def training_complete(self) -> bool:
        return len(self.data["completed"]) == len(KINDS) * self.data["games_per_agent"]

    def progress(self) -> str:
        return (
            self.data["participant"]
            + " | "
            + " | ".join(
                f"{kind}: {len(self.data['models'][kind]) - 1}/"
                f"{self.data['games_per_agent']}"
                for kind in self.data["research"]["agents"]
            )
        )

    def resume_evaluation(self, kind: str, games: int) -> HumanVsBotSession:
        if self.data["active"] is not None:
            raise ValueError("Najpierw zakończ aktywną partię.")
        point = next(
            (p for p in self.data["models"][kind] if p["games"] == games), None
        )
        if point is None:
            raise ValueError("Nie ma tego checkpointu.")
        count = sum(
            g["agent"] == kind and g["model_checkpoint"]["games"] == games
            for g in self.data["human_evaluations"]
        )
        self._new_active(kind, point, count % 2 == 0, "evaluation")
        return self.resume()

    def _new_active(self, kind: str, point: dict, white: bool, phase: str) -> None:
        self.data["active"] = {
            "id": uuid4().hex,
            "runtime_environment": environment_metadata(),
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "agent": kind,
            "human_white": white,
            "moves": [],
            "move_metrics": [],
            "phase": phase,
            "model_checkpoint": deepcopy(point),
        }
        self.save()

    def resume(self) -> HumanVsBotSession:
        if not environment_compatible(self.data["environment"]):
            raise ValueError(
                "Zmieniono środowisko badania. Użyj pierwotnej wersji aplikacji."
            )
        if self.session:
            self.session.continue_bot_turn()
            return self.session
        if self.data["active"] is None:
            if self.training_complete:
                raise ValueError("Trening zakończony.")
            index = len(self.data["completed"])
            kind = self.data["research"]["agents"][index % len(KINDS)]
            self._new_active(
                kind,
                self.data["models"][kind][-1],
                (index // len(KINDS)) % 2 == 0,
                "training",
            )
        active = self.data["active"]
        validate_model(active["model_checkpoint"])
        self.bot = ResearchAgent(
            active["model_checkpoint"]["state"],
            self.data["depth"],
            self.data["research"]["nodes"],
            active["phase"] == "training",
            self.data["research"]["seed"],
        )
        self.session = HumanVsBotSession(
            self.bot, active["human_white"], self.data["initial_fen"], self._save_move
        )
        self.session.restore_moves(active["moves"])
        self.session.continue_bot_turn()
        return self.session

    def _save_move(self, session: HumanVsBotSession) -> None:
        active = self.data["active"]
        history = session.get_move_history()
        active["moves"] = [m.move_uci for m in history]
        bot = self.bot
        if isinstance(bot, ResearchAgent):
            active["move_metrics"].append(
                {
                    "ply": len(history),
                    "learning_seconds": bot.last_learning_seconds,
                    "actor": history[-1].player_type.value,
                    "nodes": bot.nodes if history[-1].player_type.value == "bot" else 0,
                    "seconds": bot.last_seconds
                    if history[-1].player_type.value == "bot"
                    else 0,
                }
            )
        self.save()

    def finish(self, resign: bool = False) -> None:
        if self.data["active"] is None:
            return
        session = self.resume()
        if not session.is_game_over() and not resign:
            raise ValueError("Partia nadal trwa.")
        result = session.get_result() or ("0-1" if session.human_color else "1-0")
        active = self.data["active"]
        record = {
            **active,
            "result": result,
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "final_fen": session.get_fen(),
            "termination": "rules" if session.is_game_over() else "resignation",
        }
        assert isinstance(self.bot, ResearchAgent)
        if active["phase"] == "training":
            start = perf_counter()
            self.bot.end_game(session.get_board_copy(), result)
            record["final_update_seconds"] = perf_counter() - start
            history = self.data["models"][active["agent"]]
            history.append(
                model_checkpoint(active["agent"], len(history), self.bot.snapshot())
            )
            self.data["completed"].append(record)
        else:
            if self.bot.snapshot() != active["model_checkpoint"]["state"]:
                raise RuntimeError("Ocena zmieniła stan modelu.")
            self.data["human_evaluations"].append(record)
        self.data["active"] = None
        self.save()
        self.session = None
        self.bot = None


def load_campaign(path) -> Campaign:
    campaign = Campaign(path)
    return ResearchCampaign(path) if "research" in campaign.data else campaign
