"""Formal Desktop App Stylesheets (White and Black Themes) for FocusGuard."""

# ==============================================================================
# FORMAL LIGHT THEME (Crisp White / Clean Executive Desktop App)
# ==============================================================================
FORMAL_LIGHT_THEME_QSS = """
/* Base Global */
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QMainWindow, QDialog {
    background-color: #f1f5f9;
}

/* Cards and Groupboxes */
QFrame.card, QGroupBox, QFrame#sessions_frame, QFrame#add_frame, QFrame#sched_card, QFrame#settings_card, QFrame#stat_card {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: #475569;
    font-weight: 700;
    font-size: 12px;
}

/* Navigation Sidebar */
QFrame#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

QListWidget#nav_list {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#nav_list::item {
    color: #334155;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 3px 6px;
    font-weight: 600;
    font-size: 13px;
}

QListWidget#nav_list::item:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

QListWidget#nav_list::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

/* Header bar */
QFrame#header_bar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 20px;
}

/* Headings */
QLabel.heading_large {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.3px;
}

QLabel.heading_medium {
    font-size: 15px;
    font-weight: 700;
    color: #1e293b;
}

QLabel.subtext {
    color: #64748b;
    font-size: 12px;
}

/* Formal Action Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
    border-color: #cbd5e1;
}

QPushButton.secondary {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #1e293b;
}

QPushButton.secondary:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}

QPushButton.danger {
    background-color: #dc2626;
    border-color: #b91c1c;
    color: #ffffff;
}

QPushButton.danger:hover {
    background-color: #b91c1c;
}

QPushButton.success {
    background-color: #16a34a;
    border-color: #15803d;
    color: #ffffff;
}

QPushButton.success:hover {
    background-color: #15803d;
}

/* Form Controls */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 10px;
    color: #0f172a;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
    border-color: #2563eb;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #0f172a;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

/* Formal Data Tables */
QTableWidget, QTableView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    gridline-color: #e2e8f0;
    color: #0f172a;
    selection-background-color: #dbeafe;
    selection-color: #1e3a8a;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #cbd5e1;
    font-weight: 700;
    font-size: 12px;
}

QScrollBar:vertical {
    background: #f1f5f9;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Status Badges */
QLabel.badge_active {
    background-color: #dcfce7;
    color: #15803d;
    border: 1px solid #86efac;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 700;
    font-size: 11px;
}

QLabel.badge_blocked {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 700;
    font-size: 11px;
}

QLabel.badge_muted {
    background-color: #f1f5f9;
    color: #64748b;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 600;
    font-size: 11px;
}
"""

# ==============================================================================
# FORMAL DARK THEME (Sleek Black / Formal Executive Dark Desktop App)
# ==============================================================================
FORMAL_DARK_THEME_QSS = """
/* Base Global */
QWidget {
    background-color: #0b0f19;
    color: #f9fafb;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QMainWindow, QDialog {
    background-color: #0b0f19;
}

/* Cards and Containers */
QFrame.card, QGroupBox, QFrame#sessions_frame, QFrame#add_frame, QFrame#sched_card, QFrame#settings_card, QFrame#stat_card {
    background-color: #161f30;
    border: 1px solid #232f45;
    border-radius: 8px;
    padding: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: #94a3b8;
    font-weight: 700;
    font-size: 12px;
}

/* Navigation Sidebar */
QFrame#sidebar {
    background-color: #0d1322;
    border-right: 1px solid #1e293b;
}

QListWidget#nav_list {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#nav_list::item {
    color: #94a3b8;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 3px 6px;
    font-weight: 600;
    font-size: 13px;
}

QListWidget#nav_list::item:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

QListWidget#nav_list::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

/* Header bar */
QFrame#header_bar {
    background-color: #0d1322;
    border-bottom: 1px solid #1e293b;
    padding: 6px 20px;
}

/* Headings */
QLabel.heading_large {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.3px;
}

QLabel.heading_medium {
    font-size: 15px;
    font-weight: 700;
    color: #f1f5f9;
}

QLabel.subtext {
    color: #94a3b8;
    font-size: 12px;
}

/* Action Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #64748b;
    border-color: #334155;
}

QPushButton.secondary {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #f8fafc;
}

QPushButton.secondary:hover {
    background-color: #334155;
}

QPushButton.danger {
    background-color: #dc2626;
    border-color: #ef4444;
    color: #ffffff;
}

QPushButton.danger:hover {
    background-color: #b91c1c;
}

QPushButton.success {
    background-color: #16a34a;
    border-color: #22c55e;
    color: #ffffff;
}

QPushButton.success:hover {
    background-color: #15803d;
}

/* Form Controls */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 10px;
    color: #f8fafc;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
    border-color: #3b82f6;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #f8fafc;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

/* Data Tables */
QTableWidget, QTableView {
    background-color: #161f30;
    border: 1px solid #232f45;
    border-radius: 6px;
    gridline-color: #232f45;
    color: #f8fafc;
    selection-background-color: rgba(59, 130, 246, 0.25);
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #0d1322;
    color: #94a3b8;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #232f45;
    font-weight: 700;
    font-size: 12px;
}

QScrollBar:vertical {
    background: #0b0f19;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #232f45;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #3b82f6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Badges */
QLabel.badge_active {
    background-color: rgba(34, 197, 94, 0.18);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 700;
    font-size: 11px;
}

QLabel.badge_blocked {
    background-color: rgba(239, 68, 68, 0.18);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 700;
    font-size: 11px;
}

QLabel.badge_muted {
    background-color: rgba(148, 163, 184, 0.12);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: 600;
    font-size: 11px;
}
"""

DARK_THEME_QSS = FORMAL_DARK_THEME_QSS
LIGHT_THEME_QSS = FORMAL_LIGHT_THEME_QSS

def get_theme_stylesheet(theme_name: str) -> str:
    """Return the formal stylesheet corresponding to theme_name ('white'/'light' or 'black'/'dark')."""
    if theme_name.lower() in ("white", "light"):
        return FORMAL_LIGHT_THEME_QSS
    return FORMAL_DARK_THEME_QSS
