from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

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
        return tuple()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    chart_paths = [
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

    figure_width = max(8, len(summary_table) * 2.5)

    fig, ax = plt.subplots(figsize=(figure_width, 5))
    plot_data.plot(kind="bar", ax=ax)

    ax.set_title("Wyniki techniczne według eksperymentu")
    ax.set_xlabel("Eksperyment")
    ax.set_ylabel("Liczba partii")
    ax.tick_params(axis="x", labelrotation=30)

    fig.tight_layout()

    return _save_figure(fig, output_path)


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

    figure_width = max(8, len(summary_table) * 2.5)

    fig, ax = plt.subplots(figsize=(figure_width, 5))
    plot_data.plot(kind="bar", ax=ax)

    ax.axhline(0)
    ax.set_title("Średnia końcowa przewaga materialna białych")
    ax.set_xlabel("Eksperyment")
    ax.set_ylabel("Przewaga materialna")
    ax.tick_params(axis="x", labelrotation=30)

    fig.tight_layout()

    return _save_figure(fig, output_path)


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

    plot_data = summary_table.set_index("experiment_name")[
        "move_limit_reached_count"
    ]

    figure_width = max(8, len(summary_table) * 2.5)

    fig, ax = plt.subplots(figsize=(figure_width, 5))
    plot_data.plot(kind="bar", ax=ax)

    ax.set_title("Partie zakończone limitem półruchów")
    ax.set_xlabel("Eksperyment")
    ax.set_ylabel("Liczba partii")
    ax.tick_params(axis="x", labelrotation=30)

    fig.tight_layout()

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