"""System tray icon for Water Buddy (macOS menu bar)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt

logger = logging.getLogger("WaterBuddy")


def _create_tray_icon_pixmap() -> QPixmap:
    """Draw a simple water drop icon for the tray."""
    size = 64
    pm = QPixmap(size, size)
    pm.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw a blue water drop
    painter.setBrush(QColor(100, 180, 255))
    painter.setPen(Qt.PenStyle.NoPen)

    from PyQt6.QtGui import QPainterPath
    path = QPainterPath()
    cx, cy = size / 2, size / 2
    # Teardrop shape
    path.moveTo(cx, 8)
    path.cubicTo(cx - 22, cy - 4, cx - 24, cy + 16, cx, cy + 24)
    path.cubicTo(cx + 24, cy + 16, cx + 22, cy - 4, cx, 8)
    painter.drawPath(path)

    painter.end()
    return pm


class SystemTrayApp:
    """Menu-bar tray icon with quick actions."""

    def __init__(
        self,
        app,
        on_pause_toggle: Callable[[], None],
        on_drink_now: Callable[[], None],
        on_open_settings: Callable[[], None],
        on_open_stats: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self.app = app
        self._paused = False

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(_create_tray_icon_pixmap()))
        self.tray.setToolTip("Water Buddy 💧")

        # Build menu
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #0d1117;
                color: #e6edf3;
                border: 1px solid #21262d;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1c2333;
            }
            QMenu::item:disabled {
                color: #484f58;
            }
            QMenu::separator {
                height: 1px;
                background: #21262d;
                margin: 4px 8px;
            }
        """)

        # ── Live countdown (disabled, display-only) ──
        self.reminder_action = self.menu.addAction("⏱️  Next — --:--")
        self.reminder_action.setEnabled(False)

        self.menu.addSeparator()

        self.pause_action = self.menu.addAction("⏸️  Pause Reminders")
        self.pause_action.triggered.connect(on_pause_toggle)

        self.drink_action = self.menu.addAction("💧  Drink Now!")
        self.drink_action.triggered.connect(on_drink_now)

        self.menu.addSeparator()

        settings_action = self.menu.addAction("⚙️  Settings...")
        settings_action.triggered.connect(on_open_settings)

        stats_action = self.menu.addAction("📊  Today's Stats")
        stats_action.triggered.connect(on_open_stats)

        self.menu.addSeparator()

        quit_action = self.menu.addAction("❌  Quit")
        quit_action.triggered.connect(on_quit)

        self.tray.setContextMenu(self.menu)
        self.tray.show()
        logger.info("System tray icon created.")

    def set_paused(self, paused: bool) -> None:
        self._paused = paused
        if paused:
            self.pause_action.setText("▶️  Resume Reminders")
            self.tray.setToolTip("Water Buddy 💧 (Paused)")
        else:
            self.pause_action.setText("⏸️  Pause Reminders")
            self.tray.setToolTip("Water Buddy 💧")

    def update_reminder_time(self, text: str) -> None:
        self.reminder_action.setText(text)

    def update_stats_text(self, count: int, goal: int) -> None:
        self.drink_action.setText(f"💧  Drink Now! ({count}/{goal} today)")
