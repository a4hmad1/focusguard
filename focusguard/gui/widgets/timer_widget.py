"""Modern Focus Timer and Countdown Widget."""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QComboBox, QLineEdit
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
        self.setStyleSheet("""
            QFrame#timer_widget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e293b, stop:1 #0f172a);
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 24px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)

        # Header Badge
        self.status_badge = QLabel("READY TO FOCUS")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setStyleSheet("""
            background-color: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 9999px;
            padding: 4px 16px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        """)
        layout.addWidget(self.status_badge, alignment=Qt.AlignCenter)

        # Digital Countdown Display
        self.digits_label = QLabel("25:00")
        self.digits_label.setAlignment(Qt.AlignCenter)
        self.digits_label.setStyleSheet("""
            font-size: 64px;
            font-weight: 800;
            color: #f8fafc;
            letter-spacing: -2px;
            font-family: monospace, monospace;
        """)
        layout.addWidget(self.digits_label, alignment=Qt.AlignCenter)

        # Subtitle
        self.subtitle_label = QLabel("Select duration or use quick presets to begin your session.")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignCenter)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0f172a;
                border-radius: 4px;
                border: 1px solid #334155;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Preset Buttons Row
        self.presets_row = QHBoxLayout()
        self.presets_row.setSpacing(8)

        presets = [("15m", "15m"), ("25m (Pomodoro)", "25m"), ("45m", "45m"), ("1h", "1h"), ("2h", "2h")]
        self.preset_buttons = []
        for label, val in presets:
            btn = QPushButton(label)
            btn.setProperty("class", "secondary")
            btn.clicked.connect(lambda _, v=val: self._on_preset_clicked(v))
            self.presets_row.addWidget(btn)
            self.preset_buttons.append(btn)
        layout.addLayout(self.presets_row)

        # Custom Duration and Action Row
        self.action_row = QHBoxLayout()
        self.action_row.setSpacing(10)

        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("Custom (e.g. 1h 30m)")
        self.custom_input.setFixedWidth(160)
        self.action_row.addWidget(self.custom_input)

        self.start_btn = QPushButton("Start Focus Session")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                color: white;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.start_btn.clicked.connect(self._on_action_button_clicked)
        self.action_row.addWidget(self.start_btn)

        layout.addLayout(self.action_row)

        self._is_active = False
        self._total_duration_secs = 25 * 60

    def _on_preset_clicked(self, val_str: str):
        td = parse_duration(val_str)
        if td:
            self._total_duration_secs = int(td.total_seconds())
            self.digits_label.setText(format_time_remaining(self._total_duration_secs))
            self.custom_input.setText(val_str)

    def _on_action_button_clicked(self):
        if not self._is_active:
            # Start
            val = self.custom_input.text().strip() or "25m"
            td = parse_duration(val)
            if not td:
                td = timedelta(minutes=25)
            self._total_duration_secs = int(td.total_seconds())
            self.session_start_requested.emit(td, f"GUI Session ({val})")
        else:
            # Stop
            self.session_stop_requested.emit()

    def update_countdown(self, remaining_seconds: float, is_active: bool):
        self._is_active = is_active
        if is_active and remaining_seconds > 0:
            self.digits_label.setText(format_time_remaining(remaining_seconds))
            self.status_badge.setText("FOCUS SESSION IN PROGRESS")
            self.status_badge.setStyleSheet("""
                background-color: rgba(34, 197, 94, 0.15);
                color: #4ade80;
                border: 1px solid rgba(34, 197, 94, 0.3);
                border-radius: 9999px;
                padding: 4px 16px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            """)
            self.start_btn.setText("Stop Focus Session")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 24px;
                    color: white;
                    font-weight: 700;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #b91c1c;
                }
            """)
            self.subtitle_label.setText("Distracting apps & websites are locked to protect your focus.")
            pct = int((remaining_seconds / max(1, self._total_duration_secs)) * 100)
            self.progress_bar.setValue(min(100, max(0, pct)))
        else:
            self.status_badge.setText("READY TO FOCUS")
            self.status_badge.setStyleSheet("""
                background-color: rgba(59, 130, 246, 0.15);
                color: #60a5fa;
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 9999px;
                padding: 4px 16px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            """)
            self.start_btn.setText("Start Focus Session")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 24px;
                    color: white;
                    font-weight: 700;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
            """)
            self.subtitle_label.setText("Select duration or use quick presets to begin your session.")
            self.progress_bar.setValue(100)
            if not is_active:
                self.digits_label.setText("25:00")
