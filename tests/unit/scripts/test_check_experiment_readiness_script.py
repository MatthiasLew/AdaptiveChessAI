from pathlib import Path
import sys

from scripts.check_experiment_readiness import (
    REQUIRED_DIRS,
    REQUIRED_FILES,
    build_smoke_suite_command,
    build_test_command,
    collect_readiness_checks,
    has_failures,
)


def create_required_structure(project_root: Path) -> None:
    for relative_dir in REQUIRED_DIRS:
        (project_root / relative_dir).mkdir(parents=True, exist_ok=True)

    for relative_file in REQUIRED_FILES:
        file_path = project_root / relative_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("", encoding="utf-8")


def test_collect_readiness_checks_passes_when_required_paths_exist(tmp_path):
    create_required_structure(tmp_path)

    checks = collect_readiness_checks(tmp_path)

    assert checks
    assert has_failures(checks) is False
    assert all(check.exists for check in checks)


def test_collect_readiness_checks_detects_missing_paths(tmp_path):
    checks = collect_readiness_checks(tmp_path)

    assert checks
    assert has_failures(checks) is True
    assert any(not check.exists for check in checks)


def test_build_test_command_uses_current_python_executable():
    command = build_test_command()

    assert command == [
        sys.executable,
        "-m",
        "pytest",
    ]


def test_build_smoke_suite_command_skips_charts_by_default(tmp_path):
    command = build_smoke_suite_command(
        project_root=tmp_path,
        output_dir="results/readiness_smoke",
        include_charts=False,
    )

    assert command[0] == sys.executable
    assert str(tmp_path / "scripts" / "run_full_experiment_suite.py") in command
    assert "--output-dir" in command
    assert "results/readiness_smoke" in command
    assert "--matches" in command
    assert "1" in command
    assert "--max-half-moves" in command
    assert "10" in command
    assert "--depths" in command
    assert "--skip-charts" in command


def test_build_smoke_suite_command_can_include_charts(tmp_path):
    command = build_smoke_suite_command(
        project_root=tmp_path,
        output_dir="results/readiness_smoke",
        include_charts=True,
    )

    assert "--skip-charts" not in command