"""Guided training and frozen evaluation with durable, resumable progress."""

import json
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
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.experiments.campaign import Campaign
from adaptive_chess.experiments.campaign_tournament import export_campaign, standings
from adaptive_chess.experiments.live_events import PREFIX
from adaptive_chess.experiments.research import ResearchCampaign, load_campaign
from adaptive_chess.learning.agents import KINDS
from adaptive_chess.ui.experiment_config import get_project_root, writable_root
from adaptive_chess.ui.help_text import HELP, help_for, method_help
from adaptive_chess.ui.i18n import tr
from adaptive_chess.ui.move_builder import get_legal_target_squares
from adaptive_chess.ui.widgets.campaign_dashboard import CampaignDashboard
from adaptive_chess.ui.widgets.chess_board_widget import ChessBoardWidget
from adaptive_chess.ui.widgets.components import (
    BoardArea,
    Disclosure,
    PageStack,
    ResponsiveColumns,
    SectionCard,
    form_layout,
    help_field,
    label,
)


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
    def heightForWidth(self, width: int) -> int:
        current = self._pages.currentWidget()
        return current.layout().minimumHeightForWidth(max(1, width - 32)) + 32

    def minimumSizeHint(self):
        from PySide6.QtCore import QSize

        current = self._pages.currentWidget()
        hint = current.minimumSizeHint()
        return QSize(hint.width() + 32, hint.height() + 32)

    def __init__(self, on_back: Callable[[], None]) -> None:
        super().__init__()
        self.campaign: Campaign | None = None
        self._campaign_path: Path | None = None
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
        self._board.square_clicked.connect(self._click_square)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        navigation_bar = QWidget()
        navigation = QHBoxLayout(navigation_bar)
        navigation.setContentsMargins(0, 0, 0, 0)
        menu = QPushButton("← Powrót do menu")
        menu.setObjectName("BackButton")
        menu.clicked.connect(on_back)
        load = QPushButton("Wczytaj kampanię…")
        load.setObjectName("PrimaryButton")
        load.clicked.connect(self._open)
        navigation.addWidget(menu)
        navigation.addWidget(load)
        navigation.addStretch()
        self._controls.extend([menu, load])
        root.addWidget(navigation_bar)
        self._current_file = label("Nie wybrano zapisu kampanii.")
        self._current_file.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        root.addWidget(self._current_file)
        self._backup_notice = label("")
        self._backup_notice.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._backup_notice.hide()
        root.addWidget(self._backup_notice)
        self._pages = PageStack()
        self._pages.currentChanged.connect(self.updateGeometry)
        root.addWidget(self._pages)
        self._entry, self._setup, self._play = QWidget(), QWidget(), QWidget()
        self._pages.currentChanged.connect(
            lambda: navigation_bar.setVisible(
                self._pages.currentWidget() is not self._entry
            )
        )
        for page in (self._entry, self._setup, self._play):
            self._pages.addWidget(page)
        self._recovery = QWidget()
        self._pages.addWidget(self._recovery)
        recovery_layout = QVBoxLayout(self._recovery)
        recovery_layout.addWidget(
            label("Nie udało się otworzyć lub wznowić kampanii", "PageTitle")
        )
        self._recovery_message = label("", "StatusBadge")
        recovery_layout.addWidget(self._recovery_message)
        self._retry_load = QPushButton("Wczytaj ponownie tę kampanię")
        self._retry_load.setObjectName("PrimaryButton")
        self._retry_load.clicked.connect(self._reload_campaign)
        recovery_layout.addWidget(self._retry_load)
        choose = QPushButton("Wybierz inny zapis…")
        choose.clicked.connect(self._open)
        recovery_layout.addWidget(choose)
        self._controls.extend([self._retry_load, choose])
        self._recovery_details = label("")
        self._recovery_disclosure = Disclosure(
            "Szczegóły błędu", self._recovery_details
        )
        recovery_layout.addWidget(self._recovery_disclosure)
        recovery_layout.addStretch()

        def button(text, action, layout):
            control = QPushButton(text)
            control.setObjectName("PrimaryButton")
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
        button("Powrót do menu", on_back, entry).setObjectName("BackButton")
        self._entry_message = QLabel()
        self._entry_message.setWordWrap(True)
        entry.addWidget(self._entry_message)
        entry.addStretch()
        heading.setAlignment(Qt.AlignmentFlag.AlignLeft)
        heading.setWordWrap(True)
        for control in self._entry.findChildren(QPushButton):
            control.setMaximumWidth(560)
            entry.setAlignment(control, Qt.AlignmentFlag.AlignLeft)

        setup = QVBoxLayout(self._setup)
        setup.setSpacing(16)
        setup.addWidget(label("Nowa kampania — ustawienia przed grą", "PageTitle"))
        basic = SectionCard("Konfiguracja treningu")
        form = form_layout()
        basic.body.addLayout(form)
        for caption, widget in (
            ("Twój pseudonim", self._participant),
            ("Partie na każdego z 4 agentów", self._games),
        ):
            field_label = label(caption)
            field_label.setBuddy(widget)
            if widget is self._games:
                form.addRow(field_label, help_field(widget, "games"))
            else:
                form.addRow(field_label, widget)
            self._controls.append(widget)
        advanced = SectionCard()
        advanced_form = form_layout()
        advanced.body.addLayout(advanced_form)
        for caption, widget, key in (
            ("Głębokość", self._depth, "depth"),
            ("Budżet węzłów / ruch", self._nodes, "nodes"),
            ("Seed", self._seed, "seed"),
            ("Otwarcia UCI (oddziel ;)", self._openings, "openings"),
        ):
            field_label = label(caption)
            field_label.setBuddy(widget)
            help_for(field_label, key)
            help_for(widget, key)
            advanced_form.addRow(field_label, help_field(widget, key))
            self._controls.append(widget)
        basic.body.addWidget(Disclosure("Parametry zaawansowane", advanced))
        self._configuration_summary = label("", "StatusBadge")
        basic.body.addWidget(self._configuration_summary)
        self._budget_summary = label("")
        basic.body.addWidget(self._budget_summary)
        basic.body.addWidget(
            label("Ocena checkpointów i turniej wymagają dodatkowych gier.")
        )
        basic.body.addWidget(
            label("Postęp zapisuje się po każdym ruchu. Kolory zmieniają się co rundę.")
        )
        help_for(self._games, "games")
        methods = SectionCard("Cztery metody")
        for kind in KINDS:
            methods.body.addWidget(label(HELP[kind]))
        methods.body.addStretch()
        setup.addWidget(ResponsiveColumns(basic, methods))
        actions = QHBoxLayout()
        button("Utwórz kampanię i graj…", self._create, actions)
        button("Wstecz", self.show_entry, actions)
        setup.addLayout(actions)
        self._setup_message = label("")
        setup.addWidget(self._setup_message)
        setup.addStretch()
        for widget in (self._games, self._depth, self._nodes, self._seed):
            widget.valueChanged.connect(self.refresh_translation)
        self._eval_agent.currentIndexChanged.connect(self.refresh_translation)
        self.refresh_translation()

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
        row.addWidget(BoardArea(self._board), 3)
        sidebar = QWidget()
        sidebar.setMinimumWidth(290)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(0, 0, 0, 0)
        row.addWidget(sidebar, 2)
        self._resume_button = button("Rozpocznij / wznów partię", self._resume, side)
        self._resign_button = button("Poddaj partię", self._resign, side)
        self._resign_button.setObjectName("DangerButton")
        tabs = QTabWidget()
        self._assessment_tabs = tabs
        side.addWidget(tabs, 1)
        tabs.addTab(self._log, "Ruchy")
        assessment = QWidget()
        assessment_scroll = QScrollArea()
        assessment_scroll.setWidgetResizable(True)
        assessment_scroll.setWidget(assessment)
        tabs.addTab(assessment_scroll, "Ocena i raport")
        assessment_layout = QVBoxLayout(assessment)
        evaluation_form = form_layout()
        evaluation_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        assessment_layout.addLayout(evaluation_form)
        for caption, widget in (
            ("Limit półruchów", self._limit),
            ("Agent kontrolny", self._eval_agent),
            ("Checkpoint", self._eval_checkpoint),
        ):
            key = (
                "limit"
                if widget is self._limit
                else ("checkpoint" if widget is self._eval_checkpoint else "")
            )
            if key:
                evaluation_form.addRow(caption, help_field(widget, key))
            else:
                evaluation_form.addRow(caption, widget)
            self._controls.append(widget)
        help_for(self._limit, "limit")
        help_for(self._eval_checkpoint, "checkpoint")
        assessment_layout.addWidget(label(HELP["checkpoint"]))
        evaluation_button = button(
            "Oceń checkpointy / turniej", self._tournament, assessment_layout
        )
        help_for(evaluation_button, "evaluation")
        control_button = button(
            "Partia kontrolna (bez nauki)", self._human_evaluation, assessment_layout
        )
        help_for(control_button, "control")
        export_button = button(
            "Eksportuj raport i partie", self._export, assessment_layout
        )
        help_for(export_button, "files")
        self._pause = QPushButton("Zatrzymaj ocenę / turniej")
        self._pause.clicked.connect(self.stop_tournament)
        self._pause.setEnabled(False)
        assessment_layout.addWidget(self._pause)
        assessment_layout.addStretch()
        button("Wróć do wyboru kampanii", self.show_entry, side)
        self._dashboard = CampaignDashboard()
        self._dashboard.busy_changed.connect(self._set_busy)
        self._pages.addWidget(self._dashboard)
        self._summary_button = button(
            "Podsumowanie i drabinka AI", self._show_dashboard, side
        )
        self._summary_button.hide()
        actions = QHBoxLayout()
        self._dashboard.layout().addLayout(actions)
        button("Uruchom benchmark", self._tournament, actions)
        button("Eksportuj raport", self._export, actions)
        button("Partia kontrolna / ustawienia oceny", self._show_assessment, actions)
        self._benchmark_stop = QPushButton("Zatrzymaj benchmark")
        self._benchmark_stop.clicked.connect(self.stop_tournament)
        self._benchmark_stop.setEnabled(False)
        actions.addWidget(self._benchmark_stop)
        self._dashboard.escape.activated.connect(self.stop_tournament)
        self._pending_output = ""

    def _show_assessment(self) -> None:
        if not self.busy:
            self._pages.setCurrentWidget(self._play)
            self._assessment_tabs.setCurrentIndex(1)

    def _show_dashboard(self) -> None:
        if isinstance(self.campaign, ResearchCampaign) and not self.busy:
            self._dashboard.load(self.campaign)
            self._pages.setCurrentWidget(self._dashboard)

    def refresh_translation(self) -> None:
        self._configuration_summary.setText(
            tr("{games} partii / metodę \u00d7 4 = {total} partii treningowych").format(
                games=self._games.value(), total=4 * self._games.value()
            )
        )
        self._budget_summary.setText(
            tr("Głębokość {depth} • Węzły / ruch {nodes} • Seed {seed}").format(
                depth=self._depth.value(),
                nodes=self._nodes.value(),
                seed=self._seed.value(),
            )
        )
        method_help(self._eval_agent)

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
            or self._dashboard.busy
            or self._worker is not None
            or (
                self._process is not None
                and self._process.state() != QProcess.ProcessState.NotRunning
            )
        )

    @property
    def thinking(self) -> bool:
        return (
            self._worker is not None
            or self._reply_timer.isActive()
            or self._dashboard.busy
        )

    def _set_busy(self, busy: bool) -> None:
        for control in self._controls:
            control.setEnabled(not busy)
        self._board.setEnabled(not busy)

    def _create(self) -> None:
        if self.busy:
            return
        dialog = QFileDialog(
            self,
            "Nowa kampania",
            str(writable_root() / "data"),
            "Kampania (*.sqlite3)",
        )
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix("sqlite3")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        path = dialog.selectedFiles()[0]
        from adaptive_chess.ui.campaign_files import create_campaign_file

        try:
            campaign, backup = create_campaign_file(
                path,
                overwrite=True,  # Native save dialog confirmed replacement.
                participant=self._participant.text(),
                games=self._games.value(),
                depth=self._depth.value(),
                nodes=self._nodes.value(),
                seed=self._seed.value(),
                openings=[value.split() for value in self._openings.text().split(";")],
            )
            self.campaign = campaign
            self._backup_notice.setVisible(backup is not None)
            self._backup_notice.setText(
                tr("Poprzedni zapis zachowano w: {path}").format(path=backup)
                if backup
                else ""
            )
            self._campaign_path = self.campaign.path
            self._refresh()
            self._resume()
        except (OSError, ValueError, sqlite3.Error) as error:
            self._setup_message.setText(tr(str(error)))

    def _open(self) -> None:
        if self.busy:
            return
        initial = (
            self._campaign_path.parent
            if self._campaign_path
            else writable_root() / "data"
        )
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wczytaj kampanię",
            str(initial),
            "Kampania (*.sqlite3)",
        )
        if path:
            self._load_and_resume(path)

    def _load_and_resume(self, path: str | Path) -> None:
        self.load_campaign(path)
        if self.campaign and (
            self.campaign.data["active"] or not self.campaign.data["completed"]
        ):
            self._resume()

    def _reload_campaign(self) -> None:
        if not self.busy and self._campaign_path is not None:
            self._load_and_resume(self._campaign_path)

    def _show_recovery(self, message: str) -> None:
        self._waiting_for_reply = False
        self._reply_timer.stop()
        self.campaign = None
        self._continue.hide()
        self._board.setEnabled(False)
        self._resume_button.hide()
        self._resign_button.hide()
        self._retry_load.setEnabled(self._campaign_path is not None)
        text = (
            "Ten zapis wymaga zgodnej wersji aplikacji. Zamknij program i uruchom "
            "wersję obsługującą ten zapis. Potem kliknij "
            "„Wczytaj ponownie tę kampanię”. "
            "Samo ponawianie w tej wersji nie usunie błędu."
            if "Zmieniono środowisko" in message
            else "Nie można teraz kontynuować kampanii. Kliknij „Wczytaj ponownie tę "
            "kampanię”, aby spróbować z tego samego pliku, albo „Wybierz inny zapis…”."
        )
        self._recovery_message.setText(tr(text))
        self._recovery_details.setText(message)
        self._recovery_disclosure.toggle.setChecked(False)
        self._status.setText(tr("Nie udało się wznowić kampanii.") + " " + message)
        self._pages.setCurrentWidget(self._recovery)

    def _show_file_path(self) -> None:
        if self._campaign_path is not None:
            self._current_file.setText(
                tr("Plik kampanii: {path}").format(path=self._campaign_path)
            )

    def load_campaign(self, path: str | Path) -> None:
        if self.busy:
            return
        self._backup_notice.clear()
        self._backup_notice.hide()
        self._campaign_path = Path(path).resolve()
        self._show_file_path()
        try:
            self.campaign = load_campaign(path)
            self._refresh()
        except (OSError, ValueError, KeyError, sqlite3.Error) as error:
            self._show_recovery(str(error))

    def _run(self, action: Callable[[], object]) -> None:
        if self.busy:
            return
        self._error = ""
        self._set_busy(True)
        self._status.setText(tr("Bot myśli… Ruchy są zapisywane automatycznie."))
        campaign = self.campaign

        def action_and_finish() -> None:
            action()
            if campaign and campaign.session and campaign.session.is_game_over():
                campaign.finish()

        # Finishing includes model updates and SQLite writes. Keep it in the
        # worker so every failure reaches _failed, including ValueError.
        self._worker = CampaignWorker(action_and_finish, self)
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
            # A move may already be saved (including mate). Show that position
            # before requiring a reload, rather than leaving an obsolete board.
            self._refresh()
            self._show_recovery(self._error)
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
            if self._worker is not None:
                self._status.setText(
                    tr("Wczytywanie partii… Poczekaj na odtworzenie ruchów.")
                )

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
        if session.is_game_over():
            self._status.setText(
                tr("Partia zakończona. Wczytaj zapis, aby odświeżyć wynik.")
            )
            return
        if session.get_turn() != session.human_color:
            self._status.setText(tr("Ruch bota."))
            return
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
                button = dialog.addButton(tr(name), QMessageBox.ButtonRole.AcceptRole)
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
        self._campaign_path = campaign.path
        self._show_file_path()
        self._pages.setCurrentWidget(self._play)
        self._result_heading.clear()
        self._result_heading.hide()
        self._resume_button.setVisible(campaign.session is None)
        self._resign_button.setVisible(campaign.session is not None)
        self._resign_button.setEnabled(campaign.session is not None)
        self._board.setEnabled(campaign.session is not None)
        self._participant.setText(campaign.data["participant"])
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
                    f"{tr(who)}: {last.san} "
                    f"({last.move_uci[:2]} → {last.move_uci[2:4]}). "
                )
            turn = (
                "Twój ruch."
                if session.get_turn() == session.human_color
                else "Ruch bota."
            )
            self._status.setText(
                tr("{agent} • Grasz {color}. {move}{turn}").format(
                    agent=session.bot_name,
                    color=tr(color),
                    move=move_text,
                    turn=tr(turn),
                )
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
            if record and not campaign.data.get("active"):
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
                self._result_heading.setText(f"{tr(heading)} • {result}")
                self._result_heading.show()
                reason = (
                    "Poddanie partii"
                    if record["termination"] == "resignation"
                    else "Koniec według reguł szachowych"
                )
                self._status.setText(
                    tr("{reason}. Wynik zapisany. Obejrzyj ostatnią pozycję.").format(
                        reason=tr(reason)
                    )
                )
                self._log.setPlainText("\n".join(record["moves"]))
                self._resume_button.setText(tr("Rozpocznij następną partię"))
            else:
                active = campaign.data.get("active")
                board = chess.Board(campaign.data["initial_fen"])
                for uci in active["moves"] if active else []:
                    board.push_uci(uci)
                if active:
                    self._board.set_flipped(not active["human_white"])
                self._board.set_board(board)
                self._status.setText(
                    tr("Wczytano zapis. Wznów partię.")
                    if active
                    else tr("Kampania gotowa. Rozpocznij pierwszą partię.")
                )
                self._resume_button.setText(
                    tr("Wznów zapisaną partię")
                    if active
                    else tr("Rozpocznij pierwszą partię")
                )
            self._resume_button.setEnabled(not campaign.training_complete)
            if campaign.training_complete:
                self._status.setText(
                    tr(
                        self._status.text()
                        + tr(" Trening ukończony — otwórz Ocenę i raport.")
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
        completed = (
            isinstance(campaign, ResearchCampaign)
            and campaign.training_complete
            and not campaign.data.get("active")
        )
        self._summary_button.setVisible(completed)
        if completed:
            self._resume_button.hide()
            self._show_dashboard()

    def _tournament(self) -> None:
        if self.busy or not self.campaign:
            return
        if self.campaign.data.get("active"):
            self._status.setText(tr("Najpierw zakończ lub wznów aktywną partię."))
            return
        if not self.campaign.training_complete and not isinstance(
            self.campaign, ResearchCampaign
        ):
            self._status.setText(tr("Najpierw ukończ trening obu agentów."))
            return
        process = QProcess(self)
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("PYTHONUTF8", "1")
        environment.insert("ADAPTIVE_CHESS_LIVE", "1")
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
        self._pending_output = ""
        if isinstance(self.campaign, ResearchCampaign):
            self._dashboard.load(self.campaign)
            self._dashboard.benchmark_live.reset()
            self._dashboard.tabs.setCurrentWidget(self._dashboard.benchmark_live)
            self._pages.setCurrentWidget(self._dashboard)
        self._set_busy(True)
        self._dashboard.arena.setEnabled(False)
        self._dashboard.play.setEnabled(False)
        self._dashboard.shuffle.setEnabled(False)
        self._pause.setEnabled(True)
        self._benchmark_stop.setEnabled(True)
        self._status.setText(tr("Turniej zamrożonych agentów. Zapis po każdej partii."))
        process.start()

    def _read_output(self) -> None:
        if self._process:
            output = bytes(self._process.readAllStandardOutput().data())
            self._pending_output += output.decode("utf-8", errors="replace")
            lines = self._pending_output.split("\n")
            self._pending_output = lines.pop()
            if self._process.state() == QProcess.ProcessState.NotRunning:
                lines.append(self._pending_output)
                self._pending_output = ""
            for line in lines:
                if line.startswith(PREFIX):
                    try:
                        self._dashboard.benchmark_live.accept_event(
                            json.loads(line[len(PREFIX) :])
                        )
                    except (ValueError, KeyError, TypeError):
                        self._log.appendPlainText(line)
                elif line.strip():
                    self._log.appendPlainText(line)
                    self._dashboard.status_message.setText(line)

    def _process_error(self, error) -> None:
        self._status.setText(tr(f"Błąd procesu turnieju: {error}"))
        self._set_busy(False)
        self._pause.setEnabled(False)
        self._benchmark_stop.setEnabled(False)
        self._dashboard.status_message.setText(tr(f"Błąd procesu benchmarku: {error}"))
        self._dashboard.shuffle.setEnabled(True)
        self._dashboard.arena.setEnabled(True)
        self._dashboard._bracket()

    def _tournament_done(self, code: int, status) -> None:
        self._read_output()
        self._set_busy(False)
        self._pause.setEnabled(False)
        self._benchmark_stop.setEnabled(False)
        self._dashboard.shuffle.setEnabled(True)
        self._dashboard.arena.setEnabled(True)
        self._dashboard._bracket()
        if self.campaign:
            self.load_campaign(self.campaign.path)
        self._status.setText(
            tr(
                "Ocena zakończona. Raport zapisany obok kampanii."
                if code == 0
                else "Turniej zatrzymany lub błąd. Możesz wznowić zapisane partie."
            )
        )
        self._dashboard.status_message.setText(self._status.text())
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
