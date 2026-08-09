import csv
from collections.abc import Sequence
from pathlib import Path

from adaptive_chess.experiments.match_runner import MatchResult


MATCH_RESULT_FIELDNAMES = [
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
]


def match_result_to_csv_row(
    match: MatchResult,
    match_index: int,
    experiment_name: str = "",
) -> dict[str, str | int | bool]:
    """
    Zamienia wynik pojedynczej partii na wiersz CSV.

    Args:
        match: Wynik partii.
        match_index: Numer partii w serii.
        experiment_name: Nazwa eksperymentu albo konfiguracji.

    Returns:
        Słownik reprezentujący jeden wiersz CSV.
    """
    if match_index < 1:
        raise ValueError("match_index must be at least 1.")

    return {
        "experiment_name": experiment_name,
        "match_index": match_index,
        "white_bot_name": match.white_bot_name,
        "black_bot_name": match.black_bot_name,
        "result": match.result,
        "adjudicated_result": match.adjudicated_result,
        "termination_reason": match.termination_reason.value,
        "half_moves": match.half_moves,
        "final_material_balance": match.final_material_balance,
        "reached_move_limit": match.reached_move_limit,
        "moves_uci": " ".join(match.moves_uci),
        "material_balances": " ".join(str(value) for value in match.material_balances),
        "position_scores": " ".join(str(value) for value in match.position_scores),
        "final_fen": match.final_fen,
    }


def export_match_results_to_csv(
    matches: Sequence[MatchResult],
    output_path: str | Path,
    experiment_name: str = "",
) -> Path:
    """
    Zapisuje jedną serię wyników partii do pliku CSV.

    Args:
        matches: Wyniki partii.
        output_path: Ścieżka do pliku CSV.
        experiment_name: Nazwa eksperymentu zapisywana w każdym wierszu.

    Returns:
        Ścieżka do zapisanego pliku.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=MATCH_RESULT_FIELDNAMES)
        writer.writeheader()

        for index, match in enumerate(matches, start=1):
            writer.writerow(
                match_result_to_csv_row(
                    match=match,
                    match_index=index,
                    experiment_name=experiment_name,
                )
            )

    return output_file


def export_match_series_collection_to_csv(
    series_collection: Sequence[tuple[str, Sequence[MatchResult]]],
    output_path: str | Path,
) -> Path:
    """
    Zapisuje wiele serii wyników partii do jednego pliku CSV.

    Args:
        series_collection: Kolekcja par:
            - nazwa eksperymentu,
            - wyniki partii.
        output_path: Ścieżka do pliku CSV.

    Returns:
        Ścieżka do zapisanego pliku.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=MATCH_RESULT_FIELDNAMES)
        writer.writeheader()

        for experiment_name, matches in series_collection:
            for index, match in enumerate(matches, start=1):
                writer.writerow(
                    match_result_to_csv_row(
                        match=match,
                        match_index=index,
                        experiment_name=experiment_name,
                    )
                )

    return output_file