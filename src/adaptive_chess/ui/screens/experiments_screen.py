import codecs
import json
import sys
from collections.abc import Callable

from PySide6.QtCore import QProcess, QProcessEnvironment, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.experiments.live_events import PREFIX
from adaptive_chess.ui.experiment_config import (
    ExperimentKind,
    ExperimentRunConfig,
    build_experiment_command,
    get_project_root,
    resolve_output_dir,
)
from adaptive_chess.ui.help_text import help_for
from adaptive_chess.ui.i18n import tr
from adaptive_chess.ui.widgets.components import (
    HelpButton,
    ResponsiveColumns,
    form_layout,
    label,
)
from adaptive_chess.ui.widgets.live_match import LiveMatchView


class ExperimentsScreen(QWidget):
    """
    Ekran konfiguracji i uruchamiania eksperymentów bot vs bot.
    """

    def __init__(
        self,
        on_back_to_menu_clicked: Callable[[], None],
    ) -> None:
        super().__init__()

        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._process: QProcess | None = None
        self._cancelled = False
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self._pending_output = ""

        self._experiment_combo = QComboBox()
        self._matches_spinbox = QSpinBox()
        self._max_half_moves_spinbox = QSpinBox()
        self._depth_spinbox = QSpinBox()
        self._output_dir_edit = QLineEdit("results/gui_experiments")

        self._status_label = QLabel("Gotowe do rozpoczęcia.")
        self._log_output = QPlainTextEdit()

        self._run_button = QPushButton("Rozpocznij porównanie")
        self._cancel_button = QPushButton("Anuluj")
        self._open_output_button = QPushButton("Otwórz folder wyników")

        self._build_ui()

    def set_default_output_dir(self, output_dir: str) -> None:
        """
        Ustawia domyślny folder wyników eksperymentów.
        """
        self._output_dir_edit.setText(tr(output_dir))

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(30, 30, 30, 30)
        root_layout.setSpacing(16)

        title = QLabel("Porównaj boty")
        title.setObjectName("PageTitle")

        config_panel = self._build_config_panel()
        log_panel = self._build_log_panel()
        content = ResponsiveColumns(config_panel, log_panel, breakpoint=880)

        header = QHBoxLayout()
        back_button = QPushButton("← Powrót do menu")
        back_button.setObjectName("BackButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)
        header.addWidget(back_button)
        header.addWidget(title, 1)
        root_layout.addLayout(header)
        root_layout.addWidget(
            label("Boty zagrają ze sobą automatycznie. Nie musisz wykonywać ruchów.")
        )
        root_layout.addWidget(
            label("Badanie uczenia z Twoich partii rozpoczniesz w Kampanii badawczej.")
        )
        root_layout.addWidget(content, stretch=1)

        self.setLayout(root_layout)

    def _build_config_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        self._configure_experiment_combo()
        self._configure_spinboxes()
        self._configure_buttons()
        form = form_layout()
        for caption, widget, key in (
            ("Co chcesz porównać?", self._experiment_combo, ""),
            ("Liczba partii", self._matches_spinbox, "matches"),
            ("Limit półruchów", self._max_half_moves_spinbox, "limit"),
            ("Poziom przewidywania", self._depth_spinbox, "depth"),
            ("Folder wyników", self._output_dir_edit, "files"),
        ):
            field_label = label(caption)
            field_label.setBuddy(widget)
            if key:
                help_for(widget, key)
                help_for(field_label, key)
                row = QHBoxLayout()
                row.addWidget(widget, 1)
                row.addWidget(HelpButton(key))
                form.addRow(field_label, row)
            else:
                form.addRow(field_label, widget)
        layout.addLayout(form)
        self._comparison_help = label("")
        layout.addWidget(self._comparison_help)
        self._experiment_combo.currentIndexChanged.connect(self.refresh_translation)
        self.refresh_translation()
        self._run_button.setObjectName("PrimaryButton")
        layout.addWidget(self._run_button)
        actions = QHBoxLayout()
        actions.addWidget(self._cancel_button)
        actions.addWidget(self._open_output_button)
        layout.addLayout(actions)
        layout.addStretch()

        panel.setLayout(layout)

        return panel

    def _build_log_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        log_title = QLabel("Przebieg porównania")
        log_title.setObjectName("SectionTitle")

        self._log_output.setReadOnly(True)
        self._log_output.setPlaceholderText("Tutaj pojawi się log działania skryptu.")

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 1)
        self._progress_bar.setValue(0)
        self._report = QTextBrowser()
        self._report.setPlainText(
            "Wybierz porównanie i liczbę partii, a następnie rozpocznij. "
            "Wyniki pojawią się tutaj."
        )
        self._details = QCheckBox("Szczegóły techniczne")
        self._details.toggled.connect(self._log_output.setVisible)
        self._log_output.hide()
        layout.addWidget(log_title)
        self._status_label.setObjectName("StatusBadge")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)
        layout.addWidget(self._progress_bar)
        self._live_view = LiveMatchView()
        self._tabs = QTabWidget()
        self._tabs.addTab(self._live_view, "Partie i ruchy AI")
        self._tabs.addTab(self._report, "Podsumowanie")
        layout.addWidget(self._tabs, 1)
        layout.addWidget(self._details)
        layout.addWidget(self._log_output, stretch=1)

        panel.setLayout(layout)

        return panel

    def refresh_translation(self) -> None:
        descriptions = (
            "Pełny zestaw: cztery porównania botów.",
            "Losowy punkt odniesienia: obie strony wybierają losowe ruchy.",
            "Stałe przeszukiwanie kontra losowe ruchy.",
            "Bot adaptacyjny kontra losowy punkt odniesienia.",
            "Bot adaptacyjny kontra bot ze stałą oceną.",
        )
        description = tr(descriptions[self._experiment_combo.currentIndex()])
        self._comparison_help.setText(description)
        self._experiment_combo.setToolTip(description)

    def _configure_experiment_combo(self) -> None:
        self._experiment_combo.addItem(
            "Wszystkie dostępne porównania",
            ExperimentKind.FULL_SUITE.value,
        )
        self._experiment_combo.addItem(
            "Losowy z losowym",
            ExperimentKind.RANDOM_VS_RANDOM.value,
        )
        self._experiment_combo.addItem(
            "Losowy ze statycznym",
            ExperimentKind.RANDOM_VS_MINIMAX.value,
        )
        self._experiment_combo.addItem(
            "Losowy z adaptacyjnym",
            ExperimentKind.RANDOM_VS_ADAPTIVE.value,
        )
        self._experiment_combo.addItem(
            "Statyczny z adaptacyjnym",
            ExperimentKind.STATIC_VS_ADAPTIVE.value,
        )

    def _configure_spinboxes(self) -> None:
        self._matches_spinbox.setMinimum(1)
        self._matches_spinbox.setMaximum(10_000)
        self._matches_spinbox.setValue(2)

        self._max_half_moves_spinbox.setMinimum(1)
        self._max_half_moves_spinbox.setMaximum(10_000)
        self._max_half_moves_spinbox.setValue(200)

        self._depth_spinbox.setMinimum(1)
        self._depth_spinbox.setMaximum(4)
        self._depth_spinbox.setValue(1)
        self._depth_spinbox.setToolTip("Większa wartość oznacza dłuższe obliczenia.")
        self._max_half_moves_spinbox.setToolTip(
            "Jedna jednostka to ruch jednej strony. Mały limit często "
            "przerywa grę przed rozstrzygnięciem."
        )

    def _configure_buttons(self) -> None:
        self._run_button.clicked.connect(self._start_experiment)

        self._cancel_button.setObjectName("SecondaryButton")
        self._cancel_button.clicked.connect(self._cancel_experiment)
        self._cancel_button.setEnabled(False)

        self._open_output_button.setObjectName("SecondaryButton")
        self._open_output_button.clicked.connect(self._open_output_folder)

    def _start_experiment(self) -> None:
        if self._is_process_running():
            self._append_log("Eksperyment już działa.")
            return

        config = self._read_config()
        experiment_kind = self._experiment_combo.currentData()

        try:
            command = build_experiment_command(
                experiment_kind=experiment_kind,
                config=config,
            )
        except ValueError as error:
            self._status_label.setText(tr(str(error)))
            return

        self._cancelled = False
        self._decoder.reset()
        self._pending_output = ""
        self._live_view.reset()
        self._report.setPlainText(tr("Porównanie trwa…"))
        self._tabs.setCurrentIndex(0)
        self._log_output.clear()
        self._append_log("Start eksperymentu.")
        self._append_log(f"Python: {sys.executable}")
        self._append_log(f"Komenda: {' '.join(command)}")
        self._append_log("")

        process = QProcess(self)
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("PYTHONPATH", str(get_project_root() / "src"))
        environment.insert("MPLBACKEND", "Agg")
        environment.insert("PYTHONUTF8", "1")
        environment.insert("PYTHONIOENCODING", "utf-8")
        environment.insert("PYTHONUNBUFFERED", "1")
        environment.insert("ADAPTIVE_CHESS_LIVE", "1")
        process.setProcessEnvironment(environment)
        process.setProgram(sys.executable)
        from adaptive_chess.ui.experiment_config import script_arguments

        process.setArguments(script_arguments(command))
        process.setWorkingDirectory(str(get_project_root()))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        process.readyReadStandardOutput.connect(self._read_process_output)
        process.finished.connect(self._on_process_finished)
        process.errorOccurred.connect(self._on_process_error)

        self._process = process
        self._set_running_state(True)

        process.start()

    def _cancel_experiment(self) -> None:
        if self._process is None:
            return

        if not self._is_process_running():
            return

        self._append_log("")
        self._append_log("Przerwanie eksperymentu...")
        self._cancelled = True
        self._process.terminate()

    def _read_process_output(self) -> None:
        if self._process is None:
            return

        output = self._decoder.decode(
            bytes(self._process.readAllStandardOutput().data())
        )

        self._consume_output(output)

    def _consume_output(self, output: str, final: bool = False) -> None:
        self._pending_output += output
        lines = self._pending_output.split("\n")
        self._pending_output = lines.pop()
        if final and self._pending_output:
            lines.append(self._pending_output)
            self._pending_output = ""
        for line in lines:
            if line.startswith(PREFIX):
                try:
                    event = json.loads(line[len(PREFIX):])
                    self._live_view.accept_event(event)
                    if event["kind"] == "move":
                        self._status_label.setText(
                            tr("Porównanie trwa…") + f" {tr('Półruch')}: {event['ply']}"
                        )
                except (ValueError, KeyError, TypeError):
                    self._append_log(line)
            else:
                self._append_log(line)

    def _on_process_finished(self, exit_code: int, exit_status) -> None:
        self._read_process_output()
        self._consume_output(self._decoder.decode(b"", final=True), final=True)
        self._set_running_state(False)
        if self._cancelled:
            self._status_label.setText(tr("Porównanie zatrzymane."))
            return

        if exit_code == 0:
            from adaptive_chess.ui.results_presenter import overview

            self._status_label.setText(tr("Porównanie zakończone. Wyniki są gotowe."))
            try:
                self._report.setHtml(
                    overview(resolve_output_dir(self._output_dir_edit.text()))
                )
            except (OSError, ValueError, KeyError) as error:
                self._report.setPlainText(str(error))
            self._append_log("")
            self._append_log("Eksperyment zakończony poprawnie.")
            return

        self._status_label.setText(
            tr("Nie udało się ukończyć porównania. Otwórz szczegóły techniczne.")
        )
        self._append_log("")
        self._append_log(f"Eksperyment zakończony błędem: {exit_code}.")
        self._append_log(f"Status procesu: {exit_status}")

    def _on_process_error(self, error) -> None:
        self._set_running_state(False)
        self._status_label.setText(
            tr("Nie udało się ukończyć porównania. Otwórz szczegóły techniczne.")
        )
        self._append_log(f"Błąd procesu: {error}.")

    def _open_output_folder(self) -> None:
        output_dir = resolve_output_dir(self._output_dir_edit.text())
        output_dir.mkdir(parents=True, exist_ok=True)

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_dir.resolve())))

    def _read_config(self) -> ExperimentRunConfig:
        return ExperimentRunConfig(
            matches=self._matches_spinbox.value(),
            max_half_moves=self._max_half_moves_spinbox.value(),
            depth=self._depth_spinbox.value(),
            output_dir=str(resolve_output_dir(self._output_dir_edit.text().strip()))
            if self._output_dir_edit.text().strip()
            else "",
        )

    def _append_log(self, text: str) -> None:
        self._log_output.appendPlainText(text)

    def _is_process_running(self) -> bool:
        return (
            self._process is not None
            and self._process.state() != QProcess.ProcessState.NotRunning
        )

    def _set_running_state(self, running: bool) -> None:
        self._run_button.setEnabled(not running)
        self._cancel_button.setEnabled(running)

        self._experiment_combo.setEnabled(not running)
        self._matches_spinbox.setEnabled(not running)
        self._max_half_moves_spinbox.setEnabled(not running)
        self._depth_spinbox.setEnabled(not running)
        self._output_dir_edit.setEnabled(not running)

        self._progress_bar.setRange(0, 0 if running else 1)
        self._progress_bar.setValue(0 if running else 1)
        if running:
            self._status_label.setText(tr("Porównanie trwa…"))
        else:
            self._cancel_button.setEnabled(False)
