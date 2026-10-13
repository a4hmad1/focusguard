"""High-End Professional Stylesheets for FocusGuard (Modern Dark & Light Themes).

Designed following modern minimalist desktop software aesthetics (Linear / Raycast / GitHub):
subtle borders, refined typography, harmonious palettes, and clean contrast.
"""

# ==============================================================================
# MODERN OBSIDIAN DARK THEME
# ==============================================================================
FORMAL_DARK_THEME_QSS = """
/* Base Global */
QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
}

QMainWindow, QDialog {
    background-color: #0d1117;
}

/* Cards and Panels */
QFrame.card, QGroupBox, QFrame#sessions_frame, QFrame#add_frame, QFrame#sched_card, QFrame#settings_card, QFrame#stat_card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px;
}

QFrame#timer_widget {
    padding: 0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: #8b949e;
    font-weight: 600;
    font-size: 12px;
}

/* Sidebar Navigation */
QFrame#sidebar {
    background-color: #090d13;
    border-right: 1px solid #21262d;
}

QListWidget#nav_list {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#nav_list::item {
    color: #8b949e;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 2px 6px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid transparent;
}

QListWidget#nav_list::item:hover {
    background-color: #161b22;
    color: #f0f6fc;
}

QListWidget#nav_list::item:selected {
    background-color: #1f2937;
    color: #ffffff;
    border: 1px solid #388bfd;
}

/* Header bar */
QFrame#header_bar {
    background-color: #090d13;
    border-bottom: 1px solid #21262d;
    padding: 6px 20px;
}

/* Typography */
QLabel {
    background-color: transparent;
}

QLabel.heading_large {
    font-size: 18px;
    font-weight: 700;
    color: #f0f6fc;
    letter-spacing: -0.3px;
}

QLabel.heading_medium {
    font-size: 14px;
    font-weight: 600;
    color: #f0f6fc;
}

QLabel.subtext {
    color: #8b949e;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid rgba(240, 246, 252, 0.1);
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #2ea043;
}

QPushButton:pressed {
    background-color: #1b6d2d;
}

QPushButton:disabled {
    background-color: #21262d;
    color: #484f58;
    border-color: #30363d;
}

QPushButton.primary {
    background-color: #1f6feb;
    border-color: #388bfd;
    color: #ffffff;
}

QPushButton.primary:hover {
    background-color: #388bfd;
}

QPushButton.secondary {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #c9d1d9;
}

QPushButton.secondary:hover {
    background-color: #30363d;
    color: #f0f6fc;
}

QPushButton.danger {
    background-color: #da3633;
    border: 1px solid #f85149;
    color: #ffffff;
}

QPushButton.danger:hover {
    background-color: #b62324;
}

QPushButton.success {
    background-color: #238636;
    border: 1px solid #2ea043;
    color: #ffffff;
}

QPushButton.success:hover {
    background-color: #2ea043;
}

/* Inputs and Selects */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    color: #f0f6fc;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
    border: 1px solid #58a6ff;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    color: #f0f6fc;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    color: #e6edf3;
    selection-background-color: #1f2937;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #30363d;
    font-weight: 600;
    font-size: 12px;
}

QScrollBar:vertical {
    background: #0d1117;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #8b949e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Badges */
QLabel.badge_active {
    background-color: rgba(46, 160, 67, 0.15);
    color: #3fb950;
    border: 1px solid rgba(46, 160, 67, 0.4);
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 11px;
}

QLabel.badge_blocked {
    background-color: rgba(248, 81, 73, 0.15);
    color: #f85149;
    border: 1px solid rgba(248, 81, 73, 0.4);
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 11px;
}

QLabel.badge_muted {
    background-color: #21262d;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 11px;
}
"""

# ==============================================================================
# MODERN CRISP WHITE LIGHT THEME
# ==============================================================================
FORMAL_LIGHT_THEME_QSS = """
/* Base Global */
QWidget {
    background-color: #f6f8fa;
    color: #1f2328;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: #0969da;
    selection-color: #ffffff;
}

QMainWindow, QDialog {
    background-color: #f6f8fa;
}

/* Cards and Panels */
QFrame.card, QGroupBox, QFrame#sessions_frame, QFrame#add_frame, QFrame#sched_card, QFrame#settings_card, QFrame#stat_card {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    padding: 14px;
}

QFrame#timer_widget {
    padding: 0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: #656d76;
    font-weight: 600;
    font-size: 12px;
}

/* Sidebar Navigation */
QFrame#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #d0d7de;
}

QListWidget#nav_list {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#nav_list::item {
    color: #656d76;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 2px 6px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid transparent;
}

QListWidget#nav_list::item:hover {
    background-color: #f6f8fa;
    color: #1f2328;
}

QListWidget#nav_list::item:selected {
    background-color: #f6f8fa;
    color: #0969da;
    border: 1px solid #0969da;
}

/* Header bar */
QFrame#header_bar {
    background-color: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 6px 20px;
}

/* Typography */
QLabel {
    background-color: transparent;
}

QLabel.heading_large {
    font-size: 18px;
    font-weight: 700;
    color: #1f2328;
    letter-spacing: -0.3px;
}

QLabel.heading_medium {
    font-size: 14px;
    font-weight: 600;
    color: #1f2328;
}

QLabel.subtext {
    color: #656d76;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #1f883d;
    color: #ffffff;
    border: 1px solid rgba(31, 35, 40, 0.15);
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #1a7f37;
}

QPushButton:pressed {
    background-color: #166e2f;
}

QPushButton:disabled {
    background-color: #eaeef2;
    color: #8c959f;
    border-color: #d0d7de;
}

QPushButton.primary {
    background-color: #0969da;
    border-color: #0969da;
    color: #ffffff;
}

QPushButton.primary:hover {
    background-color: #0860ca;
}

QPushButton.secondary {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    color: #24292f;
}

QPushButton.secondary:hover {
    background-color: #f3f4f6;
    border-color: #afb8c1;
}

QPushButton.danger {
    background-color: #cf222e;
    border: 1px solid #a40e26;
    color: #ffffff;
}

QPushButton.danger:hover {
    background-color: #a40e26;
}

QPushButton.success {
    background-color: #1f883d;
    border: 1px solid #1a7f37;
    color: #ffffff;
}

QPushButton.success:hover {
    background-color: #1a7f37;
}

/* Inputs and Selects */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 10px;
    color: #1f2328;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
    border: 1px solid #0969da;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    color: #1f2328;
    selection-background-color: #0969da;
    selection-color: #ffffff;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    gridline-color: #eaeef2;
    color: #1f2328;
    selection-background-color: #f6f8fa;
    selection-color: #0969da;
}

QHeaderView::section {
    background-color: #f6f8fa;
    color: #656d76;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #d0d7de;
    font-weight: 600;
    font-size: 12px;
}

QScrollBar:vertical {
    background: #f6f8fa;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #d0d7de;
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #656d76;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Badges */
QLabel.badge_active {
    background-color: #dafbe1;
    color: #1a7f37;
    border: 1px solid #4ac26b;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 11px;
}

QLabel.badge_blocked {
    background-color: #ffebe9;
    color: #cf222e;
    border: 1px solid #ff8182;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 11px;
}

QLabel.badge_muted {
    background-color: #f6f8fa;
    color: #656d76;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 11px;
}
"""

DARK_THEME_QSS = FORMAL_DARK_THEME_QSS
LIGHT_THEME_QSS = FORMAL_LIGHT_THEME_QSS

def get_theme_stylesheet(theme_name: str) -> str:
    """Return the stylesheet corresponding to theme_name ('white'/'light' or 'black'/'dark')."""
    if theme_name.lower() in ("white", "light"):
        return FORMAL_LIGHT_THEME_QSS
    return FORMAL_DARK_THEME_QSS
