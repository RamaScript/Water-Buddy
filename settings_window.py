"""Settings & Stats dialog windows for Water Buddy."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QLineEdit, QPushButton,
    QTimeEdit, QFrame, QProgressBar, QWidget,
    QTabWidget,
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont

if TYPE_CHECKING:
    from settings import SettingsManager
    from stats import StatsManager

logger = logging.getLogger("WaterBuddy")

# ── Shared Styles ────────────────────────────────────────────────

DIALOG_STYLE = """
QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QLabel {
    color: #cdd6f4;
    font-size: 13px;
}
QLabel#heading {
    font-size: 20px;
    font-weight: bold;
    color: #89b4fa;
}
QLabel#subheading {
    font-size: 11px;
    color: #6c7086;
}
QSpinBox, QTimeEdit, QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}
QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {
    background-color: #45475a;
    border-radius: 3px;
    width: 18px;
}
QCheckBox {
    color: #cdd6f4;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QPushButton#save {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#save:hover {
    background-color: #94e2d5;
}
QPushButton#cancel {
    background-color: #45475a;
    color: #cdd6f4;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-size: 14px;
}
QPushButton#cancel:hover {
    background-color: #585b70;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 8px;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #313244;
    color: #6c7086;
    padding: 8px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-size: 13px;
}
QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #89b4fa;
    font-weight: bold;
}
QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 8px;
    height: 20px;
    text-align: center;
    color: #1e1e2e;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 8px;
}
"""


def _separator() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("background-color: #45475a; max-height: 1px; margin: 8px 0;")
    return line


# ══════════════════════════════════════════════════════════════════
#  Settings + Stats Dialog (Tabbed)
# ══════════════════════════════════════════════════════════════════

class SettingsDialog(QDialog):
    """Combined Settings & Stats window with tabs."""

    def __init__(self, settings: "SettingsManager", stats: "StatsManager", parent=None):
        super().__init__(parent)
        self.settings = settings
        self.stats = stats

        self.setWindowTitle("Water Buddy — Settings")
        self.setFixedSize(420, 520)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title = QLabel("💧 Water Buddy")
        title.setObjectName("heading")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_settings_tab(), "⚙️ Settings")
        tabs.addTab(self._build_stats_tab(), "📊 Stats")
        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("save")
        self.save_btn.clicked.connect(self._save_and_close)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    # ── Settings Tab ────────────────────────────────────────────

    def _build_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Name
        layout.addWidget(QLabel("👤 Your Name"))
        self.name_input = QLineEdit(self.settings.user_name)
        self.name_input.setPlaceholderText("Enter your name...")
        layout.addWidget(self.name_input)

        layout.addWidget(_separator())

        # Reminder Interval
        layout.addWidget(QLabel("⏰ Reminder Interval (minutes)"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setSuffix("  min")
        self.interval_spin.setValue(self.settings.get("reminder_interval_min"))
        layout.addWidget(self.interval_spin)

        # Snooze Duration
        layout.addWidget(QLabel("😴 Snooze Duration (minutes)"))
        self.snooze_spin = QSpinBox()
        self.snooze_spin.setRange(1, 30)
        self.snooze_spin.setSuffix("  min")
        self.snooze_spin.setValue(self.settings.get("snooze_duration_min"))
        layout.addWidget(self.snooze_spin)

        layout.addWidget(_separator())

        # Quiet Hours
        self.quiet_check = QCheckBox("🔇 Enable Quiet Hours")
        self.quiet_check.setChecked(self.settings.quiet_hours_enabled)
        layout.addWidget(self.quiet_check)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("From:"))
        self.quiet_start = QTimeEdit()
        self.quiet_start.setDisplayFormat("hh:mm AP")
        h, m = self.settings.quiet_hours_start.split(":")
        self.quiet_start.setTime(QTime(int(h), int(m)))
        time_layout.addWidget(self.quiet_start)

        time_layout.addWidget(QLabel("To:"))
        self.quiet_end = QTimeEdit()
        self.quiet_end.setDisplayFormat("hh:mm AP")
        h, m = self.settings.quiet_hours_end.split(":")
        self.quiet_end.setTime(QTime(int(h), int(m)))
        time_layout.addWidget(self.quiet_end)
        layout.addLayout(time_layout)

        layout.addWidget(_separator())

        # Sound
        self.sound_check = QCheckBox("🔔 Play sound when pet appears")
        self.sound_check.setChecked(self.settings.sound_enabled)
        layout.addWidget(self.sound_check)

        # Launch at Login
        self.login_check = QCheckBox("🚀 Launch at Login")
        self.login_check.setChecked(self.settings.get("launch_at_login"))
        layout.addWidget(self.login_check)

        layout.addStretch()
        return tab

    # ── Stats Tab ───────────────────────────────────────────────

    def _build_stats_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(14)

        # Today's progress
        count = self.stats.today_count()
        goal = self.stats.daily_goal

        today_label = QLabel(f"💧 Today: {count} / {goal} glasses")
        today_label.setObjectName("heading")
        today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(today_label)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(self.stats.today_progress() * 100))
        progress.setFormat(f"{int(self.stats.today_progress() * 100)}%")
        layout.addWidget(progress)

        layout.addWidget(_separator())

        # Streak
        streak = self.stats.streak()
        streak_label = QLabel(f"🔥 Current Streak: {streak} day{'s' if streak != 1 else ''}")
        streak_label.setStyleSheet("font-size: 16px; color: #fab387;")
        streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(streak_label)

        layout.addWidget(_separator())

        # Today's drink times
        times = self.stats.today_times()
        if times:
            layout.addWidget(QLabel("📋 Today's Drink Log:"))
            times_text = "   •   ".join(times)
            log_label = QLabel(times_text)
            log_label.setWordWrap(True)
            log_label.setStyleSheet("color: #a6e3a1; font-size: 12px;")
            layout.addWidget(log_label)
        else:
            no_drinks = QLabel("No drinks recorded yet today. Stay hydrated! 💧")
            no_drinks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_drinks.setStyleSheet("color: #6c7086; font-style: italic;")
            layout.addWidget(no_drinks)

        layout.addWidget(_separator())

        # Daily Goal
        goal_layout = QHBoxLayout()
        goal_layout.addWidget(QLabel("🎯 Daily Goal:"))
        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(1, 20)
        self.goal_spin.setSuffix("  glasses")
        self.goal_spin.setValue(self.stats.daily_goal)
        goal_layout.addWidget(self.goal_spin)
        layout.addLayout(goal_layout)

        layout.addStretch()
        return tab

    # ── Save ────────────────────────────────────────────────────

    def _save_and_close(self) -> None:
        self.settings.set("user_name", self.name_input.text().strip() or "Buddy")
        self.settings.set("reminder_interval_min", self.interval_spin.value())
        self.settings.set("snooze_duration_min", self.snooze_spin.value())
        self.settings.set("quiet_hours_enabled", self.quiet_check.isChecked())
        self.settings.set("quiet_hours_start", self.quiet_start.time().toString("HH:mm"))
        self.settings.set("quiet_hours_end", self.quiet_end.time().toString("HH:mm"))
        self.settings.set("sound_enabled", self.sound_check.isChecked())
        self.settings.set("launch_at_login", self.login_check.isChecked())
        self.settings.save()

        self.stats.daily_goal = self.goal_spin.value()

        logger.info("Settings saved by user.")
        self.accept()
