import pytest

from adaptive_chess.analysis.statistics import (
    calculate_average_final_material_balance,
    calculate_average_half_moves,
    calculate_result_counts,
    count_move_limit_reached,
    summarize_matches,
)
from adaptive_chess.experiments.match_runner import MatchResult


def create_match_result(
    result: str,
    half_moves: int,
    final_material_balance: int,
    reached_move_limit: bool = False,
) -> MatchResult:
    return MatchResult(
        white_bot_name="WhiteBot",
        black_bot_name="BlackBot",
        result=result,
        half_moves=half_moves,
        moves_uci=tuple("a2a3" for _ in range(half_moves)),
        material_balances=tuple(0 for _ in range(half_moves)),
        position_scores=tuple(0.0 for _ in range(half_moves)),
        final_material_balance=final_material_balance,
        final_fen="dummy-fen",
        reached_move_limit=reached_move_limit,
    )


def test_calculate_result_counts():
    matches = [
        create_match_result("1-0", 20, 3),
        create_match_result("0-1", 30, -5),
        create_match_result("1/2-1/2", 40, 0),
        create_match_result("1/2-1/2", 50, 1),
    ]

    counts = calculate_result_counts(matches)

    assert counts["1-0"] == 1
    assert counts["0-1"] == 1
    assert counts["1/2-1/2"] == 2


def test_calculate_result_counts_rejects_unknown_result():
    matches = [
        create_match_result("invalid", 20, 0),
    ]

    with pytest.raises(ValueError):
        calculate_result_counts(matches)


def test_calculate_average_half_moves():
    matches = [
        create_match_result("1-0", 10, 1),
        create_match_result("0-1", 20, -1),
        create_match_result("1/2-1/2", 30, 0),
    ]

    assert calculate_average_half_moves(matches) == 20.0


def test_calculate_average_half_moves_for_empty_list():
    assert calculate_average_half_moves([]) == 0.0


def test_calculate_average_final_material_balance():
    matches = [
        create_match_result("1-0", 10, 3),
        create_match_result("0-1", 20, -6),
        create_match_result("1/2-1/2", 30, 0),
    ]

    assert calculate_average_final_material_balance(matches) == -1.0


def test_calculate_average_final_material_balance_for_empty_list():
    assert calculate_average_final_material_balance([]) == 0.0


def test_count_move_limit_reached():
    matches = [
        create_match_result("1-0", 10, 1, reached_move_limit=False),
        create_match_result("1/2-1/2", 100, 0, reached_move_limit=True),
        create_match_result("1/2-1/2", 100, -1, reached_move_limit=True),
    ]

    assert count_move_limit_reached(matches) == 2


def test_summarize_matches():
    matches = [
        create_match_result("1-0", 10, 3, reached_move_limit=False),
        create_match_result("0-1", 20, -3, reached_move_limit=False),
        create_match_result("1/2-1/2", 30, 0, reached_move_limit=True),
    ]

    summary = summarize_matches(matches)

    assert summary.total_matches == 3
    assert summary.white_wins == 1
    assert summary.black_wins == 1
    assert summary.draws == 1
    assert summary.average_half_moves == 20.0
    assert summary.average_final_material_balance == 0.0
    assert summary.move_limit_reached_count == 1


def test_summarize_empty_matches():
    summary = summarize_matches([])

    assert summary.total_matches == 0
    assert summary.white_wins == 0
    assert summary.black_wins == 0
    assert summary.draws == 0
    assert summary.average_half_moves == 0.0
    assert summary.average_final_material_balance == 0.0
    assert summary.move_limit_reached_count == 0