from pathlib import Path
from typing import Sequence
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

class AnimationManager:
    FRAME_DELAY_MS = 120

    def __init__(self, image_label: QLabel, assets_dir: Path) -> None:
        self.image_label = image_label
        self.assets_dir = assets_dir

        self.timer = QTimer()
        self.timer.timeout.connect(self._play_loop)
        
        self._current_frames: list[QPixmap] = []
        self._frame_index = 0

        self.idle = self._load_image("idle.png")
        self.asking = self._load_image("idle.png")      # Use idle for asking pose
        self.happy = self._load_image("happy.png")
        self.sad = self._load_image("angry.png")         # Use angry for sad pose

        self.walk_in = self._load_frames(["walk_in1.png", "walk_in2.png", "walk_in3.png", "walk_in4.png"])
        self.walk_out = self._load_frames(["walk_out1.png", "walk_out2.png", "walk_out3.png", "walk_out4.png"])

    def _load_image(self, filename: str) -> QPixmap:
        path = self.assets_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing asset: {path}")
        pixmap = QPixmap(str(path))
        # Smooth scale to 220x220 using PyQt6 transform mode 1
        return pixmap.scaled(220, 220, transformMode=Qt.TransformationMode.SmoothTransformation)

    def _load_frames(self, filenames: Sequence[str]) -> list[QPixmap]:
        return [self._load_image(filename) for filename in filenames]

    def _set_image(self, image: QPixmap) -> None:
        self.image_label.setPixmap(image)

    def _play_loop(self) -> None:
        if not self._current_frames:
            return
        self._set_image(self._current_frames[self._frame_index])
        self._frame_index = (self._frame_index + 1) % len(self._current_frames)

    def _start_loop(self, frames: list[QPixmap]) -> None:
        self.stop()
        self._current_frames = frames
        self._frame_index = 0
        self._play_loop()
        self.timer.start(self.FRAME_DELAY_MS)

    def stop(self) -> None:
        self.timer.stop()

    def play_idle(self) -> None:
        self.stop()
        self._set_image(self.idle)

    def play_asking(self) -> None:
        self.stop()
        self._set_image(self.asking)

    def play_happy(self) -> None:
        self.stop()
        self._set_image(self.happy)

    def play_sad(self) -> None:
        self.stop()
        self._set_image(self.sad)

    def play_walk_in(self) -> None:
        self._start_loop(self.walk_in)

    def play_walk_out(self) -> None:
        self._start_loop(self.walk_out)