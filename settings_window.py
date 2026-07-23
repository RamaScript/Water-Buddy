"""Settings & Stats dialog — Water Buddy (cross-platform)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QLineEdit, QPushButton,
    QTimeEdit, QFrame, QProgressBar, QWidget,
    QTabWidget, QScrollArea,
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor

if TYPE_CHECKING:
    from settings import SettingsManager
    from stats import StatsManager

logger = logging.getLogger("WaterBuddy")

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
_CHECKMARK_PATH = ASSETS_DIR / ".checkmark.png"


def _ensure_checkmark() -> str:
    if not _CHECKMARK_PATH.exists():
        pm = QPixmap(16, 16)
        pm.fill(QColor(0, 0, 0, 0))
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ffffff"), 2.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(3, 8, 7, 12)
        p.drawLine(7, 12, 13, 4)
        p.end()
        pm.save(str(_CHECKMARK_PATH))
    return str(_CHECKMARK_PATH)

# ── Light palette ──────────────────────────────────────────────────
BG      = "#f8f9fa"
SURFACE = "#ffffff"
CARD    = "#ffffff"
BORDER  = "#dee2e6"
TEXT    = "#1a1a2e"
SUBTEXT = "#495057"
MUTED   = "#adb5bd"
BLUE    = "#2563eb"
GREEN   = "#16a34a"
ORANGE  = "#ea580c"
RED     = "#dc2626"
TEAL    = "#0d9488"
ACCENT  = BLUE

# ── Shared stylesheet (base — checkbox checked indicator added at runtime) ──
STYLE = f"""
QDialog {{
    background: {BG};
    color: {TEXT};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}}
QTabWidget::pane {{ border: none; background: transparent; }}
QTabBar::tab {{
    background: transparent;
    color: {MUTED};
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover:!selected {{
    color: {SUBTEXT};
}}
QTabBar {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: {BG}; width: 6px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QLineEdit {{
    background: {BG};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
}}
QLineEdit:focus {{
    border-color: {ACCENT};
}}
QSpinBox, QTimeEdit {{
    background: {BG};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    min-height: 26px;
}}
QSpinBox:focus, QTimeEdit:focus {{
    border-color: {ACCENT};
}}
QSpinBox:disabled, QTimeEdit:disabled {{
    color: {MUTED};
    border-color: {SURFACE};
}}
QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {{
    background: #e9ecef;
    border: 1px solid #ced4da;
    border-radius: 4px;
    width: 22px;
    height: 13px;
}}
QSpinBox::up-button, QTimeEdit::up-button {{
    subcontrol-position: top right;
    margin: 2px 2px 1px 0;
}}
QSpinBox::down-button, QTimeEdit::down-button {{
    subcontrol-position: bottom right;
    margin: 1px 2px 2px 0;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
    background: {BLUE};
    border-color: {BLUE};
}}
QSpinBox::up-button:pressed, QSpinBox::down-button:pressed,
QTimeEdit::up-button:pressed, QTimeEdit::down-button:pressed {{
    background: #1d4ed8;
}}
QSpinBox::up-arrow, QTimeEdit::up-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 6px solid {SUBTEXT};
}}
QSpinBox::up-arrow:disabled, QTimeEdit::up-arrow:disabled {{
    border-bottom-color: {MUTED};
}}
QSpinBox::down-arrow, QTimeEdit::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {SUBTEXT};
}}
QSpinBox::down-arrow:disabled, QTimeEdit::down-arrow:disabled {{
    border-top-color: {MUTED};
}}
QCheckBox {{
    color: {TEXT};
    font-size: 13px;
    spacing: 8px;
    border:none;
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background: {BG};
}}
QCheckBox::indicator:hover {{
    border-color: {ACCENT};
}}
QCheckBox::indicator:disabled {{
    background: {SURFACE};
    border-color: {BORDER};
}}
QCheckBox:disabled {{ color: {MUTED}; }}
QPushButton#save {{
    background: {ACCENT};
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 4px 24px;
    min-height: 36px;
    font-size: 14px;
    font-weight: 700;
}}
QPushButton#save:hover {{
    background: #1d4ed8;
}}
QPushButton#save:pressed {{
    background: #1e40af;
}}
QPushButton#cancel {{
    background: {SURFACE};
    color: {SUBTEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px 24px;
    min-height: 36px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#cancel:hover {{
    background: {CARD};
    color: {TEXT};
    border-color: {SUBTEXT};
}}
QPushButton#cancel:pressed {{
    background: {BG};
}}
QProgressBar {{
    background: {SURFACE};
    border: none;
    border-radius: 4px;
    min-height: 8px;
    max-height: 8px;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 4px;
}}
QFrame#divider {{
    background: {BORDER};
    max-height: 1px;
    border: none;
}}
"""


# ── Helpers ────────────────────────────────────────────────────────

def _divider() -> QFrame:
    f = QFrame()
    f.setObjectName("divider")
    f.setStyleSheet(f"background:{BORDER}; max-height:1px; border:none;")
    f.setFixedHeight(1)
    return f


def _format_ampm(time_str: str) -> str:
    try:
        h, m = map(int, time_str.split(":"))
        period = "AM" if h < 12 else "PM"
        h12 = h % 12
        if h12 == 0:
            h12 = 12
        return f"{h12}:{m:02d} {period}"
    except Exception:
        return time_str

def _section(title: str) -> QLabel:
    lbl = QLabel(title)
    lbl.setStyleSheet(
        f"font-size:11px; font-weight:700; color:{MUTED}; "
        f"letter-spacing:0.5px; background:transparent; padding:0;"
    )
    return lbl


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color:{SUBTEXT}; font-size:12px; font-weight:500; background:transparent; border:none;"
    )
    return lbl


def _hint(text: str = "", color: str = SUBTEXT) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color:{color}; font-size:11px; background:transparent;border:none;")
    return lbl


def _scrollable(w: QWidget) -> QScrollArea:
    a = QScrollArea()
    a.setWidget(w)
    a.setWidgetResizable(True)
    a.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    a.setFrameShape(QFrame.Shape.NoFrame)
    return a


def _group(items: list, spacing: int = 6) -> QFrame:
    g = QFrame()
    g.setStyleSheet(f"background:{CARD}; border:1px solid {BORDER}; border-radius:8px;")
    lay = QVBoxLayout(g)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(spacing)
    for item in items:
        if isinstance(item, QWidget):
            lay.addWidget(item)
        elif item is not None:
            lay.addWidget(QLabel(str(item)))
    return g


# ══════════════════════════════════════════════════════════════════
#  Dialog
# ══════════════════════════════════════════════════════════════════

class SettingsDialog(QDialog):
    """Tabbed Settings + Stats dialog with dark theme."""

    def __init__(self, settings: "SettingsManager", stats: "StatsManager",
                 start_tab: int = 0, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.stats    = stats

        self.setWindowTitle("Water Buddy — Settings")
        self.setFixedSize(500, 600)
        check_path = _ensure_checkmark()
        self.setStyleSheet(STYLE + f"""
            QFrame#header {{
                background: {SURFACE};
                border: none;
                border-bottom: 1px solid {BORDER};
            }}
            QFrame#footer {{
                background: {SURFACE};
                border: none;
                border-top: 1px solid {BORDER};
            }}
            QCheckBox::indicator:checked {{
                background: {ACCENT};
                border-color: {ACCENT};
                image: url("{check_path}");
            }}
            
            
        """)
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header ──
        hdr = QFrame()
        hdr.setObjectName("header")
        hl = QVBoxLayout(hdr)
        hl.setContentsMargins(24, 16, 24, 12)
        hl.setSpacing(1)
        t = QLabel("💧 Water Buddy")
        t.setStyleSheet(f"font-size:18px; font-weight:700; color:{TEXT}; background:transparent; border:none;")
        hl.addWidget(t)
        s = QLabel("Settings")
        s.setStyleSheet(f"font-size:11px; color:{MUTED}; background:transparent; border:none;")
        hl.addWidget(s)
        root.addWidget(hdr)

        # ── Tabs ──
        self.tabs = QTabWidget()
        self.tabs.addTab(_scrollable(self._settings_tab()), "Settings")
        self.tabs.addTab(_scrollable(self._stats_tab()), "Stats")
        self.tabs.setCurrentIndex(start_tab)
        root.addWidget(self.tabs)

        # ── Footer ──
        ft = QFrame()
        ft.setObjectName("footer")
        fl = QHBoxLayout(ft)
        fl.setContentsMargins(16, 10, 16, 10)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("cancel")
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.setMinimumHeight(36)
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.setObjectName("save")
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.setMinimumHeight(36)
        save.setDefault(True)
        save.clicked.connect(self._save)
        fl.addStretch()
        fl.addWidget(cancel)
        fl.addWidget(save)
        root.addWidget(ft)

    # ══════════════════════════════════════════════════════════════
    #  Settings tab
    # ══════════════════════════════════════════════════════════════

    def _settings_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(w)
        lay.setSpacing(0)
        lay.setContentsMargins(20, 16, 20, 16)

        # ── Profile ──
        lay.addWidget(_section("PROFILE"))
        lay.addSpacing(8)
        self.name_input = QLineEdit(self.settings.user_name)
        self.name_input.setPlaceholderText("Your name")
        self.name_input.setStyleSheet("QLineEdit{border:1px solid "+ BORDER +  ";background:transparent;padding:4px 8px;font-size:14px;color:" + TEXT + ";} QLineEdit:focus{border:none;}")
        lay.addWidget(_group([
           _row( _field_label("Name"),
            self.name_input)
        ]))
        lay.addSpacing(20)

        # ── Reminders ──
        lay.addWidget(_section("REMINDERS"))
        lay.addSpacing(8)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setSuffix(" min")
        self.interval_spin.setValue(self.settings.get("reminder_interval_min"))
        self.interval_spin.setStyleSheet("QSpinBox{border:1px solid "+ BORDER +  ";background:transparent;padding:4px 8px;font-size:14px;color:" + TEXT + ";} QSpinBox:focus{border:none;}")
        self.interval_spin.setFixedWidth(110)
        self.interval_spin.valueChanged.connect(self._on_interval)
        self.interval_hint = _hint()
        self.snooze_spin = QSpinBox()
        self.snooze_spin.setRange(1, 30)
        self.snooze_spin.setSuffix(" min")
        self.snooze_spin.setValue(self.settings.get("snooze_duration_min"))
        self.snooze_spin.setStyleSheet("QSpinBox{border:1px solid "+ BORDER +  ";background:transparent;padding:4px 8px;font-size:14px;color:" + TEXT + ";} QSpinBox:focus{border:none;}")
        self.snooze_spin.setFixedWidth(110)
        self.snooze_spin.valueChanged.connect(self._on_snooze)
        self.snooze_hint = _hint()
        lay.addWidget(_group([
           _row( _field_label("Remind me every"),
            self.interval_spin,
            self.interval_hint,),
            _spacer(4),
            _row( _field_label("Snooze duration"),
            self.snooze_spin,
            self.snooze_hint,),
        ], spacing=4))
        lay.addSpacing(20)

        # ── Quiet Hours ──
        lay.addWidget(_section("QUIET HOURS"))
        lay.addSpacing(8)
        self.quiet_check = QCheckBox("No reminders during these hours")
        self.quiet_check.setChecked(self.settings.quiet_hours_enabled)
        self.quiet_check.toggled.connect(self._on_quiet_toggle)
        
        self.quiet_start = QTimeEdit()
        self.quiet_start.setDisplayFormat("h:mm AP")
        h, m = self.settings.quiet_hours_start.split(":")
        self.quiet_start.setTime(QTime(int(h), int(m)))
        self.quiet_start.setFixedWidth(110)
        self.quiet_start.timeChanged.connect(self._on_quiet_time)
        self.quiet_end = QTimeEdit()
        self.quiet_end.setDisplayFormat("h:mm AP")
        h, m = self.settings.quiet_hours_end.split(":")
        self.quiet_end.setTime(QTime(int(h), int(m)))
        self.quiet_end.setFixedWidth(110)
        self.quiet_end.timeChanged.connect(self._on_quiet_time)
        self.quiet_hint = _hint()
        lay.addWidget(_group([
            self.quiet_check,
            _spacer(2),
            _row(self.quiet_start, _label("to"), self.quiet_end, stretch=False),
            self.quiet_hint,
        ]))
        lay.addSpacing(20)

        # ── Other ──
        lay.addWidget(_section("OTHER"))
        lay.addSpacing(8)
        self.sound_check = QCheckBox("Play notification sound")
        self.sound_check.setChecked(self.settings.sound_enabled)
        self.login_check = QCheckBox("Launch at login")
        self.login_check.setChecked(self.settings.get("launch_at_login"))
        self.login_check.toggled.connect(self._on_login)
        self.login_hint = _hint()
        lay.addWidget(_group([
            self.sound_check,
            _spacer(2),
            self.login_check,
            self.login_hint,
        ]))

        lay.addStretch()
        self._on_interval(self.interval_spin.value())
        self._on_snooze(self.snooze_spin.value())
        self._on_quiet_toggle(self.quiet_check.isChecked())
        return w

    # ══════════════════════════════════════════════════════════════
    #  Stats tab
    # ══════════════════════════════════════════════════════════════

    def _stats_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(w)
        lay.setSpacing(0)
        lay.setContentsMargins(20, 16, 20, 16)

        count = self.stats.today_count()
        goal  = self.stats.daily_goal
        pct   = int(self.stats.today_progress() * 100)
        streak = self.stats.streak()
        times = self.stats.today_times()

        # ── Progress ──
        lay.addWidget(_section("TODAY"))
        lay.addSpacing(8)
        pc = QFrame()
        pc.setStyleSheet(f"background:{CARD}; border:1px solid {BORDER}; border-radius:8px;")
        pcl = QVBoxLayout(pc)
        pcl.setContentsMargins(20, 18, 20, 18)
        pcl.setSpacing(8)
        top = QHBoxLayout()
        tl = QLabel("Daily goal")
        tl.setStyleSheet(f"font-size:12px; color:{MUTED}; background:transparent; border:none;")
        top.addWidget(tl)
        tp = QLabel(f"{pct}%")
        tp.setStyleSheet(
            f"font-size:12px; font-weight:700; color:{GREEN if pct >= 100 else ACCENT}; "
            f"background:transparent; border:none;"
        )
        top.addWidget(tp)
        pcl.addLayout(top)
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(pct)
        bar.setTextVisible(False)
        pcl.addWidget(bar)
        val = QLabel(f"{count}  /  {goal}  glasses")
        val.setStyleSheet(
            f"font-size:22px; font-weight:800; color:{TEXT}; background:transparent; border:none;"
        )
        pcl.addWidget(val)
        if pct >= 100:
            st = QLabel("Goal reached ✓")
            st.setStyleSheet(f"font-size:11px; font-weight:600; color:{GREEN}; background:transparent; border:none;")
            pcl.addWidget(st)
        elif count > 0:
            st = QLabel(f"{goal - count} more to go")
            st.setStyleSheet(f"font-size:11px; font-weight:600; color:{ORANGE}; background:transparent; border:none;")
            pcl.addWidget(st)
        lay.addWidget(pc)
        lay.addSpacing(20)

        # ── Streak ──
        lay.addWidget(_section("STREAK"))
        lay.addSpacing(8)
        sc = QFrame()
        sc.setStyleSheet(f"background:{CARD}; border:1px solid {BORDER}; border-radius:8px;")
        scl = QHBoxLayout(sc)
        scl.setContentsMargins(20, 16, 20, 16)
        scl.setSpacing(12)
        si = QLabel("🔥" if streak > 0 else "⏳")
        si.setStyleSheet("font-size:24px; background:transparent; border:none;")
        scl.addWidget(si)
        sv = QVBoxLayout()
        sv.setSpacing(0)
        if streak > 0:
            sv.addWidget(self._stat_label(f"{streak} day{'s' if streak > 1 else ''}", TEXT, 16))
            sv.addWidget(self._stat_label("Keep it going!", MUTED, 11))
        else:
            sv.addWidget(self._stat_label("No streak yet", SUBTEXT, 16))
            sv.addWidget(self._stat_label("Start today!", MUTED, 11))
        scl.addLayout(sv)
        scl.addStretch()
        lay.addWidget(sc)
        lay.addSpacing(20)

        # ── Goal ──
        lay.addWidget(_section("GOAL"))
        lay.addSpacing(8)
        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(1, 20)
        self.goal_spin.setSuffix(" glasses")
        self.goal_spin.setValue(self.stats.daily_goal)
        self.goal_spin.setFixedWidth(130)
        self.goal_spin.valueChanged.connect(self._on_goal)
        self.goal_hint = _hint(f"Target: {goal} per day")
        lay.addWidget(_group([
            _row(self.goal_spin, label="Daily target"),
            self.goal_hint,
        ]))
        lay.addSpacing(20)

        # ── Log ──
        lay.addWidget(_section("LOG"))
        lay.addSpacing(8)
        if times:
            lc = QFrame()
            lc.setStyleSheet(f"background:{CARD}; border:1px solid {BORDER}; border-radius:8px;")
            lcl = QVBoxLayout(lc)
            lcl.setContentsMargins(16, 10, 16, 10)
            lcl.setSpacing(3)
            for t in times[-8:]:
                e = QLabel(f"💧  {_format_ampm(t)}")
                e.setStyleSheet(f"color:{GREEN}; font-size:12px; background:transparent; border:none;")
                lcl.addWidget(e)
            if len(times) > 8:
                m = QLabel(f"…and {len(times) - 8} more")
                m.setStyleSheet(f"color:{MUTED}; font-size:11px; background:transparent; border:none;")
                lcl.addWidget(m)
            lay.addWidget(lc)
        else:
            ec = QFrame()
            ec.setStyleSheet(f"background:{CARD}; border:1px solid {BORDER}; border-radius:8px;")
            ecl = QVBoxLayout(ec)
            ecl.setContentsMargins(16, 20, 16, 20)
            ecl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ei = QLabel("💧")
            ei.setStyleSheet("font-size:24px; background:transparent; border:none;")
            ei.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ecl.addWidget(ei)
            et = QLabel("No drinks logged yet today")
            et.setAlignment(Qt.AlignmentFlag.AlignCenter)
            et.setStyleSheet(f"color:{MUTED}; font-size:12px; background:transparent; border:none;")
            ecl.addWidget(et)
            lay.addWidget(ec)

        lay.addStretch()
        return w

    def _stat_label(self, text: str, color: str, size: int) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(
            f"font-size:{size}px; font-weight:{700 if size > 14 else 500}; "
            f"color:{color}; background:transparent; border:none;"
        )
        return l

    # ══════════════════════════════════════════════════════════════
    #  Handlers
    # ══════════════════════════════════════════════════════════════

    def _on_interval(self, v: int):
        if v == 5:
            self.interval_hint.setText("Very frequent — every 5 minutes")
            self.interval_hint.setStyleSheet(f"color:{ORANGE}; font-size:11px; background:transparent;border:none;")
        elif v == 30:
            self.interval_hint.setText("Recommended")
            self.interval_hint.setStyleSheet(f"color:{GREEN}; font-size:11px; background:transparent; border:none;")
        elif v >= 90:
            self.interval_hint.setText(f"{v // 60}h {v % 60}m between reminders")
            self.interval_hint.setStyleSheet(f"color:{ORANGE}; font-size:11px; background:transparent; border:none;")
        else:
            self.interval_hint.setText(f"Every {v} minutes")
            self.interval_hint.setStyleSheet(f"color:{SUBTEXT}; font-size:11px; background:transparent; border:none;")

    def _on_snooze(self, v: int):
        if v == 1:
            self.snooze_hint.setText("1 minute — very short")
            self.snooze_hint.setStyleSheet(f"color:{ORANGE}; font-size:11px; background:transparent; border:none;")
        else:
            self.snooze_hint.setText(f"Back in {v} minutes")
            self.snooze_hint.setStyleSheet(f"color:{SUBTEXT}; font-size:11px; background:transparent; border:none;")

    def _on_quiet_toggle(self, on: bool):
        self.quiet_start.setEnabled(on)
        self.quiet_end.setEnabled(on)
        if on:
            self._on_quiet_time()
        else:
            self.quiet_hint.setText("")

    def _on_quiet_time(self):
        if not self.quiet_check.isChecked():
            return
        s = self.quiet_start.time()
        e = self.quiet_end.time()
        if s == e:
            self.quiet_hint.setText("Start and end are the same")
            self.quiet_hint.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        else:
            self.quiet_hint.setText(
                f"Quiet hours {s.toString('h:mm AP')} – {e.toString('h:mm AP')}"
            )
            self.quiet_hint.setStyleSheet(f"color:{SUBTEXT}; font-size:11px; background:transparent;")

    def _on_login(self, on: bool):
        self.login_hint.setText("Starts at login" if on else "")
        self.login_hint.setStyleSheet(f"color:{GREEN}; font-size:11px; background:transparent;" if on else f"color:{SUBTEXT}; font-size:11px; background:transparent;")

    def _on_goal(self, v: int):
        self.goal_hint.setText(f"Target: {v} per day")

    # ══════════════════════════════════════════════════════════════
    #  Save
    # ══════════════════════════════════════════════════════════════

    def _save(self):
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


# ── Inline helpers (defined after classes they use) ─────────────────

def _row(*items, label: str = "", stretch: bool = True) -> QWidget:
    c = QWidget()
    c.setStyleSheet("background:transparent;border:none;")
    r = QHBoxLayout(c)
    r.setContentsMargins(0, 0, 0, 0)
    r.setSpacing(8)
    if label:
        r.addWidget(_field_label(label))
    for item in items:
        if isinstance(item, QWidget):
            r.addWidget(item)
    if stretch:
        r.addStretch()
    return c


def _spacer(h: int = 4) -> QWidget:
    s = QWidget()
    s.setFixedHeight(h)
    s.setStyleSheet("background:transparent; border:none;")
    return s


def _label(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(f"color:{MUTED}; font-size:12px; background:transparent; border:none;")
    return l