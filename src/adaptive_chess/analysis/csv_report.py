from pathlib import Path

import pandas as pd


REQUIRED_MATCH_RESULT_COLUMNS = {
    "experiment_name",
    "match_index",
    "white_bot_name",
    "black_bot_name",
    "result",
    "adjudicated_result",
    "termination_reason",
    "half_moves",
    "final_material_balance",
    "reached_move_limit",
    "moves_uci",
    "material_balances",
    "position_scores",
    "final_fen",
}

VALID_RESULTS = {"1-0", "0-1", "1/2-1/2"}


def load_results_csv(input_path: str | Path) -> pd.DataFrame:
    """
    Wczytuje plik CSV z wynikami partii.

    Args:
        input_path: Ścieżka do pliku CSV.

    Returns:
        DataFrame z wynikami partii.

    Raises:
        FileNotFoundError: Jeśli plik nie istnieje.
        ValueError: Jeśli CSV nie zawiera wymaganych kolumn.
    """
    csv_path = Path(input_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file does not exist: {csv_path}")

    dataframe = pd.read_csv(csv_path)

    missing_columns = REQUIRED_MATCH_RESULT_COLUMNS - set(dataframe.columns)
    if missing_columns:
        sorted_columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV file is missing required columns: {sorted_columns}")

    return dataframe


def create_summary_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Tworzy tabelę podsumowującą eksperymenty zapisane w CSV.

    Args:
        dataframe: DataFrame z wynikami partii.

    Returns:
        DataFrame z jedną linią podsumowania dla każdego eksperymentu.
    """
    missing_columns = REQUIRED_MATCH_RESULT_COLUMNS - set(dataframe.columns)
    if missing_columns:
        sorted_columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"DataFrame is missing required columns: {sorted_columns}")

    if dataframe.empty:
        return pd.DataFrame(
            columns=[
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
            ]
        )

    rows: list[dict[str, object]] = []

    for experiment_name, group in dataframe.groupby("experiment_name", dropna=False):
        result_counts = _calculate_counts(group["result"])
        adjudicated_counts = _calculate_counts(group["adjudicated_result"])

        rows.append(
            {
                "experiment_name": experiment_name,
                "total_matches": int(len(group)),
                "white_wins": result_counts["1-0"],
                "black_wins": result_counts["0-1"],
                "draws": result_counts["1/2-1/2"],
                "adjudicated_white_wins": adjudicated_counts["1-0"],
                "adjudicated_black_wins": adjudicated_counts["0-1"],
                "adjudicated_draws": adjudicated_counts["1/2-1/2"],
                "average_half_moves": float(group["half_moves"].mean()),
                "average_final_material_balance": float(
                    group["final_material_balance"].mean()
                ),
                "move_limit_reached_count": int(
                    _to_bool_series(group["reached_move_limit"]).sum()
                ),
            }
        )

    return pd.DataFrame(rows)


def render_summary_report(summary_table: pd.DataFrame) -> str:
    """
    Renderuje tekstowy raport z tabeli podsumowania.

    Args:
        summary_table: DataFrame utworzony przez create_summary_table().

    Returns:
        Raport tekstowy.
    """
    if summary_table.empty:
        return "=== Raport eksperymentów szachowych ===\n\nBrak danych do analizy.\n"

    lines = [
        "=== Raport eksperymentów szachowych ===",
        "",
        f"Liczba serii eksperymentalnych: {len(summary_table)}",
        f"Łączna liczba partii: {int(summary_table['total_matches'].sum())}",
        "",
    ]

    for _, row in summary_table.iterrows():
        lines.extend(
            [
                f"--- {row['experiment_name']} ---",
                f"Liczba partii: {int(row['total_matches'])}",
                "",
                "Wyniki formalne:",
                f"  Wygrane białych: {int(row['white_wins'])}",
                f"  Wygrane czarnych: {int(row['black_wins'])}",
                f"  Remisy: {int(row['draws'])}",
                "",
                "Wyniki techniczne:",
                f"  Wygrane białych: {int(row['adjudicated_white_wins'])}",
                f"  Wygrane czarnych: {int(row['adjudicated_black_wins'])}",
                f"  Remisy: {int(row['adjudicated_draws'])}",
                "",
                "Metryki:",
                f"  Średnia liczba półruchów: {row['average_half_moves']:.2f}",
                "  Średnia końcowa przewaga materialna białych: "
                f"{row['average_final_material_balance']:.2f}",
                f"  Partie zakończone limitem: {int(row['move_limit_reached_count'])}",
                "",
            ]
        )

    return "\n".join(lines)


def analyze_results_csv(
    input_path: str | Path,
    output_report_path: str | Path | None = None,
) -> str:
    """
    Wczytuje CSV, tworzy podsumowanie i opcjonalnie zapisuje raport tekstowy.

    Args:
        input_path: Ścieżka do CSV z wynikami.
        output_report_path: Opcjonalna ścieżka do pliku raportu.

    Returns:
        Raport tekstowy.
    """
    dataframe = load_results_csv(input_path)
    summary_table = create_summary_table(dataframe)
    report = render_summary_report(summary_table)

    if output_report_path is not None:
        report_path = Path(output_report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

    return report


def _calculate_counts(series: pd.Series) -> dict[str, int]:
    """
    Liczy wystąpienia wyników partii.

    Args:
        series: Seria Pandas z wynikami.

    Returns:
        Słownik liczników wyników.

    Raises:
        ValueError: Jeśli seria zawiera nieznany wynik.
    """
    counts = {
        "1-0": 0,
        "0-1": 0,
        "1/2-1/2": 0,
    }

    for result in series:
        if result not in VALID_RESULTS:
            raise ValueError(f"Unsupported match result: {result}")

        counts[result] += 1

    return counts


def _to_bool_series(series: pd.Series) -> pd.Series:
    """
    Zamienia serię wartości bool/string na wartości bool.

    Args:
        series: Seria z wartościami typu bool albo tekstami "True"/"False".

    Returns:
        Seria bool.
    """
    return series.astype(str).str.lower().isin({"true", "1", "yes"})