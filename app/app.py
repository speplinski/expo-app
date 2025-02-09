from app.config import PositionTrackingConfig
from app.tracking.depth_application import DepthApplication


class App:
    def __init__(self):
        self.depth_app = DepthApplication(PositionTrackingConfig())

    def run(self):
        print('Starting depth application')
        self.depth_app.run()