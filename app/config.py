class PositionTrackingConfig:
    def __init__(self):
        self.RUN_CAMERAS_IN_DUMMY_MODE = True

        self.LOWER_DEPTH_THRESHOLD = 200
        self.UPPER_DEPTH_THRESHOLD = 10000
        self.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT = 10
        self.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT = 6

        self.MIN_DISTANCE_THRESHOLD_IN_M = 0.4
        self.MAX_DISTANCE_THRESHOLD_IN_M = 1.8

        self.DISPLAY_CV_2_WINDOW = False
        self.SHOW_STATS = True
        self.MIRROR_MODE = True

        self.UI_REFRESH_INTERVAL_IN_S = 0.04
        self.COUNTER_INCREMENT_INTERVAL_IN_S = 0.5
