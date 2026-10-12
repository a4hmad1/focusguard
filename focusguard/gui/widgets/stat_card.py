"""Formal Statistic Card Widget for FocusGuard Dashboard."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, title: str, initial_value: str = "0", subtext: str = "", accent_color: str = "#2563eb"):
        super().__init__()
        self.setObjectName("stat_card")
        self.setProperty("class", "card")
        self.accent_color = accent_color
        self._apply_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("stat_title")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")

        self.value_label = QLabel(initial_value)
        self.value_label.setObjectName("stat_value")
        self.value_label.setStyleSheet("font-size: 26px; font-weight: 800;")

        self.subtext_label = QLabel(subtext)
        self.subtext_label.setObjectName("stat_subtext")
        self.subtext_label.setProperty("class", "subtext")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtext_label)

    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                border-top: 3px solid {self.accent_color};
            }}
        """)

    def set_value(self, value: str):
        self.value_label.setText(str(value))

    def set_subtext(self, subtext: str):
        self.subtext_label.setText(subtext)
