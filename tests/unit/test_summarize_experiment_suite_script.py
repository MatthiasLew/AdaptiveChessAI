from pathlib import Path

import pytest

from scripts.summarize_experiment_suite import (
    REQUIRED_COLUMNS,
    discover_csv_files,
    load_csv_rows,
    render_markdown_report,
    summarize_csv_file,
    summarize_experiment_group,
)


def write_csv(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    columns = list(REQUIRED_COLUMNS)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        csv_file.write(",".join(columns))
        csv_file.write("\n")

        for row in rows:
            values = [row.get(column, "") for column in columns]
            csv_file.write(",".join(values))
            csv_file.write("\n")


def create_row(
    experiment_name: str = "Experiment A",
    match_index: str = "1",
    result: str = "1-0",
    adjudicated_result: str = "1-0",
    half_moves: str = "10",
    final_material_balance: str = "3",
    reached_move_limit: str = "False",
) -> dict[str, str]:
    return {
        "experiment_name": experiment_name,
        "match_index": match_index,
        "white_bot_name": "WhiteBot",
        "black_bot_name": "BlackBot",
        "result": result,
        "adjudicated_result": adjudicated_result,
        "termination_reason": "rules",
        "half_moves": half_moves,
        "final_material_balance": final_material_balance,
        "reached_move_limit": reached_move_limit,
        "moves_uci": "e2e4 e7e5",
        "material_balances": "0 0",
        "position_scores": "0.0 0.0",
        "final_fen": "dummy-fen",
    }


def test_discover_csv_files_returns_sorted_csv_files(tmp_path):
    first = tmp_path / "b.csv"
    second = tmp_path / "a.csv"
    ignored = tmp_path / "report.txt"

    first.write_text("", encoding="utf-8")
    second.write_text("", encoding="utf-8")
    ignored.write_text("", encoding="utf-8")

    csv_files = discover_csv_files(tmp_path)

    assert csv_files == (
        second,
        first,
    )


def test_discover_csv_files_rejects_missing_directory(tmp_path):
    missing_dir = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        discover_csv_files(missing_dir)


def test_load_csv_rows_rejects_missing_columns(tmp_path):
    csv_path = tmp_path / "broken.csv"
    csv_path.write_text("experiment_name,result\nA,1-0\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_csv_rows(csv_path)


def test_summarize_experiment_group_calculates_statistics():
    rows = [
        create_row(
            experiment_name="Experiment A",
            match_index="1",
            result="1-0",
            adjudicated_result="1-0",
            half_moves="10",
            final_material_balance="3",
            reached_move_limit="False",
        ),
        create_row(
            experiment_name="Experiment A",
            match_index="2",
            result="1/2-1/2",
            adjudicated_result="0-1",
            half_moves="20",
            final_material_balance="-4",
            reached_move_limit="True",
        ),
    ]

    summary = summarize_experiment_group(
        csv_file="sample.csv",
        experiment_name="Experiment A",
        rows=rows,
    )

    assert summary.csv_file == "sample.csv"
    assert summary.experiment_name == "Experiment A"
    assert summary.total_matches == 2

    assert summary.formal_white_wins == 1
    assert summary.formal_black_wins == 0
    assert summary.formal_draws == 1

    assert summary.adjudicated_white_wins == 1
    assert summary.adjudicated_black_wins == 1
    assert summary.adjudicated_draws == 0

    assert summary.average_half_moves == 15.0
    assert summary.average_final_material_balance == -0.5
    assert summary.move_limit_reached_count == 1


def test_summarize_csv_file_groups_by_experiment_name(tmp_path):
    csv_path = tmp_path / "sample.csv"

    write_csv(
        csv_path,
        [
            create_row(experiment_name="Experiment A", match_index="1"),
            create_row(experiment_name="Experiment B", match_index="1"),
        ],
    )

    summaries = summarize_csv_file(csv_path)

    assert len(summaries) == 2
    assert summaries[0].experiment_name == "Experiment A"
    assert summaries[1].experiment_name == "Experiment B"


def test_render_markdown_report_contains_summary_table(tmp_path):
    csv_path = tmp_path / "sample.csv"

    write_csv(
        csv_path,
        [
            create_row(experiment_name="Experiment A", match_index="1"),
        ],
    )

    summaries = summarize_csv_file(csv_path)

    report = render_markdown_report(
        summaries=summaries,
        input_dir=tmp_path,
    )

    assert "# Zbiorcze podsumowanie eksperymentów" in report
    assert "| CSV | Eksperyment | Partie |" in report
    assert "Experiment A" in report
    assert "sample.csv" in report