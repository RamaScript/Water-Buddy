"""First-run onboarding wizard for Water Buddy."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QWidget,
    QStackedWidget, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen

if TYPE_CHECKING:
    from settings import SettingsManager

logger = logging.getLogger("WaterBuddy")

# ── Palette ──────────────────────────────────────────────────────
BG      = "#1e1e2e"
MANTLE  = "#181825"
SURFACE = "#313244"
OVERLAY = "#45475a"
TEXT    = "#cdd6f4"
SUBTEXT = "#a6adc8"
MUTED   = "#6c7086"
BLUE    = "#89b4fa"
GREEN   = "#a6e3a1"
TEAL    = "#94e2d5"
PEACH   = "#fab387"

WIZARD_STYLE = f"""
QDialog {{
    background-color: {BG};
    color: {TEXT};
}}
QWidget {{
    font-family: 'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif;
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
}}
QSpinBox:focus {{
    border-color: {BLUE};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {OVERLAY};
    border-radius: 4px;
    width: 24px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {BLUE};
}}
QPushButton#next {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {BLUE}, stop:1 #74c7ec);
    color: {MANTLE};
    border: none;
    border-radius: 12px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#next:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #74c7ec, stop:1 {BLUE});
}}
QPushButton#next:pressed {{ padding: 13px 30px 11px 34px; }}
QPushButton#finish {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {GREEN}, stop:1 {TEAL});
    color: {MANTLE};
    border: none;
    border-radius: 12px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#finish:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {TEAL}, stop:1 {GREEN});
}}
QPushButton#back {{
    background: transparent;
    color: {MUTED};
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 14px;
}}
QPushButton#back:hover {{
    color: {TEXT};
    background-color: {SURFACE};
}}
QPushButton#tog_on {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {GREEN}, stop:1 {TEAL});
    color: {MANTLE};
    border: none;
    border-radius: 24px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
    min-width: 200px;
}}
QPushButton#tog_off {{
    background: {SURFACE};
    color: {SUBTEXT};
    border: 2px solid {OVERLAY};
    border-radius: 24px;
    padding: 12px 32px;
    font-size: 14px;
    min-width: 200px;
}}
QPushButton#tog_on:hover {{ background: {TEAL}; }}
QPushButton#tog_off:hover {{ background: {OVERLAY}; color: {TEXT}; }}
"""


# ── Step-dots indicator ────────────────────────────────────────────

class _Dots(QWidget):
    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.total   = total
        self.current = 0
        # Each dot: 10px wide + 8px gap; active dot 18px wide
        self.setFixedSize(total * 18 + (total - 1) * 8, 10)

    def set_step(self, step: int):
        self.current = step
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        x = 0
        for i in range(self.total):
            w = 18 if i == self.current else 10
            h = 10
            if i == self.current:
                p.setBrush(QBrush(QColor(BLUE)))
                p.setPen(Qt.PenStyle.NoPen)
            elif i < self.current:
                p.setBrush(QBrush(QColor(OVERLAY)))
                p.setPen(Qt.PenStyle.NoPen)
            else:
                p.setBrush(QBrush(QColor(SURFACE)))
                p.setPen(QPen(QColor(OVERLAY), 1.5))
            p.drawRoundedRect(x, 0, w, h, 5, 5)
            x += w + 8
        p.end()


# ── Page helpers ────────────────────────────────────────────────────

def _hero(emoji: str, size: int = 64) -> QLabel:
    lbl = QLabel(emoji)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"font-size:{size}px; background:transparent;")
    return lbl


def _title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(
        f"font-size:22px; font-weight:700; color:{TEXT}; background:transparent;"
    )
    return lbl


def _body(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(
        f"font-size:13px; color:{SUBTEXT}; background:transparent; line-height:150%;"
    )
    return lbl


def _card(emoji: str, text: str) -> QFrame:
    card = QFrame()
    card.setStyleSheet(
        f"QFrame {{ background:{SURFACE}; border-radius:10px; border:1px solid {OVERLAY}; }}"
    )
    row = QHBoxLayout(card)
    row.setContentsMargins(14, 10, 14, 10)
    row.setSpacing(12)
    ico = QLabel(emoji)
    ico.setStyleSheet("font-size:20px; background:transparent; border:none;")
    ico.setFixedWidth(28)
    row.addWidget(ico)
    txt = QLabel(text)
    txt.setWordWrap(True)
    txt.setStyleSheet(f"font-size:13px; color:{SUBTEXT}; background:transparent; border:none;")
    row.addWidget(txt, 1)
    return card


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:13px; font-weight:600; color:{TEXT}; background:transparent;"
    )
    return lbl


# ══════════════════════════════════════════════════════════════════
#  Wizard
# ══════════════════════════════════════════════════════════════════

class OnboardingWizard(QDialog):
    TOTAL = 4

    def __init__(self, settings: "SettingsManager", on_complete: Callable, parent=None):
        super().__init__(parent)
        self.settings     = settings
        self.on_complete  = on_complete
        self._login_on    = False
        self._step        = 0

        self.setWindowTitle("Welcome to Water Buddy")
        self.setFixedSize(460, 580)
        self.setStyleSheet(WIZARD_STYLE)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self._page_welcome())
        self.stack.addWidget(self._page_howto())
        self.stack.addWidget(self._page_setup())
        self.stack.addWidget(self._page_login())
        root.addWidget(self.stack, 1)

        # Nav bar
        nav = QFrame()
        nav.setFixedHeight(76)
        nav.setStyleSheet(
            f"background:{SURFACE}; border-top:1px solid {OVERLAY};"
        )
        nav_row = QHBoxLayout(nav)
        nav_row.setContentsMargins(24, 0, 24, 0)
        nav_row.setSpacing(12)

        self.dots = _Dots(self.TOTAL)
        nav_row.addWidget(self.dots)
        nav_row.addStretch()

        self.back_btn = QPushButton("← Back")
        self.back_btn.setObjectName("back")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setVisible(False)
        self.back_btn.clicked.connect(self._go_back)
        nav_row.addWidget(self.back_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.setObjectName("next")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._go_next)
        nav_row.addWidget(self.next_btn)

        root.addWidget(nav)

    # ── Pages ────────────────────────────────────────────────────

    def _page_welcome(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 44, 36, 24)
        lay.setSpacing(0)

        lay.addWidget(_hero("💧", 72))
        lay.addSpacing(18)
        lay.addWidget(_title("Welcome to Water Buddy"))
        lay.addSpacing(8)
        lay.addWidget(_body(
            "Your tiny desktop companion\nthat keeps you hydrated all day, every day."
        ))
        lay.addSpacing(28)

        for emoji, text in [
            ("🐾", "A cute pet that walks across your screen"),
            ("⏰", "Gentle reminders — never miss a drink again"),
            ("📊", "Tracks your daily intake & streak"),
        ]:
            lay.addWidget(_card(emoji, text))
            lay.addSpacing(8)

        lay.addStretch()
        return page

    def _page_howto(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 44, 36, 24)
        lay.setSpacing(0)

        lay.addWidget(_hero("🐾", 56))
        lay.addSpacing(14)
        lay.addWidget(_title("Here's how it works"))
        lay.addSpacing(24)

        for emoji, text in [
            ("😴", "Your pet hides in the background, quietly counting down"),
            ("🚶", "When the timer fires, it walks in from the screen corner"),
            ("💬", "It asks: \"Hey! Did you drink water?\""),
            ("✅", "Click Yes to celebrate — or Snooze if you're busy"),
            ("💧", "Lives in your menu bar — always there, never in the way"),
        ]:
            lay.addWidget(_card(emoji, text))
            lay.addSpacing(8)

        lay.addStretch()
        return page

    def _page_setup(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 36, 36, 24)
        lay.setSpacing(0)

        lay.addWidget(_hero("⚙️", 48))
        lay.addSpacing(10)
        lay.addWidget(_title("Quick Setup"))
        lay.addSpacing(4)
        lay.addWidget(_body("You can change everything later in Settings."))
        lay.addSpacing(28)

        # Name
        lay.addWidget(_field_label("👤  What's your name?"))
        lay.addSpacing(6)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name…")
        self.name_input.setFixedHeight(46)
        lay.addWidget(self.name_input)

        lay.addSpacing(22)

        # Interval
        lay.addWidget(_field_label("⏰  Remind me every:"))
        lay.addSpacing(6)

        spin_row = QHBoxLayout()
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setValue(self.settings.get("reminder_interval_min") or 30)
        self.interval_spin.setSuffix("  min")
        self.interval_spin.setFixedHeight(46)
        self.interval_spin.valueChanged.connect(self._update_interval_hint)
        spin_row.addWidget(self.interval_spin)
        spin_row.addStretch()
        lay.addLayout(spin_row)
        lay.addSpacing(6)

        self.interval_hint = QLabel()
        self.interval_hint.setStyleSheet(
            f"font-size:12px; color:{BLUE}; background:transparent;"
        )
        lay.addWidget(self.interval_hint)
        self._update_interval_hint(self.interval_spin.value())

        lay.addStretch()
        return page

    def _page_login(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 44, 36, 24)
        lay.setSpacing(0)

        lay.addWidget(_hero("🚀", 60))
        lay.addSpacing(14)
        lay.addWidget(_title("Start automatically?"))
        lay.addSpacing(8)
        lay.addWidget(_body(
            "Launch Water Buddy every time your computer starts.\n"
            "No need to open it manually each day."
        ))
        lay.addSpacing(32)

        # Big toggle button — centred
        self.login_toggle = QPushButton("⭕  Off — I'll start it manually")
        self.login_toggle.setObjectName("tog_off")
        self.login_toggle.setFixedHeight(50)
        self.login_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_toggle.clicked.connect(self._toggle_login)
        lay.addWidget(self.login_toggle, alignment=Qt.AlignmentFlag.AlignHCenter)

        lay.addSpacing(20)
        lay.addWidget(_card("ℹ️",
            "Water Buddy will appear in your menu bar automatically after every login."))

        lay.addSpacing(12)
        note = QLabel("You can always change this in Settings → Launch at Login")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setWordWrap(True)
        note.setStyleSheet(f"font-size:11px; color:{MUTED}; background:transparent;")
        lay.addWidget(note)

        lay.addStretch()
        return page

    # ── Navigation ───────────────────────────────────────────────

    def _go_next(self):
        if self._step < self.TOTAL - 1:
            self._step += 1
            self.stack.setCurrentIndex(self._step)
            self.dots.set_step(self._step)
            self.back_btn.setVisible(True)

            if self._step == self.TOTAL - 1:
                # Switch to finish button
                self.next_btn.setObjectName("finish")
                self.next_btn.setText("Let's go! 🎉")
                # Force style refresh for objectName change
                self.next_btn.style().unpolish(self.next_btn)
                self.next_btn.style().polish(self.next_btn)

    def _go_back(self):
        if self._step > 0:
            # Restore Next button if coming back from last page
            if self._step == self.TOTAL - 1:
                self.next_btn.setObjectName("next")
                self.next_btn.setText("Next →")
                self.next_btn.style().unpolish(self.next_btn)
                self.next_btn.style().polish(self.next_btn)

            self._step -= 1
            self.stack.setCurrentIndex(self._step)
            self.dots.set_step(self._step)
            self.back_btn.setVisible(self._step > 0)

    # ── Actions ──────────────────────────────────────────────────

    def _update_interval_hint(self, val: int):
        if val == 5:
            text, color = "⚡  Very frequent! Every 5 minutes", PEACH
        elif val == 30:
            text, color = f"💧  Every {val} minutes  ·  Recommended ✓", BLUE
        elif val >= 90:
            text, color = f"💤  {val // 60}h {val % 60}m between reminders", PEACH
        else:
            text, color = f"💧  I'll visit you every {val} minutes", BLUE
        self.interval_hint.setText(text)
        self.interval_hint.setStyleSheet(
            f"font-size:12px; color:{color}; background:transparent;"
        )

    def _toggle_login(self):
        self._login_on = not self._login_on
        if self._login_on:
            self.login_toggle.setObjectName("tog_on")
            self.login_toggle.setText("✅  On — launch at login")
        else:
            self.login_toggle.setObjectName("tog_off")
            self.login_toggle.setText("⭕  Off — I'll start it manually")
        self.login_toggle.style().unpolish(self.login_toggle)
        self.login_toggle.style().polish(self.login_toggle)

    def _finish(self):
        name = self.name_input.text().strip() or "Buddy"
        self.settings.set("user_name",             name)
        self.settings.set("reminder_interval_min", self.interval_spin.value())
        self.settings.set("launch_at_login",       self._login_on)
        self.settings.set("first_run",             False)
        self.settings.save()
        logger.info("Onboarding done. name=%s, interval=%d, login=%s",
                    name, self.interval_spin.value(), self._login_on)
        self.accept()
        self.on_complete()

    # Override Next click on last step
    def _go_next(self):  # noqa: F811
        if self._step < self.TOTAL - 1:
            self._step += 1
            self.stack.setCurrentIndex(self._step)
            self.dots.set_step(self._step)
            self.back_btn.setVisible(True)

            if self._step == self.TOTAL - 1:
                self.next_btn.setObjectName("finish")
                self.next_btn.setText("Let's go! 🎉")
                self.next_btn.style().unpolish(self.next_btn)
                self.next_btn.style().polish(self.next_btn)
                # Swap handler to finish
                self.next_btn.clicked.disconnect()
                self.next_btn.clicked.connect(self._finish)
        else:
            self._finish()

    def _go_back(self):  # noqa: F811
        if self._step > 0:
            if self._step == self.TOTAL - 1:
                # Coming back from finish step — restore Next
                self.next_btn.clicked.disconnect()
                self.next_btn.clicked.connect(self._go_next)
                self.next_btn.setObjectName("next")
                self.next_btn.setText("Next →")
                self.next_btn.style().unpolish(self.next_btn)
                self.next_btn.style().polish(self.next_btn)

            self._step -= 1
            self.stack.setCurrentIndex(self._step)
            self.dots.set_step(self._step)
            self.back_btn.setVisible(self._step > 0)
