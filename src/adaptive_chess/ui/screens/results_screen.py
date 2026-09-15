from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.ui.i18n import tr
from adaptive_chess.ui.results_loader import (
    ResultFileInfo,
    read_text_preview,
    summarize_results_folder,
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

        self._folder_edit = QLineEdit("results/gui_experiments")
        self._status_label = QLabel("Wybierz folder wyników i kliknij „Wczytaj”.")
        self._files_list = QListWidget()
        self._preview = QTextBrowser()
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

        title = QLabel("Wyniki i raporty")
        title.setObjectName("SectionTitle")

        top_panel = self._build_top_panel()

        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        files_panel = self._build_files_panel()
        preview_panel = self._build_preview_panel()

        content_layout.addWidget(files_panel, stretch=1)
        content_layout.addWidget(preview_panel, stretch=2)

        root_layout.addWidget(title)
        root_layout.addWidget(top_panel)
        root_layout.addLayout(content_layout, stretch=1)

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

        back_button = QPushButton("Powrót do menu")
        back_button.setObjectName("SecondaryButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)

        folder_row.addWidget(QLabel("Folder wyników"))
        folder_row.addWidget(self._folder_edit, stretch=1)
        folder_row.addWidget(self._browse_button)
        folder_row.addWidget(self._load_button)
        folder_row.addWidget(self._open_folder_button)
        folder_row.addWidget(back_button)

        self._status_label.setObjectName("StatusLabel")
        self._status_label.setWordWrap(True)

        layout.addLayout(folder_row)
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

        layout.addWidget(title)
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
            self._status_label.setText(tr(f"Folder nie istnieje: {summary.folder}"))
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
            tr(
                f"Wczytano folder: {summary.folder}. "
                f"Liczba plików wynikowych: {len(summary.files)}."
            )
        )

        from adaptive_chess.ui.results_presenter import overview

        try:
            self._preview.setHtml(overview(summary.folder))
        except (OSError, ValueError, KeyError) as error:
            self._preview.setPlainText(str(error))

    def _show_selected_file_preview(self) -> None:
        file_info = self._get_selected_file_info()

        if file_info is None:
            self._preview.clear()
            return

        from html import escape

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
                url = escape(QUrl.fromLocalFile(str(path)).toString(), quote=True)
                self._preview.setHtml(f'<img src="{url}" width="700">')
            else:
                self._preview.setPlainText(read_text_preview(path))
        except (OSError, ValueError, KeyError) as error:
            self._preview.setPlainText(f"Nie udało się wczytać raportu: {error}")

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
