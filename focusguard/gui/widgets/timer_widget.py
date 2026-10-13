"""Formal Focus Timer and Countdown Widget."""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from datetime import timedelta
from focusguard.core.duration import parse_duration, format_time_remaining

class TimerWidget(QFrame):
    session_start_requested = Signal(timedelta, str)  # duration, reason
    session_stop_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("timer_widget")
        self.setProperty("class", "card")
        self.setMinimumHeight(275)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(8)

        self._is_active = False
        self._is_dark = False
        self._total_duration_secs = 25 * 60

        # Header Status Badge (solid colors to prevent Linux X11 alpha blending artifacts)
        self.status_badge = QLabel("○  Focus Shield is OFF")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedHeight(28)
        layout.addWidget(self.status_badge, alignment=Qt.AlignHCenter)

        # Digital Countdown Display (Fixed height, crisp system tabular font, no vertical clipping)
        self.digits_label = QLabel("25:00")
        self.digits_label.setAlignment(Qt.AlignCenter)
        self.digits_label.setFixedHeight(56)
        layout.addWidget(self.digits_label, alignment=Qt.AlignHCenter)

        # Plain-English Subtitle
        self.subtitle_label = QLabel("All web browsers are currently unrestricted. Click Start to begin focusing.")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setProperty("class", "subtext")
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignHCenter)

        self._refresh_visuals()

        # Subtle Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        layout.addWidget(self.progress_bar)

        # Friendly Duration Presets
        self.presets_row = QHBoxLayout()
        self.presets_row.setSpacing(8)
        self.presets_row.setAlignment(Qt.AlignHCenter)

        presets = [("25 min", "25m"), ("45 min", "45m"), ("1 hour", "1h"), ("2 hours", "2h")]
        self.preset_buttons = []
        for label, val in presets:
            btn = QPushButton(label)
            btn.setProperty("class", "secondary")
            btn.setFixedHeight(30)
            btn.setStyleSheet("padding: 4px 14px; font-size: 12px; font-weight: 600; border-radius: 6px;")
            btn.clicked.connect(lambda _, v=val: self._on_preset_clicked(v))
            self.presets_row.addWidget(btn)
            self.preset_buttons.append(btn)
        
        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("Custom: e.g. 30m")
        self.custom_input.setFixedWidth(120)
        self.custom_input.setFixedHeight(30)
        self.presets_row.addWidget(self.custom_input)

        layout.addLayout(self.presets_row)

        # Prominent Big Action Buttons Row
        self.action_row = QHBoxLayout()
        self.action_row.setSpacing(12)
        self.action_row.setAlignment(Qt.AlignHCenter)

        self.start_btn = QPushButton("▶   START FOCUS SESSION")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setMinimumWidth(260)
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
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setMinimumWidth(200)
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

        self._is_active = False
        self._total_duration_secs = 25 * 60

    def _on_preset_clicked(self, val_str: str):
        td = parse_duration(val_str)
        if td:
            self._total_duration_secs = int(td.total_seconds())
            self.digits_label.setText(format_time_remaining(self._total_duration_secs))
            self.custom_input.setText(val_str)

    def _on_start_clicked(self):
        val = self.custom_input.text().strip() or "25m"
        td = parse_duration(val)
        if not td:
            td = timedelta(minutes=25)
        self._total_duration_secs = int(td.total_seconds())
        self.session_start_requested.emit(td, f"Focus Session ({val})")

    def _on_stop_clicked(self):
        self.session_stop_requested.emit()

    def _on_action_button_clicked(self):
        if not self._is_active:
            self._on_start_clicked()
        else:
            self._on_stop_clicked()

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
        was_active = self._is_active
        self._is_active = is_active
        self._refresh_visuals()

        if is_active and remaining_seconds > 0:
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
            if not is_active:
                self.digits_label.setText("25:00")
