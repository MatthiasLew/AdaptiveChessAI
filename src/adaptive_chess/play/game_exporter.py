import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import chess

from adaptive_chess.play.human_vs_bot_session import (
    HumanVsBotGameSummary,
    PlayedMove,
)


GAME_SUMMARY_CSV_FIELDNAMES = [
    "bot_name",
    "human_color",
    "bot_color",
    "result",
    "status_message",
    "final_fen",
    "half_moves",
    "final_material_balance",
    "move_index",
    "move_color",
    "move_player_type",
    "move_san",
    "move_uci",
]


def color_to_text(color: chess.Color) -> str:
    """
    Zamienia kolor python-chess na stabilny tekst eksportowy.
    """
    if color == chess.WHITE:
        return "white"

    if color == chess.BLACK:
        return "black"

    raise ValueError(f"Unsupported color: {color}")


def played_move_to_dict(
    move: PlayedMove,
    move_index: int,
) -> dict[str, Any]:
    """
    Zamienia pojedynczy ruch na słownik do eksportu.
    """
    return {
        "move_index": move_index,
        "player_type": move.player_type.value,
        "color": color_to_text(move.color),
        "san": move.san,
        "uci": move.move_uci,
    }


def game_summary_to_dict(summary: HumanVsBotGameSummary) -> dict[str, Any]:
    """
    Zamienia podsumowanie partii na słownik JSON-serializowalny.
    """
    return {
        "bot_name": summary.bot_name,
        "human_color": color_to_text(summary.human_color),
        "bot_color": color_to_text(summary.bot_color),
        "result": summary.result,
        "status_message": summary.status_message,
        "final_fen": summary.final_fen,
        "half_moves": summary.half_moves,
        "final_material_balance": summary.final_material_balance,
        "move_history": [
            played_move_to_dict(
                move=move,
                move_index=index,
            )
            for index, move in enumerate(summary.move_history, start=1)
        ],
    }


def write_game_summary_json(
    summary: HumanVsBotGameSummary,
    output_path: str | Path,
) -> Path:
    """
    Zapisuje podsumowanie partii do pliku JSON.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(
        json.dumps(
            game_summary_to_dict(summary),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_file


def write_game_summary_csv(
    summary: HumanVsBotGameSummary,
    output_path: str | Path,
) -> Path:
    """
    Zapisuje podsumowanie partii do pliku CSV.

    CSV zawiera jeden wiersz na ruch. Dane podsumowania są powtarzane
    w każdym wierszu, żeby plik był łatwy do filtrowania i analizowania.
    Jeśli partia nie ma ruchów, eksportowany jest jeden wiersz bez ruchu.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    rows = _build_csv_rows(summary)

    with output_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=GAME_SUMMARY_CSV_FIELDNAMES,
        )
        writer.writeheader()
        writer.writerows(rows)

    return output_file


def write_game_summary_exports(
    summary: HumanVsBotGameSummary,
    output_dir: str | Path,
    file_stem: str | None = None,
) -> tuple[Path, Path]:
    """
    Zapisuje podsumowanie partii jednocześnie do JSON i CSV.

    Returns:
        Para ścieżek: (json_path, csv_path).
    """
    output_directory = Path(output_dir)
    resolved_file_stem = file_stem or create_game_summary_file_stem(summary)

    json_path = output_directory / f"{resolved_file_stem}.json"
    csv_path = output_directory / f"{resolved_file_stem}.csv"

    written_json_path = write_game_summary_json(
        summary=summary,
        output_path=json_path,
    )
    written_csv_path = write_game_summary_csv(
        summary=summary,
        output_path=csv_path,
    )

    return written_json_path, written_csv_path


def create_game_summary_file_stem(
    summary: HumanVsBotGameSummary,
    created_at: datetime | None = None,
) -> str:
    """
    Buduje nazwę pliku dla eksportu partii.
    """
    timestamp = (created_at or datetime.now()).strftime("%Y%m%d_%H%M%S")
    bot_name = sanitize_file_part(summary.bot_name)
    human_color = color_to_text(summary.human_color)

    return f"human_vs_{bot_name}_{human_color}_{timestamp}"


def sanitize_file_part(value: str) -> str:
    """
    Czyści fragment nazwy pliku.
    """
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    normalized = normalized.strip("_")

    if not normalized:
        return "unknown"

    return normalized


def _build_csv_rows(summary: HumanVsBotGameSummary) -> list[dict[str, Any]]:
    base_row = {
        "bot_name": summary.bot_name,
        "human_color": color_to_text(summary.human_color),
        "bot_color": color_to_text(summary.bot_color),
        "result": summary.result,
        "status_message": summary.status_message,
        "final_fen": summary.final_fen,
        "half_moves": summary.half_moves,
        "final_material_balance": summary.final_material_balance,
    }

    if not summary.move_history:
        return [
            {
                **base_row,
                "move_index": "",
                "move_color": "",
                "move_player_type": "",
                "move_san": "",
                "move_uci": "",
            }
        ]

    rows = []

    for index, move in enumerate(summary.move_history, start=1):
        rows.append(
            {
                **base_row,
                "move_index": index,
                "move_color": color_to_text(move.color),
                "move_player_type": move.player_type.value,
                "move_san": move.san,
                "move_uci": move.move_uci,
            }
        )

    return rows