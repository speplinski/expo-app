import depthai as dai

from app.tracking.depth_info.build_oak_d_pipeline import build_oak_d_pipeline
from app.tracking.depth_info.oak_d_simulation import OakDSimulation


class DepthDataSensor:
    def __init__(self, config):
        self.run_in_dummy_mode = config.RUN_CAMERAS_IN_DUMMY_MODE

        if self.run_in_dummy_mode:
            self.simulation = OakDSimulation(config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT, config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT)
        else:
            pipeline = build_oak_d_pipeline(
                config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT, config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT,
                config.LOWER_DEPTH_THRESHOLD, config.UPPER_DEPTH_THRESHOLD
            )

            # ToDo: check if works after moving queues out of the with scope
            with dai.Device(pipeline) as device:
                device.setIrLaserDotProjectorIntensity(0.5)

                self.spatial_calc_queue = device.getOutputQueue(name="spatialData", maxSize=4, blocking=False)


    def get_distances(self):
        if self.run_in_dummy_mode:
            return self.simulation.get_distances()
        else:
            return [
                depth_data.spatialCoordinates.z / 1000
                for depth_data
                in self.spatial_calc_queue.get().getSpatialLocations()
            ]
