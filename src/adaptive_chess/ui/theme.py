DARK_THEME_STYLESHEET = """
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
"""