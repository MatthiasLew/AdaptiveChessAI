from adaptive_chess.ui.theme import DARK_THEME_STYLESHEET


def test_dark_theme_contains_core_widgets():
    assert "QMainWindow" in DARK_THEME_STYLESHEET
    assert "QPushButton" in DARK_THEME_STYLESHEET
    assert "QFrame#Panel" in DARK_THEME_STYLESHEET