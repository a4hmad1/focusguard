"""Reusable Modern Pill Badge Widget for Tables and Lists."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

def make_badge(text: str, badge_type: str) -> QWidget:
    """Create a styled centered pill badge widget.
    
    badge_type can be: 'running', 'idle', 'protected', 'blocked', 'allowed', 'category', 'active', 'muted'
    """
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignCenter)

    lbl = QLabel(text)
    lbl.setProperty("badge", badge_type)
    lbl.setAlignment(Qt.AlignCenter)
    layout.addWidget(lbl)
    return container
