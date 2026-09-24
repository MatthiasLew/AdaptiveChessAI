"""Live ASCII board with browsable moves from the current comparison."""

import chess
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.ui.i18n import tr
from adaptive_chess.ui.results_presenter import bot_name


class LiveMatchView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.games: list[dict] = []
        self.game_count = 0
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(80)
        self._refresh_timer.timeout.connect(self._refresh)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.selector = QComboBox()
        self.selector.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.selector.setMinimumContentsLength(12)
        self.selector.activated.connect(self._browse_game)
        self.follow = QCheckBox(tr("Na żywo"))
        self.follow.setChecked(True)
        self.follow.toggled.connect(self._follow_latest)
        row = QHBoxLayout()
        row.addWidget(self.selector, 1)
        row.addWidget(self.follow)
        layout.addLayout(row)
        self.board = QPlainTextEdit()
        self.board.setObjectName("LiveBoard")
        self.board.setReadOnly(True)
        self.board.setMinimumHeight(255)
        layout.addWidget(self.board)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self._render)
        self.slider.sliderPressed.connect(lambda: self.follow.setChecked(False))
        self.slider.actionTriggered.connect(lambda: self.follow.setChecked(False))
        row = QHBoxLayout()
        for caption, delta in (("← Ruch", -1), ("Ruch →", 1)):
            button = QPushButton(tr(caption))
            button.setAccessibleName(
                tr("Poprzedni ruch" if delta < 0 else "Następny ruch")
            )
            button.clicked.connect(lambda checked=False, d=delta: self._step(d))
            row.addWidget(button)
        row.addWidget(self.slider, 1)
        layout.addLayout(row)
        note = QLabel(
            tr(
                "Ruchy: K król, Q hetman, R wieża, B goniec, N skoczek. "
                "Duże litery na planszy = białe. Bilans materiału nie jest oceną błędu."
            )
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        retention = QLabel(
            tr("Podgląd zachowuje ostatnie 100 partii tego uruchomienia.")
        )
        retention.setWordWrap(True)
        retention.setObjectName("HelperText")
        layout.addWidget(retention)
        self.reset()

    def reset(self) -> None:
        self.games.clear()
        self.game_count = 0
        self._refresh_timer.stop()
        self.selector.clear()
        self.slider.setRange(0, 0)
        self.follow.setChecked(True)
        self.board.setPlainText(tr("Rozpocznij porównanie, aby śledzić ruchy AI."))

    def accept_event(self, event: dict) -> None:
        if event["kind"] == "start":
            # Retain recent games without unbounded growth in long series.
            if len(self.games) == 100:
                self.games.pop(0)
                self.selector.removeItem(0)
            self.games.append({"events": [event], "result": ""})
            self.game_count += 1
            self.selector.addItem(
                f"{self.game_count}. {tr('Białe')}: {bot_name(event['white'])} / "
                f"{tr('Czarne')}: {bot_name(event['black'])}"
            )
        elif self.games:
            if event["kind"] == "move":
                self.games[-1]["events"].append(event)
            elif event["kind"] == "end":
                self.games[-1]["result"] = (
                    (
                        tr("Zatrzymane przez użytkownika")
                        if event.get("reason") == "cancelled"
                        else tr("Przerwane limitem")
                    )
                    if event["result"] == "*"
                    else event["result"]
                )
        if not self._refresh_timer.isActive():
            self._refresh_timer.start()

    def _refresh(self) -> None:
        if self.follow.isChecked():
            self._follow_latest(True)
        elif self.games:
            index = self.selector.currentIndex()
            if 0 <= index < len(self.games):
                self.slider.setMaximum(len(self.games[index]["events"]) - 1)
                self._render()

    def _browse_game(self, index: int) -> None:
        self.follow.setChecked(False)
        self._select(index)

    def _select(self, index: int) -> None:
        if 0 <= index < len(self.games):
            self.selector.setCurrentIndex(index)
            self.slider.setRange(0, len(self.games[index]["events"]) - 1)
            self.slider.setValue(self.slider.maximum())
            self._render()

    def _follow_latest(self, checked: bool) -> None:
        if checked:
            self._select(len(self.games) - 1)

    def _step(self, delta: int) -> None:
        self.follow.setChecked(False)
        self.slider.setValue(self.slider.value() + delta)

    def _render(self) -> None:
        index = self.selector.currentIndex()
        if not 0 <= index < len(self.games):
            return
        game = self.games[index]
        ply = min(self.slider.value(), len(game["events"]) - 1)
        event = game["events"][ply]
        board = chess.Board(event["fen"])
        rows = [f"{8 - i}  {row}" for i, row in enumerate(str(board).splitlines())]
        moves = []
        for move in game["events"][1 : ply + 1]:
            number = (move["ply"] + 1) // 2
            prefix = f"{number}." if move["side"] == "white" else f"{number}..."
            moves.append(f"{prefix} {move['san']} ({move['uci']})")
        self.board.setPlainText(
            (f"{tr('Ostatni ruch')}: {event['san']} ({event['uci']})\n" if ply else "")
            + "\n".join(rows)
            + "\n   a b c d e f g h\n\n"
            + tr("Półruch")
            + f": {ply}/{len(game['events']) - 1}  |  "
            + tr("Bilans białych")
            + f": {event.get('material', 0):+d}\n"
            + (str(game["result"]) + "\n" if game["result"] else "")
            + "  ".join(moves)
        )
