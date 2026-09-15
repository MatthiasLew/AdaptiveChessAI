DARK_THEME_STYLESHEET = """
QLabel#BoardLightSquare, QLabel#BoardDarkSquare,
QLabel#BoardSelectedSquare, QLabel#BoardLegalTargetSquare,
QLabel#BoardLastMoveSquare {
    font-family: "Segoe UI Symbol";
    font-size: 38px;
}
QMainWindow {
    background-color: #101820;
}

QWidget {
    background-color: #101820;
    color: #f2f5f7;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 14px;
}

QLabel#TitleLabel {
    font-size: 34px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#SubtitleLabel {
    font-size: 15px;
    color: #b8c7d9;
}

QLabel#SectionTitle {
    font-size: 22px;
    font-weight: 600;
    color: #ffffff;
}

QPushButton {
    background-color: #1f6feb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    min-height: 28px;
}

QPushButton:hover {
    background-color: #388bfd;
}

QPushButton:pressed {
    background-color: #1158c7;
}

QPushButton#SecondaryButton {
    background-color: #30363d;
}

QPushButton#SecondaryButton:hover {
    background-color: #484f58;
}

QPushButton#DangerButton {
    background-color: #da3633;
}

QPushButton#DangerButton:hover {
    background-color: #f85149;
}

QFrame#Panel {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
}

QComboBox,
QSpinBox,
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 5px;
    padding: 6px;
    color: #f2f5f7;
}

QTextEdit,
QPlainTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 5px;
    color: #d0d7de;
}
QFrame#BoardFrame {
    background-color: #0d1117;
    border: 2px solid #30363d;
    border-radius: 8px;
}

QLabel#BoardLightSquare {
    background-color: #d6e0f0;
    color: #101820;
    border: none;
}

QLabel#BoardDarkSquare {
    background-color: #59708a;
    color: #101820;
    border: none;
}

QLabel#StatusLabel {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#FenLabel {
    color: #b8c7d9;
    font-size: 12px;
}
QLabel#BoardLastMoveSquare {
    background-color: #e1bd63;
    color: #101820;
    border: 2px solid #ffe7a1;
}
QLabel#BoardSelectedSquare {
    background-color: #f2cc60;
    color: #101820;
    border: 2px solid #ffffff;
}

QLabel#BoardLegalTargetSquare {
    background-color: #56d364;
    color: #101820;
    border: 2px solid #ffffff;
}
QLabel#SummaryResultLabel {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
}
QLabel#SaveStatusLabel {
    color: #56d364;
    font-size: 12px;
}
"""


LIGHT_THEME_STYLESHEET = DARK_THEME_STYLESHEET
for dark, light in {
    "#101820": "#f5f7fb",
    "#f2f5f7": "#172033",
    "#b8c7d9": "#475569",
    "#161b22": "#ffffff",
    "#0d1117": "#ffffff",
    "#30363d": "#dbe3ef",
    "#d0d7de": "#172033",
    "#484f58": "#cbd5e1",
}.items():
    LIGHT_THEME_STYLESHEET = LIGHT_THEME_STYLESHEET.replace(dark, light)
LIGHT_THEME_STYLESHEET += """
QLabel { color: #172033; background: transparent; }
QLabel#TitleLabel, QLabel#SectionTitle { color: #172033; }
QLabel#BoardLightSquare, QLabel#BoardDarkSquare, QLabel#BoardLastMoveSquare,
QLabel#BoardSelectedSquare, QLabel#BoardLegalTargetSquare { color: #101820; }
QPushButton#SecondaryButton { color: #172033; }
QTextBrowser, QTableView { background: #ffffff; color: #172033; }
"""
DARK_THEME_STYLESHEET += """
QLabel { background: transparent; }
QTextBrowser { background: #0d1117; color: #f2f5f7; padding: 14px; }
QProgressBar { border: 1px solid #59708a; border-radius: 5px; text-align: center; }
QProgressBar::chunk { background: #1f6feb; }
"""
