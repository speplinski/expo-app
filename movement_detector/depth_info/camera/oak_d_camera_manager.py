import logging
from typing import List

from config.modules_configs.depth_config import DepthConfig
from movement_detector.depth_info.camera.oak_camera_socket import OakCameraSocket


class OakCameraManager:
    def __init__(self, config: DepthConfig):
        self.config = config
        self.logger = logging.getLogger()
        self.cameras = {}
        self.header_length = config.header_length

        self.logger.info(f"Initializing OakCameraManager with {len(config.cameras)} cameras")

        for camera_id, camera_config in config.cameras.items():
            self.logger.info(f"Initializing camera {camera_id} at {camera_config.ip_address}")
            try:
                camera = OakCameraSocket(
                    ip_address=camera_config.ip_address,
                    port=camera_config.port,
                    timeout=camera_config.timeout
                )
                self.cameras[camera_id] = camera
            except Exception as e:
                self.logger.error(f"Failed to initialize camera {camera_id}: {e}")

    def get_distances(self) -> List[float]:
        all_distances = []
        for camera in self.cameras.values():
            try:
                distances = camera.get_distances(self.header_length)
                all_distances.extend(distances)
            except Exception as e:
                self.logger.error(f"Error getting distances: {e}")

        return all_distances

    def close(self):
        for camera in self.cameras.values():
            try:
                camera.close()
            except Exception as e:
                self.logger.error(f"Error closing camera: {e}")