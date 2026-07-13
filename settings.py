"""Persistent settings manager for Water Buddy."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("WaterBuddy")

DEFAULTS = {
    "reminder_interval_min": 30,
    "snooze_duration_min": 5,
    "quiet_hours_enabled": False,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "07:00",
    "user_name": "Buddy",
    "sound_enabled": True,
    "launch_at_login": False,
}

class SettingsManager:
    """Load, query, and persist user settings as JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or Path(__file__).resolve().parent / "settings.json"
        self._data: dict[str, Any] = dict(DEFAULTS)
        self.load()

    # ── public API ──────────────────────────────────────────────

    def get(self, key: str) -> Any:
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def save(self) -> None:
        try:
            self._path.write_text(json.dumps(self._data, indent=2))
            logger.info("Settings saved to %s", self._path)
        except OSError as exc:
            logger.error("Failed to save settings: %s", exc)

    def load(self) -> None:
        if self._path.exists():
            try:
                stored = json.loads(self._path.read_text())
                self._data.update(stored)
                logger.info("Settings loaded from %s", self._path)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Could not read settings, using defaults: %s", exc)
        else:
            logger.info("No settings file found, using defaults.")
            self.save()  # persist defaults on first run

    @property
    def reminder_interval_ms(self) -> int:
        return int(self.get("reminder_interval_min") * 60 * 1000)

    @property
    def snooze_interval_ms(self) -> int:
        return int(self.get("snooze_duration_min") * 60 * 1000)

    @property
    def user_name(self) -> str:
        return str(self.get("user_name"))

    @property
    def sound_enabled(self) -> bool:
        return bool(self.get("sound_enabled"))

    @property
    def quiet_hours_enabled(self) -> bool:
        return bool(self.get("quiet_hours_enabled"))

    @property
    def quiet_hours_start(self) -> str:
        return str(self.get("quiet_hours_start"))

    @property
    def quiet_hours_end(self) -> str:
        return str(self.get("quiet_hours_end"))
