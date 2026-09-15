"""Render real Qt screens at a specified display size/DPI, without user data.

Run in a fresh process, e.g. python scripts/gui_visual_smoke.py --scale 1.5.
Screenshots and geometry evidence are written under --output.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=float, default=1.5)
    parser.add_argument("--width", type=int, default=1366)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--theme", choices=("dark", "light"), default="dark")
    parser.add_argument("--language", choices=("pl", "en"), default="pl")
    parser.add_argument("--output", type=Path, default=Path(".ai/ux/visual"))
    args = parser.parse_args()
    probe_env = dict(os.environ, QT_SCALE_FACTOR="1")
    probe_env.pop("QT_SCREEN_SCALE_FACTORS", None)
    native_scale = float(
        subprocess.check_output(
            [
                sys.executable,
                "-c",
                "from PySide6.QtWidgets import QApplication; "
                "a=QApplication([]); print(a.primaryScreen().devicePixelRatio())",
            ],
            env=probe_env,
            text=True,
        ).strip()
    )
    os.environ.pop("QT_SCREEN_SCALE_FACTORS", None)
    os.environ["QT_SCALE_FACTOR"] = str(args.scale / native_scale)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QLabel, QTabWidget

    from adaptive_chess.experiments.research import ResearchCampaign
    from adaptive_chess.ui.app_settings import AppSettings, AppSettingsStore
    from adaptive_chess.ui.i18n import localize
    from adaptive_chess.ui.main_window import MainWindow
    from adaptive_chess.ui.navigation import ScreenName
    from adaptive_chess.ui.widgets.components import ActionCard, Disclosure

    app = QApplication([])
    settings = AppSettings(fullscreen=False, theme=args.theme, language=args.language)
    AppSettingsStore.load = lambda self: settings  # type: ignore[method-assign]
    window = MainWindow()
    # Reserve physical pixels for the title bar/taskbar, rather than treating
    # a 1366px display as 1366 logical pixels at 150%.
    window.resize(int(args.width / args.scale), int((args.height - 64) / args.scale))
    window.show()
    args.output.mkdir(parents=True, exist_ok=True)
    evidence = []

    def capture(name: str) -> None:
        localize(window)
        QTest.qWait(50)
        scroll = window._stack.currentWidget()
        scroll.verticalScrollBar().setValue(0)
        QTest.qWait(20)
        pixmap = window.grab()
        assert abs(pixmap.devicePixelRatio() - args.scale) < 0.01
        pixmap.save(str(args.output / (name + ".png")))
        evidence.append(
            {
                "screen": name,
                "logical_size": [window.width(), window.height()],
                "dpr": pixmap.devicePixelRatio(),
                "horizontal_scroll": scroll.horizontalScrollBar().maximum(),
                "vertical_scroll": scroll.verticalScrollBar().maximum(),
            }
        )
        assert scroll.horizontalScrollBar().maximum() == 0, evidence[-1]
        if name in (
            "game",
            "game_active",
            "campaign_play",
            "campaign_evaluation",
            "game_summary_checkmate",
        ):
            assert scroll.verticalScrollBar().maximum() == 0, evidence[-1]
        if scroll.verticalScrollBar().maximum():
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
            QTest.qWait(20)
            window.grab().save(str(args.output / (name + "_bottom.png")))
            scroll.verticalScrollBar().setValue(0)
        for card in window.findChildren(ActionCard):
            if card.isVisible():
                for child in card.findChildren(QLabel):
                    assert child.height() >= child.fontMetrics().height(), name

    with TemporaryDirectory(prefix="chess-ux-") as directory:
        folder = Path(directory)
        with (folder / "demo.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=[
                    "result",
                    "white_bot_name",
                    "black_bot_name",
                    "half_moves",
                    "reached_move_limit",
                ],
            )
            writer.writeheader()
            for result in ("1-0", "0-1", "1/2-1/2", "*"):
                writer.writerow(
                    {
                        "result": result,
                        "white_bot_name": "StaticMinimaxBot",
                        "black_bot_name": "AdaptiveMinimaxBot",
                        "half_moves": 20,
                        "reached_move_limit": result == "*",
                    }
                )
        for screen in ScreenName:
            window.show_screen(screen)
            if screen == ScreenName.RESULTS:
                results = window._stack.currentWidget().widget()
                results._folder_edit.setText(str(folder))
                results._load_results_folder()
            capture(screen.value)
        window.show_screen(ScreenName.CAMPAIGN)
        campaign = window._campaign_screen
        campaign._pages.setCurrentWidget(campaign._setup)
        capture("campaign_setup")
        for detail in campaign._setup.findChildren(Disclosure):
            detail.toggle.setChecked(True)
        capture("campaign_advanced")
        model = ResearchCampaign.create(
            folder / "demo.sqlite3", "UX demo", games=1, nodes=10, openings=[[]]
        )
        model.resume()
        campaign.campaign = model
        campaign._refresh()
        capture("campaign_play")
        campaign._play.findChild(QTabWidget).setCurrentIndex(1)
        capture("campaign_evaluation")
        window.show_screen(ScreenName.GAME)
        game = window._game_screen
        assert game is not None
        game._start_new_game()
        game._on_board_square_clicked(__import__("chess").E2)
        capture("game_active")
        game._finish_current_game()
        capture("game_summary_populated")
        import chess

        from adaptive_chess.play.human_vs_bot_session import (
            HumanVsBotGameSummary,
            PlayedMove,
            PlayerType,
        )

        board = chess.Board()
        history = []
        for uci in ("f2f3", "e7e5", "g2g4", "d8h4"):
            move = chess.Move.from_uci(uci)
            history.append(
                PlayedMove(
                    PlayerType.HUMAN if board.turn == chess.WHITE else PlayerType.BOT,
                    board.turn,
                    uci,
                    board.san(move),
                )
            )
            board.push(move)
        window.show_game_summary(
            HumanVsBotGameSummary(
                bot_name="RandomBot",
                human_color=chess.WHITE,
                bot_color=chess.BLACK,
                result="0-1",
                status_message="Mat. Wygrywają czarne.",
                final_fen=board.fen(),
                half_moves=4,
                final_material_balance=0,
                move_history=tuple(history),
            )
        )
        capture("game_summary_checkmate")
        assert window._game_summary_screen is not None
        for detail in window._game_summary_screen.findChildren(Disclosure):
            detail.toggle.setChecked(True)
        capture("game_summary_details")
    (args.output / "geometry.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )
    window.close()
    app.processEvents()
    print(f"{len(evidence)} views OK: {args.output}")


if __name__ == "__main__":
    main()
