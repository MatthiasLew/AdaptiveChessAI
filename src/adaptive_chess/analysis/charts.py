from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

from adaptive_chess.analysis.csv_report import create_summary_table, load_results_csv

REQUIRED_SUMMARY_COLUMNS = {
    "experiment_name",
    "total_matches",
    "white_wins",
    "black_wins",
    "draws",
    "adjudicated_white_wins",
    "adjudicated_black_wins",
    "adjudicated_draws",
    "average_half_moves",
    "average_final_material_balance",
    "move_limit_reached_count",
}


def generate_experiment_charts(
    input_csv_path: str | Path,
    output_dir: str | Path,
) -> tuple[Path, ...]:
    """
    Generuje zestaw wykresów PNG na podstawie CSV z wynikami eksperymentów.

    Args:
        input_csv_path: Ścieżka do pliku CSV z wynikami partii.
        output_dir: Folder, do którego zostaną zapisane wykresy.

    Returns:
        Krotka ścieżek do wygenerowanych plików PNG.
        Jeśli CSV nie zawiera danych, zwracana jest pusta krotka.
    """
    dataframe = load_results_csv(input_csv_path)
    summary_table = create_summary_table(dataframe)

    if summary_table.empty:
        return ()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    chart_paths = [
        plot_actual_results(dataframe, output_path / "actual_results.png"),
        plot_adjudicated_results(
            summary_table=summary_table,
            output_path=output_path / "adjudicated_results.png",
        ),
        plot_average_final_material_balance(
            summary_table=summary_table,
            output_path=output_path / "average_final_material_balance.png",
        ),
        plot_move_limit_counts(
            summary_table=summary_table,
            output_path=output_path / "move_limit_counts.png",
        ),
    ]

    return tuple(chart_paths)


def plot_adjudicated_results(
    summary_table: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Tworzy wykres słupkowy wyników technicznych.

    Args:
        summary_table: Tabela podsumowania eksperymentów.
        output_path: Ścieżka zapisu PNG.

    Returns:
        Ścieżka do zapisanego wykresu.
    """
    _validate_summary_table(summary_table)

    plot_data = summary_table.set_index("experiment_name")[
        [
            "adjudicated_white_wins",
            "adjudicated_black_wins",
            "adjudicated_draws",
        ]
    ]

    plot_data = plot_data.rename(
        columns={
            "adjudicated_white_wins": "Wygrane białych",
            "adjudicated_black_wins": "Wygrane czarnych",
            "adjudicated_draws": "Remisy",
        }
    )

    plot_data.columns = ["Na korzyść białych", "Na korzyść czarnych", "Równowaga"]
    return _horizontal_chart(
        plot_data,
        output_path,
        "Pomocnicza ocena po zakończeniu gry",
        "Liczba partii",
        "Przy limicie: ocena według materiału, a nie wynik partii.",
        stacked=True,
        integer=True,
    )


def plot_average_final_material_balance(
    summary_table: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Tworzy wykres średniej końcowej przewagi materialnej białych.

    Args:
        summary_table: Tabela podsumowania eksperymentów.
        output_path: Ścieżka zapisu PNG.

    Returns:
        Ścieżka do zapisanego wykresu.
    """
    _validate_summary_table(summary_table)

    plot_data = summary_table.set_index("experiment_name")[
        "average_final_material_balance"
    ]

    return _horizontal_chart(
        plot_data,
        output_path,
        "Końcowy bilans materiału",
        "Średnia przewaga w punktach materiału",
        "Dodatni: przewaga białych. Ujemny: przewaga czarnych. To nie wynik gry.",
    )


def plot_move_limit_counts(
    summary_table: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Tworzy wykres liczby partii zakończonych limitem półruchów.

    Args:
        summary_table: Tabela podsumowania eksperymentów.
        output_path: Ścieżka zapisu PNG.

    Returns:
        Ścieżka do zapisanego wykresu.
    """
    _validate_summary_table(summary_table)

    plot_data = summary_table.set_index("experiment_name")["move_limit_reached_count"]

    return _horizontal_chart(
        plot_data,
        output_path,
        "Partie przerwane limitem",
        "Liczba partii",
        "Przerwana partia nie oznacza remisu.",
        integer=True,
    )


def actual_result_counts(dataframe: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, group in dataframe.groupby("experiment_name", dropna=False):
        limited = group["reached_move_limit"].astype(str).str.lower().isin(
            {"true", "1", "yes"}
        )
        finished = group.loc[~limited, "result"]
        rows.append(
            {
                "experiment_name": name,
                "Wygrane białych": int(finished.eq("1-0").sum()),
                "Wygrane czarnych": int(finished.eq("0-1").sum()),
                "Remisy": int(finished.eq("1/2-1/2").sum()),
                "Przerwane limitem": int(limited.sum()),
            }
        )
    return pd.DataFrame(rows).set_index("experiment_name")


def plot_actual_results(dataframe: pd.DataFrame, output_path: str | Path) -> Path:
    return _horizontal_chart(
        actual_result_counts(dataframe),
        output_path,
        "Rzeczywiste wyniki partii",
        "Liczba partii",
        "Przerwane limitem pokazano osobno; nie są remisami.",
        stacked=True,
        integer=True,
    )


def _short_name(value: str) -> str:
    for old, new in (
        ("StaticMinimaxBot", "Statyczny"),
        ("AdaptiveMinimaxBot", "Adaptacyjny"),
        ("RandomBot", "Losowy"),
        ("-White", " (białe)"),
        ("-Black", " (czarne)"),
        ("-depth-", " / głębokość "),
        ("_vs_", " vs "),
    ):
        value = value.replace(old, new)
    return fill(value.replace("_", " "), width=32)


def _horizontal_chart(
    data, output_path, title, xlabel, note, stacked=False, integer=False
) -> Path:
    data = data.copy()
    data.index = [_short_name(str(name)) for name in data.index]
    with plt.rc_context({"font.size": 11}):
        fig, ax = plt.subplots(figsize=(10, max(4.5, len(data) * 1.25 + 2.5)))
        data.plot(
            kind="barh",
            ax=ax,
            stacked=stacked,
            color=["#246baf", "#c47814", "#448450", "#8c759e"]
            if isinstance(data, pd.DataFrame)
            else "#246baf",
            width=0.6,
        )
        for container in ax.containers:
            labels = [f"{value:g}" if value else "" for value in container.datavalues]
            ax.bar_label(
                container,
                labels=labels,
                label_type="center" if stacked else "edge",
                color="white" if stacked else "#192d3c",
                fontsize=11,
            )
        ax.set_title(title, pad=50 if stacked else 16, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("")
        ax.invert_yaxis()
        ax.axvline(0, color="#677784", linewidth=0.8)
        ax.grid(axis="x", alpha=0.2)
        ax.set_axisbelow(True)
        ax.margins(x=0.15)
        if integer:
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        if stacked:
            ax.legend(
                loc="lower left",
                bbox_to_anchor=(0, 1.01),
                ncol=2,
                frameon=False,
                fontsize=10,
            )
        fig.text(0.5, 0.02, note, ha="center", fontsize=10)
        fig.tight_layout(rect=(0, 0.07, 1, 1))
        return _save_figure(fig, output_path)


def _validate_summary_table(summary_table: pd.DataFrame) -> None:
    """
    Sprawdza, czy tabela podsumowania zawiera wymagane kolumny.

    Args:
        summary_table: Tabela do sprawdzenia.

    Raises:
        ValueError: Jeśli brakuje wymaganych kolumn.
    """
    missing_columns = REQUIRED_SUMMARY_COLUMNS - set(summary_table.columns)

    if missing_columns:
        sorted_columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"Summary table is missing required columns: {sorted_columns}")


def _save_figure(fig: plt.Figure, output_path: str | Path) -> Path:
    """
    Zapisuje wykres do pliku PNG i zamyka figurę.

    Args:
        fig: Figura matplotlib.
        output_path: Ścieżka zapisu.

    Returns:
        Ścieżka do zapisanego pliku.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(output_file, dpi=150)
    plt.close(fig)

    return output_file
