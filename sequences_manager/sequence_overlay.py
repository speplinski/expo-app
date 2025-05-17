from math import ceil
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt

class SequenceOverlay:
    def __init__(self, target_size: (int, int), overlay_path = None, max_overlay_height_percent = 0, 
                 min_images_per_column_update = 0, max_images_per_column_update = 0):
        self._target_size = target_size
        self._overlay_images = []
        self._min_images_per_column_update = min_images_per_column_update
        self._max_images_per_column_update = max_images_per_column_update

        self._overlay_image = None
        self.reset_overlay()

        self._previous_counters = None

        if (overlay_path is not None):
            self.load_images(overlay_path, max_overlay_height_percent)
        
    def load_images(self, overlay_path, max_overlay_height_percent):
        path = Path(overlay_path)

        overlay_files = sorted([
            file_path
            for file_path in path.iterdir()
            if file_path.is_file() and not file_path.name.startswith('.')
        ])

        original_images = []
        max_height = 0

        for file_path in overlay_files:
            image = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
            original_images.append(image)

            height = image.shape[0]
            if height > max_height:
                max_height = height

        max_target_height = ceil(self._target_size[1] * max_overlay_height_percent)
        scale_factor = max_target_height / max_height if max_height > 0 else 1.0

        for image in original_images:
            if scale_factor != 1.0:
                new_width = int(image.shape[1] * scale_factor)
                new_height = int(image.shape[0] * scale_factor)
                resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                self._overlay_images.append(resized_image)
            else:
                self._overlay_images.append(image)

    def reset_overlay(self):
        height, width = self._target_size[1], self._target_size[0]
        self._overlay_image = np.zeros((height, width, 4), dtype=np.uint8)
        self._overlay_image[:, :, 3] = 0

    def update_overlay_image(self, counters: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        if self._previous_counters is None:
            self._previous_counters = np.zeros_like(counters)
        
        changed_columns = np.where(counters != self._previous_counters)[0]
        
        if len(changed_columns) == 0 or len(self._overlay_images) == 0:
            self._previous_counters = counters.copy()
            return self._overlay_image
            
        height, width = self._target_size[1], self._target_size[0]
        column_width = width // len(counters)

        for column_idx in changed_columns:
            x_start = column_idx * column_width
            x_end = (column_idx + 1) * column_width if column_idx < len(counters) - 1 else width
            
            min_imgs = min(self._min_images_per_column_update, len(self._overlay_images))
            max_imgs = min(self._max_images_per_column_update, len(self._overlay_images))
            num_images = np.random.randint(min_imgs, max_imgs + 1) if min_imgs < max_imgs else max_imgs
            
            selected_indices = np.random.choice(len(self._overlay_images), num_images, replace=False)
            
            for img_idx in selected_indices:
                img = self._overlay_images[img_idx]

                x_center = np.random.randint(x_start, x_end + 1)
                y_pos = height - img.shape[0]
                
                self._overlay_alpha_blend(img, x_center, y_pos)
        
        self._previous_counters = counters.copy()

        return self._overlay_image
        
    def _overlay_alpha_blend(self, img, x_center, y_pos):
        img_h, img_w = img.shape[0], img.shape[1]
        x_left = x_center - img_w // 2
        
        height, width = self._target_size[1], self._target_size[0]
        
        src_x_start = max(0, -x_left)
        src_y_start = max(0, -y_pos)
        src_x_end = min(img_w, width - x_left)
        src_y_end = min(img_h, height - y_pos)
        
        dst_x_start = max(0, x_left)
        dst_x_end = min(width, x_left + img_w)
        dst_y_start = max(0, y_pos)
        dst_y_end = min(height, y_pos + img_h)
        
        if src_x_end <= src_x_start or src_y_end <= src_y_start:
            return
            
        src_region = img[src_y_start:src_y_end, src_x_start:src_x_end]
        dst_region = self._overlay_image[dst_y_start:dst_y_end, dst_x_start:dst_x_end]
        
        src_alpha = src_region[:, :, 3] / 255.0
        src_alpha_3d = np.dstack([src_alpha, src_alpha, src_alpha])
        
        result = np.copy(dst_region)
        result[:, :, :3] = dst_region[:, :, :3] * (1 - src_alpha_3d) + src_region[:, :, :3] * src_alpha_3d
        result[:, :, 3] = np.maximum(dst_region[:, :, 3], src_region[:, :, 3])
        
        self._overlay_image[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = result
        
    @property
    def overlay_image(self) -> npt.NDArray[np.uint8]:
        return self._overlay_image
