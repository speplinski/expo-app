import numpy as np
import reactivex as rx
from reactivex import operators as ops

from config.integrated_config import IntegratedConfig
from movement_detector.depth_detections_observable import build_depth_detections_stream


def build_detection_counters_stream(config: IntegratedConfig):
    return build_depth_detections_stream(config).pipe(
        ops.map(lambda distances: np.array(distances).reshape(
            config.depth.depth_grid_segments_count.vertical,
            config.depth.depth_grid_segments_count.horizontal
        )),
        ops.map(lambda distances: np.fliplr(distances) if config.depth.mirror_mode else distances),
        ops.map(lambda distances: {
            'distances': distances,
            'columns': np.any(
                (distances >= config.depth.distance_threshold_in_m.min) &
                (distances <= config.depth.distance_threshold_in_m.max),
                axis=0
            ).astype(int)
        }),
        ops.publish()
    )

def build_detection_counters_updates_stream(detections_stream, config: IntegratedConfig):
    sampling_interval = config.timing.counters_sampling_interval
    detection_threshold = config.timing.new_detection_epoch_threshold
    detection_threshold_diff = detection_threshold - config.timing.continued_detection_epoch_threshold
    counters_count = config.depth.depth_grid_segments_count.horizontal

    return detections_stream.pipe(
        ops.map(lambda detections: detections['columns']),
        ops.start_with(np.zeros(counters_count)),
        ops.publish(lambda published: rx.merge(
            published.pipe(ops.take(2)),
            published.pipe(ops.skip(2), ops.sample(sampling_interval))
        )),
        ops.pairwise(),
        ops.scan(
            lambda acc, pair: {
                'current_detections': pair[1],
                'epoch_triggers_diffs': pair[1] * (pair[1] * detection_threshold - pair[0] * detection_threshold_diff),
                'epoch': acc['epoch'] + 1
            },
            {
                'current_detections': np.zeros(counters_count),
                'epoch_triggers_diffs': np.zeros(counters_count),
                'epoch': 0
            }
        ),
        ops.scan(
            lambda acc, state: {
                'counters_updates': (state['current_detections'] * acc['epoch_triggers'] == state['epoch']).astype(int),
                'epoch_triggers': np.where(
                    state['current_detections'] * acc['epoch_triggers'] > state['epoch'],
                    state['current_detections'] * acc['epoch_triggers'],
                    state['current_detections'] * state['epoch'] + state['epoch_triggers_diffs']
                ),
                'epoch': state['epoch']
            },
            {
                'counters_updates': np.zeros(counters_count),
                'epoch_triggers': np.zeros(counters_count),
                'epoch': 0
            }
        )
    )

