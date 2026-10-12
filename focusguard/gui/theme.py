"""Modern Dark Theme Stylesheet for FocusGuard PySide6 GUI."""

DARK_THEME_QSS = """
/* Base Global Styles */
QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

/* Main Window and Containers */
QMainWindow, QDialog {
    background-color: #0f172a;
}

QFrame.card, QGroupBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
    margin-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 12px;
}

/* Navigation Sidebar */
QFrame#sidebar {
    background-color: #0b1120;
    border-right: 1px solid #1e293b;
}

QListWidget#nav_list {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#nav_list::item {
    color: #94a3b8;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 4px 8px;
    font-weight: 600;
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
    background-color: #131d35;
    border-bottom: 1px solid #1e293b;
    padding: 8px 16px;
}

/* Headings */
QLabel.heading_large {
    font-size: 22px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel.heading_medium {
    font-size: 16px;
    font-weight: 600;
    color: #f1f5f9;
}

QLabel.subtext {
    color: #94a3b8;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1d4ed8;
    border-color: #60a5fa;
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
    background-color: #334155;
    border-color: #475569;
    color: #f8fafc;
}

QPushButton.secondary:hover {
    background-color: #475569;
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

/* Input Fields */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background-color: #0b1120;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
    border-color: #3b82f6;
    outline: none;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

/* Tables and Lists */
QTableWidget, QTableView {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    color: #f8fafc;
    selection-background-color: rgba(59, 130, 246, 0.25);
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #334155;
    font-weight: 600;
    font-size: 12px;
}

QScrollBar:vertical {
    background: #0f172a;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Badges */
QLabel.badge_active {
    background-color: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 6px;
    padding: 2px 8px;
    font-weight: 600;
}

QLabel.badge_blocked {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 6px;
    padding: 2px 8px;
    font-weight: 600;
}

QLabel.badge_protected {
    background-color: rgba(14, 165, 233, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(14, 165, 233, 0.3);
    border-radius: 6px;
    padding: 2px 8px;
    font-weight: 600;
}

QLabel.badge_muted {
    background-color: rgba(148, 163, 184, 0.12);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 6px;
    padding: 2px 8px;
    font-weight: 500;
}

/* Tab widget */
QTabWidget::pane {
    border: none;
}

QTabBar::tab {
    background-color: #0b1120;
    color: #94a3b8;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}
"""
