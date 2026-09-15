"""Guided training and frozen evaluation with durable, resumable progress."""

import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path

import chess
from PySide6.QtCore import QProcess, QProcessEnvironment, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.experiments.campaign import Campaign
from adaptive_chess.experiments.campaign_tournament import export_campaign, standings
from adaptive_chess.experiments.research import ResearchCampaign, load_campaign
from adaptive_chess.learning.agents import KINDS
from adaptive_chess.ui.experiment_config import get_project_root, writable_root
from adaptive_chess.ui.i18n import tr
from adaptive_chess.ui.move_builder import get_legal_target_squares
from adaptive_chess.ui.widgets.chess_board_widget import ChessBoardWidget


class CampaignWorker(QThread):
    failed = Signal(str)

    def __init__(self, action: Callable[[], object], parent: QWidget) -> None:
        super().__init__(parent)
        self.action = action

    def run(self) -> None:
        try:
            self.action()
        except Exception as error:
            self.failed.emit(str(error))


class CampaignScreen(QWidget):
    def __init__(self, on_back: Callable[[], None]) -> None:
        super().__init__()
        self.campaign: Campaign | None = None
        self._worker: CampaignWorker | None = None
        self._process: QProcess | None = None
        self._error = ""
        self._selected: int | None = None
        self._controls: list[QWidget] = []
        self._waiting_for_reply = False
        self._reply_timer = QTimer(self)
        self._reply_timer.setSingleShot(True)
        self._reply_timer.setInterval(850)
        self._reply_timer.timeout.connect(self._reply)

        self._participant = QLineEdit()
        self._participant.setPlaceholderText("Pseudonim uczestnika")
        self._games = QSpinBox()
        self._games.setRange(1, 1000)
        self._games.setValue(10)
        self._depth = QSpinBox()
        self._depth.setRange(1, 2)
        self._depth.setValue(1)
        self._nodes = QSpinBox()
        self._nodes.setRange(1, 100000)
        self._nodes.setValue(500)
        self._seed = QSpinBox()
        self._seed.setRange(0, 2147483647)
        self._seed.setValue(42)
        self._openings = QLineEdit("; e2e4 e7e5; d2d4 d7d5")
        self._eval_agent = QComboBox()
        self._eval_agent.addItems(list(KINDS))
        self._eval_checkpoint = QSpinBox()
        self._eval_checkpoint.setRange(0, 1000)
        self._limit = QSpinBox()
        self._limit.setRange(20, 1000)
        self._limit.setValue(200)
        self._progress = QLabel("Utwórz kampanię albo wczytaj zapisany plik.")
        self._progress.setWordWrap(True)
        self._status = QLabel(
            "Profil, imitacja, TD i kontrola statyczna. 4X partii treningowych."
        )
        self._status.setWordWrap(True)
        self._board = ChessBoardWidget()
        self._board.setFixedSize(512, 512)
        self._board.square_clicked.connect(self._click_square)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)

        root = QVBoxLayout(self)
        self._pages = QStackedWidget()
        root.addWidget(self._pages)
        self._entry, self._setup, self._play = QWidget(), QWidget(), QWidget()
        for page in (self._entry, self._setup, self._play):
            self._pages.addWidget(page)

        def button(text, action, layout):
            control = QPushButton(text)
            if not text.startswith(("Nowa kampania", "Utwórz", "Rozpocznij")):
                control.setObjectName("SecondaryButton")
            control.clicked.connect(action)
            layout.addWidget(control)
            self._controls.append(control)
            return control

        entry = QVBoxLayout(self._entry)
        entry.addStretch()
        heading = QLabel("Zagraj i trenuj swoich agentów")
        heading.setObjectName("TitleLabel")
        entry.addWidget(heading)
        entry.addWidget(QLabel("Najpierw wybierz nową kampanię albo swój zapis."))
        button(
            "Nowa kampania", lambda: self._pages.setCurrentWidget(self._setup), entry
        )
        button("Wczytaj kampanię…", self._open, entry)
        self._continue = button("Wróć do bieżącej kampanii", self._refresh, entry)
        self._continue.hide()
        button("Powrót do menu", on_back, entry)
        self._entry_message = QLabel()
        self._entry_message.setWordWrap(True)
        entry.addWidget(self._entry_message)
        entry.addStretch()
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for control in self._entry.findChildren(QPushButton):
            control.setMinimumWidth(420)
            control.setMaximumWidth(560)
            entry.setAlignment(control, Qt.AlignmentFlag.AlignHCenter)

        setup = QVBoxLayout(self._setup)
        title = QLabel("Nowa kampania — ustawienia przed grą")
        title.setObjectName("SectionTitle")
        setup.addWidget(title)
        form = QFormLayout()
        setup.addLayout(form)
        for label, widget in (
            ("Twój pseudonim", self._participant),
            ("Partie na każdego z 4 agentów", self._games),
            ("Głębokość", self._depth),
            ("Budżet węzłów / ruch", self._nodes),
            ("Seed", self._seed),
            ("Otwarcia UCI (oddziel ;)", self._openings),
        ):
            form.addRow(label, widget)
            self._controls.append(widget)
        setup.addWidget(
            QLabel(
                "Postęp zapisuje się po każdym ruchu. Kolory zmieniają się co rundę."
            )
        )
        button("Utwórz kampanię i graj…", self._create, setup)
        button("Wstecz", self.show_entry, setup)
        self._setup_message = QLabel()
        self._setup_message.setWordWrap(True)
        setup.addWidget(self._setup_message)
        setup.addStretch()

        play = QVBoxLayout(self._play)
        play.addWidget(self._progress)
        self._result_heading = QLabel()
        self._result_heading.setObjectName("TitleLabel")
        self._result_heading.setWordWrap(True)
        play.addWidget(self._result_heading)
        self._status.setObjectName("StatusLabel")
        play.addWidget(self._status)
        row = QHBoxLayout()
        play.addLayout(row)
        row.addWidget(self._board)
        side = QVBoxLayout()
        row.addLayout(side, 1)
        self._resume_button = button("Rozpocznij / wznów partię", self._resume, side)
        self._resign_button = button("Poddaj partię", self._resign, side)
        self._resign_button.setObjectName("DangerButton")
        tabs = QTabWidget()
        side.addWidget(tabs, 1)
        tabs.addTab(self._log, "Ruchy")
        assessment = QWidget()
        tabs.addTab(assessment, "Ocena i raport")
        assessment_layout = QVBoxLayout(assessment)
        evaluation_form = QFormLayout()
        assessment_layout.addLayout(evaluation_form)
        for label, widget in (
            ("Limit półruchów", self._limit),
            ("Agent kontrolny", self._eval_agent),
            ("Checkpoint", self._eval_checkpoint),
        ):
            evaluation_form.addRow(label, widget)
            self._controls.append(widget)
        button("Oceń checkpointy / turniej", self._tournament, assessment_layout)
        button(
            "Partia kontrolna (bez nauki)", self._human_evaluation, assessment_layout
        )
        button("Eksportuj raport i partie", self._export, assessment_layout)
        self._pause = QPushButton("Zatrzymaj ocenę / turniej")
        self._pause.clicked.connect(self.stop_tournament)
        self._pause.setEnabled(False)
        assessment_layout.addWidget(self._pause)
        assessment_layout.addStretch()
        button("Zapisano automatycznie • Wróć", self.show_entry, side)

    def show_entry(self) -> None:
        if not self.busy:
            self._continue.setVisible(self.campaign is not None)
            self._pages.setCurrentWidget(self._entry)

    def _reply(self) -> None:
        if self.campaign and self.campaign.session:
            self._run(self.campaign.session.continue_bot_turn)

    @property
    def busy(self) -> bool:
        return (
            self._reply_timer.isActive()
            or self._worker is not None
            or (
                self._process is not None
                and self._process.state() != QProcess.ProcessState.NotRunning
            )
        )

    @property
    def thinking(self) -> bool:
        return self._worker is not None or self._reply_timer.isActive()

    def _set_busy(self, busy: bool) -> None:
        for control in self._controls:
            control.setEnabled(not busy)
        self._board.setEnabled(not busy)

    def _create(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Nowa kampania",
            str(writable_root() / "data" / "campaigns"),
            "Kampania (*.sqlite3)",
        )
        if not path:
            return
        if not path.endswith(".sqlite3"):
            path += ".sqlite3"
        try:
            self.campaign = ResearchCampaign.create(
                path,
                self._participant.text(),
                self._games.value(),
                self._depth.value(),
                self._nodes.value(),
                self._seed.value(),
                [value.split() for value in self._openings.text().split(";")],
            )
            self._refresh()
            self._resume()
        except (OSError, ValueError, sqlite3.Error) as error:
            self._setup_message.setText(tr(str(error)))

    def _open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wczytaj kampanię",
            str(writable_root() / "data" / "campaigns"),
            "Kampania (*.sqlite3)",
        )
        if path:
            self.load_campaign(path)
            if self.campaign and (
                self.campaign.data["active"] or not self.campaign.data["completed"]
            ):
                self._resume()

    def load_campaign(self, path: str | Path) -> None:
        try:
            self.campaign = load_campaign(path)
            self._refresh()
        except (OSError, ValueError, KeyError, sqlite3.Error) as error:
            self.campaign = None
            self._entry_message.setText(tr(f"Nie udało się wczytać kampanii: {error}"))

    def _run(self, action: Callable[[], object]) -> None:
        if self.busy:
            return
        self._error = ""
        self._set_busy(True)
        self._status.setText(tr("Bot myśli… Ruchy są zapisywane automatycznie."))
        self._worker = CampaignWorker(action, self)
        self._worker.failed.connect(self._failed)
        self._worker.finished.connect(self._done)
        self._worker.start()

    def _failed(self, message: str) -> None:
        self._error = message

    def _done(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
        self._worker = None
        self._set_busy(False)
        if self._error:
            self._waiting_for_reply = False
            self._status.setText(
                tr(f"Błąd: {self._error}. Wczytaj zapis przed kontynuacją.")
            )
            self.campaign = None
            return
        if (
            self.campaign
            and self.campaign.session
            and self.campaign.session.is_game_over()
        ):
            try:
                self.campaign.finish()
            except (OSError, RuntimeError, sqlite3.Error) as error:
                self._status.setText(tr(str(error)))
                self.campaign = None
                return
        self._refresh()
        if self._waiting_for_reply:
            self._waiting_for_reply = False
            if self.campaign and self.campaign.session:
                self._status.setText(tr("Twój ruch zapisany. Bot za chwilę odpowie…"))
                self._set_busy(True)
                self._reply_timer.start()

    def _resume(self) -> None:
        if self.campaign:
            if self.campaign.training_complete and self.campaign.data["active"] is None:
                self._status.setText(tr("Trening zakończony. Uruchom turniej."))
                return
            self._run(self.campaign.resume)

    def _human_evaluation(self) -> None:
        campaign = self.campaign
        if isinstance(campaign, ResearchCampaign):
            kind, games = self._eval_agent.currentText(), self._eval_checkpoint.value()
            if campaign.data["active"] is not None:
                self._status.setText(tr("Najpierw dokończ aktywną partię."))
                return
            if games >= len(campaign.data["models"][kind]):
                self._status.setText(tr("Ten checkpoint jeszcze nie istnieje."))
                return
            self._run(lambda: campaign.resume_evaluation(kind, games))
        else:
            self._status.setText(
                tr("Utwórz nowe badanie czterech metod, aby grać partie kontrolne.")
            )

    def _resign(self) -> None:
        if not self.campaign or self.campaign.data["active"] is None:
            return
        if (
            QMessageBox.question(
                self, "Poddanie", "Zapisać porażkę i zakończyć partię?"
            )
            == QMessageBox.StandardButton.Yes
        ):
            campaign = self.campaign
            self._run(lambda: campaign.finish(resign=True))

    def _click_square(self, square: int) -> None:
        if self.busy or not self.campaign or not self.campaign.session:
            return
        session = self.campaign.session
        board = session.get_board_copy()
        piece = board.piece_at(square)
        if piece and piece.color == session.human_color:
            self._selected = square
            self._board.set_selected_square(square)
            self._board.set_legal_target_squares(
                get_legal_target_squares(board, square)
            )
            return
        if self._selected is None:
            return
        moves = [
            m
            for m in board.legal_moves
            if m.from_square == self._selected and m.to_square == square
        ]
        if not moves:
            self._status.setText(tr("Nielegalny ruch. Wybierz podświetlone pole."))
            return
        move = moves[0]
        if move.promotion:
            dialog = QMessageBox(self)
            dialog.setWindowTitle(tr("Promocja"))
            dialog.setText(tr("Wybierz figurę"))
            choices = {}
            for name, kind in (
                ("Hetman", chess.QUEEN),
                ("Wieża", chess.ROOK),
                ("Goniec", chess.BISHOP),
                ("Skoczek", chess.KNIGHT),
            ):
                button = dialog.addButton(name, QMessageBox.ButtonRole.AcceptRole)
                choices[button] = kind
            dialog.exec()
            selected = choices.get(dialog.clickedButton())
            if selected is None:
                return
            move = next(m for m in moves if m.promotion == selected)
        self._selected = None
        self._board.clear_highlights()
        self._waiting_for_reply = True
        self._run(lambda: session.play_human_move_uci(move.uci(), defer_bot_reply=True))

    def _refresh(self) -> None:
        if not self.campaign:
            return
        campaign = self.campaign
        self._pages.setCurrentWidget(self._play)
        self._result_heading.clear()
        self._resume_button.setVisible(campaign.session is None)
        self._resign_button.setVisible(campaign.session is not None)
        self._resign_button.setEnabled(campaign.session is not None)
        self._board.setEnabled(campaign.session is not None)
        self._participant.setText(tr(campaign.data["participant"]))
        self._games.setValue(campaign.data["games_per_agent"])
        self._depth.setValue(campaign.data["depth"])
        if isinstance(campaign, ResearchCampaign):
            config = campaign.data["research"]
            self._nodes.setValue(config["nodes"])
            self._seed.setValue(config["seed"])
            self._openings.setText(
                tr("; ".join(" ".join(o) for o in config["openings"]))
            )
            evaluation = campaign.data["evaluations"]
            if evaluation:
                self._limit.setValue(evaluation["limit"])
        self._progress.setText(tr(campaign.progress()))
        self._board.clear_highlights()
        self._selected = None
        if campaign.session:
            session = campaign.session
            self._board.set_flipped(not session.human_color)
            self._board.set_board(session.get_board_copy())
            color = "białymi" if session.human_color else "czarnymi"
            history = session.get_move_history()
            last = history[-1] if history else None
            move_text = ""
            if last:
                who = "Bot" if last.player_type.value == "bot" else "Ty"
                move_text = (
                    f"{who}: {last.san} ({last.move_uci[:2]} → {last.move_uci[2:4]}). "
                )
            turn = (
                "Twój ruch."
                if session.get_turn() == session.human_color
                else "Ruch bota."
            )
            self._status.setText(
                tr(f"{session.bot_name} • Grasz {color}. {move_text}{turn}")
            )
        else:
            records = campaign.data["completed"] + campaign.data.get(
                "human_evaluations", []
            )
            record = (
                max(
                    enumerate(records),
                    key=lambda item: (item[1].get("finished_utc", ""), item[0]),
                )[1]
                if records
                else None
            )
            if record:
                board = chess.Board(campaign.data["initial_fen"])
                for uci in record["moves"]:
                    board.push_uci(uci)
                self._board.set_flipped(not record["human_white"])
                self._board.set_board(board)
                result = record["result"]
                won = result == ("1-0" if record["human_white"] else "0-1")
                heading = (
                    "Remis"
                    if result == "1/2-1/2"
                    else ("Wygrana!" if won else "Przegrana")
                )
                if result == "*":
                    heading = "Partia przerwana"
                self._result_heading.setText(tr(f"{heading} • {result}"))
                reason = (
                    "Poddanie partii"
                    if record["termination"] == "resignation"
                    else "Koniec według reguł szachowych"
                )
                self._status.setText(
                    tr(f"{reason}. Wynik zapisany. Obejrzyj ostatnią pozycję.")
                )
                self._log.setPlainText("\n".join(record["moves"]))
                self._resume_button.setText(tr("Rozpocznij następną partię"))
            else:
                self._board.set_board(chess.Board())
                self._status.setText(tr("Kampania gotowa. Rozpocznij pierwszą partię."))
                self._resume_button.setText(tr("Rozpocznij pierwszą partię"))
            self._resume_button.setEnabled(not campaign.training_complete)
            if campaign.training_complete:
                self._status.setText(
                    tr(
                        self._status.text()
                        + " Trening ukończony — otwórz Ocenę i raport."
                    )
                )
        tournament = campaign.data["tournament"]
        if not tournament and campaign.session:
            history = campaign.session.get_move_history() if campaign.session else ()
            self._log.setPlainText(
                "\n".join(
                    f"{i}. {move.player_type.value}: {move.san}"
                    for i, move in enumerate(history, 1)
                )
            )
        if tournament:
            self._limit.setValue(tournament["max_half_moves"])
            lines = [
                f"Turniej: {len(tournament['results'])}/"
                f"{len(tournament['schedule'])} zapisanych partii."
            ]
            for row in standings(campaign):
                lines.append(
                    f"{row['agent']}: {row['points']} pkt; "
                    f"W/D/L {row['wins']}/{row['draws']}/{row['losses']}; "
                    f"przerwane {row['unfinished']}"
                )
            self._log.setPlainText("\n".join(lines))

    def _tournament(self) -> None:
        if self.busy or not self.campaign:
            return
        if not self.campaign.training_complete and not isinstance(
            self.campaign, ResearchCampaign
        ):
            self._status.setText(tr("Najpierw ukończ trening obu agentów."))
            return
        process = QProcess(self)
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("PYTHONUTF8", "1")
        environment.insert("PYTHONPATH", str(get_project_root() / "src"))
        process.setProcessEnvironment(environment)
        process.setProgram(sys.executable)
        prefix = [] if getattr(sys, "frozen", False) else ["-u", "-m", "adaptive_chess"]
        process.setArguments(
            [
                *prefix,
                "--tournament",
                str(self.campaign.path),
                "--max-half-moves",
                str(self._limit.value()),
            ]
        )
        process.setWorkingDirectory(str(get_project_root()))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.readyReadStandardOutput.connect(self._read_output)
        process.finished.connect(self._tournament_done)
        process.errorOccurred.connect(self._process_error)
        self._process = process
        self._set_busy(True)
        self._pause.setEnabled(True)
        self._status.setText(tr("Turniej zamrożonych agentów. Zapis po każdej partii."))
        process.start()

    def _read_output(self) -> None:
        if self._process:
            output = bytes(self._process.readAllStandardOutput().data())
            self._log.appendPlainText(output.decode("utf-8", errors="replace"))

    def _process_error(self, error) -> None:
        self._status.setText(tr(f"Błąd procesu turnieju: {error}"))
        self._set_busy(False)
        self._pause.setEnabled(False)

    def _tournament_done(self, code: int, status) -> None:
        self._read_output()
        self._set_busy(False)
        self._pause.setEnabled(False)
        if self.campaign:
            self.load_campaign(self.campaign.path)
        self._status.setText(
            tr(
                "Ocena zakończona. Raport zapisany obok kampanii."
                if code == 0
                else "Turniej zatrzymany lub błąd. Możesz wznowić zapisane partie."
            )
        )
        if self._process:
            self._process.deleteLater()
            self._process = None

    def stop_tournament(self) -> None:
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            process = self._process
            process.terminate()
            if not process.waitForFinished(1000):
                process.kill()
                process.waitForFinished(1000)

    def _export(self) -> None:
        if self.campaign:
            try:
                path = export_campaign(self.campaign)
                self._status.setText(tr(f"Zapisano raport: {path}"))
                dialog = QDialog(self)
                dialog.setWindowTitle(tr("Raport badania"))
                dialog.resize(900, 700)
                layout = QVBoxLayout(dialog)
                browser = QTextBrowser()
                from PySide6.QtCore import QUrl

                browser.document().setBaseUrl(QUrl.fromLocalFile(str(path) + "/"))
                browser.setMarkdown((path / "report.md").read_text(encoding="utf-8"))
                layout.addWidget(browser)
                dialog.exec()
            except (OSError, ValueError) as error:
                self._status.setText(tr(str(error)))
