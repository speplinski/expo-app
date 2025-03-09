from dataclasses import dataclass
from typing import Tuple


@dataclass
class DisplayConfig:
    monitor_index: int = 1
    resolution: Tuple[int, int] = (1920, 1080)
    model_resolution: Tuple[int, int] = (1920, 640)

    full_screen_mode: bool = True

    clear_frames_queue_when_overflow: bool = True

    @property
    def vertical_resolution_offset(self) -> int:
        return (self.resolution[1] - self.model_resolution[1]) >> 1
