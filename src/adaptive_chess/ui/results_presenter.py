"""Human-readable views of exported results; raw files remain unchanged."""

import csv
import json
from html import escape
from pathlib import Path

from adaptive_chess.ui.i18n import tr

NAMES = {
    "random_series": "Losowy z losowym",
    "random_vs_minimax": "Losowy ze statycznym",
    "random_vs_adaptive": "Losowy z adaptacyjnym",
    "static_vs_adaptive": "Statyczny z adaptacyjnym",
    "suite_summary": "Podsumowanie wszystkich porównań",
    "report": "Raport kampanii",
    "learning": "Postępy uczenia",
    "standings": "Tabela turnieju",
    "human_evaluation": "Wyniki przeciw człowiekowi",
    "campaign": "Zapis kampanii",
    "move_limit_counts": "Partie przerwane limitem",
    "adjudicated_results": "Ocena pomocnicza pozycji",
    "average_final_material_balance": "Przewaga figur na końcu gry",
}
LABELS = {
    "agent": "Agent",
    "training_games": "Partie treningowe",
    "score": "Wynik punktowy",
    "wins": "Wygrane",
    "draws": "Remisy",
    "losses": "Przegrane",
    "points": "Punkty",
    "unfinished": "Przerwane limitem",
    "games": "Partie",
    "checkpoint": "Model po liczbie partii",
    "complete_pairs": "Pełne pary kolorów",
    "gain": "Zmiana od początku nauki",
    "ci_low": "Dolna granica niepewności",
    "ci_high": "Górna granica niepewności",
    "search_nodes": "Sprawdzone pozycje",
    "decision_seconds": "Czas wyboru ruchów (s)",
    "learning_seconds": "Czas uczenia (s)",
    "updates": "Aktualizacje modelu",
    "matches_count": "Liczba partii",
    "max_half_moves": "Limit ruchów obu stron",
    "experiment_type": "Rodzaj porównania",
    "generated_at_utc": "Data utworzenia (UTC)",
}


def title(path: Path) -> str:
    return tr(NAMES.get(path.stem.removesuffix("_gui"), path.stem.replace("_", " ")))


def table(headers: list[str], rows: list[list]) -> str:
    head = "".join(f"<th>{escape(tr(h))}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>"
        for row in rows
    )
    return (
        '<table border="1" cellspacing="0" cellpadding="8">'
        f"<tr>{head}</tr>{body}</table>"
    )


def bot_name(value: str) -> str:
    for old, new in (
        ("StaticMinimaxBot", "Statyczny"),
        ("AdaptiveMinimaxBot", "Adaptacyjny"),
        ("RandomBot", "Losowy"),
    ):
        value = value.replace(old, new)
    return tr(value.split("-White")[0].split("-Black")[0])


def game_rows(path: Path) -> list[dict]:
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "completed" in data:
            return [
                {
                    **g,
                    "white_bot_name": data["participant"]
                    if g["human_white"]
                    else g["agent"],
                    "black_bot_name": g["agent"]
                    if g["human_white"]
                    else data["participant"],
                }
                for g in data["completed"] + data.get("human_evaluations", [])
            ]
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return (
            list(reader) if reader.fieldnames and "result" in reader.fieldnames else []
        )


def outcome(row: dict) -> str:
    if (
        str(row.get("reached_move_limit", "")).lower() == "true"
        or row.get("result") == "*"
    ):
        return tr("Przerwane limitem")
    return tr(
        {"1-0": "Wygrane białych", "0-1": "Wygrane czarnych", "1/2-1/2": "Remisy"}.get(
            row.get("result", ""), "Brak wyniku"
        )
    )


def games_html(rows: list[dict]) -> str:
    labels = [
        tr(k)
        for k in ("Wygrane białych", "Wygrane czarnych", "Remisy", "Przerwane limitem")
    ]
    counts = [sum(outcome(r) == label for r in rows) for label in labels]
    summary = table(["Partie", *labels], [[len(rows), *counts]])
    details = [
        [
            i,
            bot_name(r.get("white_bot_name", "")),
            bot_name(r.get("black_bot_name", "")),
            outcome(r),
            r.get("half_moves", len(r.get("moves", []))),
        ]
        for i, r in enumerate(rows[:200], 1)
    ]
    return (
        summary
        + "<p>"
        + escape(
            tr(
                "Przerwane partie nie oznaczają remisu ani zwycięstwa. Kolor "
                "dotyczy strony na planszy."
            )
        )
        + "</p>"
        + table(["#", "Białymi", "Czarnymi", "Wynik", "Liczba ruchów"], details)
        + (
            "<p>"
            + tr("Pokazano pierwsze 200 partii. Pełne dane znajdują się w pliku.")
            + "</p>"
            if len(rows) > 200
            else ""
        )
    )


def file_html(path: Path) -> str:
    heading = f"<h2>{escape(title(path))}</h2>"
    if path.suffix == ".csv":
        games = game_rows(path)
        if games:
            return heading + games_html(games)
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            keys = reader.fieldnames or []
            rows = list(reader)[:200]
        return heading + table(
            [LABELS.get(k, k.replace("_", " ")) for k in keys],
            [[r.get(k, "") for k in keys] for r in rows],
        )
    games = game_rows(path)
    if games:
        return heading + games_html(games)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        settings_rows = [
            [tr(LABELS.get(k, k.replace("_", " "))), v]
            for k, v in data.items()
            if isinstance(v, (str, int, float, bool))
        ]
        return heading + table(["Ustawienia uruchomienia", "Wartość"], settings_rows)
    return heading + "<p>" + tr("Dane techniczne") + "</p>"


def overview_games(folder: Path) -> list[dict]:
    """Read the same game sources as the overview for visual summaries."""
    games = []
    for path in folder.rglob("*.csv"):
        games.extend(game_rows(path))
    if not games:
        for path in folder.rglob("campaign.json"):
            games.extend(game_rows(path))
    return games


def overview(folder: Path) -> str:
    games = overview_games(folder)
    return (
        "<h1>"
        + tr("Podsumowanie")
        + "</h1>"
        + (
            games_html(games)
            if games
            else "<p>" + tr("Brak zakończonych partii.") + "</p>"
        )
    )
