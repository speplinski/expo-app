from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt

class SequenceLayer:
    def __init__(self, gray_shade: int, target_size: (int, int), dynamic_files_path: str = None, static_file_path: str = None):
        assert dynamic_files_path is not None or static_file_path is not None, 'either files_path or static_file_path should be defined'

        self._static_mask_image = None
        self._dynamic_mask_images = {}
        self._target_size = target_size

        if static_file_path is not None:
            self._static_mask_image = self._load_image(static_file_path, gray_shade, target_size)

        if dynamic_files_path is not None:
            path = Path(dynamic_files_path)

            columns_directories = [
                d
                for d in path.iterdir()
                if d.is_dir() and not d.name.startswith('.')
            ]

            for column_directory in columns_directories:
                column_index = int(column_directory.stem.split('_')[-1])
                self._dynamic_mask_images[column_index] = []

                frames_files = sorted([
                    file_path
                    for file_path in column_directory.iterdir()
                    if file_path.is_file() and not file_path.name.startswith('.')
                ])

                assert len(frames_files) == 61, f'wrong frames files count in {column_directory}'

                for frame_file in frames_files:
                    frame_mask = self._load_image(frame_file, gray_shade, target_size)
                    self._dynamic_mask_images[column_index].append(frame_mask)

    @staticmethod
    def _load_image(image_path: str, gray_shade: int, target_size: (int, int)) -> npt.NDArray[np.uint8]:
        mask_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, mask_image = cv2.threshold(mask_image, 127, 255, cv2.THRESH_BINARY)
        mask_image[mask_image == 255] = gray_shade
        mask_image = cv2.resize(mask_image, target_size, interpolation=cv2.INTER_NEAREST)
        return mask_image

    def build_layer_image(self, counters: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        if self._static_mask_image is not None:
            return self._static_mask_image

        width, height = self._target_size
        result = np.zeros((height, width), dtype=np.uint8)

        for column_index, frames_images in self._dynamic_mask_images.items():
            result = cv2.bitwise_or(result, frames_images[counters[column_index]])

        return result
