import cv2
import numpy as np
import torch
from PIL import Image
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet


class ImageUpscaler:
    def __init__(self, weights_path, scale):
        if torch.cuda.is_available():
            self.device, self.half = torch.device("cuda"), True
        elif torch.backends.mps.is_available():
            self.device, self.half = torch.device("mps"), False
        else:
            self.device, self.half = torch.device("cpu"), False

        rrdb = RRDBNet(
            num_in_ch   = 3,
            num_out_ch  = 3,
            num_feat    = 64,
            num_block   = 23,
            num_grow_ch = 32,
            scale       = scale
        )
        
        self.up = RealESRGANer(
            scale      = scale,
            model_path = weights_path,
            model      = rrdb,
            tile       = 1024,
            tile_pad   = 10,
            pre_pad    = 0,
            half       = self.half,
            device     = self.device
        )
        print(f"[Upscaler] dev={self.device} | fp16={self.half} | tile=1024")

    def increase_saturation(self, image, factor=1.2):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * factor
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


    def upscale(self, cv_image):
        with torch.no_grad():
            sr_bgr, _ = self.up.enhance(cv_image)
            sr_bgr = self.increase_saturation(sr_bgr, 1.25)
        return sr_bgr