from pathlib import Path

import pytest

from adaptive_chess.ui.results_loader import (
    ResultFileInfo,
    discover_result_files,
    find_preferred_preview_file,
    format_file_size,
    read_text_preview,
    summarize_results_folder,
)


def test_summarize_results_folder_returns_missing_folder_summary(tmp_path):
    summary = summarize_results_folder(
        folder="missing",
        project_root=tmp_path,
    )

    assert summary.exists is False
    assert summary.folder == tmp_path / "missing"
    assert summary.files == ()
    assert summary.preferred_preview_file is None


def test_summarize_results_folder_rejects_file_path(tmp_path):
    file_path = tmp_path / "not_a_folder.txt"
    file_path.write_text("test", encoding="utf-8")

    with pytest.raises(ValueError):
        summarize_results_folder(file_path)


def test_discover_result_files_finds_supported_files(tmp_path):
    (tmp_path / "summary.md").write_text("# Summary", encoding="utf-8")
    (tmp_path / "data.csv").write_text("a,b\n1,2", encoding="utf-8")
    (tmp_path / "metadata.json").write_text("{}", encoding="utf-8")
    (tmp_path / "chart.png").write_bytes(b"png")
    (tmp_path / "ignored.exe").write_bytes(b"exe")

    files = discover_result_files(tmp_path)
    names = {file_info.name for file_info in files}

    assert names == {
        "summary.md",
        "data.csv",
        "metadata.json",
        "chart.png",
    }


def test_discover_result_files_searches_subdirectories(tmp_path):
    nested = tmp_path / "charts"
    nested.mkdir()
    (nested / "chart.png").write_bytes(b"png")

    files = discover_result_files(tmp_path)

    assert len(files) == 1
    assert files[0].name == "chart.png"


def test_find_preferred_preview_file_prefers_suite_summary():
    suite_summary = ResultFileInfo(
        name="suite_summary.md",
        path=Path("suite_summary.md"),
        category="Markdown",
        size_bytes=10,
    )
    csv_file = ResultFileInfo(
        name="results.csv",
        path=Path("results.csv"),
        category="CSV",
        size_bytes=10,
    )

    preferred = find_preferred_preview_file((csv_file, suite_summary))

    assert preferred == suite_summary


def test_find_preferred_preview_file_prefers_markdown_before_csv():
    markdown = ResultFileInfo(
        name="report.md",
        path=Path("report.md"),
        category="Markdown",
        size_bytes=10,
    )
    csv_file = ResultFileInfo(
        name="results.csv",
        path=Path("results.csv"),
        category="CSV",
        size_bytes=10,
    )

    preferred = find_preferred_preview_file((csv_file, markdown))

    assert preferred == markdown


def test_find_preferred_preview_file_returns_none_for_empty_files():
    assert find_preferred_preview_file(()) is None


def test_read_text_preview_reads_text_file(tmp_path):
    file_path = tmp_path / "report.md"
    file_path.write_text("# Report", encoding="utf-8")

    preview = read_text_preview(file_path)

    assert preview == "# Report"


def test_read_text_preview_truncates_long_file(tmp_path):
    file_path = tmp_path / "report.txt"
    file_path.write_text("a" * 100, encoding="utf-8")

    preview = read_text_preview(
        path=file_path,
        max_characters=10,
    )

    assert preview.startswith("a" * 10)
    assert "[podgląd skrócony]" in preview


def test_read_text_preview_returns_message_for_image(tmp_path):
    file_path = tmp_path / "chart.png"
    file_path.write_bytes(b"png")

    preview = read_text_preview(file_path)

    assert "Podgląd tego typu pliku nie jest dostępny" in preview


def test_format_file_size_formats_bytes():
    assert format_file_size(512) == "512 B"


def test_format_file_size_formats_kilobytes():
    assert format_file_size(2048) == "2.0 KB"


def test_format_file_size_formats_megabytes():
    assert format_file_size(2 * 1024 * 1024) == "2.0 MB"