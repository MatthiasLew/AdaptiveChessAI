"""Desktop and subprocess entrypoint, also used by the standalone executable."""

import argparse
import os
import runpy
import sys
from pathlib import Path


def main() -> int:
    # Frozen Python can ignore PYTHONIOENCODING; QProcess decodes UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", line_buffering=True)
    if len(sys.argv) > 2 and sys.argv[1] == "--script":
        os.environ.setdefault("MPLBACKEND", "Agg")
        script_name = sys.argv[2]
        rest = sys.argv[3:]
        from adaptive_chess.ui.experiment_config import get_project_root

        path = get_project_root() / "scripts" / script_name
        if Path(script_name).name != script_name or not path.is_file():
            raise ValueError("Unknown experiment script.")
        sys.argv = [str(path), *rest]
        runpy.run_path(str(path), run_name="__main__")
        return 0
    parser = argparse.ArgumentParser()
    parser.add_argument("--tournament")
    parser.add_argument("--max-half-moves", type=int, default=200)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.tournament:
        from adaptive_chess.experiments.campaign_tournament import run_tournament

        run_tournament(args.tournament, args.max_half_moves)
        return 0
    if args.smoke:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        from adaptive_chess.ui.main_window import MainWindow

        application = QApplication([])
        window = MainWindow()
        window.show()
        application.processEvents()
        window.close()
        return 0
    from adaptive_chess.ui.app import run_gui

    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
