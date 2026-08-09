import pytest

from adaptive_chess.experiments.adjudication import adjudicate_result_by_material


def test_adjudicate_result_by_material_awards_white_win():
    assert adjudicate_result_by_material(3, material_threshold=3) == "1-0"
    assert adjudicate_result_by_material(9, material_threshold=3) == "1-0"


def test_adjudicate_result_by_material_awards_black_win():
    assert adjudicate_result_by_material(-3, material_threshold=3) == "0-1"
    assert adjudicate_result_by_material(-9, material_threshold=3) == "0-1"


def test_adjudicate_result_by_material_keeps_draw_for_small_advantage():
    assert adjudicate_result_by_material(0, material_threshold=3) == "1/2-1/2"
    assert adjudicate_result_by_material(2, material_threshold=3) == "1/2-1/2"
    assert adjudicate_result_by_material(-2, material_threshold=3) == "1/2-1/2"


def test_adjudicate_result_by_material_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        adjudicate_result_by_material(5, material_threshold=0)