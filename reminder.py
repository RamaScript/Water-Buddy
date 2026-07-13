"""Reminder timer with settings integration and quiet-hours support."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable

from PyQt6.QtCore import QTimer

from settings import SettingsManager

logger = logging.getLogger("WaterBuddy")


class ReminderManager:
    def __init__(self, settings: SettingsManager, on_reminder: Callable[[], None]) -> None:
        self.settings = settings
        self.on_reminder = on_reminder
        self.timer = QTimer()
        self.timer.timeout.connect(self._trigger)
        self._paused = False

    def start(self) -> None:
        interval = self.settings.reminder_interval_ms
        logger.info("Starting reminder timer for %d ms (%d min)",
                     interval, interval // 60000)
        self.timer.start(interval)

    def start_snooze(self) -> None:
        interval = self.settings.snooze_interval_ms
        logger.info("Starting snooze timer for %d ms (%d min)",
                     interval, interval // 60000)
        self.timer.start(interval)

    def stop(self) -> None:
        self.timer.stop()

    def pause(self) -> None:
        self._paused = True
        self.timer.stop()
        logger.info("Reminders paused.")

    def resume(self) -> None:
        self._paused = False
        self.start()
        logger.info("Reminders resumed.")

    @property
    def is_paused(self) -> bool:
        return self._paused

    def _is_quiet_hours(self) -> bool:
        if not self.settings.quiet_hours_enabled:
            return False

        now = datetime.now().strftime("%H:%M")
        start = self.settings.quiet_hours_start
        end = self.settings.quiet_hours_end

        # Handle overnight quiet hours (e.g. 22:00 → 07:00)
        if start <= end:
            return start <= now <= end
        else:
            return now >= start or now <= end

    def _trigger(self) -> None:
        self.stop()

        if self._is_quiet_hours():
            logger.info("Quiet hours active. Rescheduling.")
            self.start()
            return

        self.on_reminder()