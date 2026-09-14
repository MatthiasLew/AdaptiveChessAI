"""Guided training and frozen evaluation with durable, resumable progress."""

import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path

import chess
from PySide6.QtCore import QProcess, QProcessEnvironment, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.experiments.campaign import Campaign
from adaptive_chess.experiments.campaign_tournament import export_campaign, standings
from adaptive_chess.ui.experiment_config import get_project_root
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

        self._participant = QLineEdit()
        self._participant.setPlaceholderText("Pseudonim uczestnika")
        self._games = QSpinBox()
        self._games.setRange(1, 1000)
        self._games.setValue(10)
        self._depth = QSpinBox()
        self._depth.setRange(1, 2)
        self._depth.setValue(1)
        self._limit = QSpinBox()
        self._limit.setRange(20, 1000)
        self._limit.setValue(200)
        self._progress = QLabel("Utwórz kampanię albo wczytaj zapisany plik.")
        self._progress.setWordWrap(True)
        self._status = QLabel("Trening: Adaptive oraz Static jako punkt odniesienia.")
        self._status.setWordWrap(True)
        self._board = ChessBoardWidget()
        self._board.setFixedSize(512, 512)
        self._board.square_clicked.connect(self._click_square)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)
        title = QLabel("Kampania badawcza")
        title.setObjectName("SectionTitle")
        root.addWidget(title)
        root.addWidget(self._progress)
        row = QHBoxLayout()
        root.addLayout(row)
        left = QVBoxLayout()
        left.addWidget(self._board)
        left.addWidget(self._status)
        left.addStretch()
        row.addLayout(left)
        panel = QVBoxLayout()
        row.addLayout(panel, 1)
        panel.addWidget(QLabel("Parametry nowej kampanii (zapisane są stałe)"))
        form = QFormLayout()
        panel.addLayout(form)
        for label, widget in (
            ("Uczestnik", self._participant),
            ("Partie na każdego agenta", self._games),
            ("Głębokość (stała w kampanii)", self._depth),
            ("Limit półruchów turnieju", self._limit),
        ):
            form.addRow(label, widget)
            self._controls.append(widget)
        buttons = QGridLayout()
        panel.addLayout(buttons)
        for text, action in (
            ("Nowa kampania…", self._create),
            ("Wczytaj kampanię…", self._open),
            ("Rozpocznij / wznów partię", self._resume),
            ("Poddaj partię", self._resign),
            ("Uruchom / wznów turniej", self._tournament),
            ("Eksportuj raport i partie", self._export),
            ("Powrót do menu", on_back),
        ):
            button = QPushButton(text)
            if text not in ("Rozpocznij / wznów partię", "Uruchom / wznów turniej"):
                button.setObjectName("SecondaryButton")
            if text == "Poddaj partię":
                button.setObjectName("DangerButton")
            button.clicked.connect(action)
            index = buttons.count()
            buttons.addWidget(button, index // 2, index % 2)
            self._controls.append(button)
        self._pause = QPushButton("Zatrzymaj turniej")
        self._pause.clicked.connect(self.stop_tournament)
        self._pause.setEnabled(False)
        self._pause.setObjectName("SecondaryButton")
        buttons.addWidget(self._pause, 3, 1)
        panel.addStretch()
        root.addWidget(self._log, 1)

    @property
    def busy(self) -> bool:
        return self._worker is not None or (
            self._process is not None
            and self._process.state() != QProcess.ProcessState.NotRunning
        )

    @property
    def thinking(self) -> bool:
        return self._worker is not None

    def _set_busy(self, busy: bool) -> None:
        for control in self._controls:
            control.setEnabled(not busy)
        self._board.setEnabled(not busy)

    def _create(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Nowa kampania",
            str(get_project_root() / "data" / "campaigns"),
            "Kampania (*.sqlite3)",
        )
        if not path:
            return
        if not path.endswith(".sqlite3"):
            path += ".sqlite3"
        try:
            self.campaign = Campaign.create(
                path, self._participant.text(), self._games.value(), self._depth.value()
            )
            self._refresh()
        except (OSError, ValueError, sqlite3.Error) as error:
            self._status.setText(str(error))

    def _open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wczytaj kampanię",
            str(get_project_root() / "data" / "campaigns"),
            "Kampania (*.sqlite3)",
        )
        if path:
            self.load_campaign(path)

    def load_campaign(self, path: str | Path) -> None:
        try:
            self.campaign = Campaign(path)
            self._refresh()
        except (OSError, ValueError, KeyError, sqlite3.Error) as error:
            self._status.setText(f"Nie udało się wczytać kampanii: {error}")

    def _run(self, action: Callable[[], object]) -> None:
        if self.busy:
            return
        self._error = ""
        self._set_busy(True)
        self._status.setText("Bot myśli… Ruchy są zapisywane automatycznie.")
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
            self._status.setText(
                f"Błąd: {self._error}. Wczytaj zapis przed kontynuacją."
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
                self._status.setText(str(error))
                self.campaign = None
                return
        self._refresh()

    def _resume(self) -> None:
        if self.campaign:
            if self.campaign.training_complete:
                self._status.setText("Trening zakończony. Uruchom turniej.")
                return
            self._run(self.campaign.resume)

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
            self._status.setText("Nielegalny ruch. Wybierz podświetlone pole.")
            return
        move = moves[0]
        if move.promotion:
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Promocja")
            dialog.setText("Wybierz figurę")
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
        self._run(lambda: session.play_human_move_uci(move.uci()))

    def _refresh(self) -> None:
        if not self.campaign:
            return
        campaign = self.campaign
        self._participant.setText(campaign.data["participant"])
        self._games.setValue(campaign.data["games_per_agent"])
        self._depth.setValue(campaign.data["depth"])
        self._progress.setText(campaign.progress())
        self._board.clear_highlights()
        self._selected = None
        if campaign.session:
            session = campaign.session
            self._board.set_flipped(not session.human_color)
            self._board.set_board(session.get_board_copy())
            color = "białymi" if session.human_color else "czarnymi"
            self._status.setText(
                f"{session.bot_name} | Grasz {color}. Zapisano ruchy: "
                f"{len(session.get_move_history())}."
            )
        else:
            self._board.set_flipped(False)
            self._board.set_board(chess.Board())
            self._status.setText(
                "Trening zakończony — możesz uruchomić turniej."
                if campaign.training_complete
                else "Wybierz Rozpocznij / wznów partię. Postęp jest zapisany."
            )
        tournament = campaign.data["tournament"]
        if not tournament:
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
        if not self.campaign.training_complete:
            self._status.setText("Najpierw ukończ trening obu agentów.")
            return
        process = QProcess(self)
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("PYTHONUTF8", "1")
        process.setProcessEnvironment(environment)
        process.setProgram(sys.executable)
        process.setArguments(
            [
                "-u",
                str(get_project_root() / "scripts" / "run_campaign_tournament.py"),
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
        self._status.setText("Turniej zamrożonych agentów. Zapis po każdej partii.")
        process.start()

    def _read_output(self) -> None:
        if self._process:
            output = bytes(self._process.readAllStandardOutput().data())
            self._log.appendPlainText(output.decode("utf-8", errors="replace"))

    def _process_error(self, error) -> None:
        self._status.setText(f"Błąd procesu turnieju: {error}")
        self._set_busy(False)
        self._pause.setEnabled(False)

    def _tournament_done(self, code: int, status) -> None:
        self._read_output()
        self._set_busy(False)
        self._pause.setEnabled(False)
        if self.campaign:
            self.load_campaign(self.campaign.path)
        self._status.setText(
            "Turniej zakończony. Raport zapisany obok kampanii."
            if code == 0
            else "Turniej zatrzymany lub błąd. Możesz wznowić zapisane partie."
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
                self._status.setText(f"Zapisano raport: {path}")
            except (OSError, ValueError) as error:
                self._status.setText(str(error))
