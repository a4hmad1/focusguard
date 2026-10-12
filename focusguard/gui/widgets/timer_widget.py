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

        # Header Badge
        self.status_badge = QLabel("STRICT WHITELIST READY • ALL OTHER WEBSITES BLOCKED")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setStyleSheet("""
            background-color: rgba(37, 99, 235, 0.12);
            color: #2563eb;
            border: 1px solid rgba(37, 99, 235, 0.3);
            border-radius: 4px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.status_badge, alignment=Qt.AlignCenter)

        # Digital Countdown Display
        self.digits_label = QLabel("25:00")
        self.digits_label.setAlignment(Qt.AlignCenter)
        self.digits_label.setStyleSheet("""
            font-size: 54px;
            font-weight: 800;
            letter-spacing: -1.5px;
            font-family: monospace, monospace;
        """)
        layout.addWidget(self.digits_label, alignment=Qt.AlignCenter)

        # Subtitle
        self.subtitle_label = QLabel("All browser URLs will be blocked except saved URLs in your whitelist.")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setProperty("class", "subtext")
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignCenter)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        layout.addWidget(self.progress_bar)

        # Presets Row
        self.presets_row = QHBoxLayout()
        self.presets_row.setSpacing(8)

        presets = [("25m Study", "25m"), ("45m Lecture", "45m"), ("60m Deep Work", "1h"), ("90m Session", "90m"), ("2h Exam", "2h")]
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
        self.custom_input.setPlaceholderText("Custom time (e.g. 1h 30m)")
        self.custom_input.setFixedWidth(170)
        self.action_row.addWidget(self.custom_input)

        self.start_btn = QPushButton("▶  Start Focus")
        self.start_btn.setFixedHeight(34)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: #ffffff;
                border: 1px solid #2ea043;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:disabled {
                background-color: rgba(35, 134, 54, 0.25);
                color: rgba(255, 255, 255, 0.35);
                border: 1px solid rgba(46, 160, 67, 0.2);
            }
        """)
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.action_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹  Stop Focus")
        self.stop_btn.setFixedHeight(34)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #da3633;
                color: #ffffff;
                border: 1px solid #f85149;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b62324;
            }
            QPushButton:disabled {
                background-color: rgba(218, 54, 51, 0.25);
                color: rgba(255, 255, 255, 0.35);
                border: 1px solid rgba(248, 81, 73, 0.2);
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
        self.session_start_requested.emit(td, f"Focus Shield ({val})")

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
            self.status_badge.setText("● FOCUS SHIELD ACTIVE • ONLY APPROVED SITES OPEN")
            self.status_badge.setStyleSheet("""
                background-color: rgba(34, 197, 94, 0.15);
                color: #16a34a;
                border: 1px solid rgba(34, 197, 94, 0.4);
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 700;
            """)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.subtitle_label.setText("Browsers are locked to approved URLs only. All other sites are blocked.")
            pct = int((remaining_seconds / max(1, self._total_duration_secs)) * 100)
            self.progress_bar.setValue(min(100, max(0, pct)))
        else:
            self.status_badge.setText("STRICT WHITELIST READY • ALL OTHER WEBSITES BLOCKED")
            self.status_badge.setStyleSheet("""
                background-color: rgba(37, 99, 235, 0.12);
                color: #2563eb;
                border: 1px solid rgba(37, 99, 235, 0.3);
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 700;
            """)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.subtitle_label.setText("All browser URLs will be blocked except saved URLs in your whitelist.")
            self.progress_bar.setValue(100)
            if not is_active:
                self.digits_label.setText("25:00")
