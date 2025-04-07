import numpy as np

from config.modules_configs.depth_config import DepthConfig


def reshape_and_scale_distances_for_display(
        camera_distances: list[np.ndarray],
        config: DepthConfig
) -> np.ndarray:
    reshaped_distances = [
        cam_dist.reshape(config.depth_grid_segments_count.vertical, config.depth_grid_segments_count.horizontal)
        for cam_dist in camera_distances
    ]

    combined_distances = np.concatenate(reshaped_distances, axis=1)

    height, width = combined_distances.shape

    y_indices = np.linspace(0, height, config.depth_grid_display_segments_count.vertical + 1).astype(int)
    x_indices = np.linspace(0, width, config.depth_grid_display_segments_count.horizontal + 1).astype(int)

    sums_y = np.add.reduceat(combined_distances, y_indices[:-1], axis=0)
    sums = np.add.reduceat(sums_y, x_indices[:-1], axis=1)

    mask = combined_distances > 0
    mask_sums_y = np.add.reduceat(mask, y_indices[:-1], axis=0)
    non_zero_counts = np.add.reduceat(mask_sums_y, x_indices[:-1], axis=1)
    non_zero_counts = np.maximum(non_zero_counts, 1)

    result = sums / non_zero_counts

    return result