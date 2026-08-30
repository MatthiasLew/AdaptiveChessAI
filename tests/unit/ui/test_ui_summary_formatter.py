import chess
import pytest

from adaptive_chess.ui.summary_formatter import (
    color_to_polish,
    describe_material_balance,
    describe_result,
)


def test_color_to_polish_returns_white():
    assert color_to_polish(chess.WHITE) == "białe"


def test_color_to_polish_returns_black():
    assert color_to_polish(chess.BLACK) == "czarne"


def test_color_to_polish_rejects_invalid_color():
    with pytest.raises(ValueError):
        color_to_polish("white")


def test_describe_result_describes_white_win():
    assert describe_result("1-0") == "Wygrana białych"


def test_describe_result_describes_black_win():
    assert describe_result("0-1") == "Wygrana czarnych"


def test_describe_result_describes_draw():
    assert describe_result("1/2-1/2") == "Remis"


def test_describe_result_describes_unfinished_game():
    assert describe_result("*") == "Partia bez rozstrzygnięcia"


def test_describe_material_balance_for_white_advantage():
    assert describe_material_balance(3) == "Białe +3"


def test_describe_material_balance_for_black_advantage():
    assert describe_material_balance(-5) == "Czarne +5"


def test_describe_material_balance_for_equal_material():
    assert describe_material_balance(0) == "Równy materiał"
