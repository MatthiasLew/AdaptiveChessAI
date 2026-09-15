"""Semantic palettes and shared Qt component roles (logical pixels)."""

from collections.abc import Mapping

DARK = {
    "background": "#101820",
    "surface": "#18232e",
    "surface_alt": "#22313f",
    "border": "#405363",
    "text_primary": "#edf3f7",
    "text_secondary": "#b4c3cf",
    "accent": "#246baf",
    "accent_hover": "#307abd",
    "on_accent": "#ffffff",
    "success": "#7dd3ac",
    "warning": "#edc475",
    "danger": "#c14450",
    "board_light": "#e1e7e5",
    "board_dark": "#91a7ad",
}
LIGHT = {
    "background": "#f0f3f6",
    "surface": "#ffffff",
    "surface_alt": "#e7edf2",
    "border": "#a9bac8",
    "text_primary": "#192d3c",
    "text_secondary": "#486070",
    "accent": "#205e98",
    "accent_hover": "#174d7d",
    "on_accent": "#ffffff",
    "success": "#206e50",
    "warning": "#885c15",
    "danger": "#b33745",
    "board_light": "#e1e7e5",
    "board_dark": "#91a7ad",
}


def build_stylesheet(palette: Mapping[str, str]) -> str:
    """Generate both themes from the same component contract."""
    p = palette
    return f"""
QMainWindow, QScrollArea, QStackedWidget {{ background: {p["background"]}; }}
QWidget {{ color: {p["text_primary"]}; font-family: "Segoe UI";
    font-size: 14px; }}
QLabel, QCheckBox {{ background: transparent; }}
QScrollArea {{ border: none; }}
QFrame#Panel, QFrame#Card, QFrame#SectionCard, QFrame#StatCard {{
    background: {p["surface"]}; border: 1px solid {p["border"]};
    border-radius: 10px; }}
QLabel#PageTitle, QLabel#TitleLabel {{ font-size: 28px; font-weight: 700; }}
QLabel#SectionTitle {{ font-size: 18px; font-weight: 600; }}
QLabel#HelperText, QLabel#SubtitleLabel, QLabel#FenLabel {{
    color: {p["text_secondary"]}; font-size: 13px; }}
QLabel#StatusBadge, QLabel#StatusLabel {{ background: {p["surface_alt"]};
    border-radius: 6px; padding: 8px; font-weight: 600; }}
QLabel#SummaryResultLabel, QLabel#StatValue {{ font-size: 26px; font-weight: 700; }}
QLabel#SaveStatusLabel {{ color: {p["success"]}; }}
QPushButton {{ background: {p["surface_alt"]}; color: {p["text_primary"]};
    border: 1px solid {p["border"]}; border-radius: 6px;
    padding: 7px 12px; min-height: 20px; }}
QPushButton:hover {{ border-color: {p["accent_hover"]}; }}
QPushButton#PrimaryButton {{ background: {p["accent"]};
    color: {p["on_accent"]}; border-color: {p["accent"]}; font-weight: 600; }}
QPushButton#PrimaryButton:hover {{ background: {p["accent_hover"]}; }}
QPushButton#SecondaryButton {{ background: {p["surface_alt"]}; }}
QPushButton#DangerButton {{ background: {p["danger"]}; color: {p["on_accent"]}; }}
QPushButton:focus, QToolButton:focus {{ border: 2px solid {p["accent_hover"]}; }}
QPushButton:disabled {{ background: {p["surface_alt"]};
    color: {p["text_secondary"]}; border-color: {p["border"]}; }}
QPushButton#ActionCard {{ text-align: left; padding: 20px; }}
QPushButton#ActionCard[featured="true"] {{ border: 2px solid {p["accent"]};
    background: {p["surface"]}; }}
QPushButton#ActionCard:hover {{ background: {p["surface_alt"]}; }}
QComboBox, QSpinBox, QLineEdit {{ background: {p["surface"]};
    border: 1px solid {p["border"]}; border-radius: 5px; padding: 6px;
    selection-background-color: {p["accent"]}; selection-color: {p["on_accent"]}; }}
QComboBox:focus, QSpinBox:focus, QLineEdit:focus {{ border-color: {p["accent"]}; }}
QComboBox QAbstractItemView {{ background: {p["surface"]};
    selection-background-color: {p["accent"]}; selection-color: {p["on_accent"]}; }}
QTextEdit, QPlainTextEdit, QTextBrowser, QListWidget, QTableView {{
    background: {p["surface"]}; border: 1px solid {p["border"]};
    border-radius: 6px; padding: 8px;
    selection-background-color: {p["accent"]}; selection-color: {p["on_accent"]}; }}
QListWidget::item {{ padding: 5px; }}
QHeaderView::section {{ background: {p["surface_alt"]}; padding: 8px; }}
QTabWidget::pane {{ border: 1px solid {p["border"]}; border-radius: 6px; }}
QTabBar::tab {{ background: {p["surface_alt"]}; padding: 9px 14px; }}
QTabBar::tab:selected {{ background: {p["surface"]};
    border-bottom: 2px solid {p["accent"]}; }}
QToolButton {{ background: transparent; border: 1px solid transparent;
    padding: 6px; color: {p["text_secondary"]}; }}
QToolButton:hover {{ background: {p["surface_alt"]}; }}
QProgressBar {{ border: 1px solid {p["border"]}; border-radius: 5px;
    background: {p["surface_alt"]}; text-align: center; min-height: 20px; }}
QProgressBar::chunk {{ background: {p["accent"]}; border-radius: 4px; }}
QToolTip {{ background: {p["surface"]}; color: {p["text_primary"]};
    border: 1px solid {p["border"]}; padding: 8px; }}
QScrollBar:vertical {{ background: {p["background"]}; width: 12px; }}
QScrollBar::handle:vertical {{ background: {p["border"]}; min-height: 24px;
    border-radius: 5px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QFrame#BoardFrame {{ background: {p["surface_alt"]}; border: none; }}
QLabel#BoardLightSquare {{ background: {p["board_light"]}; }}
QLabel#BoardDarkSquare {{ background: {p["board_dark"]}; }}
QLabel#BoardLastMoveSquare {{ background: #dfc779; }}
QLabel#BoardSelectedSquare {{ background: #f0d781; border: 2px solid #2e5266; }}
QLabel#BoardLegalTargetSquare {{ background: #a5cfab; border: 2px solid #37744c; }}
QLabel#BoardLightSquare, QLabel#BoardDarkSquare, QLabel#BoardLastMoveSquare,
QLabel#BoardSelectedSquare, QLabel#BoardLegalTargetSquare {{ color: #142331;
    font-family: "Segoe UI Symbol"; }}
"""


DARK_THEME_STYLESHEET = build_stylesheet(DARK)
LIGHT_THEME_STYLESHEET = build_stylesheet(LIGHT)


def apply_palette(app, theme: str) -> None:
    from PySide6.QtGui import QColor, QPalette

    colors = LIGHT if theme == "light" else DARK
    palette = QPalette()
    for role, token in (
        (QPalette.ColorRole.Window, "background"),
        (QPalette.ColorRole.WindowText, "text_primary"),
        (QPalette.ColorRole.Base, "surface"),
        (QPalette.ColorRole.AlternateBase, "surface_alt"),
        (QPalette.ColorRole.Text, "text_primary"),
        (QPalette.ColorRole.Button, "surface_alt"),
        (QPalette.ColorRole.ButtonText, "text_primary"),
        (QPalette.ColorRole.Highlight, "accent"),
        (QPalette.ColorRole.HighlightedText, "on_accent"),
        (QPalette.ColorRole.PlaceholderText, "text_secondary"),
    ):
        palette.setColor(role, QColor(colors[token]))
    app.setPalette(palette)
