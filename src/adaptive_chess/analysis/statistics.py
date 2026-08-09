from collections.abc import Sequence
from dataclasses import dataclass

from adaptive_chess.experiments.match_runner import MatchResult


VALID_RESULTS = {"1-0", "0-1", "1/2-1/2"}


@dataclass(frozen=True)
class MatchStatistics:
    """
    Podstawowe statystyki obliczone dla serii partii.

    Statystyki rozróżniają wyniki formalne oraz techniczne.
    Wynik formalny pochodzi z zasad gry albo z technicznego remisu po limicie.
    Wynik techniczny może zostać ustalony przez adjudykację materiałową.
    """

    total_matches: int

    white_wins: int
    black_wins: int
    draws: int

    adjudicated_white_wins: int
    adjudicated_black_wins: int
    adjudicated_draws: int

    average_half_moves: float
    average_final_material_balance: float
    move_limit_reached_count: int


def calculate_result_counts(matches: Sequence[MatchResult]) -> dict[str, int]:
    """
    Liczy formalne wyniki partii.

    Args:
        matches: Kolekcja wyników partii.

    Returns:
        Słownik z licznikami wyników formalnych:
        - '1-0',
        - '0-1',
        - '1/2-1/2'.

    Raises:
        ValueError: Jeśli wynik partii ma nieznany format.
    """
    return _calculate_counts_by_field(matches, field_name="result")


def calculate_adjudicated_result_counts(
    matches: Sequence[MatchResult],
) -> dict[str, int]:
    """
    Liczy techniczne wyniki partii po adjudykacji.

    Args:
        matches: Kolekcja wyników partii.

    Returns:
        Słownik z licznikami wyników technicznych:
        - '1-0',
        - '0-1',
        - '1/2-1/2'.

    Raises:
        ValueError: Jeśli wynik techniczny ma nieznany format.
    """
    return _calculate_counts_by_field(matches, field_name="adjudicated_result")


def _calculate_counts_by_field(
    matches: Sequence[MatchResult],
    field_name: str,
) -> dict[str, int]:
    """
    Liczy wyniki na podstawie wskazanego pola obiektu MatchResult.

    Args:
        matches: Kolekcja wyników partii.
        field_name: Nazwa pola, np. 'result' albo 'adjudicated_result'.

    Returns:
        Słownik z licznikami wyników.

    Raises:
        ValueError: Jeśli znaleziony wynik ma nieznany format.
    """
    counts = {
        "1-0": 0,
        "0-1": 0,
        "1/2-1/2": 0,
    }

    for match in matches:
        result = getattr(match, field_name)

        if result not in VALID_RESULTS:
            raise ValueError(f"Unsupported match result: {result}")

        counts[result] += 1

    return counts


def calculate_average_half_moves(matches: Sequence[MatchResult]) -> float:
    """
    Liczy średnią liczbę półruchów w serii partii.

    Args:
        matches: Kolekcja wyników partii.

    Returns:
        Średnia liczba półruchów. Dla pustej listy zwraca 0.0.
    """
    if not matches:
        return 0.0

    return sum(match.half_moves for match in matches) / len(matches)


def calculate_average_final_material_balance(
    matches: Sequence[MatchResult],
) -> float:
    """
    Liczy średnią końcową przewagę materialną z perspektywy białych.

    Args:
        matches: Kolekcja wyników partii.

    Returns:
        Średnia końcowa przewaga materialna.
        Wartość dodatnia oznacza średnią przewagę białych.
        Wartość ujemna oznacza średnią przewagę czarnych.
        Dla pustej listy zwraca 0.0.
    """
    if not matches:
        return 0.0

    return sum(match.final_material_balance for match in matches) / len(matches)


def count_move_limit_reached(matches: Sequence[MatchResult]) -> int:
    """
    Liczy, ile partii zakończyło się przez osiągnięcie limitu półruchów.

    Args:
        matches: Kolekcja wyników partii.

    Returns:
        Liczba partii zakończonych przez limit.
    """
    return sum(1 for match in matches if match.reached_move_limit)


def summarize_matches(matches: Sequence[MatchResult]) -> MatchStatistics:
    """
    Tworzy zbiorcze statystyki dla serii partii.

    Args:
        matches: Kolekcja wyników partii.

    Returns:
        Obiekt MatchStatistics zawierający podstawowe statystyki formalne
        oraz techniczne.
    """
    result_counts = calculate_result_counts(matches)
    adjudicated_counts = calculate_adjudicated_result_counts(matches)

    return MatchStatistics(
        total_matches=len(matches),
        white_wins=result_counts["1-0"],
        black_wins=result_counts["0-1"],
        draws=result_counts["1/2-1/2"],
        adjudicated_white_wins=adjudicated_counts["1-0"],
        adjudicated_black_wins=adjudicated_counts["0-1"],
        adjudicated_draws=adjudicated_counts["1/2-1/2"],
        average_half_moves=calculate_average_half_moves(matches),
        average_final_material_balance=calculate_average_final_material_balance(
            matches
        ),
        move_limit_reached_count=count_move_limit_reached(matches),
    )