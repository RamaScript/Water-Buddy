"""Settings & Stats dialog windows for Water Buddy."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QLineEdit, QPushButton,
    QTimeEdit, QFrame, QProgressBar, QWidget,
    QTabWidget, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont, QColor

if TYPE_CHECKING:
    from settings import SettingsManager
    from stats import StatsManager

logger = logging.getLogger("WaterBuddy")

# ── Palette ────────────────────────────────────────────────────────
BG      = "#1e1e2e"
SURFACE = "#313244"
OVERLAY = "#45475a"
TEXT    = "#cdd6f4"
SUBTEXT = "#a6adc8"
MUTED   = "#6c7086"
BLUE    = "#89b4fa"
GREEN   = "#a6e3a1"
PEACH   = "#fab387"
RED     = "#f38ba8"

DIALOG_STYLE = f"""
QDialog {{
    background-color: {BG};
    color: {TEXT};
}}
QWidget {{
    background-color: {BG};
}}
QLabel {{
    color: {TEXT};
    font-size: 13px;
    background: transparent;
}}
QLabel#heading {{
    font-size: 20px;
    font-weight: bold;
    color: {BLUE};
}}
QLabel#section {{
    font-size: 11px;
    font-weight: 700;
    color: {MUTED};
    letter-spacing: 1px;
}}
QLabel#hint {{
    font-size: 12px;
    color: {BLUE};
}}
QLabel#hint_warn {{
    font-size: 12px;
    color: {PEACH};
}}
QLabel#hint_error {{
    font-size: 12px;
    color: {RED};
}}
QSpinBox, QTimeEdit, QLineEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 2px solid {OVERLAY};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}}
QSpinBox:focus, QTimeEdit:focus, QLineEdit:focus {{
    border-color: {BLUE};
}}
QSpinBox:disabled, QTimeEdit:disabled {{
    color: {MUTED};
    border-color: {SURFACE};
    background-color: {BG};
}}
QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {{
    background-color: {OVERLAY};
    border-radius: 4px;
    width: 20px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
    background-color: {BLUE};
}}
QCheckBox {{
    color: {TEXT};
    font-size: 13px;
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {OVERLAY};
    border-radius: 6px;
    background-color: {SURFACE};
}}
QCheckBox::indicator:checked {{
    background-color: {BLUE};
    border-color: {BLUE};
    image: none;
}}
QCheckBox:disabled {{
    color: {MUTED};
}}
QPushButton#save {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {GREEN}, stop:1 #94e2d5);
    color: {BG};
    border: none;
    border-radius: 10px;
    padding: 11px 32px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#save:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #94e2d5, stop:1 {GREEN});
}}
QPushButton#cancel {{
    background-color: {SURFACE};
    color: {SUBTEXT};
    border: 1px solid {OVERLAY};
    border-radius: 10px;
    padding: 11px 32px;
    font-size: 14px;
}}
QPushButton#cancel:hover {{
    background-color: {OVERLAY};
    color: {TEXT};
}}
QTabWidget::pane {{
    border: 1px solid {OVERLAY};
    border-radius: 10px;
    background-color: {BG};
    top: -1px;
}}
QTabBar::tab {{
    background-color: {SURFACE};
    color: {MUTED};
    padding: 9px 22px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 3px;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background-color: {BG};
    color: {BLUE};
    font-weight: bold;
    border-bottom: 2px solid {BLUE};
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT};
    background-color: {OVERLAY};
}}
QProgressBar {{
    background-color: {SURFACE};
    border: none;
    border-radius: 8px;
    min-height: 18px;
    max-height: 18px;
    text-align: center;
    color: {BG};
    font-weight: bold;
    font-size: 11px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {BLUE}, stop:1 #74c7ec);
    border-radius: 8px;
}}
"""


def _separator() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"background-color: {OVERLAY}; max-height: 1px; margin: 4px 0; border: none;")
    return line


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("section")
    return lbl


def _hint(text: str, kind: str = "hint") -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName(kind)
    return lbl


# ══════════════════════════════════════════════════════════════════
#  Settings + Stats Dialog (Tabbed)
# ══════════════════════════════════════════════════════════════════

class SettingsDialog(QDialog):
    """Combined Settings & Stats window with tabs."""

    def __init__(self, settings: "SettingsManager", stats: "StatsManager",
                 start_tab: int = 0, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.stats = stats

        self.setWindowTitle("Water Buddy — Settings")
        self.setFixedSize(440, 560)
        self.setStyleSheet(DIALOG_STYLE)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("💧  Water Buddy")
        title.setObjectName("heading")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_settings_tab(), "⚙️  Settings")
        self.tabs.addTab(self._build_stats_tab(), "📊  Stats")
        self.tabs.setCurrentIndex(start_tab)
        layout.addWidget(self.tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("save")
        self.save_btn.clicked.connect(self._save_and_close)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    # ── Settings Tab ────────────────────────────────────────────

    def _build_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 16, 12, 12)

        # ── Profile ──────────────────────────
        layout.addWidget(_section_label("Profile"))
        layout.addSpacing(4)

        name_row = QHBoxLayout()
        name_lbl = QLabel("👤  Your Name")
        name_lbl.setFixedWidth(130)
        name_row.addWidget(name_lbl)
        self.name_input = QLineEdit(self.settings.user_name)
        self.name_input.setPlaceholderText("Enter your name…")
        self.name_input.setToolTip("Used in greeting messages like \"Hey Rama!\"")
        name_row.addWidget(self.name_input)
        layout.addLayout(name_row)
        layout.addWidget(_separator())

        # ── Reminders ──────────────────────────
        layout.addWidget(_section_label("Reminders"))
        layout.addSpacing(4)

        int_row = QHBoxLayout()
        int_lbl = QLabel("⏰  Interval")
        int_lbl.setFixedWidth(130)
        int_lbl.setToolTip("How often the pet appears to ask if you drank water")
        int_row.addWidget(int_lbl)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setSuffix("  min")
        self.interval_spin.setValue(self.settings.get("reminder_interval_min"))
        self.interval_spin.setToolTip("Minimum: 5 min  |  Maximum: 120 min (2 hours)")
        self.interval_spin.valueChanged.connect(self._on_interval_changed)
        int_row.addWidget(self.interval_spin)
        layout.addLayout(int_row)

        self.interval_hint = _hint("💧  I'll visit you every 30 minutes")
        layout.addWidget(self.interval_hint)
        self._on_interval_changed(self.interval_spin.value())

        layout.addSpacing(6)

        snooze_row = QHBoxLayout()
        snooze_lbl = QLabel("😴  Snooze")
        snooze_lbl.setFixedWidth(130)
        snooze_lbl.setToolTip("How long to wait before reminding again after Snooze")
        snooze_row.addWidget(snooze_lbl)
        self.snooze_spin = QSpinBox()
        self.snooze_spin.setRange(1, 30)
        self.snooze_spin.setSuffix("  min")
        self.snooze_spin.setValue(self.settings.get("snooze_duration_min"))
        self.snooze_spin.setToolTip("Minimum: 1 min  |  Maximum: 30 min")
        self.snooze_spin.valueChanged.connect(self._on_snooze_changed)
        snooze_row.addWidget(self.snooze_spin)
        layout.addLayout(snooze_row)

        self.snooze_hint = _hint("😴  I'll come back in 5 minutes")
        layout.addWidget(self.snooze_hint)
        self._on_snooze_changed(self.snooze_spin.value())

        layout.addWidget(_separator())

        # ── Quiet Hours ──────────────────────────
        layout.addWidget(_section_label("Quiet Hours"))
        layout.addSpacing(4)

        self.quiet_check = QCheckBox("🔇  No reminders during these hours")
        self.quiet_check.setChecked(self.settings.quiet_hours_enabled)
        self.quiet_check.setToolTip("Enable to stop reminders while you sleep")
        self.quiet_check.toggled.connect(self._on_quiet_toggled)
        layout.addWidget(self.quiet_check)

        time_row = QHBoxLayout()
        time_row.setSpacing(8)
        from_lbl = QLabel("From")
        from_lbl.setFixedWidth(36)
        time_row.addWidget(from_lbl)
        self.quiet_start = QTimeEdit()
        self.quiet_start.setDisplayFormat("hh:mm AP")
        self.quiet_start.setToolTip("Quiet hours begin at this time")
        h, m = self.settings.quiet_hours_start.split(":")
        self.quiet_start.setTime(QTime(int(h), int(m)))
        self.quiet_start.timeChanged.connect(self._on_quiet_time_changed)
        time_row.addWidget(self.quiet_start)

        to_lbl = QLabel("To")
        to_lbl.setFixedWidth(24)
        time_row.addWidget(to_lbl)
        self.quiet_end = QTimeEdit()
        self.quiet_end.setDisplayFormat("hh:mm AP")
        self.quiet_end.setToolTip("Quiet hours end at this time")
        h, m = self.settings.quiet_hours_end.split(":")
        self.quiet_end.setTime(QTime(int(h), int(m)))
        self.quiet_end.timeChanged.connect(self._on_quiet_time_changed)
        time_row.addWidget(self.quiet_end)
        layout.addLayout(time_row)

        self.quiet_hint = _hint("")
        layout.addWidget(self.quiet_hint)
        self._on_quiet_toggled(self.quiet_check.isChecked())

        layout.addWidget(_separator())

        # ── Other ──────────────────────────
        layout.addWidget(_section_label("Other"))
        layout.addSpacing(4)

        self.sound_check = QCheckBox("🔔  Play sound when pet appears")
        self.sound_check.setChecked(self.settings.sound_enabled)
        self.sound_check.setToolTip("Plays a water-drop sound when your buddy walks in")
        layout.addWidget(self.sound_check)

        self.login_check = QCheckBox("🚀  Launch at Login")
        self.login_check.setChecked(self.settings.get("launch_at_login"))
        self.login_check.setToolTip("Automatically start Water Buddy when your Mac boots")
        self.login_check.toggled.connect(self._on_login_toggled)
        layout.addWidget(self.login_check)

        self.login_hint = _hint("")
        layout.addWidget(self.login_hint)
        self._on_login_toggled(self.login_check.isChecked())

        layout.addStretch()
        return tab

    # ── Stats Tab ───────────────────────────────────────────────

    def _build_stats_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 16, 12, 12)

        count = self.stats.today_count()
        goal  = self.stats.daily_goal
        pct   = int(self.stats.today_progress() * 100)

        # Today's count
        today_label = QLabel(f"💧  Today: {count} / {goal} glasses")
        today_label.setObjectName("heading")
        today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(today_label)

        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(pct)
        progress.setFormat(f"{pct}%  ({count}/{goal})")
        layout.addWidget(progress)

        # Motivational message
        if count == 0:
            msg = "No drinks yet today — let's get started! 🌊"
            color = MUTED
        elif count < goal // 2:
            msg = f"Keep going! {goal - count} more to hit your goal 💪"
            color = PEACH
        elif count < goal:
            msg = f"Almost there! Just {goal - count} more to go 🔥"
            color = BLUE
        else:
            msg = "🎉 Goal reached! You're crushing it today!"
            color = GREEN

        msg_lbl = QLabel(msg)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"color: {color}; font-size: 13px; font-style: italic; background: transparent;")
        layout.addWidget(msg_lbl)

        layout.addWidget(_separator())

        # Streak
        streak = self.stats.streak()
        streak_text = f"{'🔥' * min(streak, 5)}  {streak} day streak" if streak > 0 else "0 day streak  —  start one today!"
        streak_label = QLabel(streak_text)
        streak_label.setStyleSheet(f"font-size: 17px; color: {PEACH}; font-weight: bold; background: transparent;")
        streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(streak_label)

        layout.addWidget(_separator())

        # Daily goal setter
        layout.addWidget(_section_label("Daily Goal"))
        layout.addSpacing(4)
        goal_row = QHBoxLayout()
        goal_lbl = QLabel("🎯  Target glasses")
        goal_lbl.setFixedWidth(150)
        goal_row.addWidget(goal_lbl)
        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(1, 20)
        self.goal_spin.setSuffix("  glasses")
        self.goal_spin.setValue(self.stats.daily_goal)
        self.goal_spin.setToolTip("How many glasses of water do you want to drink each day?")
        self.goal_spin.valueChanged.connect(self._on_goal_changed)
        goal_row.addWidget(self.goal_spin)
        layout.addLayout(goal_row)

        self.goal_hint = _hint(f"🎯  {self.stats.daily_goal} glasses is your daily target")
        layout.addWidget(self.goal_hint)

        layout.addWidget(_separator())

        # Drink log
        times = self.stats.today_times()
        if times:
            layout.addWidget(_section_label("Today's Log"))
            layout.addSpacing(4)
            log_box = QFrame()
            log_box.setStyleSheet(f"background-color: {SURFACE}; border-radius: 8px;")
            log_layout = QVBoxLayout(log_box)
            log_layout.setContentsMargins(12, 10, 12, 10)
            log_layout.setSpacing(4)
            for t in times[-6:]:  # last 6 entries
                row = QLabel(f"💧  {t}")
                row.setStyleSheet(f"color: {GREEN}; font-size: 12px; background: transparent;")
                log_layout.addWidget(row)
            if len(times) > 6:
                more = QLabel(f"  …and {len(times)-6} more earlier today")
                more.setStyleSheet(f"color: {MUTED}; font-size: 11px; background: transparent;")
                log_layout.addWidget(more)
            layout.addWidget(log_box)
        else:
            no_drinks = QLabel("No drinks logged yet today.\nStay hydrated! 💧")
            no_drinks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_drinks.setWordWrap(True)
            no_drinks.setStyleSheet(f"color: {MUTED}; font-style: italic; background: transparent;")
            layout.addWidget(no_drinks)

        layout.addStretch()
        return tab

    # ── Live feedback callbacks ──────────────────────────────────

    def _on_interval_changed(self, val: int):
        if val == 5:
            self.interval_hint.setObjectName("hint_warn")
            self.interval_hint.setText("⚡  Very frequent! Every 5 minutes.")
        elif val <= 15:
            self.interval_hint.setObjectName("hint")
            self.interval_hint.setText(f"💧  I'll visit you every {val} minutes")
        elif val == 30:
            self.interval_hint.setObjectName("hint")
            self.interval_hint.setText(f"💧  Every {val} minutes  ← Recommended default")
        elif val >= 90:
            self.interval_hint.setObjectName("hint_warn")
            self.interval_hint.setText(f"💤  Long gap — {val} min ({val//60}h {val%60}m) between reminders")
        else:
            self.interval_hint.setObjectName("hint")
            self.interval_hint.setText(f"💧  I'll visit you every {val} minutes")
        self.interval_hint.setStyleSheet("")
        self.setStyleSheet(DIALOG_STYLE)

    def _on_snooze_changed(self, val: int):
        if val == 1:
            self.snooze_hint.setObjectName("hint_warn")
            self.snooze_hint.setText("⚡  Very short snooze — 1 minute!")
        else:
            self.snooze_hint.setObjectName("hint")
            self.snooze_hint.setText(f"😴  I'll come back in {val} minute{'s' if val != 1 else ''}")
        self.snooze_hint.setStyleSheet("")
        self.setStyleSheet(DIALOG_STYLE)

    def _on_quiet_toggled(self, checked: bool):
        self.quiet_start.setEnabled(checked)
        self.quiet_end.setEnabled(checked)
        if checked:
            self._on_quiet_time_changed()
        else:
            self.quiet_hint.setObjectName("hint")
            self.quiet_hint.setText("")
        self.quiet_hint.setStyleSheet("")
        self.setStyleSheet(DIALOG_STYLE)

    def _on_quiet_time_changed(self):
        if not self.quiet_check.isChecked():
            return
        start = self.quiet_start.time()
        end   = self.quiet_end.time()
        start_str = start.toString("h:mm AP")
        end_str   = end.toString("h:mm AP")
        if start == end:
            self.quiet_hint.setObjectName("hint_error")
            self.quiet_hint.setText("⚠️  Start and end times are the same")
        else:
            self.quiet_hint.setObjectName("hint")
            self.quiet_hint.setText(f"🔇  No reminders from {start_str} to {end_str}")
        self.quiet_hint.setStyleSheet("")
        self.setStyleSheet(DIALOG_STYLE)

    def _on_login_toggled(self, checked: bool):
        if checked:
            self.login_hint.setObjectName("hint")
            self.login_hint.setText("✅  Water Buddy will start when your Mac logs in")
        else:
            self.login_hint.setText("")
        self.login_hint.setStyleSheet("")
        self.setStyleSheet(DIALOG_STYLE)

    def _on_goal_changed(self, val: int):
        self.goal_hint.setText(f"🎯  {val} glass{'es' if val != 1 else ''} is your daily target")

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
