from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass
class DisplayConfig:
    monitor_index: int = 1
    
    full_screen_mode: bool = True
    
    clear_frames_queue_when_overflow: bool = True
    
    # Scaling mode for displaying content
    # "fit" - Maintain aspect ratio and fit entire image on screen
    # "fill" - Maintain aspect ratio and fill screen (may crop image)
    # "stretch" - Stretch image to fill screen (may distort)
    # "none" - No scaling, center image
    scaling_mode: str = "none"
    
    background_color: Tuple[int, int, int] = (0, 0, 0)
    
    available_monitors: List[Tuple[int, int, int, int]] = field(
        default_factory=lambda: [(0, 0, 3840, 2160)]
    )