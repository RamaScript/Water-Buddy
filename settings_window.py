"""Settings & Stats dialog — Water Buddy (cross-platform)."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QLineEdit, QPushButton,
    QTimeEdit, QFrame, QProgressBar, QWidget,
    QTabWidget, QScrollArea,
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QColor

if TYPE_CHECKING:
    from settings import SettingsManager
    from stats import StatsManager

logger = logging.getLogger("WaterBuddy")

# ── Catppuccin Mocha palette ───────────────────────────────────────
BG      = "#1e1e2e"
MANTLE  = "#181825"
SURFACE = "#313244"
OVERLAY = "#45475a"
TEXT    = "#cdd6f4"
SUBTEXT = "#a6adc8"
MUTED   = "#6c7086"
BLUE    = "#89b4fa"
LAVENDER= "#b4befe"
GREEN   = "#a6e3a1"
TEAL    = "#94e2d5"
PEACH   = "#fab387"
RED     = "#f38ba8"
YELLOW  = "#f9e2af"

# ── Shared stylesheet ──────────────────────────────────────────────
DIALOG_STYLE = f"""
QDialog {{
    background-color: {BG};
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
    padding: 9px 24px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 3px;
    font-size: 13px;
    min-width: 80px;
}}
QTabBar::tab:selected {{
    background-color: {BG};
    color: {BLUE};
    font-weight: bold;
    border-top: 2px solid {BLUE};
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT};
    background-color: {OVERLAY};
}}
QScrollArea {{
    border: none;
    background-color: {BG};
}}
QScrollBar:vertical {{
    background: {BG};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {OVERLAY};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BLUE};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QLabel {{
    color: {TEXT};
    font-size: 13px;
    background: transparent;
}}
QLineEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 2px solid {OVERLAY};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}}
QLineEdit:focus {{
    border-color: {BLUE};
    background-color: {SURFACE};
}}
QSpinBox, QTimeEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 2px solid {OVERLAY};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    min-height: 20px;
}}
QSpinBox:focus, QTimeEdit:focus {{
    border-color: {BLUE};
}}
QSpinBox:disabled, QTimeEdit:disabled {{
    color: {MUTED};
    border-color: {SURFACE};
    background-color: {MANTLE};
}}
QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {{
    background-color: {OVERLAY};
    border-radius: 3px;
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
    width: 18px;
    height: 18px;
    border: 2px solid {OVERLAY};
    border-radius: 5px;
    background-color: {SURFACE};
}}
QCheckBox::indicator:checked {{
    background-color: {BLUE};
    border-color: {BLUE};
}}
QCheckBox::indicator:disabled {{
    background-color: {MANTLE};
    border-color: {SURFACE};
}}
QCheckBox:disabled {{
    color: {MUTED};
}}
QPushButton#save {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {GREEN}, stop:1 {TEAL});
    color: {MANTLE};
    border: none;
    border-radius: 10px;
    padding: 11px 32px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#save:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {TEAL}, stop:1 {GREEN});
}}
QPushButton#save:pressed {{
    padding: 12px 30px 10px 34px;
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
QProgressBar {{
    background-color: {SURFACE};
    border: none;
    border-radius: 8px;
    min-height: 16px;
    max-height: 16px;
    text-align: center;
    color: {MANTLE};
    font-weight: bold;
    font-size: 10px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {BLUE}, stop:1 {LAVENDER});
    border-radius: 8px;
}}
"""


# ── Small helpers ─────────────────────────────────────────────────

def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{OVERLAY}; max-height:1px; border:none; margin:2px 0;")
    return f


def _section(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"color:{MUTED}; font-size:10px; font-weight:700; "
        f"letter-spacing:1.2px; background:transparent;"
    )
    return lbl


def _hint_label(text: str = "", color: str = BLUE) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color:{color}; font-size:11px; background:transparent;")
    return lbl


def _scrollable(inner: QWidget) -> QScrollArea:
    area = QScrollArea()
    area.setWidget(inner)
    area.setWidgetResizable(True)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    area.setFrameShape(QFrame.Shape.NoFrame)
    area.setStyleSheet(f"background:{BG}; border:none;")
    inner.setStyleSheet(f"background:{BG};")
    return area


# ══════════════════════════════════════════════════════════════════
#  Main dialog
# ══════════════════════════════════════════════════════════════════

class SettingsDialog(QDialog):
    """Tabbed Settings + Stats dialog."""

    def __init__(self, settings: "SettingsManager", stats: "StatsManager",
                 start_tab: int = 0, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.stats    = stats

        self.setWindowTitle("Water Buddy — Settings")
        self.setFixedSize(460, 580)
        self.setStyleSheet(DIALOG_STYLE)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 20, 20, 20)

        # ── Header ─────────────────────────────────────────────
        header = QLabel("💧  Water Buddy")
        header.setStyleSheet(
            f"font-size:20px; font-weight:700; color:{BLUE}; background:transparent;"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(header)

        # ── Tabs ────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.addTab(_scrollable(self._build_settings_tab()), "⚙️  Settings")
        self.tabs.addTab(_scrollable(self._build_stats_tab()),    "📊  Stats")
        self.tabs.setCurrentIndex(start_tab)
        root.addWidget(self.tabs)

        # ── Buttons ─────────────────────────────────────────────
        row = QHBoxLayout()
        row.setSpacing(10)

        cancel = QPushButton("Cancel")
        cancel.setObjectName("cancel")
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save Changes")
        save.setObjectName("save")
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.clicked.connect(self._save_and_close)

        row.addWidget(cancel)
        row.addWidget(save)
        root.addLayout(row)

    # ── Settings tab ─────────────────────────────────────────────

    def _build_settings_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        lay.setContentsMargins(16, 16, 16, 16)

        # Profile ───────────────────────────────
        lay.addWidget(_section("Profile"))
        lay.addSpacing(2)

        lay.addWidget(QLabel("👤  Your Name"))
        self.name_input = QLineEdit(self.settings.user_name)
        self.name_input.setPlaceholderText("Enter your name…")
        self.name_input.setToolTip("Used in greeting: \"Hey Rama! Did you drink water?\"")
        lay.addWidget(self.name_input)

        lay.addSpacing(4)
        lay.addWidget(_sep())
        lay.addSpacing(4)

        # Reminders ─────────────────────────────
        lay.addWidget(_section("Reminders"))
        lay.addSpacing(2)

        row1 = QHBoxLayout()
        lbl1 = QLabel("⏰  Remind me every")
        lbl1.setStyleSheet(f"color:{TEXT}; background:transparent;")
        row1.addWidget(lbl1)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setSuffix("  min")
        self.interval_spin.setValue(self.settings.get("reminder_interval_min"))
        self.interval_spin.setToolTip("Min: 5 min  |  Max: 120 min (2 hours)")
        self.interval_spin.setFixedWidth(130)
        self.interval_spin.valueChanged.connect(self._on_interval_changed)
        row1.addWidget(self.interval_spin)
        row1.addStretch()
        lay.addLayout(row1)

        self.interval_hint = _hint_label()
        lay.addWidget(self.interval_hint)
        self._on_interval_changed(self.interval_spin.value())

        lay.addSpacing(6)

        row2 = QHBoxLayout()
        lbl2 = QLabel("😴  Snooze for")
        lbl2.setStyleSheet(f"color:{TEXT}; background:transparent;")
        row2.addWidget(lbl2)
        self.snooze_spin = QSpinBox()
        self.snooze_spin.setRange(1, 30)
        self.snooze_spin.setSuffix("  min")
        self.snooze_spin.setValue(self.settings.get("snooze_duration_min"))
        self.snooze_spin.setToolTip("Min: 1 min  |  Max: 30 min")
        self.snooze_spin.setFixedWidth(130)
        self.snooze_spin.valueChanged.connect(self._on_snooze_changed)
        row2.addWidget(self.snooze_spin)
        row2.addStretch()
        lay.addLayout(row2)

        self.snooze_hint = _hint_label()
        lay.addWidget(self.snooze_hint)
        self._on_snooze_changed(self.snooze_spin.value())

        lay.addSpacing(4)
        lay.addWidget(_sep())
        lay.addSpacing(4)

        # Quiet Hours ────────────────────────────
        lay.addWidget(_section("Quiet Hours"))
        lay.addSpacing(2)

        self.quiet_check = QCheckBox("🔇  No reminders during these hours")
        self.quiet_check.setChecked(self.settings.quiet_hours_enabled)
        self.quiet_check.setToolTip("Stops the pet from appearing while you sleep")
        self.quiet_check.toggled.connect(self._on_quiet_toggled)
        lay.addWidget(self.quiet_check)

        time_row = QHBoxLayout()
        time_row.setSpacing(10)

        from_lbl = QLabel("From")
        from_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; background:transparent;")
        from_lbl.setFixedWidth(32)
        time_row.addWidget(from_lbl)

        self.quiet_start = QTimeEdit()
        self.quiet_start.setDisplayFormat("hh:mm AP")
        self.quiet_start.setToolTip("Quiet period starts at this time")
        h, m = self.settings.quiet_hours_start.split(":")
        self.quiet_start.setTime(QTime(int(h), int(m)))
        self.quiet_start.setFixedWidth(110)
        self.quiet_start.timeChanged.connect(self._on_quiet_time_changed)
        time_row.addWidget(self.quiet_start)

        to_lbl = QLabel("to")
        to_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; background:transparent;")
        to_lbl.setFixedWidth(18)
        time_row.addWidget(to_lbl)

        self.quiet_end = QTimeEdit()
        self.quiet_end.setDisplayFormat("hh:mm AP")
        self.quiet_end.setToolTip("Quiet period ends at this time")
        h, m = self.settings.quiet_hours_end.split(":")
        self.quiet_end.setTime(QTime(int(h), int(m)))
        self.quiet_end.setFixedWidth(110)
        self.quiet_end.timeChanged.connect(self._on_quiet_time_changed)
        time_row.addWidget(self.quiet_end)
        time_row.addStretch()
        lay.addLayout(time_row)

        self.quiet_hint = _hint_label()
        lay.addWidget(self.quiet_hint)
        self._on_quiet_toggled(self.quiet_check.isChecked())

        lay.addSpacing(4)
        lay.addWidget(_sep())
        lay.addSpacing(4)

        # Other ──────────────────────────────────
        lay.addWidget(_section("Other"))
        lay.addSpacing(2)

        self.sound_check = QCheckBox("🔔  Play sound when pet appears")
        self.sound_check.setChecked(self.settings.sound_enabled)
        self.sound_check.setToolTip("Plays a water-drop sound when your buddy walks in")
        lay.addWidget(self.sound_check)

        self.login_check = QCheckBox("🚀  Launch at Login")
        self.login_check.setChecked(self.settings.get("launch_at_login"))
        self.login_check.setToolTip("Automatically start Water Buddy when your computer boots")
        self.login_check.toggled.connect(self._on_login_toggled)
        lay.addWidget(self.login_check)

        self.login_hint = _hint_label()
        lay.addWidget(self.login_hint)
        self._on_login_toggled(self.login_check.isChecked())

        lay.addStretch()
        return w

    # ── Stats tab ─────────────────────────────────────────────────

    def _build_stats_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(w)
        lay.setSpacing(12)
        lay.setContentsMargins(16, 16, 16, 16)

        count = self.stats.today_count()
        goal  = self.stats.daily_goal
        pct   = int(self.stats.today_progress() * 100)

        # Big counter card ───────────────────────
        card = QFrame()
        card.setStyleSheet(
            f"background:{SURFACE}; border-radius:12px; border:1px solid {OVERLAY};"
        )
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 14, 16, 14)
        card_lay.setSpacing(8)

        count_lbl = QLabel(f"💧  {count}  /  {goal}")
        count_lbl.setStyleSheet(
            f"font-size:28px; font-weight:700; color:{BLUE}; background:transparent;"
        )
        count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(count_lbl)

        sub = QLabel("glasses today")
        sub.setStyleSheet(f"font-size:12px; color:{MUTED}; background:transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(sub)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(pct)
        bar.setFormat(f"{pct}%")
        bar.setTextVisible(True)
        card_lay.addWidget(bar)

        lay.addWidget(card)

        # Motivational line ─────────────────────
        if count == 0:
            msg, color = "No drinks yet — let's get started! 🌊", MUTED
        elif pct < 50:
            msg, color = f"Keep going! {goal - count} more to reach your goal 💪", PEACH
        elif count < goal:
            msg, color = f"Almost there! Just {goal - count} more 🔥", YELLOW
        else:
            msg, color = "🎉 Daily goal reached! You're crushing it!", GREEN

        msg_lbl = QLabel(msg)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            f"color:{color}; font-size:13px; font-style:italic; background:transparent;"
        )
        lay.addWidget(msg_lbl)

        lay.addWidget(_sep())

        # Streak ────────────────────────────────
        streak = self.stats.streak()
        fires  = "🔥" * min(streak, 7) if streak else ""
        s_text = (
            f"{fires}  {streak} day streak" if streak > 0
            else "No streak yet — start one today!"
        )
        streak_lbl = QLabel(s_text)
        streak_lbl.setStyleSheet(
            f"font-size:18px; font-weight:700; color:{PEACH}; background:transparent;"
        )
        streak_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(streak_lbl)

        lay.addWidget(_sep())

        # Daily goal spinner ─────────────────────
        lay.addWidget(_section("Daily Goal"))
        lay.addSpacing(2)

        goal_row = QHBoxLayout()
        goal_lbl = QLabel("🎯  Target glasses per day")
        goal_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
        goal_row.addWidget(goal_lbl)
        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(1, 20)
        self.goal_spin.setSuffix("  glasses")
        self.goal_spin.setValue(self.stats.daily_goal)
        self.goal_spin.setFixedWidth(140)
        self.goal_spin.setToolTip("How many glasses is your daily hydration target?")
        self.goal_spin.valueChanged.connect(self._on_goal_changed)
        goal_row.addWidget(self.goal_spin)
        goal_row.addStretch()
        lay.addLayout(goal_row)

        self.goal_hint = _hint_label(f"🎯  {self.stats.daily_goal} glasses per day")
        lay.addWidget(self.goal_hint)

        lay.addWidget(_sep())

        # Drink log ──────────────────────────────
        lay.addWidget(_section("Today's Log"))
        lay.addSpacing(2)

        times = self.stats.today_times()
        if times:
            log_box = QFrame()
            log_box.setStyleSheet(
                f"background:{SURFACE}; border-radius:10px; border:1px solid {OVERLAY};"
            )
            log_lay = QVBoxLayout(log_box)
            log_lay.setContentsMargins(14, 10, 14, 10)
            log_lay.setSpacing(5)
            for t in times[-8:]:
                entry = QLabel(f"💧  {t}")
                entry.setStyleSheet(
                    f"color:{GREEN}; font-size:12px; background:transparent; border:none;"
                )
                log_lay.addWidget(entry)
            if len(times) > 8:
                more = QLabel(f"  …and {len(times) - 8} more earlier")
                more.setStyleSheet(
                    f"color:{MUTED}; font-size:11px; background:transparent; border:none;"
                )
                log_lay.addWidget(more)
            lay.addWidget(log_box)
        else:
            empty = QLabel("No drinks logged yet today.\nStay hydrated! 💧")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color:{MUTED}; font-style:italic; background:transparent;")
            lay.addWidget(empty)

        lay.addStretch()
        return w

    # ── Live callbacks ────────────────────────────────────────────

    def _on_interval_changed(self, val: int):
        if val == 5:
            text, color = "⚡  Very frequent — every 5 minutes!", PEACH
        elif val == 30:
            text, color = f"💧  Every {val} min  ·  Recommended ✓", BLUE
        elif val >= 90:
            text, color = f"💤  That's {val // 60}h {val % 60}m between reminders", PEACH
        else:
            text, color = f"💧  I'll visit you every {val} minutes", BLUE
        self.interval_hint.setText(text)
        self.interval_hint.setStyleSheet(f"color:{color}; font-size:11px; background:transparent;")

    def _on_snooze_changed(self, val: int):
        if val == 1:
            text, color = "⚡  Very short — back in 1 minute!", PEACH
        else:
            text, color = f"😴  I'll come back in {val} minutes", BLUE
        self.snooze_hint.setText(text)
        self.snooze_hint.setStyleSheet(f"color:{color}; font-size:11px; background:transparent;")

    def _on_quiet_toggled(self, checked: bool):
        self.quiet_start.setEnabled(checked)
        self.quiet_end.setEnabled(checked)
        if checked:
            self._on_quiet_time_changed()
        else:
            self.quiet_hint.setText("")

    def _on_quiet_time_changed(self):
        if not self.quiet_check.isChecked():
            return
        s = self.quiet_start.time()
        e = self.quiet_end.time()
        if s == e:
            self.quiet_hint.setText("⚠️  Start and end are the same time")
            self.quiet_hint.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        else:
            self.quiet_hint.setText(
                f"🔇  No reminders from {s.toString('h:mm AP')} to {e.toString('h:mm AP')}"
            )
            self.quiet_hint.setStyleSheet(f"color:{BLUE}; font-size:11px; background:transparent;")

    def _on_login_toggled(self, checked: bool):
        if checked:
            self.login_hint.setText("✅  Will start automatically at login")
            self.login_hint.setStyleSheet(f"color:{GREEN}; font-size:11px; background:transparent;")
        else:
            self.login_hint.setText("")

    def _on_goal_changed(self, val: int):
        self.goal_hint.setText(f"🎯  {val} glass{'es' if val != 1 else ''} per day")

    # ── Save ──────────────────────────────────────────────────────

    def _save_and_close(self) -> None:
        self.settings.set("user_name",             self.name_input.text().strip() or "Buddy")
        self.settings.set("reminder_interval_min", self.interval_spin.value())
        self.settings.set("snooze_duration_min",   self.snooze_spin.value())
        self.settings.set("quiet_hours_enabled",   self.quiet_check.isChecked())
        self.settings.set("quiet_hours_start",     self.quiet_start.time().toString("HH:mm"))
        self.settings.set("quiet_hours_end",       self.quiet_end.time().toString("HH:mm"))
        self.settings.set("sound_enabled",         self.sound_check.isChecked())
        self.settings.set("launch_at_login",       self.login_check.isChecked())
        self.settings.save()

        self.stats.daily_goal = self.goal_spin.value()
        logger.info("Settings saved.")
        self.accept()
