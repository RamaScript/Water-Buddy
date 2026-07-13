"""Desktop pet UI built entirely with PyQt6."""
from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt


class DesktopPetUI(QWidget):
    WINDOW_WIDTH = 360
    WINDOW_HEIGHT = 360

    BUBBLE_BG = "#fff7df"
    BUBBLE_BORDER = "#3b2f2f"
    TEXT_COLOR = "#2d2525"

    def __init__(self):
        super().__init__()
        self.on_yes: Callable[[], None] | None = None
        self.on_snooze: Callable[[], None] | None = None
        self._configure_window()
        self._build_layout()

    def _configure_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def _build_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Bubble Frame
        self.bubble_frame = QFrame()
        self.bubble_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BUBBLE_BG};
                border: 3px solid {self.BUBBLE_BORDER};
                border-radius: 10px;
            }}
        """)
        bubble_layout = QVBoxLayout(self.bubble_frame)

        self.message_label = QLabel("")
        self.message_label.setStyleSheet(f"""
            color: {self.TEXT_COLOR};
            border: none;
            font-family: 'Menlo', 'SF Mono', monospace;
            font-size: 13px;
            font-weight: bold;
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bubble_layout.addWidget(self.message_label)

        self.button_frame = QFrame()
        self.button_frame.setStyleSheet("border: none; background: transparent;")
        btn_layout = QHBoxLayout(self.button_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.yes_button = QPushButton("Yes ✅")
        self.yes_button.setFixedSize(88, 30)
        self.yes_button.setStyleSheet("""
            QPushButton {
                background-color: #6bd17b;
                color: #1d2a1f;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #58bd67; }
        """)
        self.yes_button.clicked.connect(self._handle_yes)
        btn_layout.addWidget(self.yes_button)

        self.snooze_button = QPushButton("Snooze 😴")
        self.snooze_button.setFixedSize(120, 30)
        self.snooze_button.setStyleSheet("""
            QPushButton {
                background-color: #8fd3ff;
                color: #182936;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #72bdea; }
        """)
        self.snooze_button.clicked.connect(self._handle_snooze)
        btn_layout.addWidget(self.snooze_button)

        bubble_layout.addWidget(self.button_frame)

        self.main_layout.addWidget(
            self.bubble_frame,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        )

        # Image Label
        self.image_label = QLabel()
        self.image_label.setFixedSize(220, 220)
        self.image_label.setStyleSheet("background: transparent; border: none;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(
            self.image_label,
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        )

        self.hide_bubble()

    # ── handlers ────────────────────────────────────────────────

    def _handle_yes(self):
        if self.on_yes:
            self.on_yes()

    def _handle_snooze(self):
        if self.on_snooze:
            self.on_snooze()

    def set_button_handlers(self, on_yes, on_snooze):
        self.on_yes = on_yes
        self.on_snooze = on_snooze

    # ── window control ──────────────────────────────────────────

    def show_window(self):
        self.show()
        self.raise_()

    def hide_window(self):
        self.hide()

    def set_position(self, x, y):
        self.move(x, y)

    def screen_width(self) -> int:
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        return screen.geometry().width() if screen else 1920

    def screen_height(self) -> int:
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        return screen.geometry().height() if screen else 1080

    def window_width(self) -> int:
        return self.WINDOW_WIDTH

    def window_height(self) -> int:
        return self.WINDOW_HEIGHT

    # ── bubble helpers ──────────────────────────────────────────

    def set_message(self, message: str):
        self.message_label.setText(message)

    def show_buttons(self):
        self.button_frame.show()

    def hide_buttons(self):
        self.button_frame.hide()

    def show_bubble(self):
        self.bubble_frame.show()

    def hide_bubble(self):
        self.bubble_frame.hide()

    def show_question(self, name: str = "Buddy"):
        self.set_message(f"💧 Hey {name}! Did you drink water?")
        self.show_buttons()
        self.show_bubble()

    def show_good_job(self):
        self.set_message("✨ Good job! Keep it up!")
        self.hide_buttons()
        self.show_bubble()

    def show_come_back(self):
        self.set_message("😤 Fine... I'll come back!")
        self.hide_buttons()
        self.show_bubble()