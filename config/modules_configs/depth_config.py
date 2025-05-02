from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DepthGridSegmentsCount:
    horizontal: int = 22
    vertical: int = 14


@dataclass
class DistanceThresholdInM:
    min: float = 0.7
    max: float = 2.8


@dataclass
class OakCameraConfig:
    ip_address: str
    port: int = 65432
    timeout: float = 5.0
    threshold: DistanceThresholdInM = None

    def __post_init__(self):
        if self.threshold is None:
            self.threshold = DistanceThresholdInM()


@dataclass
class DepthConfig:
    run_cameras_in_simulation_mode: bool = True

    mirror_mode: bool = True

    header_length: int = 32
    cameras: Dict[str, OakCameraConfig] = None
    depth_grid_segments_count: DepthGridSegmentsCount = field(default_factory=DepthGridSegmentsCount)
    depth_grid_display_segments_count: DepthGridSegmentsCount = field(
        default_factory=lambda: DepthGridSegmentsCount(horizontal=9, vertical=5)
    )
    horizontal_segment_count_per_camera: int = 3

    def __post_init__(self):
        if self.cameras is None:
            self.cameras = {
                "camera1": OakCameraConfig(
                    ip_address="192.168.70.64",
                    threshold=DistanceThresholdInM()
                ),
                "camera2": OakCameraConfig(
                    ip_address="192.168.70.62",
                    threshold=DistanceThresholdInM()
                ),
                "camera3": OakCameraConfig(
                    ip_address="192.168.70.65",
                    threshold=DistanceThresholdInM()
                )
            }

        self.counters_count = self.horizontal_segment_count_per_camera * len(self.cameras)