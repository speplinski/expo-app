import time

import cv2
import numpy as np
import numpy.typing as npt

class ImagesInterpolator:
    def __init__(self, target_interpolation_frames: float):
        self.target_interpolation_frames = target_interpolation_frames

        self._last_image_update_time = time.time()

        self._previous_image = None
        self._current_image = None


    def update_image(self, image: npt.NDArray[np.uint8]):
        self._previous_image = self._current_image
        self._current_image = image
        self._last_image_update_time = time.time()

    def get_intermediate_image(self):
        if self._previous_image is None:
            return self._current_image

        elapsed_time = time.time() - self._last_image_update_time

        if elapsed_time > 1:
            return self._current_image

        alpha = self._ease_in_out(elapsed_time)
        return cv2.addWeighted(self._current_image, alpha, self._previous_image, 1 - alpha, 0)

    @staticmethod
    def _ease_in_out(x):
        return 2 * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 2 / 2