"""Exercise the packaged GUI, legacy CLI and research subprocess outside the repo."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    from adaptive_chess.experiments.research import ResearchCampaign

    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    args = parser.parse_args()
    executable = args.executable.resolve()
    with tempfile.TemporaryDirectory(prefix="adaptive-chess-desktop-") as folder:
        work = Path(folder)
        path = work / "synthetic.sqlite3"
        campaign = ResearchCampaign.create(
            path, "SYNTHETIC_SMOKE_ONLY", games=1, nodes=10, openings=[[]]
        )
        for _ in range(4):
            campaign.resume().play_human_move_uci("e2e4")
            campaign.finish(resign=True)
        commands = [
            ["--smoke"],
            [
                "--script",
                "run_random_series.py",
                "--matches",
                "1",
                "--max-half-moves",
                "2",
                "--output-csv",
                str(work / "legacy.csv"),
            ],
            [
                "--script",
                "run_full_experiment_suite.py",
                "--matches",
                "1",
                "--max-half-moves",
                "2",
                "--depths",
                "1",
                "--output-dir",
                str(work / "suite"),
            ],
            ["--tournament", str(path), "--max-half-moves", "2"],
            ["--tournament", str(path), "--max-half-moves", "2"],
        ]
        for command in commands:
            result = subprocess.run(
                [str(executable), *command],
                cwd=work,
                check=True,
                timeout=90,
                capture_output=True,
                encoding="utf-8",
                errors="strict",
            )
            assert "\ufffd" not in result.stdout + result.stderr
        exported = json.loads(
            (work / "synthetic_report" / "campaign.json").read_text(encoding="utf-8")
        )
        assert len(exported["evaluations"]["results"]) == 16
        assert len(exported["tournament"]["results"]) == 12
        assert exported["models"] == campaign.data["models"]
        assert (work / "legacy.csv").is_file()
        assert (work / "suite" / "suite_summary.md").is_file()
        assert (work / "synthetic_report" / "learning.png").stat().st_size > 1000
        assert (work / "synthetic_report" / "games.pgn").stat().st_size > 100
        print("Desktop smoke passed: GUI, CLI, evaluation, resume and frozen exports.")


if __name__ == "__main__":
    main()
