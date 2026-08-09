import csv

import pytest

from adaptive_chess.analysis.csv_report import (
    create_summary_table,
    load_results_csv,
    render_summary_report,
    analyze_results_csv,
)
from adaptive_chess.data.csv_exporter import MATCH_RESULT_FIELDNAMES


def write_test_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=MATCH_RESULT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def create_csv_row(
    experiment_name: str,
    result: str,
    adjudicated_result: str,
    half_moves: int,
    final_material_balance: int,
    reached_move_limit: bool,
) -> dict[str, object]:
    return {
        "experiment_name": experiment_name,
        "match_index": 1,
        "white_bot_name": "WhiteBot",
        "black_bot_name": "BlackBot",
        "result": result,
        "adjudicated_result": adjudicated_result,
        "termination_reason": "move_limit" if reached_move_limit else "rules",
        "half_moves": half_moves,
        "final_material_balance": final_material_balance,
        "reached_move_limit": reached_move_limit,
        "moves_uci": "e2e4 e7e5",
        "material_balances": "0 0",
        "position_scores": "0.0 0.0",
        "final_fen": "dummy-fen",
    }


def test_load_results_csv_loads_valid_file(tmp_path):
    csv_path = tmp_path / "results.csv"

    write_test_csv(
        csv_path,
        [
            create_csv_row(
                experiment_name="experiment-a",
                result="1/2-1/2",
                adjudicated_result="1-0",
                half_moves=100,
                final_material_balance=5,
                reached_move_limit=True,
            )
        ],
    )

    dataframe = load_results_csv(csv_path)

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["experiment_name"] == "experiment-a"


def test_load_results_csv_rejects_missing_file(tmp_path):
    csv_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_results_csv(csv_path)


def test_load_results_csv_rejects_missing_required_columns(tmp_path):
    csv_path = tmp_path / "invalid.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["experiment_name"])
        writer.writeheader()
        writer.writerow({"experiment_name": "broken"})

    with pytest.raises(ValueError):
        load_results_csv(csv_path)


def test_create_summary_table_groups_by_experiment(tmp_path):
    csv_path = tmp_path / "results.csv"

    write_test_csv(
        csv_path,
        [
            create_csv_row(
                experiment_name="experiment-a",
                result="1/2-1/2",
                adjudicated_result="1-0",
                half_moves=100,
                final_material_balance=9,
                reached_move_limit=True,
            ),
            create_csv_row(
                experiment_name="experiment-a",
                result="1/2-1/2",
                adjudicated_result="0-1",
                half_moves=80,
                final_material_balance=-6,
                reached_move_limit=True,
            ),
            create_csv_row(
                experiment_name="experiment-b",
                result="1-0",
                adjudicated_result="1-0",
                half_moves=40,
                final_material_balance=3,
                reached_move_limit=False,
            ),
        ],
    )

    dataframe = load_results_csv(csv_path)
    summary = create_summary_table(dataframe)

    assert len(summary) == 2

    experiment_a = summary[summary["experiment_name"] == "experiment-a"].iloc[0]
    assert experiment_a["total_matches"] == 2
    assert experiment_a["white_wins"] == 0
    assert experiment_a["black_wins"] == 0
    assert experiment_a["draws"] == 2
    assert experiment_a["adjudicated_white_wins"] == 1
    assert experiment_a["adjudicated_black_wins"] == 1
    assert experiment_a["adjudicated_draws"] == 0
    assert experiment_a["average_half_moves"] == 90.0
    assert experiment_a["average_final_material_balance"] == 1.5
    assert experiment_a["move_limit_reached_count"] == 2


def test_create_summary_table_rejects_invalid_result(tmp_path):
    csv_path = tmp_path / "results.csv"

    write_test_csv(
        csv_path,
        [
            create_csv_row(
                experiment_name="experiment-a",
                result="invalid",
                adjudicated_result="1-0",
                half_moves=100,
                final_material_balance=9,
                reached_move_limit=True,
            )
        ],
    )

    dataframe = load_results_csv(csv_path)

    with pytest.raises(ValueError):
        create_summary_table(dataframe)


def test_render_summary_report_contains_key_sections(tmp_path):
    csv_path = tmp_path / "results.csv"

    write_test_csv(
        csv_path,
        [
            create_csv_row(
                experiment_name="experiment-a",
                result="1/2-1/2",
                adjudicated_result="1-0",
                half_moves=100,
                final_material_balance=9,
                reached_move_limit=True,
            )
        ],
    )

    dataframe = load_results_csv(csv_path)
    summary = create_summary_table(dataframe)

    report = render_summary_report(summary)

    assert "Raport eksperymentów szachowych" in report
    assert "experiment-a" in report
    assert "Wyniki formalne" in report
    assert "Wyniki techniczne" in report
    assert "Średnia liczba półruchów" in report


def test_analyze_results_csv_writes_report_file(tmp_path):
    csv_path = tmp_path / "results.csv"
    report_path = tmp_path / "report.txt"

    write_test_csv(
        csv_path,
        [
            create_csv_row(
                experiment_name="experiment-a",
                result="1/2-1/2",
                adjudicated_result="1-0",
                half_moves=100,
                final_material_balance=9,
                reached_move_limit=True,
            )
        ],
    )

    report = analyze_results_csv(
        input_path=csv_path,
        output_report_path=report_path,
    )

    assert report_path.exists()
    assert report_path.read_text(encoding="utf-8") == report
    assert "experiment-a" in report