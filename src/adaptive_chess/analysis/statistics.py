from collections.abc import Sequence
from dataclasses import dataclass

from adaptive_chess.experiments.match_runner import MatchResult


VALID_RESULTS = {"1-0", "0-1", "1/2-1/2"}


@dataclass(frozen=True)
class MatchStatistics:
    """
    Podstawowe statystyki obliczone dla serii partii.

    Obiekt jest niemodyfikowalny, ponieważ reprezentuje wynik analizy
    wykonanej na konkretnej kolekcji partii.
    """

    total_matches: int
    white_wins: int
    black_wins: int
    draws: int
    average_half_moves: float
    average_final_material_balance: float
    move_limit_reached_count: int


def calculate_result_counts(matches: Sequence[MatchResult]) -> dict[str, int]:
    """
    Liczy liczbę zwycięstw białych, zwycięstw czarnych i remisów.

    Args:
        matches: Kolekcja wyników partii.

    Returns:
        Słownik z licznikami wyników:
        - '1-0': zwycięstwa białych,
        - '0-1': zwycięstwa czarnych,
        - '1/2-1/2': remisy.

    Raises:
        ValueError: Jeśli wynik partii ma nieznany format.
    """
    counts = {
        "1-0": 0,
        "0-1": 0,
        "1/2-1/2": 0,
    }

    for match in matches:
        if match.result not in VALID_RESULTS:
            raise ValueError(f"Unsupported match result: {match.result}")

        counts[match.result] += 1

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
        Obiekt MatchStatistics zawierający podstawowe statystyki.
    """
    result_counts = calculate_result_counts(matches)

    return MatchStatistics(
        total_matches=len(matches),
        white_wins=result_counts["1-0"],
        black_wins=result_counts["0-1"],
        draws=result_counts["1/2-1/2"],
        average_half_moves=calculate_average_half_moves(matches),
        average_final_material_balance=calculate_average_final_material_balance(
            matches
        ),
        move_limit_reached_count=count_move_limit_reached(matches),
    )