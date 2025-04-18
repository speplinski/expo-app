import logging
import threading
import time

from config.modules_configs.depth_config import DepthConfig
from movement_detector.depth_info.camera.oak_d_camera_manager import OakCameraManager
from movement_detector.depth_info.simulation.oak_d_simulation import OakDSimulation
from movement_detector.depth_info.camera.oak_socket_adapter import OakSocketAdapter


class DepthDataSensor:
    def __init__(self, config: DepthConfig):
        self.config = config
        self.run_in_simulation_mode = config.run_cameras_in_simulation_mode
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Sensor running on thread: {threading.current_thread().name}")

        if self.run_in_simulation_mode:
            self.logger.info("Using simulation mode")
            self.simulation = OakDSimulation(
                config.depth_grid_segments_count.horizontal,
                config.depth_grid_segments_count.vertical,
                len(config.cameras)
            )
            self.last_update = time.time()
        else:
            try:
                self.logger.info("Initializing OAK-D cameras via socket connections...")
                self.socket_adapter = OakSocketAdapter(config)
                self.logger.info("Socket adapter initialized successfully")
                self.camera_manager = None
            except Exception as e:
                self.logger.error(f"Failed to initialize socket adapter: {e}")
                self.logger.info("Falling back to camera manager...")
                try:
                    self.camera_manager = OakCameraManager(config)
                    self.socket_adapter = None
                    self.logger.info("Camera manager initialized successfully")
                except Exception as e2:
                    self.logger.error(f"Failed to initialize camera manager: {e2}")
                    # Fall back to simulation mode
                    self.run_in_simulation_mode = True
                    self.simulation = OakDSimulation(
                        config.depth_grid_segments_count.horizontal,
                        config.depth_grid_segments_count.vertical,
                        len(config.cameras)
                    )
                    self.last_update = time.time()
                    self.logger.info("Falling back to simulation mode after connection failures")

    def get_distances(self):
        try:
            if self.run_in_simulation_mode:
                current_time = time.time()
                time_delta = current_time - self.last_update
                self.last_update = current_time
                self.simulation.make_step(time_delta)
                return self.simulation.get_distances()
            elif hasattr(self, 'socket_adapter') and self.socket_adapter:
                return self.socket_adapter.get_distances()
            elif hasattr(self, 'camera_manager') and self.camera_manager:
                return self.camera_manager.get_distances()
            else:
                self.logger.error("No camera source available")
                return [np.zeros(self.config.depth_grid_segments_count.horizontal * 
                               self.config.depth_grid_segments_count.vertical) 
                        for _ in range(len(self.config.cameras))]
        except Exception as e:
            self.logger.error(f"Error getting distances: {e}")
            # Return empty arrays as fallback
            return [np.zeros(self.config.depth_grid_segments_count.horizontal * 
                           self.config.depth_grid_segments_count.vertical) 
                    for _ in range(len(self.config.cameras))]

    def close(self):
        if hasattr(self, 'socket_adapter') and self.socket_adapter:
            self.socket_adapter.close()
        
        if hasattr(self, 'camera_manager') and self.camera_manager and not self.run_in_simulation_mode:
            self.camera_manager.close()
