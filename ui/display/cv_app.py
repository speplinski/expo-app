import cv2

from config.modules_configs.display_config import DisplayConfig


class CVApp:
    def __init__(self, monitor_index: int, config: DisplayConfig):
        self.config = config
        self.window_name = "The Most Polish Landscape"

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)

        if self.config.full_screen_mode:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            if monitor_index >= len(config.available_monitors):
                print(f"Warning: Monitor {monitor_index} not found. Using monitor 0.")
                monitor_index = 0

            x, y, w, h = config.available_monitors[monitor_index]
            cv2.moveWindow(self.window_name, x, y)
            cv2.resizeWindow(self.window_name, w // 2, h // 2)
    
    def show_image(self, image):
        cv2.imshow(self.window_name, image)
        cv2.waitKey(1)
        
    def close(self):
        cv2.destroyWindow(self.window_name)