from dataclasses import dataclass, field


@dataclass
class DepthThreshold:
    lower: int = 200
    upper: int = 10000


@dataclass
class DepthGridSegmentsCount:
    horizontal: int = 9
    vertical: int = 5

@dataclass
class DistanceThresholdInM:
    min: float = 0.4
    max: float = 1.8

@dataclass
class DepthConfig:
    run_cameras_in_simulation_mode: bool = True

    depth_threshold: DepthThreshold = field(default_factory=DepthThreshold)

    depth_grid_segments_count: DepthGridSegmentsCount = field(default_factory=DepthGridSegmentsCount)

    distance_threshold_in_m: DistanceThresholdInM = field(default_factory=DistanceThresholdInM)

    mirror_mode: bool = True
