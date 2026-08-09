import csv

import pytest

from adaptive_chess.data.csv_exporter import (
    export_match_results_to_csv,
    export_match_series_collection_to_csv,
    match_result_to_csv_row,
)
from adaptive_chess.experiments.match_runner import MatchResult, TerminationReason


def create_match_result(
    result: str = "1/2-1/2",
    adjudicated_result: str = "1/2-1/2",
    half_moves: int = 2,
    final_material_balance: int = 0,
    reached_move_limit: bool = True,
) -> MatchResult:
    return MatchResult(
        white_bot_name="WhiteBot",
        black_bot_name="BlackBot",
        result=result,
        adjudicated_result=adjudicated_result,
        termination_reason=(
            TerminationReason.MOVE_LIMIT
            if reached_move_limit
            else TerminationReason.RULES
        ),
        half_moves=half_moves,
        moves_uci=("e2e4", "e7e5"),
        material_balances=(0, 0),
        position_scores=(0.0, 0.0),
        final_material_balance=final_material_balance,
        final_fen="dummy-fen",
        reached_move_limit=reached_move_limit,
    )


def test_match_result_to_csv_row():
    match = create_match_result(
        result="1/2-1/2",
        adjudicated_result="1-0",
        final_material_balance=5,
        reached_move_limit=True,
    )

    row = match_result_to_csv_row(
        match=match,
        match_index=1,
        experiment_name="test-experiment",
    )

    assert row["experiment_name"] == "test-experiment"
    assert row["match_index"] == 1
    assert row["white_bot_name"] == "WhiteBot"
    assert row["black_bot_name"] == "BlackBot"
    assert row["result"] == "1/2-1/2"
    assert row["adjudicated_result"] == "1-0"
    assert row["termination_reason"] == "move_limit"
    assert row["half_moves"] == 2
    assert row["final_material_balance"] == 5
    assert row["moves_uci"] == "e2e4 e7e5"
    assert row["material_balances"] == "0 0"
    assert row["position_scores"] == "0.0 0.0"
    assert row["final_fen"] == "dummy-fen"


def test_match_result_to_csv_row_rejects_invalid_match_index():
    match = create_match_result()

    with pytest.raises(ValueError):
        match_result_to_csv_row(match=match, match_index=0)


def test_export_match_results_to_csv(tmp_path):
    output_path = tmp_path / "matches.csv"
    matches = [
        create_match_result(result="1-0", adjudicated_result="1-0"),
        create_match_result(result="1/2-1/2", adjudicated_result="0-1"),
    ]

    saved_path = export_match_results_to_csv(
        matches=matches,
        output_path=output_path,
        experiment_name="single-series",
    )

    assert saved_path == output_path
    assert output_path.exists()

    with output_path.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 2
    assert rows[0]["experiment_name"] == "single-series"
    assert rows[0]["result"] == "1-0"
    assert rows[1]["adjudicated_result"] == "0-1"


def test_export_match_series_collection_to_csv(tmp_path):
    output_path = tmp_path / "collection.csv"

    first_series = [
        create_match_result(result="1-0", adjudicated_result="1-0"),
    ]
    second_series = [
        create_match_result(result="1/2-1/2", adjudicated_result="0-1"),
        create_match_result(result="1/2-1/2", adjudicated_result="1/2-1/2"),
    ]

    export_match_series_collection_to_csv(
        series_collection=[
            ("first-series", first_series),
            ("second-series", second_series),
        ],
        output_path=output_path,
    )

    with output_path.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 3
    assert rows[0]["experiment_name"] == "first-series"
    assert rows[1]["experiment_name"] == "second-series"
    assert rows[2]["experiment_name"] == "second-series"