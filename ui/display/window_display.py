import logging
import time

import cv2
import numpy as np
import numpy.typing as npt
from textual.app import App

from config.modules_configs.display_config import DisplayConfig
from ui.display.playback_statistics import PlaybackStatistics
from ui.display.cv_app import CVApp


class WindowDisplay:
    def __init__(self, config: DisplayConfig, model_resolution: tuple[int, int], app: App):
        self.config = config
        self.logger = logging.getLogger()
        self.app = app
        
        self.model_resolution = model_resolution
        self.content_resolution = config.content_resolution
        
        self.cv_app = CVApp(config.monitor_index, config)
        
        monitor_index = min(config.monitor_index, len(config.available_monitors) - 1)
        _, _, self.monitor_width, self.monitor_height = config.available_monitors[monitor_index]
        
        self.stats = PlaybackStatistics()

    def process_frame(self, image: npt.NDArray[np.uint8]):
        try:
            self._handle_events()
            self._render(image)
        except Exception as e:
            self.logger.error(f"Error in render loop: {e}")

    def _handle_events(self):
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            self.app.action_quit()

    def _render(self, image: npt.NDArray[np.uint8]):
        display_image = self._prepare_image(image)
        
        self.stats.update_display_frame()
        if not self.stats.start_time:
            self.stats.start_playback(time.time())
        
        self.cv_app.show_image(display_image)

    def _prepare_image(self, input_image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        if self.config.full_screen_mode:
            target_width, target_height = self.monitor_width, self.monitor_height
        else:
            target_width, target_height = self.config.content_resolution
        
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        if self.config.background_color != (0, 0, 0):
            canvas[:] = self.config.background_color
        
        input_height, input_width = input_image.shape[:2]
        
        if self.config.scaling_mode == "none":
            x_offset = (target_width - input_width) // 2
            y_offset = (target_height - input_height) // 2
            
            if x_offset >= 0 and y_offset >= 0:
                canvas[y_offset:y_offset+input_height, x_offset:x_offset+input_width] = input_image
            else:
                src_x = max(0, -x_offset)
                src_y = max(0, -y_offset)
                dst_x = max(0, x_offset)
                dst_y = max(0, y_offset)
                
                copy_width = min(input_width - src_x, target_width - dst_x)
                copy_height = min(input_height - src_y, target_height - dst_y)
                
                if copy_width > 0 and copy_height > 0:
                    canvas[dst_y:dst_y+copy_height, dst_x:dst_x+copy_width] = input_image[src_y:src_y+copy_height, src_x:src_x+copy_width]
                
        elif self.config.scaling_mode == "stretch":
            return cv2.resize(input_image, (target_width, target_height))
            
        elif self.config.scaling_mode == "fit" or self.config.scaling_mode == "fill":
            scale_width = target_width / input_width
            scale_height = target_height / input_height
            
            if self.config.scaling_mode == "fit":
                scale = min(scale_width, scale_height)
            else:
                scale = max(scale_width, scale_height)
            
            new_width = int(input_width * scale)
            new_height = int(input_height * scale)
            
            resized_image = cv2.resize(input_image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2

            canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_image
        
        return canvas

    def cleanup(self):
        self.cv_app.close()