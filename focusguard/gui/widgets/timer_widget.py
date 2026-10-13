"""Formal Focus Timer and Countdown Widget.

Provides high-precision countdown display, preset selection (5m, 15m, 25m, 45m, 1h),
custom duration parsing, and live state synchronization.
"""

from datetime import timedelta
from typing import List, Tuple, Optional
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from focusguard.core.duration import parse_duration, format_time_remaining


class TimerWidget(QFrame):
    session_start_requested = Signal(timedelta, str)  # duration, reason
    session_stop_requested = Signal()

    PRESETS: List[Tuple[str, str]] = [
        ("5 min", "5m"),
        ("15 min", "15m"),
        ("25 min", "25m"),
        ("45 min", "45m"),
        ("1 hour", "1h")
    ]

    def __init__(self):
        super().__init__()
        self.setObjectName("timer_widget")
        self.setProperty("class", "card")
        self.setMinimumHeight(210)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(6)

        self._is_active = False
        self._is_dark = False
        self._selected_preset = "5m"
        self._selected_duration_secs = 5 * 60
        self._total_duration_secs = 5 * 60

        # Header Status Badge
        self.status_badge = QLabel("○  Focus Shield is OFF")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedHeight(28)
        layout.addWidget(self.status_badge, alignment=Qt.AlignHCenter)

        # Digital Countdown Display (Fixed height, tabular font)
        self.digits_label = QLabel("05:00")
        self.digits_label.setAlignment(Qt.AlignCenter)
        self.digits_label.setFixedHeight(50)
        layout.addWidget(self.digits_label, alignment=Qt.AlignHCenter)

        # Plain-English Subtitle
        self.subtitle_label = QLabel("All web browsers are currently unrestricted. Click Start to begin focusing.")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setProperty("class", "subtext")
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignHCenter)

        # Subtle Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        layout.addWidget(self.progress_bar)

        # Friendly Duration Presets Row
        self.presets_row = QHBoxLayout()
        self.presets_row.setSpacing(8)
        self.presets_row.setAlignment(Qt.AlignHCenter)

        self.preset_buttons: List[Tuple[QPushButton, str]] = []
        for label, val in self.PRESETS:
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, v=val: self._on_preset_clicked(v))
            self.presets_row.addWidget(btn)
            self.preset_buttons.append((btn, val))

        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("Custom: e.g. 10m")
        self.custom_input.setFixedWidth(125)
        self.custom_input.setFixedHeight(30)
        self.custom_input.textChanged.connect(self._on_custom_input_changed)
        self.presets_row.addWidget(self.custom_input)

        layout.addLayout(self.presets_row)

        # Prominent Big Action Buttons Row
        self.action_row = QHBoxLayout()
        self.action_row.setSpacing(12)
        self.action_row.setAlignment(Qt.AlignHCenter)

        self.start_btn = QPushButton("▶   START FOCUS SESSION")
        self.start_btn.setFixedHeight(38)
        self.start_btn.setMinimumWidth(250)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: #ffffff;
                border: 1px solid #15803d;
                border-radius: 8px;
                padding: 6px 24px;
                font-weight: 800;
                font-size: 13px;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background-color: #22c55e;
            }
        """)
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.action_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹   STOP FOCUS")
        self.stop_btn.setFixedHeight(38)
        self.stop_btn.setMinimumWidth(190)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                border: 1px solid #b91c1c;
                border-radius: 8px;
                padding: 6px 20px;
                font-weight: 800;
                font-size: 13px;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
        """)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.action_row.addWidget(self.stop_btn)
        self.stop_btn.setVisible(False)

        layout.addLayout(self.action_row)

        self._refresh_visuals()

    def _on_preset_clicked(self, val_str: str):
        td = parse_duration(val_str)
        if td:
            self._selected_preset = val_str
            self._selected_duration_secs = int(td.total_seconds())
            self._total_duration_secs = self._selected_duration_secs
            self.custom_input.blockSignals(True)
            self.custom_input.clear()
            self.custom_input.blockSignals(False)
            if not self._is_active:
                self.digits_label.setText(format_time_remaining(self._selected_duration_secs))
            self._update_preset_buttons_style()

    def _on_custom_input_changed(self, text: str):
        text = text.strip()
        if not text:
            # Restore current selected preset if custom input cleared
            td = parse_duration(self._selected_preset)
            if td:
                self._selected_duration_secs = int(td.total_seconds())
                self._total_duration_secs = self._selected_duration_secs
                if not self._is_active:
                    self.digits_label.setText(format_time_remaining(self._selected_duration_secs))
            self._update_preset_buttons_style()
            return

        td = parse_duration(text)
        if td:
            self._selected_duration_secs = int(td.total_seconds())
            self._total_duration_secs = self._selected_duration_secs
            # Check if it matches an existing preset
            matching = [v for _, v in self.PRESETS if v.lower() == text.lower()]
            self._selected_preset = matching[0] if matching else ""
            if not self._is_active:
                self.digits_label.setText(format_time_remaining(self._selected_duration_secs))
            self._update_preset_buttons_style()

    def _update_preset_buttons_style(self):
        for btn, val in self.preset_buttons:
            is_selected = (val == self._selected_preset)
            if self._is_dark:
                if is_selected:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1f6feb;
                            color: #ffffff;
                            border: 1px solid #388bfd;
                            border-radius: 6px;
                            padding: 4px 14px;
                            font-size: 12px;
                            font-weight: 700;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #21262d;
                            color: #c9d1d9;
                            border: 1px solid #30363d;
                            border-radius: 6px;
                            padding: 4px 14px;
                            font-size: 12px;
                            font-weight: 600;
                        }
                        QPushButton:hover {
                            background-color: #30363d;
                            color: #f0f6fc;
                        }
                    """)
            else:
                if is_selected:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #0969da;
                            color: #ffffff;
                            border: 1px solid #0969da;
                            border-radius: 6px;
                            padding: 4px 14px;
                            font-size: 12px;
                            font-weight: 700;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f6f8fa;
                            color: #24292f;
                            border: 1px solid #d0d7de;
                            border-radius: 6px;
                            padding: 4px 14px;
                            font-size: 12px;
                            font-weight: 600;
                        }
                        QPushButton:hover {
                            background-color: #eaeef2;
                            color: #0969da;
                        }
                    """)

    def _on_start_clicked(self):
        custom_val = self.custom_input.text().strip()
        val = custom_val if custom_val else (self._selected_preset or "5m")
        td = parse_duration(val)
        if not td:
            td = timedelta(minutes=5)
        self._total_duration_secs = int(td.total_seconds())
        self._selected_duration_secs = self._total_duration_secs
        self.session_start_requested.emit(td, f"Focus Session ({val})")

    def _on_stop_clicked(self):
        self.session_stop_requested.emit()

    def get_selected_duration(self) -> timedelta:
        """Return currently configured duration."""
        return timedelta(seconds=self._selected_duration_secs)

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        self._refresh_visuals()

    def _refresh_visuals(self):
        # Digits style
        dig_col = "#f0f6fc" if self._is_dark else "#0f172a"
        self.digits_label.setStyleSheet(f"""
            font-size: 52px;
            font-weight: 800;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            color: {dig_col};
            background: transparent;
            padding: 0;
            margin: 0;
        """)

        # Custom input styling
        if self._is_dark:
            self.custom_input.setStyleSheet("""
                QLineEdit {
                    background-color: #0d1117;
                    color: #f0f6fc;
                    border: 1px solid #30363d;
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1px solid #58a6ff;
                }
            """)
        else:
            self.custom_input.setStyleSheet("""
                QLineEdit {
                    background-color: #ffffff;
                    color: #1f2328;
                    border: 1px solid #d0d7de;
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1px solid #0969da;
                }
            """)

        self._update_preset_buttons_style()

        # Badge and subtitle style
        if self._is_active:
            bg = "#163c22" if self._is_dark else "#dcfce7"
            fg = "#3fb950" if self._is_dark else "#15803d"
            bd = "#238636" if self._is_dark else "#86efac"
            self.status_badge.setText("●  Focus Shield is ACTIVE")
            self.status_badge.setStyleSheet(f"""
                background-color: {bg};
                color: {fg};
                border: 1px solid {bd};
                border-radius: 14px;
                padding: 4px 18px;
                font-size: 12px;
                font-weight: 700;
            """)
            self.subtitle_label.setText("Browsers are locked! Only your Allowed Websites can open. All other sites are blocked.")
            self.subtitle_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #16a34a;")
        else:
            bg = "#21262d" if self._is_dark else "#f1f5f9"
            fg = "#8b949e" if self._is_dark else "#475569"
            bd = "#30363d" if self._is_dark else "#cbd5e1"
            self.status_badge.setText("○  Focus Shield is OFF")
            self.status_badge.setStyleSheet(f"""
                background-color: {bg};
                color: {fg};
                border: 1px solid {bd};
                border-radius: 14px;
                padding: 4px 18px;
                font-size: 12px;
                font-weight: 700;
            """)
            self.subtitle_label.setText("All web browsers are currently unrestricted. Click Start to begin focusing.")
            sub_col = "#8b949e" if self._is_dark else "#64748b"
            self.subtitle_label.setStyleSheet(f"font-size: 13px; font-weight: 500; color: {sub_col};")

    def update_countdown(self, remaining_seconds: float, is_active: bool):
        self._is_active = is_active
        self._refresh_visuals()

        # Disable/enable controls based on session activity
        for btn, _ in self.preset_buttons:
            btn.setEnabled(not is_active)
        self.custom_input.setEnabled(not is_active)

        if is_active and remaining_seconds > 0:
            if remaining_seconds > self._total_duration_secs:
                self._total_duration_secs = int(remaining_seconds)
            self.digits_label.setText(format_time_remaining(remaining_seconds))
            self.start_btn.setVisible(False)
            self.stop_btn.setVisible(True)
            self.stop_btn.setEnabled(True)
            pct = int((remaining_seconds / max(1, self._total_duration_secs)) * 100)
            self.progress_bar.setValue(min(100, max(0, pct)))
        else:
            self.start_btn.setVisible(True)
            self.start_btn.setEnabled(True)
            self.stop_btn.setVisible(False)
            self.progress_bar.setValue(100)
            # Restore configured preset duration rather than hardcoding 25:00
            self.digits_label.setText(format_time_remaining(self._selected_duration_secs))
