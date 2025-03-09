from dataclasses import dataclass
from typing import Tuple


@dataclass
class DisplayConfig:
    monitor_index: int = 1
    resolution: Tuple[int, int] = (960, 360)

    full_screen_mode: bool = False

    clear_frames_queue_when_overflow: bool = True
