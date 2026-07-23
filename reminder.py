"""Reminder timer with settings integration and quiet-hours support."""
from __future__ import annotations

import logging
import time
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
        self._interval_ms = 0
        self._start_time: float | None = None

    def start(self) -> None:
        interval = self.settings.reminder_interval_ms
        logger.info("Starting reminder timer for %d ms (%d min)",
                     interval, interval // 60000)
        self._interval_ms = interval
        self._start_time = time.time()
        self.timer.start(interval)

    def start_snooze(self) -> None:
        interval = self.settings.snooze_interval_ms
        logger.info("Starting snooze timer for %d ms (%d min)",
                     interval, interval // 60000)
        self._interval_ms = interval
        self._start_time = time.time()
        self.timer.start(interval)

    def stop(self) -> None:
        self.timer.stop()
        self._start_time = None

    def pause(self) -> None:
        self._paused = True
        self.timer.stop()
        self._start_time = None
        logger.info("Reminders paused.")

    def resume(self) -> None:
        self._paused = False
        self.start()
        logger.info("Reminders resumed.")

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def quiet_hours_active(self) -> bool:
        return self._is_quiet_hours()

    @property
    def remaining_ms(self) -> int:
        if self._start_time is None:
            return 0
        elapsed_ms = (time.time() - self._start_time) * 1000
        return max(0, int(self._interval_ms - elapsed_ms))

    @property
    def remaining_str(self) -> str:
        if self._start_time is None:
            return "--:--"
        total_s = self.remaining_ms // 1000
        return f"{total_s // 60:02d}:{total_s % 60:02d}"

    def _is_quiet_hours(self) -> bool:
        if not self.settings.quiet_hours_enabled:
            return False

        now = datetime.now().strftime("%H:%M")
        start = self.settings.quiet_hours_start
        end = self.settings.quiet_hours_end

        # Handle overnight quiet hours (e.g. 22:00 → 07:00)
        if start <= end:
            in_range = start <= now <= end
        else:
            in_range = now >= start or now <= end

        logger.debug(
            "Quiet hours check: now=%s start=%s end=%s enabled=True → %s",
            now, start, end, in_range,
        )
        return in_range

    def _trigger(self) -> None:
        self.stop()

        if self._is_quiet_hours():
            logger.info("Quiet hours active — rescheduling.")
            self.start()
            return

        logger.debug("Reminder triggered — showing pet.")
        self.on_reminder()