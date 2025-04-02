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

        if isinstance(cam_dist, (int, float)):
            cam_dist = np.full((config.depth_grid_segments_count.vertical * config.depth_grid_segments_count.horizontal), cam_dist)

        if len(cam_dist) == 0:
            cam_dist = np.zeros(config.depth_grid_segments_count.vertical * config.depth_grid_segments_count.horizontal)

        try:
            reshaped_distances = cam_dist.reshape(
                config.depth_grid_segments_count.vertical,
                config.depth_grid_segments_count.horizontal
            )
        except Exception as e:
            logger.error(f"Failed to reshape distances for camera {i}: {e}")
            logger.error(f"Shape: {cam_dist.shape}, Expected: ({config.depth_grid_segments_count.vertical}, {config.depth_grid_segments_count.horizontal})")
            reshaped_distances = np.zeros((config.depth_grid_segments_count.vertical, config.depth_grid_segments_count.horizontal))

        within_threshold = (reshaped_distances >= min_threshold) & (reshaped_distances <= max_threshold)

        segments = np.array_split(
            np.arange(config.depth_grid_segments_count.horizontal),
            config.horizontal_segment_count_per_camera
        )

        for j, segment_indices in enumerate(segments):
            result_idx = i * config.horizontal_segment_count_per_camera + j
            result[result_idx] = int(np.any(within_threshold[:, segment_indices]))

    return result