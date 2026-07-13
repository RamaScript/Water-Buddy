"""Water Buddy — Desktop Pet Water Reminder (PyQt6)."""
from __future__ import annotations

import sys
import logging
import subprocess
from enum import Enum, auto
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QSoundEffect

from ui import DesktopPetUI
from animations import AnimationManager
from reminder import ReminderManager
from settings import SettingsManager
from stats import StatsManager
from tray import SystemTrayApp
from settings_window import SettingsDialog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("WaterBuddy")

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
PLIST_LABEL = "com.waterbuddy.app"


class PetState(Enum):
    HIDDEN = auto()
    WALKING_IN = auto()
    ASKING = auto()
    REJOICING = auto()
    SAD = auto()
    WALKING_OUT = auto()


class AppController:
    MOVE_STEP_PX = 8
    MOVE_DELAY_MS = 16

    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.settings = SettingsManager()
        self.stats = StatsManager()

        # UI
        self.ui = DesktopPetUI()
        self.animations = AnimationManager(
            image_label=self.ui.image_label,
            assets_dir=ASSETS_DIR,
        )

        # Reminders
        self.reminders = ReminderManager(self.settings, self.handle_reminder)
        self.ui.set_button_handlers(on_yes=self.handle_yes, on_snooze=self.handle_snooze)

        # System Tray
        self.tray = SystemTrayApp(
            app=app,
            on_pause_toggle=self.toggle_pause,
            on_drink_now=self.drink_now,
            on_open_settings=self.open_settings,
            on_open_stats=self.open_stats,
            on_quit=self.quit_app,
        )

        # Sound
        self.sound = QSoundEffect()
        sound_path = ASSETS_DIR / "notification.wav"
        if sound_path.exists():
            self.sound.setSource(QUrl.fromLocalFile(str(sound_path)))
            self.sound.setVolume(0.5)

        # State
        self.state = PetState.HIDDEN
        self.x = 0
        self.y = 0
        self.target_x = 0

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self._move_step)

        # Apply launch-at-login on start
        self._sync_launch_at_login()
        self._update_tray_stats()

    # ── main loop ───────────────────────────────────────────────

    def run(self) -> None:
        logger.info("Starting Water Buddy application...")
        self.ui.hide_window()
        self.reminders.start()
        sys.exit(self.app.exec())

    # ── reminder handling ───────────────────────────────────────

    def handle_reminder(self) -> None:
        logger.info("Reminder triggered. State: %s", self.state)
        if self.state == PetState.HIDDEN:
            self.start_walk_in()

    def start_walk_in(self) -> None:
        self.state = PetState.WALKING_IN
        screen_w = self.ui.screen_width()
        screen_h = self.ui.screen_height()

        self.x = screen_w + 20
        self.y = screen_h - self.ui.window_height() - 70
        self.target_x = screen_w - self.ui.window_width() - 50

        self.ui.set_position(self.x, self.y)
        self.ui.hide_bubble()
        self.ui.show_window()
        self.animations.play_walk_in()

        # Play sound
        if self.settings.sound_enabled:
            self.sound.play()

        self.move_timer.start(self.MOVE_DELAY_MS)

    def _move_step(self) -> None:
        if self.state == PetState.WALKING_IN:
            if self.x > self.target_x:
                self.x -= self.MOVE_STEP_PX
                self.ui.set_position(self.x, self.y)
            else:
                self.move_timer.stop()
                self.state = PetState.ASKING
                self.animations.play_asking()
                self.ui.show_question(self.settings.user_name)

        elif self.state == PetState.WALKING_OUT:
            screen_w = self.ui.screen_width()
            if self.x < screen_w + 20:
                self.x += self.MOVE_STEP_PX
                self.ui.set_position(self.x, self.y)
            else:
                self.move_timer.stop()
                self.ui.hide_window()
                self.state = PetState.HIDDEN

    # ── button handlers ─────────────────────────────────────────

    def handle_yes(self) -> None:
        if self.state != PetState.ASKING:
            return
        self.state = PetState.REJOICING
        self.stats.record_drink()
        self._update_tray_stats()
        self.ui.show_good_job()
        self.animations.play_happy()
        self.reminders.start()
        QTimer.singleShot(2500, self.start_walk_out)

    def handle_snooze(self) -> None:
        if self.state != PetState.ASKING:
            return
        self.state = PetState.SAD
        snooze_min = self.settings.get("snooze_duration_min")
        self.ui.set_message(f"😤 Fine... I'll come back in {snooze_min} min!")
        self.ui.hide_buttons()
        self.ui.show_bubble()
        self.animations.play_sad()
        self.reminders.start_snooze()
        QTimer.singleShot(2000, self.start_walk_out)

    def start_walk_out(self) -> None:
        self.state = PetState.WALKING_OUT
        self.ui.hide_bubble()
        self.animations.play_walk_out()
        self.move_timer.start(self.MOVE_DELAY_MS)

    # ── tray actions ────────────────────────────────────────────

    def toggle_pause(self) -> None:
        if self.reminders.is_paused:
            self.reminders.resume()
            self.tray.set_paused(False)
        else:
            self.reminders.pause()
            self.tray.set_paused(True)

    def drink_now(self) -> None:
        self.stats.record_drink()
        self._update_tray_stats()
        logger.info("Drink recorded via tray. Today: %d", self.stats.today_count())

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self.stats)
        if dialog.exec():
            # Settings saved, apply changes
            logger.info("Settings updated. Restarting timer with new interval.")
            if not self.reminders.is_paused:
                self.reminders.start()
            self._sync_launch_at_login()
            self._update_tray_stats()

    def open_stats(self) -> None:
        """Open settings dialog on the Stats tab."""
        dialog = SettingsDialog(self.settings, self.stats)
        # Switch to stats tab (index 1)
        tabs = dialog.findChild(type(dialog.findChildren(type(dialog))[0].__class__) 
                                if dialog.findChildren(type(dialog)) else None)
        dialog.exec()
        self._update_tray_stats()

    def quit_app(self) -> None:
        logger.info("Quitting Water Buddy.")
        self.reminders.stop()
        self.app.quit()

    # ── helpers ─────────────────────────────────────────────────

    def _update_tray_stats(self) -> None:
        self.tray.update_stats_text(self.stats.today_count(), self.stats.daily_goal)

    def _sync_launch_at_login(self) -> None:
        """Create or remove a macOS LaunchAgent plist for auto-start."""
        plist_dir = Path.home() / "Library" / "LaunchAgents"
        plist_path = plist_dir / f"{PLIST_LABEL}.plist"
        python_path = Path(sys.executable).resolve()
        script_path = Path(__file__).resolve()

        if self.settings.get("launch_at_login"):
            plist_dir.mkdir(parents=True, exist_ok=True)
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
            plist_path.write_text(plist_content)
            logger.info("Launch agent created: %s", plist_path)
        else:
            if plist_path.exists():
                plist_path.unlink()
                logger.info("Launch agent removed.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when windows close
    controller = AppController(app)
    controller.run()