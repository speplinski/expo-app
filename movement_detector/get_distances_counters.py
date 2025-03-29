import numpy as np

from config.modules_configs.depth_config import DepthConfig


def get_distances_counters(
        camera_distances: list[np.ndarray],
        config: DepthConfig
) -> np.ndarray:
    result = np.zeros(len(camera_distances) * config.horizontal_segment_count_per_camera, dtype=int)

    for i, cam_dist in enumerate(camera_distances):
        camera_key = list(config.cameras.keys())[i]
        min_threshold = config.cameras[camera_key].threshold.min
        max_threshold = config.cameras[camera_key].threshold.max

        reshaped_distances = cam_dist.reshape(
            config.depth_grid_segments_count.vertical,
            config.depth_grid_segments_count.horizontal
        )

        within_threshold = (reshaped_distances >= min_threshold) & (reshaped_distances <= max_threshold)

        segment_width = config.depth_grid_segments_count.horizontal // config.horizontal_segment_count_per_camera

        for j in range(config.horizontal_segment_count_per_camera):
            start_col = j * segment_width
            end_col = min((j + 1) * segment_width, config.depth_grid_segments_count.horizontal)

            result_idx = i * config.horizontal_segment_count_per_camera + j
            result[result_idx] = int(np.any(within_threshold[:, start_col:end_col]))

    return result