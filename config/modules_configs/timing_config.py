from dataclasses import dataclass


@dataclass
class TimingConfig:
    depth_data_refresh_interval: float = 0.2
    counters_sampling_interval: float = 1.0
    sequence_switch_epoch: float = 45
    new_detection_epoch_threshold = 0
    continued_detection_epoch_threshold = 1
    max_counter_value = 30
    target_interpolation_frames = 60
