"""Post-training review and an explicitly separate spectator bracket."""

import json
import random
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from threading import Event
from uuid import uuid4

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.analysis.game_review import review_game
from adaptive_chess.analysis.research_report import learning_rows, score
from adaptive_chess.experiments.arena import spectator_match
from adaptive_chess.experiments.campaign import (
    environment_compatible,
    environment_metadata,
)
from adaptive_chess.experiments.campaign_tournament import standings
from adaptive_chess.experiments.research import ResearchCampaign
from adaptive_chess.ui.widgets.components import ResponsiveColumns
from adaptive_chess.ui.widgets.live_match import LiveMatchView


class ArenaWorker(QThread):
    event = Signal(dict)

    def __init__(self, campaign, white, black, limit, delay, parent):
        super().__init__(parent)
        self.args = campaign, white, black, limit, delay
        self.cancel = Event()
        self.result = None
        self.error = ""

    def run(self):
        try:
            self.result = spectator_match(*self.args, self.cancel, self.event.emit)
        except Exception as error:
            self.error = str(error)


class CampaignDashboard(QWidget):
    busy_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.campaign = None
        self.worker = None
        self.records: list[dict] = []
        self.winners: list[int] = []
        self.points: list[dict] = []
        self.path = None
        self.manifest = None
        root = QVBoxLayout(self)
        title = QLabel("Wyniki kampanii i arena AI")
        title.setObjectName("TitleLabel")
        root.addWidget(title)
        self.status_message = QLabel()
        self.status_message.setWordWrap(True)
        root.addWidget(self.status_message)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)
        self.summary = QTextBrowser()
        self.tabs.addTab(self.summary, "Podsumowanie i błędy")
        arena = QWidget()
        self.arena = arena
        self.tabs.addTab(arena, "Drabinka • oglądaj AI")
        arena_layout = QVBoxLayout(arena)
        settings = QWidget()
        layout = QVBoxLayout(settings)
        layout.setContentsMargins(0, 0, 0, 0)
        note = QLabel(
            "Pokaz: 2 półfinały → finał. Wybierz modele i kliknij Graj. "
            "Przy remisie lub limicie awans jest losowany "
            "(wynik partii pozostaje bez zmian). Modele nie uczą się podczas pokazu."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        grid = QGridLayout()
        layout.addLayout(grid)
        self.slots = [QComboBox() for _ in range(4)]
        for i, selector in enumerate(self.slots):
            grid.addWidget(
                QLabel(
                    f"Półfinał {i // 2 + 1} • " + ("białe" if i % 2 == 0 else "czarne")
                ),
                i,
                0,
            )
            grid.addWidget(selector, i, 1)
        self.bracket = QLabel()
        self.bracket.setWordWrap(True)
        self.bracket.setObjectName("StatusBadge")
        layout.addWidget(self.bracket)
        controls = QGridLayout()
        layout.addLayout(controls)
        self.shuffle = QPushButton("Losuj nową drabinkę")
        self.shuffle.clicked.connect(self.randomize)
        controls.addWidget(self.shuffle, 0, 0, 1, 2)
        self.limit = QSpinBox()
        self.limit.setRange(20, 1000)
        self.limit.setValue(200)
        controls.addWidget(QLabel("Limit półruchów"), 1, 0)
        controls.addWidget(self.limit, 1, 1)
        self.pace = QComboBox()
        for caption, delay in (
            ("Szybko • 0,1 s", 0.1),
            ("Spokojnie • 0,6 s", 0.6),
            ("Wolno • 1,5 s", 1.5),
        ):
            self.pace.addItem(caption, delay)
        self.pace.setCurrentIndex(1)
        controls.addWidget(QLabel("Tempo oglądania"), 2, 0)
        controls.addWidget(self.pace, 2, 1)
        self.play = QPushButton("Graj półfinał 1")
        self.play.setObjectName("PrimaryButton")
        self.play.clicked.connect(self.start_match)
        self.stop = QPushButton("Zatrzymaj mecz • Esc")
        self.stop.clicked.connect(self.cancel)
        self.stop.setEnabled(False)
        controls.addWidget(self.play, 3, 0)
        controls.addWidget(self.stop, 3, 1)
        self.restore_button = QPushButton("Wczytaj zapisaną drabinkę…")
        self.restore_button.clicked.connect(self.open_bracket)
        layout.addWidget(self.restore_button)
        self.status = QLabel("Wybierz uczestników lub wylosuj pary.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.live = LiveMatchView()
        arena_layout.addWidget(ResponsiveColumns(settings, self.live, breakpoint=1000))
        self.match_summary = QLabel()
        self.match_summary.setWordWrap(True)
        layout.addWidget(self.match_summary)
        layout.addStretch()
        self.benchmark = QTextBrowser()
        self.tabs.addTab(self.benchmark, "Benchmark • wyniki")
        self.benchmark_live = LiveMatchView()
        self.tabs.addTab(self.benchmark_live, "Benchmark • na żywo")
        self.replays = LiveMatchView()
        self.tabs.addTab(self.replays, "Powtórki treningu")
        self.escape = QShortcut(QKeySequence("Escape"), self)
        self.escape.activated.connect(self.cancel)

    @property
    def busy(self):
        return self.worker is not None

    def load(self, campaign: ResearchCampaign):
        if self.busy:
            return
        changed = (
            self.campaign is None
            or self.campaign.data["id"] != campaign.data["id"]
            or (
                not self.records
                and {p["hash"] for p in self.points}
                != {
                    p["hash"]
                    for history in campaign.data["models"].values()
                    for p in history
                }
            )
        )
        self.campaign = campaign
        self._summary()
        if changed:
            self.points = [
                p for history in campaign.data["models"].values() for p in history
            ]
            for selector in self.slots:
                selector.clear()
                for point in self.points:
                    selector.addItem(f"{point['kind']} • treningi: {point['games']}")
            self.randomize()

    def _summary(self):
        campaign = self.campaign
        if campaign is None:
            return
        rows = [
            "<h2>Trening zakończony</h2>"
            if campaign.training_complete
            else "<h2>Dotychczasowe wyniki treningu</h2>",
            "<p>Wyniki z zapisanych partii. W zakładce Drabinka wybierzesz AI "
            "i obejrzysz ich spotkania. Benchmark pokazuje osobno "
            "kontrolowane porównania.</p>",
            "<table cellpadding='8'><tr><th>AI</th><th>Wynik AI</th><th>Ruchy</th>"
            "<th>Największa przewaga AI</th><th>Śr. czas / ruch AI</th></tr>",
        ]
        details = []
        self.replays.reset()
        for number, game in enumerate(campaign.data["completed"], 1):
            review = review_game(game["moves"], campaign.data["initial_fen"])
            self.replays.accept_event(
                {
                    "kind": "start",
                    "fen": campaign.data["initial_fen"],
                    "white": "Gracz" if game["human_white"] else game["agent"],
                    "black": game["agent"] if game["human_white"] else "Gracz",
                }
            )
            for event in review["events"]:
                self.replays.accept_event(event)
            self.replays.accept_event({"kind": "end", "result": game["result"]})
            sign = -1 if game["human_white"] else 1
            balances = [e["material"] * sign for e in review["events"]]
            peak = max([0, *balances])
            peak_ply = balances.index(peak) + 1 if peak > 0 else None
            value = score(game["result"], not game["human_white"])
            outcome = {
                1.0: "Wygrana",
                0.0: "Przegrana",
                0.5: "Remis",
                None: "Przerwana",
            }[value]
            metrics = [m for m in game.get("move_metrics", []) if m["actor"] == "bot"]
            seconds = (
                sum(m["seconds"] for m in metrics) / len(metrics) if metrics else 0
            )
            advantage = (
                f"+{peak} • półruch {peak_ply}"
                if peak_ply
                else "Brak przewagi materiału"
            )
            rows.append(
                f"<tr><td>{number}. {escape(game['agent'])}</td><td>{outcome} "
                f"({game['result']})</td><td>{len(game['moves'])}</td>"
                f"<td>{advantage}</td><td>{seconds:.3f} s</td></tr>"
            )
            details.append(f"<h3>Partia {number} • {escape(game['agent'])}</h3>")
            missed = review["missed_mates"]
            if missed:
                for item in missed:
                    is_ai = (item["side"] == "white") != game["human_white"]
                    who = "AI" if is_ai else "Gracz"
                    details.append(
                        f"<p>{who}, półruch {item['ply']}: pominięty mat w 1. "
                        f"Zagrano {item['played']}; matował {item['mate']}.</p>"
                    )
            else:
                details.append("<p>Nie wykryto pominiętego mata w 1.</p>")
            for item in review["captures"][:8]:
                details.append(
                    f"<p>Półruch {item['ply']} ({item['san']}): zmiana bilansu "
                    f"białych {item['change']:+d} pkt materiału.</p>"
                )
        rows.append(
            "</table><p>Materiał: pion=1, skoczek/goniec=3, wieża=5, hetman=9. "
            "Przewaga materiału nie gwarantuje wygranej. Zmiana po biciu może być "
            "wymianą lub poświęceniem. Wykrywamy pewne pominięte maty w 1; "
            "nie jest to pełna analiza błędów ani ocena silnikiem.</p>"
        )
        self.summary.setHtml("".join(rows + details))
        benchmark = [
            "<h2>Benchmark zamrożonych modeli</h2><p>Ten sam budżet obliczeń, "
            "sparowane otwarcia i zamiana kolorów; rywal: model static przed nauką. "
            "Punkty: wygrana 1, remis ½, porażka 0. Wynik obejmuje wyłącznie "
            "kompletne pary; limity są raportowane osobno.</p>"
        ]
        measured = [r for r in learning_rows(campaign) if r["evaluated_games"]]
        if not measured:
            benchmark.append(
                "<h3>Jeszcze nie wykonano benchmarku</h3><p>Użyj przycisku "
                "Uruchom benchmark. Pokażemy ruchy i postęp na żywo.</p>"
            )
        else:
            benchmark.append(
                "<table cellpadding='8'><tr><th>AI / treningi</th><th>Pary</th>"
                "<th>Wynik punktowy</th><th>Zmiana od początku</th><th>Limity</th></tr>"
            )
            for row in measured:
                mean = (
                    f"{row['score']:.1%}"
                    if row["score"] is not None
                    else "Brak pełnej pary"
                )
                gain = (
                    f"{row['gain'] * 100:+.1f} pp" if row["gain"] is not None else "—"
                )
                benchmark.append(
                    f"<tr><td>{row['agent']} / {row['training_games']}</td>"
                    f"<td>{row['complete_pairs']}</td><td>{mean}</td>"
                    f"<td>{gain}</td><td>{row['unfinished']}</td></tr>"
                )
            benchmark.append(
                "</table><p>Mała liczba par nie wystarcza do wniosku o sile AI. "
                "Pełne dane i przedziały niepewności są w eksporcie raportu.</p>"
            )
        self.benchmark.setHtml("".join(benchmark))
        tournament = campaign.data.get("tournament")
        if tournament:
            benchmark.append(
                "<h3>Turniej badawczy • każdy z każdym</h3>"
                "<table cellpadding='8'><tr><th>AI</th><th>Punkty</th>"
                "<th>Wygrane / remisy / porażki</th><th>Limity</th></tr>"
            )
            for row in standings(campaign):
                benchmark.append(
                    f"<tr><td>{row['agent']}</td><td>{row['points']}</td>"
                    f"<td>{row['wins']} / {row['draws']} / {row['losses']}</td>"
                    f"<td>{row['unfinished']}</td></tr>"
                )
            benchmark.append("</table>")
            self.benchmark.setHtml("".join(benchmark))

    def randomize(self):
        if self.busy or not self.campaign:
            return
        latest = [history[-1] for history in self.campaign.data["models"].values()]
        random.SystemRandom().shuffle(latest)
        for selector, point in zip(self.slots, latest, strict=True):
            selector.setCurrentIndex(self.points.index(point))
            selector.setEnabled(True)
        self.records, self.winners = [], []
        self.path = None
        self.live.reset()
        self.match_summary.clear()
        self.limit.setEnabled(True)
        self._bracket()

    def _name(self, slot):
        return self.slots[slot].currentText()

    def _bracket(self):
        first = self._name(self.winners[0]) if self.winners else "Zwycięzca półfinału 1"
        second = (
            self._name(self.winners[1])
            if len(self.winners) > 1
            else "Zwycięzca półfinału 2"
        )
        text = (
            f"Półfinał 1 → {first}\nPółfinał 2 → {second}\nFinał: {first} vs {second}"
        )
        if len(self.winners) == 3:
            text += f"\nZwycięzca drabinki: {self._name(self.winners[2])}"
        self.bracket.setText(text)
        captions = [
            "Graj półfinał 1",
            "Graj półfinał 2",
            "Graj finał",
            "Drabinka zakończona",
        ]
        self.play.setText(captions[len(self.winners)])
        self.play.setEnabled(len(self.winners) < 3 and not self.busy)

    def start_match(self):
        if (
            self.busy
            or not self.campaign
            or len(self.winners) == 3
            or not self.arena.isEnabled()
        ):
            return
        if self.path is None:
            self.path = self.campaign.path.with_name(
                f"{self.campaign.path.stem}_arena_{uuid4().hex[:8]}.json"
            )
            self.manifest = environment_metadata()
        index = len(self.winners)
        self.pair = (
            (0, 1) if index == 0 else (2, 3) if index == 1 else tuple(self.winners[:2])
        )
        white, black = [self.points[self.slots[s].currentIndex()] for s in self.pair]
        self.worker = ArenaWorker(
            self.campaign,
            white,
            black,
            self.limit.value(),
            self.pace.currentData(),
            self,
        )
        self.worker.event.connect(self._event)
        self.worker.finished.connect(self._finished)
        for widget in [
            *self.slots,
            self.shuffle,
            self.play,
            self.limit,
            self.pace,
            self.restore_button,
        ]:
            widget.setEnabled(False)
        self.stop.setEnabled(True)
        self.status.setText(
            f"{self._name(self.pair[0])} vs {self._name(self.pair[1])} • start"
        )
        self.busy_changed.emit(True)
        self.worker.start()

    def _event(self, event):
        self.live.accept_event(event)
        if event["kind"] == "move":
            self.status.setText(
                f"Półruch {event['ply']}/{self.limit.value()} • {event['san']} • "
                f"bilans białych {event['material']:+d} • "
                f"{event['nodes']} węzłów • {event['seconds']:.3f} s"
            )

    def cancel(self):
        if self.worker:
            self.worker.cancel.set()
            self.status.setText("Zatrzymywanie po bieżącym obliczeniu ruchu…")

    def _finished(self):
        worker, self.worker = self.worker, None
        if worker is None:
            return
        self.stop.setEnabled(False)
        self.shuffle.setEnabled(True)
        self.pace.setEnabled(True)
        self.restore_button.setEnabled(True)
        self.busy_changed.emit(False)
        if worker.error:
            self.status.setText(
                f"Błąd meczu: {worker.error}. Możesz spróbować ponownie."
            )
        elif worker.result:
            record = worker.result
            record["slots"] = list(self.pair)
            record["round"] = len(self.winners)
            if record["termination"] == "cancelled":
                self.status.setText(
                    "Mecz zatrzymany. Graj rozpocznie tę parę od początku."
                )
            else:
                drawn = record["result"] in ("*", "1/2-1/2")
                winner = (
                    random.SystemRandom().choice(self.pair)
                    if drawn
                    else self.pair[0 if record["result"] == "1-0" else 1]
                )
                self.winners.append(winner)
                record["advances"] = winner
                record["advancement"] = "draw_lots" if drawn else "game_result"
                reason = " • awans przez losowanie" if drawn else " • awans za wygraną"
                self.status.setText(
                    f"Wynik: {record['result']} ({record['termination']}){reason}: "
                    f"{self._name(winner)}"
                )
            self.records.append(record)
            review = review_game(record["moves"])
            misses = review["missed_mates"]
            detail = "; ".join(
                f"{m['ply']}. {m['played']} zamiast {m['mate']}" for m in misses[:4]
            )
            self.match_summary.setText(
                f"{len(record['moves'])} półruchów • pominięte maty w 1: "
                f"{len(misses)}. {detail}\nZapis: {self.path}"
            )
            self._save()
        worker.deleteLater()
        self._bracket()

    def _save(self):
        if self.campaign is None or self.path is None:
            return
        document = {
            "format": "spectator_bracket_v1",
            "campaign_id": self.campaign.data["id"],
            "environment": self.manifest,
            "saved_utc": datetime.now(timezone.utc).isoformat(),
            "entrants": [self.points[s.currentIndex()] for s in self.slots],
            "limit": self.limit.value(),
            "results": self.records,
            "winners": self.winners,
            "tie_rule": "draw_lots",
            "depth": self.campaign.data["depth"],
            "nodes": self.campaign.data["research"]["nodes"],
            "seed": self.campaign.data["research"]["seed"],
            "purpose": "demonstration_not_research_benchmark",
        }
        try:
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            temporary.replace(self.path)
        except OSError as error:
            self.status.setText(f"Wynik w pamięci, ale zapis nie powiódł się: {error}")

    def open_bracket(self):
        if self.busy or self.campaign is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wczytaj drabinkę tej kampanii",
            str(self.campaign.path.parent),
            "Drabinka AI (*_arena_*.json)",
        )
        if path:
            try:
                self.restore(Path(path))
            except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
                self.status.setText(f"Nie wczytano drabinki: {error}")

    def restore(self, path: Path):
        if self.busy or self.campaign is None:
            return
        document = json.loads(path.read_text(encoding="utf-8"))
        if (
            document["format"] != "spectator_bracket_v1"
            or document["campaign_id"] != self.campaign.data["id"]
        ):
            raise ValueError("Wybierz drabinkę zapisaną dla tej kampanii.")
        if not environment_compatible(document["environment"]):
            raise ValueError(
                "Zapis pochodzi z innej wersji aplikacji. "
                "Uruchom ją, aby kontynuować te same warunki gry."
            )
        if any(
            document[key]
            != (
                self.campaign.data["depth"]
                if key == "depth"
                else self.campaign.data["research"][key]
            )
            for key in ("depth", "nodes", "seed")
        ):
            raise ValueError("Zapis ma inny budżet obliczeń lub seed.")
        indices = []
        for point in document["entrants"]:
            indices.append(self.points.index(point))
        if len(indices) != 4 or not 20 <= document["limit"] <= 1000:
            raise ValueError("Nieprawidłowi uczestnicy lub limit.")
        winners: list[int] = []
        # Validate all moves and advancement before replacing the visible bracket.
        for record in document["results"]:
            pair = (
                [0, 1]
                if len(winners) == 0
                else [2, 3]
                if len(winners) == 1
                else winners[:2]
            )
            if len(winners) >= 3 or record["slots"] != pair:
                raise ValueError("Nieprawidłowa kolejność meczów.")
            if review_game(record["moves"])["final_fen"] != record["final_fen"]:
                raise ValueError("Niezgodna pozycja końcowa meczu.")
            if record["termination"] != "cancelled":
                winner = record["advances"]
                if winner not in pair:
                    raise ValueError("Nieprawidłowy awans.")
                if record["result"] in ("1-0", "0-1"):
                    expected = pair[0 if record["result"] == "1-0" else 1]
                    if winner != expected:
                        raise ValueError("Awans nie odpowiada wynikowi partii.")
                winners.append(winner)
        if winners != document["winners"]:
            raise ValueError("Niezgodne wyniki drabinki.")
        for selector, index in zip(self.slots, indices, strict=True):
            selector.setCurrentIndex(index)
            selector.setEnabled(False)
        self.path, self.manifest = path, document["environment"]
        self.records, self.winners = document["results"], winners
        self.limit.setValue(document["limit"])
        self.limit.setEnabled(False)
        self.live.reset()
        for record in self.records:
            self.live.accept_event(
                {
                    "kind": "start",
                    "white": record["white"],
                    "black": record["black"],
                    "fen": record["initial_fen"],
                }
            )
            for event in review_game(record["moves"])["events"]:
                self.live.accept_event(event)
            self.live.accept_event(
                {
                    "kind": "end",
                    "result": record["result"],
                    "reason": record["termination"],
                }
            )
        self.status.setText(f"Wczytano drabinkę: {path}. Graj uruchomi następny mecz.")
        self._bracket()
