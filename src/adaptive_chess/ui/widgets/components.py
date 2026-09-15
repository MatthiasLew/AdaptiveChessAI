"""Small presentation components shared by the desktop screens."""

from collections.abc import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QFormLayout,
    QFrame,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.ui.i18n import tr


class HelpButton(QToolButton):
    """Discoverable parameter help, also available on keyboard activation."""

    def __init__(self, key: str) -> None:
        super().__init__()
        from adaptive_chess.ui.help_text import help_for

        self.setText("?")
        self.setAccessibleName(tr("Pomoc dotycząca parametru"))
        help_for(self, key)
        self.clicked.connect(self._show_help)

    def _show_help(self) -> None:
        QToolTip.showText(
            self.mapToGlobal(self.rect().bottomLeft()), self.toolTip(), self
        )


def label(text: str, role: str = "HelperText") -> QLabel:
    result = QLabel(tr(text))
    result.setObjectName(role)
    result.setWordWrap(True)
    result.setTextFormat(Qt.TextFormat.PlainText)
    return result


class SectionCard(QFrame):
    def __init__(self, title: str = "") -> None:
        super().__init__()
        self.setObjectName("SectionCard")
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(18, 18, 18, 18)
        self.body.setSpacing(12)
        if title:
            self.body.addWidget(label(title, "SectionTitle"))


def form_layout() -> QFormLayout:
    form = QFormLayout()
    form.setSpacing(10)
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
    return form


class Disclosure(QWidget):
    """Keyboard-accessible details; hiding never disables or resets values."""

    def __init__(self, title: str, content: QWidget) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.toggle = QToolButton()
        self.toggle.setText(tr(title))
        self.toggle.setCheckable(True)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.toggle)
        layout.addWidget(content)
        content.hide()
        self.content = content
        self.toggle.toggled.connect(self._toggle)

    def _toggle(self, checked: bool) -> None:
        self.content.setVisible(checked)
        self.toggle.setArrowType(
            Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
        )


class ResponsiveColumns(QWidget):
    """Stack columns when the logical width cannot accommodate both."""

    def __init__(self, *widgets: QWidget, breakpoint: int = 760) -> None:
        super().__init__()
        self.breakpoint = breakpoint
        self.row = QBoxLayout(QBoxLayout.Direction.LeftToRight, self)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(16)
        for widget in widgets:
            self.row.addWidget(widget, 1)

    def minimumSizeHint(self) -> QSize:
        # Allow the parent to shrink us enough to reach the stacking breakpoint.
        widths = [
            self.row.itemAt(i).widget().minimumSizeHint().width()
            for i in range(self.row.count())
        ]
        return QSize(max(widths, default=0), self.row.minimumSize().height())

    def resizeEvent(self, event) -> None:
        direction = (
            QBoxLayout.Direction.TopToBottom
            if self.width() < self.breakpoint
            else QBoxLayout.Direction.LeftToRight
        )
        if self.row.direction() != direction:
            self.row.setDirection(direction)
        super().resizeEvent(event)


class BoardArea(QWidget):
    """Center a square board within available space, including compact windows."""

    def __init__(self, board: QWidget) -> None:
        super().__init__()
        self.board = board
        board.setParent(self)
        self.setMinimumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(320, 320)

    def resizeEvent(self, event) -> None:
        side = min(self.width(), self.height())
        self.board.setGeometry((self.width() - side) // 2, 0, side, side)
        super().resizeEvent(event)


class ActionCard(QPushButton):
    def __init__(
        self,
        title: str,
        description: str,
        action: Callable[[], None],
        featured: bool = False,
    ) -> None:
        super().__init__()
        self.setObjectName("ActionCard")
        self.setProperty("featured", featured)
        self.setAccessibleName(tr(title))
        self.setAccessibleDescription(tr(description))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)
        for text, role in ((title, "SectionTitle"), (description, "HelperText")):
            child = label(text, role)
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(child)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(130)
        self.clicked.connect(action)


class StatCard(SectionCard):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("StatCard")
        self.value = label("—", "StatValue")
        self.body.addWidget(self.value)
        self.body.addWidget(label(title))

    def set_value(self, value: int | str) -> None:
        self.value.setText(str(value))


class PageStack(QStackedWidget):
    """Only the active campaign page contributes to the outer scroll size."""

    def __init__(self) -> None:
        super().__init__()
        self.layout().setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.currentChanged.connect(self.updateGeometry)

    def sizeHint(self) -> QSize:
        current = self.currentWidget()
        return current.sizeHint() if current else super().sizeHint()

    def minimumSizeHint(self) -> QSize:
        current = self.currentWidget()
        return current.minimumSizeHint() if current else super().minimumSizeHint()

    def hasHeightForWidth(self) -> bool:
        current = self.currentWidget()
        return current.hasHeightForWidth() if current else False

    def heightForWidth(self, width: int) -> int:
        current = self.currentWidget()
        return current.layout().minimumHeightForWidth(width) if current else -1
