"""Water Buddy — Desktop Pet Water Reminder (PyQt6).

Cross-platform: macOS and Windows.
"""
from __future__ import annotations

import sys
import logging
from enum import Enum, auto
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from ui import DesktopPetUI
from animations import AnimationManager
from reminder import ReminderManager
from settings import SettingsManager
from stats import StatsManager
from tray import SystemTrayApp
from settings_window import SettingsDialog
from onboarding import OnboardingWizard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("WaterBuddy")

ASSETS_DIR  = Path(__file__).resolve().parent / "assets"
PLIST_LABEL = "com.waterbuddy.app"
IS_MAC      = sys.platform == "darwin"
IS_WIN      = sys.platform == "win32"


# ── Platform helpers ────────────────────────────────────────────────

def _hide_from_dock() -> None:
    """Remove Water Buddy from the macOS Dock (no-op on Windows)."""
    if not IS_MAC:
        return
    try:
        from AppKit import NSApplication  # type: ignore[import]
        # NSApplicationActivationPolicyAccessory = 1
        NSApplication.sharedApplication().setActivationPolicy_(1)
        logger.info("App hidden from Dock via AppKit.")
    except Exception as exc:
        # Falls back gracefully — LSUIElement in .app bundle covers this
        logger.debug("Could not set Dock policy via AppKit: %s", exc)


def _set_launch_at_login_mac(enabled: bool) -> None:
    """Write or remove a LaunchAgent plist on macOS."""
    plist_dir  = Path.home() / "Library" / "LaunchAgents"
    plist_path = plist_dir / f"{PLIST_LABEL}.plist"
    python_exe = Path(sys.executable).resolve()
    script     = Path(__file__).resolve()

    if enabled:
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
        <string>{python_exe}</string>
        <string>{script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
        plist_path.write_text(plist_content)
        logger.info("macOS launch agent created: %s", plist_path)
    else:
        if plist_path.exists():
            plist_path.unlink()
            logger.info("macOS launch agent removed.")


def _set_launch_at_login_win(enabled: bool) -> None:
    """Write or remove a Windows Registry run key for auto-start."""
    try:
        import winreg  # type: ignore[import]  # Windows-only stdlib module
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "WaterBuddy"
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
        ) as key:
            if enabled:
                # Point to the executable / Python script
                exe = Path(sys.executable).resolve()
                script = Path(__file__).resolve()
                value  = f'"{exe}" "{script}"'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, value)
                logger.info("Windows run-key set: %s", value)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                    logger.info("Windows run-key removed.")
                except FileNotFoundError:
                    pass  # Already absent — that's fine
    except Exception as exc:
        logger.error("Could not set Windows launch-at-login: %s", exc)


def _sync_launch_at_login(settings: SettingsManager) -> None:
    enabled = bool(settings.get("launch_at_login"))
    if IS_MAC:
        _set_launch_at_login_mac(enabled)
    elif IS_WIN:
        _set_launch_at_login_win(enabled)
    else:
        logger.debug("Launch-at-login not supported on this platform.")


# ── State machine ───────────────────────────────────────────────────

class PetState(Enum):
    HIDDEN      = auto()
    WALKING_IN  = auto()
    ASKING      = auto()
    REJOICING   = auto()
    SAD         = auto()
    WALKING_OUT = auto()


class AppController:
    MOVE_STEP_PX = 8
    MOVE_DELAY_MS = 16

    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.settings = SettingsManager()
        self.stats     = StatsManager()

        # UI
        self.ui = DesktopPetUI()
        self.ui.set_on_hidden_externally(self._on_window_hidden_externally)
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

        # Dialog references (kept alive to prevent GC)
        self._settings_dialog = None
        self._stats_dialog = None

        # Sound
        self.sound_path = ASSETS_DIR / "notification.wav"
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        if self.sound_path.exists():
            self.player.setSource(QUrl.fromLocalFile(str(self.sound_path)))

        # State
        self.state    = PetState.HIDDEN
        self.x        = 0
        self.y        = 0
        self.target_x = 0

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self._move_step)

        # Tray reminder countdown (updates every 500ms)
        self._tray_timer = QTimer()
        self._tray_timer.timeout.connect(self._update_tray_reminder)
        self._tray_timer.start(500)

        # Sleep/wake handling
        self._was_asleep = False
        app.applicationStateChanged.connect(self._on_app_state_changed)

    # ── Main loop ───────────────────────────────────────────────────

    def run(self) -> None:
        logger.info("Starting Water Buddy (%s)…", sys.platform)
        self.ui.hide_window()

        if self.settings.get("first_run"):
            QTimer.singleShot(300, self._show_onboarding)
        else:
            self._start_normal()

        sys.exit(self.app.exec())

    def _show_onboarding(self) -> None:
        wizard = OnboardingWizard(
            settings=self.settings,
            on_complete=self._start_normal,
        )
        wizard.exec()

    def _start_normal(self) -> None:
        _sync_launch_at_login(self.settings)
        self._update_tray_stats()
        self.reminders.start()

    # ── Reminder handling ───────────────────────────────────────────

    def handle_reminder(self) -> None:
        logger.info("Reminder triggered. State: %s", self.state)
        if self.state == PetState.HIDDEN:
            self.start_walk_in()

    def start_walk_in(self) -> None:
        self.state    = PetState.WALKING_IN
        screen_w      = self.ui.screen_width()
        screen_h      = self.ui.screen_height()

        self.x        = screen_w + 20
        self.y        = screen_h - self.ui.window_height() - 70
        self.target_x = screen_w - self.ui.window_width() - 50

        self.ui.set_position(self.x, self.y)
        self.ui.hide_bubble()
        self.ui.show_window()
        self.animations.play_walk_in()

        if self.settings.sound_enabled:
            self._sync_sound_to_system_volume()
            self.player.play()

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

    # ── Button handlers ─────────────────────────────────────────────

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

    # ── Tray actions ────────────────────────────────────────────────

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
        if self._settings_dialog is not None:
            self._settings_dialog.raise_()
            self._settings_dialog.activateWindow()
            return
        dlg = SettingsDialog(self.settings, self.stats, start_tab=0)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dlg.accepted.connect(self._on_settings_saved)
        dlg.finished.connect(lambda _: self._clear_dialog("_settings_dialog"))
        self._settings_dialog = dlg
        dlg.show()

    def _on_settings_saved(self) -> None:
        logger.info("Settings saved. Restarting timer.")
        if not self.reminders.is_paused:
            self.reminders.start()
        _sync_launch_at_login(self.settings)
        self._update_tray_stats()

    def open_stats(self) -> None:
        if self._stats_dialog is not None:
            self._stats_dialog.raise_()
            self._stats_dialog.activateWindow()
            return
        dlg = SettingsDialog(self.settings, self.stats, start_tab=1)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dlg.finished.connect(lambda _: self._clear_dialog("_stats_dialog"))
        self._stats_dialog = dlg
        dlg.show()

    def _clear_dialog(self, attr: str) -> None:
        setattr(self, attr, None)

    def quit_app(self) -> None:
        logger.info("Quitting Water Buddy.")
        self.reminders.stop()
        self.app.quit()

    def _on_app_state_changed(self, state: Qt.ApplicationState) -> None:
        if state == Qt.ApplicationState.ApplicationSuspended:
            self._was_asleep = True
            if self.state != PetState.HIDDEN:
                self.ui.hide_window()
                self.move_timer.stop()
                self.state = PetState.HIDDEN
            self.reminders.stop()
            logger.info("System sleep detected — reminders paused.")
        elif state == Qt.ApplicationState.ApplicationActive and self._was_asleep:
            self._was_asleep = False
            if not self.reminders.is_paused:
                self.reminders.start()
            logger.info("System wake detected — reminders restarted.")

    def _update_tray_reminder(self) -> None:
        if self.state != PetState.HIDDEN:
            self.tray.update_reminder_time("💧  Buddy is here!")
        elif self.reminders.is_paused:
            self.tray.update_reminder_time("⏸️  Paused")
        elif self.reminders.quiet_hours_active:
            self.tray.update_reminder_time("🌙  Quiet hours")
        else:
            self.tray.update_reminder_time(f"⏱️  Next — {self.reminders.remaining_str}")

    def _on_window_hidden_externally(self) -> None:
        """Called when the OS hides our window without us asking (e.g. macOS
        window manager hiding a Tool window on app deactivation).

        Resets the state machine so the next reminder can bring the pet back.
        """
        logger.warning("Window hidden externally — resetting state to HIDDEN")
        self.move_timer.stop()
        self.state = PetState.HIDDEN

    def _sync_sound_to_system_volume(self) -> None:
        """Set sound to 50% of the current macOS system output volume."""
        if not IS_MAC:
            self.audio_output.setVolume(0.5)
            return

        try:
            import subprocess
            result = subprocess.run(
                ["osascript", "-e", "output volume of (get volume settings)"],
                capture_output=True, text=True, timeout=2,
            )
            raw = result.stdout.strip()
            sys_vol = int(raw)
            vol = max(0.0, min(1.0, sys_vol / 200.0))
            self.audio_output.setVolume(vol)
            logger.debug("System vol=%d → sound vol=%.2f", sys_vol, vol)
        except Exception as exc:
            logger.warning("Could not read system volume: %s", exc)
            self.audio_output.setVolume(0.5)

    # ── Helpers ─────────────────────────────────────────────────────

    def _update_tray_stats(self) -> None:
        self.tray.update_stats_text(self.stats.today_count(), self.stats.daily_goal)


# ── Entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Hide from macOS Dock — graceful no-op on Windows
    _hide_from_dock()

    controller = AppController(app)
    controller.run()