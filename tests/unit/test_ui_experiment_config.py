from pathlib import Path

import pytest

from adaptive_chess.ui.experiment_config import (
    ExperimentKind,
    ExperimentRunConfig,
    build_experiment_command,
    resolve_output_dir,
    validate_experiment_run_config,
)


def test_validate_experiment_run_config_accepts_valid_config():
    config = ExperimentRunConfig(
        matches=1,
        max_half_moves=10,
        depth=1,
        output_dir="results/gui",
    )

    validate_experiment_run_config(config)


def test_validate_experiment_run_config_rejects_invalid_matches():
    config = ExperimentRunConfig(
        matches=0,
        max_half_moves=10,
        depth=1,
        output_dir="results/gui",
    )

    with pytest.raises(ValueError):
        validate_experiment_run_config(config)


def test_validate_experiment_run_config_rejects_invalid_max_half_moves():
    config = ExperimentRunConfig(
        matches=1,
        max_half_moves=0,
        depth=1,
        output_dir="results/gui",
    )

    with pytest.raises(ValueError):
        validate_experiment_run_config(config)


def test_validate_experiment_run_config_rejects_invalid_depth():
    config = ExperimentRunConfig(
        matches=1,
        max_half_moves=10,
        depth=0,
        output_dir="results/gui",
    )

    with pytest.raises(ValueError):
        validate_experiment_run_config(config)


def test_validate_experiment_run_config_rejects_empty_output_dir():
    config = ExperimentRunConfig(
        matches=1,
        max_half_moves=10,
        depth=1,
        output_dir="   ",
    )

    with pytest.raises(ValueError):
        validate_experiment_run_config(config)


def test_build_experiment_command_for_full_suite(tmp_path):
    config = ExperimentRunConfig(
        matches=2,
        max_half_moves=20,
        depth=1,
        output_dir="results/gui",
    )

    command = build_experiment_command(
        experiment_kind=ExperimentKind.FULL_SUITE,
        config=config,
        project_root=tmp_path,
    )

    assert command[0] == str(tmp_path / "scripts" / "run_full_experiment_suite.py")
    assert "--output-dir" in command
    assert "results/gui" in command
    assert "--matches" in command
    assert "2" in command
    assert "--max-half-moves" in command
    assert "20" in command
    assert "--depths" in command
    assert "1" in command


def test_build_experiment_command_for_random_vs_minimax(tmp_path):
    config = ExperimentRunConfig(
        matches=2,
        max_half_moves=20,
        depth=1,
        output_dir="results/gui",
    )

    command = build_experiment_command(
        experiment_kind=ExperimentKind.RANDOM_VS_MINIMAX,
        config=config,
        project_root=tmp_path,
    )

    assert command[0] == str(tmp_path / "scripts" / "run_random_vs_minimax_series.py")
    assert "--output-csv" in command

    output_csv = command[command.index("--output-csv") + 1]

    assert Path(output_csv) == Path("results/gui") / "random_vs_minimax_gui.csv"

def test_build_experiment_command_for_random_vs_adaptive(tmp_path):
    config = ExperimentRunConfig(
        matches=2,
        max_half_moves=20,
        depth=1,
        output_dir="results/gui",
    )

    command = build_experiment_command(
        experiment_kind=ExperimentKind.RANDOM_VS_ADAPTIVE,
        config=config,
        project_root=tmp_path,
    )

    assert command[0] == str(tmp_path / "scripts" / "run_random_vs_adaptive_series.py")
    assert "--output-csv" in command

    output_csv = command[command.index("--output-csv") + 1]

    assert Path(output_csv) == Path("results/gui") / "random_vs_adaptive_gui.csv"

def test_build_experiment_command_for_static_vs_adaptive(tmp_path):
    config = ExperimentRunConfig(
        matches=2,
        max_half_moves=20,
        depth=1,
        output_dir="results/gui",
    )

    command = build_experiment_command(
        experiment_kind=ExperimentKind.STATIC_VS_ADAPTIVE,
        config=config,
        project_root=tmp_path,
    )

    assert command[0] == str(tmp_path / "scripts" / "run_static_vs_adaptive_series.py")
    assert "--output-csv" in command

    output_csv = command[command.index("--output-csv") + 1]

    assert Path(output_csv) == Path("results/gui") / "static_vs_adaptive_gui.csv"

def test_build_experiment_command_rejects_unknown_experiment_kind():
    config = ExperimentRunConfig(
        matches=1,
        max_half_moves=10,
        depth=1,
        output_dir="results/gui",
    )

    with pytest.raises(ValueError):
        build_experiment_command(
            experiment_kind="unknown",
            config=config,
        )


def test_resolve_output_dir_returns_absolute_path_for_relative_dir(tmp_path):
    resolved = resolve_output_dir(
        output_dir="results/gui",
        project_root=tmp_path,
    )

    assert resolved == tmp_path / "results" / "gui"


def test_resolve_output_dir_keeps_absolute_path(tmp_path):
    absolute_path = tmp_path / "custom"

    resolved = resolve_output_dir(
        output_dir=absolute_path,
        project_root=Path("ignored"),
    )

    assert resolved == absolute_path