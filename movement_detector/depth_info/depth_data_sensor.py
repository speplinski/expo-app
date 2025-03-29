import logging
import threading
import time

from config.modules_configs.depth_config import DepthConfig
from movement_detector.depth_info.camera.oak_d_camera_manager import OakCameraManager
from movement_detector.depth_info.simulation.oak_d_simulation import OakDSimulation


class DepthDataSensor:
    def __init__(self, config: DepthConfig):
        self.run_in_simulation_mode = config.run_cameras_in_simulation_mode
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Sensor running on thread: {threading.current_thread().name}")

        if self.run_in_simulation_mode:
            self.simulation = OakDSimulation(
                config.depth_grid_segments_count.horizontal,
                config.depth_grid_segments_count.vertical,
                len(config.cameras)
            )
            self.last_update = time.time()

            self.logger.info("Using simulation mode")
        else:
            self.logger.info("Initializing OAK-D cameras via socket connections...")

            self.camera_manager = OakCameraManager(config)
            self.logger.info("Camera manager initialized successfully")

    def get_distances(self):
        if self.run_in_simulation_mode:
            current_time = time.time()
            time_delta = current_time - self.last_update
            self.last_update = current_time

            self.simulation.make_step(time_delta)
            return self.simulation.get_distances()
        else:
            return self.camera_manager.get_distances()

    def close(self):
        if not self.run_in_simulation_mode:
            self.camera_manager.close()