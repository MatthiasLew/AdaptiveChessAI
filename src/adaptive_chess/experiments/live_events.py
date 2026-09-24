"""Opt-in, line-delimited progress for desktop subprocesses."""

import json
import os

PREFIX = "CHESS_EVENT "


def live_enabled() -> bool:
    return os.environ.get("ADAPTIVE_CHESS_LIVE") == "1"


def emit_event(kind: str, **data) -> None:
    if live_enabled():
        print(PREFIX + json.dumps({"kind": kind, **data}), flush=True)
