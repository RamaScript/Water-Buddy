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

# ── Light palette ─────────────────────────────────────────────────
BG      = "#f8f9fa"
SURFACE = "#ffffff"
CARD    = "#ffffff"
BORDER  = "#dee2e6"
TEXT    = "#1a1a2e"
SUBTEXT = "#495057"
MUTED   = "#adb5bd"
BLUE    = "#2563eb"
GREEN   = "#16a34a"
TEAL    = "#0d9488"
PEACH   = "#ea580c"

WIZARD_STYLE = f"""
QDialog {{
    background: {BG};
    color: {TEXT};
}}
QFrame#wizard_footer {{
    background: {SURFACE};
    border: none;
    border-top: 1px solid {BORDER};
}}
QWidget {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}}
QLabel {{
    color: {TEXT};
    background: transparent;
    border: none;
}}
QLineEdit {{
    background: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 15px;
}}
QLineEdit:focus {{
    border-color: {BLUE};
}}
QSpinBox {{
    background: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 15px;
}}
QSpinBox:focus {{
    border-color: {BLUE};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {BG};
    border-radius: 3px;
    width: 22px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {BLUE};
}}
QPushButton#next {{
    background: {BLUE};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: 600;
}}
QPushButton#next:hover {{
    background: #1d4ed8;
}}
QPushButton#next:pressed {{ padding: 11px 27px 9px 29px; }}
QPushButton#finish {{
    background: {GREEN};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: 600;
}}
QPushButton#finish:hover {{
    background: #15803d;
}}
QPushButton#back {{
    background: transparent;
    color: {SUBTEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
}}
QPushButton#back:hover {{
    color: {TEXT};
    background: {BG};
    border-color: {SUBTEXT};
}}
QPushButton#tog_on {{
    background: {BLUE};
    color: #ffffff;
    border: none;
    border-radius: 24px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: 600;
    min-width: 200px;
}}
QPushButton#tog_off {{
    background: {SURFACE};
    color: {SUBTEXT};
    border: 1px solid {BORDER};
    border-radius: 24px;
    padding: 12px 32px;
    font-size: 14px;
    min-width: 200px;
}}
QPushButton#tog_on:hover {{ background: #1d4ed8; }}
QPushButton#tog_off:hover {{ background: {BG}; color: {TEXT}; border-color: {SUBTEXT}; }}
"""


# ── Step-dots indicator ────────────────────────────────────────────

class _Dots(QWidget):
    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.total   = total
        self.current = 0
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
                p.setBrush(QBrush(QColor(MUTED)))
                p.setPen(Qt.PenStyle.NoPen)
            else:
                p.setBrush(QBrush(QColor(SURFACE)))
                p.setPen(QPen(QColor(BORDER), 1.5))
            p.drawRoundedRect(x, 0, w, h, 5, 5)
            x += w + 8
        p.end()


# ── Page helpers ────────────────────────────────────────────────────

def _hero(emoji: str, size: int = 64) -> QLabel:
    lbl = QLabel(emoji)
    lbl.setStyleSheet(f"font-size:{size}px; background:transparent; border:none;")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return lbl


def _heading(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:22px; font-weight:700; color:{TEXT}; background:transparent; border:none;"
    )
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setWordWrap(True)
    return lbl


def _body(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:14px; color:{SUBTEXT}; background:transparent; border:none;"
    )
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setWordWrap(True)
    return lbl


def _card(widgets: list[QWidget], spacing: int = 6) -> QFrame:
    f = QFrame()
    f.setStyleSheet(f"background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px;")
    lay = QVBoxLayout(f)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(spacing)
    for w in widgets:
        lay.addWidget(w)
    return f


# ══════════════════════════════════════════════════════════════════
#  Wizard
# ══════════════════════════════════════════════════════════════════

class OnboardingWizard(QDialog):
    """4-step first-run wizard."""

    def __init__(self, settings: "SettingsManager",
                 on_complete: Callable[[], None]):
        super().__init__()
        self.settings = settings
        self.on_complete = on_complete

        self.setWindowTitle("Welcome to Water Buddy")
        self.setFixedSize(480, 560)
        self.setStyleSheet(WIZARD_STYLE)

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Content area
        self.stack = QStackedWidget()
        self.stack.addWidget(self._page_welcome())
        self.stack.addWidget(self._page_name())
        self.stack.addWidget(self._page_interval())
        self.stack.addWidget(self._page_done())
        root.addWidget(self.stack)

        # Footer
        footer = QFrame()
        footer.setObjectName("wizard_footer")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 12, 20, 12)

        self.back_btn = QPushButton("Back")
        self.back_btn.setObjectName("back")
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dots = _Dots(4)
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("next")
        self.next_btn.clicked.connect(self._go_next)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        fl.addWidget(self.back_btn)
        fl.addStretch()
        fl.addWidget(self.dots, alignment=Qt.AlignmentFlag.AlignCenter)
        fl.addStretch()
        fl.addWidget(self.next_btn)
        root.addWidget(footer)

        self._step = 0
        self._sync()

    # ── Pages ────────────────────────────────────────────────────────

    def _page_welcome(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 20)
        l.setSpacing(16)
        l.addStretch()
        l.addWidget(_hero("💧", 72))
        l.addSpacing(8)
        l.addWidget(_heading("Meet Water Buddy"))
        l.addWidget(_body(
            "Your friendly desktop pet that reminds you to drink water "
            "throughout the day. Stay hydrated, stay healthy!"
        ))
        l.addWidget(_body("Let's get you set up in 3 quick steps →"))
        l.addStretch()
        return w

    def _page_name(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 20)
        l.setSpacing(14)
        l.addStretch()
        l.addWidget(_hero("👤", 56))
        l.addWidget(_heading("What's your name?"))
        l.addWidget(_body("Your buddy will greet you by name."))
        l.addSpacing(8)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name…")
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.name_input)
        l.addSpacing(12)
        self.login_tog = QPushButton("Launch at login")
        self.login_tog.setObjectName("tog_on")
        self.login_tog.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_tog.clicked.connect(self._toggle_login)
        self._login_on = True
        l.addWidget(self.login_tog)
        l.addStretch()
        return w

    def _page_interval(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 20)
        l.setSpacing(14)
        l.addStretch()
        l.addWidget(_hero("⏰", 56))
        l.addWidget(_heading("Reminder frequency"))
        l.addWidget(_body("How often should your buddy check in?"))
        l.addSpacing(8)

        self.interval_spin = QSpinBox()
        card = _card([
            QLabel("Remind me every"),
            self.interval_spin,
        ])
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setSuffix("  minutes")
        self.interval_spin.setValue(30)
        self.interval_spin.setFixedWidth(160)
        self.interval_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(card)

        self.interval_hint = QLabel("Recommended: 30 minutes")
        self.interval_hint.setStyleSheet(
            f"color:{MUTED}; font-size:12px; background:transparent; border:none;"
        )
        self.interval_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.interval_hint)
        self.interval_spin.valueChanged.connect(self._on_interval_changed)

        l.addStretch()
        return w

    def _page_done(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 20)
        l.setSpacing(16)
        l.addStretch()
        l.addWidget(_hero("🎉", 72))
        l.addWidget(_heading("You're all set!"))
        l.addWidget(_body(
            "Your buddy will start checking in on you soon. "
            "Stay hydrated and take care!"
        ))
        l.addStretch()
        return w

    # ── Navigation ──────────────────────────────────────────────────

    def _go_next(self):
        if self._step == 0:
            self.stack.setCurrentIndex(1)
            self._step = 1
        elif self._step == 1:
            name = self.name_input.text().strip() or "Buddy"
            self.settings.set("user_name", name)
            self.settings.set("launch_at_login", self._login_on)
            self.settings.save()
            self.stack.setCurrentIndex(2)
            self._step = 2
        elif self._step == 2:
            self.settings.set("reminder_interval_min", self.interval_spin.value())
            self.settings.save()
            self.stack.setCurrentIndex(3)
            self._step = 3
            self.back_btn.hide()
            self.next_btn.setText("Get Started 🎉")
            self.next_btn.setObjectName("finish")
            self.next_btn.setStyleSheet("")
            self.next_btn.clicked.disconnect()
            self.next_btn.clicked.connect(self._finish)
        self._sync()

    def _go_back(self):
        if self._step == 1:
            self.stack.setCurrentIndex(0)
            self._step = 0
        elif self._step == 2:
            self.stack.setCurrentIndex(1)
            self._step = 1
        self._sync()

    def _sync(self):
        self.back_btn.setVisible(self._step > 0)
        self.dots.set_step(self._step)

    def _toggle_login(self):
        self._login_on = not self._login_on
        self.login_tog.setObjectName("tog_on" if self._login_on else "tog_off")
        self.login_tog.setStyleSheet("")

    def _on_interval_changed(self, val: int):
        if val == 30:
            self.interval_hint.setText("Recommended: 30 minutes")
            self.interval_hint.setStyleSheet(
                f"color:{GREEN}; font-size:12px; background:transparent; border:none;"
            )
        elif val < 10:
            self.interval_hint.setText("Very frequent!")
            self.interval_hint.setStyleSheet(
                f"color:{PEACH}; font-size:12px; background:transparent; border:none;"
            )
        else:
            self.interval_hint.setText(f"Every {val} minutes")
            self.interval_hint.setStyleSheet(
                f"color:{MUTED}; font-size:12px; background:transparent; border:none;"
            )

    def _finish(self):
        logger.info("Onboarding complete.")
        self.settings.set("first_run", False)
        self.settings.save()
        self.accept()
        self.on_complete()
