from adaptive_chess.ui.results_presenter import games_html, outcome, overview


def test_legacy_move_limit_draw_is_presented_as_unfinished():
    record = {"result": "1/2-1/2", "reached_move_limit": "True"}
    assert outcome(record) == "Przerwane limitem"
    assert outcome({"result": "1/2-1/2"}) == "Remisy"


def test_result_tables_escape_user_supplied_names():
    html = games_html(
        [{"result": "1-0", "white_bot_name": "<script>alert(1)</script>"}]
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_folder_has_a_clear_explanation(tmp_path):
    assert "Brak zakończonych partii" in overview(tmp_path)
