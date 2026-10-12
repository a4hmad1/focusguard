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

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Status Badge
        self.status_badge = QLabel("○  Focus Shield is OFF")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setStyleSheet("""
            background-color: rgba(100, 116, 139, 0.12);
            color: #64748b;
            border: 1px solid rgba(100, 116, 139, 0.25);
            border-radius: 20px;
            padding: 5px 16px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.3px;
        """)
        layout.addWidget(self.status_badge, alignment=Qt.AlignCenter)

        # Digital Countdown Display
        self.digits_label = QLabel("25:00")
        self.digits_label.setAlignment(Qt.AlignCenter)
        self.digits_label.setStyleSheet("""
            font-size: 56px;
            font-weight: 800;
            letter-spacing: -2px;
            font-family: monospace, monospace;
            margin: 4px 0;
        """)
        layout.addWidget(self.digits_label, alignment=Qt.AlignCenter)

        # Plain-English Subtitle
        self.subtitle_label = QLabel("All web browsers are currently unrestricted. Click Start to begin focusing.")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setProperty("class", "subtext")
        self.subtitle_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignCenter)

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
        self.presets_row.setAlignment(Qt.AlignCenter)

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
        self.action_row.setAlignment(Qt.AlignCenter)

        self.start_btn = QPushButton("▶   START FOCUS SESSION")
        self.start_btn.setFixedHeight(44)
        self.start_btn.setMinimumWidth(220)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: #ffffff;
                border: 1px solid #15803d;
                border-radius: 8px;
                padding: 8px 24px;
                font-weight: 800;
                font-size: 14px;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background-color: #22c55e;
            }
            QPushButton:disabled {
                background-color: rgba(22, 163, 74, 0.25);
                color: rgba(255, 255, 255, 0.4);
                border-color: transparent;
            }
        """)
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.action_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹   STOP FOCUS")
        self.stop_btn.setFixedHeight(44)
        self.stop_btn.setMinimumWidth(160)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                border: 1px solid #b91c1c;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 800;
                font-size: 14px;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
            QPushButton:disabled {
                background-color: rgba(220, 38, 38, 0.2);
                color: rgba(255, 255, 255, 0.35);
                border-color: transparent;
            }
        """)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.action_row.addWidget(self.stop_btn)

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

    def update_countdown(self, remaining_seconds: float, is_active: bool):
        self._is_active = is_active
        if is_active and remaining_seconds > 0:
            self.digits_label.setText(format_time_remaining(remaining_seconds))
            self.status_badge.setText("●  Focus Shield is ACTIVE")
            self.status_badge.setStyleSheet("""
                background-color: rgba(22, 163, 74, 0.15);
                color: #16a34a;
                border: 1px solid rgba(22, 163, 74, 0.4);
                border-radius: 20px;
                padding: 5px 16px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.3px;
            """)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.subtitle_label.setText("Browsers are locked! Only your Allowed Websites can open. All other sites are blocked.")
            self.subtitle_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #16a34a;")
            pct = int((remaining_seconds / max(1, self._total_duration_secs)) * 100)
            self.progress_bar.setValue(min(100, max(0, pct)))
        else:
            self.status_badge.setText("○  Focus Shield is OFF")
            self.status_badge.setStyleSheet("""
                background-color: rgba(100, 116, 139, 0.12);
                color: #64748b;
                border: 1px solid rgba(100, 116, 139, 0.25);
                border-radius: 20px;
                padding: 5px 16px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.3px;
            """)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.subtitle_label.setText("All web browsers are currently unrestricted. Click Start to begin focusing.")
            self.subtitle_label.setStyleSheet("font-size: 13px; font-weight: 500;")
            self.progress_bar.setValue(100)
            if not is_active:
                self.digits_label.setText("25:00")
