from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QEvent, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QImageReader
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.ui.help_text import help_for
from adaptive_chess.ui.i18n import tr
from adaptive_chess.ui.results_loader import (
    ResultFileInfo,
    read_text_preview,
    summarize_results_folder,
)
from adaptive_chess.ui.widgets.components import (
    Disclosure,
    HelpButton,
    ResponsiveColumns,
    SectionCard,
    StatCard,
    label,
)


class ResultsScreen(QWidget):
    """
    Ekran wyników i raportów.

    Pozwala wczytać folder wyników, podejrzeć raporty tekstowe oraz
    otworzyć pliki wynikowe zewnętrznym programem.
    """

    def __init__(
        self,
        on_back_to_menu_clicked: Callable[[], None],
    ) -> None:
        super().__init__()

        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._loaded_folder: Path | None = None
        self._image_path: Path | None = None

        self._folder_edit = QLineEdit("results/gui_experiments")
        self._status_label = QLabel("Wybierz folder wyników i kliknij „Wczytaj”.")
        self._files_list = QListWidget()
        self._preview = QTextBrowser()
        self._preview.viewport().installEventFilter(self)
        self._enlarge_chart = QPushButton("Powiększ wykres")
        self._enlarge_chart.setObjectName("PrimaryButton")
        self._enlarge_chart.clicked.connect(self._open_chart_preview)
        self._enlarge_chart.hide()
        self._overview = QTextBrowser()
        self._overview.setMinimumHeight(240)
        self._technical = QCheckBox("Pokaż pliki techniczne")
        self._technical.toggled.connect(self._load_results_folder)

        self._load_button = QPushButton("Wczytaj")
        self._browse_button = QPushButton("Wybierz folder")
        self._open_folder_button = QPushButton("Otwórz folder")
        self._open_file_button = QPushButton("Otwórz wybrany plik")

        self._build_ui()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(30, 30, 30, 30)
        root_layout.setSpacing(16)

        header = QHBoxLayout()
        back_button = QPushButton("← Powrót do menu")
        back_button.setObjectName("BackButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)
        header.addWidget(back_button)
        header.addWidget(label("Wyniki i raporty", "PageTitle"), 1)
        header.addWidget(HelpButton("reports"))
        root_layout.addLayout(header)
        root_layout.addWidget(self._build_top_panel())
        self._stats = [
            StatCard(caption)
            for caption in ("Partie", "Wygrane białych", "Wygrane czarnych", "Remisy")
        ]
        root_layout.addWidget(ResponsiveColumns(*self._stats, breakpoint=660))
        chart = SectionCard("Rozkład wyników")
        self._bars = []
        for caption in (
            "Wygrane białych",
            "Wygrane czarnych",
            "Remisy",
            "Przerwane limitem",
        ):
            chart.body.addWidget(label(caption))
            bar = QProgressBar()
            bar.setRange(0, 1)
            bar.setValue(0)
            bar.setFormat("—")
            chart.body.addWidget(bar)
            self._bars.append(bar)
        chart.body.addWidget(
            label(
                "Przerwane partie nie oznaczają remisu ani zwycięstwa. Kolor "
                "dotyczy strony na planszy."
            )
        )
        self._overview.setPlaceholderText("Wczytaj folder, aby zobaczyć statystyki.")
        help_for(self._overview, "reports")
        root_layout.addWidget(ResponsiveColumns(chart, self._overview), 1)
        files = ResponsiveColumns(
            self._build_files_panel(), self._build_preview_panel()
        )
        self._reports_disclosure = Disclosure("Raporty i pliki", files)
        root_layout.addWidget(self._reports_disclosure)

        self.setLayout(root_layout)

    def _build_top_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self._load_button.clicked.connect(self._load_results_folder)

        self._browse_button.setObjectName("SecondaryButton")
        self._browse_button.clicked.connect(self._browse_folder)

        self._open_folder_button.setObjectName("SecondaryButton")
        self._open_folder_button.clicked.connect(self._open_loaded_folder)

        folder_row.addWidget(QLabel("Folder wyników"))
        folder_row.addWidget(self._folder_edit, stretch=1)
        folder_row.addWidget(self._browse_button)
        folder_row.addWidget(self._load_button)
        actions = QHBoxLayout()
        actions.addWidget(self._open_folder_button)
        actions.addStretch()
        self._load_button.setObjectName("PrimaryButton")
        help_for(self._folder_edit, "files")
        help_for(self._technical, "files")

        self._status_label.setObjectName("StatusLabel")
        self._status_label.setWordWrap(True)

        layout.addLayout(folder_row)
        layout.addLayout(actions)
        layout.addWidget(self._status_label)

        panel.setLayout(layout)

        return panel

    def _build_files_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Raporty i wykresy")
        title.setObjectName("SectionTitle")

        self._files_list.itemSelectionChanged.connect(self._show_selected_file_preview)
        self._files_list.itemDoubleClicked.connect(self._open_selected_file)

        self._open_file_button.setObjectName("SecondaryButton")
        self._open_file_button.clicked.connect(self._open_selected_file)

        layout.addWidget(title)
        layout.addWidget(self._technical)
        layout.addWidget(self._files_list, stretch=1)
        layout.addWidget(self._open_file_button)

        panel.setLayout(layout)

        return panel

    def _build_preview_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Podsumowanie")
        title.setObjectName("SectionTitle")

        self._preview.setReadOnly(True)
        self._preview.setPlaceholderText("Wybierz raport lub wykres po lewej stronie.")
        self._preview.setMinimumHeight(240)

        layout.addWidget(title)
        layout.addWidget(self._enlarge_chart)
        layout.addWidget(self._preview, stretch=1)

        panel.setLayout(layout)

        return panel

    def _browse_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Wybierz folder wyników",
            self._folder_edit.text(),
        )

        if selected_folder:
            self._folder_edit.setText(tr(selected_folder))

    def _load_results_folder(self) -> None:
        self._reset_dashboard()
        try:
            summary = summarize_results_folder(self._folder_edit.text())
        except ValueError as error:
            self._status_label.setText(tr(str(error)))
            self._files_list.clear()
            self._preview.clear()
            return

        self._loaded_folder = summary.folder
        self._files_list.clear()
        self._preview.clear()

        if not summary.exists:
            self._status_label.setText(
                tr("Folder nie istnieje: {folder}").format(folder=summary.folder)
            )
            return

        for file_info in summary.files:
            if (
                file_info.path.suffix in (".json", ".txt")
                and not self._technical.isChecked()
            ):
                continue
            item = QListWidgetItem(self._format_file_item(file_info))
            item.setData(256, file_info)
            self._files_list.addItem(item)

        self._status_label.setText(
            tr("Wczytano raporty: {count} plików.").format(count=len(summary.files))
        )

        from adaptive_chess.ui.results_presenter import (
            outcome,
            overview,
            overview_games,
        )

        try:
            games = overview_games(summary.folder)
            captions = (
                "Wygrane białych",
                "Wygrane czarnych",
                "Remisy",
                "Przerwane limitem",
            )
            counts = [
                sum(outcome(game) == tr(caption) for game in games)
                for caption in captions
            ]
            for card, value in zip(self._stats, [len(games), *counts[:3]], strict=True):
                card.set_value(value)
            for bar, count in zip(self._bars, counts, strict=True):
                bar.setRange(0, max(1, len(games)))
                bar.setValue(count)
                bar.setFormat(f"{count} / {len(games)}")
            self._overview.setHtml(overview(summary.folder))
            self._preview.setHtml(overview(summary.folder))
        except (OSError, ValueError, KeyError) as error:
            self._overview.setPlainText(str(error))

    def _reset_dashboard(self) -> None:
        self._image_path = None
        self._enlarge_chart.hide()
        self._loaded_folder = None
        self._overview.clear()
        for card in self._stats:
            card.set_value("—")
        for bar in self._bars:
            bar.setRange(0, 1)
            bar.setValue(0)
            bar.setFormat("—")

    def refresh_translation(self) -> None:
        if self._loaded_folder is not None:
            self._load_results_folder()

    def _show_selected_file_preview(self) -> None:
        self._image_path = None
        self._enlarge_chart.hide()
        file_info = self._get_selected_file_info()

        if file_info is None:
            self._preview.clear()
            return

        from adaptive_chess.ui.results_presenter import file_html, overview

        path = file_info.path
        try:
            self._preview.document().setBaseUrl(
                QUrl.fromLocalFile(str(path.parent) + "/")
            )
            if path.suffix in (".csv", ".json"):
                self._preview.setHtml(file_html(path))
            elif path.name == "suite_summary.md":
                self._preview.setHtml(overview(path.parent))
            elif path.suffix == ".md":
                self._preview.setMarkdown(path.read_text(encoding="utf-8"))
            elif path.suffix == ".png":
                self._image_path = path
                self._enlarge_chart.show()
                self._fit_image()
            else:
                self._preview.setPlainText(read_text_preview(path))
        except (OSError, ValueError, KeyError) as error:
            self._preview.setPlainText(f"Nie udało się wczytać raportu: {error}")

    def _fit_image(self) -> None:
        from html import escape

        if self._image_path is None:
            return
        size = QImageReader(str(self._image_path)).size()
        if size.isEmpty():
            return
        viewport = self._preview.viewport()
        scale = min(
            max(1, viewport.width() - 24) / size.width(),
            max(1, viewport.height() - 24) / size.height(),
            1,
        )
        url = escape(QUrl.fromLocalFile(str(self._image_path)).toString(), quote=True)
        self._preview.setHtml(
            f'<img src="{url}" width="{int(size.width() * scale)}" '
            f'height="{int(size.height() * scale)}">'
        )

    def _open_chart_preview(self) -> None:
        from adaptive_chess.ui.widgets.chart_preview import ChartPreview

        if self._image_path is not None:
            ChartPreview(self._image_path, self).show()

    def eventFilter(self, watched, event) -> bool:
        if watched is self._preview.viewport() and event.type() == QEvent.Type.Resize:
            QTimer.singleShot(0, self._fit_image)
        return super().eventFilter(watched, event)

    def _open_loaded_folder(self) -> None:
        folder = self._loaded_folder

        if folder is None:
            folder = summarize_results_folder(self._folder_edit.text()).folder

        folder.mkdir(parents=True, exist_ok=True)

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder.resolve())))

    def _open_selected_file(self) -> None:
        file_info = self._get_selected_file_info()

        if file_info is None:
            self._status_label.setText(tr("Nie wybrano pliku."))
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_info.path.resolve())))

    def _select_file(self, file_info: ResultFileInfo) -> None:
        for row in range(self._files_list.count()):
            item = self._files_list.item(row)
            item_file_info = item.data(256)

            if item_file_info == file_info:
                self._files_list.setCurrentRow(row)
                return

    def _get_selected_file_info(self) -> ResultFileInfo | None:
        selected_items = self._files_list.selectedItems()

        if not selected_items:
            return None

        file_info = selected_items[0].data(256)

        if isinstance(file_info, ResultFileInfo):
            return file_info

        return None

    def _format_file_item(self, file_info: ResultFileInfo) -> str:
        from adaptive_chess.ui.results_presenter import title

        return f"{title(file_info.path)} · {file_info.path.parent.name}"
