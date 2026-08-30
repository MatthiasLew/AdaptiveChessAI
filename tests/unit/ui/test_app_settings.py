from adaptive_chess.ui.app_settings import AppSettings


def test_default_app_settings_are_stable():
    settings = AppSettings()

    assert settings.default_bot == "random"
    assert settings.default_human_color == "white"
    assert settings.default_depth == 1
    assert settings.default_experiment_output_dir == "results/gui_experiments"