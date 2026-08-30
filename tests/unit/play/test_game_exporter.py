import csv
import json
from datetime import datetime

import chess
import pytest

from adaptive_chess.play.game_exporter import (
    color_to_text,
    create_game_summary_file_stem,
    game_summary_to_dict,
    sanitize_file_part,
    write_game_summary_csv,
    write_game_summary_exports,
    write_game_summary_json,
)
from adaptive_chess.play.human_vs_bot_session import (
    HumanVsBotGameSummary,
    PlayedMove,
    PlayerType,
)


def build_summary() -> HumanVsBotGameSummary:
    return HumanVsBotGameSummary(
        bot_name="RandomBot",
        human_color=chess.WHITE,
        bot_color=chess.BLACK,
        result="1-0",
        status_message="Checkmate. Winner: White.",
        final_fen="test-fen",
        half_moves=2,
        final_material_balance=3,
        move_history=(
            PlayedMove(
                player_type=PlayerType.HUMAN,
                color=chess.WHITE,
                move_uci="e2e4",
                san="e4",
            ),
            PlayedMove(
                player_type=PlayerType.BOT,
                color=chess.BLACK,
                move_uci="e7e5",
                san="e5",
            ),
        ),
    )


def test_color_to_text_returns_white():
    assert color_to_text(chess.WHITE) == "white"


def test_color_to_text_returns_black():
    assert color_to_text(chess.BLACK) == "black"


def test_color_to_text_rejects_invalid_color():
    with pytest.raises(ValueError):
        color_to_text("white")


def test_game_summary_to_dict_exports_summary_and_moves():
    summary = build_summary()

    exported = game_summary_to_dict(summary)

    assert exported["bot_name"] == "RandomBot"
    assert exported["human_color"] == "white"
    assert exported["bot_color"] == "black"
    assert exported["result"] == "1-0"
    assert exported["half_moves"] == 2
    assert exported["final_material_balance"] == 3
    assert exported["move_history"][0]["uci"] == "e2e4"
    assert exported["move_history"][1]["player_type"] == "bot"


def test_write_game_summary_json_creates_file(tmp_path):
    summary = build_summary()
    output_path = tmp_path / "game.json"

    written_path = write_game_summary_json(
        summary=summary,
        output_path=output_path,
    )

    assert written_path == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))

    assert loaded["bot_name"] == "RandomBot"
    assert loaded["move_history"][0]["san"] == "e4"


def test_write_game_summary_csv_creates_file(tmp_path):
    summary = build_summary()
    output_path = tmp_path / "game.csv"

    written_path = write_game_summary_csv(
        summary=summary,
        output_path=output_path,
    )

    assert written_path == output_path

    with output_path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["bot_name"] == "RandomBot"
    assert rows[0]["move_uci"] == "e2e4"
    assert rows[1]["move_player_type"] == "bot"


def test_write_game_summary_csv_exports_empty_move_row_for_no_moves(tmp_path):
    summary = HumanVsBotGameSummary(
        bot_name="RandomBot",
        human_color=chess.WHITE,
        bot_color=chess.BLACK,
        result="1-0",
        status_message="Checkmate. Winner: White.",
        final_fen="test-fen",
        half_moves=0,
        final_material_balance=0,
        move_history=(),
    )
    output_path = tmp_path / "game.csv"

    write_game_summary_csv(
        summary=summary,
        output_path=output_path,
    )

    with output_path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["move_uci"] == ""


def test_write_game_summary_exports_creates_json_and_csv(tmp_path):
    summary = build_summary()

    json_path, csv_path = write_game_summary_exports(
        summary=summary,
        output_dir=tmp_path,
        file_stem="saved_game",
    )

    assert json_path == tmp_path / "saved_game.json"
    assert csv_path == tmp_path / "saved_game.csv"
    assert json_path.exists()
    assert csv_path.exists()


def test_create_game_summary_file_stem_is_stable_with_datetime():
    summary = build_summary()

    file_stem = create_game_summary_file_stem(
        summary=summary,
        created_at=datetime(2026, 8, 30, 17, 30, 15),
    )

    assert file_stem == "human_vs_randombot_white_20260830_173015"


def test_sanitize_file_part_removes_unsafe_characters():
    assert (
        sanitize_file_part("Static Minimax Bot depth=2!")
        == "static_minimax_bot_depth_2"
    )


def test_sanitize_file_part_returns_unknown_for_empty_text():
    assert sanitize_file_part("   !!!   ") == "unknown"
