import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


VALID_RESULTS = ("1-0", "0-1", "1/2-1/2")

REQUIRED_COLUMNS = {
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


@dataclass(frozen=True)
class ExperimentGroupSummary:
    """
    Zbiorcze statystyki dla jednej grupy eksperymentalnej z CSV.
    """

    csv_file: str
    experiment_name: str
    total_matches: int

    formal_white_wins: int
    formal_black_wins: int
    formal_draws: int

    adjudicated_white_wins: int
    adjudicated_black_wins: int
    adjudicated_draws: int

    average_half_moves: float
    average_final_material_balance: float
    move_limit_reached_count: int


def parse_args() -> argparse.Namespace:
    """
    Parsuje argumenty CLI.

    Returns:
        Konfiguracja generowania zbiorczego raportu.
    """
    parser = argparse.ArgumentParser(
        description="Summarize all experiment CSV files from a full suite directory."
    )

    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing experiment CSV files.",
    )

    parser.add_argument(
        "--output-md",
        type=str,
        default=None,
        help="Optional output Markdown file. Defaults to <input-dir>/suite_summary.md.",
    )

    return parser.parse_args()


def discover_csv_files(input_dir: Path) -> tuple[Path, ...]:
    """
    Znajduje pliki CSV w katalogu wyników.

    Args:
        input_dir: Katalog z wynikami eksperymentów.

    Returns:
        Posortowana lista plików CSV.
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    return tuple(sorted(path for path in input_dir.glob("*.csv") if path.is_file()))


def load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    """
    Wczytuje wiersze z CSV i sprawdza wymagane kolumny.

    Args:
        csv_path: Ścieżka do pliku CSV.

    Returns:
        Lista wierszy CSV jako słowniki.

    Raises:
        ValueError: Jeśli CSV nie zawiera wymaganych kolumn.
    """
    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        fieldnames = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - fieldnames

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV {csv_path} is missing columns: {missing}")

        return list(reader)


def summarize_csv_file(csv_path: Path) -> tuple[ExperimentGroupSummary, ...]:
    """
    Tworzy podsumowanie grup eksperymentalnych z jednego CSV.

    Args:
        csv_path: Plik CSV z wynikami partii.

    Returns:
        Lista podsumowań pogrupowanych po `experiment_name`.
    """
    rows = load_csv_rows(csv_path)

    grouped_rows: dict[str, list[dict[str, str]]] = {}

    for row in rows:
        experiment_name = row["experiment_name"]
        grouped_rows.setdefault(experiment_name, []).append(row)

    summaries = [
        summarize_experiment_group(
            csv_file=csv_path.name,
            experiment_name=experiment_name,
            rows=experiment_rows,
        )
        for experiment_name, experiment_rows in sorted(grouped_rows.items())
    ]

    return tuple(summaries)


def summarize_experiment_group(
    csv_file: str,
    experiment_name: str,
    rows: list[dict[str, str]],
) -> ExperimentGroupSummary:
    """
    Liczy statystyki dla jednej grupy eksperymentalnej.

    Args:
        csv_file: Nazwa pliku CSV.
        experiment_name: Nazwa eksperymentu.
        rows: Wiersze należące do tej grupy.

    Returns:
        Zbiorcze statystyki.
    """
    formal_counts = calculate_result_counts(rows, "result")
    adjudicated_counts = calculate_result_counts(rows, "adjudicated_result")

    half_moves = [_to_int(row["half_moves"], "half_moves") for row in rows]
    material_balances = [
        _to_int(row["final_material_balance"], "final_material_balance")
        for row in rows
    ]

    move_limit_reached_count = sum(
        1 for row in rows if _to_bool(row["reached_move_limit"])
    )

    return ExperimentGroupSummary(
        csv_file=csv_file,
        experiment_name=experiment_name,
        total_matches=len(rows),
        formal_white_wins=formal_counts["1-0"],
        formal_black_wins=formal_counts["0-1"],
        formal_draws=formal_counts["1/2-1/2"],
        adjudicated_white_wins=adjudicated_counts["1-0"],
        adjudicated_black_wins=adjudicated_counts["0-1"],
        adjudicated_draws=adjudicated_counts["1/2-1/2"],
        average_half_moves=_average(half_moves),
        average_final_material_balance=_average(material_balances),
        move_limit_reached_count=move_limit_reached_count,
    )


def calculate_result_counts(
    rows: list[dict[str, str]],
    field_name: str,
) -> dict[str, int]:
    """
    Liczy wystąpienia wyników partii.

    Args:
        rows: Wiersze CSV.
        field_name: Nazwa pola z wynikiem.

    Returns:
        Słownik z licznikami wyników.
    """
    counts = {
        "1-0": 0,
        "0-1": 0,
        "1/2-1/2": 0,
    }

    for row in rows:
        result = row[field_name]

        if result not in VALID_RESULTS:
            raise ValueError(f"Unsupported result value in {field_name}: {result}")

        counts[result] += 1

    return counts


def render_markdown_report(
    summaries: tuple[ExperimentGroupSummary, ...],
    input_dir: Path,
) -> str:
    """
    Renderuje zbiorczy raport Markdown.

    Args:
        summaries: Podsumowania grup eksperymentalnych.
        input_dir: Katalog wejściowy z wynikami.

    Returns:
        Treść raportu Markdown.
    """
    lines = [
        "# Zbiorcze podsumowanie eksperymentów",
        "",
        f"Katalog wyników: `{input_dir}`",
        "",
        "## Podsumowanie",
        "",
        f"Liczba grup eksperymentalnych: `{len(summaries)}`",
        "",
        "## Tabela wyników",
        "",
        "| CSV | Eksperyment | Partie | Formalne W-B-D | Techniczne W-B-D | Śr. półruchów | Śr. materiał białych | Limit |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for summary in summaries:
        lines.append(
            "| "
            f"`{summary.csv_file}` | "
            f"{summary.experiment_name} | "
            f"{summary.total_matches} | "
            f"{summary.formal_white_wins}-{summary.formal_black_wins}-{summary.formal_draws} | "
            f"{summary.adjudicated_white_wins}-{summary.adjudicated_black_wins}-{summary.adjudicated_draws} | "
            f"{summary.average_half_moves:.2f} | "
            f"{summary.average_final_material_balance:.2f} | "
            f"{summary.move_limit_reached_count} |"
        )

    lines.extend(
        [
            "",
            "## Jak czytać tabelę",
            "",
            "- `Formalne W-B-D` oznacza formalne wyniki: wygrane białych, wygrane czarnych, remisy.",
            "- `Techniczne W-B-D` oznacza wyniki po adjudykacji materiałowej.",
            "- `Śr. materiał białych` to średnia końcowa przewaga materialna z perspektywy białych.",
            "- `Limit` oznacza liczbę partii zakończonych przez limit półruchów.",
            "",
            "## Uwagi interpretacyjne",
            "",
            "- Wynik formalny i techniczny mogą się różnić dla partii przerwanych limitem półruchów.",
            "- Eksperymenty z botem adaptacyjnym należy interpretować razem z plikami `*.metadata.json`, ponieważ zawierają one profile przeciwnika.",
            "- Mała liczba partii wystarcza do smoke testu, ale nie wystarcza do silnych wniosków badawczych.",
            "",
        ]
    )

    return "\n".join(lines)


def summarize_suite(
    input_dir: Path,
) -> tuple[ExperimentGroupSummary, ...]:
    """
    Tworzy zbiorcze podsumowanie wszystkich CSV z katalogu.

    Args:
        input_dir: Katalog z CSV.

    Returns:
        Wszystkie podsumowania grup eksperymentalnych.
    """
    csv_files = discover_csv_files(input_dir)

    summaries: list[ExperimentGroupSummary] = []

    for csv_file in csv_files:
        summaries.extend(summarize_csv_file(csv_file))

    return tuple(summaries)


def write_markdown_report(
    content: str,
    output_path: Path,
) -> Path:
    """
    Zapisuje raport Markdown.

    Args:
        content: Treść raportu.
        output_path: Ścieżka wyjściowa.

    Returns:
        Ścieżka do zapisanego pliku.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    return output_path


def resolve_output_path(
    input_dir: Path,
    output_md: str | None,
) -> Path:
    """
    Wyznacza ścieżkę wyjściową raportu.

    Args:
        input_dir: Katalog wyników.
        output_md: Opcjonalna ścieżka podana przez użytkownika.

    Returns:
        Ścieżka do pliku Markdown.
    """
    if output_md is not None:
        return Path(output_md)

    return input_dir / "suite_summary.md"


def _to_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"Invalid integer value in {field_name}: {value}") from error


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def _average(values: list[int]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def main() -> None:
    args = parse_args()

    input_dir = Path(args.input_dir)
    output_path = resolve_output_path(
        input_dir=input_dir,
        output_md=args.output_md,
    )

    summaries = summarize_suite(input_dir)

    if not summaries:
        print(f"Nie znaleziono danych CSV w katalogu: {input_dir}")
        raise SystemExit(1)

    report = render_markdown_report(
        summaries=summaries,
        input_dir=input_dir,
    )

    saved_path = write_markdown_report(
        content=report,
        output_path=output_path,
    )

    print("Zapisano zbiorcze podsumowanie:")
    print(saved_path)


if __name__ == "__main__":
    main()