"""First-run onboarding wizard for Water Buddy."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QWidget,
    QStackedWidget, QFrame, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap, QPen, QBrush

if TYPE_CHECKING:
    from settings import SettingsManager

logger = logging.getLogger("WaterBuddy")

# ── Palette ────────────────────────────────────────────────────────
BG        = "#1e1e2e"
SURFACE   = "#313244"
OVERLAY   = "#45475a"
TEXT      = "#cdd6f4"
SUBTEXT   = "#a6adc8"
MUTED     = "#6c7086"
BLUE      = "#89b4fa"
GREEN     = "#a6e3a1"
PEACH     = "#fab387"
ROSEWATER = "#f5e0dc"

WIZARD_STYLE = f"""
QDialog {{
    background-color: {BG};
    color: {TEXT};
    border-radius: 16px;
}}
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QLineEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 2px solid {OVERLAY};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 15px;
    font-family: 'SF Pro Display', 'Helvetica Neue', sans-serif;
}}
QLineEdit:focus {{
    border-color: {BLUE};
}}
QSpinBox {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 2px solid {OVERLAY};
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 15px;
    font-family: 'SF Pro Display', 'Helvetica Neue', sans-serif;
}}
QSpinBox:focus {{
    border-color: {BLUE};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {OVERLAY};
    border-radius: 4px;
    width: 22px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {BLUE};
}}
QPushButton#next {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {BLUE}, stop:1 #74c7ec);
    color: {BG};
    border: none;
    border-radius: 12px;
    padding: 13px 36px;
    font-size: 15px;
    font-weight: bold;
    font-family: 'SF Pro Display', 'Helvetica Neue', sans-serif;
}}
QPushButton#next:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #74c7ec, stop:1 {BLUE});
}}
QPushButton#next:pressed {{
    padding: 14px 34px 12px 38px;
}}
QPushButton#back {{
    background: transparent;
    color: {MUTED};
    border: none;
    border-radius: 12px;
    padding: 13px 24px;
    font-size: 14px;
    font-family: 'SF Pro Display', 'Helvetica Neue', sans-serif;
}}
QPushButton#back:hover {{
    color: {TEXT};
    background-color: {SURFACE};
}}
QPushButton#finish {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {GREEN}, stop:1 #94e2d5);
    color: {BG};
    border: none;
    border-radius: 12px;
    padding: 13px 36px;
    font-size: 15px;
    font-weight: bold;
    font-family: 'SF Pro Display', 'Helvetica Neue', sans-serif;
}}
QPushButton#finish:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #94e2d5, stop:1 {GREEN});
}}
QPushButton#toggle_on {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {GREEN}, stop:1 #94e2d5);
    color: {BG};
    border: none;
    border-radius: 22px;
    padding: 10px 30px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#toggle_off {{
    background-color: {SURFACE};
    color: {MUTED};
    border: 2px solid {OVERLAY};
    border-radius: 22px;
    padding: 10px 30px;
    font-size: 14px;
}}
"""


class DotsIndicator(QWidget):
    """Animated step dots indicator."""

    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.total = total
        self.current = 0
        self.setFixedSize(total * 24, 12)

    def set_step(self, step: int):
        self.current = step
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        dot_r = 5
        gap = 14
        x_start = 0
        for i in range(self.total):
            cx = x_start + i * (dot_r * 2 + gap) + dot_r
            cy = 6
            if i == self.current:
                painter.setBrush(QBrush(QColor(BLUE)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(cx - dot_r - 2), int(cy - dot_r), (dot_r + 2) * 2, dot_r * 2)
            elif i < self.current:
                painter.setBrush(QBrush(QColor(OVERLAY)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(cx - dot_r), int(cy - dot_r), dot_r * 2, dot_r * 2)
            else:
                painter.setBrush(QBrush(QColor(SURFACE)))
                painter.setPen(QPen(QColor(OVERLAY), 1.5))
                painter.drawEllipse(int(cx - dot_r), int(cy - dot_r), dot_r * 2, dot_r * 2)


def _big_label(text: str, size: int = 64) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"font-size: {size}px; background: transparent;")
    return lbl


def _heading(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {TEXT}; background: transparent;")
    return lbl


def _subtext(text: str, wrap: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setWordWrap(wrap)
    lbl.setStyleSheet(f"font-size: 14px; color: {SUBTEXT}; background: transparent; line-height: 160%;")
    return lbl


def _card(text: str, emoji: str) -> QFrame:
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {SURFACE};
            border-radius: 12px;
            padding: 4px;
        }}
    """)
    layout = QHBoxLayout(card)
    layout.setContentsMargins(16, 12, 16, 12)
    e = QLabel(emoji)
    e.setStyleSheet("font-size: 24px; background: transparent;")
    layout.addWidget(e)
    t = QLabel(text)
    t.setWordWrap(True)
    t.setStyleSheet(f"font-size: 13px; color: {SUBTEXT}; background: transparent;")
    layout.addWidget(t, 1)
    return card


# ══════════════════════════════════════════════════════════════════
#  Onboarding Wizard
# ══════════════════════════════════════════════════════════════════

class OnboardingWizard(QDialog):
    """4-step first-run setup wizard."""

    TOTAL_STEPS = 4

    def __init__(self, settings: "SettingsManager", on_complete, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.on_complete = on_complete
        self._login_enabled = False
        self._step = 0

        self.setWindowTitle("Welcome to Water Buddy")
        self.setFixedSize(460, 560)
        self.setStyleSheet(WIZARD_STYLE)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self._page_welcome())
        self.stack.addWidget(self._page_howto())
        self.stack.addWidget(self._page_setup())
        self.stack.addWidget(self._page_login())
        root.addWidget(self.stack, 1)

        # Bottom nav bar
        nav = QFrame()
        nav.setStyleSheet(f"background-color: {SURFACE}; border-top: 1px solid {OVERLAY};")
        nav.setFixedHeight(80)
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(24, 0, 24, 0)

        self.dots = DotsIndicator(self.TOTAL_STEPS)
        nav_layout.addWidget(self.dots)
        nav_layout.addStretch()

        self.back_btn = QPushButton("← Back")
        self.back_btn.setObjectName("back")
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setVisible(False)
        nav_layout.addWidget(self.back_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.setObjectName("next")
        self.next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self.next_btn)

        root.addWidget(nav)

    # ── Pages ────────────────────────────────────────────────────

    def _page_welcome(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 48, 40, 24)
        layout.setSpacing(0)

        layout.addWidget(_big_label("💧", 80))
        layout.addSpacing(20)
        layout.addWidget(_heading("Welcome to Water Buddy"))
        layout.addSpacing(12)
        layout.addWidget(_subtext("Your tiny desktop companion\nthat keeps you hydrated all day.", wrap=True))
        layout.addSpacing(32)

        # Feature pills
        features = [
            ("🐾", "A cute pet that walks across your screen"),
            ("⏰", "Gentle reminders — never miss a drink"),
            ("📊", "Tracks your daily water intake & streaks"),
        ]
        for emoji, text in features:
            layout.addWidget(_card(text, emoji))
            layout.addSpacing(8)

        layout.addStretch()
        return page

    def _page_howto(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 48, 40, 24)
        layout.setSpacing(0)

        layout.addWidget(_big_label("🐾", 64))
        layout.addSpacing(16)
        layout.addWidget(_heading("Here's how it works"))
        layout.addSpacing(24)

        steps = [
            ("1️⃣", "Your pet hides in the background, quietly counting down"),
            ("2️⃣", "Every 30 min it walks in from the corner of your screen"),
            ("3️⃣", "It asks: \"Hey! Did you drink water?\""),
            ("4️⃣", "Click Yes to celebrate 🎉 or Snooze if you're busy"),
            ("💧", "Lives in your menu bar — always available, never in the way"),
        ]
        for emoji, text in steps:
            layout.addWidget(_card(text, emoji))
            layout.addSpacing(8)

        layout.addStretch()
        return page

    def _page_setup(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 24)
        layout.setSpacing(0)

        layout.addWidget(_big_label("⚙️", 52))
        layout.addSpacing(12)
        layout.addWidget(_heading("Quick Setup"))
        layout.addSpacing(8)
        layout.addWidget(_subtext("You can change these anytime in Settings.", wrap=False))
        layout.addSpacing(28)

        # Name
        name_label = QLabel("👤  What's your name?")
        name_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT}; background: transparent;")
        layout.addWidget(name_label)
        layout.addSpacing(8)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name…")
        self.name_input.setFixedHeight(46)
        layout.addWidget(self.name_input)

        layout.addSpacing(24)

        # Interval
        interval_label = QLabel("⏰  Remind me every:")
        interval_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT}; background: transparent;")
        layout.addWidget(interval_label)
        layout.addSpacing(8)

        spin_row = QHBoxLayout()
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setValue(self.settings.get("reminder_interval_min") or 30)
        self.interval_spin.setSuffix("  min")
        self.interval_spin.setFixedHeight(46)
        self.interval_spin.valueChanged.connect(self._update_interval_hint)
        spin_row.addWidget(self.interval_spin)
        layout.addLayout(spin_row)
        layout.addSpacing(6)

        self.interval_hint = QLabel("💧  I'll visit you every 30 minutes")
        self.interval_hint.setStyleSheet(f"font-size: 12px; color: {BLUE}; background: transparent;")
        layout.addWidget(self.interval_hint)
        self._update_interval_hint(self.interval_spin.value())

        layout.addStretch()
        return page

    def _page_login(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 24)
        layout.setSpacing(0)

        layout.addWidget(_big_label("🚀", 64))
        layout.addSpacing(16)
        layout.addWidget(_heading("Start automatically?"))
        layout.addSpacing(8)

        desc = _subtext(
            "Launch Water Buddy whenever your Mac starts.\n"
            "No need to open it manually each day.",
            wrap=True
        )
        layout.addWidget(desc)
        layout.addSpacing(32)

        # Toggle button
        self.login_toggle = QPushButton("⭕  Off — start manually")
        self.login_toggle.setObjectName("toggle_off")
        self.login_toggle.setFixedHeight(48)
        self.login_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_toggle.clicked.connect(self._toggle_login)
        layout.addWidget(self.login_toggle)
        layout.addSpacing(16)

        # Info card
        info = _card(
            "Water Buddy will appear in your menu bar automatically after every login.",
            "ℹ️"
        )
        layout.addWidget(info)
        layout.addSpacing(12)

        skip_note = QLabel("You can always change this in Settings → Launch at Login")
        skip_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        skip_note.setWordWrap(True)
        skip_note.setStyleSheet(f"font-size: 11px; color: {MUTED}; background: transparent;")
        layout.addWidget(skip_note)

        layout.addStretch()
        return page

    # ── Actions ──────────────────────────────────────────────────

    def _update_interval_hint(self, val: int):
        if val == 5:
            hint = f"⚡  Very frequent — I'll check in every 5 minutes!"
        elif val <= 15:
            hint = f"💧  I'll visit you every {val} minutes"
        elif val == 30:
            hint = f"💧  I'll visit you every {val} minutes  ← Recommended"
        elif val >= 90:
            hint = f"💤  That's quite long — {val} minutes between reminders"
        else:
            hint = f"💧  I'll visit you every {val} minutes"
        self.interval_hint.setText(hint)

    def _toggle_login(self):
        self._login_enabled = not self._login_enabled
        if self._login_enabled:
            self.login_toggle.setObjectName("toggle_on")
            self.login_toggle.setText("✅  On — launch at login")
        else:
            self.login_toggle.setObjectName("toggle_off")
            self.login_toggle.setText("⭕  Off — start manually")
        self.login_toggle.setStyleSheet("")  # Force style refresh
        self.setStyleSheet(WIZARD_STYLE)

    def _go_next(self):
        if self._step < self.TOTAL_STEPS - 1:
            self._step += 1
            self.stack.setCurrentIndex(self._step)
            self.dots.set_step(self._step)
            self.back_btn.setVisible(True)
            if self._step == self.TOTAL_STEPS - 1:
                self.next_btn.setObjectName("finish")
                self.next_btn.setText("Let's go! 🎉")
                self.next_btn.setStyleSheet("")
                self.setStyleSheet(WIZARD_STYLE)
                self.next_btn.clicked.disconnect()
                self.next_btn.clicked.connect(self._finish)
        else:
            self._finish()

    def _go_back(self):
        if self._step > 0:
            self._step -= 1
            self.stack.setCurrentIndex(self._step)
            self.dots.set_step(self._step)
            self.back_btn.setVisible(self._step > 0)
            # Restore Next button if we went back from finish
            self.next_btn.setObjectName("next")
            self.next_btn.setText("Next →")
            self.next_btn.setStyleSheet("")
            self.setStyleSheet(WIZARD_STYLE)
            try:
                self.next_btn.clicked.disconnect()
            except TypeError:
                pass
            self.next_btn.clicked.connect(self._go_next)

    def _finish(self):
        # Save settings
        name = self.name_input.text().strip() or "Buddy"
        self.settings.set("user_name", name)
        self.settings.set("reminder_interval_min", self.interval_spin.value())
        self.settings.set("launch_at_login", self._login_enabled)
        self.settings.set("first_run", False)
        self.settings.save()

        logger.info("Onboarding complete. Name=%s, interval=%d, login=%s",
                    name, self.interval_spin.value(), self._login_enabled)
        self.accept()
        self.on_complete()
