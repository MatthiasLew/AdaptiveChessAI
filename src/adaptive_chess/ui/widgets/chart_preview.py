"""Resizable chart viewer with a native-resolution inspection mode."""

from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.ui.i18n import tr


class ChartPreview(QDialog):
    def __init__(self, path: Path, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Podgląd wykresu"))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._original = QPixmap(str(path))
        self._fit = True
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        for caption, fit in (("Dopasuj do okna", True), ("100%", False)):
            button = QPushButton(tr(caption))
            button.clicked.connect(lambda checked=False, value=fit: self.set_fit(value))
            controls.addWidget(button)
        close = QPushButton(tr("Zamknij"))
        close.clicked.connect(self.close)
        controls.addWidget(close)
        layout.addLayout(controls)
        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picture = QLabel()
        self.scroll.setWidget(self.picture)
        self.scroll.viewport().installEventFilter(self)
        layout.addWidget(self.scroll)
        available = self.screen().availableGeometry()
        self.resize(
            min(1200, available.width() - 60), min(850, available.height() - 80)
        )
        self.set_fit(True)

    def set_fit(self, fit: bool) -> None:
        self._fit = fit
        pixmap = self._original
        if fit:
            pixmap = pixmap.scaled(
                self.scroll.viewport().size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.picture.setPixmap(pixmap)
        self.picture.resize(pixmap.size())

    def eventFilter(self, watched, event) -> bool:
        if (
            watched is self.scroll.viewport()
            and event.type() == QEvent.Type.Resize
            and self._fit
        ):
            QTimer.singleShot(0, lambda: self.set_fit(self._fit))
        return super().eventFilter(watched, event)
