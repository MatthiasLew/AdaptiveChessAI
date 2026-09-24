"""Explicit desktop overwrite with a backup and monotonically increasing revision."""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from adaptive_chess.experiments.research import ResearchCampaign


def create_campaign_file(
    path: str | Path, *, overwrite: bool = False, **settings
) -> tuple[ResearchCampaign, Path | None]:
    target = Path(path).resolve()
    if not overwrite or not target.exists():
        return ResearchCampaign.create(target, **settings), None

    # Validate every setting and build the complete replacement before touching
    # the existing campaign. The backend's ordinary create remains exclusive.
    with TemporaryDirectory(prefix=".new-campaign-", dir=target.parent) as temp:
        staged = ResearchCampaign.create(Path(temp) / "campaign.sqlite3", **settings)
        with closing(sqlite3.connect(staged.path)) as candidate:
            document = candidate.execute(
                "SELECT document FROM campaign WHERE id=1"
            ).fetchone()[0]
        with closing(sqlite3.connect(target, timeout=10)) as current, current:
            current.execute("BEGIN IMMEDIATE")
            row = current.execute("SELECT revision FROM campaign WHERE id=1").fetchone()
            if row is None:
                raise ValueError("Wybrany plik nie jest zapisem kampanii.")
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            backup_dir = target.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup = backup_dir / f"{target.stem}-{stamp}-{uuid4().hex[:8]}.sqlite3"
            # A second reader can snapshot the old database while our reserved
            # writer lock prevents another app from changing it.
            with (
                closing(
                    sqlite3.connect(target.resolve().as_uri() + "?mode=ro", uri=True)
                ) as reader,
                closing(sqlite3.connect(backup)) as snapshot,
            ):
                reader.backup(snapshot)
            # Do not reset the revision: an old open campaign must fail its next
            # optimistic save rather than write over this newly created study.
            current.execute(
                "UPDATE campaign SET revision=revision+1, document=? WHERE id=1",
                (document,),
            )
    return ResearchCampaign(target), backup
