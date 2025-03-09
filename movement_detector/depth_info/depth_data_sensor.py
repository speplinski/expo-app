import logging
import threading
import time

import depthai as dai

from config.modules_configs.depth_config import DepthConfig
from movement_detector.depth_info.build_oak_d_pipeline import build_oak_d_pipeline
from movement_detector.depth_info.simulation.oak_d_simulation import OakDSimulation


class DepthDataSensor:
    def __init__(self, config: DepthConfig):
        self.run_in_simulation_mode = config.run_cameras_in_simulation_mode

        logger = logging.getLogger()

        logger.info(f"Sensor running on thread: {threading.current_thread().name}")

        if self.run_in_simulation_mode:
            self.simulation = OakDSimulation(config.depth_grid_segments_count.horizontal, config.depth_grid_segments_count.vertical)
            self.last_update = time.time()

            logger.info("Using simulation mode")
        else:
            logger.info("Initializing OAK-D camera...")

            pipeline = build_oak_d_pipeline(
                config.depth_grid_segments_count.horizontal, config.depth_grid_segments_count.vertical,
                config.depth_threshold.lower, config.depth_threshold.upper
            )

            logger.info("Pipeline created successfully")

            self.device = dai.Device(pipeline)
            self.device.setIrLaserDotProjectorIntensity(0.5)
            self.depth_queue = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)
            self.spatial_calc_queue = self.device.getOutputQueue(name="spatialData", maxSize=4, blocking=False)

            logger.info("Device initialized successfully")


    def get_distances(self) -> list[float]:
        if self.run_in_simulation_mode:
            current_time = time.time()
            time_delta = current_time - self.last_update
            self.last_update = current_time

            self.simulation.make_step(time_delta)
            return self.simulation.get_distances()
        else:
            return [
                depth_data.spatialCoordinates.z / 1000
                for depth_data
                in self.spatial_calc_queue.get().getSpatialLocations()
            ]

    def close(self):
        if not self.run_in_simulation_mode:
            self.device.close()