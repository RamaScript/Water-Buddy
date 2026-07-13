"""Daily water intake statistics tracker."""
from __future__ import annotations

import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("WaterBuddy")


class StatsManager:
    """Track daily water intake and streaks, persisted in stats.json."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or Path(__file__).resolve().parent / "stats.json"
        self._data: dict[str, Any] = {"days": {}, "daily_goal": 8}
        self.load()

    # ── persistence ─────────────────────────────────────────────

    def load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
                logger.info("Stats loaded from %s", self._path)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Could not read stats: %s", exc)

    def save(self) -> None:
        try:
            self._path.write_text(json.dumps(self._data, indent=2))
        except OSError as exc:
            logger.error("Failed to save stats: %s", exc)

    # ── recording ───────────────────────────────────────────────

    def record_drink(self) -> None:
        """Record one glass of water for today."""
        today = self._today_key()
        day_data = self._data["days"].setdefault(today, {"count": 0, "times": []})
        day_data["count"] += 1
        day_data["times"].append(datetime.now().strftime("%H:%M"))
        self.save()
        logger.info("Drink recorded. Today's total: %d", day_data["count"])

    # ── queries ─────────────────────────────────────────────────

    def today_count(self) -> int:
        return self._data["days"].get(self._today_key(), {}).get("count", 0)

    @property
    def daily_goal(self) -> int:
        return self._data.get("daily_goal", 8)

    @daily_goal.setter
    def daily_goal(self, value: int) -> None:
        self._data["daily_goal"] = max(1, value)
        self.save()

    def today_progress(self) -> float:
        """Return progress as 0.0 → 1.0."""
        goal = self.daily_goal
        if goal <= 0:
            return 1.0
        return min(self.today_count() / goal, 1.0)

    def streak(self) -> int:
        """Number of consecutive days (including today) that met the goal."""
        streak_count = 0
        d = date.today()
        while True:
            key = d.isoformat()
            count = self._data["days"].get(key, {}).get("count", 0)
            if count >= self.daily_goal:
                streak_count += 1
                d = date.fromordinal(d.toordinal() - 1)
            else:
                break
        return streak_count

    def today_times(self) -> list[str]:
        return self._data["days"].get(self._today_key(), {}).get("times", [])

    # ── helpers ──────────────────────────────────────────────────

    @staticmethod
    def _today_key() -> str:
        return date.today().isoformat()
