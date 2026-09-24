"""Durable training campaigns. SQLite transactions commit every individual move."""

import hashlib
import json
import platform
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any
from uuid import uuid4

import chess

from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile
from adaptive_chess.bots.adaptive_minimax_bot import (
    ADAPTIVE_BOT_VERSION,
    AdaptiveMinimaxBot,
)
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.bots.static_minimax_bot import StaticMinimaxBot
from adaptive_chess.play.human_vs_bot_session import HumanVsBotSession

AGENTS = ("adaptive", "static")
SCHEMA_VERSION = 1


def state_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def environment_metadata() -> dict:
    source_root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for path in sorted(source_root.rglob("*.py")):
        digest.update(path.relative_to(source_root).as_posix().encode())
        digest.update(path.read_bytes())
    build_info = source_root / "_build.json"
    source_hash = (
        json.loads(build_info.read_text())["source_sha256"]
        if build_info.exists()
        else digest.hexdigest()
    )
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "dependencies": {
            name: version(name) for name in ("chess", "PySide6", "pandas", "matplotlib")
        },
        "python": platform.python_version(),
        "chess": version("chess"),
        "source_sha256": source_hash,
    }


def environment_compatible(saved: dict) -> bool:
    """Allow the audited UI-only upgrade without changing research conditions.

    Preserve the original campaign manifest. New games record their runtime
    manifest separately; unknown source versions still cannot resume a study.
    """
    current = environment_metadata()
    compatible_sources = {
        current["source_sha256"],
        "d755b319cfb7961cfa0cc155b520d801f011d4597528d277c296311ff973f711",
        "3ec6a4a0990fc51d9d90eb12cfa543a2259b0c679011bf0cb8e3774217dd3d5c",
        # 2026-09-23 GUI/help/chart updates: research agents and training
        # semantics unchanged. Preserve manifests of games played during testing.
        "f3f6c0a3a4a6b216e624740e155928b026011105781fcaae7421ff319e4effb9",
        "1e3e891d838ba3bedbada285cbd84df17e31718a24ad79a91541382af2bf71c1",
        "18f8edc01a8f4af82eeb391697daa2522c95d00181f8dfb8888a17c91ebb719b",
        # Spectator/dashboard upgrade leaves the four research agents unchanged.
        "28d1830630b44993147ed2316fc0336da6326f480fc856212416330a079c9311",
    }
    return saved.get("source_sha256") in compatible_sources and {
        k: v for k, v in saved.items() if k != "source_sha256"
    } == {k: v for k, v in current.items() if k != "source_sha256"}


def checkpoint(profile: dict, games: int) -> dict:
    payload = {"profile": profile, "games": games, "version": ADAPTIVE_BOT_VERSION}
    return {**payload, "hash": state_hash(payload)}


def validate_checkpoint(value: dict) -> None:
    payload = {key: value[key] for key in ("profile", "games", "version")}
    if state_hash(payload) != value["hash"]:
        raise ValueError("Checkpoint checksum mismatch.")
    if value["version"] != ADAPTIVE_BOT_VERSION:
        raise ValueError("Unsupported adaptive bot version.")
    OpponentMoveProfile.from_dict(value["profile"])


class Campaign:
    """One local campaign per file; optimistic revisions prevent lost updates."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).resolve()
        if not self.path.is_file():
            raise ValueError("Nie znaleziono pliku kampanii.")
        try:
            with closing(sqlite3.connect(self.path)) as db, db:
                row = db.execute("SELECT revision, document FROM campaign").fetchone()
        except sqlite3.DatabaseError as error:
            raise ValueError("Nieprawidłowa baza kampanii.") from error
        if row is None:
            raise ValueError("Pusta baza kampanii.")
        self.revision, raw = row
        self.data: dict[str, Any] = json.loads(raw)
        if self.data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Nieobsługiwana wersja kampanii.")
        for item in self.data["checkpoints"]:
            validate_checkpoint(item)
        self.session: HumanVsBotSession | None = None
        self.bot: BaseBot | None = None

    @classmethod
    def create(
        cls, path: str | Path, participant: str, games: int = 10, depth: int = 1
    ) -> "Campaign":
        if not participant.strip() or not 1 <= games <= 1000 or not 1 <= depth <= 2:
            raise ValueError("Podaj pseudonim, 1-1000 partii i głębokość 1-2.")
        target = Path(path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents accidental overwrite of research data.
        with target.open("xb"):
            pass
        data = {
            "schema_version": SCHEMA_VERSION,
            "id": uuid4().hex,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "participant": participant.strip(),
            "games_per_agent": games,
            "depth": depth,
            "initial_fen": chess.STARTING_FEN,
            "completed": [],
            "active": None,
            "checkpoints": [checkpoint(OpponentMoveProfile().to_dict(), 0)],
            "tournament": None,
            "protocol": "alternating_agents_and_colors_v1",
            "environment": environment_metadata(),
        }
        with closing(sqlite3.connect(target)) as db, db:
            db.execute(
                "CREATE TABLE campaign (id INTEGER PRIMARY KEY CHECK(id=1), "
                "revision INTEGER NOT NULL, document TEXT NOT NULL)"
            )
            db.execute("INSERT INTO campaign VALUES (1, 0, ?)", (json.dumps(data),))
        return cls(target)

    def save(self) -> None:
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            cursor = db.execute(
                "UPDATE campaign SET revision=revision+1, document=? "
                "WHERE id=1 AND revision=?",
                (json.dumps(self.data, ensure_ascii=False), self.revision),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Kampania zmieniła się w innym oknie. Wczytaj ponownie."
                )
        self.revision += 1

    @property
    def training_complete(self) -> bool:
        return len(self.data["completed"]) == 2 * self.data["games_per_agent"]

    def progress(self) -> str:
        counts = {
            kind: sum(g["agent"] == kind for g in self.data["completed"])
            for kind in AGENTS
        }
        profile = self.data["checkpoints"][-1]["profile"]
        return (
            f"{self.data['participant']} | Adaptive {counts['adaptive']}/"
            f"{self.data['games_per_agent']} | Static {counts['static']}/"
            f"{self.data['games_per_agent']} | "
            f"Zapisane obserwacje: {profile['observed_moves']}"
        )

    def resume(self) -> HumanVsBotSession:
        """Rebuild from pre-game state and replay exactly once, then continue."""
        if self.session is not None:
            self.session.continue_bot_turn()
            return self.session
        if self.training_complete:
            raise ValueError("Trening zakończony. Uruchom turniej.")
        if self.data["active"] is None:
            index = len(self.data["completed"])
            self.data["active"] = {
                "id": uuid4().hex,
                "agent": AGENTS[index % 2],
                "human_white": (index // 2) % 2 == 0,
                "moves": [],
                "checkpoint": self.data["checkpoints"][-1],
            }
            self.save()
        active = self.data["active"]
        validate_checkpoint(active["checkpoint"])
        if active["agent"] == "adaptive":
            self.bot = AdaptiveMinimaxBot(
                depth=self.data["depth"],
                training=True,
                opponent_profile=OpponentMoveProfile.from_dict(
                    active["checkpoint"]["profile"]
                ),
            )
        else:
            self.bot = StaticMinimaxBot(depth=self.data["depth"])
        self.session = HumanVsBotSession(
            self.bot,
            human_color=active["human_white"],
            initial_fen=self.data["initial_fen"],
            on_move=self._save_move,
        )
        self.session.restore_moves(active["moves"])
        self.session.continue_bot_turn()
        return self.session

    def _save_move(self, session: HumanVsBotSession) -> None:
        self.data["active"]["moves"] = [m.move_uci for m in session.get_move_history()]
        self.save()

    def finish(self, resign: bool = False) -> None:
        """Commit game and checkpoint together; repeated finalization is harmless."""
        if self.data["active"] is None:
            return
        session = self.resume()
        if not session.is_game_over() and not resign:
            raise ValueError("Partia trwa. Możesz ją wznowić lub poddać.")
        result = session.get_result()
        reason = "rules"
        if result is None:
            result = "0-1" if session.human_color else "1-0"
            reason = "resignation"
        game = {
            **self.data["active"],
            "result": result,
            "termination": reason,
            "final_fen": session.get_fen(),
        }
        self.data["completed"].append(game)
        if isinstance(self.bot, AdaptiveMinimaxBot):
            games = sum(g["agent"] == "adaptive" for g in self.data["completed"])
            self.data["checkpoints"].append(
                checkpoint(self.bot.opponent_profile.to_dict(), games)
            )
        self.data["active"] = None
        self.save()
        self.session = None
        self.bot = None
