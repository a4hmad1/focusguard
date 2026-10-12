"""Modern Statistic Card Widget for FocusGuard Dashboard."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, title: str, initial_value: str = "0", subtext: str = "", accent_color: str = "#3b82f6"):
        super().__init__()
        self.setObjectName("stat_card")
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: #1e293b;
                border: 1px solid #334155;
                border-top: 3px solid {accent_color};
                border-radius: 10px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        self.title_label = QLabel(title.upper())
        self.title_label.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")

        self.value_label = QLabel(initial_value)
        self.value_label.setStyleSheet("color: #f8fafc; font-size: 28px; font-weight: 700;")

        self.subtext_label = QLabel(subtext)
        self.subtext_label.setStyleSheet("color: #64748b; font-size: 12px;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtext_label)

    def set_value(self, value: str):
        self.value_label.setText(str(value))

    def set_subtext(self, subtext: str):
        self.subtext_label.setText(subtext)
