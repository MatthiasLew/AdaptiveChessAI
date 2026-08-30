from adaptive_chess.ui.screens.experiments_screen import ExperimentsScreen
from adaptive_chess.ui.screens.game_screen import GameScreen


def test_experiments_screen_exposes_settings_api():
    assert callable(
        getattr(
            ExperimentsScreen,
            "set_default_output_dir",
            None,
        )
    )


def test_game_screen_exposes_settings_api():
    assert callable(
        getattr(
            GameScreen,
            "apply_defaults",
            None,
        )
    )


def test_game_screen_exposes_new_game_flow_api():
    assert callable(
        getattr(
            GameScreen,
            "prepare_for_new_game",
            None,
        )
    )
