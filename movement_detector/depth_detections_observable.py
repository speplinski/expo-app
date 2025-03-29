import logging

import reactivex as rx
from reactivex.disposable import Disposable

from config.integrated_config import IntegratedConfig
from movement_detector.depth_info.depth_data_sensor import DepthDataSensor


def build_depth_detections_stream(config: IntegratedConfig):
    logger = logging.getLogger()

    def subscribe(observer, scheduler):
        depth_data_sensor: DepthDataSensor | None = None

        def initialize_sensor():
            nonlocal depth_data_sensor
            try:
                depth_data_sensor = DepthDataSensor(config=config.depth)
            except RuntimeError as e:
                logger.error('Failed to initialize depth data sensor: {}'.format(e))
                observer.on_error(e)

        def action(state):
            if depth_data_sensor is None:
                if not initialize_sensor():
                    return state

            observer.on_next(depth_data_sensor.get_distances())

        disposable = scheduler.schedule_periodic(
            period=config.timing.depth_data_refresh_interval,
            action=action
        )

        def dispose():
            nonlocal depth_data_sensor

            disposable.dispose()

            if depth_data_sensor is not None:
                depth_data_sensor.close()
                depth_data_sensor = None

            logger.info("Depth data sensor closed")

        return Disposable(dispose)

    return rx.create(subscribe)
