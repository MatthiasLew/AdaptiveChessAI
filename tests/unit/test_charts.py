import csv

import pandas as pd
import pytest

from adaptive_chess.analysis.charts import (
    generate_experiment_charts,
    plot_adjudicated_results,
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


def test_generate_experiment_charts_creates_png_files(tmp_path):
    csv_path = tmp_path / "results.csv"
    output_dir = tmp_path / "charts"

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

    chart_paths = generate_experiment_charts(
        input_csv_path=csv_path,
        output_dir=output_dir,
    )

    assert len(chart_paths) == 3

    for chart_path in chart_paths:
        assert chart_path.exists()
        assert chart_path.suffix == ".png"
        assert chart_path.stat().st_size > 0


def test_generate_experiment_charts_returns_empty_tuple_for_empty_csv(tmp_path):
    csv_path = tmp_path / "empty.csv"
    output_dir = tmp_path / "charts"

    write_test_csv(csv_path, [])

    chart_paths = generate_experiment_charts(
        input_csv_path=csv_path,
        output_dir=output_dir,
    )

    assert chart_paths == tuple()


def test_plot_adjudicated_results_rejects_missing_columns(tmp_path):
    summary_table = pd.DataFrame(
        [
            {
                "experiment_name": "experiment-a",
                "total_matches": 1,
            }
        ]
    )

    with pytest.raises(ValueError):
        plot_adjudicated_results(
            summary_table=summary_table,
            output_path=tmp_path / "broken.png",
        )