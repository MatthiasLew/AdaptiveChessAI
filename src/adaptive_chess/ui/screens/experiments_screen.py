import sys
from collections.abc import Callable

from PySide6.QtCore import QProcess, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.ui.experiment_config import (
    ExperimentKind,
    ExperimentRunConfig,
    build_experiment_command,
    get_project_root,
    resolve_output_dir,
)


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

        self._experiment_combo = QComboBox()
        self._matches_spinbox = QSpinBox()
        self._max_half_moves_spinbox = QSpinBox()
        self._depth_spinbox = QSpinBox()
        self._output_dir_edit = QLineEdit("results/gui_experiments")

        self._status_label = QLabel("Gotowe do uruchomienia eksperymentu.")
        self._log_output = QPlainTextEdit()

        self._run_button = QPushButton("Uruchom eksperyment")
        self._cancel_button = QPushButton("Anuluj")
        self._open_output_button = QPushButton("Otwórz folder wyników")

        self._build_ui()

    def set_default_output_dir(self, output_dir: str) -> None:
        """
        Ustawia domyślny folder wyników eksperymentów.
        """
        self._output_dir_edit.setText(output_dir)

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(30, 30, 30, 30)
        root_layout.setSpacing(16)

        title = QLabel("Eksperymenty")
        title.setObjectName("SectionTitle")

        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        config_panel = self._build_config_panel()
        log_panel = self._build_log_panel()

        content_layout.addWidget(config_panel, stretch=1)
        content_layout.addWidget(log_panel, stretch=2)

        root_layout.addWidget(title)
        root_layout.addLayout(content_layout, stretch=1)

        self.setLayout(root_layout)

    def _build_config_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QGridLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self._configure_experiment_combo()
        self._configure_spinboxes()
        self._configure_buttons()

        self._status_label.setObjectName("StatusLabel")
        self._status_label.setWordWrap(True)

        layout.addWidget(QLabel("Typ eksperymentu"), 0, 0)
        layout.addWidget(self._experiment_combo, 0, 1)

        layout.addWidget(QLabel("Liczba partii"), 1, 0)
        layout.addWidget(self._matches_spinbox, 1, 1)

        layout.addWidget(QLabel("Limit półruchów"), 2, 0)
        layout.addWidget(self._max_half_moves_spinbox, 2, 1)

        layout.addWidget(QLabel("Depth"), 3, 0)
        layout.addWidget(self._depth_spinbox, 3, 1)

        layout.addWidget(QLabel("Folder wyników"), 4, 0)
        layout.addWidget(self._output_dir_edit, 4, 1)

        layout.addWidget(self._run_button, 5, 0, 1, 2)
        layout.addWidget(self._cancel_button, 6, 0, 1, 2)
        layout.addWidget(self._open_output_button, 7, 0, 1, 2)

        back_button = QPushButton("Powrót do menu")
        back_button.setObjectName("SecondaryButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)
        layout.addWidget(back_button, 8, 0, 1, 2)

        layout.addWidget(QLabel("Status"), 9, 0, 1, 2)
        layout.addWidget(self._status_label, 10, 0, 1, 2)

        panel.setLayout(layout)

        return panel

    def _build_log_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        log_title = QLabel("Log eksperymentu")
        log_title.setObjectName("SectionTitle")

        self._log_output.setReadOnly(True)
        self._log_output.setPlaceholderText("Tutaj pojawi się log działania skryptu.")

        layout.addWidget(log_title)
        layout.addWidget(self._log_output, stretch=1)

        panel.setLayout(layout)

        return panel

    def _configure_experiment_combo(self) -> None:
        self._experiment_combo.addItem(
            "Full suite",
            ExperimentKind.FULL_SUITE.value,
        )
        self._experiment_combo.addItem(
            "RandomBot vs RandomBot",
            ExperimentKind.RANDOM_VS_RANDOM.value,
        )
        self._experiment_combo.addItem(
            "RandomBot vs StaticMinimaxBot",
            ExperimentKind.RANDOM_VS_MINIMAX.value,
        )
        self._experiment_combo.addItem(
            "RandomBot vs AdaptiveMinimaxBot",
            ExperimentKind.RANDOM_VS_ADAPTIVE.value,
        )
        self._experiment_combo.addItem(
            "StaticMinimaxBot vs AdaptiveMinimaxBot",
            ExperimentKind.STATIC_VS_ADAPTIVE.value,
        )

    def _configure_spinboxes(self) -> None:
        self._matches_spinbox.setMinimum(1)
        self._matches_spinbox.setMaximum(10_000)
        self._matches_spinbox.setValue(2)

        self._max_half_moves_spinbox.setMinimum(1)
        self._max_half_moves_spinbox.setMaximum(10_000)
        self._max_half_moves_spinbox.setValue(20)

        self._depth_spinbox.setMinimum(1)
        self._depth_spinbox.setMaximum(4)
        self._depth_spinbox.setValue(1)

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
            self._status_label.setText(str(error))
            return

        self._log_output.clear()
        self._append_log("Start eksperymentu.")
        self._append_log(f"Python: {sys.executable}")
        self._append_log(f"Komenda: {' '.join(command)}")
        self._append_log("")

        process = QProcess(self)
        process.setProgram(sys.executable)
        process.setArguments(command)
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
        self._process.terminate()

    def _read_process_output(self) -> None:
        if self._process is None:
            return

        output = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8",
            errors="replace",
        )

        if output:
            self._append_log(output.rstrip())

    def _on_process_finished(self, exit_code: int, exit_status) -> None:
        self._set_running_state(False)

        if exit_code == 0:
            self._status_label.setText("Eksperyment zakończony poprawnie.")
            self._append_log("")
            self._append_log("Eksperyment zakończony poprawnie.")
            return

        self._status_label.setText(f"Eksperyment zakończony błędem: {exit_code}.")
        self._append_log("")
        self._append_log(f"Eksperyment zakończony błędem: {exit_code}.")
        self._append_log(f"Status procesu: {exit_status}")

    def _on_process_error(self, error) -> None:
        self._set_running_state(False)
        self._status_label.setText(f"Błąd procesu: {error}.")
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
            output_dir=self._output_dir_edit.text().strip(),
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

        if running:
            self._status_label.setText("Eksperyment jest uruchomiony.")
        else:
            self._cancel_button.setEnabled(False)
